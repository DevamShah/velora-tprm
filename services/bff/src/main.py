"""
FastAPI application for Velora BFF (Backend-for-Frontend) Service.

Handles:
- Server-side session management (httpOnly cookies + Redis)
- API aggregation for complex frontend views (dashboard, vendor detail)
- Generic proxy for all /api/v1/* requests (injects JWT from session)

The BFF never touches the database directly — it delegates to
upstream microservices and manages session state in Redis.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

import httpx
import redis.asyncio as aioredis
from fastapi import (
    Cookie,
    FastAPI,
    HTTPException,
    Request,
    Response,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field

from .aggregator import dashboard_data, vendor_full
from .config import get_settings
from .proxy import proxy_request
from .session import SessionManager

# ── Module state ──────────────────────────────────────────────────────────

_redis: aioredis.Redis | None = None
_session_mgr: SessionManager | None = None


def _get_session_mgr() -> SessionManager:
    """Return the session manager singleton (fails fast if not initialised)."""
    if _session_mgr is None:
        raise RuntimeError("SessionManager not initialised — app not started")
    return _session_mgr


# ── Request / response schemas ────────────────────────────────────────────


class LoginRequest(BaseModel):
    """Credentials submitted by the frontend login form."""

    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class LoginResponse(BaseModel):
    """Returned on successful BFF login."""

    user_id: str
    email: str
    first_name: str
    last_name: str
    roles: list[dict[str, Any]]
    permissions: list[str]


class MeResponse(BaseModel):
    """Current user profile from session."""

    id: str
    email: str
    first_name: str
    last_name: str
    is_active: bool
    mfa_enabled: bool
    roles: list[dict[str, Any]]
    permissions: list[str]


# ── Lifespan ──────────────────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator:
    """Open and close the Redis connection pool."""
    global _redis, _session_mgr

    settings = get_settings()
    _redis = aioredis.from_url(
        settings.REDIS_URL,
        decode_responses=True,
    )
    _session_mgr = SessionManager(_redis)
    yield
    if _redis:
        await _redis.aclose()


# ── App construction ──────────────────────────────────────────────────────


def create_app() -> FastAPI:
    """Build the FastAPI application with all routes."""
    settings = get_settings()

    app = FastAPI(
        title="Velora BFF Service",
        version="2.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Health ────────────────────────────────────────────────────────

    @app.get("/health", tags=["infra"])
    async def health() -> dict:
        return {"status": "healthy", "service": "bff"}

    # ── Auth endpoints (cookie-based) ─────────────────────────────────

    @app.post(
        "/api/bff/login",
        response_model=LoginResponse,
        status_code=status.HTTP_200_OK,
        tags=["bff-auth"],
    )
    async def bff_login(body: LoginRequest, response: Response) -> LoginResponse:
        """
        Authenticate via the auth-service, store tokens server-side,
        and return an httpOnly session cookie.
        """
        sm = _get_session_mgr()

        # 1. Forward credentials to auth-service
        async with httpx.AsyncClient() as client:
            try:
                auth_resp = await client.post(
                    f"{settings.AUTH_SERVICE_URL}/api/v1/auth/login",
                    json={"email": body.email, "password": body.password},
                    timeout=10.0,
                )
            except httpx.HTTPError:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Auth service unavailable",
                )

        if auth_resp.status_code != 200:
            raise HTTPException(
                status_code=auth_resp.status_code,
                detail=auth_resp.json().get("detail", "Authentication failed"),
            )

        tokens = auth_resp.json()

        # 2. Fetch user profile with the fresh access token
        async with httpx.AsyncClient() as client:
            try:
                me_resp = await client.get(
                    f"{settings.AUTH_SERVICE_URL}/api/v1/auth/me",
                    headers={"Authorization": f"Bearer {tokens['access_token']}"},
                    timeout=10.0,
                )
            except httpx.HTTPError:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Auth service unavailable",
                )

        if me_resp.status_code != 200:
            raise HTTPException(
                status_code=me_resp.status_code,
                detail="Failed to retrieve user profile",
            )

        user_info = me_resp.json()

        # 3. Create server-side session
        session_id = await sm.create_session(tokens, user_info)

        # 4. Set httpOnly cookie
        response.set_cookie(
            key=settings.SESSION_COOKIE_NAME,
            value=session_id,
            httponly=True,
            secure=settings.SESSION_COOKIE_SECURE,
            samesite="lax",
            max_age=settings.SESSION_EXPIRE_SECONDS,
            path="/",
            domain=settings.SESSION_COOKIE_DOMAIN,
        )

        return LoginResponse(
            user_id=str(user_info.get("id", "")),
            email=str(user_info.get("email", "")),
            first_name=str(user_info.get("first_name", "")),
            last_name=str(user_info.get("last_name", "")),
            roles=user_info.get("roles", []),
            permissions=user_info.get("permissions", []),
        )

    @app.post(
        "/api/bff/logout",
        status_code=status.HTTP_204_NO_CONTENT,
        tags=["bff-auth"],
    )
    async def bff_logout(
        response: Response,
        velora_session: str | None = Cookie(None, alias="velora_session"),
    ) -> None:
        """Clear the server-side session and delete the cookie."""
        sm = _get_session_mgr()

        if velora_session:
            # Also tell auth-service to revoke the refresh token
            session = await sm.get_session(velora_session)
            if session:
                async with httpx.AsyncClient() as client:
                    try:
                        await client.post(
                            f"{settings.AUTH_SERVICE_URL}/api/v1/auth/logout",
                            json={"refresh_token": session.refresh_token},
                            headers={
                                "Authorization": f"Bearer {session.access_token}"
                            },
                            timeout=5.0,
                        )
                    except httpx.HTTPError:
                        pass  # Best-effort — session is destroyed regardless

            await sm.destroy_session(velora_session)

        response.delete_cookie(
            key=settings.SESSION_COOKIE_NAME,
            path="/",
            domain=settings.SESSION_COOKIE_DOMAIN,
        )

    @app.get(
        "/api/bff/me",
        response_model=MeResponse,
        tags=["bff-auth"],
    )
    async def bff_me(
        velora_session: str | None = Cookie(None, alias="velora_session"),
    ) -> MeResponse:
        """Return the current user from the server-side session."""
        sm = _get_session_mgr()

        if not velora_session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No session cookie",
            )

        session = await sm.get_session(velora_session)
        if session is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session expired or invalid",
            )

        # Fetch fresh profile from auth-service
        async with httpx.AsyncClient() as client:
            try:
                me_resp = await client.get(
                    f"{settings.AUTH_SERVICE_URL}/api/v1/auth/me",
                    headers={
                        "Authorization": f"Bearer {session.access_token}"
                    },
                    timeout=10.0,
                )
            except httpx.HTTPError:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Auth service unavailable",
                )

        if me_resp.status_code == 401:
            # Access token expired — attempt refresh
            refreshed = await _try_refresh(sm, velora_session, session)
            if not refreshed:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Session expired",
                )
            # Retry with new token
            async with httpx.AsyncClient() as client:
                me_resp = await client.get(
                    f"{settings.AUTH_SERVICE_URL}/api/v1/auth/me",
                    headers={
                        "Authorization": f"Bearer {refreshed}"
                    },
                    timeout=10.0,
                )

        if me_resp.status_code != 200:
            raise HTTPException(
                status_code=me_resp.status_code,
                detail="Failed to retrieve user profile",
            )

        data = me_resp.json()

        # Refresh session TTL on activity
        await sm.refresh_ttl(velora_session)

        return MeResponse(
            id=str(data.get("id", "")),
            email=str(data.get("email", "")),
            first_name=str(data.get("first_name", "")),
            last_name=str(data.get("last_name", "")),
            is_active=data.get("is_active", True),
            mfa_enabled=data.get("mfa_enabled", False),
            roles=data.get("roles", []),
            permissions=data.get("permissions", []),
        )

    # ── Aggregation endpoints ─────────────────────────────────────────

    @app.get(
        "/api/bff/dashboard",
        tags=["bff-aggregation"],
    )
    async def bff_dashboard(
        velora_session: str | None = Cookie(None, alias="velora_session"),
    ) -> dict[str, Any]:
        """
        Aggregated dashboard data — vendors, assessments, findings,
        alerts, and scores in one response.
        """
        access_token = await _require_session_token(velora_session)
        return await dashboard_data(access_token)

    @app.get(
        "/api/bff/vendor/{vendor_id}/full",
        tags=["bff-aggregation"],
    )
    async def bff_vendor_full(
        vendor_id: str,
        velora_session: str | None = Cookie(None, alias="velora_session"),
    ) -> dict[str, Any]:
        """
        Full vendor view — detail + assessments + scores + findings + timeline.
        """
        access_token = await _require_session_token(velora_session)
        return await vendor_full(vendor_id, access_token)

    # ── Proxy catch-all ───────────────────────────────────────────────

    @app.api_route(
        "/api/v1/{path:path}",
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        tags=["bff-proxy"],
        include_in_schema=False,
    )
    async def bff_proxy(
        request: Request,
        velora_session: str | None = Cookie(None, alias="velora_session"),
    ) -> Response:
        """
        Proxy all /api/v1/* requests to the appropriate upstream
        microservice, injecting the JWT from the server-side session.
        """
        access_token = await _require_session_token(velora_session)
        return await proxy_request(request, access_token)

    # ── Error handlers ────────────────────────────────────────────────

    @app.exception_handler(Exception)
    async def generic_error_handler(
        _request: Request, exc: Exception
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "type": "about:blank",
                "title": "Internal Server Error",
                "status": 500,
                "detail": "An unexpected error occurred",
            },
        )

    return app


# ── Helpers ───────────────────────────────────────────────────────────────


async def _require_session_token(session_cookie: str | None) -> str:
    """Extract and validate session, returning the access token."""
    sm = _get_session_mgr()

    if not session_cookie:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No session cookie",
        )

    session = await sm.get_session(session_cookie)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or invalid",
        )

    await sm.refresh_ttl(session_cookie)
    return session.access_token


async def _try_refresh(
    sm: SessionManager,
    session_id: str,
    session: Any,
) -> str | None:
    """
    Attempt to refresh an expired access token via auth-service.
    Updates the session in Redis on success. Returns the new access
    token or None on failure.
    """
    settings = get_settings()

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                f"{settings.AUTH_SERVICE_URL}/api/v1/auth/refresh",
                json={"refresh_token": session.refresh_token},
                timeout=10.0,
            )
        except httpx.HTTPError:
            return None

    if resp.status_code != 200:
        return None

    new_tokens = resp.json()
    await sm.update_tokens(
        session_id,
        new_tokens["access_token"],
        new_tokens["refresh_token"],
    )
    return new_tokens["access_token"]


app = create_app()
