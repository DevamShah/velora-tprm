"""
Auth API endpoints — login, refresh, logout, profile.

All responses follow RFC 7807 error shape on failure.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from velora_common.config import BaseServiceSettings as _Settings
from velora_common.db import get_db
from velora_common.auth import get_current_user
from velora_common.logging import get_logger
from velora_common.security import FieldEncryptor
from .schemas import (
    LoginRequest,
    RefreshRequest,
    RoleResponse,
    TokenResponse,
    UserResponse,
)
from .service import AuthService
from .sso import SSOProviderConfig

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


# -- SSO Endpoints --------------------------------------------------


@router.get("/sso/authorize")
async def sso_authorize(
    tenant_slug: str,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """Initiate SSO login — returns redirect URL."""
    import secrets
    # TODO: Look up SSO config from DB by tenant_slug
    _ = tenant_slug  # will be used when SSO config lookup is implemented
    # For now, return a placeholder
    state = secrets.token_urlsafe(32)
    nonce = secrets.token_urlsafe(32)
    return {
        "redirect_url": "",
        "state": state,
        "message": "SSO provider not configured for this tenant",
    }


@router.post("/sso/callback")
async def sso_callback(
    code: str,
    state: str,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """Handle SSO callback — exchange code for tokens."""
    # TODO: Validate state, look up tenant config,
    # call SSOService.handle_oidc_callback()
    # For MVP: structure is ready, needs tenant SSO config CRUD
    return {
        "error": "SSO callback handler ready — tenant SSO config CRUD needed",
    }


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
async def login(
    body: LoginRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    """Authenticate with email + password, receive JWT pair."""
    service = AuthService(session)
    user = await service.authenticate(body.email, body.password)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    logger.info("user_login_success", user_id=str(user.id))
    return await service.create_tokens(user)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
async def refresh(
    body: RefreshRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    """Rotate a refresh token and receive a fresh JWT pair."""
    service = AuthService(session)
    result = await service.refresh_tokens(body.refresh_token)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or revoked refresh token",
        )

    return result


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout(
    body: RefreshRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
    _current_user: Annotated[dict, Depends(get_current_user)],
) -> None:
    """Revoke the provided refresh token."""
    service = AuthService(session)
    await service.revoke_refresh_token(body.refresh_token)


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
async def me(
    current_user: Annotated[dict, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> UserResponse:
    """Return the authenticated user's profile with roles."""
    service = AuthService(session)
    settings = _Settings()
    encryptor = FieldEncryptor(settings.ENCRYPTION_KEY)

    user = await service.get_user_by_id(
        str(current_user["user_id"])
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    permissions = service._collect_permissions(user)
    roles = [
        RoleResponse(
            id=ur.role.id,
            name=ur.role.name,
            permissions=ur.role.permissions or [],
        )
        for ur in user.user_roles
        if ur.role is not None
    ]

    return UserResponse(
        id=user.id,
        email=encryptor.decrypt(user.email_encrypted),
        first_name=user.first_name,
        last_name=user.last_name,
        is_active=user.is_active,
        mfa_enabled=user.mfa_enabled,
        last_login_at=user.last_login_at,
        roles=roles,
        permissions=permissions,
    )
