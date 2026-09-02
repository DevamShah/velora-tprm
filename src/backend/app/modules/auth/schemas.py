"""
Auth Pydantic v2 request / response schemas.

All user-facing email is returned in plaintext (decrypted server-side).
No PII leaves the system in log-serialisable form.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

# ── Requests ──────────────────────────────────────────────────────────────


class LoginRequest(BaseModel):
    """Credentials for email + password authentication."""

    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class RefreshRequest(BaseModel):
    """Rotate an active refresh token."""

    refresh_token: str = Field(min_length=1)


# ── Responses ─────────────────────────────────────────────────────────────


class TokenResponse(BaseModel):
    """JWT pair returned on successful authentication."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(
        description="Access token lifetime in seconds"
    )


class RoleResponse(BaseModel):
    """Minimal role projection for user profile responses."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    permissions: list[str]


class UserResponse(BaseModel):
    """Public user profile — returned by /auth/me."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    first_name: str
    last_name: str
    is_active: bool
    mfa_enabled: bool
    last_login_at: datetime | None = None
    roles: list[RoleResponse] = []
    permissions: list[str] = []
