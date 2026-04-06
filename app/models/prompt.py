"""
Daily Prompts — structured prompts that rotate daily to drive participation.
Each day, users see fresh prompts they can respond to with video posts.
"""
import uuid
from datetime import datetime, timezone, date
from sqlalchemy import String, Integer, Boolean, DateTime, Date, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class DailyPrompt(Base):
    __tablename__ = "daily_prompts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    text: Mapped[str] = mapped_column(Text)  # e.g. "Convince me to cancel my date tonight"
    category: Mapped[str] = mapped_column(String(50))  # flirty, bold, funny, deep, chaotic
    active_date: Mapped[date] = mapped_column(Date, index=True)  # The day this prompt is live
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    total_responses: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


# Seed bank — prompts that get scheduled by the system
PROMPT_BANK = [
    # Flirty
    {"text": "Convince me to cancel my date tonight", "category": "flirty"},
    {"text": "Your best pickup line — but make it actually work", "category": "flirty"},
    {"text": "Show me the face you make when you see someone cute", "category": "flirty"},
    {"text": "You have 15 seconds to make me blush", "category": "flirty"},
    {"text": "What's your 'I just woke up' look?", "category": "flirty"},
    # Bold
    {"text": "Hot take that would make my friends argue", "category": "bold"},
    {"text": "Tell me something most people are too afraid to say on a first date", "category": "bold"},
    {"text": "Your most controversial opinion about relationships", "category": "bold"},
    {"text": "What's the boldest thing you've ever done for someone you liked?", "category": "bold"},
    {"text": "Roast my last relationship in 10 seconds", "category": "bold"},
    # Funny
    {"text": "Do your best impression of someone sliding into DMs", "category": "funny"},
    {"text": "Reenact the worst date you've ever been on", "category": "funny"},
    {"text": "Your toxic trait but make it funny", "category": "funny"},
    {"text": "POV: You just got caught stalking their Instagram", "category": "funny"},
    {"text": "Tell me your red flag like it's a flex", "category": "funny"},
    # Deep
    {"text": "What do you actually want in a relationship — no cap", "category": "deep"},
    {"text": "The one thing you wish someone would ask you on a date", "category": "deep"},
    {"text": "What's something that instantly makes you lose interest?", "category": "deep"},
    {"text": "Describe your ideal Sunday morning with someone", "category": "deep"},
    {"text": "What does love look like to you?", "category": "deep"},
    # Chaotic
    {"text": "Text your ex and show the reaction live", "category": "chaotic"},
    {"text": "Speed-date three imaginary people in 30 seconds", "category": "chaotic"},
    {"text": "Your dating life as a movie trailer — go", "category": "chaotic"},
    {"text": "Rate yourself 1-10 and explain — no modesty allowed", "category": "chaotic"},
    {"text": "Make me fall in love using only sound effects", "category": "chaotic"},
]
