"""Business logic for browsing challenges and managing challenge sessions."""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.challenge import Challenge, ChallengeSession
from app.repositories.challenge_repository import ChallengeRepository


class ChallengeService:
    def __init__(self, db: Session):
        self.db = db
        self.challenges = ChallengeRepository(db)

    def list_challenges(
        self, category_id: int | None, type_: str | None, difficulty: str | None
    ) -> list[Challenge]:
        return self.challenges.list_challenges(category_id, type_, difficulty)

    def get_challenge(self, challenge_id: str) -> Challenge:
        challenge = self.challenges.get_by_id(challenge_id)
        if challenge is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Challenge not found")
        return challenge

    def start_challenge(self, user_id: str, challenge_id: str) -> ChallengeSession:
        self.get_challenge(challenge_id)  # 404s if missing
        existing = self.challenges.get_active_session(user_id, challenge_id)
        if existing:
            return existing
        session = ChallengeSession(user_id=user_id, challenge_id=challenge_id, status="active")
        return self.challenges.create_session(session)
