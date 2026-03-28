"""
Unified seed runner — uses the monolith codebase (src/backend/) which has
a single unified model set without cross_deps conflicts.

Usage:
    cd /path/to/tprm
    cd src/backend && ../.venv/bin/python ../../scripts/seed_all.py
    OR
    cd /path/to/tprm && uv run python scripts/seed_all.py
"""

import asyncio
import sys
from pathlib import Path

# Add the monolith to the path
TPRM_ROOT = Path(__file__).resolve().parent.parent
MONOLITH_ROOT = TPRM_ROOT / "src" / "backend"
sys.path.insert(0, str(MONOLITH_ROOT))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings
from app.core.seed import run_seed as seed_auth
from app.modules.vendors.seed import seed_vendors
from app.modules.frameworks.seed import seed_frameworks
from app.modules.assessments.seed import seed_assessments
from app.modules.monitoring.seed import seed_monitoring
from app.modules.findings.seed import seed_sprint_678


async def run_all_seeds() -> None:
    settings = get_settings()
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    print("=" * 60)
    print("  Velora TPRM — Full Database Seed")
    print("=" * 60)

    async with async_session() as session:
        # 1. Auth (tenant, roles, users)
        print("\n[1/6] Seeding auth (tenant, roles, users)...")
        await seed_auth(session)
        print("  Done: auth")

    # Use separate sessions for each to avoid FK resolution issues
    async with async_session() as session:
        # 2. Vendors
        print("\n[2/6] Seeding vendors...")
        count = await seed_vendors(session)
        await session.commit()
        print(f"  Done: {count} vendors")

    async with async_session() as session:
        # 3. Frameworks + scoring model
        print("\n[3/6] Seeding frameworks...")
        await seed_frameworks(session)
        await session.commit()
        print("  Done: frameworks")

    async with async_session() as session:
        # 4. Assessments
        print("\n[4/6] Seeding assessments...")
        await seed_assessments(session)
        await session.commit()
        print("  Done: assessments")

    async with async_session() as session:
        # 5. Monitoring
        print("\n[5/6] Seeding monitoring...")
        await seed_monitoring(session)
        await session.commit()
        print("  Done: monitoring")

    async with async_session() as session:
        # 6. Findings, notifications, audit logs
        print("\n[6/6] Seeding findings, communications, audit logs...")
        await seed_sprint_678(session)
        await session.commit()
        print("  Done: findings + comms")

    await engine.dispose()

    print("\n" + "=" * 60)
    print("  All seeds complete!")
    print("=" * 60)
    print("\nTest credentials:")
    print("  admin@velora-demo.com / admin123")
    print("  analyst@velora-demo.com / analyst123")


if __name__ == "__main__":
    asyncio.run(run_all_seeds())
