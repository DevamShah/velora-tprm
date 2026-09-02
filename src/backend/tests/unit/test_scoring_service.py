"""
Unit tests for ScoringService.

Mocks the async SQLAlchemy session so the service's orchestration —
model CRUD, score calculation and persistence, history and portfolio
aggregation — is exercised against the real engine arithmetic without
touching a database.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.modules.scoring.models import (
    ScoreHistory,
    ScoringModel,
    VendorScore,
)
from app.modules.scoring.schemas import (
    DimensionWeight,
    ScoringMethod,
    ScoringModelCreate,
    ScoringModelUpdate,
)
from app.modules.scoring.service import ScoringService
from app.modules.vendors.models import Vendor

TENANT_ID = uuid.UUID("00000000-0000-4000-a000-000000000001")
VENDOR_ID = uuid.UUID("00000000-0000-4000-a000-000000000100")
OTHER_VENDOR_ID = uuid.UUID("00000000-0000-4000-a000-000000000101")
MODEL_ID = uuid.UUID("00000000-0000-4000-a000-000000000300")
OTHER_MODEL_ID = uuid.UUID("00000000-0000-4000-a000-000000000301")
SCORE_ID = uuid.UUID("00000000-0000-4000-a000-000000000400")
HISTORY_ID = uuid.UUID("00000000-0000-4000-a000-000000000500")

NOW = datetime(2026, 1, 15, 12, 0, 0, tzinfo=timezone.utc)


def _make_vendor(**overrides) -> Vendor:
    """Create a Vendor ORM stub with sensible defaults."""
    defaults = dict(
        id=VENDOR_ID,
        tenant_id=TENANT_ID,
        name="Acme Corp",
        domain="acme.com",
        description="Test vendor",
        status="active",
        tier="medium",
        industry="Technology",
        country="US",
        employee_count=500,
        annual_revenue=Decimal("1000000"),
        data_classification="confidential",
        business_criticality="high",
        contract_start_date=None,
        contract_end_date=None,
        contract_value=Decimal("200000"),
        primary_contact_name="John Doe",
        primary_contact_email_encrypted=None,
        primary_contact_email_hash=None,
        tags=["saas"],
        notes=None,
        inherent_risk_score=60.0,
        residual_risk_score=None,
        external_rating_score=80.0,
        external_rating_provider="SecurityScorecard",
        last_assessed_at=None,
        next_assessment_due=None,
        deleted_at=None,
        created_at=NOW,
        updated_at=NOW,
        contacts=[],
        enrichments=[],
    )
    defaults.update(overrides)
    vendor = MagicMock(spec=Vendor)
    for k, v in defaults.items():
        setattr(vendor, k, v)
    return vendor


def _make_scoring_model(**overrides) -> ScoringModel:
    """Create a ScoringModel ORM stub with sensible defaults."""
    defaults = dict(
        id=MODEL_ID,
        tenant_id=TENANT_ID,
        name="Default Model",
        description="Balanced model",
        method="weighted_average",
        is_default=True,
        config={
            "dimensions": [
                {"name": "security", "weight": 0.7},
                {"name": "compliance", "weight": 0.3},
            ]
        },
        inherent_risk_factors=None,
        risk_thresholds=None,
        created_at=NOW,
        updated_at=NOW,
        scores=[],
    )
    defaults.update(overrides)
    model = MagicMock(spec=ScoringModel)
    for k, v in defaults.items():
        setattr(model, k, v)
    return model


def _make_vendor_score(**overrides) -> VendorScore:
    """Create a VendorScore ORM stub with sensible defaults."""
    defaults = dict(
        id=SCORE_ID,
        tenant_id=TENANT_ID,
        vendor_id=VENDOR_ID,
        scoring_model_id=MODEL_ID,
        overall_score=70.0,
        dimension_scores={"security": 70.0, "compliance": 70.0},
        inherent_score=80.0,
        residual_score=70.0,
        external_score=80.0,
        input_snapshot={"tier": "medium"},
        calculated_at=NOW,
        created_at=NOW,
        updated_at=NOW,
        scoring_model=None,
    )
    defaults.update(overrides)
    score = MagicMock(spec=VendorScore)
    for k, v in defaults.items():
        setattr(score, k, v)
    return score


def _make_history(**overrides) -> ScoreHistory:
    """Create a ScoreHistory ORM stub with sensible defaults."""
    defaults = dict(
        id=HISTORY_ID,
        tenant_id=TENANT_ID,
        vendor_id=VENDOR_ID,
        overall_score=65.5,
        dimension_scores={"security": 65.5},
        recorded_at=NOW,
        created_at=NOW,
        updated_at=NOW,
    )
    defaults.update(overrides)
    history = MagicMock(spec=ScoreHistory)
    for k, v in defaults.items():
        setattr(history, k, v)
    return history


def _mock_execute_result(items):
    """Create a mock execute result that returns scalars."""
    result = MagicMock()
    scalars = MagicMock()
    scalars.first.return_value = items[0] if items else None
    scalars.all.return_value = items
    result.scalars.return_value = scalars
    result.scalar.return_value = len(items)
    return result


def _mock_count_result(count):
    """Create a mock execute result for a scalar COUNT query."""
    result = MagicMock()
    result.scalar.return_value = count
    return result


def _stamp(obj) -> None:
    """Fill in DB-side defaults the way a flush would."""
    if getattr(obj, "id", None) is None:
        obj.id = uuid.uuid4()
    if getattr(obj, "created_at", None) is None:
        obj.created_at = NOW
    if getattr(obj, "updated_at", None) is None:
        obj.updated_at = NOW


@pytest.fixture
def mock_session():
    """Async mock session that stamps added objects like a flush would."""
    session = AsyncMock()
    session.add = MagicMock(side_effect=_stamp)
    session.flush = AsyncMock()
    return session


@pytest.fixture
def service(mock_session):
    """ScoringService bound to the mocked session."""
    return ScoringService(mock_session)


# ── list_models ────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_models_returns_responses(service, mock_session):
    """Each ORM row is mapped to a ScoringModelResponse."""
    models = [
        _make_scoring_model(name="Strict"),
        _make_scoring_model(
            id=OTHER_MODEL_ID,
            name="Lenient",
            method="multiplicative",
            is_default=False,
        ),
    ]
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result(models)
    )

    result = await service.list_models(TENANT_ID)

    assert [m.name for m in result] == ["Strict", "Lenient"]
    assert result[0].is_default is True
    assert result[1].method == "multiplicative"
    assert result[1].id == OTHER_MODEL_ID
    assert result[0].tenant_id == TENANT_ID


@pytest.mark.asyncio
async def test_list_models_empty(service, mock_session):
    """No rows yields an empty list."""
    mock_session.execute = AsyncMock(return_value=_mock_execute_result([]))

    assert await service.list_models(TENANT_ID) == []


# ── create_model ───────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_model_persists_dimensions(service, mock_session):
    """Dimensions are serialised into config and the row is flushed."""
    data = ScoringModelCreate(
        name="Security First",
        description="Weighted towards security",
        method=ScoringMethod.weighted_average,
        is_default=False,
        dimensions=[
            DimensionWeight(name="security", weight=0.8),
            DimensionWeight(name="compliance", weight=0.2),
        ],
        risk_thresholds={"critical": 30.0},
    )

    result = await service.create_model(TENANT_ID, data)

    mock_session.add.assert_called_once()
    mock_session.flush.assert_awaited_once()
    added = mock_session.add.call_args.args[0]
    assert isinstance(added, ScoringModel)
    assert added.config == {
        "dimensions": [
            {"name": "security", "weight": 0.8, "description": None},
            {"name": "compliance", "weight": 0.2, "description": None},
        ]
    }
    assert result.name == "Security First"
    assert result.method == "weighted_average"
    assert result.is_default is False
    assert result.risk_thresholds == {"critical": 30.0}
    # No default flag -> no clear-default query was issued.
    mock_session.execute.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_model_default_clears_existing(service, mock_session):
    """Creating a default model unsets the previous default."""
    existing = _make_scoring_model(id=OTHER_MODEL_ID, is_default=True)
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([existing])
    )
    data = ScoringModelCreate(
        name="New Default",
        method=ScoringMethod.multiplicative,
        is_default=True,
        dimensions=[DimensionWeight(name="security", weight=1.0)],
    )

    result = await service.create_model(TENANT_ID, data)

    assert existing.is_default is False
    assert result.is_default is True
    assert result.method == "multiplicative"
    mock_session.execute.assert_awaited_once()


# ── update_model ───────────────────────────────────────────


@pytest.mark.asyncio
async def test_update_model_not_found(service, mock_session):
    """A missing model returns None and never flushes."""
    mock_session.execute = AsyncMock(return_value=_mock_execute_result([]))

    result = await service.update_model(
        TENANT_ID, MODEL_ID, ScoringModelUpdate(name="Nope")
    )

    assert result is None
    mock_session.flush.assert_not_awaited()


@pytest.mark.asyncio
async def test_update_model_scalar_fields(service, mock_session):
    """Set fields are applied; enum values are unwrapped to strings."""
    model = _make_scoring_model(name="Old", method="weighted_average")
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([model])
    )
    data = ScoringModelUpdate(
        name="Renamed",
        description="Now multiplicative",
        method=ScoringMethod.multiplicative,
    )

    result = await service.update_model(TENANT_ID, MODEL_ID, data)

    assert model.name == "Renamed"
    assert model.method == "multiplicative"
    assert model.description == "Now multiplicative"
    assert result.name == "Renamed"
    assert result.method == "multiplicative"
    mock_session.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_model_leaves_unset_fields_alone(service, mock_session):
    """Fields absent from the payload are not touched."""
    model = _make_scoring_model(name="Original", description="Keep me")
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([model])
    )

    await service.update_model(
        TENANT_ID, MODEL_ID, ScoringModelUpdate(name="Changed")
    )

    assert model.name == "Changed"
    assert model.description == "Keep me"
    assert model.method == "weighted_average"


@pytest.mark.asyncio
async def test_update_model_rebuilds_config_from_dimensions(
    service, mock_session
):
    """Supplying dimensions replaces the stored config wholesale."""
    model = _make_scoring_model()
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([model])
    )
    data = ScoringModelUpdate(
        dimensions=[
            DimensionWeight(
                name="resilience", weight=1.0, description="BCP/DR"
            )
        ]
    )

    result = await service.update_model(TENANT_ID, MODEL_ID, data)

    assert model.config == {
        "dimensions": [
            {
                "name": "resilience",
                "weight": 1.0,
                "description": "BCP/DR",
            }
        ]
    }
    assert result.config == model.config


@pytest.mark.asyncio
async def test_update_model_default_clears_others(service, mock_session):
    """Promoting a model to default demotes every other default."""
    target = _make_scoring_model(is_default=False)
    other = _make_scoring_model(id=OTHER_MODEL_ID, is_default=True)
    mock_session.execute = AsyncMock(
        side_effect=[
            _mock_execute_result([target]),
            _mock_execute_result([other]),
        ]
    )

    result = await service.update_model(
        TENANT_ID, MODEL_ID, ScoringModelUpdate(is_default=True)
    )

    assert target.is_default is True
    assert other.is_default is False
    assert result.is_default is True
    assert mock_session.execute.await_count == 2


# ── calculate_score ────────────────────────────────────────


@pytest.mark.asyncio
async def test_calculate_score_vendor_not_found(service, mock_session):
    """An unknown vendor returns None without resolving a model."""
    mock_session.execute = AsyncMock(return_value=_mock_execute_result([]))

    result = await service.calculate_score(TENANT_ID, VENDOR_ID)

    assert result is None
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_calculate_score_no_model_raises(service, mock_session):
    """A tenant with no default scoring model is an error."""
    mock_session.execute = AsyncMock(
        side_effect=[
            _mock_execute_result([_make_vendor()]),
            _mock_execute_result([]),
        ]
    )

    with pytest.raises(ValueError, match="No scoring model found"):
        await service.calculate_score(TENANT_ID, VENDOR_ID)


@pytest.mark.asyncio
async def test_calculate_score_computes_and_persists(service, mock_session):
    """The full scoring path computes, persists and writes back."""
    vendor = _make_vendor(
        inherent_risk_score=60.0,
        external_rating_score=80.0,
        data_classification="confidential",
        business_criticality="high",
    )
    model = _make_scoring_model()
    mock_session.execute = AsyncMock(
        side_effect=[
            _mock_execute_result([vendor]),
            _mock_execute_result([model]),
        ]
    )

    result = await service.calculate_score(TENANT_ID, VENDOR_ID)

    # dimensions score (60 + 80) / 2 == 70.0; weights 0.7/0.3 -> 70.0
    assert result.overall_score == 70.0
    assert result.dimension_scores == {
        "security": 70.0,
        "compliance": 70.0,
    }
    # confidential (70) + high (+10) == 80.0
    assert result.inherent_score == 80.0
    assert result.residual_score == 70.0
    assert result.external_score == 80.0
    assert result.risk_level == "medium"
    assert result.vendor_id == VENDOR_ID
    assert result.scoring_model_id == MODEL_ID

    # Vendor risk fields are written back.
    assert vendor.inherent_risk_score == 80.0
    assert vendor.residual_risk_score == 70.0

    # A VendorScore and a ScoreHistory row are both added.
    added = [c.args[0] for c in mock_session.add.call_args_list]
    assert len(added) == 2
    score_row, history_row = added
    assert isinstance(score_row, VendorScore)
    assert isinstance(history_row, ScoreHistory)
    assert score_row.overall_score == 70.0
    assert score_row.input_snapshot == {
        "tier": "medium",
        "status": "active",
        "data_classification": "confidential",
        "business_criticality": "high",
        "inherent_risk_score": 60.0,
        "external_rating_score": 80.0,
    }
    assert history_row.overall_score == 70.0
    assert history_row.recorded_at == score_row.calculated_at
    mock_session.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_calculate_score_uses_explicit_model(service, mock_session):
    """An explicit model id bypasses the default-model lookup."""
    vendor = _make_vendor(
        inherent_risk_score=None,
        external_rating_score=None,
        data_classification="restricted",
        business_criticality="critical",
    )
    model = _make_scoring_model(
        id=OTHER_MODEL_ID,
        method="multiplicative",
        is_default=False,
        risk_thresholds={"critical": 30.0, "high": 60.0, "medium": 90.0},
    )
    mock_session.execute = AsyncMock(
        side_effect=[
            _mock_execute_result([vendor]),
            _mock_execute_result([model]),
        ]
    )

    result = await service.calculate_score(
        TENANT_ID, VENDOR_ID, scoring_model_id=OTHER_MODEL_ID
    )

    # Each dimension falls back to 50.0; 0.5 * 0.5 == 0.25 -> 25.0
    assert result.overall_score == 25.0
    assert result.scoring_model_id == OTHER_MODEL_ID
    # restricted (90) + critical (+20) clamps to 100.0
    assert result.inherent_score == 100.0
    # Custom thresholds put 25.0 below the critical cut-off of 30.
    assert result.risk_level == "critical"


@pytest.mark.asyncio
async def test_calculate_score_with_no_dimensions(service, mock_session):
    """A model without dimensions scores zero rather than exploding."""
    vendor = _make_vendor()
    model = _make_scoring_model(config={})
    mock_session.execute = AsyncMock(
        side_effect=[
            _mock_execute_result([vendor]),
            _mock_execute_result([model]),
        ]
    )

    result = await service.calculate_score(TENANT_ID, VENDOR_ID)

    assert result.overall_score == 0.0
    assert result.dimension_scores == {}
    assert result.residual_score == 0.0
    assert result.risk_level == "critical"


# ── bulk_calculate ─────────────────────────────────────────


@pytest.mark.asyncio
async def test_bulk_calculate_mixed_outcomes(service, mock_session):
    """Successes, missing vendors and raised errors are all tallied."""
    vendor = _make_vendor()
    model = _make_scoring_model()
    missing_id = uuid.UUID("00000000-0000-4000-a000-0000000001ff")

    mock_session.execute = AsyncMock(
        side_effect=[
            # vendor 1: found, model found -> success
            _mock_execute_result([vendor]),
            _mock_execute_result([model]),
            # vendor 2: not found
            _mock_execute_result([]),
            # vendor 3: found, but no scoring model -> ValueError
            _mock_execute_result([_make_vendor(id=OTHER_VENDOR_ID)]),
            _mock_execute_result([]),
        ]
    )

    result = await service.bulk_calculate(
        TENANT_ID, [VENDOR_ID, missing_id, OTHER_VENDOR_ID]
    )

    assert result.calculated == 1
    assert result.failed == 2
    assert len(result.results) == 1
    assert result.results[0].overall_score == 70.0
    assert result.errors[0] == {
        "vendor_id": str(missing_id),
        "error": "Vendor not found",
    }
    assert result.errors[1]["vendor_id"] == str(OTHER_VENDOR_ID)
    assert "No scoring model found" in result.errors[1]["error"]


@pytest.mark.asyncio
async def test_bulk_calculate_all_successful(service, mock_session):
    """A clean run reports zero failures and no error entries."""
    mock_session.execute = AsyncMock(
        side_effect=[
            _mock_execute_result([_make_vendor()]),
            _mock_execute_result([_make_scoring_model()]),
            _mock_execute_result([_make_vendor(id=OTHER_VENDOR_ID)]),
            _mock_execute_result([_make_scoring_model()]),
        ]
    )

    result = await service.bulk_calculate(
        TENANT_ID, [VENDOR_ID, OTHER_VENDOR_ID]
    )

    assert result.calculated == 2
    assert result.failed == 0
    assert result.errors == []
    assert {r.vendor_id for r in result.results} == {
        VENDOR_ID,
        OTHER_VENDOR_ID,
    }


# ── get_vendor_score ───────────────────────────────────────


@pytest.mark.asyncio
async def test_get_vendor_score_none(service, mock_session):
    """A vendor that has never been scored returns None."""
    mock_session.execute = AsyncMock(return_value=_mock_execute_result([]))

    assert await service.get_vendor_score(TENANT_ID, VENDOR_ID) is None


@pytest.mark.asyncio
async def test_get_vendor_score_applies_model_thresholds(
    service, mock_session
):
    """The owning model's thresholds drive the reported risk level."""
    score = _make_vendor_score(overall_score=45.0)
    model = _make_scoring_model(
        risk_thresholds={"critical": 50.0, "high": 70.0, "medium": 85.0}
    )
    mock_session.execute = AsyncMock(
        side_effect=[
            _mock_execute_result([score]),
            _mock_execute_result([model]),
        ]
    )

    result = await service.get_vendor_score(TENANT_ID, VENDOR_ID)

    assert result.overall_score == 45.0
    assert result.risk_level == "critical"
    assert result.vendor_id == VENDOR_ID
    assert result.inherent_score == 80.0
    assert result.dimension_scores == {
        "security": 70.0,
        "compliance": 70.0,
    }
    assert mock_session.execute.await_count == 2


