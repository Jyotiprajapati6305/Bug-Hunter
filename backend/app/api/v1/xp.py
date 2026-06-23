"""XP ledger and level-table endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db_session
from app.models.user import User
from app.schemas.xp import LevelInfo, LevelTableResponse, XpTransactionOut
from app.services.xp_query_service import XpQueryService

router = APIRouter(prefix="/xp", tags=["xp"])


@router.get("/me/transactions", response_model=list[XpTransactionOut], summary="List the current user's XP transactions")
def my_transactions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
):
    service = XpQueryService(db)
    return service.list_transactions(current_user.id)


@router.get("/levels", response_model=LevelTableResponse, summary="Get the full XP level table")
def levels(db: Session = Depends(get_db_session)):
    service = XpQueryService(db)
    table = service.level_table()
    return LevelTableResponse(levels=[LevelInfo(level=lvl, xp_required=xp) for lvl, xp in table])
