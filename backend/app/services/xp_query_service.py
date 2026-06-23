"""Read-side queries for the XP ledger and level table (kept separate from the
XP calculation logic in xp_service.py to keep concerns small and testable)."""
from sqlalchemy.orm import Session

from app.repositories.xp_repository import XpRepository
from app.services.xp_service import get_level_table


class XpQueryService:
    def __init__(self, db: Session):
        self.xp = XpRepository(db)

    def list_transactions(self, user_id: str):
        return self.xp.list_for_user(user_id)

    def level_table(self):
        return get_level_table()
