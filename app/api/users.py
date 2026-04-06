from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.auth import get_current_user
from app.core.storage import generate_playback_url
from app.models.user import User
from app.schemas.user import UserProfile, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserProfile)
async def get_me(user: User = Depends(get_current_user)):
    avatar_url = generate_playback_url(user.avatar_key) if user.avatar_key else None
    return UserProfile(
        id=user.id, display_name=user.display_name, bio=user.bio,
        avatar_url=avatar_url, clout_score=user.clout_score,
        tier=user.tier.value, is_anchor=user.is_anchor, is_elite=user.is_elite,
    )

@router.patch("/me", response_model=UserProfile)
async def update_me(
    body: UserUpdate, user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    await db.commit()
    await db.refresh(user)
    avatar_url = generate_playback_url(user.avatar_key) if user.avatar_key else None
    return UserProfile(
        id=user.id, display_name=user.display_name, bio=user.bio,
        avatar_url=avatar_url, clout_score=user.clout_score,
        tier=user.tier.value, is_anchor=user.is_anchor, is_elite=user.is_elite,
    )
