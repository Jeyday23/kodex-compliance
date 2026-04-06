"""
Background worker — recalculates clout scores for all users.
Run via: python -m app.services.clout_worker
In production: use Celery or APScheduler.

This is equivalent to Tinder's offline recommendation pipeline
that recalculates desirability scores.
"""
import asyncio
from datetime import datetime, timezone
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.core.redis import get_redis
from app.models.user import User
from app.services.clout_engine import compute_clout_score, score_to_tier, update_user_clout_in_redis


async def recalculate_all_scores():
    r = await get_redis()
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.is_active == True))
        users = result.scalars().all()

        for user in users:
            # Compute days since last active
            days_inactive = (datetime.now(timezone.utc) - user.last_active).days

            # Compute reply rate (replies received / posts made)
            post_count = len(user.posts) if user.posts else 1
            reply_rate = user.total_replies_received / max(post_count, 1)

            # Like rate
            total_views = sum(p.view_count for p in user.posts) if user.posts else 1
            like_rate = user.total_likes_received / max(total_views, 1)

            # Avg watch percentage across all posts
            if user.posts:
                avg_watch = sum(p.avg_watch_pct for p in user.posts) / len(user.posts)
            else:
                avg_watch = 0.0

            score = compute_clout_score(
                avg_watch_pct=avg_watch,
                reply_rate=reply_rate,
                like_rate=like_rate,
                response_rate=user.response_rate,
                days_since_last_active=days_inactive,
            )

            # Anchor users get a floor of 85 (they're hand-picked)
            if user.is_anchor:
                score = max(score, 85.0)

            user.clout_score = score
            user.tier = score_to_tier(score)
            await update_user_clout_in_redis(r, user.id, score)

        await db.commit()
        print(f"Updated {len(users)} user clout scores")


if __name__ == "__main__":
    asyncio.run(recalculate_all_scores())
