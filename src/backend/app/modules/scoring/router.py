"""
Scoring engine API endpoints — model CRUD, score calculation,
history, and portfolio summary.

All endpoints require authentication and are tenant-scoped.
"""

from __future__ import annotations

import uuid
from typing import Annotated

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
from app.modules.scoring.schemas import (
    BulkCalculateRequest,
    BulkCalculateResponse,
    CalculateRequest,
    PortfolioSummary,
    ScoreBreakdown,
    ScoreHistoryResponse,
    ScoringModelCreate,
    ScoringModelResponse,
    ScoringModelUpdate,
)
from app.modules.scoring.service import ScoringService

logger = get_logger(__name__)

router = APIRouter(prefix="/scoring", tags=["scoring"])


# -- List Scoring Models -------------------------------------------


@router.get(
    "/models",
    response_model=list[ScoringModelResponse],
    dependencies=[Depends(require_permission("scoring.read"))],
)
async def list_models(
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> list[ScoringModelResponse]:
    """List scoring models for the current tenant."""
    service = ScoringService(session)
    return await service.list_models(current_user["tenant_id"])


# -- Create Scoring Model -----------------------------------------


@router.post(
    "/models",
    response_model=ScoringModelResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("scoring.write"))],
)
async def create_model(
    body: ScoringModelCreate,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> ScoringModelResponse:
    """Create a new scoring model."""
    service = ScoringService(session)
    return await service.create_model(current_user["tenant_id"], body)


# -- Update Scoring Model -----------------------------------------


@router.put(
    "/models/{model_id}",
    response_model=ScoringModelResponse,
    dependencies=[Depends(require_permission("scoring.write"))],
)
async def update_model(
    model_id: uuid.UUID,
    body: ScoringModelUpdate,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> ScoringModelResponse:
    """Update an existing scoring model."""
    service = ScoringService(session)
    result = await service.update_model(
        current_user["tenant_id"], model_id, body
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scoring model not found",
        )
    return result


# -- Bulk Calculate ------------------------------------------------
# Must be registered before /calculate/{vendor_id} to avoid collision


@router.post(
    "/calculate/bulk",
    response_model=BulkCalculateResponse,
    dependencies=[Depends(require_permission("scoring.write"))],
)
async def bulk_calculate(
    body: BulkCalculateRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> BulkCalculateResponse:
    """Calculate scores for multiple vendors at once."""
    service = ScoringService(session)
    return await service.bulk_calculate(
        current_user["tenant_id"],
        body.vendor_ids,
        body.scoring_model_id,
    )


# -- Calculate Score -----------------------------------------------


@router.post(
    "/calculate/{vendor_id}",
    response_model=ScoreBreakdown,
    dependencies=[Depends(require_permission("scoring.write"))],
)
async def calculate_score(
    vendor_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
    body: CalculateRequest | None = None,
) -> ScoreBreakdown:
    """Calculate risk score for a vendor."""
    service = ScoringService(session)
    try:
        result = await service.calculate_score(
            current_user["tenant_id"],
            vendor_id,
            body.scoring_model_id if body else None,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vendor not found",
        )
    return result


# -- Get Vendor Score ----------------------------------------------


@router.get(
    "/vendors/{vendor_id}",
    response_model=ScoreBreakdown,
    dependencies=[Depends(require_permission("scoring.read"))],
)
async def get_vendor_score(
    vendor_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> ScoreBreakdown:
    """Get current score for a vendor."""
    service = ScoringService(session)
    result = await service.get_vendor_score(
        current_user["tenant_id"], vendor_id
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Score not found for vendor",
        )
    return result


# -- Score History -------------------------------------------------


@router.get(
    "/vendors/{vendor_id}/history",
    response_model=ScoreHistoryResponse,
    dependencies=[Depends(require_permission("scoring.read"))],
)
async def get_score_history(
    vendor_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> ScoreHistoryResponse:
    """Get historical scores for a vendor."""
    service = ScoringService(session)
    return await service.get_score_history(
        current_user["tenant_id"], vendor_id
    )


# -- Portfolio Summary ---------------------------------------------


@router.get(
    "/portfolio",
    response_model=PortfolioSummary,
    dependencies=[Depends(require_permission("scoring.read"))],
)
async def get_portfolio_summary(
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> PortfolioSummary:
    """Get aggregate scoring summary across portfolio."""
    service = ScoringService(session)
    return await service.get_portfolio_summary(current_user["tenant_id"])
