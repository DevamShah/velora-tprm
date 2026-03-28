"""
SOC 2 Type II report extraction pipeline.

Extracts: audit period, auditor, opinion type, scope, exceptions,
control statuses, trust service criteria coverage.
"""

from __future__ import annotations

import re
import uuid
from typing import List, Tuple

from ..doc_parser import DocumentParseResult
from ..models import EvidenceExtraction


def extract_soc2(
    parse_result: DocumentParseResult,
    tenant_id: uuid.UUID,
    evidence_id: uuid.UUID,
) -> List[EvidenceExtraction]:
    """Extract structured fields from a SOC 2 report."""
    extractions: List[EvidenceExtraction] = []
    content = parse_result.content.lower()
    full_content = parse_result.content

    # Audit period
    period = _find_audit_period(full_content)
    if period:
        extractions.append(_make(
            tenant_id, evidence_id,
            "audit_period", period[0],
            period[1], period[2],
        ))

    # Auditor / service organization
    auditor = _find_auditor(full_content)
    if auditor:
        extractions.append(_make(
            tenant_id, evidence_id,
            "auditor", auditor[0],
            auditor[1], auditor[2],
        ))

    # Opinion type
    opinion = _find_opinion(content, full_content)
    if opinion:
        extractions.append(_make(
            tenant_id, evidence_id,
            "opinion_type", opinion[0],
            opinion[1], opinion[2],
        ))

    # Scope
    scope = _find_scope(full_content)
    if scope:
        extractions.append(_make(
            tenant_id, evidence_id,
            "scope", scope[0],
            scope[1], scope[2],
        ))

    # Exceptions
    exceptions = _find_exceptions(content)
    extractions.append(_make(
        tenant_id, evidence_id,
        "exceptions_noted", exceptions[0],
        exceptions[1], exceptions[2],
    ))

    # Trust service criteria
    tsc = _find_trust_criteria(content)
    if tsc:
        extractions.append(_make(
            tenant_id, evidence_id,
            "trust_service_criteria", tsc[0],
            tsc[1], tsc[2],
        ))

    return extractions


def _make(
    tenant_id, evidence_id,
    name, value, confidence, page,
) -> EvidenceExtraction:
    return EvidenceExtraction(
        tenant_id=tenant_id,
        evidence_id=evidence_id,
        field_name=name,
        field_value=str(value),
        confidence=confidence,
        page_number=page,
    )


def _find_audit_period(
    text: str,
) -> Tuple[str, float, int] | None:
    """Find audit period dates."""
    patterns = [
        r"(?:period|from)\s+(\w+\s+\d{1,2},?\s+\d{4})\s+(?:to|through)\s+(\w+\s+\d{1,2},?\s+\d{4})",
        r"(\d{4}-\d{2}-\d{2})\s+(?:to|through)\s+(\d{4}-\d{2}-\d{2})",
    ]
    for pat in patterns:
        match = re.search(pat, text, re.IGNORECASE)
        if match:
            return (
                f"{match.group(1)} to {match.group(2)}",
                0.90, 1,
            )
    return None


def _find_auditor(
    text: str,
) -> Tuple[str, float, int] | None:
    """Find the auditing firm name."""
    patterns = [
        r"(?:independent\s+(?:service\s+)?auditor|audited\s+by|prepared\s+by)[:\s]+([A-Z][A-Za-z\s&,.]+(?:LLP|LLC|Inc|Corp))",
    ]
    for pat in patterns:
        match = re.search(pat, text)
        if match:
            return (match.group(1).strip(), 0.88, 1)
    return None


def _find_opinion(
    lower: str, full: str,
) -> Tuple[str, float, int] | None:
    """Determine opinion type."""
    if "unqualified" in lower or "unmodified" in lower:
        return ("Unqualified", 0.92, 2)
    if "qualified" in lower and "except for" in lower:
        return ("Qualified", 0.85, 2)
    if "adverse" in lower:
        return ("Adverse", 0.90, 2)
    if "disclaimer" in lower:
        return ("Disclaimer", 0.88, 2)
    return None


def _find_scope(
    text: str,
) -> Tuple[str, float, int] | None:
    """Extract scope description."""
    match = re.search(
        r"(?:scope|description\s+of\s+.*system)[:\s]+(.{20,200}?)(?:\.|$)",
        text, re.IGNORECASE,
    )
    if match:
        return (match.group(1).strip(), 0.82, 3)
    return None


def _find_exceptions(
    lower: str,
) -> Tuple[str, float, int]:
    """Check for exceptions noted."""
    if "no exceptions" in lower:
        return ("None", 0.90, -1)
    if "exception" in lower:
        return ("Exceptions noted", 0.75, -1)
    return ("Unknown", 0.50, -1)


def _find_trust_criteria(
    lower: str,
) -> Tuple[str, float, int] | None:
    """Find which TSC categories are covered."""
    categories = []
    for cat in [
        "security", "availability",
        "processing integrity",
        "confidentiality", "privacy",
    ]:
        if cat in lower:
            categories.append(cat.title())
    if categories:
        return (", ".join(categories), 0.85, -1)
    return None
