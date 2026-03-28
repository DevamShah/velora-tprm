"""
BFF service configuration.

Extends base settings with BFF-specific service URLs and session config.
Does NOT inherit database fields — the BFF has no direct DB access.
"""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BFFSettings(BaseSettings):
    """Configuration for the Backend-for-Frontend service."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    APP_NAME: str = "Velora BFF Service"
    APP_VERSION: str = "2.0.0"
    LOG_LEVEL: str = "INFO"

    # Redis — session storage
    REDIS_URL: str = Field(
        default="redis://redis:6379/1",
        description="Redis connection string for session storage",
    )

    # Session
    SESSION_COOKIE_NAME: str = "velora_session"
    SESSION_EXPIRE_SECONDS: int = Field(
        default=604800,  # 7 days — matches refresh token expiry
        description="Session TTL in seconds",
    )
    SESSION_COOKIE_SECURE: bool = Field(
        default=False,
        description="Set True in production (requires HTTPS)",
    )
    SESSION_COOKIE_DOMAIN: str | None = None

    # Upstream service base URLs
    AUTH_SERVICE_URL: str = "http://auth-service:8000"
    VENDOR_SERVICE_URL: str = "http://vendor-service:8000"
    ASSESSMENT_SERVICE_URL: str = "http://assessment-engine:8000"
    FRAMEWORK_SERVICE_URL: str = "http://framework-service:8000"
    SCORING_SERVICE_URL: str = "http://scoring-engine:8000"
    EVIDENCE_SERVICE_URL: str = "http://evidence-service:8000"
    MONITORING_SERVICE_URL: str = "http://monitoring-service:8000"
    FINDING_SERVICE_URL: str = "http://finding-service:8000"
    COMMUNICATION_SERVICE_URL: str = "http://communication-hub:8000"
    REPORTING_SERVICE_URL: str = "http://reporting-service:8000"
    ADMIN_SERVICE_URL: str = "http://admin-service:8000"
    AI_SERVICE_URL: str = "http://ai-service:8000"

    # CORS
    CORS_ORIGINS: list[str] = Field(
        default=["http://localhost:3000"],
        description="Allowed CORS origins",
    )

    def service_url_for_prefix(self, prefix: str) -> str | None:
        """Map a URL path prefix to its upstream service URL."""
        mapping: dict[str, str] = {
            "/api/v1/auth": self.AUTH_SERVICE_URL,
            "/api/v1/vendors": self.VENDOR_SERVICE_URL,
            "/api/v1/assessments": self.ASSESSMENT_SERVICE_URL,
            "/api/v1/frameworks": self.FRAMEWORK_SERVICE_URL,
            "/api/v1/scoring": self.SCORING_SERVICE_URL,
            "/api/v1/evidence": self.EVIDENCE_SERVICE_URL,
            "/api/v1/monitoring": self.MONITORING_SERVICE_URL,
            "/api/v1/findings": self.FINDING_SERVICE_URL,
            "/api/v1/communications": self.COMMUNICATION_SERVICE_URL,
            "/api/v1/reports": self.REPORTING_SERVICE_URL,
            "/api/v1/admin": self.ADMIN_SERVICE_URL,
            "/api/v1/ai": self.AI_SERVICE_URL,
        }
        for route_prefix, url in mapping.items():
            if prefix.startswith(route_prefix):
                return url
        return None


_settings: BFFSettings | None = None


def get_settings() -> BFFSettings:
    """Singleton accessor — avoids re-parsing env on every request."""
    global _settings
    if _settings is None:
        _settings = BFFSettings()  # type: ignore[call-arg]
    return _settings
