"""
Assessment Pydantic v2 request / response schemas.

Handles templates, questions, assessments, responses,
review queue, and filter parameters.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

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
    description: Optional[str] = None
    framework_ids: Optional[List[uuid.UUID]] = None
    tier_applicability: Optional[List[str]] = None
    is_system: bool = False
    scoring_weights: Optional[Dict[str, Any]] = None
    estimated_duration_minutes: Optional[int] = Field(
        None, ge=1
    )


class AssessmentTemplateResponse(BaseModel):
    """Template summary for list and detail views."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    description: Optional[str] = None
    framework_ids: Optional[List[uuid.UUID]] = None
    tier_applicability: Optional[List[str]] = None
    is_system: bool
    is_active: bool
    scoring_weights: Optional[Dict[str, Any]] = None
    question_count: int
    estimated_duration_minutes: Optional[int] = None
    created_at: datetime
    updated_at: datetime


# -- Question Schemas -----------------------------------------------


class QuestionCreate(BaseModel):
    """Create a question in a template or bank."""

    question_bank_id: Optional[uuid.UUID] = None
    template_id: Optional[uuid.UUID] = None
    section: Optional[str] = Field(
        None, max_length=255
    )
    subsection: Optional[str] = Field(
        None, max_length=255
    )
    question_text: str = Field(min_length=1)
    question_type: QuestionType = QuestionType.text
    options: Optional[Dict[str, Any]] = None
    is_required: bool = True
    weight: float = Field(default=1.0, ge=0.0, le=10.0)
    risk_domain: Optional[str] = Field(
        None, max_length=100
    )
    guidance_text: Optional[str] = None
    order_index: int = Field(default=0, ge=0)


class QuestionResponse(BaseModel):
    """Question detail for API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    question_bank_id: Optional[uuid.UUID] = None
    template_id: Optional[uuid.UUID] = None
    section: Optional[str] = None
    subsection: Optional[str] = None
    question_text: str
    question_type: str
    options: Optional[Dict[str, Any]] = None
    is_required: bool
    weight: float
    risk_domain: Optional[str] = None
    guidance_text: Optional[str] = None
    order_index: int
    created_at: datetime
    updated_at: datetime


# -- Assessment Schemas ---------------------------------------------


class AssessmentCreate(BaseModel):
    """Create a new assessment from a template."""

    vendor_id: uuid.UUID
    template_id: uuid.UUID
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    due_date: Optional[datetime] = None


class AssessmentUpdate(BaseModel):
    """Update assessment metadata."""

    title: Optional[str] = Field(
        None, min_length=1, max_length=255
    )
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    assigned_to: Optional[uuid.UUID] = None


class AssessmentResponse(BaseModel):
    """Assessment summary for list views."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    vendor_id: uuid.UUID
    template_id: Optional[uuid.UUID] = None
    title: str
    description: Optional[str] = None
    status: str
    assigned_to: Optional[uuid.UUID] = None
    distributed_at: Optional[datetime] = None
    submitted_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    due_date: Optional[datetime] = None
    overall_score: Optional[float] = None
    ai_confidence: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    vendor_name: Optional[str] = None
    template_name: Optional[str] = None


class AssessmentListResponse(BaseModel):
    """Paginated assessment list."""

    items: List[AssessmentResponse]
    total: int
    page: int
    page_size: int


class QuestionnaireResponseItem(BaseModel):
    """Single response with its question context."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    assessment_id: uuid.UUID
    question_id: uuid.UUID
    response_value: Optional[str] = None
    response_text: Optional[str] = None
    response_options: Optional[Dict[str, Any]] = None
    ai_prefilled: bool
    ai_confidence: Optional[float] = None
    ai_citations: Optional[Dict[str, Any]] = None
    reviewer_id: Optional[uuid.UUID] = None
    review_status: str
    reviewer_notes: Optional[str] = None
    responded_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    question: Optional[QuestionResponse] = None


class AssessmentDetailResponse(BaseModel):
    """Full assessment detail with responses and context."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    vendor_id: uuid.UUID
    template_id: Optional[uuid.UUID] = None
    title: str
    description: Optional[str] = None
    status: str
    assigned_to: Optional[uuid.UUID] = None
    distributed_at: Optional[datetime] = None
    submitted_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    due_date: Optional[datetime] = None
    overall_score: Optional[float] = None
    ai_confidence: Optional[float] = None
    scoring_details: Optional[Dict[str, Any]] = None
    reminder_schedule: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    vendor_name: Optional[str] = None
    template_name: Optional[str] = None
    responses: List[QuestionnaireResponseItem] = []
    response_count: int = 0
    answered_count: int = 0


# -- Response Update ------------------------------------------------


class QuestionnaireResponseUpdate(BaseModel):
    """Update a questionnaire response (fill or review)."""

    response_value: Optional[str] = Field(
        None, max_length=500
    )
    response_text: Optional[str] = None
    review_status: Optional[ReviewStatus] = None
    reviewer_notes: Optional[str] = None


# -- Review Queue ---------------------------------------------------


class ReviewQueueItem(BaseModel):
    """Item needing human review."""

    model_config = ConfigDict(from_attributes=True)

    response_id: uuid.UUID
    assessment_id: uuid.UUID
    assessment_title: str
    vendor_name: str
    question_text: str
    section: Optional[str] = None
    response_value: Optional[str] = None
    ai_confidence: Optional[float] = None
    review_status: str


class ReviewQueueResponse(BaseModel):
    """Paginated review queue."""

    items: List[ReviewQueueItem]
    total: int


# -- Filter Parameters ----------------------------------------------


class AssessmentFilterParams(BaseModel):
    """Query parameters for assessment list filtering."""

    status: Optional[AssessmentStatus] = None
    vendor_id: Optional[uuid.UUID] = None
    template_id: Optional[uuid.UUID] = None
    search: Optional[str] = Field(
        None, max_length=255
    )
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
            raise ValueError(
                f"sort_by must be one of {allowed}"
            )
        return value
