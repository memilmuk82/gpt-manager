from pathlib import Path

from flask import Flask

from app.auth import auth_bp
from app.config import Config
from app.extensions import db, login_manager
from app.routes.main import main_bp


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

    with app.app_context():
        db.create_all()

    return app
