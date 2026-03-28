"""
Async Claude API client with retry, rate limiting, and token tracking.

All AI calls in Velora go through this wrapper — no direct anthropic imports
elsewhere in the service.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import anthropic
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from velora_common.logging import get_logger

logger = get_logger(__name__)

_DEFAULT_MODEL = "claude-sonnet-4-20250514"
_DEFAULT_TIMEOUT = 30.0
_MAX_RETRIES = 3


@dataclass(frozen=True)
class ClaudeResponse:
    """Structured response from Claude API."""

    content: str
    input_tokens: int
    output_tokens: int
    model: str
    stop_reason: Optional[str] = None


class ClaudeClient:
    """Reusable async Claude client with retry and token tracking."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = _DEFAULT_MODEL,
        timeout: float = _DEFAULT_TIMEOUT,
        max_tokens: int = 4096,
    ) -> None:
        resolved_key = api_key or os.environ.get(
            "ANTHROPIC_API_KEY"
        )
        if not resolved_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not set in environment"
            )

        self._client = anthropic.AsyncAnthropic(
            api_key=resolved_key,
            timeout=timeout,
        )
        self._model = model
        self._max_tokens = max_tokens

    async def send_message(
        self,
        *,
        system: str,
        messages: List[Dict[str, str]],
        max_tokens: Optional[int] = None,
        temperature: float = 0.2,
    ) -> ClaudeResponse:
        """Send a message to Claude with retry on rate limits."""
        return await self._send_with_retry(
            system=system,
            messages=messages,
            max_tokens=max_tokens or self._max_tokens,
            temperature=temperature,
        )

    @retry(
        retry=retry_if_exception_type(
            anthropic.RateLimitError
        ),
        stop=stop_after_attempt(_MAX_RETRIES),
        wait=wait_exponential(
            multiplier=1, min=1, max=8
        ),
        reraise=True,
    )
    async def _send_with_retry(
        self,
        *,
        system: str,
        messages: List[Dict[str, str]],
        max_tokens: int,
        temperature: float,
    ) -> ClaudeResponse:
        """Internal method with tenacity retry decorator."""
        try:
            response = await self._client.messages.create(
                model=self._model,
                max_tokens=max_tokens,
                system=system,
                messages=messages,
                temperature=temperature,
            )
        except anthropic.APITimeoutError:
            logger.error(
                "claude_timeout",
                model=self._model,
                timeout=self._client._client.timeout,
            )
            raise
        except anthropic.RateLimitError:
            logger.warning(
                "claude_rate_limited",
                model=self._model,
            )
            raise
        except anthropic.APIError as exc:
            logger.error(
                "claude_api_error",
                status=getattr(exc, "status_code", None),
                message=str(exc),
            )
            raise

        content = response.content[0].text if response.content else ""
        usage = response.usage

        logger.info(
            "claude_call_complete",
            model=response.model,
            input_tokens=usage.input_tokens,
            output_tokens=usage.output_tokens,
            stop_reason=response.stop_reason,
        )

        return ClaudeResponse(
            content=content,
            input_tokens=usage.input_tokens,
            output_tokens=usage.output_tokens,
            model=response.model,
            stop_reason=response.stop_reason,
        )

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self._client.close()
