"""Data-access layer for challenges, sessions, and submissions."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.challenge import Challenge, ChallengeSession, ChallengeSubmission


class ChallengeRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_challenges(
        self,
        category_id: int | None = None,
        type_: str | None = None,
        difficulty: str | None = None,
    ) -> list[Challenge]:
        stmt = select(Challenge).where(
            Challenge.deleted_at.is_(None), Challenge.is_published.is_(True)
        )
        if category_id is not None:
            stmt = stmt.where(Challenge.category_id == category_id)
        if type_ is not None:
            stmt = stmt.where(Challenge.type == type_)
        if difficulty is not None:
            stmt = stmt.where(Challenge.difficulty == difficulty)
        return list(self.db.scalars(stmt).all())

    def get_by_id(self, challenge_id: str) -> Challenge | None:
        challenge = self.db.get(Challenge, challenge_id)
        if challenge is None or challenge.deleted_at is not None:
            return None
        return challenge

    def create_session(self, session: ChallengeSession) -> ChallengeSession:
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_session(self, session_id: str) -> ChallengeSession | None:
        return self.db.get(ChallengeSession, session_id)

    def get_active_session(self, user_id: str, challenge_id: str) -> ChallengeSession | None:
        stmt = select(ChallengeSession).where(
            ChallengeSession.user_id == user_id,
            ChallengeSession.challenge_id == challenge_id,
            ChallengeSession.status == "active",
        )
        return self.db.scalars(stmt).first()

    def create_submission(self, submission: ChallengeSubmission) -> ChallengeSubmission:
        self.db.add(submission)
        self.db.commit()
        self.db.refresh(submission)
        return submission

    def complete_session(self, session: ChallengeSession) -> ChallengeSession:
        from datetime import datetime, timezone

        session.status = "completed"
        session.completed_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(session)
        return session
