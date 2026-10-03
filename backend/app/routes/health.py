from flask import Blueprint, jsonify
from sqlalchemy import text

from app.extensions import db, redis_store
from app.utils.cache import get_cache_telemetry

health_bp = Blueprint("health", __name__)

@health_bp.route("/health", methods=["GET"])
def health_check():
    """Readiness probe checking PostgreSQL and Redis connectivity."""
    db_status = "connected"
    redis_status = "connected"

    engine_name = "PostgreSQL"
    # 1. Probe PostgreSQL / Database
    try:
        db.session.execute(text("SELECT 1"))
        db_status = "connected"
        if "sqlite" in str(db.engine.url):
            engine_name = "SQLite (Local Fallback)"
    except Exception as e:
        db_status = f"unhealthy ({e!s})"

    # 2. Probe Redis
    try:
        redis_store.client.ping()
    except Exception as e:
        redis_status = f"unhealthy ({e!s})"

    cache_telemetry = get_cache_telemetry()
    is_overall_healthy = ("unhealthy" not in db_status) and ("unhealthy" not in redis_status)

    return jsonify({
        "status": "healthy" if is_overall_healthy else "degraded",
        "database": db_status,
        "database_engine": engine_name,
        "redis": redis_status,
        "cache": cache_telemetry
    }), 200 if is_overall_healthy else 503
