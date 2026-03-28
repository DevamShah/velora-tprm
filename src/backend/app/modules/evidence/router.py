"""
Evidence API endpoints — upload, process, list, map, verify.

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
from app.modules.evidence.schemas import (
    EvidenceControlMappingResponse,
    EvidenceDetailResponse,
    EvidenceFilterParams,
    EvidenceListResponse,
    EvidenceUploadRequest,
    EvidenceUploadResponse,
    MappingVerifyRequest,
)
from app.modules.evidence.service import EvidenceService

logger = get_logger(__name__)

router = APIRouter(
    prefix="/evidence", tags=["evidence"]
)


# -- Upload URL -----------------------------------------------------


@router.post(
    "/upload-url",
    response_model=EvidenceUploadResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(require_permission("evidence.write"))
    ],
)
async def upload_evidence(
    body: EvidenceUploadRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
) -> EvidenceUploadResponse:
    """Generate a presigned upload URL and create record."""
    service = EvidenceService(session)
    return await service.upload_evidence(
        current_user["tenant_id"],
        body,
        current_user["user_id"],
    )


# -- Process --------------------------------------------------------


@router.post(
    "/{evidence_id}/process",
    response_model=EvidenceDetailResponse,
    dependencies=[
        Depends(require_permission("evidence.write"))
    ],
)
async def process_evidence(
    evidence_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
) -> EvidenceDetailResponse:
    """Trigger AI processing on uploaded evidence."""
    service = EvidenceService(session)
    result = await service.process_evidence(
        current_user["tenant_id"], evidence_id
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evidence not found",
        )
    return result


# -- List -----------------------------------------------------------


@router.get(
    "",
    response_model=EvidenceListResponse,
    dependencies=[
        Depends(require_permission("evidence.read"))
    ],
)
async def list_evidence(
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
    vendor_id: Optional[uuid.UUID] = Query(None),
    document_type: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(
        None, alias="status"
    ),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> EvidenceListResponse:
    """List evidence with filtering and pagination."""
    filters = EvidenceFilterParams(
        vendor_id=vendor_id,
        document_type=document_type,
        status=status_filter,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
    )
    service = EvidenceService(session)
    return await service.list_evidence(
        current_user["tenant_id"], filters
    )


# -- Get Detail -----------------------------------------------------


@router.get(
    "/{evidence_id}",
    response_model=EvidenceDetailResponse,
    dependencies=[
        Depends(require_permission("evidence.read"))
    ],
)
async def get_evidence(
    evidence_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
) -> EvidenceDetailResponse:
    """Fetch full evidence detail."""
    service = EvidenceService(session)
    result = await service.get_evidence(
        current_user["tenant_id"], evidence_id
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evidence not found",
        )
    return result


# -- Get Mappings ---------------------------------------------------


@router.get(
    "/{evidence_id}/mappings",
    response_model=List[EvidenceControlMappingResponse],
    dependencies=[
        Depends(require_permission("evidence.read"))
    ],
)
async def get_mappings(
    evidence_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
) -> List[EvidenceControlMappingResponse]:
    """List control mappings for evidence."""
    service = EvidenceService(session)
    result = await service.get_mappings(
        current_user["tenant_id"], evidence_id
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evidence not found",
        )
    return result


# -- Verify Mapping -------------------------------------------------


@router.put(
    "/{evidence_id}/mappings/{mapping_id}",
    response_model=EvidenceControlMappingResponse,
    dependencies=[
        Depends(require_permission("evidence.write"))
    ],
)
async def verify_mapping(
    evidence_id: uuid.UUID,
    mapping_id: uuid.UUID,
    body: MappingVerifyRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
) -> EvidenceControlMappingResponse:
    """Verify or reject a control mapping."""
    service = EvidenceService(session)
    result = await service.verify_mapping(
        current_user["tenant_id"],
        evidence_id,
        mapping_id,
        body.verified,
        current_user["user_id"],
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mapping not found",
        )
    return result


# -- Delete ---------------------------------------------------------


@router.delete(
    "/{evidence_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Depends(require_permission("evidence.write"))
    ],
)
async def delete_evidence(
    evidence_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
) -> None:
    """Soft-delete evidence."""
    service = EvidenceService(session)
    deleted = await service.delete_evidence(
        current_user["tenant_id"], evidence_id
    )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evidence not found",
        )
