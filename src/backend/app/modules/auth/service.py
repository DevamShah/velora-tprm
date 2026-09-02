"""
Auth business logic — login, token lifecycle, user lookup.

All DB queries run inside the caller-provided async session so
the transaction boundary is controlled by the FastAPI dependency.
"""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime, timedelta

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import get_settings
from app.core.logging import get_logger
from app.core.security import (
    FieldEncryptor,
    create_access_token,
    create_refresh_token,
    verify_password,
    verify_token,
)
from app.modules.auth.models import (
    RefreshToken,
    User,
    UserRole,
)
from app.modules.auth.schemas import TokenResponse

logger = get_logger(__name__)


class AuthService:
    """Stateless service — receives a session per call."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._settings = get_settings()
        self._encryptor = FieldEncryptor(self._settings.ENCRYPTION_KEY)

    # ── Authentication ────────────────────────────────────────

    async def authenticate(self, email: str, password: str) -> User | None:
        """
        Verify credentials and return the User or None.

        Lookup uses HMAC hash of the email so we never
        decrypt every row to find a match.
        """
        email_hash = self._encryptor.hmac_hash(email)

        result = await self._session.execute(
            select(User)
            .options(selectinload(User.user_roles).selectinload(UserRole.role))
            .where(
                User.email_hash == email_hash,
                User.is_active.is_(True),
            )
        )
        user = result.scalars().first()

        if user is None:
            return None

        if not verify_password(password, user.password_hash):
            logger.info("login_failed_bad_password")
            return None

        # Stamp last login
        user.last_login_at = datetime.now(UTC)
        return user

    # ── Token lifecycle ───────────────────────────────────────

    async def create_tokens(self, user: User) -> TokenResponse:
        """Issue an access + refresh token pair for a user."""
        permissions = self._collect_permissions(user)

        token_data = {
            "sub": str(user.id),
            "tenant_id": str(user.tenant_id),
            "roles": [ur.role.name for ur in user.user_roles],
            "permissions": permissions,
        }

        access = create_access_token(
            data=token_data,
            secret_key=self._settings.JWT_SECRET_KEY,
            algorithm=self._settings.JWT_ALGORITHM,
            expires_minutes=(self._settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        refresh = create_refresh_token(
            data=token_data,
            secret_key=self._settings.JWT_SECRET_KEY,
            algorithm=self._settings.JWT_ALGORITHM,
            expires_days=(self._settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
        )

        # Persist refresh token hash
        await self._store_refresh_token(user, refresh)

        return TokenResponse(
            access_token=access,
            refresh_token=refresh,
            expires_in=(self._settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60),
        )

    async def refresh_tokens(
        self, refresh_token_raw: str
    ) -> TokenResponse | None:
        """
        Rotate a refresh token — revoke the old, issue a new pair.

        Returns None if the token is invalid or already revoked.
        """
        payload = verify_token(
            refresh_token_raw,
            self._settings.JWT_SECRET_KEY,
            algorithm=self._settings.JWT_ALGORITHM,
            expected_type="refresh",
        )
        if payload is None:
            return None

        token_hash = _sha256(refresh_token_raw)
        result = await self._session.execute(
            select(RefreshToken).where(
                RefreshToken.token_hash == token_hash,
                RefreshToken.revoked_at.is_(None),
            )
        )
        stored = result.scalars().first()
        if stored is None:
            logger.warning("refresh_token_not_found_or_revoked")
            return None

        # Revoke the old token
        stored.revoked_at = datetime.now(UTC)

        # Fetch fresh user
        user = await self.get_user_by_id(payload["sub"])
        if user is None or not user.is_active:
            return None

        return await self.create_tokens(user)

    async def revoke_refresh_token(self, refresh_token_raw: str) -> bool:
        """Revoke a single refresh token. Returns True on success."""
        token_hash = _sha256(refresh_token_raw)
        result = await self._session.execute(
            update(RefreshToken)
            .where(
                RefreshToken.token_hash == token_hash,
                RefreshToken.revoked_at.is_(None),
            )
            .values(revoked_at=datetime.now(UTC))
        )
        return result.rowcount > 0  # type: ignore[return-value]

    # ── User queries ──────────────────────────────────────────

    async def get_user_by_id(self, user_id: str) -> User | None:
        """Fetch a user by primary key with roles eagerly loaded."""
        result = await self._session.execute(
            select(User)
            .options(selectinload(User.user_roles).selectinload(UserRole.role))
            .where(User.id == user_id)
        )
        return result.scalars().first()

    async def get_user_permissions(self, user_id: str) -> list[str]:
        """Aggregate distinct permissions across all user roles."""
        user = await self.get_user_by_id(user_id)
        if user is None:
            return []
        return self._collect_permissions(user)

    # ── Helpers ────────────────────────────────────────────────

    @staticmethod
    def _collect_permissions(user: User) -> list[str]:
        """Flatten permissions from all assigned roles."""
        perms: set[str] = set()
        for user_role in user.user_roles:
            if user_role.role and user_role.role.permissions:
                perms.update(user_role.role.permissions)
        return sorted(perms)

    async def _store_refresh_token(self, user: User, raw_token: str) -> None:
        """Persist a hashed refresh token to the database."""
        expires_at = datetime.now(UTC) + timedelta(
            days=self._settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
        )
        record = RefreshToken(
            user_id=user.id,
            tenant_id=user.tenant_id,
            token_hash=_sha256(raw_token),
            expires_at=expires_at,
        )
        self._session.add(record)
        await self._session.flush()


def _sha256(value: str) -> str:
    """Produce a hex SHA-256 digest for token storage."""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()
