"""
Shared test fixtures for Velora TPRM backend tests.

Provides async session mocking, test user context, and app client.
"""

from __future__ import annotations

import base64
import os
import uuid
from datetime import datetime, timezone
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

# Set required env vars BEFORE importing app code
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://test:test@localhost:5432/test",
)
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("S3_ENDPOINT", "http://localhost:9000")
os.environ.setdefault("S3_BUCKET", "test-bucket")
os.environ.setdefault(
    "JWT_SECRET_KEY",
    "test-secret-key-that-is-at-least-32-characters-long",
)
_test_key = base64.urlsafe_b64encode(os.urandom(32)).decode()
os.environ.setdefault("ENCRYPTION_KEY", _test_key)


DEMO_TENANT_ID = uuid.UUID(
    "00000000-0000-4000-a000-000000000001"
)
TEST_USER_ID = uuid.UUID(
    "00000000-0000-4000-a000-000000000010"
)


@pytest.fixture
def tenant_id() -> uuid.UUID:
    """Fixed tenant ID for tests."""
    return DEMO_TENANT_ID


@pytest.fixture
def user_id() -> uuid.UUID:
    """Fixed user ID for tests."""
    return TEST_USER_ID


@pytest.fixture
def current_user() -> dict:
    """Authenticated user context with all permissions."""
    return {
        "user_id": TEST_USER_ID,
        "tenant_id": DEMO_TENANT_ID,
        "roles": ["Admin"],
        "permissions": [
            "vendors.read",
            "vendors.write",
            "vendors.delete",
            "assessments.read",
            "assessments.write",
            "assessments.manage",
        ],
    }


@pytest.fixture
def mock_session() -> AsyncMock:
    """Mock async SQLAlchemy session."""
    session = AsyncMock()
    session.execute = AsyncMock()
    session.flush = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.add = MagicMock()
    return session
