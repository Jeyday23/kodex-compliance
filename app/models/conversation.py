"""
Conversations & Messages — unlocked when a poster likes a reply (mutual interest).
This is the VibeCrush equivalent of a Tinder "match", except it's earned through
public performance, not passive swiping.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Conversation(Base):
    """Created when a post author likes a reply — both users can now DM."""
    __tablename__ = "conversations"
    __table_args__ = (
        UniqueConstraint("post_author_id", "reply_author_id", name="uq_conversation_pair"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    post_author_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    reply_author_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    post_id: Mapped[str] = mapped_column(String(36), ForeignKey("posts.id"))
    reply_id: Mapped[str] = mapped_column(String(36), ForeignKey("replies.id"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    messages = relationship("Message", back_populates="conversation", lazy="selectin")
    post_author = relationship("User", foreign_keys=[post_author_id], lazy="selectin")
    reply_author = relationship("User", foreign_keys=[reply_author_id], lazy="selectin")


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id: Mapped[str] = mapped_column(String(36), ForeignKey("conversations.id"), index=True)
    sender_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    body: Mapped[str] = mapped_column(Text)
    video_key: Mapped[str | None] = mapped_column(String(255), nullable=True)  # Optional video message
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    conversation = relationship("Conversation", back_populates="messages")
    sender = relationship("User", lazy="selectin")
