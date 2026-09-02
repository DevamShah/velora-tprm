"""
Admin Pydantic v2 request / response schemas.

Handles user management, role management, and audit logs.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

# -- User Schemas ---------------------------------------------------


class UserResponse(BaseModel):
    """User response for admin views."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    first_name: str
    last_name: str
    email: str | None = None
    is_active: bool
    mfa_enabled: bool
    last_login_at: datetime | None = None
    roles: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class UserListResponse(BaseModel):
    """Paginated user list."""

    items: list[UserResponse]
    total: int


class UserCreate(BaseModel):
    """Create / invite a new user."""

    email: str = Field(min_length=1, max_length=255)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=8, max_length=128)
    role_id: uuid.UUID | None = None


class UserUpdate(BaseModel):
    """Update user details."""

    first_name: str | None = Field(None, min_length=1, max_length=100)
    last_name: str | None = Field(None, min_length=1, max_length=100)
    is_active: bool | None = None
    mfa_enabled: bool | None = None


# -- Role Schemas ---------------------------------------------------


class RoleResponse(BaseModel):
    """Role response."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    description: str | None = None
    permissions: list[str] = Field(default_factory=list)
    is_system: bool
    is_default: bool
    created_at: datetime
    updated_at: datetime


class RoleCreate(BaseModel):
    """Create a custom role."""

    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    permissions: list[str] = Field(default_factory=list)


class RoleUpdate(BaseModel):
    """Update a role."""

    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    permissions: list[str] | None = None


class RoleAssign(BaseModel):
    """Assign a role to a user."""

    role_id: uuid.UUID


# -- Audit Log Schemas ----------------------------------------------


class AuditLogResponse(BaseModel):
    """Audit log entry response."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    user_id: uuid.UUID | None = None
    action: str
    entity_type: str | None = None
    entity_id: uuid.UUID | None = None
    details: dict[str, Any] | None = None
    ip_address: str | None = None
    created_at: datetime


class AuditLogListResponse(BaseModel):
    """Paginated audit log list."""

    items: list[AuditLogResponse]
    total: int
    page: int
    page_size: int


class AuditLogExportRequest(BaseModel):
    """Filters for audit log export."""

    user_id: uuid.UUID | None = None
    action: str | None = None
    entity_type: str | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
