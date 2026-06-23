"""Challenge browsing, session start, and bug submission endpoints."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db_session, require_roles
from app.models.user import User
from app.schemas.challenge import (
    BugSubmitRequest,
    BugSubmitResponse,
    ChallengeDetail,
    ChallengeListItem,
    ChallengeSessionOut,
)
from app.services.bug_service import BugService
from app.services.challenge_service import ChallengeService

router = APIRouter(prefix="/challenges", tags=["challenges"])


@router.get("", response_model=list[ChallengeListItem], summary="List published challenges, optionally filtered")
def list_challenges(
    category_id: int | None = Query(default=None),
    type: str | None = Query(default=None),
    difficulty: str | None = Query(default=None),
    db: Session = Depends(get_db_session),
):
    service = ChallengeService(db)
    return service.list_challenges(category_id, type, difficulty)


@router.get("/{challenge_id}", response_model=ChallengeDetail, summary="Get full challenge detail")
def get_challenge(challenge_id: str, db: Session = Depends(get_db_session)):
    service = ChallengeService(db)
    return service.get_challenge(challenge_id)


@router.post(
    "/{challenge_id}/start",
    response_model=ChallengeSessionOut,
    summary="Start (or resume) a challenge session for the current user",
)
def start_challenge(
    challenge_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
):
    service = ChallengeService(db)
    return service.start_challenge(current_user.id, challenge_id)


@router.post(
    "/{challenge_id}/submit-bug",
    response_model=BugSubmitResponse,
    summary="Submit a bug report against an active challenge session (tester role only)",
)
def submit_bug(
    challenge_id: str,
    payload: BugSubmitRequest,
    current_user: User = Depends(require_roles("tester")),
    db: Session = Depends(get_db_session),
):
    service = BugService(db)
    bug, new_total, new_level = service.submit_bug(current_user.id, challenge_id, payload)
    return BugSubmitResponse(
        id=bug.id,
        title=bug.title,
        severity=bug.severity,
        priority=bug.priority,
        status=bug.status,
        xp_awarded=bug.xp_awarded,
        new_xp_total=new_total,
        new_level=new_level,
    )
