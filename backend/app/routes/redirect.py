import json
from datetime import datetime, timezone

from flask import Blueprint, current_app, jsonify, redirect, request

from app.extensions import db, limiter
from app.models.click import ClickAnalytics
from app.models.url import URL
from app.tasks.click_logger import record_click_event
from app.utils.cache import delete_cached_url, get_cached_url, set_cached_url
from app.utils.security import hash_ip
from app.utils.user_agent import clean_referrer, extract_coarse_country, parse_user_agent

redirect_bp = Blueprint("redirect", __name__)

RESERVED_ROOT_PATHS = {
    "favicon.ico", "robots.txt", "static", "api", "health",
    "docs", "redoc", "openapi.json"
}

def _safe_dispatch_click(url_id, referrer, user_agent, client_ip, country):
    try:
        record_click_event.delay(
            url_id=url_id,
            referrer=referrer,
            user_agent=user_agent,
            client_ip=client_ip,
            country=country
        )
    except Exception as exc:
        current_app.logger.warning("Could not dispatch Celery click logging task: %s. Falling back to direct database log.", exc)
        try:
            salt = current_app.config.get("IP_SALT", "default-salt")
            anonymized_ip_hash = hash_ip(client_ip, salt)
            device, browser = parse_user_agent(user_agent)
            cleaned_ref = clean_referrer(referrer)
            click = ClickAnalytics(
                url_id=url_id,
                clicked_at=datetime.now(timezone.utc),
                referrer=cleaned_ref,
                device=device,
                browser=browser,
                country=country or "Unknown",
                ip_hash=anonymized_ip_hash
            )
            db.session.add(click)
            db.session.commit()
        except Exception as db_exc:
            db.session.rollback()
            current_app.logger.warning("Direct DB click logging fallback failed: %s", db_exc)

def resolve_short_code(short_code: str):
    """
    Core resolution routine for shortened links.
    Returns:
        tuple (target_url, error_dict, status_code)
        On success: (target_url, None, 200)
        On error:   (None, {"error": "..."}, status_code)
    """
    if short_code in RESERVED_ROOT_PATHS:
        return None, {"error": "Not found"}, 404

    referrer = request.headers.get("Referer", "Direct")
    user_agent = request.headers.get("User-Agent", "Unknown")
    client_ip = request.headers.get("X-Forwarded-For", request.remote_addr or "127.0.0.1").split(",")[0].strip()
    country = extract_coarse_country(dict(request.headers))

    # --- 1. Redis Cache Lookup ---
    cached_data = get_cached_url(short_code)
    if cached_data:
        try:
            payload = json.loads(cached_data)
            url_id = payload.get("id")
            original_url = payload.get("url")
            expires_at_str = payload.get("expires_at")

            # Check expiration if stored
            if expires_at_str:
                exp_dt = datetime.fromisoformat(expires_at_str)
                if exp_dt.tzinfo is None:
                    exp_dt = exp_dt.replace(tzinfo=timezone.utc)
                if datetime.now(timezone.utc) > exp_dt:
                    delete_cached_url(short_code)
                    return None, {"error": "This shortened link has expired."}, 410

            # Asynchronous click logging via Celery (non-blocking)
            if url_id:
                _safe_dispatch_click(url_id, referrer, user_agent, client_ip, country)

            return original_url, None, 200
        except Exception:
            # Fall back to database on corrupted cache entry
            pass

    # --- 2. Database Lookup on Cache Miss ---
    url = URL.query.filter_by(short_code=short_code, is_active=True).first()

    if not url:
        return None, {"error": "Short link not found."}, 404

    if url.is_expired:
        return None, {"error": "This shortened link has expired."}, 410

    # Calculate remaining TTL and populate Redis cache
    ttl_seconds = current_app.config.get("CACHE_DEFAULT_TIMEOUT", 86400)
    if url.expires_at:
        exp = url.expires_at
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)
        delta = (exp - datetime.now(timezone.utc)).total_seconds()
        ttl_seconds = max(1, int(delta))

    cached_payload = json.dumps({
        "id": url.id,
        "url": url.original_url,
        "expires_at": url.expires_at.isoformat() if url.expires_at else None
    })
    set_cached_url(short_code, cached_payload, ttl_seconds=ttl_seconds)

    # Asynchronous click logging
    _safe_dispatch_click(url.id, referrer, user_agent, client_ip, country)

    return url.original_url, None, 200

@redirect_bp.route("/<short_code>", methods=["GET"])
@limiter.exempt
def handle_redirect(short_code: str):
    """
    High-Throughput Redirect Controller:
    1. Checks Redis cache first (sub-millisecond resolution).
    2. Dispatches asynchronous Celery task for click logging.
    3. Returns immediate HTTP 302 Found redirect to target URL.
    4. Handles 404 for missing links, 410 for expired links.
    """
    original_url, err_data, status_code = resolve_short_code(short_code)
    if err_data:
        return jsonify(err_data), status_code
    return redirect(original_url, code=302)
