"""FastAPI application for Velora Workflow Service.

Runs a Temporal worker as a background task alongside a lightweight
FastAPI health endpoint for container orchestration probes.
"""

from __future__ import annotations

import asyncio
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from velora_common.logging import configure_logging, get_logger

logger = get_logger(__name__)

# Worker task reference for graceful shutdown
_worker_task: asyncio.Task | None = None  # type: ignore[type-arg]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Start the Temporal worker on startup; cancel on shutdown."""
    global _worker_task

    configure_logging(os.getenv("LOG_LEVEL", "INFO"))

    # Import here to avoid circular imports and allow module-level
    # env var resolution in the worker module.
    from .worker import run_worker

    _worker_task = asyncio.create_task(
        run_worker(), name="temporal-worker"
    )
    logger.info("workflow_service_started")

    yield

    # Graceful shutdown
    if _worker_task and not _worker_task.done():
        _worker_task.cancel()
        try:
            await _worker_task
        except asyncio.CancelledError:
            pass

    logger.info("workflow_service_stopped")


app = FastAPI(
    title="Velora Workflow Service",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["infra"])
async def health() -> dict:
    """Health check endpoint for container probes."""
    worker_status = "running"
    if _worker_task is None:
        worker_status = "not_started"
    elif _worker_task.done():
        worker_status = "stopped"

    return {
        "status": "healthy",
        "service": "workflow",
        "temporal_worker": worker_status,
    }
