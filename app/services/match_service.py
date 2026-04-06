"""
Match Service — when a post author likes a reply, it creates a
conversation (DM unlock). This is the core matching mechanic.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.reply import Reply
from app.models.conversation import Conversation
from app.models.notification import Notification, NotificationType


async def handle_reply_like(
    db: AsyncSession,
    post_author_id: str,
    reply_id: str,
) -> Conversation | None:
    """
    Called when a post author likes a reply.
    Creates a Conversation (DM unlock) and notifies both users.
    """
    reply = await db.get(Reply, reply_id)
    if not reply:
        return None

    reply.is_liked_by_poster = True

    # Check if conversation already exists
    existing = await db.execute(
        select(Conversation).where(
            Conversation.post_author_id == post_author_id,
            Conversation.reply_author_id == reply.author_id,
        )
    )
    if existing.scalars().first():
        await db.commit()
        return existing.scalars().first()

    # Create conversation
    convo = Conversation(
        id=str(uuid.uuid4()),
        post_author_id=post_author_id,
        reply_author_id=reply.author_id,
        post_id=reply.post_id,
        reply_id=reply.id,
    )
    db.add(convo)

    # Notify both users
    for uid, title, body in [
        (reply.author_id, "It's a match! 🔥", "Your reply caught their eye — DMs are open!"),
        (post_author_id, "Match unlocked! 💬", "You liked their reply — start the conversation!"),
    ]:
        db.add(Notification(
            id=str(uuid.uuid4()),
            user_id=uid,
            type=NotificationType.MATCH_CREATED,
            title=title,
            body=body,
            related_user_id=post_author_id if uid == reply.author_id else reply.author_id,
            related_post_id=reply.post_id,
        ))

    await db.commit()
    return convo
