from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.auth import create_access_token
from app.models.user import User
from app.schemas.user import AuthRequest, AuthResponse
import uuid

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=AuthResponse)
async def login_or_register(body: AuthRequest, db: AsyncSession = Depends(get_db)):
    """
    Phone + OTP login. Tinder uses the same pattern (phone-first, no email).
    In MVP: any 6-digit OTP code is accepted.
    """
    # Find or create user
    result = await db.execute(select(User).where(User.phone == body.phone))
    user = result.scalar_one_or_none()
    is_new = False

    if not user:
        user = User(
            id=str(uuid.uuid4()),
            phone=body.phone,
            display_name=f"User_{body.phone[-4:]}",
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        is_new = True

    token = create_access_token(user.id)
    return AuthResponse(access_token=token, user_id=user.id, is_new_user=is_new)
