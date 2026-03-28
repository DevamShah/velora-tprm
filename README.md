<div align="center">

# Velora TPRM

**AI-Native Third-Party Risk Management Platform**

[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-red.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)]()
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-green.svg)]()
[![Next.js 15](https://img.shields.io/badge/next.js-15-black.svg)]()
[![Services](https://img.shields.io/badge/microservices-14-purple.svg)]()

[Features](#features) | [Architecture](#architecture) | [Quick Start](#quick-start) | [Development](#development) | [Contributing](#contributing)

</div>

---

Velora TPRM unifies the entire vendor risk lifecycle -- discovery, classification, assessment, onboarding, continuous monitoring, reassessment, and offboarding -- in a single platform. AI handles the assessment burden; humans focus on decisions.

Built for TPRM teams managing 200-2000+ vendors who need to move faster than questionnaire-based workflows allow, without sacrificing the rigor regulators demand.

## Features

### Vendor Lifecycle Management
- Full vendor inventory with bulk CSV import
- AI-powered vendor enrichment (firmographics, ratings, certifications)
- Configurable 4-tier inherent risk classification
- 360-degree vendor profile with contacts, timeline, and risk scores

### Assessment Engine
- Framework-aware questionnaires (SIG Core/Lite, CAIQ v4, custom)
- AI pre-population from prior responses and uploaded evidence
- Evidence parsing (SOC 2, ISO certs, pen test reports) with control mapping
- Hybrid risk scoring with AI-assisted review queue

### Framework Intelligence
- Built-in: SOC 2, ISO 27001:2022, NIST CSF 2.0, HIPAA, PCI DSS 4.0, GDPR, DORA
- Cross-framework mapping engine
- Unified control library eliminating redundant assessment

### Continuous Monitoring and Alerts
- Multi-signal monitoring hub with P0-P4 priority alerts
- Deduplication, correlation, and escalation engine
- Vendor risk timeline with chronological event tracking
- Configurable alert rules with condition builder

### Executive Dashboard and Reporting
- Real-time portfolio dashboard (risk heatmap, tier distribution, trend charts)
- Board-ready report generation (PDF/CSV)
- Top-10 risk vendors, assessment pipeline, compliance posture

### Platform Security
- Multi-tenant Row-Level Security
- RBAC + ABAC via OPA (Open Policy Agent)
- AES-256-GCM field-level PII encryption
- Immutable audit trail
- API-first architecture (OpenAPI 3.0)

## Architecture

```
                           +------------------+
                           |   Next.js SPA    |
                           |   (React 19)     |
                           +--------+---------+
                                    |
                           +--------+---------+
                           |  BFF Service     |
                           | (sessions, agg)  |
                           +--------+---------+
                                    |
                    +---------------+----------------+
                    |       Traefik API Gateway       |
                    +--+--+--+--+--+--+--+--+--+--+--+
                       |  |  |  |  |  |  |  |  |  |
         +-------+  +--+--+ +--+--+ +--+--+ +--+--+  +--------+
         | auth  |  |vendor| |assess| |score | |frame|  |evidence|
         | :8001 |  |:8002 | |:8003 | |:8005 | |:8004|  | :8006  |
         +-------+  +------+ +------+ +------+ +-----+  +--------+

         +--------+ +------+ +------+ +------+ +-----+  +--------+
         |monitor | |finding| |comms | |report| |admin|  |  ai    |
         | :8007  | |:8008  | |:8009 | |:8010 | |:8011|  | :8012  |
         +--------+ +-------+ +------+ +------+ +-----+  +--------+
                                    |
                    +---------------+----------------+
                    |       Shared Infrastructure     |
                    | PostgreSQL | Redis | Temporal   |
                    | MinIO | OPA | Typesense         |
                    +--------------------------------+
```

14 microservices communicating via REST + Redis Streams, orchestrated by Temporal, authorized by OPA.

| Service | Port | Purpose |
|---------|------|---------|
| auth-service | 8001 | Authentication, SSO, JWT sessions |
| vendor-service | 8002 | Vendor lifecycle, contacts, enrichment |
| assessment-engine | 8003 | Questionnaires, templates, lifecycle |
| framework-service | 8004 | Compliance frameworks, clause mapping |
| scoring-engine | 8005 | Risk scoring, FAIR, portfolio |
| evidence-service | 8006 | Upload, parse, control mapping |
| monitoring-service | 8007 | Signals, alerts, rules engine |
| finding-service | 8008 | Findings, remediation tracking |
| communication-hub | 8009 | Notifications, email, Slack/Teams |
| reporting-service | 8010 | Dashboards, PDF generation, CQRS |
| admin-service | 8011 | Users, audit logs, configuration |
| ai-service | 8012 | LLM orchestration, RAG, auto-fill |
| workflow-service | 8013 | Temporal workers |
| bff-service | 8000 | Backend-for-Frontend, session mgmt |

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for frontend development)
- Python 3.9+ (for backend development)

### Using Docker Compose

```bash
git clone https://github.com/anthropics/velora-tprm.git
cd velora-tprm

cp .env.example .env
docker compose up -d                    # infrastructure
docker compose --profile core up -d     # core services
docker compose --profile frontend up -d # frontend

open http://localhost:3000
```

### Running Locally

```bash
# Infrastructure
docker compose up -d  # postgres, redis, minio

# Backend
cd src/backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# Frontend
cd src/frontend
npm install && npm run dev
```

### Test Credentials

| Email | Password | Role |
|-------|----------|------|
| devam@velora.io | devam123 | Admin |
| manager@velora.io | manager123 | TPRM Manager |
| analyst@velora.io | analyst123 | Risk Analyst |
| viewer@velora.io | viewer123 | Viewer |

## Project Structure

```
velora-tprm/
+-- packages/velora-common/     # Shared library (auth, events, OPA, security)
+-- services/                   # 14 microservices
+-- frontend/web/               # Next.js dashboard (25 routes)
+-- src/backend/                # Monolith mode (local dev)
+-- src/frontend/               # Frontend source (local dev)
+-- policies/                   # OPA Rego policies (10 files)
+-- infra/                      # Docker, Traefik, DB init
+-- tests/                      # QA checklists (396 items)
+-- docs/                       # PRD, HLD, LLD, research
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.9+ / FastAPI |
| Frontend | Next.js 15 / React 19 / TypeScript |
| UI | shadcn/ui + Radix UI + Tailwind CSS |
| Charts | Recharts |
| Database | PostgreSQL 16 (RLS, schema-per-service) |
| Cache / Events | Redis 7 (Streams) |
| Authorization | OPA (Open Policy Agent) |
| Workflows | Temporal.io |
| Gateway | Traefik |
| Object Storage | MinIO (S3-compatible) |
| AI | Anthropic Claude / OpenAI (abstracted) |

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Security

See [SECURITY.md](SECURITY.md). Do not open public issues for security reports.

## License

Velora TPRM is licensed under the **GNU Affero General Public License v3.0** (AGPL-3.0). See [LICENSE](LICENSE).

If you run a modified version as a network service, you must release your source code under the same license.

## Author

**Devam Shah** -- Built with the Archeon autonomous product factory.
