"""Assessment lifecycle workflow — from creation through completion.

Steps:
1. Create assessment from template
2. Distribute to vendor
3. Send periodic reminders (Day 7, 14, 21)
4. Wait for vendor submission (up to 30 days)
5. Auto-score submitted assessment
6. Notify internal team for review

Supports signals: ``vendor_submitted`` to short-circuit the wait.
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

# Reminder schedule in days from distribution
REMINDER_DAYS = [7, 14, 21]
# Maximum wait for vendor submission
SUBMISSION_DEADLINE_DAYS = 30


@workflow.defn
class AssessmentLifecycleWorkflow:
    """Durable workflow managing the full assessment lifecycle.

    Long-running: can span weeks while waiting for vendor submission.
    Uses Temporal signals to react to external events (vendor submits).
    """

    def __init__(self) -> None:
        self._submitted = False

    @workflow.signal
    async def vendor_submitted(self) -> None:
        """Signal handler — called when the vendor submits the assessment."""
        self._submitted = True

    @workflow.run
    async def run(self, input: dict[str, Any]) -> dict[str, Any]:
        """Execute the assessment lifecycle.

        Args:
            input: Must contain ``vendor_id``, ``template_id``, ``tenant_id``.

        Returns:
            Dict with ``status`` and ``assessment_id``; optionally ``score``.
        """
        workflow.logger.info(
            "assessment_lifecycle_started",
            extra={
                "vendor_id": input.get("vendor_id"),
                "template_id": input.get("template_id"),
            },
        )

        # Step 1: Create assessment from template
        assessment: dict[str, Any] = await workflow.execute_activity(
            "create_assessment",
            input,
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=DEFAULT_RETRY,
        )
        assessment_id = assessment["id"]

        # Step 2: Distribute to vendor
        await workflow.execute_activity(
            "distribute_assessment",
            {"assessment_id": assessment_id},
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=DEFAULT_RETRY,
        )

        # Step 3: Send reminders at scheduled intervals
        elapsed_days = 0
        for day in REMINDER_DAYS:
            if self._submitted:
                break

            # Sleep for the delta between last checkpoint and this one
            delta = day - elapsed_days
            if delta > 0:
                await workflow.sleep(timedelta(days=delta))
            elapsed_days = day

            if not self._submitted:
                await workflow.execute_activity(
                    "send_reminder",
                    {
                        "assessment_id": assessment_id,
                        "day": day,
                        "vendor_id": input.get("vendor_id"),
                    },
                    start_to_close_timeout=timedelta(seconds=15),
                    retry_policy=DEFAULT_RETRY,
                )

        # Step 4: Wait for vendor submission (remaining time up to deadline)
        if not self._submitted:
            remaining_days = SUBMISSION_DEADLINE_DAYS - elapsed_days
            try:
                await workflow.wait_condition(
                    lambda: self._submitted,
                    timeout=timedelta(days=max(remaining_days, 1)),
                )
            except TimeoutError:
                # Deadline breached — escalate
                await workflow.execute_activity(
                    "escalate_overdue",
                    {
                        "assessment_id": assessment_id,
                        "vendor_id": input.get("vendor_id"),
                        "days_overdue": SUBMISSION_DEADLINE_DAYS,
                    },
                    start_to_close_timeout=timedelta(seconds=15),
                    retry_policy=DEFAULT_RETRY,
                )

                workflow.logger.warn(
                    "assessment_overdue",
                    extra={"assessment_id": assessment_id},
                )

                return {
                    "status": "overdue",
                    "assessment_id": assessment_id,
                }

        # Step 5: Auto-score the submitted assessment
        score: dict[str, Any] = await workflow.execute_activity(
            "score_assessment",
            {
                "assessment_id": assessment_id,
                "vendor_id": input.get("vendor_id"),
            },
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=DEFAULT_RETRY,
        )

        # Step 6: Notify for review
        await workflow.execute_activity(
            "send_notification",
            {
                "type": "assessment_ready_for_review",
                "assessment_id": assessment_id,
                "vendor_id": input.get("vendor_id"),
                "score": score.get("score"),
            },
            start_to_close_timeout=timedelta(seconds=15),
            retry_policy=DEFAULT_RETRY,
        )

        workflow.logger.info(
            "assessment_lifecycle_completed",
            extra={
                "assessment_id": assessment_id,
                "score": score.get("score"),
            },
        )

        return {
            "status": "awaiting_review",
            "assessment_id": assessment_id,
            "score": score,
        }
