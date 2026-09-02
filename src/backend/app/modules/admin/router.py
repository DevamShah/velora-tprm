"""
Admin API endpoints — users, roles, audit logs.

All endpoints require authentication and admin permissions.
"""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import (
    get_current_user,
    require_permission,
)
from app.core.logging import get_logger
from app.modules.admin.schemas import (
    AuditLogExportRequest,
    AuditLogListResponse,
    AuditLogResponse,
    RoleCreate,
    RoleResponse,
    RoleUpdate,
    UserCreate,
    UserListResponse,
    UserResponse,
    UserUpdate,
)
from app.modules.admin.service import AdminService

logger = get_logger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])


# -- List Users -----------------------------------------------------


@router.get(
    "/users",
    response_model=UserListResponse,
    dependencies=[Depends(require_permission("admin.users"))],
)
async def list_users(
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> UserListResponse:
    """List all users in the tenant."""
    service = AdminService(session)
    return await service.list_users(current_user["tenant_id"])


# -- Create User ----------------------------------------------------


@router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("admin.users"))],
)
async def create_user(
    body: UserCreate,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> UserResponse:
    """Create / invite a new user."""
    service = AdminService(session)
    return await service.create_user(current_user["tenant_id"], body)


# -- Update User ----------------------------------------------------


@router.put(
    "/users/{user_id}",
    response_model=UserResponse,
    dependencies=[Depends(require_permission("admin.users"))],
)
async def update_user(
    user_id: uuid.UUID,
    body: UserUpdate,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> UserResponse:
    """Update a user's details."""
    service = AdminService(session)
    result = await service.update_user(
        current_user["tenant_id"], user_id, body
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return result


# -- Deactivate User ------------------------------------------------


@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("admin.users"))],
)
async def deactivate_user(
    user_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> None:
    """Deactivate a user (soft delete)."""
    service = AdminService(session)
    found = await service.deactivate_user(current_user["tenant_id"], user_id)
    if not found:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )


# -- Assign Role to User -------------------------------------------


@router.post(
    "/users/{user_id}/roles",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("admin.roles"))],
)
async def assign_role(
    user_id: uuid.UUID,
    body: dict,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> dict:
    """Assign a role to a user."""
    role_id = body.get("role_id")
    if not role_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="role_id is required",
        )
    service = AdminService(session)
    assigned = await service.assign_role(
        current_user["tenant_id"],
        user_id,
        uuid.UUID(role_id),
    )
    if not assigned:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return {"status": "assigned"}


# -- Remove Role from User -----------------------------------------


@router.delete(
    "/users/{user_id}/roles/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("admin.roles"))],
)
async def remove_role(
    user_id: uuid.UUID,
    role_id: uuid.UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> None:
    """Remove a role from a user."""
    service = AdminService(session)
    removed = await service.remove_role(
        current_user["tenant_id"], user_id, role_id
    )
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role assignment not found",
        )


# -- List Roles -----------------------------------------------------


@router.get(
    "/roles",
    response_model=list[RoleResponse],
    dependencies=[Depends(require_permission("admin.roles"))],
)
async def list_roles(
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> list[RoleResponse]:
    """List all roles in the tenant."""
    service = AdminService(session)
    return await service.list_roles(current_user["tenant_id"])


# -- Create Role ----------------------------------------------------


@router.post(
    "/roles",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("admin.roles"))],
)
async def create_role(
    body: RoleCreate,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> RoleResponse:
    """Create a custom role."""
    service = AdminService(session)
    return await service.create_role(current_user["tenant_id"], body)


# -- Update Role ----------------------------------------------------


@router.put(
    "/roles/{role_id}",
    response_model=RoleResponse,
    dependencies=[Depends(require_permission("admin.roles"))],
)
async def update_role(
    role_id: uuid.UUID,
    body: RoleUpdate,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> RoleResponse:
    """Update a role."""
    service = AdminService(session)
    result = await service.update_role(
        current_user["tenant_id"], role_id, body
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )
    return result


# -- Query Audit Logs -----------------------------------------------


@router.get(
    "/audit-logs",
    response_model=AuditLogListResponse,
    dependencies=[Depends(require_permission("admin.audit"))],
)
async def query_audit_logs(
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
    user_id: uuid.UUID | None = Query(None),
    action: str | None = Query(None),
    entity_type: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> AuditLogListResponse:
    """Query audit logs with filters."""
    service = AdminService(session)
    return await service.query_audit_logs(
        tenant_id=current_user["tenant_id"],
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        page=page,
        page_size=page_size,
    )


# -- Export Audit Logs ----------------------------------------------


@router.post(
    "/audit-logs/export",
    response_model=list[AuditLogResponse],
    dependencies=[Depends(require_permission("admin.audit"))],
)
async def export_audit_logs(
    body: AuditLogExportRequest,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[dict, Depends(get_current_user)],
) -> list[AuditLogResponse]:
    """Export audit logs for CSV generation."""
    service = AdminService(session)
    return await service.export_audit_logs(current_user["tenant_id"], body)
