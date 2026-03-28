"""CQRS read-model event consumer for the Reporting Service.

Consumes events from ALL domain streams and materialises dashboard_read
data that powers executive dashboards and reporting endpoints.

Runs as a background ``asyncio`` task started by the FastAPI lifespan.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any

import redis.asyncio as aioredis

from velora_common.event_types import (
    ALERT_CREATED,
    ALERT_RESOLVED,
    ASSESSMENT_CANCELLED,
    ASSESSMENT_COMPLETED,
    ASSESSMENT_CREATED,
    ASSESSMENT_DISTRIBUTED,
    ASSESSMENT_SUBMITTED,
    FINDING_CLOSED,
    FINDING_CREATED,
    SCORE_CALCULATED,
    SCORE_CHANGED,
    STREAM_ALERT,
    STREAM_ASSESSMENT,
    STREAM_FINDING,
    STREAM_SCORE,
    STREAM_VENDOR,
    VENDOR_CREATED,
    VENDOR_DELETED,
    VENDOR_ENRICHED,
    VENDOR_TIER_CHANGED,
    VENDOR_UPDATED,
)
from velora_common.events import EventConsumer
from velora_common.logging import get_logger

logger = get_logger(__name__)

# Redis hash key that stores the materialised dashboard counters
DASHBOARD_KEY = "reporting:dashboard_read"


class DashboardReadModelConsumer:
    """Maintains a materialised read model in Redis for fast dashboard queries.

    Counters stored in ``reporting:dashboard_read`` (Redis hash):

    * ``vendor_count`` — total active vendors
    * ``vendor_tier:{tier}`` — vendors per tier (critical / high / medium / low)
    * ``assessment_count`` — total assessments
    * ``assessment_status:{status}`` — assessments per status
    * ``avg_score`` — running average vendor risk score
    * ``score_sum`` / ``score_count`` — helpers for average calculation
    * ``top_risk_vendors`` — JSON list of highest-risk vendor IDs
    * ``finding_count`` — total open findings
    * ``finding_severity:{sev}`` — findings per severity
    * ``alert_count`` — total open alerts
    * ``alert_priority:{pri}`` — alerts per priority
    * ``last_updated`` — ISO timestamp of last materialisation
    """

    def __init__(self, redis_url: str) -> None:
        self._redis_url = redis_url
        self._redis: aioredis.Redis | None = None
        self._consumer: EventConsumer | None = None
        self._task: asyncio.Task | None = None  # type: ignore[type-arg]

    # -- lifecycle -----------------------------------------------------------

    async def start(self) -> None:
        """Wire up subscriptions and launch the background loop."""
        self._redis = aioredis.from_url(
            self._redis_url, decode_responses=True
        )

        self._consumer = EventConsumer(
            redis_url=self._redis_url,
            group="reporting-read-model",
            consumer="reporting-worker-1",
        )

        # Subscribe to all relevant streams
        self._consumer.subscribe(STREAM_VENDOR, self._handle_vendor)
        self._consumer.subscribe(STREAM_ASSESSMENT, self._handle_assessment)
        self._consumer.subscribe(STREAM_SCORE, self._handle_score)
        self._consumer.subscribe(STREAM_FINDING, self._handle_finding)
        self._consumer.subscribe(STREAM_ALERT, self._handle_alert)

        self._task = asyncio.create_task(
            self._consumer.run(), name="dashboard-read-model-consumer"
        )
        logger.info("dashboard_read_model_consumer_started")

    async def stop(self) -> None:
        """Gracefully shut down the consumer loop."""
        if self._consumer:
            self._consumer.stop()
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        if self._consumer:
            await self._consumer.close()
        if self._redis:
            await self._redis.aclose()
        logger.info("dashboard_read_model_consumer_stopped")

    # -- helpers -------------------------------------------------------------

    async def _incr(self, field: str, amount: int = 1) -> None:
        """Increment a counter in the dashboard hash."""
        assert self._redis is not None
        await self._redis.hincrby(DASHBOARD_KEY, field, amount)
        await self._redis.hset(
            DASHBOARD_KEY,
            "last_updated",
            datetime.now(timezone.utc).isoformat(),
        )

    async def _decr(self, field: str, amount: int = 1) -> None:
        """Decrement a counter (floored at 0)."""
        assert self._redis is not None
        current = int(await self._redis.hget(DASHBOARD_KEY, field) or 0)
        new_val = max(0, current - amount)
        await self._redis.hset(DASHBOARD_KEY, field, str(new_val))
        await self._redis.hset(
            DASHBOARD_KEY,
            "last_updated",
            datetime.now(timezone.utc).isoformat(),
        )

    # -- event handlers ------------------------------------------------------

    async def _handle_vendor(self, event: dict[str, Any]) -> None:
        """Vendor events → update vendor counts, tier distribution."""
        etype = event.get("event_type", "")
        data = event.get("data", {})

        if etype == VENDOR_CREATED:
            await self._incr("vendor_count")
            tier = data.get("tier", "medium")
            await self._incr(f"vendor_tier:{tier}")
            logger.debug("read_model_vendor_created", vendor_id=data.get("id"))

        elif etype == VENDOR_UPDATED:
            logger.debug("read_model_vendor_updated", vendor_id=data.get("id"))

        elif etype == VENDOR_DELETED:
            await self._decr("vendor_count")
            tier = data.get("tier", "medium")
            await self._decr(f"vendor_tier:{tier}")
            logger.debug("read_model_vendor_deleted", vendor_id=data.get("id"))

        elif etype == VENDOR_ENRICHED:
            logger.debug(
                "read_model_vendor_enriched", vendor_id=data.get("id")
            )

        elif etype == VENDOR_TIER_CHANGED:
            old_tier = data.get("old_tier")
            new_tier = data.get("new_tier")
            if old_tier:
                await self._decr(f"vendor_tier:{old_tier}")
            if new_tier:
                await self._incr(f"vendor_tier:{new_tier}")
            logger.debug(
                "read_model_vendor_tier_changed",
                vendor_id=data.get("vendor_id"),
                old_tier=old_tier,
                new_tier=new_tier,
            )

    async def _handle_assessment(self, event: dict[str, Any]) -> None:
        """Assessment events → update assessment counts by status."""
        etype = event.get("event_type", "")
        data = event.get("data", {})

        if etype == ASSESSMENT_CREATED:
            await self._incr("assessment_count")
            await self._incr("assessment_status:draft")
            logger.debug(
                "read_model_assessment_created",
                assessment_id=data.get("id"),
            )

        elif etype == ASSESSMENT_DISTRIBUTED:
            await self._decr("assessment_status:draft")
            await self._incr("assessment_status:distributed")

        elif etype == ASSESSMENT_SUBMITTED:
            await self._decr("assessment_status:distributed")
            await self._incr("assessment_status:submitted")

        elif etype == ASSESSMENT_COMPLETED:
            await self._decr("assessment_status:submitted")
            await self._incr("assessment_status:completed")

        elif etype == ASSESSMENT_CANCELLED:
            status = data.get("previous_status", "draft")
            await self._decr(f"assessment_status:{status}")
            await self._incr("assessment_status:cancelled")
            await self._decr("assessment_count")

    async def _handle_score(self, event: dict[str, Any]) -> None:
        """Score events → update average score, track top risk vendors."""
        etype = event.get("event_type", "")
        data = event.get("data", {})
        assert self._redis is not None

        if etype in (SCORE_CALCULATED, SCORE_CHANGED):
            score = data.get("score")
            if score is not None:
                score = float(score)
                await self._redis.hincrbyfloat(
                    DASHBOARD_KEY, "score_sum", score
                )
                await self._incr("score_count")

                # Recalculate running average
                raw_sum = await self._redis.hget(DASHBOARD_KEY, "score_sum")
                raw_cnt = await self._redis.hget(DASHBOARD_KEY, "score_count")
                s = float(raw_sum or 0)
                c = int(raw_cnt or 1)
                avg = round(s / max(c, 1), 2)
                await self._redis.hset(
                    DASHBOARD_KEY, "avg_score", str(avg)
                )

            logger.debug(
                "read_model_score_updated",
                vendor_id=data.get("vendor_id"),
                score=score,
            )

    async def _handle_finding(self, event: dict[str, Any]) -> None:
        """Finding events → update finding counts by severity."""
        etype = event.get("event_type", "")
        data = event.get("data", {})
        severity = data.get("severity", "medium")

        if etype == FINDING_CREATED:
            await self._incr("finding_count")
            await self._incr(f"finding_severity:{severity}")
            logger.debug(
                "read_model_finding_created",
                finding_id=data.get("id"),
                severity=severity,
            )

        elif etype == FINDING_CLOSED:
            await self._decr("finding_count")
            await self._decr(f"finding_severity:{severity}")
            logger.debug(
                "read_model_finding_closed",
                finding_id=data.get("id"),
            )

    async def _handle_alert(self, event: dict[str, Any]) -> None:
        """Alert events → update alert counts by priority."""
        etype = event.get("event_type", "")
        data = event.get("data", {})
        priority = data.get("priority", "medium")

        if etype == ALERT_CREATED:
            await self._incr("alert_count")
            await self._incr(f"alert_priority:{priority}")
            logger.debug(
                "read_model_alert_created",
                alert_id=data.get("id"),
                priority=priority,
            )

        elif etype == ALERT_RESOLVED:
            await self._decr("alert_count")
            await self._decr(f"alert_priority:{priority}")
            logger.debug(
                "read_model_alert_resolved",
                alert_id=data.get("id"),
            )
