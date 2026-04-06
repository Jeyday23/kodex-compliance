"""
Conversations API — DMs unlocked by mutual interest (poster likes a reply).
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, or_, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.conversation import Conversation, Message
from app.models.notification import Notification, NotificationType
from app.schemas.conversation import ConversationOut, MessageOut, MessageIn
import uuid
from datetime import datetime, timezone

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("/", response_model=list[ConversationOut])
async def list_conversations(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """List all DM conversations for the current user."""
    result = await db.execute(
        select(Conversation)
        .where(
            or_(
                Conversation.post_author_id == user.id,
                Conversation.reply_author_id == user.id,
            ),
            Conversation.is_active == True,
        )
        .order_by(Conversation.created_at.desc())
    )
    convos = result.scalars().all()
    out = []
    for c in convos:
        partner = c.reply_author if c.post_author_id == user.id else c.post_author
        last_msg = c.messages[-1].body if c.messages else None
        unread = sum(1 for m in c.messages if not m.is_read and m.sender_id != user.id)
        out.append(ConversationOut(
            id=c.id,
            partner_id=partner.id,
            partner_name=partner.display_name,
            partner_avatar_key=partner.avatar_key,
            last_message=last_msg,
            unread_count=unread,
            created_at=c.created_at,
        ))
    return out


@router.get("/{conversation_id}/messages", response_model=list[MessageOut])
async def get_messages(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Get messages in a conversation. Marks unread as read."""
    convo = await db.get(Conversation, conversation_id)
    if not convo:
        raise HTTPException(404, "Conversation not found")
    if user.id not in (convo.post_author_id, convo.reply_author_id):
        raise HTTPException(403, "Not your conversation")

    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    )
    messages = result.scalars().all()

    # Mark unread messages as read
    for m in messages:
        if m.sender_id != user.id and not m.is_read:
            m.is_read = True
    await db.commit()

    return [
        MessageOut(
            id=m.id, sender_id=m.sender_id,
            sender_name=m.sender.display_name if m.sender else "",
            body=m.body, video_key=m.video_key,
            is_read=m.is_read, created_at=m.created_at,
        )
        for m in messages
    ]


@router.post("/{conversation_id}/messages", response_model=MessageOut)
async def send_message(
    conversation_id: str,
    payload: MessageIn,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Send a message in a conversation."""
    convo = await db.get(Conversation, conversation_id)
    if not convo:
        raise HTTPException(404, "Conversation not found")
    if user.id not in (convo.post_author_id, convo.reply_author_id):
        raise HTTPException(403, "Not your conversation")

    msg = Message(
        id=str(uuid.uuid4()),
        conversation_id=conversation_id,
        sender_id=user.id,
        body=payload.body,
        video_key=payload.video_key,
    )
    db.add(msg)
    await db.commit()
    await db.refresh(msg)

    return MessageOut(
        id=msg.id, sender_id=msg.sender_id,
        sender_name=user.display_name,
        body=msg.body, video_key=msg.video_key,
        is_read=msg.is_read, created_at=msg.created_at,
    )
