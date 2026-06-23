"""Bug reports submitted by testers, plus comments and attachments."""
from __future__ import annotations

import uuid

from sqlalchemy import Enum, ForeignKey, Integer, String, Text
from app.db.types import GUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import SoftDeleteMixin, TimestampMixin


def _uuid() -> str:
    return str(uuid.uuid4())


class Bug(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "bugs"

    id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=_uuid)
    challenge_submission_id: Mapped[str] = mapped_column(
        GUID(),
        ForeignKey("challenge_submissions.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    reporter_id: Mapped[str] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    steps_to_reproduce: Mapped[str] = mapped_column(Text, nullable=False)
    actual_result: Mapped[str] = mapped_column(Text, nullable=False)
    expected_result: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(
        Enum("critical", "high", "medium", "low", name="bug_severity"), nullable=False
    )
    priority: Mapped[str] = mapped_column(
        Enum("urgent", "high", "normal", "low", name="bug_priority"),
        nullable=False,
        default="normal",
    )
    status: Mapped[str] = mapped_column(
        Enum("pending", "accepted", "rejected", "duplicate", name="bug_status"),
        nullable=False,
        default="pending",
    )
    xp_awarded: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    reviewed_by_id: Mapped[str | None] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    submission: Mapped["ChallengeSubmission"] = relationship(back_populates="bug")
    comments: Mapped[list["BugComment"]] = relationship(
        back_populates="bug", cascade="all, delete-orphan"
    )
    attachments: Mapped[list["BugAttachment"]] = relationship(
        back_populates="bug", cascade="all, delete-orphan"
    )


class BugComment(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "bug_comments"

    id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=_uuid)
    bug_id: Mapped[str] = mapped_column(
        GUID(), ForeignKey("bugs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    author_id: Mapped[str | None] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    body: Mapped[str] = mapped_column(Text, nullable=False)

    bug: Mapped["Bug"] = relationship(back_populates="comments")


class BugAttachment(Base, TimestampMixin):
    __tablename__ = "bug_attachments"

    id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=_uuid)
    bug_id: Mapped[str] = mapped_column(
        GUID(), ForeignKey("bugs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    file_url: Mapped[str] = mapped_column(String(512), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str | None] = mapped_column(String(128), nullable=True)

    bug: Mapped["Bug"] = relationship(back_populates="attachments")
