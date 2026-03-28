"""
Communications business logic — notifications, preferences, templates, logs.

All DB queries run inside the caller-provided async session.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.modules.communications.models import (
    CommunicationLog,
    EmailTemplate,
    Notification,
    NotificationPreference,
)
from app.modules.communications.schemas import (
    CommLogListResponse,
    CommLogResponse,
    EmailTemplateCreate,
    EmailTemplateResponse,
    EmailTemplateUpdate,
    NotificationListResponse,
    NotificationResponse,
    PreferenceResponse,
    PreferenceUpdate,
)

logger = get_logger(__name__)


class CommunicationsService:
    """Stateless communications service."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # -- List Notifications -----------------------------------------

    async def list_notifications(
        self,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> NotificationListResponse:
        """List notifications for a user with pagination."""
        base = select(Notification).where(
            Notification.tenant_id == tenant_id,
            Notification.user_id == user_id,
        )
        count_q = select(func.count()).select_from(
            base.subquery()
        )
        total = (
            await self._session.execute(count_q)
        ).scalar() or 0

        offset = (page - 1) * page_size
        result = await self._session.execute(
            base.order_by(
                Notification.created_at.desc()
            )
            .offset(offset)
            .limit(page_size)
        )
        items = result.scalars().all()

        return NotificationListResponse(
            items=[
                self._to_notification(n) for n in items
            ],
            total=total,
            page=page,
            page_size=page_size,
        )

    # -- Mark Read --------------------------------------------------

    async def mark_read(
        self,
        tenant_id: uuid.UUID,
        notification_id: uuid.UUID,
    ) -> Optional[NotificationResponse]:
        """Mark a single notification as read."""
        result = await self._session.execute(
            select(Notification).where(
                Notification.id == notification_id,
                Notification.tenant_id == tenant_id,
            )
        )
        notif = result.scalars().first()
        if notif is None:
            return None

        notif.read = True
        notif.read_at = datetime.now(timezone.utc)
        await self._session.flush()
        return self._to_notification(notif)

    # -- Mark All Read ----------------------------------------------

    async def mark_all_read(
        self,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> int:
        """Mark all unread notifications as read."""
        result = await self._session.execute(
            select(Notification).where(
                Notification.tenant_id == tenant_id,
                Notification.user_id == user_id,
                Notification.read.is_(False),
            )
        )
        notifs = result.scalars().all()
        now = datetime.now(timezone.utc)
        for n in notifs:
            n.read = True
            n.read_at = now
        await self._session.flush()
        return len(notifs)

    # -- Get Preferences --------------------------------------------

    async def get_preferences(
        self,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> List[PreferenceResponse]:
        """Fetch notification preferences for a user."""
        result = await self._session.execute(
            select(NotificationPreference).where(
                NotificationPreference.tenant_id
                == tenant_id,
                NotificationPreference.user_id
                == user_id,
            )
        )
        prefs = result.scalars().all()
        return [self._to_preference(p) for p in prefs]

    # -- Update Preferences -----------------------------------------

    async def update_preferences(
        self,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        data: PreferenceUpdate,
    ) -> PreferenceResponse:
        """Create or update a notification preference."""
        result = await self._session.execute(
            select(NotificationPreference).where(
                NotificationPreference.tenant_id
                == tenant_id,
                NotificationPreference.user_id
                == user_id,
                NotificationPreference.category
                == data.category,
            )
        )
        pref = result.scalars().first()

        if pref is None:
            pref = NotificationPreference(
                tenant_id=tenant_id,
                user_id=user_id,
                category=data.category,
                channel_config=data.channel_config,
                quiet_hours_start=data.quiet_hours_start,
                quiet_hours_end=data.quiet_hours_end,
            )
            self._session.add(pref)
        else:
            update_data = data.model_dump(
                exclude_unset=True
            )
            for field, value in update_data.items():
                setattr(pref, field, value)

        await self._session.flush()
        return self._to_preference(pref)

    # -- Email Templates --------------------------------------------

    async def list_email_templates(
        self,
        tenant_id: uuid.UUID,
    ) -> List[EmailTemplateResponse]:
        """List all email templates for tenant."""
        result = await self._session.execute(
            select(EmailTemplate).where(
                EmailTemplate.tenant_id == tenant_id
            )
        )
        templates = result.scalars().all()
        return [
            self._to_email_template(t)
            for t in templates
        ]

    async def create_email_template(
        self,
        tenant_id: uuid.UUID,
        data: EmailTemplateCreate,
    ) -> EmailTemplateResponse:
        """Create a new email template."""
        template = EmailTemplate(
            tenant_id=tenant_id,
            name=data.name,
            subject_template=data.subject_template,
            body_template=data.body_template,
            variables=data.variables,
            is_system=data.is_system,
        )
        self._session.add(template)
        await self._session.flush()
        logger.info(
            "email_template_created",
            template_id=str(template.id),
        )
        return self._to_email_template(template)

    async def update_email_template(
        self,
        tenant_id: uuid.UUID,
        template_id: uuid.UUID,
        data: EmailTemplateUpdate,
    ) -> Optional[EmailTemplateResponse]:
        """Update an existing email template."""
        result = await self._session.execute(
            select(EmailTemplate).where(
                EmailTemplate.id == template_id,
                EmailTemplate.tenant_id == tenant_id,
            )
        )
        template = result.scalars().first()
        if template is None:
            return None

        update_data = data.model_dump(
            exclude_unset=True
        )
        for field, value in update_data.items():
            setattr(template, field, value)

        await self._session.flush()
        logger.info(
            "email_template_updated",
            template_id=str(template_id),
        )
        return self._to_email_template(template)

    # -- Send Notification ------------------------------------------

    async def send_notification(
        self,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        title: str,
        message: str,
        channel: str = "in_app",
        entity_type: Optional[str] = None,
        entity_id: Optional[uuid.UUID] = None,
    ) -> NotificationResponse:
        """Create a notification record."""
        notif = Notification(
            tenant_id=tenant_id,
            user_id=user_id,
            title=title,
            message=message,
            channel=channel,
            entity_type=entity_type,
            entity_id=entity_id,
        )
        self._session.add(notif)
        await self._session.flush()
        logger.info(
            "notification_sent",
            notification_id=str(notif.id),
        )
        return self._to_notification(notif)

    # -- Communication Logs -----------------------------------------

    async def get_communication_logs(
        self,
        tenant_id: uuid.UUID,
        channel: Optional[str] = None,
        status_filter: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> CommLogListResponse:
        """List communication logs with filters."""
        base = select(CommunicationLog).where(
            CommunicationLog.tenant_id == tenant_id
        )
        if channel:
            base = base.where(
                CommunicationLog.channel == channel
            )
        if status_filter:
            base = base.where(
                CommunicationLog.status == status_filter
            )

        count_q = select(func.count()).select_from(
            base.subquery()
        )
        total = (
            await self._session.execute(count_q)
        ).scalar() or 0

        offset = (page - 1) * page_size
        result = await self._session.execute(
            base.order_by(
                CommunicationLog.created_at.desc()
            )
            .offset(offset)
            .limit(page_size)
        )
        logs = result.scalars().all()

        return CommLogListResponse(
            items=[
                self._to_comm_log(lg) for lg in logs
            ],
            total=total,
            page=page,
            page_size=page_size,
        )

    # -- Mappers ----------------------------------------------------

    @staticmethod
    def _to_notification(
        n: Notification,
    ) -> NotificationResponse:
        """Map Notification ORM to response schema."""
        return NotificationResponse(
            id=n.id,
            tenant_id=n.tenant_id,
            user_id=n.user_id,
            title=n.title,
            message=n.message,
            channel=n.channel,
            read=n.read,
            read_at=n.read_at,
            entity_type=n.entity_type,
            entity_id=n.entity_id,
            created_at=n.created_at,
        )

    @staticmethod
    def _to_preference(
        p: NotificationPreference,
    ) -> PreferenceResponse:
        """Map NotificationPreference to response."""
        return PreferenceResponse(
            id=p.id,
            category=p.category,
            channel_config=p.channel_config,
            quiet_hours_start=p.quiet_hours_start,
            quiet_hours_end=p.quiet_hours_end,
            created_at=p.created_at,
            updated_at=p.updated_at,
        )

    @staticmethod
    def _to_email_template(
        t: EmailTemplate,
    ) -> EmailTemplateResponse:
        """Map EmailTemplate ORM to response schema."""
        return EmailTemplateResponse(
            id=t.id,
            tenant_id=t.tenant_id,
            name=t.name,
            subject_template=t.subject_template,
            body_template=t.body_template,
            variables=t.variables,
            is_system=t.is_system,
            created_at=t.created_at,
            updated_at=t.updated_at,
        )

    @staticmethod
    def _to_comm_log(
        lg: CommunicationLog,
    ) -> CommLogResponse:
        """Map CommunicationLog ORM to response."""
        return CommLogResponse(
            id=lg.id,
            tenant_id=lg.tenant_id,
            channel=lg.channel,
            recipient=lg.recipient,
            subject=lg.subject,
            status=lg.status,
            sent_at=lg.sent_at,
            error_message=lg.error_message,
            created_at=lg.created_at,
        )
