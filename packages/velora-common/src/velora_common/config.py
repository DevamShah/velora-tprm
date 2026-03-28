"""
Base service configuration via environment variables.

Each microservice extends BaseServiceSettings with its own fields.
Uses Pydantic Settings for type-safe configuration with validation.
"""

from __future__ import annotations

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseServiceSettings(BaseSettings):
    """Base configuration shared by all Velora TPRM services."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    APP_NAME: str = "Velora Service"
    APP_VERSION: str = "2.0.0"
    LOG_LEVEL: str = "INFO"

    # Database — required, no default
    DATABASE_URL: str = Field(
        ..., description="Async PostgreSQL connection string"
    )

    # Redis — required for caching and rate limiting
    REDIS_URL: str = Field(
        ..., description="Redis connection string"
    )

    # S3-compatible object storage
    S3_ENDPOINT: str = Field(
        ..., description="S3-compatible endpoint URL"
    )
    S3_BUCKET: str = Field(
        ..., description="S3 bucket name for file storage"
    )

    # JWT authentication
    JWT_SECRET_KEY: str = Field(
        ...,
        min_length=32,
        description="Secret key for signing JWTs",
    )
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    JWT_ALGORITHM: str = "HS256"

    # Field-level AES-256-GCM encryption for PII
    ENCRYPTION_KEY: str = Field(
        ...,
        min_length=32,
        description="Base64-encoded 256-bit key for AES-256-GCM",
    )

    # CORS
    CORS_ORIGINS: list[str] = Field(
        default=["http://localhost:3000"],
        description="Allowed CORS origins",
    )

    # Optional LLM provider keys
    ANTHROPIC_API_KEY: str | None = None
    OPENAI_API_KEY: str | None = None

    # Sentry (optional)
    SENTRY_DSN: str | None = None

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        """Ensure the database URL uses the async driver."""
        if not value.startswith("postgresql+asyncpg://"):
            raise ValueError(
                "DATABASE_URL must use the asyncpg driver "
                "(postgresql+asyncpg://...)"
            )
        return value

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, value: str) -> str:
        """Restrict log level to standard choices."""
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        upper = value.upper()
        if upper not in allowed:
            raise ValueError(
                f"LOG_LEVEL must be one of {allowed}"
            )
        return upper
