from datetime import datetime, time

from flask import Blueprint, jsonify, render_template
from flask_login import login_required

from app.models import Reservation, ReservationStatus
from app.services import legal_markdown_service


main_bp = Blueprint("main", __name__)


@main_bp.get("/")
def index():
    return render_template("index.html")


@main_bp.get("/dashboard")
@login_required
def dashboard():
    now = datetime.now()
    today_start = datetime.combine(now.date(), time.min)
    today_end = datetime.combine(now.date(), time.max)

    current_reservation = (
        Reservation.query.filter(
            Reservation.status == ReservationStatus.RESERVED,
            Reservation.start_at <= now,
            Reservation.end_at > now,
        )
        .order_by(Reservation.end_at.asc())
        .first()
    )
    next_reservation = (
        Reservation.query.filter(
            Reservation.status == ReservationStatus.RESERVED,
            Reservation.start_at > now,
        )
        .order_by(Reservation.start_at.asc())
        .first()
    )
    today_reservations = (
        Reservation.query.filter(
            Reservation.status != ReservationStatus.CANCELLED,
            Reservation.start_at >= today_start,
            Reservation.start_at <= today_end,
        )
        .order_by(Reservation.start_at.asc())
        .limit(8)
        .all()
    )

    return render_template(
        "dashboard.html",
        current_reservation=current_reservation,
        next_reservation=next_reservation,
        today_reservations=today_reservations,
    )


@main_bp.get("/guide")
@login_required
def guide():
    return render_template("guide.html")


@main_bp.get("/terms")
def terms():
    return render_template(
        "legal/document.html",
        title="이용약관",
        document_html=legal_markdown_service.render_legal_markdown("terms"),
    )


@main_bp.get("/privacy")
def privacy():
    return render_template(
        "legal/document.html",
        title="개인정보처리방침",
        document_html=legal_markdown_service.render_legal_markdown("privacy"),
    )


@main_bp.get("/healthz")
def healthz():
    return jsonify(status="ok")
