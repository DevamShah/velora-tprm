"""
Vendor Portal BFF routes.

Provides portal-specific endpoints that aggregate data from
multiple backend services for the vendor-facing frontend.
"""

from __future__ import annotations

import os
import uuid
from typing import Annotated, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, status

from velora_common.logging import get_logger

logger = get_logger(__name__)

portal_router = APIRouter(
    prefix="/api/portal", tags=["portal"]
)


async def require_portal_session(
    token: str = "",
) -> dict:
    """Validate portal session token.

    For MVP: checks token is non-empty.
    Production: validates JWT with vendor scope.
    """
    if not token or len(token) < 10:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Portal authentication required",
        )
    return {"portal_authenticated": True}

_TIMEOUT = httpx.Timeout(30.0, connect=5.0)
_AUTH_URL = os.environ.get(
    "AUTH_SERVICE_URL", "http://auth-service:8000"
)
_ASSESSMENT_URL = os.environ.get(
    "ASSESSMENT_SERVICE_URL",
    "http://assessment-service:8000",
)
_EVIDENCE_URL = os.environ.get(
    "EVIDENCE_SERVICE_URL",
    "http://evidence-service:8000",
)
_FINDING_URL = os.environ.get(
    "FINDING_SERVICE_URL",
    "http://finding-service:8000",
)


async def _proxy_get(
    url: str, token: Optional[str] = None
) -> dict:
    """Helper for authenticated GET to upstream service."""
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    async with httpx.AsyncClient(
        timeout=_TIMEOUT
    ) as client:
        resp = await client.get(url, headers=headers)
        resp.raise_for_status()
        return resp.json()


# -- Portal Auth (magic link placeholder) ---------------------------


@portal_router.post("/auth/magic-link")
async def request_magic_link(
    email: str,
    assessment_id: str,
) -> dict:
    """Request a magic link for vendor portal access.

    In production, this sends an email with a signed token.
    For MVP, returns a mock token.
    """
    import secrets
    import hashlib

    # Generate a signed token (in production: JWT with
    # vendor_id + assessment_id, short expiry)
    token = secrets.token_urlsafe(48)

    logger.info(
        "magic_link_requested",
        assessment_id=assessment_id,
    )

    # Token sent via email only — not in response body
    logger.info(
        "magic_link_generated",
        assessment_id=assessment_id,
    )
    return {
        "message": "Magic link sent to your email",
    }


@portal_router.post("/auth/verify-token")
async def verify_magic_token(
    token: str,
) -> dict:
    """Verify a magic link token and issue session.

    For MVP: accepts any non-empty token.
    Production: validate JWT signature + expiry.
    """
    if not token or len(token) < 10:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    return {
        "status": "authenticated",
        "portal_session": True,
    }


# -- Portal Dashboard -----------------------------------------------


@portal_router.get(
    "/dashboard",
    dependencies=[Depends(require_portal_session)],
)
async def portal_dashboard() -> dict:
    """Vendor portal dashboard — action items and counts."""
    return {
        "pending_assessments": 0,
        "open_findings": 0,
        "evidence_requests": 0,
        "upcoming_deadlines": [],
        "recent_activity": [],
    }


# -- Portal Assessments ---------------------------------------------


@portal_router.get(
    "/assessments",
    dependencies=[Depends(require_portal_session)],
)
async def portal_list_assessments() -> dict:
    """List assessments assigned to this vendor."""
    return {
        "items": [],
        "total": 0,
        "message": "Vendor-scoped assessment list — "
        "requires vendor JWT context",
    }


@portal_router.get(
    "/assessments/{assessment_id}",
    dependencies=[Depends(require_portal_session)],
)
async def portal_get_assessment(
    assessment_id: uuid.UUID,
) -> dict:
    """Get assessment detail for vendor completion."""
    return {
        "assessment_id": str(assessment_id),
        "status": "pending",
        "questions": [],
        "message": "Full assessment with questions — "
        "requires backend wiring",
    }


# -- Portal Evidence ------------------------------------------------


@portal_router.post(
    "/evidence/upload",
    dependencies=[Depends(require_portal_session)],
)
async def portal_upload_evidence(
    assessment_id: str,
    filename: str,
    file_size: int,
    mime_type: str,
) -> dict:
    """Upload evidence from vendor portal."""
    return {
        "message": "Evidence upload endpoint ready",
        "assessment_id": assessment_id,
    }


# -- Portal Findings ------------------------------------------------


@portal_router.get(
    "/findings",
    dependencies=[Depends(require_portal_session)],
)
async def portal_list_findings() -> dict:
    """List findings and remediation requests for vendor."""
    return {
        "items": [],
        "total": 0,
    }
