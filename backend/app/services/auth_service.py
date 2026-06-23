"""Business logic for registration, login, refresh, logout, and password reset."""
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.models.user import User, UserProfile
from app.repositories.token_repository import TokenRepository
from app.repositories.user_repository import UserRepository
from app.tasks.email_tasks import send_email_task


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)
        self.tokens = TokenRepository(db)

    def register(self, email: str, username: str, password: str, role_name: str) -> User:
        if self.users.get_by_email(email):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email already registered")
        if self.users.get_by_username(username):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Username already taken")

        role = self.users.get_role_by_name(role_name)
        if role is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Unknown role: {role_name}")

        user = User(
            email=email,
            username=username,
            hashed_password=hash_password(password),
            role_id=role.id,
            is_active=True,
            is_verified=False,
        )
        profile = UserProfile(display_name=username)
        created = self.users.create(user, profile)
        send_email_task.delay(email, "Welcome to Bug Hunter Arena", "Your account has been created.")
        return created

    def authenticate(self, email: str, password: str) -> User:
        user = self.users.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password")
        if not user.is_active:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Account is disabled")
        user.last_login_at = datetime.now(timezone.utc)
        self.users.save(user)
        return user

    def issue_tokens(self, user: User) -> tuple[str, str]:
        role_name = user.role.name if user.role else "tester"
        access = create_access_token(user.id, role_name)
        refresh = create_refresh_token(user.id)
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        self.tokens.create_refresh_token(user.id, refresh, expires_at)
        return access, refresh

    def refresh_access_token(self, refresh_token: str) -> tuple[str, str]:
        from app.core.security import decode_token

        try:
            payload = decode_token(refresh_token)
        except ValueError as exc:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid refresh token") from exc

        if payload.get("type") != "refresh":
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token type")

        stored = self.tokens.get_refresh_token(refresh_token)
        if not self.tokens.is_refresh_token_valid(stored):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Refresh token revoked or expired")

        user = self.users.get_by_id(payload["sub"])
        if user is None or not user.is_active:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found or inactive")

        # Rotate: revoke old, issue new pair.
        self.tokens.revoke_refresh_token(refresh_token)
        return self.issue_tokens(user)

    def logout(self, refresh_token: str) -> None:
        self.tokens.revoke_refresh_token(refresh_token)

    def forgot_password(self, email: str) -> str:
        user = self.users.get_by_email(email)
        if user is None:
            # Don't leak whether the email exists; still behave the same way.
            raise HTTPException(status.HTTP_404_NOT_FOUND, "If that email exists, a reset link was sent")
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        self.tokens.create_password_reset(user.id, token, expires_at)
        reset_link = f"https://bughunterarena.dev/reset-password?token={token}"
        send_email_task.delay(email, "Password reset requested", f"Reset link: {reset_link}")
        return token

    def reset_password(self, token: str, new_password: str) -> None:
        row = self.tokens.get_password_reset(token)
        if row is None or row.used or row.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid or expired reset token")

        user = self.users.get_by_id(row.user_id)
        if user is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid reset token")

        user.hashed_password = hash_password(new_password)
        self.users.save(user)
        self.tokens.mark_password_reset_used(row)
