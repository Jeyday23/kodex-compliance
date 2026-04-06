from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.core.auth import get_current_user
from app.core.storage import generate_playback_url, generate_upload_url
from app.core.redis import get_redis
from app.models.user import User
from app.models.post import Post
from app.models.reply import Reply
from app.schemas.post import PostCreate, PostResponse, ReplyCreate, ReplyResponse
from app.services.feed_engine import get_feed_for_user
import redis.asyncio as redis

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("/upload-url")
async def get_upload_url(user: User = Depends(get_current_user)):
    """Get a presigned S3 URL to upload a video. Client uploads directly to S3."""
    return generate_upload_url(prefix="posts")


@router.post("", response_model=PostResponse)
async def create_post(
    body: PostCreate, user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    post = Post(author_id=user.id, video_key=body.video_key,
                prompt_text=body.prompt_text, duration_seconds=body.duration_seconds)
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return PostResponse(
        id=post.id, author_id=user.id, author_name=user.display_name,
        author_tier=user.tier.value, video_url=generate_playback_url(post.video_key),
        prompt_text=post.prompt_text, view_count=0, reply_count=0, like_count=0,
        is_boosted=False, created_at=post.created_at,
    )


@router.get("/feed", response_model=list[PostResponse])
async def get_feed(
    limit: int = Query(20, le=50), offset: int = Query(0),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    r: redis.Redis = Depends(get_redis),
):
    posts = await get_feed_for_user(db, r, user, limit, offset)
    return [
        PostResponse(
            id=p.id, author_id=p.author_id, author_name=p.author.display_name,
            author_tier=p.author.tier.value, video_url=generate_playback_url(p.video_key),
            prompt_text=p.prompt_text, view_count=p.view_count, reply_count=p.reply_count,
            like_count=p.like_count, is_boosted=p.is_boosted, created_at=p.created_at,
        ) for p in posts
    ]


@router.post("/{post_id}/replies", response_model=ReplyResponse)
async def create_reply(
    post_id: str, body: ReplyCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify post exists
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Post not found")

    # Prevent self-reply
    if post.author_id == user.id:
        raise HTTPException(status_code=400, detail="Cannot reply to your own post")

    # Prevent duplicate reply
    existing = await db.execute(
        select(Reply).where(Reply.author_id == user.id, Reply.post_id == post_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Already replied to this post")

    reply = Reply(post_id=post_id, author_id=user.id, video_key=body.video_key,
                  duration_seconds=body.duration_seconds, rank_score=user.clout_score)
    db.add(reply)
    post.reply_count += 1
    await db.commit()
    await db.refresh(reply)
    return ReplyResponse(
        id=reply.id, post_id=post_id, author_id=user.id, author_name=user.display_name,
        video_url=generate_playback_url(reply.video_key), rank_score=reply.rank_score,
        is_boosted=False, like_count=0, is_seen=False, is_liked_by_poster=False,
        created_at=reply.created_at,
    )


@router.get("/{post_id}/replies", response_model=list[ReplyResponse])
async def get_replies(
    post_id: str, user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get replies ranked by score. Boosted replies appear first."""
    result = await db.execute(
        select(Reply)
        .options(selectinload(Reply.author))
        .where(Reply.post_id == post_id, Reply.is_active == True)
        .order_by(desc(Reply.is_boosted), desc(Reply.rank_score))
    )
    replies = result.scalars().all()
    return [
        ReplyResponse(
            id=r.id, post_id=r.post_id, author_id=r.author_id,
            author_name=r.author.display_name if r.author else "Unknown",
            video_url=generate_playback_url(r.video_key), rank_score=r.rank_score,
            is_boosted=r.is_boosted, like_count=r.like_count, is_seen=r.is_seen,
            is_liked_by_poster=r.is_liked_by_poster, created_at=r.created_at,
        ) for r in replies
    ]


@router.post("/{post_id}/replies/{reply_id}/like")
async def like_reply(
    post_id: str, reply_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Post author likes a reply — this is the 'match' signal."""
    # Verify the liker is the post author
    post_result = await db.execute(select(Post).where(Post.id == post_id))
    post = post_result.scalar_one_or_none()
    if not post or post.author_id != user.id:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Only the post author can like replies")

    result = await db.execute(select(Reply).where(Reply.id == reply_id, Reply.post_id == post_id))
    reply = result.scalar_one_or_none()
    if not reply:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Reply not found")
    reply.is_liked_by_poster = True
    reply.like_count += 1
    await db.commit()
    return {"status": "liked"}
