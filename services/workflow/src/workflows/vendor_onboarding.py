"""Vendor onboarding workflow — orchestrates vendor creation through initial assessment.

Steps:
1. Create vendor record via vendor-service
2. Trigger enrichment (external data lookups)
3. Calculate initial risk tier
4. Send onboarding notification
"""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from velora_common.logging import get_logger

logger = get_logger(__name__)

DEFAULT_RETRY = RetryPolicy(
    maximum_attempts=3,
    initial_interval=timedelta(seconds=1),
    maximum_interval=timedelta(seconds=30),
    backoff_coefficient=2.0,
)


@workflow.defn
class VendorOnboardingWorkflow:
    """Durable workflow that takes a vendor from creation to fully onboarded."""

    @workflow.run
    async def run(self, input: dict[str, Any]) -> dict[str, Any]:
        """Execute the onboarding pipeline.

        Args:
            input: Must contain ``vendor_data`` dict with at minimum
                   ``name``, ``tenant_id``.

        Returns:
            Dict with ``vendor_id`` and assigned ``tier``.
        """
        workflow.logger.info(
            "vendor_onboarding_started",
            extra={"vendor_name": input["vendor_data"].get("name")},
        )

        # Step 1: Create vendor record
        vendor: dict[str, Any] = await workflow.execute_activity(
            "create_vendor",
            input["vendor_data"],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=DEFAULT_RETRY,
        )

        vendor_id = vendor["id"]

        # Step 2: Trigger enrichment (may call external APIs — longer timeout)
        enrichment: dict[str, Any] = await workflow.execute_activity(
            "enrich_vendor",
            {"vendor_id": vendor_id},
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=DEFAULT_RETRY,
        )

        # Step 3: Calculate initial risk tier based on enrichment data
        tier_result: dict[str, Any] = await workflow.execute_activity(
            "calculate_tier",
            {"vendor_id": vendor_id},
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=DEFAULT_RETRY,
        )

        # Step 4: Send onboarding notification
        await workflow.execute_activity(
            "send_notification",
            {
                "type": "vendor_onboarded",
                "vendor_id": vendor_id,
                "vendor_name": input["vendor_data"]["name"],
                "tier": tier_result.get("tier", "unknown"),
            },
            start_to_close_timeout=timedelta(seconds=15),
            retry_policy=DEFAULT_RETRY,
        )

        workflow.logger.info(
            "vendor_onboarding_completed",
            extra={"vendor_id": vendor_id, "tier": tier_result.get("tier")},
        )

        return {
            "vendor_id": vendor_id,
            "tier": tier_result.get("tier", "unknown"),
            "enrichment_status": enrichment.get("status", "completed"),
        }
