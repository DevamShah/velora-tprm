"""
Unit tests for AuthService.

Mocks the database session and FieldEncryptor, but exercises the
real JWT and bcrypt primitives so token issuance, rotation and
credential checks are verified end to end.
"""

from __future__ import annotations

import hashlib
import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from jose import jwt

from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
)
from app.modules.auth.models import RefreshToken, Role, User, UserRole
from app.modules.auth.service import AuthService, _sha256

TENANT_ID = uuid.UUID("00000000-0000-4000-a000-000000000001")
USER_ID = uuid.UUID("00000000-0000-4000-a000-000000000010")
ROLE_ID = uuid.UUID("00000000-0000-4000-a000-000000000020")

JWT_SECRET = "unit-test-jwt-secret-key-at-least-32-chars"
JWT_ALGORITHM = "HS256"
ACCESS_MINUTES = 30
REFRESH_DAYS = 7

PASSWORD = "correct horse battery staple"
# Computed once — bcrypt cost 12 is deliberately slow.
PASSWORD_HASH = hash_password(PASSWORD)


def _make_role(**overrides) -> Role:
    """Create a Role ORM stand-in with defaults."""
    defaults = dict(
        id=ROLE_ID,
        tenant_id=TENANT_ID,
        name="Admin",
        description="Full access",
        permissions=["vendors.read", "vendors.write"],
        is_system=True,
        is_default=False,
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
        email_encrypted="enc:user@example.com",
        email_hash="emailhash",
        first_name="Jane",
        last_name="Doe",
        password_hash=PASSWORD_HASH,
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


def _make_refresh_record(**overrides) -> RefreshToken:
    """Create a stored RefreshToken stand-in."""
    now = datetime.now(UTC)
    defaults = dict(
        id=uuid.uuid4(),
        tenant_id=TENANT_ID,
        user_id=USER_ID,
        token_hash="stored-hash",
        expires_at=now + timedelta(days=REFRESH_DAYS),
        revoked_at=None,
        device_info=None,
        created_at=now,
        updated_at=now,
    )
    defaults.update(overrides)
    record = MagicMock(spec=RefreshToken)
    for k, v in defaults.items():
        setattr(record, k, v)
    return record


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


@pytest.fixture
def mock_session():
    """Async mock session."""
    session = AsyncMock()
    session.add = MagicMock()
    return session


@pytest.fixture
def service(mock_session):
    """AuthService with mocked session, settings and encryptor."""
    with patch(
        "app.modules.auth.service.get_settings"
    ) as mock_settings, patch(
        "app.modules.auth.service.FieldEncryptor"
    ) as mock_enc_cls:
        settings = MagicMock()
        settings.ENCRYPTION_KEY = "dGVzdC1rZXktdGhhdC1pcy0zMi1ieXRlcw=="
        settings.JWT_SECRET_KEY = JWT_SECRET
        settings.JWT_ALGORITHM = JWT_ALGORITHM
        settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES = ACCESS_MINUTES
        settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS = REFRESH_DAYS
        mock_settings.return_value = settings

        enc = MagicMock()
        enc.encrypt.return_value = "encrypted_value"
        enc.decrypt.return_value = "user@example.com"
        enc.hmac_hash.return_value = "emailhash"
        mock_enc_cls.return_value = enc

        svc = AuthService(mock_session)
        svc._encryptor = enc
        yield svc


# ── authenticate ───────────────────────────────────────────


@pytest.mark.asyncio
async def test_authenticate_success(service, mock_session):
    """Valid credentials return the user and stamp last_login_at."""
    user = _make_user()
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([user])
    )

    result = await service.authenticate("user@example.com", PASSWORD)

    assert result is user
    assert isinstance(user.last_login_at, datetime)


@pytest.mark.asyncio
async def test_authenticate_looks_up_by_hmac_hash(
    service, mock_session
):
    """Lookup hashes the email rather than decrypting rows."""
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([])
    )

    await service.authenticate("User@Example.com", PASSWORD)

    service._encryptor.hmac_hash.assert_called_once_with(
        "User@Example.com"
    )
    service._encryptor.decrypt.assert_not_called()


@pytest.mark.asyncio
async def test_authenticate_unknown_user_returns_none(
    service, mock_session
):
    """No matching row returns None."""
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([])
    )

    result = await service.authenticate("nobody@example.com", PASSWORD)

    assert result is None


@pytest.mark.asyncio
async def test_authenticate_bad_password_returns_none(
    service, mock_session
):
    """A wrong password returns None and leaves last_login_at unset."""
    user = _make_user()
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([user])
    )

    result = await service.authenticate(
        "user@example.com", "not-the-password"
    )

    assert result is None
    assert user.last_login_at is None


