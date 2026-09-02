"""
Scoring calculation engine — pure functions for score computation.

Separated from service layer for testability and Blueprint compliance.
"""

from __future__ import annotations

from app.modules.scoring.models import ScoringModel
from app.modules.vendors.models import Vendor


def extract_dimensions(
    model: ScoringModel,
) -> list[dict]:
    """Extract dimension configs from model."""
    config = model.config or {}
    return config.get("dimensions", [])


def calculate_dimensions(
    vendor: Vendor,
    dimensions: list[dict],
) -> dict[str, float]:
    """Calculate per-dimension scores from vendor data."""
    scores: dict[str, float] = {}
    for dim in dimensions:
        name = dim.get("name", "unknown")
        score = _dimension_score(vendor, name)
        scores[name] = round(score, 2)
    return scores


def aggregate_score(
    method: str,
    dim_scores: dict[str, float],
    dimensions: list[dict],
) -> float:
    """Calculate overall score from dimension scores."""
    if not dim_scores:
        return 0.0

    if method == "multiplicative":
        product = 1.0
        for dim in dimensions:
            name = dim.get("name", "")
            val = dim_scores.get(name, 50.0)
            product *= val / 100.0
        return round(product * 100.0, 2)

    total = 0.0
    weight_sum = 0.0
    for dim in dimensions:
        name = dim.get("name", "")
        weight = dim.get("weight", 0.0)
        val = dim_scores.get(name, 0.0)
        total += val * weight
        weight_sum += weight

    if weight_sum == 0:
        return 0.0
    return round(total / weight_sum, 2)


def calculate_inherent(
    vendor: Vendor,
    model: ScoringModel,
) -> float:
    """Calculate inherent risk score."""
    base = 50.0
    factors = model.inherent_risk_factors or {}

    dc_weights = factors.get(
        "data_classification",
        {
            "restricted": 90,
            "confidential": 70,
            "internal": 40,
            "public": 20,
        },
    )
    if vendor.data_classification:
        base = dc_weights.get(vendor.data_classification, base)

    bc_adj = factors.get(
        "business_criticality",
        {
            "critical": 20,
            "high": 10,
            "medium": 0,
            "low": -10,
        },
    )
    if vendor.business_criticality:
        base += bc_adj.get(vendor.business_criticality, 0)

    return min(100.0, max(0.0, round(base, 2)))


def classify_risk(
    score: float,
    thresholds: dict | None,
) -> str:
    """Classify a score into a risk level."""
    t = thresholds or {
        "critical": 25.0,
        "high": 50.0,
        "medium": 75.0,
    }
    if score < t.get("critical", 25.0):
        return "critical"
    if score < t.get("high", 50.0):
        return "high"
    if score < t.get("medium", 75.0):
        return "medium"
    return "low"


def build_snapshot(vendor: Vendor) -> dict:
    """Capture vendor state at scoring time."""
    return {
        "tier": vendor.tier,
        "status": vendor.status,
        "data_classification": vendor.data_classification,
        "business_criticality": vendor.business_criticality,
        "inherent_risk_score": vendor.inherent_risk_score,
        "external_rating_score": vendor.external_rating_score,
    }


def _dimension_score(vendor: Vendor, dimension: str) -> float:
    """Estimate score for a dimension from vendor data."""
    base = 50.0
    if vendor.inherent_risk_score is not None:
        base = vendor.inherent_risk_score
    if vendor.external_rating_score is not None:
        base = (base + vendor.external_rating_score) / 2
    return min(100.0, max(0.0, base))
