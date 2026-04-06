"""
User model — similar to Tinder's user entity.
Tinder stores users in PostgreSQL with Redis caching for active sessions.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Float, Integer, Boolean, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
import enum


class UserTier(str, enum.Enum):
    A = "A"   # Top ~10%
    B = "B"   # Middle ~60%
    C = "C"   # Bottom ~30%


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    phone: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(50))
    bio: Mapped[str] = mapped_column(String(500), default="")
    avatar_key: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Location (Tinder uses geohashing — we store lat/lng + compute geohash in Redis)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Clout system
    clout_score: Mapped[float] = mapped_column(Float, default=50.0)  # 0-100
    tier: Mapped[UserTier] = mapped_column(SAEnum(UserTier), default=UserTier.B)
    is_anchor: Mapped[bool] = mapped_column(Boolean, default=False)  # Hand-picked hot users

    # Engagement metrics (updated by background jobs)
    total_watch_time_received: Mapped[int] = mapped_column(Integer, default=0)  # seconds
    total_replies_received: Mapped[int] = mapped_column(Integer, default=0)
    total_likes_received: Mapped[int] = mapped_column(Integer, default=0)
    response_rate: Mapped[float] = mapped_column(Float, default=0.0)  # 0.0-1.0

    # Monetization
    boost_credits: Mapped[int] = mapped_column(Integer, default=0)
    is_elite: Mapped[bool] = mapped_column(Boolean, default=False)  # Paid subscriber
    total_spent_cents: Mapped[int] = mapped_column(Integer, default=0)

    # Stripe
    stripe_customer_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_active: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    posts = relationship("Post", back_populates="author", lazy="selectin")
