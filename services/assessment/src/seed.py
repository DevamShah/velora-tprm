"""
Assessment seed data — 3 templates with questions, 5 demo assessments.

Idempotent: safe to run multiple times. Skips entities that already
exist by name within the demo tenant.
"""

from __future__ import annotations

import uuid
from typing import Dict, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from velora_common.logging import get_logger
from velora_common.seed import DEMO_TENANT_ID
from .models import (
    Assessment,
    AssessmentTemplate,
    Question,
    QuestionnaireResponse,
)
from .cross_deps.vendor_models import Vendor  # TODO: Replace with API call in Phase 2

logger = get_logger(__name__)


# -- Template definitions -------------------------------------------

TEMPLATE_SEEDS: List[Dict] = [
    {
        "name": "SIG Core Assessment",
        "description": (
            "Standardized Information Gathering (SIG) "
            "Core questionnaire for critical/high tier "
            "vendors. Comprehensive security evaluation."
        ),
        "tier_applicability": ["critical", "high"],
        "is_system": True,
        "estimated_duration_minutes": 120,
        "scoring_weights": {
            "information_security": 1.5,
            "access_control": 1.3,
            "data_protection": 1.5,
            "business_continuity": 1.2,
            "incident_response": 1.4,
        },
    },
    {
        "name": "SIG Lite Assessment",
        "description": (
            "Standardized Information Gathering (SIG) "
            "Lite questionnaire for medium tier vendors. "
            "Focused security evaluation."
        ),
        "tier_applicability": ["medium"],
        "is_system": True,
        "estimated_duration_minutes": 60,
        "scoring_weights": {
            "information_security": 1.2,
            "access_control": 1.1,
            "data_protection": 1.3,
            "business_continuity": 1.0,
            "incident_response": 1.1,
        },
    },
    {
        "name": "Custom Security Review",
        "description": (
            "Lightweight custom security review for "
            "low tier vendors. Quick evaluation of "
            "essential security controls."
        ),
        "tier_applicability": ["low", "unclassified"],
        "is_system": True,
        "estimated_duration_minutes": 30,
        "scoring_weights": {
            "information_security": 1.0,
            "access_control": 1.0,
            "data_protection": 1.0,
        },
    },
]


# -- Question definitions per template ------------------------------

