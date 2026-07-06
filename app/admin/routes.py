import csv
import importlib.util
import io
import re
import shutil
import subprocess
import sys
from calendar import monthrange
from collections import defaultdict
from datetime import date, datetime, time
from functools import wraps
from pathlib import Path

from flask import Response, abort, current_app, flash, redirect, render_template, request, send_from_directory, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_

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
    UserApiKey,
    WorkType,
)

MAX_BACKUP_FILES = 20

ROLE_LABELS = {
    "user": "일반 사용자",
    "assistant_admin": "보조관리자",
    "admin": "관리자",
}

TEST_FILE_DESCRIPTIONS = {
    "tests/test_admin.py": {
        "target": "관리자 기능",
        "checks": "관리자/보조관리자 접근, 사용자 승인과 정지 제한, 리소스와 작업유형 관리, 안내 문구, 인증번호 담당자 제한, 테스트 실행, 월간 보고서, 감사 로그, 사용자 필터, CSV 내보내기, SQLite 백업",
    },
    "tests/test_api_keys.py": {
        "target": "사용자 API Key 관리",
        "checks": "API Key 설정 접근, Provider별 키 저장, 암호화 저장, 원문 미노출, 마지막 4자리 표시, 교체와 삭제, 연결 테스트, 모델 목록 갱신 fallback",
    },
    "tests/test_app.py": {
        "target": "기본 화면과 대시보드",
        "checks": "앱 팩토리 생성, 첫 화면 응답, 대시보드 사용 로그 알림, 최근 30일 기준 안내, 공지 배너 표시",
    },
    "tests/test_auth.py": {
        "target": "사용자 인증",
        "checks": "회원가입, 비밀번호 해시 저장, 중복 가입 차단, 로그인과 로그아웃, 승인/정지 상태 처리, 역할 부여, CSRF 보호",
    },
    "tests/test_config.py": {
        "target": "설정과 DB 초기화",
        "checks": "SQLite 상대 경로 보정, 메모리 DB 유지, 기존 사용자 테이블의 인증/승인 컬럼 자동 보강",
    },
    "tests/test_google_oauth.py": {
        "target": "Google OAuth 로그인",
        "checks": "OAuth 리다이렉트와 콜백, senedu 계정 자동 승인, 외부 계정 승인 정책, 기존 로컬 계정 연결, 미검증 이메일과 허용되지 않은 도메인 차단, 관리자 역할 보존",
    },
    "tests/test_health.py": {
        "target": "헬스 체크",
        "checks": "healthz 엔드포인트 응답 코드와 JSON 상태값",
    },
    "tests/test_legal_pages.py": {
        "target": "약관과 개인정보처리방침",
        "checks": "Footer 링크와 공개 접근, Markdown 렌더링, raw HTML escape를 확인한다. 법적 내용 타당성은 기관 검토로 확인한다.",
    },
    "tests/test_prompt_reviews.py": {
        "target": "프롬프트 정리 기능",
        "checks": "로그인과 API Key 요구, 현재 화면 문구, 저장된 키와 일회성 키 사용, 입력 길이 제한, 일일 한도와 연속 요청 제한, 사용자별 접근 제어, 프롬프트 조립, Markdown 다운로드, 검색, 템플릿과 Provider 표시",
    },
    "tests/test_reservations.py": {
        "target": "예약 기능",
        "checks": "예약 생성과 취소, 본인 예약 목록, 같은 리소스 시간 충돌, 연속 예약과 다른 리소스 허용, 취소 예약 제외, 비활성 리소스 차단, 시간 검증, 오늘 예약, 필터, 월간 캘린더, 사용 규칙 버전 기록",
    },
    "tests/test_usage_logs.py": {
        "target": "사용 로그",
        "checks": "예약 기반 사용 로그, 리소스 단독 로그, 예약 사전 선택, 타인 예약 사용 차단, 타인 로그 접근 차단, 키워드/작업유형/리소스 필터",
    },
    "tests/test_user_model.py": {
        "target": "사용자 모델 보안",
        "checks": "비밀번호 해시 검증, 잘못된 비밀번호 거부, 원문 비밀번호 미저장",
    },
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


@admin_bp.get("/exports/users.csv")
@admin_required
def export_users_csv():
    filters = _export_filter_values()
    query = User.query
    if filters["q"]:
        like = f"%{filters['q']}%"
        query = query.filter(or_(User.name.ilike(like), User.email.ilike(like), User.department.ilike(like)))
    if filters["user_id"]:
        query = query.filter(User.id == filters["user_id"])
    if filters["start_at"]:
        query = query.filter(User.created_at >= filters["start_at"])
    if filters["end_at"]:
        query = query.filter(User.created_at <= filters["end_at"])

    rows = [["id", "email", "name", "department", "extension", "role", "approval_status", "is_active", "is_auth_manager", "created_at"]]
    for user in query.order_by(User.id.asc()).all():
        rows.append([user.id, user.email, user.name, user.department, user.extension, user.role, user.approval_status, user.is_active, user.is_auth_manager, user.created_at.isoformat()])
    return _csv_response("users.csv", rows)


@admin_bp.get("/exports/reservations.csv")
@admin_required
def export_reservations_csv():
    filters = _export_filter_values()
    query = Reservation.query.join(User).join(AiResource)
    if filters["q"]:
        like = f"%{filters['q']}%"
        query = query.filter(or_(Reservation.purpose.ilike(like), Reservation.work_type.ilike(like), Reservation.description.ilike(like), User.name.ilike(like), User.email.ilike(like)))
    if filters["user_id"]:
        query = query.filter(Reservation.user_id == filters["user_id"])
    if filters["resource_id"]:
        query = query.filter(Reservation.resource_id == filters["resource_id"])
    if filters["work_type"]:
        query = query.filter(Reservation.work_type == filters["work_type"])
    if filters["status"] in {ReservationStatus.RESERVED, ReservationStatus.COMPLETED, ReservationStatus.CANCELLED}:
        query = query.filter(Reservation.status == filters["status"])
    if filters["start_at"]:
        query = query.filter(Reservation.start_at >= filters["start_at"])
    if filters["end_at"]:
        query = query.filter(Reservation.start_at <= filters["end_at"])

    rows = [["id", "user_email", "resource", "start_at", "end_at", "work_type", "purpose", "status", "consent_version"]]
    for reservation in query.order_by(Reservation.start_at.desc()).all():
        rows.append([reservation.id, reservation.user.email, reservation.resource.name, reservation.start_at.isoformat(), reservation.end_at.isoformat(), reservation.work_type, reservation.purpose, reservation.status, reservation.consent_version])
    return _csv_response("reservations.csv", rows)


@admin_bp.get("/exports/usage-logs.csv")
@admin_required
def export_usage_logs_csv():
    filters = _export_filter_values()
    query = UsageLog.query.join(User).outerjoin(AiResource)
    if filters["q"]:
        like = f"%{filters['q']}%"
        query = query.filter(or_(UsageLog.summary.ilike(like), UsageLog.work_type.ilike(like), User.name.ilike(like), User.email.ilike(like)))
    if filters["user_id"]:
        query = query.filter(UsageLog.user_id == filters["user_id"])
    if filters["resource_id"]:
        query = query.filter(UsageLog.resource_id == filters["resource_id"])
    if filters["work_type"]:
        query = query.filter(UsageLog.work_type == filters["work_type"])
    if filters["start_at"]:
        query = query.filter(UsageLog.created_at >= filters["start_at"])
    if filters["end_at"]:
        query = query.filter(UsageLog.created_at <= filters["end_at"])

    rows = [["id", "user_email", "reservation_id", "resource", "work_type", "summary", "created_at"]]
    for log in query.order_by(UsageLog.created_at.desc()).all():
        rows.append([log.id, log.user.email, log.reservation_id or "", log.resource.name if log.resource else "", log.work_type, log.summary, log.created_at.isoformat()])
    return _csv_response("usage-logs.csv", rows)


@admin_bp.post("/backups")
@admin_required
def create_backup():
    db_path = _sqlite_database_path()
    if db_path is None or not db_path.exists():
        flash("백업할 SQLite DB 파일을 찾을 수 없습니다.", "error")
        return redirect(url_for("admin.dashboard", section="backups"))
    backup_dir = _backup_dir()
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_path = backup_dir / f"app-{datetime.now().strftime('%Y%m%d-%H%M%S')}.db"
    shutil.copy2(db_path, backup_path)
    removed_count = _prune_old_backups(MAX_BACKUP_FILES)
    summary = "SQLite DB 백업을 생성했습니다."
    if removed_count:
        summary += f" 오래된 백업 {removed_count}개를 정리했습니다."
    _record_audit("backups.create", "sqlite", backup_path.name, summary)
    db.session.commit()
    flash(f"백업을 생성했습니다: {backup_path.name}", "success")
    if removed_count:
        flash(f"최근 {MAX_BACKUP_FILES}개를 남기고 오래된 백업 {removed_count}개를 정리했습니다.", "warning")
    return redirect(url_for("admin.dashboard", section="backups"))


@admin_bp.get("/backups/<path:filename>")
@admin_required
def download_backup(filename: str):
    if "/" in filename or not filename.startswith("app-") or not filename.endswith(".db"):
        abort(404)
    return send_from_directory(_backup_dir(), filename, as_attachment=True)


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
        output = completed.stdout + "\n" + completed.stderr
        summary = _pytest_summary(output)
        test_files = _pytest_file_results(output)
        result = {
            "returncode": completed.returncode,
            "summary": summary,
            "total_tests": _pytest_total_tests(summary),
            "duration": _pytest_duration(summary),
            "output": output[-12000:],
            "test_files": test_files,
            "failure_summary": _pytest_failure_summary(output, test_files, completed.returncode),
            "resolution_hint": _pytest_resolution_hint(output, test_files, completed.returncode),
        }
        _record_audit("tests.run", "pytest", str(completed.returncode), result["summary"])
        db.session.commit()
        flash("전체 테스트 실행이 완료되었습니다.", "success" if completed.returncode == 0 else "error")
    except Exception as exc:  # pragma: no cover - 운영 환경 보호용
        test_files = _pytest_file_results("")
        result = {
            "returncode": 1,
            "summary": str(exc),
            "total_tests": None,
            "duration": None,
            "output": str(exc),
            "test_files": test_files,
            "failure_summary": f"테스트 실행 예외: {exc}",
            "resolution_hint": "서버의 Python/uv 실행 환경, 권한, 작업 디렉터리, pytest 설치 상태를 먼저 확인하세요.",
        }
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
        "backups": _available_backups(),
        "backup_keep_count": MAX_BACKUP_FILES,
        "export_filters": _export_filter_values(),
        "all_users": all_users,
        "guide_settings": _guide_settings(),
        "guides": GuideItem.query.order_by(GuideItem.sort_order.asc()).all(),
        "resources": AiResource.query.order_by(AiResource.name.asc()).all(),
        "work_types": WorkType.query.order_by(WorkType.sort_order.asc(), WorkType.name.asc()).all(),
        "users": users,
        "pending_users": pending_users,
        "role_labels": ROLE_LABELS,
        "edit_user": edit_user,
        "admin_stats": _usage_statistics(all_users, reservations),
        "api_key_statuses": UserApiKey.query.order_by(UserApiKey.provider.asc(), UserApiKey.created_at.desc()).all(),
        "test_result": test_result,
    }


