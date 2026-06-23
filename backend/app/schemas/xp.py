"""Pydantic schemas for the XP ledger and level table."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class XpTransactionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    amount: int
    reason: str
    reference_type: str | None
    reference_id: str | None
    created_at: datetime


class LevelInfo(BaseModel):
    level: int
    xp_required: int


class LevelTableResponse(BaseModel):
    levels: list[LevelInfo]
