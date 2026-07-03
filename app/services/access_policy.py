from flask import current_app

from app.models import ApprovalStatus


def normalize_email(email: str) -> str:
    return email.strip().lower()


def is_admin_email(email: str) -> bool:
    return normalize_email(email) in current_app.config.get("ADMIN_EMAILS", [])


def is_assistant_admin_email(email: str) -> bool:
    return normalize_email(email) in current_app.config.get("ASSISTANT_ADMIN_EMAILS", [])


def initial_approval_status(email: str) -> str:
    return ApprovalStatus.APPROVED


def initial_role(email: str) -> str:
    if is_admin_email(email):
        return "admin"
    if is_assistant_admin_email(email):
        return "assistant_admin"
    return "user"
