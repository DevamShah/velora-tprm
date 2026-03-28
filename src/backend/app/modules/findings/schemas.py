"""
Findings Pydantic v2 request / response schemas.

Handles findings CRUD, remediation actions, and filters.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import List, Optional

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
    submitted_for_verification = (
        "submitted_for_verification"
    )
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
    assessment_id: Optional[uuid.UUID] = None
    title: str = Field(min_length=1, max_length=500)
    description: Optional[str] = None
    severity: FindingSeverity = FindingSeverity.medium
    affected_controls: Optional[List[str]] = None
    remediation_guidance: Optional[str] = None
    sla_due_date: Optional[datetime] = None
    assigned_to: Optional[uuid.UUID] = None


class FindingUpdate(BaseModel):
    """Update a finding."""

    title: Optional[str] = Field(
        None, min_length=1, max_length=500
    )
    description: Optional[str] = None
    severity: Optional[FindingSeverity] = None
    status: Optional[FindingStatus] = None
    affected_controls: Optional[List[str]] = None
    remediation_guidance: Optional[str] = None
    sla_due_date: Optional[datetime] = None
    assigned_to: Optional[uuid.UUID] = None


class FindingClose(BaseModel):
    """Close a finding with a final status."""

    status: FindingStatus


# -- Remediation Requests -------------------------------------------


class RemediationCreate(BaseModel):
    """Create a remediation action."""

    action_type: str = Field(
        min_length=1, max_length=100
    )
    description: str = Field(min_length=1)
    effort_estimate: Optional[str] = None


class RemediationUpdate(BaseModel):
    """Update a remediation action."""

    action_type: Optional[str] = Field(
        None, min_length=1, max_length=100
    )
    description: Optional[str] = None
    status: Optional[RemediationStatus] = None
    effort_estimate: Optional[str] = None


# -- Responses ------------------------------------------------------


class RemediationResponse(BaseModel):
    """Remediation action response."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    finding_id: uuid.UUID
    action_type: str
    description: str
    status: str
    effort_estimate: Optional[str] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class FindingResponse(BaseModel):
    """Single finding response."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    vendor_id: uuid.UUID
    assessment_id: Optional[uuid.UUID] = None
    title: str
    description: Optional[str] = None
    severity: str
    status: str
    affected_controls: Optional[List[str]] = None
    remediation_guidance: Optional[str] = None
    sla_due_date: Optional[datetime] = None
    assigned_to: Optional[uuid.UUID] = None
    closed_at: Optional[datetime] = None
    remediation_actions: List[RemediationResponse] = (
        Field(default_factory=list)
    )
    created_at: datetime
    updated_at: datetime


class FindingListResponse(BaseModel):
    """Paginated finding list."""

    items: List[FindingResponse]
    total: int
    page: int
    page_size: int
