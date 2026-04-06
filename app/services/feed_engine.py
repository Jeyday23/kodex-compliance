"""
Feed Ranking Engine — determines what posts users see.

Tinder's recommendation engine:
- Uses a multi-pass system: candidate generation -> scoring -> filtering -> ranking
- Candidates are pre-computed and stored in Redis queues per user
- Scoring factors: mutual attractiveness, distance, activity, preferences

VibeCrush Feed:
- Posts are ranked by a feed score combining post quality + author clout + boost status
- Distribution is ASYMMETRIC by design:
  * Tier A posts: shown to everyone (wide distribution)
  * Tier B posts: shown to B + C users, occasionally A
  * Tier C posts: shown mainly to C users (unless boosted)
- "Controlled wins" and "micro-virality" are injected randomly
"""
import redis.asyncio as redis
import random
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from app.models.post import Post
from app.models.user import User, UserTier
from datetime import datetime, timezone, timedelta


async def compute_post_feed_score(post: Post, viewer_tier: str) -> float:
    """Score a post for a specific viewer. Higher = shown first."""
    base_score = 0.0

    # Author clout contributes to visibility
    author_clout = post.author.clout_score if post.author else 50.0
    base_score += author_clout * 0.4

    # Engagement velocity (replies per hour since creation)
    age_hours = max(1, (datetime.now(timezone.utc) - post.created_at).total_seconds() / 3600)
    velocity = post.reply_count / age_hours
    base_score += min(velocity * 20, 30)  # Cap at 30 pts

    # Recency bonus (newer posts score higher)
    recency = max(0, 30 - age_hours)
    base_score += recency * 0.5

    # Boost multiplier
    if post.is_boosted and post.boost_expires_at and post.boost_expires_at > datetime.now(timezone.utc):
        base_score *= 1.5
        # If boosted to target tier A and viewer is A, extra boost
        if post.boost_tier_target == viewer_tier:
            base_score *= 1.3

    # === MICRO-VIRALITY INJECTION ===
    # 5% chance any post gets a random score boost (creates "hope" for lower tiers)
    if random.random() < 0.05:
        base_score += random.uniform(20, 40)

    return round(base_score, 2)


async def get_feed_for_user(
    db: AsyncSession, r: redis.Redis, user: User,
    limit: int = 20, offset: int = 0,
) -> list[Post]:
    """
    Build a ranked feed for this user.
    Uses the asymmetric distribution model.
    """
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=72)  # Only show posts from last 72h

    query = (
        select(Post)
        .where(Post.is_active == True, Post.created_at >= cutoff)
        .options(selectinload(Post.author))
        .order_by(desc(Post.created_at))
        .limit(200)  # Candidate pool
    )
    result = await db.execute(query)
    candidates = list(result.scalars().all())

    # Filter by tier-based distribution rules
    filtered = []
    for post in candidates:
        author_tier = post.author.tier if post.author else UserTier.B

        if user.tier == UserTier.A:
            # Tier A sees: all A posts, 40% of B posts, 10% of C posts
            if author_tier == UserTier.A:
                filtered.append(post)
            elif author_tier == UserTier.B and random.random() < 0.40:
                filtered.append(post)
            elif author_tier == UserTier.C and random.random() < 0.10:
                filtered.append(post)

        elif user.tier == UserTier.B:
            # Tier B sees: all A posts, all B posts, 30% of C posts
            if author_tier in (UserTier.A, UserTier.B):
                filtered.append(post)
            elif author_tier == UserTier.C and random.random() < 0.30:
                filtered.append(post)

        else:  # Tier C
            # Tier C sees: 60% of A posts, all B posts, all C posts
            if author_tier == UserTier.A:
                if random.random() < 0.60:
                    filtered.append(post)
            else:
                filtered.append(post)

    # Score and rank
    scored = []
    for post in filtered:
        score = await compute_post_feed_score(post, user.tier.value)
        scored.append((score, post))

    scored.sort(key=lambda x: x[0], reverse=True)

    # === CONTROLLED WINS: inject 1-2 tier C posts into top 10 for everyone ===
    if user.tier != UserTier.C and len(scored) > 10:
        c_posts = [s for s in scored if s[1].author and s[1].author.tier == UserTier.C]
        if c_posts:
            lucky = random.sample(c_posts, min(2, len(c_posts)))
            for item in lucky:
                scored.remove(item)
                insert_pos = random.randint(3, min(8, len(scored)))
                scored.insert(insert_pos, item)

    return [post for _, post in scored[offset:offset + limit]]
