import os

import fakeredis
import pytest

# Set testing environment variable
os.environ["FLASK_ENV"] = "testing"
os.environ["DISABLE_TALISMAN"] = "1"

import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.extensions import db as _db
from app.extensions import redis_store


@pytest.fixture(scope="session")
def app():
    """Session-wide test Flask application."""
    test_app = create_app("testing")
    with test_app.app_context():
        # Use FakeRedis for isolated unit & integration testing
        redis_store._client = fakeredis.FakeRedis(decode_responses=True)
        _db.create_all()
        yield test_app
        _db.drop_all()

@pytest.fixture(scope="function")
def client(app):
    """Test HTTP client."""
    return app.test_client()

@pytest.fixture(scope="function", autouse=True)
def clean_db(app):
    """Cleans database tables and flush Redis between test runs."""
    with app.app_context():
        _db.session.rollback()
        for table in reversed(_db.metadata.sorted_tables):
            _db.session.execute(table.delete())
        _db.session.commit()
        if redis_store._client:
            redis_store._client.flushall()

@pytest.fixture
def auth_user(client):
    """Registers and authenticates a test user, returning JWT header."""
    user_payload = {
        "email": "engineer@portfolio.dev",
        "password": "SecurePassword123!"
    }
    client.post("/api/auth/register", json=user_payload)
    login_resp = client.post("/api/auth/login", json=user_payload)
    token = login_resp.get_json()["access_token"]
    return {
        "email": user_payload["email"],
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"}
    }
