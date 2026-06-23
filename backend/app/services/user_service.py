"""Business logic for the current-user profile endpoints."""
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserUpdateRequest


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)

    def update_me(self, user: User, payload: UserUpdateRequest) -> User:
        self.users.update_profile(
            user.profile,
            display_name=payload.display_name,
            bio=payload.bio,
            avatar_url=payload.avatar_url,
        )
        self.db.refresh(user)
        return user
