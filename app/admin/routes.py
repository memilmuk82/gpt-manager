import csv
import importlib.util
import io
import shutil
import subprocess
import sys
from calendar import monthrange
from collections import defaultdict
from datetime import date, datetime, time
from functools import wraps
from pathlib import Path

from flask import Response, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.admin import admin_bp
from app.extensions import db
from app.models import (
    AiResource,
    AppSetting,
    AuditLog,
    ApprovalStatus,
    GuideItem,
    PromptReview,
    Reservation,
    ReservationStatus,
    UsageLog,
    User,
    WorkType,
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


@admin_bp.get("/reports/monthly.md")
@admin_required
def monthly_report_download():
    report = _monthly_report_context()
    filename = f"gpt-manager-monthly-report-{report['month']}.md"
    return Response(
        report["markdown"],
        mimetype="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@admin_bp.post("/settings")
@admin_required
def save_settings():
    for setting in AppSetting.query.order_by(AppSetting.sort_order.asc()).all():
        value = request.form.get(setting.key, "").strip()
        if not value:
            flash(f"{setting.label} 항목을 입력하세요.", "error")
            return redirect(url_for("admin.dashboard", section="settings"))
        setting.value = value
    _record_audit("settings.update", "settings", "app", "관리자 설정을 저장했습니다.")
    db.session.commit()
    flash("설정 변경사항을 저장했습니다.", "success")
    return redirect(url_for("admin.dashboard", section="settings"))


@admin_bp.post("/guides")
@admin_required
def save_guides():
    for setting in _guide_settings():
        value = request.form.get(f"setting_{setting.key}", "").strip()
        if not value:
            flash(f"{setting.label} 항목을 입력하세요.", "error")
            return redirect(url_for("admin.dashboard", section="guides"))
        setting.value = value

    for guide in GuideItem.query.order_by(GuideItem.sort_order.asc()).all():
        prefix = f"guide_{guide.id}_"
        guide.category = request.form.get(prefix + "category", "").strip() or guide.category
        guide.title = request.form.get(prefix + "title", "").strip() or guide.title
        guide.body = request.form.get(prefix + "body", "").strip()
        guide.sort_order = _int_or_default(request.form.get(prefix + "sort_order"), guide.sort_order)
        guide.is_active = request.form.get(prefix + "is_active") == "on"
    _record_audit("guides.update", "guides", "all", "안내 문구를 저장했습니다.")
    db.session.commit()
    flash("안내 문구를 저장했습니다.", "success")
    return redirect(url_for("admin.dashboard", section="guides"))


@admin_bp.post("/resources")
@admin_required
def save_resources():
    for resource in AiResource.query.order_by(AiResource.name.asc()).all():
        prefix = f"resource_{resource.id}_"
        name = request.form.get(prefix + "name", "").strip()
        provider = request.form.get(prefix + "provider", "").strip()
        if not name or not provider:
            flash("AI 리소스 이름과 제공사를 모두 입력하세요.", "error")
            return redirect(url_for("admin.dashboard", section="resources"))
        resource.name = name
        resource.provider = provider
        resource.description = request.form.get(prefix + "description", "").strip()
        resource.is_active = request.form.get(prefix + "is_active") == "on"

    new_name = request.form.get("new_resource_name", "").strip()
    new_provider = request.form.get("new_resource_provider", "").strip()
    new_description = request.form.get("new_resource_description", "").strip()
    if new_name or new_provider or new_description:
        if not new_name or not new_provider:
            flash("새 AI 리소스의 이름과 제공사를 모두 입력하세요.", "error")
            return redirect(url_for("admin.dashboard", section="resources"))
        db.session.add(
            AiResource(
                name=new_name,
                provider=new_provider,
                description=new_description,
                is_active=request.form.get("new_resource_is_active") == "on",
            )
        )

    _record_audit("resources.update", "ai_resource", "all", "AI 리소스 변경사항을 저장했습니다.")
    db.session.commit()
    flash("AI 리소스 변경사항을 저장했습니다.", "success")
    return redirect(url_for("admin.dashboard", section="resources"))


@admin_bp.post("/work-types")
@admin_required
def save_work_types():
    for work_type in WorkType.query.order_by(WorkType.sort_order.asc(), WorkType.name.asc()).all():
        prefix = f"work_type_{work_type.id}_"
        name = request.form.get(prefix + "name", "").strip()
        if not name:
            flash("작업유형 이름을 입력하세요.", "error")
            return redirect(url_for("admin.dashboard", section="resources"))
        work_type.name = name
        work_type.sort_order = _int_or_default(request.form.get(prefix + "sort_order"), work_type.sort_order)
        work_type.is_active = request.form.get(prefix + "is_active") == "on"

    new_name = request.form.get("new_work_type_name", "").strip()
    if new_name:
        db.session.add(
            WorkType(
                name=new_name,
                sort_order=_int_or_default(request.form.get("new_work_type_sort_order"), 100),
                is_active=request.form.get("new_work_type_is_active") == "on",
            )
        )

    db.session.flush()
    active_count = WorkType.query.filter_by(is_active=True).count()
    if active_count == 0:
        db.session.rollback()
        flash("최소 1개의 활성 작업유형이 필요합니다.", "error")
        return redirect(url_for("admin.dashboard", section="resources"))

    _record_audit("work_types.update", "work_type", "all", "작업유형 변경사항을 저장했습니다.")
    db.session.commit()
    flash("작업유형 변경사항을 저장했습니다.", "success")
    return redirect(url_for("admin.dashboard", section="resources"))


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
    if _auth_manager_limit_exceeded(user):
        db.session.rollback()
        flash("인증번호 담당자는 최대 2명까지만 지정할 수 있습니다.", "error")
        return redirect(url_for("admin.dashboard", section="users"))
    user.set_password(password)
    db.session.add(user)
    db.session.flush()
    _record_audit("users.create", "user", str(user.id), f"{user.email} 사용자를 추가했습니다.")
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
    if _auth_manager_limit_exceeded(user):
        db.session.rollback()
        flash("인증번호 담당자는 최대 2명까지만 지정할 수 있습니다.", "error")
        return redirect(url_for("admin.dashboard", section="users", edit_user_id=user.id))
    _record_audit("users.update", "user", str(user.id), f"{user.email} 사용자 정보를 저장했습니다.")
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

    existing_auth_managers = User.query.filter_by(
        is_auth_manager=True,
        is_active=True,
        approval_status=ApprovalStatus.APPROVED,
    ).count()
    new_auth_managers = sum(
        1
        for row, _, _, _ in prepared
        if _csv_bool(row.get("is_auth_manager"), False) and _csv_bool(row.get("active"), True)
    )
    if existing_auth_managers + new_auth_managers > 2:
        flash("인증번호 담당자는 최대 2명까지만 지정할 수 있습니다.", "error")
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
    _record_audit("users.bulk_create", "user", "bulk", f"CSV 사용자 {len(prepared)}명을 일괄 등록했습니다.")
    db.session.commit()
    flash(f"CSV 사용자 {len(prepared)}명을 일괄 등록했습니다.", "success")
    return redirect(url_for("admin.dashboard", section="users"))


@admin_bp.post("/users/<int:user_id>/approve")
@admin_required
def approve_user(user_id: int):
    user = db.session.get(User, user_id) or abort(404)
    user.approval_status = ApprovalStatus.APPROVED
    user.is_active = True
    _record_audit("users.approve", "user", str(user.id), f"{user.email} 계정을 승인했습니다.")
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
    _record_audit("users.suspend", "user", str(user.id), f"{user.email} 계정을 비활성화했습니다.")
    db.session.commit()
    flash(f"{user.email} 계정을 비활성화했습니다.", "success")
    return redirect(url_for("admin.dashboard", section="users"))


@admin_bp.post("/users/<int:user_id>/activate")
@admin_required
def activate_user(user_id: int):
    user = db.session.get(User, user_id) or abort(404)
    user.approval_status = ApprovalStatus.APPROVED
    user.is_active = True
    _record_audit("users.activate", "user", str(user.id), f"{user.email} 계정을 활성화했습니다.")
    db.session.commit()
    flash(f"{user.email} 계정을 활성화했습니다.", "success")
    return redirect(url_for("admin.dashboard", section="users"))


@admin_bp.post("/tests/run")
@admin_required
def run_tests():
    result = None
    try:
        completed = subprocess.run(
            _pytest_command(),
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
        _record_audit("tests.run", "pytest", str(completed.returncode), result["summary"])
        db.session.commit()
        flash("전체 테스트 실행이 완료되었습니다.", "success" if completed.returncode == 0 else "error")
    except Exception as exc:  # pragma: no cover - 운영 환경 보호용
        result = {"returncode": 1, "summary": str(exc), "output": str(exc)}
        flash("테스트 실행 중 오류가 발생했습니다.", "error")
    return render_template("admin/dashboard.html", **_admin_context(section="tests", test_result=result))


def _admin_context(section: str = "overview", test_result: dict | None = None) -> dict:
    all_users = User.query.order_by(User.sort_order.asc(), User.approval_status.asc(), User.name.asc()).all()
    users = _filtered_users(all_users)
    pending_users = [user for user in all_users if user.approval_status == ApprovalStatus.PENDING]
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
        "user_filters": _user_filter_values(),
        "report": _monthly_report_context(),
        "audit_logs": AuditLog.query.order_by(AuditLog.created_at.desc()).limit(100).all(),
        "guide_settings": _guide_settings(),
        "guides": GuideItem.query.order_by(GuideItem.sort_order.asc()).all(),
        "resources": AiResource.query.order_by(AiResource.name.asc()).all(),
        "work_types": WorkType.query.order_by(WorkType.sort_order.asc(), WorkType.name.asc()).all(),
        "users": users,
        "pending_users": pending_users,
        "role_labels": ROLE_LABELS,
        "edit_user": edit_user,
        "admin_stats": _usage_statistics(all_users, reservations),
        "test_result": test_result,
    }


def _filtered_users(users: list[User]) -> list[User]:
    filters = _user_filter_values()
    filtered = users
    if filters["q"]:
        needle = filters["q"].lower()
        filtered = [
            user
            for user in filtered
            if needle in user.name.lower()
            or needle in user.email.lower()
            or needle in (user.department or "").lower()
        ]
    if filters["role"]:
        filtered = [user for user in filtered if user.role == filters["role"]]
    if filters["status"] == "active":
        filtered = [user for user in filtered if user.is_active and user.approval_status == ApprovalStatus.APPROVED]
    elif filters["status"] == "inactive":
        filtered = [user for user in filtered if not user.is_active or user.approval_status == ApprovalStatus.SUSPENDED]
    elif filters["status"] == "pending":
        filtered = [user for user in filtered if user.approval_status == ApprovalStatus.PENDING]
    return filtered


def _user_filter_values() -> dict:
    return {
        "q": request.args.get("q", "").strip(),
        "role": request.args.get("role", "").strip(),
        "status": request.args.get("status", "").strip(),
    }


def _monthly_report_context() -> dict:
    raw_month = request.args.get("month", "").strip()
    today = date.today()
    try:
        year, month = [int(part) for part in raw_month.split("-", 1)] if raw_month else (today.year, today.month)
        start_date = date(year, month, 1)
    except (TypeError, ValueError):
        start_date = date(today.year, today.month, 1)
    last_day = monthrange(start_date.year, start_date.month)[1]
    end_date = date(start_date.year, start_date.month, last_day)
    start_at = datetime.combine(start_date, time.min)
    end_at = datetime.combine(end_date, time.max)

    reservations = Reservation.query.filter(
        Reservation.start_at >= start_at,
        Reservation.start_at <= end_at,
    ).all()
    usage_logs = UsageLog.query.filter(
        UsageLog.created_at >= start_at,
        UsageLog.created_at <= end_at,
    ).order_by(UsageLog.created_at.asc()).all()
    prompt_reviews = PromptReview.query.filter(
        PromptReview.created_at >= start_at,
        PromptReview.created_at <= end_at,
    ).count()
    stats = _usage_statistics(User.query.all(), reservations)
    month_label = start_date.strftime("%Y-%m")
    markdown = _build_monthly_report_markdown(month_label, stats, usage_logs, prompt_reviews)
    return {
        "month": month_label,
        "start_date": start_date,
        "end_date": end_date,
        "stats": stats,
        "usage_logs": usage_logs,
        "prompt_reviews": prompt_reviews,
        "markdown": markdown,
    }


def _build_monthly_report_markdown(month: str, stats: dict, usage_logs: list[UsageLog], prompt_reviews: int) -> str:
    lines = [
        f"# 생성형 AI 계정 월간 운영 보고서 ({month})",
        "",
        "## 요약",
        "",
        f"- 전체 예약: {stats['total_reservations']}건",
        f"- 이용 사용자: {stats['target_users']}명",
        f"- 예약 기준 사용 시간: {stats['reserved_minutes']}분",
        f"- 완료 기준 실제 사용 시간: {stats['actual_minutes']}분",
        f"- 사용 로그: {len(usage_logs)}건",
        f"- 프롬프트 점검: {prompt_reviews}건",
        "",
        "## 작업 유형별 사용",
        "",
    ]
    if stats["by_type"]:
        for row in stats["by_type"]:
            lines.append(f"- {row['work_type']}: {row['count']}건, 예약 {row['reserved']}분, 완료 {row['actual']}분")
    else:
        lines.append("- 집계된 작업 유형이 없습니다.")
    lines.extend(["", "## 주요 사용 로그", ""])
    if usage_logs:
        for log in usage_logs[:20]:
            user_name = log.user.name if log.user else "알 수 없음"
            lines.append(f"- {log.created_at.strftime('%Y-%m-%d')} / {user_name} / {log.work_type}: {log.summary}")
    else:
        lines.append("- 작성된 사용 로그가 없습니다.")
    lines.append("")
    return "\n".join(lines)


def _record_audit(action: str, target_type: str, target_id: str, summary: str) -> None:
    db.session.add(
        AuditLog(
            actor_user_id=current_user.id if current_user.is_authenticated else None,
            action=action,
            target_type=target_type,
            target_id=target_id,
            summary=summary,
            ip_address=request.headers.get("X-Forwarded-For", request.remote_addr or "").split(",", 1)[0],
        )
    )


def _guide_settings() -> list[AppSetting]:
    keys = [
        "auth_info_title",
        "board_reference_message",
        "auth_message",
        "logout_notice",
        "reservation_intro_text",
        "reservation_helper_text",
        "guide_intro_text",
    ]
    settings = AppSetting.query.filter(AppSetting.key.in_(keys)).all()
    return sorted(settings, key=lambda setting: keys.index(setting.key))


def _auth_manager_limit_exceeded(user: User) -> bool:
    if not user.is_auth_manager or not user.is_active or user.approval_status != ApprovalStatus.APPROVED:
        return False
    with db.session.no_autoflush:
        query = User.query.filter_by(
            is_auth_manager=True,
            is_active=True,
            approval_status=ApprovalStatus.APPROVED,
        )
        if user.id is not None:
            query = query.filter(User.id != user.id)
        return query.count() >= 2


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


def _pytest_command() -> list[str]:
    if importlib.util.find_spec("pytest") is not None:
        return [sys.executable, "-m", "pytest"]
    uv_path = shutil.which("uv")
    if uv_path:
        return [uv_path, "run", "--frozen", "pytest"]
    return [sys.executable, "-m", "pytest"]


def _pytest_summary(output: str) -> str:
    for line in reversed(output.splitlines()):
        if " passed" in line or " failed" in line or " error" in line:
            return line.strip("= ")
    return "테스트 결과 요약을 확인할 수 없습니다."
