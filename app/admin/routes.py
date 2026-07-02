from functools import wraps

from flask import abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.admin import admin_bp
from app.extensions import db
from app.models import ApprovalStatus, PromptReview, Reservation, UsageLog, User


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
    stats = {
        "users": User.query.count(),
        "pending_users": User.query.filter_by(approval_status=ApprovalStatus.PENDING).count(),
        "reservations": Reservation.query.count(),
        "usage_logs": UsageLog.query.count(),
        "prompt_reviews": PromptReview.query.count(),
    }
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
    recent_reservations = Reservation.query.order_by(Reservation.created_at.desc()).limit(10).all()
    recent_logs = UsageLog.query.order_by(UsageLog.created_at.desc()).limit(10).all()
    recent_reviews = PromptReview.query.order_by(PromptReview.created_at.desc()).limit(10).all()
    return render_template(
        "admin/dashboard.html",
        stats=stats,
        recent_users=recent_users,
        recent_reservations=recent_reservations,
        recent_logs=recent_logs,
        recent_reviews=recent_reviews,
    )


@admin_bp.get("/users")
@admin_required
def users():
    users = User.query.order_by(User.approval_status.asc(), User.created_at.desc()).all()
    return render_template("admin/users.html", users=users)


@admin_bp.post("/users/<int:user_id>/approve")
@admin_required
def approve_user(user_id: int):
    user = db.session.get(User, user_id) or abort(404)
    user.approval_status = ApprovalStatus.APPROVED
    user.is_active = True
    db.session.commit()
    flash(f"{user.email} 계정을 승인했습니다.", "success")
    return redirect(url_for("admin.users"))


@admin_bp.post("/users/<int:user_id>/suspend")
@admin_required
def suspend_user(user_id: int):
    user = db.session.get(User, user_id) or abort(404)
    if user.id == current_user.id:
        flash("자기 자신의 계정은 정지할 수 없습니다.", "error")
        return redirect(url_for("admin.users"))

    user.approval_status = ApprovalStatus.SUSPENDED
    db.session.commit()
    flash(f"{user.email} 계정을 정지했습니다.", "success")
    return redirect(url_for("admin.users"))
