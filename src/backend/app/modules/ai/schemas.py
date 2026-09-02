"""
AI services Pydantic v2 request / response schemas.

Handles auto-fill, review queue, and usage tracking.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict

# -- Enums ----------------------------------------------------------


class ReviewItemType(str, Enum):
    """Types of items in the AI review queue."""

    evidence_mapping = "evidence_mapping"
    ai_response = "ai_response"


class ReviewDecision(str, Enum):
    """Reviewer decisions."""

    approve = "approve"
    reject = "reject"
    revise = "revise"


# -- Requests -------------------------------------------------------


class AutoFillRequest(BaseModel):
    """Trigger AI auto-fill for an assessment."""

    assessment_id: uuid.UUID


class ReviewSubmitRequest(BaseModel):
    """Submit a review decision for a queue item."""

    item_type: ReviewItemType
    decision: ReviewDecision
    notes: str | None = None


# -- Responses ------------------------------------------------------


class AutoFillResponse(BaseModel):
    """Result of AI auto-fill operation."""

    assessment_id: uuid.UUID
    questions_filled: int
    total_questions: int
    average_confidence: float
    skipped_count: int


class ReviewQueueItem(BaseModel):
    """Single item in the AI review queue."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    item_type: str
    title: str
    description: str
    confidence: float
    vendor_name: str | None = None
    assessment_title: str | None = None
    created_at: datetime
    metadata: dict[str, Any] | None = None


class ReviewQueueResponse(BaseModel):
    """Paginated review queue."""

    items: list[ReviewQueueItem]
    total: int


class ReviewSubmitResponse(BaseModel):
    """Result of review submission."""

    id: uuid.UUID
    item_type: str
    decision: str
    updated: bool


class AIUsageStats(BaseModel):
    """AI usage statistics for a tenant."""

    total_tokens_used: int
    total_requests: int
    tokens_this_month: int
    requests_this_month: int
    auto_fills_completed: int
    evidence_processed: int
    average_confidence: float
    monthly_limit: int
    usage_percentage: float
