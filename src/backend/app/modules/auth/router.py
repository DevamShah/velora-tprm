"""
Auth API endpoints — login, refresh, logout, profile.

All responses follow RFC 7807 error shape on failure.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.logging import get_logger
from app.core.security import FieldEncryptor
from app.modules.auth.schemas import (
    LoginRequest,
    RefreshRequest,
    RoleResponse,
    TokenResponse,
    UserResponse,
)
from app.modules.auth.service import AuthService

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


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
    settings = get_settings()
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
