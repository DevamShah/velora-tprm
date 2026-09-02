"""
Unit tests for MonitoringService.

Mocks the database session to exercise alert CRUD, rule
evaluation, signal ingestion, and the pure mapping helpers
without any infrastructure dependency.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.modules.monitoring.models import (
    Alert,
    AlertRule,
    MonitoringSignal,
    VendorTimeline,
)
from app.modules.monitoring.schemas import (
    AlertFilterParams,
    AlertPriority,
    AlertRuleCreate,
    AlertRuleUpdate,
    AlertStatus,
    SignalIngestRequest,
    SignalSeverity,
    SortOrder,
)
from app.modules.monitoring.service import MonitoringService

TENANT_ID = uuid.UUID("00000000-0000-4000-a000-000000000001")
USER_ID = uuid.UUID("00000000-0000-4000-a000-000000000010")
VENDOR_ID = uuid.UUID("00000000-0000-4000-a000-000000000100")
ALERT_ID = uuid.UUID("00000000-0000-4000-a000-000000000300")
RULE_ID = uuid.UUID("00000000-0000-4000-a000-000000000400")
SIGNAL_ID = uuid.UUID("00000000-0000-4000-a000-000000000500")
EVENT_ID = uuid.UUID("00000000-0000-4000-a000-000000000600")


# ── model factories ────────────────────────────────────────


def _make_alert(**overrides) -> Alert:
    """Create an Alert ORM double with sensible defaults."""
    now = datetime.now(UTC)
    defaults = dict(
        id=ALERT_ID,
        tenant_id=TENANT_ID,
        vendor_id=VENDOR_ID,
        priority="p2",
        status="new",
        title="Breach reported",
        description="Vendor disclosed an incident",
        signal_ids=[SIGNAL_ID],
        impact_assessment={"source": "news", "severity": "high"},
        acknowledged_by=None,
        resolved_by=None,
        acknowledged_at=None,
        resolved_at=None,
        resolution_notes=None,
        created_at=now,
        updated_at=now,
    )
    defaults.update(overrides)
    alert = MagicMock(spec=Alert)
    for k, v in defaults.items():
        setattr(alert, k, v)
    return alert


def _make_rule(**overrides) -> AlertRule:
    """Create an AlertRule ORM double with defaults."""
    now = datetime.now(UTC)
    defaults = dict(
        id=RULE_ID,
        tenant_id=TENANT_ID,
        name="Critical breaches",
        description="Alert on critical breach signals",
        conditions={"severity": ["critical", "high"]},
        actions={"notify": ["security@example.com"]},
        is_active=True,
        created_at=now,
        updated_at=now,
    )
    defaults.update(overrides)
    rule = MagicMock(spec=AlertRule)
    for k, v in defaults.items():
        setattr(rule, k, v)
    return rule


def _make_signal(**overrides) -> MonitoringSignal:
    """Create a MonitoringSignal ORM double with defaults."""
    now = datetime.now(UTC)
    defaults = dict(
        id=SIGNAL_ID,
        tenant_id=TENANT_ID,
        vendor_id=VENDOR_ID,
        source="haveibeenpwned",
        signal_type="breach",
        severity="critical",
        title="Credential dump",
        description="500k records exposed",
        raw_data={"records": 500000},
        dedup_key="hibp:acme:2026",
        processed=False,
        created_at=now,
        updated_at=now,
    )
    defaults.update(overrides)
    signal = MagicMock(spec=MonitoringSignal)
    for k, v in defaults.items():
        setattr(signal, k, v)
    return signal


def _make_timeline_event(**overrides) -> VendorTimeline:
    """Create a VendorTimeline ORM double with defaults."""
    now = datetime.now(UTC)
    defaults = dict(
        id=EVENT_ID,
        tenant_id=TENANT_ID,
        vendor_id=VENDOR_ID,
        event_type="assessment_completed",
        title="SIG Lite completed",
        description="Vendor returned the questionnaire",
        event_metadata={"assessment_id": "abc"},
        actor_id=USER_ID,
        created_at=now,
        updated_at=now,
    )
    defaults.update(overrides)
    event = MagicMock(spec=VendorTimeline)
    for k, v in defaults.items():
        setattr(event, k, v)
    return event


def _mock_execute_result(items):
    """Create a mock execute result that returns scalars."""
    result = MagicMock()
    scalars = MagicMock()
    scalars.first.return_value = items[0] if items else None
    scalars.all.return_value = items
    result.scalars.return_value = scalars
    result.scalar.return_value = len(items)
    return result


def _count_result(total: int):
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
    """MonitoringService bound to the mocked session."""
    return MonitoringService(mock_session)


# ── _signal_matches_rule ───────────────────────────────────


def test_signal_matches_rule_no_conditions():
    """Empty conditions match every signal."""
    signal = _make_signal()
    rule = _make_rule(conditions={})
    assert (
        MonitoringService._signal_matches_rule(signal, rule)
        is True
    )


def test_signal_matches_rule_null_conditions():
    """conditions=None is treated as an empty dict."""
    signal = _make_signal()
    rule = _make_rule(conditions=None)
    assert (
        MonitoringService._signal_matches_rule(signal, rule)
        is True
    )


def test_signal_matches_rule_severity_list_hit():
    """Severity present in the condition list matches."""
    signal = _make_signal(severity="high")
    rule = _make_rule(
        conditions={"severity": ["critical", "high"]}
    )
    assert (
        MonitoringService._signal_matches_rule(signal, rule)
        is True
    )


def test_signal_matches_rule_severity_list_miss():
    """Severity absent from the condition list fails."""
    signal = _make_signal(severity="low")
    rule = _make_rule(
        conditions={"severity": ["critical", "high"]}
    )
    assert (
        MonitoringService._signal_matches_rule(signal, rule)
        is False
    )


def test_signal_matches_rule_severity_empty_list_never_matches():
    """An empty severity list can never be satisfied."""
    signal = _make_signal(severity="critical")
    rule = _make_rule(conditions={"severity": []})
    assert (
        MonitoringService._signal_matches_rule(signal, rule)
        is False
    )


def test_signal_matches_rule_severity_scalar_hit():
    """A scalar severity condition matches on equality."""
    signal = _make_signal(severity="medium")
    rule = _make_rule(conditions={"severity": "medium"})
    assert (
        MonitoringService._signal_matches_rule(signal, rule)
        is True
    )


def test_signal_matches_rule_severity_scalar_miss():
    """A scalar severity condition fails on inequality."""
    signal = _make_signal(severity="medium")
    rule = _make_rule(conditions={"severity": "critical"})
    assert (
        MonitoringService._signal_matches_rule(signal, rule)
        is False
    )


def test_signal_matches_rule_source_hit():
    """Matching source alone is enough when it is the only rule."""
    signal = _make_signal(source="shodan")
    rule = _make_rule(conditions={"source": "shodan"})
    assert (
        MonitoringService._signal_matches_rule(signal, rule)
        is True
    )


def test_signal_matches_rule_source_miss():
    """A non-matching source short-circuits to False."""
    signal = _make_signal(source="shodan")
    rule = _make_rule(conditions={"source": "haveibeenpwned"})
    assert (
        MonitoringService._signal_matches_rule(signal, rule)
        is False
    )


def test_signal_matches_rule_signal_type_hit():
    """Matching signal_type passes the final predicate."""
    signal = _make_signal(signal_type="cve")
    rule = _make_rule(conditions={"signal_type": "cve"})
    assert (
        MonitoringService._signal_matches_rule(signal, rule)
        is True
    )


def test_signal_matches_rule_signal_type_miss():
    """Non-matching signal_type fails the final predicate."""
    signal = _make_signal(signal_type="cve")
    rule = _make_rule(conditions={"signal_type": "breach"})
    assert (
        MonitoringService._signal_matches_rule(signal, rule)
        is False
    )


def test_signal_matches_rule_all_three_conditions_hit():
    """All three condition keys satisfied together."""
    signal = _make_signal(
        severity="critical",
        source="nvd",
        signal_type="cve",
    )
    rule = _make_rule(
        conditions={
            "severity": ["critical"],
            "source": "nvd",
            "signal_type": "cve",
        }
    )
    assert (
        MonitoringService._signal_matches_rule(signal, rule)
        is True
    )


@pytest.mark.parametrize(
    "overrides",
    [
        {"severity": "low"},
        {"source": "other"},
        {"signal_type": "breach"},
    ],
    ids=["severity", "source", "signal_type"],
)
def test_signal_matches_rule_any_single_mismatch_fails(overrides):
    """Any one mismatched key fails the whole rule."""
    base = dict(
        severity="critical", source="nvd", signal_type="cve"
    )
    base.update(overrides)
    signal = _make_signal(**base)
    rule = _make_rule(
        conditions={
            "severity": ["critical"],
            "source": "nvd",
            "signal_type": "cve",
        }
    )
    assert (
        MonitoringService._signal_matches_rule(signal, rule)
        is False
    )


def test_signal_matches_rule_ignores_unknown_condition_keys():
    """Unknown condition keys are not evaluated."""
    signal = _make_signal()
    rule = _make_rule(
        conditions={"unsupported_key": "whatever"}
    )
    assert (
        MonitoringService._signal_matches_rule(signal, rule)
        is True
    )


# ── _severity_to_priority ──────────────────────────────────


@pytest.mark.parametrize(
    ("severity", "expected"),
    [
        ("critical", "p0"),
        ("high", "p1"),
        ("medium", "p2"),
        ("low", "p3"),
        ("info", "p4"),
    ],
)
def test_severity_to_priority_known(severity, expected):
    """Known severities map to their documented priority."""
    assert (
        MonitoringService._severity_to_priority(severity)
        == expected
    )


@pytest.mark.parametrize(
    "severity", ["", "CRITICAL", "unknown", "p0"]
)
def test_severity_to_priority_unknown_defaults_to_p3(severity):
    """Unrecognised severities fall back to p3."""
    assert (
        MonitoringService._severity_to_priority(severity)
        == "p3"
    )


# ── _apply_alert_filters ───────────────────────────────────


def _where_sql(query) -> str:
    """Render the WHERE clause of a Select as literal SQL."""
    return str(
        query.whereclause.compile(
            compile_kwargs={"literal_binds": True}
        )
    )


def test_apply_alert_filters_no_filters_leaves_query_alone():
    """With no filters set the query is returned unchanged."""
    from sqlalchemy import select

    base = select(Alert).where(Alert.tenant_id == TENANT_ID)
    out = MonitoringService._apply_alert_filters(
        base, AlertFilterParams()
    )
    assert out is base


def test_apply_alert_filters_adds_each_clause():
    """Each populated filter adds its own WHERE clause."""
    from sqlalchemy import select

    base = select(Alert).where(Alert.tenant_id == TENANT_ID)
    filters = AlertFilterParams(
        priority=AlertPriority.p1,
        status=AlertStatus.acknowledged,
        vendor_id=VENDOR_ID,
    )
    out = MonitoringService._apply_alert_filters(base, filters)
    sql = _where_sql(out)

    assert out is not base
    assert "alerts.priority = 'p1'" in sql
    assert "alerts.status = 'acknowledged'" in sql
    assert "alerts.vendor_id" in sql


def test_apply_alert_filters_partial():
    """Only the supplied filter is applied."""
    from sqlalchemy import select

    base = select(Alert).where(Alert.tenant_id == TENANT_ID)
    out = MonitoringService._apply_alert_filters(
        base, AlertFilterParams(status=AlertStatus.resolved)
    )
    sql = _where_sql(out)

    assert "alerts.status = 'resolved'" in sql
    assert "alerts.priority" not in sql


# ── list_alerts ────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_alerts_returns_paginated_items(
    service, mock_session
):
    """list_alerts maps rows and echoes pagination inputs."""
    alert = _make_alert()
    mock_session.execute = AsyncMock(
        side_effect=[
            _count_result(37),
            _mock_execute_result([alert]),
        ]
    )

    result = await service.list_alerts(
        TENANT_ID, AlertFilterParams(page=2, page_size=10)
    )

    assert result.total == 37
    assert result.page == 2
    assert result.page_size == 10
    assert len(result.items) == 1
    assert result.items[0].id == ALERT_ID
    assert result.items[0].priority == "p2"


@pytest.mark.asyncio
async def test_list_alerts_empty_count_coerced_to_zero(
    service, mock_session
):
    """A NULL count from the DB becomes 0, not None."""
    null_count = MagicMock()
    null_count.scalar.return_value = None
    mock_session.execute = AsyncMock(
        side_effect=[null_count, _mock_execute_result([])]
    )

    result = await service.list_alerts(
        TENANT_ID, AlertFilterParams()
    )

    assert result.total == 0
    assert result.items == []


@pytest.mark.asyncio
async def test_list_alerts_sort_order_desc_default(
    service, mock_session
):
    """Default sort is created_at DESC."""
    mock_session.execute = AsyncMock(
        side_effect=[_count_result(0), _mock_execute_result([])]
    )

    await service.list_alerts(TENANT_ID, AlertFilterParams())

    listing_query = mock_session.execute.await_args_list[1].args[0]
    assert "ORDER BY alerts.created_at DESC" in str(
        listing_query
    )


@pytest.mark.asyncio
async def test_list_alerts_sort_order_asc_on_custom_column(
    service, mock_session
):
    """sort_by/sort_order drive the ORDER BY clause."""
    mock_session.execute = AsyncMock(
        side_effect=[_count_result(0), _mock_execute_result([])]
    )

    await service.list_alerts(
        TENANT_ID,
        AlertFilterParams(
            sort_by="priority", sort_order=SortOrder.asc
        ),
    )

    listing_query = mock_session.execute.await_args_list[1].args[0]
    assert "ORDER BY alerts.priority ASC" in str(listing_query)


def test_alert_filter_params_rejects_unknown_sort_column():
    """sort_by is validated against an allow-list."""
    with pytest.raises(ValueError, match="sort_by must be one of"):
        AlertFilterParams(sort_by="password")


# ── get_alert ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_alert_found(service, mock_session):
    """get_alert maps the ORM row into a response."""
    alert = _make_alert(status="investigating")
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([alert])
    )

    result = await service.get_alert(TENANT_ID, ALERT_ID)

    assert result is not None
    assert result.id == ALERT_ID
    assert result.status == "investigating"
    assert result.signal_ids == [SIGNAL_ID]


@pytest.mark.asyncio
async def test_get_alert_missing_returns_none(
    service, mock_session
):
    """get_alert returns None when nothing matches."""
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([])
    )

    assert await service.get_alert(TENANT_ID, ALERT_ID) is None


# ── acknowledge / resolve / suppress ───────────────────────


@pytest.mark.asyncio
async def test_acknowledge_alert_sets_actor_and_timestamp(
    service, mock_session
):
    """acknowledge_alert stamps status, actor, and time."""
    alert = _make_alert()
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([alert])
    )

    result = await service.acknowledge_alert(
        TENANT_ID, ALERT_ID, USER_ID
    )

    assert alert.status == "acknowledged"
    assert alert.acknowledged_by == USER_ID
    assert isinstance(alert.acknowledged_at, datetime)
    assert result.status == "acknowledged"
    assert result.acknowledged_by == USER_ID
    mock_session.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_acknowledge_alert_missing_returns_none(
    service, mock_session
):
    """acknowledge_alert on an unknown alert is a no-op."""
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([])
    )

    result = await service.acknowledge_alert(
        TENANT_ID, ALERT_ID, USER_ID
    )

    assert result is None
    mock_session.flush.assert_not_awaited()


@pytest.mark.asyncio
async def test_resolve_alert_records_notes(
    service, mock_session
):
    """resolve_alert stores resolver, timestamp, and notes."""
    alert = _make_alert()
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([alert])
    )

    result = await service.resolve_alert(
        TENANT_ID, ALERT_ID, USER_ID, "Patched upstream"
    )

    assert alert.status == "resolved"
    assert alert.resolved_by == USER_ID
    assert isinstance(alert.resolved_at, datetime)
    assert result.resolution_notes == "Patched upstream"
    mock_session.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_resolve_alert_accepts_null_notes(
    service, mock_session
):
    """resolve_alert tolerates omitted notes."""
    alert = _make_alert()
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([alert])
    )

    result = await service.resolve_alert(
        TENANT_ID, ALERT_ID, USER_ID, None
    )

    assert result.resolution_notes is None
    assert result.status == "resolved"


@pytest.mark.asyncio
async def test_resolve_alert_missing_returns_none(
    service, mock_session
):
    """resolve_alert on an unknown alert is a no-op."""
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([])
    )

    result = await service.resolve_alert(
        TENANT_ID, ALERT_ID, USER_ID, "n/a"
    )

    assert result is None
    mock_session.flush.assert_not_awaited()


@pytest.mark.asyncio
async def test_suppress_alert(service, mock_session):
    """suppress_alert only changes status."""
    alert = _make_alert()
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([alert])
    )

    result = await service.suppress_alert(TENANT_ID, ALERT_ID)

    assert alert.status == "suppressed"
    assert alert.resolved_by is None
    assert alert.acknowledged_at is None
    assert result.status == "suppressed"
    mock_session.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_suppress_alert_missing_returns_none(
    service, mock_session
):
    """suppress_alert on an unknown alert is a no-op."""
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([])
    )

    assert (
        await service.suppress_alert(TENANT_ID, ALERT_ID)
        is None
    )
    mock_session.flush.assert_not_awaited()


# ── vendor timeline ────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_vendor_timeline_maps_events(
    service, mock_session
):
    """Timeline events are mapped and counted."""
    events = [
        _make_timeline_event(),
        _make_timeline_event(
            id=uuid.uuid4(),
            event_type="alert_raised",
            title="Alert raised",
            event_metadata=None,
            actor_id=None,
        ),
    ]
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result(events)
    )

    result = await service.get_vendor_timeline(
        TENANT_ID, VENDOR_ID
    )

    assert result.vendor_id == VENDOR_ID
    assert result.total == 2
    assert result.events[0].event_type == "assessment_completed"
    assert result.events[0].metadata == {"assessment_id": "abc"}
    assert result.events[1].metadata is None
    assert result.events[1].actor_id is None


@pytest.mark.asyncio
async def test_get_vendor_timeline_empty(
    service, mock_session
):
    """A vendor with no events yields an empty timeline."""
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([])
    )

    result = await service.get_vendor_timeline(
        TENANT_ID, VENDOR_ID
    )

    assert result.total == 0
    assert result.events == []


# ── alert rules ────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_alert_rules(service, mock_session):
    """list_alert_rules maps every rule row."""
    rules = [
        _make_rule(),
        _make_rule(
            id=uuid.uuid4(),
            name="Inactive rule",
            is_active=False,
            conditions={"source": "nvd"},
        ),
    ]
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result(rules)
    )

    result = await service.list_alert_rules(TENANT_ID)

    assert len(result) == 2
    assert result[0].name == "Critical breaches"
    assert result[0].is_active is True
    assert result[1].is_active is False
    assert result[1].conditions == {"source": "nvd"}


@pytest.mark.asyncio
async def test_list_alert_rules_empty(service, mock_session):
    """No rules yields an empty list, not None."""
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([])
    )

    assert await service.list_alert_rules(TENANT_ID) == []


@pytest.mark.asyncio
async def test_create_alert_rule(service, mock_session):
    """create_alert_rule persists and maps the new rule."""
    created = _make_rule(
        name="CVE watch",
        description="Track NVD CVEs",
        conditions={"signal_type": "cve"},
        actions={"notify": ["ops@example.com"]},
        is_active=False,
    )
    data = AlertRuleCreate(
        name="CVE watch",
        description="Track NVD CVEs",
        conditions={"signal_type": "cve"},
        actions={"notify": ["ops@example.com"]},
        is_active=False,
    )

    with patch(
        "app.modules.monitoring.service.AlertRule",
        return_value=created,
    ) as rule_cls:
        result = await service.create_alert_rule(
            TENANT_ID, data
        )

    rule_cls.assert_called_once_with(
        tenant_id=TENANT_ID,
        name="CVE watch",
        description="Track NVD CVEs",
        conditions={"signal_type": "cve"},
        actions={"notify": ["ops@example.com"]},
        is_active=False,
    )
    mock_session.add.assert_called_once_with(created)
    mock_session.flush.assert_awaited_once()
    assert result.name == "CVE watch"
    assert result.is_active is False


@pytest.mark.asyncio
async def test_update_alert_rule_applies_only_set_fields(
    service, mock_session
):
    """Unset fields are left untouched by the update."""
    rule = _make_rule()
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([rule])
    )

    result = await service.update_alert_rule(
        TENANT_ID,
        RULE_ID,
        AlertRuleUpdate(is_active=False),
    )

    assert rule.is_active is False
    assert rule.name == "Critical breaches"
    assert result.is_active is False
    mock_session.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_alert_rule_replaces_conditions(
    service, mock_session
):
    """Conditions can be swapped wholesale."""
    rule = _make_rule()
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([rule])
    )

    result = await service.update_alert_rule(
        TENANT_ID,
        RULE_ID,
        AlertRuleUpdate(
            name="Renamed",
            conditions={"source": "shodan"},
        ),
    )

    assert rule.name == "Renamed"
    assert rule.conditions == {"source": "shodan"}
    assert result.conditions == {"source": "shodan"}


@pytest.mark.asyncio
async def test_update_alert_rule_missing_returns_none(
    service, mock_session
):
    """Updating an unknown rule returns None without a flush."""
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([])
    )

    result = await service.update_alert_rule(
        TENANT_ID, RULE_ID, AlertRuleUpdate(name="Nope")
    )

    assert result is None
    mock_session.flush.assert_not_awaited()


# ── _evaluate_rules ────────────────────────────────────────


@pytest.mark.asyncio
async def test_evaluate_rules_creates_alert_per_match(
    service, mock_session
):
    """One alert is created for each matching rule."""
    signal = _make_signal(severity="critical", source="nvd")
    rules = [
        _make_rule(
            name="Crit",
            conditions={"severity": ["critical"]},
        ),
        _make_rule(
            id=uuid.uuid4(),
            name="NVD only",
            conditions={"source": "nvd"},
        ),
        _make_rule(
            id=uuid.uuid4(),
            name="Lows",
            conditions={"severity": ["low"]},
        ),
    ]
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result(rules)
    )

    created = await service._evaluate_rules(TENANT_ID, signal)

    assert created == 2
    assert mock_session.add.call_count == 2
    mock_session.flush.assert_awaited_once()

    alerts = [c.args[0] for c in mock_session.add.call_args_list]
    assert {a.title for a in alerts} == {
        "[Crit] Credential dump",
        "[NVD only] Credential dump",
    }
    assert all(a.priority == "p0" for a in alerts)
    assert all(a.status == "new" for a in alerts)
    assert all(a.vendor_id == VENDOR_ID for a in alerts)
    assert all(a.signal_ids == [SIGNAL_ID] for a in alerts)
    assert alerts[0].impact_assessment == {
        "source": "nvd",
        "severity": "critical",
        "rule": "Crit",
    }


@pytest.mark.asyncio
async def test_evaluate_rules_no_match_creates_nothing(
    service, mock_session
):
    """A signal matching no rule creates no alerts and no flush."""
    signal = _make_signal(severity="info")
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result(
            [_make_rule(conditions={"severity": ["critical"]})]
        )
    )

    created = await service._evaluate_rules(TENANT_ID, signal)

    assert created == 0
    mock_session.add.assert_not_called()
    mock_session.flush.assert_not_awaited()


@pytest.mark.asyncio
async def test_evaluate_rules_no_rules(service, mock_session):
    """A tenant with no active rules produces no alerts."""
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([])
    )

    created = await service._evaluate_rules(
        TENANT_ID, _make_signal()
    )

    assert created == 0
    mock_session.flush.assert_not_awaited()


# ── ingest_signal ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_ingest_signal_persists_and_evaluates(
    service, mock_session
):
    """ingest_signal stores the signal then evaluates rules."""
    signal = _make_signal(processed=False)
    data = SignalIngestRequest(
        vendor_id=VENDOR_ID,
        source="haveibeenpwned",
        signal_type="breach",
        severity=SignalSeverity.critical,
        title="Credential dump",
        description="500k records exposed",
        raw_data={"records": 500000},
        dedup_key="hibp:acme:2026",
    )

    with patch(
        "app.modules.monitoring.service.MonitoringSignal",
        return_value=signal,
    ) as signal_cls, patch.object(
        service,
        "_evaluate_rules",
        new_callable=AsyncMock,
        return_value=3,
    ) as evaluate:
        result = await service.ingest_signal(TENANT_ID, data)

    assert signal_cls.call_args.kwargs["severity"] == "critical"
    assert signal_cls.call_args.kwargs["processed"] is False
    mock_session.add.assert_called_once_with(signal)
    evaluate.assert_awaited_once_with(TENANT_ID, signal)
    assert signal.processed is True
    assert mock_session.flush.await_count == 2
    assert result.signal_id == SIGNAL_ID
    assert result.alerts_created == 3


@pytest.mark.asyncio
async def test_ingest_signal_defaults_severity_to_info(
    service, mock_session
):
    """Severity defaults to info when omitted."""
    signal = _make_signal(severity="info")
    data = SignalIngestRequest(
        vendor_id=VENDOR_ID,
        source="rss",
        signal_type="news",
        title="Minor mention",
    )

    with patch(
        "app.modules.monitoring.service.MonitoringSignal",
        return_value=signal,
    ) as signal_cls, patch.object(
        service,
        "_evaluate_rules",
        new_callable=AsyncMock,
        return_value=0,
    ):
        result = await service.ingest_signal(TENANT_ID, data)

    assert signal_cls.call_args.kwargs["severity"] == "info"
    assert signal_cls.call_args.kwargs["raw_data"] is None
    assert signal_cls.call_args.kwargs["dedup_key"] is None
    assert result.alerts_created == 0


@pytest.mark.asyncio
async def test_ingest_signal_end_to_end_creates_alert(
    service, mock_session
):
    """Ingesting a matching signal creates a real Alert row."""
    signal = _make_signal(severity="high", source="nvd")
    rule = _make_rule(
        name="High from NVD",
        conditions={"severity": ["high"], "source": "nvd"},
    )
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([rule])
    )
    data = SignalIngestRequest(
        vendor_id=VENDOR_ID,
        source="nvd",
        signal_type="cve",
        severity=SignalSeverity.high,
        title="Credential dump",
    )

    with patch(
        "app.modules.monitoring.service.MonitoringSignal",
        return_value=signal,
    ):
        result = await service.ingest_signal(TENANT_ID, data)

    assert result.alerts_created == 1
    created_alert = mock_session.add.call_args_list[-1].args[0]
    assert created_alert.priority == "p1"
    assert created_alert.title == "[High from NVD] Credential dump"


# ── response mappers ───────────────────────────────────────


def test_to_alert_response_maps_every_field():
    """_to_alert_response copies the full alert record."""
    now = datetime.now(UTC)
    alert = _make_alert(
        status="resolved",
        acknowledged_by=USER_ID,
        resolved_by=USER_ID,
        acknowledged_at=now,
        resolved_at=now,
        resolution_notes="done",
    )

    out = MonitoringService._to_alert_response(alert)

    assert out.id == ALERT_ID
    assert out.tenant_id == TENANT_ID
    assert out.vendor_id == VENDOR_ID
    assert out.status == "resolved"
    assert out.acknowledged_by == USER_ID
    assert out.resolved_by == USER_ID
    assert out.acknowledged_at == now
    assert out.resolved_at == now
    assert out.resolution_notes == "done"
    assert out.impact_assessment == {
        "source": "news",
        "severity": "high",
    }


def test_to_alert_response_nullable_fields():
    """Optional alert fields survive as None."""
    alert = _make_alert(
        description=None,
        signal_ids=None,
        impact_assessment=None,
    )

    out = MonitoringService._to_alert_response(alert)

    assert out.description is None
    assert out.signal_ids is None
    assert out.impact_assessment is None


def test_to_rule_response_maps_every_field():
    """_to_rule_response copies the full rule record."""
    rule = _make_rule()

    out = MonitoringService._to_rule_response(rule)

    assert out.id == RULE_ID
    assert out.tenant_id == TENANT_ID
    assert out.name == "Critical breaches"
    assert out.conditions == {"severity": ["critical", "high"]}
    assert out.actions == {"notify": ["security@example.com"]}
    assert out.is_active is True


def test_to_timeline_event_renames_event_metadata():
    """event_metadata is exposed as `metadata`."""
    event = _make_timeline_event(
        event_metadata={"k": "v"}, description=None
    )

    out = MonitoringService._to_timeline_event(event)

    assert out.id == EVENT_ID
    assert out.vendor_id == VENDOR_ID
    assert out.event_type == "assessment_completed"
    assert out.metadata == {"k": "v"}
    assert out.description is None
    assert out.actor_id == USER_ID
