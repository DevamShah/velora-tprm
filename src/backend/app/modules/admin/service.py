"""
Admin business logic — users, roles, audit logs.

All DB queries run inside the caller-provided async session.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import get_settings
from app.core.logging import get_logger
from app.core.security import (
    FieldEncryptor,
    hash_password,
)
from app.modules.admin.models import AuditLog
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
from app.modules.auth.models import Role, User, UserRole

logger = get_logger(__name__)


class AdminService:
    """Stateless admin service — receives session per call."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._settings = get_settings()
        self._encryptor = FieldEncryptor(
            self._settings.ENCRYPTION_KEY
        )

    # -- List Users -------------------------------------------------

    async def list_users(
        self,
        tenant_id: uuid.UUID,
    ) -> UserListResponse:
        """List all users in a tenant."""
        result = await self._session.execute(
            select(User)
            .options(selectinload(User.user_roles))
            .where(User.tenant_id == tenant_id)
        )
        users = result.scalars().all()
        items = [self._to_user_response(u) for u in users]
        return UserListResponse(
            items=items, total=len(items)
        )

    # -- Create User ------------------------------------------------

    async def create_user(
        self,
        tenant_id: uuid.UUID,
        data: UserCreate,
    ) -> UserResponse:
        """Create a new user (invite flow)."""
        email_hash = self._encryptor.hmac_hash(
            data.email
        )
        user = User(
            tenant_id=tenant_id,
            email_encrypted=self._encryptor.encrypt(
                data.email
            ),
            email_hash=email_hash,
            first_name=data.first_name,
            last_name=data.last_name,
            password_hash=hash_password(data.password),
            is_active=True,
        )
        self._session.add(user)
        await self._session.flush()

        if data.role_id:
            user_role = UserRole(
                user_id=user.id,
                role_id=data.role_id,
                granted_at=datetime.now(UTC),
            )
            self._session.add(user_role)
            await self._session.flush()

        logger.info(
            "user_created", user_id=str(user.id)
        )
        return self._to_user_response(user)

    # -- Update User ------------------------------------------------

    async def update_user(
        self,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        data: UserUpdate,
    ) -> UserResponse | None:
        """Update user details."""
        user = await self._get_user(
            tenant_id, user_id
        )
        if user is None:
            return None

        update_data = data.model_dump(
            exclude_unset=True
        )
        for field, value in update_data.items():
            setattr(user, field, value)

        await self._session.flush()
        logger.info(
            "user_updated", user_id=str(user_id)
        )
        return self._to_user_response(user)

    # -- Deactivate User --------------------------------------------

    async def deactivate_user(
        self,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> bool:
        """Deactivate a user. Returns False if not found."""
        user = await self._get_user(
            tenant_id, user_id
        )
        if user is None:
            return False

        user.is_active = False
        await self._session.flush()
        logger.info(
            "user_deactivated", user_id=str(user_id)
        )
        return True

    # -- List Roles -------------------------------------------------

    async def list_roles(
        self,
        tenant_id: uuid.UUID,
    ) -> list[RoleResponse]:
        """List all roles in a tenant."""
        result = await self._session.execute(
            select(Role).where(
                Role.tenant_id == tenant_id
            )
        )
        roles = result.scalars().all()
        return [self._to_role_response(r) for r in roles]

    # -- Create Role ------------------------------------------------

    async def create_role(
        self,
        tenant_id: uuid.UUID,
        data: RoleCreate,
    ) -> RoleResponse:
        """Create a custom role."""
        role = Role(
            tenant_id=tenant_id,
            name=data.name,
            description=data.description,
            permissions=data.permissions,
            is_system=False,
            is_default=False,
        )
        self._session.add(role)
        await self._session.flush()
        logger.info(
            "role_created", role_id=str(role.id)
        )
        return self._to_role_response(role)

    # -- Update Role ------------------------------------------------

    async def update_role(
        self,
        tenant_id: uuid.UUID,
        role_id: uuid.UUID,
        data: RoleUpdate,
    ) -> RoleResponse | None:
        """Update an existing role."""
        result = await self._session.execute(
            select(Role).where(
                Role.id == role_id,
                Role.tenant_id == tenant_id,
            )
        )
        role = result.scalars().first()
        if role is None:
            return None

        update_data = data.model_dump(
            exclude_unset=True
        )
        for field, value in update_data.items():
            setattr(role, field, value)

        await self._session.flush()
        logger.info(
            "role_updated", role_id=str(role_id)
        )
        return self._to_role_response(role)

    # -- Assign Role ------------------------------------------------

    async def assign_role(
        self,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        role_id: uuid.UUID,
    ) -> bool:
        """Assign a role to a user."""
        user = await self._get_user(
            tenant_id, user_id
        )
        if user is None:
            return False

        user_role = UserRole(
            user_id=user_id,
            role_id=role_id,
            granted_at=datetime.now(UTC),
        )
        self._session.add(user_role)
        await self._session.flush()
        logger.info(
            "role_assigned",
            user_id=str(user_id),
            role_id=str(role_id),
        )
        return True

    # -- Remove Role ------------------------------------------------

    async def remove_role(
        self,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        role_id: uuid.UUID,
    ) -> bool:
        """Remove a role from a user."""
        result = await self._session.execute(
            select(UserRole).where(
                UserRole.user_id == user_id,
                UserRole.role_id == role_id,
            )
        )
        user_role = result.scalars().first()
        if user_role is None:
            return False

        await self._session.delete(user_role)
        await self._session.flush()
        logger.info(
            "role_removed",
            user_id=str(user_id),
            role_id=str(role_id),
        )
        return True

    # -- Query Audit Logs -------------------------------------------

    async def query_audit_logs(
        self,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID | None = None,
        action: str | None = None,
        entity_type: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> AuditLogListResponse:
        """Query audit logs with filters and pagination."""
        base = select(AuditLog).where(
            AuditLog.tenant_id == tenant_id
        )
        base = self._apply_audit_filters(
            base, user_id, action, entity_type,
            date_from, date_to,
        )

        count_q = select(func.count()).select_from(
            base.subquery()
        )
        total = (
            await self._session.execute(count_q)
        ).scalar() or 0

        offset = (page - 1) * page_size
        result = await self._session.execute(
            base.order_by(AuditLog.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        logs = result.scalars().all()

        return AuditLogListResponse(
            items=[
                self._to_audit_response(lg)
                for lg in logs
            ],
            total=total,
            page=page,
            page_size=page_size,
        )

    # -- Export Audit Logs ------------------------------------------

    async def export_audit_logs(
        self,
        tenant_id: uuid.UUID,
        filters: AuditLogExportRequest,
    ) -> list[AuditLogResponse]:
        """Export audit logs matching filters (no pagination)."""
        base = select(AuditLog).where(
            AuditLog.tenant_id == tenant_id
        )
        base = self._apply_audit_filters(
            base,
            filters.user_id,
            filters.action,
            filters.entity_type,
            filters.date_from,
            filters.date_to,
        )

        result = await self._session.execute(
            base.order_by(AuditLog.created_at.desc())
            .limit(10000)
        )
        logs = result.scalars().all()
        return [
            self._to_audit_response(lg)
            for lg in logs
        ]

    # -- Log Action -------------------------------------------------

    async def log_action(
        self,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID | None,
        action: str,
        entity_type: str | None = None,
        entity_id: uuid.UUID | None = None,
        details: dict | None = None,
        ip_address: str | None = None,
    ) -> AuditLogResponse:
        """Create an audit log entry."""
        log = AuditLog(
            tenant_id=tenant_id,
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
            ip_address=ip_address,
        )
        self._session.add(log)
        await self._session.flush()
        return self._to_audit_response(log)

    # -- Private helpers --------------------------------------------

    async def _get_user(
        self,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> User | None:
        """Fetch a user by tenant and ID."""
        result = await self._session.execute(
            select(User)
            .options(selectinload(User.user_roles))
            .where(
                User.id == user_id,
                User.tenant_id == tenant_id,
            )
        )
        return result.scalars().first()

    def _to_user_response(
        self, user: User
    ) -> UserResponse:
        """Map User ORM to admin response schema."""
        email = None
        try:
            email = self._encryptor.decrypt(
                user.email_encrypted
            )
        except Exception:
            email = None

        role_names: list[str] = []
        try:
            for ur in user.user_roles or []:
                if ur.role and ur.role.name:
                    role_names.append(ur.role.name)
        except Exception:
            pass

        return UserResponse(
            id=user.id,
            tenant_id=user.tenant_id,
            first_name=user.first_name,
            last_name=user.last_name,
            email=email,
            is_active=user.is_active,
            mfa_enabled=user.mfa_enabled,
            last_login_at=user.last_login_at,
            roles=role_names,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    @staticmethod
    def _to_role_response(role: Role) -> RoleResponse:
        """Map Role ORM to response schema."""
        return RoleResponse(
            id=role.id,
            tenant_id=role.tenant_id,
            name=role.name,
            description=role.description,
            permissions=role.permissions or [],
            is_system=role.is_system,
            is_default=role.is_default,
            created_at=role.created_at,
            updated_at=role.updated_at,
        )

    @staticmethod
    def _to_audit_response(
        log: AuditLog,
    ) -> AuditLogResponse:
        """Map AuditLog ORM to response schema."""
        return AuditLogResponse(
            id=log.id,
            tenant_id=log.tenant_id,
            user_id=log.user_id,
            action=log.action,
            entity_type=log.entity_type,
            entity_id=log.entity_id,
            details=log.details,
            ip_address=log.ip_address,
            created_at=log.created_at,
        )

    @staticmethod
    def _apply_audit_filters(
        query,
        user_id: uuid.UUID | None,
        action: str | None,
        entity_type: str | None,
        date_from: datetime | None,
        date_to: datetime | None,
    ):
        """Apply WHERE clauses for audit log filters."""
        if user_id:
            query = query.where(
                AuditLog.user_id == user_id
            )
        if action:
            query = query.where(
                AuditLog.action == action
            )
        if entity_type:
            query = query.where(
                AuditLog.entity_type == entity_type
            )
        if date_from:
            query = query.where(
                AuditLog.created_at >= date_from
            )
        if date_to:
            query = query.where(
                AuditLog.created_at <= date_to
            )
        return query
