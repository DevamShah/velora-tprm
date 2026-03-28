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
from typing import Any, List, Optional

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
    domain: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    status: Optional[VendorStatus] = VendorStatus.discovered
    tier: Optional[VendorTier] = VendorTier.unclassified
    industry: Optional[str] = Field(None, max_length=255)
    country: Optional[str] = Field(None, max_length=100)
    employee_count: Optional[int] = Field(None, ge=0)
    annual_revenue: Optional[Decimal] = Field(None, ge=0)
    data_classification: Optional[DataClassification] = None
    business_criticality: Optional[BusinessCriticality] = None
    contract_start_date: Optional[date] = None
    contract_end_date: Optional[date] = None
    contract_value: Optional[Decimal] = Field(None, ge=0)
    primary_contact_name: Optional[str] = Field(
        None, max_length=255
    )
    primary_contact_email: Optional[str] = Field(
        None, max_length=255
    )
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    inherent_risk_score: Optional[float] = Field(
        None, ge=0.0, le=100.0
    )
    residual_risk_score: Optional[float] = Field(
        None, ge=0.0, le=100.0
    )


class VendorUpdate(BaseModel):
    """Update a vendor — all fields optional."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    domain: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    status: Optional[VendorStatus] = None
    tier: Optional[VendorTier] = None
    industry: Optional[str] = Field(None, max_length=255)
    country: Optional[str] = Field(None, max_length=100)
    employee_count: Optional[int] = Field(None, ge=0)
    annual_revenue: Optional[Decimal] = Field(None, ge=0)
    data_classification: Optional[DataClassification] = None
    business_criticality: Optional[BusinessCriticality] = None
    contract_start_date: Optional[date] = None
    contract_end_date: Optional[date] = None
    contract_value: Optional[Decimal] = Field(None, ge=0)
    primary_contact_name: Optional[str] = Field(
        None, max_length=255
    )
    primary_contact_email: Optional[str] = Field(
        None, max_length=255
    )
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    inherent_risk_score: Optional[float] = Field(
        None, ge=0.0, le=100.0
    )
    residual_risk_score: Optional[float] = Field(
        None, ge=0.0, le=100.0
    )


# ── Vendor Responses ───────────────────────────────────────


class VendorResponse(BaseModel):
    """Single vendor summary for list views."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    domain: Optional[str] = None
    description: Optional[str] = None
    status: str
    tier: str
    industry: Optional[str] = None
    country: Optional[str] = None
    employee_count: Optional[int] = None
    annual_revenue: Optional[Decimal] = None
    data_classification: Optional[str] = None
    business_criticality: Optional[str] = None
    contract_start_date: Optional[date] = None
    contract_end_date: Optional[date] = None
    contract_value: Optional[Decimal] = None
    primary_contact_name: Optional[str] = None
    primary_contact_email: Optional[str] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    inherent_risk_score: Optional[float] = None
    residual_risk_score: Optional[float] = None
    external_rating_score: Optional[float] = None
    external_rating_provider: Optional[str] = None
    last_assessed_at: Optional[datetime] = None
    next_assessment_due: Optional[datetime] = None
    contacts_count: int = 0
    created_at: datetime
    updated_at: datetime


class VendorListResponse(BaseModel):
    """Paginated vendor list."""

    items: List[VendorResponse]
    total: int
    page: int
    page_size: int


# ── Vendor Contact Schemas ─────────────────────────────────


class VendorContactCreate(BaseModel):
    """Create a contact for a vendor."""

    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    role: Optional[str] = Field(None, max_length=100)
    is_primary: bool = False
    portal_access: bool = False


class VendorContactUpdate(BaseModel):
    """Update a vendor contact — all fields optional."""

    first_name: Optional[str] = Field(
        None, min_length=1, max_length=100
    )
    last_name: Optional[str] = Field(
        None, min_length=1, max_length=100
    )
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    role: Optional[str] = Field(None, max_length=100)
    is_primary: Optional[bool] = None
    portal_access: Optional[bool] = None


class VendorContactResponse(BaseModel):
    """Contact response with decrypted PII."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    vendor_id: uuid.UUID
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None
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
    data: Optional[Any] = None
    confidence: Optional[float] = None
    is_current: bool
    enriched_at: Optional[datetime] = None
    created_at: datetime


class VendorDetailResponse(BaseModel):
    """Full vendor detail with contacts and enrichment."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    domain: Optional[str] = None
    description: Optional[str] = None
    status: str
    tier: str
    industry: Optional[str] = None
    country: Optional[str] = None
    employee_count: Optional[int] = None
    annual_revenue: Optional[Decimal] = None
    data_classification: Optional[str] = None
    business_criticality: Optional[str] = None
    contract_start_date: Optional[date] = None
    contract_end_date: Optional[date] = None
    contract_value: Optional[Decimal] = None
    primary_contact_name: Optional[str] = None
    primary_contact_email: Optional[str] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    inherent_risk_score: Optional[float] = None
    residual_risk_score: Optional[float] = None
    external_rating_score: Optional[float] = None
    external_rating_provider: Optional[str] = None
    last_assessed_at: Optional[datetime] = None
    next_assessment_due: Optional[datetime] = None
    contacts: List[VendorContactResponse] = []
    enrichments: List[VendorEnrichmentResponse] = []
    timeline: List[Any] = Field(default_factory=list)
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
    field: Optional[str] = None
    message: str


class BulkImportResult(BaseModel):
    """Summary of a bulk import operation."""

    success_count: int = 0
    error_count: int = 0
    errors: List[BulkImportError] = []


# ── Filter Parameters ──────────────────────────────────────


class VendorFilterParams(BaseModel):
    """Query parameters for vendor list filtering."""

    status: Optional[VendorStatus] = None
    tier: Optional[VendorTier] = None
    search: Optional[str] = Field(None, max_length=255)
    tags: Optional[List[str]] = None
    data_classification: Optional[DataClassification] = None
    business_criticality: Optional[BusinessCriticality] = None
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
