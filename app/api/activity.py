"""
Activity API — daily limits, streaks, and participation stats.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.auth import get_current_user
from app.services.streak_service import get_daily_activity

router = APIRouter(prefix="/activity", tags=["activity"])


@router.get("/daily")
async def daily_activity(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Get today's post/reply limits, streak, and bonus status."""
    return await get_daily_activity(db, user.id)
