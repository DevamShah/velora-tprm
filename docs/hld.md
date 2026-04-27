---
tags:
  - archeon
  - forgeon
  - product
  - product-velora
---

# Velora TPRM -- High-Level Design

> **Product**: Velora TPRM (Third-Party Risk Management)
> **Author**: Rachnika (System Architect, Pantheon)
> **Version**: 1.0.0
> **Date**: 2026-03-27
> **Status**: Draft -- Pending MCA Review
> **Classification**: Internal -- Architecture
> **Inputs**: PRD v1.0.0 (Darshika), Technical Architecture Research v1.0.0, Scoring & Framework Research v1.0.0

---

## Table of Contents

1. [System Context](#1-system-context)
2. [Architecture Style](#2-architecture-style)
3. [Tech Stack Decisions](#3-tech-stack-decisions)
4. [Module Architecture](#4-module-architecture)
5. [Data Architecture](#5-data-architecture)
6. [AI Architecture](#6-ai-architecture)
7. [Integration Architecture](#7-integration-architecture)
8. [Security Architecture](#8-security-architecture)
9. [Deployment Architecture](#9-deployment-architecture)
10. [Key Architecture Decisions (ADRs)](#10-key-architecture-decisions-adrs)
11. [Non-Functional Architecture](#11-non-functional-architecture)

---

## 1. System Context

### 1.1 System Boundary Diagram

```
                          VELORA TPRM -- SYSTEM CONTEXT
                          ============================

  +------------------+     +------------------+     +------------------+
  | SSO Providers    |     | Rating APIs      |     | Monitoring Feeds |
  | - Okta           |     | - SecurityScore  |     | - Breachsense    |
  | - Azure AD       |     |   card           |     | - SpyCloud       |
  | - Google WS      |     | - BitSight       |     | - HIBP           |
  | - OneLogin       |     | - RiskRecon      |     | - CT Logs        |
  +--------|---------+     +--------|----------+     +--------|----------+
           |                        |                          |
           v                        v                          v
  +------------------------------------------------------------------------+
  |                                                                        |
  |                          VELORA TPRM PLATFORM                          |
  |                                                                        |
  |  +------------------+  +-------------------+  +---------------------+  |
  |  | Web Application  |  | REST API          |  | Vendor Portal       |  |
  |  | (Next.js 15)     |  | (FastAPI)         |  | (Next.js, white-    |  |
  |  |                  |  | OpenAPI 3.1       |  |  labeled)           |  |
  |  +------------------+  +-------------------+  +---------------------+  |
  |                                                                        |
  |  +------------------+  +-------------------+  +---------------------+  |
  |  | AI Engine        |  | Scoring Engine    |  | Monitoring Engine   |  |
  |  | - LLM Orchestr.  |  | - Config-driven   |  | - Signal aggreg.   |  |
  |  | - RAG Pipeline   |  | - FAIR quant.     |  | - Alert routing    |  |
  |  | - Evidence Parse  |  | - Multi-dim.      |  | - Trend analysis   |  |
  |  +------------------+  +-------------------+  +---------------------+  |
  |                                                                        |
  |  +------------------+  +-------------------+  +---------------------+  |
  |  | PostgreSQL 16+   |  | Redis 7+          |  | S3 / MinIO         |  |
  |  | + pgvector       |  | + BullMQ          |  | (Evidence Store)   |  |
  |  +------------------+  +-------------------+  +---------------------+  |
  |                                                                        |
  +------------------------------------------------------------------------+
           |                        |                          |
           v                        v                          v
  +------------------+     +------------------+     +------------------+
  | Email Delivery   |     | Messaging        |     | Enrichment APIs  |
  | - SendGrid       |     | - Slack Webhooks |     | - Clearbit       |
  | - AWS SES        |     | - Teams Bots     |     | - ZoomInfo       |
  | - Custom SMTP    |     | - Twilio (SMS)   |     | - Crunchbase     |
  +------------------+     +------------------+     +------------------+

  +------------------+     +------------------+     +------------------+
  | Doc Intelligence |     | Cert Registries  |     | Threat Intel     |
  | - Azure Doc AI   |     | - IAF CertSearch |     | - MITRE ATT&CK   |
  | - AWS Textract   |     | - UKAS CertCheck |     | - NVD/CVE        |
  |                  |     | - CSA STAR       |     | - Recorded Future |
  +------------------+     +------------------+     +------------------+
```

### 1.2 External Integrations

| Category | Systems | Protocol | Direction |
|----------|---------|----------|-----------|
| **Identity** | Okta, Azure AD/Entra ID, Google Workspace, OneLogin | SAML 2.0, OIDC, SCIM 2.0 | Bidirectional |
| **Security Ratings** | SecurityScorecard, BitSight, RiskRecon | REST API (polling + webhooks) | Inbound |
| **Breach Intelligence** | Breachsense, SpyCloud, Have I Been Pwned | REST API (polling) | Inbound |
| **Enrichment** | Clearbit/HubSpot, ZoomInfo, Crunchbase | REST API | Inbound |
| **Document Parsing** | Azure Document Intelligence, AWS Textract | REST API | Outbound (docs sent for parsing) |
| **Email** | SendGrid, AWS SES, custom SMTP | REST API / SMTP | Outbound |
| **Messaging** | Slack (webhooks + app), Teams (webhooks + bot), Twilio | REST API / Webhooks | Bidirectional |
| **Certification** | IAF CertSearch, UKAS CertCheck, CSA STAR | Web scraping / API | Inbound |
| **Threat Intelligence** | MITRE ATT&CK, NVD, AlienVault OTX, Recorded Future | REST API / STIX-TAXII | Inbound |
| **ITSM** | Jira, ServiceNow | REST API | Bidirectional |
| **Procurement** | Coupa, SAP Ariba | REST API / CSV | Inbound |
| **LLM Providers** | Anthropic Claude, OpenAI GPT-4o | REST API (via platform-core/llm-abstraction) | Outbound |

### 1.3 Actor Model

**Internal Users (authenticated via SSO)**

| Actor | Role | Primary Actions |
|-------|------|----------------|
| **TPRM Program Lead** | TPRM Manager | Oversee vendor portfolio, configure scoring, manage assessments, approve risk decisions |
| **Risk Analyst** | Risk Analyst | Conduct assessments, review AI outputs, manage findings, evidence review |
| **CISO** | Executive + Approver | View dashboards, approve critical risk decisions, board reporting |
| **Vendor Relationship Manager** | VRM | Manage vendor communications, onboarding/offboarding, relationship tracking |
| **Auditor** | Auditor (read-only) | Access evidence, audit logs, compliance reports for examination |
| **Platform Admin** | Super Admin | Tenant configuration, user management, integration setup |

**External Users (vendor portal)**

| Actor | Role | Primary Actions |
|-------|------|----------------|
| **Vendor Security Responder** | Vendor Portal User | Complete questionnaires, upload evidence, view findings, manage trust profile |
| **Vendor Admin** | Vendor Portal Admin | Manage vendor trust profile, designate responders, publish security posture |

**System Actors**

| Actor | Description |
|-------|-------------|
| **Enrichment Engine** | Auto-enriches vendor profiles from external APIs on creation and schedule |
| **Monitoring Engine** | Polls external feeds, processes signals, generates alerts per vendor tier schedule |
| **Evidence Parser** | Processes uploaded documents through classification, parsing, extraction, and mapping |
| **Scoring Engine** | Recalculates risk scores when inputs change (assessment, evidence, monitoring signal) |
| **Notification Engine** | Dispatches alerts and reminders across email, Slack/Teams, in-app, SMS channels |
| **Report Generator** | Produces scheduled and on-demand reports (PDF, PPTX) with AI narratives |

**AI Actors**

| Actor | Capability | Human Oversight |
|-------|-----------|-----------------|
| **Questionnaire Pre-Filler** | Pre-populates vendor responses from evidence, trust centers, prior answers | Items below 85% confidence route to human review |
| **Evidence Extractor** | Extracts controls, findings, dates from SOC 2/ISO/pen test documents | Items below 90% confidence route to human review |
| **Framework Mapper** | Maps controls across frameworks using embeddings + LLM validation | All high-stakes mappings require human verification |
| **Risk Narrator** | Generates narrative summaries for reports and dashboards | All report outputs require human review before publishing |
| **Vendor Enricher** | Infers industry, size, tech stack, risk signals from public data | Items below 80% confidence flagged for review |

---

## 2. Architecture Style

### 2.1 Modular Monolith

Velora TPRM adopts a **modular monolith** architecture for the MVP and initial production releases. This is a deliberate choice driven by the research recommendation and team-size economics.

```
                    MODULAR MONOLITH STRUCTURE
                    =========================

  +----------------------------------------------------------------+
  |                     API GATEWAY LAYER                           |
  |  FastAPI Router -> Module-specific route groups -> Middleware    |
  +----------------------------------------------------------------+
       |          |          |          |          |          |
  +--------+ +--------+ +--------+ +--------+ +--------+ +--------+
  | Auth   | | Vendor | | Assess | | Frame  | | Score  | | Monitor|
  | Module | | Module | | Module | | Module | | Module | | Module |
  |        | |        | |        | |        | |        | |        |
  | - SSO  | | - CRUD | | - Qst  | | - Lib  | | - Calc | | - Feed |
  | - RBAC | | - Enr. | | - Evid | | - Map  | | - FAIR | | - Alert|
  | - Sess | | - Tier | | - Rev. | | - Diff | | - Conf | | - Trend|
  +--------+ +--------+ +--------+ +--------+ +--------+ +--------+
       |          |          |          |          |          |
  +--------+ +--------+ +--------+ +--------+ +--------+ +--------+
  | Evid.  | | Report | | Comms  | | Portal | | Admin  | | AI     |
  | Module | | Module | | Module | | Module | | Module | | Module |
  |        | |        | |        | |        | |        | |        |
  | - Ingest| | - Dash | | - Email| | - Self | | - Conf | | - LLM |
  | - Parse| | - Gen  | | - Slack| | - Trust| | - Audit| | - RAG  |
  | - Map  | | - Sched| | - Escl | | - Exch | | - Data | | - Conf |
  +--------+ +--------+ +--------+ +--------+ +--------+ +--------+
       |          |          |          |          |          |
  +----------------------------------------------------------------+
  |                     SHARED KERNEL                               |
  |  Tenant Context | Event Bus | Config Engine | Rule Engine       |
  |  Audit Logger   | Cache     | Job Scheduler | Error Handling    |
  +----------------------------------------------------------------+
       |
  +----------------------------------------------------------------+
  |                     DATA LAYER                                  |
  |  PostgreSQL (RLS) | Redis | S3/MinIO | Typesense | Temporal    |
  +----------------------------------------------------------------+
```

**Module boundaries are enforced through**:
- Each module has its own Python package under `app/modules/{module_name}/`
- Modules expose interfaces (abstract base classes) and depend on interfaces, not implementations
- Cross-module communication through the shared event bus (synchronous in-process events for queries, async events via Redis Streams for side effects)
- Direct database table ownership: each module owns its tables and exposes data through service interfaces
- No direct imports between module internals -- only through public module APIs

**Scale-out path**: Individual modules can be extracted into independent services when load demands it. The event bus and interface-based design make this extraction mechanical, not architectural. The Monitoring Module and AI Module are the most likely candidates for early extraction due to their compute-intensive workloads.

### 2.2 API-First Design

Every feature is built API-first. The Next.js frontend is a consumer of the same public API available to external integrations.

- **OpenAPI 3.1** spec auto-generated from FastAPI route decorators and Pydantic models
- **TypeScript client** auto-generated from OpenAPI spec for the frontend (using `openapi-typescript-codegen`)
- **Versioned endpoints**: `/api/v1/` prefix, with backward-compatible evolution and explicit deprecation
- **Cursor-based pagination** on all list endpoints for consistency under concurrent writes
- **Standardized error format**: RFC 7807 Problem Details for HTTP APIs

### 2.3 Event-Driven Async Operations

Operations that do not need synchronous response follow an event-driven pattern:

| Trigger Event | Async Operation | Mechanism |
|--------------|----------------|-----------|
| Vendor created | Enrichment pipeline (firmographics, ratings, certs) | Temporal workflow |
| Evidence uploaded | Parse, extract, map, index pipeline | Temporal workflow |
| Assessment submitted | AI validation, scoring, review routing | Temporal workflow |
| Monitoring signal received | Deduplicate, correlate, alert, notify | BullMQ job chain |
| Score input changed | Recalculate composite risk score | BullMQ job |
| Report requested | Data collection, section generation, assembly | Temporal workflow |
| Webhook event | Serialize, sign, deliver with retry | BullMQ job |

**Event bus**: Redis Streams for durable, at-least-once event delivery between modules. PostgreSQL LISTEN/NOTIFY for lightweight real-time notifications (e.g., cache invalidation).

---

## 3. Tech Stack Decisions

### 3.1 Decisions with Rationale

| Layer | Technology | Version | Rationale |
|-------|-----------|---------|-----------|
| **Backend** | FastAPI + Pydantic v2 | Python 3.12+ | Async-native for LLM/enrichment I/O waits. Pydantic v2 provides end-to-end type safety. OpenAPI auto-gen eliminates spec drift. Python's AI/ML ecosystem (LangChain, LlamaIndex, sentence-transformers) is unmatched. No other language has equivalent LLM SDK maturity. |
| **Frontend** | Next.js 15 (App Router) + TypeScript | v15+ | React Server Components for performance. SSR for marketing/SEO pages. Middleware for auth flow. TypeScript + Zod provides runtime validation matching Pydantic on the backend. Dominant enterprise SaaS UI framework. |
| **UI Components** | shadcn/ui + Tailwind CSS + Radix UI | Latest | Accessible, customizable components without vendor lock-in. Copy-paste model means full control over styling. Tailwind produces consistent, information-dense layouts suitable for enterprise dashboards. |
| **Database** | PostgreSQL 16+ with RLS | v16+ | Industry-standard multi-tenant SaaS database. Row-Level Security provides transparent tenant isolation. JSONB columns handle semi-structured data (configs, questionnaire responses, scoring rules) without a separate document store. Mature ecosystem, excellent tooling. |
| **Vector Storage** | pgvector (start) -> Qdrant (scale) | pgvector 0.7+ | pgvector eliminates a separate infrastructure component at MVP. HNSW indexes provide good recall for framework clause embeddings (approx 5,000-50,000 vectors initially). Qdrant migration path when vectors exceed 10M and query latency becomes critical. |
| **Cache** | Redis 7+ | v7+ | Distributed cache for sessions, tenant configs, API responses, rate limiting. Also backs BullMQ job queues. Hybrid pattern with in-process Python `lru_cache` for hot-path reads (tenant settings, permission matrices) reduces latency from ~45ms to ~2ms. |
| **Search** | Typesense | Latest | Query-time field weighting configuration is critical for multi-tenant search where each tenant weights fields differently. Lower operational overhead than Elasticsearch. Typo tolerance and faceted search out of the box. Sub-50ms search latency for vendor, control, and evidence search. |
| **Simple Jobs** | BullMQ (Redis-backed) | Latest | Email sending, webhook delivery, cache invalidation, notification dispatch, score recalculation. Supports priority queues, rate limiting, retry with backoff, concurrency control. Python workers via `bullmq` Python package. |
| **Complex Workflows** | Temporal | Latest | Durable execution for multi-step processes: vendor enrichment, assessment lifecycle, evidence parsing, remediation tracking. Code-based workflow definitions (Python SDK). Automatic pause/resume during provider outages. Complete event history for audit trails. |
| **File Storage** | AWS S3 / MinIO | Latest | S3 for production with SSE-KMS encryption. MinIO for development and self-hosted enterprise deployments requiring data sovereignty. Presigned URLs for secure client-side upload/download. Versioning enabled for evidence audit trails. |
| **Real-Time** | SSE (primary) + WebSockets (collaborative) | Native | SSE for assessment status updates, enrichment progress, monitoring alerts, notification delivery. Simpler than WebSockets, works through proxies, auto-reconnects. WebSockets reserved for future collaborative editing features. FastAPI supports both natively. |
| **AI/LLM** | LangChain + LlamaIndex via platform-core/llm-abstraction | Latest | LangChain for LLM orchestration chains (enrichment, pre-fill, report generation). LlamaIndex for RAG pipeline (framework intelligence). All LLM calls routed through platform-core/llm-abstraction for provider switching, cost tracking, and fallback. |
| **Document Parsing** | Azure Document Intelligence (primary) + AWS Textract (fallback) | Latest | Azure leads in layout analysis and table reconstruction for SOC 2 reports with complex table structures. AWS Textract as fallback for AWS-native deployments. Both accessed asynchronously from Temporal workflows. |
| **Monitoring** | Prometheus + Grafana | Latest | Standard observability stack. Prometheus scrapes application metrics. Grafana dashboards for infrastructure and business metrics. AlertManager for ops alerts. |
| **Logging** | Structured JSON -> Loki | Latest | Structured JSON log output from all services. Loki for log aggregation (lighter than ELK, integrates with Grafana). Log correlation via trace IDs. |
| **CI/CD** | GitHub Actions + Docker + Kubernetes | Latest | GitHub Actions for build, test, security scan, deploy pipelines. Docker for consistent build artifacts. Kubernetes for orchestration with horizontal pod autoscaling. |
| **Key Management** | AWS KMS + HashiCorp Vault | Latest | AWS KMS for envelope encryption of data at rest. Vault for application secrets, API keys, database credentials, per-tenant encryption keys. |

---

## 4. Module Architecture

### 4.1 Auth Module

**Responsibility**: Authentication, authorization, session management, tenant context injection.

```
Auth Module
  ├── services/
  │   ├── sso_service.py        # SAML 2.0 + OIDC flows
  │   ├── session_service.py    # JWT issuance, refresh, revocation
  │   ├── rbac_service.py       # Role resolution, permission checks
  │   ├── abac_service.py       # Attribute-based policy evaluation
  │   └── scim_service.py       # SCIM 2.0 user provisioning
  ├── middleware/
  │   ├── auth_middleware.py     # JWT validation, tenant context injection
  │   └── permission_middleware.py  # Route-level permission checks
  ├── models/
  │   └── auth_models.py        # User, Role, Permission, Session
  └── routes/
      └── auth_routes.py        # /auth/login, /auth/callback, /auth/logout
```

**Interfaces exposed**:
- `authenticate(token: str) -> AuthContext` -- validates JWT, returns user + tenant + roles
- `authorize(context: AuthContext, action: str, resource: Resource) -> bool` -- RBAC + ABAC check
- `get_tenant_context() -> TenantContext` -- current request tenant ID for RLS injection

**Dependencies**: Redis (sessions), PostgreSQL (users, roles, permissions)

**Key behaviors**:
- On every authenticated request, middleware extracts `tenant_id` from JWT and sets PostgreSQL session variable `app.current_tenant_id` before any query executes
- RBAC provides 8 base roles (Super Admin, TPRM Manager, Risk Analyst, VRM, Auditor, Executive, Vendor Portal User, API Service Account)
- ABAC overlay evaluates dynamic policies: `resource.risk_level == "critical" && user.role != "ciso" -> deny approve`
- MFA enforcement configurable per tenant
- Session timeout: 30 minutes default, configurable per tenant (15-60 min range)

### 4.2 Tenant Module

**Responsibility**: Organization setup, configuration management, tenant customization, branding.

**Interfaces exposed**:
- `get_tenant_config(tenant_id: UUID) -> TenantConfig` -- returns full tenant configuration (cached in Redis, 5min TTL)
- `update_tenant_config(tenant_id: UUID, patch: ConfigPatch) -> TenantConfig` -- validates against JSON Schema, updates config, invalidates cache
- `get_tenant_branding(tenant_id: UUID) -> Branding` -- logo, colors, portal domain for white-labeling

**Dependencies**: PostgreSQL (tenants, tenant_configs), Redis (config cache)

**Key behaviors**:
- Tenant config stored as JSONB, validated against JSON Schema on every write
- Config categories: scoring models, workflow definitions, escalation rules, notification preferences, role definitions, integration settings, branding
- Config changes emit events to the event bus for downstream cache invalidation
- Onboarding wizard: 4-step setup (company profile with AI enrichment, framework selection, scoring model defaults, team roles)

### 4.3 Vendor Module

**Responsibility**: Vendor lifecycle management, enrichment, tiering, relationship tracking, Nth-party mapping.

```
Vendor Module
  ├── services/
  │   ├── vendor_service.py           # CRUD, bulk import (CSV, API)
  │   ├── enrichment_service.py       # Orchestrates enrichment pipeline
  │   ├── tiering_service.py          # Inherent risk tier calculation
  │   ├── nth_party_service.py        # Sub-processor mapping, concentration risk
  │   └── discovery_service.py        # Shadow IT vendor discovery (P2)
  ├── workflows/
  │   ├── enrichment_workflow.py      # Temporal: multi-source enrichment
  │   ├── onboarding_workflow.py      # Temporal: configurable onboarding steps
  │   └── offboarding_workflow.py     # Temporal: checklist-driven offboarding
  ├── models/
  │   └── vendor_models.py            # Vendor, VendorContact, NthParty
  └── routes/
      └── vendor_routes.py            # /api/v1/vendors/*
```

**Interfaces exposed**:
- `create_vendor(data: VendorCreate) -> Vendor` -- creates vendor, triggers enrichment workflow
- `import_vendors(file: CSV | vendors: list) -> ImportResult` -- bulk import with dedup
- `get_vendor_profile(vendor_id: UUID) -> VendorProfile` -- 360-degree view (scores, assessments, evidence, alerts)
- `calculate_inherent_tier(vendor_id: UUID) -> Tier` -- weighted factor calculation using tenant's scoring config
- `get_nth_party_graph(vendor_id: UUID) -> NthPartyGraph` -- sub-processor dependency graph

**Dependencies**: Auth Module (authorization), Tenant Module (scoring config), AI Module (enrichment inference), Scoring Module (tier calculation)

**Enrichment pipeline** (Temporal workflow):
1. Firmographics lookup (Clearbit/ZoomInfo) -- industry, employee count, revenue, HQ location
2. Security rating fetch (SecurityScorecard/BitSight) -- external posture score
3. Certification registry check (IAF CertSearch, CSA STAR) -- ISO 27001, SOC 2 status
4. Trust center detection and scraping -- published security documentation
5. Breach history check (HIBP) -- historical breach records
6. AI inference -- tech stack, risk signals from public data (confidence scored)
7. Composite enrichment profile assembled, stored, indexed in Typesense

### 4.4 Assessment Module

**Responsibility**: Questionnaire engine, evidence collection, AI-assisted review, findings management, remediation tracking.

**Interfaces exposed**:
- `create_assessment(vendor_id: UUID, template_id: UUID) -> Assessment` -- creates assessment with auto-selected template based on vendor tier and frameworks
- `distribute_assessment(assessment_id: UUID) -> DistributionResult` -- sends to vendor portal with deadline, starts SLA timer
- `submit_assessment(assessment_id: UUID, responses: list) -> Assessment` -- vendor submission triggers AI validation
- `get_review_queue(filters: ReviewFilters) -> list[ReviewItem]` -- items below confidence threshold awaiting human review
- `create_finding(assessment_id: UUID, data: FindingCreate) -> Finding` -- auto-generated or manual finding with severity, remediation guidance, deadline

**Dependencies**: Auth Module, Vendor Module, Framework Module (templates), Scoring Module (assessment scoring), AI Module (pre-fill, validation), Evidence Module (parsed evidence), Comms Module (distribution, reminders)

**Assessment lifecycle** (Temporal workflow):
1. Template selection based on vendor tier + applicable frameworks
2. AI pre-population from vendor's prior responses, trust center docs, public info, evidence corpus
3. Distribution to vendor portal with configurable deadline (30 days SIG Core, 14 days SIG Lite)
4. Automated reminders at Day 7, 14, 21 with escalating recipients
5. Vendor submission triggers: AI cross-validation of responses against evidence, confidence scoring per item
6. Items below threshold routed to human review queue with role-based assignment
7. Reviewer accepts/modifies/rejects with justification -- feedback logged for model improvement
8. Findings auto-generated for identified gaps with severity-based SLA deadlines (Critical: 30d, High: 60d, Medium: 90d)
9. Remediation tracking through vendor portal with AI verification of submitted evidence

### 4.5 Framework Module

**Responsibility**: Framework ingestion, clause-level storage (OSCAL format), cross-framework mapping, question bank management, version diffing.

**Interfaces exposed**:
- `get_framework(id: UUID) -> Framework` -- framework metadata and clause tree
- `get_clause(clause_id: UUID) -> FrameworkClause` -- single clause with embeddings, mappings
- `get_cross_mappings(source_clause_id: UUID) -> list[ControlMapping]` -- all cross-framework mappings for a clause
- `get_unified_controls(framework_ids: list[UUID]) -> list[UnifiedControl]` -- deduplicated control set across multiple frameworks
- `diff_framework_versions(old_id: UUID, new_id: UUID) -> FrameworkDiff` -- clause-level added/modified/removed

**Dependencies**: AI Module (embedding generation, mapping validation), Tenant Module (applicable frameworks per tenant)

**Key behaviors**:
- Frameworks stored in OSCAL JSON format for machine-readability
- Each clause decomposed to atomic level with embedding (1536-dim, text-embedding-3-large)
- Cross-framework mappings: NIST OLIR imports as authoritative baseline, AI-assisted for uncovered pairs, human verification for high-stakes mappings
- Unified control library: one internal control tagged with source framework(s), eliminating redundant assessment across overlapping frameworks (SOC 2 and ISO 27001 share ~96% controls)
- GA frameworks: SOC 2 TSC (~60 criteria), ISO 27001:2022 (93 controls), NIST CSF 2.0 (106 subcategories), HIPAA Security Rule (~50 standards), GDPR (key articles). DORA (64 articles) and NIS2 (46 articles) within 60 days post-GA. PCI DSS 4.0 (250+ requirements) in Q1 post-GA.
- Framework version monitoring: RSS/Atom feeds from NIST, ISO, CSA, CIS. OSCAL catalog diffing for programmatic change detection. Affected tenants notified automatically.

### 4.6 Scoring Module

**Responsibility**: Configurable scoring engine, multi-dimensional risk calculation, inherent/residual risk, FAIR quantification, external rating normalization, portfolio aggregation.

**Interfaces exposed**:
- `calculate_inherent_risk(vendor_id: UUID) -> InherentRiskScore` -- weighted factor calculation (data sensitivity, access level, business criticality, regulatory exposure)
- `calculate_residual_risk(vendor_id: UUID) -> ResidualRiskScore` -- inherent risk adjusted by control effectiveness
- `calculate_composite_score(vendor_id: UUID) -> CompositeScore` -- multi-dimensional composite from all inputs
- `normalize_external_rating(provider: str, raw_score: float) -> float` -- SecurityScorecard A-F/0-100, BitSight 250-900 normalized to internal 0-100
- `quantify_financial_risk(vendor_id: UUID) -> FAIRResult` -- FAIR-based dollar-value loss exposure (P1)
- `get_portfolio_risk(tenant_id: UUID) -> PortfolioRisk` -- aggregate risk metrics, concentration analysis, trends

**Dependencies**: Tenant Module (scoring config), Vendor Module (vendor attributes), Assessment Module (questionnaire scores), Evidence Module (evidence scores), Monitoring Module (external ratings, alert signals)

**Scoring engine architecture**:

```
                    SCORING ENGINE FLOW
                    ===================

  +------------------+     +------------------+     +------------------+
  | Inherent Risk    |     | Control Effect.  |     | External Posture |
  | Factors:         |     | Factors:         |     | Factors:         |
  | - Data sens.     |     | - Questionnaire  |     | - Security rating|
  |   (15-20%)       |     |   score          |     |   (20-25%)       |
  | - Access level   |     | - Evidence score |     | - Scan results   |
  |   (15-20%)       |     |   (weighted by   |     | - Breach history |
  | - Business crit. |     |    freshness &   |     |   (5-10%)        |
  |   (15-20%)       |     |    confidence)   |     +--------|---------+
  | - Regulatory exp.|     | - Control mat.   |              |
  |   (10-15%)       |     |   (10-15%)       |              |
  +--------|---------+     +--------|---------+              |
           |                        |                        |
           v                        v                        v
  +--------------------------------------------------------------+
  |              CONFIG-DRIVEN SCORING ENGINE                     |
  |                                                              |
  |  Scoring Model (JSON rules from tenant_config):              |
  |  - Method: weighted_average | multiplicative                 |
  |  - Weights: admin-configurable per factor                    |
  |  - Thresholds: Critical >85, High 70-84, Med 40-69, Low <40 |
  |  - Templates: per-industry, per-regulation presets           |
  |                                                              |
  |  Residual Risk Calculation:                                  |
  |  - Subtraction: IR - CE = RR                                 |
  |  - Multiplication: IR x (1 - CE%) = RR  (recommended)       |
  |  - Admin selects method per scoring template                 |
  +--------------------------------------------------------------+
           |
           v
  +--------------------------------------------------------------+
  |  Composite Risk Score (0-100)                                |
  |  + Multi-dimensional breakdown (security, privacy, ops, etc) |
  |  + Risk tier classification (Critical / High / Medium / Low) |
  |  + FAIR overlay (optional): Annual Loss Expectancy in $      |
  |  + Audit trail: every score change logged with reason        |
  |  + Manual override: with mandatory justification, expires    |
  |    on next assessment unless renewed                         |
  +--------------------------------------------------------------+
```

- All scoring formulas stored as JSON rules in `tenant_configs`, not hardcoded
- Both additive (weighted average) and multiplicative (inherent x control factor) models supported
- Per-tier, per-industry, per-regulation scoring templates
- Score recalculation triggered by events: assessment completed, evidence uploaded, rating changed, monitoring alert
- Portfolio-level aggregation: average risk, risk distribution, concentration risk (single-vendor, geographic), 30/60/90-day trends

### 4.7 Monitoring Module

**Responsibility**: Multi-signal aggregation, alert engine with prioritization, deduplication, correlation, trend analysis, vendor risk timeline.

**Interfaces exposed**:
- `ingest_signal(signal: MonitoringSignal) -> ProcessedSignal` -- receives signal, deduplicates, enriches, scores
- `get_alerts(filters: AlertFilters) -> list[Alert]` -- filtered alert list for review queue
- `get_vendor_timeline(vendor_id: UUID) -> list[TimelineEvent]` -- chronological view of all vendor events
- `get_trend_analysis(vendor_id: UUID, period: str) -> TrendResult` -- 30/60/90-day trend with trajectory prediction

**Dependencies**: Vendor Module (vendor context), Scoring Module (score recalculation trigger), Comms Module (alert delivery), Tenant Module (escalation rules, monitoring frequency config)

**Alert priority classification**:
- **P0**: Active breach involving customer data, ransomware attack on vendor
- **P1**: Critical CVE on vendor stack, leaked credentials, rating drop >15 points
- **P2**: Certificate expiry, DNS changes, regulatory action against vendor
- **P3**: Moderate rating drop 5-15 points, certification expiry approaching, key personnel departure
- **P4**: Minor rating fluctuation (<5 points), website/tech stack changes

**Deduplication and correlation**: Match signals by vendor + signal type + 24-hour window. Multiple P2/P3 from same vendor within 48 hours elevates to P1. Known false positives suppressed with documented justification.

**Monitoring frequency by vendor tier**:
| Activity | Tier 1 (Critical) | Tier 2 (High) | Tier 3 (Medium) | Tier 4 (Low) |
|----------|-------------------|---------------|-----------------|--------------|
| Rating check | Daily | Weekly | Monthly | Quarterly |
| Breach monitoring | Real-time | Real-time | Daily | Weekly |
| Dark web credentials | Daily | Weekly | Monthly | Quarterly |
| DNS/SSL monitoring | Daily | Weekly | Monthly | N/A |
| News monitoring | Daily | Weekly | Monthly | Quarterly |

### 4.8 Evidence Module

**Responsibility**: Document ingestion, classification, parsing, extraction, control mapping, versioning, freshness tracking.

**Interfaces exposed**:
- `initiate_upload(metadata: UploadMetadata) -> PresignedUrl` -- returns presigned S3 URL for client-side upload
- `process_evidence(evidence_id: UUID) -> ProcessingResult` -- triggers Temporal parsing workflow
- `get_evidence_mappings(evidence_id: UUID) -> list[ControlMapping]` -- extracted controls with coverage type and confidence
- `get_expiring_evidence(days_ahead: int) -> list[Evidence]` -- evidence approaching expiry threshold
- `get_evidence_confidence(evidence_id: UUID) -> ConfidenceScore` -- composite confidence based on source, recency, completeness, consistency, verification

**Dependencies**: AI Module (classification, extraction, mapping), Framework Module (control references), S3/MinIO (file storage), Vendor Module (vendor context)

**Evidence processing pipeline** (Temporal workflow):

```
  Upload (presigned S3 URL)
    |
    v
  [Intake] Validate file type/size, virus scan (ClamAV), SHA-256 hash,
           store raw file in S3 (tenant_id/vendor_id/assessment_id/hash.ext),
           create evidence record in PostgreSQL
    |
    v
  [Classify] Detect document type (SOC 2, ISO cert, pen test, policy, etc),
             extract metadata (date, issuer, subject, validity period)
    |
    v
  [Parse] PDF/DOCX -> Azure Document Intelligence (layout + tables)
          Images -> OCR pipeline
          Structured data -> direct parsing
    |
    v
  [Extract] LLM-powered extraction:
            - SOC 2: audit period, opinion type, exceptions, control statuses, CUECs
            - ISO cert: certifying body, scope, certificate number, validity dates
            - Pen test: date, scope, critical/high findings, remediation status
            - Policy: effective date, review date, key provisions
    |
    v
  [Map] Auto-map extracted controls to framework clauses
        Coverage type: Full | Partial | Supportive
        Confidence score per mapping
        Flag gaps where expected evidence is missing
    |
    v
  [Index] Full-text index in Typesense
          Embedding generation for semantic search (pgvector)
          Parsed structured data stored in PostgreSQL JSONB
```

**Evidence freshness tracking**:
- SOC 2 Type II: 12-month validity, alerts at 90/60/30/14/7 days before expiry
- ISO 27001 certificate: 3-year validity with annual surveillance, alerts at 60/30 days
- Penetration test: 12-month best practice, alerts at 90/60/30 days
- Vulnerability scan: 30-90 day validity
- Insurance certificate: policy period, alerts at 30/14 days before expiry

### 4.9 Reporting Module

**Responsibility**: Executive dashboards, board report generation, regulatory compliance reports, operational analytics, scheduled delivery.

**Interfaces exposed**:
- `get_dashboard_data(dashboard_type: str) -> DashboardData` -- executive, operational, or compliance dashboard
- `generate_report(template_id: UUID, params: ReportParams) -> ReportJob` -- triggers async report generation
- `get_regulatory_export(format: str) -> ExportResult` -- DORA Register of Information, HIPAA compliance matrix, etc.
- `schedule_report(schedule: ReportSchedule) -> Schedule` -- configure auto-generation and delivery

**Dependencies**: Vendor Module, Assessment Module, Scoring Module, Monitoring Module, AI Module (narrative generation), Comms Module (delivery)

**Report types**:
- Executive dashboard: real-time portfolio summary, risk heatmap, top-10 riskiest vendors, open findings, assessment completion rates, regulatory compliance posture
- Board report (PDF/PPTX): risk heatmap, vendor analysis, FAIR financial exposure, regulatory posture, trends, AI-generated narrative sections
- Regulatory reports: DORA Register of Information, HIPAA vendor compliance matrix, GDPR Article 28 processor summary, PCI DSS third-party status
- Operational analytics: assessment throughput, cycle time, vendor response rates, SLA adherence, analyst productivity, AI automation rate

### 4.10 Communications Module

**Responsibility**: Email delivery, Slack/Teams integration, in-app notifications, vendor outreach automation, escalation engine.

**Interfaces exposed**:
- `send_notification(notification: Notification) -> DeliveryResult` -- routes to configured channels (email, Slack, Teams, in-app, SMS)
- `send_vendor_outreach(vendor_id: UUID, template: str, params: dict) -> OutreachResult` -- template-based email with dynamic content
- `escalate(escalation: Escalation) -> EscalationResult` -- applies tenant escalation rules
- `get_reminder_schedule(assessment_id: UUID) -> list[ScheduledReminder]` -- upcoming reminders for an assessment

**Dependencies**: Tenant Module (notification preferences, escalation rules, email config), Auth Module (recipient resolution)

**Escalation engine**:
- Vendor non-response: analyst -> procurement lead -> business owner -> CISO (5 business days per level)
- Critical finding: analyst -> CISO -> business owner (24-hour acknowledge SLA)
- Active vendor breach: analyst -> incident response -> CISO -> legal -> exec (within 1 hour)
- Rating drop below threshold: automated alert -> analyst -> VRM (48-hour investigation SLA)

### 4.11 Portal Module

**Responsibility**: Vendor self-service portal, trust profiles, trust exchange.

**Interfaces exposed**:
- `get_portal_assessments(vendor_token: str) -> list[Assessment]` -- assessments pending for this vendor
- `submit_portal_response(assessment_id: UUID, responses: list) -> SubmissionResult` -- vendor submits questionnaire
- `upload_portal_evidence(vendor_token: str, file: UploadFile) -> Evidence` -- vendor uploads evidence
- `manage_trust_profile(vendor_id: UUID) -> TrustProfile` -- vendor manages shared trust profile (P1)

**Dependencies**: Assessment Module, Evidence Module, Comms Module, Auth Module (portal-specific auth, no full Velora account required for basic access)

**Key behaviors**:
- White-labeled portal per tenant (custom domain, logo, colors from Tenant Module branding config)
- Vendors access via tokenized link (no Velora account required for basic access) or authenticated portal login (for trust profile management)
- AI pre-filled answers displayed with citations for vendor review and correction
- SLA timer visible to vendor with upcoming deadline and reminder schedule
- Findings and remediation requests visible with severity, guidance, and deadline

### 4.12 Admin Module

**Responsibility**: Platform configuration, audit log access, data management, integration management.

**Interfaces exposed**:
- `get_audit_logs(filters: AuditFilters) -> list[AuditLog]` -- filtered, paginated audit log access
- `manage_integrations(tenant_id: UUID) -> list[Integration]` -- configure external integrations
- `export_tenant_data(tenant_id: UUID) -> ExportJob` -- GDPR data portability (right to data portability)
- `delete_tenant_data(tenant_id: UUID) -> DeletionJob` -- GDPR right to erasure

**Dependencies**: All modules (audit logging is cross-cutting)

**Audit logging architecture**:
- Every action logged: actor, action, resource, changes (old/new values), IP address, timestamp
- Append-only table with no UPDATE or DELETE permissions
- Partitioned by month for retention management and query performance
- Retention: 7 years default (configurable per tenant for regulatory requirements)
- Exportable in JSON/CSV for regulatory examination

### 4.13 AI Module

**Responsibility**: LLM orchestration, RAG pipeline, confidence scoring, human-in-the-loop routing.

```
AI Module
  ├── services/
  │   ├── llm_service.py            # Abstraction over platform-core/llm-abstraction
  │   ├── rag_service.py            # RAG pipeline for framework intelligence
  │   ├── confidence_service.py     # Composite confidence scoring
  │   ├── review_router.py          # Confidence-based human-in-the-loop routing
  │   └── feedback_service.py       # Collects human corrections for improvement
  ├── pipelines/
  │   ├── evidence_extraction.py    # SOC 2 / ISO / pen test extraction chains
  │   ├── questionnaire_prefill.py  # Pre-fill from evidence + trust center + prior
  │   ├── vendor_enrichment.py      # Public data inference chains
  │   ├── report_generation.py      # Narrative section generation
  │   └── framework_mapping.py      # Cross-framework mapping with validation
  ├── models/
  │   └── ai_models.py              # AIOutput, ConfidenceScore, ReviewItem
  └── routes/
      └── ai_routes.py              # /api/v1/ai/ask (natural language Q&A, P2)
```

**Interfaces exposed**:
- `run_pipeline(pipeline: str, input: PipelineInput) -> AIOutput` -- execute an AI pipeline with confidence scoring
- `get_review_queue(filters: ReviewFilters) -> list[ReviewItem]` -- items below confidence threshold
- `submit_review(item_id: UUID, decision: ReviewDecision) -> ReviewResult` -- human accepts/modifies/rejects
- `ask(query: str, context: QueryContext) -> NLAnswer` -- natural language Q&A over vendor data (P2)

**Dependencies**: platform-core/llm-abstraction (mandatory -- no direct LLM API calls), Framework Module (embeddings, clause data), Evidence Module (parsed content), Vendor Module (enrichment data)

Full AI architecture details in Section 6.

### 4.14 Module Dependency Map

```
                    MODULE DEPENDENCY GRAPH
                    ======================

                      +----------+
                      |  Auth    |<---------- All modules depend on Auth
                      +----------+
                           |
                      +----------+
                      |  Tenant  |<---------- Most modules depend on Tenant config
                      +----------+
                        /    |    \
                       /     |     \
              +--------+ +--------+ +--------+
              | Vendor | | Frame  | | Admin  |
              +--------+ +--------+ +--------+
                |    \      |   |       |
                |     \     |   |       |
              +--------+ +--------+ +--------+
              | Assess | | Score  | | AI     |
              +--------+ +--------+ +--------+
                |    |      |           |
                |    |      |           |
              +--------+ +--------+ +--------+
              | Evid.  | | Monitor| | Report |
              +--------+ +--------+ +--------+
                             |
                          +--------+
                          | Comms  |<--------- Assessment, Monitor, Report, Portal use Comms
                          +--------+
                             |
                          +--------+
                          | Portal |
                          +--------+

  Legend:
  Arrow direction = "depends on" (arrow points to dependency)
  Auth and Tenant are foundational (no circular deps)
  AI is a utility consumed by Assessment, Evidence, Vendor, Report, Framework
  Comms is a utility consumed by Assessment, Monitor, Report, Portal
```

---

## 5. Data Architecture

### 5.1 Multi-Tenant Strategy

**Pattern**: Shared database, shared schema, Row-Level Security (Pool model).

```
Request Flow:
  API Request
    -> Auth Middleware: validate JWT, extract tenant_id
    -> Set PostgreSQL session variable: SET app.current_tenant_id = '{tenant_id}'
    -> RLS policies automatically filter ALL queries
    -> Response contains only requesting tenant's data

RLS Policy (applied to every tenant-scoped table):
  CREATE POLICY tenant_isolation ON {table}
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);
```

**Tiered isolation for enterprise**:
| Tier | Model | Use Case | Pricing Tier |
|------|-------|----------|-------------|
| Standard | Shared schema + RLS | Most tenants | Professional, Business |
| Premium | Schema-per-tenant | Regulated industries needing stronger isolation | Enterprise |
| Enterprise | Database-per-tenant | Banks, government, data sovereignty | Enterprise (custom) |

**Every tenant-scoped table** has `tenant_id UUID NOT NULL` as the first column after the primary key, with a composite index `(tenant_id, id)` for RLS-filtered query performance.

### 5.2 Core Entity Model (High-Level)

```
                    CORE ENTITY RELATIONSHIPS
                    =========================

  Tenant (1) ----< Vendor (N)
    |                 |
    |                 |----< Assessment (N)
    |                 |         |
    |                 |         |----< QuestionnaireResponse (N)
    |                 |         |----< Finding (N)
    |                 |         |         |----< RemediationAction (N)
    |                 |         |----< AssessmentEvidence (N) ---> Evidence
    |                 |
    |                 |----< Evidence (N)
    |                 |         |----< EvidenceControlMapping (N) ---> FrameworkClause
    |                 |
    |                 |----< MonitoringAlert (N)
    |                 |
    |                 |----< VendorContact (N)
    |                 |
    |                 |----< NthParty (N) ---> Vendor (self-ref)
    |
    |----< User (N) ----< UserRole (N) ---> Role
    |
    |----< TenantConfig (1)
    |
    |----< ScoringTemplate (N)

  Framework (1) ----< FrameworkClause (N)
                         |----< ControlMapping (N) ---> FrameworkClause (target)

  (Frameworks and FrameworkClauses are global, NOT tenant-scoped)
  (All other entities are tenant-scoped with RLS)
```

**Key entities and their table ownership by module**:

| Module | Tables Owned |
|--------|-------------|
| Auth | users, roles, permissions, user_roles, sessions, api_keys |
| Tenant | tenants, tenant_configs |
| Vendor | vendors, vendor_contacts, nth_parties, vendor_enrichment_cache |
| Assessment | assessments, questionnaire_responses, findings, remediation_actions, assessment_schedules |
| Framework | frameworks, framework_clauses, control_mappings, question_banks (global, not tenant-scoped) |
| Scoring | scoring_templates, score_history, score_overrides |
| Monitoring | monitoring_signals, monitoring_alerts, vendor_timelines |
| Evidence | evidence, evidence_control_mappings, evidence_versions |
| Reporting | report_templates, report_jobs, scheduled_reports |
| Comms | notification_rules, notification_log, escalation_log, outreach_log |
| Portal | vendor_portal_tokens, trust_profiles |
| Admin | audit_logs (partitioned by month), integration_configs |
| AI | ai_outputs, review_queue, feedback_log |

### 5.3 Vector Storage Strategy

**Phase 1 (MVP-Launch, <5M vectors)**: pgvector within PostgreSQL
- Framework clause embeddings (~5,000 clauses x 1536 dimensions)
- Evidence content embeddings (~100,000 chunks)
- Vendor enrichment text embeddings (~50,000)
- HNSW index: `CREATE INDEX ... USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64)`
- No additional infrastructure component

**Phase 2 (Growth, 5-10M vectors)**: pgvector with tuned HNSW indexes
- Increase HNSW parameters for better recall
- Partition vector-heavy tables by tenant for query performance
- Monitor query latency (target: <100ms for top-20 similarity search)

**Phase 3 (Enterprise Scale, 10M+ vectors)**: Migrate to Qdrant (self-hosted)
- Rust-based, consistently fastest across benchmarks
- Sophisticated metadata filtering (tenant_id, framework_id, document_type)
- Production-proven at billion-vector scale
- Migration is transparent to application code -- vector search abstracted behind a service interface

### 5.4 File Storage Strategy

**Bucket structure**: `velora-evidence/{tenant_id}/{vendor_id}/{assessment_id}/{sha256_hash}.{ext}`

**Security**:
- Server-side encryption: SSE-KMS with per-tenant KMS keys (Enterprise tier) or shared key (Standard/Business)
- Bucket policies: deny all except presigned URL access and service account
- Presigned URLs: 15-minute expiry for uploads, 1-hour expiry for downloads
- No direct bucket access from frontend -- all access through backend-generated presigned URLs

**Retention**:
- Versioning enabled for all evidence buckets (audit trail of document versions)
- Lifecycle policies: transition to S3 Glacier after 2 years (configurable per tenant)
- Deletion: soft-delete in PostgreSQL, hard-delete from S3 after retention period + 30-day grace

**Development**: MinIO as S3-compatible local storage with identical API surface.

### 5.5 Caching Strategy

| Data Category | Cache Layer | TTL | Invalidation Strategy |
|--------------|------------|-----|----------------------|
| User sessions | Redis | 30 min (configurable) | Explicit logout, session timeout |
| Tenant config | Redis + in-process `lru_cache` | 5 min | Event-driven (config change event) |
| Framework data | Redis + in-process | 1 hour | Version-triggered (framework update) |
| Vendor list/detail | Redis | 30-300 seconds | Write-through on mutation |
| Scoring configs | Redis + in-process | 5 min | Event-driven |
| Rate limit counters | Redis | Sliding window | Auto-expire |
| API responses | Redis | 30-300 seconds | Write-through |
| Static assets | CDN (Cloudflare/CloudFront) | 1 day | Deploy-triggered |

**Key naming convention**: `velora:{tenant_id}:{resource_type}:{resource_id}` to prevent cross-tenant cache collisions.

**Cache warming**: On tenant config change, proactively warm caches for scoring configs, role matrices, and framework metadata.

---

## 6. AI Architecture

### 6.1 RAG Pipeline for Framework Intelligence

```
                RAG PIPELINE FOR FRAMEWORK INTELLIGENCE
                ========================================

  INGESTION (one-time per framework version):

    Source Document (PDF / HTML / OSCAL JSON)
      |
      v
    [Parser Layer]
    - OSCAL JSON/XML: direct structured parsing (NIST SP 800-53, CSF 2.0, CIS)
    - PDF: Azure Document Intelligence (ISO 27001, DORA, NIS2 publications)
    - HTML: structure-preserving scraper (online regulatory texts)
      |
      v
    [Decomposition Engine]
    - Split into clause-level atomic units
    - Each clause: framework_id, version, section_path, clause_text,
      parent_clause_id, effective_date, keywords, applicability tags
      |
      v
    [Embedding Generation]
    - Model: text-embedding-3-large (1536 dimensions)
    - Batch processing via platform-core/llm-abstraction
    - Each clause gets one embedding vector
      |
      v
    [Dual Indexing]
    - pgvector: vector search (semantic similarity)
    - Typesense: keyword search + faceted filtering (framework, version, domain)
    - PostgreSQL: full structured data with JSONB metadata

  QUERY (per user request / AI pipeline):

    Input Query (e.g., "What controls cover encryption at rest?")
      |
      v
    [Query Embedding] -> text-embedding-3-large
      |
      v
    [Hybrid Search]
    - Vector similarity search (pgvector, top-50 candidates)
    - Keyword search (Typesense, top-50 candidates)
    - Merge and deduplicate
      |
      v
    [Re-Rank]
    - Cross-encoder model or LLM-based re-ranking
    - Score by relevance to original query
    - Select top-k (k=10 default) most relevant clauses
      |
      v
    [Context Assembly]
    - Top-k clauses + their metadata (framework, version, section path)
    - Parent clause context for hierarchical understanding
    - Cross-framework mappings for related clauses
      |
      v
    [LLM Generation]
    - Prompt: query + assembled context + output format instructions
    - Provider: via platform-core/llm-abstraction (Claude or GPT-4o)
    - Response includes: answer, citations (clause IDs), reasoning
      |
      v
    [Confidence Scoring] -> composite score (see 6.4)
      |
      v
    [Output] Response + sources + confidence + requires_human_review flag
```

### 6.2 Evidence Parsing Pipeline

```
                EVIDENCE PARSING PIPELINE
                =========================

    Document Upload (presigned S3 URL)
      |
      v
    [Intake + Validation]
    - File type check (PDF, DOCX, images)
    - Size limit (50MB default)
    - Virus scan (ClamAV)
    - SHA-256 hash for deduplication
    - Store raw file in S3 with tenant-prefixed key
      |
      v
    [Document Classification] (LLM)
    - Input: first 2 pages + filename + metadata
    - Output: document_type enum:
      soc2_type1 | soc2_type2 | iso27001_cert | pentest_report |
      vuln_scan | policy_document | insurance_cert | bcp_plan | other
    - Confidence score for classification
      |
      v
    [Layout Parsing] (Azure Document Intelligence)
    - Full document layout analysis
    - Table detection and reconstruction
    - Section/heading hierarchy extraction
    - Output: structured document representation (text blocks + tables + metadata)
      |
      v
    [Semantic Extraction] (LLM, type-specific prompts)

    For SOC 2 Type II:
    - Audit period (start date, end date)
    - Opinion type (unqualified / qualified / adverse / disclaimer)
    - Exceptions and qualifications (list with affected controls)
    - Individual control statuses (CC1.1-CC9.9 + optional TSC)
    - Complementary User Entity Controls (CUECs)
    - Subservice organizations and carve-out/inclusive method

    For ISO 27001 Certificate:
    - Certifying body (accredited?)
    - Certificate number
    - Scope description
    - Issue date, expiry date
    - Surveillance audit dates
    - Annex A controls in scope (Statement of Applicability mapping)

    For Penetration Test Report:
    - Testing firm and tester credentials
    - Test date and scope
    - Methodology (OWASP, PTES, OSSTMM)
    - Findings: critical/high/medium/low counts
    - Individual findings with CVSS scores
    - Remediation status per finding
      |
      v
    [Control Mapping] (LLM + embedding similarity)
    - Map extracted controls/findings to framework clauses
    - Coverage type: Full (proves compliance), Partial (partial evidence),
      Supportive (corroborating but not sufficient alone)
    - Confidence score per mapping
    - Cross-reference against questionnaire responses for consistency
    - Flag contradictions (e.g., vendor claims MFA enforced, SOC 2 notes exception)
      |
      v
    [Indexing]
    - Parsed content stored in evidence.parsed_content (JSONB)
    - Full-text indexed in Typesense
    - Embedding generated and stored in pgvector
    - Control mappings stored in evidence_control_mappings table
```

### 6.3 Vendor Enrichment Pipeline

```
  Trigger: vendor.created event OR scheduled re-enrichment

    Vendor Domain + Name
      |
      v
    [Parallel Enrichment Workers] (Temporal workflow, parallel activities)
      |
      +-- [Firmographics] Clearbit/ZoomInfo API
      |     -> industry, employee_count, revenue, HQ, founded, tech_stack
      |
      +-- [Security Rating] SecurityScorecard OR BitSight API
      |     -> external_score, risk_factors, last_updated
      |
      +-- [Certification] IAF CertSearch + CSA STAR scrape
      |     -> iso27001_status, soc2_status, star_level, validity_dates
      |
      +-- [Breach History] HIBP API
      |     -> breaches[], breach_dates, affected_data_types
      |
      +-- [Trust Center] Web scrape + AI extraction
      |     -> trust_center_url, published_docs[], security_page_content
      |
      +-- [DNS/SSL] Direct queries
            -> ssl_grade, cert_expiry, spf_dkim_dmarc, open_ports
      |
      v
    [AI Inference] (LLM)
    - Synthesize all enrichment data
    - Infer: risk signals, technology stack, data handling practices
    - Confidence score per inference
      |
      v
    [Enrichment Profile Assembly]
    - Merge all sources into structured vendor enrichment record
    - Store in vendor_enrichment_cache (JSONB)
    - Update vendor record with key fields
    - Trigger inherent risk tier recalculation
```

### 6.4 Confidence Scoring Architecture

Every AI output receives a composite confidence score from four signals:

```
  Composite Confidence = weighted_average(
    retrieval_relevance:  0.35   # Average cosine similarity of retrieved chunks
    source_coverage:      0.25   # Diversity of sources (multiple frameworks,
                                 #   multiple evidence types = higher)
    llm_self_assessment:  0.20   # LLM's own confidence in structured output
    historical_accuracy:  0.20   # Rolling accuracy for this query type
                                 #   (calibrated from human review feedback)
  )

  Classification:
    HIGH:   > 85%  -> Auto-approve with "AI-generated" badge
    MEDIUM: 60-85% -> Route to human review queue
    LOW:    < 60%  -> Flag as low-confidence, require human input
```

**Domain-specific thresholds** (overridable per tenant):

| Domain | Auto-Approve | Human Review | Reject |
|--------|-------------|-------------|--------|
| Questionnaire auto-fill | >85% | 60-85% | <60% |
| Evidence-to-control mapping | >90% | 70-90% | <70% |
| Vendor risk scoring | >80% | 50-80% | <50% |
| Cross-framework mapping | >90% | 70-90% | <70% |
| Report narrative generation | Always human review | N/A | N/A |

### 6.5 Human-in-the-Loop Routing

```
  AI Pipeline Output
    |
    v
  [Confidence Scorer] -> composite score + breakdown
    |
    +-- score >= auto_approve_threshold
    |     -> Auto-approve
    |     -> Tag output: "AI-generated, confidence: {score}%"
    |     -> Log decision + confidence for audit
    |     -> Proceed to downstream consumers
    |
    +-- score >= reject_threshold AND < auto_approve_threshold
    |     -> Route to review queue
    |     -> Assign to qualified reviewer (role-based, round-robin)
    |     -> Start SLA timer (default: 4 hours for P0/P1, 24 hours for P2+)
    |     -> Reviewer: Accept (as-is) | Modify (with changes) | Reject (with reason)
    |     -> Log reviewer decision + modifications for model improvement
    |     -> Modified outputs feed back into training signal
    |
    +-- score < reject_threshold
          -> Flag as "requires manual input"
          -> Do not present AI output as suggestion
          -> Route to human for original work
          -> Log failure mode for pipeline improvement
```

### 6.6 LLM Abstraction Layer

All LLM calls go through `platform-core/llm-abstraction`. No module makes direct LLM API calls.

```
  AI Module
    |
    v
  [platform-core/llm-abstraction]
    |
    +-- Provider Registry (Claude, GPT-4o, etc.)
    +-- Request Routing (by capability, cost, latency)
    +-- Failover (primary -> fallback provider on error)
    +-- Cost Tracking (per-tenant, per-pipeline token usage)
    +-- Rate Limiting (per-provider rate limits respected)
    +-- Response Caching (identical prompts within TTL window)
    +-- Audit Logging (every LLM call logged: input hash, output hash, tokens, cost, latency)
```

**Provider strategy for GA**:
- Primary: Anthropic Claude (stronger document analysis, better at structured extraction from SOC 2 reports)
- Fallback: OpenAI GPT-4o (widest enterprise acceptance, proven at scale)
- Embedding: OpenAI text-embedding-3-large (best cost/quality ratio for 1536-dim embeddings)
- Decision: both providers supported from day one via abstraction layer; customer can configure preference per tenant

---

## 7. Integration Architecture

### 7.1 SSO / SAML / OIDC

```
                    SSO AUTHENTICATION FLOW
                    =======================

  User Browser                 Velora                    Identity Provider
       |                         |                            |
       |-- GET /login ---------->|                            |
       |                         |-- Lookup tenant IdP ------>|
       |                         |   config from              |
       |                         |   tenant_configs           |
       |                         |                            |
       |<-- Redirect to IdP ----|                            |
       |                         |                            |
       |-- Authenticate ---------|--------------------------->|
       |                         |                            |
       |<-- SAML Assertion / ----|------- OIDC token --------|
       |    OIDC callback        |                            |
       |                         |                            |
       |-- POST /auth/callback ->|                            |
       |                         |-- Validate assertion/token |
       |                         |-- Extract: email, name,    |
       |                         |   groups, tenant_id        |
       |                         |-- Create/update user       |
       |                         |-- Issue Velora JWT         |
       |                         |   (access + refresh)       |
       |<-- Set JWT cookie ------|                            |
       |                         |                            |
```

**Supported protocols**: SAML 2.0 (python-saml), OIDC (authlib). Alternative: WorkOS as SSO abstraction for faster implementation of 25+ IdP integrations.

**SCIM 2.0**: Automated user provisioning/deprovisioning from IdP. When user is deactivated in Okta/Azure AD, Velora session is revoked and user is deactivated within minutes.

**Per-tenant IdP configuration**: stored in `tenant_configs.sso` (JSONB). Supports: IdP metadata URL, entity ID, certificate, attribute mapping (email, name, groups -> roles).

**Day-one support**: Okta, Microsoft Entra ID (Azure AD), Google Workspace, OneLogin.

### 7.2 External Rating APIs

```
  [Monitoring Scheduler] (BullMQ repeatable job, per vendor tier frequency)
    |
    v
  [Rating Fetch Worker]
    |
    +-- SecurityScorecard API
    |     GET /companies/{domain}/factors
    |     -> score (0-100), grade (A-F), 10 risk factor scores
    |     -> Rate limit: respect API tier limits
    |
    +-- BitSight API
    |     GET /ratings/v2/companies/{guid}
    |     -> rating (250-900), 25 risk vector grades
    |     -> Rate limit: respect API tier limits
    |
    v
  [Normalization Service]
    - SecurityScorecard: direct (already 0-100)
    - BitSight: linear normalization (250-900 -> 0-100)
    - Configurable normalization curves per tenant
    |
    v
  [Signal Processing]
    - Compare with previous score
    - Calculate delta
    - If delta > threshold: generate monitoring alert
    - Update vendor.external_rating
    - Trigger score recalculation
```

**Graceful degradation**: If rating API is unavailable, platform continues to function with stale rating data. Staleness indicator displayed in UI. Score recalculates without external rating component (weights redistributed).

### 7.3 Monitoring Feeds

| Feed | Integration Pattern | Polling Frequency |
|------|-------------------|-------------------|
| Breachsense / SpyCloud | REST API polling per vendor domain/email list | Tier 1: daily, Tier 2: weekly |
| Have I Been Pwned | REST API per vendor email domain | Tier 1: daily, Tier 2: weekly |
| Certificate Transparency | CT log subscription (Server-Sent Events) | Real-time |
| CVE/NVD | REST API polling + webhook | Daily |
| News/media | Google News API / RSS aggregation per vendor name | Tier 1: daily, Tier 2: weekly |
| Dark web intelligence | Commercial API (Recorded Future / Flashpoint) | Daily batch |
| DNS monitoring | Direct DNS queries per vendor domain | Tier 1: daily, Tier 2: weekly |

### 7.4 Email Delivery

**Abstraction**: Email provider abstracted behind `EmailProvider` interface. Tenant configures preferred provider in `tenant_configs.email`.

| Provider | Use Case | Configuration |
|----------|---------|---------------|
| SendGrid | Default for transactional email | API key per tenant or shared Velora key |
| AWS SES | High-volume, cost-sensitive | AWS credentials, verified domain |
| Custom SMTP | Enterprise with email policies | SMTP host, port, credentials, TLS |

**Email types**: assessment distribution, reminders (Day 7/14/21), alert notifications (P0-P2), report delivery, finding notifications, remediation requests.

**Sender identity**: configurable per tenant (from address, reply-to, display name). DKIM/SPF configured for Velora's sending domains.

### 7.5 Slack / Teams Webhooks

**Slack integration**:
- Incoming webhooks for alert notifications (configured per tenant channel)
- Slack App with interactive components: approve/reject buttons on assessment reviews, vendor risk summary commands
- Slash commands: `/velora vendor {name}` for quick vendor risk lookup

**Teams integration**:
- Incoming webhooks for alert notifications
- Teams Bot with Adaptive Cards for interactive approvals
- Connector card format for rich alert display

**Configuration**: per-tenant webhook URLs stored in `tenant_configs.integrations.slack` and `tenant_configs.integrations.teams`.

### 7.6 API Gateway and Rate Limiting

```
                    API REQUEST FLOW
                    ================

  Client Request
    |
    v
  [CDN / WAF] (Cloudflare)
    - DDoS protection
    - Bot detection
    - Geographic restrictions (if configured)
    |
    v
  [Load Balancer] (Kubernetes Ingress / ALB)
    - TLS termination (TLS 1.3)
    - Health checks
    - Session affinity (optional)
    |
    v
  [FastAPI Application]
    |
    +-- [CORS Middleware] Strict origin allowlisting per tenant
    +-- [Auth Middleware] JWT validation, tenant context injection
    +-- [Rate Limit Middleware] Redis-based, per-tenant configurable
    |     Default: 1000 req/min per tenant
    |     API keys: separate limits per key
    |     Burst allowance: 2x rate for 10-second window
    +-- [Request Validation] Pydantic model validation
    +-- [RLS Context] SET app.current_tenant_id
    +-- [Route Handler] Module-specific logic
    +-- [Response Serialization] Pydantic model -> JSON
    +-- [Audit Logging] Async log to audit_logs table
```

---

## 8. Security Architecture

### 8.1 Encryption

| Layer | Mechanism | Standard | Implementation |
|-------|-----------|----------|---------------|
| **In transit** | TLS 1.3 (minimum TLS 1.2) | Mandatory on all connections | Load balancer TLS termination, internal service mesh mTLS |
| **At rest (database)** | AES-256 | Mandatory | AWS RDS encryption (KMS-managed) or PostgreSQL TDE |
| **At rest (files)** | AES-256 | Mandatory | S3 SSE-KMS, per-tenant keys for Enterprise tier |
| **At rest (cache)** | AES-256 | Mandatory | Redis TLS + at-rest encryption |
| **Field-level (PII)** | AES-256-GCM | Recommended | Application-layer encryption for: vendor contact emails, phone numbers, API keys, credentials, PII fields |
| **Key management** | Envelope encryption | Mandatory | AWS KMS for data encryption keys. HashiCorp Vault for application secrets, API keys, database credentials. Key rotation: automatic annual, manual on-demand. |

### 8.2 RBAC / ABAC Hybrid

**RBAC baseline** -- 8 core roles:

| Role | Permissions Summary |
|------|-------------------|
| **Super Admin** | Full tenant administration, user management, integration config, all data access |
| **TPRM Manager** | Vendor management, assessment oversight, scoring config, reporting, approval authority |
| **Risk Analyst** | Conduct assessments, review AI outputs, manage findings, evidence review, vendor communication |
| **Vendor Relationship Manager** | Vendor onboarding/offboarding, communication, relationship management, limited assessment view |
| **Auditor** | Read-only access to all data + evidence + audit logs. No write permissions. |
| **Executive** | Dashboards, reports, high-level vendor views. No operational access. |
| **Vendor Portal User** | Portal-scoped: complete own assessments, upload evidence, view own findings. No internal access. |
| **API Service Account** | Scoped API access per integration. No UI access. |

**ABAC overlay** -- dynamic attribute-based policies:

```
  Examples:
  - resource.risk_level == "critical" && user.role != "ciso"
      -> DENY approve_vendor
  - resource.vendor.tier == 1 && action == "accept_risk"
      -> REQUIRE additional_approval("ciso")
  - time.is_business_hours == false && action == "bulk_export"
      -> DENY (unless user.role == "super_admin")
  - resource.data_classification == "pii" && user.department != "security"
      -> DENY view_raw_data
```

**Custom roles**: Admins can create custom roles combining permissions from base roles. Stored in `tenant_configs.roles.custom_roles`.

### 8.3 Audit Logging

```sql
-- Audit log table (partitioned by month)
audit_logs (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL,
    actor_id UUID NOT NULL,
    actor_type TEXT NOT NULL,        -- 'user' | 'system' | 'api_key' | 'ai_pipeline'
    action TEXT NOT NULL,            -- 'vendor.created' | 'assessment.submitted' | etc.
    resource_type TEXT NOT NULL,
    resource_id UUID,
    changes JSONB,                   -- {field: {old: value, new: value}}
    ip_address INET,
    user_agent TEXT,
    session_id UUID,
    timestamp TIMESTAMP DEFAULT NOW(),
    metadata JSONB                   -- additional context (e.g., ai_confidence, pipeline_id)
)
```

**Properties**:
- **Immutable**: no UPDATE or DELETE permissions granted on audit_logs. Append-only.
- **Partitioned**: by month for retention management and query performance
- **Retention**: 7 years default (financial services), configurable per tenant
- **Exportable**: JSON/CSV export for regulatory examination
- **Indexed**: by tenant_id + timestamp, by actor_id, by resource_type + resource_id
- **Every action logged**: create, read (sensitive resources), update, delete, approve, reject, export, login, logout, config change, AI pipeline execution

### 8.4 API Security

| Control | Implementation |
|---------|---------------|
| **Authentication** | JWT (RS256, 15-min access token + 7-day refresh token) |
| **API keys** | For system-to-system: scoped per tenant, rate-limited independently, rotatable |
| **Rate limiting** | Redis-based sliding window: 1000 req/min per tenant (default), configurable |
| **Input validation** | Pydantic v2 models on all endpoints. Zod on frontend. Reject malformed input. |
| **CORS** | Strict origin allowlisting per tenant. No wildcard origins. |
| **Request signing** | HMAC-SHA256 for outbound webhook deliveries |
| **IP allowlisting** | Optional per-tenant for Enterprise customers |
| **OWASP API Top 10** | Automated scanning in CI/CD pipeline (OWASP ZAP) |
| **Dependency auditing** | Dependabot + Snyk for vulnerability scanning on every PR |
| **Content Security Policy** | Strict CSP headers on all responses |
| **SQL injection** | Parameterized queries via SQLAlchemy ORM. No raw SQL from user input. |
| **XSS** | React's default escaping + DOMPurify for any rendered HTML content |

### 8.5 Tenant Isolation Guarantees

```
  Layer 1: Network
    - Tenant data never leaves the shared infrastructure boundary
    - Enterprise tier: dedicated VPC peering option

  Layer 2: Application
    - Auth middleware injects tenant_id from JWT on every request
    - No endpoint accepts tenant_id as a parameter (always from JWT)
    - Cross-tenant requests are architecturally impossible

  Layer 3: Database
    - RLS policies on every tenant-scoped table
    - PostgreSQL session variable set before every query
    - Automated RLS testing in CI/CD: test suite verifies tenant A
      cannot see tenant B's data across all tables

  Layer 4: Storage
    - S3 keys prefixed with tenant_id
    - Presigned URLs scoped to tenant's prefix
    - No listing permissions on bucket root

  Layer 5: Cache
    - All Redis keys prefixed with tenant_id
    - Key pattern: velora:{tenant_id}:{resource}:{id}
    - No wildcard key operations across tenants

  Layer 6: Search
    - Typesense collections filtered by tenant_id on every query
    - Tenant_id as mandatory filter parameter

  Layer 7: Verification
    - Penetration testing focused on tenant isolation (annual + on major changes)
    - Automated RLS regression tests in CI/CD
    - Bug bounty program with tenant isolation as top-priority scope
```

---

## 9. Deployment Architecture

### 9.1 Container and Orchestration

```
                    DEPLOYMENT ARCHITECTURE
                    =======================

  +------------------------------------------------------------------+
  |                      KUBERNETES CLUSTER                          |
  |                                                                  |
  |  Namespace: velora-production                                    |
  |  +-----------------------------------------------------------+  |
  |  |                                                           |  |
  |  |  [Ingress Controller]  (nginx-ingress or ALB Ingress)     |  |
  |  |    - TLS termination                                      |  |
  |  |    - Rate limiting (backup)                               |  |
  |  |    - Health check routing                                 |  |
  |  |                                                           |  |
  |  |  +--------------+  +--------------+  +---------------+   |  |
  |  |  | FastAPI Pods |  | Next.js Pods |  | Portal Pods   |   |  |
  |  |  | (API)        |  | (Web App)    |  | (Vendor)      |   |  |
  |  |  | replicas: 3+ |  | replicas: 2+ |  | replicas: 2+  |   |  |
  |  |  | HPA: cpu/mem |  | HPA: cpu/mem |  | HPA: cpu/mem  |   |  |
  |  |  +--------------+  +--------------+  +---------------+   |  |
  |  |                                                           |  |
  |  |  +--------------+  +--------------+  +---------------+   |  |
  |  |  | BullMQ       |  | Temporal     |  | Monitoring    |   |  |
  |  |  | Workers      |  | Workers      |  | Workers       |   |  |
  |  |  | (email, wh.) |  | (workflows)  |  | (feeds, alerts)|  |  |
  |  |  | replicas: 2+ |  | replicas: 2+ |  | replicas: 2+  |   |  |
  |  |  +--------------+  +--------------+  +---------------+   |  |
  |  |                                                           |  |
  |  +-----------------------------------------------------------+  |
  |                                                                  |
  |  Managed Services (outside K8s):                                 |
  |  +-------------------+  +-------------------+                    |
  |  | AWS RDS           |  | ElastiCache       |                    |
  |  | (PostgreSQL 16)   |  | (Redis 7)         |                    |
  |  | Multi-AZ          |  | Multi-AZ          |                    |
  |  | Read replicas     |  | Cluster mode      |                    |
  |  +-------------------+  +-------------------+                    |
  |                                                                  |
  |  +-------------------+  +-------------------+                    |
  |  | S3                |  | Temporal Server   |                    |
  |  | (Evidence store)  |  | (Temporal Cloud   |                    |
  |  | Versioning on     |  |  or self-hosted)  |                    |
  |  +-------------------+  +-------------------+                    |
  |                                                                  |
  |  +-------------------+                                           |
  |  | Typesense         |                                           |
  |  | (self-hosted on   |                                           |
  |  |  K8s or managed)  |                                           |
  |  +-------------------+                                           |
  +------------------------------------------------------------------+
```

**Container images**: Multi-stage Docker builds. Python (slim-bookworm base) for FastAPI + workers. Node (alpine) for Next.js. Distroless base images where possible for minimal attack surface.

**Resource allocation** (initial, tuned by HPA):

| Service | CPU Request | Memory Request | Replicas (min) |
|---------|------------|---------------|----------------|
| FastAPI API | 500m | 512Mi | 3 |
| Next.js Web | 250m | 256Mi | 2 |
| Portal | 250m | 256Mi | 2 |
| BullMQ Workers | 250m | 256Mi | 2 |
| Temporal Workers | 500m | 512Mi | 2 |
| Monitoring Workers | 250m | 256Mi | 2 |

### 9.2 CI/CD Pipeline

```
                    CI/CD PIPELINE (GitHub Actions)
                    ===============================

  Pull Request:
    [Lint] -> [Type Check] -> [Unit Tests] -> [Integration Tests]
      -> [Security Scan (Snyk/OWASP)] -> [RLS Isolation Tests]
      -> [Build Docker Images] -> [Deploy to Preview Environment]
      -> [E2E Tests (Playwright)] -> [PR Review]

  Merge to main:
    [Build] -> [Test (full suite)] -> [Security Scan]
      -> [Build + Push Docker Images (tagged: sha + latest)]
      -> [Deploy to Staging] -> [Smoke Tests] -> [Manual Approval Gate]
      -> [Deploy to Production (rolling update)]
      -> [Post-Deploy Smoke Tests] -> [Monitor for 30 min]

  Rollback:
    [Detect failure (automated health checks or manual)]
      -> [kubectl rollout undo] -> [Notify on-call]
```

**Security gates in CI/CD**:
- Dependency vulnerability scan (Snyk) -- block on critical/high
- OWASP ZAP API scan against staging
- Secret scanning (detect-secrets / git-secrets)
- Docker image scan (Trivy)
- RLS isolation test suite: verify tenant A cannot access tenant B data for every table
- License compliance check (no GPL in production dependencies)

### 9.3 Environment Strategy

| Environment | Purpose | Data | Infrastructure |
|------------|---------|------|---------------|
| **Local dev** | Developer workstation | Seed data, MinIO for S3 | Docker Compose (PostgreSQL, Redis, MinIO, Typesense, Temporal dev server) |
| **CI** | Automated testing | Ephemeral test data | GitHub Actions runners, ephemeral PostgreSQL |
| **Staging** | Pre-production validation, design partner demos | Anonymized production subset | Kubernetes (smaller replicas), same managed services |
| **Production** | Live customer traffic | Real customer data | Kubernetes (full HA), managed services (Multi-AZ) |

### 9.4 Monitoring and Observability

```
  Application Metrics (Prometheus):
    - Request latency (p50, p95, p99) per endpoint
    - Error rates per endpoint and module
    - Active sessions per tenant
    - Assessment processing throughput
    - Evidence parsing queue depth and latency
    - AI pipeline latency and confidence score distribution
    - LLM token usage and cost per tenant
    - Background job success/failure rates

  Infrastructure Metrics (Prometheus):
    - CPU, memory, disk per pod
    - PostgreSQL: connections, query latency, replication lag
    - Redis: memory usage, hit rate, eviction rate
    - S3: request latency, storage usage per tenant

  Dashboards (Grafana):
    - System health overview
    - Per-tenant usage and performance
    - AI pipeline performance (latency, confidence, human review rate)
    - Business metrics (assessments/day, vendors onboarded, evidence processed)

  Alerting (Prometheus AlertManager -> PagerDuty/Slack):
    - P0: Service down, data integrity issue, security incident
    - P1: Elevated error rate (>1%), latency spike (p95 > 2s), queue backlog
    - P2: Disk space warning, certificate expiry, dependency degradation
```

### 9.5 Logging

**Format**: Structured JSON on all application logs.

```json
{
  "timestamp": "2026-03-27T14:30:00.123Z",
  "level": "INFO",
  "service": "velora-api",
  "module": "assessment",
  "trace_id": "abc123",
  "tenant_id": "tenant-uuid",
  "user_id": "user-uuid",
  "action": "assessment.created",
  "message": "Assessment created for vendor",
  "vendor_id": "vendor-uuid",
  "assessment_type": "sig_core",
  "duration_ms": 45
}
```

**Stack**: Application -> structured JSON stdout -> Loki (via Promtail sidecar) -> Grafana for querying.

**Log correlation**: `trace_id` propagated through all service calls, background jobs, and LLM requests for end-to-end traceability.

**Retention**: 30 days hot (Loki), 1 year cold (S3 archive). Audit logs separate (7 years, PostgreSQL).

---

## 10. Key Architecture Decisions (ADRs)

### ADR-001: Modular Monolith over Microservices

**Context**: The team is building an AI-first TPRM platform. The product has 13 modules with significant cross-module data flows (e.g., assessment scoring requires data from Vendor, Evidence, Framework, and Monitoring modules). The team is small (Archeon agent workforce).

**Decision**: Adopt a modular monolith with clean module boundaries (interface-based, event-driven) that can be decomposed into microservices when scale demands it.

**Rationale**:
- Microservices at MVP stage introduce distributed system complexity (service discovery, distributed transactions, network latency, deployment orchestration) without corresponding scale benefits
- Cross-module joins and data aggregation (e.g., vendor profile = vendor + assessments + evidence + scores + alerts) are trivially efficient in a monolith and expensive across services
- Module boundaries enforced through code organization and interface contracts provide the same separation of concerns without network overhead
- Scale-out path is clear: Monitoring and AI modules are the first extraction candidates due to independent compute workloads

**Consequences**:
- Single deployable unit simplifies CI/CD, debugging, and operational management
- Module boundary discipline must be enforced through code review -- there is no network boundary to prevent shortcuts
- Database schema is shared -- modules must respect table ownership and use service interfaces for cross-module data
- When extraction is needed, the event bus and interface contracts make it mechanical

### ADR-002: PostgreSQL RLS over Schema-per-Tenant

**Context**: Multi-tenant SaaS platform targeting 500 tenants in Year 1, 5,000 in Year 3. Must provide strong tenant data isolation for regulated customers (financial services, healthcare).

**Decision**: Shared schema with Row-Level Security (RLS) as the default isolation model. Schema-per-tenant and database-per-tenant available as premium tiers.

**Rationale**:
- Shared schema with RLS is the most cost-efficient model at scale: one connection pool, one migration path, one backup strategy
- RLS provides strong isolation with minimal application code changes -- `tenant_id` on every table, one policy per table
- Schema-per-tenant introduces migration complexity (each tenant schema must be migrated independently) and connection pool explosion (PostgreSQL connections are expensive)
- Research confirms this is the industry-standard pattern for multi-tenant SaaS in 2025-2026
- Premium isolation tiers (schema/database-per-tenant) are available for Enterprise customers who require stronger isolation or data sovereignty

**Consequences**:
- Every tenant-scoped table must have `tenant_id` as a column with RLS policy -- enforced by migration linting
- Application must set `app.current_tenant_id` session variable before every query -- enforced by middleware
- RLS adds ~2-5% query overhead on simple queries (acceptable given the isolation benefit)
- Automated RLS testing in CI/CD catches any new table missing tenant isolation

### ADR-003: Temporal for Complex Workflows

**Context**: TPRM workflows are multi-step, long-running, and must be durable (vendor onboarding, assessment lifecycle, evidence parsing, remediation tracking). Some workflows span days or weeks (vendor response to questionnaire).

**Decision**: Temporal for complex durable workflows. BullMQ for simple async jobs (email, webhooks, cache operations).

**Rationale**:
- Temporal provides durable execution: workflows survive server restarts, provider outages, and infrastructure failures without losing state
- Code-based workflow definitions (Python SDK) express complex business logic better than YAML/JSON DSLs
- Complete event history for every workflow execution provides audit trail required by regulated customers
- Automatic retry with configurable policies for each activity (e.g., LLM call retries with backoff, API call retries)
- BullMQ handles simple fire-and-forget jobs without the overhead of Temporal's durable execution guarantees

**Consequences**:
- Temporal Server is an additional infrastructure component (Temporal Cloud or self-hosted)
- Developers must understand Temporal's programming model (activities, workflows, signals, queries)
- Workflow definitions become the single source of truth for business process logic, improving auditability
- Temporal's visibility store provides operational dashboards for workflow monitoring

### ADR-004: pgvector over Dedicated Vector Database at Start

**Context**: RAG pipeline requires vector storage for framework clause embeddings, evidence content embeddings, and vendor enrichment text. Initial scale: ~50,000-200,000 vectors (1536 dimensions).

**Decision**: Start with pgvector extension within PostgreSQL. Plan migration to Qdrant when vectors exceed 10M.

**Rationale**:
- pgvector eliminates a separate infrastructure component, reducing operational complexity and cost at MVP
- At startup scale (50K-200K vectors), pgvector with HNSW indexes provides adequate performance (<100ms for top-20 similarity search)
- Vectors co-located with metadata in PostgreSQL simplifies queries that combine vector similarity with attribute filtering (e.g., "find similar clauses in ISO 27001:2022 framework only")
- Qdrant (Rust-based, consistently fastest in benchmarks) is the clear scale-out choice when vectors exceed 10M and query latency becomes critical
- Vector search is abstracted behind a service interface (`VectorSearchService`) making the migration from pgvector to Qdrant a backend swap with no API changes

**Consequences**:
- PostgreSQL resource requirements increase with vector index size (memory for HNSW index)
- Vector queries share database connections with transactional queries -- monitor for contention
- Migration to Qdrant is planned as a Phase 3 activity, triggered by performance monitoring thresholds

### ADR-005: Config-Driven over Hardcoded Business Logic

**Context**: Every customer has different scoring models, workflow approval chains, escalation rules, notification preferences, risk thresholds, and questionnaire templates. The PRD explicitly requires "admin-configurable without code."

**Decision**: Store all business rules as structured data (JSON in PostgreSQL JSONB columns) validated against JSON Schema. Runtime engines evaluate stored rules, not compiled code.

**Rationale**:
- Leading GRC platforms (LogicGate, MetricStream, ServiceNow GRC) all use UI-driven configuration stored as structured data
- JSON Schema as single source of truth: validates on frontend (Zod/ajv), validates on backend (Pydantic), stores in PostgreSQL JSONB, generates dynamic UI forms
- Scoring formulas, escalation matrices, workflow stages, notification triggers, questionnaire templates -- all stored in `tenant_configs` and evaluated at runtime
- A lightweight custom rule engine (condition/action pairs in JSON) handles scoring, escalation, and notification rules. Temporal handles complex multi-step workflow orchestration.
- This approach means zero code deployments for business rule changes -- an admin changes a config in the UI and the change takes effect after the 5-minute cache TTL

**Consequences**:
- Rule engine must be thoroughly tested for correctness with complex configurations
- Performance: cached configs (Redis + in-process, 5-min TTL) ensure rule evaluation does not become a bottleneck
- Debugging: when a scoring result is unexpected, the full config + input + output must be traceable (logged)
- Default configs (per-industry templates) must be carefully designed so new tenants have a working system immediately

### ADR-006: FastAPI (Python) over Node.js (TypeScript)

**Context**: Backend language choice for an AI-first SaaS platform. Both Python and Node.js/TypeScript are viable.

**Decision**: FastAPI with Python 3.12+ as the primary backend.

**Rationale**:
- Python's AI/ML ecosystem is unmatched: LangChain, LlamaIndex, sentence-transformers, tiktoken -- every major LLM SDK is Python-first
- FastAPI's native async support is mandatory for I/O-heavy workloads (LLM inference calls, document parsing API calls, enrichment API calls)
- Pydantic v2 provides runtime type validation and automatic OpenAPI schema generation -- eliminating spec drift between API docs and implementation
- FastAPI generates OpenAPI 3.1 spec automatically, which is consumed to auto-generate TypeScript client for the Next.js frontend -- maintaining type safety across the stack
- Node.js/TypeScript would require bridging to Python for AI pipelines, introducing inter-process communication overhead

**Consequences**:
- Python's single-threaded nature requires careful async/await discipline and horizontal scaling via multiple Uvicorn workers
- CPU-intensive operations (embedding generation, score calculation) should use worker processes to avoid blocking the event loop
- Type safety is strong at API boundaries (Pydantic) but less strict than TypeScript within application logic -- mitigated by mypy type checking in CI

### ADR-007: Hybrid RBAC/ABAC over Pure RBAC

**Context**: The platform requires 8 core roles but also needs dynamic, context-dependent access control (e.g., critical vendors require CISO approval, bulk exports only during business hours).

**Decision**: RBAC as baseline (8 core roles with defined permissions) plus ABAC overlay for dynamic, context-sensitive policies.

**Rationale**:
- Pure RBAC for all dynamic rules would require an estimated 150+ roles to cover all combinations of context, resource type, and action
- RBAC + ABAC hybrid reduces this to 8 core roles + ~45 dynamic attribute policies
- ABAC policies are stored in tenant config (JSON rules) and evaluated by the Auth Module's policy engine at request time
- Research confirms this is the standard pattern for enterprise SaaS authorization
- Custom roles (admin-created) provide additional flexibility without code changes

**Consequences**:
- ABAC policy evaluation adds latency to authorization checks -- mitigated by in-process caching of policy definitions
- Policy conflicts (RBAC grants, ABAC denies) resolved by deny-wins precedence
- Policy debugging requires clear logging: every authorization decision logged with policy trace

---

## 11. Non-Functional Architecture

### 11.1 Performance Targets

| Metric | Target | Architecture Support |
|--------|--------|---------------------|
| API response time (p95, reads) | < 200ms | Redis caching (30-300s TTL), PostgreSQL composite indexes with tenant_id first, connection pooling (PgBouncer) |
| API response time (p95, writes) | < 500ms | Async side effects via event bus, synchronous path limited to validation + write |
| Dashboard load time | < 2 seconds (500 vendors) | Pre-aggregated dashboard data in Redis, incremental updates via SSE |
| Search latency | < 50ms | Typesense with per-tenant query-time field weighting |
| Evidence parsing throughput | 100-page SOC 2 in < 3 minutes | Temporal workflow with parallel activities: Azure Doc Intelligence (layout) + LLM (extraction) |
| Concurrent users per tenant | 50+ without degradation | Horizontal pod autoscaling, Redis session management, PostgreSQL connection pooling |
| Vendor portal page load | < 1 second | CDN for static assets, SSR for initial load, client-side for interactions |

### 11.2 Scalability Approach

| Dimension | Year 1 Target | Year 3 Target | Scaling Strategy |
|-----------|--------------|--------------|-----------------|
| Tenants | 500 | 5,000 | RLS scales linearly. Connection pooling (PgBouncer) prevents connection exhaustion. |
| Vendors per tenant | 1,000 | 10,000 | Composite indexes (tenant_id, id) ensure O(log n) query performance regardless of total vendor count. |
| Assessments/month | 10,000 | 500,000 | Temporal workflow workers scale horizontally. Assessment scoring is parallelizable. |
| Evidence documents | 500,000 | 10,000,000 | S3 scales infinitely. PostgreSQL table partitioning for evidence table at Year 2. pgvector -> Qdrant migration at Year 2-3. |
| Monitoring signals/day | 100,000 | 5,000,000 | BullMQ workers scale horizontally. Monitoring events table partitioned by week. Redis Streams for high-throughput event processing. |
| API requests/day | 1,000,000 | 50,000,000 | Horizontal pod autoscaling on FastAPI. CDN for static/cacheable. Redis caching reduces database load by 70-90%. |

**Database scaling path**:
1. **Year 1**: Single PostgreSQL primary + read replicas for reporting queries. PgBouncer for connection pooling.
2. **Year 2**: Table partitioning for high-volume tables (audit_logs by month, monitoring_events by week). Read replica routing for dashboard/report queries.
3. **Year 3**: Evaluate CockroachDB or Citus for horizontal sharding if single-node PostgreSQL limits are reached. Most likely not needed for projected volumes.

### 11.3 Availability Targets

| Metric | Target | Implementation |
|--------|--------|---------------|
| Uptime SLA | 99.9% (8.76 hours max downtime/year) | Multi-AZ deployment for all stateful services (RDS, ElastiCache, S3). Kubernetes pod anti-affinity across AZs. |
| RPO (Recovery Point Objective) | < 1 hour | Continuous WAL archiving to S3. Point-in-time recovery capability. |
| RTO (Recovery Time Objective) | < 4 hours | Automated failover for RDS Multi-AZ (~60s). Kubernetes self-healing for stateless pods (~30s). Temporal workflows resume automatically after recovery. |
| Backup frequency | Continuous WAL + daily snapshots | RDS automated backups (35-day retention). S3 cross-region replication for evidence files. |

### 11.4 Disaster Recovery

```
  PRIMARY REGION (e.g., us-east-1)              DR REGION (e.g., us-west-2)
  +----------------------------+                +----------------------------+
  | Kubernetes Cluster         |                | Kubernetes Cluster (cold)  |
  | - API pods (active)        |                | - API pods (scaled to 0)   |
  | - Worker pods (active)     |                | - Worker pods (scaled to 0)|
  +----------------------------+                +----------------------------+
  | RDS PostgreSQL (primary)   |   async repl   | RDS PostgreSQL (read repl) |
  | - Multi-AZ within region   |--------------->| - Promotable to primary    |
  +----------------------------+                +----------------------------+
  | ElastiCache Redis          |                | ElastiCache Redis          |
  | - Multi-AZ cluster         |                | - Standalone (DR)          |
  +----------------------------+                +----------------------------+
  | S3 Evidence Bucket         |  cross-region  | S3 Evidence Bucket (repl)  |
  | - Versioning enabled       |   replication  | - Versioning enabled       |
  +----------------------------+  ------------->+----------------------------+

  DR Activation (manual decision):
  1. Promote RDS read replica to primary in DR region
  2. Scale up Kubernetes pods in DR region
  3. Update DNS (Route 53 failover) to point to DR region
  4. Verify Temporal workflows resume from last checkpoint
  5. Estimated RTO: 2-4 hours
```

**Regular DR testing**: quarterly failover drill to DR region with documented results and improvement actions.

---

## Appendix A: PRD Feature Coverage Matrix

Every PRD feature requirement is mapped to the responsible module and architectural component.

| PRD Feature | ID | Module | Key Architectural Support |
|------------|-----|--------|--------------------------|
| Vendor inventory with bulk import | VLM-01 | Vendor | CSV parser, API integrations, Typesense indexing |
| AI-powered vendor enrichment | VLM-02 | Vendor + AI | Temporal enrichment workflow, parallel API calls |
| Inherent risk tiering engine | VLM-03 | Vendor + Scoring | Config-driven weighted factor calculation |
| Vendor profile management | VLM-04 | Vendor | Cross-module aggregation (scores, assessments, evidence, alerts) |
| Vendor onboarding workflow | VLM-05 | Vendor | Temporal onboarding workflow |
| Vendor offboarding workflow | VLM-06 | Vendor | Temporal offboarding workflow |
| Fourth-party mapping | VLM-07 | Vendor | Self-referential vendor relationships, graph queries |
| Automated vendor discovery | VLM-08 | Vendor | SSO/IdP log integration, financial system integration |
| Multi-entity vendor management | VLM-09 | Vendor + Tenant | Parent-subsidiary tenant model |
| Framework-aware questionnaire engine | ASM-01 | Assessment + Framework | Unified control library, template auto-selection |
| AI questionnaire pre-population | ASM-02 | Assessment + AI | LLM pre-fill pipeline with confidence scoring |
| Evidence parsing and extraction | ASM-03 | Evidence + AI | Azure Doc Intelligence + LLM extraction |
| Evidence-to-control mapping | ASM-04 | Evidence + Framework | Embedding similarity + LLM validation |
| Hybrid risk scoring | ASM-05 | Scoring | Config-driven multi-input composite score |
| Assessment distribution and tracking | ASM-06 | Assessment + Comms + Portal | SLA timer, reminder cadence engine |
| AI-assisted review queue | ASM-07 | Assessment + AI | Confidence-based HITL routing |
| Findings management | ASM-08 | Assessment | Auto-generated findings with severity-based SLAs |
| Remediation tracking | ASM-09 | Assessment + Portal | Temporal remediation workflow |
| Assessment scheduling | ASM-10 | Assessment | BullMQ scheduled jobs, event-triggered fast-track |
| Natural language risk Q&A | ASM-11 | AI | RAG pipeline + NL-to-SQL translation |
| Contract risk analysis | ASM-12 | Evidence + AI | LLM contract clause extraction |
| Framework library | FRM-01 | Framework | OSCAL JSON storage, clause-level decomposition |
| Cross-framework mapping engine | FRM-02 | Framework + AI | NIST OLIR imports + AI-assisted mapping |
| Unified control library | FRM-03 | Framework | Single control tagged with multiple framework sources |
| Framework versioning and diffing | FRM-04 | Framework | OSCAL catalog diff, affected assessment flagging |
| Custom framework support | FRM-05 | Framework | Admin-created frameworks with standard mappings |
| DORA Register of Information | FRM-06 | Framework + Reporting | Auto-generated from vendor data, regulatory export |
| Regulatory change intelligence | FRM-07 | Framework + Monitoring | RSS feed monitoring, OSCAL diffing |
| Configurable scoring engine | SCR-01 | Scoring | JSON rule storage, config-driven evaluation |
| Multi-dimensional risk scoring | SCR-02 | Scoring | 8 weighted factors, admin-configurable |
| Inherent-to-residual risk | SCR-03 | Scoring | Both subtraction and multiplication methods |
| External rating normalization | SCR-04 | Scoring | Configurable normalization curves |
| FAIR financial risk quantification | SCR-05 | Scoring | LEF x LM = ALE, what-if analysis |
| Score override with audit trail | SCR-06 | Scoring | Override record with justification, expiry |
| Portfolio-level risk aggregation | SCR-07 | Scoring + Reporting | Aggregate metrics, concentration analysis |
| Peer benchmarking | SCR-08 | Scoring | Anonymized cross-tenant aggregation |
| Multi-signal monitoring hub | MON-01 | Monitoring | Scheduled + event-driven, tier-based frequency |
| Alert engine with prioritization | MON-02 | Monitoring | P0-P4 classification, dedup, correlation |
| Vendor risk timeline | MON-03 | Monitoring | Chronological event aggregation |
| Trend analysis and prediction | MON-04 | Monitoring | 30/60/90-day trend detection, trajectory prediction |
| CVE impact correlation | MON-05 | Monitoring + Vendor | Tech stack matching from enrichment data |
| Vendor self-service portal | VPT-01 | Portal | White-labeled, tokenized access, no account required |
| Vendor trust profile | VPT-02 | Portal | Persistent profile, multi-customer sharing |
| Trust exchange marketplace | VPT-03 | Portal | Browse/consume trust profiles (P2) |
| Executive dashboard | RPT-01 | Reporting | Pre-aggregated data, real-time via SSE |
| Board-ready report generation | RPT-02 | Reporting + AI | Temporal workflow, AI narrative generation |
| Regulatory compliance reports | RPT-03 | Reporting + Framework | DORA, HIPAA, GDPR, PCI DSS exports |
| Operational analytics | RPT-04 | Reporting | Internal metrics aggregation |
| Scheduled report delivery | RPT-05 | Reporting + Comms | BullMQ scheduled jobs |
| Automated vendor outreach | COM-01 | Comms | Template engine, dynamic content, sender config |
| Internal notifications | COM-02 | Comms | Multi-channel (email, Slack, Teams, in-app, SMS) |
| In-app collaboration | COM-03 | Comms | Threaded comments, @mentions, audit trail |
| Escalation automation | COM-04 | Comms | Rule-based escalation engine, SLA timers |
| Multi-tenant isolation | ADM-01 | Auth + Tenant | RLS, tiered isolation options |
| RBAC with ABAC overlay | ADM-02 | Auth | 8 roles + dynamic attribute policies |
| SSO/SAML/OIDC | ADM-03 | Auth | SAML 2.0, OIDC, SCIM 2.0 |
| Complete audit trail | ADM-04 | Admin | Immutable, partitioned, 7-year retention |
| API-first architecture | ADM-05 | All modules | OpenAPI 3.1, auto-gen TypeScript client |
| Integration marketplace | ADM-06 | Admin | Pre-built integrations, webhook system |
| Data residency controls | ADM-07 | Tenant + Admin | Region-specific deployments |

---

## Appendix B: Technology Reference

```
COMPLETE TECHNOLOGY STACK
=========================

Layer            | Technology                    | Version
-----------------+-------------------------------+---------
Frontend         | Next.js 15 (App Router)       | 15+
                 | TypeScript                    | 5.4+
                 | Tailwind CSS                  | 3.4+
                 | shadcn/ui + Radix UI          | Latest
                 | Zod (runtime validation)      | 3.x
Backend          | FastAPI                       | 0.110+
                 | Python                        | 3.12+
                 | Pydantic v2                   | 2.x
                 | SQLAlchemy (async)            | 2.x
                 | Alembic (migrations)          | 1.13+
Database         | PostgreSQL + pgvector         | 16+ / 0.7+
Cache            | Redis                         | 7+
Search           | Typesense                     | 27+
Jobs (simple)    | BullMQ                        | 5.x
Jobs (complex)   | Temporal                      | Latest
File Storage     | AWS S3 / MinIO                | Latest
AI / LLM        | LangChain + LlamaIndex        | Latest
                 | via platform-core/llm-abstraction
LLM Providers    | Anthropic Claude (primary)    | Latest
                 | OpenAI GPT-4o (fallback)      | Latest
Embeddings       | text-embedding-3-large        | Latest
Doc Parsing      | Azure Document Intelligence   | Latest
                 | AWS Textract (fallback)       | Latest
Monitoring       | Prometheus + Grafana          | Latest
Logging          | Loki + Promtail               | Latest
CI/CD            | GitHub Actions                | N/A
Containers       | Docker + Kubernetes           | Latest
Infrastructure   | Terraform                     | 1.x
Key Management   | AWS KMS + HashiCorp Vault     | Latest
Security Scan    | Snyk + Trivy + OWASP ZAP      | Latest
SSO              | python-saml + authlib         | Latest
                 | (or WorkOS for SSO abstraction)
```

---

*End of High-Level Design. This document is the authoritative architecture reference for Velora TPRM. All implementation decisions must be consistent with this HLD. Deviations require an ADR in `decretum/decisions/` with Rachnika's review and Rudron's approval.*
