"""
Integration tests for vendor API endpoints.

Uses httpx.AsyncClient against the FastAPI app with mocked
dependencies for database session and authentication.
A valid JWT is generated to pass the AuthMiddleware layer.
"""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from typing import AsyncGenerator
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.core.security import create_access_token
from app.modules.vendors.schemas import (
    VendorDetailResponse,
    VendorListResponse,
    VendorResponse,
)

TENANT_ID = uuid.UUID("00000000-0000-4000-a000-000000000001")
USER_ID = uuid.UUID("00000000-0000-4000-a000-000000000010")
VENDOR_ID = uuid.UUID("00000000-0000-4000-a000-000000000100")
NOW = datetime.now(timezone.utc)

JWT_SECRET = os.environ["JWT_SECRET_KEY"]

MOCK_USER = {
    "user_id": USER_ID,
    "tenant_id": TENANT_ID,
    "roles": ["Admin"],
    "permissions": [
        "vendors.read",
        "vendors.write",
        "vendors.delete",
    ],
}

MOCK_USER_READONLY = {
    "user_id": USER_ID,
    "tenant_id": TENANT_ID,
    "roles": ["Viewer"],
    "permissions": ["vendors.read"],
}


def _make_token(user_data: dict) -> str:
    """Generate a valid JWT for passing AuthMiddleware."""
    return create_access_token(
        data={
            "sub": str(user_data["user_id"]),
            "tenant_id": str(user_data["tenant_id"]),
            "roles": user_data["roles"],
            "permissions": user_data["permissions"],
        },
        secret_key=JWT_SECRET,
        expires_minutes=30,
    )


def _auth_headers(user_data: dict) -> dict:
    """Build Authorization header with valid JWT."""
    token = _make_token(user_data)
    return {"Authorization": f"Bearer {token}"}


def _vendor_response(**overrides) -> VendorResponse:
    """Build a VendorResponse with defaults."""
    defaults = dict(
        id=VENDOR_ID,
        tenant_id=TENANT_ID,
        name="Test Vendor",
        domain="test.com",
        description=None,
        status="active",
        tier="medium",
        industry="Tech",
        country="US",
        employee_count=100,
        annual_revenue=None,
        data_classification=None,
        business_criticality=None,
        contract_start_date=None,
        contract_end_date=None,
        contract_value=None,
        primary_contact_name=None,
        primary_contact_email=None,
        tags=[],
        notes=None,
        inherent_risk_score=None,
        residual_risk_score=None,
        external_rating_score=None,
        external_rating_provider=None,
        last_assessed_at=None,
        next_assessment_due=None,
        contacts_count=0,
        created_at=NOW,
        updated_at=NOW,
    )
    defaults.update(overrides)
    return VendorResponse(**defaults)


def _detail_response(**overrides) -> VendorDetailResponse:
    """Build a VendorDetailResponse with defaults."""
    defaults = dict(
        id=VENDOR_ID,
        tenant_id=TENANT_ID,
        name="Test Vendor",
        domain="test.com",
        description=None,
        status="active",
        tier="medium",
        industry="Tech",
        country="US",
        employee_count=100,
        annual_revenue=None,
        data_classification=None,
        business_criticality=None,
        contract_start_date=None,
        contract_end_date=None,
        contract_value=None,
        primary_contact_name=None,
        primary_contact_email=None,
        tags=[],
        notes=None,
        inherent_risk_score=None,
        residual_risk_score=None,
        external_rating_score=None,
        external_rating_provider=None,
        last_assessed_at=None,
        next_assessment_due=None,
        contacts=[],
        enrichments=[],
        timeline=[],
        created_at=NOW,
        updated_at=NOW,
    )
    defaults.update(overrides)
    return VendorDetailResponse(**defaults)


