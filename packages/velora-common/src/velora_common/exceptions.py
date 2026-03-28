"""
Standard exception hierarchy for Velora TPRM services.

All services use these exceptions for consistent error handling
and RFC 7807-compliant error responses.
"""

from __future__ import annotations


class VeloraError(Exception):
    """Base exception for all Velora errors."""

    def __init__(
        self,
        detail: str = "An unexpected error occurred",
        status_code: int = 500,
    ) -> None:
        self.detail = detail
        self.status_code = status_code
        super().__init__(detail)


class NotFoundError(VeloraError):
    """Resource not found."""

    def __init__(self, resource: str = "Resource", identifier: str = "") -> None:
        detail = f"{resource} not found"
        if identifier:
            detail = f"{resource} '{identifier}' not found"
        super().__init__(detail=detail, status_code=404)


class ConflictError(VeloraError):
    """Resource already exists or state conflict."""

    def __init__(self, detail: str = "Resource conflict") -> None:
        super().__init__(detail=detail, status_code=409)


class ValidationError(VeloraError):
    """Business logic validation failure."""

    def __init__(self, detail: str = "Validation failed") -> None:
        super().__init__(detail=detail, status_code=422)


class AuthenticationError(VeloraError):
    """Authentication failure."""

    def __init__(self, detail: str = "Authentication required") -> None:
        super().__init__(detail=detail, status_code=401)


class AuthorizationError(VeloraError):
    """Authorization / permission failure."""

    def __init__(self, detail: str = "Insufficient permissions") -> None:
        super().__init__(detail=detail, status_code=403)


class RateLimitError(VeloraError):
    """Rate limit exceeded."""

    def __init__(self, detail: str = "Rate limit exceeded") -> None:
        super().__init__(detail=detail, status_code=429)


class ServiceUnavailableError(VeloraError):
    """Downstream service is unavailable."""

    def __init__(self, service: str = "Service") -> None:
        super().__init__(
            detail=f"{service} is currently unavailable",
            status_code=503,
        )
