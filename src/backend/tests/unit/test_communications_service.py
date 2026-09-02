"""
Unit tests for CommunicationsService.

Mocks the database session to exercise notification listing and
read-state transitions, preferences, email templates and
communication logs without touching infrastructure.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.modules.communications.models import (
    CommunicationLog,
    EmailTemplate,
    Notification,
    NotificationPreference,
)
from app.modules.communications.schemas import (
    EmailTemplateCreate,
    EmailTemplateUpdate,
    PreferenceUpdate,
)
from app.modules.communications.service import (
    CommunicationsService,
)

TENANT_ID = uuid.UUID("00000000-0000-4000-a000-000000000001")
USER_ID = uuid.UUID("00000000-0000-4000-a000-000000000010")
NOTIF_ID = uuid.UUID("00000000-0000-4000-a000-000000000400")
PREF_ID = uuid.UUID("00000000-0000-4000-a000-000000000401")
TEMPLATE_ID = uuid.UUID("00000000-0000-4000-a000-000000000402")
LOG_ID = uuid.UUID("00000000-0000-4000-a000-000000000403")
ENTITY_ID = uuid.UUID("00000000-0000-4000-a000-000000000404")

NOW = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


def _make_notification(**overrides) -> Notification:
    """Create a Notification ORM object with defaults."""
    defaults = dict(
        id=NOTIF_ID,
        tenant_id=TENANT_ID,
        user_id=USER_ID,
        title="Assessment due",
        message="Acme Corp assessment is due in 3 days.",
        channel="in_app",
        read=False,
        read_at=None,
        entity_type="assessment",
        entity_id=ENTITY_ID,
        created_at=NOW,
        updated_at=NOW,
    )
    defaults.update(overrides)
    notif = MagicMock(spec=Notification)
    for k, v in defaults.items():
        setattr(notif, k, v)
    return notif


def _make_preference(**overrides) -> NotificationPreference:
    """Create a NotificationPreference ORM object with defaults."""
    defaults = dict(
        id=PREF_ID,
        tenant_id=TENANT_ID,
        user_id=USER_ID,
        category="assessments",
        channel_config={"email": True, "slack": False},
        quiet_hours_start="22:00",
        quiet_hours_end="07:00",
        created_at=NOW,
        updated_at=NOW,
    )
    defaults.update(overrides)
    pref = MagicMock(spec=NotificationPreference)
    for k, v in defaults.items():
        setattr(pref, k, v)
    return pref


def _make_email_template(**overrides) -> EmailTemplate:
    """Create an EmailTemplate ORM object with defaults."""
    defaults = dict(
        id=TEMPLATE_ID,
        tenant_id=TENANT_ID,
        name="Assessment reminder",
        subject_template="Reminder: {{assessment}}",
        body_template="Hello {{name}}, please complete it.",
        variables={"name": "string"},
        is_system=False,
        created_at=NOW,
        updated_at=NOW,
    )
    defaults.update(overrides)
    template = MagicMock(spec=EmailTemplate)
    for k, v in defaults.items():
        setattr(template, k, v)
    return template


def _make_comm_log(**overrides) -> CommunicationLog:
    """Create a CommunicationLog ORM object with defaults."""
    defaults = dict(
        id=LOG_ID,
        tenant_id=TENANT_ID,
        channel="email",
        recipient="ciso@acme.com",
        subject="Reminder: Q1 assessment",
        status="sent",
        sent_at=NOW,
        error_message=None,
        created_at=NOW,
        updated_at=NOW,
    )
    defaults.update(overrides)
    log = MagicMock(spec=CommunicationLog)
    for k, v in defaults.items():
        setattr(log, k, v)
    return log


def _mock_execute_result(items=None, scalar=None):
    """Mock execute result supporting scalars() and scalar()."""
    items = items or []
    result = MagicMock()
    scalars = MagicMock()
    scalars.first.return_value = items[0] if items else None
    scalars.all.return_value = items
    result.scalars.return_value = scalars
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
    """CommunicationsService bound to the mocked session."""
    return CommunicationsService(mock_session)


def _stamp_on_add(session, **attrs):
    """Make session.add() populate DB-assigned attributes."""

    def _apply(obj):
        for key, value in attrs.items():
            setattr(obj, key, value)

    session.add.side_effect = _apply


# -- List notifications ---------------------------------------------


@pytest.mark.asyncio
async def test_list_notifications_paginates(service, mock_session):
    """list_notifications returns mapped items plus metadata."""
    count_result = MagicMock()
    count_result.scalar.return_value = 7

    mock_session.execute = AsyncMock(
        side_effect=[
            count_result,
            _mock_execute_result(
                items=[
                    _make_notification(),
                    _make_notification(
                        id=uuid.uuid4(),
                        title="Finding opened",
                        read=True,
                        read_at=NOW,
                    ),
                ]
            ),
        ]
    )

    page = await service.list_notifications(
        TENANT_ID, USER_ID, page=2, page_size=2
    )

    assert page.total == 7
    assert page.page == 2
    assert page.page_size == 2
    assert [n.title for n in page.items] == [
        "Assessment due",
        "Finding opened",
    ]
    assert page.items[0].read is False
    assert page.items[0].read_at is None
    assert page.items[1].read is True
    assert page.items[1].read_at == NOW


@pytest.mark.asyncio
async def test_list_notifications_null_count_becomes_zero(
    service, mock_session
):
    """A NULL count degrades to a total of zero."""
    count_result = MagicMock()
    count_result.scalar.return_value = None

    mock_session.execute = AsyncMock(
        side_effect=[count_result, _mock_execute_result(items=[])]
    )

    page = await service.list_notifications(TENANT_ID, USER_ID)

    assert page.total == 0
    assert page.items == []
    assert page.page == 1
    assert page.page_size == 20


# -- Mark read ------------------------------------------------------


@pytest.mark.asyncio
async def test_mark_read_sets_flag_and_timestamp(
    service, mock_session
):
    """mark_read flips read and stamps read_at."""
    notif = _make_notification()
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result(items=[notif])
    )

    result = await service.mark_read(TENANT_ID, NOTIF_ID)

    assert notif.read is True
    assert notif.read_at is not None
    assert notif.read_at.tzinfo is not None
    mock_session.flush.assert_awaited_once()
    assert result is not None
    assert result.id == NOTIF_ID
    assert result.read is True


@pytest.mark.asyncio
async def test_mark_read_missing_returns_none(
    service, mock_session
):
    """mark_read returns None and does not flush when absent."""
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result(items=[])
    )

    result = await service.mark_read(TENANT_ID, NOTIF_ID)

    assert result is None
    mock_session.flush.assert_not_awaited()


@pytest.mark.asyncio
async def test_mark_all_read_updates_every_unread(
    service, mock_session
):
    """mark_all_read stamps every unread row with one timestamp."""
    unread = [
        _make_notification(id=uuid.uuid4()),
        _make_notification(id=uuid.uuid4()),
        _make_notification(id=uuid.uuid4()),
    ]
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result(items=unread)
    )

    count = await service.mark_all_read(TENANT_ID, USER_ID)

    assert count == 3
    assert all(n.read is True for n in unread)
    stamps = {n.read_at for n in unread}
    assert len(stamps) == 1
    assert next(iter(stamps)) is not None
    mock_session.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_mark_all_read_none_unread(service, mock_session):
    """mark_all_read returns 0 when there is nothing unread."""
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result(items=[])
    )

    assert await service.mark_all_read(TENANT_ID, USER_ID) == 0
    mock_session.flush.assert_awaited_once()


# -- Preferences ----------------------------------------------------


@pytest.mark.asyncio
async def test_get_preferences_maps_rows(service, mock_session):
    """get_preferences maps every preference row."""
    other = _make_preference(
        id=uuid.uuid4(),
        category="findings",
        channel_config=None,
        quiet_hours_start=None,
        quiet_hours_end=None,
    )
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result(
            items=[_make_preference(), other]
        )
    )

    prefs = await service.get_preferences(TENANT_ID, USER_ID)

    assert [p.category for p in prefs] == [
        "assessments",
        "findings",
    ]
    assert prefs[0].channel_config == {
        "email": True,
        "slack": False,
    }
    assert prefs[0].quiet_hours_start == "22:00"
    assert prefs[1].channel_config is None
    assert prefs[1].quiet_hours_end is None


@pytest.mark.asyncio
async def test_get_preferences_empty(service, mock_session):
    """No preferences yields an empty list."""
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result(items=[])
    )

    assert await service.get_preferences(TENANT_ID, USER_ID) == []


@pytest.mark.asyncio
async def test_update_preferences_creates_when_absent(
    service, mock_session
):
    """A missing preference is created from the payload."""
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result(items=[])
    )
    _stamp_on_add(
        mock_session, id=PREF_ID, created_at=NOW, updated_at=NOW
    )

    data = PreferenceUpdate(
        category="alerts",
        channel_config={"slack": True},
        quiet_hours_start="23:00",
        quiet_hours_end="06:00",
    )
    result = await service.update_preferences(
        TENANT_ID, USER_ID, data
    )

    mock_session.add.assert_called_once()
    added = mock_session.add.call_args.args[0]
    assert isinstance(added, NotificationPreference)
    assert added.tenant_id == TENANT_ID
    assert added.user_id == USER_ID
    assert added.category == "alerts"
    assert added.channel_config == {"slack": True}
    assert added.quiet_hours_start == "23:00"
    assert added.quiet_hours_end == "06:00"
    assert result.category == "alerts"
    mock_session.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_preferences_patches_existing(
    service, mock_session
):
    """An existing preference is patched on set fields only."""
    pref = _make_preference()
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result(items=[pref])
    )

    data = PreferenceUpdate(
        category="assessments",
        channel_config={"email": False},
    )
    result = await service.update_preferences(
        TENANT_ID, USER_ID, data
    )

    mock_session.add.assert_not_called()
    assert pref.channel_config == {"email": False}
    # quiet hours were unset in the payload, so left as-is
    assert pref.quiet_hours_start == "22:00"
    assert pref.quiet_hours_end == "07:00"
    assert result.channel_config == {"email": False}
    mock_session.flush.assert_awaited_once()


# -- Email templates ------------------------------------------------


@pytest.mark.asyncio
async def test_list_email_templates_maps_rows(
    service, mock_session
):
    """list_email_templates maps each row to a response."""
    system = _make_email_template(
        id=uuid.uuid4(),
        name="System welcome",
        variables=None,
        is_system=True,
    )
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result(
            items=[_make_email_template(), system]
        )
    )

    templates = await service.list_email_templates(TENANT_ID)

    assert [t.name for t in templates] == [
        "Assessment reminder",
        "System welcome",
    ]
    assert templates[0].subject_template == "Reminder: {{assessment}}"
    assert templates[0].variables == {"name": "string"}
    assert templates[0].is_system is False
    assert templates[1].variables is None
    assert templates[1].is_system is True


@pytest.mark.asyncio
async def test_create_email_template(service, mock_session):
    """create_email_template persists and maps the new template."""
    _stamp_on_add(
        mock_session,
        id=TEMPLATE_ID,
        created_at=NOW,
        updated_at=NOW,
    )

    data = EmailTemplateCreate(
        name="Breach notice",
        subject_template="Security incident at {{vendor}}",
        body_template="Details: {{details}}",
        variables={"vendor": "string", "details": "string"},
        is_system=True,
    )
    result = await service.create_email_template(TENANT_ID, data)

    mock_session.add.assert_called_once()
    added = mock_session.add.call_args.args[0]
    assert isinstance(added, EmailTemplate)
    assert added.tenant_id == TENANT_ID
    assert added.name == "Breach notice"
    assert added.subject_template == (
        "Security incident at {{vendor}}"
    )
    assert added.body_template == "Details: {{details}}"
    assert added.is_system is True
    mock_session.flush.assert_awaited_once()

    assert result.id == TEMPLATE_ID
    assert result.name == "Breach notice"
    assert result.variables == {
        "vendor": "string",
        "details": "string",
    }


@pytest.mark.asyncio
async def test_create_email_template_defaults(
    service, mock_session
):
    """Optional fields default to None / False on create."""
    _stamp_on_add(
        mock_session,
        id=TEMPLATE_ID,
        created_at=NOW,
        updated_at=NOW,
    )

    result = await service.create_email_template(
        TENANT_ID,
        EmailTemplateCreate(
            name="Minimal",
            subject_template="Hi",
            body_template="Body",
        ),
    )

    added = mock_session.add.call_args.args[0]
    assert added.variables is None
    assert added.is_system is False
    assert result.variables is None
    assert result.is_system is False


@pytest.mark.asyncio
async def test_update_email_template_patches_set_fields(
    service, mock_session
):
    """update_email_template applies only the supplied fields."""
    template = _make_email_template()
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result(items=[template])
    )

    data = EmailTemplateUpdate(body_template="New body")
    result = await service.update_email_template(
        TENANT_ID, TEMPLATE_ID, data
    )

    assert template.body_template == "New body"
    assert template.name == "Assessment reminder"
    assert template.subject_template == "Reminder: {{assessment}}"
    assert result is not None
    assert result.body_template == "New body"
    mock_session.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_email_template_can_null_variables(
    service, mock_session
):
    """Explicitly passing None clears a nullable field."""
    template = _make_email_template()
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result(items=[template])
    )

    result = await service.update_email_template(
        TENANT_ID,
        TEMPLATE_ID,
        EmailTemplateUpdate(variables=None),
    )

    assert template.variables is None
    assert result is not None
    assert result.variables is None


@pytest.mark.asyncio
async def test_update_email_template_missing_returns_none(
    service, mock_session
):
    """Updating an absent template returns None without flushing."""
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result(items=[])
    )

    result = await service.update_email_template(
        TENANT_ID,
        TEMPLATE_ID,
        EmailTemplateUpdate(name="Nope"),
    )

    assert result is None
    mock_session.flush.assert_not_awaited()


# -- Send notification ----------------------------------------------


@pytest.mark.asyncio
async def test_send_notification_defaults_to_in_app(
    service, mock_session
):
    """send_notification defaults channel and nulls entity refs."""
    _stamp_on_add(
        mock_session,
        id=NOTIF_ID,
        created_at=NOW,
        read=False,
        read_at=None,
    )

    result = await service.send_notification(
        TENANT_ID, USER_ID, "Hello", "World"
    )

    mock_session.add.assert_called_once()
    added = mock_session.add.call_args.args[0]
    assert isinstance(added, Notification)
    assert added.channel == "in_app"
    assert added.entity_type is None
    assert added.entity_id is None
    assert result.title == "Hello"
    assert result.message == "World"
    assert result.channel == "in_app"
    assert result.read is False
    mock_session.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_send_notification_with_entity_and_channel(
    service, mock_session
):
    """send_notification carries channel and entity references."""
    _stamp_on_add(
        mock_session,
        id=NOTIF_ID,
        created_at=NOW,
        read=False,
        read_at=None,
    )

    result = await service.send_notification(
        TENANT_ID,
        USER_ID,
        "Vendor breached",
        "See the alert.",
        channel="slack",
        entity_type="vendor",
        entity_id=ENTITY_ID,
    )

    added = mock_session.add.call_args.args[0]
    assert added.channel == "slack"
    assert added.entity_type == "vendor"
    assert added.entity_id == ENTITY_ID
    assert result.channel == "slack"
    assert result.entity_type == "vendor"
    assert result.entity_id == ENTITY_ID


# -- Communication logs ---------------------------------------------


@pytest.mark.asyncio
async def test_get_communication_logs_unfiltered(
    service, mock_session
):
    """Logs list without filters returns mapped rows."""
    count_result = MagicMock()
    count_result.scalar.return_value = 2

    failed = _make_comm_log(
        id=uuid.uuid4(),
        channel="sms",
        recipient="+15550000",
        subject=None,
        status="failed",
        sent_at=None,
        error_message="carrier rejected",
        created_at=NOW - timedelta(hours=1),
    )
    mock_session.execute = AsyncMock(
        side_effect=[
            count_result,
            _mock_execute_result(items=[_make_comm_log(), failed]),
        ]
    )

    page = await service.get_communication_logs(TENANT_ID)

    assert page.total == 2
    assert page.page == 1
    assert page.page_size == 20
    assert page.items[0].recipient == "ciso@acme.com"
    assert page.items[0].status == "sent"
    assert page.items[0].error_message is None
    assert page.items[1].channel == "sms"
    assert page.items[1].subject is None
    assert page.items[1].sent_at is None
    assert page.items[1].error_message == "carrier rejected"


@pytest.mark.asyncio
async def test_get_communication_logs_with_filters(
    service, mock_session
):
    """Channel and status filters narrow the query and paginate."""
    count_result = MagicMock()
    count_result.scalar.return_value = 1

    mock_session.execute = AsyncMock(
        side_effect=[
            count_result,
            _mock_execute_result(items=[_make_comm_log()]),
        ]
    )

    page = await service.get_communication_logs(
        TENANT_ID,
        channel="email",
        status_filter="sent",
        page=2,
        page_size=5,
    )

    assert page.total == 1
    assert page.page == 2
    assert page.page_size == 5
    assert len(page.items) == 1

    # The filtered query must carry both WHERE clauses.
    list_query = str(mock_session.execute.await_args_list[1].args[0])
    assert "communication_logs.channel" in list_query
    assert "communication_logs.status" in list_query


@pytest.mark.asyncio
async def test_get_communication_logs_null_count_becomes_zero(
    service, mock_session
):
    """A NULL count degrades to a total of zero."""
    count_result = MagicMock()
    count_result.scalar.return_value = None

    mock_session.execute = AsyncMock(
        side_effect=[count_result, _mock_execute_result(items=[])]
    )

    page = await service.get_communication_logs(
        TENANT_ID, channel="teams"
    )

    assert page.total == 0
    assert page.items == []


# -- Mappers --------------------------------------------------------


def test_to_notification_maps_nullable_entity():
    """_to_notification tolerates missing entity references."""
    notif = _make_notification(
        entity_type=None, entity_id=None, read=True, read_at=NOW
    )

    response = CommunicationsService._to_notification(notif)

    assert response.entity_type is None
    assert response.entity_id is None
    assert response.read is True
    assert response.read_at == NOW
    assert response.user_id == USER_ID


def test_to_preference_omits_tenant_and_user():
    """PreferenceResponse exposes only the per-category fields."""
    pref = _make_preference()

    response = CommunicationsService._to_preference(pref)

    assert response.id == PREF_ID
    assert response.category == "assessments"
    assert not hasattr(response, "user_id")


def test_to_comm_log_maps_failure_details():
    """_to_comm_log carries error details for failed sends."""
    log = _make_comm_log(
        status="bounced",
        sent_at=None,
        error_message="mailbox full",
    )

    response = CommunicationsService._to_comm_log(log)

    assert response.status == "bounced"
    assert response.sent_at is None
    assert response.error_message == "mailbox full"
    assert response.recipient == "ciso@acme.com"
