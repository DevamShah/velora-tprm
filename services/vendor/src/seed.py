"""
Vendor seed data — 15 realistic demo vendors across all tiers.

Idempotent: safe to run multiple times. Skips vendors that already
exist by name within the demo tenant.
"""

from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from velora_common.config import BaseServiceSettings as _Settings
from velora_common.logging import get_logger
from velora_common.security import FieldEncryptor
from velora_common.seed import DEMO_TENANT_ID
from .models import Vendor

logger = get_logger(__name__)


VENDOR_SEEDS: List[dict] = [
    # ── Critical Tier (3) ──────────────────────────────
    {
        "name": "Amazon Web Services",
        "domain": "aws.amazon.com",
        "industry": "Cloud Infrastructure",
        "country": "US",
        "employee_count": 1_500_000,
        "status": "active",
        "tier": "critical",
        "data_classification": "restricted",
        "business_criticality": "critical",
        "contract_value": Decimal("2400000.00"),
        "contract_start_date": date(2024, 1, 1),
        "contract_end_date": date(2027, 12, 31),
        "tags": ["cloud", "infrastructure", "critical"],
        "inherent_risk_score": 85.0,
        "primary_contact_name": "Enterprise Support",
        "primary_contact_email": "enterprise@aws.example.com",
    },
    {
        "name": "Salesforce",
        "domain": "salesforce.com",
        "industry": "CRM / SaaS",
        "country": "US",
        "employee_count": 79_000,
        "status": "active",
        "tier": "critical",
        "data_classification": "confidential",
        "business_criticality": "critical",
        "contract_value": Decimal("850000.00"),
        "contract_start_date": date(2024, 3, 1),
        "contract_end_date": date(2026, 2, 28),
        "tags": ["crm", "saas", "critical"],
        "inherent_risk_score": 78.0,
        "primary_contact_name": "Account Manager",
        "primary_contact_email": "accounts@sf.example.com",
    },
    {
        "name": "Workday",
        "domain": "workday.com",
        "industry": "HR / Finance SaaS",
        "country": "US",
        "employee_count": 18_800,
        "status": "active",
        "tier": "critical",
        "data_classification": "restricted",
        "business_criticality": "critical",
        "contract_value": Decimal("1200000.00"),
        "contract_start_date": date(2024, 6, 1),
        "contract_end_date": date(2027, 5, 31),
        "tags": ["hr", "finance", "saas", "critical"],
        "inherent_risk_score": 82.0,
        "primary_contact_name": "Customer Success",
        "primary_contact_email": "cs@workday.example.com",
    },
    # ── High Tier (4) ─────────────────────────────────
    {
        "name": "Stripe",
        "domain": "stripe.com",
        "industry": "Payment Processing",
        "country": "US",
        "employee_count": 8_000,
        "status": "active",
        "tier": "high",
        "data_classification": "confidential",
        "business_criticality": "high",
        "contract_value": Decimal("500000.00"),
        "tags": ["payments", "fintech", "high"],
        "inherent_risk_score": 72.0,
        "primary_contact_name": "Partner Lead",
        "primary_contact_email": "partner@stripe.example.com",
    },
    {
        "name": "Datadog",
        "domain": "datadoghq.com",
        "industry": "Observability / APM",
        "country": "US",
        "employee_count": 5_200,
        "status": "active",
        "tier": "high",
        "data_classification": "internal",
        "business_criticality": "high",
        "contract_value": Decimal("320000.00"),
        "tags": ["monitoring", "observability", "devops"],
        "inherent_risk_score": 62.0,
        "primary_contact_name": "Account Executive",
        "primary_contact_email": "ae@datadog.example.com",
    },
    {
        "name": "Okta",
        "domain": "okta.com",
        "industry": "Identity / IAM",
        "country": "US",
        "employee_count": 6_000,
        "status": "active",
        "tier": "high",
        "data_classification": "confidential",
        "business_criticality": "high",
        "contract_value": Decimal("280000.00"),
        "tags": ["identity", "iam", "security"],
        "inherent_risk_score": 70.0,
        "primary_contact_name": "Security Liaison",
        "primary_contact_email": "sec@okta.example.com",
    },
    {
        "name": "Snowflake",
        "domain": "snowflake.com",
        "industry": "Data Warehouse",
        "country": "US",
        "employee_count": 7_000,
        "status": "active",
        "tier": "high",
        "data_classification": "confidential",
        "business_criticality": "high",
        "contract_value": Decimal("600000.00"),
        "tags": ["data", "analytics", "cloud"],
        "inherent_risk_score": 68.0,
        "primary_contact_name": "Solutions Architect",
        "primary_contact_email": "sa@snowflake.example.com",
    },
    # ── Medium Tier (5) ────────────────────────────────
    {
        "name": "Zoom",
        "domain": "zoom.us",
        "industry": "Video Conferencing",
        "country": "US",
        "employee_count": 8_400,
        "status": "active",
        "tier": "medium",
        "data_classification": "internal",
        "business_criticality": "medium",
        "contract_value": Decimal("95000.00"),
        "tags": ["communications", "video"],
        "inherent_risk_score": 48.0,
        "primary_contact_name": "Account Rep",
        "primary_contact_email": "rep@zoom.example.com",
    },
    {
        "name": "Slack",
        "domain": "slack.com",
        "industry": "Team Collaboration",
        "country": "US",
        "employee_count": 3_500,
        "status": "active",
        "tier": "medium",
        "data_classification": "internal",
        "business_criticality": "medium",
        "contract_value": Decimal("120000.00"),
        "tags": ["communications", "messaging"],
        "inherent_risk_score": 45.0,
        "primary_contact_name": "CSM",
        "primary_contact_email": "csm@slack.example.com",
    },
    {
        "name": "HubSpot",
        "domain": "hubspot.com",
        "industry": "Marketing / CRM",
        "country": "US",
        "employee_count": 7_400,
        "status": "active",
        "tier": "medium",
        "data_classification": "internal",
        "business_criticality": "medium",
        "contract_value": Decimal("85000.00"),
        "tags": ["marketing", "crm", "automation"],
        "inherent_risk_score": 42.0,
        "primary_contact_name": "Partner Manager",
        "primary_contact_email": "pm@hubspot.example.com",
    },
    {
        "name": "Twilio",
        "domain": "twilio.com",
        "industry": "Communications API",
        "country": "US",
        "employee_count": 5_800,
        "status": "active",
        "tier": "medium",
        "data_classification": "internal",
        "business_criticality": "medium",
        "contract_value": Decimal("150000.00"),
        "tags": ["communications", "api", "sms"],
        "inherent_risk_score": 50.0,
        "primary_contact_name": "TAM",
        "primary_contact_email": "tam@twilio.example.com",
    },
    {
        "name": "Cloudflare",
        "domain": "cloudflare.com",
        "industry": "CDN / Security",
        "country": "US",
        "employee_count": 3_800,
        "status": "active",
        "tier": "medium",
        "data_classification": "internal",
        "business_criticality": "medium",
        "contract_value": Decimal("110000.00"),
        "tags": ["cdn", "security", "dns"],
        "inherent_risk_score": 52.0,
        "primary_contact_name": "SE",
        "primary_contact_email": "se@cloudflare.example.com",
    },
    # ── Low Tier (3) ──────────────────────────────────
    {
        "name": "Calendly",
        "domain": "calendly.com",
        "industry": "Scheduling",
        "country": "US",
        "employee_count": 700,
        "status": "active",
        "tier": "low",
        "data_classification": "public",
        "business_criticality": "low",
        "contract_value": Decimal("12000.00"),
        "tags": ["scheduling", "productivity"],
        "inherent_risk_score": 18.0,
        "primary_contact_name": "Support",
        "primary_contact_email": "support@calendly.example.com",
    },
    {
        "name": "Loom",
        "domain": "loom.com",
        "industry": "Video Messaging",
        "country": "US",
        "employee_count": 500,
        "status": "active",
        "tier": "low",
        "data_classification": "public",
        "business_criticality": "low",
        "contract_value": Decimal("8000.00"),
        "tags": ["video", "async", "productivity"],
        "inherent_risk_score": 15.0,
        "primary_contact_name": "Support",
        "primary_contact_email": "support@loom.example.com",
    },
    {
        "name": "Miro",
        "domain": "miro.com",
        "industry": "Visual Collaboration",
        "country": "NL",
        "employee_count": 1_800,
        "status": "active",
        "tier": "low",
        "data_classification": "public",
        "business_criticality": "low",
        "contract_value": Decimal("15000.00"),
        "tags": ["whiteboard", "collaboration"],
        "inherent_risk_score": 20.0,
        "primary_contact_name": "CSM",
        "primary_contact_email": "csm@miro.example.com",
    },
]


