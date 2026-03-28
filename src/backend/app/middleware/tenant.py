"""
Tenant context middleware.

Extracts tenant_id from the JWT (not from a header — security fix
from v1.0) and sets the PostgreSQL session variable for RLS.
"""

from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import get_logger, tenant_id_ctx
from app.core.security import verify_token

logger = get_logger(__name__)

# Paths that do not require tenant context
_SKIP_PREFIXES = (
    "/auth/login",
    "/auth/register",
    "/auth/sso",
    "/api/v1/auth/login",
    "/api/v1/auth/register",
    "/api/v1/auth/sso",
    "/api/v1/auth/refresh",
    "/health",
    "/ready",
    "/docs",
    "/openapi.json",
    "/redoc",
)


class TenantMiddleware(BaseHTTPMiddleware):
    """
    Populate the tenant_id context variable from the JWT.

    The actual RLS SET LOCAL happens inside the dependency layer
    (get_current_user) where we have a live DB session. This
    middleware only sets the logging context var early so that
    even middleware-level logs carry the tenant.
    """

    def __init__(self, app, jwt_secret: str) -> None:  # noqa: ANN001
        super().__init__(app)
        self._jwt_secret = jwt_secret

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        path = request.url.path

        if request.method == "OPTIONS":
            return await call_next(request)

        if any(path.startswith(p) for p in _SKIP_PREFIXES):
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            payload = verify_token(
                token,
                self._jwt_secret,
                expected_type="access",
            )
            if payload and "tenant_id" in payload:
                tenant_id_ctx.set(payload["tenant_id"])

        return await call_next(request)
