# Velora TPRM AI Service — Phase 8 Execution (Sprint 1)

## Context
- Product: Velora TPRM
- Sprint: 1 of 11 (v2.1 Intelligence Layer)
- Goal: Replace mock AI responses with real Anthropic Claude API calls
- Service: services/ai/ (Port 8012)
- Existing: Mock _mock_answer() in service.py; CRUD for review queue works

## [SECURE-CODE-MANDATE: ACTIVE]
Agent: Nirmitya (via Ralph)
Task: TSK-01001 through TSK-01005
Pre-code checklist: PENDING

## Coding Standards (Blueprint S10.1)
- TDD: tests first, implementation second where practical
- Minimum 80% unit test coverage
- Max 40 lines/function, 400 lines/file
- No direct LLM API calls outside claude_client.py — all AI calls go through the wrapper
- Error handling for every external call (Anthropic API)
- Input validation for every public function
- Structured logging (JSON format), no PII in logs
- No hardcoded API keys — use environment variables only

## Tech Stack
- Backend: Python 3.12+ / FastAPI / Pydantic v2
- AI SDK: anthropic (AsyncAnthropic)
- Testing: pytest + pytest-asyncio + pytest-cov
- Existing patterns: See service.py for router/service/schema/model patterns

## Security Rules
- S1: Validate all inputs to AI endpoints
- S4: ZERO hardcoded secrets — ANTHROPIC_API_KEY from env only
- S5: No PII in logs — vendor names/domains OK, but no user emails or assessment content in log messages
- S8: Error messages to clients reveal nothing about internal API state
- S10: Rate limiting on /ai/auto-fill (already exists via gateway)

## Validation Commands
- Test: `cd services/ai && python -m pytest tests/ -v --tb=short`
- Lint: `cd services/ai && python -m ruff check src/`
- Type: `cd services/ai && python -m mypy src/ --ignore-missing-imports`

## File Ownership (Sprint 1 — Nirmitya ONLY)
| File | Action |
|------|--------|
| pyproject.toml | MODIFY — add anthropic dependency |
| src/claude_client.py | CREATE — async Claude wrapper |
| src/prompts.py | CREATE — prompt templates |
| src/service.py | MODIFY — replace mock with real calls |
| src/schemas.py | MODIFY — add token tracking fields |
| tests/test_claude_integration.py | CREATE — integration tests |
| tests/conftest.py | MODIFY — add Claude fixtures |

## Rules
- Every story must be completable in one context window
- Commit after each passing story
- Log learnings to progress.txt
- Do NOT modify files outside services/ai/
- Do NOT modify the router.py endpoints — only the service layer changes
- Existing /ai/auto-fill, /ai/review-queue, /ai/usage endpoints MUST continue to work
