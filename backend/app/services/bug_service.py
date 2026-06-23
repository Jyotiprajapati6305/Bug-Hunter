"""Business logic for submitting bugs against a challenge session and awarding XP."""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.bug import Bug
from app.models.challenge import ChallengeSubmission
from app.models.xp import XpTransaction
from app.repositories.bug_repository import BugRepository
from app.repositories.challenge_repository import ChallengeRepository
from app.repositories.user_repository import UserRepository
from app.repositories.xp_repository import XpRepository
from app.schemas.challenge import BugSubmitRequest
from app.services.xp_service import level_for_xp, xp_for_bug


class BugService:
    def __init__(self, db: Session):
        self.db = db
        self.challenges = ChallengeRepository(db)
        self.bugs = BugRepository(db)
        self.xp = XpRepository(db)
        self.users = UserRepository(db)

    def submit_bug(self, user_id: str, challenge_id: str, payload: BugSubmitRequest) -> tuple[Bug, int, int]:
        challenge = self.challenges.get_by_id(challenge_id)
        if challenge is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Challenge not found")

        session = self.challenges.get_active_session(user_id, challenge_id)
        if session is None:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "No active session for this challenge — call start first",
            )

        status_value = "duplicate" if payload.is_duplicate else "accepted"
        xp_amount = xp_for_bug(payload.severity, payload.is_duplicate, status_value)

        submission = ChallengeSubmission(
            session_id=session.id, submission_type="bug_report", xp_awarded=xp_amount
        )
        submission = self.challenges.create_submission(submission)

        bug = Bug(
            challenge_submission_id=submission.id,
            reporter_id=user_id,
            title=payload.title,
            description=payload.description,
            steps_to_reproduce=payload.steps_to_reproduce,
            actual_result=payload.actual_result,
            expected_result=payload.expected_result,
            severity=payload.severity,
            priority=payload.priority,
            status=status_value,
            xp_awarded=xp_amount,
        )
        bug = self.bugs.create(bug)

        new_total = self._award_xp(
            user_id, xp_amount, f"Bug submission ({payload.severity})", "bug", bug.id
        )
        new_level = level_for_xp(new_total)

        profile = self.users.get_by_id(user_id).profile
        self.users.update_profile(
            profile,
            xp_total=new_total,
            level=new_level,
            bugs_found_count=profile.bugs_found_count + 1,
        )

        self.challenges.complete_session(session)

        return bug, new_total, new_level

    def _award_xp(self, user_id: str, amount: int, reason: str, ref_type: str, ref_id: str) -> int:
        transaction = XpTransaction(
            user_id=user_id, amount=amount, reason=reason, reference_type=ref_type, reference_id=ref_id
        )
        self.xp.create_transaction(transaction)

        user = self.users.get_by_id(user_id)
        new_total = user.profile.xp_total + amount
        return new_total
