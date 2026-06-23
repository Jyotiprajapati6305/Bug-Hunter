"""Pydantic schemas for challenges, sessions, and bug submissions."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ChallengeCategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    description: str | None


class ChallengeListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    difficulty: str
    type: str
    base_xp: int
    category_id: int | None
    is_published: bool


class ChallengeDetail(ChallengeListItem):
    description: str
    environment_url: str | None


class ChallengeSessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    challenge_id: str
    user_id: str
    status: str
    started_at: datetime
    completed_at: datetime | None


class BugSubmitRequest(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    description: str = Field(min_length=1)
    steps_to_reproduce: str = Field(min_length=1)
    actual_result: str = Field(min_length=1)
    expected_result: str = Field(min_length=1)
    severity: str = Field(pattern="^(critical|high|medium|low)$")
    priority: str = Field(default="normal", pattern="^(urgent|high|normal|low)$")
    is_duplicate: bool = Field(
        default=False,
        description="Tester/admin can flag a known duplicate at submission time; awards 0 XP.",
    )


class BugSubmitResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    severity: str
    priority: str
    status: str
    xp_awarded: int
    new_xp_total: int
    new_level: int