# ── create_tokens ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_tokens_returns_valid_pair(
    service, mock_session
):
    """Both tokens decode and carry identity + permission claims."""
    user = _make_user()

    tokens = await service.create_tokens(user)

    assert tokens.token_type == "bearer"
    assert tokens.expires_in == ACCESS_MINUTES * 60

    access = jwt.decode(
        tokens.access_token, JWT_SECRET, algorithms=[JWT_ALGORITHM]
    )
    assert access["sub"] == str(USER_ID)
    assert access["tenant_id"] == str(TENANT_ID)
    assert access["roles"] == ["Admin"]
    assert access["permissions"] == ["vendors.read", "vendors.write"]
    assert access["type"] == "access"

    refresh = jwt.decode(
        tokens.refresh_token, JWT_SECRET, algorithms=[JWT_ALGORITHM]
    )
    assert refresh["type"] == "refresh"
    assert refresh["sub"] == str(USER_ID)


@pytest.mark.asyncio
async def test_create_tokens_persists_hashed_refresh_token(
    service, mock_session
):
    """The refresh token is stored hashed, never in plaintext."""
    user = _make_user()

    tokens = await service.create_tokens(user)

    mock_session.add.assert_called_once()
    record = mock_session.add.call_args.args[0]
    assert isinstance(record, RefreshToken)
    assert record.user_id == USER_ID
    assert record.tenant_id == TENANT_ID
    assert record.token_hash == _sha256(tokens.refresh_token)
    assert record.token_hash != tokens.refresh_token
    assert record.expires_at > datetime.now(UTC) + timedelta(
        days=REFRESH_DAYS - 1
    )
    mock_session.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_tokens_merges_permissions_across_roles(
    service, mock_session
):
    """Permissions from every role are merged, deduped and sorted."""
    user = _make_user(
        user_roles=[
            _make_user_role(
                role=_make_role(
                    name="Analyst",
                    permissions=["vendors.read", "assessments.read"],
                )
            ),
            _make_user_role(
                role=_make_role(
                    name="Admin",
                    permissions=["vendors.read", "admin.write"],
                )
            ),
        ]
    )

    tokens = await service.create_tokens(user)
    access = jwt.decode(
        tokens.access_token, JWT_SECRET, algorithms=[JWT_ALGORITHM]
    )

    assert access["roles"] == ["Analyst", "Admin"]
    assert access["permissions"] == [
        "admin.write",
        "assessments.read",
        "vendors.read",
    ]


# ── _collect_permissions ───────────────────────────────────


def test_collect_permissions_sorted_and_deduped():
    """Duplicate permissions collapse into a sorted list."""
    user = _make_user(
        user_roles=[
            _make_user_role(
                role=_make_role(permissions=["b.read", "a.read"])
            ),
            _make_user_role(
                role=_make_role(permissions=["a.read", "c.read"])
            ),
        ]
    )

    assert AuthService._collect_permissions(user) == [
        "a.read",
        "b.read",
        "c.read",
    ]


def test_collect_permissions_no_roles():
    """A user with no roles has no permissions."""
    assert AuthService._collect_permissions(_make_user(user_roles=[])) == []


def test_collect_permissions_skips_null_role_and_empty_perms():
    """Rows with a missing role or empty permissions are skipped."""
    user = _make_user(
        user_roles=[
            _make_user_role(role=None),
            _make_user_role(role=_make_role(permissions=[])),
            _make_user_role(role=_make_role(permissions=["x.read"])),
        ]
    )

    assert AuthService._collect_permissions(user) == ["x.read"]


# ── refresh_tokens ─────────────────────────────────────────


@pytest.mark.asyncio
async def test_refresh_tokens_rotates_pair(service, mock_session):
    """A valid refresh token is revoked and a new pair issued."""
    raw = create_refresh_token(
        {"sub": str(USER_ID)}, JWT_SECRET, expires_days=REFRESH_DAYS
    )
    stored = _make_refresh_record(token_hash=_sha256(raw))
    user = _make_user()

    mock_session.execute = AsyncMock(
        side_effect=[
            _mock_execute_result([stored]),
            _mock_execute_result([user]),
        ]
    )

    result = await service.refresh_tokens(raw)

    assert result is not None
    assert isinstance(stored.revoked_at, datetime)
    new_payload = jwt.decode(
        result.refresh_token, JWT_SECRET, algorithms=[JWT_ALGORITHM]
    )
    assert new_payload["sub"] == str(USER_ID)
    mock_session.add.assert_called_once()


@pytest.mark.asyncio
async def test_refresh_tokens_rejects_invalid_token(
    service, mock_session
):
    """A malformed token short-circuits before any DB access."""
    result = await service.refresh_tokens("garbage.token.value")

    assert result is None
    mock_session.execute.assert_not_awaited()


@pytest.mark.asyncio
async def test_refresh_tokens_rejects_access_token(
    service, mock_session
):
    """An access token cannot be exchanged for a new pair."""
    access = create_access_token({"sub": str(USER_ID)}, JWT_SECRET)

    assert await service.refresh_tokens(access) is None


