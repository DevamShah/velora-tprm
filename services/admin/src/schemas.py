"""
Admin Pydantic v2 request / response schemas.

Handles user management, role management, and audit logs.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


# -- User Schemas ---------------------------------------------------


class UserResponse(BaseModel):
    """User response for admin views."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    first_name: str
    last_name: str
    email: Optional[str] = None
    is_active: bool
    mfa_enabled: bool
    last_login_at: Optional[datetime] = None
    roles: List[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class UserListResponse(BaseModel):
    """Paginated user list."""

    items: List[UserResponse]
    total: int


class UserCreate(BaseModel):
    """Create / invite a new user."""

    email: str = Field(min_length=1, max_length=255)
    first_name: str = Field(
        min_length=1, max_length=100
    )
    last_name: str = Field(
        min_length=1, max_length=100
    )
    password: str = Field(min_length=8, max_length=128)
    role_id: Optional[uuid.UUID] = None


class UserUpdate(BaseModel):
    """Update user details."""

    first_name: Optional[str] = Field(
        None, min_length=1, max_length=100
    )
    last_name: Optional[str] = Field(
        None, min_length=1, max_length=100
    )
    is_active: Optional[bool] = None
    mfa_enabled: Optional[bool] = None


# -- Role Schemas ---------------------------------------------------


class RoleResponse(BaseModel):
    """Role response."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    description: Optional[str] = None
    permissions: List[str] = Field(
        default_factory=list
    )
    is_system: bool
    is_default: bool
    created_at: datetime
    updated_at: datetime


class RoleCreate(BaseModel):
    """Create a custom role."""

    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(
        None, max_length=500
    )
    permissions: List[str] = Field(
        default_factory=list
    )


class RoleUpdate(BaseModel):
    """Update a role."""

    name: Optional[str] = Field(
        None, min_length=1, max_length=100
    )
    description: Optional[str] = Field(
        None, max_length=500
    )
    permissions: Optional[List[str]] = None


class RoleAssign(BaseModel):
    """Assign a role to a user."""

    role_id: uuid.UUID


# -- Audit Log Schemas ----------------------------------------------


class AuditLogResponse(BaseModel):
    """Audit log entry response."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    user_id: Optional[uuid.UUID] = None
    action: str
    entity_type: Optional[str] = None
    entity_id: Optional[uuid.UUID] = None
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    created_at: datetime


class AuditLogListResponse(BaseModel):
    """Paginated audit log list."""

    items: List[AuditLogResponse]
    total: int
    page: int
    page_size: int


class AuditLogExportRequest(BaseModel):
    """Filters for audit log export."""

    user_id: Optional[uuid.UUID] = None
    action: Optional[str] = None
    entity_type: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
