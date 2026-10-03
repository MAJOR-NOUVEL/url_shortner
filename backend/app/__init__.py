import logging
import os

from flask import Flask, jsonify, send_from_directory

from app.celery_app import celery_app, init_celery
from app.config import config_by_name
from app.extensions import cors, db, jwt, limiter, migrate, redis_store, talisman
from app.routes import analytics_bp, auth_bp, health_bp, redirect_bp, urls_bp

logger = logging.getLogger("url_shortener")

def create_app(config_name: str = None) -> Flask:
    """
    Application factory for the URL shortener Flask application.
    Initializes database, migrations, Redis caching, rate limiting, and security headers.
    """
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "default")

    app = Flask(__name__, static_folder="static", static_url_path="/static")
    config_obj = config_by_name.get(config_name, config_by_name["default"])
    app.config.from_object(config_obj)

    # Logging configuration
    logging.basicConfig(
        level=logging.INFO if not app.config.get("DEBUG") else logging.DEBUG,
        format="[%(asctime)s] %(levelname)s in %(name)s: %(message)s"
    )

    # --- Initialize Extensions ---
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Configure CORS for API endpoints
    cors.init_app(
        app,
        resources={
            r"/api/*": {"origins": "*"},
            r"/health": {"origins": "*"},
            r"/*": {"origins": "*"}
        },
        supports_credentials=True
    )

    # Redis Client initialization
    redis_store.init_app(app)

    # Configure rate limiter storage URI from app config
    if not app.config.get("TESTING"):
        storage_uri = app.config.get("RATELIMIT_STORAGE_URI", "redis://localhost:6379/0")
        try:
            limiter.storage_uri = storage_uri
        except Exception:
            pass
        limiter.init_app(app)
    else:
        # In test mode, limiter is disabled
        limiter.enabled = False

    # Security Headers via Talisman (disable in test environment or if configured)
    if not app.config.get("TESTING") and os.getenv("DISABLE_TALISMAN") != "1":
        talisman.init_app(app, **app.config.get("TALISMAN_CONFIG", {}))

    # Initialize Celery with Flask context
    init_celery(app, celery_app)

    # --- Register Blueprints ---
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(urls_bp)
    app.register_blueprint(analytics_bp)

    # Dashboard Frontend Route
    @app.route("/", methods=["GET"])
    def index():
        static_dir = os.path.join(app.root_path, "static")
        index_file = os.path.join(static_dir, "index.html")
        if os.path.exists(index_file):
            return send_from_directory(static_dir, "index.html")
        return jsonify({
            "service": "BitRoot API",
            "version": "1.0.0",
            "docs": "/health"
        }), 200

    @app.route("/favicon.ico", methods=["GET"])
    def favicon():
        static_dir = os.path.join(app.root_path, "static")
        ico_file = os.path.join(static_dir, "favicon.ico")
        if os.path.exists(ico_file):
            return send_from_directory(static_dir, "favicon.ico", mimetype="image/vnd.microsoft.icon")
        return send_from_directory(static_dir, "logo-bitroot.png", mimetype="image/png")

    # Redirection blueprint registered last to prevent shadowing API routes
    app.register_blueprint(redirect_bp)

    # --- Error Handlers ---
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify({
            "error": "Rate limit exceeded",
            "message": f"Too many requests: {e.description}"
        }), 429

    @app.errorhandler(404)
    def not_found_handler(e):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_error_handler(e):
        logger.error("Internal Server Error: %s", e)
        return jsonify({"error": "Internal server error"}), 500

    # Auto-create tables in development / test SQLite environments
    if app.config.get("TESTING") or "sqlite" in str(app.config.get("SQLALCHEMY_DATABASE_URI", "")):
        with app.app_context():
            db.create_all()

    return app
