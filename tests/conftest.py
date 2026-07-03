import pytest

from app import create_app
from app.extensions import db


class TestConfig:
    SECRET_KEY = "test-secret"
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = False
    GEMINI_MODEL = "gemini-3.5-flash"
    GEMINI_MAX_INPUT_CHARS = 3000
    GEMINI_MAX_OUTPUT_TOKENS = 1200
    MAX_DAILY_AI_CALLS_PER_USER = 50
    GOOGLE_CLIENT_ID = "test-google-client"
    GOOGLE_CLIENT_SECRET = "test-google-secret"
    GOOGLE_REDIRECT_URI = "http://localhost/auth/google/callback"
    ALLOWED_GOOGLE_DOMAIN = ""
    ADMIN_EMAILS = ["admin@senedu.kr"]
    ASSISTANT_ADMIN_EMAILS = ["assistant@senedu.kr"]


@pytest.fixture()
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()
