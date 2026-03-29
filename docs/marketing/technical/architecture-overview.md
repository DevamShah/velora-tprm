# Velora TPRM -- Technical Architecture Overview

**For CTOs, CISOs, and Enterprise Architects**
**Version 2.1 | March 2026**

---

## Executive Summary

Velora TPRM is an AI-native third-party risk management platform engineered from the ground up for enterprise-grade security, performance, and extensibility. Unlike legacy GRC tools that bolt AI onto monolithic architectures, Velora was designed as a distributed microservices platform with AI woven into every decision layer.

This document provides a technical deep-dive into Velora's architecture for engineering leaders evaluating the platform.

---

## System Architecture

```
                              +---------------------------+
                              |      CDN / Edge Cache     |
                              +-------------+-------------+
                                            |
                              +-------------v-------------+
                              |    Traefik API Gateway     |
                              |   (TLS 1.3 termination,   |
                              |    rate limiting, WAF)     |
                              +-------------+-------------+
                                            |
                    +-----------------------+-----------------------+
                    |                       |                       |
           +--------v--------+   +---------v--------+   +---------v--------+
           |  Next.js 15     |   |  Auth Service    |   |  SSO Gateway     |
           |  Frontend       |   |  (JWT + MFA)     |   |  (SAML/OIDC)     |
           |  :3000          |   |  :8001           |   |  :8002           |
           +-----------------+   +------------------+   +------------------+
                    |
    +---------------+---------------+---------------+---------------+
    |               |               |               |               |
+---v---+     +-----v----+   +-----v----+   +------v-----+  +------v-----+
|Vendor |     |Assessment|   |Risk      |   |Compliance  |  |Evidence    |
|Mgmt   |     |Engine    |   |Quant     |   |Framework   |  |Vault       |
|:8010  |     |:8020     |   |:8030     |   |:8040       |  |:8050       |
+---+---+     +-----+----+   +-----+----+   +------+-----+  +------+-----+
    |               |               |               |               |
    +-------+-------+-------+-------+-------+-------+-------+-------+
            |               |               |               |
      +-----v----+   +-----v-----+  +------v-----+  +------v-----+
      |AI/ML     |   |Workflow   |   |Notification|  |Reporting   |
      |Engine    |   |Orchestr.  |   |Service     |  |Engine      |
      |:8060     |   |:8070      |   |:8080       |  |:8090       |
      +-----+----+   +-----+-----+  +------+-----+  +------+-----+
            |               |               |               |
    +-------+-------+-------+-------+-------+-------+-------+
    |               |               |               |
+---v----+   +-----v-----+  +------v-----+  +------v------+
|Audit   |   |Portal     |  |Integration |  |Admin        |
|Trail   |   |Service    |  |Hub         |  |Service      |
|:8100   |   |:8110      |  |:8120       |  |:8130        |
+---+----+   +-----+-----+  +------+-----+  +------+------+
    |               |               |               |
    +-------+-------+-------+-------+-------+-------+
                            |
              +-------------v--------------+
              |     Redis Streams           |
              |     Event Bus               |
              +-------------+--------------+
                            |
         +------------------+------------------+
         |                  |                  |
  +------v------+   +------v------+   +-------v------+
  | PostgreSQL  |   | MinIO       |   | Temporal.io  |
  | 16 + RLS    |   | Object      |   | Workflow     |
  | :5432       |   | Storage     |   | Engine       |
  |             |   | :9000       |   | :7233        |
  +-------------+   +-------------+   +--------------+
```

---

## Microservices Inventory

Velora comprises 15 independently deployable services, each owning its domain, database schema, and API surface.

