"""Bug-related read endpoints (creation happens via challenges/{id}/submit-bug)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db_session
from app.models.bug import Bug
from app.models.user import User

router = APIRouter(prefix="/bugs", tags=["bugs"])


@router.get("/{bug_id}", summary="Get a single bug report by id")
def get_bug(
    bug_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
):
    bug = db.get(Bug, bug_id)
    if bug is None or bug.deleted_at is not None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Bug not found")
    return {
        "id": bug.id,
        "title": bug.title,
        "description": bug.description,
        "steps_to_reproduce": bug.steps_to_reproduce,
        "actual_result": bug.actual_result,
        "expected_result": bug.expected_result,
        "severity": bug.severity,
        "priority": bug.priority,
        "status": bug.status,
        "xp_awarded": bug.xp_awarded,
        "reporter_id": bug.reporter_id,
    }
