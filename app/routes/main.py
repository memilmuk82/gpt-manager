from datetime import datetime, time, timedelta

from flask import Blueprint, jsonify, render_template
from flask_login import current_user, login_required

from app.models import GuideItem, PromptReview, Reservation, ReservationStatus, UsageLog
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
    today_query = Reservation.query.filter(
        Reservation.status != ReservationStatus.CANCELLED,
        Reservation.start_at >= today_start,
        Reservation.start_at <= today_end,
    )
    today_reservations = today_query.order_by(Reservation.start_at.asc()).limit(8).all()
    month_start = datetime.combine(now.date().replace(day=1), time.min)
    missing_log_cutoff = now - timedelta(days=30)
    missing_log_reservations = [
        reservation
        for reservation in Reservation.query.filter(
            Reservation.user_id == current_user.id,
            Reservation.status == ReservationStatus.COMPLETED,
            Reservation.end_at >= missing_log_cutoff,
        ).order_by(Reservation.end_at.desc()).all()
        if reservation.usage_logs.count() == 0
    ]
    dashboard_stats = {
        "today_reservations": today_query.count(),
        "my_month_reservations": Reservation.query.filter(
            Reservation.user_id == current_user.id,
            Reservation.start_at >= month_start,
            Reservation.status != ReservationStatus.CANCELLED,
        ).count(),
        "my_month_logs": UsageLog.query.filter(
            UsageLog.user_id == current_user.id,
            UsageLog.created_at >= month_start,
        ).count(),
        "my_month_prompt_reviews": PromptReview.query.filter(
            PromptReview.user_id == current_user.id,
            PromptReview.created_at >= month_start,
        ).count(),
        "missing_logs": len(missing_log_reservations),
    }

    return render_template(
        "dashboard.html",
        current_reservation=current_reservation,
        next_reservation=next_reservation,
        today_reservations=today_reservations,
        missing_log_reservations=missing_log_reservations[:5],
        dashboard_stats=dashboard_stats,
    )


@main_bp.get("/guide")
@login_required
def guide():
    guides = GuideItem.query.filter_by(is_active=True).order_by(GuideItem.sort_order.asc()).all()
    return render_template("guide.html", guides=guides)


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
