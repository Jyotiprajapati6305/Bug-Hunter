"""Email-sending tasks.

Phase 1 has no real SMTP integration. Sending an email simply logs the
intent so the rest of the system (registration, password reset) can be
built and tested against a real, working async task pipeline today, and a
real provider (SES/SendGrid/etc.) can be dropped in later without touching
any calling code.
"""
import logging

from app.tasks.celery_app import celery_app

logger = logging.getLogger("bug_hunter_arena.email")


@celery_app.task(name="tasks.send_email")
def send_email_task(to_email: str, subject: str, body: str) -> dict:
    logger.info("Would send email to %s | subject=%r | body=%r", to_email, subject, body)
    return {"to": to_email, "subject": subject, "sent": True}
