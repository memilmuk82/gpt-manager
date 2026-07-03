import calendar as calendar_lib
from collections import defaultdict
from datetime import date, datetime, time

from flask import flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_

from app.defaults import DEFAULT_WORK_TYPES
from app.extensions import db
from app.models import AiResource, AppSetting, Reservation, ReservationStatus, WorkType
from app.reservations import reservations_bp
from app.services.reservation_service import (
    ReservationValidationError,
    find_reservation_conflict,
    parse_datetime_local,
    validate_reservation_request,
)


@reservations_bp.get("")
@login_required
def index():
    filters = {
        "q": request.args.get("q", "").strip(),
        "status": request.args.get("status", "").strip(),
    }
    query = Reservation.query.filter_by(user_id=current_user.id)
    if filters["q"]:
        like = f"%{filters['q']}%"
        query = query.filter(
            or_(
                Reservation.purpose.ilike(like),
                Reservation.work_type.ilike(like),
                Reservation.description.ilike(like),
            )
        )
    if filters["status"] in {ReservationStatus.RESERVED, ReservationStatus.COMPLETED, ReservationStatus.CANCELLED}:
        query = query.filter(Reservation.status == filters["status"])
    reservations = query.order_by(Reservation.start_at.desc()).all()
    return render_template("reservations/index.html", reservations=reservations, filters=filters)


@reservations_bp.get("/calendar")
@login_required
def calendar():
    selected_month = _selected_month(request.args.get("month", ""))
    month_start = datetime.combine(selected_month, time.min)
    last_day = calendar_lib.monthrange(selected_month.year, selected_month.month)[1]
    month_end = datetime.combine(date(selected_month.year, selected_month.month, last_day), time.max)
    reservations = (
        Reservation.query.filter(
            Reservation.status != ReservationStatus.CANCELLED,
            Reservation.start_at >= month_start,
            Reservation.start_at <= month_end,
        )
        .order_by(Reservation.start_at.asc(), Reservation.end_at.asc())
        .all()
    )
    reservations_by_date = defaultdict(list)
    for reservation in reservations:
        reservations_by_date[reservation.start_at.date()].append(reservation)
    weeks = calendar_lib.Calendar(firstweekday=6).monthdatescalendar(selected_month.year, selected_month.month)
    previous_month = _shift_month(selected_month, -1)
    next_month = _shift_month(selected_month, 1)
    return render_template(
        "reservations/calendar.html",
        selected_month=selected_month,
        previous_month=previous_month,
        next_month=next_month,
        weeks=weeks,
        reservations_by_date=reservations_by_date,
    )


@reservations_bp.get("/today")
@login_required
def today():
    selected_date = _selected_date(request.args.get("date", ""))
    day_start = datetime.combine(selected_date, time.min)
    day_end = datetime.combine(selected_date, time.max)
    reservations = (
        Reservation.query.filter(
            Reservation.status != ReservationStatus.CANCELLED,
            Reservation.start_at >= day_start,
            Reservation.start_at <= day_end,
        )
        .order_by(Reservation.start_at.asc(), Reservation.end_at.asc())
        .all()
    )
    return render_template(
        "reservations/today.html",
        reservations=reservations,
        selected_date=selected_date,
    )


@reservations_bp.get("/new")
@login_required
def new():
    return render_template(
        "reservations/new.html",
        resources=_active_resources(),
        work_types=_active_work_types(),
        default_duration=_setting_int("default_duration_minutes", 60),
        max_duration=_setting_int("max_duration_minutes", 180),
        usage_policy_version=_setting_value("usage_policy_version", "2026-07-04"),
    )


@reservations_bp.get("/conflicts")
@login_required
def conflicts():
    resource_id = request.args.get("resource_id", type=int)
    try:
        start_at = parse_datetime_local(request.args.get("start_at", ""))
        end_at = parse_datetime_local(request.args.get("end_at", ""))
        if not resource_id:
            raise ReservationValidationError("AI 리소스를 선택하세요.")
        conflict = find_reservation_conflict(resource_id, start_at, end_at)
    except ReservationValidationError as exc:
        return jsonify(ok=False, message=str(exc)), 400

    if conflict:
        return jsonify(
            ok=False,
            has_conflict=True,
            message=f"동시간대 예약이 있습니다: {conflict.user.name} / {conflict.start_at.strftime('%m-%d %H:%M')} ~ {conflict.end_at.strftime('%m-%d %H:%M')}",
        )
    return jsonify(ok=True, has_conflict=False, message="동시간대 예약이 없습니다.")


