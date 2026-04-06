"""
Real-user verification API — selfie upload + liveness check.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.auth import get_current_user
from app.core.storage import get_storage
from app.models.verification import UserVerification, VerificationStatus
import uuid

router = APIRouter(prefix="/verification", tags=["verification"])


@router.post("/submit")
async def submit_verification(
    selfie: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
    storage=Depends(get_storage),
):
    """Submit a verification selfie. System checks for liveness."""
    # Check if already verified
    existing = await db.execute(
        select(UserVerification)
        .where(
            UserVerification.user_id == user.id,
            UserVerification.status == VerificationStatus.APPROVED,
        )
    )
    if existing.scalars().first():
        return {"status": "already_verified"}

    # Upload selfie to S3
    key = f"verification/{user.id}/{uuid.uuid4()}.jpg"
    content = await selfie.read()
    await storage.upload(key, content, content_type="image/jpeg")

    verification = UserVerification(
        id=str(uuid.uuid4()),
        user_id=user.id,
        selfie_key=key,
        status=VerificationStatus.PENDING,
    )
    db.add(verification)
    await db.commit()

    return {"status": "submitted", "verification_id": verification.id}


@router.get("/status")
async def verification_status(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    """Check the user's verification status."""
    result = await db.execute(
        select(UserVerification)
        .where(UserVerification.user_id == user.id)
        .order_by(UserVerification.created_at.desc())
        .limit(1)
    )
    v = result.scalars().first()
    if not v:
        return {"status": "not_submitted"}
    return {"status": v.status.value, "submitted_at": v.created_at.isoformat()}
