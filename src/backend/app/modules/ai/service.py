"""
AI business logic — auto-fill, review queue, usage tracking.

All operations are mock implementations for v2.0 MVP.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.logging import get_logger
from app.modules.ai.schemas import (
    AIUsageStats,
    AutoFillResponse,
    ReviewQueueItem,
    ReviewQueueResponse,
    ReviewSubmitRequest,
    ReviewSubmitResponse,
)
from app.modules.assessments.models import (
    Assessment,
    QuestionnaireResponse,
)
from app.modules.evidence.models import (
    EvidenceControlMapping,
)

logger = get_logger(__name__)


class AIService:
    """Stateless AI service — receives session per call."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # -- Auto-fill --------------------------------------------------

    async def auto_fill_assessment(
        self,
        tenant_id: uuid.UUID,
        assessment_id: uuid.UUID,
    ) -> AutoFillResponse | None:
        """Generate mock AI responses for empty questions."""
        query = (
            select(Assessment)
            .options(
                selectinload(Assessment.responses).
                selectinload(QuestionnaireResponse.question),
            )
            .where(
                Assessment.id == assessment_id,
                Assessment.tenant_id == tenant_id,
            )
        )
        result = await self._session.execute(query)
        assessment = result.scalars().first()
        if assessment is None:
            return None

        responses = assessment.responses or []
        filled = 0
        skipped = 0

        for resp in responses:
            if resp.response_value or resp.response_text:
                skipped += 1
                continue
            resp.ai_prefilled = True
            resp.ai_confidence = 0.82
            resp.response_text = self._mock_answer(
                resp.question.question_text
                if resp.question
                else "Unknown"
            )
            resp.review_status = "ai_pending"
            resp.responded_at = datetime.now(
                UTC
            )
            filled += 1

        await self._session.flush()
        total = len(responses)
        avg = 0.82 if filled > 0 else 0.0

        logger.info(
            "auto_fill_complete",
            assessment_id=str(assessment_id),
            filled=filled,
        )
        return AutoFillResponse(
            assessment_id=assessment_id,
            questions_filled=filled,
            total_questions=total,
            average_confidence=avg,
            skipped_count=skipped,
        )

    # -- Review Queue -----------------------------------------------

    async def get_review_queue(
        self,
        tenant_id: uuid.UUID,
    ) -> ReviewQueueResponse:
        """Combine evidence needing review + low-confidence AI responses."""
        items: list[ReviewQueueItem] = []

        # Evidence mappings needing verification
        ecm_query = select(EvidenceControlMapping).where(
            EvidenceControlMapping.tenant_id == tenant_id,
            EvidenceControlMapping.verified.is_(False),
        )
        ecm_result = await self._session.execute(
            ecm_query
        )
        for m in ecm_result.scalars().all():
            items.append(
                ReviewQueueItem(
                    id=m.id,
                    item_type="evidence_mapping",
                    title=f"Evidence mapping {str(m.id)[:8]}",
                    description=(
                        f"Coverage: {m.coverage_type},"
                        f" confidence: {m.confidence:.0%}"
                    ),
                    confidence=m.confidence,
                    created_at=m.created_at,
                )
            )

        # AI-prefilled responses pending review
        resp_query = select(QuestionnaireResponse).where(
            QuestionnaireResponse.tenant_id == tenant_id,
            QuestionnaireResponse.ai_prefilled.is_(True),
            QuestionnaireResponse.review_status
            == "ai_pending",
        )
        resp_result = await self._session.execute(
            resp_query
        )
        for r in resp_result.scalars().all():
            items.append(
                ReviewQueueItem(
                    id=r.id,
                    item_type="ai_response",
                    title=f"AI response {str(r.id)[:8]}",
                    description=(
                        f"Confidence: "
                        f"{r.ai_confidence or 0:.0%}"
                    ),
                    confidence=r.ai_confidence or 0.0,
                    created_at=r.created_at,
                )
            )

        items.sort(key=lambda x: x.confidence)
        return ReviewQueueResponse(
            items=items, total=len(items)
        )

    # -- Submit Review ----------------------------------------------

    async def submit_review(
        self,
        tenant_id: uuid.UUID,
        item_id: uuid.UUID,
        data: ReviewSubmitRequest,
    ) -> ReviewSubmitResponse | None:
        """Process a review decision on a queue item."""
        if data.item_type.value == "evidence_mapping":
            return await self._review_mapping(
                tenant_id, item_id, data
            )
        return await self._review_response(
            tenant_id, item_id, data
        )

    # -- Usage Stats ------------------------------------------------

    async def get_usage_stats(
        self,
        tenant_id: uuid.UUID,
    ) -> AIUsageStats:
        """Return mock AI usage statistics."""
        return AIUsageStats(
            total_tokens_used=284_500,
            total_requests=142,
            tokens_this_month=48_200,
            requests_this_month=31,
            auto_fills_completed=8,
            evidence_processed=15,
            average_confidence=0.84,
            monthly_limit=500_000,
            usage_percentage=9.64,
        )

    # -- Private helpers --------------------------------------------

    async def _review_mapping(
        self,
        tenant_id: uuid.UUID,
        item_id: uuid.UUID,
        data: ReviewSubmitRequest,
    ) -> ReviewSubmitResponse | None:
        """Review an evidence control mapping."""
        result = await self._session.execute(
            select(EvidenceControlMapping).where(
                EvidenceControlMapping.id == item_id,
                EvidenceControlMapping.tenant_id
                == tenant_id,
            )
        )
        mapping = result.scalars().first()
        if mapping is None:
            return None

        if data.decision.value == "approve":
            mapping.verified = True
        await self._session.flush()

        return ReviewSubmitResponse(
            id=item_id,
            item_type="evidence_mapping",
            decision=data.decision.value,
            updated=True,
        )

    async def _review_response(
        self,
        tenant_id: uuid.UUID,
        item_id: uuid.UUID,
        data: ReviewSubmitRequest,
    ) -> ReviewSubmitResponse | None:
        """Review an AI-prefilled response."""
        result = await self._session.execute(
            select(QuestionnaireResponse).where(
                QuestionnaireResponse.id == item_id,
                QuestionnaireResponse.tenant_id
                == tenant_id,
            )
        )
        resp = result.scalars().first()
        if resp is None:
            return None

        if data.decision.value == "approve":
            resp.review_status = "approved"
        elif data.decision.value == "reject":
            resp.review_status = "rejected"
            resp.ai_prefilled = False
            resp.response_text = None
        else:
            resp.review_status = "revision_needed"

        resp.reviewer_notes = data.notes
        resp.reviewed_at = datetime.now(UTC)
        await self._session.flush()

        return ReviewSubmitResponse(
            id=item_id,
            item_type="ai_response",
            decision=data.decision.value,
            updated=True,
        )

    @staticmethod
    def _mock_answer(question: str) -> str:
        """Generate a plausible mock answer."""
        q_lower = question.lower()
        if "encrypt" in q_lower:
            return (
                "All data is encrypted at rest using "
                "AES-256-GCM and in transit using TLS 1.3."
            )
        if "access" in q_lower or "auth" in q_lower:
            return (
                "Role-based access control (RBAC) is "
                "enforced with MFA required for all users."
            )
        if "backup" in q_lower:
            return (
                "Daily automated backups with 30-day "
                "retention. RPO: 1 hour, RTO: 4 hours."
            )
        if "incident" in q_lower:
            return (
                "Formal incident response plan with "
                "24/7 SOC monitoring and 1-hour SLA."
            )
        if "audit" in q_lower or "log" in q_lower:
            return (
                "Comprehensive audit logging with "
                "12-month retention in immutable storage."
            )
        return (
            "The organisation maintains documented "
            "policies and procedures that are reviewed "
            "annually and align with industry standards."
        )
