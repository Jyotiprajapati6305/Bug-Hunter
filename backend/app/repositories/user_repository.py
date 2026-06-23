"""Data-access layer for users, roles, and profiles."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import Role, User, UserProfile


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: str) -> User | None:
        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email, User.deleted_at.is_(None))
        return self.db.scalars(stmt).first()

    def get_by_username(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username, User.deleted_at.is_(None))
        return self.db.scalars(stmt).first()

    def get_role_by_name(self, name: str) -> Role | None:
        stmt = select(Role).where(Role.name == name)
        return self.db.scalars(stmt).first()

    def create(self, user: User, profile: UserProfile) -> User:
        self.db.add(user)
        self.db.flush()
        profile.user_id = user.id
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_profile(self, profile: UserProfile, **fields) -> UserProfile:
        for key, value in fields.items():
            if value is not None:
                setattr(profile, key, value)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def save(self, user: User) -> User:
        self.db.commit()
        self.db.refresh(user)
        return user
