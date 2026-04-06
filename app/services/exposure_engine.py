"""
Algorithmic Exposure Engine — ensures every user gets baseline visibility
and occasional spikes to keep retention stable.

Key principle: Even low-clout users get periodic boosts in visibility
(like TikTok's "For You" page giving new creators a chance).
"""
import random
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.post import Post
from app.models.user import User, UserTier


# Baseline impressions every user gets regardless of clout
BASELINE_IMPRESSIONS_PER_DAY = 50
# Spike probability — chance of a "viral" push for any user
SPIKE_PROBABILITY = 0.08  # 8% chance per feed refresh
SPIKE_MULTIPLIER = 5  # 5x normal visibility during a spike


async def get_exposure_weighted_feed(
    db: AsyncSession,
    viewer: User,
    limit: int = 20,
) -> list[Post]:
    """
    Build a feed that balances engagement-ranked content with
    algorithmic fairness so every user gets seen.

    Distribution:
    - 50% — high-engagement posts (organic ranking)
    - 30% — fresh posts from users who need baseline exposure
    - 20% — random "discovery" posts (spike candidates)
    """
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=48)

    # 1. Top-ranked posts
    top_result = await db.execute(
        select(Post)
        .where(Post.created_at >= cutoff, Post.is_active == True)
        .order_by(
            (Post.like_count * 2 + Post.reply_count * 5 + Post.view_count * 0.1).desc()
        )
        .limit(int(limit * 0.5))
    )
    top_posts = list(top_result.scalars().all())

    # 2. Baseline exposure — fresh posts from users with low recent views
    fresh_result = await db.execute(
        select(Post)
        .where(
            Post.created_at >= cutoff,
            Post.is_active == True,
            Post.view_count < BASELINE_IMPRESSIONS_PER_DAY,
        )
        .order_by(Post.created_at.desc())
        .limit(int(limit * 0.3))
    )
    fresh_posts = list(fresh_result.scalars().all())

    # 3. Discovery / spike candidates — random selection
    random_result = await db.execute(
        select(Post)
        .where(Post.created_at >= cutoff, Post.is_active == True)
        .order_by(func.random())
        .limit(int(limit * 0.2))
    )
    discovery_posts = list(random_result.scalars().all())

    # Merge, deduplicate, shuffle for natural feel
    seen_ids = set()
    feed = []
    for post in top_posts + fresh_posts + discovery_posts:
        if post.id not in seen_ids:
            seen_ids.add(post.id)
            feed.append(post)

    random.shuffle(feed)

    # Apply spike — randomly boost one low-clout post to the top
    if feed and random.random() < SPIKE_PROBABILITY:
        low_clout = [p for p in feed if p.view_count < 20]
        if low_clout:
            spike_post = random.choice(low_clout)
            feed.remove(spike_post)
            feed.insert(0, spike_post)

    return feed[:limit]
