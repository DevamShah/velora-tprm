"""
Authentication middleware.

Validates JWTs on protected routes and rejects unauthenticated
requests before they reach endpoint handlers.
"""

from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.logging import get_logger, user_id_ctx
from app.core.security import verify_token

logger = get_logger(__name__)

# Endpoints that do not require authentication
_PUBLIC_PREFIXES = (
    "/health",
    "/ready",
    "/auth/login",
    "/auth/register",
    "/auth/sso",
    "/api/v1/auth/login",
    "/api/v1/auth/register",
    "/api/v1/auth/sso",
    "/api/v1/auth/refresh",
    "/docs",
    "/openapi.json",
    "/redoc",
)


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Reject requests without a valid JWT on protected routes.

    Populates user_id logging context for downstream handlers.
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

        # CORS preflight must always pass through
        if request.method == "OPTIONS":
            return await call_next(request)

        if any(path.startswith(p) for p in _PUBLIC_PREFIXES):
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return _unauthorized("Missing Authorization header")

        token = auth_header[7:]
        payload = verify_token(
            token,
            self._jwt_secret,
            expected_type="access",
        )

        if payload is None:
            return _unauthorized("Invalid or expired token")

        user_id = payload.get("sub")
        if user_id:
            user_id_ctx.set(user_id)

        return await call_next(request)


def _unauthorized(detail: str) -> JSONResponse:
    """Return an RFC 7807-style 401 response."""
    return JSONResponse(
        status_code=401,
        content={
            "type": "about:blank",
            "title": "Unauthorized",
            "status": 401,
            "detail": detail,
        },
    )
