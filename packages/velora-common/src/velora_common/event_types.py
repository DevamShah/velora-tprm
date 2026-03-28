"""Canonical event type definitions for inter-service communication.

All event types and stream names are defined here as constants so that
publishers and consumers share a single source of truth.
"""

# ---------------------------------------------------------------------------
# Vendor events
# ---------------------------------------------------------------------------
VENDOR_CREATED = "vendor.created"
VENDOR_UPDATED = "vendor.updated"
VENDOR_DELETED = "vendor.deleted"
VENDOR_ENRICHED = "vendor.enriched"
VENDOR_TIER_CHANGED = "vendor.tier_changed"

# ---------------------------------------------------------------------------
# Assessment events
# ---------------------------------------------------------------------------
ASSESSMENT_CREATED = "assessment.created"
ASSESSMENT_DISTRIBUTED = "assessment.distributed"
ASSESSMENT_SUBMITTED = "assessment.submitted"
ASSESSMENT_COMPLETED = "assessment.completed"
ASSESSMENT_CANCELLED = "assessment.cancelled"

# ---------------------------------------------------------------------------
# Evidence events
# ---------------------------------------------------------------------------
EVIDENCE_UPLOADED = "evidence.uploaded"
EVIDENCE_PARSED = "evidence.parsed"
EVIDENCE_MAPPED = "evidence.mapped"

# ---------------------------------------------------------------------------
# Score events
# ---------------------------------------------------------------------------
SCORE_CALCULATED = "score.calculated"
SCORE_CHANGED = "score.changed"

# ---------------------------------------------------------------------------
# Alert events
# ---------------------------------------------------------------------------
ALERT_CREATED = "alert.created"
ALERT_RESOLVED = "alert.resolved"

# ---------------------------------------------------------------------------
# Finding events
# ---------------------------------------------------------------------------
FINDING_CREATED = "finding.created"
FINDING_CLOSED = "finding.closed"

# ---------------------------------------------------------------------------
# Config events
# ---------------------------------------------------------------------------
CONFIG_UPDATED = "config.updated"

# ---------------------------------------------------------------------------
# Stream names — one stream per aggregate / bounded context
# ---------------------------------------------------------------------------
STREAM_VENDOR = "events:vendor"
STREAM_ASSESSMENT = "events:assessment"
STREAM_EVIDENCE = "events:evidence"
STREAM_SCORE = "events:score"
STREAM_ALERT = "events:alert"
STREAM_FINDING = "events:finding"
STREAM_CONFIG = "events:config"

# ---------------------------------------------------------------------------
# Lookup: event type → stream name
# ---------------------------------------------------------------------------
EVENT_STREAM_MAP: dict[str, str] = {
    # Vendor
    VENDOR_CREATED: STREAM_VENDOR,
    VENDOR_UPDATED: STREAM_VENDOR,
    VENDOR_DELETED: STREAM_VENDOR,
    VENDOR_ENRICHED: STREAM_VENDOR,
    VENDOR_TIER_CHANGED: STREAM_VENDOR,
    # Assessment
    ASSESSMENT_CREATED: STREAM_ASSESSMENT,
    ASSESSMENT_DISTRIBUTED: STREAM_ASSESSMENT,
    ASSESSMENT_SUBMITTED: STREAM_ASSESSMENT,
    ASSESSMENT_COMPLETED: STREAM_ASSESSMENT,
    ASSESSMENT_CANCELLED: STREAM_ASSESSMENT,
    # Evidence
    EVIDENCE_UPLOADED: STREAM_EVIDENCE,
    EVIDENCE_PARSED: STREAM_EVIDENCE,
    EVIDENCE_MAPPED: STREAM_EVIDENCE,
    # Score
    SCORE_CALCULATED: STREAM_SCORE,
    SCORE_CHANGED: STREAM_SCORE,
    # Alert
    ALERT_CREATED: STREAM_ALERT,
    ALERT_RESOLVED: STREAM_ALERT,
    # Finding
    FINDING_CREATED: STREAM_FINDING,
    FINDING_CLOSED: STREAM_FINDING,
    # Config
    CONFIG_UPDATED: STREAM_CONFIG,
}
