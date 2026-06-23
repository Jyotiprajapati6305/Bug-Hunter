"""Tables for future achievements/leaderboard features.

No service/API logic is built against these in Phase 1 — they exist purely so
that later migrations can build on a stable schema.
"""
from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from app.db.types import GUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin


def _uuid() -> str:
    return str(uuid.uuid4())


class Achievement(Base, TimestampMixin):
    __tablename__ = "achievements"

    id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=_uuid)
    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    xp_bonus: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    icon_url: Mapped[str | None] = mapped_column(String(512), nullable=True)


class UserAchievement(Base, TimestampMixin):
    __tablename__ = "user_achievements"
    __table_args__ = (UniqueConstraint("user_id", "achievement_id", name="uq_user_achievement"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    achievement_id: Mapped[str] = mapped_column(
        GUID(), ForeignKey("achievements.id", ondelete="CASCADE"), nullable=False, index=True
    )


class Leaderboard(Base, TimestampMixin):
    """Periodic leaderboard snapshot rows (e.g. weekly/monthly/all-time)."""

    __tablename__ = "leaderboards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    period: Mapped[str] = mapped_column(String(32), nullable=False, default="all_time")
    rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    xp_total: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
