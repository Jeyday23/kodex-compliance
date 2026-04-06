from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.boost import BoostPurchase, BoostType
from app.models.post import Post
from app.models.reply import Reply
from app.schemas.boost import BoostRequest, BoostPriceResponse, BoostPaymentResponse
from app.services.boost_service import BOOST_PRICES, create_boost_payment_intent
from datetime import datetime, timezone, timedelta
import stripe
from app.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/boosts", tags=["boosts"])


@router.get("/prices", response_model=list[BoostPriceResponse])
async def get_prices():
    return [
        BoostPriceResponse(boost_type=bt.value, price_cents=price)
        for bt, price in BOOST_PRICES.items()
    ]


@router.post("", response_model=BoostPaymentResponse)
async def purchase_boost(
    body: BoostRequest, user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        boost_type = BoostType(body.boost_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid boost type: {body.boost_type}")

    # Ensure Stripe customer exists
    if not user.stripe_customer_id:
        customer = stripe.Customer.create(metadata={"user_id": user.id})
        user.stripe_customer_id = customer.id
        await db.commit()

    payment = await create_boost_payment_intent(user.stripe_customer_id, boost_type)

    # Record purchase
    purchase = BoostPurchase(
        user_id=user.id, boost_type=boost_type, target_id=body.target_id,
        amount_cents=payment["amount_cents"], stripe_payment_intent_id=payment["intent_id"],
    )
    db.add(purchase)
    await db.commit()
    await db.refresh(purchase)

    return BoostPaymentResponse(
        client_secret=payment["client_secret"],
        boost_id=purchase.id, amount_cents=payment["amount_cents"],
    )


@router.post("/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Stripe webhook — activates boosts after successful payment.
    Webhook signature is ALWAYS verified — no bypass.
    """
    payload = await request.body()
    sig = request.headers.get("stripe-signature", "")

    if not settings.STRIPE_WEBHOOK_SECRET:
        raise HTTPException(status_code=500, detail="Webhook secret not configured")

    try:
        event = stripe.Webhook.construct_event(payload, sig, settings.STRIPE_WEBHOOK_SECRET)
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid webhook signature")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")

    if event["type"] == "payment_intent.succeeded":
        intent = event["data"]["object"]
        intent_id = intent["id"]

        # Find the purchase
        result = await db.execute(
            select(BoostPurchase).where(BoostPurchase.stripe_payment_intent_id == intent_id)
        )
        purchase = result.scalar_one_or_none()
        if not purchase:
            return {"status": "not_found"}

        # Activate the boost
        if purchase.boost_type in (BoostType.POST_BOOST, BoostType.SKIP_THE_LINE):
            r = await db.execute(select(Post).where(Post.id == purchase.target_id))
            post = r.scalar_one_or_none()
            if post:
                post.is_boosted = True
                post.boost_expires_at = datetime.now(timezone.utc) + timedelta(hours=6)
                if purchase.boost_type == BoostType.SKIP_THE_LINE:
                    post.boost_tier_target = "A"

        elif purchase.boost_type in (BoostType.REPLY_BOOST, BoostType.RESURFACE):
            r = await db.execute(select(Reply).where(Reply.id == purchase.target_id))
            reply = r.scalar_one_or_none()
            if reply:
                reply.is_boosted = True
                reply.rank_score += 50
                if purchase.boost_type == BoostType.RESURFACE:
                    reply.is_seen = False

        # Update user spend tracking
        r = await db.execute(select(User).where(User.id == purchase.user_id))
        user = r.scalar_one_or_none()
        if user:
            user.total_spent_cents += purchase.amount_cents

        await db.commit()

    return {"status": "ok"}
