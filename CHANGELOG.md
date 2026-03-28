# Velora TPRM -- Changelog

All notable changes to this product will be documented in this file.

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
