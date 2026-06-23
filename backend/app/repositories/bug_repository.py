"""Data-access layer for bug reports."""
from sqlalchemy.orm import Session

from app.models.bug import Bug


class BugRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, bug: Bug) -> Bug:
        self.db.add(bug)
        self.db.commit()
        self.db.refresh(bug)
        return bug
