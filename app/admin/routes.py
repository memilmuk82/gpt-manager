import csv
import io
import subprocess
import sys
from collections import defaultdict
from functools import wraps
from pathlib import Path

from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.admin import admin_bp
from app.defaults import DEFAULT_WORK_TYPES
from app.extensions import db
from app.models import (
    AppSetting,
    ApprovalStatus,
    GuideItem,
    PromptReview,
    Reservation,
    ReservationStatus,
    UsageLog,
    User,
)

ROLE_LABELS = {
    "user": "일반 사용자",
    "assistant_admin": "보조관리자",
    "admin": "관리자",
}


def admin_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if not current_user.can_access_admin or not current_user.is_approved:
            abort(403)
        return view(*args, **kwargs)

    return wrapped


@admin_bp.get("")
@admin_required
def dashboard():
    section = request.args.get("section", "overview")
    return render_template("admin/dashboard.html", **_admin_context(section=section))


@admin_bp.get("/users")
@admin_required
def users():
    return render_template("admin/dashboard.html", **_admin_context(section="users"))


@admin_bp.post("/settings")
@admin_required
def save_settings():
    for setting in AppSetting.query.order_by(AppSetting.sort_order.asc()).all():
        value = request.form.get(setting.key, "").strip()
        if not value:
            flash(f"{setting.label} 항목을 입력하세요.", "error")
            return redirect(url_for("admin.dashboard", section="settings"))
        setting.value = value
    db.session.commit()
    flash("설정 변경사항을 저장했습니다.", "success")
    return redirect(url_for("admin.dashboard", section="settings"))


@admin_bp.post("/guides")
@admin_required
def save_guides():
    for guide in GuideItem.query.order_by(GuideItem.sort_order.asc()).all():
        prefix = f"guide_{guide.id}_"
        guide.category = request.form.get(prefix + "category", "").strip() or guide.category
        guide.title = request.form.get(prefix + "title", "").strip() or guide.title
        guide.body = request.form.get(prefix + "body", "").strip()
        guide.sort_order = _int_or_default(request.form.get(prefix + "sort_order"), guide.sort_order)
        guide.is_active = request.form.get(prefix + "is_active") == "on"
    db.session.commit()
    flash("안내 문구를 저장했습니다.", "success")
    return redirect(url_for("admin.dashboard", section="guides"))


@admin_bp.post("/users")
@admin_required
def create_user():
    email = request.form.get("email", "").strip().lower()
    name = request.form.get("name", "").strip()
    password = request.form.get("password", "").strip() or "password123"
    if not email or not name:
        flash("이메일과 이름을 입력하세요.", "error")
        return redirect(url_for("admin.dashboard", section="users"))
    if User.query.filter_by(email=email).first():
        flash("이미 등록된 이메일입니다.", "error")
        return redirect(url_for("admin.dashboard", section="users"))

    user = User(email=email, name=name, approval_status=ApprovalStatus.APPROVED)
    _apply_user_form(user)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    flash(f"{name} 사용자를 추가했습니다.", "success")
    return redirect(url_for("admin.dashboard", section="users"))


@admin_bp.post("/users/<int:user_id>/update")
@admin_required
def update_user(user_id: int):
    user = db.session.get(User, user_id) or abort(404)
    if user.id == current_user.id and request.form.get("role") not in {"admin", "assistant_admin"}:
        flash("자기 자신의 관리자 권한은 해제할 수 없습니다.", "error")
        return redirect(url_for("admin.dashboard", section="users", edit_user_id=user.id))
    _apply_user_form(user)
    db.session.commit()
    flash(f"{user.email} 사용자 정보를 저장했습니다.", "success")
    return redirect(url_for("admin.dashboard", section="users"))


