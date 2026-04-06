from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from pydantic import BaseModel
from app.core.database import get_db
from app.core.auth import get_current_user
from app.core.redis import get_redis
from app.models.user import User
from app.models.post import Post
from app.models.like import PostLike
import redis.asyncio as redis

router = APIRouter(prefix="/engagement", tags=["engagement"])


class WatchEvent(BaseModel):
    post_id: str
    watch_seconds: int
    completed: bool = False


@router.post("/watch")
async def track_watch(
    body: WatchEvent, user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db), r: redis.Redis = Depends(get_redis),
):
    if body.watch_seconds < 0:
        raise HTTPException(status_code=400, detail="Invalid watch time")

    result = await db.execute(select(Post).where(Post.id == body.post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    post.view_count += 1
    post.total_watch_time += body.watch_seconds
    if post.duration_seconds > 0:
        watch_pct = min(body.watch_seconds / post.duration_seconds, 1.0)
        post.avg_watch_pct = (post.avg_watch_pct * (post.view_count - 1) + watch_pct) / post.view_count
    await db.commit()

    await r.zincrby("clout:watch_time", body.watch_seconds, post.author_id)
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
