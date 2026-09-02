"""
Vendor domain SQLAlchemy models.

Four tables: vendors, vendor_contacts, vendor_tags, vendor_enrichment.
All PII fields (contact email, phone) encrypted with AES-256-GCM.
All tenant-scoped tables use TenantBase for RLS isolation.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import TenantBase


class Vendor(TenantBase):
    """Third-party vendor with lifecycle state and risk metadata."""

    __tablename__ = "vendors"

    name: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    domain: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )
    description: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="discovered"
    )
    tier: Mapped[str] = mapped_column(
        String(50), nullable=False, default="unclassified"
    )
    industry: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )
    country: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    employee_count: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    annual_revenue: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 2), nullable=True
    )
    data_classification: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )
    business_criticality: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )
    contract_start_date: Mapped[date | None] = mapped_column(
        Date, nullable=True
    )
    contract_end_date: Mapped[date | None] = mapped_column(
        Date, nullable=True
    )
    contract_value: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 2), nullable=True
    )
    primary_contact_name: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )
    primary_contact_email_encrypted: Mapped[str | None] = (
        mapped_column(Text, nullable=True)
    )
    primary_contact_email_hash: Mapped[str | None] = (
        mapped_column(String(64), nullable=True)
    )
    tags: Mapped[list[str] | None] = mapped_column(
        ARRAY(Text), nullable=True, default=list
    )
    notes: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    inherent_risk_score: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )
    residual_risk_score: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )
    external_rating_score: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )
    external_rating_provider: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    last_assessed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    next_assessment_due: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    contacts: Mapped[list[VendorContact]] = relationship(
        back_populates="vendor",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    enrichments: Mapped[list[VendorEnrichment]] = relationship(
        back_populates="vendor",
        lazy="noload",
        cascade="all, delete-orphan",
    )


class VendorContact(TenantBase):
    """Contact person associated with a vendor. PII is encrypted."""

    __tablename__ = "vendor_contacts"

    vendor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vendors.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    first_name: Mapped[str] = mapped_column(
        String(100), nullable=False
    )
    last_name: Mapped[str] = mapped_column(
        String(100), nullable=False
    )
    email_encrypted: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    email_hash: Mapped[str | None] = mapped_column(
        String(64), nullable=True
    )
    phone_encrypted: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    phone_hash: Mapped[str | None] = mapped_column(
        String(64), nullable=True
    )
    role: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    is_primary: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    portal_access: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    # Relationships
    vendor: Mapped[Vendor] = relationship(
        back_populates="contacts"
    )


class VendorTag(TenantBase):
    """Reusable tag scoped to a tenant."""

    __tablename__ = "vendor_tags"

    __table_args__ = (
        UniqueConstraint(
            "tenant_id", "name", name="uq_vendor_tags_tenant_name"
        ),
    )

    name: Mapped[str] = mapped_column(
        String(100), nullable=False
    )
    color: Mapped[str | None] = mapped_column(
        String(7), nullable=True
    )


class VendorEnrichment(TenantBase):
    """External enrichment data snapshot for a vendor."""

    __tablename__ = "vendor_enrichment"

    vendor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vendors.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    source: Mapped[str] = mapped_column(
        String(100), nullable=False
    )
    data: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True
    )
    confidence: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )
    is_current: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    enriched_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    vendor: Mapped[Vendor] = relationship(
        back_populates="enrichments"
    )
