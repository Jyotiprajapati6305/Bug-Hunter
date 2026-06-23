"""Celery application instance shared by the API process and the worker container."""
from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "bug_hunter_arena",
    broker=settings.celery_broker,
    backend=settings.celery_backend,
    include=["app.tasks.email_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # In tests/local dev without a running broker, execute tasks synchronously
    # in-process instead of trying to publish to Redis.
    task_always_eager=settings.ENVIRONMENT == "test",
)
