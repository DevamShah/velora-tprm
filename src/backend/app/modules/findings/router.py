"""
Findings API endpoints — CRUD, remediation, close.

All endpoints require authentication. Permissions enforced per-route.
"""

from __future__ import annotations

import uuid
from typing import Annotated, Optional

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
from app.modules.findings.schemas import (
    FindingClose,
    FindingCreate,
    FindingListResponse,
    FindingResponse,
    FindingUpdate,
    RemediationCreate,
    RemediationResponse,
    RemediationUpdate,
)
from app.modules.findings.service import FindingsService

logger = get_logger(__name__)

router = APIRouter(
    prefix="/findings", tags=["findings"]
)


# -- List Findings --------------------------------------------------


@router.get(
    "",
    response_model=FindingListResponse,
    dependencies=[
        Depends(
            require_permission("assessments.read")
        )
    ],
)
async def list_findings(
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
    vendor_id: Optional[uuid.UUID] = Query(None),
    severity: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(
        None, alias="status"
    ),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> FindingListResponse:
    """List findings with optional filters."""
    service = FindingsService(session)
    return await service.list_findings(
        tenant_id=current_user["tenant_id"],
        vendor_id=vendor_id,
        severity=severity,
        status=status_filter,
        page=page,
        page_size=page_size,
    )


# -- Create Finding -------------------------------------------------


@router.post(
    "",
    response_model=FindingResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(
            require_permission("assessments.write")
        )
    ],
)
async def create_finding(
    body: FindingCreate,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
) -> FindingResponse:
    """Create a new finding."""
    service = FindingsService(session)
    return await service.create_finding(
        current_user["tenant_id"], body
    )


# -- Get Finding ----------------------------------------------------


@router.get(
    "/{finding_id}",
    response_model=FindingResponse,
    dependencies=[
        Depends(
            require_permission("assessments.read")
        )
    ],
)
async def get_finding(
    finding_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
) -> FindingResponse:
    """Fetch a single finding with remediation actions."""
    service = FindingsService(session)
    result = await service.get_finding(
        current_user["tenant_id"], finding_id
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Finding not found",
        )
    return result


# -- Update Finding -------------------------------------------------


@router.put(
    "/{finding_id}",
    response_model=FindingResponse,
    dependencies=[
        Depends(
            require_permission("assessments.write")
        )
    ],
)
async def update_finding(
    finding_id: uuid.UUID,
    body: FindingUpdate,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
) -> FindingResponse:
    """Update a finding."""
    service = FindingsService(session)
    result = await service.update_finding(
        current_user["tenant_id"], finding_id, body
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Finding not found",
        )
    return result


# -- Close Finding --------------------------------------------------


@router.post(
    "/{finding_id}/close",
    response_model=FindingResponse,
    dependencies=[
        Depends(
            require_permission("assessments.write")
        )
    ],
)
async def close_finding(
    finding_id: uuid.UUID,
    body: FindingClose,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
) -> FindingResponse:
    """Close a finding with a final status."""
    service = FindingsService(session)
    result = await service.close_finding(
        current_user["tenant_id"], finding_id, body
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Finding not found",
        )
    return result


# -- Add Remediation ------------------------------------------------


@router.post(
    "/{finding_id}/remediation",
    response_model=RemediationResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(
            require_permission("assessments.write")
        )
    ],
)
async def add_remediation(
    finding_id: uuid.UUID,
    body: RemediationCreate,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
) -> RemediationResponse:
    """Add a remediation action to a finding."""
    service = FindingsService(session)
    result = await service.add_remediation(
        current_user["tenant_id"], finding_id, body
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Finding not found",
        )
    return result


# -- Update Remediation ---------------------------------------------


@router.put(
    "/{finding_id}/remediation/{action_id}",
    response_model=RemediationResponse,
    dependencies=[
        Depends(
            require_permission("assessments.write")
        )
    ],
)
async def update_remediation(
    finding_id: uuid.UUID,
    action_id: uuid.UUID,
    body: RemediationUpdate,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
) -> RemediationResponse:
    """Update a remediation action."""
    service = FindingsService(session)
    result = await service.update_remediation(
        current_user["tenant_id"],
        finding_id,
        action_id,
        body,
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Remediation action not found",
        )
    return result
