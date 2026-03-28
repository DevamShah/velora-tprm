"""Evidence processing workflow — upload, parse, map, verify.

Steps:
1. Register evidence upload in evidence-service
2. Classify document type (SOC2, ISO cert, policy doc, etc.)
3. Parse document with AI extraction
4. Map extracted controls to framework requirements
5. Queue for human review
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

AI_RETRY = RetryPolicy(
    maximum_attempts=2,
    initial_interval=timedelta(seconds=2),
    maximum_interval=timedelta(seconds=60),
    backoff_coefficient=2.0,
)


@workflow.defn
class EvidenceProcessingWorkflow:
    """Durable workflow for evidence ingestion and AI-powered analysis.

    Handles the full pipeline from raw file upload to mapped control
    evidence ready for reviewer sign-off.
    """

    def __init__(self) -> None:
        self._review_completed = False

    @workflow.signal
    async def review_completed(self, decision: str = "approved") -> None:
        """Signal that a human reviewer has completed their review."""
        self._review_decision = decision
        self._review_completed = True

    @workflow.run
    async def run(self, input: dict[str, Any]) -> dict[str, Any]:
        """Execute evidence processing pipeline.

        Args:
            input: Must contain ``evidence_id``, ``vendor_id``,
                   ``assessment_id``, ``file_key`` (S3 object key),
                   ``tenant_id``.

        Returns:
            Dict with processing results and review status.
        """
        self._review_decision = "pending"

        workflow.logger.info(
            "evidence_processing_started",
            extra={
                "evidence_id": input.get("evidence_id"),
                "vendor_id": input.get("vendor_id"),
            },
        )

        evidence_id = input["evidence_id"]

        # Step 1: Register the upload and get file metadata
        registration: dict[str, Any] = await workflow.execute_activity(
            "register_evidence",
            {
                "evidence_id": evidence_id,
                "vendor_id": input["vendor_id"],
                "assessment_id": input.get("assessment_id"),
                "file_key": input["file_key"],
            },
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=DEFAULT_RETRY,
        )

        # Step 2: Classify document type via AI
        classification: dict[str, Any] = await workflow.execute_activity(
            "classify_document",
            {
                "evidence_id": evidence_id,
                "file_key": input["file_key"],
                "file_type": registration.get("file_type", "unknown"),
            },
            start_to_close_timeout=timedelta(minutes=2),
            retry_policy=AI_RETRY,
        )

        doc_type = classification.get("document_type", "unknown")

        # Step 3: Parse document — extract structured data with AI
        extraction: dict[str, Any] = await workflow.execute_activity(
            "parse_evidence_document",
            {
                "evidence_id": evidence_id,
                "file_key": input["file_key"],
                "document_type": doc_type,
            },
            start_to_close_timeout=timedelta(minutes=10),
            retry_policy=AI_RETRY,
        )

        # Step 4: Map extracted controls to framework requirements
        mapping: dict[str, Any] = await workflow.execute_activity(
            "map_evidence_to_controls",
            {
                "evidence_id": evidence_id,
                "assessment_id": input.get("assessment_id"),
                "extracted_controls": extraction.get("controls", []),
                "document_type": doc_type,
            },
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=DEFAULT_RETRY,
        )

        # Step 5: Notify reviewer and queue for human review
        await workflow.execute_activity(
            "send_notification",
            {
                "type": "evidence_ready_for_review",
                "evidence_id": evidence_id,
                "vendor_id": input["vendor_id"],
                "document_type": doc_type,
                "controls_mapped": len(mapping.get("mapped_controls", [])),
            },
            start_to_close_timeout=timedelta(seconds=15),
            retry_policy=DEFAULT_RETRY,
        )

        # Step 6: Wait for human review (up to 7 days)
        try:
            await workflow.wait_condition(
                lambda: self._review_completed,
                timeout=timedelta(days=7),
            )
        except TimeoutError:
            workflow.logger.warn(
                "evidence_review_timeout",
                extra={"evidence_id": evidence_id},
            )
            self._review_decision = "timeout"

        # Step 7: Finalise evidence record with review outcome
        finalisation: dict[str, Any] = await workflow.execute_activity(
            "finalise_evidence",
            {
                "evidence_id": evidence_id,
                "review_decision": self._review_decision,
                "mapped_controls": mapping.get("mapped_controls", []),
            },
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=DEFAULT_RETRY,
        )

        workflow.logger.info(
            "evidence_processing_completed",
            extra={
                "evidence_id": evidence_id,
                "review_decision": self._review_decision,
            },
        )

        return {
            "evidence_id": evidence_id,
            "document_type": doc_type,
            "controls_extracted": len(extraction.get("controls", [])),
            "controls_mapped": len(mapping.get("mapped_controls", [])),
            "review_decision": self._review_decision,
            "status": finalisation.get("status", "completed"),
        }
