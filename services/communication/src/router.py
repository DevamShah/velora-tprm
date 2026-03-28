"""
Communications API endpoints — notifications, preferences, templates, logs.

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
    CommLogListResponse,
    EmailTemplateCreate,
    EmailTemplateResponse,
    EmailTemplateUpdate,
    NotificationListResponse,
    NotificationResponse,
    PreferenceResponse,
    PreferenceUpdate,
)
from .service import (
    CommunicationsService,
)

logger = get_logger(__name__)

router = APIRouter(
    prefix="/communications",
    tags=["communications"],
)


# -- List Notifications ---------------------------------------------


@router.get(
    "/notifications",
    response_model=NotificationListResponse,
)
async def list_notifications(
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> NotificationListResponse:
    """List notifications for the current user."""
    service = CommunicationsService(session)
    return await service.list_notifications(
        current_user["tenant_id"],
        current_user["user_id"],
        page,
        page_size,
    )


# -- Mark Notification Read -----------------------------------------


@router.put(
    "/notifications/{notification_id}/read",
    response_model=NotificationResponse,
)
async def mark_notification_read(
    notification_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
) -> NotificationResponse:
    """Mark a single notification as read."""
    service = CommunicationsService(session)
    result = await service.mark_read(
        current_user["tenant_id"], notification_id
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )
    return result


# -- Mark All Notifications Read ------------------------------------


@router.put(
    "/notifications/read-all",
    response_model=dict,
)
async def mark_all_notifications_read(
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
) -> dict:
    """Mark all unread notifications as read."""
    service = CommunicationsService(session)
    count = await service.mark_all_read(
        current_user["tenant_id"],
        current_user["user_id"],
    )
    return {"marked_read": count}


# -- Get Preferences ------------------------------------------------


@router.get(
    "/preferences",
    response_model=List[PreferenceResponse],
)
async def get_preferences(
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
) -> List[PreferenceResponse]:
    """Fetch notification preferences for current user."""
    service = CommunicationsService(session)
    return await service.get_preferences(
        current_user["tenant_id"],
        current_user["user_id"],
    )


# -- Update Preferences ---------------------------------------------


@router.put(
    "/preferences",
    response_model=PreferenceResponse,
)
async def update_preferences(
    body: PreferenceUpdate,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
) -> PreferenceResponse:
    """Create or update a notification preference."""
    service = CommunicationsService(session)
    return await service.update_preferences(
        current_user["tenant_id"],
        current_user["user_id"],
        body,
    )


# -- List Email Templates -------------------------------------------


@router.get(
    "/templates",
    response_model=List[EmailTemplateResponse],
    dependencies=[
        Depends(require_permission("admin.settings"))
    ],
)
async def list_email_templates(
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
) -> List[EmailTemplateResponse]:
    """List all email templates."""
    service = CommunicationsService(session)
    return await service.list_email_templates(
        current_user["tenant_id"]
    )


# -- Create Email Template ------------------------------------------


@router.post(
    "/templates",
    response_model=EmailTemplateResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(require_permission("admin.settings"))
    ],
)
async def create_email_template(
    body: EmailTemplateCreate,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
) -> EmailTemplateResponse:
    """Create a new email template."""
    service = CommunicationsService(session)
    return await service.create_email_template(
        current_user["tenant_id"], body
    )


# -- Update Email Template ------------------------------------------


@router.put(
    "/templates/{template_id}",
    response_model=EmailTemplateResponse,
    dependencies=[
        Depends(require_permission("admin.settings"))
    ],
)
async def update_email_template(
    template_id: uuid.UUID,
    body: EmailTemplateUpdate,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
) -> EmailTemplateResponse:
    """Update an existing email template."""
    service = CommunicationsService(session)
    result = await service.update_email_template(
        current_user["tenant_id"], template_id, body
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email template not found",
        )
    return result


# -- Communication Logs ---------------------------------------------


@router.get(
    "/logs",
    response_model=CommLogListResponse,
    dependencies=[
        Depends(require_permission("admin.settings"))
    ],
)
async def get_communication_logs(
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[
        dict, Depends(get_current_user)
    ],
    channel: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(
        None, alias="status"
    ),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> CommLogListResponse:
    """List communication logs with optional filters."""
    service = CommunicationsService(session)
    return await service.get_communication_logs(
        current_user["tenant_id"],
        channel=channel,
        status_filter=status_filter,
        page=page,
        page_size=page_size,
    )
