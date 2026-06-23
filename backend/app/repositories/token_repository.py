"""Data-access layer for refresh tokens and password reset tokens."""
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import PasswordReset, RefreshToken


class TokenRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_refresh_token(self, user_id: str, token: str, expires_at: datetime) -> RefreshToken:
        row = RefreshToken(user_id=user_id, token=token, expires_at=expires_at)
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def get_refresh_token(self, token: str) -> RefreshToken | None:
        stmt = select(RefreshToken).where(RefreshToken.token == token)
        return self.db.scalars(stmt).first()

    def revoke_refresh_token(self, token: str) -> None:
        row = self.get_refresh_token(token)
        if row:
            row.revoked = True
            self.db.commit()

    def is_refresh_token_valid(self, row: RefreshToken | None) -> bool:
        if row is None or row.revoked:
            return False
        return row.expires_at.replace(tzinfo=timezone.utc) > datetime.now(timezone.utc)

    def create_password_reset(self, user_id: str, token: str, expires_at: datetime) -> PasswordReset:
        row = PasswordReset(user_id=user_id, token=token, expires_at=expires_at)
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def get_password_reset(self, token: str) -> PasswordReset | None:
        stmt = select(PasswordReset).where(PasswordReset.token == token)
        return self.db.scalars(stmt).first()

    def mark_password_reset_used(self, row: PasswordReset) -> None:
        row.used = True
        self.db.commit()