@pytest.mark.asyncio
async def test_refresh_tokens_rejects_foreign_signature(
    service, mock_session
):
    """A refresh token signed with another key is rejected."""
    raw = create_refresh_token(
        {"sub": str(USER_ID)}, "some-other-secret-key-32-characters"
    )

    assert await service.refresh_tokens(raw) is None


@pytest.mark.asyncio
async def test_refresh_tokens_rejects_unknown_or_revoked_token(
    service, mock_session
):
    """A valid JWT with no live DB row is rejected."""
    raw = create_refresh_token({"sub": str(USER_ID)}, JWT_SECRET)
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([])
    )

    result = await service.refresh_tokens(raw)

    assert result is None
    mock_session.add.assert_not_called()


@pytest.mark.asyncio
async def test_refresh_tokens_rejects_missing_user(
    service, mock_session
):
    """A token whose subject no longer exists is rejected."""
    raw = create_refresh_token({"sub": str(USER_ID)}, JWT_SECRET)
    stored = _make_refresh_record(token_hash=_sha256(raw))

    mock_session.execute = AsyncMock(
        side_effect=[
            _mock_execute_result([stored]),
            _mock_execute_result([]),
        ]
    )

    assert await service.refresh_tokens(raw) is None
    assert isinstance(stored.revoked_at, datetime)


@pytest.mark.asyncio
async def test_refresh_tokens_rejects_deactivated_user(
    service, mock_session
):
    """A deactivated user cannot rotate tokens."""
    raw = create_refresh_token({"sub": str(USER_ID)}, JWT_SECRET)
    stored = _make_refresh_record(token_hash=_sha256(raw))
    user = _make_user(is_active=False)

    mock_session.execute = AsyncMock(
        side_effect=[
            _mock_execute_result([stored]),
            _mock_execute_result([user]),
        ]
    )

    assert await service.refresh_tokens(raw) is None
    mock_session.add.assert_not_called()


@pytest.mark.asyncio
async def test_refresh_tokens_looks_up_by_token_hash(
    service, mock_session
):
    """The DB lookup uses the SHA-256 hash, not the raw token."""
    raw = create_refresh_token({"sub": str(USER_ID)}, JWT_SECRET)
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([])
    )

    await service.refresh_tokens(raw)

    compiled = mock_session.execute.await_args.args[0].compile()
    params = compiled.params
    assert _sha256(raw) in params.values()
    assert raw not in params.values()


# ── revoke_refresh_token ───────────────────────────────────


@pytest.mark.asyncio
async def test_revoke_refresh_token_success(service, mock_session):
    """A matched row returns True."""
    result_mock = MagicMock()
    result_mock.rowcount = 1
    mock_session.execute = AsyncMock(return_value=result_mock)

    assert await service.revoke_refresh_token("some-token") is True


@pytest.mark.asyncio
async def test_revoke_refresh_token_no_match(service, mock_session):
    """An already-revoked or unknown token returns False."""
    result_mock = MagicMock()
    result_mock.rowcount = 0
    mock_session.execute = AsyncMock(return_value=result_mock)

    assert await service.revoke_refresh_token("some-token") is False


# ── get_user_by_id / get_user_permissions ──────────────────


@pytest.mark.asyncio
async def test_get_user_by_id_found(service, mock_session):
    """A known ID returns the user."""
    user = _make_user()
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([user])
    )

    assert await service.get_user_by_id(str(USER_ID)) is user


@pytest.mark.asyncio
async def test_get_user_by_id_missing(service, mock_session):
    """An unknown ID returns None."""
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([])
    )

    assert await service.get_user_by_id(str(uuid.uuid4())) is None


@pytest.mark.asyncio
async def test_get_user_permissions_returns_sorted(
    service, mock_session
):
    """Permissions for a known user are aggregated."""
    user = _make_user(
        user_roles=[
            _make_user_role(
                role=_make_role(permissions=["z.read", "a.read"])
            )
        ]
    )
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([user])
    )

    perms = await service.get_user_permissions(str(USER_ID))

    assert perms == ["a.read", "z.read"]


@pytest.mark.asyncio
async def test_get_user_permissions_missing_user(
    service, mock_session
):
    """An unknown user yields an empty permission list."""
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([])
    )

    assert await service.get_user_permissions(str(uuid.uuid4())) == []


# ── _sha256 ────────────────────────────────────────────────


def test_sha256_matches_hashlib():
    """The helper is a plain hex SHA-256 digest."""
    assert _sha256("abc") == hashlib.sha256(b"abc").hexdigest()


def test_sha256_is_deterministic_and_distinguishing():
    """Equal inputs match; different inputs do not."""
    assert _sha256("token-a") == _sha256("token-a")
    assert _sha256("token-a") != _sha256("token-b")
    assert len(_sha256("token-a")) == 64
