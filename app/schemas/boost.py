from pydantic import BaseModel

class BoostRequest(BaseModel):
    boost_type: str  # reply_boost, post_boost, skip_the_line, resurface
    target_id: str   # post or reply id

class BoostPriceResponse(BaseModel):
    boost_type: str
    price_cents: int
    currency: str = "eur"

class BoostPaymentResponse(BaseModel):
    client_secret: str
    boost_id: str
    amount_cents: int
