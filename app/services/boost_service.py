"""
Boost Service — handles payment + boost activation.
"""
import stripe
from app.config import get_settings
from app.models.boost import BoostType

settings = get_settings()
stripe.api_key = settings.STRIPE_SECRET_KEY

# Pricing in cents (EUR)
BOOST_PRICES = {
    BoostType.REPLY_BOOST: 299,       # 2.99 EUR
    BoostType.POST_BOOST: 999,        # 9.99 EUR
    BoostType.SKIP_THE_LINE: 599,     # 5.99 EUR
    BoostType.RESURFACE: 199,         # 1.99 EUR
}

ELITE_PRICE_CENTS = 999  # 9.99 EUR/month


async def create_boost_payment_intent(
    user_stripe_id: str,
    boost_type: BoostType,
) -> dict:
    """Create a Stripe PaymentIntent for a boost purchase."""
    amount = BOOST_PRICES[boost_type]
    intent = stripe.PaymentIntent.create(
        amount=amount,
        currency="eur",
        customer=user_stripe_id,
        metadata={"boost_type": boost_type.value},
    )
    return {"client_secret": intent.client_secret, "amount_cents": amount, "intent_id": intent.id}


async def create_elite_subscription(user_stripe_id: str) -> dict:
    """Create recurring subscription for Elite Access."""
    # In production, use Stripe Checkout or a pre-created Price object
    session = stripe.checkout.Session.create(
        customer=user_stripe_id,
        mode="subscription",
        line_items=[{"price_data": {
            "currency": "eur",
            "product_data": {"name": "VibeCrush Elite Access"},
            "recurring": {"interval": "month"},
            "unit_amount": ELITE_PRICE_CENTS,
        }, "quantity": 1}],
        success_url="vibecrush://elite/success",
        cancel_url="vibecrush://elite/cancel",
    )
    return {"checkout_url": session.url, "session_id": session.id}
