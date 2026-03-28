"""
Monitoring API endpoints — alerts, rules, timelines.

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

from app.core.database import get_db
from app.core.dependencies import (
    get_current_user,
    require_permission,
)
from app.core.logging import get_logger
from app.modules.monitoring.schemas import (
    AlertFilterParams,
    AlertListResponse,
    AlertResolveRequest,
    AlertResponse,
    AlertRuleCreate,
    AlertRuleResponse,
    AlertRuleUpdate,
    VendorTimelineResponse,
)
from app.modules.monitoring.service import (
    MonitoringService,
)

logger = get_logger(__name__)

router = APIRouter(
    prefix="/monitoring", tags=["monitoring"]
)


# -- List Alerts ----------------------------------------------------


@router.get(
    "/alerts",
    response_model=AlertListResponse,
    dependencies=[
        Depends(
            require_permission("monitoring.read")
        )
    ],
)
async def list_alerts(
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
    priority: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(
        None, alias="status"
    ),
    vendor_id: Optional[uuid.UUID] = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> AlertListResponse:
    """List alerts with filtering and pagination."""
    filters = AlertFilterParams(
        priority=priority,
        status=status_filter,
        vendor_id=vendor_id,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
    )
    service = MonitoringService(session)
    return await service.list_alerts(
        current_user["tenant_id"], filters
    )


# -- Get Alert ------------------------------------------------------


@router.get(
    "/alerts/{alert_id}",
    response_model=AlertResponse,
    dependencies=[
        Depends(
            require_permission("monitoring.read")
        )
    ],
)
async def get_alert(
    alert_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
) -> AlertResponse:
    """Fetch a single alert detail."""
    service = MonitoringService(session)
    result = await service.get_alert(
        current_user["tenant_id"], alert_id
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found",
        )
    return result


# -- Acknowledge Alert ----------------------------------------------


@router.put(
    "/alerts/{alert_id}/acknowledge",
    response_model=AlertResponse,
    dependencies=[
        Depends(
            require_permission("monitoring.write")
        )
    ],
)
async def acknowledge_alert(
    alert_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
) -> AlertResponse:
    """Acknowledge an alert."""
    service = MonitoringService(session)
    result = await service.acknowledge_alert(
        current_user["tenant_id"],
        alert_id,
        current_user["user_id"],
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found",
        )
    return result


# -- Resolve Alert --------------------------------------------------


@router.put(
    "/alerts/{alert_id}/resolve",
    response_model=AlertResponse,
    dependencies=[
        Depends(
            require_permission("monitoring.write")
        )
    ],
)
async def resolve_alert(
    alert_id: uuid.UUID,
    body: AlertResolveRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
) -> AlertResponse:
    """Resolve an alert with optional notes."""
    service = MonitoringService(session)
    result = await service.resolve_alert(
        current_user["tenant_id"],
        alert_id,
        current_user["user_id"],
        body.notes,
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found",
        )
    return result


# -- Suppress Alert -------------------------------------------------


@router.put(
    "/alerts/{alert_id}/suppress",
    response_model=AlertResponse,
    dependencies=[
        Depends(
            require_permission("monitoring.write")
        )
    ],
)
async def suppress_alert(
    alert_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
) -> AlertResponse:
    """Suppress an alert."""
    service = MonitoringService(session)
    result = await service.suppress_alert(
        current_user["tenant_id"], alert_id
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found",
        )
    return result


# -- Vendor Timeline ------------------------------------------------


@router.get(
    "/vendors/{vendor_id}/timeline",
    response_model=VendorTimelineResponse,
    dependencies=[
        Depends(
            require_permission("monitoring.read")
        )
    ],
)
async def get_vendor_timeline(
    vendor_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
) -> VendorTimelineResponse:
    """Fetch chronological timeline for a vendor."""
    service = MonitoringService(session)
    return await service.get_vendor_timeline(
        current_user["tenant_id"], vendor_id
    )


# -- Alert Rules ----------------------------------------------------


@router.get(
    "/alert-rules",
    response_model=List[AlertRuleResponse],
    dependencies=[
        Depends(
            require_permission("monitoring.read")
        )
    ],
)
async def list_alert_rules(
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
) -> List[AlertRuleResponse]:
    """List all alert rules."""
    service = MonitoringService(session)
    return await service.list_alert_rules(
        current_user["tenant_id"]
    )


@router.post(
    "/alert-rules",
    response_model=AlertRuleResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(
            require_permission("monitoring.write")
        )
    ],
)
async def create_alert_rule(
    body: AlertRuleCreate,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
) -> AlertRuleResponse:
    """Create a new alert rule."""
    service = MonitoringService(session)
    return await service.create_alert_rule(
        current_user["tenant_id"], body
    )


@router.put(
    "/alert-rules/{rule_id}",
    response_model=AlertRuleResponse,
    dependencies=[
        Depends(
            require_permission("monitoring.write")
        )
    ],
)
async def update_alert_rule(
    rule_id: uuid.UUID,
    body: AlertRuleUpdate,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
) -> AlertRuleResponse:
    """Update an alert rule."""
    service = MonitoringService(session)
    result = await service.update_alert_rule(
        current_user["tenant_id"], rule_id, body
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert rule not found",
        )
    return result
