"""
Scoring engine Pydantic v2 request / response schemas.

Handles scoring model CRUD, score calculation, history,
and portfolio summary responses.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

# -- Enums ----------------------------------------------------------


class ScoringMethod(str, Enum):
    """Scoring calculation methods."""

    weighted_average = "weighted_average"
    multiplicative = "multiplicative"


# -- Scoring Model Schemas ------------------------------------------


class DimensionWeight(BaseModel):
    """Single dimension with weight and optional metadata."""

    name: str
    weight: float = Field(ge=0.0, le=1.0)
    description: str | None = None


class ScoringModelCreate(BaseModel):
    """Create a new scoring model."""

    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    method: ScoringMethod = ScoringMethod.weighted_average
    is_default: bool = False
    dimensions: list[DimensionWeight] = Field(min_length=1)
    inherent_risk_factors: dict[str, Any] | None = None
    risk_thresholds: dict[str, float] | None = None


class ScoringModelUpdate(BaseModel):
    """Update a scoring model — all fields optional."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    method: ScoringMethod | None = None
    is_default: bool | None = None
    dimensions: list[DimensionWeight] | None = None
    inherent_risk_factors: dict[str, Any] | None = None
    risk_thresholds: dict[str, float] | None = None


class ScoringModelResponse(BaseModel):
    """Scoring model response."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    description: str | None = None
    method: str
    is_default: bool
    config: dict[str, Any] | None = None
    inherent_risk_factors: dict[str, Any] | None = None
    risk_thresholds: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime


# -- Score Schemas --------------------------------------------------


class ScoreBreakdown(BaseModel):
    """Score with per-dimension breakdown."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    vendor_id: uuid.UUID
    scoring_model_id: uuid.UUID | None = None
    overall_score: float
    dimension_scores: dict[str, Any] | None = None
    inherent_score: float | None = None
    residual_score: float | None = None
    external_score: float | None = None
    risk_level: str = "medium"
    calculated_at: datetime
    created_at: datetime


class ScoreHistoryItem(BaseModel):
    """Historical score data point."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    overall_score: float
    dimension_scores: dict[str, Any] | None = None
    recorded_at: datetime


class ScoreHistoryResponse(BaseModel):
    """Score history for a vendor."""

    vendor_id: uuid.UUID
    items: list[ScoreHistoryItem]
    total: int


class CalculateRequest(BaseModel):
    """Optional parameters for score calculation."""

    scoring_model_id: uuid.UUID | None = None


class BulkCalculateRequest(BaseModel):
    """Bulk score calculation for multiple vendors."""

    vendor_ids: list[uuid.UUID] = Field(min_length=1)
    scoring_model_id: uuid.UUID | None = None


class BulkCalculateResponse(BaseModel):
    """Results of bulk score calculation."""

    calculated: int = 0
    failed: int = 0
    results: list[ScoreBreakdown] = Field(default_factory=list)
    errors: list[dict[str, str]] = Field(default_factory=list)


# -- Portfolio Schemas ----------------------------------------------


class TierDistribution(BaseModel):
    """Count of vendors per risk tier."""

    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0


class PortfolioSummary(BaseModel):
    """Aggregate portfolio scoring summary."""

    total_vendors: int = 0
    scored_vendors: int = 0
    average_score: float | None = None
    tier_distribution: TierDistribution = Field(
        default_factory=TierDistribution
    )
    risk_level_counts: dict[str, int] = Field(default_factory=dict)
