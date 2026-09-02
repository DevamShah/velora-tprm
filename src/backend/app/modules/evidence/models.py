"""
Evidence domain SQLAlchemy models.

Three tables: evidence, evidence_control_mappings, evidence_extractions.
All tenant-scoped via TenantBase for RLS isolation.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import TenantBase


class Evidence(TenantBase):
    """Uploaded evidence document with parsing status."""

    __tablename__ = "evidence"

    vendor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vendors.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    assessment_id: Mapped[uuid.UUID | None] = (
        mapped_column(
            UUID(as_uuid=True),
            ForeignKey(
                "assessments.id", ondelete="SET NULL"
            ),
            nullable=True,
            index=True,
        )
    )
    filename: Mapped[str] = mapped_column(
        String(500), nullable=False
    )
    file_size: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    mime_type: Mapped[str] = mapped_column(
        String(100), nullable=False
    )
    s3_key: Mapped[str] = mapped_column(
        String(1000), nullable=False
    )
    document_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="other"
    )
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="uploaded"
    )
    parsed_content: Mapped[dict | None] = (
        mapped_column(JSONB, nullable=True)
    )
    extraction_summary: Mapped[dict | None] = (
        mapped_column(JSONB, nullable=True)
    )
    classification_confidence: Mapped[
        float | None
    ] = mapped_column(Float, nullable=True)
    uploaded_by: Mapped[uuid.UUID | None] = (
        mapped_column(
            UUID(as_uuid=True),
            ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        )
    )
    deleted_at: Mapped[datetime | None] = (
        mapped_column(
            DateTime(timezone=True), nullable=True
        )
    )

    # Relationships
    extractions: Mapped[
        list[EvidenceExtraction]
    ] = relationship(
        back_populates="evidence",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    control_mappings: Mapped[
        list[EvidenceControlMapping]
    ] = relationship(
        back_populates="evidence",
        lazy="selectin",
        cascade="all, delete-orphan",
    )


class EvidenceControlMapping(TenantBase):
    """Mapping between evidence and framework clauses."""

    __tablename__ = "evidence_control_mappings"

    evidence_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("evidence.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    clause_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "framework_clauses.id", ondelete="CASCADE"
        ),
        nullable=False,
        index=True,
    )
    coverage_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="supportive",
    )
    confidence: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.0
    )
    verified: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    verified_by: Mapped[uuid.UUID | None] = (
        mapped_column(
            UUID(as_uuid=True),
            ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        )
    )

    # Relationships
    evidence: Mapped[Evidence] = relationship(
        back_populates="control_mappings"
    )


class EvidenceExtraction(TenantBase):
    """Extracted field from evidence document."""

    __tablename__ = "evidence_extractions"

    evidence_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("evidence.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    field_name: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    field_value: Mapped[str] = mapped_column(
        Text, nullable=False
    )
    confidence: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.0
    )
    page_number: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )

    # Relationships
    evidence: Mapped[Evidence] = relationship(
        back_populates="extractions"
    )
