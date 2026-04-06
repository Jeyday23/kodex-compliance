import secrets
from pydantic_settings import BaseSettings
from pydantic import field_validator
from functools import lru_cache


class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379/0"
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_MINUTES: int = 10080
    S3_ENDPOINT: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    S3_BUCKET: str = "vibecrush-videos"
    S3_REGION: str = "us-east-1"
    STRIPE_SECRET_KEY: str
    STRIPE_WEBHOOK_SECRET: str
    ALLOWED_ORIGINS: str = ""
    MAX_VIDEO_DURATION_SECONDS: int = 30
    MAX_VIDEO_SIZE_MB: int = 50
    OTP_BYPASS_ENABLED: bool = False

    @field_validator("JWT_SECRET")
    @classmethod
    def jwt_secret_must_be_strong(cls, v: str) -> str:
        if v in ("change-me", "", "secret", "test"):
            raise ValueError(
                "JWT_SECRET is insecure. Set a strong random secret "
                "(hint: python -c \"import secrets; print(secrets.token_urlsafe(64))\")"
            )
        if len(v) < 32:
            raise ValueError("JWT_SECRET must be at least 32 characters")
        return v

    @field_validator("STRIPE_SECRET_KEY")
    @classmethod
    def stripe_key_must_exist(cls, v: str) -> str:
        if not v:
            raise ValueError("STRIPE_SECRET_KEY must be set")
        return v

    @field_validator("STRIPE_WEBHOOK_SECRET")
    @classmethod
    def stripe_webhook_must_exist(cls, v: str) -> str:
        if not v:
            raise ValueError("STRIPE_WEBHOOK_SECRET must be set")
        return v

    def get_allowed_origins(self) -> list[str]:
        if not self.ALLOWED_ORIGINS:
            return []
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