@pytest.mark.asyncio
async def test_get_vendor_score_without_model_uses_defaults(
    service, mock_session
):
    """A score with no model skips the lookup and uses default bands."""
    score = _make_vendor_score(scoring_model_id=None, overall_score=45.0)
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([score])
    )

    result = await service.get_vendor_score(TENANT_ID, VENDOR_ID)

    assert result.risk_level == "high"
    assert result.scoring_model_id is None
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_vendor_score_missing_model_row(service, mock_session):
    """A dangling model reference falls back to default thresholds."""
    score = _make_vendor_score(overall_score=90.0)
    mock_session.execute = AsyncMock(
        side_effect=[
            _mock_execute_result([score]),
            _mock_execute_result([]),
        ]
    )

    result = await service.get_vendor_score(TENANT_ID, VENDOR_ID)

    assert result.risk_level == "low"


# ── get_score_history ──────────────────────────────────────


@pytest.mark.asyncio
async def test_get_score_history_returns_items(service, mock_session):
    """History rows are mapped to items with a matching total."""
    older = datetime(2026, 1, 1, tzinfo=timezone.utc)
    rows = [
        _make_history(overall_score=65.5),
        _make_history(
            id=uuid.uuid4(),
            overall_score=40.0,
            dimension_scores={"security": 40.0},
            recorded_at=older,
        ),
    ]
    mock_session.execute = AsyncMock(return_value=_mock_execute_result(rows))

    result = await service.get_score_history(TENANT_ID, VENDOR_ID)

    assert result.vendor_id == VENDOR_ID
    assert result.total == 2
    assert [i.overall_score for i in result.items] == [65.5, 40.0]
    assert result.items[0].dimension_scores == {"security": 65.5}
    assert result.items[1].recorded_at == older


