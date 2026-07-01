from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db, login_manager


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)
    role = db.Column(db.String(20), nullable=False, default="user")
    google_sub = db.Column(db.String(255), unique=True, nullable=True)
    auth_provider = db.Column(db.String(40), nullable=False, default="local")
    approval_status = db.Column(db.String(20), nullable=False, default="approved", index=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    @property
    def is_approved(self) -> bool:
        return self.approval_status == ApprovalStatus.APPROVED

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)


class ApprovalStatus:
    PENDING = "pending"
    APPROVED = "approved"
    SUSPENDED = "suspended"


class ReservationStatus:
    RESERVED = "reserved"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class AiResource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    provider = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    reservations = db.relationship("Reservation", back_populates="resource")


class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    resource_id = db.Column(db.Integer, db.ForeignKey("ai_resource.id"), nullable=False, index=True)
    start_at = db.Column(db.DateTime, nullable=False, index=True)
    end_at = db.Column(db.DateTime, nullable=False, index=True)
    purpose = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), nullable=False, default=ReservationStatus.RESERVED, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user = db.relationship("User", backref=db.backref("reservations", lazy="dynamic"))
    resource = db.relationship("AiResource", back_populates="reservations")


class UsageLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    reservation_id = db.Column(db.Integer, db.ForeignKey("reservation.id"), nullable=True, index=True)
    resource_id = db.Column(db.Integer, db.ForeignKey("ai_resource.id"), nullable=True, index=True)
    work_type = db.Column(db.String(120), nullable=False)
    summary = db.Column(db.Text, nullable=False)
    prompt_text = db.Column(db.Text, nullable=True)
    result_note = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user = db.relationship("User", backref=db.backref("usage_logs", lazy="dynamic"))
    reservation = db.relationship("Reservation", backref=db.backref("usage_logs", lazy="dynamic"))
    resource = db.relationship("AiResource", backref=db.backref("usage_logs", lazy="dynamic"))


class UserApiKey(db.Model):
    __table_args__ = (db.UniqueConstraint("user_id", "provider", name="uq_user_api_key_user_provider"),)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    provider = db.Column(db.String(80), nullable=False, default="gemini", index=True)
    encrypted_api_key = db.Column(db.Text, nullable=False)
    key_last4 = db.Column(db.String(4), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user = db.relationship("User", backref=db.backref("api_keys", lazy="dynamic"))


class PromptReview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    source_prompt = db.Column(db.Text, nullable=False)
    review_goal = db.Column(db.String(255), nullable=False)
    assembled_prompt = db.Column(db.Text, nullable=False)
    review_result = db.Column(db.Text, nullable=False)
    model_name = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user = db.relationship("User", backref=db.backref("prompt_reviews", lazy="dynamic"))


@login_manager.user_loader
def load_user(user_id: str) -> User | None:
    if not user_id.isdigit():
        return None
    return db.session.get(User, int(user_id))
