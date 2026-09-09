import logging
import os
import sys

from flask import Flask, render_template
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

from config import config

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()


def create_app(config_name=None):
    """Application factory."""
    app = Flask(__name__)

    config_name = config_name or os.getenv("FLASK_CONFIG", "default")
    app.config.from_object(config[config_name])

    # Serverless platforms (e.g. Vercel) mount everything except /tmp
    # read-only, so creating the instance folder can fail there. It's only
    # needed for the default local SQLite path, so don't let it crash boot.
    
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    login_manager.login_view = "main.login"
    login_manager.login_message = "Please log in to access that page."
    login_manager.login_message_category = "info"

    from app.routes import main
    app.register_blueprint(main)

    register_error_handlers(app)
    configure_logging(app)

    @app.context_processor
    def inject_globals():
        from datetime import datetime, timezone

        return {"now_year": datetime.now(timezone.utc).year}

    return app


def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(403)
    def forbidden(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(500)
    def server_error(error):
        db.session.rollback()
        return render_template("errors/500.html"), 500


def configure_logging(app):
    if app.debug or app.testing:
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
    )
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)