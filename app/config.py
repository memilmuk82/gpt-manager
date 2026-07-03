import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DATABASE_PATH = BASE_DIR / "instance" / "app.db"


def normalize_database_url(database_url: str) -> str:
    if database_url == "sqlite:///:memory:":
        return database_url
    if database_url.startswith("sqlite:///") and not database_url.startswith("sqlite:////"):
        relative_path = database_url.removeprefix("sqlite:///")
        return f"sqlite:///{BASE_DIR / relative_path}"
    return database_url


class Config:
    APP_TITLE = os.getenv("APP_TITLE", "ChatGPT Pro 5X 공동 사용 지원 시스템")
    ORGANIZATION_NAME = os.getenv("ORGANIZATION_NAME", "종로산업정보학교")

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-change-me")
    SQLALCHEMY_DATABASE_URI = normalize_database_url(
        os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DATABASE_PATH}")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"
    WTF_CSRF_ENABLED = os.getenv("WTF_CSRF_ENABLED", "true").lower() == "true"

    APP_ENCRYPTION_KEY = os.getenv("APP_ENCRYPTION_KEY", "")
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI = os.getenv(
        "GOOGLE_REDIRECT_URI",
        "http://localhost:5000/auth/google/callback",
    )
    ALLOWED_GOOGLE_DOMAIN = os.getenv("ALLOWED_GOOGLE_DOMAIN", "")
    ADMIN_EMAILS = [email.strip().lower() for email in os.getenv("ADMIN_EMAILS", "").split(",") if email.strip()]
    ASSISTANT_ADMIN_EMAILS = [
        email.strip().lower()
        for email in os.getenv("ASSISTANT_ADMIN_EMAILS", "").split(",")
        if email.strip()
    ]
    ENABLE_REVIEW_ADMIN = os.getenv("ENABLE_REVIEW_ADMIN", "false").lower() == "true"
    REVIEW_ADMIN_EMAIL = os.getenv("REVIEW_ADMIN_EMAIL", "review.admin@senedu.kr")
    REVIEW_ADMIN_PASSWORD = os.getenv("REVIEW_ADMIN_PASSWORD", "ReviewAdmin!2026")

    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
    GEMINI_MAX_INPUT_CHARS = int(os.getenv("GEMINI_MAX_INPUT_CHARS", "3000"))
    GEMINI_MAX_OUTPUT_TOKENS = int(os.getenv("GEMINI_MAX_OUTPUT_TOKENS", "1200"))
    MAX_DAILY_AI_CALLS_PER_USER = int(os.getenv("MAX_DAILY_AI_CALLS_PER_USER", "50"))
