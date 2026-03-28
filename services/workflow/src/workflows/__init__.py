"""Temporal workflow definitions for Velora TPRM.

Each workflow orchestrates a multi-step business process with durable
execution, automatic retries, and long-running timer support.
"""

from .assessment_lifecycle import AssessmentLifecycleWorkflow
from .evidence_processing import EvidenceProcessingWorkflow
from .remediation_tracking import RemediationTrackingWorkflow
from .vendor_onboarding import VendorOnboardingWorkflow

ALL_WORKFLOWS = [
    VendorOnboardingWorkflow,
    AssessmentLifecycleWorkflow,
    EvidenceProcessingWorkflow,
    RemediationTrackingWorkflow,
]

__all__ = [
    "VendorOnboardingWorkflow",
    "AssessmentLifecycleWorkflow",
    "EvidenceProcessingWorkflow",
    "RemediationTrackingWorkflow",
    "ALL_WORKFLOWS",
]
