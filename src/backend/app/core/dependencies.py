"""
FastAPI dependency injection factories.

Provides session management, user extraction from JWT,
tenant isolation, and permission enforcement.
"""

from __future__ import annotations

import uuid
from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db, set_tenant_context
from app.core.logging import (
    get_logger,
    tenant_id_ctx,
    user_id_ctx,
)
from app.core.security import verify_token

logger = get_logger(__name__)


def _extract_bearer_token(request: Request) -> str:
    """Pull the Bearer token from the Authorization header."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or malformed Authorization header",
        )
    return auth_header[7:]


async def get_current_user(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """
    Decode the JWT and return user metadata.

    Sets logging context vars for tenant_id and user_id.
    """
    from app.core.config import get_settings

    settings = get_settings()
    token = _extract_bearer_token(request)

    payload = verify_token(
        token,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
        expected_type="access",
    )
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
        )

    # Inject RLS context for this session
    tid = payload.get("tenant_id")
    uid = payload.get("sub")

    if tid is None or uid is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing required claims",
        )

    await set_tenant_context(session, tid)

    # Populate structured-logging context vars
    tenant_id_ctx.set(tid)
    user_id_ctx.set(uid)

    return {
        "user_id": uuid.UUID(uid),
        "tenant_id": uuid.UUID(tid),
        "roles": payload.get("roles", []),
        "permissions": payload.get("permissions", []),
    }


async def get_tenant_id(
    current_user: Annotated[dict, Depends(get_current_user)],
) -> uuid.UUID:
    """Extract the tenant ID from the authenticated user context."""
    return current_user["tenant_id"]


def require_permission(permission: str) -> Callable:
    """
    Factory that returns a dependency enforcing a single permission.

    Usage:
        @router.get(
            "/foo",
            dependencies=[
                Depends(require_permission("foo.read"))
            ],
        )
    """

    async def _check(
        current_user: Annotated[dict, Depends(get_current_user)],
    ) -> dict:
        user_perms: list[str] = current_user.get("permissions", [])
        if permission not in user_perms:
            logger.warning(
                "permission_denied",
                required=permission,
                user_id=str(current_user["user_id"]),
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission required: {permission}",
            )
        return current_user

    return _check
