"""
Vendor Pydantic v2 request / response schemas.

Handles create, update, list (paginated), detail, contacts,
bulk import, and filter parameters.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)

# ── Enums ──────────────────────────────────────────────────


class VendorStatus(str, Enum):
    """Allowed vendor lifecycle states."""

    discovered = "discovered"
    classified = "classified"
    assessing = "assessing"
    active = "active"
    monitoring = "monitoring"
    reassessing = "reassessing"
    offboarding = "offboarding"
    offboarded = "offboarded"
    archived = "archived"


class VendorTier(str, Enum):
    """Risk-based tier classification."""

    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"
    unclassified = "unclassified"


class DataClassification(str, Enum):
    """Data sensitivity levels."""

    public = "public"
    internal = "internal"
    confidential = "confidential"
    restricted = "restricted"


class BusinessCriticality(str, Enum):
    """Business impact levels."""

    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"


class SortOrder(str, Enum):
    """Sort direction."""

    asc = "asc"
    desc = "desc"


# ── Vendor Requests ────────────────────────────────────────


class VendorCreate(BaseModel):
    """Create a new vendor. Only name is required."""

    name: str = Field(min_length=1, max_length=255)
    domain: str | None = Field(None, max_length=255)
    description: str | None = None
    status: VendorStatus | None = VendorStatus.discovered
    tier: VendorTier | None = VendorTier.unclassified
    industry: str | None = Field(None, max_length=255)
    country: str | None = Field(None, max_length=100)
    employee_count: int | None = Field(None, ge=0)
    annual_revenue: Decimal | None = Field(None, ge=0)
    data_classification: DataClassification | None = None
    business_criticality: BusinessCriticality | None = None
    contract_start_date: date | None = None
    contract_end_date: date | None = None
    contract_value: Decimal | None = Field(None, ge=0)
    primary_contact_name: str | None = Field(
        None, max_length=255
    )
    primary_contact_email: str | None = Field(
        None, max_length=255
    )
    tags: list[str] | None = None
    notes: str | None = None
    inherent_risk_score: float | None = Field(
        None, ge=0.0, le=100.0
    )
    residual_risk_score: float | None = Field(
        None, ge=0.0, le=100.0
    )


class VendorUpdate(BaseModel):
    """Update a vendor — all fields optional."""

    name: str | None = Field(None, min_length=1, max_length=255)
    domain: str | None = Field(None, max_length=255)
    description: str | None = None
    status: VendorStatus | None = None
    tier: VendorTier | None = None
    industry: str | None = Field(None, max_length=255)
    country: str | None = Field(None, max_length=100)
    employee_count: int | None = Field(None, ge=0)
    annual_revenue: Decimal | None = Field(None, ge=0)
    data_classification: DataClassification | None = None
    business_criticality: BusinessCriticality | None = None
    contract_start_date: date | None = None
    contract_end_date: date | None = None
    contract_value: Decimal | None = Field(None, ge=0)
    primary_contact_name: str | None = Field(
        None, max_length=255
    )
    primary_contact_email: str | None = Field(
        None, max_length=255
    )
    tags: list[str] | None = None
    notes: str | None = None
    inherent_risk_score: float | None = Field(
        None, ge=0.0, le=100.0
    )
    residual_risk_score: float | None = Field(
        None, ge=0.0, le=100.0
    )


# ── Vendor Responses ───────────────────────────────────────


class VendorResponse(BaseModel):
    """Single vendor summary for list views."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    domain: str | None = None
    description: str | None = None
    status: str
    tier: str
    industry: str | None = None
    country: str | None = None
    employee_count: int | None = None
    annual_revenue: Decimal | None = None
    data_classification: str | None = None
    business_criticality: str | None = None
    contract_start_date: date | None = None
    contract_end_date: date | None = None
    contract_value: Decimal | None = None
    primary_contact_name: str | None = None
    primary_contact_email: str | None = None
    tags: list[str] | None = None
    notes: str | None = None
    inherent_risk_score: float | None = None
    residual_risk_score: float | None = None
    external_rating_score: float | None = None
    external_rating_provider: str | None = None
    last_assessed_at: datetime | None = None
    next_assessment_due: datetime | None = None
    contacts_count: int = 0
    created_at: datetime
    updated_at: datetime


