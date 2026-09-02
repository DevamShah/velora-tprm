"""
Scoring engine SQLAlchemy models.

Three tables: scoring_models, vendor_scores, score_history.
All tenant-scoped with RLS isolation.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import TenantBase


class ScoringModel(TenantBase):
    """Configurable scoring model with weighted dimensions."""

    __tablename__ = "scoring_models"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    method: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="weighted_average",
    )
    is_default: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    config: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    inherent_risk_factors: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True
    )
    risk_thresholds: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Relationships
    scores: Mapped[list[VendorScore]] = relationship(
        back_populates="scoring_model",
        lazy="noload",
    )


class VendorScore(TenantBase):
    """Calculated score for a vendor against a scoring model."""

    __tablename__ = "vendor_scores"

    vendor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vendors.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    scoring_model_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "scoring_models.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )
    overall_score: Mapped[float] = mapped_column(Float, nullable=False)
    dimension_scores: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    inherent_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    residual_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    external_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    input_snapshot: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    # Relationships
    scoring_model: Mapped[ScoringModel | None] = relationship(
        back_populates="scores"
    )


class ScoreHistory(TenantBase):
    """Point-in-time score snapshot for trend analysis."""

    __tablename__ = "score_history"

    vendor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vendors.id", ondelete="CASCADE"),
        nullable=False,
    )
    overall_score: Mapped[float] = mapped_column(Float, nullable=False)
    dimension_scores: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
