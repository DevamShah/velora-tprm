"""
AI API endpoints — auto-fill, review queue, usage stats.

All endpoints require authentication. Permissions enforced per-route.
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
from app.modules.ai.schemas import (
    AIUsageStats,
    AutoFillRequest,
    AutoFillResponse,
    ReviewQueueResponse,
    ReviewSubmitRequest,
    ReviewSubmitResponse,
)
from app.modules.ai.service import AIService

logger = get_logger(__name__)

router = APIRouter(prefix="/ai", tags=["ai"])


# -- Auto-Fill ------------------------------------------------------


@router.post(
    "/auto-fill",
    response_model=AutoFillResponse,
    dependencies=[
        Depends(
            require_permission("assessments.write")
        )
    ],
)
async def auto_fill(
    body: AutoFillRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
) -> AutoFillResponse:
    """Trigger AI auto-fill for an assessment."""
    service = AIService(session)
    result = await service.auto_fill_assessment(
        current_user["tenant_id"], body.assessment_id
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found",
        )
    return result


# -- Review Queue ---------------------------------------------------


@router.get(
    "/review-queue",
    response_model=ReviewQueueResponse,
    dependencies=[
        Depends(
            require_permission("assessments.write")
        )
    ],
)
async def get_review_queue(
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
) -> ReviewQueueResponse:
    """Get items needing human review."""
    service = AIService(session)
    return await service.get_review_queue(
        current_user["tenant_id"]
    )


# -- Submit Review --------------------------------------------------


@router.put(
    "/review-queue/{item_id}",
    response_model=ReviewSubmitResponse,
    dependencies=[
        Depends(
            require_permission("assessments.write")
        )
    ],
)
async def submit_review(
    item_id: uuid.UUID,
    body: ReviewSubmitRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
) -> ReviewSubmitResponse:
    """Submit a review decision for a queue item."""
    service = AIService(session)
    result = await service.submit_review(
        current_user["tenant_id"], item_id, body
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review item not found",
        )
    return result


# -- Usage Stats ----------------------------------------------------


@router.get(
    "/usage",
    response_model=AIUsageStats,
    dependencies=[
        Depends(
            require_permission("assessments.read")
        )
    ],
)
async def get_usage(
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
) -> AIUsageStats:
    """Get AI usage statistics for the tenant."""
    service = AIService(session)
    return await service.get_usage_stats(
        current_user["tenant_id"]
    )
