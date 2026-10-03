import logging

from app.extensions import redis_store

logger = logging.getLogger("url_shortener.cache")

CACHE_PREFIX = "url:"
CACHE_STATS_HITS = "cache_stats:hits"
CACHE_STATS_MISSES = "cache_stats:misses"

def get_cached_url(short_code: str) -> str | None:
    """
    Retrieves original URL from Redis cache.
    Returns None on cache miss or Redis failure.
    """
    try:
        client = redis_store.client
        key = f"{CACHE_PREFIX}{short_code}"
        cached = client.get(key)
        if cached:
            client.incr(CACHE_STATS_HITS)
            return cached
        else:
            client.incr(CACHE_STATS_MISSES)
            return None
    except Exception as e:
        logger.error("Redis cache get error for code '%s': %s", short_code, e)
        return None

def set_cached_url(short_code: str, original_url: str, ttl_seconds: int = 86400) -> bool:
    """Stores URL in Redis cache with an expiration TTL (default 24h)."""
    try:
        client = redis_store.client
        key = f"{CACHE_PREFIX}{short_code}"
        client.set(key, original_url, ex=ttl_seconds)
        return True
    except Exception as e:
        logger.error("Redis cache set error for code '%s': %s", short_code, e)
        return False

def delete_cached_url(short_code: str) -> bool:
    """Invalidates and deletes a short code from Redis cache."""
    try:
        client = redis_store.client
        key = f"{CACHE_PREFIX}{short_code}"
        client.delete(key)
        return True
    except Exception as e:
        logger.error("Redis cache delete error for code '%s': %s", short_code, e)
        return False

def get_cache_telemetry() -> dict:
    """Returns real-time cache performance and latency telemetry."""
    try:
        client = redis_store.client
        hits = int(client.get(CACHE_STATS_HITS) or 0)
        misses = int(client.get(CACHE_STATS_MISSES) or 0)
        total = hits + misses
        hit_ratio = round((hits / total) * 100, 1) if total > 0 else 100.0

        keys = client.keys(f"{CACHE_PREFIX}*")
        cached_count = len(keys)

        return {
            "status": "healthy",
            "is_fallback": redis_store.is_fallback,
            "engine": "In-Memory FakeRedis" if redis_store.is_fallback else "Native Redis",
            "cached_keys_count": cached_count,
            "hits": hits,
            "misses": misses,
            "hit_ratio_percent": hit_ratio
        }
    except Exception as e:
        return {
            "status": "degraded",
            "is_fallback": True,
            "error": str(e),
            "hits": 0,
            "misses": 0,
            "hit_ratio_percent": 0.0
        }
