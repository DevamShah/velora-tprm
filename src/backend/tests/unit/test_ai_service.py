"""
Unit tests for AIService.

The v2.0 MVP AI service is a deterministic mock — it never calls an
external LLM provider, so there is no network client to stub. These
tests mock only the database session and assert on the generated
answers, the review-queue composition and the review state machine.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.modules.ai.schemas import (
    ReviewDecision,
    ReviewItemType,
    ReviewSubmitRequest,
)
from app.modules.ai.service import AIService
from app.modules.vendors.models import Vendor  # noqa: F401
from app.modules.assessments.models import (
    Assessment,
    Question,
    QuestionnaireResponse,
)
from app.modules.evidence.models import EvidenceControlMapping

TENANT_ID = uuid.UUID("00000000-0000-4000-a000-000000000001")
ASSESSMENT_ID = uuid.UUID("00000000-0000-4000-a000-000000000500")
MAPPING_ID = uuid.UUID("aaaaaaaa-0000-4000-a000-000000000501")
RESPONSE_ID = uuid.UUID("bbbbbbbb-0000-4000-a000-000000000502")
QUESTION_ID = uuid.UUID("00000000-0000-4000-a000-000000000503")

NOW = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


def _make_question(**overrides) -> Question:
    """Create a Question ORM object with defaults."""
    defaults = dict(
        id=QUESTION_ID,
        tenant_id=TENANT_ID,
        question_text="Do you encrypt customer data at rest?",
        question_type="text",
        section="Security",
        is_required=True,
        weight=1.0,
        created_at=NOW,
        updated_at=NOW,
    )
    defaults.update(overrides)
    question = MagicMock(spec=Question)
    for k, v in defaults.items():
        setattr(question, k, v)
    return question


def _make_response(**overrides) -> QuestionnaireResponse:
    """Create a QuestionnaireResponse ORM object with defaults."""
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
        created_at=NOW,
        updated_at=NOW,
    )
    defaults.update(overrides)
    resp = MagicMock(spec=QuestionnaireResponse)
    for k, v in defaults.items():
        setattr(resp, k, v)
    return resp


def _make_assessment(**overrides) -> Assessment:
    """Create an Assessment ORM object with defaults."""
    defaults = dict(
        id=ASSESSMENT_ID,
        tenant_id=TENANT_ID,
        title="Q1 Security Review",
        status="in_progress",
        responses=[],
        created_at=NOW,
        updated_at=NOW,
    )
    defaults.update(overrides)
    assessment = MagicMock(spec=Assessment)
    for k, v in defaults.items():
        setattr(assessment, k, v)
    return assessment


def _make_mapping(**overrides) -> EvidenceControlMapping:
    """Create an EvidenceControlMapping ORM object with defaults."""
    defaults = dict(
        id=MAPPING_ID,
        tenant_id=TENANT_ID,
        evidence_id=uuid.uuid4(),
        clause_id=uuid.uuid4(),
        coverage_type="full",
        confidence=0.9,
        verified=False,
        verified_by=None,
        created_at=NOW,
        updated_at=NOW,
    )
    defaults.update(overrides)
    mapping = MagicMock(spec=EvidenceControlMapping)
    for k, v in defaults.items():
        setattr(mapping, k, v)
    return mapping


def _mock_execute_result(items=None):
    """Mock execute result exposing scalars().first()/.all()."""
    items = items or []
    result = MagicMock()
    scalars = MagicMock()
    scalars.first.return_value = items[0] if items else None
    scalars.all.return_value = items
    result.scalars.return_value = scalars
    return result


@pytest.fixture
def mock_session():
    """Async mock session with a synchronous add()."""
    session = AsyncMock()
    session.add = MagicMock()
    return session


@pytest.fixture
def service(mock_session):
    """AIService bound to the mocked session."""
    return AIService(mock_session)


# -- Auto-fill ------------------------------------------------------


@pytest.mark.asyncio
async def test_auto_fill_fills_only_empty_responses(
    service, mock_session
):
    """Empty responses are filled; answered ones are skipped."""
    empty = _make_response(id=uuid.uuid4())
    answered_value = _make_response(
        id=uuid.uuid4(), response_value="yes"
    )
    answered_text = _make_response(
        id=uuid.uuid4(), response_text="Already answered"
    )
    assessment = _make_assessment(
        responses=[empty, answered_value, answered_text]
    )
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([assessment])
    )

    result = await service.auto_fill_assessment(
        TENANT_ID, ASSESSMENT_ID
    )

    assert result is not None
    assert result.assessment_id == ASSESSMENT_ID
    assert result.questions_filled == 1
    assert result.skipped_count == 2
    assert result.total_questions == 3
    assert result.average_confidence == 0.82

    assert empty.ai_prefilled is True
    assert empty.ai_confidence == 0.82
    assert empty.review_status == "ai_pending"
    assert empty.responded_at is not None
    assert "AES-256-GCM" in empty.response_text

    # Untouched rows keep their original state.
    assert answered_value.ai_prefilled is False
    assert answered_value.review_status == "pending"
    assert answered_text.response_text == "Already answered"
    mock_session.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_auto_fill_missing_assessment_returns_none(
    service, mock_session
):
    """A missing assessment returns None and never flushes."""
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([])
    )

    result = await service.auto_fill_assessment(
        TENANT_ID, ASSESSMENT_ID
    )

    assert result is None
    mock_session.flush.assert_not_awaited()


@pytest.mark.asyncio
async def test_auto_fill_no_responses_yields_zero_confidence(
    service, mock_session
):
    """With nothing to fill, average confidence is 0.0."""
    assessment = _make_assessment(responses=[])
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([assessment])
    )

    result = await service.auto_fill_assessment(
        TENANT_ID, ASSESSMENT_ID
    )

    assert result is not None
    assert result.questions_filled == 0
    assert result.skipped_count == 0
    assert result.total_questions == 0
    assert result.average_confidence == 0.0


@pytest.mark.asyncio
async def test_auto_fill_handles_null_responses_collection(
    service, mock_session
):
    """A NULL responses relationship is treated as empty."""
    assessment = _make_assessment(responses=None)
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([assessment])
    )

    result = await service.auto_fill_assessment(
        TENANT_ID, ASSESSMENT_ID
    )

    assert result is not None
    assert result.total_questions == 0
    assert result.questions_filled == 0


@pytest.mark.asyncio
async def test_auto_fill_response_without_question(
    service, mock_session
):
    """A detached question falls back to the generic answer."""
    orphan = _make_response(question=None)
    assessment = _make_assessment(responses=[orphan])
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([assessment])
    )

    result = await service.auto_fill_assessment(
        TENANT_ID, ASSESSMENT_ID
    )

    assert result is not None
    assert result.questions_filled == 1
    assert orphan.response_text == AIService._mock_answer(
        "Unknown"
    )
    assert "documented" in orphan.response_text


@pytest.mark.asyncio
async def test_auto_fill_uses_question_text_for_answer(
    service, mock_session
):
    """The generated answer is derived from the question text."""
    backup_q = _make_response(
        question=_make_question(
            question_text="Describe your backup strategy."
        )
    )
    assessment = _make_assessment(responses=[backup_q])
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([assessment])
    )

    await service.auto_fill_assessment(TENANT_ID, ASSESSMENT_ID)

    assert "RPO: 1 hour" in backup_q.response_text


# -- Review queue ---------------------------------------------------


@pytest.mark.asyncio
async def test_get_review_queue_combines_and_sorts(
    service, mock_session
):
    """Queue merges both sources and sorts by ascending confidence."""
    mapping = _make_mapping(confidence=0.9)
    low_resp = _make_response(
        ai_prefilled=True,
        ai_confidence=0.4,
        review_status="ai_pending",
    )
    mid_resp = _make_response(
        id=uuid.UUID("cccccccc-0000-4000-a000-000000000504"),
        ai_prefilled=True,
        ai_confidence=0.55,
        review_status="ai_pending",
    )
    mock_session.execute = AsyncMock(
        side_effect=[
            _mock_execute_result([mapping]),
            _mock_execute_result([low_resp, mid_resp]),
        ]
    )

    queue = await service.get_review_queue(TENANT_ID)

    assert queue.total == 3
    assert [i.confidence for i in queue.items] == [0.4, 0.55, 0.9]
    assert [i.item_type for i in queue.items] == [
        "ai_response",
        "ai_response",
        "evidence_mapping",
    ]
    assert queue.items[0].title == "AI response bbbbbbbb"
    assert queue.items[0].description == "Confidence: 40%"
    assert queue.items[1].title == "AI response cccccccc"
    assert queue.items[2].title == "Evidence mapping aaaaaaaa"
    assert queue.items[2].description == (
        "Coverage: full, confidence: 90%"
    )
    assert queue.items[2].created_at == NOW


@pytest.mark.asyncio
async def test_get_review_queue_empty(service, mock_session):
    """Nothing pending yields an empty queue with total 0."""
    mock_session.execute = AsyncMock(
        side_effect=[
            _mock_execute_result([]),
            _mock_execute_result([]),
        ]
    )

    queue = await service.get_review_queue(TENANT_ID)

    assert queue.total == 0
    assert queue.items == []


@pytest.mark.asyncio
async def test_get_review_queue_null_ai_confidence(
    service, mock_session
):
    """A NULL AI confidence is coerced to 0.0 for sorting."""
    resp = _make_response(
        ai_prefilled=True,
        ai_confidence=None,
        review_status="ai_pending",
    )
    mock_session.execute = AsyncMock(
        side_effect=[
            _mock_execute_result([_make_mapping(confidence=0.5)]),
            _mock_execute_result([resp]),
        ]
    )

    queue = await service.get_review_queue(TENANT_ID)

    assert queue.items[0].confidence == 0.0
    assert queue.items[0].description == "Confidence: 0%"
    assert queue.items[1].confidence == 0.5


# -- Submit review: routing -----------------------------------------


@pytest.mark.asyncio
async def test_submit_review_routes_to_mapping(
    service, mock_session
):
    """An evidence_mapping item is routed to the mapping handler."""
    mapping = _make_mapping()
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([mapping])
    )

    data = ReviewSubmitRequest(
        item_type=ReviewItemType.evidence_mapping,
        decision=ReviewDecision.approve,
    )
    result = await service.submit_review(
        TENANT_ID, MAPPING_ID, data
    )

    assert result is not None
    assert result.item_type == "evidence_mapping"
    assert result.decision == "approve"
    assert result.updated is True
    assert result.id == MAPPING_ID
    assert mapping.verified is True
    mock_session.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_submit_review_routes_to_response(
    service, mock_session
):
    """An ai_response item is routed to the response handler."""
    resp = _make_response(ai_prefilled=True)
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([resp])
    )

    data = ReviewSubmitRequest(
        item_type=ReviewItemType.ai_response,
        decision=ReviewDecision.approve,
        notes="Looks right",
    )
    result = await service.submit_review(
        TENANT_ID, RESPONSE_ID, data
    )

    assert result is not None
    assert result.item_type == "ai_response"
    assert resp.review_status == "approved"
    assert resp.reviewer_notes == "Looks right"


# -- Review: evidence mapping ---------------------------------------


@pytest.mark.asyncio
async def test_review_mapping_reject_leaves_unverified(
    service, mock_session
):
    """Rejecting a mapping does not mark it verified."""
    mapping = _make_mapping()
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([mapping])
    )

    result = await service._review_mapping(
        TENANT_ID,
        MAPPING_ID,
        ReviewSubmitRequest(
            item_type=ReviewItemType.evidence_mapping,
            decision=ReviewDecision.reject,
        ),
    )

    assert mapping.verified is False
    assert result is not None
    assert result.decision == "reject"
    assert result.updated is True
    mock_session.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_review_mapping_missing_returns_none(
    service, mock_session
):
    """A missing mapping returns None without flushing."""
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([])
    )

    result = await service.submit_review(
        TENANT_ID,
        MAPPING_ID,
        ReviewSubmitRequest(
            item_type=ReviewItemType.evidence_mapping,
            decision=ReviewDecision.approve,
        ),
    )

    assert result is None
    mock_session.flush.assert_not_awaited()


# -- Review: AI response --------------------------------------------


@pytest.mark.asyncio
async def test_review_response_reject_clears_ai_answer(
    service, mock_session
):
    """Rejection wipes the AI answer and clears the prefill flag."""
    resp = _make_response(
        ai_prefilled=True,
        response_text="AI generated text",
        review_status="ai_pending",
    )
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([resp])
    )

    result = await service.submit_review(
        TENANT_ID,
        RESPONSE_ID,
        ReviewSubmitRequest(
            item_type=ReviewItemType.ai_response,
            decision=ReviewDecision.reject,
            notes="Wrong control",
        ),
    )

    assert resp.review_status == "rejected"
    assert resp.ai_prefilled is False
    assert resp.response_text is None
    assert resp.reviewer_notes == "Wrong control"
    assert resp.reviewed_at is not None
    assert result is not None
    assert result.decision == "reject"


@pytest.mark.asyncio
async def test_review_response_revise_sets_revision_needed(
    service, mock_session
):
    """The revise decision maps to revision_needed and keeps text."""
    resp = _make_response(
        ai_prefilled=True,
        response_text="AI generated text",
        review_status="ai_pending",
    )
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([resp])
    )

    result = await service.submit_review(
        TENANT_ID,
        RESPONSE_ID,
        ReviewSubmitRequest(
            item_type=ReviewItemType.ai_response,
            decision=ReviewDecision.revise,
        ),
    )

    assert resp.review_status == "revision_needed"
    assert resp.ai_prefilled is True
    assert resp.response_text == "AI generated text"
    assert resp.reviewer_notes is None
    assert result is not None
    assert result.decision == "revise"
    assert result.updated is True


@pytest.mark.asyncio
async def test_review_response_missing_returns_none(
    service, mock_session
):
    """A missing response returns None without flushing."""
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([])
    )

    result = await service.submit_review(
        TENANT_ID,
        RESPONSE_ID,
        ReviewSubmitRequest(
            item_type=ReviewItemType.ai_response,
            decision=ReviewDecision.approve,
        ),
    )

    assert result is None
    mock_session.flush.assert_not_awaited()


# -- Usage stats ----------------------------------------------------


@pytest.mark.asyncio
async def test_get_usage_stats_returns_mock_figures(service):
    """Usage stats are the documented MVP placeholder values."""
    stats = await service.get_usage_stats(TENANT_ID)

    assert stats.total_tokens_used == 284_500
    assert stats.total_requests == 142
    assert stats.tokens_this_month == 48_200
    assert stats.requests_this_month == 31
    assert stats.auto_fills_completed == 8
    assert stats.evidence_processed == 15
    assert stats.average_confidence == 0.84
    assert stats.monthly_limit == 500_000
    assert stats.usage_percentage == 9.64
    assert stats.tokens_this_month < stats.monthly_limit


# -- Mock answer generation -----------------------------------------


@pytest.mark.parametrize(
    "question,marker",
    [
        ("Is data encrypted at rest?", "AES-256-GCM"),
        ("How is access controlled?", "Role-based access control"),
        ("Describe your auth model.", "MFA required"),
        ("What is your backup policy?", "RTO: 4 hours"),
        ("Incident response process?", "24/7 SOC monitoring"),
        ("Do you keep audit trails?", "12-month retention"),
        ("Are logs immutable?", "immutable storage"),
        ("Tell us about your culture.", "reviewed"),
    ],
)
def test_mock_answer_branches(question, marker):
    """Each keyword branch produces its own canned answer."""
    assert marker in AIService._mock_answer(question)


def test_mock_answer_is_case_insensitive():
    """Keyword matching lowercases the question first."""
    assert AIService._mock_answer(
        "IS DATA ENCRYPTED?"
    ) == AIService._mock_answer("is data encrypted?")


def test_mock_answer_encryption_wins_over_access():
    """Earlier branches take precedence over later ones."""
    answer = AIService._mock_answer(
        "How do you encrypt data and control access?"
    )

    assert "AES-256-GCM" in answer
    assert "Role-based" not in answer


def test_mock_answer_default_for_unrelated_question():
    """Unmatched questions fall back to the generic statement."""
    answer = AIService._mock_answer("What is your head count?")

    assert answer == (
        "The organisation maintains documented "
        "policies and procedures that are reviewed "
        "annually and align with industry standards."
    )
