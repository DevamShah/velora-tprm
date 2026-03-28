"""
Findings business logic — CRUD, remediation, close.

All DB queries run inside the caller-provided async session.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.logging import get_logger
from app.modules.findings.models import (
    Finding,
    RemediationAction,
)
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

logger = get_logger(__name__)


class FindingsService:
    """Stateless findings service."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # -- List Findings ----------------------------------------------

    async def list_findings(
        self,
        tenant_id: uuid.UUID,
        vendor_id: Optional[uuid.UUID] = None,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> FindingListResponse:
        """List findings with filters and pagination."""
        base = select(Finding).where(
            Finding.tenant_id == tenant_id
        )
        if vendor_id:
            base = base.where(
                Finding.vendor_id == vendor_id
            )
        if severity:
            base = base.where(
                Finding.severity == severity
            )
        if status:
            base = base.where(
                Finding.status == status
            )

        count_q = select(func.count()).select_from(
            base.subquery()
        )
        total = (
            await self._session.execute(count_q)
        ).scalar() or 0

        offset = (page - 1) * page_size
        result = await self._session.execute(
            base.options(
                selectinload(
                    Finding.remediation_actions
                )
            )
            .order_by(Finding.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        findings = result.scalars().all()

        return FindingListResponse(
            items=[
                self._to_response(f) for f in findings
            ],
            total=total,
            page=page,
            page_size=page_size,
        )

    # -- Get Finding ------------------------------------------------

    async def get_finding(
        self,
        tenant_id: uuid.UUID,
        finding_id: uuid.UUID,
    ) -> Optional[FindingResponse]:
        """Fetch a single finding with remediation."""
        result = await self._session.execute(
            select(Finding)
            .options(
                selectinload(
                    Finding.remediation_actions
                )
            )
            .where(
                Finding.id == finding_id,
                Finding.tenant_id == tenant_id,
            )
        )
        finding = result.scalars().first()
        if finding is None:
            return None
        return self._to_response(finding)

    # -- Create Finding ---------------------------------------------

    async def create_finding(
        self,
        tenant_id: uuid.UUID,
        data: FindingCreate,
    ) -> FindingResponse:
        """Create a new finding."""
        finding = Finding(
            tenant_id=tenant_id,
            vendor_id=data.vendor_id,
            assessment_id=data.assessment_id,
            title=data.title,
            description=data.description,
            severity=data.severity.value,
            status="open",
            affected_controls=data.affected_controls,
            remediation_guidance=data.remediation_guidance,
            sla_due_date=data.sla_due_date,
            assigned_to=data.assigned_to,
        )
        self._session.add(finding)
        await self._session.flush()
        logger.info(
            "finding_created",
            finding_id=str(finding.id),
        )
        return self._to_response(finding)

    # -- Update Finding ---------------------------------------------

    async def update_finding(
        self,
        tenant_id: uuid.UUID,
        finding_id: uuid.UUID,
        data: FindingUpdate,
    ) -> Optional[FindingResponse]:
        """Update a finding."""
        finding = await self._get_finding(
            tenant_id, finding_id
        )
        if finding is None:
            return None

        update_data = data.model_dump(
            exclude_unset=True
        )
        for field, value in update_data.items():
            if hasattr(value, "value"):
                value = value.value
            setattr(finding, field, value)

        await self._session.flush()
        logger.info(
            "finding_updated",
            finding_id=str(finding_id),
        )
        return self._to_response(finding)

    # -- Close Finding ----------------------------------------------

    async def close_finding(
        self,
        tenant_id: uuid.UUID,
        finding_id: uuid.UUID,
        data: FindingClose,
    ) -> Optional[FindingResponse]:
        """Close a finding with a final status."""
        finding = await self._get_finding(
            tenant_id, finding_id
        )
        if finding is None:
            return None

        finding.status = data.status.value
        finding.closed_at = datetime.now(timezone.utc)
        await self._session.flush()
        logger.info(
            "finding_closed",
            finding_id=str(finding_id),
            status=data.status.value,
        )
        return self._to_response(finding)

    # -- Add Remediation --------------------------------------------

    async def add_remediation(
        self,
        tenant_id: uuid.UUID,
        finding_id: uuid.UUID,
        data: RemediationCreate,
    ) -> Optional[RemediationResponse]:
        """Add a remediation action to a finding."""
        finding = await self._get_finding(
            tenant_id, finding_id
        )
        if finding is None:
            return None

        action = RemediationAction(
            tenant_id=tenant_id,
            finding_id=finding_id,
            action_type=data.action_type,
            description=data.description,
            status="pending",
            effort_estimate=data.effort_estimate,
        )
        self._session.add(action)
        await self._session.flush()
        logger.info(
            "remediation_added",
            finding_id=str(finding_id),
            action_id=str(action.id),
        )
        return self._to_remediation(action)

    # -- Update Remediation -----------------------------------------

    async def update_remediation(
        self,
        tenant_id: uuid.UUID,
        finding_id: uuid.UUID,
        action_id: uuid.UUID,
        data: RemediationUpdate,
    ) -> Optional[RemediationResponse]:
        """Update a remediation action."""
        result = await self._session.execute(
            select(RemediationAction).where(
                RemediationAction.id == action_id,
                RemediationAction.finding_id
                == finding_id,
                RemediationAction.tenant_id
                == tenant_id,
            )
        )
        action = result.scalars().first()
        if action is None:
            return None

        update_data = data.model_dump(
            exclude_unset=True
        )
        for field, value in update_data.items():
            if hasattr(value, "value"):
                value = value.value
            setattr(action, field, value)

        if action.status == "completed":
            action.completed_at = datetime.now(
                timezone.utc
            )

        await self._session.flush()
        logger.info(
            "remediation_updated",
            action_id=str(action_id),
        )
        return self._to_remediation(action)

    # -- Private helpers --------------------------------------------

    async def _get_finding(
        self,
        tenant_id: uuid.UUID,
        finding_id: uuid.UUID,
    ) -> Optional[Finding]:
        """Fetch finding or return None."""
        result = await self._session.execute(
            select(Finding)
            .options(
                selectinload(
                    Finding.remediation_actions
                )
            )
            .where(
                Finding.id == finding_id,
                Finding.tenant_id == tenant_id,
            )
        )
        return result.scalars().first()

    @staticmethod
    def _to_response(
        finding: Finding,
    ) -> FindingResponse:
        """Map Finding ORM to response schema."""
        actions = []
        try:
            actions = [
                FindingsService._to_remediation(a)
                for a in (
                    finding.remediation_actions or []
                )
            ]
        except Exception:
            pass

        return FindingResponse(
            id=finding.id,
            tenant_id=finding.tenant_id,
            vendor_id=finding.vendor_id,
            assessment_id=finding.assessment_id,
            title=finding.title,
            description=finding.description,
            severity=finding.severity,
            status=finding.status,
            affected_controls=finding.affected_controls,
            remediation_guidance=finding.remediation_guidance,
            sla_due_date=finding.sla_due_date,
            assigned_to=finding.assigned_to,
            closed_at=finding.closed_at,
            remediation_actions=actions,
            created_at=finding.created_at,
            updated_at=finding.updated_at,
        )

    @staticmethod
    def _to_remediation(
        action: RemediationAction,
    ) -> RemediationResponse:
        """Map RemediationAction ORM to response."""
        return RemediationResponse(
            id=action.id,
            finding_id=action.finding_id,
            action_type=action.action_type,
            description=action.description,
            status=action.status,
            effort_estimate=action.effort_estimate,
            completed_at=action.completed_at,
            created_at=action.created_at,
            updated_at=action.updated_at,
        )
