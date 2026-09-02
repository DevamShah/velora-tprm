"""
Findings Pydantic v2 request / response schemas.

Handles findings CRUD, remediation actions, and filters.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

# -- Enums ----------------------------------------------------------


class FindingSeverity(str, Enum):
    """Finding severity levels."""

    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"
    info = "info"


class FindingStatus(str, Enum):
    """Finding lifecycle states."""

    open = "open"
    remediation_in_progress = "remediation_in_progress"
    submitted_for_verification = "submitted_for_verification"
    verified_closed = "verified_closed"
    risk_accepted = "risk_accepted"
    wont_fix = "wont_fix"


class RemediationStatus(str, Enum):
    """Remediation action status."""

    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    verified = "verified"


# -- Finding Requests -----------------------------------------------


class FindingCreate(BaseModel):
    """Create a new finding."""

    vendor_id: uuid.UUID
    assessment_id: uuid.UUID | None = None
    title: str = Field(min_length=1, max_length=500)
    description: str | None = None
    severity: FindingSeverity = FindingSeverity.medium
    affected_controls: list[str] | None = None
    remediation_guidance: str | None = None
    sla_due_date: datetime | None = None
    assigned_to: uuid.UUID | None = None


class FindingUpdate(BaseModel):
    """Update a finding."""

    title: str | None = Field(None, min_length=1, max_length=500)
    description: str | None = None
    severity: FindingSeverity | None = None
    status: FindingStatus | None = None
    affected_controls: list[str] | None = None
    remediation_guidance: str | None = None
    sla_due_date: datetime | None = None
    assigned_to: uuid.UUID | None = None


class FindingClose(BaseModel):
    """Close a finding with a final status."""

    status: FindingStatus


# -- Remediation Requests -------------------------------------------


class RemediationCreate(BaseModel):
    """Create a remediation action."""

    action_type: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1)
    effort_estimate: str | None = None


class RemediationUpdate(BaseModel):
    """Update a remediation action."""

    action_type: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None
    status: RemediationStatus | None = None
    effort_estimate: str | None = None


# -- Responses ------------------------------------------------------


class RemediationResponse(BaseModel):
    """Remediation action response."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    finding_id: uuid.UUID
    action_type: str
    description: str
    status: str
    effort_estimate: str | None = None
    completed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class FindingResponse(BaseModel):
    """Single finding response."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    vendor_id: uuid.UUID
    assessment_id: uuid.UUID | None = None
    title: str
    description: str | None = None
    severity: str
    status: str
    affected_controls: list[str] | None = None
    remediation_guidance: str | None = None
    sla_due_date: datetime | None = None
    assigned_to: uuid.UUID | None = None
    closed_at: datetime | None = None
    remediation_actions: list[RemediationResponse] = Field(
        default_factory=list
    )
    created_at: datetime
    updated_at: datetime


class FindingListResponse(BaseModel):
    """Paginated finding list."""

    items: list[FindingResponse]
    total: int
    page: int
    page_size: int
