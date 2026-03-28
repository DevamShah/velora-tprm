"""
Tests for Claude API integration — client, prompts, and auto-fill.

Unit tests mock the Anthropic client. Integration tests (marked
@pytest.mark.integration) require ANTHROPIC_API_KEY in environment.
"""

from __future__ import annotations

import json
import os
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.claude_client import ClaudeClient, ClaudeResponse
from src.prompts import (
    QUESTIONNAIRE_SYSTEM_PROMPT,
    batch_questions,
    build_autofill_prompt,
    parse_autofill_response,
)


# -- ClaudeClient tests -----------------------------------------------


class TestClaudeClient:
    """Tests for the async Claude client wrapper."""

    def test_init_requires_api_key(self):
        """Client raises ValueError without API key."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
                ClaudeClient()

    def test_init_with_env_var(self):
        """Client initializes when ANTHROPIC_API_KEY is set."""
        with patch.dict(
            os.environ, {"ANTHROPIC_API_KEY": "test-key-123"}
        ):
            client = ClaudeClient()
            assert client._model == "claude-sonnet-4-20250514"

    def test_init_with_explicit_key(self):
        """Client accepts explicit API key."""
        client = ClaudeClient(api_key="explicit-key")
        assert client is not None

    @pytest.mark.asyncio
    async def test_send_message_success(
        self, mock_claude_response
    ):
        """Successful message returns structured ClaudeResponse."""
        with patch.dict(
            os.environ, {"ANTHROPIC_API_KEY": "test"}
        ):
            client = ClaudeClient()

        mock_msg = MagicMock()
        mock_msg.content = [
            MagicMock(text=mock_claude_response.content)
        ]
        mock_msg.usage = MagicMock(
            input_tokens=450, output_tokens=120
        )
        mock_msg.model = "claude-sonnet-4-20250514"
        mock_msg.stop_reason = "end_turn"

        client._client.messages.create = AsyncMock(
            return_value=mock_msg
        )

        result = await client.send_message(
            system="test system",
            messages=[{"role": "user", "content": "test"}],
        )

        assert isinstance(result, ClaudeResponse)
        assert result.input_tokens == 450
        assert result.output_tokens == 120
        assert "AES-256-GCM" in result.content

    @pytest.mark.asyncio
    async def test_timeout_raises(self):
        """API timeout is raised after logging."""
        import anthropic

        with patch.dict(
            os.environ, {"ANTHROPIC_API_KEY": "test"}
        ):
            client = ClaudeClient()

        client._client.messages.create = AsyncMock(
            side_effect=anthropic.APITimeoutError(request=MagicMock())
        )

        with pytest.raises(anthropic.APITimeoutError):
            await client.send_message(
                system="test",
                messages=[{"role": "user", "content": "test"}],
            )

    @pytest.mark.asyncio
    async def test_rate_limit_retries(self):
        """Rate limit triggers retry via tenacity."""
        import anthropic

        with patch.dict(
            os.environ, {"ANTHROPIC_API_KEY": "test"}
        ):
            client = ClaudeClient()

        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="ok")]
        mock_response.usage = MagicMock(
            input_tokens=10, output_tokens=5
        )
        mock_response.model = "claude-sonnet-4-20250514"
        mock_response.stop_reason = "end_turn"

        mock_request = MagicMock()
        mock_request.url = "https://api.anthropic.com/v1/messages"
        mock_request.method = "POST"
        mock_request.headers = {}

        mock_http_response = MagicMock()
        mock_http_response.status_code = 429
        mock_http_response.headers = {}

        # Fail twice with rate limit, succeed on third
        client._client.messages.create = AsyncMock(
            side_effect=[
                anthropic.RateLimitError(
                    message="rate limited",
                    response=mock_http_response,
                    body={"error": {"message": "rate limited"}},
                ),
                anthropic.RateLimitError(
                    message="rate limited",
                    response=mock_http_response,
                    body={"error": {"message": "rate limited"}},
                ),
                mock_response,
            ]
        )

        result = await client.send_message(
            system="test",
            messages=[{"role": "user", "content": "test"}],
        )
        assert result.content == "ok"


# -- Prompt tests ------------------------------------------------------


class TestPrompts:
    """Tests for prompt building and response parsing."""

    def test_build_prompt_includes_vendor(
        self, sample_vendor_context, sample_questions
    ):
        """Prompt includes vendor profile fields."""
        prompt = build_autofill_prompt(
            vendor_context=sample_vendor_context,
            questions=sample_questions,
        )
        assert "Acme Cloud" in prompt
        assert "acmecloud.com" in prompt
        assert "critical" in prompt

    def test_build_prompt_includes_evidence(
        self,
        sample_vendor_context,
        sample_evidence_context,
        sample_questions,
    ):
        """Prompt includes evidence when provided."""
        prompt = build_autofill_prompt(
            vendor_context=sample_vendor_context,
            evidence_context=sample_evidence_context,
            questions=sample_questions,
        )
        assert "SOC 2 Type II" in prompt
        assert "Unqualified opinion" in prompt

    def test_build_prompt_includes_questions(
        self, sample_vendor_context, sample_questions
    ):
        """Prompt includes all questions with IDs."""
        prompt = build_autofill_prompt(
            vendor_context=sample_vendor_context,
            questions=sample_questions,
        )
        assert "encrypted at rest" in prompt
        assert "access control" in prompt

    def test_batch_questions_splits_correctly(self):
        """Questions are batched into groups of 10."""
        questions = [{"q": i} for i in range(25)]
        batches = batch_questions(questions)
        assert len(batches) == 3
        assert len(batches[0]) == 10
        assert len(batches[1]) == 10
        assert len(batches[2]) == 5

    def test_parse_valid_json(self):
        """Clean JSON array is parsed correctly."""
        raw = json.dumps([
            {
                "question_id": "abc-123",
                "answer": "Yes",
                "confidence": 0.9,
            }
        ])
        result = parse_autofill_response(raw)
        assert len(result) == 1
        assert result[0]["answer"] == "Yes"

    def test_parse_markdown_wrapped_json(self):
        """JSON inside markdown code blocks is parsed."""
        raw = '```json\n[{"question_id": "x", "answer": "No"}]\n```'
        result = parse_autofill_response(raw)
        assert len(result) == 1
        assert result[0]["answer"] == "No"

    def test_parse_invalid_json_returns_empty(self):
        """Invalid JSON returns empty list."""
        result = parse_autofill_response("not json at all")
        assert result == []

    def test_parse_validates_required_fields(self):
        """Items missing required fields are filtered out."""
        raw = json.dumps([
            {"question_id": "a", "answer": "Yes", "confidence": 0.9},
            {"question_id": "b"},  # missing answer + confidence
            {"random": "junk"},
        ])
        result = parse_autofill_response(raw)
        assert len(result) == 1
        assert result[0]["question_id"] == "a"

    def test_system_prompt_enforces_json(self):
        """System prompt requires JSON output format."""
        assert "JSON" in QUESTIONNAIRE_SYSTEM_PROMPT
        assert "question_id" in QUESTIONNAIRE_SYSTEM_PROMPT
        assert "confidence" in QUESTIONNAIRE_SYSTEM_PROMPT


# -- Integration test (requires real API key) --------------------------


@pytest.mark.integration
@pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set",
)
class TestClaudeIntegration:
    """Real API tests — only run when API key is available."""

    @pytest.mark.asyncio
    async def test_real_autofill_response(
        self, sample_vendor_context, sample_questions
    ):
        """Real Claude call returns parseable JSON answers."""
        client = ClaudeClient()
        prompt = build_autofill_prompt(
            vendor_context=sample_vendor_context,
            questions=sample_questions[:1],
        )

        response = await client.send_message(
            system=QUESTIONNAIRE_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )

        assert response.input_tokens > 0
        assert response.output_tokens > 0

        parsed = parse_autofill_response(response.content)
        assert len(parsed) >= 1
        assert "answer" in parsed[0]
        assert "confidence" in parsed[0]

        await client.close()
