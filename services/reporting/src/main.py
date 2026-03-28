"""
FastAPI application for Velora Reporting Service.

Microservice entry point with health check, CORS, and error handling.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from velora_common.config import BaseServiceSettings
from velora_common.db import close_engine, init_engine
from velora_common.logging import configure_logging, get_logger

from .event_consumer import DashboardReadModelConsumer
from .router import router

logger = get_logger(__name__)

# Module-level reference so the health endpoint can inspect status
_event_consumer: DashboardReadModelConsumer | None = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Startup / shutdown lifecycle for the ASGI server."""
    global _event_consumer

    settings = BaseServiceSettings()  # type: ignore[call-arg]
    configure_logging(settings.LOG_LEVEL)
    init_engine(settings.DATABASE_URL)

    # Start the CQRS read-model event consumer as a background task
    _event_consumer = DashboardReadModelConsumer(settings.REDIS_URL)
    await _event_consumer.start()

    logger.info(
        "service_started",
        service="reporting",
        version=settings.APP_VERSION,
    )
    yield

    # Shutdown
    if _event_consumer:
        await _event_consumer.stop()
    await close_engine()
    logger.info("service_stopped", service="reporting")


def create_app() -> FastAPI:
    """Construct the FastAPI application."""
    app = FastAPI(
        title="Velora Reporting Service",
        version="2.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    app.include_router(router, prefix="/api/v1")

    # Health check
    @app.get("/health", tags=["infra"])
    async def health() -> dict:
        return {"status": "healthy", "service": "reporting"}

    # Error handlers
    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        _request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "type": "about:blank",
                "title": "Validation Error",
                "status": 422,
                "detail": str(exc.errors()),
            },
        )

    @app.exception_handler(Exception)
    async def generic_error_handler(
        _request: Request, exc: Exception
    ) -> JSONResponse:
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

    return app


app = create_app()