def _csv_response(filename: str, rows: list[list]) -> Response:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerows(rows)
    return Response(
        "﻿" + output.getvalue(),
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


def _sqlite_database_path() -> Path | None:
    db_uri = current_app.config.get("SQLALCHEMY_DATABASE_URI", "")
    if db_uri == "sqlite:///:memory:" or not db_uri.startswith("sqlite:///"):
        return None
    return Path(db_uri.removeprefix("sqlite:///"))


def _backup_dir() -> Path:
    return Path(current_app.root_path).resolve().parent / "backups"


def _available_backups() -> list[dict]:
    backup_dir = _backup_dir()
    if not backup_dir.exists():
        return []
    backups = []
    for path in sorted(backup_dir.glob("app-*.db"), key=lambda item: item.stat().st_mtime, reverse=True)[:MAX_BACKUP_FILES]:
        stat = path.stat()
        backups.append({
            "name": path.name,
            "size_kb": max(1, stat.st_size // 1024),
            "created_at": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
        })
    return backups


def _prune_old_backups(keep_count: int = MAX_BACKUP_FILES) -> int:
    backup_dir = _backup_dir()
    if not backup_dir.exists():
        return 0
    backup_paths = sorted(backup_dir.glob("app-*.db"), key=lambda item: item.stat().st_mtime, reverse=True)
    removed_count = 0
    for path in backup_paths[keep_count:]:
        path.unlink(missing_ok=True)
        removed_count += 1
    return removed_count


def _export_filter_values() -> dict:
    return {
        "q": request.args.get("q", "").strip(),
        "start_date": request.args.get("start_date", "").strip(),
        "end_date": request.args.get("end_date", "").strip(),
        "start_at": _date_filter_bound(request.args.get("start_date", ""), end_of_day=False),
        "end_at": _date_filter_bound(request.args.get("end_date", ""), end_of_day=True),
        "user_id": request.args.get("user_id", type=int),
        "resource_id": request.args.get("resource_id", type=int),
        "work_type": request.args.get("work_type", "").strip(),
        "status": request.args.get("status", "").strip(),
    }


def _date_filter_bound(raw_value: str, *, end_of_day: bool) -> datetime | None:
    try:
        value = date.fromisoformat((raw_value or "").strip())
    except ValueError:
        return None
    return datetime.combine(value, time.max if end_of_day else time.min)


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
        f"- 프롬프트 정리: {prompt_reviews}건",
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


def _test_file_catalog() -> list[dict]:
    repo_root = Path(__file__).resolve().parents[2]
    discovered = sorted(path.as_posix() for path in (repo_root / "tests").glob("test_*.py"))
    paths = sorted(set(TEST_FILE_DESCRIPTIONS) | {f"tests/{Path(path).name}" for path in discovered})
    catalog = []
    for test_path in paths:
        description = TEST_FILE_DESCRIPTIONS.get(test_path, {})
        target = description.get("target", "설명 미등록")
        checks = description.get("checks", "설명 미등록")
        catalog.append(
            {
                "file": test_path,
                "target": target,
                "checks": checks,
                "hint": description.get("hint", _default_test_hint(test_path, target, checks)),
            }
        )
    return catalog


def _pytest_file_results(output: str) -> list[dict]:
    rows = _test_file_catalog()
    statuses = {row["file"]: "NOT RUN" for row in rows}
    failed_items = _pytest_failed_items(output)
    failed_by_file: dict[str, list[dict]] = defaultdict(list)
    for item in failed_items:
        failed_by_file[item["file"]].append(item)
    for line in output.splitlines():
        _apply_pytest_line_status(statuses, line.strip())
    for failed_file in failed_by_file:
        _merge_pytest_status(statuses, failed_file, "FAIL")
    results = []
    for row in rows:
        failures = failed_by_file.get(row["file"], [])
        results.append({
            **row,
            "status": statuses[row["file"]],
            "failures": failures,
            "failure_summary": _file_failure_summary(row["file"], statuses[row["file"]], failures),
        })
    return results



def _pytest_failed_items(output: str) -> list[dict]:
    failures = []
    seen = set()
    for line in output.splitlines():
        failed_match = re.match(r"^FAILED\s+(tests/[^:\s]+\.py)::([^\s]+)(?:\s+-\s+(.*))?", line.strip())
        error_match = re.match(r"^ERROR\s+(tests/[^:\s]+\.py)(?:::(\S+))?(?:\s+-\s+(.*))?", line.strip())
        match = failed_match or error_match
        if not match:
            continue
        path, test_name, reason = match.groups()
        key = (path, test_name or "module")
        if key in seen:
            continue
        seen.add(key)
        failures.append({
            "file": path,
            "test": test_name or "module setup",
            "reason": (reason or "pytest 상세 로그 확인 필요").strip(),
        })
    return failures


def _file_failure_summary(path: str, status: str, failures: list[dict]) -> str:
    if status == "PASS":
        return "실패 없음"
    if status == "SKIP":
        return "건너뜀 또는 조건부 실행"
    if status == "NOT RUN":
        return "이번 실행에서 수집되지 않음"
    if not failures:
        return f"{path}에서 실패가 감지됐습니다. 상세 로그를 확인하세요."
    first = failures[0]
    suffix = f" 외 {len(failures) - 1}건" if len(failures) > 1 else ""
    return f"{first['test']}: {first['reason']}{suffix}"


def _pytest_failure_summary(output: str, test_files: list[dict], returncode: int) -> str:
    if returncode == 0:
        return "실패한 테스트가 없습니다."
    failed_rows = [row for row in test_files if row.get("status") == "FAIL"]
    if failed_rows:
        summaries = [row.get("failure_summary", row["file"]) for row in failed_rows[:3]]
        suffix = f" 외 {len(failed_rows) - 3}개 파일" if len(failed_rows) > 3 else ""
        return " / ".join(summaries) + suffix
    error_lines = [line.strip() for line in output.splitlines() if line.strip().startswith("E   ")]
    if error_lines:
        return error_lines[0].replace("E   ", "", 1)[:240]
    return "pytest가 실패했지만 파일별 실패를 자동 요약하지 못했습니다. 상세 로그를 확인하세요."


def _pytest_resolution_hint(output: str, test_files: list[dict], returncode: int) -> str:
    if returncode == 0:
        return "배포 전 동일 테스트를 한 번 더 실행하고, 주요 화면을 수동으로 확인하세요."
    lowered = output.lower()
    if "template" in lowered or "jinja" in lowered or "templatenotfound" in lowered:
        return "Jinja 템플릿 이름, block 구조, include 경로, 전달 context 변수를 우선 확인하세요."
    if "builderror" in lowered or "url_for" in lowered:
        return "변경한 endpoint 이름과 url_for 인자, blueprint prefix가 일치하는지 확인하세요."
    if "assertionerror" in lowered:
        return "최근 UI 문구, 버튼 라벨, 상태 badge 텍스트 변경이 테스트 기대값과 맞는지 먼저 확인하세요."
    if "csrf" in lowered:
        return "POST form의 CSRF hidden input 또는 base submit hook이 유지되는지 확인하세요."
    if "sqlalchemy" in lowered or "operationalerror" in lowered or "integrityerror" in lowered:
        return "모델 필드, fixture 데이터, DB 초기화 순서, unique 제약 조건 충돌 여부를 확인하세요."
    if "modulenotfounderror" in lowered or "importerror" in lowered:
        return "새 dependency가 추가됐는지 확인하고, pyproject와 Dockerfile 설치 범위를 점검하세요."
    failed_rows = [row for row in test_files if row.get("status") == "FAIL"]
    if failed_rows:
        return failed_rows[0].get("hint") or "실패 파일의 대상 기능과 관련 route/form 필드를 우선 확인하세요."
    return "상세 pytest output의 FAILURES 또는 ERRORS 섹션에서 첫 번째 실패부터 확인하세요."


def _default_test_hint(path: str, target: str, checks: str) -> str:
    if "admin" in path:
        return "관리자 권한, section query string, form action, audit log 기록 여부를 확인하세요."
    if "api_keys" in path:
        return "Provider 선택, API Key 암호화/마스킹, 연결 테스트 fallback, 원문 노출 여부를 확인하세요."
    if "auth" in path or "oauth" in path:
        return "로그인 상태, 승인/정지 정책, redirect URL, OAuth fixture 값을 확인하세요."
    if "prompt" in path:
        return "Provider/model 선택, API Key 요구, rate limit, prompt 조립, 화면 문구 변경 여부를 확인하세요."
    if "reservation" in path:
        return "예약 시간 계산, resource_id, 충돌 조건, 상태 badge와 form 필드를 확인하세요."
    if "usage_logs" in path:
        return "예약 소유권, resource 선택, 로그 필터, 상세 접근 권한을 확인하세요."
    if "legal" in path:
        return "Footer 링크, Markdown 렌더링, raw HTML escape, 승인 대기 접근 정책을 확인하세요."
    return f"{target} 영역의 최근 route, template, fixture 변경을 확인하세요."

def _apply_pytest_line_status(statuses: dict[str, str], line: str) -> None:
    if not line:
        return

    verbose_match = re.match(r"^(tests/[^:\s]+\.py)::[^\s]+\s+(PASSED|FAILED|ERROR|SKIPPED|XFAIL|XPASS)\b", line)
    if verbose_match:
        path, status_text = verbose_match.groups()
        _merge_pytest_status(statuses, path, _normalize_pytest_status(status_text))
        return

    error_match = re.search(r"\bERROR\s+(tests/[^\s:]+\.py)", line)
    if error_match:
        _merge_pytest_status(statuses, error_match.group(1), "FAIL")
        return

    progress_match = re.match(r"^(tests/[^\s:]+\.py)\s+([.FfEeSsXx]+)", line)
    if progress_match:
        path, progress = progress_match.groups()
        if any(char in progress for char in "FfEe"):
            status = "FAIL"
        elif any(char in progress for char in "Ss"):
            status = "SKIP"
        elif any(char == "." for char in progress):
            status = "PASS"
        else:
            status = "NOT RUN"
        _merge_pytest_status(statuses, path, status)


def _normalize_pytest_status(status_text: str) -> str:
    if status_text in {"FAILED", "ERROR"}:
        return "FAIL"
    if status_text == "SKIPPED":
        return "SKIP"
    if status_text in {"PASSED", "XFAIL", "XPASS"}:
        return "PASS"
    return "NOT RUN"


def _merge_pytest_status(statuses: dict[str, str], path: str, status: str) -> None:
    if path not in statuses:
        return
    priority = {"NOT RUN": 0, "PASS": 1, "SKIP": 2, "FAIL": 3}
    if priority[status] > priority[statuses[path]]:
        statuses[path] = status


def _pytest_total_tests(summary: str) -> int | None:
    counts = [int(value) for value in re.findall(r"(\d+)\s+(?:passed|failed|errors?|skipped|xfailed|xpassed)", summary)]
    return sum(counts) if counts else None


def _pytest_duration(summary: str) -> str | None:
    match = re.search(r"\bin\s+([0-9.]+s)\b", summary)
    return match.group(1) if match else None


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
