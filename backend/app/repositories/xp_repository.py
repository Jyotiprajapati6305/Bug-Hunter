"""Data-access layer for the XP transaction ledger."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.xp import XpTransaction


class XpRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_transaction(self, transaction: XpTransaction) -> XpTransaction:
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def list_for_user(self, user_id: str, limit: int = 50) -> list[XpTransaction]:
        stmt = (
            select(XpTransaction)
            .where(XpTransaction.user_id == user_id)
            .order_by(XpTransaction.created_at.desc())
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())
