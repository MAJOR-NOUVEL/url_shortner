import logging

import fakeredis
import redis
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_talisman import Talisman

logger = logging.getLogger("url_shortener.extensions")

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
cors = CORS()
talisman = Talisman()

def get_limiter_key():
    """
    Returns JWT identity (user ID) if authenticated,
    otherwise falls back to remote IP address for rate limiting.
    """
    from flask_jwt_extended import get_jwt_identity
    try:
        identity = get_jwt_identity()
        if identity:
            return f"user:{identity}"
    except Exception:
        pass
    return get_remote_address()

limiter = Limiter(
    key_func=get_limiter_key,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"  # Overridden in create_app with config.RATELIMIT_STORAGE_URI
)

class RedisClientWrapper:
    """Wrapper that provides Redis connectivity with local FakeRedis fallback."""
    def __init__(self):
        self._client = None
        self.is_fallback = False

    def init_app(self, app):
        redis_url = app.config.get("REDIS_URL", "redis://localhost:6379/0")
        try:
            client = redis.from_url(redis_url, decode_responses=True, socket_connect_timeout=1)
            client.ping()
            self._client = client
            self.is_fallback = False
            logger.info("Connected to native Redis at %s", redis_url)
        except Exception as e:
            logger.warning("Native Redis unavailable (%s). Using in-memory FakeRedis.", e)
            self._client = fakeredis.FakeRedis(decode_responses=True)
            self.is_fallback = True

    @property
    def client(self):
        if self._client is None:
            self._client = fakeredis.FakeRedis(decode_responses=True)
            self.is_fallback = True
        return self._client

redis_store = RedisClientWrapper()