@admin_bp.post("/users/bulk")
@admin_required
def bulk_users():
    upload = request.files.get("csv_file")
    if upload is None or not upload.filename:
        flash("CSV 파일을 선택하세요.", "error")
        return redirect(url_for("admin.dashboard", section="users"))

    try:
        text = upload.stream.read().decode("utf-8-sig")
        rows = list(csv.DictReader(io.StringIO(text)))
    except UnicodeDecodeError:
        flash("CSV 파일은 UTF-8 형식이어야 합니다.", "error")
        return redirect(url_for("admin.dashboard", section="users"))

    errors = []
    prepared = []
    seen_emails = set()
    for index, row in enumerate(rows, start=2):
        email = (row.get("email") or "").strip().lower()
        name = (row.get("name") or "").strip()
        role = (row.get("role") or "user").strip() or "user"
        if not email or not name:
            errors.append(f"{index}행: email, name은 필수입니다.")
        if role not in ROLE_LABELS:
            errors.append(f"{index}행: role 값은 user, assistant_admin, admin 중 하나여야 합니다.")
        if email in seen_emails or User.query.filter_by(email=email).first():
            errors.append(f"{index}행: 이미 등록되었거나 중복된 이메일입니다. {email}")
        seen_emails.add(email)
        prepared.append((row, email, name, role))

    if errors:
        for error in errors[:5]:
            flash(error, "error")
        if len(errors) > 5:
            flash(f"외 {len(errors) - 5}건의 오류가 있습니다. 한 건이라도 실패하면 저장하지 않습니다.", "error")
        return redirect(url_for("admin.dashboard", section="users"))

    for row, email, name, role in prepared:
        user = User(
            email=email,
            name=name,
            department=(row.get("department") or "").strip(),
            extension=(row.get("extension") or "").strip(),
            role=role,
            approval_status=ApprovalStatus.APPROVED,
            is_active=_csv_bool(row.get("active"), True),
            is_auth_manager=_csv_bool(row.get("is_auth_manager"), False),
            sort_order=_int_or_default(row.get("sort_order"), 100),
        )
        user.set_password("password123")
        db.session.add(user)
    db.session.commit()
    flash(f"CSV 사용자 {len(prepared)}명을 일괄 등록했습니다.", "success")
    return redirect(url_for("admin.dashboard", section="users"))


@admin_bp.post("/users/<int:user_id>/approve")
@admin_required
def approve_user(user_id: int):
    user = db.session.get(User, user_id) or abort(404)
    user.approval_status = ApprovalStatus.APPROVED
    user.is_active = True
    db.session.commit()
    flash(f"{user.email} 계정을 승인했습니다.", "success")
    return redirect(url_for("admin.dashboard", section="requests"))


@admin_bp.post("/users/<int:user_id>/suspend")
@admin_required
def suspend_user(user_id: int):
    user = db.session.get(User, user_id) or abort(404)
    if user.id == current_user.id:
        flash("자기 자신의 계정은 정지할 수 없습니다.", "error")
        return redirect(url_for("admin.dashboard", section="users"))

    user.approval_status = ApprovalStatus.SUSPENDED
    user.is_active = False
    db.session.commit()
    flash(f"{user.email} 계정을 비활성화했습니다.", "success")
    return redirect(url_for("admin.dashboard", section="users"))


@admin_bp.post("/users/<int:user_id>/activate")
@admin_required
def activate_user(user_id: int):
    user = db.session.get(User, user_id) or abort(404)
    user.approval_status = ApprovalStatus.APPROVED
    user.is_active = True
    db.session.commit()
    flash(f"{user.email} 계정을 활성화했습니다.", "success")
    return redirect(url_for("admin.dashboard", section="users"))


