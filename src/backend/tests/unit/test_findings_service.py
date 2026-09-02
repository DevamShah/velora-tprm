"""
Unit tests for FindingsService.

Mocks the database session to exercise finding CRUD, closure,
remediation actions, and the ORM-to-schema mappers without any
infrastructure dependency.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.modules.findings.models import Finding, RemediationAction
from app.modules.findings.schemas import (
    FindingClose,
    FindingCreate,
    FindingSeverity,
    FindingStatus,
    FindingUpdate,
    RemediationCreate,
    RemediationStatus,
    RemediationUpdate,
)
from app.modules.findings.service import FindingsService

TENANT_ID = uuid.UUID("00000000-0000-4000-a000-000000000001")
USER_ID = uuid.UUID("00000000-0000-4000-a000-000000000010")
VENDOR_ID = uuid.UUID("00000000-0000-4000-a000-000000000100")
ASSESSMENT_ID = uuid.UUID("00000000-0000-4000-a000-000000000200")
FINDING_ID = uuid.UUID("00000000-0000-4000-a000-000000000700")
ACTION_ID = uuid.UUID("00000000-0000-4000-a000-000000000800")


# ── model factories ────────────────────────────────────────


def _make_remediation(**overrides) -> RemediationAction:
    """Create a RemediationAction ORM double with defaults."""
    now = datetime.now(UTC)
    defaults = dict(
        id=ACTION_ID,
        tenant_id=TENANT_ID,
        finding_id=FINDING_ID,
        action_type="patch",
        description="Apply vendor patch 4.2.1",
        status="pending",
        effort_estimate="2d",
        completed_at=None,
        created_at=now,
        updated_at=now,
    )
    defaults.update(overrides)
    action = MagicMock(spec=RemediationAction)
    for k, v in defaults.items():
        setattr(action, k, v)
    return action


def _make_finding(**overrides) -> Finding:
    """Create a Finding ORM double with sensible defaults."""
    now = datetime.now(UTC)
    defaults = dict(
        id=FINDING_ID,
        tenant_id=TENANT_ID,
        vendor_id=VENDOR_ID,
        assessment_id=ASSESSMENT_ID,
        title="MFA not enforced",
        description="Admin console allows password-only login",
        severity="high",
        status="open",
        affected_controls=["AC-2", "IA-2"],
        remediation_guidance="Enable MFA for all admins",
        sla_due_date=now + timedelta(days=30),
        assigned_to=USER_ID,
        closed_at=None,
        remediation_actions=[],
        created_at=now,
        updated_at=now,
    )
    defaults.update(overrides)
    finding = MagicMock(spec=Finding)
    for k, v in defaults.items():
        setattr(finding, k, v)
    return finding


class _DetachedRelation:
    """Stand-in for a relationship that cannot be lazy-loaded."""

    def __bool__(self) -> bool:
        raise RuntimeError("greenlet_spawn has not been called")


def _mock_execute_result(items):
    """Create a mock execute result that returns scalars."""
    result = MagicMock()
    scalars = MagicMock()
    scalars.first.return_value = items[0] if items else None
    scalars.all.return_value = items
    result.scalars.return_value = scalars
    result.scalar.return_value = len(items)
    return result


def _count_result(total):
    """Create a mock execute result for a COUNT query."""
    result = MagicMock()
    result.scalar.return_value = total
    return result


@pytest.fixture
def mock_session():
    """Async mock session."""
    session = AsyncMock()
    session.add = MagicMock()
    return session


@pytest.fixture
def service(mock_session):
    """FindingsService bound to the mocked session."""
    return FindingsService(mock_session)


# ── list_findings ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_findings_returns_paginated_items(
    service, mock_session
):
    """list_findings maps rows and echoes pagination inputs."""
    finding = _make_finding()
    mock_session.execute = AsyncMock(
        side_effect=[
            _count_result(42),
            _mock_execute_result([finding]),
        ]
    )

    result = await service.list_findings(
        TENANT_ID, page=3, page_size=15
    )

    assert result.total == 42
    assert result.page == 3
    assert result.page_size == 15
    assert len(result.items) == 1
    assert result.items[0].id == FINDING_ID
    assert result.items[0].severity == "high"


@pytest.mark.asyncio
async def test_list_findings_null_count_coerced_to_zero(
    service, mock_session
):
    """A NULL count from the DB becomes 0, not None."""
    null_count = MagicMock()
    null_count.scalar.return_value = None
    mock_session.execute = AsyncMock(
        side_effect=[null_count, _mock_execute_result([])]
    )

    result = await service.list_findings(TENANT_ID)

    assert result.total == 0
    assert result.items == []
    assert result.page == 1
    assert result.page_size == 20


@pytest.mark.asyncio
async def test_list_findings_no_filters_only_scopes_tenant(
    service, mock_session
):
    """With no filters only the tenant predicate is applied."""
    mock_session.execute = AsyncMock(
        side_effect=[_count_result(0), _mock_execute_result([])]
    )

    await service.list_findings(TENANT_ID)

    listing_query = mock_session.execute.await_args_list[1].args[0]
    sql = str(listing_query)
    assert "findings.vendor_id =" not in sql
    assert "findings.severity =" not in sql
    assert "findings.status =" not in sql


@pytest.mark.asyncio
async def test_list_findings_applies_all_filters(
    service, mock_session
):
    """vendor_id, severity, and status each add a predicate."""
    mock_session.execute = AsyncMock(
        side_effect=[_count_result(0), _mock_execute_result([])]
    )

    await service.list_findings(
        TENANT_ID,
        vendor_id=VENDOR_ID,
        severity="critical",
        status="open",
    )

    listing_query = mock_session.execute.await_args_list[1].args[0]
    sql = str(
        listing_query.whereclause.compile(
            compile_kwargs={"literal_binds": True}
        )
    )
    assert "findings.severity = 'critical'" in sql
    assert "findings.status = 'open'" in sql
    assert "findings.vendor_id" in sql


@pytest.mark.asyncio
async def test_list_findings_orders_newest_first(
    service, mock_session
):
    """Findings are listed newest-first."""
    mock_session.execute = AsyncMock(
        side_effect=[_count_result(0), _mock_execute_result([])]
    )

    await service.list_findings(TENANT_ID)

    listing_query = mock_session.execute.await_args_list[1].args[0]
    assert "ORDER BY findings.created_at DESC" in str(
        listing_query
    )


# ── get_finding ────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_finding_found(service, mock_session):
    """get_finding maps the row including remediation actions."""
    finding = _make_finding(
        remediation_actions=[_make_remediation()]
    )
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([finding])
    )

    result = await service.get_finding(TENANT_ID, FINDING_ID)

    assert result is not None
    assert result.id == FINDING_ID
    assert result.title == "MFA not enforced"
    assert len(result.remediation_actions) == 1
    assert result.remediation_actions[0].id == ACTION_ID


@pytest.mark.asyncio
async def test_get_finding_missing_returns_none(
    service, mock_session
):
    """get_finding returns None when nothing matches."""
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([])
    )

    assert (
        await service.get_finding(TENANT_ID, FINDING_ID) is None
    )


# ── create_finding ─────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_finding(service, mock_session):
    """create_finding persists a new open finding."""
    due = datetime.now(UTC) + timedelta(days=14)
    created = _make_finding(
        title="Backups not encrypted",
        severity="critical",
        status="open",
        sla_due_date=due,
    )
    data = FindingCreate(
        vendor_id=VENDOR_ID,
        assessment_id=ASSESSMENT_ID,
        title="Backups not encrypted",
        description="Nightly dumps land unencrypted in S3",
        severity=FindingSeverity.critical,
        affected_controls=["SC-28"],
        remediation_guidance="Enable SSE-KMS",
        sla_due_date=due,
        assigned_to=USER_ID,
    )

    with patch(
        "app.modules.findings.service.Finding",
        return_value=created,
    ) as finding_cls:
        result = await service.create_finding(TENANT_ID, data)

    kwargs = finding_cls.call_args.kwargs
    assert kwargs["tenant_id"] == TENANT_ID
    assert kwargs["severity"] == "critical"
    assert kwargs["status"] == "open"
    assert kwargs["affected_controls"] == ["SC-28"]
    assert kwargs["sla_due_date"] == due
    mock_session.add.assert_called_once_with(created)
    mock_session.flush.assert_awaited_once()
    assert result.title == "Backups not encrypted"
    assert result.status == "open"


@pytest.mark.asyncio
async def test_create_finding_defaults(service, mock_session):
    """Severity defaults to medium and optionals stay None."""
    created = _make_finding(
        severity="medium",
        assessment_id=None,
        affected_controls=None,
        description=None,
        remediation_guidance=None,
        sla_due_date=None,
        assigned_to=None,
    )
    data = FindingCreate(vendor_id=VENDOR_ID, title="Minor gap")

    with patch(
        "app.modules.findings.service.Finding",
        return_value=created,
    ) as finding_cls:
        result = await service.create_finding(TENANT_ID, data)

    kwargs = finding_cls.call_args.kwargs
    assert kwargs["severity"] == "medium"
    assert kwargs["assessment_id"] is None
    assert kwargs["affected_controls"] is None
    assert result.severity == "medium"
    assert result.assessment_id is None


# ── update_finding ─────────────────────────────────────────


@pytest.mark.asyncio
async def test_update_finding_unwraps_enum_values(
    service, mock_session
):
    """Enum fields are stored as their string values."""
    finding = _make_finding()
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([finding])
    )

    result = await service.update_finding(
        TENANT_ID,
        FINDING_ID,
        FindingUpdate(
            severity=FindingSeverity.low,
            status=FindingStatus.remediation_in_progress,
        ),
    )

    assert finding.severity == "low"
    assert finding.status == "remediation_in_progress"
    assert result.severity == "low"
    assert result.status == "remediation_in_progress"
    mock_session.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_finding_leaves_unset_fields_alone(
    service, mock_session
):
    """Only explicitly supplied fields are written."""
    finding = _make_finding()
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([finding])
    )

    result = await service.update_finding(
        TENANT_ID,
        FINDING_ID,
        FindingUpdate(title="MFA not enforced (confirmed)"),
    )

    assert finding.title == "MFA not enforced (confirmed)"
    assert finding.severity == "high"
    assert finding.status == "open"
    assert result.title == "MFA not enforced (confirmed)"


@pytest.mark.asyncio
async def test_update_finding_accepts_explicit_nulls(
    service, mock_session
):
    """Explicitly passing None clears the field."""
    finding = _make_finding()
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([finding])
    )

    result = await service.update_finding(
        TENANT_ID,
        FINDING_ID,
        FindingUpdate(assigned_to=None, sla_due_date=None),
    )

    assert finding.assigned_to is None
    assert finding.sla_due_date is None
    assert result.assigned_to is None


@pytest.mark.asyncio
async def test_update_finding_missing_returns_none(
    service, mock_session
):
    """Updating an unknown finding is a no-op."""
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([])
    )

    result = await service.update_finding(
        TENANT_ID, FINDING_ID, FindingUpdate(title="Nope")
    )

    assert result is None
    mock_session.flush.assert_not_awaited()


# ── close_finding ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_close_finding_sets_status_and_timestamp(
    service, mock_session
):
    """close_finding stamps the terminal status and closed_at."""
    finding = _make_finding()
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([finding])
    )

    result = await service.close_finding(
        TENANT_ID,
        FINDING_ID,
        FindingClose(status=FindingStatus.verified_closed),
    )

    assert finding.status == "verified_closed"
    assert isinstance(finding.closed_at, datetime)
    assert finding.closed_at.tzinfo is not None
    assert result.status == "verified_closed"
    assert result.closed_at == finding.closed_at
    mock_session.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_close_finding_risk_accepted(
    service, mock_session
):
    """Any terminal status from the enum is accepted."""
    finding = _make_finding()
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([finding])
    )

    result = await service.close_finding(
        TENANT_ID,
        FINDING_ID,
        FindingClose(status=FindingStatus.risk_accepted),
    )

    assert result.status == "risk_accepted"


@pytest.mark.asyncio
async def test_close_finding_missing_returns_none(
    service, mock_session
):
    """Closing an unknown finding is a no-op."""
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([])
    )

    result = await service.close_finding(
        TENANT_ID,
        FINDING_ID,
        FindingClose(status=FindingStatus.wont_fix),
    )

    assert result is None
    mock_session.flush.assert_not_awaited()


# ── add_remediation ────────────────────────────────────────


@pytest.mark.asyncio
async def test_add_remediation(service, mock_session):
    """add_remediation attaches a pending action."""
    finding = _make_finding()
    action = _make_remediation(
        action_type="compensating_control",
        description="Restrict admin console to VPN",
        effort_estimate="1w",
    )
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([finding])
    )

    with patch(
        "app.modules.findings.service.RemediationAction",
        return_value=action,
    ) as action_cls:
        result = await service.add_remediation(
            TENANT_ID,
            FINDING_ID,
            RemediationCreate(
                action_type="compensating_control",
                description="Restrict admin console to VPN",
                effort_estimate="1w",
            ),
        )

    action_cls.assert_called_once_with(
        tenant_id=TENANT_ID,
        finding_id=FINDING_ID,
        action_type="compensating_control",
        description="Restrict admin console to VPN",
        status="pending",
        effort_estimate="1w",
    )
    mock_session.add.assert_called_once_with(action)
    mock_session.flush.assert_awaited_once()
    assert result.status == "pending"
    assert result.finding_id == FINDING_ID
    assert result.effort_estimate == "1w"


@pytest.mark.asyncio
async def test_add_remediation_missing_finding_returns_none(
    service, mock_session
):
    """No action is created for an unknown finding."""
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([])
    )

    result = await service.add_remediation(
        TENANT_ID,
        FINDING_ID,
        RemediationCreate(action_type="patch", description="x"),
    )

    assert result is None
    mock_session.add.assert_not_called()
    mock_session.flush.assert_not_awaited()


# ── update_remediation ─────────────────────────────────────


@pytest.mark.asyncio
async def test_update_remediation_completed_sets_timestamp(
    service, mock_session
):
    """Moving an action to completed stamps completed_at."""
    action = _make_remediation()
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([action])
    )

    result = await service.update_remediation(
        TENANT_ID,
        FINDING_ID,
        ACTION_ID,
        RemediationUpdate(status=RemediationStatus.completed),
    )

    assert action.status == "completed"
    assert isinstance(action.completed_at, datetime)
    assert result.status == "completed"
    assert result.completed_at == action.completed_at
    mock_session.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_remediation_in_progress_leaves_timestamp_null(
    service, mock_session
):
    """A non-completed status does not stamp completed_at."""
    action = _make_remediation()
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([action])
    )

    result = await service.update_remediation(
        TENANT_ID,
        FINDING_ID,
        ACTION_ID,
        RemediationUpdate(status=RemediationStatus.in_progress),
    )

    assert action.status == "in_progress"
    assert action.completed_at is None
    assert result.completed_at is None


@pytest.mark.asyncio
async def test_update_remediation_non_status_field(
    service, mock_session
):
    """Editing description alone leaves the status untouched."""
    action = _make_remediation()
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([action])
    )

    result = await service.update_remediation(
        TENANT_ID,
        FINDING_ID,
        ACTION_ID,
        RemediationUpdate(description="Apply patch 4.2.2"),
    )

    assert action.description == "Apply patch 4.2.2"
    assert action.status == "pending"
    assert action.completed_at is None
    assert result.description == "Apply patch 4.2.2"


@pytest.mark.asyncio
async def test_update_remediation_already_completed_restamps(
    service, mock_session
):
    """An already-completed action is re-stamped on any edit."""
    action = _make_remediation(
        status="completed", completed_at=None
    )
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([action])
    )

    await service.update_remediation(
        TENANT_ID,
        FINDING_ID,
        ACTION_ID,
        RemediationUpdate(effort_estimate="4h"),
    )

    assert action.effort_estimate == "4h"
    assert isinstance(action.completed_at, datetime)


@pytest.mark.asyncio
async def test_update_remediation_missing_returns_none(
    service, mock_session
):
    """Updating an unknown action is a no-op."""
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([])
    )

    result = await service.update_remediation(
        TENANT_ID,
        FINDING_ID,
        ACTION_ID,
        RemediationUpdate(description="x"),
    )

    assert result is None
    mock_session.flush.assert_not_awaited()


@pytest.mark.asyncio
async def test_update_remediation_scopes_query_to_tenant(
    service, mock_session
):
    """The lookup is scoped by action, finding, and tenant."""
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([_make_remediation()])
    )

    await service.update_remediation(
        TENANT_ID,
        FINDING_ID,
        ACTION_ID,
        RemediationUpdate(description="x"),
    )

    query = mock_session.execute.await_args.args[0]
    sql = str(query.whereclause)
    assert "remediation_actions.id =" in sql
    assert "remediation_actions.finding_id =" in sql
    assert "remediation_actions.tenant_id =" in sql


# ── response mappers ───────────────────────────────────────


def test_to_response_maps_every_field():
    """_to_response copies the full finding record."""
    closed = datetime.now(UTC)
    finding = _make_finding(
        status="verified_closed", closed_at=closed
    )

    out = FindingsService._to_response(finding)

    assert out.id == FINDING_ID
    assert out.tenant_id == TENANT_ID
    assert out.vendor_id == VENDOR_ID
    assert out.assessment_id == ASSESSMENT_ID
    assert out.title == "MFA not enforced"
    assert out.severity == "high"
    assert out.status == "verified_closed"
    assert out.affected_controls == ["AC-2", "IA-2"]
    assert out.remediation_guidance == "Enable MFA for all admins"
    assert out.assigned_to == USER_ID
    assert out.closed_at == closed
    assert out.remediation_actions == []


def test_to_response_maps_nested_actions():
    """Related remediation actions are mapped in order."""
    finding = _make_finding(
        remediation_actions=[
            _make_remediation(action_type="patch"),
            _make_remediation(
                id=uuid.uuid4(),
                action_type="policy",
                status="completed",
                completed_at=datetime.now(UTC),
            ),
        ]
    )

    out = FindingsService._to_response(finding)

    assert [a.action_type for a in out.remediation_actions] == [
        "patch",
        "policy",
    ]
    assert out.remediation_actions[0].completed_at is None
    assert out.remediation_actions[1].status == "completed"


def test_to_response_handles_null_relationship():
    """A None relationship degrades to an empty list."""
    finding = _make_finding(remediation_actions=None)

    out = FindingsService._to_response(finding)

    assert out.remediation_actions == []


def test_to_response_swallows_unloadable_relationship():
    """A failing lazy load is logged, not raised."""
    finding = _make_finding(
        remediation_actions=_DetachedRelation()
    )

    with patch(
        "app.modules.findings.service.logger"
    ) as mock_logger:
        out = FindingsService._to_response(finding)

    assert out.remediation_actions == []
    assert out.id == FINDING_ID
    mock_logger.warning.assert_called_once()
    assert (
        mock_logger.warning.call_args.args[0]
        == "findings.remediation_actions_unavailable"
    )


def test_to_response_nullable_fields():
    """Optional finding fields survive as None."""
    finding = _make_finding(
        assessment_id=None,
        description=None,
        affected_controls=None,
        remediation_guidance=None,
        sla_due_date=None,
        assigned_to=None,
    )

    out = FindingsService._to_response(finding)

    assert out.assessment_id is None
    assert out.description is None
    assert out.affected_controls is None
    assert out.remediation_guidance is None
    assert out.sla_due_date is None
    assert out.assigned_to is None


def test_to_remediation_maps_every_field():
    """_to_remediation copies the full action record."""
    completed = datetime.now(UTC)
    action = _make_remediation(
        status="verified", completed_at=completed
    )

    out = FindingsService._to_remediation(action)

    assert out.id == ACTION_ID
    assert out.finding_id == FINDING_ID
    assert out.action_type == "patch"
    assert out.description == "Apply vendor patch 4.2.1"
    assert out.status == "verified"
    assert out.effort_estimate == "2d"
    assert out.completed_at == completed


def test_to_remediation_nullable_fields():
    """Optional action fields survive as None."""
    action = _make_remediation(
        effort_estimate=None, completed_at=None
    )

    out = FindingsService._to_remediation(action)

    assert out.effort_estimate is None
    assert out.completed_at is None
