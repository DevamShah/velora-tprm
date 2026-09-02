"""
API aggregation for complex frontend views.

Fetches data from multiple microservices in parallel and composes
a single response payload, reducing frontend round-trips.
"""

from __future__ import annotations

import asyncio
import uuid
from typing import Any

import httpx

from .config import get_settings

# Reusable timeout — 10s per upstream call
_TIMEOUT = httpx.Timeout(10.0, connect=5.0)


async def _fetch(
    client: httpx.AsyncClient,
    url: str,
    token: str,
    params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    GET a URL with bearer auth.  Returns parsed JSON on success,
    or an error dict on failure (never raises).

    Query values go through ``params`` so httpx encodes them.  Never
    interpolate caller-supplied values into ``url`` — that allows a
    caller to append their own parameters to an internal service call.
    """
    try:
        resp = await client.get(
            url,
            params=params,
            headers={"Authorization": f"Bearer {token}"},
            timeout=_TIMEOUT,
        )
        if resp.status_code == 200:
            return resp.json()
        return {"_error": True, "status": resp.status_code}
    except httpx.HTTPError:
        return {"_error": True, "status": 503}


async def dashboard_data(access_token: str) -> dict[str, Any]:
    """
    Aggregate dashboard data from multiple services in parallel.

    Returns a single dict with keys:
      vendors, assessments, findings, monitoring, scoring
    Each key contains the service response or an error marker.
    """
    settings = get_settings()
    async with httpx.AsyncClient() as client:
        vendors_task = _fetch(
            client,
            f"{settings.VENDOR_SERVICE_URL}/api/v1/vendors",
            access_token,
            params={"page": 1, "size": 5},
        )
        assessments_task = _fetch(
            client,
            f"{settings.ASSESSMENT_SERVICE_URL}/api/v1/assessments",
            access_token,
            params={"page": 1, "size": 5},
        )
        findings_task = _fetch(
            client,
            f"{settings.FINDING_SERVICE_URL}/api/v1/findings?page=1&size=10",
            access_token,
        )
        monitoring_task = _fetch(
            client,
            f"{settings.MONITORING_SERVICE_URL}/api/v1/monitoring/alerts?page=1&size=5",
            access_token,
        )
        scoring_task = _fetch(
            client,
            f"{settings.SCORING_SERVICE_URL}/api/v1/scoring/summary",
            access_token,
        )

        results = await asyncio.gather(
            vendors_task,
            assessments_task,
            findings_task,
            monitoring_task,
            scoring_task,
            return_exceptions=True,
        )

    keys = ["vendors", "assessments", "findings", "monitoring", "scoring"]
    dashboard: dict[str, Any] = {}
    for key, result in zip(keys, results):
        if isinstance(result, Exception):
            dashboard[key] = {"_error": True, "status": 503}
        else:
            dashboard[key] = result

    return dashboard


async def vendor_full(
    vendor_id: uuid.UUID | str,
    access_token: str,
) -> dict[str, Any]:
    """
    Aggregate full vendor detail from multiple services in parallel.

    Returns a single dict with keys:
      vendor, assessments, scores, findings, timeline

    ``vendor_id`` is coerced to ``uuid.UUID`` before it reaches a URL.
    The route already types it as a UUID, so this is the second line of
    defence: it guarantees the value is 36 hex-and-dash characters and
    cannot carry a path segment, an extra query parameter, or a
    fragment into an internal service call.  Raises ``ValueError`` on
    anything else.
    """
    vid = str(uuid.UUID(str(vendor_id)))
    settings = get_settings()
    async with httpx.AsyncClient() as client:
        vendor_task = _fetch(
            client,
            f"{settings.VENDOR_SERVICE_URL}/api/v1/vendors/{vid}",
            access_token,
        )
        assessments_task = _fetch(
            client,
            f"{settings.ASSESSMENT_SERVICE_URL}/api/v1/assessments",
            access_token,
            params={"vendor_id": vid},
        )
        scores_task = _fetch(
            client,
            f"{settings.SCORING_SERVICE_URL}/api/v1/scoring/vendor/{vid}",
            access_token,
        )
        findings_task = _fetch(
            client,
            f"{settings.FINDING_SERVICE_URL}/api/v1/findings",
            access_token,
            params={"vendor_id": vid},
        )
        timeline_task = _fetch(
            client,
            f"{settings.MONITORING_SERVICE_URL}"
            f"/api/v1/monitoring/vendor/{vid}/timeline",
            access_token,
        )

        results = await asyncio.gather(
            vendor_task,
            assessments_task,
            scores_task,
            findings_task,
            timeline_task,
            return_exceptions=True,
        )

    keys = ["vendor", "assessments", "scores", "findings", "timeline"]
    full: dict[str, Any] = {}
    for key, result in zip(keys, results):
        if isinstance(result, Exception):
            full[key] = {"_error": True, "status": 503}
        else:
            full[key] = result

    return full
