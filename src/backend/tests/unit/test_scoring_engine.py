"""
Unit tests for the scoring calculation engine.

engine.py holds pure functions with no database access, so these
tests exercise the real arithmetic directly and assert on exact
computed values, including default fallbacks, clamping and rounding.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from app.modules.scoring import engine
from app.modules.scoring.models import ScoringModel
from app.modules.vendors.models import Vendor

TENANT_ID = uuid.UUID("00000000-0000-4000-a000-000000000001")
VENDOR_ID = uuid.UUID("00000000-0000-4000-a000-000000000100")
MODEL_ID = uuid.UUID("00000000-0000-4000-a000-000000000300")


def _make_vendor(**overrides) -> Vendor:
    """Create a Vendor ORM stub with sensible defaults."""
    now = datetime.now(timezone.utc)
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
        data_classification="internal",
        business_criticality="medium",
        contract_start_date=None,
        contract_end_date=None,
        contract_value=Decimal("200000"),
        primary_contact_name="John Doe",
        primary_contact_email_encrypted=None,
        primary_contact_email_hash=None,
        tags=["saas"],
        notes=None,
        inherent_risk_score=None,
        residual_risk_score=None,
        external_rating_score=None,
        external_rating_provider=None,
        last_assessed_at=None,
        next_assessment_due=None,
        deleted_at=None,
        created_at=now,
        updated_at=now,
        contacts=[],
        enrichments=[],
    )
    defaults.update(overrides)
    vendor = MagicMock(spec=Vendor)
    for k, v in defaults.items():
        setattr(vendor, k, v)
    return vendor


def _make_model(**overrides) -> ScoringModel:
    """Create a ScoringModel ORM stub with sensible defaults."""
    now = datetime.now(timezone.utc)
    defaults = dict(
        id=MODEL_ID,
        tenant_id=TENANT_ID,
        name="Default Model",
        description="Test scoring model",
        method="weighted_average",
        is_default=True,
        config={
            "dimensions": [
                {"name": "security", "weight": 0.6},
                {"name": "compliance", "weight": 0.4},
            ]
        },
        inherent_risk_factors=None,
        risk_thresholds=None,
        created_at=now,
        updated_at=now,
        scores=[],
    )
    defaults.update(overrides)
    model = MagicMock(spec=ScoringModel)
    for k, v in defaults.items():
        setattr(model, k, v)
    return model


# ── extract_dimensions ─────────────────────────────────────


def test_extract_dimensions_returns_configured_list():
    """Dimensions come straight out of the model config."""
    model = _make_model()

    dims = engine.extract_dimensions(model)

    assert dims == [
        {"name": "security", "weight": 0.6},
        {"name": "compliance", "weight": 0.4},
    ]


def test_extract_dimensions_with_null_config():
    """A model with no config yields an empty dimension list."""
    model = _make_model(config=None)

    assert engine.extract_dimensions(model) == []


def test_extract_dimensions_with_config_missing_key():
    """A config without a 'dimensions' key yields an empty list."""
    model = _make_model(config={"other": "value"})

    assert engine.extract_dimensions(model) == []


# ── calculate_dimensions ───────────────────────────────────


def test_calculate_dimensions_defaults_to_fifty():
    """With no vendor risk data every dimension scores 50.0."""
    vendor = _make_vendor(
        inherent_risk_score=None,
        external_rating_score=None,
    )
    dims = [{"name": "security"}, {"name": "compliance"}]

    scores = engine.calculate_dimensions(vendor, dims)

    assert scores == {"security": 50.0, "compliance": 50.0}


def test_calculate_dimensions_uses_inherent_score():
    """Inherent risk score replaces the 50.0 baseline."""
    vendor = _make_vendor(
        inherent_risk_score=45.0,
        external_rating_score=None,
    )
    dims = [{"name": "security", "weight": 1.0}]

    assert engine.calculate_dimensions(vendor, dims) == {"security": 45.0}


def test_calculate_dimensions_averages_external_rating():
    """External rating is averaged against the running base."""
    vendor = _make_vendor(
        inherent_risk_score=60.0,
        external_rating_score=80.0,
    )
    dims = [{"name": "security"}]

    # (60 + 80) / 2 == 70.0
    assert engine.calculate_dimensions(vendor, dims) == {"security": 70.0}


def test_calculate_dimensions_external_only_averages_with_baseline():
    """With no inherent score the external rating averages with 50."""
    vendor = _make_vendor(
        inherent_risk_score=None,
        external_rating_score=80.0,
    )
    dims = [{"name": "security"}]

    # (50 + 80) / 2 == 65.0
    assert engine.calculate_dimensions(vendor, dims) == {"security": 65.0}


def test_calculate_dimensions_clamps_upper_bound():
    """Scores above 100 are clamped to 100.0."""
    vendor = _make_vendor(
        inherent_risk_score=150.0,
        external_rating_score=None,
    )

    scores = engine.calculate_dimensions(vendor, [{"name": "security"}])

    assert scores == {"security": 100.0}


def test_calculate_dimensions_clamps_lower_bound():
    """Negative scores are clamped to 0.0."""
    vendor = _make_vendor(
        inherent_risk_score=-25.0,
        external_rating_score=None,
    )

    scores = engine.calculate_dimensions(vendor, [{"name": "security"}])

    assert scores == {"security": 0.0}


def test_calculate_dimensions_rounds_to_two_places():
    """Dimension scores are rounded to two decimal places."""
    vendor = _make_vendor(
        inherent_risk_score=33.0,
        external_rating_score=44.005,
    )

    scores = engine.calculate_dimensions(vendor, [{"name": "security"}])

    # (33 + 44.005) / 2 == 38.5025 -> 38.5
    assert scores == {"security": 38.5}


def test_calculate_dimensions_unnamed_dimension_key():
    """A dimension without a name is keyed as 'unknown'."""
    vendor = _make_vendor(inherent_risk_score=42.0)

    scores = engine.calculate_dimensions(vendor, [{"weight": 1.0}])

    assert scores == {"unknown": 42.0}


def test_calculate_dimensions_with_no_dimensions():
    """No dimensions produces an empty score map."""
    assert engine.calculate_dimensions(_make_vendor(), []) == {}


# ── aggregate_score ────────────────────────────────────────


def test_aggregate_score_empty_scores_is_zero():
    """No dimension scores short-circuits to 0.0."""
    dims = [{"name": "security", "weight": 1.0}]

    assert engine.aggregate_score("weighted_average", {}, dims) == 0.0


def test_aggregate_score_weighted_average():
    """Weighted average honours per-dimension weights."""
    dims = [
        {"name": "security", "weight": 0.6},
        {"name": "compliance", "weight": 0.4},
    ]
    scores = {"security": 80.0, "compliance": 60.0}

    # 80*0.6 + 60*0.4 == 72.0, weight sum 1.0
    assert engine.aggregate_score("weighted_average", scores, dims) == 72.0


def test_aggregate_score_normalises_unnormalised_weights():
    """Weights that do not sum to 1 are normalised by their total."""
    dims = [
        {"name": "security", "weight": 3.0},
        {"name": "compliance", "weight": 1.0},
    ]
    scores = {"security": 80.0, "compliance": 40.0}

    # (240 + 40) / 4 == 70.0
    assert engine.aggregate_score("weighted_average", scores, dims) == 70.0


def test_aggregate_score_rounds_to_two_places():
    """A repeating average is rounded to two decimals."""
    dims = [
        {"name": "a", "weight": 1.0},
        {"name": "b", "weight": 1.0},
        {"name": "c", "weight": 1.0},
    ]
    scores = {"a": 70.0, "b": 80.0, "c": 85.0}

    # 235 / 3 == 78.3333...
    assert engine.aggregate_score("weighted_average", scores, dims) == 78.33


def test_aggregate_score_missing_dimension_counts_as_zero():
    """A weighted dimension absent from the scores contributes 0."""
    dims = [
        {"name": "security", "weight": 0.5},
        {"name": "privacy", "weight": 0.5},
    ]
    scores = {"security": 80.0}

    # (80*0.5 + 0*0.5) / 1.0 == 40.0
    assert engine.aggregate_score("weighted_average", scores, dims) == 40.0


def test_aggregate_score_zero_weight_sum_is_zero():
    """All-zero weights avoid a divide-by-zero and return 0.0."""
    dims = [
        {"name": "security", "weight": 0.0},
        {"name": "compliance", "weight": 0.0},
    ]
    scores = {"security": 90.0, "compliance": 90.0}

    assert engine.aggregate_score("weighted_average", scores, dims) == 0.0


def test_aggregate_score_dimension_without_weight_key():
    """A dimension with no weight key defaults to weight 0.0."""
    dims = [
        {"name": "security", "weight": 1.0},
        {"name": "compliance"},
    ]
    scores = {"security": 90.0, "compliance": 10.0}

    # compliance carries weight 0 -> 90*1 / 1 == 90.0
    assert engine.aggregate_score("weighted_average", scores, dims) == 90.0


def test_aggregate_score_unknown_method_falls_back_to_weighted():
    """Any non-multiplicative method uses the weighted branch."""
    dims = [
        {"name": "security", "weight": 0.5},
        {"name": "compliance", "weight": 0.5},
    ]
    scores = {"security": 100.0, "compliance": 50.0}

    assert engine.aggregate_score("mystery_method", scores, dims) == 75.0


def test_aggregate_score_multiplicative():
    """Multiplicative multiplies normalised dimension fractions."""
    dims = [{"name": "security"}, {"name": "compliance"}]
    scores = {"security": 80.0, "compliance": 50.0}

    # 0.8 * 0.5 == 0.4 -> 40.0
    assert engine.aggregate_score("multiplicative", scores, dims) == 40.0


def test_aggregate_score_multiplicative_missing_dimension_defaults_50():
    """A dimension absent from the scores defaults to 50 (0.5)."""
    dims = [{"name": "security"}, {"name": "privacy"}]
    scores = {"security": 80.0}

    # 0.8 * 0.5 == 0.4 -> 40.0
    assert engine.aggregate_score("multiplicative", scores, dims) == 40.0


def test_aggregate_score_multiplicative_no_dimensions_is_full_marks():
    """An empty dimension list leaves the product at 1.0 -> 100.0."""
    scores = {"security": 10.0}

    assert engine.aggregate_score("multiplicative", scores, []) == 100.0


def test_aggregate_score_multiplicative_rounds():
    """Multiplicative results are rounded to two decimals."""
    dims = [{"name": "a"}, {"name": "b"}, {"name": "c"}]
    scores = {"a": 90.0, "b": 90.0, "c": 90.0}

    # 0.9^3 == 0.729 -> 72.9
    assert engine.aggregate_score("multiplicative", scores, dims) == 72.9


# ── calculate_inherent ─────────────────────────────────────


def test_calculate_inherent_default_baseline():
    """No classification or criticality leaves the 50.0 baseline."""
    vendor = _make_vendor(
        data_classification=None,
        business_criticality=None,
    )

    assert engine.calculate_inherent(vendor, _make_model()) == 50.0


def test_calculate_inherent_default_weights():
    """Built-in weights apply when the model defines no factors."""
    vendor = _make_vendor(
        data_classification="confidential",
        business_criticality="high",
    )

    # 70 + 10 == 80.0
    assert engine.calculate_inherent(vendor, _make_model()) == 80.0


def test_calculate_inherent_low_criticality_subtracts():
    """A 'low' criticality subtracts 10 from the classification base."""
    vendor = _make_vendor(
        data_classification="internal",
        business_criticality="low",
    )

    # 40 - 10 == 30.0
    assert engine.calculate_inherent(vendor, _make_model()) == 30.0


def test_calculate_inherent_clamps_at_one_hundred():
    """Restricted plus critical exceeds 100 and is clamped."""
    vendor = _make_vendor(
        data_classification="restricted",
        business_criticality="critical",
    )

    # 90 + 20 == 110 -> 100.0
    assert engine.calculate_inherent(vendor, _make_model()) == 100.0


def test_calculate_inherent_clamps_at_zero():
    """Custom factors driving the score negative clamp to 0.0."""
    model = _make_model(
        inherent_risk_factors={
            "data_classification": {"trivial": 5},
            "business_criticality": {"none": -30},
        }
    )
    vendor = _make_vendor(
        data_classification="trivial",
        business_criticality="none",
    )

    # 5 - 30 == -25 -> 0.0
    assert engine.calculate_inherent(vendor, model) == 0.0


def test_calculate_inherent_custom_factors():
    """Model-supplied factors override the built-in defaults."""
    model = _make_model(
        inherent_risk_factors={
            "data_classification": {"secret": 95},
            "business_criticality": {"elevated": -50},
        }
    )
    vendor = _make_vendor(
        data_classification="secret",
        business_criticality="elevated",
    )

    assert engine.calculate_inherent(vendor, model) == 45.0


def test_calculate_inherent_unknown_values_keep_base():
    """Unmapped classification/criticality values leave the base alone."""
    vendor = _make_vendor(
        data_classification="not-a-real-class",
        business_criticality="not-a-real-criticality",
    )

    assert engine.calculate_inherent(vendor, _make_model()) == 50.0


def test_calculate_inherent_partial_factors_use_defaults():
    """A factors dict missing a key falls back to the default map."""
    model = _make_model(
        inherent_risk_factors={
            "business_criticality": {"critical": 5},
        }
    )
    vendor = _make_vendor(
        data_classification="public",
        business_criticality="critical",
    )

    # default data_classification map -> 20, custom criticality -> +5
    assert engine.calculate_inherent(vendor, model) == 25.0


def test_calculate_inherent_public_classification():
    """Public data with medium criticality scores the lowest tier."""
    vendor = _make_vendor(
        data_classification="public",
        business_criticality="medium",
    )

    assert engine.calculate_inherent(vendor, _make_model()) == 20.0


# ── classify_risk ──────────────────────────────────────────


@pytest.mark.parametrize(
    ("score", "expected"),
    [
        (0.0, "critical"),
        (24.99, "critical"),
        (25.0, "high"),
        (49.99, "high"),
        (50.0, "medium"),
        (74.99, "medium"),
        (75.0, "low"),
        (100.0, "low"),
    ],
)
def test_classify_risk_default_thresholds(score, expected):
    """Default boundaries are 25 / 50 / 75, lower bound exclusive."""
    assert engine.classify_risk(score, None) == expected


def test_classify_risk_empty_thresholds_uses_defaults():
    """An empty threshold dict still resolves the default cut-offs."""
    assert engine.classify_risk(30.0, {}) == "high"
    assert engine.classify_risk(80.0, {}) == "low"


@pytest.mark.parametrize(
    ("score", "expected"),
    [
        (35.0, "critical"),
        (50.0, "high"),
        (70.0, "medium"),
        (90.0, "low"),
    ],
)
def test_classify_risk_custom_thresholds(score, expected):
    """Custom thresholds shift every boundary."""
    thresholds = {"critical": 40.0, "high": 60.0, "medium": 80.0}

    assert engine.classify_risk(score, thresholds) == expected


def test_classify_risk_partial_thresholds():
    """Unspecified threshold keys fall back to their defaults."""
    thresholds = {"high": 60.0}

    assert engine.classify_risk(20.0, thresholds) == "critical"
    assert engine.classify_risk(30.0, thresholds) == "high"
    assert engine.classify_risk(65.0, thresholds) == "medium"
    assert engine.classify_risk(75.0, thresholds) == "low"


# ── build_snapshot ─────────────────────────────────────────


def test_build_snapshot_captures_vendor_state():
    """The snapshot records exactly the six scoring inputs."""
    vendor = _make_vendor(
        tier="critical",
        status="active",
        data_classification="restricted",
        business_criticality="critical",
        inherent_risk_score=88.0,
        external_rating_score=72.5,
    )

    snapshot = engine.build_snapshot(vendor)

    assert snapshot == {
        "tier": "critical",
        "status": "active",
        "data_classification": "restricted",
        "business_criticality": "critical",
        "inherent_risk_score": 88.0,
        "external_rating_score": 72.5,
    }


def test_build_snapshot_preserves_nulls():
    """Missing vendor risk data is preserved as None, not defaulted."""
    vendor = _make_vendor(
        data_classification=None,
        business_criticality=None,
        inherent_risk_score=None,
        external_rating_score=None,
    )

    snapshot = engine.build_snapshot(vendor)

    assert snapshot["data_classification"] is None
    assert snapshot["business_criticality"] is None
    assert snapshot["inherent_risk_score"] is None
    assert snapshot["external_rating_score"] is None
    assert snapshot["tier"] == "medium"


# ── end-to-end pipeline ────────────────────────────────────


def test_full_pipeline_weighted_average():
    """extract -> calculate -> aggregate -> classify agree end to end."""
    model = _make_model(
        config={
            "dimensions": [
                {"name": "security", "weight": 0.7},
                {"name": "compliance", "weight": 0.3},
            ]
        },
        method="weighted_average",
    )
    vendor = _make_vendor(
        inherent_risk_score=60.0,
        external_rating_score=80.0,
        data_classification="confidential",
        business_criticality="high",
    )

    dims = engine.extract_dimensions(model)
    dim_scores = engine.calculate_dimensions(vendor, dims)
    overall = engine.aggregate_score(model.method, dim_scores, dims)

    assert dim_scores == {"security": 70.0, "compliance": 70.0}
    assert overall == 70.0
    assert engine.classify_risk(overall, model.risk_thresholds) == "medium"
    assert engine.calculate_inherent(vendor, model) == 80.0


def test_full_pipeline_multiplicative_is_harsher():
    """Multiplicative aggregation penalises the same inputs harder."""
    model = _make_model(
        config={
            "dimensions": [
                {"name": "security", "weight": 0.5},
                {"name": "compliance", "weight": 0.5},
            ]
        },
        method="multiplicative",
    )
    vendor = _make_vendor(
        inherent_risk_score=60.0,
        external_rating_score=80.0,
    )

    dims = engine.extract_dimensions(model)
    dim_scores = engine.calculate_dimensions(vendor, dims)
    weighted = engine.aggregate_score("weighted_average", dim_scores, dims)
    multiplicative = engine.aggregate_score(model.method, dim_scores, dims)

    # 0.7 * 0.7 == 0.49 -> 49.0 vs the weighted 70.0
    assert multiplicative == 49.0
    assert weighted == 70.0
    assert multiplicative < weighted
    assert engine.classify_risk(multiplicative, None) == "high"
