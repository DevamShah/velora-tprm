"""
Unit tests for ReportsService.

Mocks the database session to exercise dashboard aggregation,
report generation, templates and dashboard-config CRUD without
touching infrastructure.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.modules.monitoring.models import Alert
from app.modules.reports.models import (
    DashboardConfig,
    GeneratedReport,
    ReportTemplate,
)
from app.modules.reports.schemas import DashboardConfigUpdate
from app.modules.reports.service import ReportsService
from app.modules.vendors.models import Vendor

TENANT_ID = uuid.UUID("00000000-0000-4000-a000-000000000001")
USER_ID = uuid.UUID("00000000-0000-4000-a000-000000000010")
REPORT_ID = uuid.UUID("00000000-0000-4000-a000-000000000300")
TEMPLATE_ID = uuid.UUID("00000000-0000-4000-a000-000000000301")
CONFIG_ID = uuid.UUID("00000000-0000-4000-a000-000000000302")
ALERT_ID = uuid.UUID("00000000-0000-4000-a000-000000000303")
VENDOR_ID = uuid.UUID("00000000-0000-4000-a000-000000000304")

NOW = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


def _make_report(**overrides) -> GeneratedReport:
    """Create a GeneratedReport ORM object with defaults."""
    defaults = dict(
        id=REPORT_ID,
        tenant_id=TENANT_ID,
        template_id=TEMPLATE_ID,
        title="Q1 Risk Review",
        format="pdf",
        status="completed",
        s3_key="reports/q1.pdf",
        generated_by=USER_ID,
        created_at=NOW,
        updated_at=NOW,
    )
    defaults.update(overrides)
    report = MagicMock(spec=GeneratedReport)
    for k, v in defaults.items():
        setattr(report, k, v)
    return report


def _make_template(**overrides) -> ReportTemplate:
    """Create a ReportTemplate ORM object with defaults."""
    defaults = dict(
        id=TEMPLATE_ID,
        tenant_id=TENANT_ID,
        name="Executive Summary",
        description="Board-level summary",
        template_type="executive",
        sections={"order": ["risk", "findings"]},
        is_system=True,
        created_at=NOW,
        updated_at=NOW,
    )
    defaults.update(overrides)
    template = MagicMock(spec=ReportTemplate)
    for k, v in defaults.items():
        setattr(template, k, v)
    return template


def _make_config(**overrides) -> DashboardConfig:
    """Create a DashboardConfig ORM object with defaults."""
    defaults = dict(
        id=CONFIG_ID,
        tenant_id=TENANT_ID,
        user_id=USER_ID,
        dashboard_type="executive",
        widget_layout={"cols": 3},
        created_at=NOW,
        updated_at=NOW,
    )
    defaults.update(overrides)
    config = MagicMock(spec=DashboardConfig)
    for k, v in defaults.items():
        setattr(config, k, v)
    return config


def _make_alert(**overrides) -> Alert:
    """Create an Alert ORM object with defaults."""
    defaults = dict(
        id=ALERT_ID,
        tenant_id=TENANT_ID,
        vendor_id=VENDOR_ID,
        title="Breach disclosed",
        priority="p1",
        status="new",
        created_at=NOW,
    )
    defaults.update(overrides)
    alert = MagicMock(spec=Alert)
    for k, v in defaults.items():
        setattr(alert, k, v)
    return alert


def _make_vendor(**overrides) -> Vendor:
    """Create a Vendor ORM object with defaults."""
    defaults = dict(
        id=VENDOR_ID,
        tenant_id=TENANT_ID,
        name="Acme Corp",
        tier="critical",
        inherent_risk_score=88.5,
        deleted_at=None,
        created_at=NOW,
        updated_at=NOW,
    )
    defaults.update(overrides)
    vendor = MagicMock(spec=Vendor)
    for k, v in defaults.items():
        setattr(vendor, k, v)
    return vendor


def _mock_execute_result(items=None, rows=None, scalar=None):
    """Mock execute result supporting scalars(), all() and scalar()."""
    items = items or []
    result = MagicMock()
    scalars = MagicMock()
    scalars.first.return_value = items[0] if items else None
    scalars.all.return_value = items
    result.scalars.return_value = scalars
    result.all.return_value = rows if rows is not None else []
    result.scalar.return_value = (
        scalar if scalar is not None else len(items)
    )
    return result


@pytest.fixture
def mock_session():
    """Async mock session with a synchronous add()."""
    session = AsyncMock()
    session.add = MagicMock()
    return session


@pytest.fixture
def service(mock_session):
    """ReportsService bound to the mocked session."""
    return ReportsService(mock_session)


def _stamp_on_add(session, **attrs):
    """Make session.add() populate DB-assigned attributes."""

    def _apply(obj):
        for key, value in attrs.items():
            setattr(obj, key, value)

    session.add.side_effect = _apply


# -- Executive dashboard --------------------------------------------


@pytest.mark.asyncio
async def test_get_executive_dashboard_aggregates_all_sources(
    service, mock_session
):
    """Dashboard should merge all seven queries into one payload."""
    alert = _make_alert()
    vendor = _make_vendor()

    mock_session.execute = AsyncMock(
        side_effect=[
            # vendor stats
            _mock_execute_result(
                rows=[("critical", 2), ("low", 3)]
            ),
            # assessment stats
            _mock_execute_result(
                rows=[("draft", 1), ("completed", 4)]
            ),
            # finding stats
            _mock_execute_result(
                rows=[("high", 5), ("info", 1)]
            ),
            # alert stats
            _mock_execute_result(rows=[("p0", 1), ("p3", 2)]),
            # avg risk score
            _mock_execute_result(scalar=61.239),
            # recent alerts
            _mock_execute_result(items=[alert]),
            # top risk vendors
            _mock_execute_result(items=[vendor]),
        ]
    )

    data = await service.get_executive_dashboard(TENANT_ID)

    assert data.total_vendors == 5
    assert data.vendors_by_tier.critical == 2
    assert data.vendors_by_tier.low == 3
    assert data.vendors_by_tier.high == 0

    assert data.total_assessments == 5
    assert data.assessments_by_status.completed == 4
    assert data.assessments_by_status.overdue == 0

    assert data.open_findings == 6
    assert data.findings_by_severity.high == 5
    assert data.findings_by_severity.critical == 0

    assert data.active_alerts == 3
    assert data.alerts_by_priority.p0 == 1
    assert data.alerts_by_priority.p3 == 2

    assert data.avg_risk_score == 61.24
    assert len(data.recent_alerts) == 1
    assert data.recent_alerts[0].title == "Breach disclosed"
    assert data.recent_alerts[0].priority == "p1"
    assert len(data.top_risk_vendors) == 1
    assert data.top_risk_vendors[0].name == "Acme Corp"
    assert data.top_risk_vendors[0].inherent_risk_score == 88.5
    assert data.top_risk_vendors[0].open_findings == 0
    assert mock_session.execute.await_count == 7


@pytest.mark.asyncio
async def test_get_executive_dashboard_empty_tenant(
    service, mock_session
):
    """Empty tenant should yield zeroed counters and no avg score."""
    mock_session.execute = AsyncMock(
        side_effect=[
            _mock_execute_result(rows=[]),
            _mock_execute_result(rows=[]),
            _mock_execute_result(rows=[]),
            _mock_execute_result(rows=[]),
            _mock_execute_result(scalar=None),
            _mock_execute_result(items=[]),
            _mock_execute_result(items=[]),
        ]
    )

    data = await service.get_executive_dashboard(TENANT_ID)

    assert data.total_vendors == 0
    assert data.total_assessments == 0
    assert data.open_findings == 0
    assert data.active_alerts == 0
    assert data.avg_risk_score is None
    assert data.recent_alerts == []
    assert data.top_risk_vendors == []


@pytest.mark.asyncio
async def test_get_avg_risk_score_rounds_to_two_places(
    service, mock_session
):
    """_get_avg_risk_score rounds the SQL average."""
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result(scalar=72.5551)
    )

    assert await service._get_avg_risk_score(TENANT_ID) == 72.56


@pytest.mark.asyncio
async def test_get_avg_risk_score_none_when_no_rows(
    service, mock_session
):
    """A NULL average maps to None rather than 0.0."""
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result(scalar=None)
    )

    assert await service._get_avg_risk_score(TENANT_ID) is None


@pytest.mark.asyncio
async def test_get_recent_alerts_maps_every_field(
    service, mock_session
):
    """Recent alerts are mapped into RecentAlert rows in order."""
    older = _make_alert(
        id=uuid.uuid4(),
        title="Older alert",
        priority="p4",
        created_at=NOW - timedelta(days=1),
    )
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result(
            items=[_make_alert(), older]
        )
    )

    alerts = await service._get_recent_alerts(TENANT_ID)

    assert [a.title for a in alerts] == [
        "Breach disclosed",
        "Older alert",
    ]
    assert alerts[1].priority == "p4"
    assert alerts[0].vendor_id == VENDOR_ID
    assert alerts[0].created_at == NOW


@pytest.mark.asyncio
async def test_get_top_risk_vendors_preserves_query_order(
    service, mock_session
):
    """Top risk vendors are returned in the order the query gave."""
    second = _make_vendor(
        id=uuid.uuid4(),
        name="Beta Ltd",
        tier="high",
        inherent_risk_score=70.0,
    )
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result(
            items=[_make_vendor(), second]
        )
    )

    vendors = await service._get_top_risk_vendors(TENANT_ID)

    assert [v.name for v in vendors] == ["Acme Corp", "Beta Ltd"]
    assert [v.tier for v in vendors] == ["critical", "high"]
    assert vendors[1].inherent_risk_score == 70.0


# -- Report generation ----------------------------------------------


@pytest.mark.asyncio
async def test_generate_report_persists_pending_record(
    service, mock_session
):
    """generate_report adds a pending record and maps the response."""
    _stamp_on_add(
        mock_session,
        id=REPORT_ID,
        created_at=NOW,
        updated_at=NOW,
        s3_key=None,
    )

    result = await service.generate_report(
        TENANT_ID,
        TEMPLATE_ID,
        "Annual Vendor Report",
        "pptx",
        USER_ID,
    )

    mock_session.add.assert_called_once()
    added = mock_session.add.call_args.args[0]
    assert isinstance(added, GeneratedReport)
    assert added.tenant_id == TENANT_ID
    assert added.template_id == TEMPLATE_ID
    assert added.title == "Annual Vendor Report"
    assert added.format == "pptx"
    assert added.status == "pending"
    assert added.generated_by == USER_ID
    mock_session.flush.assert_awaited_once()

    assert result.id == REPORT_ID
    assert result.title == "Annual Vendor Report"
    assert result.status == "pending"
    assert result.format == "pptx"
    assert result.s3_key is None


@pytest.mark.asyncio
async def test_generate_report_without_template(
    service, mock_session
):
    """A report may be generated with no template attached."""
    _stamp_on_add(
        mock_session,
        id=REPORT_ID,
        created_at=NOW,
        updated_at=NOW,
        s3_key=None,
    )

    result = await service.generate_report(
        TENANT_ID, None, "Ad-hoc", "csv", USER_ID
    )

    added = mock_session.add.call_args.args[0]
    assert added.template_id is None
    assert result.template_id is None
    assert result.format == "csv"


# -- Listing --------------------------------------------------------


@pytest.mark.asyncio
async def test_list_reports_paginates(service, mock_session):
    """list_reports returns items plus pagination metadata."""
    count_result = MagicMock()
    count_result.scalar.return_value = 42

    mock_session.execute = AsyncMock(
        side_effect=[
            count_result,
            _mock_execute_result(items=[_make_report()]),
        ]
    )

    page = await service.list_reports(
        TENANT_ID, page=3, page_size=5
    )

    assert page.total == 42
    assert page.page == 3
    assert page.page_size == 5
    assert len(page.items) == 1
    assert page.items[0].title == "Q1 Risk Review"
    assert page.items[0].s3_key == "reports/q1.pdf"


@pytest.mark.asyncio
async def test_list_reports_null_count_becomes_zero(
    service, mock_session
):
    """A NULL count from SQL degrades to a total of zero."""
    count_result = MagicMock()
    count_result.scalar.return_value = None

    mock_session.execute = AsyncMock(
        side_effect=[count_result, _mock_execute_result(items=[])]
    )

    page = await service.list_reports(TENANT_ID)

    assert page.total == 0
    assert page.items == []
    assert page.page == 1
    assert page.page_size == 20


@pytest.mark.asyncio
async def test_get_report_found(service, mock_session):
    """get_report maps a matching row to ReportResponse."""
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result(items=[_make_report()])
    )

    result = await service.get_report(TENANT_ID, REPORT_ID)

    assert result is not None
    assert result.id == REPORT_ID
    assert result.generated_by == USER_ID
    assert result.status == "completed"


@pytest.mark.asyncio
async def test_get_report_missing_returns_none(
    service, mock_session
):
    """get_report returns None when nothing matches."""
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result(items=[])
    )

    assert await service.get_report(TENANT_ID, REPORT_ID) is None


@pytest.mark.asyncio
async def test_list_templates_maps_all(service, mock_session):
    """list_templates maps every row to a response object."""
    custom = _make_template(
        id=uuid.uuid4(),
        name="Custom",
        description=None,
        template_type="detailed",
        sections=None,
        is_system=False,
    )
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result(
            items=[_make_template(), custom]
        )
    )

    templates = await service.list_templates(TENANT_ID)

    assert len(templates) == 2
    assert templates[0].name == "Executive Summary"
    assert templates[0].is_system is True
    assert templates[0].sections == {"order": ["risk", "findings"]}
    assert templates[1].description is None
    assert templates[1].sections is None
    assert templates[1].is_system is False


@pytest.mark.asyncio
async def test_list_templates_empty(service, mock_session):
    """No templates yields an empty list, not None."""
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result(items=[])
    )

    assert await service.list_templates(TENANT_ID) == []


# -- Dashboard config -----------------------------------------------


@pytest.mark.asyncio
async def test_get_dashboard_config_found(service, mock_session):
    """get_dashboard_config maps an existing config."""
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result(items=[_make_config()])
    )

    config = await service.get_dashboard_config(
        TENANT_ID, USER_ID
    )

    assert config is not None
    assert config.user_id == USER_ID
    assert config.dashboard_type == "executive"
    assert config.widget_layout == {"cols": 3}


@pytest.mark.asyncio
async def test_get_dashboard_config_missing(service, mock_session):
    """get_dashboard_config returns None when absent."""
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result(items=[])
    )

    assert (
        await service.get_dashboard_config(TENANT_ID, USER_ID)
        is None
    )


@pytest.mark.asyncio
async def test_update_dashboard_config_creates_when_absent(
    service, mock_session
):
    """Missing config is created with the supplied values."""
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result(items=[])
    )
    _stamp_on_add(
        mock_session,
        id=CONFIG_ID,
        created_at=NOW,
        updated_at=NOW,
    )

    data = DashboardConfigUpdate(
        dashboard_type="analyst",
        widget_layout={"cols": 2},
    )
    result = await service.update_dashboard_config(
        TENANT_ID, USER_ID, data
    )

    mock_session.add.assert_called_once()
    added = mock_session.add.call_args.args[0]
    assert isinstance(added, DashboardConfig)
    assert added.dashboard_type == "analyst"
    assert added.widget_layout == {"cols": 2}
    assert added.user_id == USER_ID
    assert result.dashboard_type == "analyst"
    mock_session.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_dashboard_config_defaults_type_to_executive(
    service, mock_session
):
    """Creating without a dashboard_type falls back to executive."""
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result(items=[])
    )
    _stamp_on_add(
        mock_session,
        id=CONFIG_ID,
        created_at=NOW,
        updated_at=NOW,
    )

    result = await service.update_dashboard_config(
        TENANT_ID,
        USER_ID,
        DashboardConfigUpdate(widget_layout={"cols": 1}),
    )

    assert result.dashboard_type == "executive"
    assert result.widget_layout == {"cols": 1}


@pytest.mark.asyncio
async def test_update_dashboard_config_patches_existing(
    service, mock_session
):
    """Existing config is patched only on the fields provided."""
    config = _make_config()
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result(items=[config])
    )

    data = DashboardConfigUpdate(widget_layout={"cols": 4})
    result = await service.update_dashboard_config(
        TENANT_ID, USER_ID, data
    )

    mock_session.add.assert_not_called()
    assert config.widget_layout == {"cols": 4}
    # dashboard_type was not in the payload, so left untouched
    assert config.dashboard_type == "executive"
    assert result.widget_layout == {"cols": 4}
    mock_session.flush.assert_awaited_once()


# -- Mappers --------------------------------------------------------


def test_to_report_response_maps_nullable_fields():
    """_to_report_response tolerates null template/s3/generator."""
    report = _make_report(
        template_id=None, s3_key=None, generated_by=None
    )

    response = ReportsService._to_report_response(report)

    assert response.template_id is None
    assert response.s3_key is None
    assert response.generated_by is None
    assert response.id == REPORT_ID
    assert response.created_at == NOW


def test_to_template_response_maps_fields():
    """_to_template_response copies template fields verbatim."""
    template = _make_template()

    response = ReportsService._to_template_response(template)

    assert response.name == "Executive Summary"
    assert response.template_type == "executive"
    assert response.sections == {"order": ["risk", "findings"]}
    assert response.is_system is True


def test_to_config_response_allows_null_user_and_layout():
    """_to_config_response accepts a null user and layout."""
    config = _make_config(user_id=None, widget_layout=None)

    response = ReportsService._to_config_response(config)

    assert response.user_id is None
    assert response.widget_layout is None
    assert response.dashboard_type == "executive"
