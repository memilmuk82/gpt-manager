from app.config import BASE_DIR, normalize_database_url


def test_relative_sqlite_database_url_is_rooted_at_project_instance_dir():
    database_url = normalize_database_url("sqlite:///instance/app.db")

    assert database_url == f"sqlite:///{BASE_DIR / 'instance' / 'app.db'}"


def test_memory_sqlite_database_url_is_unchanged():
    assert normalize_database_url("sqlite:///:memory:") == "sqlite:///:memory:"


def test_legacy_sqlite_user_table_gets_phase6_columns(tmp_path):
    import sqlite3

    from app import create_app

    db_path = tmp_path / "legacy.db"
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        CREATE TABLE user (
            id INTEGER NOT NULL PRIMARY KEY,
            email VARCHAR(255) NOT NULL UNIQUE,
            name VARCHAR(120) NOT NULL,
            password_hash VARCHAR(255),
            role VARCHAR(20) NOT NULL,
            google_sub VARCHAR(255),
            is_active BOOLEAN NOT NULL,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()

    class LegacyConfig:
        SECRET_KEY = "test"
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{db_path}"
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        SESSION_COOKIE_HTTPONLY = True
        SESSION_COOKIE_SAMESITE = "Lax"
        SESSION_COOKIE_SECURE = False
        APP_ENCRYPTION_KEY = ""
        GOOGLE_CLIENT_ID = ""
        GOOGLE_CLIENT_SECRET = ""
        GOOGLE_REDIRECT_URI = "http://localhost:5000/auth/google/callback"
        ALLOWED_GOOGLE_DOMAIN = ""
        ADMIN_EMAILS = []
        GEMINI_MODEL = "gemini-3.1-flash-lite"
        GEMINI_MAX_INPUT_CHARS = 3000
        GEMINI_MAX_OUTPUT_TOKENS = 1200
        MAX_DAILY_AI_CALLS_PER_USER = 50

    create_app(LegacyConfig)

    conn = sqlite3.connect(db_path)
    columns = {row[1] for row in conn.execute("PRAGMA table_info(user)")}
    conn.close()

    assert "auth_provider" in columns
    assert "approval_status" in columns
