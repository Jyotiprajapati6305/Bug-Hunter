"""Pydantic schemas for user/profile endpoints."""
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    display_name: str | None
    bio: str | None
    avatar_url: str | None
    xp_total: int
    level: int
    bugs_found_count: int
    challenges_completed_count: int
    test_cases_written_count: int


class UserMeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: EmailStr
    username: str
    role: str
    is_active: bool
    is_verified: bool
    profile: UserProfileOut


class UserUpdateRequest(BaseModel):
    display_name: str | None = Field(default=None, max_length=128)
    bio: str | None = Field(default=None, max_length=2000)
    avatar_url: str | None = Field(default=None, max_length=512)
