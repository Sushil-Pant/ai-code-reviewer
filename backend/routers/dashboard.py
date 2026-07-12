"""Dashboard analytics router."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.db import get_db, User
from services.review_service import get_dashboard_stats
from utils.dependencies import get_current_user

router = APIRouter()


@router.get("/stats")
async def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get dashboard statistics."""
    stats = get_dashboard_stats(db, current_user.id)
    return stats
