"""
Auth domain SQLAlchemy models.

User email is encrypted at rest (AES-256-GCM) with an HMAC hash
column for lookups. Passwords use bcrypt cost-12. Refresh tokens
are stored hashed to prevent theft via DB compromise.
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from velora_common.models import Base, TenantBase


class Tenant(Base):
    """Top-level tenant / organisation."""

    __tablename__ = "tenants"

    name: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    slug: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )


class User(TenantBase):
    """Application user with encrypted PII."""

    __tablename__ = "users"

    # Encrypted email + deterministic hash for WHERE lookups
    email_encrypted: Mapped[str] = mapped_column(
        Text, nullable=False
    )
    email_hash: Mapped[str] = mapped_column(
        String(64), nullable=False, index=True
    )

    first_name: Mapped[str] = mapped_column(
        String(100), nullable=False
    )
    last_name: Mapped[str] = mapped_column(
        String(100), nullable=False
    )
    password_hash: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    last_login_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    mfa_enabled: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    notification_preferences: Mapped[Optional[Dict]] = mapped_column(
        JSONB, nullable=True, default=dict
    )
    sso_provider: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )
    sso_provider_id: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )

    # Relationships
    user_roles: Mapped[List["UserRole"]] = relationship(
        back_populates="user", lazy="selectin"
    )


class Role(TenantBase):
    """RBAC role with a list of permission strings."""

    __tablename__ = "roles"

    name: Mapped[str] = mapped_column(
        String(100), nullable=False
    )
    description: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True
    )
    permissions: Mapped[List[str]] = mapped_column(
        ARRAY(String), nullable=False, default=list
    )
    is_system: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    is_default: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    # Relationships
    user_roles: Mapped[List["UserRole"]] = relationship(
        back_populates="role", lazy="selectin"
    )


class UserRole(Base):
    """Many-to-many join between users and roles."""

    __tablename__ = "user_roles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    granted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    granted_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="user_roles")
    role: Mapped["Role"] = relationship(back_populates="user_roles")


class RefreshToken(TenantBase):
    """Persisted refresh token — stored as a hash."""

    __tablename__ = "refresh_tokens"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    token_hash: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    revoked_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    device_info: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True
    )
