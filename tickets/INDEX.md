---
tags:
  - archeon
  - forgeon
  - product
  - product-velora
---

# Velora TPRM -- Ticket Index

> **Last Updated**: 2026-03-28
> **Sprint Plan**: v2.1 (intelligence layer + automation) -- REVISED Iteration 2, addressing F1-F4

---

## Completed (v2.0)

| Ticket ID | Title | Type | Status | Maker | Phase |
|-----------|-------|------|--------|-------|-------|
| TSK-00001 | Create product skeleton | TSK | DONE | Harion | 0 |
| TSK-00002 | Build allocation plan + MCA matrix | TSK | DONE | Harion | 0 |
| TSK-00003 | TPRM market research (deep) | TSK | DONE | Anveshon | 5 |
| TSK-00004 | TPRM technical architecture research | TSK | DONE | Anveshon | 5 |
| TSK-00005 | Problem validation + Ideation | TSK | DONE | Darshika | 1 |
| TSK-00006 | Full PRD creation (18+ sections) | TSK | DONE | Darshika | 2 |

---

## v2.1 Sprint Tickets

### Sprint 1: AI Service -- Real Claude API Integration

| Ticket ID | Title | Type | Status | Maker | Sprint | Route | Dependencies |
|-----------|-------|------|--------|-------|--------|-------|-------------|
| TSK-01001 | Add Anthropic SDK dependency to AI service | TSK | BACKLOG | Nirmitya | S1 | Ralph | None |
| TSK-01002 | Create async Claude client wrapper with retry + rate limiting | TSK | BACKLOG | Nirmitya | S1 | Ralph | TSK-01001 |
| TSK-01003 | Build TPRM questionnaire prompt templates | TSK | BACKLOG | Nirmitya | S1 | Ralph | TSK-01002 |
| TSK-01004 | Replace _mock_answer() with real Claude calls in AIService | TSK | BACKLOG | Nirmitya | S1 | Ralph | TSK-01003 |
| TSK-01005 | Integration tests for Claude API auto-fill | TSK | BACKLOG | Nirmitya | S1 | Ralph | TSK-01004 |

### Sprint 2: Evidence Parsing via Azure Document Intelligence (parallel with S4)

| Ticket ID | Title | Type | Status | Maker | Sprint | Route | Dependencies |
|-----------|-------|------|--------|-------|--------|-------|-------------|
| TSK-02001 | Add Azure Document Intelligence SDK to evidence service | TSK | BACKLOG | Nirmitya | S2 | Ralph | None |
| TSK-02002 | Create async document parser client (Azure Doc Intelligence) | TSK | BACKLOG | Nirmitya | S2 | Ralph | TSK-02001 |
| TSK-02003 | Build typed extraction pipelines: SOC 2, ISO 27001, pen test | TSK | BACKLOG | Nirmitya | S2 | Ralph | TSK-02002 |
| TSK-02004 | Integrate MinIO for real file storage (replace mock S3) | TSK | BACKLOG | Nirmitya | S2 | Ralph | None |
| TSK-02005 | Replace mock extractions with real Azure parsing pipeline | TSK | BACKLOG | Nirmitya | S2 | Ralph | TSK-02003, TSK-02004 |
| TSK-02006 | Integration tests for document parsing with sample PDFs | TSK | BACKLOG | Nirmitya | S2 | Ralph | TSK-02005 |

### Sprint 3: Evidence-to-Control Mapping Engine

| Ticket ID | Title | Type | Status | Maker | Sprint | Route | Dependencies |
|-----------|-------|------|--------|-------|--------|-------|-------------|
| TSK-03001 | Build control mapping prompt templates for Claude | TSK | BACKLOG | Nirmitya | S3 | OpenHands | TSK-01002 |
| TSK-03002 | Create EvidenceMappingEngine (evidence + AI + framework via httpx/Docker DNS) | TSK | BACKLOG | Nirmitya | S3 | OpenHands | TSK-03001 |
| TSK-03003 | Add bulk clause retrieval API to framework service | TSK | BACKLOG | Nirmitya | S3 | OpenHands | None |
| TSK-03004 | Wire mapping into evidence processing pipeline | TSK | BACKLOG | Nirmitya | S3 | OpenHands | TSK-03002, TSK-03003 |
| TSK-03005 | Integration tests for evidence-to-control mapping | TSK | BACKLOG | Nirmitya | S3 | OpenHands | TSK-03004 |

