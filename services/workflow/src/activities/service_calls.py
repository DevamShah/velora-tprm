"""Temporal activities that call other Velora TPRM microservices via HTTP.

Each activity is a thin wrapper around an ``httpx`` call to the relevant
service.  Temporal handles retries; activities raise on non-2xx responses
so the retry policy kicks in automatically.
"""

from __future__ import annotations

import os
from typing import Any

import httpx
from temporalio import activity

# ---------------------------------------------------------------------------
# Service base URLs — resolved from env vars with in-cluster defaults
# ---------------------------------------------------------------------------

VENDOR_SERVICE_URL = os.getenv("VENDOR_SERVICE_URL", "http://vendor-service:8000")
ASSESSMENT_ENGINE_URL = os.getenv("ASSESSMENT_ENGINE_URL", "http://assessment-engine:8000")
SCORING_ENGINE_URL = os.getenv("SCORING_ENGINE_URL", "http://scoring-engine:8000")
EVIDENCE_SERVICE_URL = os.getenv("EVIDENCE_SERVICE_URL", "http://evidence-service:8000")
FINDING_SERVICE_URL = os.getenv("FINDING_SERVICE_URL", "http://finding-service:8000")
COMMUNICATION_HUB_URL = os.getenv("COMMUNICATION_HUB_URL", "http://communication-hub:8000")
AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://ai-service:8000")

# Shared timeout for HTTP calls (seconds)
HTTP_TIMEOUT = 60.0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _post(url: str, payload: dict[str, Any]) -> dict[str, Any]:
    """POST JSON to a service and return the parsed response.

    Raises ``httpx.HTTPStatusError`` on non-2xx so Temporal retries.
    """
    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        resp = await client.post(url, json=payload)
        resp.raise_for_status()
        return resp.json()


async def _get(url: str) -> dict[str, Any]:
    """GET from a service and return the parsed response."""
    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.json()


# ---------------------------------------------------------------------------
# Vendor activities
# ---------------------------------------------------------------------------


@activity.defn(name="create_vendor")
async def create_vendor(data: dict[str, Any]) -> dict[str, Any]:
    """Create a vendor record via the vendor-service."""
    activity.logger.info("activity_create_vendor", extra={"name": data.get("name")})
    return await _post(f"{VENDOR_SERVICE_URL}/api/v1/vendors", data)


@activity.defn(name="enrich_vendor")
async def enrich_vendor(data: dict[str, Any]) -> dict[str, Any]:
    """Trigger vendor enrichment (external data lookups)."""
    vendor_id = data["vendor_id"]
    activity.logger.info("activity_enrich_vendor", extra={"vendor_id": vendor_id})
    return await _post(
        f"{VENDOR_SERVICE_URL}/api/v1/vendors/{vendor_id}/enrich", {}
    )


@activity.defn(name="calculate_tier")
async def calculate_tier(data: dict[str, Any]) -> dict[str, Any]:
    """Calculate risk tier for a vendor via the scoring engine."""
    vendor_id = data["vendor_id"]
    activity.logger.info("activity_calculate_tier", extra={"vendor_id": vendor_id})
    return await _post(
        f"{SCORING_ENGINE_URL}/api/v1/scoring/calculate/{vendor_id}", {}
    )


# ---------------------------------------------------------------------------
# Assessment activities
# ---------------------------------------------------------------------------


@activity.defn(name="create_assessment")
async def create_assessment(data: dict[str, Any]) -> dict[str, Any]:
    """Create an assessment from a template via the assessment engine."""
    activity.logger.info(
        "activity_create_assessment",
        extra={"vendor_id": data.get("vendor_id")},
    )
    return await _post(f"{ASSESSMENT_ENGINE_URL}/api/v1/assessments", data)


@activity.defn(name="distribute_assessment")
async def distribute_assessment(data: dict[str, Any]) -> dict[str, Any]:
    """Distribute an assessment to a vendor."""
    assessment_id = data["assessment_id"]
    activity.logger.info(
        "activity_distribute_assessment",
        extra={"assessment_id": assessment_id},
    )
    return await _post(
        f"{ASSESSMENT_ENGINE_URL}/api/v1/assessments/{assessment_id}/distribute",
        {},
    )


@activity.defn(name="score_assessment")
async def score_assessment(data: dict[str, Any]) -> dict[str, Any]:
    """Score a submitted assessment via the scoring engine."""
    vendor_id = data.get("vendor_id", "")
    assessment_id = data.get("assessment_id", "")
    activity.logger.info(
        "activity_score_assessment",
        extra={"assessment_id": assessment_id, "vendor_id": vendor_id},
    )
    return await _post(
        f"{SCORING_ENGINE_URL}/api/v1/scoring/calculate/{vendor_id}",
        {"assessment_id": assessment_id},
    )


# ---------------------------------------------------------------------------
# Communication activities
# ---------------------------------------------------------------------------


@activity.defn(name="send_notification")
async def send_notification(data: dict[str, Any]) -> dict[str, Any]:
    """Send a notification via the communication hub."""
    activity.logger.info(
        "activity_send_notification",
        extra={"type": data.get("type")},
    )
    return await _post(
        f"{COMMUNICATION_HUB_URL}/api/v1/communications/send", data
    )


