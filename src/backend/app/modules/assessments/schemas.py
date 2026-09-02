"""
Assessment Pydantic v2 request / response schemas.

Handles templates, questions, assessments, responses,
review queue, and filter parameters.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)

# -- Enums ----------------------------------------------------------


class AssessmentStatus(str, Enum):
    """Allowed assessment lifecycle states."""

    draft = "draft"
    distributed = "distributed"
    in_progress = "in_progress"
    submitted = "submitted"
    under_review = "under_review"
    completed = "completed"
    cancelled = "cancelled"


class QuestionType(str, Enum):
    """Supported question input types."""

    yes_no = "yes_no"
    multiple_choice = "multiple_choice"
    text = "text"
    file_upload = "file_upload"
    scale = "scale"
    date = "date"


class QuestionBankType(str, Enum):
    """Question bank classification."""

    sig_core = "sig_core"
    sig_lite = "sig_lite"
    caiq_v4 = "caiq_v4"
    cis = "cis"
    custom = "custom"


class ReviewStatus(str, Enum):
    """Response review states."""

    pending = "pending"
    accepted = "accepted"
    modified = "modified"
    flagged = "flagged"


# -- Template Schemas -----------------------------------------------


class AssessmentTemplateCreate(BaseModel):
    """Create an assessment template."""

    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    framework_ids: list[uuid.UUID] | None = None
    tier_applicability: list[str] | None = None
    is_system: bool = False
    scoring_weights: dict[str, Any] | None = None
    estimated_duration_minutes: int | None = Field(None, ge=1)


class AssessmentTemplateResponse(BaseModel):
    """Template summary for list and detail views."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    description: str | None = None
    framework_ids: list[uuid.UUID] | None = None
    tier_applicability: list[str] | None = None
    is_system: bool
    is_active: bool
    scoring_weights: dict[str, Any] | None = None
    question_count: int
    estimated_duration_minutes: int | None = None
    created_at: datetime
    updated_at: datetime


# -- Question Schemas -----------------------------------------------


class QuestionCreate(BaseModel):
    """Create a question in a template or bank."""

    question_bank_id: uuid.UUID | None = None
    template_id: uuid.UUID | None = None
    section: str | None = Field(None, max_length=255)
    subsection: str | None = Field(None, max_length=255)
    question_text: str = Field(min_length=1)
    question_type: QuestionType = QuestionType.text
    options: dict[str, Any] | None = None
    is_required: bool = True
    weight: float = Field(default=1.0, ge=0.0, le=10.0)
    risk_domain: str | None = Field(None, max_length=100)
    guidance_text: str | None = None
    order_index: int = Field(default=0, ge=0)


class QuestionResponse(BaseModel):
    """Question detail for API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    question_bank_id: uuid.UUID | None = None
    template_id: uuid.UUID | None = None
    section: str | None = None
    subsection: str | None = None
    question_text: str
    question_type: str
    options: dict[str, Any] | None = None
    is_required: bool
    weight: float
    risk_domain: str | None = None
    guidance_text: str | None = None
    order_index: int
    created_at: datetime
    updated_at: datetime


# -- Assessment Schemas ---------------------------------------------


class AssessmentCreate(BaseModel):
    """Create a new assessment from a template."""

    vendor_id: uuid.UUID
    template_id: uuid.UUID
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    due_date: datetime | None = None


class AssessmentUpdate(BaseModel):
    """Update assessment metadata."""

    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    due_date: datetime | None = None
    assigned_to: uuid.UUID | None = None


class AssessmentResponse(BaseModel):
    """Assessment summary for list views."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    vendor_id: uuid.UUID
    template_id: uuid.UUID | None = None
    title: str
    description: str | None = None
    status: str
    assigned_to: uuid.UUID | None = None
    distributed_at: datetime | None = None
    submitted_at: datetime | None = None
    completed_at: datetime | None = None
    due_date: datetime | None = None
    overall_score: float | None = None
    ai_confidence: float | None = None
    created_at: datetime
    updated_at: datetime
    vendor_name: str | None = None
    template_name: str | None = None


class AssessmentListResponse(BaseModel):
    """Paginated assessment list."""

    items: list[AssessmentResponse]
    total: int
    page: int
    page_size: int


class QuestionnaireResponseItem(BaseModel):
    """Single response with its question context."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    assessment_id: uuid.UUID
    question_id: uuid.UUID
    response_value: str | None = None
    response_text: str | None = None
    response_options: dict[str, Any] | None = None
    ai_prefilled: bool
    ai_confidence: float | None = None
    ai_citations: dict[str, Any] | None = None
    reviewer_id: uuid.UUID | None = None
    review_status: str
    reviewer_notes: str | None = None
    responded_at: datetime | None = None
    reviewed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    question: QuestionResponse | None = None


class AssessmentDetailResponse(BaseModel):
    """Full assessment detail with responses and context."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    vendor_id: uuid.UUID
    template_id: uuid.UUID | None = None
    title: str
    description: str | None = None
    status: str
    assigned_to: uuid.UUID | None = None
    distributed_at: datetime | None = None
    submitted_at: datetime | None = None
    completed_at: datetime | None = None
    due_date: datetime | None = None
    overall_score: float | None = None
    ai_confidence: float | None = None
    scoring_details: dict[str, Any] | None = None
    reminder_schedule: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime
    vendor_name: str | None = None
    template_name: str | None = None
    responses: list[QuestionnaireResponseItem] = []
    response_count: int = 0
    answered_count: int = 0


# -- Response Update ------------------------------------------------


class QuestionnaireResponseUpdate(BaseModel):
    """Update a questionnaire response (fill or review)."""

    response_value: str | None = Field(None, max_length=500)
    response_text: str | None = None
    review_status: ReviewStatus | None = None
    reviewer_notes: str | None = None


# -- Review Queue ---------------------------------------------------


class ReviewQueueItem(BaseModel):
    """Item needing human review."""

    model_config = ConfigDict(from_attributes=True)

    response_id: uuid.UUID
    assessment_id: uuid.UUID
    assessment_title: str
    vendor_name: str
    question_text: str
    section: str | None = None
    response_value: str | None = None
    ai_confidence: float | None = None
    review_status: str


class ReviewQueueResponse(BaseModel):
    """Paginated review queue."""

    items: list[ReviewQueueItem]
    total: int


# -- Filter Parameters ----------------------------------------------


class AssessmentFilterParams(BaseModel):
    """Query parameters for assessment list filtering."""

    status: AssessmentStatus | None = None
    vendor_id: uuid.UUID | None = None
    template_id: uuid.UUID | None = None
    search: str | None = Field(None, max_length=255)
    sort_by: str = Field(default="created_at")
    sort_order: str = Field(default="desc")
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

    @field_validator("sort_by")
    @classmethod
    def validate_sort_by(cls, value: str) -> str:
        """Restrict sortable columns to prevent injection."""
        allowed = {
            "title",
            "status",
            "due_date",
            "overall_score",
            "created_at",
            "updated_at",
        }
        if value not in allowed:
            raise ValueError(f"sort_by must be one of {allowed}")
        return value