@reservations_bp.post("")
@login_required
def create():
    resource_id = request.form.get("resource_id", type=int)
    purpose = request.form.get("purpose", "").strip()
    work_type = request.form.get("work_type", "").strip()
    description = request.form.get("description", "").strip()
    safety_confirmed = request.form.get("safety_confirmed") == "on"

    try:
        start_at = parse_datetime_local(request.form.get("start_at", ""))
        end_at = parse_datetime_local(request.form.get("end_at", ""))
        resource = db.session.get(AiResource, resource_id) if resource_id else None
        if not work_type:
            raise ReservationValidationError("작업 유형을 선택하세요.")
        if not purpose:
            raise ReservationValidationError("작업명을 입력하세요.")
        if not safety_confirmed:
            raise ReservationValidationError("사용 전 확인 항목을 확인하세요.")
        validate_reservation_request(resource, start_at, end_at)
    except ReservationValidationError as exc:
        flash(str(exc), "error")
        return render_template(
            "reservations/new.html",
            resources=_active_resources(),
            work_types=_active_work_types(),
            default_duration=_setting_int("default_duration_minutes", 60),
            max_duration=_setting_int("max_duration_minutes", 180),
            usage_policy_version=_setting_value("usage_policy_version", "2026-07-04"),
        ), 400

    reservation = Reservation(
        user_id=current_user.id,
        resource_id=resource.id,
        start_at=start_at,
        end_at=end_at,
        work_type=work_type,
        purpose=purpose,
        description=description,
        safety_confirmed=safety_confirmed,
        consent_version=_setting_value("usage_policy_version", "2026-07-04"),
    )
    db.session.add(reservation)
    db.session.commit()

    flash("예약이 생성되었습니다.", "success")
    return redirect(url_for("reservations.index"))


@reservations_bp.post("/<int:reservation_id>/cancel")
@login_required
def cancel(reservation_id: int):
    reservation = _get_owned_reservation(reservation_id)
    if reservation.status == ReservationStatus.CANCELLED:
        flash("이미 취소된 예약입니다.", "warning")
        return redirect(url_for("reservations.index"))

    reservation.status = ReservationStatus.CANCELLED
    db.session.commit()
    flash("예약이 취소되었습니다.", "success")
    return redirect(url_for("reservations.index"))


@reservations_bp.post("/<int:reservation_id>/complete")
@login_required
def complete(reservation_id: int):
    reservation = _get_owned_reservation(reservation_id)
    if reservation.status == ReservationStatus.CANCELLED:
        flash("취소된 예약은 완료 처리할 수 없습니다.", "error")
        return redirect(url_for("reservations.index"))

    reservation.status = ReservationStatus.COMPLETED
    db.session.commit()
    flash("예약을 완료 처리했습니다.", "success")
    return redirect(url_for("reservations.index"))


def _get_owned_reservation(reservation_id: int) -> Reservation:
    return Reservation.query.filter_by(id=reservation_id, user_id=current_user.id).first_or_404()


def _selected_month(raw_value: str) -> date:
    if not raw_value:
        today = date.today()
        return date(today.year, today.month, 1)
    try:
        year, month = [int(part) for part in raw_value.split("-", 1)]
        return date(year, month, 1)
    except (TypeError, ValueError):
        flash("월 형식이 올바르지 않아 이번 달 예약을 표시합니다.", "warning")
        today = date.today()
        return date(today.year, today.month, 1)


def _shift_month(value: date, delta: int) -> date:
    month_index = value.year * 12 + value.month - 1 + delta
    return date(month_index // 12, month_index % 12 + 1, 1)


def _selected_date(raw_value: str) -> date:
    if not raw_value:
        return date.today()
    try:
        return date.fromisoformat(raw_value)
    except ValueError:
        flash("날짜 형식이 올바르지 않아 오늘 예약을 표시합니다.", "warning")
        return date.today()


def _active_resources():
    return AiResource.query.filter_by(is_active=True).order_by(AiResource.name.asc()).all()


def _active_work_types() -> list[str]:
    work_types = (
        WorkType.query.filter_by(is_active=True)
        .order_by(WorkType.sort_order.asc(), WorkType.name.asc())
        .all()
    )
    return [work_type.name for work_type in work_types] or DEFAULT_WORK_TYPES


def _setting_value(key: str, default: str) -> str:
    setting = db.session.get(AppSetting, key)
    return setting.value if setting is not None else default


def _setting_int(key: str, default: int) -> int:
    setting = db.session.get(AppSetting, key)
    if setting is None:
        return default
    try:
        return int(setting.value)
    except ValueError:
        return default
