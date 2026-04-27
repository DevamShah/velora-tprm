---
tags:
  - archeon
  - forgeon
  - product
  - product-velora
---

# Velora TPRM -- Technical Architecture Research

> **Version:** 1.0.0
> **Date:** 2026-03-27
> **Status:** Research Complete
> **Confidence Baseline:** Sources marked [HIGH] have multiple corroborating references; [MEDIUM] have single authoritative source; [LOW] are extrapolated from adjacent domains.

---

## Table of Contents

1. [Recommended Tech Stack](#1-recommended-tech-stack)
2. [Multi-Tenant Architecture](#2-multi-tenant-architecture)
3. [Config-Driven Architecture](#3-config-driven-architecture)
4. [AI Integration Architecture](#4-ai-integration-architecture)
5. [Framework Intelligence System](#5-framework-intelligence-system)
6. [Evidence Management Architecture](#6-evidence-management-architecture)
7. [Continuous Monitoring Architecture](#7-continuous-monitoring-architecture)
8. [Security Architecture](#8-security-architecture)
9. [Scalability and Performance](#9-scalability-and-performance)
10. [Integration Architecture](#10-integration-architecture)
11. [Architecture Summary Diagram](#11-architecture-summary-diagram)
12. [Sources](#12-sources)

---

## 1. Recommended Tech Stack

### 1.1 Backend Framework

| Option | Language | Strengths | Weaknesses | Verdict |
|--------|----------|-----------|------------|---------|
| **FastAPI** | Python | Async-native, Pydantic validation, OpenAPI auto-gen, strong ML/AI ecosystem | Single-language limitation for compute-heavy ops | **RECOMMENDED** |
| Node/Express/NestJS | TypeScript | Large ecosystem, shared language with frontend | Weaker ML ecosystem, callback complexity | Runner-up |
| Go (Gin/Fiber) | Go | Raw performance, low memory | Smaller ORM ecosystem, verbose error handling | Microservice sidecar |
| Java/Spring Boot | Java | Enterprise-proven, strong typing | Heavyweight, slow iteration, verbose | Not recommended for AI-first |

**Recommendation: FastAPI (Python 3.12+) as primary backend** [HIGH]

Reasoning:
- FastAPI is the dominant choice for AI-first SaaS platforms in 2025-2026. Its native async support is mandatory when waiting for LLM inference, document parsing, and enrichment tasks to complete.
- Pydantic v2 provides end-to-end type safety and schema validation. OpenAPI schema auto-generation enables automatic TypeScript client generation for the frontend.
- Python's ML/AI ecosystem (LangChain, LlamaIndex, sentence-transformers, tiktoken) is unmatched. Every major LLM SDK is Python-first.
- FastAPI + Gunicorn/Uvicorn with workers scales horizontally. Celery or BullMQ handles async workloads.

Sources: [Next.js FastAPI Template](https://www.vintasoftware.com/blog/next-js-fastapi-template), [NightCoders Analysis](https://nightcoders.id/blogs/next-js-vs-fastapi-for-modern-saas-the-perfect-stack-for-mvps)

### 1.2 Frontend Framework

| Option | Strengths | Weaknesses | Verdict |
|--------|-----------|------------|---------|
| **Next.js 15 (App Router)** | SSR/SSG, React Server Components, excellent DX, Vercel ecosystem | Learning curve for App Router | **RECOMMENDED** |
| Angular 19 | Enterprise-standard, strong typing, opinionated | Heavier bundle, slower iteration | Enterprise alternative |
| SvelteKit | Performance, small bundles | Smaller ecosystem, fewer enterprise UI libs | Not mature enough |

**Recommendation: Next.js 15 with TypeScript** [HIGH]

Reasoning:
- React dominates enterprise SaaS UI development. Next.js adds SSR for SEO (marketing pages), API routes, middleware for auth, and React Server Components for performance.
- TypeScript is non-negotiable for enterprise-grade frontend. Combined with Zod for runtime validation, it provides end-to-end type safety when paired with FastAPI's OpenAPI schema.
- Component libraries: shadcn/ui + Tailwind CSS + Radix UI provide accessible, customizable enterprise components without vendor lock-in.

### 1.3 Database

| Option | Pattern | Strengths | Weaknesses | Verdict |
|--------|---------|-----------|------------|---------|
| **PostgreSQL 16+ with RLS** | Shared schema, row-level security | Cost-efficient, operationally simple, strong ecosystem | RLS overhead on complex queries | **PRIMARY** |
| PostgreSQL (schema-per-tenant) | Separate schema per tenant | Stronger isolation | Migration complexity, connection pooling | Premium tier option |
| MongoDB | Document store | Flexible schema for questionnaires | Weaker transactions, no RLS equivalent | Evidence metadata only |
| CockroachDB | Distributed SQL | Global distribution | Higher cost, operational complexity | Future consideration |

**Recommendation: PostgreSQL 16+ with Row-Level Security as primary datastore** [HIGH]

Reasoning:
- PostgreSQL with RLS is the industry-standard pattern for multi-tenant SaaS in 2025. The shared-schema-with-RLS approach (Pool model) saves the most on operational costs while providing strong data separation.
- `tenant_id` as a first-class column on every tenant-scoped table, with RLS policies using `current_setting('session.current_tenant_id')` for transparent isolation.
- PostgreSQL's JSONB columns handle semi-structured data (questionnaire responses, scoring configs, workflow definitions) without needing a separate document store.
- pgvector extension provides native vector search for RAG without a separate vector database at startup scale.

Sources: [Nile.dev RLS Guide](https://www.thenile.dev/blog/multi-tenant-rls), [AWS Multi-tenant RLS](https://aws.amazon.com/blogs/database/multi-tenant-data-isolation-with-postgresql-row-level-security/), [Simplyblock RLS Analysis](https://www.simplyblock.io/blog/underated-postgres-multi-tenancy-with-row-level-security/)

### 1.4 Search Engine

| Option | Strengths | Weaknesses | Verdict |
|--------|-----------|------------|---------|
| **Typesense** | Fast setup, query-time config, multi-tenant features, typo tolerance | Smaller ecosystem than ES | **RECOMMENDED** |
| Elasticsearch | Enterprise-proven, aggregations, log analytics | Operational complexity, resource-heavy | Overkill for search-only |
| Meilisearch | Best DX, sub-50ms search | Fewer enterprise features | Alternative to Typesense |

**Recommendation: Typesense for application search** [MEDIUM]

Reasoning:
- Typesense's standout feature is the ability to configure search parameters at query time rather than index creation, which is critical for multi-tenant TPRM where each tenant has different field weightings.
- Lower operational overhead than Elasticsearch. TPRM search volumes (vendors, controls, evidence) don't require ES-scale aggregation.
- If log analytics or complex aggregations are needed later, Elasticsearch can be added as a complementary system.

Sources: [Meilisearch ES vs Typesense Comparison](https://www.meilisearch.com/blog/elasticsearch-vs-typesense), [Typesense Comparison Docs](https://typesense.org/docs/overview/comparison-with-alternatives.html)

### 1.5 Background Jobs and Workflow Orchestration

| Component | Technology | Use Case |
|-----------|-----------|----------|
| **Simple async jobs** | BullMQ (Redis-backed) | Email sending, webhook delivery, cache invalidation |
| **Complex workflows** | Temporal | Multi-step vendor assessments, enrichment pipelines, evidence parsing workflows |
| **Scheduled tasks** | BullMQ Repeatable Jobs | Monitoring schedules, certificate expiry checks, report generation |

**Recommendation: Dual-layer -- BullMQ for simple jobs, Temporal for durable workflows** [HIGH]

Reasoning:
- BullMQ is the natural choice for a Node.js/TypeScript ecosystem adjacent to FastAPI. Redis-backed, lightweight, handles retries, rate limits, job delays, and concurrency control. However, BullMQ workers can also be written in Python.
- Temporal provides durable execution for complex, long-running workflows (vendor onboarding, multi-step enrichment, assessment orchestration). Its code-based workflow definitions express complex business logic better than YAML/JSON DSLs. Automatic pause/resume during provider outages and complete event history for audit trails.
- This dual-layer approach avoids over-engineering simple tasks while providing guarantees for high-value workflows.

Sources: [Temporal Workflow Principles](https://temporal.io/blog/workflow-engine-principles), [Pranav Prakash Queue Comparison](https://medium.com/@pranavprakash4777/modern-queueing-architectures-celery-rabbitmq-redis-or-temporal-f93ea7c526ec)

### 1.6 Caching

**Recommendation: Redis 7+ with hybrid caching pattern** [HIGH]

- **Distributed cache (Redis):** Session management, tenant config caching, API response caching, rate limiting.
- **In-process cache (node-cache or Python lru_cache):** Hot-path data like tenant settings, permission matrices, framework metadata.
- **Key naming convention:** `tenant:{tenant_id}:{resource_type}:{resource_id}` to prevent cross-tenant collisions.
- **TTL strategy:** Sessions 15-30min, tenant config 5min, framework data 1hr, vendor enrichment 24hr.
- Redis reduces API latency by up to 70-90% under load. The hybrid approach (Redis + in-process) reduces latency from 45ms to 2ms for hot-path reads.

Sources: [Redis Multi-Tenancy](https://redis.io/blog/multi-tenancy-redis-enterprise/), [Hybrid Caching Patterns](https://medium.com/@okan.yurt/multi-tenant-caching-strategies-why-redis-alone-isnt-enough-hybrid-pattern-f404877632e0)

### 1.7 File/Evidence Storage

**Recommendation: S3-compatible storage (AWS S3 or MinIO for self-hosted)** [HIGH]

- S3 for production: Server-side encryption (SSE-S3 or SSE-KMS), bucket policies per tenant prefix, presigned URLs for secure upload/download.
- MinIO for development and self-hosted enterprise deployments requiring data sovereignty.
- Bucket structure: `velora-evidence/{tenant_id}/{vendor_id}/{assessment_id}/{file_hash}.{ext}`
- Versioning enabled for evidence audit trail. Lifecycle policies for retention compliance.

### 1.8 Real-Time Communication

**Recommendation: Server-Sent Events (SSE) as primary, WebSockets for collaborative features** [MEDIUM]

- SSE for: Assessment status updates, enrichment progress, monitoring alerts, notification delivery. Simpler to implement, works through proxies, auto-reconnects.
- WebSockets for: Real-time collaborative editing (if needed), live dashboard updates with bidirectional communication.
- Implementation: FastAPI supports both natively. Frontend uses EventSource API for SSE.

### 1.9 Complete Stack Summary

```
Frontend:       Next.js 15 + TypeScript + Tailwind + shadcn/ui
Backend:        FastAPI (Python 3.12+) + Pydantic v2
Database:       PostgreSQL 16+ (RLS) + pgvector
Cache:          Redis 7+ (distributed) + in-process cache
Search:         Typesense
Jobs:           BullMQ (simple) + Temporal (complex workflows)
Storage:        AWS S3 / MinIO
Real-time:      SSE + WebSockets
AI/ML:          LangChain/LlamaIndex + OpenAI/Anthropic APIs
Vector:         pgvector (start) -> Qdrant (scale)
Monitoring:     Prometheus + Grafana
Logging:        Structured JSON -> ELK or Loki
CI/CD:          GitHub Actions + Docker + Kubernetes
```

---

## 2. Multi-Tenant Architecture

### 2.1 Recommended Pattern: Shared Schema with Row-Level Security

**Confidence: [HIGH]**

The Pool model (shared database, shared schema, tenant_id partitioning key) is recommended as the primary pattern. This provides the best cost-to-isolation ratio for a SaaS platform targeting hundreds to thousands of tenants.

#### Implementation Architecture

```
Request Flow:
  API Request -> Auth Middleware -> Extract tenant_id from JWT
    -> Set PostgreSQL session variable: SET app.current_tenant_id = '{tenant_id}'
    -> RLS policies automatically filter all queries
    -> Response (only tenant's data)
```

#### RLS Policy Pattern

```sql
-- Every tenant-scoped table has tenant_id as first column
CREATE TABLE vendors (
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    -- ...
);

-- RLS policy
ALTER TABLE vendors ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON vendors
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

-- Composite index for performance
CREATE INDEX idx_vendors_tenant ON vendors (tenant_id, id);
```

#### Tiered Isolation for Enterprise Customers

| Tier | Isolation Model | Use Case |
|------|----------------|----------|
| Standard | Shared schema + RLS | Most tenants, cost-efficient |
| Premium | Schema-per-tenant | Regulated industries needing stronger isolation |
| Enterprise | Database-per-tenant | Banks, government, data sovereignty requirements |

Sources: [AWS RLS Blog](https://aws.amazon.com/blogs/database/multi-tenant-data-isolation-with-postgresql-row-level-security/), [Nile.dev RLS](https://www.thenile.dev/blog/multi-tenant-rls), [Permit.io RLS Guide](https://www.permit.io/blog/postgres-rls-implementation-guide)

### 2.2 Tenant-Specific Customization

Each tenant gets a `tenant_config` JSONB column (or dedicated config table) storing:

```json
{
  "scoring": {
    "model": "weighted_average",
    "weights": { "security": 0.4, "compliance": 0.3, "financial": 0.2, "operational": 0.1 },
    "thresholds": { "critical": 0, "high": 40, "medium": 60, "low": 80 }
  },
  "workflows": {
    "assessment_approval": ["reviewer", "manager", "ciso"],
    "vendor_onboarding": ["requester", "procurement", "security"]
  },
  "roles": {
    "custom_roles": [
      { "name": "Regional Risk Manager", "permissions": ["view_vendors", "edit_assessments", "approve_vendors"] }
    ]
  },
  "escalation": {
    "rules": [
      { "condition": "risk_score < 40", "action": "escalate_to_ciso", "sla_hours": 24 }
    ]
  }
}
```

### 2.3 Compliance Considerations

- **SOC 2:** RLS provides demonstrable data isolation. Audit logs prove tenant data never crosses boundaries.
- **ISO 27001:** Encryption at rest (PostgreSQL TDE or AWS RDS encryption) + in-transit (TLS 1.3). Access controls documented per Annex A.
- **GDPR:** Tenant data deletion (right to erasure) is simplified with `DELETE FROM * WHERE tenant_id = ?` across all tables. Data residency handled via region-specific database deployments.

---

## 3. Config-Driven Architecture

### 3.1 JSON Schema-Driven Configuration

**Confidence: [HIGH]**

JSON Schema serves as the single source of truth for validation, UI generation, and runtime behavior. This is the dominant pattern for multi-tenant SaaS where every customer needs different data models, forms, and workflows.

#### Configuration Categories

| Category | Storage | Validation | UI Generation |
|----------|---------|------------|---------------|
| Scoring formulas | `tenant_configs.scoring` (JSONB) | JSON Schema | Dynamic form builder |
| Escalation matrices | `tenant_configs.escalation` (JSONB) | JSON Schema + business rules | Rule builder UI |
| Workflow stages | `workflow_templates` table | State machine schema | Visual workflow editor |
| Question sets | `question_banks` table | JSON Schema per question type | Form renderer |
| Roles/permissions | `roles` + `permissions` tables | Enum validation | Permission matrix UI |
| Notification rules | `notification_rules` table | JSON Schema | Trigger/action builder |
| Report templates | `report_templates` table | Template schema | Template editor |

#### Architecture Pattern

```
Admin configures in UI
  -> Frontend validates against JSON Schema (Zod/ajv)
  -> API validates against same schema (Pydantic)
  -> Stored in PostgreSQL JSONB
  -> Runtime engine reads config
  -> Config cached in Redis (5min TTL)
  -> Applied to tenant's data processing
```

### 3.2 Rule Engine Design

**Recommendation: Lightweight custom rule engine over heavy frameworks** [MEDIUM]

For TPRM-specific rules (scoring, escalation, notification triggers), a custom rule engine is preferable to generic engines like Drools or n8n:

```python
# Rule definition (stored as JSON in DB)
{
  "id": "escalate_critical_vendor",
  "trigger": "assessment.completed",
  "conditions": [
    {"field": "risk_score", "operator": "lt", "value": 40},
    {"field": "vendor.tier", "operator": "eq", "value": "critical"}
  ],
  "actions": [
    {"type": "escalate", "to": "ciso", "sla_hours": 4},
    {"type": "notify", "channel": "slack", "template": "critical_vendor_alert"},
    {"type": "set_status", "value": "requires_immediate_review"}
  ]
}
```

**Temporal for complex workflows** -- assessment approval chains, vendor onboarding sequences, and remediation tracking use Temporal's durable execution model with code-defined workflows.

### 3.3 How Leading GRC Tools Handle Configurability

Based on research of MetricStream, LogicGate, and ServiceNow GRC:
- **MetricStream:** Uses a low-code configuration layer with drag-and-drop workflow builders and configurable risk taxonomies.
- **LogicGate:** Named a Gartner Leader, uses a no-code platform where admins build workflows, forms, and scoring without engineering.
- **ServiceNow GRC:** Leverages the Now Platform's flow designer for configurable workflows, with GRC-specific modules layered on top.

The common pattern: **UI-driven configuration stored as structured data, not code changes.**

Sources: [Schema-Driven Platforms](https://peterhrynkow.com/ai/architecture/2025/02/01/schema-driven-platforms.html), [JSON Schema Versioning](https://medium.com/@ansujain/designing-a-robust-configuration-versioning-system-with-json-schema-validation-0f24d7ac53d3)

---

## 4. AI Integration Architecture

### 4.1 LLM Integration Points

**Confidence: [HIGH]**

| Capability | LLM Use | Input | Output | Confidence Target |
|-----------|---------|-------|--------|-------------------|
| Vendor Enrichment | Extract risk signals from public data | Company name, domain | Structured risk profile | 80%+ |
| Evidence Parsing | Extract controls from SOC reports, policies | PDF/DOCX documents | Structured control evidence | 85%+ |
| Questionnaire Auto-Fill | Pre-populate answers from evidence | Evidence corpus + questions | Draft answers + citations | 75%+ |
| Report Generation | Summarize assessment findings | Assessment data + template | Narrative risk report | 90%+ |
| Org Profile Inference | Infer company details from limited data | Company name, website | Industry, size, tech stack | 70%+ |
| Framework Mapping | Map controls across frameworks | Control description | Mapped control IDs | 85%+ |

### 4.2 RAG Architecture for Framework Intelligence

```
Document Ingestion Pipeline:
  Framework Document (PDF/HTML)
    -> Clause-Level Chunking (by section/article/control)
    -> Metadata Extraction (framework, version, section_id, effective_date)
    -> Embedding Generation (text-embedding-3-large or similar)
    -> Store in pgvector (vector + metadata + full text)

Query Pipeline:
  User Query / Evidence Text
    -> Generate Query Embedding
    -> Hybrid Search (vector similarity + keyword match via Typesense)
    -> Re-rank Results (cross-encoder or LLM-based)
    -> Context Assembly (top-k chunks + metadata)
    -> LLM Generation (with citations)
    -> Confidence Score Calculation
    -> Return Response + Sources + Confidence
```

### 4.3 Vector Database Strategy

**Recommendation: Start with pgvector, graduate to Qdrant at scale** [HIGH]

| Phase | Vector DB | Scale | Reasoning |
|-------|-----------|-------|-----------|
| MVP-Launch | pgvector | <5M vectors | Zero additional infrastructure. Lives in PostgreSQL. Good enough performance for framework clauses + evidence embeddings. |
| Growth | pgvector + HNSW indexes | 5-10M vectors | PostgreSQL's HNSW index support in pgvector 0.7+ provides good recall at scale. |
| Enterprise Scale | Qdrant (self-hosted) | 10M+ vectors | Rust-based, consistently fastest across benchmarks, sophisticated metadata filtering, production-proven at billion-vector scale. |

pgvector is the right starting point -- it eliminates operational complexity. Qdrant offers the best performance per dollar for self-hosted deployments at scale. Pinecone is viable if ops investment must be zero.

Sources: [Firecrawl Vector DB Comparison](https://www.firecrawl.dev/blog/best-vector-databases), [Shakudo Top 9 Vector DBs](https://www.shakudo.io/blog/top-9-vector-databases), [Athenic pgvector vs Others](https://getathenic.com/blog/pinecone-vs-weaviate-vs-qdrant-vs-pgvector)

### 4.4 Confidence Scoring Architecture

**Confidence: [HIGH]**

Every AI output receives a confidence score based on multiple signals:

```python
class AIConfidenceScorer:
    """
    Composite confidence score from multiple signals.
    """
    def calculate(self, response):
        scores = {
            "retrieval_relevance": self.avg_similarity_score(response.retrieved_chunks),
            "source_coverage": self.source_diversity_score(response.sources),
            "llm_self_assessment": self.parse_llm_confidence(response.raw_output),
            "historical_accuracy": self.lookup_accuracy_for_query_type(response.query_type),
        }
        composite = weighted_average(scores, weights={
            "retrieval_relevance": 0.35,
            "source_coverage": 0.25,
            "llm_self_assessment": 0.20,
            "historical_accuracy": 0.20,
        })
        return {
            "score": composite,
            "tier": self.classify(composite),  # HIGH (>85), MEDIUM (60-85), LOW (<60)
            "breakdown": scores,
            "requires_human_review": composite < 0.80,
        }
```

### 4.5 Human-in-the-Loop Patterns

**Confidence: [HIGH]**

Confidence-based routing is the core pattern. Decisions above threshold proceed autonomously; below threshold triggers human review.

| Domain | Auto-Approve Threshold | Human Review Range | Reject Threshold |
|--------|----------------------|-------------------|-----------------|
| Questionnaire auto-fill | >85% confidence | 60-85% | <60% |
| Evidence-to-control mapping | >90% confidence | 70-90% | <70% |
| Vendor risk scoring | >80% confidence | 50-80% | <50% |
| Report generation | Always human review | N/A | N/A |

**Review Queue Architecture:**
```
AI Output -> Confidence Scorer -> Router
  If confidence >= threshold:
    -> Auto-approve with "AI-generated" badge
    -> Log decision + confidence for audit
  If confidence < threshold:
    -> Route to review queue
    -> Assign to qualified reviewer (role-based)
    -> SLA timer starts
    -> Reviewer: Accept / Modify / Reject
    -> Feedback logged for model improvement
```

Organizations using smart escalation rules report that fewer than 10% of decisions require human intervention.

Sources: [Galileo HITL Guide](https://galileo.ai/blog/human-in-the-loop-agent-oversight), [AllDaysTech Review Queues](https://alldaystech.com/guides/artificial-intelligence/human-in-the-loop-ai-review-queue-workflows), [SoluLab Enterprise HITL](https://www.solulab.com/how-do-enterprises-implement-human-in-the-loop-frameworks/)

---

## 5. Framework Intelligence System

### 5.1 Framework Ingestion Architecture

**Confidence: [HIGH]**

```
Source Document (PDF/HTML/structured data)
  |
  v
[Parser Layer]
  - PDF: Azure Document Intelligence / AWS Textract
  - HTML: Custom scraper with structure preservation
  - Structured: Direct JSON/XML parsing (NIST, OSCAL)
  |
  v
[Decomposition Engine]
  - Split into clause-level units
  - Each clause gets: framework_id, version, section_path, clause_text,
    effective_date, supersedes, related_clauses
  |
  v
[Embedding + Indexing]
  - Generate embeddings for each clause
  - Index in pgvector (vector search)
  - Index in Typesense (keyword search)
  - Store full structured data in PostgreSQL
  |
  v
[Cross-Framework Mapper]
  - Use embeddings to find semantically similar clauses across frameworks
  - LLM-assisted mapping validation
  - Store mappings in control_mappings table with confidence scores
```

### 5.2 Supported Frameworks and Storage Model

| Framework | Structure | Clause Count (approx) | Update Frequency |
|-----------|-----------|----------------------|------------------|
| GDPR | Articles + Recitals | ~200 | Rare (amendments) |
| ISO 27001:2022 | Annex A Controls | 93 controls | ~10 year cycle |
| SOC 2 (TSC) | Trust Services Criteria | ~60 criteria | Annual updates |
| NIST CSF 2.0 | Functions/Categories/Subcategories | ~106 subcategories | ~5 year cycle |
| NIST 800-53 | Control Families | ~1000+ controls | Periodic revisions |
| HIPAA | Rules/Standards | ~50 standards | Rare |
| DORA | Articles | ~64 articles | New (2025) |
| NIS2 | Articles | ~46 articles | New (2024) |
| PCI DSS 4.0 | Requirements | ~250+ requirements | ~3 year cycle |

#### Data Model

```sql
CREATE TABLE frameworks (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,          -- 'ISO 27001'
    version TEXT NOT NULL,       -- '2022'
    effective_date DATE,
    status TEXT DEFAULT 'active', -- active, superseded, draft
    source_url TEXT,
    metadata JSONB
);

CREATE TABLE framework_clauses (
    id UUID PRIMARY KEY,
    framework_id UUID REFERENCES frameworks(id),
    section_path TEXT NOT NULL,  -- 'A.5.1' or 'Art. 25(1)'
    title TEXT,
    clause_text TEXT NOT NULL,
    parent_clause_id UUID REFERENCES framework_clauses(id),
    embedding vector(1536),     -- pgvector
    metadata JSONB,             -- keywords, applicability, etc.
    UNIQUE(framework_id, section_path)
);

CREATE TABLE control_mappings (
    id UUID PRIMARY KEY,
    source_clause_id UUID REFERENCES framework_clauses(id),
    target_clause_id UUID REFERENCES framework_clauses(id),
    mapping_type TEXT,          -- 'equivalent', 'partial', 'related'
    confidence FLOAT,
    verified_by UUID,           -- human verification
    verified_at TIMESTAMP,
    notes TEXT
);
```

### 5.3 Framework Versioning and Diff Detection

- Each framework version is a separate row in `frameworks` table with `supersedes` reference.
- When a new version is ingested, clause-level diff is computed (added/modified/removed).
- Modified clauses trigger re-evaluation of dependent control mappings and active assessments.
- Notifications sent to affected tenants.

### 5.4 Cross-Framework Mapping

ISO 27001 Annex A controls map closely to NIST CSF functions, SOC 2 Trust Services Criteria, and HIPAA standards. Key mapping overlaps:

- Access control appears across ISO 27001 (A.5/A.8), NIST CSF (PR.AC), SOC 2 (CC6), HIPAA (Access Controls)
- Incident response: ISO 27001 (A.5.24-28), NIST CSF (RS), SOC 2 (CC7), HIPAA (Incident Procedures)
- Asset management: ISO 27001 (A.5.9-13), NIST CSF (ID.AM), SOC 2 (CC6.1)

The system uses semantic similarity of clause embeddings + LLM validation to establish and maintain these mappings automatically, with human verification for high-stakes mappings.

Sources: [Ampcus ISO Mapping](https://www.ampcuscyber.com/blogs/iso-27001-mapping-with-security-standards/), [Thoropass SOC 2 Mapping](https://www.thoropass.com/blog/soc-2-mapping), [Censinet Control Mapping](https://censinet.com/perspectives/iso-27001-and-nist-csf-control-mapping-checklist)

### 5.5 Question Bank Generation

```
Framework Clause -> LLM Analysis -> Generated Questions
  Input:  "A.8.9: Configuration management -
           Configurations, including security configurations,
           of hardware, software, services and networks
           shall be established, documented, implemented,
           monitored and reviewed."

  Output: [
    {
      "question": "Describe your configuration management process for
                   hardware, software, services, and networks.",
      "type": "open_text",
      "evidence_expected": ["Configuration Management Policy",
                           "CMDB screenshots", "Change management records"],
      "scoring_guidance": "Look for: documented process, coverage of all
                          asset types, monitoring mechanism, review cadence"
    },
    {
      "question": "Do you maintain a Configuration Management Database (CMDB)?",
      "type": "yes_no_na",
      "follow_up_if_yes": "Provide evidence of CMDB completeness and accuracy."
    }
  ]
```

---

## 6. Evidence Management Architecture

### 6.1 Document Ingestion Pipeline

**Confidence: [HIGH]**

```
Upload (presigned S3 URL)
  |
  v
[Intake Service]
  - Validate file type, size, virus scan (ClamAV)
  - Generate file hash (SHA-256) for deduplication
  - Store raw file in S3 with tenant prefix
  - Create evidence record in PostgreSQL
  |
  v
[Classification Service] (async via Temporal workflow)
  - Detect document type: SOC report, policy, certificate, questionnaire response
  - Extract metadata: date, issuer, subject, validity period
  |
  v
[Parsing Service]
  - PDF/DOCX -> Azure Document Intelligence (recommended) or AWS Textract
  - Images -> OCR pipeline
  - Structured data -> Direct parsing
  |
  v
[Extraction Service]
  - LLM-powered extraction of:
    - Control statements and their status
    - Audit findings and exceptions
    - Certificate validity dates
    - Policy effective dates and review dates
  |
  v
[Mapping Service]
  - Map extracted controls to framework clauses
  - Generate evidence-to-control linkages with confidence scores
  - Flag gaps where expected evidence is missing
  |
  v
[Indexing Service]
  - Full-text index in Typesense
  - Embedding generation for semantic search
  - Store in pgvector for RAG retrieval
```

### 6.2 OCR and Document Parsing Comparison

| Service | Strengths | Best For | Cost Model |
|---------|-----------|----------|------------|
| **Azure Document Intelligence** | Best layout analysis, table extraction, prebuilt models for invoices/receipts | SOC reports with complex tables | Per-page pricing |
| AWS Textract | Strong AWS integration, async batch processing, HIPAA-eligible | AWS-native deployments | Per-page pricing |
| Google Document AI | Strong multi-language support | International documents | Per-page pricing |
| Tesseract (open source) | Free, self-hosted, good for simple documents | Cost-sensitive, simple PDFs | Free (compute cost) |

**Recommendation: Azure Document Intelligence as primary parser** [MEDIUM]

Reasoning: SOC 2 reports, ISO certificates, and policy documents contain complex layouts with tables, headers, and structured sections. Azure's Document Intelligence leads in layout understanding and table reconstruction. AWS Textract is the fallback for AWS-native deployments.

Sources: [WindowsForum OCR Comparison](https://windowsforum.com/threads/document-intelligence-in-2025-ocr-platforms-compared-for-idp.387634/), [InfoQ Document Processing](https://www.infoq.com/articles/ocr-ai-document-processing/)

### 6.3 Evidence Versioning and Expiry

```sql
CREATE TABLE evidence (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL,
    vendor_id UUID NOT NULL,
    file_name TEXT NOT NULL,
    file_hash TEXT NOT NULL,        -- SHA-256 for deduplication
    s3_key TEXT NOT NULL,
    document_type TEXT,             -- 'soc2_report', 'iso_cert', 'policy', etc.
    version INT DEFAULT 1,
    previous_version_id UUID REFERENCES evidence(id),
    valid_from DATE,
    valid_until DATE,               -- expiry tracking
    expiry_notified BOOLEAN DEFAULT FALSE,
    parsing_status TEXT DEFAULT 'pending', -- pending, processing, completed, failed
    parsed_content JSONB,           -- extracted structured data
    embedding vector(1536),
    uploaded_by UUID,
    uploaded_at TIMESTAMP DEFAULT NOW(),
    metadata JSONB
);

-- Expiry monitoring query
CREATE INDEX idx_evidence_expiry ON evidence (tenant_id, valid_until)
    WHERE valid_until IS NOT NULL AND valid_until > NOW();
```

- **Version chain:** Each new upload references `previous_version_id`, creating a full audit trail.
- **Expiry monitoring:** Background job checks `valid_until` dates daily. Alerts at 90, 60, 30, 14, 7 days before expiry.
- **SOC report parsing:** Specialized extractor identifies Type I vs Type II, opinion period, exceptions/qualifications, and specific control descriptions.

---

## 7. Continuous Monitoring Architecture

### 7.1 Monitoring Data Sources

| Source Type | Examples | Update Frequency | Integration Method |
|------------|---------|-----------------|-------------------|
| Breach monitoring | Breachsense, SpyCloud, Have I Been Pwned | Real-time / daily | API polling + webhooks |
| Dark web monitoring | Cyble, SpyCloud, Breachsense | Daily | API |
| Security ratings | BitSight, SecurityScorecard | Daily / weekly | API |
| News/threat feeds | MITRE ATT&CK, CVE, NVD, RSS | Real-time | API + RSS ingestion |
| Certificate monitoring | Certificate Transparency logs | Real-time | CT log subscription |
| Domain/DNS monitoring | Custom or third-party | Hourly | DNS queries |
| Financial signals | D&B, public filings | Weekly/monthly | API |

### 7.2 Architecture

```
[Scheduler] (BullMQ Repeatable Jobs)
  |
  v
[Monitoring Workers] (per source type)
  - Breach API check for vendor domains/emails
  - Security rating fetch
  - News aggregation (vendor name + "breach" / "vulnerability" / "incident")
  - Certificate expiry check
  - DNS change detection
  |
  v
[Signal Processing Engine]
  - Deduplicate signals
  - Enrich with context (affected vendor, impact assessment)
  - Score severity (critical/high/medium/low/info)
  - Match to tenant's vendor portfolio
  |
  v
[Alert Router]
  - Apply tenant's escalation rules
  - Route to appropriate stakeholders
  - Create investigation ticket
  - Update vendor risk score
  - Log in monitoring history
  |
  v
[Notification Delivery]
  - Email (SendGrid/SES)
  - Slack/Teams webhook
  - In-app notification (SSE)
  - SMS for critical alerts (Twilio)
```

### 7.3 Scheduled vs Event-Driven Monitoring

| Pattern | Use Case | Implementation |
|---------|----------|----------------|
| Scheduled polling | Security ratings, financial data, certificate checks | BullMQ repeatable jobs (configurable per vendor tier) |
| Event-driven | Breach notifications, CVE alerts, news alerts | Webhook receivers + streaming API consumers |
| Hybrid | Dark web monitoring (daily poll + real-time alerts from providers) | Scheduled baseline + webhook overlay |

**Vendor tier-based scheduling:**
- Critical vendors: 4-hour monitoring cycle
- High-risk vendors: Daily monitoring
- Standard vendors: Weekly monitoring
- Low-risk vendors: Monthly monitoring

Sources: [Breachsense](https://www.breachsense.com/), [BitSight Continuous Monitoring](https://www.bitsight.com/products/continuous-monitoring), [SpyCloud](https://spycloud.com/use-case/dark-web-monitoring/)

---

## 8. Security Architecture

### 8.1 Encryption

**Confidence: [HIGH]**

| Layer | Mechanism | Standard |
|-------|-----------|----------|
| In transit | TLS 1.3 (minimum TLS 1.2) | Mandatory |
| At rest (database) | PostgreSQL TDE or AWS RDS encryption (AES-256) | Mandatory |
| At rest (files) | S3 SSE-KMS with per-tenant keys (optional) | Mandatory |
| At rest (cache) | Redis TLS + at-rest encryption | Mandatory |
| Application-level | Field-level encryption for PII (AES-256-GCM) | Recommended |
| Key management | AWS KMS or HashiCorp Vault | Mandatory |

### 8.2 RBAC/ABAC Hybrid Implementation

**Recommendation: RBAC as baseline with ABAC for dynamic policies** [HIGH]

```
Permission Resolution:
  User -> Roles (RBAC baseline)
    -> Role grants base permissions (view_vendors, edit_assessments, etc.)

  + Attributes (ABAC overlay)
    -> user.department == "security" -> grant approve_vendor
    -> resource.risk_level == "critical" && user.role != "ciso" -> deny approve
    -> time.is_business_hours == false && action == "export" -> deny
```

This hybrid reduces the number of required roles from an estimated 150 (pure RBAC) to approximately 12 core roles + 45 dynamic attributes.

**Core Roles for TPRM:**
1. Super Admin (tenant-level)
2. TPRM Manager
3. Risk Analyst
4. Vendor Relationship Manager
5. Auditor (read-only + evidence access)
6. Executive (dashboards + reports)
7. Vendor Portal User (external)
8. API Service Account

### 8.3 Audit Logging Architecture

```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    actor_id UUID NOT NULL,
    actor_type TEXT NOT NULL,        -- 'user', 'system', 'api_key'
    action TEXT NOT NULL,            -- 'vendor.created', 'assessment.submitted', etc.
    resource_type TEXT NOT NULL,
    resource_id UUID,
    changes JSONB,                   -- {field: {old: x, new: y}}
    ip_address INET,
    user_agent TEXT,
    session_id UUID,
    timestamp TIMESTAMP DEFAULT NOW(),
    metadata JSONB
);

-- Partition by month for retention management
CREATE TABLE audit_logs_2026_03 PARTITION OF audit_logs
    FOR VALUES FROM ('2026-03-01') TO ('2026-04-01');

-- Immutability: no UPDATE or DELETE permissions granted
-- Retention: 7 years for financial services, configurable per tenant
```

Audit logs must be immutable, encrypted, and retained according to regulatory requirements. The append-only design with time-based partitioning supports efficient querying and compliant retention policies.

### 8.4 API Security

| Control | Implementation |
|---------|---------------|
| Authentication | JWT (short-lived access tokens) + refresh tokens |
| API keys | For system-to-system integration, scoped per tenant |
| Rate limiting | Redis-based, per-tenant configurable (default: 1000 req/min) |
| Input validation | Pydantic models (backend) + Zod schemas (frontend) |
| OWASP API Top 10 | Automated scanning in CI/CD pipeline |
| CORS | Strict origin allowlisting per tenant |
| Request signing | HMAC-SHA256 for webhook deliveries |
| IP allowlisting | Optional per-tenant for enterprise customers |

### 8.5 SOC 2 Compliance for the Platform

Key requirements the platform must satisfy:

- **CC1 (Control Environment):** Documented security policies, org structure, roles
- **CC2 (Communication):** Security awareness, incident notification procedures
- **CC3 (Risk Assessment):** Formal risk assessment process, vulnerability management
- **CC5 (Control Activities):** Access controls, change management, operations monitoring
- **CC6 (Logical Access):** MFA enforcement, SSO integration, principle of least privilege
- **CC7 (System Operations):** Monitoring, incident response, disaster recovery
- **CC8 (Change Management):** Code review, CI/CD controls, deployment procedures
- **CC9 (Risk Mitigation):** Vendor management, insurance, business continuity

SOC 2 adoption surged 40% in 2024 -- it is now the price of admission for enterprise SaaS deals.

Sources: [TryComp SOC 2 Checklist](https://trycomp.ai/soc-2-checklist-for-saas-startups), [CertPro RBAC Guide](https://certpro.com/role-based-access-control/), [Logto Enterprise-Ready](https://blog.logto.io/enterprise-ready)

---

## 9. Scalability and Performance

### 9.1 Expected Data Volumes (Enterprise TPRM)

| Entity | Per Tenant (Medium) | Per Tenant (Large Enterprise) | Platform Total (1000 tenants) |
|--------|--------------------|-----------------------------|------------------------------|
| Vendors | 200-500 | 5,000-50,000 | 5M-50M |
| Assessments/year | 500-2,000 | 10,000-100,000 | 10M-100M |
| Evidence files | 1,000-5,000 | 50,000-500,000 | 50M-500M files |
| Evidence storage | 10-50 GB | 500 GB - 5 TB | 500 TB - 5 PB |
| Framework clauses | Shared (~5,000) | Shared + custom (~10,000) | ~50,000 |
| Monitoring events/day | 1,000-5,000 | 50,000-500,000 | 50M-500M/day |
| Audit log entries/day | 5,000-20,000 | 100,000-1,000,000 | 100M-1B/day |

### 9.2 Database Indexing Strategy

```sql
-- Composite indexes with tenant_id first (RLS performance)
CREATE INDEX idx_vendors_tenant_name ON vendors (tenant_id, name);
CREATE INDEX idx_assessments_tenant_status ON assessments (tenant_id, status, created_at DESC);
CREATE INDEX idx_evidence_tenant_vendor ON evidence (tenant_id, vendor_id, document_type);

-- Partial indexes for common queries
CREATE INDEX idx_assessments_active ON assessments (tenant_id, due_date)
    WHERE status IN ('in_progress', 'pending_review');

CREATE INDEX idx_evidence_expiring ON evidence (tenant_id, valid_until)
    WHERE valid_until IS NOT NULL
    AND valid_until BETWEEN NOW() AND NOW() + INTERVAL '90 days';

-- GIN indexes for JSONB queries
CREATE INDEX idx_vendor_metadata ON vendors USING GIN (metadata);

-- HNSW index for vector search
CREATE INDEX idx_clause_embedding ON framework_clauses
    USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);

-- Table partitioning for high-volume tables
-- audit_logs: range partition by month
-- monitoring_events: range partition by week
-- assessments: could partition by tenant_id for very large tenants
```

### 9.3 Caching Strategy

| Cache Layer | Technology | Data | TTL | Invalidation |
|-------------|-----------|------|-----|-------------|
| CDN | Cloudflare/CloudFront | Static assets, public pages | 1 day | Deploy-triggered |
| API response | Redis | List/detail API responses | 30-300s | Write-through |
| Tenant config | Redis + in-process | Scoring configs, role matrices | 5 min | Event-driven |
| Framework data | Redis + in-process | Clause data, cross-mappings | 1 hour | Version-triggered |
| Session | Redis | User sessions, CSRF tokens | 15-30 min | Explicit logout |
| Rate limit counters | Redis | Request counts per tenant/user | Sliding window | Auto-expire |

### 9.4 Background Job Architecture

```
[BullMQ Queues - Redis-backed]
  email_queue:       Priority-based email delivery
  webhook_queue:     Tenant webhook delivery with retry
  notification_queue: In-app + push notifications
  cache_queue:       Cache warming and invalidation

[Temporal Workflows - Durable Execution]
  VendorEnrichmentWorkflow:    Multi-step vendor data collection
  AssessmentWorkflow:          Assessment lifecycle (create -> assign -> review -> approve)
  EvidenceParsingWorkflow:     Upload -> parse -> extract -> map -> index
  MonitoringWorkflow:          Scheduled monitoring execution per vendor tier
  RemediationWorkflow:         Finding -> assign -> track -> verify -> close
  ReportGenerationWorkflow:    Collect data -> generate sections -> assemble -> review
```

---

## 10. Integration Architecture

### 10.1 SSO (SAML/OIDC)

**Confidence: [HIGH]**

**Recommendation: Support both OIDC (preferred) and SAML 2.0** [HIGH]

- OIDC for modern/cloud-native enterprise customers (Okta, Azure AD/Entra ID, Google Workspace)
- SAML 2.0 for legacy enterprise identity providers
- Many organizations adopt a hybrid strategy: SAML for legacy apps, OIDC for new systems

**Implementation approach:**
- Use WorkOS or Auth0 as an SSO abstraction layer (handles SAML/OIDC complexity)
- Alternatively, implement directly with `python-saml` + `authlib` for OIDC
- Support SCIM 2.0 for automated user provisioning/deprovisioning
- Email as stable unique identifier across identity systems
- Per-tenant identity provider configuration (stored in tenant_config)

Must support from day one: Okta, Microsoft Entra ID (Azure AD), Google Workspace, OneLogin.

Sources: [Okta SSO Guide](https://developer.okta.com/docs/guides/build-sso-integration/saml2/main/), [WorkOS SAML Providers](https://workos.com/blog/the-best-saml-providers-for-b2b-saas-in-2025), [Scalekit Build vs Buy](https://www.scalekit.com/blog/build-vs-buy-how-to-approach-sso-for-your-saas-app)

### 10.2 Email Integration

| Provider | Use Case | Strengths |
|----------|----------|-----------|
| **SendGrid** | Transactional email (notifications, alerts, reports) | Best deliverability, template engine |
| AWS SES | High-volume, cost-sensitive | Lowest cost at scale |
| Custom SMTP | Enterprise customers with email policies | Compliance requirement |

Support all three via abstraction layer. Tenant configures preferred email provider.

### 10.3 Slack/Teams Integration

- **Slack:** Incoming webhooks for alerts, Slack App for interactive commands (approve/reject from Slack)
- **Teams:** Incoming webhooks + Teams Bot for interactive cards
- **Bidirectional:** Receive commands (approve vendor, view status) and send notifications

### 10.4 API-First Design

```
Public API:
  - RESTful JSON API (OpenAPI 3.1 spec)
  - Versioned: /api/v1/, /api/v2/
  - Authentication: API key (header) or OAuth 2.0 client credentials
  - Rate limiting: per-key, configurable per tenant
  - Pagination: cursor-based (not offset-based) for consistency
  - Filtering: standardized query parameter syntax
  - Bulk operations: batch endpoints for high-volume integrations

SDK Generation:
  - Auto-generate TypeScript, Python, Go SDKs from OpenAPI spec
  - Publish to npm, PyPI, GitHub
```

### 10.5 Webhook System

```
[Event Producer] -> [Event Bus (Redis Streams / PostgreSQL LISTEN/NOTIFY)]
  |
  v
[Webhook Dispatcher Service]
  - Load tenant webhook subscriptions
  - Filter events by subscription rules
  - Serialize payload (JSON)
  - Sign payload (HMAC-SHA256 with per-subscription secret)
  - Enqueue delivery (BullMQ)
  |
  v
[Delivery Workers]
  - POST to subscriber URL with signed payload
  - Retry policy: exponential backoff with jitter (1s, 2s, 4s, 8s, 16s, 32s)
  - Max 6 retries over ~1 hour
  - Dead letter queue for persistent failures
  - Delivery logging (attempt, status code, latency, response body snippet)
  |
  v
[Webhook Management API]
  - CRUD webhook subscriptions
  - Event type catalog
  - Delivery history and replay
  - Test endpoint (send sample payload)
  - Signature verification documentation
```

**Event types:**
- `vendor.created`, `vendor.updated`, `vendor.risk_changed`
- `assessment.created`, `assessment.submitted`, `assessment.approved`
- `evidence.uploaded`, `evidence.expiring`, `evidence.expired`
- `monitoring.alert_created`, `monitoring.breach_detected`
- `finding.created`, `finding.remediated`

Sources: [Beeceptor Webhook Design](https://beeceptor.com/docs/webhook-feature-design/), [SystemDesignHandbook Webhooks](https://www.systemdesignhandbook.com/guides/design-a-webhook-system/)

---

## 11. Architecture Summary Diagram

```
                         VELORA TPRM - HIGH-LEVEL ARCHITECTURE
                         ======================================

    [Browser/Mobile]                    [External Systems]
         |                                     |
    [CDN/WAF]                          [API Gateway]
         |                                     |
    +----|-------------------------------------|----+
    |    |          PRESENTATION LAYER         |    |
    |    v                                     v    |
    | [Next.js 15 App]              [REST API (FastAPI)] |
    | - Server Components           - OpenAPI 3.1       |
    | - Client Components           - JWT + API Key Auth|
    | - SSR/SSG                     - Rate Limiting     |
    +--------------------------------------------------|
         |                                     |
    +----|-------------------------------------|----+
    |              APPLICATION LAYER                |
    |                                               |
    | [Auth Service]    [Tenant Service]            |
    | - SSO (SAML/OIDC) - Config management         |
    | - RBAC/ABAC       - Tenant isolation          |
    | - Session mgmt    - Customization engine      |
    |                                               |
    | [Assessment Engine]  [Workflow Engine]         |
    | - Scoring engine     - Temporal workflows     |
    | - Rule evaluation    - BullMQ jobs            |
    | - Template rendering - Notification dispatch  |
    |                                               |
    | [AI Service Layer]   [Monitoring Service]     |
    | - LLM orchestration  - Breach detection       |
    | - RAG pipeline       - Rating aggregation     |
    | - Confidence scoring - Alert routing          |
    | - Evidence parser    - News/threat feeds      |
    +----------------------------------------------|
         |                                     |
    +----|-------------------------------------|----+
    |              DATA LAYER                       |
    |                                               |
    | [PostgreSQL 16+]    [Redis 7+]               |
    | - RLS isolation     - Cache                   |
    | - pgvector          - Sessions                |
    | - JSONB configs     - Rate limits             |
    | - Audit logs        - Job queues              |
    |                                               |
    | [Typesense]         [S3/MinIO]               |
    | - Full-text search  - Evidence files          |
    | - Faceted search    - Report exports          |
    | - Multi-tenant      - Encrypted at rest       |
    |                                               |
    | [Temporal Server]                             |
    | - Workflow state                              |
    | - Activity history                            |
    | - Visibility store                            |
    +----------------------------------------------|
         |
    +----|------------------------------------------+
    |         INFRASTRUCTURE LAYER                  |
    |                                               |
    | [Kubernetes]  [Prometheus/Grafana]            |
    | [Docker]      [ELK/Loki (Logging)]           |
    | [Terraform]   [GitHub Actions (CI/CD)]       |
    | [Vault]       [AWS KMS (Key Mgmt)]           |
    +----------------------------------------------+
```

---

## 12. Sources

### Tech Stack and Architecture
- [Next.js FastAPI Template](https://www.vintasoftware.com/blog/next-js-fastapi-template)
- [Next.js vs FastAPI for Modern SaaS](https://nightcoders.id/blogs/next-js-vs-fastapi-for-modern-saas-the-perfect-stack-for-mvps)
- [Deploying Next.js, FastAPI, and PostgreSQL](https://medium.com/@zafarobad/ultimate-guide-to-deploying-next-js-d57ab72f6ba6)

### Multi-Tenant Architecture
- [Shipping Multi-Tenant SaaS Using Postgres RLS](https://www.thenile.dev/blog/multi-tenant-rls)
- [AWS Multi-Tenant Data Isolation with PostgreSQL RLS](https://aws.amazon.com/blogs/database/multi-tenant-data-isolation-with-postgresql-row-level-security/)
- [Row-Level Security for Multi-Tenant Applications](https://www.simplyblock.io/blog/underated-postgres-multi-tenancy-with-row-level-security/)
- [Postgres RLS Implementation Guide](https://www.permit.io/blog/postgres-rls-implementation-guide)
- [HealthTech Multi-Tenant Case Study](https://www.wellally.tech/blog/postgres-multi-tenant-database-row-level-security)

### AI and TPRM
- [Modern TPRM 2025: AI-Powered Vendor Risk Management](https://digitalxforce.com/blogs/modern-tprm-2025-ai-powered-vendor-risk-management/)
- [AI-Driven Third-Party Risk Management](https://www.atlassystems.com/complyscore/ai-tprm/introduction)
- [ProcessUnity AI for TPRM](https://www.processunity.com/third-party-risk-management/processunity-ai/)
- [SAFE Super AI Agents for TPRM](https://safe.security/resources/blog/safe-super-ai-agents-third-party-risk-management/)
- [How AI Is Transforming TPRM Workflows](https://panorays.com/blog/ai-in-third-party-risk-management/)
- [Harnessing AI in TPRM (OCEG)](https://www.oceg.org/ai-for-tprm/)

### Vector Databases
- [Best Vector Databases in 2025](https://www.firecrawl.dev/blog/best-vector-databases)
- [Top 9 Vector Databases 2026](https://www.shakudo.io/blog/top-9-vector-databases)
- [Pinecone vs Weaviate vs Qdrant vs pgvector](https://getathenic.com/blog/pinecone-vs-weaviate-vs-qdrant-vs-pgvector)
- [Vector Database Comparison 2025](https://liquidmetal.ai/casesAndBlogs/vector-comparison/)

### RAG and Compliance
- [RAG Architecture Explained 2025](https://orq.ai/blog/rag-architecture)
- [Data Governance in RAG Systems](https://dev.to/artyom_mukhopad_a9444ed6d/data-governance-in-rag-systems-security-privacy-and-compliance-by-design-2dj9)
- [Next Frontier of RAG 2026-2030](https://nstarxinc.com/blog/the-next-frontier-of-rag-how-enterprise-knowledge-systems-will-evolve-2026-2030/)

### Workflow and Background Jobs
- [Temporal Workflow Engine Principles](https://temporal.io/blog/workflow-engine-principles)
- [State of Workflow Orchestration 2025](https://www.pracdata.io/p/state-of-workflow-orchestration-ecosystem-2025)
- [Modern Queueing Architectures](https://medium.com/@pranavprakash4777/modern-queueing-architectures-celery-rabbitmq-redis-or-temporal-f93ea7c526ec)

### Search
- [Elasticsearch vs Typesense Comparison](https://www.meilisearch.com/blog/elasticsearch-vs-typesense)
- [Typesense Comparison with Alternatives](https://typesense.org/docs/overview/comparison-with-alternatives.html)

### Document Processing
- [Document Intelligence in 2025: OCR Platforms Compared](https://windowsforum.com/threads/document-intelligence-in-2025-ocr-platforms-compared-for-idp.387634/)
- [Beyond OCR: AI Document Processing](https://www.infoq.com/articles/ocr-ai-document-processing/)
- [LLM-Powered Pipeline for Document Analytics](https://dzone.com/articles/architecting-intelligence-llm-powered-pipeline)

### Security and Compliance
- [SOC 2 Checklist for SaaS Startups](https://trycomp.ai/soc-2-checklist-for-saas-startups)
- [RBAC Implementation for SOC 2 and HIPAA](https://certpro.com/role-based-access-control/)
- [Enterprise-Ready Product Checklist](https://blog.logto.io/enterprise-ready)
- [SOC 2 Compliance for Devs](https://www.aikido.dev/learn/compliance/compliance-frameworks/soc-2)

### Caching
- [Multi-Tenant Caching: Hybrid Pattern](https://medium.com/@okan.yurt/multi-tenant-caching-strategies-why-redis-alone-isnt-enough-hybrid-pattern-f404877632e5)
- [Redis Multi-Tenancy](https://redis.io/blog/multi-tenancy-redis-enterprise/)
- [Redis Caching Strategies for SaaS 2025](https://dev.to/ash_dubai/boosting-speed-essential-redis-caching-strategies-for-saas-in-2025-50pl)

### Monitoring
- [Breachsense Dark Web Monitoring](https://www.breachsense.com/)
- [BitSight Continuous Monitoring](https://www.bitsight.com/products/continuous-monitoring)
- [SpyCloud Dark Web Monitoring](https://spycloud.com/use-case/dark-web-monitoring/)

### SSO and Identity
- [Okta SSO Integration Guide](https://developer.okta.com/docs/guides/build-sso-integration/saml2/main/)
- [WorkOS Best SAML Providers 2025](https://workos.com/blog/the-best-saml-providers-for-b2b-saas-in-2025)
- [Build vs Buy SSO](https://www.scalekit.com/blog/build-vs-buy-how-to-approach-sso-for-your-saas-app)

### Human-in-the-Loop
- [HITL Agent Oversight (Galileo)](https://galileo.ai/blog/human-in-the-loop-agent-oversight)
- [HITL Review Queue Workflows 2025](https://alldaystech.com/guides/artificial-intelligence/human-in-the-loop-ai-review-queue-workflows)
- [Enterprise HITL Framework](https://www.solulab.com/how-do-enterprises-implement-human-in-the-loop-frameworks/)

### Webhooks and Integration
- [Webhook Architecture Design Pattern](https://beeceptor.com/docs/webhook-feature-design/)
- [Design a Webhook System](https://www.systemdesignhandbook.com/guides/design-a-webhook-system/)

### Framework Mapping
- [ISO 27001 Mapping with SOC 2, HIPAA, PCI DSS, NIST CSF](https://www.ampcuscyber.com/blogs/iso-27001-mapping-with-security-standards/)
- [SOC 2 Mapping Strategies](https://www.thoropass.com/blog/soc-2-mapping)
- [ISO 27001 and NIST CSF Control Mapping](https://censinet.com/perspectives/iso-27001-and-nist-csf-control-mapping-checklist)

### GRC Platform Landscape
- [12 Best GRC Tools 2026 (ConductorOne)](https://www.conductorone.com/guides/best-grc-solutions/)
- [10 Best GRC Tools 2026 (SmartSuite)](https://www.smartsuite.com/blog/grc-tools)
- [Best GRC Software 2025 (BD Emerson)](https://www.bdemerson.com/article/the-best-grc-software-a-practical-evaluation)

### Config-Driven Architecture
- [Schema-Driven Platforms](https://peterhrynkow.com/ai/architecture/2025/02/01/schema-driven-platforms.html)
- [Configuration Versioning with JSON Schema](https://medium.com/@ansujain/designing-a-robust-configuration-versioning-system-with-json-schema-validation-0f24d7ac53d3)

---

> **Document Status:** Research complete. Ready for architecture decision records and detailed design phase.
