import os
import socket
from datetime import timedelta


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-insecure-secret-key-change-me-32-bytes-minimum!!")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret-key-change-me-to-a-cryptographically-secure-64-byte-key!!")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Redis configuration
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    RATELIMIT_STORAGE_URI = os.getenv("RATELIMIT_STORAGE_URI", os.getenv("REDIS_URL", "redis://localhost:6379/0"))
    RATELIMIT_DEFAULT = "100/minute"
    RATELIMIT_STRATEGY = "moving-window"

    # Celery configuration
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", os.getenv("REDIS_URL", "redis://localhost:6379/0"))
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", os.getenv("REDIS_URL", "redis://localhost:6379/0"))

    BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")
    CACHE_DEFAULT_TIMEOUT = int(os.getenv("CACHE_DEFAULT_TIMEOUT", 86400))  # 24h
    IP_SALT = os.getenv("IP_SALT", "default-privacy-preserving-salt-change-in-prod")

    # Security: Talisman headers configuration
    TALISMAN_CONFIG = {
        "force_https": os.getenv("FLASK_ENV") == "production",
        "strict_transport_security": os.getenv("FLASK_ENV") == "production",
        "content_security_policy": {
            "default-src": "'self'",
            "script-src": ["'self'", "'unsafe-inline'", "https://cdn.tailwindcss.com", "https://unpkg.com", "https://cdnjs.cloudflare.com"],
            "style-src": ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"],
            "font-src": ["'self'", "https://fonts.gstatic.com"],
            "img-src": ["'self'", "data:", "https:"],
            "connect-src": ["'self'", "http:", "https:"]
        }
    }
def _get_dev_db_uri() -> str:
    env_uri = os.getenv("DATABASE_URL")
    if env_uri:
        return env_uri
    # Probe local Postgres on port 5432
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        is_open = sock.connect_ex(("localhost", 5432)) == 0
        sock.close()
        if is_open:
            return "postgresql://shortener_user:shortener_pass@localhost:5432/shortener_db"
    except Exception:
        pass
    # Seamless fallback to SQLite for local development when Postgres is not running
    return "sqlite:///shortener.db"

class DevelopmentConfig(BaseConfig):
    DEBUG = True
    ENV = "development"
    SQLALCHEMY_DATABASE_URI = _get_dev_db_uri()

class TestingConfig(BaseConfig):
    TESTING = True
    DEBUG = True
    ENV = "testing"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    RATELIMIT_ENABLED = False
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    CACHE_DEFAULT_TIMEOUT = 300

class ProductionConfig(BaseConfig):
    DEBUG = False
    ENV = "production"
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")

    @classmethod
    def validate_production_env(cls):
        required = ["SECRET_KEY", "JWT_SECRET_KEY", "DATABASE_URL", "REDIS_URL"]
        missing = [var for var in required if not os.getenv(var) or "change-me" in os.getenv(var, "")]
        if missing:
            raise ValueError(f"CRITICAL: Missing or insecure production environment variables: {', '.join(missing)}")

config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}
