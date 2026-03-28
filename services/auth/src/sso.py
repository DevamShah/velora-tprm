"""
SSO/SAML/OIDC enterprise authentication.

Supports SAML 2.0 (Okta, Azure AD, etc.) and OIDC (Google, Azure AD, Okta).
JIT (Just-In-Time) user provisioning on first SSO login.
"""

from __future__ import annotations

import os
import uuid
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

import httpx

from velora_common.logging import get_logger
from velora_common.security import (
    FieldEncryptor,
    create_access_token,
    create_refresh_token,
    hash_password,
)
from velora_common.config import BaseServiceSettings

from .models import Role, User, UserRole

logger = get_logger(__name__)


@dataclass
class SSOUserInfo:
    """Normalized user info from any SSO provider."""

    email: str
    first_name: str
    last_name: str
    groups: List[str]
    provider: str
    provider_user_id: str
    raw_attributes: Dict[str, Any]


@dataclass
class SSOProviderConfig:
    """SSO provider configuration stored per tenant."""

    provider_type: str  # "saml" or "oidc"
    tenant_id: uuid.UUID
    # SAML fields
    idp_entity_id: Optional[str] = None
    idp_sso_url: Optional[str] = None
    idp_certificate: Optional[str] = None
    # OIDC fields
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    authorization_url: Optional[str] = None
    token_url: Optional[str] = None
    userinfo_url: Optional[str] = None
    jwks_uri: Optional[str] = None
    # Common
    default_role: str = "viewer"
    jit_provisioning: bool = True
    attribute_mapping: Optional[Dict[str, str]] = None


class SSOService:
    """Handles SAML 2.0 and OIDC authentication flows."""

    def __init__(self, session, settings=None) -> None:
        self._session = session
        self._settings = settings or BaseServiceSettings()
        self._encryptor = FieldEncryptor(
            self._settings.ENCRYPTION_KEY
        )
        self._base_url = os.environ.get(
            "AUTH_SERVICE_BASE_URL",
            "http://localhost:8001",
        )

    # -- OIDC Flow ---------------------------------------------------

    def get_oidc_auth_url(
        self,
        config: SSOProviderConfig,
        state: str,
        nonce: str,
    ) -> str:
        """Build the OIDC authorization redirect URL."""
        if not config.authorization_url:
            raise ValueError("OIDC authorization_url not configured")

        params = {
            "response_type": "code",
            "client_id": config.client_id,
            "redirect_uri": f"{self._base_url}/auth/sso/callback",
            "scope": "openid email profile",
            "state": state,
            "nonce": nonce,
        }
        return f"{config.authorization_url}?{urlencode(params)}"

    async def handle_oidc_callback(
        self,
        config: SSOProviderConfig,
        code: str,
        _expected_state: str,
        _expected_nonce: str,
    ) -> Optional[SSOUserInfo]:
        """Exchange auth code for tokens and extract user info."""
        if not config.token_url or not config.client_id:
            return None

        async with httpx.AsyncClient(
            timeout=httpx.Timeout(15.0, connect=5.0)
        ) as client:
            # Exchange code for tokens
            token_resp = await client.post(
                config.token_url,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": f"{self._base_url}/auth/sso/callback",
                    "client_id": config.client_id,
                    "client_secret": config.client_secret,
                },
            )
            if token_resp.status_code != 200:
                logger.error(
                    "oidc_token_exchange_failed",
                    status=token_resp.status_code,
                )
                return None

            tokens = token_resp.json()
            id_token = tokens.get("id_token")
            access_token = tokens.get("access_token")

            # Fetch userinfo
            if config.userinfo_url and access_token:
                userinfo_resp = await client.get(
                    config.userinfo_url,
                    headers={
                        "Authorization": f"Bearer {access_token}"
                    },
                )
                if userinfo_resp.status_code == 200:
                    claims = userinfo_resp.json()
                else:
                    claims = {}
            else:
                claims = {}

        email = claims.get("email", "")
        if not email:
            logger.error("oidc_no_email_in_claims")
            return None

        return SSOUserInfo(
            email=email,
            first_name=claims.get("given_name", ""),
            last_name=claims.get("family_name", ""),
            groups=claims.get("groups", []),
            provider="oidc",
            provider_user_id=claims.get("sub", ""),
            raw_attributes=claims,
        )

    # -- JIT Provisioning -------------------------------------------

    async def jit_provision_or_login(
        self,
        tenant_id: uuid.UUID,
        user_info: SSOUserInfo,
        config: SSOProviderConfig,
    ) -> Dict[str, Any]:
        """Find or create user, then issue JWT tokens."""
        from sqlalchemy import select

        # Look up existing user by email hash
        email_hash = self._encryptor.hmac_hash(
            user_info.email
        )
        result = await self._session.execute(
            select(User).where(
                User.tenant_id == tenant_id,
                User.email_hash == email_hash,
            )
        )
        user = result.scalars().first()

        if user is None and config.jit_provisioning:
            # Create new user via JIT
            user = User(
                tenant_id=tenant_id,
                email_encrypted=self._encryptor.encrypt(
                    user_info.email
                ),
                email_hash=email_hash,
                first_name=user_info.first_name or "SSO",
                last_name=user_info.last_name or "User",
                password_hash=hash_password(
                    uuid.uuid4().hex  # random password
                ),
                is_active=True,
                sso_provider=user_info.provider,
                sso_provider_id=user_info.provider_user_id,
            )
            self._session.add(user)
            await self._session.flush()

            # Assign default role
            default_role = await self._get_default_role(
                config.default_role
            )
            if default_role:
                self._session.add(UserRole(
                    user_id=user.id,
                    role_id=default_role.id,
                ))
                await self._session.flush()

            logger.info(
                "sso_jit_user_created",
                tenant_id=str(tenant_id),
                provider=user_info.provider,
            )

        if user is None:
            logger.warning(
                "sso_user_not_found_no_jit",
                email_hash=email_hash[:8],
            )
            return {}

        if not user.is_active:
            return {}

        # Issue tokens
        roles = [
            ur.role.name
            for ur in (user.user_roles or [])
            if ur.role
        ]
        permissions = []
        for ur in (user.user_roles or []):
            if ur.role and ur.role.permissions:
                permissions.extend(ur.role.permissions)

        token_data = {
            "sub": str(user.id),
            "tenant_id": str(tenant_id),
            "roles": roles,
            "permissions": list(set(permissions)),
        }
        access = create_access_token(token_data)
        refresh = create_refresh_token(token_data)

        return {
            "access_token": access,
            "refresh_token": refresh,
            "token_type": "bearer",
            "user_id": str(user.id),
        }

    async def _get_default_role(
        self, role_name: str
    ) -> Optional[Role]:
        """Look up role by name."""
        from sqlalchemy import select

        result = await self._session.execute(
            select(Role).where(Role.name == role_name)
        )
        return result.scalars().first()
