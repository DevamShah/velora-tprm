"""
Generic API proxy for the BFF.

Forwards requests that the BFF does not handle directly to the
appropriate upstream microservice, injecting the JWT from the
server-side session.
"""

from __future__ import annotations

from typing import Any

import httpx
from fastapi import Request, Response

from .config import get_settings

_TIMEOUT = httpx.Timeout(30.0, connect=5.0)

# Headers that must NOT be forwarded to upstream services
_HOP_BY_HOP = frozenset({
    "host",
    "connection",
    "keep-alive",
    "transfer-encoding",
    "te",
    "trailer",
    "upgrade",
    "proxy-authorization",
    "proxy-authenticate",
})


def _build_upstream_url(path: str, query: str | None) -> str | None:
    """
    Resolve the upstream service URL for a given request path.

    Returns the full URL (service base + path + query) or None if
    no service matches the prefix.
    """
    settings = get_settings()
    base_url = settings.service_url_for_prefix(path)
    if base_url is None:
        return None
    url = f"{base_url}{path}"
    if query:
        url = f"{url}?{query}"
    return url


async def proxy_request(
    request: Request,
    access_token: str,
) -> Response:
    """
    Forward the incoming request to the matching upstream service.

    - Injects Authorization header from session.
    - Strips hop-by-hop headers.
    - Returns the upstream response (status, headers, body) as-is.
    """
    path = request.url.path
    query = request.url.query or None
    upstream_url = _build_upstream_url(path, query)

    if upstream_url is None:
        return Response(
            content='{"detail":"No upstream service for this path"}',
            status_code=502,
            media_type="application/json",
        )

    # Build forwarded headers
    headers: dict[str, str] = {}
    for key, value in request.headers.items():
        if key.lower() not in _HOP_BY_HOP:
            headers[key] = value
    headers["Authorization"] = f"Bearer {access_token}"

    # Read request body (empty for GET/DELETE)
    body = await request.body()

    async with httpx.AsyncClient() as client:
        try:
            upstream_resp = await client.request(
                method=request.method,
                url=upstream_url,
                headers=headers,
                content=body if body else None,
                timeout=_TIMEOUT,
            )
        except httpx.ConnectError:
            return Response(
                content='{"detail":"Upstream service unavailable"}',
                status_code=503,
                media_type="application/json",
            )
        except httpx.TimeoutException:
            return Response(
                content='{"detail":"Upstream service timeout"}',
                status_code=504,
                media_type="application/json",
            )

    # Build response, stripping hop-by-hop from upstream
    response_headers: dict[str, str] = {}
    for key, value in upstream_resp.headers.items():
        if key.lower() not in _HOP_BY_HOP and key.lower() != "content-encoding":
            response_headers[key] = value

    return Response(
        content=upstream_resp.content,
        status_code=upstream_resp.status_code,
        headers=response_headers,
        media_type=upstream_resp.headers.get("content-type", "application/json"),
    )
