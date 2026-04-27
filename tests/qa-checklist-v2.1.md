---
tags:
  - archeon
  - forgeon
  - product
  - product-velora
---

# Velora TPRM v2.1 — QA Checklist (Stage A)

> Created by: Parikshika (QA) via Harion
> Sprint plan: v2.1 (11 sprints, 63 stories)
> Scope: All new features added in v2.1 intelligence layer

---

## Sprint 1: AI Service — Claude API

| # | Test | Pass/Fail |
|---|------|-----------|
| 1.1 | POST /ai/auto-fill returns real Claude responses (not mock) | |
| 1.2 | Auto-fill includes confidence scores per answer (0.0-1.0) | |
| 1.3 | Answers with confidence < 0.7 appear in review queue | |
| 1.4 | Auto-fill falls back gracefully when ANTHROPIC_API_KEY missing | |
| 1.5 | Token usage tracked in response (input_tokens, output_tokens) | |
| 1.6 | GET /ai/usage returns real DB-based stats, not hardcoded | |
| 1.7 | Rate limit handling: 429 retries with backoff | |
| 1.8 | Question cap: >200 questions truncated | |

## Sprint 2: Evidence Parsing

| # | Test | Pass/Fail |
|---|------|-----------|
| 2.1 | Upload returns real MinIO presigned URL (not mock s3.mock.velora.io) | |
| 2.2 | POST /evidence/{id}/process triggers Azure parsing | |
| 2.3 | SOC 2 report: extracts audit_period, auditor, opinion_type | |
| 2.4 | ISO 27001 cert: extracts certificate_number, standard, validity | |
| 2.5 | Pen test: extracts methodology, findings by severity | |
| 2.6 | Unsupported file type rejected (mime_type validation) | |
| 2.7 | Filename sanitized (no path traversal in s3_key) | |
| 2.8 | File > 100MB rejected at download | |
| 2.9 | Azure unavailable → status set to "failed" | |

## Sprint 3: Control Mapping

| # | Test | Pass/Fail |
|---|------|-----------|
| 3.1 | GET /frameworks/{id}/clauses/bulk returns flat clause list | |
| 3.2 | Internal endpoint /internal/frameworks/{id}/clauses/bulk works without auth | |
| 3.3 | Evidence processing auto-maps to framework controls | |
| 3.4 | Mappings include coverage_type (full/partial/supportive) | |
| 3.5 | Mappings include confidence score >= 0.5 | |

## Sprint 4: SSO/SAML/OIDC

| # | Test | Pass/Fail |
|---|------|-----------|
| 4.1 | GET /auth/sso/authorize returns redirect URL structure | |
| 4.2 | POST /auth/sso/callback endpoint exists and responds | |
| 4.3 | User model has sso_provider, sso_provider_id fields | |
| 4.4 | python3-saml and authlib in auth service dependencies | |

## Sprint 5: Distribution + Email

| # | Test | Pass/Fail |
|---|------|-----------|
| 5.1 | POST /assessments/{id}/distribute creates distribution record | |
| 5.2 | Distribution endpoint accepts vendor_email and due_days params | |
| 5.3 | Email sender renders Jinja2 templates with vendor context | |
| 5.4 | SendGrid integration configured (or logs warning if no key) | |

## Sprint 6: Vendor Portal

| # | Test | Pass/Fail |
|---|------|-----------|
| 6.1 | /portal renders vendor dashboard layout | |
| 6.2 | /portal/assessments renders assessment list | |
| 6.3 | /portal/evidence renders evidence page with upload button | |
| 6.4 | /portal/findings renders findings page | |
| 6.5 | Portal BFF routes respond at /api/portal/* | |
| 6.6 | Magic link auth endpoint works | |

## Sprint 7: Monitoring + Alerts

| # | Test | Pass/Fail |
|---|------|-----------|
| 7.1 | SecurityScorecard client handles 404 gracefully | |
| 7.2 | Alert correlation: P0 keywords trigger P0 priority | |
| 7.3 | Alert deduplication: same signal type within 24h ignored | |
| 7.4 | Alert escalation: 3+ P2/P3 in 48h → escalate to P1 | |
| 7.5 | Alert model has signal_type, signal_data fields | |

## Sprint 9: FAIR Quantification

| # | Test | Pass/Fail |
|---|------|-----------|
| 9.1 | POST /scoring/fair/analyze returns ALE with range | |
| 9.2 | Monte Carlo simulation runs 10,000 iterations | |
| 9.3 | Risk level classified (critical/high/medium/low) | |
| 9.4 | Data sensitivity multiplier applied correctly | |

## Sprint 10: Board Reports

| # | Test | Pass/Fail |
|---|------|-----------|
| 10.1 | PDF generation produces valid PDF bytes | |
| 10.2 | PPTX generation produces valid PowerPoint file | |
| 10.3 | Report includes branded HTML template | |
| 10.4 | Report data includes metrics, vendor analysis | |

---

## Cross-Cutting

| # | Test | Pass/Fail |
|---|------|-----------|
| X.1 | All 4 test users still work (devam, manager, analyst, viewer) | |
| X.2 | RBAC: viewer blocked from write/delete endpoints | |
| X.3 | All existing v2.0 endpoints still respond correctly | |
| X.4 | docker-compose up starts all services healthy | |
| X.5 | No secrets in committed code | |
| X.6 | No PII in log output | |
