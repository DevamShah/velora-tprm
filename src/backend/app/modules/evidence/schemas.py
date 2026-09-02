"""
Evidence Pydantic v2 request / response schemas.

Handles upload, process, list, detail, mapping verification.
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


class DocumentType(str, Enum):
    """Allowed evidence document types."""

    soc2 = "soc2"
    iso_cert = "iso_cert"
    pen_test = "pen_test"
    policy = "policy"
    questionnaire = "questionnaire"
    contract = "contract"
    other = "other"


class EvidenceStatus(str, Enum):
    """Evidence processing lifecycle."""

    uploaded = "uploaded"
    processing = "processing"
    parsed = "parsed"
    mapped = "mapped"
    verified = "verified"
    failed = "failed"


class CoverageType(str, Enum):
    """How evidence covers a control."""

    full = "full"
    partial = "partial"
    supportive = "supportive"


class SortOrder(str, Enum):
    """Sort direction."""

    asc = "asc"
    desc = "desc"


# -- Requests -------------------------------------------------------


class EvidenceUploadRequest(BaseModel):
    """Request to generate a presigned upload URL."""

    vendor_id: uuid.UUID
    assessment_id: uuid.UUID | None = None
    filename: str = Field(min_length=1, max_length=500)
    file_size: int = Field(ge=1, le=104857600)
    mime_type: str = Field(max_length=100)
    document_type: DocumentType = DocumentType.other


class EvidenceProcessRequest(BaseModel):
    """Request to trigger AI processing on evidence."""

    pass


class MappingVerifyRequest(BaseModel):
    """Verify or reject an evidence-to-control mapping."""

    verified: bool
    notes: str | None = None


# -- Filter ---------------------------------------------------------


class EvidenceFilterParams(BaseModel):
    """Query parameters for evidence listing."""

    vendor_id: uuid.UUID | None = None
    document_type: DocumentType | None = None
    status: EvidenceStatus | None = None
    sort_by: str = Field(default="created_at")
    sort_order: SortOrder = SortOrder.desc
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

    @field_validator("sort_by")
    @classmethod
    def validate_sort_by(cls, value: str) -> str:
        allowed = {
            "created_at",
            "filename",
            "file_size",
            "status",
            "document_type",
        }
        if value not in allowed:
            raise ValueError(
                f"sort_by must be one of {allowed}"
            )
        return value


# -- Responses ------------------------------------------------------


class EvidenceExtractionResponse(BaseModel):
    """Single extracted field from a document."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    field_name: str
    field_value: str
    confidence: float
    page_number: int | None = None
    created_at: datetime


class EvidenceControlMappingResponse(BaseModel):
    """Single evidence-to-control mapping."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    evidence_id: uuid.UUID
    clause_id: uuid.UUID
    coverage_type: str
    confidence: float
    verified: bool
    verified_by: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime


class EvidenceResponse(BaseModel):
    """Evidence summary for list views."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    vendor_id: uuid.UUID
    assessment_id: uuid.UUID | None = None
    filename: str
    file_size: int
    mime_type: str
    s3_key: str
    document_type: str
    status: str
    classification_confidence: float | None = None
    uploaded_by: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime


class EvidenceDetailResponse(EvidenceResponse):
    """Full evidence detail with extractions and mappings."""

    parsed_content: dict[str, Any] | None = None
    extraction_summary: dict[str, Any] | None = None
    extractions: list[EvidenceExtractionResponse] = []
    control_mappings: list[
        EvidenceControlMappingResponse
    ] = []


class EvidenceListResponse(BaseModel):
    """Paginated evidence list."""

    items: list[EvidenceResponse]
    total: int
    page: int
    page_size: int


class EvidenceUploadResponse(BaseModel):
    """Response from upload URL generation."""

    evidence_id: uuid.UUID
    upload_url: str
    s3_key: str