@pytest.mark.asyncio
async def test_get_score_history_empty(service, mock_session):
    """No history yields an empty, zero-total response."""
    mock_session.execute = AsyncMock(return_value=_mock_execute_result([]))

    result = await service.get_score_history(TENANT_ID, VENDOR_ID)

    assert result.items == []
    assert result.total == 0
    assert result.vendor_id == VENDOR_ID


# ── get_portfolio_summary ──────────────────────────────────


@pytest.mark.asyncio
async def test_get_portfolio_summary_no_scores(service, mock_session):
    """Vendors with no scores yield counts but no average."""
    mock_session.execute = AsyncMock(
        side_effect=[
            _mock_count_result(7),
            _mock_execute_result([]),
        ]
    )

    result = await service.get_portfolio_summary(TENANT_ID)

    assert result.total_vendors == 7
    assert result.scored_vendors == 0
    assert result.average_score is None
    assert result.risk_level_counts == {}
    assert result.tier_distribution.low == 0


@pytest.mark.asyncio
async def test_get_portfolio_summary_aggregates(service, mock_session):
    """Average, tier distribution and risk counts are all computed."""
    scores = [
        _make_vendor_score(id=uuid.uuid4(), overall_score=80.0),
        _make_vendor_score(id=uuid.uuid4(), overall_score=60.0),
        _make_vendor_score(id=uuid.uuid4(), overall_score=30.0),
        _make_vendor_score(id=uuid.uuid4(), overall_score=10.0),
    ]
    mock_session.execute = AsyncMock(
        side_effect=[
            _mock_count_result(10),
            _mock_execute_result(scores),
        ]
    )

    result = await service.get_portfolio_summary(TENANT_ID)

    assert result.total_vendors == 10
    assert result.scored_vendors == 4
    # (80 + 60 + 30 + 10) / 4 == 45.0
    assert result.average_score == 45.0
    assert result.risk_level_counts == {
        "low": 1,
        "medium": 1,
        "high": 1,
        "critical": 1,
    }
    assert result.tier_distribution.low == 1
    assert result.tier_distribution.medium == 1
    assert result.tier_distribution.high == 1
    assert result.tier_distribution.critical == 1


