"""
Communications domain SQLAlchemy models.

Four tables: notifications, notification_preferences,
email_templates, communication_logs.
All tenant-scoped via TenantBase for RLS isolation.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import TenantBase


class Notification(TenantBase):
    """In-app or multi-channel notification to a user."""

    __tablename__ = "notifications"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    channel: Mapped[str] = mapped_column(
        String(20), nullable=False, default="in_app"
    )
    read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    read_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    entity_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    entity_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )


class NotificationPreference(TenantBase):
    """User notification preference per category."""

    __tablename__ = "notification_preferences"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    channel_config: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    quiet_hours_start: Mapped[str | None] = mapped_column(
        String(5), nullable=True
    )
    quiet_hours_end: Mapped[str | None] = mapped_column(
        String(5), nullable=True
    )


class EmailTemplate(TenantBase):
    """Email template with variable interpolation."""

    __tablename__ = "email_templates"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    subject_template: Mapped[str] = mapped_column(Text, nullable=False)
    body_template: Mapped[str] = mapped_column(Text, nullable=False)
    variables: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    is_system: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )


class CommunicationLog(TenantBase):
    """Log of outbound communications across channels."""

    __tablename__ = "communication_logs"

    channel: Mapped[str] = mapped_column(String(50), nullable=False)
    recipient: Mapped[str] = mapped_column(String(500), nullable=False)
    subject: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="sent"
    )
    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
