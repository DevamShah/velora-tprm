# Velora TPRM -- Changelog

All notable changes to this product will be documented in this file.

---

## [2.1.0] -- 2026-03-29

### AI Intelligence Layer (replacing v2.0 mocks)
- **Real Claude API integration** — Anthropic Claude auto-fill with confidence scoring, evidence citations, prompt injection protection (XML delimiters + sanitization), 200-question cap, token tracking, graceful fallback
- **Evidence parsing** — Azure Document Intelligence for SOC 2, ISO 27001, pen test reports with typed extractors; MinIO S3-compatible storage replacing mock URLs
- **Evidence-to-control mapping** — Keyword-based mapping engine with coverage types (full/partial/supportive), confidence scoring, internal service API for cross-service calls
- **FAIR quantification** — Monte Carlo simulation (10K iterations), Annual Loss Expectancy with percentile ranges, data sensitivity multipliers
- **Cross-framework mapping** — Bulk clause retrieval API, keyword matching across framework controls

### Enterprise Authentication
- **SSO/OIDC** — OIDC authorization code flow, JIT (Just-In-Time) user provisioning, User model extended with sso_provider fields
- **SSO endpoints** — /auth/sso/authorize and /auth/sso/callback scaffolded for tenant SSO config

### Vendor Portal
- **Portal frontend** — White-labeled Next.js portal with vendor dashboard, assessments, evidence upload, findings pages
- **Portal BFF routes** — /api/portal/* endpoints with magic link auth, portal session validation
- **Portal navigation** — Separate layout with Velora Vendor Portal branding

### Monitoring & Alerting
- **SecurityScorecard API client** — Async client with retry, score normalization (0-100)
- **Alert correlation engine** — P0-P4 auto-priority classification, 24h deduplication, 48h correlation (3+ P2/P3 escalates to P1)
- **Signal model extensions** — signal_type, signal_data, priority fields on MonitoringSignal and Alert models

### Communications & Distribution
- **Real email via SendGrid** — Template rendering (sandboxed Jinja2), assessment invitations, SLA reminders
- **Assessment distribution** — /distribute-email endpoint with email validation, due date, SLA configuration
- **Email delivery status** — Response distinguishes distributed vs distributed_email_pending

### Reporting
- **Board-ready PDF** — WeasyPrint with branded HTML templates, autoescape enabled
- **Board-ready PPTX** — python-pptx with title, executive summary, metrics, top-10 vendors slides
- **AI narrative engine** — Executive summary generation via Claude API
- **Chart generation** — matplotlib for risk heatmaps, trend charts, FAIR curves

### Quality & Security Hardening
- **Dockerfile security** — All 14 Dockerfiles now run as non-root USER (appuser)
- **Prompt injection protection** — XML delimiter tags, _sanitize() with length caps on all AI prompts
- **Response validation** — Confidence clamping [0.0, 1.0], answer truncation, question_id validation against sent batch
- **Error leakage prevention** — Generic 502 at router level for unhandled AI errors
- **Jinja2 sandboxing** — SandboxedEnvironment in email sender, autoescape in report generator
- **File upload security** — mime_type allowlist, filename sanitization (path traversal prevention), 100MB download cap
- **Import path fix** — Reporting service cross_deps from absolute to relative imports (fixed dashboard 500)

### Code Quality
- **Complexity reduction** — auto_fill_assessment and process_evidence refactored into smaller methods
- **Dead code cleanup** — 15 unused imports/variables removed across 7 services
- **Frontend deduplication** — Shared useCrudList, useCrudDetail, useCrudMutation, useCrudArray hooks
- **Runtime bug fixes** — admin/settings TypeError, vendor-timeline TypeError, audit-log object rendering, portal unescaped entity, review-queue duplicate keys

### Testing Infrastructure
- **Playwright E2E** — 18 smoke tests + 18 interaction tests with headless Chromium
- **48 screenshots** — Every page, tab, search, filter, detail view, sidebar state captured
- **Tool scanning** — Bandit, Semgrep (296 rules), Gitleaks, Trivy, Ruff, ESLint, Radon, Vulture, JSCPD, Madge, Lighthouse, TypeScript strict check
- **Build verification** — next build with 0 errors enforced as gate

### Process & Governance
- 4 process documents (PROC-sprint-plan-mca, PROC-phase8-execution, PROC-phase9-qa, PROC-gate5-release)
- Sprint plan v2.1: 11 sprints, 63 stories, full MCA (Yojika → Tantron → Rudron)
- RCA-VELORA-001: Root cause analysis on testing failures, 5 fixes implemented

---

## [2.0.0] -- 2026-03-28

### Architecture
- Microservices architecture: 14 independent services with Docker Compose orchestration
- OPA (Open Policy Agent) for RBAC + ABAC + tenant isolation (10 Rego policies)
- Temporal.io workflows for long-running processes (vendor onboarding, assessment lifecycle, evidence processing, remediation tracking)
- Redis Streams event bus for inter-service communication with consumer groups
- CQRS materialized read model for dashboard aggregation
- Traefik API Gateway with service routing
- BFF (Backend-for-Frontend) with httpOnly cookie sessions
- Schema-per-service PostgreSQL with Row-Level Security
- Shared library: velora-common (auth, events, OPA client, security, models)

### Backend (14 Services)
- **auth-service**: JWT authentication, bcrypt password hashing, token refresh/revocation, multi-tenant sessions
- **vendor-service**: Full CRUD, bulk CSV import, tier calculation, contact management, 15 seeded demo vendors
- **assessment-engine**: Template-based questionnaires (SIG Core/Lite, Custom), lifecycle state machine (draft-distributed-submitted-reviewed-completed), question cloning, weighted scoring
- **framework-service**: 4 frameworks (SOC 2, ISO 27001, NIST CSF 2.0, HIPAA), 74 clauses, cross-framework mappings, unified control library
- **scoring-engine**: Config-driven multi-dimensional scoring, weighted average/multiplicative methods, portfolio aggregation, score history
- **evidence-service**: Upload with presigned URLs, document classification, AI parsing, control mapping with confidence scores
- **monitoring-service**: Multi-signal ingestion, P0-P4 alert engine, deduplication, vendor timeline, configurable alert rules
- **finding-service**: Severity-based findings, remediation action tracking, lifecycle management
- **communication-hub**: In-app notifications, email templates, communication logs
- **reporting-service**: Executive dashboard aggregation, report generation
- **admin-service**: User management, role management, immutable audit logs, configuration
- **ai-service**: LLM abstraction (Claude/GPT), auto-fill assessments, review queue, usage tracking
- **workflow-service**: Temporal workers with 4 workflows and 18 activities
- **bff-service**: Session management, API aggregation, reverse proxy

### Frontend (25 Routes)
- Premium navy theme (Stripe-inspired #0A2540)
- Executive dashboard with 7 interactive widgets (risk heatmap, donut chart, trend line, top vendors, alert feed, pipeline bar, compliance posture)
- Vendor management: list with filters/sort/pagination, create form, 360-degree detail with tabs (overview, contacts, timeline), bulk import, tier calculation
- Assessment engine: list, 3-step creation wizard, detail with questionnaire workspace, review queue
- Framework browser: card grid, expandable clause tree, cross-framework mapping viewer
- Scoring: score gauge, radar dimension chart, trend line chart, portfolio summary
- Evidence management: list, upload dialog, detail drawer with extractions and control mappings
- Monitoring: alert list with priority badges (P0-P4), detail with action buttons (acknowledge/resolve/suppress), alert rules management
- Findings: list with severity badges, detail with remediation tracking
- Reports: list, generate dialog, report history
- Communications: notifications (with header bell), email templates, communication logs
- Admin: user management, role management, audit log with filters/export, settings (4 tabs), integrations (8 cards)
- Command palette (Cmd+K), loading skeletons, toast notifications, empty states

### Security
- AES-256-GCM field-level PII encryption with HMAC lookup hashes
- bcrypt password hashing (cost factor 12)
- JWT access + refresh token authentication
- Multi-tenant Row-Level Security on all tenant-scoped tables
- OPA policy-as-code authorization
- Rate limiting on all endpoints
- RFC 7807 error responses (no stack trace leakage)

### Testing
- 396-item QA checklist across 18 categories
- 18 dynamic test scenarios with 231 steps
- 62/62 API endpoint tests passing (100%)
- 4 test users across roles (Admin, Manager, Analyst, Viewer)

### Seed Data
- 15 vendors (AWS, Salesforce, Stripe, Okta, etc.) across 4 tiers
- 5 assessments across lifecycle states
- 4 compliance frameworks with 74 clauses and cross-mappings
- 5 alerts (P0-P4), 8 findings, 10 audit log entries, 5 notifications
- 8 roles with 22 permissions

## [1.0.0] -- 2026-03-27

- Initial monolith build (discarded due to quality issues)
- PRD, HLD, LLD, and research retained

## [0.1.0] -- 2026-03-27

- Product intake and skeleton
