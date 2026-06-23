"""XP ledger. Every XP-affecting event creates an immutable transaction row."""
from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Integer, String
from app.db.types import GUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin


def _uuid() -> str:
    return str(uuid.uuid4())


class XpTransaction(Base, TimestampMixin):
    __tablename__ = "xp_transactions"

    id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    reference_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    reference_id: Mapped[str | None] = mapped_column(String(64), nullable=True)

    user: Mapped["User"] = relationship()
