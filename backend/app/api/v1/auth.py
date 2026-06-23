"""Authentication endpoints: register, login, refresh, logout, password reset."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import get_db_session
from app.schemas.auth import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    LogoutRequest,
    MessageResponse,
    RefreshRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
)
from app.schemas.user import UserMeResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserMeResponse, status_code=status.HTTP_201_CREATED, summary="Register a new tester or developer account")
def register(payload: RegisterRequest, db: Session = Depends(get_db_session)):
    service = AuthService(db)
    user = service.register(payload.email, payload.username, payload.password, payload.role)
    return UserMeResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        role=user.role.name,
        is_active=user.is_active,
        is_verified=user.is_verified,
        profile=user.profile,
    )


@router.post("/login", response_model=TokenResponse, summary="Log in and receive an access/refresh token pair")
def login(payload: LoginRequest, db: Session = Depends(get_db_session)):
    service = AuthService(db)
    user = service.authenticate(payload.email, payload.password)
    access, refresh = service.issue_tokens(user)
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/refresh", response_model=TokenResponse, summary="Exchange a refresh token for a new token pair")
def refresh(payload: RefreshRequest, db: Session = Depends(get_db_session)):
    service = AuthService(db)
    access, refresh_token = service.refresh_access_token(payload.refresh_token)
    return TokenResponse(access_token=access, refresh_token=refresh_token)


@router.post("/logout", response_model=MessageResponse, summary="Revoke a refresh token")
def logout(payload: LogoutRequest, db: Session = Depends(get_db_session)):
    service = AuthService(db)
    service.logout(payload.refresh_token)
    return MessageResponse(message="Logged out")


@router.post("/forgot-password", response_model=ForgotPasswordResponse, summary="Request a password reset link (logged, not emailed, in Phase 1)")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db_session)):
    service = AuthService(db)
    token = service.forgot_password(payload.email)
    return ForgotPasswordResponse(
        message="If that email exists, a reset link has been generated and logged.",
        reset_token_debug=token,
    )


@router.post("/reset-password", response_model=MessageResponse, summary="Reset password using a reset token")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db_session)):
    service = AuthService(db)
    service.reset_password(payload.token, payload.new_password)
    return MessageResponse(message="Password has been reset")
