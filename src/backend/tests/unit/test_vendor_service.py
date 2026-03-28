"""
Unit tests for VendorService.

Mocks the database session and FieldEncryptor to test pure
business logic without infrastructure dependencies.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio

from app.modules.vendors.models import Vendor, VendorContact
from app.modules.vendors.schemas import (
    VendorContactCreate,
    VendorCreate,
    VendorFilterParams,
    VendorUpdate,
)
from app.modules.vendors.service import VendorService

TENANT_ID = uuid.UUID("00000000-0000-4000-a000-000000000001")
VENDOR_ID = uuid.UUID("00000000-0000-4000-a000-000000000100")
CONTACT_ID = uuid.UUID("00000000-0000-4000-a000-000000000200")


def _make_vendor(**overrides) -> Vendor:
    """Create a Vendor ORM object with sensible defaults."""
    now = datetime.now(timezone.utc)
    defaults = dict(
        id=VENDOR_ID,
        tenant_id=TENANT_ID,
        name="Acme Corp",
        domain="acme.com",
        description="Test vendor",
        status="active",
        tier="medium",
        industry="Technology",
        country="US",
        employee_count=500,
        annual_revenue=Decimal("1000000"),
        data_classification="internal",
        business_criticality="medium",
        contract_start_date=None,
        contract_end_date=None,
        contract_value=Decimal("200000"),
        primary_contact_name="John Doe",
        primary_contact_email_encrypted=None,
        primary_contact_email_hash=None,
        tags=["saas", "tech"],
        notes="Test notes",
        inherent_risk_score=45.0,
        residual_risk_score=30.0,
        external_rating_score=None,
        external_rating_provider=None,
        last_assessed_at=None,
        next_assessment_due=None,
        deleted_at=None,
        created_at=now,
        updated_at=now,
        contacts=[],
        enrichments=[],
    )
    defaults.update(overrides)
    vendor = MagicMock(spec=Vendor)
    for k, v in defaults.items():
        setattr(vendor, k, v)
    return vendor


def _make_contact(**overrides) -> VendorContact:
    """Create a VendorContact ORM object with defaults."""
    now = datetime.now(timezone.utc)
    defaults = dict(
        id=CONTACT_ID,
        tenant_id=TENANT_ID,
        vendor_id=VENDOR_ID,
        first_name="Jane",
        last_name="Smith",
        email_encrypted=None,
        email_hash=None,
        phone_encrypted=None,
        phone_hash=None,
        role="Security Lead",
        is_primary=True,
        portal_access=False,
        created_at=now,
        updated_at=now,
    )
    defaults.update(overrides)
    contact = MagicMock(spec=VendorContact)
    for k, v in defaults.items():
        setattr(contact, k, v)
    return contact


def _mock_execute_result(items):
    """Create a mock execute result that returns scalars."""
    result = MagicMock()
    scalars = MagicMock()
    scalars.first.return_value = items[0] if items else None
    scalars.all.return_value = items
    result.scalars.return_value = scalars
    result.scalar.return_value = len(items)
    return result


@pytest.fixture
def mock_session():
    """Async mock session."""
    session = AsyncMock()
    session.add = MagicMock()
    return session


@pytest.fixture
def service(mock_session):
    """VendorService with mocked session and encryptor."""
    with patch(
        "app.modules.vendors.service.get_settings"
    ) as mock_settings, patch(
        "app.modules.vendors.service.FieldEncryptor"
    ) as mock_enc_cls:
        settings = MagicMock()
        settings.ENCRYPTION_KEY = "dGVzdC1rZXktdGhhdC1pcy0zMi1ieXRlcw=="
        mock_settings.return_value = settings

        enc = MagicMock()
        enc.encrypt.return_value = "encrypted_value"
        enc.decrypt.return_value = "decrypted@example.com"
        enc.hmac_hash.return_value = "abc123hash"
        mock_enc_cls.return_value = enc

        svc = VendorService(mock_session)
        svc._encryptor = enc
        yield svc


# ── test_create_vendor ─────────────────────────────────────


@pytest.mark.asyncio
async def test_create_vendor(service, mock_session):
    """create_vendor should persist and return a VendorResponse."""
    mock_session.flush = AsyncMock()
    mock_session.add = MagicMock()

    data = VendorCreate(
        name="Acme Corp",
        domain="acme.com",
        industry="Technology",
        country="US",
    )

    with patch.object(
        service, "_to_response"
    ) as mock_resp:
        mock_resp.return_value = MagicMock(name="Acme Corp")
        result = await service.create_vendor(TENANT_ID, data)

    mock_session.add.assert_called_once()
    mock_session.flush.assert_awaited_once()
    assert result is not None


# ── test_list_vendors_with_pagination ──────────────────────


@pytest.mark.asyncio
async def test_list_vendors_with_pagination(
    service, mock_session
):
    """list_vendors should return paginated results."""
    vendor = _make_vendor()
    count_result = MagicMock()
    count_result.scalar.return_value = 1

    list_result = _mock_execute_result([vendor])

    mock_session.execute = AsyncMock(
        side_effect=[count_result, list_result]
    )

    filters = VendorFilterParams(page=1, page_size=10)
    result = await service.list_vendors(TENANT_ID, filters)

    assert result.total == 1
    assert result.page == 1
    assert result.page_size == 10
    assert len(result.items) == 1


# ── test_list_vendors_with_filters ─────────────────────────


@pytest.mark.asyncio
async def test_list_vendors_with_filters(
    service, mock_session
):
    """list_vendors should apply status and search filters."""
    count_result = MagicMock()
    count_result.scalar.return_value = 0

    list_result = _mock_execute_result([])

    mock_session.execute = AsyncMock(
        side_effect=[count_result, list_result]
    )

    filters = VendorFilterParams(
        status="active", search="acme", page=1, page_size=20
    )
    result = await service.list_vendors(TENANT_ID, filters)

    assert result.total == 0
    assert result.items == []


# ── test_get_vendor_detail ─────────────────────────────────


@pytest.mark.asyncio
async def test_get_vendor_detail(service, mock_session):
    """get_vendor should return VendorDetailResponse."""
    vendor = _make_vendor()
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([vendor])
    )

    result = await service.get_vendor(TENANT_ID, VENDOR_ID)

    assert result is not None
    assert result.name == "Acme Corp"
    assert result.contacts == []


# ── test_update_vendor ─────────────────────────────────────


@pytest.mark.asyncio
async def test_update_vendor(service, mock_session):
    """update_vendor should apply changes and return updated."""
    vendor = _make_vendor()
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([vendor])
    )

    data = VendorUpdate(name="Acme Corp Updated")
    result = await service.update_vendor(
        TENANT_ID, VENDOR_ID, data
    )

    assert result is not None
    assert vendor.name == "Acme Corp Updated"
    mock_session.flush.assert_awaited()


# ── test_delete_vendor ─────────────────────────────────────


@pytest.mark.asyncio
async def test_delete_vendor(service, mock_session):
    """delete_vendor should set deleted_at timestamp."""
    vendor = _make_vendor()
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([vendor])
    )

    result = await service.delete_vendor(TENANT_ID, VENDOR_ID)

    assert result is True
    assert vendor.deleted_at is not None
    mock_session.flush.assert_awaited()


# ── test_calculate_tier ────────────────────────────────────


@pytest.mark.asyncio
async def test_calculate_tier(service, mock_session):
    """calculate_tier should derive tier from vendor attributes."""
    vendor = _make_vendor(
        data_classification="restricted",
        business_criticality="critical",
        contract_value=Decimal("2000000"),
        employee_count=50000,
    )
    mock_session.execute = AsyncMock(
        return_value=_mock_execute_result([vendor])
    )

    tier = await service.calculate_tier(TENANT_ID, VENDOR_ID)

    assert tier == "critical"
    assert vendor.tier == "critical"


# ── test_bulk_import_success ───────────────────────────────


@pytest.mark.asyncio
async def test_bulk_import_success(service, mock_session):
    """bulk_import should parse CSV and create vendors."""
    mock_session.flush = AsyncMock()

    csv_data = (
        "name,domain,industry,country\n"
        "Test Vendor,test.com,Tech,US\n"
        "Another Vendor,another.com,Finance,UK\n"
    )

    with patch.object(
        service,
        "create_vendor",
        new_callable=AsyncMock,
    ) as mock_create:
        mock_create.return_value = MagicMock()
        result = await service.bulk_import(
            TENANT_ID, csv_data
        )

    assert result.success_count == 2
    assert result.error_count == 0
    assert mock_create.await_count == 2


# ── test_bulk_import_with_errors ───────────────────────────


@pytest.mark.asyncio
async def test_bulk_import_with_errors(
    service, mock_session
):
    """bulk_import should track per-row errors."""
    csv_data = (
        "name,domain,industry,country\n"
        "Good Vendor,good.com,Tech,US\n"
        ",bad.com,Tech,US\n"
    )

    call_count = 0

    async def side_effect(tid, data):
        nonlocal call_count
        call_count += 1
        if call_count == 2:
            raise ValueError("Name is required")
        return MagicMock()

    with patch.object(
        service,
        "create_vendor",
        side_effect=side_effect,
    ):
        result = await service.bulk_import(
            TENANT_ID, csv_data
        )

    assert result.success_count == 1
    assert result.error_count == 1
    assert result.errors[0].row == 3
    assert "string_too_short" in result.errors[0].message


# ── test_compute_tier_logic ────────────────────────────────


def test_compute_tier_critical():
    """_compute_tier returns critical for high-score vendor."""
    vendor = _make_vendor(
        data_classification="restricted",
        business_criticality="critical",
        contract_value=Decimal("2000000"),
        employee_count=50000,
    )
    assert VendorService._compute_tier(vendor) == "critical"


def test_compute_tier_low():
    """_compute_tier returns low for minimal vendor."""
    vendor = _make_vendor(
        data_classification="public",
        business_criticality="low",
        contract_value=Decimal("5000"),
        employee_count=50,
    )
    assert VendorService._compute_tier(vendor) == "low"


def test_compute_tier_unclassified():
    """_compute_tier returns unclassified when no data."""
    vendor = _make_vendor(
        data_classification=None,
        business_criticality=None,
        contract_value=None,
        employee_count=None,
    )
    assert (
        VendorService._compute_tier(vendor) == "unclassified"
    )
