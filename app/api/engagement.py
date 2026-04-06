from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, field_validator
from app.core.database import get_db
from app.core.auth import get_current_user
from app.core.redis import get_redis
from app.models.user import User
from app.models.post import Post
from app.models.like import PostLike
from app.config import get_settings
import redis.asyncio as redis

router = APIRouter(prefix="/engagement", tags=["engagement"])

MAX_WATCH_SECONDS = 300  # 5 min hard cap


class WatchEvent(BaseModel):
    post_id: str
    watch_seconds: int
    completed: bool = False

    @field_validator("watch_seconds")
    @classmethod
    def clamp_watch_seconds(cls, v: int) -> int:
        if v < 0:
            raise ValueError("watch_seconds cannot be negative")
        if v > MAX_WATCH_SECONDS:
            raise ValueError(f"watch_seconds cannot exceed {MAX_WATCH_SECONDS}")
        return v

    @field_validator("post_id")
    @classmethod
    def post_id_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("post_id is required")
        return v.strip()


@router.post("/watch")
async def track_watch(
    body: WatchEvent, user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db), r: redis.Redis = Depends(get_redis),
):
    settings = get_settings()

    result = await db.execute(select(Post).where(Post.id == body.post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Cap watch_seconds to actual video duration to prevent inflation
    capped_seconds = min(body.watch_seconds, post.duration_seconds) if post.duration_seconds > 0 else body.watch_seconds

    post.view_count += 1
    post.total_watch_time += capped_seconds
    if post.duration_seconds > 0:
        watch_pct = min(capped_seconds / post.duration_seconds, 1.0)
        post.avg_watch_pct = (post.avg_watch_pct * (post.view_count - 1) + watch_pct) / post.view_count
    await db.commit()

    await r.zincrby("clout:watch_time", capped_seconds, post.author_id)
    return {"status": "tracked"}


@router.post("/like/{post_id}")
async def like_post(
    post_id: str, user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Check post exists
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Prevent self-like
    if post.author_id == user.id:
        raise HTTPException(status_code=400, detail="Cannot like your own post")

    # Deduplicate likes
    existing = await db.execute(
        select(PostLike).where(PostLike.user_id == user.id, PostLike.post_id == post_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Already liked")

    like = PostLike(user_id=user.id, post_id=post_id)
    db.add(like)
    post.like_count += 1
    await db.commit()
    return {"status": "liked"}