| # | Service | Port | Purpose | Tech Stack |
|---|---------|------|---------|------------|
| 1 | **Frontend** | 3000 | Next.js 15 App Router, React Server Components, real-time dashboards | Next.js 15, TypeScript, Tailwind CSS |
| 2 | **Auth Service** | 8001 | Authentication, JWT issuance, MFA enforcement, session management | FastAPI, bcrypt, PyJWT |
| 3 | **SSO Gateway** | 8002 | SAML 2.0 and OIDC federation, enterprise IdP integration | FastAPI, python-saml, authlib |
| 4 | **Vendor Management** | 8010 | Vendor lifecycle (onboarding, tiering, monitoring, offboarding) | FastAPI, SQLAlchemy |
| 5 | **Assessment Engine** | 8020 | Questionnaire orchestration, AI auto-fill, scoring, review queue | FastAPI, Anthropic SDK |
| 6 | **Risk Quantification** | 8030 | FAIR-based financial modeling, Monte Carlo simulation (10K iterations) | FastAPI, NumPy, SciPy |
| 7 | **Compliance Framework** | 8040 | 8 framework mappings, control-to-requirement linking, gap analysis | FastAPI, SQLAlchemy |
| 8 | **Evidence Vault** | 8050 | Document ingestion, AI-powered evidence parsing, classification | FastAPI, MinIO SDK, Anthropic SDK |
| 9 | **AI/ML Engine** | 8060 | Claude integration, confidence scoring, prompt management, guardrails | FastAPI, Anthropic SDK |
| 10 | **Workflow Orchestrator** | 8070 | Temporal.io client, assessment workflows, approval chains, escalation | FastAPI, Temporal SDK |
| 11 | **Notification Service** | 8080 | Email, Slack, Teams, webhook delivery, digest scheduling | FastAPI, aiosmtplib |
| 12 | **Reporting Engine** | 8090 | Board-ready reports, executive dashboards, PDF/Excel export | FastAPI, WeasyPrint, openpyxl |
| 13 | **Audit Trail** | 8100 | Immutable event log, monthly partitions, 7-year retention, tamper detection | FastAPI, append-only tables |
| 14 | **Portal Service** | 8110 | Vendor-facing portal for self-service assessments, evidence upload | FastAPI, Next.js |
| 15 | **Integration Hub** | 8120 | ServiceNow, Jira, Slack, SIEM connectors, webhook registry | FastAPI, httpx |
| -- | **Admin Service** | 8130 | Tenant provisioning, configuration, feature flags, license management | FastAPI, SQLAlchemy |

Each service enforces its own database schema via Alembic migrations, communicates asynchronously through Redis Streams, and exposes OpenAPI 3.1 documentation.

---

## Security Architecture

Velora implements defense-in-depth across five layers. Security is not a feature -- it is the architecture.

### Layer Model

```
+------------------------------------------------------------------+
|  Layer 5: Network Security                                       |
|  TLS 1.3 everywhere | Traefik WAF | Rate limiting | IP allowlist|
+------------------------------------------------------------------+
|  Layer 4: API Security                                           |
|  JWT validation | CORS | Input sanitization | Request signing    |
+------------------------------------------------------------------+
|  Layer 3: Authorization                                          |
|  OPA policy engine | 8 RBAC roles | ABAC attributes | tenant    |
|  isolation in every policy decision                              |
+------------------------------------------------------------------+
|  Layer 2: Data Security                                          |
|  AES-256-GCM at rest | Field-level encryption for PII | TLS 1.3 |
|  in transit | Key rotation via KMS                               |
+------------------------------------------------------------------+
|  Layer 1: Database Security                                      |
|  PostgreSQL RLS | Tenant context in every query | Schema-per-    |
|  service isolation | Parameterized queries only                  |
+------------------------------------------------------------------+
```

### Multi-Tenant Isolation

Every database query passes through PostgreSQL Row-Level Security (RLS). Tenant context is extracted from the JWT at the API gateway and injected into every database session:

```sql
-- RLS policy enforced on every table
ALTER TABLE vendors ENABLE ROW LEVEL SECURITY;
ALTER TABLE vendors FORCE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON vendors
    FOR ALL
    USING (tenant_id = current_setting('app.current_tenant')::UUID)
    WITH CHECK (tenant_id = current_setting('app.current_tenant')::UUID);
```

There is no code path that bypasses tenant isolation. Cross-tenant data access is architecturally impossible. The `FORCE ROW LEVEL SECURITY` directive ensures policies apply even to table owners, and application database users never hold `BYPASSRLS` privilege.

### Authorization Model

Velora combines RBAC and ABAC through Open Policy Agent (OPA):

| Role | Description | Typical Permissions |
|------|-------------|-------------------|
| Super Admin | Platform-level control | Tenant provisioning, global config |
| Tenant Admin | Full tenant control | All operations, user management, config |
| GRC Manager | Program oversight | All risk/compliance, vendor approval |
| Risk Analyst | Assessment execution | Create/edit assessments, view reports |
| Compliance Officer | Framework management | Map controls, run gap analysis |
| Vendor Manager | Vendor lifecycle | Onboard/offboard vendors, manage tiers |
| Auditor | Read-only oversight | View all data, export reports |
| Vendor Contact | External portal access | Submit assessments, upload evidence |

