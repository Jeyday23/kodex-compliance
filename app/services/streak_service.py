"""
Streak Service — tracks daily participation to drive retention.
Response limits force daily engagement; streaks reward consistency.
"""
from datetime import date, datetime, timezone, timedelta
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.post import Post
from app.models.reply import Reply

# Limits per user per day
MAX_POSTS_PER_DAY = 3
MAX_REPLIES_PER_DAY = 10


async def get_daily_activity(db: AsyncSession, user_id: str) -> dict:
    """Get user's post/reply counts for today and streak info."""
    today = date.today()
    start = datetime(today.year, today.month, today.day, tzinfo=timezone.utc)

    posts_today = await db.execute(
        select(func.count()).where(
            Post.author_id == user_id,
            Post.created_at >= start,
        )
    )
    replies_today = await db.execute(
        select(func.count()).where(
            Reply.author_id == user_id,
            Reply.created_at >= start,
        )
    )

    post_count = posts_today.scalar() or 0
    reply_count = replies_today.scalar() or 0

    # Calculate streak (consecutive days with at least 1 post or reply)
    streak = await _calculate_streak(db, user_id)

    return {
        "posts_today": post_count,
        "posts_remaining": max(0, MAX_POSTS_PER_DAY - post_count),
        "replies_today": reply_count,
        "replies_remaining": max(0, MAX_REPLIES_PER_DAY - reply_count),
        "current_streak": streak,
        "streak_bonus_active": streak >= 3,  # 3+ day streak = clout bonus
    }


async def can_post(db: AsyncSession, user_id: str) -> bool:
    activity = await get_daily_activity(db, user_id)
    return activity["posts_remaining"] > 0


async def can_reply(db: AsyncSession, user_id: str) -> bool:
    activity = await get_daily_activity(db, user_id)
    return activity["replies_remaining"] > 0


async def _calculate_streak(db: AsyncSession, user_id: str) -> int:
    """Count consecutive days the user posted or replied."""
    streak = 0
    check_date = date.today()

    for _ in range(365):  # Max 1 year lookback
        start = datetime(check_date.year, check_date.month, check_date.day, tzinfo=timezone.utc)
        end = start + timedelta(days=1)

        post_count = await db.execute(
            select(func.count()).where(
                Post.author_id == user_id,
                Post.created_at >= start,
                Post.created_at < end,
            )
        )
        reply_count = await db.execute(
            select(func.count()).where(
                Reply.author_id == user_id,
                Reply.created_at >= start,
                Reply.created_at < end,
            )
        )

        if (post_count.scalar() or 0) + (reply_count.scalar() or 0) > 0:
            streak += 1
            check_date -= timedelta(days=1)
        else:
            break

    return streak