### Sprint 4: SSO/SAML/OIDC Enterprise Authentication (parallel with S2)

| Ticket ID | Title | Type | Status | Maker | Sprint | Route | Dependencies |
|-----------|-------|------|--------|-------|--------|-------|-------------|
| TSK-04000 | Initialize alembic in auth service | TSK | BACKLOG | Nirmitya | S4 | Ralph | None |
| TSK-04001 | Add python3-saml + authlib dependencies to auth service | TSK | BACKLOG | Nirmitya | S4 | Ralph | None |
| TSK-04002 | SSO provider configuration DB model + migration | TSK | BACKLOG | Nirmitya | S4 | Ralph | TSK-04000, TSK-04001 |
| TSK-04003 | SAML 2.0 Service Provider implementation | TSK | BACKLOG | Nirmitya | S4 | Ralph | TSK-04002 |
| TSK-04004 | OIDC provider implementation (Azure AD, Google, Okta) | TSK | BACKLOG | Nirmitya | S4 | Ralph | TSK-04002 |
| TSK-04005 | JIT user provisioning + IdP attribute mapping | TSK | BACKLOG | Nirmitya | S4 | Ralph | TSK-04003, TSK-04004 |
| TSK-04006 | Integration tests for SAML + OIDC flows | TSK | BACKLOG | Nirmitya | S4 | Ralph | TSK-04005 |

### Sprint 5: Assessment Distribution + SLA + Real Email

| Ticket ID | Title | Type | Status | Maker | Sprint | Route | Dependencies |
|-----------|-------|------|--------|-------|--------|-------|-------------|
| TSK-05000 | Initialize alembic in assessment service | TSK | BACKLOG | Nirmitya | S5 | OpenHands | None |
| TSK-05001 | Assessment distribution endpoint with due_date | TSK | BACKLOG | Nirmitya | S5 | OpenHands | TSK-05000, TSK-04005 |
| TSK-05002 | SLA configuration model + CRUD + seed data | TSK | BACKLOG | Nirmitya | S5 | OpenHands | TSK-05000 |
| TSK-05003 | Real email sending via SendGrid in communication service | TSK | BACKLOG | Nirmitya | S5 | OpenHands | None |
| TSK-05004 | Branded HTML email templates for assessment lifecycle | TSK | BACKLOG | Nirmitya | S5 | OpenHands | TSK-05003 |
| TSK-05005 | SLA timer background task + automated reminders (calls communication service via httpx) | TSK | BACKLOG | Nirmitya | S5 | OpenHands | TSK-05001, TSK-05002, TSK-05003 |
| TSK-05006 | Distribution triggers notification + email + log chain (via httpx to communication service) | TSK | BACKLOG | Nirmitya | S5 | OpenHands | TSK-05001, TSK-05003 |
| TSK-05007 | Integration tests for distribution + email pipeline | TSK | BACKLOG | Nirmitya | S5 | OpenHands | TSK-05006 |

### Sprint 6a: Vendor Portal -- Scaffold + Auth + BFF + Dashboard

| Ticket ID | Title | Type | Status | Maker | Sprint | Route | Dependencies |
|-----------|-------|------|--------|-------|--------|-------|-------------|
| TSK-06a01 | Vendor portal Next.js scaffold with white-label theming | TSK | BACKLOG | Drishyon | S6a | OpenHands | None |
| TSK-06a02 | Vendor auth: magic link + SSO login flow | TSK | BACKLOG | Nirmitya | S6a | OpenHands | TSK-04005 |
| TSK-06a03 | BFF portal routes (assessments, evidence, findings) via httpx to downstream services | TSK | BACKLOG | Nirmitya | S6a | OpenHands | TSK-06a02 |
| TSK-06a04 | Vendor portal dashboard (counts, activity, action items) | TSK | BACKLOG | Drishyon | S6a | OpenHands | TSK-06a03 |

