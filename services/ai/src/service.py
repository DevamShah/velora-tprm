"""
AI business logic — auto-fill via Claude, review queue, usage tracking.

v2.1: Real Anthropic Claude API integration replacing mock responses.
"""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import anthropic

from velora_common.logging import get_logger
from .claude_client import ClaudeClient, ClaudeResponse
from .prompts import (
    QUESTIONNAIRE_SYSTEM_PROMPT,
    batch_questions,
    build_autofill_prompt,
    parse_autofill_response,
)
from .cross_deps.assessment_models import (
    Assessment,
    QuestionnaireResponse,
)
from .cross_deps.evidence_models import (
    Evidence,
    EvidenceControlMapping,
)
from .schemas import (
    AIUsageStats,
    AutoFillAnswerDetail,
    AutoFillResponse,
    ReviewQueueItem,
    ReviewQueueResponse,
    ReviewSubmitRequest,
    ReviewSubmitResponse,
)

logger = get_logger(__name__)

_REVIEW_THRESHOLD = 0.7


def _get_claude_client() -> Optional[ClaudeClient]:
    """Create a Claude client if API key is available."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        logger.warning("claude_client_unavailable",
                       reason="ANTHROPIC_API_KEY not set")
        return None
    return ClaudeClient()


class AIService:
    """AI service — Claude-powered auto-fill + review queue."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # -- Auto-fill --------------------------------------------------

    async def auto_fill_assessment(
        self,
        tenant_id: uuid.UUID,
        assessment_id: uuid.UUID,
    ) -> Optional[AutoFillResponse]:
        """Auto-fill empty assessment questions using Claude."""
        query = (
            select(Assessment)
            .options(
                selectinload(Assessment.responses)
                .selectinload(QuestionnaireResponse.question),
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
        empty_responses = [
            r for r in responses
            if not r.response_value and not r.response_text
        ]
        skipped = len(responses) - len(empty_responses)

        if not empty_responses:
            return AutoFillResponse(
                assessment_id=assessment_id,
                questions_filled=0,
                total_questions=len(responses),
                average_confidence=0.0,
                skipped_count=skipped,
            )

        # Build vendor context from assessment
        vendor_context = self._build_vendor_context(
            assessment
        )
        evidence_context = await self._get_evidence_context(
            tenant_id, assessment
        )

        questions = self._prepare_questions(empty_responses)

        # Call Claude in batches
        client = _get_claude_client()
        all_answers: List[AutoFillAnswerDetail] = []
        total_in = 0
        total_out = 0

        try:
            for batch in batch_questions(questions):
                answers, tokens_in, tokens_out = (
                    await self._fill_batch(
                        client, vendor_context,
                        evidence_context, batch,
                    )
                )
                all_answers.extend(answers)
                total_in += tokens_in
                total_out += tokens_out
        finally:
            if client is not None:
                await client.close()

        filled, avg_conf = self._apply_answers(
            empty_responses, all_answers
        )

        await self._session.flush()

        logger.info(
            "auto_fill_complete",
            assessment_id=str(assessment_id),
            filled=filled,
            total_tokens=total_in + total_out,
        )

        return AutoFillResponse(
            assessment_id=assessment_id,
            questions_filled=filled,
            total_questions=len(responses),
            average_confidence=round(avg_conf, 3),
            skipped_count=skipped,
            total_input_tokens=total_in,
            total_output_tokens=total_out,
            answers=all_answers,
        )

    @staticmethod
    def _prepare_questions(
        empty_responses: list,
    ) -> list:
        """Build and cap the question dicts for batching."""
        questions = [
            {
                "question_id": str(r.id),
                "question_text": (
                    r.question.question_text
                    if r.question else "Unknown"
                ),
            }
            for r in empty_responses
        ]

        max_questions = 200
        if len(questions) > max_questions:
            logger.warning(
                "auto_fill_capped",
                requested=len(questions),
                cap=max_questions,
            )
            questions = questions[:max_questions]

        return questions

    @staticmethod
    def _apply_answers(
        empty_responses: list,
        all_answers: List[AutoFillAnswerDetail],
    ) -> tuple[int, float]:
        """Apply AI answers to empty responses. Returns (filled, avg_confidence)."""
        answer_map = {
            a.question_id: a for a in all_answers
        }
        filled = 0
        total_confidence = 0.0

        for resp in empty_responses:
            answer = answer_map.get(resp.id)
            if answer is None:
                continue
            resp.ai_prefilled = True
            resp.ai_confidence = answer.confidence
            resp.response_text = answer.answer
            resp.review_status = (
                "ai_pending"
                if answer.confidence < _REVIEW_THRESHOLD
                else "ai_approved"
            )
            resp.responded_at = datetime.now(timezone.utc)
            filled += 1
            total_confidence += answer.confidence

        avg_conf = (
            total_confidence / filled if filled > 0 else 0.0
        )
        return filled, avg_conf

    async def _fill_batch(
        self,
        client: Optional[ClaudeClient],
        vendor_context: dict,
        evidence_context: Optional[list],
        questions: list,
    ) -> tuple[
        List[AutoFillAnswerDetail], int, int
    ]:
        """Fill one batch of questions via Claude."""
        if client is None:
            return self._fallback_answers(questions), 0, 0

        prompt = build_autofill_prompt(
            vendor_context=vendor_context,
            evidence_context=evidence_context,
            questions=questions,
        )

        try:
            response = await client.send_message(
                system=QUESTIONNAIRE_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
        except (
            anthropic.APIError,
            anthropic.APITimeoutError,
            anthropic.RateLimitError,
        ) as exc:
            logger.error(
                "claude_batch_failed",
                error_type=type(exc).__name__,
            )
            return self._fallback_answers(questions), 0, 0

        parsed = parse_autofill_response(response.content)
        answers: List[AutoFillAnswerDetail] = []

        # Build set of valid question IDs from this batch
        valid_qids = {
            q["question_id"] for q in questions
        }

        for item in parsed:
            try:
                qid = str(item["question_id"])
                # Only accept answers for questions we sent
                if qid not in valid_qids:
                    continue
                raw_conf = float(
                    item.get("confidence", 0.5)
                )
                # Clamp confidence to [0.0, 1.0]
                clamped_conf = max(0.0, min(1.0, raw_conf))
                # Truncate answer to reasonable length
                answer_text = str(
                    item.get("answer", "")
                )[:10_000]
                answers.append(AutoFillAnswerDetail(
                    question_id=uuid.UUID(qid),
                    answer=answer_text,
                    confidence=clamped_conf,
                    reasoning=str(
                        item.get("reasoning", "")
                    )[:2000],
                    evidence_citations=item.get(
                        "evidence_citations", []
                    )[:20],
                ))
            except (KeyError, ValueError, TypeError):
                continue

        return (
            answers,
            response.input_tokens,
            response.output_tokens,
        )

    @staticmethod
    def _fallback_answers(
        questions: list,
    ) -> List[AutoFillAnswerDetail]:
        """Low-confidence fallback when Claude is unavailable."""
        return [
            AutoFillAnswerDetail(
                question_id=uuid.UUID(q["question_id"]),
                answer=(
                    "AI service unavailable. "
                    "Manual review required."
                ),
                confidence=0.1,
                reasoning="Claude API unavailable — fallback",
                evidence_citations=[],
            )
            for q in questions
        ]

    def _build_vendor_context(
        self, assessment: Assessment
    ) -> dict:
        """Extract vendor context from assessment."""
        vendor = getattr(assessment, "vendor", None)
        if vendor is None:
            return {"name": "Unknown vendor"}
        return {
            "name": getattr(vendor, "name", "Unknown"),
            "domain": getattr(vendor, "domain", None),
            "tier": getattr(vendor, "tier", None),
            "data_classification": getattr(
                vendor, "data_classification", None
            ),
            "business_criticality": getattr(
                vendor, "business_criticality", None
            ),
        }

    async def _get_evidence_context(
        self,
        tenant_id: uuid.UUID,
        assessment: Assessment,
    ) -> Optional[list]:
        """Fetch parsed evidence for the vendor."""
        vendor_id = getattr(assessment, "vendor_id", None)
        if vendor_id is None:
            return None

        query = select(Evidence).where(
            Evidence.tenant_id == tenant_id,
            Evidence.vendor_id == vendor_id,
            Evidence.status == "parsed",
        )
        result = await self._session.execute(query)
        evidence_list = result.scalars().all()
        if not evidence_list:
            return None

        return [
            {
                "document_type": e.document_type,
                "extraction_summary": getattr(
                    e, "extraction_summary", ""
                ),
            }
            for e in evidence_list
        ]

    # -- Review Queue -----------------------------------------------

    async def get_review_queue(
        self,
        tenant_id: uuid.UUID,
    ) -> ReviewQueueResponse:
        """Combine evidence needing review + low-confidence AI responses."""
        items: List[ReviewQueueItem] = []

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
    ) -> Optional[ReviewSubmitResponse]:
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
        """Compute AI usage from completed auto-fill responses."""
        # Count AI-prefilled responses for this tenant
        prefilled_query = select(QuestionnaireResponse).where(
            QuestionnaireResponse.tenant_id == tenant_id,
            QuestionnaireResponse.ai_prefilled.is_(True),
        )
        prefilled_result = await self._session.execute(
            prefilled_query
        )
        prefilled = prefilled_result.scalars().all()
        total_fills = len(prefilled)

        # Count evidence processed
        evidence_query = select(Evidence).where(
            Evidence.tenant_id == tenant_id,
            Evidence.status == "parsed",
        )
        evidence_result = await self._session.execute(
            evidence_query
        )
        evidence_count = len(
            evidence_result.scalars().all()
        )

        # Compute average confidence
        confidences = [
            r.ai_confidence
            for r in prefilled
            if r.ai_confidence is not None
        ]
        avg_conf = (
            sum(confidences) / len(confidences)
            if confidences else 0.0
        )

        monthly_limit = 500_000
        # Token tracking requires persistent storage
        # (Sprint 1 scope: per-call logging only)
        estimated_tokens = total_fills * 600

        return AIUsageStats(
            total_tokens_used=estimated_tokens,
            total_requests=total_fills,
            tokens_this_month=estimated_tokens,
            requests_this_month=total_fills,
            auto_fills_completed=total_fills,
            evidence_processed=evidence_count,
            average_confidence=round(avg_conf, 2),
            monthly_limit=monthly_limit,
            usage_percentage=round(
                (estimated_tokens / monthly_limit) * 100, 2
            ) if monthly_limit > 0 else 0.0,
        )

    # -- Private helpers --------------------------------------------

    async def _review_mapping(
        self,
        tenant_id: uuid.UUID,
        item_id: uuid.UUID,
        data: ReviewSubmitRequest,
    ) -> Optional[ReviewSubmitResponse]:
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
    ) -> Optional[ReviewSubmitResponse]:
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
        resp.reviewed_at = datetime.now(timezone.utc)
        await self._session.flush()

        return ReviewSubmitResponse(
            id=item_id,
            item_type="ai_response",
            decision=data.decision.value,
            updated=True,
        )
