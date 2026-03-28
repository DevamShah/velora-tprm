"""
Reports Pydantic v2 request / response schemas.

Handles dashboard data, report generation, templates,
and dashboard config CRUD.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


# -- Enums ----------------------------------------------------------


class ReportFormat(str, Enum):
    """Supported report output formats."""

    pdf = "pdf"
    pptx = "pptx"
    csv = "csv"


class ReportStatus(str, Enum):
    """Report generation status."""

    pending = "pending"
    generating = "generating"
    completed = "completed"
    failed = "failed"


# -- Dashboard Data -------------------------------------------------


class VendorsByTier(BaseModel):
    """Vendor count breakdown by tier."""

    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    unclassified: int = 0


class AssessmentsByStatus(BaseModel):
    """Assessment count breakdown by status."""

    draft: int = 0
    in_progress: int = 0
    submitted: int = 0
    completed: int = 0
    overdue: int = 0


class FindingsBySeverity(BaseModel):
    """Finding count breakdown by severity."""

    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    info: int = 0


class AlertsByPriority(BaseModel):
    """Alert count breakdown by priority."""

    p0: int = 0
    p1: int = 0
    p2: int = 0
    p3: int = 0
    p4: int = 0


class RecentAlert(BaseModel):
    """Summary alert for dashboard display."""

    id: uuid.UUID
    title: str
    priority: str
    vendor_id: uuid.UUID
    created_at: datetime


class TopRiskVendor(BaseModel):
    """Top risk vendor for dashboard display."""

    id: uuid.UUID
    name: str
    tier: str
    inherent_risk_score: Optional[float] = None
    open_findings: int = 0


class ExecutiveDashboardData(BaseModel):
    """Aggregated executive dashboard data."""

    total_vendors: int = 0
    vendors_by_tier: VendorsByTier = Field(
        default_factory=VendorsByTier
    )
    total_assessments: int = 0
    assessments_by_status: AssessmentsByStatus = Field(
        default_factory=AssessmentsByStatus
    )
    open_findings: int = 0
    findings_by_severity: FindingsBySeverity = Field(
        default_factory=FindingsBySeverity
    )
    active_alerts: int = 0
    alerts_by_priority: AlertsByPriority = Field(
        default_factory=AlertsByPriority
    )
    avg_risk_score: Optional[float] = None
    recent_alerts: List[RecentAlert] = Field(
        default_factory=list
    )
    top_risk_vendors: List[TopRiskVendor] = Field(
        default_factory=list
    )


# -- Report Requests ------------------------------------------------


class GenerateReportRequest(BaseModel):
    """Request to generate a new report."""

    template_id: Optional[uuid.UUID] = None
    title: str = Field(min_length=1, max_length=500)
    format: ReportFormat = ReportFormat.pdf


# -- Report Responses -----------------------------------------------


class ReportResponse(BaseModel):
    """Single generated report response."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    template_id: Optional[uuid.UUID] = None
    title: str
    format: str
    status: str
    s3_key: Optional[str] = None
    generated_by: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime


class ReportListResponse(BaseModel):
    """Paginated report list."""

    items: List[ReportResponse]
    total: int
    page: int
    page_size: int


class ReportTemplateResponse(BaseModel):
    """Report template response."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    description: Optional[str] = None
    template_type: str
    sections: Optional[Dict[str, Any]] = None
    is_system: bool
    created_at: datetime
    updated_at: datetime


# -- Dashboard Config -----------------------------------------------


class DashboardConfigResponse(BaseModel):
    """Dashboard configuration response."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    dashboard_type: str
    widget_layout: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime


class DashboardConfigUpdate(BaseModel):
    """Update dashboard configuration."""

    dashboard_type: Optional[str] = None
    widget_layout: Optional[Dict[str, Any]] = None
