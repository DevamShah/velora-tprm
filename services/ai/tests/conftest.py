"""
Shared fixtures for AI service tests.
"""

from __future__ import annotations

import os
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.claude_client import ClaudeClient, ClaudeResponse


@pytest.fixture
def tenant_id() -> uuid.UUID:
    return uuid.UUID("11111111-1111-1111-1111-111111111111")


@pytest.fixture
def assessment_id() -> uuid.UUID:
    return uuid.UUID("22222222-2222-2222-2222-222222222222")


@pytest.fixture
def mock_claude_response() -> ClaudeResponse:
    """A typical successful Claude response."""
    return ClaudeResponse(
        content='[{"question_id": "33333333-3333-3333-3333-333333333333", '
        '"answer": "AES-256-GCM encryption at rest, TLS 1.3 in transit.", '
        '"confidence": 0.88, '
        '"reasoning": "Based on SOC 2 Type II report section 4.2.", '
        '"evidence_citations": ["SOC 2 Type II 2025"]}]',
        input_tokens=450,
        output_tokens=120,
        model="claude-sonnet-4-20250514",
        stop_reason="end_turn",
    )


@pytest.fixture
def mock_claude_client(mock_claude_response):
    """A mocked ClaudeClient that returns predictable responses."""
    client = MagicMock(spec=ClaudeClient)
    client.send_message = AsyncMock(
        return_value=mock_claude_response
    )
    client.close = AsyncMock()
    return client


@pytest.fixture
def sample_questions():
    """Sample questionnaire questions for testing."""
    return [
        {
            "question_id": "33333333-3333-3333-3333-333333333333",
            "question_text": "How is data encrypted at rest and in transit?",
        },
        {
            "question_id": "44444444-4444-4444-4444-444444444444",
            "question_text": "Describe your access control mechanisms.",
        },
    ]


@pytest.fixture
def sample_vendor_context():
    """Sample vendor profile for testing."""
    return {
        "name": "Acme Cloud",
        "domain": "acmecloud.com",
        "tier": "critical",
        "data_classification": "confidential",
        "business_criticality": "high",
        "certifications": "SOC 2 Type II, ISO 27001",
        "industry": "Cloud Services",
    }


@pytest.fixture
def sample_evidence_context():
    """Sample parsed evidence for testing."""
    return [
        {
            "document_type": "SOC 2 Type II",
            "extraction_summary": (
                "Audit period: 2025-01-01 to 2025-12-31. "
                "Unqualified opinion. No exceptions noted. "
                "Controls: encryption, access control, monitoring."
            ),
        },
    ]
