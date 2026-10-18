import json
import os
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required, verify_jwt_in_request
from pydantic import ValidationError

from app.extensions import db, limiter
from app.models.url import URL
from app.routes.redirect import resolve_short_code
from app.schemas.url import CreateURLSchema
from app.utils.base62 import generate_random_base62
from app.utils.cache import delete_cached_url, set_cached_url

urls_bp = Blueprint("urls", __name__, url_prefix="/api/urls")

def get_effective_base_url() -> str:
    """
    Determines the best public domain for generated short links:
    1. Origin header sent by browser (e.g. Vercel frontend or custom domain)
    2. Referer header domain
    3. Explicitly configured BASE_URL (from env var)
    4. Fallback to request.host_url
    """
    origin = request.headers.get("Origin")
    if origin and origin.startswith(("http://", "https://")):
        return origin.rstrip("/")

    referer = request.headers.get("Referer")
    if referer and referer.startswith(("http://", "https://")):
        parsed = urlparse(referer)
        if parsed.scheme and parsed.netloc:
            return f"{parsed.scheme}://{parsed.netloc}".rstrip("/")

    configured = current_app.config.get("BASE_URL")
    if configured and configured.strip():
        if os.getenv("FLASK_ENV") == "production" and "localhost" in configured:
            return request.host_url.rstrip("/")
        return configured.rstrip("/")

    return request.host_url.rstrip("/")

@urls_bp.route("", methods=["POST"])
@limiter.limit("30 per minute")
def create_url():
    """
    Creates a shortened URL. Supports optional custom alias, expiration,
    and optional user authentication. Pre-warms Redis cache.
    """
    # Check if request has an optional authenticated user
    user_id = None
    try:
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
        if identity:
            user_id = int(identity)
    except Exception:
        pass

    data = request.get_json(silent=True) or {}
    try:
        validated = CreateURLSchema(**data)
    except ValidationError as e:
        formatted_errors = [{"field": ".".join(str(loc) for loc in err["loc"]), "message": err["msg"]} for err in e.errors()]
        return jsonify({"error": "Validation error", "details": formatted_errors}), 400

    target_code = ""
    is_custom = False

    # 1. Custom Alias handling
    if validated.custom_alias:
        existing = URL.query.filter_by(short_code=validated.custom_alias).first()
        if existing:
            return jsonify({"error": f"Alias '{validated.custom_alias}' is already taken."}), 409
        target_code = validated.custom_alias
        is_custom = True
    else:
        # 2. Collision-safe short code generation
        for _ in range(5):
            candidate = generate_random_base62(length=6)
            if not URL.query.filter_by(short_code=candidate).first():
                target_code = candidate
                break
        if not target_code:
            target_code = generate_random_base62(length=8)

    # 3. Calculate expiration timestamp
    expires_at = None
    ttl_seconds = current_app.config.get("CACHE_DEFAULT_TIMEOUT", 86400)

    if validated.expires_in_hours:
        expires_at = datetime.now(timezone.utc) + timedelta(hours=validated.expires_in_hours)
        ttl_seconds = validated.expires_in_hours * 3600
    elif validated.expires_at:
        exp = validated.expires_at
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)
        expires_at = exp
        delta = (exp - datetime.now(timezone.utc)).total_seconds()
        ttl_seconds = max(1, int(delta))

    # 4. Persist in database
    new_url = URL(
        short_code=target_code,
        original_url=validated.url,
        custom_alias=is_custom,
        user_id=user_id,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        expires_at=expires_at
    )
    db.session.add(new_url)
    db.session.commit()

    # 5. Pre-warm Redis cache with JSON payload for instant zero-DB redirects
    cached_payload = json.dumps({
        "id": new_url.id,
        "url": new_url.original_url,
        "expires_at": new_url.expires_at.isoformat() if new_url.expires_at else None
    })
    set_cached_url(target_code, cached_payload, ttl_seconds=ttl_seconds)

    base_url = get_effective_base_url()
    return jsonify(new_url.to_dict(base_url=base_url)), 201

@urls_bp.route("", methods=["GET"])
@jwt_required()
def list_my_urls():
    """Returns list of links created by authenticated user."""
    user_id = int(get_jwt_identity())
    base_url = get_effective_base_url()

    urls = (
        URL.query
        .filter_by(user_id=user_id, is_active=True)
        .order_by(URL.created_at.desc())
        .all()
    )

    return jsonify([u.to_dict(base_url=base_url) for u in urls]), 200

@urls_bp.route("/resolve/<short_code>", methods=["GET"])
@limiter.limit("120 per minute")
def resolve_short_url(short_code: str):
    """
    Public resolution API for client-side redirection (SPA).
    Returns JSON { "short_code": ..., "original_url": ... }
    """
    original_url, err_data, status_code = resolve_short_code(short_code)
    if err_data:
        return jsonify(err_data), status_code
    return jsonify({
        "short_code": short_code,
        "original_url": original_url
    }), 200

@urls_bp.route("/<int:url_id>", methods=["DELETE"])
@jwt_required()
def delete_url(url_id: int):
    """Deletes short link and purges it from Redis cache."""
    user_id = int(get_jwt_identity())
    url = URL.query.filter_by(id=url_id, user_id=user_id).first()

    if not url:
        return jsonify({"error": "Link not found or unauthorized."}), 404

    # Purge from Redis cache
    delete_cached_url(url.short_code)

    # Remove from Database
    db.session.delete(url)
    db.session.commit()

    return jsonify({"message": f"Link /{url.short_code} successfully removed."}), 200
