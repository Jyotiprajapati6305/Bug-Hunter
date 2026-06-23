"""Notifications, logging tables, and the developer-review stub table."""
from __future__ import annotations

import uuid

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, String, Text
from app.db.types import GUID, JSONType
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin


def _uuid() -> str:
    return str(uuid.uuid4())


class Notification(Base, TimestampMixin):
    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    notification_type: Mapped[str] = mapped_column(String(64), nullable=False, default="general")


class ActivityLog(Base, TimestampMixin):
    """User-facing activity feed events (e.g. 'submitted a bug', 'leveled up')."""

    __tablename__ = "activity_logs"

    id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    action: Mapped[str] = mapped_column(String(128), nullable=False)
    metadata_json: Mapped[dict | None] = mapped_column(JSONType, nullable=True)


class AuditLog(Base, TimestampMixin):
    """System/admin-facing audit trail, separate from user activity feed."""

    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=_uuid)
    actor_id: Mapped[str | None] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    details_json: Mapped[dict | None] = mapped_column(JSONType, nullable=True)


class DeveloperReview(Base, TimestampMixin):
    """Stub table for the future developer-review feature (no API/UI yet)."""

    __tablename__ = "developer_reviews"

    id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=_uuid)
    bug_id: Mapped[str] = mapped_column(
        GUID(), ForeignKey("bugs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    reviewer_id: Mapped[str] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    verdict: Mapped[str] = mapped_column(
        Enum("approved", "rejected", "needs_info", name="developer_review_verdict"),
        nullable=False,
        default="needs_info",
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
