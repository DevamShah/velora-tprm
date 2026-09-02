"""
Async SQLAlchemy engine, session factory, and base model classes.

Provides connection pooling, per-request sessions via FastAPI dependency,
and RLS tenant context injection for multi-tenant isolation.
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
)

from app.core.logging import get_logger

logger = get_logger(__name__)

# Module-level references — initialised by init_engine()
_engine = None
_async_session_maker = None


class Base(DeclarativeBase):
    """
    Abstract base for every model.

    Provides UUID primary key plus created_at / updated_at timestamps.
    """

    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )


class TenantBase(Base):
    """
    Extended base that adds tenant_id for RLS-backed models.

    Every query against a TenantBase table is filtered by the
    tenant context set at connection time.
    """

    __abstract__ = True

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )


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
    Uses string formatting for SET LOCAL which doesn't support
    parameterised queries in PostgreSQL.
    """
    # Sanitise: tenant_id must be a valid UUID to prevent injection
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
