"""
Shared Pydantic schemas used across multiple services.

Includes pagination, error responses, and common base schemas.
"""

from __future__ import annotations

from typing import Any, Generic, List, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard paginated response wrapper."""

    items: List[T]
    total: int
    page: int
    page_size: int


class ErrorResponse(BaseModel):
    """RFC 7807 Problem Details response."""

    type: str = "about:blank"
    title: str
    status: int
    detail: str
    instance: str | None = None


class HealthResponse(BaseModel):
    """Standard health check response."""

    status: str
    service: str
    version: str = "2.0.0"


class PaginationParams(BaseModel):
    """Common pagination query parameters."""

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