SIG_CORE_QUESTIONS: List[Dict] = [
    # Information Security (3)
    {
        "section": "Information Security",
        "subsection": "Policy & Governance",
        "question_text": (
            "Does your organization maintain a formal "
            "information security policy approved by "
            "senior management?"
        ),
        "question_type": "yes_no",
        "risk_domain": "information_security",
        "weight": 1.5,
        "order_index": 1,
        "guidance_text": (
            "Provide a copy of the policy or link to "
            "the publicly available version."
        ),
    },
    {
        "section": "Information Security",
        "subsection": "Risk Management",
        "question_text": (
            "Do you perform regular information "
            "security risk assessments at least "
            "annually?"
        ),
        "question_type": "yes_no",
        "risk_domain": "information_security",
        "weight": 1.3,
        "order_index": 2,
    },
    {
        "section": "Information Security",
        "subsection": "Security Awareness",
        "question_text": (
            "Do all employees complete mandatory "
            "security awareness training upon hire "
            "and annually thereafter?"
        ),
        "question_type": "yes_no",
        "risk_domain": "information_security",
        "weight": 1.0,
        "order_index": 3,
    },
    # Access Control (3)
    {
        "section": "Access Control",
        "subsection": "Authentication",
        "question_text": (
            "Is multi-factor authentication enforced "
            "for all administrative and remote access?"
        ),
        "question_type": "yes_no",
        "risk_domain": "access_control",
        "weight": 1.5,
        "order_index": 4,
    },
    {
        "section": "Access Control",
        "subsection": "Authorization",
        "question_text": (
            "Do you implement role-based access "
            "controls with least-privilege principles?"
        ),
        "question_type": "yes_no",
        "risk_domain": "access_control",
        "weight": 1.3,
        "order_index": 5,
    },
    {
        "section": "Access Control",
        "subsection": "Review",
        "question_text": (
            "How frequently do you review and "
            "recertify user access privileges?"
        ),
        "question_type": "multiple_choice",
        "options": {
            "choices": [
                "Monthly",
                "Quarterly",
                "Semi-annually",
                "Annually",
                "No formal process",
            ]
        },
        "risk_domain": "access_control",
        "weight": 1.0,
        "order_index": 6,
    },
    # Data Protection (3)
    {
        "section": "Data Protection",
        "subsection": "Encryption",
        "question_text": (
            "Is all sensitive data encrypted at rest "
            "using AES-256 or equivalent?"
        ),
        "question_type": "yes_no",
        "risk_domain": "data_protection",
        "weight": 1.5,
        "order_index": 7,
    },
    {
        "section": "Data Protection",
        "subsection": "Transit",
        "question_text": (
            "Is all data in transit protected using "
            "TLS 1.2 or higher?"
        ),
        "question_type": "yes_no",
        "risk_domain": "data_protection",
        "weight": 1.5,
        "order_index": 8,
    },
    {
        "section": "Data Protection",
        "subsection": "Retention",
        "question_text": (
            "Do you have a documented data retention "
            "and destruction policy?"
        ),
        "question_type": "yes_no",
        "risk_domain": "data_protection",
        "weight": 1.0,
        "order_index": 9,
    },
    # Business Continuity (3)
    {
        "section": "Business Continuity",
        "subsection": "BCP",
        "question_text": (
            "Do you maintain a documented business "
            "continuity plan that is tested annually?"
        ),
        "question_type": "yes_no",
        "risk_domain": "business_continuity",
        "weight": 1.2,
        "order_index": 10,
    },
    {
        "section": "Business Continuity",
        "subsection": "Disaster Recovery",
        "question_text": (
            "What is your Recovery Time Objective "
            "(RTO) for critical systems?"
        ),
        "question_type": "multiple_choice",
        "options": {
            "choices": [
                "< 1 hour",
                "1-4 hours",
                "4-24 hours",
                "24-72 hours",
                "> 72 hours",
            ]
        },
        "risk_domain": "business_continuity",
        "weight": 1.2,
        "order_index": 11,
    },
    {
        "section": "Business Continuity",
        "subsection": "Backup",
        "question_text": (
            "Are backups encrypted and stored in a "
            "geographically separate location?"
        ),
        "question_type": "yes_no",
        "risk_domain": "business_continuity",
        "weight": 1.0,
        "order_index": 12,
    },
    # Incident Response (3)
    {
        "section": "Incident Response",
        "subsection": "Plan",
        "question_text": (
            "Do you maintain a documented incident "
            "response plan with defined roles?"
        ),
        "question_type": "yes_no",
        "risk_domain": "incident_response",
        "weight": 1.4,
        "order_index": 13,
    },
    {
        "section": "Incident Response",
        "subsection": "Notification",
        "question_text": (
            "What is your committed notification "
            "timeframe for security incidents?"
        ),
        "question_type": "multiple_choice",
        "options": {
            "choices": [
                "Within 24 hours",
                "Within 48 hours",
                "Within 72 hours",
                "No committed timeframe",
            ]
        },
        "risk_domain": "incident_response",
        "weight": 1.3,
        "order_index": 14,
    },
    {
        "section": "Incident Response",
        "subsection": "Testing",
        "question_text": (
            "Do you conduct regular tabletop "
            "exercises or simulated incident "
            "response drills?"
        ),
        "question_type": "yes_no",
        "risk_domain": "incident_response",
        "weight": 1.0,
        "order_index": 15,
    },
]

SIG_LITE_QUESTIONS: List[Dict] = [
    {
        "section": "Information Security",
        "question_text": (
            "Does your organization have a formal "
            "information security programme?"
        ),
        "question_type": "yes_no",
        "risk_domain": "information_security",
        "weight": 1.2,
        "order_index": 1,
    },
    {
        "section": "Information Security",
        "question_text": (
            "Are security policies reviewed and "
            "updated at least annually?"
        ),
        "question_type": "yes_no",
        "risk_domain": "information_security",
        "weight": 1.0,
        "order_index": 2,
    },
    {
        "section": "Access Control",
        "question_text": (
            "Is multi-factor authentication available "
            "for your platform?"
        ),
        "question_type": "yes_no",
        "risk_domain": "access_control",
        "weight": 1.3,
        "order_index": 3,
    },
    {
        "section": "Access Control",
        "question_text": (
            "Do you perform regular access reviews?"
        ),
        "question_type": "yes_no",
        "risk_domain": "access_control",
        "weight": 1.0,
        "order_index": 4,
    },
    {
        "section": "Data Protection",
        "question_text": (
            "Is data encrypted at rest and in transit?"
        ),
        "question_type": "yes_no",
        "risk_domain": "data_protection",
        "weight": 1.5,
        "order_index": 5,
    },
    {
        "section": "Data Protection",
        "question_text": (
            "Do you have a data classification scheme?"
        ),
        "question_type": "yes_no",
        "risk_domain": "data_protection",
        "weight": 1.0,
        "order_index": 6,
    },
    {
        "section": "Business Continuity",
        "question_text": (
            "Do you have a business continuity plan?"
        ),
        "question_type": "yes_no",
        "risk_domain": "business_continuity",
        "weight": 1.0,
        "order_index": 7,
    },
    {
        "section": "Business Continuity",
        "question_text": (
            "What is your guaranteed uptime SLA?"
        ),
        "question_type": "text",
        "risk_domain": "business_continuity",
        "weight": 1.0,
        "order_index": 8,
    },
    {
        "section": "Incident Response",
        "question_text": (
            "Do you have an incident response process?"
        ),
        "question_type": "yes_no",
        "risk_domain": "incident_response",
        "weight": 1.2,
        "order_index": 9,
    },
    {
        "section": "Incident Response",
        "question_text": (
            "Will you notify us within 72 hours of "
            "a security breach?"
        ),
        "question_type": "yes_no",
        "risk_domain": "incident_response",
        "weight": 1.3,
        "order_index": 10,
    },
]