def _create_app_with_overrides(user_data=None):
    """Create app with DB and auth dependency overrides."""
    from app.core.database import get_db
    from app.core.dependencies import get_current_user
    from app.main import create_app

    app = create_app()

    async def _mock_db():
        yield AsyncMock()

    app.dependency_overrides[get_db] = _mock_db

    if user_data is not None:
        async def _mock_user():
            return user_data
        app.dependency_overrides[get_current_user] = _mock_user

    return app


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Authenticated client with full permissions."""
    app = _create_app_with_overrides(MOCK_USER)
    transport = ASGITransport(app=app)
    headers = _auth_headers(MOCK_USER)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        headers=headers,
    ) as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def unauth_client() -> AsyncGenerator[AsyncClient, None]:
    """Client with no auth — tests 401 paths."""
    app = _create_app_with_overrides()
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def readonly_client() -> AsyncGenerator[AsyncClient, None]:
    """Client with read-only permissions — tests 403 paths."""
    app = _create_app_with_overrides(MOCK_USER_READONLY)
    transport = ASGITransport(app=app)
    headers = _auth_headers(MOCK_USER_READONLY)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        headers=headers,
    ) as ac:
        yield ac
    app.dependency_overrides.clear()


# ── test_create_vendor_returns_201 ─────────────────────────


@pytest.mark.asyncio
async def test_create_vendor_returns_201(client):
    """POST /api/v1/vendors should return 201 with vendor data."""
    resp_data = _vendor_response()

    with patch(
        "app.modules.vendors.router.VendorService"
    ) as mock_svc_cls:
        mock_svc = AsyncMock()
        mock_svc.create_vendor.return_value = resp_data
        mock_svc_cls.return_value = mock_svc

        response = await client.post(
            "/api/v1/vendors",
            json={"name": "Test Vendor"},
        )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Vendor"
    assert data["id"] == str(VENDOR_ID)


# ── test_list_vendors_returns_paginated ────────────────────


@pytest.mark.asyncio
async def test_list_vendors_returns_paginated(client):
    """GET /api/v1/vendors should return paginated list."""
    resp_data = VendorListResponse(
        items=[_vendor_response()],
        total=1,
        page=1,
        page_size=20,
    )

    with patch(
        "app.modules.vendors.router.VendorService"
    ) as mock_svc_cls:
        mock_svc = AsyncMock()
        mock_svc.list_vendors.return_value = resp_data
        mock_svc_cls.return_value = mock_svc

        response = await client.get("/api/v1/vendors")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["page"] == 1


# ── test_get_vendor_returns_detail ─────────────────────────


@pytest.mark.asyncio
async def test_get_vendor_returns_detail(client):
    """GET /api/v1/vendors/{id} should return full detail."""
    resp_data = _detail_response()

    with patch(
        "app.modules.vendors.router.VendorService"
    ) as mock_svc_cls:
        mock_svc = AsyncMock()
        mock_svc.get_vendor.return_value = resp_data
        mock_svc_cls.return_value = mock_svc

        response = await client.get(
            f"/api/v1/vendors/{VENDOR_ID}"
        )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Vendor"
    assert "contacts" in data
    assert "enrichments" in data


# ── test_update_vendor_returns_updated ─────────────────────


@pytest.mark.asyncio
async def test_update_vendor_returns_updated(client):
    """PUT /api/v1/vendors/{id} should return updated vendor."""
    resp_data = _vendor_response(name="Updated Vendor")

    with patch(
        "app.modules.vendors.router.VendorService"
    ) as mock_svc_cls:
        mock_svc = AsyncMock()
        mock_svc.update_vendor.return_value = resp_data
        mock_svc_cls.return_value = mock_svc

        response = await client.put(
            f"/api/v1/vendors/{VENDOR_ID}",
            json={"name": "Updated Vendor"},
        )

    assert response.status_code == 200
    assert response.json()["name"] == "Updated Vendor"


# ── test_delete_vendor_returns_204 ─────────────────────────


@pytest.mark.asyncio
async def test_delete_vendor_returns_204(client):
    """DELETE /api/v1/vendors/{id} should return 204."""
    with patch(
        "app.modules.vendors.router.VendorService"
    ) as mock_svc_cls:
        mock_svc = AsyncMock()
        mock_svc.delete_vendor.return_value = True
        mock_svc_cls.return_value = mock_svc

        response = await client.delete(
            f"/api/v1/vendors/{VENDOR_ID}"
        )

    assert response.status_code == 204


# ── test_unauthorized_returns_401 ──────────────────────────


@pytest.mark.asyncio
async def test_unauthorized_returns_401(unauth_client):
    """Requests without auth should return 401."""
    response = await unauth_client.get("/api/v1/vendors")
    assert response.status_code == 401


# ── test_insufficient_permission_returns_403 ───────────────


@pytest.mark.asyncio
async def test_insufficient_permission_returns_403(
    readonly_client,
):
    """Write requests with read-only perms should return 403."""
    response = await readonly_client.post(
        "/api/v1/vendors",
        json={"name": "Blocked Vendor"},
    )
    assert response.status_code == 403
