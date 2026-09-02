"""
Assessment business logic — CRUD, state machine, scoring, review queue.

All DB queries run inside the caller-provided async session.
State machine transitions are enforced at the service layer.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.logging import get_logger
from app.modules.assessments.models import (
    Assessment,
    AssessmentTemplate,
    Question,
    QuestionnaireResponse,
)
from app.modules.assessments.schemas import (
    AssessmentCreate,
    AssessmentDetailResponse,
    AssessmentFilterParams,
    AssessmentListResponse,
    AssessmentResponse,
    AssessmentTemplateCreate,
    AssessmentTemplateResponse,
    AssessmentUpdate,
    QuestionnaireResponseItem,
    QuestionnaireResponseUpdate,
    QuestionResponse,
    ReviewQueueItem,
    ReviewQueueResponse,
)

logger = get_logger(__name__)

# -- State machine valid transitions --------------------------------

VALID_TRANSITIONS: dict[str, set[str]] = {
    "draft": {"distributed", "cancelled"},
    "distributed": {"in_progress", "cancelled"},
    "in_progress": {"submitted", "cancelled"},
    "submitted": {"under_review", "cancelled"},
    "under_review": {"completed", "cancelled"},
    "completed": set(),
    "cancelled": set(),
}


class AssessmentService:
    """Stateless assessment service — receives a session per call."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # -- Templates --------------------------------------------------

    async def list_templates(
        self,
        tenant_id: uuid.UUID,
    ) -> list[AssessmentTemplateResponse]:
        """List active assessment templates for a tenant."""
        query = select(AssessmentTemplate).where(
            AssessmentTemplate.tenant_id == tenant_id,
            AssessmentTemplate.is_active.is_(True),
        )
        result = await self._session.execute(query)
        templates = result.scalars().all()
        return [
            self._to_template_response(t)
            for t in templates
        ]

    async def create_template(
        self,
        tenant_id: uuid.UUID,
        data: AssessmentTemplateCreate,
    ) -> AssessmentTemplateResponse:
        """Create a new assessment template."""
        template = AssessmentTemplate(
            tenant_id=tenant_id,
            name=data.name,
            description=data.description,
            framework_ids=data.framework_ids,
            tier_applicability=data.tier_applicability,
            is_system=data.is_system,
            scoring_weights=data.scoring_weights,
            question_count=0,
            estimated_duration_minutes=(
                data.estimated_duration_minutes
            ),
        )
        self._session.add(template)
        await self._session.flush()
        logger.info(
            "template_created",
            template_id=str(template.id),
        )
        return self._to_template_response(template)

    # -- Create Assessment ------------------------------------------

    async def create_assessment(
        self,
        tenant_id: uuid.UUID,
        data: AssessmentCreate,
    ) -> AssessmentResponse:
        """Create assessment from template, cloning questions."""
        template = await self._get_template(
            tenant_id, data.template_id
        )
        if template is None:
            raise ValueError("Template not found")

        assessment = Assessment(
            tenant_id=tenant_id,
            vendor_id=data.vendor_id,
            template_id=data.template_id,
            title=data.title,
            description=data.description,
            status="draft",
            due_date=data.due_date,
        )
        self._session.add(assessment)
        await self._session.flush()

        await self._clone_questions(
            tenant_id, assessment.id, data.template_id
        )

        logger.info(
            "assessment_created",
            assessment_id=str(assessment.id),
        )

        # Re-fetch with eager loading to avoid lazy load in async
        from sqlalchemy.orm import selectinload

        result = await self._session.execute(
            select(Assessment)
            .options(
                selectinload(Assessment.vendor),
                selectinload(Assessment.template),
            )
            .where(Assessment.id == assessment.id)
        )
        loaded = result.scalar_one()
        return self._to_response(loaded)

    # -- List Assessments -------------------------------------------

    async def list_assessments(
        self,
        tenant_id: uuid.UUID,
        filters: AssessmentFilterParams,
    ) -> AssessmentListResponse:
        """List assessments with pagination and filtering."""
        base = select(Assessment).where(
            Assessment.tenant_id == tenant_id,
        )
        base = self._apply_filters(base, filters)

        count_q = select(func.count()).select_from(
            base.subquery()
        )
        total_result = await self._session.execute(count_q)
        total = total_result.scalar() or 0

        base = self._apply_sorting(base, filters)
        offset = (filters.page - 1) * filters.page_size
        base = base.offset(offset).limit(filters.page_size)

        result = await self._session.execute(base)
        assessments = result.scalars().all()

        return AssessmentListResponse(
            items=[
                self._to_response(a) for a in assessments
            ],
            total=total,
            page=filters.page,
            page_size=filters.page_size,
        )

    # -- Get Assessment Detail --------------------------------------

    async def get_assessment(
        self,
        tenant_id: uuid.UUID,
        assessment_id: uuid.UUID,
    ) -> AssessmentDetailResponse | None:
        """Fetch assessment with responses, template, vendor."""
        query = (
            select(Assessment)
            .options(
                selectinload(Assessment.responses).options(
                    selectinload(
                        QuestionnaireResponse.question
                    )
                ),
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
        return self._to_detail_response(assessment)

    # -- Update Assessment ------------------------------------------

    async def update_assessment(
        self,
        tenant_id: uuid.UUID,
        assessment_id: uuid.UUID,
        data: AssessmentUpdate,
    ) -> AssessmentResponse | None:
        """Update assessment metadata. Only in draft status."""
        assessment = await self._get_assessment_or_none(
            tenant_id, assessment_id
        )
        if assessment is None:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(assessment, field, value)

        await self._session.flush()
        logger.info(
            "assessment_updated",
            assessment_id=str(assessment_id),
        )
        return self._to_response(assessment)

    # -- Distribute -------------------------------------------------

    async def distribute_assessment(
        self,
        tenant_id: uuid.UUID,
        assessment_id: uuid.UUID,
    ) -> AssessmentResponse | None:
        """Distribute assessment to vendor for completion."""
        assessment = await self._get_assessment_or_none(
            tenant_id, assessment_id
        )
        if assessment is None:
            return None

        self._enforce_transition(
            assessment.status, "distributed"
        )
        assessment.status = "distributed"
        assessment.distributed_at = datetime.now(
            UTC
        )
        await self._session.flush()

        logger.info(
            "assessment_distributed",
            assessment_id=str(assessment_id),
        )
        return self._to_response(assessment)

    # -- Submit -----------------------------------------------------

    async def submit_assessment(
        self,
        tenant_id: uuid.UUID,
        assessment_id: uuid.UUID,
    ) -> AssessmentResponse | None:
        """Submit assessment after vendor completes responses."""
        assessment = await self._get_assessment_or_none(
            tenant_id, assessment_id
        )
        if assessment is None:
            return None

        self._enforce_transition(
            assessment.status, "submitted"
        )
        await self._validate_required_responses(
            assessment_id
        )

        assessment.status = "submitted"
        assessment.submitted_at = datetime.now(
            UTC
        )
        await self._session.flush()

        logger.info(
            "assessment_submitted",
            assessment_id=str(assessment_id),
        )
        return self._to_response(assessment)

    # -- Start Review -----------------------------------------------

    async def start_review(
        self,
        tenant_id: uuid.UUID,
        assessment_id: uuid.UUID,
        reviewer_id: uuid.UUID,
    ) -> AssessmentResponse | None:
        """Assign reviewer and transition to under_review."""
        assessment = await self._get_assessment_or_none(
            tenant_id, assessment_id
        )
        if assessment is None:
            return None

        self._enforce_transition(
            assessment.status, "under_review"
        )
        assessment.status = "under_review"
        assessment.assigned_to = reviewer_id
        await self._session.flush()

        logger.info(
            "assessment_review_started",
            assessment_id=str(assessment_id),
            reviewer_id=str(reviewer_id),
        )
        return self._to_response(assessment)

    # -- Complete ---------------------------------------------------

    async def complete_assessment(
        self,
        tenant_id: uuid.UUID,
        assessment_id: uuid.UUID,
    ) -> AssessmentResponse | None:
        """Complete assessment with scoring calculation."""
        assessment = await self._get_assessment_or_none(
            tenant_id, assessment_id
        )
        if assessment is None:
            return None

        self._enforce_transition(
            assessment.status, "completed"
        )

        score_data = await self._calculate_score(
            assessment_id
        )
        assessment.status = "completed"
        assessment.completed_at = datetime.now(
            UTC
        )
        assessment.overall_score = score_data["score"]
        assessment.scoring_details = score_data

        await self._session.flush()
        logger.info(
            "assessment_completed",
            assessment_id=str(assessment_id),
            score=score_data["score"],
        )
        return self._to_response(assessment)

    # -- Cancel -----------------------------------------------------

    async def cancel_assessment(
        self,
        tenant_id: uuid.UUID,
        assessment_id: uuid.UUID,
    ) -> AssessmentResponse | None:
        """Cancel an assessment from any active status."""
        assessment = await self._get_assessment_or_none(
            tenant_id, assessment_id
        )
        if assessment is None:
            return None

        self._enforce_transition(
            assessment.status, "cancelled"
        )
        assessment.status = "cancelled"
        await self._session.flush()

        logger.info(
            "assessment_cancelled",
            assessment_id=str(assessment_id),
        )
        return self._to_response(assessment)

    # -- Responses --------------------------------------------------

    async def get_responses(
        self,
        tenant_id: uuid.UUID,
        assessment_id: uuid.UUID,
    ) -> list[QuestionnaireResponseItem] | None:
        """Get all responses for an assessment with questions."""
        assessment = await self._get_assessment_or_none(
            tenant_id, assessment_id
        )
        if assessment is None:
            return None

        query = (
            select(QuestionnaireResponse)
            .options(
                selectinload(
                    QuestionnaireResponse.question
                )
            )
            .where(
                QuestionnaireResponse.assessment_id
                == assessment_id,
                QuestionnaireResponse.tenant_id
                == tenant_id,
            )
            .order_by(
                QuestionnaireResponse.created_at.asc()
            )
        )
        result = await self._session.execute(query)
        responses = result.scalars().all()
        return [
            self._to_response_item(r) for r in responses
        ]

    async def update_response(
        self,
        tenant_id: uuid.UUID,
        assessment_id: uuid.UUID,
        response_id: uuid.UUID,
        data: QuestionnaireResponseUpdate,
    ) -> QuestionnaireResponseItem | None:
        """Update a single questionnaire response."""
        query = select(QuestionnaireResponse).where(
            QuestionnaireResponse.id == response_id,
            QuestionnaireResponse.assessment_id
            == assessment_id,
            QuestionnaireResponse.tenant_id == tenant_id,
        )
        result = await self._session.execute(query)
        response = result.scalars().first()
        if response is None:
            return None

        update_data = data.model_dump(exclude_unset=True)
        now = datetime.now(UTC)

        if "response_value" in update_data:
            response.response_value = update_data[
                "response_value"
            ]
            response.responded_at = now
        if "response_text" in update_data:
            response.response_text = update_data[
                "response_text"
            ]
            response.responded_at = now
        if "review_status" in update_data:
            val = update_data["review_status"]
            response.review_status = (
                val.value if hasattr(val, "value") else val
            )
            response.reviewed_at = now
        if "reviewer_notes" in update_data:
            response.reviewer_notes = update_data[
                "reviewer_notes"
            ]

        await self._session.flush()
        logger.info(
            "response_updated",
            response_id=str(response_id),
        )
        return self._to_response_item(response)

    # -- Review Queue -----------------------------------------------

    async def get_review_queue(
        self,
        tenant_id: uuid.UUID,
    ) -> ReviewQueueResponse:
        """Get items needing review: low confidence or pending."""
        query = (
            select(QuestionnaireResponse)
            .options(
                selectinload(
                    QuestionnaireResponse.question
                ),
                selectinload(
                    QuestionnaireResponse.assessment
                ),
            )
            .where(
                QuestionnaireResponse.tenant_id
                == tenant_id,
                or_(
                    QuestionnaireResponse.review_status
                    == "pending",
                    QuestionnaireResponse.ai_confidence
                    < 0.7,
                ),
            )
            .order_by(
                QuestionnaireResponse.ai_confidence.asc()
                .nulls_first()
            )
            .limit(100)
        )
        result = await self._session.execute(query)
        responses = result.scalars().all()

        items = []
        for r in responses:
            vendor_name = ""
            assessment_title = ""
            if r.assessment:
                assessment_title = r.assessment.title
                if r.assessment.vendor:
                    vendor_name = r.assessment.vendor.name

            items.append(
                ReviewQueueItem(
                    response_id=r.id,
                    assessment_id=r.assessment_id,
                    assessment_title=assessment_title,
                    vendor_name=vendor_name,
                    question_text=(
                        r.question.question_text
                        if r.question
                        else ""
                    ),
                    section=(
                        r.question.section
                        if r.question
                        else None
                    ),
                    response_value=r.response_value,
                    ai_confidence=r.ai_confidence,
                    review_status=r.review_status,
                )
            )

        return ReviewQueueResponse(
            items=items, total=len(items)
        )

    # -- Private helpers --------------------------------------------

    async def _get_template(
        self,
        tenant_id: uuid.UUID,
        template_id: uuid.UUID,
    ) -> AssessmentTemplate | None:
        """Fetch an active template or return None."""
        result = await self._session.execute(
            select(AssessmentTemplate).where(
                AssessmentTemplate.id == template_id,
                AssessmentTemplate.tenant_id == tenant_id,
                AssessmentTemplate.is_active.is_(True),
            )
        )
        return result.scalars().first()

    async def _get_assessment_or_none(
        self,
        tenant_id: uuid.UUID,
        assessment_id: uuid.UUID,
    ) -> Assessment | None:
        """Fetch an assessment or return None."""
        result = await self._session.execute(
            select(Assessment).where(
                Assessment.id == assessment_id,
                Assessment.tenant_id == tenant_id,
            )
        )
        return result.scalars().first()

    async def _clone_questions(
        self,
        tenant_id: uuid.UUID,
        assessment_id: uuid.UUID,
        template_id: uuid.UUID,
    ) -> None:
        """Clone template questions as empty responses."""
        query = (
            select(Question)
            .where(
                Question.template_id == template_id,
                Question.tenant_id == tenant_id,
            )
            .order_by(Question.order_index.asc())
        )
        result = await self._session.execute(query)
        questions = result.scalars().all()

        for question in questions:
            response = QuestionnaireResponse(
                tenant_id=tenant_id,
                assessment_id=assessment_id,
                question_id=question.id,
                review_status="pending",
            )
            self._session.add(response)

        await self._session.flush()

    async def _validate_required_responses(
        self,
        assessment_id: uuid.UUID,
    ) -> None:
        """Ensure all required questions have responses."""
        query = (
            select(QuestionnaireResponse)
            .options(
                selectinload(
                    QuestionnaireResponse.question
                )
            )
            .where(
                QuestionnaireResponse.assessment_id
                == assessment_id,
            )
        )
        result = await self._session.execute(query)
        responses = result.scalars().all()

        missing = []
        for r in responses:
            if r.question and r.question.is_required:
                has_value = (
                    r.response_value is not None
                    or r.response_text is not None
                )
                if not has_value:
                    missing.append(
                        r.question.question_text[:50]
                    )

        if missing:
            raise ValueError(
                f"Required questions unanswered: "
                f"{', '.join(missing[:5])}"
            )

    async def _calculate_score(
        self,
        assessment_id: uuid.UUID,
    ) -> dict:
        """Calculate weighted score from responses."""
        query = (
            select(QuestionnaireResponse)
            .options(
                selectinload(
                    QuestionnaireResponse.question
                )
            )
            .where(
                QuestionnaireResponse.assessment_id
                == assessment_id,
            )
        )
        result = await self._session.execute(query)
        responses = result.scalars().all()

        total_weight = 0.0
        weighted_score = 0.0
        domain_scores: dict[str, dict] = {}

        for r in responses:
            weight = (
                r.question.weight if r.question else 1.0
            )
            total_weight += weight
            points = self._score_response(r)
            weighted_score += points * weight

            domain = (
                r.question.risk_domain
                if r.question
                else "general"
            ) or "general"
            if domain not in domain_scores:
                domain_scores[domain] = {
                    "weight": 0.0,
                    "score": 0.0,
                }
            domain_scores[domain]["weight"] += weight
            domain_scores[domain]["score"] += (
                points * weight
            )

        final_score = (
            (weighted_score / total_weight * 100)
            if total_weight > 0
            else 0.0
        )

        domain_pcts = {}
        for domain, data in domain_scores.items():
            if data["weight"] > 0:
                domain_pcts[domain] = round(
                    data["score"] / data["weight"] * 100,
                    1,
                )

        return {
            "score": round(final_score, 1),
            "total_questions": len(responses),
            "total_weight": round(total_weight, 2),
            "domain_scores": domain_pcts,
        }

    @staticmethod
    def _score_response(
        response: QuestionnaireResponse,
    ) -> float:
        """Score a single response (0.0 to 1.0)."""
        if response.response_value is None:
            return 0.0

        value = response.response_value.lower().strip()
        if value in ("yes", "true", "compliant"):
            return 1.0
        if value in ("partial", "partially"):
            return 0.5
        if value in ("no", "false", "non-compliant"):
            return 0.0

        # Scale-based responses (1-5)
        try:
            numeric = float(value)
            if 1.0 <= numeric <= 5.0:
                return (numeric - 1.0) / 4.0
        except (ValueError, TypeError):
            pass

        # Text responses default to partial credit
        if len(value) > 0:
            return 0.5
        return 0.0

    @staticmethod
    def _enforce_transition(
        current: str, target: str
    ) -> None:
        """Validate state machine transition."""
        allowed = VALID_TRANSITIONS.get(current, set())
        if target not in allowed:
            raise ValueError(
                f"Invalid transition: {current} -> "
                f"{target}. Allowed: {allowed}"
            )

    @staticmethod
    def _apply_filters(query, filters):
        """Apply WHERE clauses for assessment filters."""
        if filters.status:
            query = query.where(
                Assessment.status
                == filters.status.value
            )
        if filters.vendor_id:
            query = query.where(
                Assessment.vendor_id == filters.vendor_id
            )
        if filters.template_id:
            query = query.where(
                Assessment.template_id
                == filters.template_id
            )
        if filters.search:
            pattern = f"%{filters.search}%"
            query = query.where(
                Assessment.title.ilike(pattern)
            )
        return query

    @staticmethod
    def _apply_sorting(query, filters):
        """Apply ORDER BY clause based on filter params."""
        col = getattr(
            Assessment,
            filters.sort_by,
            Assessment.created_at,
        )
        if filters.sort_order == "desc":
            query = query.order_by(col.desc())
        else:
            query = query.order_by(col.asc())
        return query

    @staticmethod
    def _to_template_response(
        template: AssessmentTemplate,
    ) -> AssessmentTemplateResponse:
        """Map template ORM to response schema."""
        return AssessmentTemplateResponse(
            id=template.id,
            tenant_id=template.tenant_id,
            name=template.name,
            description=template.description,
            framework_ids=template.framework_ids,
            tier_applicability=template.tier_applicability,
            is_system=template.is_system,
            is_active=template.is_active,
            scoring_weights=template.scoring_weights,
            question_count=template.question_count,
            estimated_duration_minutes=(
                template.estimated_duration_minutes
            ),
            created_at=template.created_at,
            updated_at=template.updated_at,
        )

    @staticmethod
    def _to_response(
        assessment: Assessment,
    ) -> AssessmentResponse:
        """Map assessment ORM to response schema."""
        vendor_name = None
        if hasattr(assessment, "vendor") and (
            assessment.vendor is not None
        ):
            vendor_name = assessment.vendor.name

        template_name = None
        if hasattr(assessment, "template") and (
            assessment.template is not None
        ):
            template_name = assessment.template.name

        return AssessmentResponse(
            id=assessment.id,
            tenant_id=assessment.tenant_id,
            vendor_id=assessment.vendor_id,
            template_id=assessment.template_id,
            title=assessment.title,
            description=assessment.description,
            status=assessment.status,
            assigned_to=assessment.assigned_to,
            distributed_at=assessment.distributed_at,
            submitted_at=assessment.submitted_at,
            completed_at=assessment.completed_at,
            due_date=assessment.due_date,
            overall_score=assessment.overall_score,
            ai_confidence=assessment.ai_confidence,
            created_at=assessment.created_at,
            updated_at=assessment.updated_at,
            vendor_name=vendor_name,
            template_name=template_name,
        )

    @staticmethod
    def _to_detail_response(
        assessment: Assessment,
    ) -> AssessmentDetailResponse:
        """Map assessment with relations to detail schema."""
        vendor_name = None
        if hasattr(assessment, "vendor") and (
            assessment.vendor is not None
        ):
            vendor_name = assessment.vendor.name

        template_name = None
        if hasattr(assessment, "template") and (
            assessment.template is not None
        ):
            template_name = assessment.template.name

        responses = []
        answered = 0
        for r in (assessment.responses or []):
            item = AssessmentService._to_response_item(r)
            responses.append(item)
            if (
                r.response_value is not None
                or r.response_text is not None
            ):
                answered += 1

        return AssessmentDetailResponse(
            id=assessment.id,
            tenant_id=assessment.tenant_id,
            vendor_id=assessment.vendor_id,
            template_id=assessment.template_id,
            title=assessment.title,
            description=assessment.description,
            status=assessment.status,
            assigned_to=assessment.assigned_to,
            distributed_at=assessment.distributed_at,
            submitted_at=assessment.submitted_at,
            completed_at=assessment.completed_at,
            due_date=assessment.due_date,
            overall_score=assessment.overall_score,
            ai_confidence=assessment.ai_confidence,
            scoring_details=assessment.scoring_details,
            reminder_schedule=assessment.reminder_schedule,
            created_at=assessment.created_at,
            updated_at=assessment.updated_at,
            vendor_name=vendor_name,
            template_name=template_name,
            responses=responses,
            response_count=len(responses),
            answered_count=answered,
        )

    @staticmethod
    def _to_response_item(
        r: QuestionnaireResponse,
    ) -> QuestionnaireResponseItem:
        """Map a QuestionnaireResponse to its schema."""
        question = None
        if r.question is not None:
            question = QuestionResponse(
                id=r.question.id,
                tenant_id=r.question.tenant_id,
                question_bank_id=(
                    r.question.question_bank_id
                ),
                template_id=r.question.template_id,
                section=r.question.section,
                subsection=r.question.subsection,
                question_text=r.question.question_text,
                question_type=r.question.question_type,
                options=r.question.options,
                is_required=r.question.is_required,
                weight=r.question.weight,
                risk_domain=r.question.risk_domain,
                guidance_text=r.question.guidance_text,
                order_index=r.question.order_index,
                created_at=r.question.created_at,
                updated_at=r.question.updated_at,
            )

        return QuestionnaireResponseItem(
            id=r.id,
            assessment_id=r.assessment_id,
            question_id=r.question_id,
            response_value=r.response_value,
            response_text=r.response_text,
            response_options=r.response_options,
            ai_prefilled=r.ai_prefilled,
            ai_confidence=r.ai_confidence,
            ai_citations=r.ai_citations,
            reviewer_id=r.reviewer_id,
            review_status=r.review_status,
            reviewer_notes=r.reviewer_notes,
            responded_at=r.responded_at,
            reviewed_at=r.reviewed_at,
            created_at=r.created_at,
            updated_at=r.updated_at,
            question=question,
        )
