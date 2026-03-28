"""
Monitoring business logic — alerts, signals, rules, timelines.

All DB queries run inside the caller-provided async session.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.modules.monitoring.models import (
    Alert,
    AlertRule,
    MonitoringSignal,
    VendorTimeline,
)
from app.modules.monitoring.schemas import (
    AlertFilterParams,
    AlertListResponse,
    AlertResponse,
    AlertRuleCreate,
    AlertRuleResponse,
    AlertRuleUpdate,
    SignalIngestRequest,
    SignalResponse,
    VendorTimelineEvent,
    VendorTimelineResponse,
)

logger = get_logger(__name__)


class MonitoringService:
    """Stateless monitoring service — receives session per call."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # -- List Alerts ------------------------------------------------

    async def list_alerts(
        self,
        tenant_id: uuid.UUID,
        filters: AlertFilterParams,
    ) -> AlertListResponse:
        """List alerts with pagination and filters."""
        base = select(Alert).where(
            Alert.tenant_id == tenant_id
        )
        base = self._apply_alert_filters(base, filters)

        count_q = select(func.count()).select_from(
            base.subquery()
        )
        total = (
            await self._session.execute(count_q)
        ).scalar() or 0

        col = getattr(
            Alert, filters.sort_by, Alert.created_at
        )
        if filters.sort_order.value == "desc":
            base = base.order_by(col.desc())
        else:
            base = base.order_by(col.asc())

        offset = (filters.page - 1) * filters.page_size
        base = base.offset(offset).limit(
            filters.page_size
        )
        result = await self._session.execute(base)
        alerts = result.scalars().all()

        return AlertListResponse(
            items=[
                self._to_alert_response(a)
                for a in alerts
            ],
            total=total,
            page=filters.page,
            page_size=filters.page_size,
        )

    # -- Get Alert --------------------------------------------------

    async def get_alert(
        self,
        tenant_id: uuid.UUID,
        alert_id: uuid.UUID,
    ) -> Optional[AlertResponse]:
        """Fetch a single alert detail."""
        result = await self._session.execute(
            select(Alert).where(
                Alert.id == alert_id,
                Alert.tenant_id == tenant_id,
            )
        )
        alert = result.scalars().first()
        if alert is None:
            return None
        return self._to_alert_response(alert)

    # -- Acknowledge ------------------------------------------------

    async def acknowledge_alert(
        self,
        tenant_id: uuid.UUID,
        alert_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Optional[AlertResponse]:
        """Mark an alert as acknowledged."""
        alert = await self._get_alert_or_none(
            tenant_id, alert_id
        )
        if alert is None:
            return None

        alert.status = "acknowledged"
        alert.acknowledged_by = user_id
        alert.acknowledged_at = datetime.now(
            timezone.utc
        )
        await self._session.flush()
        logger.info(
            "alert_acknowledged",
            alert_id=str(alert_id),
        )
        return self._to_alert_response(alert)

    # -- Resolve ----------------------------------------------------

    async def resolve_alert(
        self,
        tenant_id: uuid.UUID,
        alert_id: uuid.UUID,
        user_id: uuid.UUID,
        notes: Optional[str],
    ) -> Optional[AlertResponse]:
        """Mark an alert as resolved."""
        alert = await self._get_alert_or_none(
            tenant_id, alert_id
        )
        if alert is None:
            return None

        alert.status = "resolved"
        alert.resolved_by = user_id
        alert.resolved_at = datetime.now(timezone.utc)
        alert.resolution_notes = notes
        await self._session.flush()
        logger.info(
            "alert_resolved",
            alert_id=str(alert_id),
        )
        return self._to_alert_response(alert)

    # -- Suppress ---------------------------------------------------

    async def suppress_alert(
        self,
        tenant_id: uuid.UUID,
        alert_id: uuid.UUID,
    ) -> Optional[AlertResponse]:
        """Suppress an alert."""
        alert = await self._get_alert_or_none(
            tenant_id, alert_id
        )
        if alert is None:
            return None

        alert.status = "suppressed"
        await self._session.flush()
        logger.info(
            "alert_suppressed",
            alert_id=str(alert_id),
        )
        return self._to_alert_response(alert)

    # -- Vendor Timeline --------------------------------------------

    async def get_vendor_timeline(
        self,
        tenant_id: uuid.UUID,
        vendor_id: uuid.UUID,
    ) -> VendorTimelineResponse:
        """Fetch chronological events for a vendor."""
        result = await self._session.execute(
            select(VendorTimeline)
            .where(
                VendorTimeline.tenant_id == tenant_id,
                VendorTimeline.vendor_id == vendor_id,
            )
            .order_by(VendorTimeline.created_at.desc())
        )
        events = result.scalars().all()
        return VendorTimelineResponse(
            vendor_id=vendor_id,
            events=[
                self._to_timeline_event(e)
                for e in events
            ],
            total=len(events),
        )

    # -- Alert Rules ------------------------------------------------

    async def list_alert_rules(
        self,
        tenant_id: uuid.UUID,
    ) -> List[AlertRuleResponse]:
        """List all alert rules for a tenant."""
        result = await self._session.execute(
            select(AlertRule).where(
                AlertRule.tenant_id == tenant_id
            )
        )
        rules = result.scalars().all()
        return [
            self._to_rule_response(r) for r in rules
        ]

    async def create_alert_rule(
        self,
        tenant_id: uuid.UUID,
        data: AlertRuleCreate,
    ) -> AlertRuleResponse:
        """Create a new alert rule."""
        rule = AlertRule(
            tenant_id=tenant_id,
            name=data.name,
            description=data.description,
            conditions=data.conditions,
            actions=data.actions,
            is_active=data.is_active,
        )
        self._session.add(rule)
        await self._session.flush()
        logger.info(
            "alert_rule_created",
            rule_id=str(rule.id),
        )
        return self._to_rule_response(rule)

    async def update_alert_rule(
        self,
        tenant_id: uuid.UUID,
        rule_id: uuid.UUID,
        data: AlertRuleUpdate,
    ) -> Optional[AlertRuleResponse]:
        """Update an existing alert rule."""
        result = await self._session.execute(
            select(AlertRule).where(
                AlertRule.id == rule_id,
                AlertRule.tenant_id == tenant_id,
            )
        )
        rule = result.scalars().first()
        if rule is None:
            return None

        update_data = data.model_dump(
            exclude_unset=True
        )
        for field, value in update_data.items():
            setattr(rule, field, value)

        await self._session.flush()
        logger.info(
            "alert_rule_updated",
            rule_id=str(rule_id),
        )
        return self._to_rule_response(rule)

    # -- Signal Ingestion -------------------------------------------

    async def ingest_signal(
        self,
        tenant_id: uuid.UUID,
        data: SignalIngestRequest,
    ) -> SignalResponse:
        """Create signal, check rules, create alerts."""
        signal = MonitoringSignal(
            tenant_id=tenant_id,
            vendor_id=data.vendor_id,
            source=data.source,
            signal_type=data.signal_type,
            severity=data.severity.value,
            title=data.title,
            description=data.description,
            raw_data=data.raw_data,
            dedup_key=data.dedup_key,
            processed=False,
        )
        self._session.add(signal)
        await self._session.flush()

        alerts_created = await self._evaluate_rules(
            tenant_id, signal
        )
        signal.processed = True
        await self._session.flush()

        logger.info(
            "signal_ingested",
            signal_id=str(signal.id),
            alerts=alerts_created,
        )
        return SignalResponse(
            signal_id=signal.id,
            alerts_created=alerts_created,
        )

    # -- Private helpers --------------------------------------------

    async def _get_alert_or_none(
        self,
        tenant_id: uuid.UUID,
        alert_id: uuid.UUID,
    ) -> Optional[Alert]:
        """Fetch alert or return None."""
        result = await self._session.execute(
            select(Alert).where(
                Alert.id == alert_id,
                Alert.tenant_id == tenant_id,
            )
        )
        return result.scalars().first()

    async def _evaluate_rules(
        self,
        tenant_id: uuid.UUID,
        signal: MonitoringSignal,
    ) -> int:
        """Check active rules against a signal."""
        result = await self._session.execute(
            select(AlertRule).where(
                AlertRule.tenant_id == tenant_id,
                AlertRule.is_active.is_(True),
            )
        )
        rules = result.scalars().all()
        created = 0

        for rule in rules:
            if self._signal_matches_rule(signal, rule):
                alert = Alert(
                    tenant_id=tenant_id,
                    vendor_id=signal.vendor_id,
                    priority=self._severity_to_priority(
                        signal.severity
                    ),
                    status="new",
                    title=f"[{rule.name}] {signal.title}",
                    description=signal.description,
                    signal_ids=[signal.id],
                    impact_assessment={
                        "source": signal.source,
                        "severity": signal.severity,
                        "rule": rule.name,
                    },
                )
                self._session.add(alert)
                created += 1

        if created > 0:
            await self._session.flush()
        return created

    @staticmethod
    def _signal_matches_rule(
        signal: MonitoringSignal,
        rule: AlertRule,
    ) -> bool:
        """Check if a signal matches a rule's conditions."""
        conditions = rule.conditions or {}
        if "severity" in conditions:
            severity_list = conditions["severity"]
            if isinstance(severity_list, list):
                if signal.severity not in severity_list:
                    return False
            elif signal.severity != severity_list:
                return False
        if "source" in conditions:
            if signal.source != conditions["source"]:
                return False
        if "signal_type" in conditions:
            if (
                signal.signal_type
                != conditions["signal_type"]
            ):
                return False
        return True

    @staticmethod
    def _severity_to_priority(severity: str) -> str:
        """Map signal severity to alert priority."""
        mapping = {
            "critical": "p0",
            "high": "p1",
            "medium": "p2",
            "low": "p3",
            "info": "p4",
        }
        return mapping.get(severity, "p3")

    @staticmethod
    def _apply_alert_filters(query, filters):
        """Apply WHERE clauses for alert filters."""
        if filters.priority:
            query = query.where(
                Alert.priority
                == filters.priority.value
            )
        if filters.status:
            query = query.where(
                Alert.status == filters.status.value
            )
        if filters.vendor_id:
            query = query.where(
                Alert.vendor_id == filters.vendor_id
            )
        return query

    @staticmethod
    def _to_alert_response(
        alert: Alert,
    ) -> AlertResponse:
        """Map Alert ORM to response schema."""
        return AlertResponse(
            id=alert.id,
            tenant_id=alert.tenant_id,
            vendor_id=alert.vendor_id,
            priority=alert.priority,
            status=alert.status,
            title=alert.title,
            description=alert.description,
            signal_ids=alert.signal_ids,
            impact_assessment=alert.impact_assessment,
            acknowledged_by=alert.acknowledged_by,
            resolved_by=alert.resolved_by,
            acknowledged_at=alert.acknowledged_at,
            resolved_at=alert.resolved_at,
            resolution_notes=alert.resolution_notes,
            created_at=alert.created_at,
            updated_at=alert.updated_at,
        )

    @staticmethod
    def _to_rule_response(
        rule: AlertRule,
    ) -> AlertRuleResponse:
        """Map AlertRule ORM to response schema."""
        return AlertRuleResponse(
            id=rule.id,
            tenant_id=rule.tenant_id,
            name=rule.name,
            description=rule.description,
            conditions=rule.conditions,
            actions=rule.actions,
            is_active=rule.is_active,
            created_at=rule.created_at,
            updated_at=rule.updated_at,
        )

    @staticmethod
    def _to_timeline_event(
        event: VendorTimeline,
    ) -> VendorTimelineEvent:
        """Map VendorTimeline ORM to response schema."""
        return VendorTimelineEvent(
            id=event.id,
            vendor_id=event.vendor_id,
            event_type=event.event_type,
            title=event.title,
            description=event.description,
            metadata=event.event_metadata,
            actor_id=event.actor_id,
            created_at=event.created_at,
        )
