"""
VibeCrush — Clout Mode API

Video-first dating as an attention marketplace.
- FastAPI (async) = microservices layer
- PostgreSQL = persistent user/content storage
- Redis sorted sets = real-time ranking engine
- S3 = media pipeline
- Stripe = payment processing
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, users, posts, boosts, engagement
from app.api import prompts, conversations, notifications, verification, activity
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title="VibeCrush API",
    version="0.3.0",
    description="Clout Mode — Video Dating Attention Marketplace",
    docs_url="/docs" if settings.OTP_BYPASS_ENABLED else None,
    redoc_url=None,
)

allowed_origins = settings.get_allowed_origins()
if not allowed_origins:
    import logging
    logging.getLogger(__name__).warning(
        "ALLOWED_ORIGINS is empty — CORS will reject all cross-origin requests. "
        "Set ALLOWED_ORIGINS in .env (comma-separated)."
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)

# Core routes
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(posts.router)
app.include_router(boosts.router)
app.include_router(engagement.router)

# Feature routes
app.include_router(prompts.router)
app.include_router(conversations.router)
app.include_router(notifications.router)
app.include_router(verification.router)
app.include_router(activity.router)


@app.get("/health")
async def health():
    return {"status": "crushing it", "version": "0.3.0"}
