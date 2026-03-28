"""
Monitoring domain SQLAlchemy models.

Five tables: monitoring_configs, monitoring_signals, alerts,
alert_rules, vendor_timelines. All tenant-scoped via TenantBase.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import (
    ARRAY,
    JSONB,
    UUID,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import TenantBase


class MonitoringConfig(TenantBase):
    """Configuration for a monitoring source."""

    __tablename__ = "monitoring_configs"

    vendor_id: Mapped[Optional[uuid.UUID]] = (
        mapped_column(
            UUID(as_uuid=True),
            ForeignKey(
                "vendors.id", ondelete="CASCADE"
            ),
            nullable=True,
            index=True,
        )
    )
    source: Mapped[str] = mapped_column(
        Text, nullable=False
    )
    frequency_hours: Mapped[int] = mapped_column(
        Integer, nullable=False, default=24
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    last_polled_at: Mapped[Optional[datetime]] = (
        mapped_column(
            DateTime(timezone=True), nullable=True
        )
    )


class MonitoringSignal(TenantBase):
    """Raw signal from a monitoring source."""

    __tablename__ = "monitoring_signals"

    vendor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vendors.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    source: Mapped[str] = mapped_column(
        Text, nullable=False
    )
    signal_type: Mapped[str] = mapped_column(
        Text, nullable=False
    )
    severity: Mapped[str] = mapped_column(
        String(50), nullable=False, default="info"
    )
    title: Mapped[str] = mapped_column(
        String(500), nullable=False
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )
    raw_data: Mapped[Optional[Dict]] = mapped_column(
        JSONB, nullable=True
    )
    dedup_key: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )
    processed: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )


class Alert(TenantBase):
    """Actionable alert created from one or more signals."""

    __tablename__ = "alerts"

    vendor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vendors.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    priority: Mapped[str] = mapped_column(
        String(20), nullable=False, default="p3"
    )
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="new"
    )
    title: Mapped[str] = mapped_column(
        String(500), nullable=False
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )
    signal_ids: Mapped[Optional[List[uuid.UUID]]] = (
        mapped_column(
            ARRAY(UUID(as_uuid=True)), nullable=True
        )
    )
    impact_assessment: Mapped[Optional[Dict]] = (
        mapped_column(JSONB, nullable=True)
    )
    acknowledged_by: Mapped[Optional[uuid.UUID]] = (
        mapped_column(
            UUID(as_uuid=True),
            ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        )
    )
    resolved_by: Mapped[Optional[uuid.UUID]] = (
        mapped_column(
            UUID(as_uuid=True),
            ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        )
    )
    acknowledged_at: Mapped[Optional[datetime]] = (
        mapped_column(
            DateTime(timezone=True), nullable=True
        )
    )
    resolved_at: Mapped[Optional[datetime]] = (
        mapped_column(
            DateTime(timezone=True), nullable=True
        )
    )
    resolution_notes: Mapped[Optional[str]] = (
        mapped_column(Text, nullable=True)
    )


class AlertRule(TenantBase):
    """Rule that generates alerts from signals."""

    __tablename__ = "alert_rules"

    name: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )
    conditions: Mapped[Dict] = mapped_column(
        JSONB, nullable=False
    )
    actions: Mapped[Dict] = mapped_column(
        JSONB, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )


class VendorTimeline(TenantBase):
    """Chronological event on a vendor's timeline."""

    __tablename__ = "vendor_timelines"

    vendor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vendors.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    event_type: Mapped[str] = mapped_column(
        Text, nullable=False
    )
    title: Mapped[str] = mapped_column(
        String(500), nullable=False
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )
    event_metadata: Mapped[Optional[Dict]] = mapped_column(
        "metadata", JSONB, nullable=True
    )
    actor_id: Mapped[Optional[uuid.UUID]] = (
        mapped_column(
            UUID(as_uuid=True),
            ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        )
    )