async def _seed_single_vendor(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    encryptor: FieldEncryptor,
    vendor_def: dict,
) -> bool:
    """Create one vendor if it does not exist. Returns True if created."""
    result = await session.execute(
        select(Vendor).where(
            Vendor.tenant_id == tenant_id,
            Vendor.name == vendor_def["name"],
        )
    )
    if result.scalars().first() is not None:
        return False

    email = vendor_def.pop("primary_contact_email", None)
    vendor = Vendor(tenant_id=tenant_id, **vendor_def)

    if email:
        vendor.primary_contact_email_encrypted = (
            encryptor.encrypt(email)
        )
        vendor.primary_contact_email_hash = (
            encryptor.hmac_hash(email)
        )

    session.add(vendor)
    await session.flush()
    return True


async def seed_vendors(session: AsyncSession) -> int:
    """Seed all demo vendors. Returns count of newly created."""
    settings = _Settings()
    encryptor = FieldEncryptor(settings.ENCRYPTION_KEY)
    created = 0

    for vendor_def in VENDOR_SEEDS:
        data = dict(vendor_def)
        if await _seed_single_vendor(
            session, DEMO_TENANT_ID, encryptor, data
        ):
            created += 1
            logger.info(
                "seed_vendor_created",
                name=vendor_def["name"],
            )

    await session.commit()
    logger.info("vendor_seed_complete", created=created)
    return created
