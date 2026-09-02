"""
Admin domain SQLAlchemy models.

Audit log table for tracking all user actions.
Tenant-scoped via TenantBase for RLS isolation.
"""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import TenantBase


class AuditLog(TenantBase):
    """Immutable record of a user action."""

    __tablename__ = "audit_logs"

    user_id: Mapped[uuid.UUID | None] = (
        mapped_column(
            UUID(as_uuid=True),
            ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        )
    )
    action: Mapped[str] = mapped_column(
        Text, nullable=False
    )
    entity_type: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    entity_id: Mapped[uuid.UUID | None] = (
        mapped_column(
            UUID(as_uuid=True), nullable=True
        )
    )
    details: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True
    )
    ip_address: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
