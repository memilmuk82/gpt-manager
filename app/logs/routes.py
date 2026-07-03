from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.logs import logs_bp
from app.models import AiResource, Reservation, UsageLog


@logs_bp.get("")
@login_required
def index():
    logs = (
        UsageLog.query.filter_by(user_id=current_user.id)
        .order_by(UsageLog.created_at.desc())
        .all()
    )
    return render_template("logs/index.html", logs=logs)


@logs_bp.get("/new")
@login_required
def new():
    return render_template("logs/new.html", **_form_options())


@logs_bp.post("")
@login_required
def create():
    work_type = request.form.get("work_type", "").strip()
    summary = request.form.get("summary", "").strip()
    prompt_text = request.form.get("prompt_text", "").strip() or None
    result_note = request.form.get("result_note", "").strip() or None
    reservation_id = request.form.get("reservation_id", type=int)
    resource_id = request.form.get("resource_id", type=int)

    reservation = None
    if reservation_id:
        reservation = Reservation.query.filter_by(
            id=reservation_id,
            user_id=current_user.id,
        ).first()
        if reservation is None:
            flash("연결할 예약을 확인하세요.", "error")
            return render_template("logs/new.html", **_form_options()), 400
        resource_id = reservation.resource_id

    resource = db.session.get(AiResource, resource_id) if resource_id else None
    if not work_type or not summary:
        flash("작업 유형과 요약을 입력하세요.", "error")
        return render_template("logs/new.html", **_form_options()), 400
    if resource_id and resource is None:
        flash("AI 리소스를 확인하세요.", "error")
        return render_template("logs/new.html", **_form_options()), 400
    if reservation is None and resource is None:
        flash("예약 또는 AI 리소스를 선택하세요.", "error")
        return render_template("logs/new.html", **_form_options()), 400

    usage_log = UsageLog(
        user_id=current_user.id,
        reservation_id=reservation.id if reservation else None,
        resource_id=resource.id if resource else None,
        work_type=work_type,
        summary=summary,
        prompt_text=prompt_text,
        result_note=result_note,
    )
    db.session.add(usage_log)
    db.session.commit()

    flash("사용 로그가 저장되었습니다.", "success")
    return redirect(url_for("logs.show", log_id=usage_log.id))


@logs_bp.get("/<int:log_id>")
@login_required
def show(log_id: int):
    usage_log = UsageLog.query.filter_by(id=log_id, user_id=current_user.id).first_or_404()
    return render_template("logs/show.html", usage_log=usage_log)


def _form_options() -> dict:
    selected_reservation_id = request.args.get("reservation_id", type=int)
    reservations = (
        Reservation.query.filter_by(user_id=current_user.id)
        .order_by(Reservation.start_at.desc())
        .all()
    )
    resources = AiResource.query.filter_by(is_active=True).order_by(AiResource.name.asc()).all()
    return {
        "reservations": reservations,
        "resources": resources,
        "selected_reservation_id": selected_reservation_id,
    }