@admin_bp.post("/tests/run")
@admin_required
def run_tests():
    result = None
    try:
        completed = subprocess.run(
            [sys.executable, "-m", "pytest"],
            cwd=Path(__file__).resolve().parents[2],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        result = {
            "returncode": completed.returncode,
            "summary": _pytest_summary(completed.stdout + "\n" + completed.stderr),
            "output": (completed.stdout + "\n" + completed.stderr)[-12000:],
        }
        flash("전체 테스트 실행이 완료되었습니다.", "success" if completed.returncode == 0 else "error")
    except Exception as exc:  # pragma: no cover - 운영 환경 보호용
        result = {"returncode": 1, "summary": str(exc), "output": str(exc)}
        flash("테스트 실행 중 오류가 발생했습니다.", "error")
    return render_template("admin/dashboard.html", **_admin_context(section="tests", test_result=result))


def _admin_context(section: str = "overview", test_result: dict | None = None) -> dict:
    users = User.query.order_by(User.sort_order.asc(), User.approval_status.asc(), User.name.asc()).all()
    pending_users = [user for user in users if user.approval_status == ApprovalStatus.PENDING]
    reservations = Reservation.query.all()
    usage_logs = UsageLog.query.all()
    stats = {
        "users": len(users),
        "pending_users": len(pending_users),
        "reservations": len(reservations),
        "usage_logs": len(usage_logs),
        "prompt_reviews": PromptReview.query.count(),
    }
    edit_user_id = request.args.get("edit_user_id", type=int)
    edit_user = db.session.get(User, edit_user_id) if edit_user_id else None
    return {
        "section": section,
        "stats": stats,
        "settings": AppSetting.query.order_by(AppSetting.sort_order.asc()).all(),
        "guides": GuideItem.query.order_by(GuideItem.sort_order.asc()).all(),
        "users": users,
        "pending_users": pending_users,
        "role_labels": ROLE_LABELS,
        "edit_user": edit_user,
        "admin_stats": _usage_statistics(users, reservations),
        "work_types": DEFAULT_WORK_TYPES,
        "test_result": test_result,
    }


def _apply_user_form(user: User) -> None:
    user.name = request.form.get("name", "").strip() or user.name
    user.department = request.form.get("department", "").strip()
    user.extension = request.form.get("extension", "").strip()
    user.role = request.form.get("role", "user") if request.form.get("role") in ROLE_LABELS else "user"
    user.is_active = request.form.get("is_active") == "on"
    user.is_auth_manager = request.form.get("is_auth_manager") == "on"
    user.sort_order = _int_or_default(request.form.get("sort_order"), user.sort_order or 100)
    user.approval_status = ApprovalStatus.APPROVED if user.is_active else ApprovalStatus.SUSPENDED


def _usage_statistics(users: list[User], reservations: list[Reservation]) -> dict:
    total_reserved = 0
    total_actual = 0
    by_user = {user.id: {"user": user, "count": 0, "reserved": 0, "actual": 0} for user in users}
    by_type = defaultdict(lambda: {"count": 0, "reserved": 0, "actual": 0})

    for reservation in reservations:
        if reservation.status == ReservationStatus.CANCELLED:
            continue
        minutes = max(0, int((reservation.end_at - reservation.start_at).total_seconds() // 60))
        actual = minutes if reservation.status == ReservationStatus.COMPLETED else 0
        total_reserved += minutes
        total_actual += actual
        if reservation.user_id in by_user:
            by_user[reservation.user_id]["count"] += 1
            by_user[reservation.user_id]["reserved"] += minutes
            by_user[reservation.user_id]["actual"] += actual
        work_type = reservation.work_type or "미분류"
        by_type[work_type]["count"] += 1
        by_type[work_type]["reserved"] += minutes
        by_type[work_type]["actual"] += actual

    return {
        "total_reservations": sum(item["count"] for item in by_user.values()),
        "target_users": sum(1 for item in by_user.values() if item["count"] > 0),
        "reserved_minutes": total_reserved,
        "actual_minutes": total_actual,
        "by_user": by_user.values(),
        "by_type": [{"work_type": key, **value} for key, value in by_type.items()],
    }


def _int_or_default(value: str | None, default: int) -> int:
    try:
        return int(value or default)
    except (TypeError, ValueError):
        return default


def _csv_bool(value: str | None, default: bool) -> bool:
    if value is None or value == "":
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on", "활성", "예"}


def _pytest_summary(output: str) -> str:
    for line in reversed(output.splitlines()):
        if " passed" in line or " failed" in line or " error" in line:
            return line.strip("= ")
    return "테스트 결과 요약을 확인할 수 없습니다."
