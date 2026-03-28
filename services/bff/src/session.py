"""
Redis-backed session management for the BFF.

Sessions store JWT tokens server-side, keyed by an opaque session ID.
The session ID is transmitted to the browser as an httpOnly cookie.
This keeps access/refresh tokens off the client entirely.
"""

from __future__ import annotations

import json
import secrets
from dataclasses import dataclass
from typing import Any

import redis.asyncio as aioredis

from .config import get_settings

_SESSION_PREFIX = "bff:session:"


@dataclass(frozen=True, slots=True)
class SessionData:
    """Data stored in a session."""

    access_token: str
    refresh_token: str
    user_id: str
    tenant_id: str
    email: str
    roles: list[str]


class SessionManager:
    """Manages server-side sessions backed by Redis."""

    def __init__(self, redis_client: aioredis.Redis) -> None:
        self._redis = redis_client
        self._settings = get_settings()

    @staticmethod
    def _key(session_id: str) -> str:
        return f"{_SESSION_PREFIX}{session_id}"

    @staticmethod
    def _generate_id() -> str:
        """Cryptographically secure 32-byte hex session ID."""
        return secrets.token_hex(32)

    async def create_session(
        self,
        tokens: dict[str, Any],
        user_info: dict[str, Any],
    ) -> str:
        """
        Create a new session with JWT tokens and user metadata.

        Returns the session ID to set in the httpOnly cookie.
        """
        session_id = self._generate_id()
        data = {
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "user_id": str(user_info.get("id", "")),
            "tenant_id": str(user_info.get("tenant_id", "")),
            "email": str(user_info.get("email", "")),
            "roles": user_info.get("roles", []),
        }
        await self._redis.setex(
            self._key(session_id),
            self._settings.SESSION_EXPIRE_SECONDS,
            json.dumps(data),
        )
        return session_id

    async def get_session(self, session_id: str) -> SessionData | None:
        """Retrieve session data. Returns None if expired or missing."""
        raw = await self._redis.get(self._key(session_id))
        if raw is None:
            return None
        data = json.loads(raw)
        return SessionData(
            access_token=data["access_token"],
            refresh_token=data["refresh_token"],
            user_id=data["user_id"],
            tenant_id=data["tenant_id"],
            email=data["email"],
            roles=data.get("roles", []),
        )

    async def update_tokens(
        self,
        session_id: str,
        access_token: str,
        refresh_token: str,
    ) -> bool:
        """
        Update the JWT tokens in an existing session (after refresh).

        Returns False if the session does not exist.
        """
        raw = await self._redis.get(self._key(session_id))
        if raw is None:
            return False
        data = json.loads(raw)
        data["access_token"] = access_token
        data["refresh_token"] = refresh_token
        ttl = await self._redis.ttl(self._key(session_id))
        if ttl < 0:
            ttl = self._settings.SESSION_EXPIRE_SECONDS
        await self._redis.setex(
            self._key(session_id),
            ttl,
            json.dumps(data),
        )
        return True

    async def destroy_session(self, session_id: str) -> None:
        """Remove a session (logout)."""
        await self._redis.delete(self._key(session_id))

    async def refresh_ttl(self, session_id: str) -> None:
        """Reset the session TTL on activity (sliding expiry)."""
        await self._redis.expire(
            self._key(session_id),
            self._settings.SESSION_EXPIRE_SECONDS,
        )