@pytest.mark.asyncio
async def test_get_portfolio_summary_groups_same_level(
    service, mock_session
):
    """Several vendors in one band accumulate into the same bucket."""
    scores = [
        _make_vendor_score(id=uuid.uuid4(), overall_score=90.0),
        _make_vendor_score(id=uuid.uuid4(), overall_score=85.0),
        _make_vendor_score(id=uuid.uuid4(), overall_score=80.0),
    ]
    mock_session.execute = AsyncMock(
        side_effect=[
            _mock_count_result(3),
            _mock_execute_result(scores),
        ]
    )

    result = await service.get_portfolio_summary(TENANT_ID)

    assert result.average_score == 85.0
    assert result.risk_level_counts == {"low": 3}
    assert result.tier_distribution.low == 3
    assert result.tier_distribution.high == 0


@pytest.mark.asyncio
async def test_get_portfolio_summary_rounds_average(service, mock_session):
    """A repeating average is rounded to two decimals."""
    scores = [
        _make_vendor_score(id=uuid.uuid4(), overall_score=10.0),
        _make_vendor_score(id=uuid.uuid4(), overall_score=20.0),
        _make_vendor_score(id=uuid.uuid4(), overall_score=25.0),
    ]
    mock_session.execute = AsyncMock(
        side_effect=[
            _mock_count_result(3),
            _mock_execute_result(scores),
        ]
    )

    result = await service.get_portfolio_summary(TENANT_ID)

    # 55 / 3 == 18.3333...
    assert result.average_score == 18.33


@pytest.mark.asyncio
async def test_count_vendors_handles_null_scalar(service, mock_session):
    """A NULL count collapses to 0 rather than propagating None."""
    mock_session.execute = AsyncMock(
        side_effect=[
            _mock_count_result(None),
            _mock_execute_result([]),
        ]
    )

    result = await service.get_portfolio_summary(TENANT_ID)

    assert result.total_vendors == 0


# ── _score_to_breakdown ────────────────────────────────────


def test_score_to_breakdown_maps_all_fields():
    """The static mapper copies every field and derives risk level."""
    score = _make_vendor_score(overall_score=20.0)

    breakdown = ScoringService._score_to_breakdown(score, None)

    assert breakdown.id == SCORE_ID
    assert breakdown.vendor_id == VENDOR_ID
    assert breakdown.scoring_model_id == MODEL_ID
    assert breakdown.overall_score == 20.0
    assert breakdown.inherent_score == 80.0
    assert breakdown.residual_score == 70.0
    assert breakdown.external_score == 80.0
    assert breakdown.risk_level == "critical"
    assert breakdown.calculated_at == NOW