### Sprint 6b: Vendor Portal -- Assessment UI + Evidence + Findings + Integration Tests

| Ticket ID | Title | Type | Status | Maker | Sprint | Route | Dependencies |
|-----------|-------|------|--------|-------|--------|-------|-------------|
| TSK-06b01 | Assessment completion UI (all question types) | TSK | BACKLOG | Drishyon | S6b | OpenHands | TSK-06a03 |
| TSK-06b02 | Evidence upload UI from vendor portal | TSK | BACKLOG | Drishyon | S6b | OpenHands | TSK-06a03 |
| TSK-06b03 | Findings view + acknowledge UI for vendors | TSK | BACKLOG | Drishyon | S6b | OpenHands | TSK-06a03 |
| TSK-06b04 | Integration tests for full vendor portal journey | TSK | BACKLOG | Nirmitya + Drishyon | S6b | OpenHands | TSK-06b01, TSK-06b02, TSK-06b03 |

### Sprint 7: External Rating API + Alert Correlation Engine

| Ticket ID | Title | Type | Status | Maker | Sprint | Route | Dependencies |
|-----------|-------|------|--------|-------|--------|-------|-------------|
| TSK-07001 | SecurityScorecard async API client (httpx) | TSK | BACKLOG | Nirmitya | S7 | OpenHands | None |
| TSK-07002 | Signal ingestion pipeline (polling + webhook) | TSK | BACKLOG | Nirmitya | S7 | OpenHands | TSK-07001 |
| TSK-07003 | Alert correlation engine (dedup + correlate + escalate) | TSK | BACKLOG | Nirmitya | S7 | OpenHands | TSK-07002 |
| TSK-07004 | Auto-priority assignment rules engine | TSK | BACKLOG | Nirmitya | S7 | OpenHands | TSK-07003 |
| TSK-07005 | Update vendor scores from external rating changes (calls scoring service via httpx) | TSK | BACKLOG | Nirmitya | S7 | OpenHands | TSK-07002 |
| TSK-07006 | Integration tests for monitoring pipeline | TSK | BACKLOG | Nirmitya | S7 | OpenHands | TSK-07005 |

### Sprint 8: Temporal Workflows -- Real Orchestration

| Ticket ID | Title | Type | Status | Maker | Sprint | Route | Dependencies |
|-----------|-------|------|--------|-------|--------|-------|-------------|
| TSK-08001 | Verify Temporal server in docker-compose | TSK | BACKLOG | Prasaron | S8 | Ralph | None |
| TSK-08002 | Wire vendor onboarding workflow to real services (httpx activities) | TSK | BACKLOG | Prasaron | S8 | Ralph | TSK-08001 |
| TSK-08003 | Wire assessment lifecycle workflow (distribute + SLA + score via httpx) | TSK | BACKLOG | Prasaron | S8 | Ralph | TSK-08001, TSK-05005 |
| TSK-08004 | Wire evidence processing workflow (classify + parse + map via httpx) | TSK | BACKLOG | Prasaron | S8 | Ralph | TSK-08001, TSK-03004 |
| TSK-08005 | Workflow integration tests (all 3 workflows end-to-end) | TSK | BACKLOG | Prasaron | S8 | Ralph | TSK-08002, TSK-08003, TSK-08004 |

### Sprint 9: FAIR Quantification + Cross-Framework Mapping

