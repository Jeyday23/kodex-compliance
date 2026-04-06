"""
Clout Score Engine — the ranking heart of VibeCrush.

Similar to how Tinder's ELO/Desirability score worked:
- Tinder used a modified ELO: if a "high-rated" person swiped right on you, your score went up more.
- They later moved to a multi-factor system considering: right-swipe %, message rate, profile completeness.

VibeCrush Clout Score factors:
1. Watch time received (how long people watch YOUR videos)
2. Reply rate (how many replies your posts get)
3. Like rate (likes / views)
4. Selectivity bonus (responding to fewer people = higher perceived value)
5. Recency decay (recent engagement matters more)

Score range: 0-100
Tier thresholds: A >= 80, B >= 40, C < 40
"""
import redis.asyncio as redis
from datetime import datetime, timezone

# Weights — tune these to control the marketplace dynamics
WEIGHTS = {
    "watch_time": 0.30,      # Most important: are people actually watching?
    "reply_rate": 0.25,      # Do your posts generate responses?
    "like_rate": 0.20,       # Quality signal
    "selectivity": 0.15,     # Scarcity = value
    "recency": 0.10,         # Fresh activity bonus
}

TIER_THRESHOLDS = {"A": 80.0, "B": 40.0}


def compute_clout_score(
    avg_watch_pct: float,          # 0.0-1.0, avg % of video watched
    reply_rate: float,             # replies_received / posts_created
    like_rate: float,              # likes / views
    response_rate: float,          # how often they reply back (lower = more selective)
    days_since_last_active: int,
) -> float:
    """
    Compute raw clout score 0-100.
    This runs as a background job every ~hour, updating all users.
    """
    # Normalize each factor to 0-100
    watch_score = min(avg_watch_pct * 100, 100)
    reply_score = min(reply_rate * 10, 100)       # 10 replies/post = max
    like_score = min(like_rate * 200, 100)         # 50% like rate = max
    # Selectivity: lower response rate = higher score (playing hard to get)
    selectivity_score = max(0, (1.0 - response_rate) * 100)
    # Recency: decays over 30 days
    recency_score = max(0, 100 - (days_since_last_active * 3.33))

    score = (
        watch_score * WEIGHTS["watch_time"]
        + reply_score * WEIGHTS["reply_rate"]
        + like_score * WEIGHTS["like_rate"]
        + selectivity_score * WEIGHTS["selectivity"]
        + recency_score * WEIGHTS["recency"]
    )
    return round(min(max(score, 0), 100), 2)


def score_to_tier(score: float) -> str:
    if score >= TIER_THRESHOLDS["A"]:
        return "A"
    elif score >= TIER_THRESHOLDS["B"]:
        return "B"
    return "C"


async def update_user_clout_in_redis(r: redis.Redis, user_id: str, score: float):
    """
    Store clout score in Redis sorted set for fast feed ranking.
    Tinder uses Redis sorted sets for their recommendation queue — same pattern here.
    """
    await r.zadd("clout:scores", {user_id: score})
    tier = score_to_tier(score)
    # Add to tier sets for tier-based feed filtering
    for t in ["A", "B", "C"]:
        await r.srem(f"clout:tier:{t}", user_id)
    await r.sadd(f"clout:tier:{tier}", user_id)
