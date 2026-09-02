"""
Combined seed data for Sprint 6-8 modules.

Seeds: notifications, email templates, findings, audit logs.
Idempotent: safe to run multiple times.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

# Import all models to resolve FK references
import app.modules.assessments.models
import app.modules.evidence.models
import app.modules.frameworks.models
import app.modules.monitoring.models
import app.modules.vendors.models  # noqa: F401
from app.core.logging import get_logger
from app.core.seed import DEMO_TENANT_ID
from app.modules.admin.models import AuditLog
from app.modules.auth.models import User
from app.modules.communications.models import (
    EmailTemplate,
    Notification,
)
from app.modules.findings.models import (
    Finding,
)
from app.modules.vendors.models import Vendor

logger = get_logger(__name__)


async def _get_admin_user_id(
    session: AsyncSession,
    tenant_id: uuid.UUID,
) -> uuid.UUID:
    """Fetch first admin user ID."""
    result = await session.execute(
        select(User.id).where(User.tenant_id == tenant_id).limit(1)
    )
    row = result.first()
    return row[0] if row else uuid.uuid4()


async def _get_vendor_ids(
    session: AsyncSession,
    tenant_id: uuid.UUID,
) -> list[uuid.UUID]:
    """Fetch up to 5 seeded vendor IDs."""
    result = await session.execute(
        select(Vendor.id)
        .where(
            Vendor.tenant_id == tenant_id,
            Vendor.deleted_at.is_(None),
        )
        .limit(5)
    )
    return [row[0] for row in result.all()]


async def _seed_notifications(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
) -> int:
    """Seed 5 demo notifications for admin user."""
    count_result = await session.execute(
        select(func.count())
        .select_from(Notification)
        .where(Notification.tenant_id == tenant_id)
    )
    if (count_result.scalar() or 0) > 0:
        return 0

    now = datetime.now(UTC)
    notifs = [
        {
            "title": "Critical finding detected",
            "message": (
                "A critical finding was identified "
                "for vendor AWS during assessment."
            ),
            "channel": "in_app",
            "entity_type": "finding",
        },
        {
            "title": "Assessment overdue",
            "message": (
                "Salesforce annual assessment is 7 days past due date."
            ),
            "channel": "in_app",
            "entity_type": "assessment",
        },
        {
            "title": "New vendor onboarded",
            "message": (
                "Workday has been added to the vendor registry and classified."
            ),
            "channel": "in_app",
            "entity_type": "vendor",
        },
        {
            "title": "Alert: Rating downgrade",
            "message": (
                "External security rating for Workday dropped from A to B-."
            ),
            "channel": "email",
            "entity_type": "alert",
        },
        {
            "title": "Weekly risk digest ready",
            "message": (
                "Your weekly TPRM risk summary report is ready for review."
            ),
            "channel": "in_app",
            "entity_type": "report",
        },
    ]

    for i, data in enumerate(notifs):
        notif = Notification(
            tenant_id=tenant_id,
            user_id=user_id,
            title=data["title"],
            message=data["message"],
            channel=data["channel"],
            entity_type=data["entity_type"],
            read=i >= 3,
        )
        notif.created_at = now - timedelta(hours=i * 6)
        if i >= 3:
            notif.read_at = now - timedelta(hours=i * 3)
        session.add(notif)

    await session.flush()
    return len(notifs)


async def _seed_email_templates(
    session: AsyncSession,
    tenant_id: uuid.UUID,
) -> int:
    """Seed 3 system email templates."""
    count_result = await session.execute(
        select(func.count())
        .select_from(EmailTemplate)
        .where(EmailTemplate.tenant_id == tenant_id)
    )
    if (count_result.scalar() or 0) > 0:
        return 0

    templates = [
        EmailTemplate(
            tenant_id=tenant_id,
            name="assessment_reminder",
            subject_template=(
                "Reminder: {{vendor_name}} assessment due {{due_date}}"
            ),
            body_template=(
                "Hello {{recipient_name}},\n\n"
                "This is a reminder that the assessment "
                "for {{vendor_name}} is due on "
                "{{due_date}}.\n\n"
                "Please complete the assessment at your "
                "earliest convenience.\n\n"
                "Best regards,\nVelora TPRM"
            ),
            variables={
                "vendor_name": "string",
                "due_date": "date",
                "recipient_name": "string",
            },
            is_system=True,
        ),
        EmailTemplate(
            tenant_id=tenant_id,
            name="finding_notification",
            subject_template=("Finding: {{severity}} - {{title}}"),
            body_template=(
                "Hello {{recipient_name}},\n\n"
                "A new {{severity}} finding has been "
                "identified for {{vendor_name}}:\n\n"
                "Title: {{title}}\n"
                "Description: {{description}}\n"
                "SLA Due: {{sla_date}}\n\n"
                "Please review and take appropriate "
                "action.\n\nBest regards,\nVelora TPRM"
            ),
            variables={
                "severity": "string",
                "title": "string",
                "vendor_name": "string",
                "description": "string",
                "sla_date": "date",
                "recipient_name": "string",
            },
            is_system=True,
        ),
        EmailTemplate(
            tenant_id=tenant_id,
            name="alert_notification",
            subject_template=("Alert [{{priority}}]: {{title}}"),
            body_template=(
                "Hello {{recipient_name}},\n\n"
                "A {{priority}} alert has been raised "
                "for {{vendor_name}}:\n\n"
                "{{description}}\n\n"
                "Please investigate and respond "
                "accordingly.\n\nBest regards,\n"
                "Velora TPRM"
            ),
            variables={
                "priority": "string",
                "title": "string",
                "vendor_name": "string",
                "description": "string",
                "recipient_name": "string",
            },
            is_system=True,
        ),
    ]

    for t in templates:
        session.add(t)
    await session.flush()
    return len(templates)


async def _seed_findings(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    vendor_ids: list[uuid.UUID],
) -> int:
    """Seed 8 demo findings across vendors."""
    count_result = await session.execute(
        select(func.count())
        .select_from(Finding)
        .where(Finding.tenant_id == tenant_id)
    )
    if (count_result.scalar() or 0) > 0:
        return 0

    if len(vendor_ids) < 3:
        return 0

    now = datetime.now(UTC)
    findings_data = [
        {
            "vendor_id": vendor_ids[0],
            "title": "Missing data encryption at rest",
            "description": (
                "Vendor does not encrypt PII data "
                "at rest in their production database."
            ),
            "severity": "critical",
            "status": "open",
            "affected_controls": ["SC-28", "SC-13"],
            "sla_days": 14,
        },
        {
            "vendor_id": vendor_ids[0],
            "title": "Outdated TLS version",
            "description": (
                "API endpoints support TLS 1.0 and 1.1 which are deprecated."
            ),
            "severity": "high",
            "status": "remediation_in_progress",
            "affected_controls": ["SC-8"],
            "sla_days": 30,
        },
        {
            "vendor_id": vendor_ids[1],
            "title": "No MFA for admin access",
            "description": (
                "Administrative console lacks multi-factor authentication."
            ),
            "severity": "critical",
            "status": "open",
            "affected_controls": ["IA-2", "IA-5"],
            "sla_days": 7,
        },
        {
            "vendor_id": vendor_ids[1],
            "title": "Insufficient logging",
            "description": (
                "Audit logs do not capture all administrative actions."
            ),
            "severity": "medium",
            "status": "submitted_for_verification",
            "affected_controls": ["AU-2", "AU-3"],
            "sla_days": 45,
        },
        {
            "vendor_id": vendor_ids[2],
            "title": "Weak password policy",
            "description": (
                "Password policy allows passwords shorter than 12 characters."
            ),
            "severity": "high",
            "status": "remediation_in_progress",
            "affected_controls": ["IA-5"],
            "sla_days": 30,
        },
        {
            "vendor_id": vendor_ids[2],
            "title": "Missing incident response plan",
            "description": (
                "No documented incident response procedure for data breaches."
            ),
            "severity": "high",
            "status": "open",
            "affected_controls": ["IR-1", "IR-4"],
            "sla_days": 30,
        },
        {
            "vendor_id": vendor_ids[3 % len(vendor_ids)],
            "title": "Expired SSL certificate",
            "description": ("Production SSL certificate expired 2 weeks ago."),
            "severity": "low",
            "status": "verified_closed",
            "affected_controls": ["SC-8"],
            "sla_days": 0,
        },
        {
            "vendor_id": vendor_ids[4 % len(vendor_ids)],
            "title": "Unpatched CVE in dependency",
            "description": (
                "Known CVE-2025-1234 in a third-party library used by vendor."
            ),
            "severity": "info",
            "status": "risk_accepted",
            "affected_controls": ["SI-2"],
            "sla_days": 0,
        },
    ]

    for fd in findings_data:
        sla_days = fd.pop("sla_days")
        finding = Finding(
            tenant_id=tenant_id,
            vendor_id=fd["vendor_id"],
            title=fd["title"],
            description=fd["description"],
            severity=fd["severity"],
            status=fd["status"],
            affected_controls=fd.get("affected_controls"),
            remediation_guidance=("Implement recommended controls."),
            sla_due_date=(
                now + timedelta(days=sla_days) if sla_days > 0 else None
            ),
        )
        if fd["status"] in ("verified_closed", "risk_accepted"):
            finding.closed_at = now - timedelta(days=3)
        session.add(finding)

    await session.flush()
    return len(findings_data)


async def _seed_audit_logs(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
) -> int:
    """Seed 10 audit log entries."""
    count_result = await session.execute(
        select(func.count())
        .select_from(AuditLog)
        .where(AuditLog.tenant_id == tenant_id)
    )
    if (count_result.scalar() or 0) > 0:
        return 0

    now = datetime.now(UTC)
    entries = [
        {
            "action": "user.login",
            "entity_type": "user",
            "details": {"method": "password"},
        },
        {
            "action": "vendor.create",
            "entity_type": "vendor",
            "details": {"name": "AWS"},
        },
        {
            "action": "vendor.create",
            "entity_type": "vendor",
            "details": {"name": "Salesforce"},
        },
        {
            "action": "assessment.create",
            "entity_type": "assessment",
            "details": {"template": "SOC 2"},
        },
        {
            "action": "assessment.submit",
            "entity_type": "assessment",
            "details": {"score": 85},
        },
        {
            "action": "finding.create",
            "entity_type": "finding",
            "details": {"severity": "critical"},
        },
        {
            "action": "role.assign",
            "entity_type": "user_role",
            "details": {"role": "Risk Analyst"},
        },
        {
            "action": "report.generate",
            "entity_type": "report",
            "details": {"format": "pdf"},
        },
        {
            "action": "settings.update",
            "entity_type": "tenant",
            "details": {"field": "mfa_required"},
        },
        {
            "action": "user.logout",
            "entity_type": "user",
            "details": {"method": "manual"},
        },
    ]

    for i, entry in enumerate(entries):
        log = AuditLog(
            tenant_id=tenant_id,
            user_id=user_id,
            action=entry["action"],
            entity_type=entry["entity_type"],
            details=entry["details"],
            ip_address="192.168.1.100",
        )
        log.created_at = now - timedelta(hours=i * 2)
        session.add(log)

    await session.flush()
    return len(entries)


async def seed_sprint_678(
    session: AsyncSession,
) -> int:
    """Seed all Sprint 6-8 demo data. Returns count."""
    user_id = await _get_admin_user_id(session, DEMO_TENANT_ID)
    vendor_ids = await _get_vendor_ids(session, DEMO_TENANT_ID)

    notifs = await _seed_notifications(session, DEMO_TENANT_ID, user_id)
    templates = await _seed_email_templates(session, DEMO_TENANT_ID)
    findings = await _seed_findings(session, DEMO_TENANT_ID, vendor_ids)
    audit = await _seed_audit_logs(session, DEMO_TENANT_ID, user_id)

    await session.commit()
    total = notifs + templates + findings + audit
    logger.info(
        "sprint_678_seed_complete",
        notifications=notifs,
        email_templates=templates,
        findings=findings,
        audit_logs=audit,
    )
    return total