| Ticket ID | Title | Type | Status | Maker | Sprint | Route | Dependencies |
|-----------|-------|------|--------|-------|--------|-------|-------------|
| TSK-09000 | Initialize alembic in scoring service | TSK | BACKLOG | Nirmitya | S9 | OpenHands | None |
| TSK-09001 | FAIR model data structures + DB migration | TSK | BACKLOG | Nirmitya | S9 | OpenHands | TSK-09000 |
| TSK-09002 | FAIR calculation engine (Monte Carlo, ALE) | TSK | BACKLOG | Nirmitya | S9 | OpenHands | TSK-09001 |
| TSK-09003 | FAIR API endpoints (analyze + portfolio aggregate) | TSK | BACKLOG | Nirmitya | S9 | OpenHands | TSK-09002 |
| TSK-09004 | Cross-framework mapping engine with confidence scoring | TSK | BACKLOG | Nirmitya | S9 | OpenHands | None |
| TSK-09005 | Seed known cross-framework mappings (50+ across 4 frameworks) | TSK | BACKLOG | Nirmitya | S9 | OpenHands | TSK-09004 |
| TSK-09006 | Integration tests for FAIR + cross-framework mapping | TSK | BACKLOG | Nirmitya | S9 | OpenHands | TSK-09003, TSK-09005 |

### Sprint 10: Board-Ready Reports

| Ticket ID | Title | Type | Status | Maker | Sprint | Route | Dependencies |
|-----------|-------|------|--------|-------|--------|-------|-------------|
| TSK-10001 | Add weasyprint + python-pptx + matplotlib to reporting | TSK | BACKLOG | Nirmitya | S10 | OpenHands | None |
| TSK-10002 | PDF report generator with branded templates | TSK | BACKLOG | Nirmitya | S10 | OpenHands | TSK-10001 |
| TSK-10003 | PPTX board presentation generator | TSK | BACKLOG | Nirmitya | S10 | OpenHands | TSK-10001 |
| TSK-10004 | AI narrative engine for executive summaries | TSK | BACKLOG | Nirmitya | S10 | OpenHands | TSK-01002 |
| TSK-10005 | Chart/heatmap generation (risk heatmap, trends, FAIR curves) | TSK | BACKLOG | Nirmitya | S10 | OpenHands | TSK-09002 |
| TSK-10006 | Integration tests for report generation | TSK | BACKLOG | Nirmitya | S10 | OpenHands | TSK-10002, TSK-10003 |

---

## Summary Statistics

| Metric | Count |
|--------|-------|
| Total v2.1 tickets | 63 |
| Sprint 1 tickets | 5 |
| Sprint 2 tickets | 6 |
| Sprint 3 tickets | 5 |
| Sprint 4 tickets | 7 (+1 alembic init) |
| Sprint 5 tickets | 8 (+1 alembic init) |
| Sprint 6a tickets | 4 |
| Sprint 6b tickets | 4 |
| Sprint 7 tickets | 6 |
| Sprint 8 tickets | 5 |
| Sprint 9 tickets | 7 (+1 alembic init) |
| Sprint 10 tickets | 6 |
| Assigned to Nirmitya | 48 |
| Assigned to Drishyon | 7 |
| Assigned to Prasaron | 5 |
| Shared (Nirmitya + Drishyon) | 3 |
| Route: Ralph (single service) | 23 |
| Route: OpenHands (multi-service) | 40 |

---

## Changes from Iteration 1 (Tantron Findings)

| Finding | Change |
|---------|--------|
| F1: Sprint 6 over-scoped | Split S6 into S6a (4 tickets: scaffold, auth, BFF, dashboard) and S6b (4 tickets: assessment UI, evidence, findings, integration tests) |
| F2: Missing alembic setup | Added TSK-04000 (alembic init in auth), TSK-05000 (alembic init in assessment), TSK-09000 (alembic init in scoring) as first tasks in their respective sprints |
| F3: False serialization S4 | Reordered: S2 and S4 now marked as parallel (both depend only on S1). Critical path: S1->S2->S3->S5->S6a->S6b->S7->S8->S9->S10. S4 runs alongside S2. |
| F4: Inter-service communication unspecified | All cross-service tickets now specify httpx.AsyncClient via Docker DNS. Sprint plan has dedicated "Inter-Service Communication Pattern" section. Affected tickets in S3, S5, S6a, S7, S8 updated with explicit pattern references. |
