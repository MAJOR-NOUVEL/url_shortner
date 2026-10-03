import logging
from datetime import datetime, timezone

from flask import current_app

from app.celery_app import celery_app
from app.extensions import db
from app.models.click import ClickAnalytics
from app.utils.security import hash_ip
from app.utils.user_agent import clean_referrer, parse_user_agent

logger = logging.getLogger("url_shortener.tasks")

@celery_app.task(name="app.tasks.click_logger.record_click_event", bind=True, max_retries=3)
def record_click_event(self, url_id: int, referrer: str, user_agent: str, client_ip: str, country: str = "Unknown"):
    """
    Asynchronous Celery task:
    Parses user agent, anonymizes client IP, and commits click analytics to PostgreSQL.
    Shields redirection endpoints from slow disk I/O.
    """
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
        return {"status": "success", "url_id": url_id, "click_id": click.id}

    except Exception as exc:
        db.session.rollback()
        logger.error("Failed to record click event for URL id %s: %s", url_id, exc)
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
