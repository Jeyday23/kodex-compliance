from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://vibecrush:vibecrush@localhost:5432/vibecrush"
    REDIS_URL: str = "redis://localhost:6379/0"
    JWT_SECRET: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_MINUTES: int = 10080
    S3_ENDPOINT: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"
    S3_BUCKET: str = "vibecrush-videos"
    S3_REGION: str = "us-east-1"
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    MAX_VIDEO_DURATION_SECONDS: int = 30
    MAX_VIDEO_SIZE_MB: int = 50
    class Config:
        env_file = ".env"

@lru_cache
def get_settings() -> Settings:
    return Settings()
