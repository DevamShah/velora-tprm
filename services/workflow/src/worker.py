"""Temporal worker for Velora TPRM workflows.

Connects to the Temporal server, registers all workflow definitions and
activity implementations, then runs the worker event loop.
"""

from __future__ import annotations

import asyncio
import os

from temporalio.client import Client
from temporalio.worker import Worker

from velora_common.logging import configure_logging, get_logger

from .activities import ALL_ACTIVITIES
from .workflows import ALL_WORKFLOWS

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

TEMPORAL_ADDRESS = os.getenv("TEMPORAL_ADDRESS", "temporal:7233")
TEMPORAL_NAMESPACE = os.getenv("TEMPORAL_NAMESPACE", "default")
TASK_QUEUE = os.getenv("TEMPORAL_TASK_QUEUE", "velora-tprm")


async def create_worker() -> Worker:
    """Create and return a configured Temporal worker (not yet started).

    The caller is responsible for calling ``await worker.run()`` or using
    the worker as an async context manager.
    """
    logger.info(
        "connecting_to_temporal",
        address=TEMPORAL_ADDRESS,
        namespace=TEMPORAL_NAMESPACE,
        task_queue=TASK_QUEUE,
    )

    client = await Client.connect(
        TEMPORAL_ADDRESS,
        namespace=TEMPORAL_NAMESPACE,
    )

    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=ALL_WORKFLOWS,
        activities=ALL_ACTIVITIES,
    )

    logger.info(
        "temporal_worker_created",
        workflows=[w.__name__ for w in ALL_WORKFLOWS],
        activities=[a.__name__ for a in ALL_ACTIVITIES],
    )

    return worker


async def run_worker() -> None:
    """Connect to Temporal and run the worker until cancelled.

    This is the main entry point used by the FastAPI lifespan and
    can also be run standalone via ``python -m src.worker``.
    """
    worker = await create_worker()

    logger.info("temporal_worker_starting", task_queue=TASK_QUEUE)

    try:
        await worker.run()
    except asyncio.CancelledError:
        logger.info("temporal_worker_cancelled")
    except Exception:
        logger.error("temporal_worker_error", exc_info=True)
        raise
    finally:
        logger.info("temporal_worker_stopped")


if __name__ == "__main__":
    configure_logging(os.getenv("LOG_LEVEL", "INFO"))
    asyncio.run(run_worker())