class VendorListResponse(BaseModel):
    """Paginated vendor list."""

    items: list[VendorResponse]
    total: int
    page: int
    page_size: int


# ── Vendor Contact Schemas ─────────────────────────────────


class VendorContactCreate(BaseModel):
    """Create a contact for a vendor."""

    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: str | None = Field(None, max_length=255)
    phone: str | None = Field(None, max_length=50)
    role: str | None = Field(None, max_length=100)
    is_primary: bool = False
    portal_access: bool = False


class VendorContactUpdate(BaseModel):
    """Update a vendor contact — all fields optional."""

    first_name: str | None = Field(
        None, min_length=1, max_length=100
    )
    last_name: str | None = Field(
        None, min_length=1, max_length=100
    )
    email: str | None = Field(None, max_length=255)
    phone: str | None = Field(None, max_length=50)
    role: str | None = Field(None, max_length=100)
    is_primary: bool | None = None
    portal_access: bool | None = None


class VendorContactResponse(BaseModel):
    """Contact response with decrypted PII."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    vendor_id: uuid.UUID
    first_name: str
    last_name: str
    email: str | None = None
    phone: str | None = None
    role: str | None = None
    is_primary: bool
    portal_access: bool
    created_at: datetime
    updated_at: datetime


# ── Vendor Detail Response ─────────────────────────────────


class VendorEnrichmentResponse(BaseModel):
    """Enrichment data snapshot."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    source: str
    data: Any | None = None
    confidence: float | None = None
    is_current: bool
    enriched_at: datetime | None = None
    created_at: datetime


class VendorDetailResponse(BaseModel):
    """Full vendor detail with contacts and enrichment."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    domain: str | None = None
    description: str | None = None
    status: str
    tier: str
    industry: str | None = None
    country: str | None = None
    employee_count: int | None = None
    annual_revenue: Decimal | None = None
    data_classification: str | None = None
    business_criticality: str | None = None
    contract_start_date: date | None = None
    contract_end_date: date | None = None
    contract_value: Decimal | None = None
    primary_contact_name: str | None = None
    primary_contact_email: str | None = None
    tags: list[str] | None = None
    notes: str | None = None
    inherent_risk_score: float | None = None
    residual_risk_score: float | None = None
    external_rating_score: float | None = None
    external_rating_provider: str | None = None
    last_assessed_at: datetime | None = None
    next_assessment_due: datetime | None = None
    contacts: list[VendorContactResponse] = []
    enrichments: list[VendorEnrichmentResponse] = []
    timeline: list[Any] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


# ── Bulk Import ────────────────────────────────────────────


class BulkImportRequest(BaseModel):
    """CSV bulk import payload."""

    csv_data: str = Field(
        min_length=1,
        description="Raw CSV content with header row",
    )


class BulkImportError(BaseModel):
    """Single row import error."""

    row: int
    field: str | None = None
    message: str


class BulkImportResult(BaseModel):
    """Summary of a bulk import operation."""

    success_count: int = 0
    error_count: int = 0
    errors: list[BulkImportError] = []


# ── Filter Parameters ──────────────────────────────────────


class VendorFilterParams(BaseModel):
    """Query parameters for vendor list filtering."""

    status: VendorStatus | None = None
    tier: VendorTier | None = None
    search: str | None = Field(None, max_length=255)
    tags: list[str] | None = None
    data_classification: DataClassification | None = None
    business_criticality: BusinessCriticality | None = None
    sort_by: str = Field(default="created_at")
    sort_order: SortOrder = SortOrder.desc
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

    @field_validator("sort_by")
    @classmethod
    def validate_sort_by(cls, value: str) -> str:
        """Restrict sortable columns to prevent injection."""
        allowed = {
            "name",
            "domain",
            "status",
            "tier",
            "created_at",
            "updated_at",
            "inherent_risk_score",
            "contract_value",
        }
        if value not in allowed:
            raise ValueError(
                f"sort_by must be one of {allowed}"
            )
        return value
