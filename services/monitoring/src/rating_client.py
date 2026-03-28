"""
External security rating API client (SecurityScorecard).

Fetches vendor security scores and signals for continuous monitoring.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
)

from velora_common.logging import get_logger

logger = get_logger(__name__)

_BASE_URL = "https://api.securityscorecard.io"
_TIMEOUT = httpx.Timeout(30.0, connect=5.0)


@dataclass
class VendorRating:
    """Normalized vendor security rating."""

    domain: str
    overall_score: float  # 0-100
    grade: str  # A-F
    factors: Dict[str, float]
    last_updated: str
    signal_count: int


class SecurityScorecardClient:
    """Async client for SecurityScorecard API."""

    def __init__(
        self, api_key: Optional[str] = None
    ) -> None:
        self._api_key = api_key or os.environ.get(
            "SECURITYSCORECARD_API_KEY", ""
        )
        if not self._api_key:
            logger.warning(
                "securityscorecard_not_configured",
            )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        reraise=True,
    )
    async def get_company_score(
        self, domain: str
    ) -> Optional[VendorRating]:
        """Fetch overall security score for a company."""
        if not self._api_key:
            return None

        async with httpx.AsyncClient(
            timeout=_TIMEOUT
        ) as client:
            resp = await client.get(
                f"{_BASE_URL}/companies/{domain}",
                headers={
                    "Authorization": f"Token {self._api_key}",
                    "Accept": "application/json",
                },
            )
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            data = resp.json()

        score = data.get("score", 0)
        grade = data.get("grade", "N/A")
        factors = {}
        for factor in data.get("factor_grades", []):
            factors[factor.get("name", "")] = factor.get(
                "score", 0
            )

        return VendorRating(
            domain=domain,
            overall_score=score,
            grade=grade,
            factors=factors,
            last_updated=data.get(
                "last_score_date", ""
            ),
            signal_count=data.get(
                "total_signals", 0
            ),
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        reraise=True,
    )
    async def get_company_signals(
        self,
        domain: str,
        severity: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Fetch recent signals/findings for a company."""
        if not self._api_key:
            return []

        params: Dict[str, str] = {}
        if severity:
            params["severity"] = severity

        async with httpx.AsyncClient(
            timeout=_TIMEOUT
        ) as client:
            resp = await client.get(
                f"{_BASE_URL}/companies/{domain}"
                f"/issues",
                headers={
                    "Authorization": f"Token {self._api_key}",
                    "Accept": "application/json",
                },
                params=params,
            )
            if resp.status_code == 404:
                return []
            resp.raise_for_status()
            data = resp.json()

        return data.get("entries", [])


def normalize_score(
    score: float, source: str = "securityscorecard"
) -> float:
    """Normalize external rating to 0-100 scale."""
    if source == "securityscorecard":
        return max(0.0, min(100.0, score))
    if source == "bitsight":
        # BitSight: 250-900 → 0-100
        return max(
            0.0,
            min(100.0, (score - 250) / 650 * 100),
        )
    return score
