from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.auth import create_access_token
from app.models.user import User
from app.schemas.user import AuthRequest, AuthResponse
from app.config import get_settings
import uuid
import re
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])

# Strict E.164 phone validation
PHONE_REGEX = re.compile(r"^\+[1-9]\d{6,14}$")


@router.post("/login", response_model=AuthResponse)
async def login_or_register(body: AuthRequest, db: AsyncSession = Depends(get_db)):
    """
    Phone + OTP login. In production, OTP must be verified via
    a real provider (Twilio Verify, etc.). The bypass flag is
    for local dev/testing ONLY and is disabled by default.
    """
    settings = get_settings()

    # Validate phone format
    if not PHONE_REGEX.match(body.phone):
        raise HTTPException(status_code=422, detail="Invalid phone number format. Use E.164 (e.g. +14155551234)")

    # Validate OTP
    if not settings.OTP_BYPASS_ENABLED:
        # TODO: Replace with real OTP verification (e.g. Twilio Verify)
        # For now, reject all requests when bypass is disabled
        # to prevent the "any 6-digit code works" vulnerability.
        #
        # When you integrate a real OTP provider, replace this block:
        #   verified = await twilio_client.verify(body.phone, body.otp_code)
        #   if not verified:
        #       raise HTTPException(status_code=401, detail="Invalid OTP code")
        raise HTTPException(
            status_code=501,
            detail="OTP verification not yet configured. Set OTP_BYPASS_ENABLED=true for dev only."
        )
    else:
        # Dev bypass: still require a 6-digit code format
        otp_code = getattr(body, "otp_code", None)
        if not otp_code or not re.match(r"^\d{6}$", otp_code):
            raise HTTPException(status_code=422, detail="OTP must be exactly 6 digits")
        logger.warning("OTP bypass active — accepting any 6-digit code for %s", body.phone[-4:])

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
