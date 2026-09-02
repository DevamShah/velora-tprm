"""
Unit tests for AdminService.

Mocks the database session and FieldEncryptor to test user, role
and audit-log business logic without infrastructure dependencies.
The mock session applies SQLAlchemy column defaults on ``add`` so
freshly constructed ORM objects map cleanly onto response schemas.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy import inspect as sa_inspect
from sqlalchemy import select

from app.modules.admin.models import AuditLog
from app.modules.admin.schemas import (
    AuditLogExportRequest,
    RoleCreate,
    RoleUpdate,
    UserCreate,
    UserUpdate,
)
from app.modules.admin.service import AdminService
from app.modules.auth.models import Role, User, UserRole

TENANT_ID = uuid.UUID("00000000-0000-4000-a000-000000000001")
USER_ID = uuid.UUID("00000000-0000-4000-a000-000000000010")
ROLE_ID = uuid.UUID("00000000-0000-4000-a000-000000000020")
LOG_ID = uuid.UUID("00000000-0000-4000-a000-000000000030")

DECRYPTED_EMAIL = "jane.doe@example.com"


def _apply_orm_defaults(obj) -> None:
    """Apply SQLAlchemy Python-side column defaults, as flush would."""
    mapper = sa_inspect(type(obj))
    for column in mapper.columns:
        key = mapper.get_property_by_column(column).key
        if getattr(obj, key, None) is not None:
            continue
        default = column.default
        if default is None:
            continue
        if default.is_callable:
            # SQLAlchemy wraps callables to take an execution context.
            setattr(obj, key, default.arg(None))
        elif default.is_scalar:
            setattr(obj, key, default.arg)


class _RaisingRelationship:
    """Stand-in for a lazy relationship that cannot load."""

    def __bool__(self) -> bool:
        raise RuntimeError("lazy load outside of a session")


def _make_role(**overrides) -> Role:
    """Create a Role ORM stand-in with defaults."""
    now = datetime.now(UTC)
    defaults = dict(
        id=ROLE_ID,
        tenant_id=TENANT_ID,
        name="Admin",
        description="Full access",
        permissions=["vendors.read", "vendors.write"],
        is_system=True,
        is_default=False,
        created_at=now,
        updated_at=now,
    )
    defaults.update(overrides)
    role = MagicMock(spec=Role)
    for k, v in defaults.items():
        setattr(role, k, v)
    return role


def _make_user_role(**overrides) -> UserRole:
    """Create a UserRole ORM stand-in bound to a role."""
    defaults = dict(
        id=uuid.uuid4(),
        user_id=USER_ID,
        role_id=ROLE_ID,
        granted_at=datetime.now(UTC),
        granted_by=None,
        expires_at=None,
        role=_make_role(),
    )
    defaults.update(overrides)
    user_role = MagicMock(spec=UserRole)
    for k, v in defaults.items():
        setattr(user_role, k, v)
    return user_role


def _make_user(**overrides) -> User:
    """Create a User ORM stand-in with defaults."""
    now = datetime.now(UTC)
    defaults = dict(
        id=USER_ID,
        tenant_id=TENANT_ID,
        email_encrypted="enc:jane.doe@example.com",
        email_hash="emailhash",
        first_name="Jane",
        last_name="Doe",
        password_hash="$2b$12$notarealhash",
        is_active=True,
        last_login_at=None,
        mfa_enabled=False,
        notification_preferences=None,
        user_roles=[_make_user_role()],
        created_at=now,
        updated_at=now,
    )
    defaults.update(overrides)
    user = MagicMock(spec=User)
    for k, v in defaults.items():
        setattr(user, k, v)
    return user


def _make_audit_log(**overrides) -> AuditLog:
    """Create an AuditLog ORM stand-in with defaults."""
    now = datetime.now(UTC)
    defaults = dict(
        id=LOG_ID,
        tenant_id=TENANT_ID,
        user_id=USER_ID,
        action="vendor.created",
        entity_type="vendor",
        entity_id=uuid.uuid4(),
        details={"name": "Acme"},
        ip_address="10.0.0.1",
        created_at=now,
        updated_at=now,
    )
    defaults.update(overrides)
    log = MagicMock(spec=AuditLog)
    for k, v in defaults.items():
        setattr(log, k, v)
    return log


def _mock_execute_result(items):
    """Create a mock execute result that returns scalars."""
    result = MagicMock()
    scalars = MagicMock()
    scalars.first.return_value = items[0] if items else None
    scalars.all.return_value = items
    result.scalars.return_value = scalars
    result.scalar.return_value = len(items)
    result.rowcount = len(items)
    return result


def _mock_count_result(total):
    """Create a mock execute result for a COUNT query."""
    result = MagicMock()
    result.scalar.return_value = total
    return result


@pytest.fixture
def mock_session():
    """Async mock session that fills ORM defaults on add()."""
    session = AsyncMock()
    added: list = []

    def _add(obj):
        added.append(obj)
        _apply_orm_defaults(obj)

    session.add = MagicMock(side_effect=_add)
    session.added = added
    return session


@pytest.fixture
def service(mock_session):
    """AdminService with mocked session, settings and encryptor."""
    with patch(
        "app.modules.admin.service.get_settings"
    ) as mock_settings, patch(
        "app.modules.admin.service.FieldEncryptor"
    ) as mock_enc_cls:
        settings = MagicMock()
        settings.ENCRYPTION_KEY = "dGVzdC1rZXktdGhhdC1pcy0zMi1ieXRlcw=="
        mock_settings.return_value = settings

        enc = MagicMock()
        enc.encrypt.return_value = "encrypted_value"
        enc.decrypt.return_value = DECRYPTED_EMAIL
        enc.hmac_hash.return_value = "abc123hash"
        mock_enc_cls.return_value = enc

        svc = AdminService(mock_session)
        svc._encryptor = enc
        yield svc


# ── list_users ─────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_users_returns_mapped_users(service, mock_session):
    """Users are mapped to responses with decrypted email + roles."""
    users = [_make_user(), _make_user(id=uuid.uuid4(), first_name="Bob")]
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result(users)
    )

    result = await service.list_users(TENANT_ID)

    assert result.total == 2
    assert len(result.items) == 2
    assert result.items[0].email == DECRYPTED_EMAIL
    assert result.items[0].roles == ["Admin"]
    assert result.items[1].first_name == "Bob"


@pytest.mark.asyncio
async def test_list_users_empty(service, mock_session):
    """An empty tenant yields an empty list with total 0."""
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([])
    )

    result = await service.list_users(TENANT_ID)

    assert result.total == 0
    assert result.items == []


# ── create_user ────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_user_without_role(service, mock_session):
    """A user is created with encrypted email and hashed password."""
    data = UserCreate(
        email="new.user@example.com",
        first_name="New",
        last_name="User",
        password="sup3r-secret-pw",
    )

    with patch(
        "app.modules.admin.service.hash_password",
        return_value="$2b$12$hashed",
    ) as mock_hash:
        result = await service.create_user(TENANT_ID, data)

    mock_hash.assert_called_once_with("sup3r-secret-pw")
    service._encryptor.encrypt.assert_called_once_with(
        "new.user@example.com"
    )
    service._encryptor.hmac_hash.assert_called_once_with(
        "new.user@example.com"
    )

    assert mock_session.add.call_count == 1
    created = mock_session.added[0]
    assert isinstance(created, User)
    assert created.tenant_id == TENANT_ID
    assert created.email_encrypted == "encrypted_value"
    assert created.email_hash == "abc123hash"
    assert created.password_hash == "$2b$12$hashed"
    assert created.is_active is True

    mock_session.flush.assert_awaited_once()
    assert result.first_name == "New"
    assert result.email == DECRYPTED_EMAIL
    assert result.roles == []


@pytest.mark.asyncio
async def test_create_user_with_role_assignment(
    service, mock_session
):
    """Supplying role_id also persists a UserRole join row."""
    data = UserCreate(
        email="new.user@example.com",
        first_name="New",
        last_name="User",
        password="sup3r-secret-pw",
        role_id=ROLE_ID,
    )

    with patch(
        "app.modules.admin.service.hash_password",
        return_value="$2b$12$hashed",
    ):
        await service.create_user(TENANT_ID, data)

    assert mock_session.add.call_count == 2
    user, user_role = mock_session.added
    assert isinstance(user_role, UserRole)
    assert user_role.user_id == user.id
    assert user_role.role_id == ROLE_ID
    assert isinstance(user_role.granted_at, datetime)
    assert mock_session.flush.await_count == 2


# ── update_user ────────────────────────────────────────────


@pytest.mark.asyncio
async def test_update_user_applies_set_fields_only(
    service, mock_session
):
    """Only explicitly supplied fields are written."""
    user = _make_user()
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([user])
    )

    result = await service.update_user(
        TENANT_ID, USER_ID, UserUpdate(first_name="Janet")
    )

    assert user.first_name == "Janet"
    assert user.last_name == "Doe"
    assert user.is_active is True
    assert result is not None
    assert result.first_name == "Janet"
    mock_session.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_user_can_toggle_flags(service, mock_session):
    """Boolean flags including False are applied when set."""
    user = _make_user()
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([user])
    )

    result = await service.update_user(
        TENANT_ID,
        USER_ID,
        UserUpdate(is_active=False, mfa_enabled=True),
    )

    assert user.is_active is False
    assert user.mfa_enabled is True
    assert result.is_active is False
    assert result.mfa_enabled is True


@pytest.mark.asyncio
async def test_update_user_not_found(service, mock_session):
    """An unknown user returns None and does not flush."""
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([])
    )

    result = await service.update_user(
        TENANT_ID, USER_ID, UserUpdate(first_name="Nope")
    )

    assert result is None
    mock_session.flush.assert_not_awaited()


# ── deactivate_user ────────────────────────────────────────


@pytest.mark.asyncio
async def test_deactivate_user_success(service, mock_session):
    """Deactivation flips is_active and returns True."""
    user = _make_user()
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([user])
    )

    assert await service.deactivate_user(TENANT_ID, USER_ID) is True
    assert user.is_active is False
    mock_session.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_deactivate_user_not_found(service, mock_session):
    """An unknown user returns False."""
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([])
    )

    assert await service.deactivate_user(TENANT_ID, USER_ID) is False
    mock_session.flush.assert_not_awaited()


# ── roles ──────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_roles(service, mock_session):
    """Roles are mapped to RoleResponse objects."""
    roles = [_make_role(), _make_role(id=uuid.uuid4(), name="Analyst")]
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result(roles)
    )

    result = await service.list_roles(TENANT_ID)

    assert [r.name for r in result] == ["Admin", "Analyst"]
    assert result[0].permissions == ["vendors.read", "vendors.write"]


@pytest.mark.asyncio
async def test_list_roles_empty(service, mock_session):
    """No roles yields an empty list."""
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([])
    )

    assert await service.list_roles(TENANT_ID) == []


@pytest.mark.asyncio
async def test_create_role_is_custom(service, mock_session):
    """Created roles are never system or default roles."""
    data = RoleCreate(
        name="Auditor",
        description="Read-only auditor",
        permissions=["assessments.read"],
    )

    result = await service.create_role(TENANT_ID, data)

    created = mock_session.added[0]
    assert isinstance(created, Role)
    assert created.tenant_id == TENANT_ID
    assert created.is_system is False
    assert created.is_default is False

    assert result.name == "Auditor"
    assert result.description == "Read-only auditor"
    assert result.permissions == ["assessments.read"]
    assert result.is_system is False
    mock_session.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_role_applies_changes(service, mock_session):
    """Set fields are written to the role."""
    role = _make_role()
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([role])
    )

    result = await service.update_role(
        TENANT_ID,
        ROLE_ID,
        RoleUpdate(name="Renamed", permissions=["vendors.read"]),
    )

    assert role.name == "Renamed"
    assert role.permissions == ["vendors.read"]
    assert role.description == "Full access"
    assert result.name == "Renamed"
    assert result.permissions == ["vendors.read"]
    mock_session.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_role_not_found(service, mock_session):
    """An unknown role returns None."""
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([])
    )

    result = await service.update_role(
        TENANT_ID, ROLE_ID, RoleUpdate(name="Renamed")
    )

    assert result is None
    mock_session.flush.assert_not_awaited()


# ── role assignment ────────────────────────────────────────


@pytest.mark.asyncio
async def test_assign_role_success(service, mock_session):
    """Assigning a role adds a UserRole row."""
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([_make_user()])
    )

    assert (
        await service.assign_role(TENANT_ID, USER_ID, ROLE_ID) is True
    )

    added = mock_session.added[0]
    assert isinstance(added, UserRole)
    assert added.user_id == USER_ID
    assert added.role_id == ROLE_ID
    assert isinstance(added.granted_at, datetime)
    mock_session.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_assign_role_unknown_user(service, mock_session):
    """Assigning to an unknown user returns False and adds nothing."""
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([])
    )

    assert (
        await service.assign_role(TENANT_ID, USER_ID, ROLE_ID) is False
    )
    mock_session.add.assert_not_called()


@pytest.mark.asyncio
async def test_remove_role_success(service, mock_session):
    """An existing assignment is deleted."""
    user_role = _make_user_role()
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([user_role])
    )

    assert (
        await service.remove_role(TENANT_ID, USER_ID, ROLE_ID) is True
    )
    mock_session.delete.assert_awaited_once_with(user_role)
    mock_session.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_remove_role_not_assigned(service, mock_session):
    """Removing a non-existent assignment returns False."""
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([])
    )

    assert (
        await service.remove_role(TENANT_ID, USER_ID, ROLE_ID) is False
    )
    mock_session.delete.assert_not_awaited()


# ── query_audit_logs ───────────────────────────────────────


@pytest.mark.asyncio
async def test_query_audit_logs_pagination(service, mock_session):
    """Results are wrapped with total/page/page_size."""
    logs = [_make_audit_log(), _make_audit_log(id=uuid.uuid4())]
    mock_session.execute = AsyncMock(
        side_effect=[
            _mock_count_result(42),
            _mock_execute_result(logs),
        ]
    )

    result = await service.query_audit_logs(
        TENANT_ID, page=3, page_size=20
    )

    assert result.total == 42
    assert result.page == 3
    assert result.page_size == 20
    assert len(result.items) == 2
    assert result.items[0].action == "vendor.created"

    page_query = str(mock_session.execute.await_args_list[1].args[0])
    assert "LIMIT" in page_query
    assert "OFFSET" in page_query


@pytest.mark.asyncio
async def test_query_audit_logs_null_count_defaults_to_zero(
    service, mock_session
):
    """A NULL count is coerced to 0."""
    mock_session.execute = AsyncMock(
        side_effect=[
            _mock_count_result(None),
            _mock_execute_result([]),
        ]
    )

    result = await service.query_audit_logs(TENANT_ID)

    assert result.total == 0
    assert result.items == []
    assert result.page == 1
    assert result.page_size == 20


@pytest.mark.asyncio
async def test_query_audit_logs_applies_filters(
    service, mock_session
):
    """Every supplied filter reaches the generated SQL."""
    mock_session.execute = AsyncMock(
        side_effect=[
            _mock_count_result(0),
            _mock_execute_result([]),
        ]
    )

    await service.query_audit_logs(
        TENANT_ID,
        user_id=USER_ID,
        action="user.login",
        entity_type="user",
        date_from=datetime.now(UTC) - timedelta(days=1),
        date_to=datetime.now(UTC),
    )

    sql = str(mock_session.execute.await_args_list[1].args[0])
    assert "audit_logs.user_id =" in sql
    assert "audit_logs.action =" in sql
    assert "audit_logs.entity_type =" in sql
    assert "audit_logs.created_at >=" in sql
    assert "audit_logs.created_at <=" in sql


# ── export_audit_logs ──────────────────────────────────────


@pytest.mark.asyncio
async def test_export_audit_logs_returns_flat_list(
    service, mock_session
):
    """Export returns bare responses with no pagination wrapper."""
    logs = [_make_audit_log(), _make_audit_log(id=uuid.uuid4())]
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result(logs)
    )

    result = await service.export_audit_logs(
        TENANT_ID, AuditLogExportRequest()
    )

    assert len(result) == 2
    assert result[0].tenant_id == TENANT_ID
    assert result[0].ip_address == "10.0.0.1"

    sql = str(mock_session.execute.await_args.args[0])
    assert "LIMIT" in sql
    assert "OFFSET" not in sql


@pytest.mark.asyncio
async def test_export_audit_logs_honours_filters(
    service, mock_session
):
    """Export filters are pushed into the query."""
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([])
    )

    result = await service.export_audit_logs(
        TENANT_ID,
        AuditLogExportRequest(action="user.login", user_id=USER_ID),
    )

    assert result == []
    sql = str(mock_session.execute.await_args.args[0])
    assert "audit_logs.action =" in sql
    assert "audit_logs.user_id =" in sql
    assert "audit_logs.entity_type =" not in sql


# ── log_action ─────────────────────────────────────────────


@pytest.mark.asyncio
async def test_log_action_persists_entry(service, mock_session):
    """An audit entry is added, flushed and returned."""
    entity_id = uuid.uuid4()

    result = await service.log_action(
        TENANT_ID,
        USER_ID,
        "vendor.deleted",
        entity_type="vendor",
        entity_id=entity_id,
        details={"reason": "offboarded"},
        ip_address="192.0.2.7",
    )

    created = mock_session.added[0]
    assert isinstance(created, AuditLog)
    mock_session.flush.assert_awaited_once()

    assert result.tenant_id == TENANT_ID
    assert result.user_id == USER_ID
    assert result.action == "vendor.deleted"
    assert result.entity_type == "vendor"
    assert result.entity_id == entity_id
    assert result.details == {"reason": "offboarded"}
    assert result.ip_address == "192.0.2.7"
    assert result.id == created.id


@pytest.mark.asyncio
async def test_log_action_system_event_without_user(
    service, mock_session
):
    """System events may omit the acting user and all optionals."""
    result = await service.log_action(TENANT_ID, None, "system.startup")

    assert result.user_id is None
    assert result.action == "system.startup"
    assert result.entity_type is None
    assert result.entity_id is None
    assert result.details is None
    assert result.ip_address is None


# ── _get_user ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_user_scopes_by_tenant_and_id(
    service, mock_session
):
    """The lookup filters on both id and tenant_id."""
    user = _make_user()
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([user])
    )

    assert await service._get_user(TENANT_ID, USER_ID) is user

    sql = str(mock_session.execute.await_args.args[0])
    assert "users.id =" in sql
    assert "users.tenant_id =" in sql


# ── _to_user_response ──────────────────────────────────────


def test_to_user_response_maps_all_fields(service):
    """Every response field is sourced from the ORM object."""
    last_login = datetime.now(UTC) - timedelta(hours=2)
    user = _make_user(mfa_enabled=True, last_login_at=last_login)

    result = service._to_user_response(user)

    assert result.id == USER_ID
    assert result.tenant_id == TENANT_ID
    assert result.first_name == "Jane"
    assert result.last_name == "Doe"
    assert result.email == DECRYPTED_EMAIL
    assert result.is_active is True
    assert result.mfa_enabled is True
    assert result.last_login_at == last_login
    assert result.roles == ["Admin"]


def test_to_user_response_email_none_when_decrypt_fails(service):
    """A decryption failure degrades to email=None, not an error."""
    service._encryptor.decrypt.side_effect = ValueError("bad key")

    result = service._to_user_response(_make_user())

    assert result.email is None
    assert result.first_name == "Jane"


def test_to_user_response_collects_multiple_role_names(service):
    """Names from every assigned role are collected in order."""
    user = _make_user(
        user_roles=[
            _make_user_role(role=_make_role(name="Admin")),
            _make_user_role(role=_make_role(name="Analyst")),
        ]
    )

    assert service._to_user_response(user).roles == ["Admin", "Analyst"]


def test_to_user_response_skips_null_roles(service):
    """Join rows with no role, or a nameless role, are skipped."""
    user = _make_user(
        user_roles=[
            _make_user_role(role=None),
            _make_user_role(role=_make_role(name=None)),
            _make_user_role(role=_make_role(name="Analyst")),
        ]
    )

    assert service._to_user_response(user).roles == ["Analyst"]


def test_to_user_response_handles_no_roles(service):
    """A None relationship collapses to an empty role list."""
    assert service._to_user_response(_make_user(user_roles=None)).roles == []


def test_to_user_response_survives_unloadable_relationship(service):
    """A relationship that raises on access yields empty roles."""
    user = _make_user(user_roles=_RaisingRelationship())

    result = service._to_user_response(user)

    assert result.roles == []
    assert result.email == DECRYPTED_EMAIL


# ── _to_role_response ──────────────────────────────────────


def test_to_role_response_maps_fields():
    """Role fields map straight through."""
    role = _make_role(is_default=True)

    result = AdminService._to_role_response(role)

    assert result.id == ROLE_ID
    assert result.name == "Admin"
    assert result.description == "Full access"
    assert result.permissions == ["vendors.read", "vendors.write"]
    assert result.is_system is True
    assert result.is_default is True


def test_to_role_response_null_permissions_becomes_empty_list():
    """A NULL permissions column becomes []."""
    result = AdminService._to_role_response(_make_role(permissions=None))

    assert result.permissions == []


# ── _to_audit_response ─────────────────────────────────────


def test_to_audit_response_maps_fields():
    """Audit log fields map straight through."""
    log = _make_audit_log()

    result = AdminService._to_audit_response(log)

    assert result.id == LOG_ID
    assert result.tenant_id == TENANT_ID
    assert result.user_id == USER_ID
    assert result.action == "vendor.created"
    assert result.details == {"name": "Acme"}
    assert result.ip_address == "10.0.0.1"


def test_to_audit_response_allows_nullable_fields():
    """Optional columns are allowed to be None."""
    log = _make_audit_log(
        user_id=None,
        entity_type=None,
        entity_id=None,
        details=None,
        ip_address=None,
    )

    result = AdminService._to_audit_response(log)

    assert result.user_id is None
    assert result.entity_type is None
    assert result.details is None


# ── _apply_audit_filters ───────────────────────────────────


def test_apply_audit_filters_no_filters_is_a_noop():
    """With no filters the query is unchanged."""
    base = select(AuditLog)

    result = AdminService._apply_audit_filters(
        base, None, None, None, None, None
    )

    assert str(result) == str(base)


def test_apply_audit_filters_adds_each_clause():
    """Each supplied filter contributes a WHERE clause."""
    now = datetime.now(UTC)

    result = AdminService._apply_audit_filters(
        select(AuditLog),
        USER_ID,
        "user.login",
        "user",
        now - timedelta(days=7),
        now,
    )

    sql = str(result)
    assert sql.count("WHERE") == 1
    assert sql.count("AND") == 4
    assert "audit_logs.user_id =" in sql
    assert "audit_logs.action =" in sql
    assert "audit_logs.entity_type =" in sql
    assert "audit_logs.created_at >=" in sql
    assert "audit_logs.created_at <=" in sql


def test_apply_audit_filters_partial_filters():
    """Only the supplied filters appear in the SQL."""
    sql = str(
        AdminService._apply_audit_filters(
            select(AuditLog), None, "user.login", None, None, None
        )
    )

    assert "audit_logs.action =" in sql
    assert "audit_logs.user_id =" not in sql
    assert "audit_logs.created_at >=" not in sql


def test_apply_audit_filters_preserves_existing_where():
    """Filters are appended to an already-filtered query."""
    base = select(AuditLog).where(AuditLog.tenant_id == TENANT_ID)

    sql = str(
        AdminService._apply_audit_filters(
            base, None, "user.login", None, None, None
        )
    )

    assert "audit_logs.tenant_id =" in sql
    assert "audit_logs.action =" in sql
