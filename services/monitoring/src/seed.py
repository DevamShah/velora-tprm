"""
Monitoring seed data — 5 demo alerts + 10 timeline events.

Idempotent: safe to run multiple times. Skips if alerts
already exist for the demo tenant.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import List

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from velora_common.logging import get_logger
from velora_common.seed import DEMO_TENANT_ID
from .models import (
    Alert,
    AlertRule,
    MonitoringSignal,
    VendorTimeline,
)
from .cross_deps.vendor_models import Vendor  # TODO: Replace with API call in Phase 2

logger = get_logger(__name__)


async def _get_vendor_ids(
    session: AsyncSession,
    tenant_id: uuid.UUID,
) -> List[uuid.UUID]:
    """Fetch up to 5 seeded vendor IDs."""
    result = await session.execute(
        select(Vendor.id)
        .where(
            Vendor.tenant_id == tenant_id,
            Vendor.deleted_at.is_(None),
        )
        .limit(5)
    )
    return [row[0] for row in result.all()]


async def _seed_alert_rules(
    session: AsyncSession,
    tenant_id: uuid.UUID,
) -> int:
    """Seed default alert rules."""
    count_result = await session.execute(
        select(func.count())
        .select_from(AlertRule)
        .where(AlertRule.tenant_id == tenant_id)
    )
    if (count_result.scalar() or 0) > 0:
        return 0

    rules = [
        AlertRule(
            tenant_id=tenant_id,
            name="Critical Severity Auto-Alert",
            description=(
                "Generate P0 alert for any critical signal"
            ),
            conditions={"severity": ["critical"]},
            actions={"notify": ["admin"], "priority": "p0"},
            is_active=True,
        ),
        AlertRule(
            tenant_id=tenant_id,
            name="High Severity Auto-Alert",
            description=(
                "Generate P1 alert for high severity signals"
            ),
            conditions={"severity": ["high"]},
            actions={"notify": ["manager"], "priority": "p1"},
            is_active=True,
        ),
        AlertRule(
            tenant_id=tenant_id,
            name="Data Breach Signal",
            description=(
                "Alert on any data breach signals"
            ),
            conditions={
                "signal_type": "data_breach",
                "severity": ["critical", "high"],
            },
            actions={
                "notify": ["admin", "ciso"],
                "priority": "p0",
            },
            is_active=True,
        ),
    ]
    for rule in rules:
        session.add(rule)
    await session.flush()
    return len(rules)


async def _seed_alerts(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    vendor_ids: List[uuid.UUID],
) -> int:
    """Seed 5 demo alerts across vendors."""
    count_result = await session.execute(
        select(func.count())
        .select_from(Alert)
        .where(Alert.tenant_id == tenant_id)
    )
    if (count_result.scalar() or 0) > 0:
        return 0

    if len(vendor_ids) < 3:
        logger.warning(
            "seed_alerts_skipped",
            reason="not enough vendors",
        )
        return 0

    now = datetime.now(timezone.utc)
    alerts_data = [
        {
            "vendor_id": vendor_ids[0],
            "priority": "p0",
            "status": "new",
            "title": "Critical: SOC 2 report expired",
            "description": (
                "AWS SOC 2 Type II report expired 7 days ago. "
                "Vendor risk score may be inaccurate."
            ),
            "impact_assessment": {
                "risk_impact": "high",
                "affected_controls": 12,
                "recommendation": "Request updated report",
            },
        },
        {
            "vendor_id": vendor_ids[1],
            "priority": "p1",
            "status": "acknowledged",
            "title": "Salesforce data breach reported",
            "description": (
                "News article reports potential data exposure "
                "affecting Salesforce customers."
            ),
            "impact_assessment": {
                "risk_impact": "high",
                "source": "news_monitoring",
                "recommendation": "Contact vendor immediately",
            },
        },
        {
            "vendor_id": vendor_ids[2],
            "priority": "p2",
            "status": "investigating",
            "title": "Workday security rating downgraded",
            "description": (
                "External rating dropped from A to B- "
                "due to newly discovered CVEs."
            ),
            "impact_assessment": {
                "risk_impact": "medium",
                "previous_rating": "A",
                "current_rating": "B-",
            },
        },
        {
            "vendor_id": vendor_ids[3 % len(vendor_ids)],
            "priority": "p3",
            "status": "resolved",
            "title": "Stripe PCI-DSS certificate renewal",
            "description": (
                "PCI-DSS certificate was renewed. "
                "New certificate uploaded and verified."
            ),
            "resolution_notes": (
                "Certificate verified and updated in system."
            ),
            "impact_assessment": {
                "risk_impact": "low",
                "resolved_action": "certificate_updated",
            },
        },
        {
            "vendor_id": vendor_ids[4 % len(vendor_ids)],
            "priority": "p4",
            "status": "suppressed",
            "title": "Datadog minor policy update",
            "description": (
                "Privacy policy updated with minor "
                "clarifications. No material changes."
            ),
            "impact_assessment": {
                "risk_impact": "none",
                "change_type": "policy_update",
            },
        },
    ]

    for i, data in enumerate(alerts_data):
        alert = Alert(
            tenant_id=tenant_id,
            **data,
        )
        if data["status"] == "acknowledged":
            alert.acknowledged_at = now - timedelta(
                hours=2
            )
        elif data["status"] == "resolved":
            alert.resolved_at = now - timedelta(days=1)
        session.add(alert)

    await session.flush()
    return len(alerts_data)


async def _seed_timeline(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    vendor_ids: List[uuid.UUID],
) -> int:
    """Seed 10 timeline events across vendors."""
    count_result = await session.execute(
        select(func.count())
        .select_from(VendorTimeline)
        .where(VendorTimeline.tenant_id == tenant_id)
    )
    if (count_result.scalar() or 0) > 0:
        return 0

    if not vendor_ids:
        return 0

    now = datetime.now(timezone.utc)
    events = [
        {
            "vendor_id": vendor_ids[0],
            "event_type": "onboarding",
            "title": "Vendor onboarded",
            "description": "AWS added to vendor registry",
            "offset_days": 90,
        },
        {
            "vendor_id": vendor_ids[0],
            "event_type": "assessment_completed",
            "title": "Initial risk assessment completed",
            "description": "Scored 85/100 — tier: critical",
            "offset_days": 80,
        },
        {
            "vendor_id": vendor_ids[0],
            "event_type": "evidence_uploaded",
            "title": "SOC 2 Type II report uploaded",
            "description": "2024 audit report received",
            "offset_days": 75,
        },
        {
            "vendor_id": vendor_ids[1],
            "event_type": "onboarding",
            "title": "Vendor onboarded",
            "description": "Salesforce added to registry",
            "offset_days": 85,
        },
        {
            "vendor_id": vendor_ids[1],
            "event_type": "alert_created",
            "title": "Data breach alert triggered",
            "description": "News monitoring signal detected",
            "offset_days": 5,
        },
        {
            "vendor_id": vendor_ids[2],
            "event_type": "onboarding",
            "title": "Vendor onboarded",
            "description": "Workday added to registry",
            "offset_days": 70,
        },
        {
            "vendor_id": vendor_ids[2],
            "event_type": "rating_change",
            "title": "External rating downgraded",
            "description": "Rating changed from A to B-",
            "offset_days": 3,
        },
        {
            "vendor_id": vendor_ids[3 % len(vendor_ids)],
            "event_type": "evidence_uploaded",
            "title": "PCI-DSS certificate uploaded",
            "description": "New certificate verified",
            "offset_days": 10,
        },
        {
            "vendor_id": vendor_ids[3 % len(vendor_ids)],
            "event_type": "assessment_completed",
            "title": "Quarterly assessment completed",
            "description": "Score: 72/100 — tier: high",
            "offset_days": 15,
        },
        {
            "vendor_id": vendor_ids[4 % len(vendor_ids)],
            "event_type": "contract_update",
            "title": "Contract renewed",
            "description": "Annual contract renewed until 2027",
            "offset_days": 30,
        },
    ]

    for ev_data in events:
        offset = ev_data.pop("offset_days")
        event = VendorTimeline(
            tenant_id=tenant_id,
            event_metadata=None,
            **ev_data,
        )
        # Override created_at for realistic ordering
        event.created_at = now - timedelta(days=offset)
        session.add(event)

    await session.flush()
    return len(events)


async def seed_monitoring(
    session: AsyncSession,
) -> int:
    """Seed all monitoring demo data. Returns count."""
    vendor_ids = await _get_vendor_ids(
        session, DEMO_TENANT_ID
    )
    rules = await _seed_alert_rules(
        session, DEMO_TENANT_ID
    )
    alerts = await _seed_alerts(
        session, DEMO_TENANT_ID, vendor_ids
    )
    timeline = await _seed_timeline(
        session, DEMO_TENANT_ID, vendor_ids
    )

    await session.commit()
    total = rules + alerts + timeline
    logger.info(
        "monitoring_seed_complete",
        rules=rules,
        alerts=alerts,
        timeline=timeline,
    )
    return total