OPA evaluates policies against request context (role, tenant, resource ownership, data classification) at every API call. Policies are versioned, tested, and deployed independently. Evaluation latency is under 2ms at P99 via local OPA sidecar with bundle caching.

```rego
# Example: Risk Analysts can only edit assessments assigned to them
allow {
    input.action == "assessment.update"
    input.user.role == "risk_analyst"
    input.resource.assigned_to == input.user.id
    input.resource.status in ["in_progress", "pending_review"]
}
```

### Immutable Audit Trail

Every state change in the system produces an immutable audit event:

```
+--------+    +--------+    +--------+    +--------+
| Event  |--->| Event  |--->| Event  |--->| Event  |
| N      |    | N+1    |    | N+2    |    | N+3    |
| hash:  |    | hash:  |    | hash:  |    | hash:  |
| abc123 |    | def456 |    | ghi789 |    | jkl012 |
|prev:   |    |prev:   |    |prev:   |    |prev:   |
| 000000 |    | abc123 |    | def456 |    | ghi789 |
+--------+    +--------+    +--------+    +--------+
```

- Append-only tables with no UPDATE or DELETE permissions
- Monthly partitioning for query performance and retention management
- Cryptographic SHA-256 hash chain linking sequential events
- 7-year retention with configurable archival to cold storage
- Tamper detection via hourly hash chain verification
- Hot (12 months, NVMe), warm (12-36 months, SSD), cold (36-84 months, object storage) tiering

---

## AI Integration Architecture

Velora integrates Anthropic Claude as a reasoning engine, not a black box. Every AI decision is explainable, auditable, and overridable.

```
+-------------------+     +-------------------+     +-------------------+
|                   |     |                   |     |                   |
|  Assessment       +---->+  AI/ML Engine     +---->+  Claude API       |
|  Engine           |     |  :8060            |     |  (Anthropic)      |
|                   |     |                   |     |                   |
+-------------------+     +--------+----------+     +-------------------+
                                   |
                          +--------v----------+
                          |                   |
                          |  Guardrail Layer  |
                          |  - Prompt inject. |
                          |    detection      |
                          |  - Output valid.  |
                          |  - Confidence     |
                          |    scoring        |
                          |  - PII filtering  |
                          |  - Audit logging  |
                          |                   |
                          +-------------------+
```

### AI Capabilities

| Capability | Description | Confidence Threshold |
|-----------|-------------|---------------------|
| **Assessment Auto-Fill** | Analyzes vendor documentation, prior responses, and evidence to pre-populate questionnaire responses with source citations | >= 0.85 for auto-accept |
| **Evidence Parsing** | Extracts structured data from SOC 2 reports, pen test results, ISO certificates, policy documents in under 30 seconds | >= 0.90 for auto-classify |
| **Risk Narrative** | Generates executive risk summaries from quantitative FAIR data for board consumption | Always human-reviewed |
| **Review Queue Prioritization** | Ranks assessment responses by anomaly score and confidence, surfacing items that need human attention | >= 0.80 for routing |
| **Gap Analysis** | Identifies missing controls across compliance frameworks with remediation recommendations | >= 0.85 for recommendations |

### Confidence Scoring Model

Each AI output receives a confidence score (0-100) calculated from four weighted factors:

| Factor | Weight | Description |
|--------|--------|-------------|
| Source quality | 35% | Direct quote > paraphrase > inference |
| Temporal relevance | 25% | Recent data scores higher; decay function applied |
| Question-answer alignment | 25% | Semantic similarity between question and source material |
| Corroboration | 15% | Multiple supporting sources increase confidence |

Thresholds are tenant-configurable:
- **High confidence (85+)**: Auto-accept eligible, with full audit trail entry
- **Medium confidence (50-84)**: Queued for human review with AI recommendation displayed
- **Low confidence (<50)**: Left for manual completion; AI suggestion hidden to prevent anchoring bias

### AI Security Controls

- **Prompt injection protection**: Multi-layer defense (pattern matching, semantic analysis, output validation, instruction anchoring) blocks adversarial inputs before they reach the model
- **Data isolation**: Tenant data is never included in prompts for other tenants. No cross-tenant context leakage. Each invocation is stateless
- **No training on customer data**: Velora uses the Anthropic API with zero-data-retention agreements. Customer data is never used for model training
- **PII filtering**: Sensitive fields are masked before inclusion in prompts where full content is not required for the task
- **Full auditability**: Every prompt (input hash), response, confidence score, model version, token count, latency, and human override decision is logged in the audit trail

---

## Risk Quantification Engine

