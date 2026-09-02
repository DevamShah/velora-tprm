"""
Database seeder — idempotent seed data for development and testing.

Creates the demo tenant, default RBAC roles with permissions, and
test users (2 admin + 2 analyst) with encrypted email and hashed
passwords. Safe to run multiple times.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.logging import get_logger
from app.core.security import FieldEncryptor, hash_password
from app.modules.auth.models import (
    Role,
    Tenant,
    User,
    UserRole,
)

logger = get_logger(__name__)

# Fixed UUIDs for deterministic seeding
DEMO_TENANT_ID = uuid.UUID("00000000-0000-4000-a000-000000000001")

# ── Permission catalogue ──────────────────────────────────────

ALL_PERMISSIONS: list[str] = [
    "vendors.read",
    "vendors.write",
    "vendors.delete",
    "assessments.read",
    "assessments.write",
    "assessments.manage",
    "frameworks.read",
    "frameworks.write",
    "scoring.read",
    "scoring.write",
    "scoring.configure",
    "monitoring.read",
    "monitoring.write",
    "evidence.read",
    "evidence.write",
    "reports.read",
    "reports.generate",
    "admin.users",
    "admin.roles",
    "admin.audit",
    "admin.settings",
    "portal.access",
]

# ── Role definitions ──────────────────────────────────────────

ROLE_DEFS: list[dict] = [
    {
        "name": "Admin",
        "description": "Full system administration",
        "permissions": ALL_PERMISSIONS,
        "is_system": True,
    },
    {
        "name": "TPRM Manager",
        "description": "Manage third-party risk programme",
        "permissions": [
            "vendors.read",
            "vendors.write",
            "assessments.read",
            "assessments.write",
            "assessments.manage",
            "frameworks.read",
            "scoring.read",
            "scoring.write",
            "monitoring.read",
            "monitoring.write",
            "evidence.read",
            "evidence.write",
            "reports.read",
            "reports.generate",
        ],
    },
    {
        "name": "Risk Analyst",
        "description": "Conduct risk assessments and scoring",
        "permissions": [
            "vendors.read",
            "assessments.read",
            "assessments.write",
            "frameworks.read",
            "scoring.read",
            "scoring.write",
            "monitoring.read",
            "evidence.read",
            "evidence.write",
            "reports.read",
        ],
    },
    {
        "name": "GRC Analyst",
        "description": "Governance, risk, and compliance analysis",
        "permissions": [
            "vendors.read",
            "assessments.read",
            "frameworks.read",
            "frameworks.write",
            "scoring.read",
            "monitoring.read",
            "evidence.read",
            "reports.read",
            "reports.generate",
        ],
    },
    {
        "name": "Viewer",
        "description": "Read-only access across modules",
        "permissions": [
            "vendors.read",
            "assessments.read",
            "frameworks.read",
            "scoring.read",
            "monitoring.read",
            "evidence.read",
            "reports.read",
        ],
        "is_default": True,
    },
    {
        "name": "Vendor Manager",
        "description": "Manage vendor lifecycle",
        "permissions": [
            "vendors.read",
            "vendors.write",
            "vendors.delete",
            "assessments.read",
            "evidence.read",
            "evidence.write",
            "portal.access",
        ],
    },
    {
        "name": "IT Security",
        "description": "Security monitoring and assessment",
        "permissions": [
            "vendors.read",
            "assessments.read",
            "assessments.write",
            "frameworks.read",
            "scoring.read",
            "monitoring.read",
            "monitoring.write",
            "evidence.read",
            "reports.read",
        ],
    },
    {
        "name": "Auditor",
        "description": "Audit trail and compliance review",
        "permissions": [
            "vendors.read",
            "assessments.read",
            "frameworks.read",
            "scoring.read",
            "monitoring.read",
            "evidence.read",
            "reports.read",
            "reports.generate",
            "admin.audit",
        ],
    },
]

# ── Test users ────────────────────────────────────────────────

TEST_USERS: list[dict] = [
    {
        "email": "admin@velora-demo.com",
        "password": "admin123",
        "first_name": "Admin",
        "last_name": "Primary",
        "role": "Admin",
    },
    {
        "email": "admin2@velora-demo.com",
        "password": "admin123",
        "first_name": "Admin",
        "last_name": "Secondary",
        "role": "Admin",
    },
    {
        "email": "analyst@velora-demo.com",
        "password": "analyst123",
        "first_name": "Analyst",
        "last_name": "Primary",
        "role": "Risk Analyst",
    },
    {
        "email": "analyst2@velora-demo.com",
        "password": "analyst123",
        "first_name": "Analyst",
        "last_name": "Secondary",
        "role": "Risk Analyst",
    },
]


# ── Seeder functions ──────────────────────────────────────────


async def _seed_tenant(session: AsyncSession) -> Tenant:
    """Create the demo tenant if it does not exist."""
    result = await session.execute(
        select(Tenant).where(Tenant.id == DEMO_TENANT_ID)
    )
    tenant = result.scalars().first()
    if tenant is not None:
        logger.info("seed_tenant_exists")
        return tenant

    tenant = Tenant(
        id=DEMO_TENANT_ID,
        name="Velora Demo",
        slug="velora-demo",
        is_active=True,
    )
    session.add(tenant)
    await session.flush()
    logger.info("seed_tenant_created", name=tenant.name)
    return tenant


async def _seed_roles(
    session: AsyncSession,
    tenant_id: uuid.UUID,
) -> dict[str, Role]:
    """Create default roles, returning a name->Role map."""
    role_map: dict[str, Role] = {}

    for role_def in ROLE_DEFS:
        result = await session.execute(
            select(Role).where(
                Role.tenant_id == tenant_id,
                Role.name == role_def["name"],
            )
        )
        existing = result.scalars().first()

        if existing is not None:
            role_map[existing.name] = existing
            continue

        role = Role(
            tenant_id=tenant_id,
            name=role_def["name"],
            description=role_def.get("description", ""),
            permissions=role_def["permissions"],
            is_system=role_def.get("is_system", False),
            is_default=role_def.get("is_default", False),
        )
        session.add(role)
        await session.flush()
        role_map[role.name] = role
        logger.info("seed_role_created", name=role.name)

    return role_map


async def _seed_users(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    role_map: dict[str, Role],
    encryptor: FieldEncryptor,
) -> None:
    """Create test users with encrypted emails and role grants."""
    now = datetime.now(UTC)

    for user_def in TEST_USERS:
        email_hash = encryptor.hmac_hash(user_def["email"])

        result = await session.execute(
            select(User).where(
                User.tenant_id == tenant_id,
                User.email_hash == email_hash,
            )
        )
        if result.scalars().first() is not None:
            continue

        user = User(
            tenant_id=tenant_id,
            email_encrypted=encryptor.encrypt(
                user_def["email"]
            ),
            email_hash=email_hash,
            first_name=user_def["first_name"],
            last_name=user_def["last_name"],
            password_hash=hash_password(user_def["password"]),
            is_active=True,
        )
        session.add(user)
        await session.flush()

        role = role_map.get(user_def["role"])
        if role is not None:
            user_role = UserRole(
                user_id=user.id,
                role_id=role.id,
                granted_at=now,
            )
            session.add(user_role)

        logger.info(
            "seed_user_created",
            first_name=user_def["first_name"],
            role=user_def["role"],
        )

    await session.flush()


async def run_seed(session: AsyncSession) -> None:
    """Execute the full seed pipeline (idempotent)."""
    settings = get_settings()
    encryptor = FieldEncryptor(settings.ENCRYPTION_KEY)

    tenant = await _seed_tenant(session)
    role_map = await _seed_roles(session, tenant.id)
    await _seed_users(session, tenant.id, role_map, encryptor)

    await session.commit()
    logger.info("seed_complete")
