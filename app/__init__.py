import secrets
from pathlib import Path

from sqlalchemy import inspect, text

from flask import Flask, abort, flash, redirect, request, session, url_for
from flask_login import current_user, logout_user

from app.admin import admin_bp
from app.auth import auth_bp
from app.config import Config
from app.defaults import DEFAULT_GUIDES, DEFAULT_SETTINGS, DEFAULT_WORK_TYPES
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

    @app.context_processor
    def inject_app_settings():
        def setting_value(key: str, default: str = "") -> str:
            from app.models import AppSetting

            setting = db.session.get(AppSetting, key)
            return setting.value if setting else default

        def auth_manager_users(limit: int = 2):
            from app.models import ApprovalStatus, User

            return (
                User.query.filter_by(
                    is_auth_manager=True,
                    is_active=True,
                    approval_status=ApprovalStatus.APPROVED,
                )
                .order_by(User.sort_order.asc(), User.name.asc())
                .limit(limit)
                .all()
            )

        def csrf_token() -> str:
            token = session.get("_csrf_token")
            if not token:
                token = secrets.token_urlsafe(32)
                session["_csrf_token"] = token
            return token

        return {
            "setting_value": setting_value,
            "auth_manager_users": auth_manager_users,
            "csrf_token": csrf_token,
        }

    @app.before_request
    def enforce_csrf_token():
        if not app.config.get("WTF_CSRF_ENABLED", True):
            return None
        if request.method not in {"POST", "PUT", "PATCH", "DELETE"}:
            return None
        expected_token = session.get("_csrf_token")
        submitted_token = (
            request.form.get("csrf_token")
            or request.headers.get("X-CSRFToken")
            or request.headers.get("X-CSRF-Token")
        )
        if not expected_token or not submitted_token or not secrets.compare_digest(expected_token, submitted_token):
            abort(400)
        return None

    @app.before_request
    def enforce_user_approval():
        allowed_endpoints = {
            "static",
            "main.index",
            "main.healthz",
            "main.terms",
            "main.privacy",
            "main.guide",
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
        _seed_default_records(app)

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
    if "department" not in user_columns:
        migrations.append("ALTER TABLE user ADD COLUMN department VARCHAR(120) NOT NULL DEFAULT ''")
    if "extension" not in user_columns:
        migrations.append("ALTER TABLE user ADD COLUMN extension VARCHAR(40) NOT NULL DEFAULT ''")
    if "is_auth_manager" not in user_columns:
        migrations.append("ALTER TABLE user ADD COLUMN is_auth_manager BOOLEAN NOT NULL DEFAULT 0")
    if "sort_order" not in user_columns:
        migrations.append("ALTER TABLE user ADD COLUMN sort_order INTEGER NOT NULL DEFAULT 100")

    table_names = inspector.get_table_names()
    if "reservation" in table_names:
        reservation_columns = {column["name"] for column in inspector.get_columns("reservation")}
        if "work_type" not in reservation_columns:
            migrations.append("ALTER TABLE reservation ADD COLUMN work_type VARCHAR(120) NOT NULL DEFAULT ''")
        if "description" not in reservation_columns:
            migrations.append("ALTER TABLE reservation ADD COLUMN description TEXT NOT NULL DEFAULT ''")
        if "safety_confirmed" not in reservation_columns:
            migrations.append("ALTER TABLE reservation ADD COLUMN safety_confirmed BOOLEAN NOT NULL DEFAULT 0")

    for statement in migrations:
        db.session.execute(text(statement))
    if migrations:
        db.session.commit()


def _seed_default_records(app: Flask) -> None:
    if app.config.get("TESTING"):
        return

    from app.models import AiResource, AppSetting, GuideItem, User, WorkType

    changed = False
    for key, value, label, help_text, sort_order in DEFAULT_SETTINGS:
        if db.session.get(AppSetting, key) is None:
            db.session.add(
                AppSetting(
                    key=key,
                    value=value,
                    label=label,
                    help_text=help_text,
                    sort_order=sort_order,
                )
            )
            changed = True

    for code, category, title, body, sort_order, is_active in DEFAULT_GUIDES:
        if GuideItem.query.filter_by(code=code).first() is None:
            db.session.add(
                GuideItem(
                    code=code,
                    category=category,
                    title=title,
                    body=body,
                    sort_order=sort_order,
                    is_active=is_active,
                )
            )
            changed = True

    for index, name in enumerate(DEFAULT_WORK_TYPES, start=1):
        if WorkType.query.filter_by(name=name).first() is None:
            db.session.add(WorkType(name=name, sort_order=index * 10, is_active=True))
            changed = True

    if AiResource.query.filter_by(name="학교 공용 GPT Pro 5X 계정").first() is None:
        db.session.add(
            AiResource(
                name="학교 공용 GPT Pro 5X 계정",
                provider="OpenAI",
                description="부서 공용 ChatGPT Pro 5X 계정",
            )
        )
        changed = True

    review_email = app.config.get("REVIEW_ADMIN_EMAIL", "review.admin@senedu.kr").strip().lower()
    review_password = app.config.get("REVIEW_ADMIN_PASSWORD", "")
    if (
        app.config.get("ENABLE_REVIEW_ADMIN", False)
        and review_email
        and review_password
        and User.query.filter_by(email=review_email).first() is None
    ):
        user = User(
            email=review_email,
            name="리뷰용 관리자 계정",
            department="시스템",
            role="admin",
            approval_status="approved",
            is_active=True,
            is_auth_manager=True,
            sort_order=2,
        )
        user.set_password(review_password)
        db.session.add(user)
        changed = True

    if changed:
        db.session.commit()
