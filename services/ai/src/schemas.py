"""
AI services Pydantic v2 request / response schemas.

Handles auto-fill, review queue, and usage tracking.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


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
    notes: Optional[str] = None


# -- Responses ------------------------------------------------------


class ReviewQueueItem(BaseModel):
    """Single item in the AI review queue."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    item_type: str
    title: str
    description: str
    confidence: float
    vendor_name: Optional[str] = None
    assessment_title: Optional[str] = None
    created_at: datetime
    metadata: Optional[Dict[str, Any]] = None


class ReviewQueueResponse(BaseModel):
    """Paginated review queue."""

    items: List[ReviewQueueItem]
    total: int


class ReviewSubmitResponse(BaseModel):
    """Result of review submission."""

    id: uuid.UUID
    item_type: str
    decision: str
    updated: bool


class AutoFillAnswerDetail(BaseModel):
    """Single AI-generated answer with confidence and citations."""

    question_id: uuid.UUID
    answer: str
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str = ""
    evidence_citations: List[str] = Field(default_factory=list)


class AutoFillResponse(BaseModel):
    """Result of AI auto-fill operation."""

    assessment_id: uuid.UUID
    questions_filled: int
    total_questions: int
    average_confidence: float
    skipped_count: int
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    answers: List[AutoFillAnswerDetail] = Field(default_factory=list)


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
