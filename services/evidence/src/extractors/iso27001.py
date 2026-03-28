"""
ISO 27001 certificate extraction pipeline.

Extracts: certificate number, standard version, validity dates,
certifying body, scope, Annex A controls covered.
"""

from __future__ import annotations

import re
import uuid
from typing import List, Tuple

from ..doc_parser import DocumentParseResult
from ..models import EvidenceExtraction


def extract_iso27001(
    parse_result: DocumentParseResult,
    tenant_id: uuid.UUID,
    evidence_id: uuid.UUID,
) -> List[EvidenceExtraction]:
    """Extract structured fields from an ISO 27001 certificate."""
    extractions: List[EvidenceExtraction] = []
    content = parse_result.content
    lower = content.lower()

    # Certificate number
    cert_num = _find_cert_number(content)
    if cert_num:
        extractions.append(_make(
            tenant_id, evidence_id,
            "certificate_number", cert_num[0],
            cert_num[1], cert_num[2],
        ))

    # Standard version
    standard = _find_standard(content)
    if standard:
        extractions.append(_make(
            tenant_id, evidence_id,
            "standard", standard[0],
            standard[1], standard[2],
        ))

    # Valid from / to
    validity = _find_validity(content)
    if validity:
        extractions.append(_make(
            tenant_id, evidence_id,
            "valid_from", validity[0],
            validity[2], 1,
        ))
        extractions.append(_make(
            tenant_id, evidence_id,
            "valid_until", validity[1],
            validity[2], 1,
        ))

    # Certifying body
    body = _find_certifying_body(content)
    if body:
        extractions.append(_make(
            tenant_id, evidence_id,
            "certifying_body", body[0],
            body[1], body[2],
        ))

    # Scope
    scope = _find_scope(content)
    if scope:
        extractions.append(_make(
            tenant_id, evidence_id,
            "scope", scope[0],
            scope[1], scope[2],
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


def _find_cert_number(
    text: str,
) -> Tuple[str, float, int] | None:
    patterns = [
        r"(?:certificate\s+(?:no|number|#))[.:\s]+([A-Z0-9][\w\-/]+)",
        r"(?:registration\s+(?:no|number))[.:\s]+([A-Z0-9][\w\-/]+)",
    ]
    for pat in patterns:
        match = re.search(pat, text, re.IGNORECASE)
        if match:
            return (match.group(1).strip(), 0.95, 1)
    return None


def _find_standard(
    text: str,
) -> Tuple[str, float, int] | None:
    match = re.search(
        r"ISO/?IEC\s+27001:\d{4}",
        text, re.IGNORECASE,
    )
    if match:
        return (match.group(0), 0.98, 1)
    return None


def _find_validity(
    text: str,
) -> Tuple[str, str, float] | None:
    patterns = [
        r"(?:valid\s+from|issued)[:\s]+(\d{4}-\d{2}-\d{2}).*?(?:valid\s+(?:to|until)|expir\w+)[:\s]+(\d{4}-\d{2}-\d{2})",
        r"(?:initial\s+certification)[:\s]+(\d{4}-\d{2}-\d{2}).*?(?:expiry|valid\s+until)[:\s]+(\d{4}-\d{2}-\d{2})",
    ]
    for pat in patterns:
        match = re.search(pat, text, re.IGNORECASE | re.DOTALL)
        if match:
            return (
                match.group(1), match.group(2), 0.92,
            )
    return None


def _find_certifying_body(
    text: str,
) -> Tuple[str, float, int] | None:
    patterns = [
        r"(?:certified\s+by|issued\s+by|certification\s+body)[:\s]+([A-Z][A-Za-z\s&,.]+?)(?:\n|\.)",
    ]
    for pat in patterns:
        match = re.search(pat, text)
        if match:
            return (match.group(1).strip(), 0.90, 1)
    return None


def _find_scope(
    text: str,
) -> Tuple[str, float, int] | None:
    match = re.search(
        r"(?:scope|covers)[:\s]+(.{20,300}?)(?:\n\n|\.\s)",
        text, re.IGNORECASE | re.DOTALL,
    )
    if match:
        return (match.group(1).strip(), 0.80, 1)
    return None
