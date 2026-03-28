"""
Reports API endpoints — dashboards, report generation, templates.

All endpoints require authentication. Permissions enforced per-route.
"""

from __future__ import annotations

import uuid
from typing import Annotated, List, Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from velora_common.db import get_db
from velora_common.auth import (
    get_current_user,
    require_permission,
)
from velora_common.logging import get_logger
from .schemas import (
    DashboardConfigResponse,
    DashboardConfigUpdate,
    ExecutiveDashboardData,
    GenerateReportRequest,
    ReportListResponse,
    ReportResponse,
    ReportTemplateResponse,
)
from .service import ReportsService

logger = get_logger(__name__)

router = APIRouter(prefix="/reports", tags=["reports"])


# -- Executive Dashboard Data --------------------------------------


@router.get(
    "/dashboards/data/executive",
    response_model=ExecutiveDashboardData,
    dependencies=[
        Depends(require_permission("reports.read"))
    ],
)
async def get_executive_dashboard(
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
) -> ExecutiveDashboardData:
    """Fetch aggregated executive dashboard data."""
    service = ReportsService(session)
    return await service.get_executive_dashboard(
        current_user["tenant_id"]
    )


# -- Generate Report -----------------------------------------------


@router.post(
    "/generate",
    response_model=ReportResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(
            require_permission("reports.generate")
        )
    ],
)
async def generate_report(
    body: GenerateReportRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
) -> ReportResponse:
    """Generate a new report."""
    service = ReportsService(session)
    return await service.generate_report(
        tenant_id=current_user["tenant_id"],
        template_id=body.template_id,
        title=body.title,
        fmt=body.format.value,
        generated_by=current_user["user_id"],
    )


# -- List Reports ---------------------------------------------------


@router.get(
    "",
    response_model=ReportListResponse,
    dependencies=[
        Depends(require_permission("reports.read"))
    ],
)
async def list_reports(
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> ReportListResponse:
    """List generated reports with pagination."""
    service = ReportsService(session)
    return await service.list_reports(
        current_user["tenant_id"], page, page_size
    )


# -- Get Report -----------------------------------------------------


@router.get(
    "/{report_id}",
    response_model=ReportResponse,
    dependencies=[
        Depends(require_permission("reports.read"))
    ],
)
async def get_report(
    report_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
) -> ReportResponse:
    """Fetch a single generated report."""
    service = ReportsService(session)
    result = await service.get_report(
        current_user["tenant_id"], report_id
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found",
        )
    return result


# -- List Templates -------------------------------------------------


@router.get(
    "/templates",
    response_model=List[ReportTemplateResponse],
    dependencies=[
        Depends(require_permission("reports.read"))
    ],
)
async def list_templates(
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
) -> List[ReportTemplateResponse]:
    """List all report templates."""
    service = ReportsService(session)
    return await service.list_templates(
        current_user["tenant_id"]
    )


# -- Get Dashboard Config -------------------------------------------


@router.get(
    "/dashboards",
    response_model=Optional[DashboardConfigResponse],
    dependencies=[
        Depends(require_permission("reports.read"))
    ],
)
async def get_dashboard_config(
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
) -> Optional[DashboardConfigResponse]:
    """Fetch current user's dashboard configuration."""
    service = ReportsService(session)
    return await service.get_dashboard_config(
        current_user["tenant_id"],
        current_user["user_id"],
    )


# -- Update Dashboard Config ----------------------------------------


@router.put(
    "/dashboards/{config_id}",
    response_model=DashboardConfigResponse,
    dependencies=[
        Depends(require_permission("reports.read"))
    ],
)
async def update_dashboard_config(
    config_id: uuid.UUID,
    body: DashboardConfigUpdate,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
) -> DashboardConfigResponse:
    """Update dashboard configuration."""
    service = ReportsService(session)
    return await service.update_dashboard_config(
        current_user["tenant_id"],
        current_user["user_id"],
        body,
    )