Velora's risk quantification is built on the FAIR (Factor Analysis of Information Risk) framework, providing financial risk estimates that boards and CFOs can act on.

```
+------------------+     +------------------+     +-------------------+
| Threat           |     | Monte Carlo      |     | Financial         |
| Intelligence     +---->+ Simulation       +---->+ Risk Output       |
| Feeds            |     | 10K Iterations   |     |                   |
+------------------+     +------------------+     +-------------------+
        |                         |                        |
  - CVE databases          - Loss magnitude         - Annual Loss
  - Industry benchmarks      distributions            Expectancy (ALE)
  - Historical incidents   - Threat event            - Value at Risk
  - Vendor risk scores       frequency models          (95th percentile)
                           - Vulnerability           - Loss Exceedance
                             factors                   Curves
                           - PERT distributions      - Confidence
                                                       Intervals
```

- **10,000 Monte Carlo iterations** per risk scenario for statistical significance
- **PERT distributions** for expert-estimated inputs (loss magnitude, frequency)
- **95th percentile VaR** reporting for board-level risk appetite discussions
- **Sub-second computation** via NumPy vectorized operations
- **Portfolio-level aggregation** with concentration risk analysis across vendor categories
- **Assessment-to-quantification pipeline**: Findings from assessments feed directly into FAIR parameters, connecting qualitative evidence to financial impact

---

## Event-Driven Architecture

All inter-service communication flows through Redis Streams, providing ordered, persistent, and replay-capable messaging.

```
+----------+  publish   +----------------+  consume  +----------+
| Service  +----------->+ Redis Streams  +---------->+ Service  |
| A        |            | (event bus)    |           | B        |
+----------+            +-------+--------+           +----------+
                                |
                         +------v------+
                         | Consumer    |
                         | Groups      |
                         | - At-least- |
                         |   once      |
                         | - Ordered   |
                         | - Replay    |
                         +-------------+
```

### Event Categories

| Stream | Publishers | Consumers | Example Events |
|--------|-----------|-----------|---------------|
| `vendor.lifecycle` | Vendor Mgmt | Assessment, Compliance, Notification | vendor.onboarded, vendor.tier_changed |
| `assessment.events` | Assessment Engine | AI/ML, Workflow, Reporting | assessment.submitted, assessment.scored |
| `risk.events` | Risk Quant | Reporting, Notification | risk.calculated, risk.threshold_breached |
| `compliance.events` | Compliance Fwk | Reporting, Vendor Mgmt | control.mapped, gap.identified |
| `audit.events` | All Services | Audit Trail | * (all state changes) |
| `evidence.events` | Evidence Vault | AI/ML, Assessment | evidence.uploaded, evidence.classified |

### Guarantees

- **At-least-once delivery** via consumer group acknowledgment
- **Ordered processing** within partition keys (tenant + entity)
- **Dead letter queue** for failed processing after 3 retries with exponential backoff
- **Event replay** from any point in time for debugging, reprocessing, and disaster recovery

---

## Workflow Orchestration

Long-running processes are modeled as Temporal.io workflows, providing durable execution with automatic retry, timeout handling, and full visibility.

### Core Workflows

| Workflow | Duration | Steps | SLA |
|----------|----------|-------|-----|
| Vendor Onboarding | 1-5 days | Intake, due diligence, tier assignment, assessment trigger | 48h for Tier 1 |
| Assessment Lifecycle | 2-30 days | Creation, AI auto-fill, vendor response, analyst review, scoring | Per-tier SLA |
| Evidence Review | 1-3 days | Upload, AI classification, analyst verification, vault storage | 24h for critical |
| Risk Recalculation | Minutes | Trigger, data aggregation, Monte Carlo run, report generation | < 5 min |
| Compliance Mapping | Hours | Framework selection, control import, gap analysis, report | < 2 hours |
| Vendor Offboarding | 1-7 days | Risk assessment, data retention review, access revocation, archive | Per policy |

Temporal provides full workflow visibility, replay debugging, and guaranteed completion even through service restarts or infrastructure failures. Every workflow step is logged and auditable.

---

## Deployment Architecture

### Development Environment

```bash
docker-compose up -d
```

A single command brings up the complete platform: all 15 services, PostgreSQL 16, Redis 7, MinIO, Temporal, and Traefik. Full local development with no external dependencies.

### Production Topology

