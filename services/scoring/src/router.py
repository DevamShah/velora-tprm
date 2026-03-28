"""
Scoring engine API endpoints — model CRUD, score calculation,
history, and portfolio summary.

All endpoints require authentication and are tenant-scoped.
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

from velora_common.db import get_db
from velora_common.auth import (
    get_current_user,
    require_permission,
)
from velora_common.logging import get_logger
from .schemas import (
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
from .service import ScoringService

logger = get_logger(__name__)

router = APIRouter(prefix="/scoring", tags=["scoring"])


# -- List Scoring Models -------------------------------------------


@router.get(
    "/models",
    response_model=List[ScoringModelResponse],
    dependencies=[
        Depends(require_permission("scoring.read"))
    ],
)
async def list_models(
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
) -> List[ScoringModelResponse]:
    """List scoring models for the current tenant."""
    service = ScoringService(session)
    return await service.list_models(
        current_user["tenant_id"]
    )


# -- Create Scoring Model -----------------------------------------


@router.post(
    "/models",
    response_model=ScoringModelResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(require_permission("scoring.write"))
    ],
)
async def create_model(
    body: ScoringModelCreate,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
) -> ScoringModelResponse:
    """Create a new scoring model."""
    service = ScoringService(session)
    return await service.create_model(
        current_user["tenant_id"], body
    )


# -- Update Scoring Model -----------------------------------------


@router.put(
    "/models/{model_id}",
    response_model=ScoringModelResponse,
    dependencies=[
        Depends(require_permission("scoring.write"))
    ],
)
async def update_model(
    model_id: uuid.UUID,
    body: ScoringModelUpdate,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
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
    dependencies=[
        Depends(require_permission("scoring.write"))
    ],
)
async def bulk_calculate(
    body: BulkCalculateRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
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
    dependencies=[
        Depends(require_permission("scoring.write"))
    ],
)
async def calculate_score(
    vendor_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
    body: CalculateRequest = CalculateRequest(),
) -> ScoreBreakdown:
    """Calculate risk score for a vendor."""
    service = ScoringService(session)
    try:
        result = await service.calculate_score(
            current_user["tenant_id"],
            vendor_id,
            body.scoring_model_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
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
    dependencies=[
        Depends(require_permission("scoring.read"))
    ],
)
async def get_vendor_score(
    vendor_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
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
    dependencies=[
        Depends(require_permission("scoring.read"))
    ],
)
async def get_score_history(
    vendor_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
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
    dependencies=[
        Depends(require_permission("scoring.read"))
    ],
)
async def get_portfolio_summary(
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
) -> PortfolioSummary:
    """Get aggregate scoring summary across portfolio."""
    service = ScoringService(session)
    return await service.get_portfolio_summary(
        current_user["tenant_id"]
    )


# -- FAIR Quantification --------------------------------------------


@router.post(
    "/fair/analyze",
    dependencies=[
        Depends(require_permission("scoring.read"))
    ],
)
async def fair_analyze(
    vendor_id: uuid.UUID,
    data_sensitivity: str = "medium",
    annual_revenue_at_risk: float = 1_000_000,
    session: Annotated[AsyncSession, Depends(get_db)] = None,
    current_user: Annotated[
        dict, Depends(get_current_user)
    ] = None,
) -> dict:
    """Run FAIR risk quantification for a vendor."""
    from .fair import FAIRInput, calculate_fair

    # Get vendor's current risk score
    service = ScoringService(session)
    history = await service.get_score_history(
        current_user["tenant_id"], vendor_id
    )
    current_score = 50.0  # default
    if history and history.items:
        current_score = history.items[0].overall_score

    # Map risk score to threat frequency
    threat_freq = max(0.1, current_score / 20)
    vulnerability = min(1.0, current_score / 100)

    params = FAIRInput(
        vendor_name=str(vendor_id),
        risk_score=current_score,
        data_sensitivity=data_sensitivity,
        annual_revenue_at_risk=annual_revenue_at_risk,
        threat_event_frequency=threat_freq,
        vulnerability=vulnerability,
    )

    result = calculate_fair(params)

    return {
        "vendor_id": str(vendor_id),
        "annual_loss_expectancy": result.annual_loss_expectancy,
        "ale_range": {
            "min": result.ale_min,
            "max": result.ale_max,
        },
        "loss_event_frequency": result.loss_event_frequency,
        "single_loss_expectancy": result.single_loss_expectancy,
        "risk_level": result.risk_level,
        "simulation_count": result.simulation_count,
        "confidence": result.confidence,
    }
