from datetime import datetime, timedelta, timezone

from app.extensions import db, redis_store
from app.models.url import URL
from app.utils.cache import get_cached_url


def test_redirect_lifecycle_and_redis_cache(client):
    # 1. Create link
    resp = client.post("/api/urls", json={
        "url": "https://fastapi.tiangolo.com"
    })
    data = resp.get_json()
    code = data["short_code"]

    # Verify cache pre-warmed
    cached = get_cached_url(code)
    assert cached is not None
    assert "https://fastapi.tiangolo.com" in cached

    # 2. First redirect
    redir_resp = client.get(f"/{code}", follow_redirects=False)
    assert redir_resp.status_code == 302
    assert redir_resp.headers["Location"] == "https://fastapi.tiangolo.com"

    # 3. Simulate cache miss by clearing Redis, test database fallback
    redis_store.client.flushall()
    assert get_cached_url(code) is None

    # Redirect on cache miss
    redir_miss = client.get(f"/{code}", follow_redirects=False)
    assert redir_miss.status_code == 302
    assert redir_miss.headers["Location"] == "https://fastapi.tiangolo.com"

    # Cache should be repopulated now
    assert get_cached_url(code) is not None

def test_redirect_404_for_unknown_code(client):
    resp = client.get("/nonexistent-slug-xyz", follow_redirects=False)
    assert resp.status_code == 404

def test_redirect_410_for_expired_link(client, app):
    with app.app_context():
        # Create an expired URL in DB
        expired_url = URL(
            short_code="expired-link",
            original_url="https://example.com",
            is_active=True,
            created_at=datetime.now(timezone.utc) - timedelta(days=2),
            expires_at=datetime.now(timezone.utc) - timedelta(days=1)
        )
        db.session.add(expired_url)
        db.session.commit()

    resp = client.get("/expired-link", follow_redirects=False)
    assert resp.status_code == 410
