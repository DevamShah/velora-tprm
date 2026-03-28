"""Redis Streams event bus for inter-service communication.

Provides publish/subscribe with consumer groups for load-balanced consumption.
Each service subscribes to relevant event streams and processes events.
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from typing import Any, AsyncGenerator, Callable, Coroutine
from uuid import uuid4

import redis.asyncio as aioredis
from pydantic import BaseModel, Field

from velora_common.logging import get_logger

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Event schema
# ---------------------------------------------------------------------------


class EventMetadata(BaseModel):
    """Metadata attached to every event."""

    source_service: str = ""
    correlation_id: str = Field(default_factory=lambda: str(uuid4()))


class Event(BaseModel):
    """Canonical event schema for inter-service communication."""

    id: str = Field(default_factory=lambda: str(uuid4()))
    type: str
    tenant_id: str | None = None
    actor_id: str | None = None
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    data: dict[str, Any] = Field(default_factory=dict)
    metadata: EventMetadata = Field(default_factory=EventMetadata)


# ---------------------------------------------------------------------------
# Publisher
# ---------------------------------------------------------------------------


class EventPublisher:
    """Publish domain events to Redis Streams with standard schema."""

    def __init__(
        self,
        redis_url: str,
        source_service: str = "unknown",
    ) -> None:
        self._redis = aioredis.from_url(redis_url, decode_responses=True)
        self._source_service = source_service

    async def publish(
        self,
        stream: str,
        event_type: str,
        data: dict[str, Any],
        *,
        tenant_id: str | None = None,
        actor_id: str | None = None,
        correlation_id: str | None = None,
    ) -> str:
        """Publish an event to a Redis Stream.

        Auto-generates event ID, sets timestamp to UTC now, and attaches
        source_service from config.  Uses ``XADD`` with ``MAXLEN ~10000``
        for bounded memory consumption.

        Returns the Redis message ID.
        """
        event = Event(
            type=event_type,
            tenant_id=tenant_id,
            actor_id=actor_id,
            data=data,
            metadata=EventMetadata(
                source_service=self._source_service,
                correlation_id=correlation_id or str(uuid4()),
            ),
        )

        message = {
            "event_id": event.id,
            "event_type": event.type,
            "tenant_id": event.tenant_id or "",
            "actor_id": event.actor_id or "",
            "timestamp": event.timestamp,
            "data": json.dumps(event.data),
            "source_service": event.metadata.source_service,
            "correlation_id": event.metadata.correlation_id,
        }

        msg_id: str = await self._redis.xadd(  # type: ignore[assignment]
            stream,
            message,
            maxlen=10_000,
            approximate=True,
        )

        logger.info(
            "event_published",
            stream=stream,
            event_type=event_type,
            event_id=event.id,
            msg_id=msg_id,
            correlation_id=event.metadata.correlation_id,
        )
        return msg_id

    async def close(self) -> None:
        """Close the underlying Redis connection."""
        await self._redis.aclose()


# ---------------------------------------------------------------------------
# Type alias for event handlers
# ---------------------------------------------------------------------------

EventHandler = Callable[[dict[str, Any]], Coroutine[Any, Any, None]]


# ---------------------------------------------------------------------------
# Consumer
# ---------------------------------------------------------------------------


class EventConsumer:
    """Subscribe to Redis Streams with consumer groups for load-balanced consumption.

    Supports multiple stream subscriptions, automatic group creation,
    and graceful error handling (log-and-continue).
    """

    def __init__(
        self,
        redis_url: str,
        group: str,
        consumer: str,
    ) -> None:
        self._redis = aioredis.from_url(redis_url, decode_responses=True)
        self._group = group
        self._consumer = consumer
        self._handlers: dict[str, list[EventHandler]] = {}
        self._streams: list[str] = []
        self._running = False

    # -- subscription helpers ------------------------------------------------

    def subscribe(
        self,
        stream: str,
        handler: EventHandler,
    ) -> None:
        """Register *handler* for events on *stream*.

        Multiple handlers per stream are supported.
        """
        if stream not in self._streams:
            self._streams.append(stream)
        self._handlers.setdefault(stream, []).append(handler)

    # -- consumer-group bootstrapping ----------------------------------------

    async def _ensure_groups(self) -> None:
        """Create consumer groups for every subscribed stream (idempotent)."""
        for stream in self._streams:
            try:
                await self._redis.xgroup_create(
                    stream,
                    self._group,
                    id="0",
                    mkstream=True,
                )
                logger.info(
                    "consumer_group_created",
                    stream=stream,
                    group=self._group,
                )
            except aioredis.ResponseError as exc:
                if "BUSYGROUP" not in str(exc):
                    raise
                # Group already exists — fine.

    # -- main consumption loop -----------------------------------------------

    async def run(
        self,
        count: int = 10,
        block_ms: int = 2000,
    ) -> None:
        """Read and process events in a continuous loop.

        Reads from all subscribed streams using ``XREADGROUP``, dispatches
        to registered handlers, and acknowledges each message.  On handler
        errors the message is logged and the loop continues.
        """
        await self._ensure_groups()
        self._running = True

        logger.info(
            "event_consumer_started",
            group=self._group,
            consumer=self._consumer,
            streams=self._streams,
        )

        while self._running:
            try:
                results = await self._redis.xreadgroup(
                    groupname=self._group,
                    consumername=self._consumer,
                    streams={s: ">" for s in self._streams},
                    count=count,
                    block=block_ms,
                )

                if not results:
                    continue

                for stream_name, messages in results:
                    for msg_id, raw in messages:
                        event = self._decode(raw)
                        event["msg_id"] = msg_id
                        event["_stream"] = stream_name

                        handlers = self._handlers.get(stream_name, [])
                        for handler in handlers:
                            try:
                                await handler(event)
                            except Exception:
                                logger.error(
                                    "event_handler_error",
                                    stream=stream_name,
                                    msg_id=msg_id,
                                    event_type=event.get("event_type"),
                                    exc_info=True,
                                )

                        # Acknowledge after all handlers have run (or failed)
                        await self._redis.xack(
                            stream_name,
                            self._group,
                            msg_id,
                        )

            except asyncio.CancelledError:
                logger.info("event_consumer_cancelled")
                break
            except Exception:
                logger.error(
                    "event_consumer_loop_error",
                    exc_info=True,
                )
                # Back off briefly to avoid tight error loops
                await asyncio.sleep(1)

        logger.info("event_consumer_stopped")

    # -- graceful shutdown ---------------------------------------------------

    def stop(self) -> None:
        """Signal the consumer loop to stop after the current iteration."""
        self._running = False

    async def close(self) -> None:
        """Stop the loop and close the Redis connection."""
        self.stop()
        await self._redis.aclose()

    # -- helpers -------------------------------------------------------------

    @staticmethod
    def _decode(raw: dict[str, str]) -> dict[str, Any]:
        """Decode a raw Redis hash into a typed event dict."""
        data_str = raw.get("data", "{}")
        try:
            data = json.loads(data_str)
        except (json.JSONDecodeError, TypeError):
            data = {}

        return {
            "event_id": raw.get("event_id", ""),
            "event_type": raw.get("event_type", ""),
            "tenant_id": raw.get("tenant_id") or None,
            "actor_id": raw.get("actor_id") or None,
            "timestamp": raw.get("timestamp", ""),
            "data": data,
            "source_service": raw.get("source_service", ""),
            "correlation_id": raw.get("correlation_id", ""),
        }

    # -- convenience iterator (for one-shot reads) ---------------------------

    async def consume(
        self,
        count: int = 10,
        block_ms: int = 5000,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Single-pass read from all subscribed streams.

        Yields decoded event dicts. Caller must call :meth:`acknowledge`
        to confirm processing.
        """
        await self._ensure_groups()

        results = await self._redis.xreadgroup(
            groupname=self._group,
            consumername=self._consumer,
            streams={s: ">" for s in self._streams},
            count=count,
            block=block_ms,
        )

        for _stream_name, messages in (results or []):
            for msg_id, raw in messages:
                event = self._decode(raw)
                event["msg_id"] = msg_id
                event["_stream"] = _stream_name
                yield event

    async def acknowledge(self, stream: str, msg_id: str) -> None:
        """Acknowledge a processed message."""
        await self._redis.xack(stream, self._group, msg_id)
