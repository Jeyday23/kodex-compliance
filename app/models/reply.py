"""
Reply = a video response to a Post. This is the core interaction.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, Float, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class Reply(Base):
    __tablename__ = "replies"
    __table_args__ = (UniqueConstraint("author_id", "post_id", name="uq_user_post_reply"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    post_id: Mapped[str] = mapped_column(String(36), ForeignKey("posts.id"), index=True)
    author_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    video_key: Mapped[str] = mapped_column(String(255))
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0)

    # Ranking within the post's reply list
    rank_score: Mapped[float] = mapped_column(Float, default=0.0)
    is_boosted: Mapped[bool] = mapped_column(Boolean, default=False)  # Paid boost
    boost_amount_cents: Mapped[int] = mapped_column(Integer, default=0)

    # Engagement
    like_count: Mapped[int] = mapped_column(Integer, default=0)
    watch_time: Mapped[int] = mapped_column(Integer, default=0)

    # Status
    is_seen: Mapped[bool] = mapped_column(Boolean, default=False)
    is_liked_by_poster: Mapped[bool] = mapped_column(Boolean, default=False)  # "Match" signal
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    post = relationship("Post", back_populates="replies")
    author = relationship("User", lazy="selectin")
