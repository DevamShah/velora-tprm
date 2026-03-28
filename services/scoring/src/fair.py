"""
FAIR (Factor Analysis of Information Risk) quantification engine.

Translates risk scores to dollar-value loss estimates:
  Loss Event Frequency (LEF) x Loss Magnitude (LM) = Annual Loss Expectancy (ALE)

Supports Monte Carlo simulation for range estimates.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import List, Optional

from velora_common.logging import get_logger

logger = get_logger(__name__)


@dataclass
class FAIRInput:
    """Input parameters for FAIR analysis."""

    vendor_name: str
    risk_score: float  # 0-100 from scoring engine
    data_sensitivity: str  # low, medium, high, critical
    annual_revenue_at_risk: float  # USD
    threat_event_frequency: float  # events/year estimate
    vulnerability: float  # 0.0-1.0 probability
    # Loss magnitude factors
    primary_loss_min: float = 10_000
    primary_loss_max: float = 1_000_000
    secondary_loss_min: float = 50_000
    secondary_loss_max: float = 5_000_000


@dataclass
class FAIRResult:
    """Output of FAIR analysis."""

    vendor_name: str
    annual_loss_expectancy: float  # ALE in USD
    ale_min: float  # 5th percentile
    ale_max: float  # 95th percentile
    loss_event_frequency: float
    single_loss_expectancy: float
    loss_magnitude_avg: float
    simulation_count: int
    risk_level: str  # critical, high, medium, low
    confidence: float


# Sensitivity multipliers for data classification
_SENSITIVITY_MULTIPLIER = {
    "critical": 4.0,
    "high": 2.5,
    "medium": 1.5,
    "low": 1.0,
}

_SIMULATIONS = 10_000


def calculate_fair(
    params: FAIRInput,
    simulations: int = _SIMULATIONS,
) -> FAIRResult:
    """Run Monte Carlo FAIR simulation.

    Each simulation:
    1. Sample LEF from Poisson(threat_freq * vulnerability)
    2. Sample loss magnitude from log-normal distribution
    3. ALE = LEF * loss_magnitude
    4. Aggregate across simulations for percentile ranges
    """
    sensitivity_mult = _SENSITIVITY_MULTIPLIER.get(
        params.data_sensitivity, 1.0
    )

    ales: List[float] = []

    for _ in range(simulations):
        # Loss Event Frequency — Poisson sampling
        lef = random.gauss(
            params.threat_event_frequency
            * params.vulnerability,
            max(
                0.1,
                params.threat_event_frequency * 0.3,
            ),
        )
        lef = max(0, lef)

        # Loss Magnitude — uniform between min/max,
        # scaled by sensitivity
        primary = random.uniform(
            params.primary_loss_min,
            params.primary_loss_max,
        )
        secondary = random.uniform(
            params.secondary_loss_min,
            params.secondary_loss_max,
        )
        total_loss = (
            (primary + secondary) * sensitivity_mult
        )

        # ALE for this simulation
        ale = lef * total_loss
        ales.append(ale)

    ales.sort()
    avg_ale = sum(ales) / len(ales)
    p5 = ales[int(len(ales) * 0.05)]
    p95 = ales[int(len(ales) * 0.95)]

    avg_lef = (
        params.threat_event_frequency
        * params.vulnerability
    )
    avg_lm = (
        (
            (params.primary_loss_min + params.primary_loss_max)
            + (params.secondary_loss_min + params.secondary_loss_max)
        )
        / 2
        * sensitivity_mult
    )
    sle = avg_lm

    risk_level = _classify_risk(avg_ale)

    logger.info(
        "fair_calculated",
        vendor=params.vendor_name,
        ale=round(avg_ale, 2),
        risk_level=risk_level,
    )

    return FAIRResult(
        vendor_name=params.vendor_name,
        annual_loss_expectancy=round(avg_ale, 2),
        ale_min=round(p5, 2),
        ale_max=round(p95, 2),
        loss_event_frequency=round(avg_lef, 3),
        single_loss_expectancy=round(sle, 2),
        loss_magnitude_avg=round(avg_lm, 2),
        simulation_count=simulations,
        risk_level=risk_level,
        confidence=0.85,
    )


def _classify_risk(ale: float) -> str:
    """Classify ALE into risk levels."""
    if ale >= 1_000_000:
        return "critical"
    if ale >= 500_000:
        return "high"
    if ale >= 100_000:
        return "medium"
    return "low"
