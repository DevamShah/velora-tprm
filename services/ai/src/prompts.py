"""
TPRM-domain prompt templates for Claude-powered questionnaire auto-fill.

Confidence scoring rules:
  0.9+ — answer backed by direct evidence (SOC 2, ISO cert, pen test)
  0.6-0.8 — answer inferred from public info (trust center, website)
  0.3-0.5 — answer based on general inference only
  < 0.3 — insufficient context, should not auto-fill
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

_MAX_VENDOR_FIELD_LEN = 500
_MAX_EVIDENCE_SUMMARY_LEN = 5000
_MAX_QUESTION_LEN = 2000

QUESTIONNAIRE_SYSTEM_PROMPT = """\
You are a Third-Party Risk Management (TPRM) analyst AI assistant.
Your task is to answer vendor security questionnaire questions based on
available vendor context and evidence.

RULES:
1. Answer ONLY based on the provided vendor context and evidence.
2. If evidence directly supports an answer, confidence should be 0.85-0.95.
3. If only public information is available, confidence should be 0.6-0.75.
4. If you must infer without evidence, confidence should be 0.3-0.5.
5. Never fabricate certifications, audit results, or specific dates.
6. If you truly cannot answer, set confidence to 0.1 and say so.
7. Cite specific evidence documents by name when available.

OUTPUT FORMAT — respond with ONLY a JSON array, no markdown:
[
  {
    "question_id": "<uuid>",
    "answer": "<your answer text>",
    "confidence": <0.0 to 1.0>,
    "reasoning": "<brief explanation of how you arrived at this answer>",
    "evidence_citations": ["<document name or source>"]
  }
]
"""

_BATCH_SIZE = 10


def _sanitize(text: str, max_len: int) -> str:
    """Sanitize user-supplied text for prompt injection defense."""
    if not isinstance(text, str):
        text = str(text)
    # Truncate to max length
    text = text[:max_len]
    # Strip control characters (keep newlines, tabs)
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    return text


def build_autofill_prompt(
    *,
    vendor_context: Dict[str, Any],
    evidence_context: Optional[List[Dict[str, Any]]] = None,
    questions: List[Dict[str, Any]],
) -> str:
    """Build the user message for questionnaire auto-fill.

    All user-supplied data is wrapped in XML delimiter tags and
    length-capped to mitigate prompt injection.
    """
    parts: List[str] = []

    # Vendor profile section — wrapped in delimiters
    parts.append("<vendor_profile>")
    for key in (
        "name", "domain", "tier", "data_classification",
        "business_criticality", "certifications", "industry",
    ):
        val = vendor_context.get(key)
        if val is not None:
            safe_val = _sanitize(
                str(val), _MAX_VENDOR_FIELD_LEN
            )
            parts.append(f"- {key}: {safe_val}")
    parts.append("</vendor_profile>")

    # Evidence section — wrapped in delimiters
    if evidence_context:
        parts.append("\n<evidence_documents>")
        for doc in evidence_context:
            doc_type = _sanitize(
                doc.get("document_type", "Unknown"),
                _MAX_VENDOR_FIELD_LEN,
            )
            summary = _sanitize(
                doc.get("extraction_summary", ""),
                _MAX_EVIDENCE_SUMMARY_LEN,
            )
            parts.append(f"\n<document type=\"{doc_type}\">")
            if summary:
                parts.append(summary)
            parts.append("</document>")
        parts.append("</evidence_documents>")

    # Questions section — wrapped in delimiters
    parts.append("\n<questions>")
    for q in questions:
        qid = q.get("question_id", "unknown")
        text = _sanitize(
            q.get("question_text", ""),
            _MAX_QUESTION_LEN,
        )
        parts.append(f"\n<question id=\"{qid}\">{text}</question>")
    parts.append("</questions>")

    return "\n".join(parts)


def batch_questions(
    questions: List[Dict[str, Any]],
) -> List[List[Dict[str, Any]]]:
    """Split questions into batches for API efficiency."""
    return [
        questions[i : i + _BATCH_SIZE]
        for i in range(0, len(questions), _BATCH_SIZE)
    ]


def parse_autofill_response(
    raw_content: str,
) -> List[Dict[str, Any]]:
    """Parse Claude's JSON response into structured answers.

    Handles both clean JSON and JSON wrapped in markdown code blocks.
    """
    text = raw_content.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove first and last lines (code block markers)
        lines = [
            ln for ln in lines
            if not ln.strip().startswith("```")
        ]
        text = "\n".join(lines).strip()

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return []

    if not isinstance(parsed, list):
        parsed = [parsed] if isinstance(parsed, dict) else []

    # Validate each item has required fields
    validated = []
    required_keys = {"question_id", "answer", "confidence"}
    for item in parsed:
        if not isinstance(item, dict):
            continue
        if not required_keys.issubset(item.keys()):
            continue
        validated.append(item)

    return validated
