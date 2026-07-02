from pathlib import Path

from sqlalchemy import inspect, text

from flask import Flask, flash, redirect, request, url_for
from flask_login import current_user, logout_user

from app.admin import admin_bp
from app.auth import auth_bp
from app.config import Config
from app.extensions import db, login_manager
from app.logs import logs_bp
from app.prompts import prompts_bp
from app.reservations import reservations_bp
from app.routes.main import main_bp
from app.settings import settings_bp


def create_app(config_object: type[Config] | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_object or Config)

    db_uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
    if db_uri.startswith("sqlite:///") and db_uri != "sqlite:///:memory:":
        Path(db_uri.removeprefix("sqlite:///")).parent.mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(logs_bp)
    app.register_blueprint(reservations_bp)
    app.register_blueprint(prompts_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(admin_bp)

    @app.before_request
    def enforce_user_approval():
        allowed_endpoints = {
            "static",
            "main.index",
            "main.healthz",
            "main.terms",
            "main.privacy",
            "auth.login",
            "auth.login_post",
            "auth.register",
            "auth.register_post",
            "auth.google_login",
            "auth.google_callback",
            "auth.pending",
            "auth.logout",
        }
        if not current_user.is_authenticated or request.endpoint in allowed_endpoints:
            return None
        if current_user.approval_status == "suspended":
            logout_user()
            flash("정지된 계정입니다. 관리자에게 문의하세요.", "error")
            return redirect(url_for("auth.login"))
        if not current_user.is_approved:
            return redirect(url_for("auth.pending"))
        return None

    with app.app_context():
        db.create_all()
        _ensure_sqlite_schema_compatibility(app)

    return app


def _ensure_sqlite_schema_compatibility(app: Flask) -> None:
    db_uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
    if not db_uri.startswith("sqlite:///"):
        return

    inspector = inspect(db.engine)
    if "user" not in inspector.get_table_names():
        return

    user_columns = {column["name"] for column in inspector.get_columns("user")}
    migrations = []
    if "auth_provider" not in user_columns:
        migrations.append("ALTER TABLE user ADD COLUMN auth_provider VARCHAR(40) NOT NULL DEFAULT 'local'")
    if "approval_status" not in user_columns:
        migrations.append("ALTER TABLE user ADD COLUMN approval_status VARCHAR(20) NOT NULL DEFAULT 'approved'")

    for statement in migrations:
        db.session.execute(text(statement))
    if migrations:
        db.session.commit()