CUSTOM_QUESTIONS: List[Dict] = [
    {
        "section": "Information Security",
        "question_text": (
            "Do you have a security policy in place?"
        ),
        "question_type": "yes_no",
        "risk_domain": "information_security",
        "weight": 1.0,
        "order_index": 1,
    },
    {
        "section": "Information Security",
        "question_text": (
            "Have you completed a SOC 2 Type II "
            "or equivalent audit?"
        ),
        "question_type": "yes_no",
        "risk_domain": "information_security",
        "weight": 1.0,
        "order_index": 2,
    },
    {
        "section": "Access Control",
        "question_text": (
            "Do you support single sign-on (SSO)?"
        ),
        "question_type": "yes_no",
        "risk_domain": "access_control",
        "weight": 1.0,
        "order_index": 3,
    },
    {
        "section": "Data Protection",
        "question_text": (
            "Where is customer data stored "
            "geographically?"
        ),
        "question_type": "text",
        "risk_domain": "data_protection",
        "weight": 1.0,
        "order_index": 4,
    },
    {
        "section": "Data Protection",
        "question_text": (
            "Is customer data encrypted at rest?"
        ),
        "question_type": "yes_no",
        "risk_domain": "data_protection",
        "weight": 1.0,
        "order_index": 5,
    },
    {
        "section": "Data Protection",
        "question_text": (
            "Can you provide a data processing "
            "agreement (DPA)?"
        ),
        "question_type": "yes_no",
        "risk_domain": "data_protection",
        "weight": 1.0,
        "order_index": 6,
    },
    {
        "section": "Business Continuity",
        "question_text": (
            "What is your target uptime percentage?"
        ),
        "question_type": "text",
        "risk_domain": "business_continuity",
        "weight": 1.0,
        "order_index": 7,
    },
    {
        "section": "Incident Response",
        "question_text": (
            "How do you handle security incident "
            "notifications to customers?"
        ),
        "question_type": "text",
        "risk_domain": "incident_response",
        "weight": 1.0,
        "order_index": 8,
    },
]

TEMPLATE_QUESTIONS_MAP = {
    "SIG Core Assessment": SIG_CORE_QUESTIONS,
    "SIG Lite Assessment": SIG_LITE_QUESTIONS,
    "Custom Security Review": CUSTOM_QUESTIONS,
}


# -- Demo assessment definitions ------------------------------------

DEMO_ASSESSMENTS: List[Dict] = [
    {
        "vendor_name": "Amazon Web Services",
        "template_name": "SIG Core Assessment",
        "title": "AWS Annual Security Assessment 2026",
        "status": "in_progress",
        "description": (
            "Annual comprehensive security review "
            "of AWS cloud infrastructure services."
        ),
    },
    {
        "vendor_name": "Salesforce",
        "template_name": "SIG Core Assessment",
        "title": "Salesforce CRM Security Review",
        "status": "submitted",
        "description": (
            "Security assessment for Salesforce CRM "
            "platform renewal."
        ),
    },
    {
        "vendor_name": "Zoom",
        "template_name": "SIG Lite Assessment",
        "title": "Zoom Communications Review",
        "status": "draft",
        "description": (
            "Periodic assessment of Zoom video "
            "conferencing platform."
        ),
    },
    {
        "vendor_name": "Okta",
        "template_name": "SIG Core Assessment",
        "title": "Okta IAM Security Assessment",
        "status": "completed",
        "overall_score": 87.3,
        "description": (
            "Identity provider security assessment "
            "for contract renewal."
        ),
    },
    {
        "vendor_name": "Calendly",
        "template_name": "Custom Security Review",
        "title": "Calendly Quick Security Check",
        "status": "distributed",
        "description": (
            "Lightweight security review for low-tier "
            "scheduling tool."
        ),
    },
]


# -- Seeder functions -----------------------------------------------