@activity.defn(name="send_reminder")
async def send_reminder(data: dict[str, Any]) -> dict[str, Any]:
    """Send a reminder notification via the communication hub."""
    activity.logger.info(
        "activity_send_reminder",
        extra={
            "assessment_id": data.get("assessment_id"),
            "finding_id": data.get("finding_id"),
            "day": data.get("day"),
        },
    )
    payload = {
        "type": data.get("type", "assessment_reminder"),
        **data,
    }
    return await _post(
        f"{COMMUNICATION_HUB_URL}/api/v1/communications/send", payload
    )


@activity.defn(name="escalate_overdue")
async def escalate_overdue(data: dict[str, Any]) -> dict[str, Any]:
    """Escalate an overdue assessment or finding."""
    activity.logger.info(
        "activity_escalate_overdue",
        extra={
            "assessment_id": data.get("assessment_id"),
            "finding_id": data.get("finding_id"),
        },
    )
    payload = {
        "type": "overdue_escalation",
        **data,
    }
    return await _post(
        f"{COMMUNICATION_HUB_URL}/api/v1/communications/send", payload
    )


# ---------------------------------------------------------------------------
# Evidence activities
# ---------------------------------------------------------------------------


@activity.defn(name="register_evidence")
async def register_evidence(data: dict[str, Any]) -> dict[str, Any]:
    """Register an evidence upload in the evidence service."""
    activity.logger.info(
        "activity_register_evidence",
        extra={"evidence_id": data.get("evidence_id")},
    )
    return await _post(f"{EVIDENCE_SERVICE_URL}/api/v1/evidence", data)


@activity.defn(name="classify_document")
async def classify_document(data: dict[str, Any]) -> dict[str, Any]:
    """Classify a document type using the AI service."""
    activity.logger.info(
        "activity_classify_document",
        extra={"evidence_id": data.get("evidence_id")},
    )
    return await _post(f"{AI_SERVICE_URL}/api/v1/ai/classify-document", data)


@activity.defn(name="parse_evidence_document")
async def parse_evidence_document(data: dict[str, Any]) -> dict[str, Any]:
    """Parse and extract structured data from evidence document via AI."""
    activity.logger.info(
        "activity_parse_evidence",
        extra={
            "evidence_id": data.get("evidence_id"),
            "document_type": data.get("document_type"),
        },
    )
    return await _post(f"{AI_SERVICE_URL}/api/v1/ai/parse-evidence", data)


@activity.defn(name="map_evidence_to_controls")
async def map_evidence_to_controls(data: dict[str, Any]) -> dict[str, Any]:
    """Map extracted evidence to framework controls."""
    activity.logger.info(
        "activity_map_evidence_to_controls",
        extra={"evidence_id": data.get("evidence_id")},
    )
    return await _post(
        f"{EVIDENCE_SERVICE_URL}/api/v1/evidence/{data['evidence_id']}/map-controls",
        data,
    )


@activity.defn(name="finalise_evidence")
async def finalise_evidence(data: dict[str, Any]) -> dict[str, Any]:
    """Finalise evidence record with review outcome."""
    evidence_id = data["evidence_id"]
    activity.logger.info(
        "activity_finalise_evidence",
        extra={
            "evidence_id": evidence_id,
            "decision": data.get("review_decision"),
        },
    )
    return await _post(
        f"{EVIDENCE_SERVICE_URL}/api/v1/evidence/{evidence_id}/finalise",
        data,
    )


# ---------------------------------------------------------------------------
# Finding / Remediation activities
# ---------------------------------------------------------------------------


@activity.defn(name="create_remediation_plan")
async def create_remediation_plan(data: dict[str, Any]) -> dict[str, Any]:
    """Create a remediation plan for a finding."""
    finding_id = data["finding_id"]
    activity.logger.info(
        "activity_create_remediation_plan",
        extra={"finding_id": finding_id},
    )
    return await _post(
        f"{FINDING_SERVICE_URL}/api/v1/findings/{finding_id}/remediation",
        data,
    )


@activity.defn(name="verify_remediation_evidence")
async def verify_remediation_evidence(data: dict[str, Any]) -> dict[str, Any]:
    """Auto-verify remediation evidence against the finding requirements."""
    finding_id = data["finding_id"]
    activity.logger.info(
        "activity_verify_remediation",
        extra={"finding_id": finding_id},
    )
    return await _post(
        f"{FINDING_SERVICE_URL}/api/v1/findings/{finding_id}/verify",
        data,
    )


@activity.defn(name="close_finding")
async def close_finding(data: dict[str, Any]) -> dict[str, Any]:
    """Close a finding after successful remediation."""
    finding_id = data["finding_id"]
    activity.logger.info(
        "activity_close_finding",
        extra={"finding_id": finding_id},
    )
    return await _post(
        f"{FINDING_SERVICE_URL}/api/v1/findings/{finding_id}/close",
        data,
    )


@activity.defn(name="reopen_finding")
async def reopen_finding(data: dict[str, Any]) -> dict[str, Any]:
    """Re-open a finding after failed verification."""
    finding_id = data["finding_id"]
    activity.logger.info(
        "activity_reopen_finding",
        extra={
            "finding_id": finding_id,
            "cycle": data.get("cycle"),
        },
    )
    return await _post(
        f"{FINDING_SERVICE_URL}/api/v1/findings/{finding_id}/reopen",
        data,
    )
