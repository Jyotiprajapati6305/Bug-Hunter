"""Challenge catalogue, sessions, submissions and type-specific detail tables."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from app.db.types import GUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import SoftDeleteMixin, TimestampMixin


def _uuid() -> str:
    return str(uuid.uuid4())


class ChallengeCategory(Base, TimestampMixin):
    __tablename__ = "challenge_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    challenges: Mapped[list["Challenge"]] = relationship(back_populates="category")


class Challenge(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "challenges"

    id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=_uuid)
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("challenge_categories.id", ondelete="SET NULL"), nullable=True, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty: Mapped[str] = mapped_column(
        Enum("beginner", "intermediate", "advanced", "expert", name="challenge_difficulty"),
        nullable=False,
        default="beginner",
    )
    type: Mapped[str] = mapped_column(
        Enum("functional", "ui", "api", "security", "performance", name="challenge_type"),
        nullable=False,
    )
    base_xp: Mapped[int] = mapped_column(Integer, nullable=False, default=50)
    is_published: Mapped[bool] = mapped_column(default=True, nullable=False)
    environment_url: Mapped[str | None] = mapped_column(String(512), nullable=True)

    category: Mapped["ChallengeCategory"] = relationship(back_populates="challenges")
    sessions: Mapped[list["ChallengeSession"]] = relationship(
        back_populates="challenge", cascade="all, delete-orphan"
    )
    test_cases: Mapped[list["TestCase"]] = relationship(
        back_populates="challenge", cascade="all, delete-orphan"
    )
    api_detail: Mapped["ApiChallenge"] = relationship(
        back_populates="challenge", uselist=False, cascade="all, delete-orphan"
    )
    security_detail: Mapped["SecurityChallenge"] = relationship(
        back_populates="challenge", uselist=False, cascade="all, delete-orphan"
    )
    performance_detail: Mapped["PerformanceChallenge"] = relationship(
        back_populates="challenge", uselist=False, cascade="all, delete-orphan"
    )


class ChallengeSession(Base, TimestampMixin):
    """Tracks a user's attempt window on a challenge."""

    __tablename__ = "challenge_sessions"

    id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    challenge_id: Mapped[str] = mapped_column(
        GUID(), ForeignKey("challenges.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(
        Enum("active", "completed", "abandoned", name="session_status"),
        nullable=False,
        default="active",
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    challenge: Mapped["Challenge"] = relationship(back_populates="sessions")
    submissions: Mapped[list["ChallengeSubmission"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )


class ChallengeSubmission(Base, TimestampMixin):
    """A single submission event within a challenge session (e.g. a bug report)."""

    __tablename__ = "challenge_submissions"

    id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=_uuid)
    session_id: Mapped[str] = mapped_column(
        GUID(),
        ForeignKey("challenge_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    submission_type: Mapped[str] = mapped_column(
        Enum("bug_report", "test_case", name="submission_type"),
        nullable=False,
        default="bug_report",
    )
    xp_awarded: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    session: Mapped["ChallengeSession"] = relationship(back_populates="submissions")
    bug: Mapped["Bug"] = relationship(
        back_populates="submission", uselist=False, cascade="all, delete-orphan"
    )


class TestCase(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "test_cases"

    id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=_uuid)
    challenge_id: Mapped[str] = mapped_column(
        GUID(), ForeignKey("challenges.id", ondelete="CASCADE"), nullable=False, index=True
    )
    author_id: Mapped[str | None] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    preconditions: Mapped[str | None] = mapped_column(Text, nullable=True)
    steps: Mapped[str] = mapped_column(Text, nullable=False)
    expected_result: Mapped[str] = mapped_column(Text, nullable=False)

    challenge: Mapped["Challenge"] = relationship(back_populates="test_cases")


class ApiChallenge(Base, TimestampMixin):
    """Type-specific detail table for API testing challenges."""

    __tablename__ = "api_challenges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    challenge_id: Mapped[str] = mapped_column(
        GUID(), ForeignKey("challenges.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    base_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    openapi_spec_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    auth_instructions: Mapped[str | None] = mapped_column(Text, nullable=True)

    challenge: Mapped["Challenge"] = relationship(back_populates="api_detail")


class SecurityChallenge(Base, TimestampMixin):
    """Type-specific detail table for security testing challenges."""

    __tablename__ = "security_challenges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    challenge_id: Mapped[str] = mapped_column(
        GUID(), ForeignKey("challenges.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    vulnerability_class: Mapped[str | None] = mapped_column(String(128), nullable=True)
    target_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    rules_of_engagement: Mapped[str | None] = mapped_column(Text, nullable=True)

    challenge: Mapped["Challenge"] = relationship(back_populates="security_detail")


class PerformanceChallenge(Base, TimestampMixin):
    """Type-specific detail table for performance testing challenges."""

    __tablename__ = "performance_challenges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    challenge_id: Mapped[str] = mapped_column(
        GUID(), ForeignKey("challenges.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    target_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    expected_throughput: Mapped[str | None] = mapped_column(String(128), nullable=True)
    max_acceptable_latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    challenge: Mapped["Challenge"] = relationship(back_populates="performance_detail")
