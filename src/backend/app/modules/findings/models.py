"""
Findings domain SQLAlchemy models.

Two tables: findings, remediation_actions.
All tenant-scoped via TenantBase for RLS isolation.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import TenantBase


class Finding(TenantBase):
    """Security or compliance finding from an assessment."""

    __tablename__ = "findings"

    vendor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vendors.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    assessment_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assessments.id", ondelete="SET NULL"),
        nullable=True,
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    severity: Mapped[str] = mapped_column(
        String(20), nullable=False, default="medium"
    )
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="open"
    )
    affected_controls: Mapped[list[str] | None] = mapped_column(
        ARRAY(Text), nullable=True
    )
    remediation_guidance: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    sla_due_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    assigned_to: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    closed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    remediation_actions: Mapped[list[RemediationAction]] = relationship(
        back_populates="finding",
        lazy="selectin",
        cascade="all, delete-orphan",
    )


class RemediationAction(TenantBase):
    """Action item to remediate a finding."""

    __tablename__ = "remediation_actions"

    finding_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("findings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    action_type: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending"
    )
    effort_estimate: Mapped[str | None] = mapped_column(Text, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    finding: Mapped[Finding] = relationship(
        back_populates="remediation_actions"
    )
