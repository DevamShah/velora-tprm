"""
Framework API endpoints — list, detail, clause trees, mappings,
unified control library.

All endpoints require authentication. Frameworks are read-only
global reference data.
"""

from __future__ import annotations

import uuid
from typing import Annotated, List

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import (
    get_current_user,
    require_permission,
)
from app.core.logging import get_logger
from app.modules.frameworks.schemas import (
    FrameworkDetailResponse,
    FrameworkListResponse,
    MappingResponse,
    UnifiedControl,
)
from app.modules.frameworks.service import (
    FrameworkService,
)

logger = get_logger(__name__)

router = APIRouter(
    prefix="/frameworks", tags=["frameworks"]
)


# -- List Frameworks ------------------------------------------------


@router.get(
    "",
    response_model=FrameworkListResponse,
    dependencies=[
        Depends(require_permission("frameworks.read"))
    ],
)
async def list_frameworks(
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
) -> FrameworkListResponse:
    """List all compliance frameworks."""
    service = FrameworkService(session)
    return await service.list_frameworks()


# -- Unified Control Library ----------------------------------------
# Must be registered before /{framework_id} to avoid path collision


@router.get(
    "/unified-controls",
    response_model=List[UnifiedControl],
    dependencies=[
        Depends(require_permission("frameworks.read"))
    ],
)
async def get_unified_controls(
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
) -> List[UnifiedControl]:
    """Get deduplicated controls across all frameworks."""
    service = FrameworkService(session)
    return await service.get_unified_controls()


# -- Get Framework Detail -------------------------------------------


@router.get(
    "/{framework_id}",
    response_model=FrameworkDetailResponse,
    dependencies=[
        Depends(require_permission("frameworks.read"))
    ],
)
async def get_framework(
    framework_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
) -> FrameworkDetailResponse:
    """Fetch framework detail with clause tree."""
    service = FrameworkService(session)
    result = await service.get_framework(framework_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Framework not found",
        )
    return result


# -- Get Clause Tree ------------------------------------------------


@router.get(
    "/{framework_id}/clauses",
    response_model=list,
    dependencies=[
        Depends(require_permission("frameworks.read"))
    ],
)
async def get_clause_tree(
    framework_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
) -> list:
    """Get hierarchical clause structure for a framework."""
    service = FrameworkService(session)
    return await service.get_clause_tree(framework_id)


# -- Get Clause Mappings --------------------------------------------


@router.get(
    "/{framework_id}/clauses/{clause_id}/mappings",
    response_model=List[MappingResponse],
    dependencies=[
        Depends(require_permission("frameworks.read"))
    ],
)
async def get_clause_mappings(
    framework_id: uuid.UUID,
    clause_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
) -> List[MappingResponse]:
    """Get cross-framework mappings for a clause."""
    service = FrameworkService(session)
    return await service.get_clause_mappings(clause_id)
