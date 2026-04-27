---
tags:
  - archeon
  - forgeon
  - product
  - product-velora
---

# Velora TPRM v2.1 -- Sprint Plan

> **Author**: Yojika (Sprint Planning Agent, Pantheon)
> **Orchestrator**: Harion
> **Version**: 2.0.0
> **Date**: 2026-03-28
> **Status**: REVISED -- Iteration 2, addressing F1-F4 (Tantron review findings)
> **Baseline**: v2.0 MVP (14 microservices, 62/62 API tests passing, CRUD complete, intelligence layer stubbed)
> **Scope**: 13 pending P0 features from gap analysis (Tier 1 + Tier 2 + Tier 3)
> **Review History**:
> - v1.0.0 (2026-03-28): MAKER OUTPUT -- Initial sprint plan
> - v2.0.0 (2026-03-28): REVISED -- Addresses Tantron findings F1 (S6 split), F2 (alembic setup), F3 (reordered S4 parallel), F4 (inter-service communication pattern)

---

## Build Philosophy (inherited from v2.0, adapted for intelligence layer)

1. **One sprint = one session** -- Each sprint is a self-contained session with demonstrable output
2. **Vertical slices remain mandatory** -- DB schema changes + service logic + API endpoints + tests in one unit
3. **No mock replacement without tests** -- Every mock-to-real swap must have integration tests proving the real thing works
4. **Dependency-ordered** -- Sprints are sequenced by hard technical dependencies, not arbitrary priority
5. **External API keys required before sprint starts** -- Any sprint touching external APIs must have credentials provisioned in `.env` before execution begins
6. **One frontend agent at a time** -- Drishyon owns all frontend work; no parallel frontend agents (per Devam's directive)

---

## Inter-Service Communication Pattern (F4)

All cross-service calls in this plan follow a single, consistent pattern. This section is normative -- Ralph/OpenHands MUST implement exactly this way.

### Pattern: Async HTTP via httpx

- **Client-to-Backend**: All frontend requests go through the BFF. The BFF is the single entry point; vendor portal and internal dashboard never call microservices directly.
- **BFF-to-Service**: BFF calls downstream services via `httpx.AsyncClient` over Docker DNS (e.g., `http://assessment-service:8000/api/v1/...`). Each service is addressable by its `container_name` in `docker-compose.yml`.
- **Service-to-Service**: When one microservice needs data from another (e.g., evidence service fetching framework clauses, monitoring service triggering scoring re-calculation), it calls the target service directly via `httpx.AsyncClient` over Docker DNS. No message bus, no shared DB access.
- **Service Discovery**: Docker Compose DNS. Each service's `container_name` is its hostname. No external service registry needed in Phase 1.
- **Retry + Timeout**: Every `httpx.AsyncClient` instance MUST be configured with:
  - `timeout=httpx.Timeout(30.0, connect=5.0)` (30s total, 5s connect)
  - Retry with exponential backoff (3 attempts, 1s/2s/4s) via `tenacity` or manual loop
  - Circuit breaker pattern for non-critical calls (e.g., enrichment) -- fail open, log, continue
- **Error Handling**: On downstream failure, the caller logs the error, returns a meaningful error response (not a raw 500), and includes the failing service name in the error detail.
- **Health Checks**: Every service exposes `GET /health` returning `{"status": "ok"}`. The BFF checks downstream health on startup and exposes an aggregate health endpoint.

### Affected Sprints

| Sprint | Cross-Service Calls | Pattern |
|--------|---------------------|---------|
| S3 | Evidence service -> Framework service (`GET /api/v1/frameworks/{id}/clauses/bulk`); Evidence service -> AI service (mapping prompts) | Direct service-to-service via Docker DNS |
| S5 | Assessment service -> Communication service (send email + notification on distribute); BFF -> Assessment service (distribute endpoint) | Direct service-to-service via Docker DNS |
| S6a/S6b | BFF -> Auth, Assessment, Evidence, Findings services (all portal routes) | BFF-to-service via Docker DNS |
| S7 | Monitoring service -> Scoring service (trigger re-score on rating change) | Direct service-to-service via Docker DNS |
| S8 | Workflow service -> All services (Temporal activities call service endpoints) | Temporal activities use httpx to call service endpoints via Docker DNS |

---

## Dependency Graph (F3: S4 parallelized with S2)

```
Sprint 1: AI Service (Claude API)
    |
    +-------+-------+
    |               |
    v               v
Sprint 2            Sprint 4: SSO/SAML/OIDC (parallel with S2, independent of evidence chain)
    |               |
    v               |
Sprint 3            |
    |               |
    +-------+-------+
            |
            v
Sprint 5: Assessment Distribution + SLA + Real Email (depends on S3 + S4)
    |
    v
Sprint 6a: Vendor Portal -- Scaffold + Auth + BFF + Dashboard
    |
    v
Sprint 6b: Vendor Portal -- Assessment UI + Evidence + Findings + Integration Tests
    |
    v
Sprint 7: External Rating API + Alert Correlation
    |
    v
Sprint 8: Temporal Workflows (wires together all services built in S1-S7)
    |
    v
Sprint 9: FAIR Quantification + Cross-Framework Mapping
    |
    v
Sprint 10: Board-Ready Reports (depends on scoring, AI narratives, all data flowing)
```

**Critical path**: S1 -> S2 -> S3 -> S5 -> S6a -> S6b -> S7 -> S8 -> S9 -> S10
**Parallel path**: S4 can execute any time after S1 completes. It MUST complete before S5 starts. Recommended: run S4 in parallel with S2.

---

## Sprint Overview Table

| Sprint | Goal | Stories | Route | Primary Agent | Services Touched | Est. Complexity |
|--------|------|---------|-------|---------------|------------------|-----------------|
| S1 | AI Service: Real Claude API Integration | 5 | Ralph (single service) | Nirmitya | ai | Medium |
| S2 | Evidence Parsing via Azure Document Intelligence | 6 | Ralph (single service) | Nirmitya | evidence | High |
| S3 | Evidence-to-Control Mapping Engine | 5 | OpenHands (ai + evidence + framework) | Nirmitya | evidence, ai, framework | High |
| S4 | SSO/SAML/OIDC Enterprise Auth | 7 | Ralph (single service) | Nirmitya | auth | High |
| S5 | Assessment Distribution + SLA + Real Email | 8 | OpenHands (assessment + communication + workflow) | Nirmitya | assessment, communication, workflow | High |
| S6a | Vendor Portal: Scaffold + Auth + BFF + Dashboard | 4 | OpenHands (frontend + bff + auth) | Drishyon (FE) + Nirmitya (BFF/auth) | frontend, bff, auth | High |
| S6b | Vendor Portal: Assessment UI + Evidence + Findings + Integration Tests | 4 | OpenHands (frontend + bff) | Drishyon (FE) + Nirmitya (BFF) | frontend, bff | High |
| S7 | External Rating API + Alert Correlation Engine | 6 | OpenHands (monitoring + scoring) | Nirmitya | monitoring, scoring | High |
| S8 | Temporal Workflows: Real Orchestration | 5 | Ralph (single service) | Prasaron | workflow | High |
| S9 | FAIR Quantification + Cross-Framework Mapping | 7 | OpenHands (scoring + framework) | Nirmitya | scoring, framework | High |
| S10 | Board-Ready Reports (PDF/PPTX + AI Narratives) | 6 | OpenHands (reporting + ai) | Nirmitya | reporting, ai | High |

**MCA per sprint**: Samikshon (code review) + Rakshon (security review) -> Rudron (approval)
**Darshika**: PRD alignment check after each sprint
**Tantron**: Architecture oversight during execution

---

## Sprint 1: AI Service -- Real Claude API Integration

**Goal**: Replace `_mock_answer()` with actual Anthropic Claude API calls. Every AI response comes from Claude with proper prompt engineering, token tracking, and fallback.

**Prerequisite**: `ANTHROPIC_API_KEY` provisioned in `.env`

### Stories

| ID | Title | Description | Acceptance Criteria | Files to Modify/Create | Assigned |
|----|-------|-------------|--------------------|-----------------------|----------|
| S1-1 | Add Anthropic SDK dependency | Add `anthropic` package to ai service pyproject.toml | `anthropic>=0.40.0` in dependencies; `pip install` succeeds | `services/ai/pyproject.toml` | Nirmitya |
| S1-2 | Create Claude client wrapper | Build a reusable async Claude client with retry, timeout, token counting, and rate limiting | Client initializes with API key from env; sends messages; returns structured responses; handles rate limits with exponential backoff; logs token usage per call | `services/ai/src/claude_client.py` (new) | Nirmitya |
| S1-3 | Build prompt templates for questionnaire pre-fill | Create domain-specific prompts for TPRM questionnaire answering with vendor context injection | Prompts include vendor profile context, evidence context, question text; confidence scoring based on evidence availability; system prompt enforces structured JSON output | `services/ai/src/prompts.py` (new) | Nirmitya |
| S1-4 | Replace _mock_answer with Claude calls | Refactor `AIService.auto_fill_assessment()` to call Claude for each empty question, passing vendor + evidence context | Mock answers replaced; real Claude responses with per-answer confidence; batch processing (not one API call per question -- group into batches of 10); total token usage tracked in DB; fallback to mock if API fails | `services/ai/src/service.py` (modify lines 46-104, 273-307) | Nirmitya |
| S1-5 | Integration tests for real Claude calls | Test auto-fill with real API (can be mocked in CI, real in integration) | Tests cover: successful fill, API timeout fallback, rate limit handling, token tracking accuracy; at least 8 test cases | `services/ai/tests/test_claude_integration.py` (new), `services/ai/tests/conftest.py` (modify) | Nirmitya |

### File Ownership Table

| File | Owner | Action |
|------|-------|--------|
| `services/ai/pyproject.toml` | Nirmitya | MODIFY -- add anthropic dependency |
| `services/ai/src/claude_client.py` | Nirmitya | CREATE -- async Claude wrapper |
| `services/ai/src/prompts.py` | Nirmitya | CREATE -- prompt templates |
| `services/ai/src/service.py` | Nirmitya | MODIFY -- replace mock with real calls |
| `services/ai/src/schemas.py` | Nirmitya | MODIFY -- add token tracking fields |
| `services/ai/tests/test_claude_integration.py` | Nirmitya | CREATE -- integration tests |
| `services/ai/tests/conftest.py` | Nirmitya | MODIFY -- add Claude fixtures |

### Dependencies
- **Hard**: `ANTHROPIC_API_KEY` must exist in `.env` before sprint starts
- **Soft**: None (AI service is self-contained)

### Risk Register
| Risk | Impact | Mitigation |
|------|--------|------------|
| API key not provisioned | Sprint blocked | Pre-validate `.env` in Sprint 0 pre-check |
| Claude rate limits hit during batch fill | Slow responses | Implement exponential backoff + batch grouping in S1-4 |
| Token costs unexpectedly high | Budget overrun | Add per-tenant token budget caps in S1-2; log all usage |
| Claude output format unpredictable | Parsing failures | Enforce structured JSON output via system prompt; validate response schema |

---

## Sprint 2: Evidence Parsing via Azure Document Intelligence

**Goal**: Replace `_generate_mock_extractions()` with real document parsing. SOC 2 reports, ISO certs, and pen test reports get parsed into structured extractions.

**Prerequisite**: `AZURE_DOC_INTELLIGENCE_ENDPOINT` + `AZURE_DOC_INTELLIGENCE_KEY` in `.env`. MinIO running for file storage.

**Note**: S2 can run in parallel with S4 (SSO). Both depend only on S1 being complete. Coordinate accordingly.

### Stories

| ID | Title | Description | Acceptance Criteria | Files to Modify/Create | Assigned |
|----|-------|-------------|--------------------|-----------------------|----------|
| S2-1 | Add Azure Document Intelligence SDK | Add `azure-ai-documentintelligence` to evidence service dependencies | Package installs; import succeeds | `services/evidence/pyproject.toml` | Nirmitya |
| S2-2 | Create document parser client | Build async wrapper around Azure Doc Intelligence with polling for long documents | Client sends PDF/image to Azure; polls for completion; returns structured extraction result; handles timeouts up to 5 min; retries on transient failures | `services/evidence/src/doc_parser.py` (new) | Nirmitya |
| S2-3 | Build extraction pipelines per document type | Create typed extraction logic for SOC 2 (audit period, opinion, scope, exceptions), ISO 27001 (cert number, valid dates, scope, certifier), and pen test (date, tester, findings by severity) | Each document type has a dedicated extraction function; extractions include page numbers and confidence from Azure; at least 6 fields per SOC 2, 5 per ISO, 5 per pen test | `services/evidence/src/extractors/__init__.py` (new), `services/evidence/src/extractors/soc2.py` (new), `services/evidence/src/extractors/iso27001.py` (new), `services/evidence/src/extractors/pentest.py` (new) | Nirmitya |
| S2-4 | Integrate MinIO for real file storage | Replace mock S3 URL with real MinIO presigned upload/download. Evidence upload writes to MinIO; parsing reads from MinIO. | Upload returns real presigned URL; download retrieves actual file bytes; files persist across service restarts | `services/evidence/src/storage.py` (new), `services/evidence/src/service.py` (modify upload_evidence, process_evidence) | Nirmitya |
| S2-5 | Replace mock extractions with real parsing | Refactor `process_evidence()` to: download file from MinIO -> send to Azure -> run type-specific extractor -> persist EvidenceExtraction rows | Status transitions: uploaded -> processing -> parsed (or failed); real extraction rows with real confidence scores; parsed_content contains actual Azure output; extraction_summary is computed from real data | `services/evidence/src/service.py` (modify lines 155-194, remove _generate_mock_extractions) | Nirmitya |
| S2-6 | Integration tests for document parsing | Test with sample SOC 2, ISO cert, pen test PDFs. Mock Azure in unit tests; real Azure in integration. | At least 10 test cases: upload + parse for each doc type; malformed PDF handling; timeout handling; unsupported format graceful failure | `services/evidence/tests/test_parsing_integration.py` (new), `services/evidence/tests/fixtures/` (new -- sample PDFs) | Nirmitya |

### File Ownership Table

| File | Owner | Action |
|------|-------|--------|
| `services/evidence/pyproject.toml` | Nirmitya | MODIFY |
| `services/evidence/src/doc_parser.py` | Nirmitya | CREATE |
| `services/evidence/src/storage.py` | Nirmitya | CREATE |
| `services/evidence/src/extractors/__init__.py` | Nirmitya | CREATE |
| `services/evidence/src/extractors/soc2.py` | Nirmitya | CREATE |
| `services/evidence/src/extractors/iso27001.py` | Nirmitya | CREATE |
| `services/evidence/src/extractors/pentest.py` | Nirmitya | CREATE |
| `services/evidence/src/service.py` | Nirmitya | MODIFY |
| `services/evidence/tests/test_parsing_integration.py` | Nirmitya | CREATE |
| `services/evidence/tests/fixtures/` | Nirmitya | CREATE |
| `docker-compose.yml` | Nirmitya | MODIFY -- ensure MinIO config correct |

### Dependencies
- **Hard**: Azure Doc Intelligence credentials in `.env`; MinIO running in docker-compose
- **Soft**: Sprint 1 complete (AI client pattern reusable)

### Risk Register
| Risk | Impact | Mitigation |
|------|--------|------------|
| Azure Doc Intelligence not available in region | Sprint blocked | Fall back to AWS Textract as alternative; abstraction layer in doc_parser.py |
| Large PDF parsing exceeds 5 min timeout | Incomplete extractions | Implement async polling with configurable timeout; partial extraction on timeout |
| Sample test PDFs not representative | False confidence in tests | Source real anonymized SOC 2 / ISO samples; at least 3 per type |
| MinIO connectivity issues in Docker | Upload failures | Health check in docker-compose; retry logic in storage.py |

---

## Sprint 3: Evidence-to-Control Mapping Engine

**Goal**: After evidence is parsed, automatically map extracted findings to framework controls with coverage type (full/partial/supportive) and confidence scores. Uses Claude for semantic matching.

**Prerequisite**: Sprint 1 (Claude client) + Sprint 2 (real extractions) complete

**Inter-service communication (F4)**: This sprint introduces the first cross-service calls. Evidence service calls Framework service via `httpx.AsyncClient` at `http://framework-service:8000/api/v1/frameworks/{id}/clauses/bulk`. Evidence service calls AI service at `http://ai-service:8000/api/v1/ai/...`. Both use Docker DNS resolution. See "Inter-Service Communication Pattern" section above.

### Stories

| ID | Title | Description | Acceptance Criteria | Files to Modify/Create | Assigned |
|----|-------|-------------|--------------------|-----------------------|----------|
| S3-1 | Build control mapping prompt templates | Create prompts that take extracted evidence fields + framework clause text and determine coverage type + confidence | Prompts handle SOC 2 -> multiple frameworks; output is structured JSON array of `{clause_id, coverage_type, confidence, reasoning}` | `services/ai/src/prompts.py` (modify -- add mapping prompts) | Nirmitya |
| S3-2 | Create mapping engine in evidence service | Build `EvidenceMappingEngine` that: loads relevant framework clauses, sends evidence+clauses to AI service, persists `EvidenceControlMapping` rows | Engine accepts evidence_id + framework_ids; queries framework service for clauses via `httpx.AsyncClient` at `http://framework-service:8000`; calls AI service for mapping via `httpx.AsyncClient` at `http://ai-service:8000`; creates EvidenceControlMapping rows with coverage_type and confidence | `services/evidence/src/mapping_engine.py` (new) | Nirmitya |
| S3-3 | Add cross-service API for clause retrieval | Evidence service needs to fetch framework clauses. Add internal API endpoint in framework service for bulk clause retrieval by framework_id. | `GET /api/v1/frameworks/{id}/clauses/bulk` returns all clauses with text; response cached in Redis for 1 hour | `services/framework/src/router.py` (modify), `services/framework/src/service.py` (modify) | Nirmitya |
| S3-4 | Wire mapping into evidence processing pipeline | After `process_evidence()` parses a document, automatically trigger mapping if framework_ids are associated with the assessment | Status transition: parsed -> mapped; mapping runs asynchronously after parsing; mappings appear in evidence detail response | `services/evidence/src/service.py` (modify process_evidence to call mapping_engine) | Nirmitya |
| S3-5 | Integration tests for end-to-end mapping | Test: upload evidence -> parse -> map to controls -> verify mappings appear with correct coverage types | At least 8 test cases: SOC 2 mapped to SOC 2 TSC; ISO cert mapped to ISO 27001; cross-framework mapping (SOC 2 evidence -> NIST CSF); no-match handling | `services/evidence/tests/test_mapping_integration.py` (new) | Nirmitya |

### File Ownership Table

| File | Owner | Action |
|------|-------|--------|
| `services/ai/src/prompts.py` | Nirmitya | MODIFY |
| `services/evidence/src/mapping_engine.py` | Nirmitya | CREATE |
| `services/evidence/src/service.py` | Nirmitya | MODIFY |
| `services/framework/src/router.py` | Nirmitya | MODIFY |
| `services/framework/src/service.py` | Nirmitya | MODIFY |
| `services/evidence/tests/test_mapping_integration.py` | Nirmitya | CREATE |

### Dependencies
- **Hard**: Sprint 1 (Claude client), Sprint 2 (real extractions)
- **Hard**: Framework service must have clauses seeded in DB

### Risk Register
| Risk | Impact | Mitigation |
|------|--------|------------|
| Claude mapping accuracy below 70% | Poor user trust | Include confidence threshold; below 0.6 = flagged for human review |
| Framework clause volume too large for single prompt | Token limit exceeded | Batch clauses into groups of 50; parallel Claude calls |
| Cross-service HTTP calls add latency | Slow mapping | Cache framework clauses in Redis; async mapping after parsing |

---

## Sprint 4: SSO/SAML/OIDC Enterprise Authentication

**Goal**: Add enterprise SSO support. Organizations can configure Okta, Azure AD, or Google Workspace for SAML 2.0 / OIDC login alongside existing email/password.

**Prerequisite**: Sprint 1 complete (for consistent async client patterns). `SAML_CERT_PATH` and OIDC provider configs in `.env`.

**Parallelism (F3)**: S4 is independent of the evidence chain (S2, S3). It CAN and SHOULD execute in parallel with S2 after S1 completes. The critical path to the vendor portal (S6a) runs through S4+S5, so starting S4 early is essential.

### Stories

| ID | Title | Description | Acceptance Criteria | Files to Modify/Create | Assigned |
|----|-------|-------------|--------------------|-----------------------|----------|
| S4-0 | Initialize alembic in auth service | Set up alembic migration infrastructure for the auth service if not already initialized. Create `alembic.ini`, `alembic/env.py`, `alembic/versions/` directory. | `alembic init` succeeds; `alembic revision --autogenerate` works against auth service models; `alembic upgrade head` runs without error | `services/auth/alembic.ini` (new or verify), `services/auth/alembic/` (new or verify), `services/auth/alembic/env.py` (new or verify) | Nirmitya |
| S4-1 | Add SSO dependencies | Add `python3-saml`, `authlib` (OIDC), `pyjwt` to auth service | Packages install; imports succeed | `services/auth/pyproject.toml` | Nirmitya |
| S4-2 | SSO provider configuration model | DB model for tenant SSO configs: provider type (saml/oidc), metadata URL, client ID/secret, attribute mappings | Migration creates `sso_configurations` table; CRUD endpoints for admin to configure SSO per tenant | `services/auth/src/models.py` (modify), `services/auth/alembic/versions/` (new migration) | Nirmitya |
| S4-3 | SAML 2.0 SP implementation | Service Provider that handles SAML AuthnRequest generation and Response validation | `GET /auth/sso/saml/login?tenant_id=X` redirects to IdP; `POST /auth/sso/saml/acs` processes SAML response; creates/updates user from SAML attributes; returns JWT tokens | `services/auth/src/sso/__init__.py` (new), `services/auth/src/sso/saml_provider.py` (new), `services/auth/src/router.py` (modify) | Nirmitya |
| S4-4 | OIDC provider implementation | Generic OIDC flow for Azure AD, Google Workspace, Okta | `GET /auth/sso/oidc/login?tenant_id=X` redirects to authorization endpoint; `GET /auth/sso/oidc/callback` exchanges code for tokens; validates ID token; creates/updates user; returns JWT tokens | `services/auth/src/sso/oidc_provider.py` (new), `services/auth/src/router.py` (modify) | Nirmitya |
| S4-5 | JIT user provisioning + attribute mapping | On first SSO login, auto-create user with role derived from IdP group claims. On subsequent logins, update attributes. | New SSO user gets created with correct tenant_id, email, name; role mapped from IdP groups via configurable mapping; existing user attributes updated on login | `services/auth/src/sso/provisioning.py` (new), `services/auth/src/service.py` (modify) | Nirmitya |
| S4-6 | SSO integration tests | Test SAML and OIDC flows with mock IdPs | At least 10 test cases: SAML happy path, SAML invalid signature, OIDC happy path, OIDC expired token, JIT create, JIT update, tenant without SSO falls back to password, invalid tenant | `services/auth/tests/test_sso_integration.py` (new) | Nirmitya |

### File Ownership Table

| File | Owner | Action |
|------|-------|--------|
| `services/auth/alembic.ini` | Nirmitya | CREATE or VERIFY |
| `services/auth/alembic/env.py` | Nirmitya | CREATE or VERIFY |
| `services/auth/pyproject.toml` | Nirmitya | MODIFY |
| `services/auth/src/models.py` | Nirmitya | MODIFY |
| `services/auth/alembic/versions/` | Nirmitya | CREATE (migration) |
| `services/auth/src/sso/__init__.py` | Nirmitya | CREATE |
| `services/auth/src/sso/saml_provider.py` | Nirmitya | CREATE |
| `services/auth/src/sso/oidc_provider.py` | Nirmitya | CREATE |
| `services/auth/src/sso/provisioning.py` | Nirmitya | CREATE |
| `services/auth/src/router.py` | Nirmitya | MODIFY |
| `services/auth/src/service.py` | Nirmitya | MODIFY |
| `services/auth/tests/test_sso_integration.py` | Nirmitya | CREATE |

### Dependencies
- **Hard**: Sprint 1 complete (async client pattern)
- **Hard**: Can run in parallel with S2 (no dependency on evidence chain)
- **Soft**: Should complete before Sprint 5 (vendor portal needs SSO for vendor users)

### Risk Register
| Risk | Impact | Mitigation |
|------|--------|------------|
| SAML XML signature validation edge cases | Security vulnerability | Use well-tested `python3-saml` library; strict signature validation; reject unsigned assertions |
| IdP metadata URL unreachable | SSO login fails | Cache metadata locally; refresh every 24h; fallback to cached on failure |
| Attribute mapping mismatch across IdPs | Wrong role assignments | Admin-configurable attribute mapping per SSO config; default mappings for Okta/Azure/Google |
| Session fixation during SSO flow | Security vulnerability | Generate fresh session on SSO callback; validate state parameter; CSRF protection |

---

## Sprint 5: Assessment Distribution + SLA + Real Email

**Goal**: Send assessments to vendors with deadlines. Automated SLA tracking with reminders at Day 7/14/21. Real email delivery via SendGrid/SES.

**Prerequisite**: Sprint 3 (evidence mapping complete) + Sprint 4 (SSO for vendor user accounts). `SENDGRID_API_KEY` or `SES_*` credentials in `.env`.

**Inter-service communication (F4)**: Assessment service calls Communication service via `httpx.AsyncClient` at `http://communication-service:8000/api/v1/communications/...` to send emails and create notifications. See "Inter-Service Communication Pattern" section above.

### Stories

| ID | Title | Description | Acceptance Criteria | Files to Modify/Create | Assigned |
|----|-------|-------------|--------------------|-----------------------|----------|
| S5-0 | Initialize alembic in assessment service | Set up alembic migration infrastructure for the assessment service if not already initialized. Create `alembic.ini`, `alembic/env.py`, `alembic/versions/` directory. | `alembic init` succeeds; `alembic revision --autogenerate` works against assessment service models; `alembic upgrade head` runs without error | `services/assessment/alembic.ini` (new or verify), `services/assessment/alembic/` (new or verify), `services/assessment/alembic/env.py` (new or verify) | Nirmitya |
| S5-1 | Assessment distribution endpoint | `POST /api/v1/assessments/{id}/distribute` sets status to `distributed`, records distribution timestamp, sets due_date based on SLA config | Assessment status changes to `distributed`; `distributed_at` and `due_date` set; returns updated assessment | `services/assessment/src/router.py` (modify), `services/assessment/src/service.py` (modify), `services/assessment/src/models.py` (modify -- add distributed_at, due_date columns) | Nirmitya |
| S5-2 | SLA configuration model | Admin-configurable SLA per tier: default deadline days, reminder schedule, escalation rules | Migration creates `sla_configurations` table; CRUD endpoints for admin; default configs seeded: Tier 1 = 14 days, Tier 2 = 21 days, Tier 3 = 30 days | `services/assessment/src/models.py` (modify), `services/assessment/alembic/versions/` (new migration), `services/assessment/src/schemas.py` (modify), `services/assessment/src/router.py` (modify) | Nirmitya |
| S5-3 | Real email sending via SendGrid | Replace in-app-only notifications with actual email delivery for assessment distribution and reminders | `CommunicationsService.send_email()` sends via SendGrid API; delivery status tracked in `communication_logs`; templates rendered with Jinja2; HTML emails with Velora branding | `services/communication/src/email_sender.py` (new), `services/communication/src/service.py` (modify -- add send_email method), `services/communication/pyproject.toml` (modify -- add sendgrid) | Nirmitya |
| S5-4 | Email templates for assessment lifecycle | Create branded HTML email templates: assessment_distributed, reminder_day_7, reminder_day_14, reminder_day_21, overdue_escalation | 5 email templates created in DB seed; each renders correctly with vendor name, assessment title, due date, action URL; responsive HTML | `services/communication/src/templates/` (new directory with .html files), `services/communication/src/seed.py` (modify or create) | Nirmitya |
| S5-5 | SLA timer + automated reminders | Background task (Redis BullMQ or cron) that checks distributed assessments daily: sends reminders at configured intervals, escalates overdue | Daily job runs; identifies assessments approaching/past due date; sends appropriate reminder email via `httpx` call to communication service; creates notification; logs in communication_logs | `services/assessment/src/sla_tracker.py` (new), `services/assessment/src/main.py` (modify -- register background task) | Nirmitya |
| S5-6 | Distribution triggers notification chain | When assessment is distributed: create in-app notification for vendor user + send email + log in communication_logs. Assessment service calls communication service via `httpx.AsyncClient` at `http://communication-service:8000`. | Distribution creates records in 3 places: notifications table, communication_logs, and sends real email; all traceable by assessment_id | `services/assessment/src/service.py` (modify distribute method to call communication service) | Nirmitya |
| S5-7 | Integration tests for distribution + email | Test full distribution flow including email sending (mocked SendGrid in tests) | At least 10 test cases: distribute happy path, SLA calculation, reminder scheduling, overdue detection, email template rendering, SendGrid failure handling | `services/assessment/tests/test_distribution_integration.py` (new), `services/communication/tests/test_email_integration.py` (new) | Nirmitya |

### File Ownership Table

| File | Owner | Action |
|------|-------|--------|
| `services/assessment/alembic.ini` | Nirmitya | CREATE or VERIFY |
| `services/assessment/alembic/env.py` | Nirmitya | CREATE or VERIFY |
| `services/assessment/src/models.py` | Nirmitya | MODIFY |
| `services/assessment/src/service.py` | Nirmitya | MODIFY |
| `services/assessment/src/router.py` | Nirmitya | MODIFY |
| `services/assessment/src/schemas.py` | Nirmitya | MODIFY |
| `services/assessment/src/sla_tracker.py` | Nirmitya | CREATE |
| `services/assessment/src/main.py` | Nirmitya | MODIFY |
| `services/assessment/alembic/versions/` | Nirmitya | CREATE (migration) |
| `services/communication/src/email_sender.py` | Nirmitya | CREATE |
| `services/communication/src/service.py` | Nirmitya | MODIFY |
| `services/communication/src/templates/` | Nirmitya | CREATE |
| `services/communication/src/seed.py` | Nirmitya | CREATE |
| `services/communication/pyproject.toml` | Nirmitya | MODIFY |
| `services/assessment/tests/test_distribution_integration.py` | Nirmitya | CREATE |
| `services/communication/tests/test_email_integration.py` | Nirmitya | CREATE |

### Dependencies
- **Hard**: Sprint 3 (evidence mapping complete) + Sprint 4 (SSO for vendor user creation)
- **Hard**: SendGrid API key or SES credentials
- **Soft**: Sprint 1 (AI service pattern for external API wrappers)

### Risk Register
| Risk | Impact | Mitigation |
|------|--------|------------|
| SendGrid API key not provisioned | No emails sent | Fallback to console logging in dev; real SendGrid in staging/prod |
| Email deliverability issues (spam folder) | Vendors don't see assessments | SPF/DKIM/DMARC configuration; SendGrid dedicated IP for production |
| SLA timer drift in container restarts | Missed reminders | Persist reminder state in DB; check on startup; idempotent reminder sending |
| Background task failure undetected | Silent SLA violations | Health check endpoint for SLA tracker; log every run; alert on failure |

---

## Sprint 6a: Vendor Portal -- Scaffold + Auth + BFF + Dashboard (F1)

**Goal**: Stand up the vendor portal foundation: Next.js app scaffold with white-label theming, vendor authentication via magic link + SSO, BFF portal routes, and vendor dashboard.

**Prerequisite**: Sprint 4 (SSO), Sprint 5 (assessment distribution).

**Inter-service communication (F4)**: BFF calls Auth, Assessment, Evidence, and Findings services via `httpx.AsyncClient` using Docker DNS hostnames. Vendor portal frontend calls ONLY the BFF -- never microservices directly. See "Inter-Service Communication Pattern" section above.

### Stories

| ID | Title | Description | Acceptance Criteria | Files to Modify/Create | Assigned |
|----|-------|-------------|--------------------|-----------------------|----------|
| S6a-1 | Vendor portal Next.js app scaffold | New Next.js app (or route group under `/portal`) with white-label theming support (tenant logo, colors from config) | App builds; renders login page; supports tenant-specific branding via config; mobile-responsive layout | `frontend/web/src/app/portal/layout.tsx` (new), `frontend/web/src/app/portal/page.tsx` (new), `frontend/web/src/app/portal/login/page.tsx` (new) | Drishyon |
| S6a-2 | Vendor auth: magic link + SSO | Vendor users authenticate via magic link (emailed token) or SSO. No password required for vendor users. | `POST /auth/vendor/magic-link` sends login email with one-time token; `GET /auth/vendor/verify?token=X` validates and returns JWT; SSO flow from Sprint 4 also works for vendor users | `services/auth/src/router.py` (modify), `services/auth/src/service.py` (modify -- add magic link methods) | Nirmitya |
| S6a-3 | Vendor portal BFF endpoints | BFF routes for vendor context: my assessments, my evidence, my findings. Scoped to vendor_id from JWT. | `GET /api/portal/assessments` returns assessments assigned to logged-in vendor; `GET /api/portal/assessments/{id}` returns assessment with questions; `POST /api/portal/assessments/{id}/respond` submits responses. BFF calls downstream services via `httpx.AsyncClient` at Docker DNS hostnames. | `services/bff/src/router.py` (modify -- add portal routes), `services/bff/src/portal_routes.py` (new) | Nirmitya |
| S6a-4 | Vendor portal dashboard | Landing page showing: assigned assessments count, overdue count, evidence requests, recent activity | Dashboard renders with real data from BFF; cards with counts; recent activity timeline; action items highlighted | `frontend/web/src/app/portal/dashboard/page.tsx` (new) | Drishyon |

### File Ownership Table

| File | Owner | Action |
|------|-------|--------|
| `frontend/web/src/app/portal/layout.tsx` | Drishyon | CREATE |
| `frontend/web/src/app/portal/page.tsx` | Drishyon | CREATE |
| `frontend/web/src/app/portal/login/page.tsx` | Drishyon | CREATE |
| `frontend/web/src/app/portal/dashboard/page.tsx` | Drishyon | CREATE |
| `services/bff/src/portal_routes.py` | Nirmitya | CREATE |
| `services/bff/src/router.py` | Nirmitya | MODIFY |
| `services/auth/src/router.py` | Nirmitya | MODIFY |
| `services/auth/src/service.py` | Nirmitya | MODIFY |

### Dependencies
- **Hard**: Sprint 4 (SSO/auth for vendor users), Sprint 5 (assessment distribution)
- **Hard**: BFF service must proxy all portal API calls (vendor portal never calls microservices directly)

### Risk Register
| Risk | Impact | Mitigation |
|------|--------|------------|
| White-label theming complexity | Delayed delivery | Start with single theme; make theming config-driven for later extension |
| Magic link email deliverability | Vendors can't log in | Same SendGrid infrastructure as Sprint 5; fallback to SSO |

---

## Sprint 6b: Vendor Portal -- Assessment UI + Evidence + Findings + Integration Tests (F1)

**Goal**: Build the interactive vendor experience: assessment completion UI (all question types), evidence upload from portal, findings view with acknowledge, and full integration tests for the vendor journey.

**Prerequisite**: Sprint 6a (scaffold, auth, BFF, dashboard all in place).

### Stories

| ID | Title | Description | Acceptance Criteria | Files to Modify/Create | Assigned |
|----|-------|-------------|--------------------|-----------------------|----------|
| S6b-1 | Assessment completion UI | Vendor sees assigned assessment, answers questions (supports all question types: yes/no, single select, multi select, open text, numeric, date, file upload), saves progress, submits | All question types render correctly; progress saved on blur/navigation; submit validates required fields; shows completion percentage | `frontend/web/src/app/portal/assessments/[id]/page.tsx` (new), `frontend/web/src/components/portal/` (new directory) | Drishyon |
| S6b-2 | Evidence upload from portal | Vendor uploads evidence documents directly from portal. Files go to MinIO; evidence record created in evidence service. | Upload component with drag-and-drop; file type validation; progress indicator; uploaded files appear in evidence list; links to assessment | `frontend/web/src/app/portal/evidence/page.tsx` (new), `frontend/web/src/components/portal/evidence-upload.tsx` (new) | Drishyon |
| S6b-3 | Findings view for vendor | Vendor sees findings raised against them with severity, description, remediation guidance. Can acknowledge findings. | Findings list with severity badges; detail view with remediation steps; acknowledge button changes finding status; timeline of interactions | `frontend/web/src/app/portal/findings/page.tsx` (new), `frontend/web/src/app/portal/findings/[id]/page.tsx` (new) | Drishyon |
| S6b-4 | Integration tests for full vendor portal journey | End-to-end: vendor logs in -> views dashboard -> views assessment -> answers questions -> uploads evidence -> views findings -> acknowledges finding -> submits | At least 8 test cases covering full vendor journey; BFF endpoint tests; magic link auth flow test | `services/bff/tests/test_portal_integration.py` (new), `frontend/web/src/app/portal/__tests__/` (new) | Nirmitya (BFF) + Drishyon (FE) |

### File Ownership Table

| File | Owner | Action |
|------|-------|--------|
| `frontend/web/src/app/portal/assessments/[id]/page.tsx` | Drishyon | CREATE |
| `frontend/web/src/components/portal/` | Drishyon | CREATE |
| `frontend/web/src/app/portal/evidence/page.tsx` | Drishyon | CREATE |
| `frontend/web/src/components/portal/evidence-upload.tsx` | Drishyon | CREATE |
| `frontend/web/src/app/portal/findings/page.tsx` | Drishyon | CREATE |
| `frontend/web/src/app/portal/findings/[id]/page.tsx` | Drishyon | CREATE |
| `services/bff/tests/test_portal_integration.py` | Nirmitya | CREATE |
| `frontend/web/src/app/portal/__tests__/` | Drishyon | CREATE |

### Dependencies
- **Hard**: Sprint 6a (scaffold, auth, BFF routes, dashboard)
- **Soft**: Sprint 2 (evidence upload with MinIO)

### Risk Register
| Risk | Impact | Mitigation |
|------|--------|------------|
| Question type rendering bugs | Incomplete assessments | Test each question type individually; component library approach |
| Portal performance with large assessments | Bad UX | Paginate questions by section; lazy load sections; virtual scrolling |
| Evidence upload failures | Vendor frustration | Retry logic; progress indicator; resume-able uploads for large files |

---

## Sprint 7: External Rating API + Alert Correlation Engine

**Goal**: Integrate SecurityScorecard (or BitSight) for real monitoring signals. Build alert correlation engine that auto-prioritizes, deduplicates, and correlates alerts.

**Prerequisite**: `SECURITYSCORECARD_API_KEY` in `.env`. Sprint 6b complete.

**Inter-service communication (F4)**: Monitoring service calls Scoring service via `httpx.AsyncClient` at `http://scoring-service:8000/api/v1/scoring/...` to trigger score re-calculation when external ratings change. See "Inter-Service Communication Pattern" section above.

### Stories

| ID | Title | Description | Acceptance Criteria | Files to Modify/Create | Assigned |
|----|-------|-------------|--------------------|-----------------------|----------|
| S7-1 | SecurityScorecard API client | Async client for SecurityScorecard: company lookup, score retrieval, factor details, alert webhooks | Client authenticates with API key; retrieves company by domain; returns overall score + factor scores; handles rate limits; logs all calls. Uses `httpx.AsyncClient` with standard timeout/retry config. | `services/monitoring/src/external/__init__.py` (new), `services/monitoring/src/external/securityscorecard.py` (new), `services/monitoring/pyproject.toml` (modify -- add httpx) | Nirmitya |
| S7-2 | Signal ingestion pipeline | Ingest signals from SecurityScorecard into `monitoring_signals` table. Scheduled polling (every 6h) + webhook receiver. | `POST /api/v1/monitoring/signals/ingest` accepts external signals; scheduled job polls SecurityScorecard for score changes; new signals persisted with source, vendor_id, signal_type, raw_data | `services/monitoring/src/signal_ingest.py` (new), `services/monitoring/src/router.py` (modify -- add ingest endpoint + webhook), `services/monitoring/src/main.py` (modify -- register polling job) | Nirmitya |
| S7-3 | Alert correlation engine | Engine that processes new signals: assigns priority (P0-P4), deduplicates within 24h window, correlates multiple signals for same vendor within 48h | `CorrelationEngine.process_signal()` returns: new alert, deduplicated (existing alert updated), or correlated (existing alert priority escalated); dedup key = vendor_id + signal_type + 24h window; correlation = 2+ different signal types within 48h | `services/monitoring/src/correlation_engine.py` (new) | Nirmitya |
| S7-4 | Auto-priority assignment | Priority rules: P0 = active breach/data leak, P1 = score drop >15 pts, P2 = new critical vulnerability, P3 = score drop 5-15 pts, P4 = informational | Each signal type has a priority mapping; priority can escalate (never downgrade) during correlation; rules are configurable in `alert_rules` table | `services/monitoring/src/priority_rules.py` (new) | Nirmitya |
| S7-5 | Update vendor scores from external ratings | When SecurityScorecard score changes, update `vendor.external_rating_score` and trigger re-scoring. Monitoring service calls Scoring service via `httpx.AsyncClient` at `http://scoring-service:8000/api/v1/scoring/recalculate`. | Vendor score updated; scoring engine re-calculates composite score; score history entry created; alert created if score dropped | `services/monitoring/src/service.py` (modify), `services/scoring/src/service.py` (modify -- add trigger endpoint) | Nirmitya |
| S7-6 | Integration tests for monitoring pipeline | Test: signal ingest -> correlation -> alert creation -> vendor score update | At least 10 test cases: new signal creates alert, duplicate signal deduplicates, correlated signals escalate, score drop triggers re-score, webhook validation | `services/monitoring/tests/test_correlation_integration.py` (new) | Nirmitya |

### File Ownership Table

| File | Owner | Action |
|------|-------|--------|
| `services/monitoring/src/external/__init__.py` | Nirmitya | CREATE |
| `services/monitoring/src/external/securityscorecard.py` | Nirmitya | CREATE |
| `services/monitoring/src/signal_ingest.py` | Nirmitya | CREATE |
| `services/monitoring/src/correlation_engine.py` | Nirmitya | CREATE |
| `services/monitoring/src/priority_rules.py` | Nirmitya | CREATE |
| `services/monitoring/src/router.py` | Nirmitya | MODIFY |
| `services/monitoring/src/service.py` | Nirmitya | MODIFY |
| `services/monitoring/src/main.py` | Nirmitya | MODIFY |
| `services/monitoring/pyproject.toml` | Nirmitya | MODIFY |
| `services/scoring/src/service.py` | Nirmitya | MODIFY |
| `services/monitoring/tests/test_correlation_integration.py` | Nirmitya | CREATE |

### Dependencies
- **Hard**: SecurityScorecard API key
- **Soft**: Sprint 1 (pattern for external API wrappers)

### Risk Register
| Risk | Impact | Mitigation |
|------|--------|------------|
| SecurityScorecard API rate limits | Missed score changes | 6h polling interval; cache responses; respect rate limit headers |
| SecurityScorecard API unavailable | No external signals | Graceful degradation; system works without external ratings; retry with backoff |
| Alert flood from initial sync | Overwhelming users | First sync creates signals but suppresses alerts older than 7 days; only recent changes generate alerts |
| Correlation window too narrow/wide | Missed correlations or false positives | Configurable windows in alert_rules; start with 24h dedup / 48h correlate; tunable per tenant |

---

## Sprint 8: Temporal Workflows -- Real Orchestration

**Goal**: Wire up the existing Temporal workflow definitions with real service calls. Vendor onboarding, assessment lifecycle, evidence processing, and remediation tracking become durable workflows.

**Prerequisite**: Sprints 1-7 complete (all services have real endpoints). Temporal server running in docker-compose.

**Inter-service communication (F4)**: Temporal activities call service endpoints via `httpx.AsyncClient` using Docker DNS hostnames. Each activity is an HTTP call to a specific service endpoint. See "Inter-Service Communication Pattern" section above.

### Stories

| ID | Title | Description | Acceptance Criteria | Files to Modify/Create | Assigned |
|----|-------|-------------|--------------------|-----------------------|----------|
| S8-1 | Verify Temporal server in docker-compose | Ensure Temporal server + UI are in docker-compose and accessible | `docker compose up` includes temporal server; Temporal UI accessible at localhost:8233; worker can connect | `docker-compose.yml` (modify -- verify temporal config) | Prasaron |
| S8-2 | Wire vendor onboarding workflow | Connect VendorOnboardingWorkflow activities to real service endpoints. Test full flow: create vendor -> enrich -> calculate tier -> notify. All activities use `httpx.AsyncClient` to call service endpoints via Docker DNS. | Workflow completes end-to-end; vendor created in DB; enrichment attempted (graceful failure OK for now); tier calculated; notification sent via communication service | `services/workflow/src/activities/service_calls.py` (verify/fix URLs), `services/workflow/src/worker.py` (modify -- register all activities) | Prasaron |
| S8-3 | Wire assessment lifecycle workflow | AssessmentLifecycleWorkflow: create -> distribute -> wait for submission -> score -> generate findings -> notify. Activities call assessment, scoring, communication services via `httpx.AsyncClient`. | Workflow handles full lifecycle; SLA timer integrated; reminders sent at configured intervals; overdue escalation works; completion triggers scoring | `services/workflow/src/workflows/assessment_lifecycle.py` (modify), `services/workflow/src/activities/service_calls.py` (modify) | Prasaron |
| S8-4 | Wire evidence processing workflow | EvidenceProcessingWorkflow: upload -> classify -> parse -> map to controls -> notify for review. Activities call evidence, ai, framework services via `httpx.AsyncClient`. | Workflow handles document processing pipeline; classification via AI service; parsing via evidence service; mapping via evidence mapping engine; review notification sent | `services/workflow/src/workflows/evidence_processing.py` (modify), `services/workflow/src/activities/service_calls.py` (modify) | Prasaron |
| S8-5 | Workflow integration tests | Test each workflow end-to-end with real services (or service-level mocks) | At least 6 test cases: onboarding happy path, assessment lifecycle happy path, evidence processing happy path, workflow retry on service failure, workflow timeout handling, concurrent workflow execution | `services/workflow/tests/test_workflow_integration.py` (new) | Prasaron |

### File Ownership Table

| File | Owner | Action |
|------|-------|--------|
| `docker-compose.yml` | Prasaron | MODIFY |
| `services/workflow/src/worker.py` | Prasaron | MODIFY |
| `services/workflow/src/workflows/assessment_lifecycle.py` | Prasaron | MODIFY |
| `services/workflow/src/workflows/evidence_processing.py` | Prasaron | MODIFY |
| `services/workflow/src/activities/service_calls.py` | Prasaron | MODIFY |
| `services/workflow/tests/test_workflow_integration.py` | Prasaron | CREATE |

### Dependencies
- **Hard**: Sprints 1-7 (all service endpoints must be real)
- **Hard**: Temporal server running

### Risk Register
| Risk | Impact | Mitigation |
|------|--------|------------|
| Temporal worker can't connect to services | Workflows fail | Verify all service URLs in docker network; health check activities |
| Long-running workflows exceed session timeout | Incomplete orchestration | Temporal handles this natively; heartbeat activities; continue-as-new for very long workflows |
| Activity retries cause duplicate side effects | Double emails, duplicate records | Idempotency keys on all activity calls; communication service deduplicates by idempotency_key |
| Workflow versioning needed for future changes | Breaking existing workflows | Use Temporal versioning API from start; version all workflow definitions |

---

## Sprint 9: FAIR Quantification + Cross-Framework Mapping

**Goal**: Implement FAIR (Factor Analysis of Information Risk) quantification in scoring engine. Build real cross-framework mapping engine with confidence scores.

**Prerequisite**: Sprint 7 (external ratings flowing), Sprint 3 (evidence mapping pattern)

### Stories

| ID | Title | Description | Acceptance Criteria | Files to Modify/Create | Assigned |
|----|-------|-------------|--------------------|-----------------------|----------|
| S9-0 | Initialize alembic in scoring service | Set up alembic migration infrastructure for the scoring service if not already initialized. Create `alembic.ini`, `alembic/env.py`, `alembic/versions/` directory. | `alembic init` succeeds; `alembic revision --autogenerate` works against scoring service models; `alembic upgrade head` runs without error | `services/scoring/alembic.ini` (new or verify), `services/scoring/alembic/` (new or verify), `services/scoring/alembic/env.py` (new or verify) | Nirmitya |
| S9-1 | FAIR model data structures | Add FAIR-specific models: Loss Event Frequency (TEF, Vulnerability, TCAP), Loss Magnitude (Primary/Secondary loss), Monte Carlo parameters | Migration adds `fair_analyses` table with all FAIR taxonomy fields; Pydantic schemas for input/output; supports single vendor or portfolio-level analysis | `services/scoring/src/models.py` (modify), `services/scoring/alembic/versions/` (new migration), `services/scoring/src/schemas.py` (modify) | Nirmitya |
| S9-2 | FAIR calculation engine | Implement FAIR: TEF x Vulnerability = LEF; Primary Loss + Secondary Loss = Loss Magnitude; LEF x LM = ALE. Monte Carlo simulation with configurable iterations (default 10,000). | Engine accepts FAIR input parameters; runs Monte Carlo simulation; returns ALE distribution (min, max, mean, P10, P50, P90); execution time < 5s for 10K iterations | `services/scoring/src/fair_engine.py` (new) | Nirmitya |
| S9-3 | FAIR API endpoints | CRUD for FAIR analyses + calculation endpoint + portfolio aggregation | `POST /api/v1/scoring/fair/analyze` runs FAIR for a vendor; `GET /api/v1/scoring/fair/portfolio` aggregates across all vendors; results include dollar amounts and confidence intervals | `services/scoring/src/router.py` (modify), `services/scoring/src/service.py` (modify) | Nirmitya |
| S9-4 | Cross-framework mapping engine | Build engine that maps controls between frameworks (e.g., SOC 2 CC6.1 <-> ISO 27001 A.9.1 <-> NIST CSF PR.AC) with confidence scores and mapping types (equivalent/partial/related) | Engine loads all framework clauses; uses semantic similarity (embedding comparison) + keyword matching + known mappings for confidence scoring; results stored in `control_mappings` table | `services/framework/src/mapping_engine.py` (new) | Nirmitya |
| S9-5 | Pre-computed mapping seed data | Seed known mappings: SOC 2 TSC <-> ISO 27001:2022 <-> NIST CSF 2.0 <-> PCI DSS 4.0 (at least 50 high-confidence mappings) | Seed script populates `control_mappings` with known mappings; each mapping has type, confidence, and source reference; at least 50 mappings across 4 frameworks | `services/framework/src/seed_mappings.py` (new) | Nirmitya |
| S9-6 | Integration tests for FAIR + mapping | Test FAIR calculation accuracy and cross-framework mapping correctness | At least 10 test cases: FAIR with known inputs produces expected ALE range; Monte Carlo convergence; cross-framework mapping accuracy for known pairs; portfolio aggregation | `services/scoring/tests/test_fair_integration.py` (new), `services/framework/tests/test_mapping_integration.py` (new) | Nirmitya |

### File Ownership Table

| File | Owner | Action |
|------|-------|--------|
| `services/scoring/alembic.ini` | Nirmitya | CREATE or VERIFY |
| `services/scoring/alembic/env.py` | Nirmitya | CREATE or VERIFY |
| `services/scoring/src/models.py` | Nirmitya | MODIFY |
| `services/scoring/src/schemas.py` | Nirmitya | MODIFY |
| `services/scoring/alembic/versions/` | Nirmitya | CREATE (migration) |
| `services/scoring/src/fair_engine.py` | Nirmitya | CREATE |
| `services/scoring/src/router.py` | Nirmitya | MODIFY |
| `services/scoring/src/service.py` | Nirmitya | MODIFY |
| `services/framework/src/mapping_engine.py` | Nirmitya | CREATE |
| `services/framework/src/seed_mappings.py` | Nirmitya | CREATE |
| `services/scoring/tests/test_fair_integration.py` | Nirmitya | CREATE |
| `services/framework/tests/test_mapping_integration.py` | Nirmitya | CREATE |

### Dependencies
- **Hard**: Sprint 7 (external rating scores for FAIR inputs)
- **Hard**: Framework service must have clause data seeded
- **Soft**: Sprint 3 (evidence-to-control mapping pattern reusable)

### Risk Register
| Risk | Impact | Mitigation |
|------|--------|------------|
| FAIR Monte Carlo performance | Slow calculations | NumPy vectorized operations; 10K iterations as default; configurable per analysis |
| FAIR parameter estimation difficult | Garbage-in-garbage-out | Provide sensible defaults based on vendor tier + industry; allow manual override |
| Cross-framework mapping accuracy | False mappings mislead users | Seed known mappings as ground truth; AI-generated mappings marked as "suggested"; human verification workflow |
| Embedding model for semantic similarity | Additional dependency | Use pre-computed embeddings stored in pgvector; generate offline; update monthly |

---

## Sprint 10: Board-Ready Reports

**Goal**: Generate PDF and PPTX reports with AI-written executive narratives, risk heatmaps, FAIR financial exposure charts, and portfolio summaries. Upgrade from basic report templates to board-presentation quality.

**Prerequisite**: Sprints 1, 7, 9 (AI narratives, external ratings, FAIR data all flowing)

### Stories

| ID | Title | Description | Acceptance Criteria | Files to Modify/Create | Assigned |
|----|-------|-------------|--------------------|-----------------------|----------|
| S10-1 | Add report generation dependencies | Add `weasyprint` (PDF), `python-pptx` (PPTX), `matplotlib`/`plotly` (charts) to reporting service | All packages install; imports succeed; weasyprint generates PDF from HTML | `services/reporting/pyproject.toml` (modify) | Nirmitya |
| S10-2 | PDF report generator | Generate branded PDF reports from HTML templates using weasyprint. Include: cover page, executive summary, risk heatmap, vendor detail pages, FAIR analysis, appendices. | `POST /api/v1/reports/generate` with `format=pdf` returns downloadable PDF; cover page has tenant logo + report title + date; heatmap renders correctly; at least 3 report templates (executive summary, vendor deep-dive, portfolio risk) | `services/reporting/src/generators/__init__.py` (new), `services/reporting/src/generators/pdf_generator.py` (new), `services/reporting/src/templates/` (new -- HTML/CSS templates) | Nirmitya |
| S10-3 | PPTX report generator | Generate PowerPoint presentations for board meetings. Slides: title, executive summary, risk heatmap, top-10 vendors, FAIR exposure, recommendations. | `format=pptx` returns downloadable .pptx; at least 8 slide types; charts embedded as images; branded with tenant colors; editable text (not images) | `services/reporting/src/generators/pptx_generator.py` (new) | Nirmitya |
| S10-4 | AI narrative generation | Use Claude to generate executive narratives: "Your portfolio risk increased 12% this quarter, driven by..." Contextual, data-backed, non-generic. | Narratives are specific to tenant's data; reference actual vendor names, score changes, finding counts; tone is board-appropriate; generated fresh per report (not cached stale) | `services/reporting/src/narrative_engine.py` (new), `services/ai/src/prompts.py` (modify -- add report narrative prompts) | Nirmitya |
| S10-5 | Chart/heatmap generation | Generate: risk heatmap (likelihood x impact grid), score trend line charts, FAIR loss exceedance curves, tier distribution pie charts | Charts render as PNG for PDF/PPTX embedding; heatmap color-codes by risk level; trend charts show 6-month history; FAIR curve shows P10/P50/P90 | `services/reporting/src/charts.py` (new) | Nirmitya |
| S10-6 | Integration tests for report generation | Test PDF and PPTX generation with real data | At least 8 test cases: PDF generates without error, PPTX generates, AI narrative included, charts render, empty data handled gracefully, large portfolio (100+ vendors) performance < 30s | `services/reporting/tests/test_report_generation.py` (new) | Nirmitya |

### File Ownership Table

| File | Owner | Action |
|------|-------|--------|
| `services/reporting/pyproject.toml` | Nirmitya | MODIFY |
| `services/reporting/src/generators/__init__.py` | Nirmitya | CREATE |
| `services/reporting/src/generators/pdf_generator.py` | Nirmitya | CREATE |
| `services/reporting/src/generators/pptx_generator.py` | Nirmitya | CREATE |
| `services/reporting/src/narrative_engine.py` | Nirmitya | CREATE |
| `services/reporting/src/charts.py` | Nirmitya | CREATE |
| `services/reporting/src/templates/` | Nirmitya | CREATE |
| `services/reporting/src/router.py` | Nirmitya | MODIFY |
| `services/reporting/src/service.py` | Nirmitya | MODIFY |
| `services/ai/src/prompts.py` | Nirmitya | MODIFY |
| `services/reporting/tests/test_report_generation.py` | Nirmitya | CREATE |

### Dependencies
- **Hard**: Sprint 1 (Claude for narratives), Sprint 9 (FAIR data), Sprint 7 (external ratings)
- **Soft**: All services should be producing real data for meaningful reports

### Risk Register
| Risk | Impact | Mitigation |
|------|--------|------------|
| weasyprint rendering inconsistencies | Ugly PDFs | Test with multiple browsers' rendering; use simple CSS; avoid complex layouts |
| PPTX generation slow for large portfolios | Timeout | Pre-generate charts as images; cache vendor data; paginate large reports |
| AI narratives hallucinate numbers | Misleading board | Pass only verified data to prompt; validate AI output against source data; include data source references |
| Chart library compatibility issues in Docker | Charts fail to render | Use matplotlib with Agg backend (headless); test in Docker specifically |

---

## QA Checklist Skeleton (Stage A -- PRD Alignment for Parikshika)

This checklist is derived from the PRD and must be validated by Parikshika after each sprint.

### Per-Sprint Checklist Items

| # | Check | Sprint(s) | Pass/Fail |
|---|-------|-----------|-----------|
| QA-01 | AI auto-fill produces non-generic, context-aware responses (not keyword matching) | S1 | |
| QA-02 | AI confidence scores correlate with evidence availability (higher when evidence exists) | S1, S3 | |
| QA-03 | SOC 2 Type II report parsed correctly: audit period, opinion type, scope, exceptions extracted | S2 | |
| QA-04 | ISO 27001 certificate parsed: cert number, valid dates, scope, certifying body extracted | S2 | |
| QA-05 | Pen test report parsed: test date, tester, findings by severity extracted | S2 | |
| QA-06 | Evidence-to-control mapping produces coverage_type (full/partial/supportive) with confidence | S3 | |
| QA-07 | Cross-framework mapping: SOC 2 evidence maps to NIST CSF controls where applicable | S3 | |
| QA-08 | SAML 2.0 login works with Okta IdP (or mock) | S4 | |
| QA-09 | OIDC login works with Azure AD (or mock) | S4 | |
| QA-10 | JIT user provisioning creates user with correct role from IdP groups | S4 | |
| QA-11 | Assessment distribution sets status to `distributed` with due_date | S5 | |
| QA-12 | SLA reminders sent at Day 7, 14, 21 (verified via communication_logs) | S5 | |
| QA-13 | Real email sent via SendGrid with correct template rendering | S5 | |
| QA-14 | Vendor portal: scaffold renders, login page works, tenant branding applies | S6a | |
| QA-15 | Vendor portal: vendor can log in via magic link | S6a | |
| QA-16 | Vendor portal: BFF portal routes return vendor-scoped data | S6a | |
| QA-17 | Vendor portal: dashboard shows accurate counts and activity | S6a | |
| QA-18 | Vendor portal: vendor can view and complete assigned assessment | S6b | |
| QA-19 | Vendor portal: all question types render and submit correctly | S6b | |
| QA-20 | Vendor portal: vendor can upload evidence documents | S6b | |
| QA-21 | Vendor portal: vendor can view findings and acknowledge them | S6b | |
| QA-22 | SecurityScorecard signals ingested and stored correctly | S7 | |
| QA-23 | Alert correlation: duplicate signals within 24h deduplicated | S7 | |
| QA-24 | Alert correlation: multiple signal types within 48h escalate priority | S7 | |
| QA-25 | Auto-priority: P0 for breach, P1 for >15pt drop, P2 for critical vuln | S7 | |
| QA-26 | Temporal onboarding workflow completes end-to-end | S8 | |
| QA-27 | Temporal assessment lifecycle handles SLA + reminders durably | S8 | |
| QA-28 | Temporal evidence processing pipeline: upload -> classify -> parse -> map | S8 | |
| QA-29 | FAIR analysis produces ALE with Monte Carlo distribution (P10/P50/P90) | S9 | |
| QA-30 | Cross-framework mapping: known SOC2 <-> ISO27001 pairs mapped correctly | S9 | |
| QA-31 | PDF report generates with cover page, heatmap, executive summary | S10 | |
| QA-32 | PPTX report generates with embedded charts and editable text | S10 | |
| QA-33 | AI narrative references actual vendor data (not generic filler) | S10 | |

### Stage B: Dynamic Scenarios (Samikshon defines per sprint)

Stage B scenarios are generated dynamically by Samikshon based on actual implementation. They test edge cases, error handling, security boundaries, and performance that cannot be predicted from the PRD alone.

---

## Global Risk Register

| # | Risk | Impact | Likelihood | Mitigation | Sprint(s) Affected |
|---|------|--------|------------|------------|-------------------|
| GR-1 | External API keys not provisioned before sprint | Sprint blocked | High | Pre-check all keys in Sprint 0 pre-flight; maintain `.env.example` | S1, S2, S5, S7 |
| GR-2 | Cross-service communication failures in Docker network | Integration failures | Medium | All services use httpx.AsyncClient with 30s timeout, 3-retry backoff, Docker DNS resolution. Health checks on every service. See Inter-Service Communication Pattern section. | S3, S5, S6a, S6b, S7, S8 |
| GR-3 | Database migration conflicts between sprints | Schema corruption | Low | One service modifies its own schema only; alembic per-service (initialized in S4-0, S5-0, S9-0); never cross-service migrations | S4, S5, S9 |
| GR-4 | Token costs exceed expectations with real Claude calls | Budget impact | Medium | Per-tenant token budgets; prompt optimization; batch processing; usage dashboard | S1, S3, S10 |
| GR-5 | Frontend agent overlap with backend changes | Build conflicts | Medium | Drishyon only touches frontend/; Nirmitya only touches services/; BFF is the boundary | S6a, S6b |
| GR-6 | Temporal workflow changes break running instances | Data loss | Low | Workflow versioning from Day 1; never modify running workflow definitions | S8 |
| GR-7 | Alembic not initialized in service before migration needed | Migration fails | High | Explicit alembic setup tasks (S4-0, S5-0, S9-0) run BEFORE any migration task | S4, S5, S9 |
| GR-8 | Test data insufficient for realistic testing | False confidence | Medium | Generate comprehensive seed data in Sprint 0; include edge cases (large vendors, many assessments) | All |

---

## Credential Pre-Flight Checklist

Before any sprint execution begins, these must be verified:

| Credential | Needed By | Status |
|------------|-----------|--------|
| `ANTHROPIC_API_KEY` | Sprint 1 | PENDING |
| `AZURE_DOC_INTELLIGENCE_ENDPOINT` | Sprint 2 | PENDING |
| `AZURE_DOC_INTELLIGENCE_KEY` | Sprint 2 | PENDING |
| `SENDGRID_API_KEY` | Sprint 5 | PENDING |
| `SECURITYSCORECARD_API_KEY` | Sprint 7 | PENDING |
| MinIO running in docker-compose | Sprint 2 | VERIFY |
| Temporal server in docker-compose | Sprint 8 | VERIFY |
| Sample SOC 2 / ISO / pen test PDFs | Sprint 2 | PENDING |

---

## MCA Schedule

| Sprint | Maker | Checker (Code) | Checker (Security) | Approver | Darshika (PRD) | Tantron (CTO) |
|--------|-------|----------------|--------------------|---------|--------------|----|
| S1 | Nirmitya | Samikshon | Rakshon | Rudron | Post-sprint | During |
| S2 | Nirmitya | Samikshon | Rakshon | Rudron | Post-sprint | During |
| S3 | Nirmitya | Samikshon | Rakshon | Rudron | Post-sprint | During |
| S4 | Nirmitya | Samikshon | Rakshon | Rudron | Post-sprint | During |
| S5 | Nirmitya | Samikshon | Rakshon | Rudron | Post-sprint | During |
| S6a | Drishyon + Nirmitya | Samikshon | Rakshon | Rudron | Post-sprint | During |
| S6b | Drishyon + Nirmitya | Samikshon | Rakshon | Rudron | Post-sprint | During |
| S7 | Nirmitya | Samikshon | Rakshon | Rudron | Post-sprint | During |
| S8 | Prasaron | Samikshon | Rakshon | Rudron | Post-sprint | During |
| S9 | Nirmitya | Samikshon | Rakshon | Rudron | Post-sprint | During |
| S10 | Nirmitya | Samikshon | Rakshon | Rudron | Post-sprint | During |

---

## Summary

- **11 sprints** (S6 split into S6a + S6b) covering all 13 P0 features
- **63 stories** total across all sprints (added S4-0, S5-0, S9-0 for alembic setup)
- **Dependency-ordered with parallelism** -- S2 and S4 can run in parallel after S1; critical path: S1->S2->S3->S5->S6a->S6b->S7->S8->S9->S10
- **3 agents**: Nirmitya (primary), Drishyon (frontend), Prasaron (infrastructure)
- **Full MCA** on every sprint: Samikshon + Rakshon -> Rudron
- **Darshika validates** PRD alignment after each sprint
- **Tantron monitors** architecture compliance during each sprint
- **Inter-service communication**: Standardized on async httpx over Docker DNS (documented in dedicated section)
- **Alembic pre-initialized**: Explicit setup tasks before any sprint that needs migrations
- **Estimated timeline**: 11 sessions (1 sprint per session), with S2||S4 parallelism saving 1 session on calendar time

---

*REVISED -- Iteration 2. Addresses Tantron findings F1 (S6 split into S6a/S6b), F2 (alembic init tasks in S4/S5/S9), F3 (S4 parallelized with S2), F4 (inter-service communication pattern documented). Pending re-check by Tantron and approval by Rudron.*
