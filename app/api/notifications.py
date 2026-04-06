"""
Notifications API — engagement alerts that drive the behavior loop.
"""
from fastapi import APIRouter, Depends
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.notification import Notification
from app.schemas.notification import NotificationOut

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/", response_model=list[NotificationOut])
async def get_notifications(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Get user's notifications, newest first."""
    result = await db.execute(
        select(Notification)
        .where(Notification.user_id == user.id)
        .order_by(Notification.created_at.desc())
        .limit(limit)
    )
    return result.scalars().all()


@router.post("/read-all")
async def mark_all_read(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Mark all notifications as read."""
    await db.execute(
        update(Notification)
        .where(Notification.user_id == user.id, Notification.is_read == False)
        .values(is_read=True)
    )
    await db.commit()
    return {"status": "ok"}


@router.get("/unread-count")
async def unread_count(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    from sqlalchemy import func
    result = await db.execute(
        select(func.count())
        .where(Notification.user_id == user.id, Notification.is_read == False)
    )
    return {"count": result.scalar() or 0}