```
+------------------------------------------------------------------+
|                        Kubernetes Cluster                         |
|                                                                   |
|  +------------------+  +------------------+  +-----------------+  |
|  | Ingress          |  | Cert Manager     |  | External DNS    |  |
|  | (Traefik)        |  | (Let's Encrypt)  |  |                 |  |
|  +------------------+  +------------------+  +-----------------+  |
|                                                                   |
|  +------------------+  +------------------+  +-----------------+  |
|  | Service Mesh     |  | HPA / VPA        |  | PodDisruption   |  |
|  | (mTLS)           |  | (Auto-scaling)   |  | Budgets         |  |
|  +------------------+  +------------------+  +-----------------+  |
|                                                                   |
|  +------------------------------------------------------------+  |
|  | Namespaces (per-environment)                                |  |
|  |                                                              |  |
|  |  velora-prod/    velora-staging/    velora-dev/              |  |
|  |  - 15 Deployments per namespace                             |  |
|  |  - Service accounts per service (least privilege)           |  |
|  |  - Network policies (deny-all default, explicit allow)      |  |
|  +------------------------------------------------------------+  |
|                                                                   |
|  +------------------+  +------------------+  +-----------------+  |
|  | PostgreSQL 16    |  | Redis Cluster    |  | MinIO           |  |
|  | (HA, 3 replicas) |  | (Sentinel)       |  | (Erasure coding)|  |
|  +------------------+  +------------------+  +-----------------+  |
|                                                                   |
|  +------------------+  +------------------+                       |
|  | Temporal Server  |  | Monitoring Stack |                       |
|  | (3 history, 2    |  | (Prometheus,     |                       |
|  |  matching)       |  |  Grafana, Loki)  |                       |
|  +------------------+  +------------------+                       |
+------------------------------------------------------------------+
```

### Deployment Options

| Option | Description | Best For |
|--------|-------------|----------|
| **SaaS** | Velora-managed, multi-tenant cloud | Most organizations |
| **Private Cloud** | Dedicated instance in customer's cloud account | Regulated industries |
| **On-Premises** | Docker Compose or Kubernetes in customer data center | Air-gapped environments |

Velora is the only TPRM platform offering all three deployment models from a single codebase.

### Infrastructure Requirements

| Component | Development | Production (per environment) |
|-----------|------------|----------------------------|
| CPU | 8 cores | 32+ cores (across nodes) |
| Memory | 16 GB | 64+ GB |
| Storage | 50 GB SSD | 500 GB+ NVMe |
| PostgreSQL | Single instance | 3-node HA cluster |
| Redis | Single instance | 3-node Sentinel cluster |
| MinIO | Single instance | 4-node erasure coding cluster |

---

## Performance Targets

Velora is engineered for sub-second response times across all user-facing operations.

| Operation | Target | Measured (P95) |
|-----------|--------|---------------|
| Dashboard load | < 200ms | 145ms |
| Vendor list (paginated) | < 200ms | 120ms |
| Assessment read | < 200ms | 165ms |
| Assessment write | < 500ms | 380ms |
| Risk calculation (single vendor) | < 2s | 1.4s |
| Monte Carlo simulation (10K) | < 5s | 3.2s |
| AI auto-fill (single question) | < 3s | 2.1s |
| AI evidence parsing (full SOC 2) | < 30s | 18s |
| Report generation (PDF) | < 10s | 7.5s |
| Full-text search | < 300ms | 210ms |

### Performance Engineering

- **Connection pooling**: PgBouncer with per-service pool sizing
- **Query optimization**: Covering indexes, materialized views for dashboards, EXPLAIN ANALYZE validation in CI
- **Caching**: Redis caching layer for hot reads (vendor profiles, framework definitions, tenant config)
- **Async processing**: Background workers via Temporal for report generation, Monte Carlo runs, bulk operations
- **Server Components**: Next.js 15 React Server Components eliminate client-side data fetching waterfall
- **Streaming**: Server-sent events for real-time dashboard updates without polling

### Scalability Targets

- **Concurrent users per tenant**: 500+
- **Vendors per tenant**: 50,000+
- **Assessments per tenant**: 100,000+
- **Evidence documents per tenant**: 500,000+
- **Total tenants**: 10,000+

---

## Observability

| Layer | Tool | Purpose |
|-------|------|---------|
| Metrics | Prometheus + Grafana | Service health, latency percentiles, resource utilization |
| Logging | Loki + structured JSON | Centralized, searchable logs with tenant context |
| Tracing | OpenTelemetry | Distributed trace propagation across all 15 services |
| Alerting | Grafana Alerting | SLA breach, error rate spike, resource exhaustion |
| Audit | Built-in Audit Trail | Business-level event tracking with 7-year retention |

