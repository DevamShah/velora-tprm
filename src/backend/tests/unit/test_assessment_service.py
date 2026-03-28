"""
Unit tests for AssessmentService.

Mocks the database session to test pure business logic:
state machine transitions, create from template, score
calculation, and review queue.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.modules.vendors.models import Vendor  # noqa: F401
from app.modules.assessments.models import (
    Assessment,
    AssessmentTemplate,
    Question,
    QuestionnaireResponse,
)
from app.modules.assessments.schemas import (
    AssessmentCreate,
    AssessmentFilterParams,
    AssessmentUpdate,
    QuestionnaireResponseUpdate,
)
from app.modules.assessments.service import (
    VALID_TRANSITIONS,
    AssessmentService,
)

TENANT_ID = uuid.UUID(
    "00000000-0000-4000-a000-000000000001"
)
ASSESSMENT_ID = uuid.UUID(
    "00000000-0000-4000-a000-000000000300"
)
TEMPLATE_ID = uuid.UUID(
    "00000000-0000-4000-a000-000000000400"
)
VENDOR_ID = uuid.UUID(
    "00000000-0000-4000-a000-000000000100"
)
QUESTION_ID = uuid.UUID(
    "00000000-0000-4000-a000-000000000500"
)
RESPONSE_ID = uuid.UUID(
    "00000000-0000-4000-a000-000000000600"
)
REVIEWER_ID = uuid.UUID(
    "00000000-0000-4000-a000-000000000010"
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _make_template(**overrides) -> AssessmentTemplate:
    """Create a mock AssessmentTemplate."""
    now = _now()
    defaults = dict(
        id=TEMPLATE_ID,
        tenant_id=TENANT_ID,
        name="SIG Core Assessment",
        description="Test template",
        framework_ids=None,
        tier_applicability=["critical", "high"],
        is_system=True,
        is_active=True,
        scoring_weights={"info_sec": 1.5},
        question_count=5,
        estimated_duration_minutes=60,
        questions=[],
        assessments=[],
        created_at=now,
        updated_at=now,
    )
    defaults.update(overrides)
    template = MagicMock(spec=AssessmentTemplate)
    for k, v in defaults.items():
        setattr(template, k, v)
    return template


def _make_assessment(**overrides) -> Assessment:
    """Create a mock Assessment."""
    now = _now()
    vendor = MagicMock()
    vendor.name = "Acme Corp"
    tmpl = MagicMock()
    tmpl.name = "SIG Core Assessment"
    defaults = dict(
        id=ASSESSMENT_ID,
        tenant_id=TENANT_ID,
        vendor_id=VENDOR_ID,
        template_id=TEMPLATE_ID,
        title="Annual Assessment",
        description="Test assessment",
        status="draft",
        assigned_to=None,
        distributed_at=None,
        submitted_at=None,
        completed_at=None,
        due_date=None,
        reminder_schedule=None,
        overall_score=None,
        ai_confidence=None,
        scoring_details=None,
        vendor=vendor,
        template=tmpl,
        responses=[],
        created_at=now,
        updated_at=now,
    )
    defaults.update(overrides)
    assessment = MagicMock(spec=Assessment)
    for k, v in defaults.items():
        setattr(assessment, k, v)
    return assessment


def _make_question(**overrides) -> Question:
    """Create a mock Question."""
    now = _now()
    defaults = dict(
        id=QUESTION_ID,
        tenant_id=TENANT_ID,
        question_bank_id=None,
        template_id=TEMPLATE_ID,
        section="Information Security",
        subsection="Policy",
        question_text="Do you have a security policy?",
        question_type="yes_no",
        options=None,
        is_required=True,
        weight=1.5,
        risk_domain="information_security",
        guidance_text="Provide policy doc.",
        order_index=1,
        created_at=now,
        updated_at=now,
    )
    defaults.update(overrides)
    question = MagicMock(spec=Question)
    for k, v in defaults.items():
        setattr(question, k, v)
    return question


def _make_response(**overrides) -> QuestionnaireResponse:
    """Create a mock QuestionnaireResponse."""
    now = _now()
    defaults = dict(
        id=RESPONSE_ID,
        tenant_id=TENANT_ID,
        assessment_id=ASSESSMENT_ID,
        question_id=QUESTION_ID,
        response_value=None,
        response_text=None,
        response_options=None,
        ai_prefilled=False,
        ai_confidence=None,
        ai_citations=None,
        reviewer_id=None,
        review_status="pending",
        reviewer_notes=None,
        responded_at=None,
        reviewed_at=None,
        question=_make_question(),
        assessment=None,
        created_at=now,
        updated_at=now,
    )
    defaults.update(overrides)
    response = MagicMock(spec=QuestionnaireResponse)
    for k, v in defaults.items():
        setattr(response, k, v)
    return response


def _mock_execute_result(items):
    """Create a mock execute result."""
    result = MagicMock()
    scalars = MagicMock()
    scalars.first.return_value = (
        items[0] if items else None
    )
    scalars.all.return_value = items
    result.scalars.return_value = scalars
    result.scalar.return_value = len(items)
    return result


@pytest.fixture
def mock_session():
    """Async mock session."""
    session = AsyncMock()
    session.add = MagicMock()
    return session


@pytest.fixture
def service(mock_session):
    """AssessmentService with mocked session."""
    return AssessmentService(mock_session)


# -- State Machine Tests ------------------------------------------


class TestStateMachine:
    """Test state machine transition enforcement."""

    def test_valid_transitions_defined(self):
        """All statuses have transition entries."""
        expected = {
            "draft",
            "distributed",
            "in_progress",
            "submitted",
            "under_review",
            "completed",
            "cancelled",
        }
        assert set(VALID_TRANSITIONS.keys()) == expected

    def test_draft_to_distributed_valid(self):
        """draft -> distributed is allowed."""
        AssessmentService._enforce_transition(
            "draft", "distributed"
        )

    def test_draft_to_cancelled_valid(self):
        """draft -> cancelled is allowed."""
        AssessmentService._enforce_transition(
            "draft", "cancelled"
        )

    def test_draft_to_completed_invalid(self):
        """draft -> completed is NOT allowed."""
        with pytest.raises(ValueError, match="Invalid"):
            AssessmentService._enforce_transition(
                "draft", "completed"
            )

    def test_submitted_to_under_review_valid(self):
        """submitted -> under_review is allowed."""
        AssessmentService._enforce_transition(
            "submitted", "under_review"
        )

    def test_completed_to_anything_invalid(self):
        """completed is a terminal state."""
        with pytest.raises(ValueError, match="Invalid"):
            AssessmentService._enforce_transition(
                "completed", "draft"
            )

    def test_cancelled_is_terminal(self):
        """cancelled is a terminal state."""
        with pytest.raises(ValueError, match="Invalid"):
            AssessmentService._enforce_transition(
                "cancelled", "draft"
            )

    def test_in_progress_to_submitted(self):
        """in_progress -> submitted is allowed."""
        AssessmentService._enforce_transition(
            "in_progress", "submitted"
        )

    def test_any_active_to_cancelled(self):
        """All non-terminal states can be cancelled."""
        active = [
            "draft",
            "distributed",
            "in_progress",
            "submitted",
            "under_review",
        ]
        for status in active:
            AssessmentService._enforce_transition(
                status, "cancelled"
            )


# -- Score Calculation Tests --------------------------------------


class TestScoreCalculation:
    """Test the response scoring logic."""

    def test_score_yes(self):
        """'yes' response scores 1.0."""
        resp = _make_response(response_value="yes")
        assert AssessmentService._score_response(resp) == 1.0

    def test_score_no(self):
        """'no' response scores 0.0."""
        resp = _make_response(response_value="no")
        assert AssessmentService._score_response(resp) == 0.0

    def test_score_partial(self):
        """'partial' response scores 0.5."""
        resp = _make_response(response_value="partial")
        assert AssessmentService._score_response(resp) == 0.5

    def test_score_compliant(self):
        """'compliant' scores 1.0."""
        resp = _make_response(response_value="Compliant")
        assert AssessmentService._score_response(resp) == 1.0

    def test_score_scale_5(self):
        """Scale value 5 (max) scores 1.0."""
        resp = _make_response(response_value="5")
        assert AssessmentService._score_response(resp) == 1.0

    def test_score_scale_1(self):
        """Scale value 1 (min) scores 0.0."""
        resp = _make_response(response_value="1")
        assert AssessmentService._score_response(resp) == 0.0

    def test_score_scale_3(self):
        """Scale value 3 (mid) scores 0.5."""
        resp = _make_response(response_value="3")
        assert AssessmentService._score_response(resp) == 0.5

    def test_score_none(self):
        """None response scores 0.0."""
        resp = _make_response(response_value=None)
        assert AssessmentService._score_response(resp) == 0.0

    def test_score_text_response(self):
        """Non-empty text gets partial credit (0.5)."""
        resp = _make_response(
            response_value="We use AES-256 encryption"
        )
        assert AssessmentService._score_response(resp) == 0.5


# -- Create Assessment Tests --------------------------------------


@pytest.mark.asyncio
async def test_create_assessment(service, mock_session):
    """create_assessment should persist and return."""
    template = _make_template()
    mock_session.execute = AsyncMock(
        side_effect=[
            _mock_execute_result([template]),  # get template
            _mock_execute_result([]),  # clone questions
        ]
    )
    mock_session.flush = AsyncMock()

    data = AssessmentCreate(
        vendor_id=VENDOR_ID,
        template_id=TEMPLATE_ID,
        title="Annual Assessment",
    )

    with patch.object(
        service, "_clone_questions", new_callable=AsyncMock
    ):
        with patch.object(
            service, "_to_response"
        ) as mock_resp:
            mock_resp.return_value = MagicMock()
            result = await service.create_assessment(
                TENANT_ID, data
            )

    mock_session.add.assert_called_once()
    assert result is not None


@pytest.mark.asyncio
async def test_create_assessment_template_not_found(
    service, mock_session
):
    """create_assessment raises when template not found."""
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([])
    )

    data = AssessmentCreate(
        vendor_id=VENDOR_ID,
        template_id=TEMPLATE_ID,
        title="Bad Assessment",
    )

    with pytest.raises(
        ValueError, match="Template not found"
    ):
        await service.create_assessment(TENANT_ID, data)


# -- List Assessments Tests ---------------------------------------


@pytest.mark.asyncio
async def test_list_assessments_paginated(
    service, mock_session
):
    """list_assessments returns paginated results."""
    assessment = _make_assessment()
    count_result = MagicMock()
    count_result.scalar.return_value = 1

    list_result = _mock_execute_result([assessment])

    mock_session.execute = AsyncMock(
        side_effect=[count_result, list_result]
    )

    filters = AssessmentFilterParams(
        page=1, page_size=10
    )
    result = await service.list_assessments(
        TENANT_ID, filters
    )

    assert result.total == 1
    assert result.page == 1
    assert len(result.items) == 1


# -- Distribute Tests ---------------------------------------------


@pytest.mark.asyncio
async def test_distribute_assessment(
    service, mock_session
):
    """distribute_assessment changes status correctly."""
    assessment = _make_assessment(status="draft")
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([assessment])
    )

    result = await service.distribute_assessment(
        TENANT_ID, ASSESSMENT_ID
    )

    assert assessment.status == "distributed"
    assert assessment.distributed_at is not None
    assert result is not None


@pytest.mark.asyncio
async def test_distribute_from_completed_fails(
    service, mock_session
):
    """Cannot distribute a completed assessment."""
    assessment = _make_assessment(status="completed")
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([assessment])
    )

    with pytest.raises(ValueError, match="Invalid"):
        await service.distribute_assessment(
            TENANT_ID, ASSESSMENT_ID
        )


# -- Complete Tests -----------------------------------------------


@pytest.mark.asyncio
async def test_complete_assessment_scores(
    service, mock_session
):
    """complete_assessment calculates and stores score."""
    assessment = _make_assessment(status="under_review")
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([assessment])
    )

    score_data = {
        "score": 85.0,
        "total_questions": 15,
        "total_weight": 18.5,
        "domain_scores": {
            "information_security": 90.0,
        },
    }

    with patch.object(
        service,
        "_calculate_score",
        new_callable=AsyncMock,
        return_value=score_data,
    ):
        result = await service.complete_assessment(
            TENANT_ID, ASSESSMENT_ID
        )

    assert assessment.status == "completed"
    assert assessment.overall_score == 85.0
    assert assessment.completed_at is not None


# -- Cancel Tests -------------------------------------------------


@pytest.mark.asyncio
async def test_cancel_draft_assessment(
    service, mock_session
):
    """Cancel from draft status."""
    assessment = _make_assessment(status="draft")
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([assessment])
    )

    result = await service.cancel_assessment(
        TENANT_ID, ASSESSMENT_ID
    )

    assert assessment.status == "cancelled"
    assert result is not None


@pytest.mark.asyncio
async def test_cancel_in_progress(
    service, mock_session
):
    """Cancel from in_progress status."""
    assessment = _make_assessment(status="in_progress")
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([assessment])
    )

    await service.cancel_assessment(
        TENANT_ID, ASSESSMENT_ID
    )
    assert assessment.status == "cancelled"


# -- Review Queue Tests -------------------------------------------


@pytest.mark.asyncio
async def test_review_queue_returns_pending(
    service, mock_session
):
    """Review queue includes pending responses."""
    assessment_mock = _make_assessment()
    vendor_mock = MagicMock()
    vendor_mock.name = "Acme Corp"
    assessment_mock.vendor = vendor_mock
    response = _make_response(
        review_status="pending",
        ai_confidence=0.4,
        assessment=assessment_mock,
    )
    # Use unique() wrapper for selectinload queries
    execute_result = MagicMock()
    scalars_mock = MagicMock()
    scalars_mock.all.return_value = [response]
    execute_result.scalars.return_value = scalars_mock
    unique_mock = MagicMock()
    unique_mock.scalars.return_value = scalars_mock
    execute_result.unique.return_value = unique_mock
    mock_session.execute = AsyncMock(
        return_value=execute_result
    )

    result = await service.get_review_queue(TENANT_ID)

    assert result.total == 1
    assert result.items[0].review_status == "pending"
    assert result.items[0].ai_confidence == 0.4


# -- Update Response Tests ----------------------------------------


@pytest.mark.asyncio
async def test_update_response(service, mock_session):
    """update_response updates value and timestamp."""
    response = _make_response()
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([response])
    )

    data = QuestionnaireResponseUpdate(
        response_value="yes",
        review_status="accepted",
    )
    result = await service.update_response(
        TENANT_ID, ASSESSMENT_ID, RESPONSE_ID, data
    )

    assert response.response_value == "yes"
    assert response.review_status == "accepted"
    assert response.responded_at is not None
    assert response.reviewed_at is not None


# -- Score Calculation Integration --------------------------------


@pytest.mark.asyncio
async def test_calculate_score_weighted(
    service, mock_session
):
    """_calculate_score applies weights correctly."""
    q1 = _make_question(
        weight=2.0,
        risk_domain="information_security",
    )
    q2 = _make_question(
        id=uuid.uuid4(),
        weight=1.0,
        risk_domain="access_control",
    )
    r1 = _make_response(
        response_value="yes", question=q1
    )
    r2 = _make_response(
        id=uuid.uuid4(),
        response_value="no",
        question=q2,
    )

    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([r1, r2])
    )

    result = await service._calculate_score(
        ASSESSMENT_ID
    )

    # r1: 1.0 * 2.0 = 2.0, r2: 0.0 * 1.0 = 0.0
    # total weight = 3.0, weighted = 2.0
    # score = 2.0 / 3.0 * 100 = 66.7
    assert result["score"] == 66.7
    assert result["total_questions"] == 2
    assert "information_security" in result["domain_scores"]
    assert "access_control" in result["domain_scores"]
