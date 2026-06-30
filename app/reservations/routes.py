from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models import AiResource, Reservation, ReservationStatus
from app.reservations import reservations_bp
from app.services.reservation_service import (
    ReservationValidationError,
    parse_datetime_local,
    validate_reservation_request,
)


@reservations_bp.get("")
@login_required
def index():
    reservations = (
        Reservation.query.filter_by(user_id=current_user.id)
        .order_by(Reservation.start_at.desc())
        .all()
    )
    return render_template("reservations/index.html", reservations=reservations)


@reservations_bp.get("/new")
@login_required
def new():
    resources = AiResource.query.filter_by(is_active=True).order_by(AiResource.name.asc()).all()
    return render_template("reservations/new.html", resources=resources)


@reservations_bp.post("")
@login_required
def create():
    resource_id = request.form.get("resource_id", type=int)
    purpose = request.form.get("purpose", "").strip()

    try:
        start_at = parse_datetime_local(request.form.get("start_at", ""))
        end_at = parse_datetime_local(request.form.get("end_at", ""))
        resource = db.session.get(AiResource, resource_id) if resource_id else None
        if not purpose:
            raise ReservationValidationError("예약 목적을 입력하세요.")
        validate_reservation_request(resource, start_at, end_at)
    except ReservationValidationError as exc:
        flash(str(exc), "error")
        resources = AiResource.query.filter_by(is_active=True).order_by(AiResource.name.asc()).all()
        return render_template("reservations/new.html", resources=resources), 400

    reservation = Reservation(
        user_id=current_user.id,
        resource_id=resource.id,
        start_at=start_at,
        end_at=end_at,
        purpose=purpose,
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