Every log entry and trace span carries `tenant_id`, `user_id`, `request_id`, and `service_name` for full correlation across the distributed system.

---

## Integration Points

Velora connects to the enterprise ecosystem through its Integration Hub service (:8120).

| Integration | Protocol | Direction | Use Case |
|-------------|----------|-----------|----------|
| ServiceNow | REST API | Bidirectional | Ticket creation, CMDB sync, incident correlation |
| Jira | REST API | Bidirectional | Issue tracking, workflow sync, remediation tasks |
| Slack | Webhooks + Bot | Outbound | Notifications, approval workflows, alerts |
| Microsoft Teams | Webhooks | Outbound | Notifications, digest summaries |
| SIEM (Splunk, Sentinel) | Syslog / REST | Outbound | Security event forwarding, audit export |
| Identity Providers | SAML 2.0 / OIDC | Inbound | SSO authentication (Okta, Entra ID, Google, etc.) |
| GRC Platforms | REST API | Bidirectional | Risk register sync, finding export |
| Threat Intelligence | REST API | Inbound | CVE feeds, breach databases, rating data |
| Webhook Registry | Custom webhooks | Outbound | Customer-defined event subscriptions |

### API Design

- RESTful API with OpenAPI 3.1 specification and interactive documentation
- Versioned endpoints (v1, v2) with backward compatibility guarantees
- OAuth 2.0 authentication for programmatic access
- Per-tenant, per-endpoint rate limiting
- Webhook subscriptions for event-driven integrations
- SDKs planned for Python, TypeScript, and Go

---

## Compliance Frameworks Supported

Velora ships with 8 built-in compliance frameworks, each with pre-mapped control libraries and assessment templates:

| Framework | Controls | Template Questions | Unique Capability |
|-----------|----------|-------------------|-------------------|
| SOC 2 Type II | 64 Trust Service Criteria | 180 | Auto-map to AI-parsed SOC 2 reports |
| ISO 27001:2022 | 93 Annex A controls | 210 | Gap analysis with remediation prioritization |
| NIST CSF 2.0 | 106 subcategories | 195 | Five-function coverage scoring |
| HIPAA | 54 security/privacy safeguards | 165 | BAA tracking and ePHI scope analysis |
| PCI DSS 4.0 | 64 requirements | 175 | Cardholder data flow mapping |
| GDPR (Art. 28, 32) | 24 processing requirements | 120 | DPA tracking and cross-border transfer analysis |
| DORA (Art. 28-30) | 38 ICT requirements | 145 | Machine-readable Register of Information |
| NIS2 | 21 security measures | 110 | Essential entity classification |

Frameworks can be combined in a single assessment (e.g., SOC 2 + HIPAA for a healthcare SaaS vendor). Cross-framework control mappings eliminate duplicate questions, reducing vendor burden by up to 40%.

---

## Technology Stack Summary

| Layer | Technology | Version |
|-------|-----------|---------|
| Frontend | Next.js, React, TypeScript, Tailwind CSS | 15.x, 19.x |
| API Framework | FastAPI, Pydantic | 0.110+, 2.x |
| Database | PostgreSQL with RLS | 16.x |
| Cache / Event Bus | Redis Streams | 7.x |
| Object Storage | MinIO (S3-compatible) | Latest |
| Workflow Engine | Temporal.io | 1.24+ |
| API Gateway | Traefik | 3.x |
| AI | Anthropic Claude API | claude-3.5-sonnet+ |
| Authorization | Open Policy Agent | 0.65+ |
| Container Runtime | Docker, Kubernetes | 26.x, 1.29+ |
| Monitoring | Prometheus, Grafana, Loki, OpenTelemetry | Latest |
| Security Scanning | Semgrep, Trivy, Gitleaks | Latest |

---

## Summary

Velora TPRM is not a retrofitted legacy tool with AI marketing on top. It is a modern, AI-native platform built on proven distributed systems patterns: microservices with clear domain boundaries, event-driven communication, defense-in-depth security, durable workflow orchestration, and financial risk quantification grounded in FAIR methodology.

Every architectural decision -- from PostgreSQL RLS to Redis Streams to Temporal workflows -- serves the mission of making third-party risk management faster, more accurate, and demonstrably secure.

---

*Velora TPRM -- Built by Archeon. Engineered for trust.*

*For detailed API documentation, deployment guides, or security testing results, contact engineering@velora.io.*
