"""
FastAPI application factory for Velora TPRM v2.0.

Sets up middleware, routers, health checks, and RFC 7807 error handling.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import redis.asyncio as aioredis
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.core.config import get_settings, settings
from app.core.database import close_engine, init_engine
from app.core.logging import configure_logging, get_logger
from app.middleware.auth import AuthMiddleware
from app.middleware.tenant import TenantMiddleware
from app.modules.assessments.router import (
    router as assessments_router,
)
from app.modules.auth.router import router as auth_router
from app.modules.frameworks.router import (
    router as frameworks_router,
)
from app.modules.scoring.router import (
    router as scoring_router,
)
from app.modules.vendors.router import router as vendors_router
from app.modules.evidence.router import (
    router as evidence_router,
)
from app.modules.ai.router import router as ai_router
from app.modules.monitoring.router import (
    router as monitoring_router,
)
from app.modules.reports.router import (
    router as reports_router,
)
from app.modules.communications.router import (
    router as communications_router,
)
from app.modules.admin.router import (
    router as admin_router,
)
from app.modules.findings.router import (
    router as findings_router,
)

logger = get_logger(__name__)

limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Startup / shutdown lifecycle for the ASGI server."""
    settings = get_settings()
    configure_logging(settings.LOG_LEVEL)
    init_engine(settings.DATABASE_URL)
    logger.info(
        "application_started",
        app=settings.APP_NAME,
        version=settings.APP_VERSION,
    )
    yield
    await close_engine()
    logger.info("application_stopped")


def create_app() -> FastAPI:
    """Construct the FastAPI application with all wiring."""
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # ── Rate limiting ─────────────────────────────────────
    app.state.limiter = limiter
    app.add_exception_handler(
        RateLimitExceeded, _rate_limit_exceeded_handler
    )

    # ── CORS ──────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Custom middleware (outermost first) ────────────────
    app.add_middleware(
        TenantMiddleware,
        jwt_secret=settings.JWT_SECRET_KEY,
    )
    app.add_middleware(
        AuthMiddleware,
        jwt_secret=settings.JWT_SECRET_KEY,
    )

    # ── RFC 7807 error handlers ───────────────────────────
    app.add_exception_handler(
        RequestValidationError, _validation_error_handler
    )
    app.add_exception_handler(Exception, _generic_error_handler)

    # ── Routers ───────────────────────────────────────────
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(vendors_router, prefix="/api/v1")
    app.include_router(
        assessments_router, prefix="/api/v1"
    )
    app.include_router(
        frameworks_router, prefix="/api/v1"
    )
    app.include_router(
        scoring_router, prefix="/api/v1"
    )
    app.include_router(
        evidence_router, prefix="/api/v1"
    )
    app.include_router(ai_router, prefix="/api/v1")
    app.include_router(
        monitoring_router, prefix="/api/v1"
    )
    app.include_router(
        reports_router, prefix="/api/v1"
    )
    app.include_router(
        communications_router, prefix="/api/v1"
    )
    app.include_router(
        admin_router, prefix="/api/v1"
    )
    app.include_router(
        findings_router, prefix="/api/v1"
    )

    # ── Health / readiness probes ─────────────────────────
    @app.get("/health", tags=["infra"])
    async def health() -> dict:
        return {"status": "healthy"}

    @app.get("/ready", tags=["infra"])
    async def ready() -> dict:
        checks: dict[str, str] = {}
        try:
            from app.core.database import _engine

            if _engine is not None:
                async with _engine.connect() as conn:
                    await conn.execute(
                        __import__(
                            "sqlalchemy"
                        ).text("SELECT 1")
                    )
                checks["database"] = "ok"
            else:
                checks["database"] = "not_initialised"
        except Exception:
            checks["database"] = "unreachable"

        try:
            redis_client = aioredis.from_url(
                settings.REDIS_URL,
                socket_connect_timeout=2,
            )
            await redis_client.ping()
            await redis_client.aclose()
            checks["redis"] = "ok"
        except Exception:
            checks["redis"] = "unreachable"

        all_ok = all(v == "ok" for v in checks.values())
        code = (
            status.HTTP_200_OK
            if all_ok
            else status.HTTP_503_SERVICE_UNAVAILABLE
        )
        return JSONResponse(
            status_code=code,
            content={
                "status": "ready" if all_ok else "degraded",
                "checks": checks,
            },
        )

    return app


# ── Error handlers ────────────────────────────────────────────


async def _validation_error_handler(
    _request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Map Pydantic validation errors to RFC 7807."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "type": "about:blank",
            "title": "Validation Error",
            "status": 422,
            "detail": str(exc.errors()),
        },
    )


async def _generic_error_handler(
    _request: Request, exc: Exception
) -> JSONResponse:
    """Catch-all — never leak stack traces to clients."""
    logger.error("unhandled_exception", exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "type": "about:blank",
            "title": "Internal Server Error",
            "status": 500,
            "detail": "An unexpected error occurred",
        },
    )


# Module-level instance for uvicorn
app = create_app()
