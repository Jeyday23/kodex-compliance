"""
Post = a video dating prompt.
Think of it like a Tinder card but video-first + prompt-driven.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    author_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    video_key: Mapped[str] = mapped_column(String(255))  # S3 key
    thumbnail_key: Mapped[str | None] = mapped_column(String(255), nullable=True)
    prompt_text: Mapped[str] = mapped_column(Text)  # "Convince me to cancel my date tonight"
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0)

    # Engagement counters (denormalized for speed — Tinder does this too)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    reply_count: Mapped[int] = mapped_column(Integer, default=0)
    like_count: Mapped[int] = mapped_column(Integer, default=0)
    total_watch_time: Mapped[int] = mapped_column(Integer, default=0)  # seconds across all viewers
    avg_watch_pct: Mapped[float] = mapped_column(Float, default=0.0)

    # Boost state
    is_boosted: Mapped[bool] = mapped_column(Boolean, default=False)
    boost_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    boost_tier_target: Mapped[str | None] = mapped_column(String(1), nullable=True)  # "A", "B"

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, default=lambda: datetime.now(timezone.utc))

    author = relationship("User", back_populates="posts", lazy="selectin")
    replies = relationship("Reply", back_populates="post", lazy="selectin")
