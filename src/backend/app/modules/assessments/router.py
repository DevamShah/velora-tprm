"""
Assessment API endpoints — CRUD, state transitions, review queue.

All endpoints require authentication. Permissions enforced per-route.
"""

from __future__ import annotations

import uuid
from typing import Annotated

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
from app.modules.assessments.schemas import (
    AssessmentCreate,
    AssessmentDetailResponse,
    AssessmentFilterParams,
    AssessmentListResponse,
    AssessmentResponse,
    AssessmentTemplateCreate,
    AssessmentTemplateResponse,
    AssessmentUpdate,
    QuestionnaireResponseItem,
    QuestionnaireResponseUpdate,
    ReviewQueueResponse,
)
from app.modules.assessments.service import (
    AssessmentService,
)

logger = get_logger(__name__)

router = APIRouter(prefix="/assessments", tags=["assessments"])


# -- List Templates -------------------------------------------------


@router.get(
    "/templates",
    response_model=list[AssessmentTemplateResponse],
    dependencies=[Depends(require_permission("assessments.read"))],
)
async def list_templates(
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> list[AssessmentTemplateResponse]:
    """List available assessment templates."""
    service = AssessmentService(session)
    return await service.list_templates(current_user["tenant_id"])


# -- Create Template ------------------------------------------------


@router.post(
    "/templates",
    response_model=AssessmentTemplateResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("assessments.manage"))],
)
async def create_template(
    body: AssessmentTemplateCreate,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> AssessmentTemplateResponse:
    """Create a new assessment template."""
    service = AssessmentService(session)
    return await service.create_template(current_user["tenant_id"], body)


# -- Review Queue ---------------------------------------------------


@router.get(
    "/review-queue",
    response_model=ReviewQueueResponse,
    dependencies=[Depends(require_permission("assessments.read"))],
)
async def get_review_queue(
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> ReviewQueueResponse:
    """Get responses needing human review."""
    service = AssessmentService(session)
    return await service.get_review_queue(current_user["tenant_id"])


# -- List Assessments -----------------------------------------------


@router.get(
    "",
    response_model=AssessmentListResponse,
    dependencies=[Depends(require_permission("assessments.read"))],
)
async def list_assessments(
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
    status_filter: str | None = Query(None, alias="status"),
    vendor_id: uuid.UUID | None = Query(None),
    template_id: uuid.UUID | None = Query(None),
    search: str | None = Query(None, max_length=255),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> AssessmentListResponse:
    """List assessments with filtering and pagination."""
    filters = AssessmentFilterParams(
        status=status_filter,
        vendor_id=vendor_id,
        template_id=template_id,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
    )
    service = AssessmentService(session)
    return await service.list_assessments(current_user["tenant_id"], filters)


# -- Create Assessment ----------------------------------------------


@router.post(
    "",
    response_model=AssessmentResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("assessments.write"))],
)
async def create_assessment(
    body: AssessmentCreate,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> AssessmentResponse:
    """Create a new assessment from a template."""
    service = AssessmentService(session)
    try:
        return await service.create_assessment(current_user["tenant_id"], body)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# -- Get Assessment Detail ------------------------------------------


@router.get(
    "/{assessment_id}",
    response_model=AssessmentDetailResponse,
    dependencies=[Depends(require_permission("assessments.read"))],
)
async def get_assessment(
    assessment_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> AssessmentDetailResponse:
    """Fetch full assessment detail with responses."""
    service = AssessmentService(session)
    result = await service.get_assessment(
        current_user["tenant_id"], assessment_id
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found",
        )
    return result


# -- Update Assessment ----------------------------------------------


@router.put(
    "/{assessment_id}",
    response_model=AssessmentResponse,
    dependencies=[Depends(require_permission("assessments.write"))],
)
async def update_assessment(
    assessment_id: uuid.UUID,
    body: AssessmentUpdate,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> AssessmentResponse:
    """Update assessment metadata."""
    service = AssessmentService(session)
    result = await service.update_assessment(
        current_user["tenant_id"],
        assessment_id,
        body,
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found",
        )
    return result


# -- Distribute -----------------------------------------------------


@router.post(
    "/{assessment_id}/distribute",
    response_model=AssessmentResponse,
    dependencies=[Depends(require_permission("assessments.manage"))],
)
async def distribute_assessment(
    assessment_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> AssessmentResponse:
    """Distribute assessment to vendor."""
    service = AssessmentService(session)
    try:
        result = await service.distribute_assessment(
            current_user["tenant_id"], assessment_id
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found",
        )
    return result


# -- Submit ---------------------------------------------------------


@router.post(
    "/{assessment_id}/submit",
    response_model=AssessmentResponse,
    dependencies=[Depends(require_permission("assessments.write"))],
)
async def submit_assessment(
    assessment_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> AssessmentResponse:
    """Submit assessment for review."""
    service = AssessmentService(session)
    try:
        result = await service.submit_assessment(
            current_user["tenant_id"], assessment_id
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found",
        )
    return result


# -- Start Review ---------------------------------------------------


@router.post(
    "/{assessment_id}/start-review",
    response_model=AssessmentResponse,
    dependencies=[Depends(require_permission("assessments.manage"))],
)
async def start_review(
    assessment_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> AssessmentResponse:
    """Assign current user as reviewer."""
    service = AssessmentService(session)
    try:
        result = await service.start_review(
            current_user["tenant_id"],
            assessment_id,
            current_user["user_id"],
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found",
        )
    return result


# -- Complete -------------------------------------------------------


@router.post(
    "/{assessment_id}/complete",
    response_model=AssessmentResponse,
    dependencies=[Depends(require_permission("assessments.manage"))],
)
async def complete_assessment(
    assessment_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> AssessmentResponse:
    """Complete assessment with final scoring."""
    service = AssessmentService(session)
    try:
        result = await service.complete_assessment(
            current_user["tenant_id"], assessment_id
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found",
        )
    return result


# -- Cancel ---------------------------------------------------------


@router.post(
    "/{assessment_id}/cancel",
    response_model=AssessmentResponse,
    dependencies=[Depends(require_permission("assessments.manage"))],
)
async def cancel_assessment(
    assessment_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> AssessmentResponse:
    """Cancel an assessment."""
    service = AssessmentService(session)
    try:
        result = await service.cancel_assessment(
            current_user["tenant_id"], assessment_id
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found",
        )
    return result


# -- Get Responses --------------------------------------------------


@router.get(
    "/{assessment_id}/responses",
    response_model=list[QuestionnaireResponseItem],
    dependencies=[Depends(require_permission("assessments.read"))],
)
async def get_responses(
    assessment_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> list[QuestionnaireResponseItem]:
    """Get all responses for an assessment."""
    service = AssessmentService(session)
    result = await service.get_responses(
        current_user["tenant_id"], assessment_id
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment not found",
        )
    return result


# -- Update Response ------------------------------------------------


@router.put(
    "/{assessment_id}/responses/{response_id}",
    response_model=QuestionnaireResponseItem,
    dependencies=[Depends(require_permission("assessments.write"))],
)
async def update_response(
    assessment_id: uuid.UUID,
    response_id: uuid.UUID,
    body: QuestionnaireResponseUpdate,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> QuestionnaireResponseItem:
    """Update or review a questionnaire response."""
    service = AssessmentService(session)
    result = await service.update_response(
        current_user["tenant_id"],
        assessment_id,
        response_id,
        body,
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Response not found",
        )
    return result
