"""Current-user profile endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db_session
from app.models.user import User
from app.schemas.user import UserMeResponse, UserUpdateRequest
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


def _to_me_response(user: User) -> UserMeResponse:
    return UserMeResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        role=user.role.name,
        is_active=user.is_active,
        is_verified=user.is_verified,
        profile=user.profile,
    )


@router.get("/me", response_model=UserMeResponse, summary="Get the current user's profile, XP, and level")
def get_me(current_user: User = Depends(get_current_user)):
    return _to_me_response(current_user)


@router.patch("/me", response_model=UserMeResponse, summary="Update the current user's profile fields")
def update_me(
    payload: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
):
    service = UserService(db)
    updated = service.update_me(current_user, payload)
    return _to_me_response(updated)
