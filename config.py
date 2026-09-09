"""
Application configuration.

Configuration is selected via the FLASK_CONFIG environment variable and
read from the environment (see .env.example). Never commit real secrets —
the defaults below are only safe for local development.
"""
import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base config with sane, secure-by-default settings."""

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-this")

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "sqlite:///" + os.path.join(basedir, "instance", "jobhunter.db")
    )
    # Some hosts hand out postgres:// URLs, which SQLAlchemy 1.4+/2.x
    # no longer accepts directly — normalize to postgresql://.
    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace(
            "postgres://", "postgresql://", 1
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Sessions / cookies
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # CSRF (Flask-WTF)
    WTF_CSRF_ENABLED = True

    APPLICATIONS_PER_PAGE = 10


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False  # simplifies posting forms directly in tests
    SECRET_KEY = "test-secret"


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
