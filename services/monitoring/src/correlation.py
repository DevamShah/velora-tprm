"""
Alert correlation engine.

Auto-prioritizes alerts (P0-P4), deduplicates within 24h window,
and correlates multiple signals within 48h to escalate priority.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from velora_common.logging import get_logger
from .models import Alert, MonitoringSignal

logger = get_logger(__name__)

# Priority definitions per PRD
PRIORITY_RULES = {
    "P0": {
        "keywords": [
            "active breach", "ransomware", "data leak",
            "credential dump",
        ],
        "rating_drop": 30,
    },
    "P1": {
        "keywords": [
            "critical cve", "leaked credentials",
            "zero-day",
        ],
        "rating_drop": 15,
    },
    "P2": {
        "keywords": [
            "cert expiry", "dns change",
            "regulatory action",
        ],
        "rating_drop": 10,
    },
    "P3": {
        "keywords": [
            "moderate drop", "approaching expiry",
            "personnel change",
        ],
        "rating_drop": 5,
    },
}

DEDUP_WINDOW = timedelta(hours=24)
CORRELATION_WINDOW = timedelta(hours=48)


class AlertCorrelationEngine:
    """Processes signals into prioritized, deduplicated alerts."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def process_signal(
        self,
        tenant_id: uuid.UUID,
        vendor_id: uuid.UUID,
        signal_type: str,
        signal_data: dict,
    ) -> Optional[Alert]:
        """Process an incoming signal into an alert.

        Steps:
        1. Classify priority (P0-P4)
        2. Check deduplication (24h window)
        3. Check correlation (48h — multiple P2/P3 → P1)
        4. Create or update alert
        """
        priority = self._classify_priority(
            signal_type, signal_data
        )

        # Deduplication check
        existing = await self._find_duplicate(
            tenant_id, vendor_id, signal_type,
        )
        if existing:
            logger.info(
                "signal_deduplicated",
                alert_id=str(existing.id),
                signal_type=signal_type,
            )
            return None

        # Create signal record
        signal = MonitoringSignal(
            tenant_id=tenant_id,
            vendor_id=vendor_id,
            source=signal_data.get("source", "external"),
            signal_type=signal_type,
            severity=signal_data.get("severity", "info"),
            title=self._generate_title(
                signal_type, signal_data
            ),
            raw_data=signal_data,
            signal_data=signal_data,
            priority=priority,
        )
        self._session.add(signal)

        # Correlation — check if multiple P2/P3 in 48h
        if priority in ("P2", "P3"):
            escalated = await self._check_correlation(
                tenant_id, vendor_id,
            )
            if escalated:
                priority = "P1"
                logger.info(
                    "priority_escalated",
                    vendor_id=str(vendor_id),
                    from_priority="P2/P3",
                    to_priority="P1",
                )

        # Create alert
        alert = Alert(
            tenant_id=tenant_id,
            vendor_id=vendor_id,
            title=self._generate_title(
                signal_type, signal_data
            ),
            description=self._generate_description(
                signal_type, signal_data
            ),
            priority=priority,
            status="new",
            signal_type=signal_type,
            signal_data=signal_data,
        )
        self._session.add(alert)
        await self._session.flush()

        logger.info(
            "alert_created",
            alert_id=str(alert.id),
            priority=priority,
            vendor_id=str(vendor_id),
        )
        return alert

    def _classify_priority(
        self, signal_type: str, data: dict
    ) -> str:
        """Classify signal into P0-P4 based on rules."""
        text = (
            f"{signal_type} "
            f"{str(data.get('description', ''))} "
            f"{str(data.get('severity', ''))}"
        ).lower()

        rating_drop = abs(
            data.get("rating_change", 0)
        )

        for priority, rules in PRIORITY_RULES.items():
            for kw in rules["keywords"]:
                if kw in text:
                    return priority
            if rating_drop >= rules["rating_drop"]:
                return priority

        return "P4"  # Info-level default

    async def _find_duplicate(
        self,
        tenant_id: uuid.UUID,
        vendor_id: uuid.UUID,
        signal_type: str,
    ) -> Optional[Alert]:
        """Check for duplicate alert within dedup window."""
        cutoff = datetime.now(timezone.utc) - DEDUP_WINDOW
        result = await self._session.execute(
            select(Alert).where(
                Alert.tenant_id == tenant_id,
                Alert.vendor_id == vendor_id,
                Alert.signal_type == signal_type,
                Alert.created_at >= cutoff,
            ).limit(1)
        )
        return result.scalars().first()

    async def _check_correlation(
        self,
        tenant_id: uuid.UUID,
        vendor_id: uuid.UUID,
    ) -> bool:
        """Check if 3+ P2/P3 signals in 48h → escalate."""
        cutoff = (
            datetime.now(timezone.utc) - CORRELATION_WINDOW
        )
        result = await self._session.execute(
            select(MonitoringSignal).where(
                MonitoringSignal.tenant_id == tenant_id,
                MonitoringSignal.vendor_id == vendor_id,
                MonitoringSignal.priority.in_(
                    ["P2", "P3"]
                ),
                MonitoringSignal.created_at >= cutoff,
            )
        )
        signals = result.scalars().all()
        return len(signals) >= 3

    @staticmethod
    def _generate_title(
        signal_type: str, data: dict
    ) -> str:
        """Generate alert title from signal."""
        severity = data.get("severity", "info")
        domain = data.get("domain", "unknown")
        return (
            f"[{severity.upper()}] {signal_type} — "
            f"{domain}"
        )[:255]

    @staticmethod
    def _generate_description(
        signal_type: str, data: dict
    ) -> str:
        """Generate alert description from signal."""
        desc = data.get(
            "description",
            f"Signal detected: {signal_type}",
        )
        return str(desc)[:5000]
