"""
Seed compliance frameworks, clauses, cross-mappings,
and a default scoring model.

Data definitions live in seed_data.py.
Run via: python -m app.modules.frameworks.seed
"""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Import auth models to resolve FK references
# (control_mappings.verified_by -> users.id)
import app.modules.auth.models  # noqa: F401
from app.core.logging import get_logger
from app.modules.frameworks.models import (
    ControlMapping,
    Framework,
    FrameworkClause,
)
from app.modules.frameworks.seed_data import (
    ALL_CLAUSES,
    DEFAULT_INHERENT_FACTORS,
    DEFAULT_MODEL_CONFIG,
    DEFAULT_THRESHOLDS,
    FRAMEWORKS,
    MAPPINGS,
    uid,
)
from app.modules.scoring.models import ScoringModel

logger = get_logger(__name__)


async def seed_frameworks(
    session: AsyncSession,
    tenant_id: uuid.UUID | None = None,
) -> dict[str, int]:
    """
    Seed frameworks, clauses, mappings, and default model.

    Skips existing records (idempotent). Returns insert counts.
    """
    counts = {
        "frameworks": 0,
        "clauses": 0,
        "mappings": 0,
        "scoring_models": 0,
    }

    counts["frameworks"] = await _seed_frameworks(session)
    await session.flush()

    counts["clauses"] = await _seed_clauses(session)
    await session.flush()

    await _update_clause_counts(session)
    await session.flush()

    counts["mappings"] = await _seed_mappings(session)
    await session.flush()

    if tenant_id:
        counts["scoring_models"] = await _seed_scoring_model(
            session, tenant_id
        )
        await session.flush()

    logger.info("seed_complete", counts=counts)
    return counts


async def _seed_frameworks(
    session: AsyncSession,
) -> int:
    """Insert framework records if not present."""
    count = 0
    for fw_data in FRAMEWORKS:
        existing = await session.execute(
            select(Framework).where(Framework.id == fw_data["id"])
        )
        if existing.scalars().first():
            continue
        session.add(Framework(**fw_data))
        count += 1
    return count


async def _seed_clauses(
    session: AsyncSession,
) -> int:
    """Insert clause records if not present."""
    count = 0
    for cl_data in ALL_CLAUSES:
        existing = await session.execute(
            select(FrameworkClause).where(FrameworkClause.id == cl_data["id"])
        )
        if existing.scalars().first():
            continue
        session.add(FrameworkClause(**cl_data))
        count += 1
    return count


async def _update_clause_counts(
    session: AsyncSession,
) -> None:
    """Refresh clause_count on each framework."""
    for fw_data in FRAMEWORKS:
        result = await session.execute(
            select(FrameworkClause).where(
                FrameworkClause.framework_id == fw_data["id"]
            )
        )
        clause_list = result.scalars().all()
        fw_result = await session.execute(
            select(Framework).where(Framework.id == fw_data["id"])
        )
        fw_obj = fw_result.scalars().first()
        if fw_obj:
            fw_obj.clause_count = len(clause_list)


async def _seed_mappings(
    session: AsyncSession,
) -> int:
    """Insert control mappings if not present."""
    count = 0
    for mp_data in MAPPINGS:
        existing = await session.execute(
            select(ControlMapping).where(ControlMapping.id == mp_data["id"])
        )
        if existing.scalars().first():
            continue
        session.add(ControlMapping(**mp_data))
        count += 1
    return count


async def _seed_scoring_model(
    session: AsyncSession,
    tenant_id: uuid.UUID,
) -> int:
    """Insert default scoring model for a tenant."""
    model_id = uid(f"default_model_{tenant_id}")
    existing = await session.execute(
        select(ScoringModel).where(ScoringModel.id == model_id)
    )
    if existing.scalars().first():
        return 0

    model = ScoringModel(
        id=model_id,
        tenant_id=tenant_id,
        name="Default TPRM Scoring Model",
        description=(
            "Five-dimension weighted average scoring "
            "model for vendor risk assessment"
        ),
        method="weighted_average",
        is_default=True,
        config=DEFAULT_MODEL_CONFIG,
        inherent_risk_factors=DEFAULT_INHERENT_FACTORS,
        risk_thresholds=DEFAULT_THRESHOLDS,
    )
    session.add(model)
    return 1
