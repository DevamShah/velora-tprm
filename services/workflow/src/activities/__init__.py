"""Temporal activity implementations for Velora TPRM workflows.

Activities are the side-effect-bearing units — they make HTTP calls
to other microservices and are automatically retried by Temporal.
"""

from .service_calls import (
    calculate_tier,
    classify_document,
    close_finding,
    create_assessment,
    create_remediation_plan,
    create_vendor,
    distribute_assessment,
    enrich_vendor,
    escalate_overdue,
    finalise_evidence,
    map_evidence_to_controls,
    parse_evidence_document,
    register_evidence,
    reopen_finding,
    score_assessment,
    send_notification,
    send_reminder,
    verify_remediation_evidence,
)

ALL_ACTIVITIES = [
    create_vendor,
    enrich_vendor,
    calculate_tier,
    create_assessment,
    distribute_assessment,
    score_assessment,
    send_notification,
    send_reminder,
    escalate_overdue,
    register_evidence,
    classify_document,
    parse_evidence_document,
    map_evidence_to_controls,
    finalise_evidence,
    create_remediation_plan,
    verify_remediation_evidence,
    close_finding,
    reopen_finding,
]

__all__ = [
    "ALL_ACTIVITIES",
    "create_vendor",
    "enrich_vendor",
    "calculate_tier",
    "create_assessment",
    "distribute_assessment",
    "score_assessment",
    "send_notification",
    "send_reminder",
    "escalate_overdue",
    "register_evidence",
    "classify_document",
    "parse_evidence_document",
    "map_evidence_to_controls",
    "finalise_evidence",
    "create_remediation_plan",
    "verify_remediation_evidence",
    "close_finding",
    "reopen_finding",
]
