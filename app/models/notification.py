"""
Notifications — real-time engagement alerts that drive the behavior loop.
visibility → effort → engagement → monetization
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
import enum


class NotificationType(str, enum.Enum):
    NEW_REPLY = "new_reply"           # Someone replied to your post
    REPLY_LIKED = "reply_liked"       # Post author liked your reply → match!
    POST_LIKED = "post_liked"         # Someone liked your post
    MATCH_CREATED = "match_created"   # DM unlocked
    CLOUT_SPIKE = "clout_spike"       # Your visibility just spiked
    DAILY_PROMPT = "daily_prompt"     # New prompts available
    BOOST_EXPIRED = "boost_expired"   # Your boost has ended
    STREAK_REMINDER = "streak_reminder"  # Don't lose your participation streak


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    type: Mapped[NotificationType] = mapped_column(SAEnum(NotificationType))
    title: Mapped[str] = mapped_column(String(200))
    body: Mapped[str] = mapped_column(Text)
    related_user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    related_post_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("posts.id"), nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", foreign_keys=[user_id], lazy="selectin")
