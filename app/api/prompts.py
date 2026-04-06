"""
Daily Prompts API — drives daily participation through structured prompts.
"""
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.prompt import DailyPrompt, PROMPT_BANK
from app.schemas.prompt import DailyPromptOut
import uuid

router = APIRouter(prefix="/prompts", tags=["prompts"])


@router.get("/today", response_model=list[DailyPromptOut])
async def get_todays_prompts(db: AsyncSession = Depends(get_db)):
    """Get today's active prompts — 3 per day from different categories."""
    today = date.today()
    result = await db.execute(
        select(DailyPrompt)
        .where(DailyPrompt.active_date == today, DailyPrompt.is_active == True)
        .order_by(DailyPrompt.sort_order)
    )
    prompts = result.scalars().all()

    # Auto-generate if none exist for today (self-healing)
    if not prompts:
        prompts = await _seed_daily_prompts(db, today)

    return prompts


@router.get("/history", response_model=list[DailyPromptOut])
async def get_prompt_history(
    days: int = 7,
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    """Get recent prompts (last N days) for browsing older threads."""
    cutoff = date.today() - timedelta(days=days)
    result = await db.execute(
        select(DailyPrompt)
        .where(DailyPrompt.active_date >= cutoff, DailyPrompt.is_active == True)
        .order_by(DailyPrompt.active_date.desc(), DailyPrompt.sort_order)
    )
    return result.scalars().all()


async def _seed_daily_prompts(db: AsyncSession, target_date: date) -> list[DailyPrompt]:
    """Pick 3 prompts from different categories for the day."""
    import random
    categories = ["flirty", "bold", "funny", "deep", "chaotic"]
    selected_cats = random.sample(categories, 3)
    prompts = []
    for i, cat in enumerate(selected_cats):
        pool = [p for p in PROMPT_BANK if p["category"] == cat]
        chosen = random.choice(pool)
        prompt = DailyPrompt(
            id=str(uuid.uuid4()),
            text=chosen["text"],
            category=cat,
            active_date=target_date,
            sort_order=i,
        )
        db.add(prompt)
        prompts.append(prompt)
    await db.commit()
    return prompts
