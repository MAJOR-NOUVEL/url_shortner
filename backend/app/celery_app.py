from celery import Celery


def create_celery(app=None):
    celery = Celery(
        "url_shortener",
        include=["app.tasks.click_logger"]
    )

    if app:
        init_celery(app, celery)

    return celery

def init_celery(app, celery):
    from app.extensions import redis_store

    # Check if native Redis is available or if using local fallback
    is_fallback = getattr(redis_store, "is_fallback", False)

    if is_fallback:
        broker_url = "memory://"
        result_backend = "cache+memory://"
        task_always_eager = True
    else:
        broker_url = app.config.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
        result_backend = app.config.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
        task_always_eager = app.config.get("CELERY_TASK_ALWAYS_EAGER", app.config.get("TESTING", False))

    celery.conf.update(
        broker_url=broker_url,
        result_backend=result_backend,
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
        timezone="UTC",
        enable_utc=True,
        task_track_started=True,
        task_always_eager=task_always_eager,
        task_eager_propagates=False
    )

    class ContextTask(celery.Task):
        """Ensures Celery tasks run within Flask application context for DB access."""
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask

celery_app = create_celery()
