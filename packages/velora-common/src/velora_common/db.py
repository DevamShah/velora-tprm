"""
Async SQLAlchemy engine, session factory, and tenant context.

Provides connection pooling, per-request sessions via FastAPI dependency,
and RLS tenant context injection for multi-tenant isolation.
"""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from velora_common.logging import get_logger

logger = get_logger(__name__)

# Module-level references — initialised by init_engine()
_engine = None
_async_session_maker = None


def init_engine(database_url: str) -> None:
    """
    Create the async engine and session factory.

    Called once during application startup (lifespan handler).
    """
    global _engine, _async_session_maker  # noqa: PLW0603

    _engine = create_async_engine(
        database_url,
        pool_size=20,
        max_overflow=10,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=False,
    )
    _async_session_maker = async_sessionmaker(
        bind=_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    logger.info("database_engine_initialised")


async def close_engine() -> None:
    """Dispose of the engine's connection pool during shutdown."""
    global _engine  # noqa: PLW0603
    if _engine is not None:
        await _engine.dispose()
        logger.info("database_engine_closed")
        _engine = None


async def set_tenant_context(
    session: AsyncSession,
    tenant_id: str,
) -> None:
    """
    Inject the current tenant ID into the PostgreSQL session.

    RLS policies reference this variable to restrict visible rows.
    """
    import uuid as _uuid

    _uuid.UUID(tenant_id)  # raises ValueError if not a valid UUID
    await session.execute(
        text(f"SET LOCAL app.current_tenant_id = '{tenant_id}'")
    )


async def get_db() -> AsyncSession:  # type: ignore[misc]
    """
    FastAPI dependency that yields a scoped async session.

    Commits on success, rolls back on exception, always closes.
    """
    if _async_session_maker is None:
        raise RuntimeError(
            "Database engine not initialised — call init_engine() first"
        )

    async with _async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def get_engine():
    """Return the current engine instance (for health checks)."""
    return _engine
