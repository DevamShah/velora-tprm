"""
Evidence-to-control mapping engine.

Uses extracted evidence fields + Claude AI to map evidence to
framework control clauses with coverage type and confidence scoring.
"""

from __future__ import annotations

import os
import uuid
from typing import Any, Dict, List, Optional, Tuple

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
)

from velora_common.logging import get_logger
from .models import EvidenceControlMapping, EvidenceExtraction

logger = get_logger(__name__)

_FRAMEWORK_SERVICE_URL = os.environ.get(
    "FRAMEWORK_SERVICE_URL",
    "http://framework-service:8000",
)
_AI_SERVICE_URL = os.environ.get(
    "AI_SERVICE_URL",
    "http://ai-service:8000",
)
_HTTP_TIMEOUT = httpx.Timeout(30.0, connect=5.0)


MAPPING_SYSTEM_PROMPT = """\
You are a compliance control mapping specialist.
Given evidence extractions and a list of framework control clauses,
determine which clauses each piece of evidence supports.

For each mapping, provide:
- clause_id: the UUID of the matched clause
- coverage_type: "full" (evidence fully satisfies), "partial" (partially satisfies), or "supportive" (provides context)
- confidence: 0.0 to 1.0

Output ONLY a JSON array:
[{"clause_id": "<uuid>", "coverage_type": "full|partial|supportive", "confidence": 0.85}]

Only include clauses with confidence >= 0.5. Be conservative.
"""


class MappingEngine:
    """Maps evidence extractions to framework controls."""

    def __init__(
        self,
        tenant_id: uuid.UUID,
        framework_id: uuid.UUID,
    ) -> None:
        self._tenant_id = tenant_id
        self._framework_id = framework_id

    async def map_evidence(
        self,
        evidence_id: uuid.UUID,
        extractions: List[EvidenceExtraction],
    ) -> List[EvidenceControlMapping]:
        """Map evidence extractions to framework clauses."""
        if not extractions:
            return []

        # Fetch framework clauses via HTTP
        clauses = await self._fetch_clauses()
        if not clauses:
            logger.warning(
                "no_clauses_for_mapping",
                framework_id=str(self._framework_id),
            )
            return []

        # Build extraction summary for AI
        extraction_text = self._format_extractions(
            extractions
        )
        clause_text = self._format_clauses(clauses)

        # Use keyword matching as primary method
        # (AI enhancement planned for future sprint)
        mappings = self._keyword_match(
            extractions, clauses,
            self._tenant_id, evidence_id,
        )

        logger.info(
            "evidence_mapped",
            evidence_id=str(evidence_id),
            mappings_found=len(mappings),
        )
        return mappings

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        reraise=True,
    )
    async def _fetch_clauses(
        self,
    ) -> List[Dict[str, Any]]:
        """Fetch clauses from framework service via HTTP."""
        url = (
            f"{_FRAMEWORK_SERVICE_URL}/api/v1"
            f"/internal/frameworks"
            f"/{self._framework_id}/clauses/bulk"
        )
        async with httpx.AsyncClient(
            timeout=_HTTP_TIMEOUT
        ) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.json()

    @staticmethod
    def _format_extractions(
        extractions: List[EvidenceExtraction],
    ) -> str:
        """Format extractions for AI prompt."""
        lines = []
        for e in extractions:
            lines.append(
                f"- {e.field_name}: {e.field_value} "
                f"(confidence: {e.confidence:.0%})"
            )
        return "\n".join(lines)

    @staticmethod
    def _format_clauses(
        clauses: List[Dict[str, Any]],
    ) -> str:
        """Format clauses for AI prompt."""
        lines = []
        for c in clauses[:100]:  # Cap at 100 clauses
            lines.append(
                f"[{c['id']}] {c.get('clause_ref', '')}: "
                f"{c.get('title', '')} — "
                f"{c.get('description', '')[:200]}"
            )
        return "\n".join(lines)

    @staticmethod
    def _keyword_match(
        extractions: List[EvidenceExtraction],
        clauses: List[Dict[str, Any]],
        tenant_id: uuid.UUID,
        evidence_id: uuid.UUID,
    ) -> List[EvidenceControlMapping]:
        """Simple keyword matching for control mapping."""
        # Build keyword index from extractions
        evidence_keywords = set()
        for e in extractions:
            words = (
                e.field_name.lower().split("_")
                + e.field_value.lower().split()
            )
            evidence_keywords.update(
                w for w in words if len(w) > 3
            )

        mappings = []
        for clause in clauses:
            clause_text = (
                f"{clause.get('title', '')} "
                f"{clause.get('description', '')}"
            ).lower()

            # Count keyword matches
            matches = sum(
                1 for kw in evidence_keywords
                if kw in clause_text
            )

            if matches < 2:
                continue

            # Calculate confidence from match density
            total_words = len(clause_text.split())
            if total_words == 0:
                continue
            confidence = min(
                0.95,
                0.4 + (matches / total_words) * 2,
            )
            if confidence < 0.5:
                continue

            coverage = (
                "full" if confidence >= 0.8
                else "partial" if confidence >= 0.6
                else "supportive"
            )

            mappings.append(EvidenceControlMapping(
                tenant_id=tenant_id,
                evidence_id=evidence_id,
                clause_id=uuid.UUID(clause["id"]),
                coverage_type=coverage,
                confidence=round(confidence, 2),
                verified=False,
            ))

        return mappings