async def _seed_template(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    template_def: Dict,
) -> AssessmentTemplate:
    """Create template if it does not exist."""
    result = await session.execute(
        select(AssessmentTemplate).where(
            AssessmentTemplate.tenant_id == tenant_id,
            AssessmentTemplate.name == template_def["name"],
        )
    )
    existing = result.scalars().first()
    if existing is not None:
        return existing

    questions = TEMPLATE_QUESTIONS_MAP.get(
        template_def["name"], []
    )
    template = AssessmentTemplate(
        tenant_id=tenant_id,
        name=template_def["name"],
        description=template_def.get("description"),
        tier_applicability=template_def.get(
            "tier_applicability"
        ),
        is_system=template_def.get("is_system", True),
        scoring_weights=template_def.get(
            "scoring_weights"
        ),
        question_count=len(questions),
        estimated_duration_minutes=template_def.get(
            "estimated_duration_minutes"
        ),
    )
    session.add(template)
    await session.flush()
    logger.info(
        "seed_template_created", name=template.name
    )
    return template


async def _seed_questions(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    template: AssessmentTemplate,
    questions_def: List[Dict],
) -> None:
    """Seed questions for a template if none exist."""
    result = await session.execute(
        select(func.count()).select_from(
            select(Question)
            .where(
                Question.template_id == template.id,
                Question.tenant_id == tenant_id,
            )
            .subquery()
        )
    )
    if (result.scalar() or 0) > 0:
        return

    for q_def in questions_def:
        question = Question(
            tenant_id=tenant_id,
            template_id=template.id,
            section=q_def.get("section"),
            subsection=q_def.get("subsection"),
            question_text=q_def["question_text"],
            question_type=q_def.get(
                "question_type", "text"
            ),
            options=q_def.get("options"),
            is_required=q_def.get("is_required", True),
            weight=q_def.get("weight", 1.0),
            risk_domain=q_def.get("risk_domain"),
            guidance_text=q_def.get("guidance_text"),
            order_index=q_def.get("order_index", 0),
        )
        session.add(question)

    await session.flush()
    logger.info(
        "seed_questions_created",
        template=template.name,
        count=len(questions_def),
    )


async def _get_vendor_by_name(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    name: str,
) -> Vendor:
    """Find a vendor by name within the tenant."""
    result = await session.execute(
        select(Vendor).where(
            Vendor.tenant_id == tenant_id,
            Vendor.name == name,
        )
    )
    return result.scalars().first()


async def _seed_assessment(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    assessment_def: Dict,
    template_map: Dict[str, AssessmentTemplate],
) -> bool:
    """Create a demo assessment if it does not exist."""
    result = await session.execute(
        select(Assessment).where(
            Assessment.tenant_id == tenant_id,
            Assessment.title == assessment_def["title"],
        )
    )
    if result.scalars().first() is not None:
        return False

    vendor = await _get_vendor_by_name(
        session,
        tenant_id,
        assessment_def["vendor_name"],
    )
    if vendor is None:
        logger.warning(
            "seed_assessment_skip_no_vendor",
            vendor=assessment_def["vendor_name"],
        )
        return False

    template = template_map.get(
        assessment_def["template_name"]
    )
    if template is None:
        return False

    assessment = Assessment(
        tenant_id=tenant_id,
        vendor_id=vendor.id,
        template_id=template.id,
        title=assessment_def["title"],
        description=assessment_def.get("description"),
        status=assessment_def.get("status", "draft"),
        overall_score=assessment_def.get("overall_score"),
    )
    session.add(assessment)
    await session.flush()

    # Clone questions as responses
    q_result = await session.execute(
        select(Question)
        .where(
            Question.template_id == template.id,
            Question.tenant_id == tenant_id,
        )
        .order_by(Question.order_index.asc())
    )
    questions = q_result.scalars().all()

    for question in questions:
        resp = QuestionnaireResponse(
            tenant_id=tenant_id,
            assessment_id=assessment.id,
            question_id=question.id,
            review_status="pending",
        )
        session.add(resp)

    await session.flush()
    logger.info(
        "seed_assessment_created",
        title=assessment_def["title"],
    )
    return True


# Need func import for count query
from sqlalchemy import func  # noqa: E402


async def seed_assessments(
    session: AsyncSession,
) -> int:
    """Seed templates, questions, and demo assessments."""
    tenant_id = DEMO_TENANT_ID
    created = 0

    # 1. Seed templates
    template_map: Dict[str, AssessmentTemplate] = {}
    for template_def in TEMPLATE_SEEDS:
        template = await _seed_template(
            session, tenant_id, template_def
        )
        template_map[template.name] = template

        # 2. Seed questions per template
        questions_def = TEMPLATE_QUESTIONS_MAP.get(
            template.name, []
        )
        await _seed_questions(
            session, tenant_id, template, questions_def
        )

    # 3. Seed demo assessments
    for assessment_def in DEMO_ASSESSMENTS:
        if await _seed_assessment(
            session,
            tenant_id,
            assessment_def,
            template_map,
        ):
            created += 1

    await session.commit()
    logger.info(
        "assessment_seed_complete", created=created
    )
    return created
