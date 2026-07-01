from flask import current_app

from app.models import ApprovalStatus


def normalize_email(email: str) -> str:
    return email.strip().lower()


def email_domain(email: str) -> str:
    normalized = normalize_email(email)
    if "@" not in normalized:
        return ""
    return normalized.rsplit("@", 1)[1]


def is_trusted_email(email: str) -> bool:
    allowed_domain = current_app.config.get("ALLOWED_GOOGLE_DOMAIN", "").strip().lower()
    return bool(allowed_domain) and email_domain(email) == allowed_domain


def is_admin_email(email: str) -> bool:
    return normalize_email(email) in current_app.config.get("ADMIN_EMAILS", [])


def initial_approval_status(email: str) -> str:
    if is_trusted_email(email) or is_admin_email(email):
        return ApprovalStatus.APPROVED
    return ApprovalStatus.PENDING


def initial_role(email: str) -> str:
    return "admin" if is_admin_email(email) else "user"
