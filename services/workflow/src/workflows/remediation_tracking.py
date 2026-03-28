"""Remediation tracking workflow — finding to plan to verify to close.

Long-running workflow that tracks a finding from creation through
remediation, evidence submission, verification, and closure (or re-open).

Steps:
1. Create remediation plan with deadline
2. Notify vendor of required remediation
3. Send periodic reminders until deadline
4. Wait for vendor evidence submission
5. Auto-verify submitted evidence
6. Close finding or re-open if verification fails
"""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from temporalio import workflow
from temporalio.common import RetryPolicy

DEFAULT_RETRY = RetryPolicy(
    maximum_attempts=3,
    initial_interval=timedelta(seconds=1),
    maximum_interval=timedelta(seconds=30),
    backoff_coefficient=2.0,
)

# Reminder schedule: send at 25%, 50%, 75%, 90% of the remediation window
REMINDER_PERCENTAGES = [0.25, 0.50, 0.75, 0.90]

# Maximum re-open cycles before escalation
MAX_REOPEN_CYCLES = 3


@workflow.defn
class RemediationTrackingWorkflow:
    """Durable workflow for tracking finding remediation end-to-end.

    Can span weeks/months. Uses signals for vendor evidence submission
    and reviewer decisions.
    """

    def __init__(self) -> None:
        self._evidence_submitted = False
        self._evidence_data: dict[str, Any] = {}
        self._reopen_count = 0

    @workflow.signal
    async def evidence_submitted(self, data: dict[str, Any]) -> None:
        """Signal that the vendor has submitted remediation evidence."""
        self._evidence_submitted = True
        self._evidence_data = data

    @workflow.run
    async def run(self, input: dict[str, Any]) -> dict[str, Any]:
        """Execute the remediation tracking pipeline.

        Args:
            input: Must contain ``finding_id``, ``vendor_id``,
                   ``tenant_id``, ``severity``,
                   ``remediation_days`` (deadline in days, default 30).

        Returns:
            Dict with final status and cycle count.
        """
        finding_id = input["finding_id"]
        vendor_id = input["vendor_id"]
        remediation_days = input.get("remediation_days", 30)

        workflow.logger.info(
            "remediation_tracking_started",
            extra={
                "finding_id": finding_id,
                "vendor_id": vendor_id,
                "remediation_days": remediation_days,
            },
        )

        # Step 1: Create remediation plan
        plan: dict[str, Any] = await workflow.execute_activity(
            "create_remediation_plan",
            {
                "finding_id": finding_id,
                "vendor_id": vendor_id,
                "severity": input.get("severity", "medium"),
                "remediation_days": remediation_days,
            },
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=DEFAULT_RETRY,
        )

        plan_id = plan.get("plan_id", finding_id)

        # Step 2: Notify vendor
        await workflow.execute_activity(
            "send_notification",
            {
                "type": "remediation_required",
                "finding_id": finding_id,
                "vendor_id": vendor_id,
                "plan_id": plan_id,
                "deadline_days": remediation_days,
                "severity": input.get("severity", "medium"),
            },
            start_to_close_timeout=timedelta(seconds=15),
            retry_policy=DEFAULT_RETRY,
        )

        # Remediation loop — supports re-opens
        while self._reopen_count <= MAX_REOPEN_CYCLES:
            self._evidence_submitted = False
            self._evidence_data = {}

            # Step 3: Send reminders at scheduled percentages
            elapsed_days = 0
            for pct in REMINDER_PERCENTAGES:
                if self._evidence_submitted:
                    break

                target_day = int(remediation_days * pct)
                delta = target_day - elapsed_days
                if delta > 0:
                    await workflow.sleep(timedelta(days=delta))
                elapsed_days = target_day

                if not self._evidence_submitted:
                    await workflow.execute_activity(
                        "send_reminder",
                        {
                            "type": "remediation_reminder",
                            "finding_id": finding_id,
                            "vendor_id": vendor_id,
                            "day": elapsed_days,
                            "total_days": remediation_days,
                        },
                        start_to_close_timeout=timedelta(seconds=15),
                        retry_policy=DEFAULT_RETRY,
                    )

            # Step 4: Wait for evidence submission (remaining window)
            if not self._evidence_submitted:
                remaining = remediation_days - elapsed_days
                try:
                    await workflow.wait_condition(
                        lambda: self._evidence_submitted,
                        timeout=timedelta(days=max(remaining, 1)),
                    )
                except TimeoutError:
                    # Deadline breached
                    await workflow.execute_activity(
                        "escalate_overdue",
                        {
                            "finding_id": finding_id,
                            "vendor_id": vendor_id,
                            "plan_id": plan_id,
                            "days_overdue": remediation_days,
                            "cycle": self._reopen_count + 1,
                        },
                        start_to_close_timeout=timedelta(seconds=15),
                        retry_policy=DEFAULT_RETRY,
                    )

                    workflow.logger.warn(
                        "remediation_overdue",
                        extra={
                            "finding_id": finding_id,
                            "cycle": self._reopen_count + 1,
                        },
                    )

                    return {
                        "finding_id": finding_id,
                        "plan_id": plan_id,
                        "status": "overdue",
                        "cycles": self._reopen_count + 1,
                    }

            # Step 5: Auto-verify the submitted evidence
            verification: dict[str, Any] = await workflow.execute_activity(
                "verify_remediation_evidence",
                {
                    "finding_id": finding_id,
                    "plan_id": plan_id,
                    "evidence": self._evidence_data,
                },
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=DEFAULT_RETRY,
            )

            if verification.get("verified", False):
                # Step 6a: Close the finding
                await workflow.execute_activity(
                    "close_finding",
                    {
                        "finding_id": finding_id,
                        "plan_id": plan_id,
                        "verification": verification,
                    },
                    start_to_close_timeout=timedelta(seconds=30),
                    retry_policy=DEFAULT_RETRY,
                )

                await workflow.execute_activity(
                    "send_notification",
                    {
                        "type": "finding_remediated",
                        "finding_id": finding_id,
                        "vendor_id": vendor_id,
                        "plan_id": plan_id,
                    },
                    start_to_close_timeout=timedelta(seconds=15),
                    retry_policy=DEFAULT_RETRY,
                )

                workflow.logger.info(
                    "remediation_completed",
                    extra={
                        "finding_id": finding_id,
                        "cycles": self._reopen_count + 1,
                    },
                )

                return {
                    "finding_id": finding_id,
                    "plan_id": plan_id,
                    "status": "remediated",
                    "cycles": self._reopen_count + 1,
                }

            else:
                # Step 6b: Verification failed — re-open
                self._reopen_count += 1

                await workflow.execute_activity(
                    "reopen_finding",
                    {
                        "finding_id": finding_id,
                        "plan_id": plan_id,
                        "reason": verification.get("reason", "Verification failed"),
                        "cycle": self._reopen_count,
                    },
                    start_to_close_timeout=timedelta(seconds=30),
                    retry_policy=DEFAULT_RETRY,
                )

                await workflow.execute_activity(
                    "send_notification",
                    {
                        "type": "remediation_rejected",
                        "finding_id": finding_id,
                        "vendor_id": vendor_id,
                        "reason": verification.get("reason"),
                        "cycle": self._reopen_count,
                    },
                    start_to_close_timeout=timedelta(seconds=15),
                    retry_policy=DEFAULT_RETRY,
                )

                workflow.logger.info(
                    "remediation_rejected_reopened",
                    extra={
                        "finding_id": finding_id,
                        "cycle": self._reopen_count,
                    },
                )

                # Continue loop for next cycle

        # Exhausted re-open cycles — escalate
        await workflow.execute_activity(
            "escalate_overdue",
            {
                "finding_id": finding_id,
                "vendor_id": vendor_id,
                "plan_id": plan_id,
                "reason": f"Exceeded {MAX_REOPEN_CYCLES} remediation cycles",
                "cycle": self._reopen_count,
            },
            start_to_close_timeout=timedelta(seconds=15),
            retry_policy=DEFAULT_RETRY,
        )

        return {
            "finding_id": finding_id,
            "plan_id": plan_id,
            "status": "escalated",
            "cycles": self._reopen_count,
        }
