"""
Boost purchase records — the money engine.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
import enum


class BoostType(str, enum.Enum):
    REPLY_BOOST = "reply_boost"       # Push reply to top slots (2-5 EUR)
    POST_BOOST = "post_boost"         # Show post to higher tiers (5-15 EUR)
    SKIP_THE_LINE = "skip_the_line"   # Appear in Tier A top responses (3-10 EUR)
    RESURFACE = "resurface"           # Re-show after "seen but ignored" (1-3 EUR)


class BoostPurchase(Base):
    __tablename__ = "boost_purchases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    boost_type: Mapped[BoostType] = mapped_column(SAEnum(BoostType))
    target_id: Mapped[str] = mapped_column(String(36))  # post_id or reply_id
    amount_cents: Mapped[int] = mapped_column(Integer)
    stripe_payment_intent_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
