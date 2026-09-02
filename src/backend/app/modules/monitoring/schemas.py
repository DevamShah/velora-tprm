"""
Monitoring Pydantic v2 request / response schemas.

Handles alerts, signals, rules, and vendor timelines.
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


class AlertPriority(str, Enum):
    """Alert priority levels."""

    p0 = "p0"
    p1 = "p1"
    p2 = "p2"
    p3 = "p3"
    p4 = "p4"


class AlertStatus(str, Enum):
    """Alert lifecycle states."""

    new = "new"
    acknowledged = "acknowledged"
    investigating = "investigating"
    resolved = "resolved"
    suppressed = "suppressed"


class SignalSeverity(str, Enum):
    """Signal severity levels."""

    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"
    info = "info"


class SortOrder(str, Enum):
    """Sort direction."""

    asc = "asc"
    desc = "desc"


# -- Alert Requests -------------------------------------------------


class AlertResolveRequest(BaseModel):
    """Resolve an alert with notes."""

    notes: str | None = Field(None, max_length=2000)


# -- Alert Rule Requests --------------------------------------------


class AlertRuleCreate(BaseModel):
    """Create an alert rule."""

    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    conditions: dict[str, Any]
    actions: dict[str, Any]
    is_active: bool = True


class AlertRuleUpdate(BaseModel):
    """Update an alert rule — all fields optional."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    conditions: dict[str, Any] | None = None
    actions: dict[str, Any] | None = None
    is_active: bool | None = None


# -- Filter ---------------------------------------------------------


class AlertFilterParams(BaseModel):
    """Query parameters for alert listing."""

    priority: AlertPriority | None = None
    status: AlertStatus | None = None
    vendor_id: uuid.UUID | None = None
    sort_by: str = Field(default="created_at")
    sort_order: SortOrder = SortOrder.desc
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

    @field_validator("sort_by")
    @classmethod
    def validate_sort_by(cls, value: str) -> str:
        allowed = {
            "created_at",
            "priority",
            "status",
            "title",
        }
        if value not in allowed:
            raise ValueError(f"sort_by must be one of {allowed}")
        return value


# -- Responses ------------------------------------------------------


class AlertResponse(BaseModel):
    """Alert summary for list views."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    vendor_id: uuid.UUID
    priority: str
    status: str
    title: str
    description: str | None = None
    signal_ids: list[uuid.UUID] | None = None
    impact_assessment: dict[str, Any] | None = None
    acknowledged_by: uuid.UUID | None = None
    resolved_by: uuid.UUID | None = None
    acknowledged_at: datetime | None = None
    resolved_at: datetime | None = None
    resolution_notes: str | None = None
    created_at: datetime
    updated_at: datetime


class AlertListResponse(BaseModel):
    """Paginated alert list."""

    items: list[AlertResponse]
    total: int
    page: int
    page_size: int


class AlertRuleResponse(BaseModel):
    """Alert rule detail."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    description: str | None = None
    conditions: dict[str, Any]
    actions: dict[str, Any]
    is_active: bool
    created_at: datetime
    updated_at: datetime


class VendorTimelineEvent(BaseModel):
    """Single event on a vendor timeline."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    vendor_id: uuid.UUID
    event_type: str
    title: str
    description: str | None = None
    metadata: dict[str, Any] | None = None
    actor_id: uuid.UUID | None = None
    created_at: datetime


class VendorTimelineResponse(BaseModel):
    """Chronological vendor timeline."""

    vendor_id: uuid.UUID
    events: list[VendorTimelineEvent]
    total: int


class SignalIngestRequest(BaseModel):
    """Ingest a monitoring signal."""

    vendor_id: uuid.UUID
    source: str = Field(min_length=1)
    signal_type: str = Field(min_length=1)
    severity: SignalSeverity = SignalSeverity.info
    title: str = Field(min_length=1, max_length=500)
    description: str | None = None
    raw_data: dict[str, Any] | None = None
    dedup_key: str | None = None


class SignalResponse(BaseModel):
    """Response after signal ingestion."""

    signal_id: uuid.UUID
    alerts_created: int
