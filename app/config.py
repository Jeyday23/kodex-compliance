import sys
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://vibecrush:vibecrush@localhost:5432/vibecrush"
    REDIS_URL: str = "redis://localhost:6379/0"
    JWT_SECRET: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_MINUTES: int = 60  # 1 hour — was 7 days
    S3_ENDPOINT: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = ""
    S3_SECRET_KEY: str = ""
    S3_BUCKET: str = "vibecrush-videos"
    S3_REGION: str = "us-east-1"
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    MAX_VIDEO_DURATION_SECONDS: int = 30
    MAX_VIDEO_SIZE_MB: int = 50
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    class Config:
        env_file = ".env"


INSECURE_DEFAULTS = {"change-me", "change-me-to-a-long-random-secret", ""}


@lru_cache
def get_settings() -> Settings:
    s = Settings()
    # Block startup with insecure secrets
    if s.JWT_SECRET in INSECURE_DEFAULTS or len(s.JWT_SECRET) < 32:
        print("FATAL: JWT_SECRET is missing or insecure. Set a random string >= 32 chars.")
        sys.exit(1)
    if s.STRIPE_SECRET_KEY and not s.STRIPE_WEBHOOK_SECRET:
        print("FATAL: STRIPE_WEBHOOK_SECRET must be set when STRIPE_SECRET_KEY is configured.")
        sys.exit(1)
    return s
