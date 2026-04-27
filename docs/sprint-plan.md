---
tags:
  - archeon
  - forgeon
  - product
  - product-velora
---

# Velora TPRM v2.0 — Sprint Plan

> **Author**: Yojika (Sprint Planning Agent) under Harion orchestration
> **Methodology**: Vertical Slicing (CTO-standard) — every function built DB→API→Service→UI→Test as one unit
> **Date**: 2026-03-27
> **Status**: Active
> **Total P0 Features**: 23 | **Total Endpoints**: ~141 | **Total Tables**: ~50

---

## Build Philosophy

1. **Vertical slices only** — No horizontal layers. Every function delivers working end-to-end functionality
2. **Foundation first** — Auth, DB, routing, UI shell before any features
3. **One function at a time** — Developer builds → Tester validates → CTO approves → Next function
4. **No dead buttons** — If it's on screen, it works. Period.
5. **Real data from Day 1** — Test users, seed data, actual API calls. No mocks after Sprint 0
6. **Multiple iterations** — Iterate until genuinely satisfactory. No "good enough"

---

## Sprint 0: Foundation (MUST complete before any features)

### 0.1 Database & Migrations
| # | Function | Acceptance Criteria |
|---|----------|-------------------|
| 0.1.1 | PostgreSQL setup with pgvector extension | DB runs, pgvector enabled, RLS enabled |
| 0.1.2 | Alembic migration framework | `alembic upgrade head` works, `alembic downgrade` works |
| 0.1.3 | Tenant table + RLS policies | Tenant created, RLS blocks cross-tenant access |
| 0.1.4 | User table with encrypted PII fields | User created, PII encrypted at rest, HMAC lookup works |
| 0.1.5 | Role + Permission tables + seed data | 8 default roles seeded, permissions matrix complete |
| 0.1.6 | Session/refresh token table | Tokens stored, indexed, revocable |

### 0.2 Backend Skeleton
| # | Function | Acceptance Criteria |
|---|----------|-------------------|
| 0.2.1 | FastAPI app factory with lifespan | App starts, health check returns 200 |
| 0.2.2 | CORS, rate limiting, error handling middleware | RFC 7807 errors, rate limit headers, CORS works from frontend origin |
| 0.2.3 | Tenant context middleware | X-Tenant-ID header → tenant_id in DB session RLS |
| 0.2.4 | Auth middleware (JWT validation) | Protected routes reject invalid/missing tokens |
| 0.2.5 | Permission dependency (`require_permission()`) | Endpoint rejects users without required permission |
| 0.2.6 | Structured JSON logging | All requests logged with tenant_id, user_id, latency |
| 0.2.7 | Database session management (async) | Connection pool works, sessions properly closed |
| 0.2.8 | Pydantic Settings with env validation | App fails fast on missing required env vars |

### 0.3 Auth Module (Full Vertical Slice)
| # | Function | Acceptance Criteria |
|---|----------|-------------------|
| 0.3.1 | `POST /auth/login` — email/password login | Returns JWT access + refresh tokens. Invalid creds return 401 |
| 0.3.2 | `POST /auth/refresh` — refresh token rotation | New access token issued, old refresh token revoked |
| 0.3.3 | `POST /auth/logout` — session revocation | Refresh token invalidated, subsequent refresh fails |
| 0.3.4 | `GET /auth/me` — current user profile | Returns user profile with roles and permissions |
| 0.3.5 | Password hashing with bcrypt | Passwords never stored in plaintext, bcrypt cost factor ≥12 |
| 0.3.6 | Test users seed script | 2 users per role (admin, analyst, viewer, vendor). Working login for each |

### 0.4 Frontend Shell
| # | Function | Acceptance Criteria |
|---|----------|-------------------|
| 0.4.1 | Next.js 15 project setup (App Router, TypeScript strict) | `npm run dev` works, `npm run build` succeeds with zero errors |
| 0.4.2 | Tailwind CSS + shadcn/ui + Radix setup | Theme tokens applied, navy color palette active |
| 0.4.3 | Layout: Sidebar + Header + Main content area | Sidebar renders with all navigation sections, responsive |
| 0.4.4 | Routing: All page routes created (empty but navigable) | Every sidebar link navigates to correct route. ZERO 404s |
| 0.4.5 | Auth context + protected route wrapper | Unauthenticated users redirect to /login |
| 0.4.6 | Login page — connected to `POST /auth/login` | Test user can log in, token stored, redirects to dashboard |
| 0.4.7 | API client with auth header injection | All API calls include Bearer token, 401 triggers re-login |
| 0.4.8 | Command palette (Cmd+K) shell | Opens/closes, empty for now but functional |
| 0.4.9 | Breadcrumb component | Shows current navigation path on every page |
| 0.4.10 | Loading skeleton + error boundary components | Skeleton shows during API calls, errors caught gracefully |
| 0.4.11 | Toast notification system (sonner) | Success/error/info toasts work from any page |

### 0.5 Infrastructure
| # | Function | Acceptance Criteria |
|---|----------|-------------------|
| 0.5.1 | docker-compose.yml (PostgreSQL, Redis, MinIO, Typesense) | `docker compose up` starts all services, health checks pass |
| 0.5.2 | .env.example with all required variables | Copy .env.example → .env, app starts |
| 0.5.3 | Backend Dockerfile (multi-stage) | Image builds, app runs in container |
| 0.5.4 | Frontend Dockerfile (multi-stage) | Image builds, app runs in container |
| 0.5.5 | Seed script (tenants, users, roles) | Fresh DB can be seeded in one command |

### 0.6 CI Pipeline
| # | Function | Acceptance Criteria |
|---|----------|-------------------|
| 0.6.1 | GitHub Actions: lint + typecheck + test on every push | Pipeline runs, blocks on failure |
| 0.6.2 | Backend: ruff lint + mypy typecheck | Zero lint errors, zero type errors |
| 0.6.3 | Frontend: ESLint + TypeScript strict | Zero lint errors, zero type errors |

**Sprint 0 Gate**: App starts. Test user logs in. Sidebar navigation works (every link → correct page). API health check returns 200. CI passes. ZERO dead buttons.

---

## Sprint 1: Vendor Core (P0: VLM-01, VLM-02, VLM-03, VLM-04)

### 1.1 Vendor Data Layer
| # | Function | Acceptance Criteria |
|---|----------|-------------------|
| 1.1.1 | Vendor table migration | Table created with all columns, RLS active |
| 1.1.2 | Vendor SQLAlchemy model | Model maps correctly, CRUD operations work |
| 1.1.3 | Vendor Pydantic schemas (create, update, list, detail) | Validation works, nested objects serialize correctly |
| 1.1.4 | VendorService — create vendor | Creates vendor in DB, returns full object |
| 1.1.5 | VendorService — list vendors (paginated, filtered, sorted) | Pagination works, filter by status/tier/tags, sort by any column |
| 1.1.6 | VendorService — get vendor detail (360-degree) | Returns vendor with scores, contacts, recent assessments, alerts |
| 1.1.7 | VendorService — update vendor | Updates fields, audit logged |
| 1.1.8 | VendorService — soft delete | Sets deleted_at, excluded from list queries |

### 1.2 Vendor API
| # | Function | Acceptance Criteria |
|---|----------|-------------------|
| 1.2.1 | `POST /vendors` — create vendor | 201 with vendor object. 422 on invalid input. Permission checked |
| 1.2.2 | `GET /vendors` — list vendors | Pagination, filter, sort all work. Empty state returns [] |
| 1.2.3 | `GET /vendors/{id}` — vendor detail | Full 360-degree view. 404 for missing. Cross-tenant blocked |
| 1.2.4 | `PUT /vendors/{id}` — update vendor | 200 with updated object. 403 for insufficient permission |
| 1.2.5 | `DELETE /vendors/{id}` — soft delete | 204 on success. Vendor no longer in list |

### 1.3 Vendor UI
| # | Function | Acceptance Criteria |
|---|----------|-------------------|
| 1.3.1 | Vendor list page with data table | Table loads real vendor data. Columns: name, tier, risk score, status, last assessed, actions |
| 1.3.2 | Vendor list — filtering (status, tier, risk level, search) | Each filter works. Combined filters work. Clear all works |
| 1.3.3 | Vendor list — sorting (click column headers) | Each sortable column toggles asc/desc/none |
| 1.3.4 | Vendor list — pagination | Page size selector (10/25/50). Next/prev. Page count |
| 1.3.5 | Vendor list — empty state | Clean message when no vendors. "Add Vendor" CTA |
| 1.3.6 | Create vendor modal/page | Form with all required fields. Validation. Success toast + redirect |
| 1.3.7 | Vendor detail page — overview tab | Hero card with name, tier badge, risk score gauge, status, key dates |
| 1.3.8 | Vendor detail page — contacts tab | List contacts, add/edit/delete contact |
| 1.3.9 | Vendor detail page — timeline tab | Chronological event list (placeholder for now, will populate as events happen) |
| 1.3.10 | Edit vendor — inline or modal | Pre-populated form, save updates, success toast |
| 1.3.11 | Delete vendor — confirmation dialog | "Are you sure?" modal with vendor name. Deletes on confirm |

### 1.4 Bulk Import (VLM-01)
| # | Function | Acceptance Criteria |
|---|----------|-------------------|
| 1.4.1 | `POST /vendors/bulk-import` — CSV upload | Parses CSV, creates vendors, returns success/failure per row |
| 1.4.2 | CSV validation (required fields, format) | Returns detailed error per invalid row |
| 1.4.3 | Bulk import UI — file upload + preview | Drag-drop CSV, preview first 5 rows, confirm to import |
| 1.4.4 | Bulk import UI — results screen | Shows created count, error count, downloadable error report |

### 1.5 Vendor Contacts
| # | Function | Acceptance Criteria |
|---|----------|-------------------|
| 1.5.1 | Vendor contacts table migration | Table created, encrypted email/phone fields |
| 1.5.2 | `GET /vendors/{id}/contacts` | Returns contacts list |
| 1.5.3 | `POST /vendors/{id}/contacts` | Creates contact, encrypted PII |
| 1.5.4 | `PUT /vendors/{id}/contacts/{contact_id}` | Updates contact |

### 1.6 Vendor Tiering (VLM-03)
| # | Function | Acceptance Criteria |
|---|----------|-------------------|
| 1.6.1 | Inherent risk tiering service | Calculates tier from weighted factors (data access, spend, criticality, regulatory) |
| 1.6.2 | `POST /vendors/{id}/calculate-tier` | Returns calculated tier with breakdown |
| 1.6.3 | Tier badge display on vendor list and detail | Color-coded tier badge (Critical=red, High=orange, Medium=yellow, Low=green) |

### 1.7 Tests
| # | Function | Acceptance Criteria |
|---|----------|-------------------|
| 1.7.1 | Unit tests: VendorService CRUD | All service methods tested. ≥90% coverage |
| 1.7.2 | Integration tests: Vendor API endpoints | All endpoints tested with valid/invalid/unauthorized requests |
| 1.7.3 | Frontend: Vendor list renders with test data | Component test with mock API response |
| 1.7.4 | E2E: Create vendor → appears in list → view detail | Full flow works end-to-end |

**Sprint 1 Gate**: Vendor list loads real data. Create/edit/delete work. Bulk CSV import works. Tier calculation works. Every button on vendor pages does something. Tests pass ≥80% coverage.

---

## Sprint 2: Assessment Engine (P0: ASM-01 through ASM-07)

### 2.1 Assessment Data Layer
| # | Function | Acceptance Criteria |
|---|----------|-------------------|
| 2.1.1 | Assessment tables migration (templates, assessments, questions, responses) | Tables created, RLS active, state machine enum |
| 2.1.2 | Assessment models + schemas | All models map correctly, lifecycle states enforced |
| 2.1.3 | AssessmentService — create assessment from template | Clones template questions, sets draft state |
| 2.1.4 | AssessmentService — assessment lifecycle state machine | State transitions enforced: draft→distributed→in_progress→submitted→under_review→completed |
| 2.1.5 | AssessmentService — distribute to vendor | Sets status, creates portal access token, starts SLA timer |
| 2.1.6 | AssessmentService — submit (vendor submits responses) | Validates all required responses, transitions state |
| 2.1.7 | AssessmentService — review queue | Returns assessments needing review, sorted by priority |

### 2.2 Assessment API
| # | Function | Acceptance Criteria |
|---|----------|-------------------|
| 2.2.1 | `GET /assessments` — list assessments | Filterable by status, vendor, template, date range |
| 2.2.2 | `POST /assessments` — create assessment | Creates from template for vendor. 201 response |
| 2.2.3 | `GET /assessments/{id}` — assessment detail | Full detail with questions, responses, scores |
| 2.2.4 | `POST /assessments/{id}/distribute` — distribute to vendor | Triggers notification, creates portal access |
| 2.2.5 | `POST /assessments/{id}/submit` — vendor submits | Validates completeness, transitions to review |
| 2.2.6 | `POST /assessments/{id}/start-review` — begin review | Assigns to analyst, transitions state |
| 2.2.7 | `POST /assessments/{id}/complete` — complete assessment | Calculates final score, generates findings |
| 2.2.8 | `GET /assessments/{id}/responses` — get responses | All questions with responses, confidence scores |
| 2.2.9 | `PUT /assessments/{id}/responses/{id}` — review response | Analyst accepts/modifies/flags response |
| 2.2.10 | `GET /assessments/review-queue` — review queue | Prioritized items needing analyst attention |
| 2.2.11 | `GET /assessments/templates` — list templates | Available assessment templates |
| 2.2.12 | `POST /assessments/templates` — create template | Custom template with questions and scoring |

### 2.3 Assessment UI
| # | Function | Acceptance Criteria |
|---|----------|-------------------|
| 2.3.1 | Assessment list page | Data table with status badges, vendor name, template, dates, progress bar |
| 2.3.2 | Assessment list — filtering and sorting | Filter by status, vendor, template. Sort by date, status |
| 2.3.3 | Create assessment — select vendor + template | Step 1: pick vendor. Step 2: pick template. Step 3: confirm. Creates assessment |
| 2.3.4 | Assessment detail — overview | Status badge, vendor info, scores, SLA countdown, action buttons |
| 2.3.5 | Assessment workspace — question list + answer panel | Left: question list with completion status. Right: selected question with response, evidence, confidence |
| 2.3.6 | Assessment workspace — review a response | Accept/modify/flag. Add analyst notes. Confidence indicator |
| 2.3.7 | Assessment workspace — progress tracking | Progress bar, section completion counts, time spent |
| 2.3.8 | Review queue page | List of items needing review, sorted by priority. Click to jump to response |
| 2.3.9 | Template management page | List templates, create/edit custom templates |
| 2.3.10 | Distribute assessment — confirmation + notification | Confirm dialog, sends notification, updates status |

### 2.4 Question Bank
| # | Function | Acceptance Criteria |
|---|----------|-------------------|
| 2.4.1 | Question bank table migration | Table with question types, options, framework links |
| 2.4.2 | Seed SIG Core/Lite question sets | Standard questionnaire questions loaded |
| 2.4.3 | Question types (yes/no, multiple choice, text, file upload, scale) | Each type renders correctly with proper input |

### 2.5 Tests
| # | Function | Acceptance Criteria |
|---|----------|-------------------|
| 2.5.1 | Unit tests: AssessmentService lifecycle | State machine transitions tested, invalid transitions rejected |
| 2.5.2 | Integration tests: Assessment API | All endpoints tested |
| 2.5.3 | E2E: Create assessment → distribute → submit → review → complete | Full lifecycle works end-to-end |

**Sprint 2 Gate**: Assessment lifecycle works end-to-end. Template selection works. Question workspace functional. Review queue shows items. Every button works. Tests pass ≥80%.

---

## Sprint 3: Framework Intelligence & Scoring Engine (P0: FRM-01, FRM-02, FRM-03, SCR-01 through SCR-04)

### 3.1 Framework Data Layer
| # | Function | Acceptance Criteria |
|---|----------|-------------------|
| 3.1.1 | Framework tables migration (frameworks, clauses, mappings) | Tables created, vector column for embeddings |
| 3.1.2 | Framework models + schemas | OSCAL format stored, clause tree navigable |
| 3.1.3 | FrameworkService — list frameworks | Returns available frameworks with clause counts |
| 3.1.4 | FrameworkService — get clause tree | Returns hierarchical clause structure |
| 3.1.5 | FrameworkService — cross-framework mapping | Returns mappings between framework clauses |
| 3.1.6 | Seed data: SOC 2, ISO 27001:2022, NIST CSF 2.0, HIPAA, PCI DSS 4.0, GDPR, DORA | All standard frameworks loaded with clauses |

### 3.2 Scoring Data Layer
| # | Function | Acceptance Criteria |
|---|----------|-------------------|
| 3.2.1 | Scoring tables migration (models, configs, vendor_scores, history) | Tables created |
| 3.2.2 | ScoringService — configurable scoring engine | JSON rules, weighted average + multiplicative methods |
| 3.2.3 | ScoringService — multi-dimensional scoring | 8 dimensions with configurable weights |
| 3.2.4 | ScoringService — calculate vendor score | Takes inputs, returns composite score with dimension breakdown |
| 3.2.5 | ScoringService — external rating normalization | Maps SecurityScorecard/BitSight scale to internal 0-100 |
| 3.2.6 | ScoringService — score history | Stores snapshots for trend analysis |

### 3.3 Framework & Scoring API
| # | Function | Acceptance Criteria |
|---|----------|-------------------|
| 3.3.1 | `GET /frameworks` — list frameworks | Returns all with metadata |
| 3.3.2 | `GET /frameworks/{id}/clauses` — clause tree | Hierarchical clause view |
| 3.3.3 | `GET /frameworks/{id}/clauses/{id}/mappings` — cross-mappings | Shows how clause maps to other frameworks |
| 3.3.4 | `GET /frameworks/unified-controls` — deduplicated controls | Single control library across frameworks |
| 3.3.5 | `GET /scoring/models` — list scoring models | Available models with configuration |
| 3.3.6 | `POST /scoring/calculate/{vendor_id}` — calculate score | Returns score with dimension breakdown |
| 3.3.7 | `GET /scoring/vendors/{vendor_id}` — current score | Score with breakdown and trend |
| 3.3.8 | `GET /scoring/vendors/{vendor_id}/history` — score history | Historical scores for trend chart |
| 3.3.9 | `GET /scoring/portfolio` — portfolio aggregation | Average, distribution, concentration metrics |

### 3.4 Framework & Scoring UI
| # | Function | Acceptance Criteria |
|---|----------|-------------------|
| 3.4.1 | Frameworks page — list all frameworks | Cards with name, version, clause count, status |
| 3.4.2 | Framework detail — clause browser | Expandable tree view of clauses |
| 3.4.3 | Framework detail — cross-mapping viewer | Select clause → see mapped clauses in other frameworks |
| 3.4.4 | Vendor detail — scoring tab | Risk score gauge, dimension breakdown radar chart, trend line |
| 3.4.5 | Scoring configuration page (admin) | Edit scoring model weights, thresholds, dimensions |
| 3.4.6 | Portfolio risk view | Distribution chart, average score, concentration indicators |

### 3.5 Tests
| # | Function | Acceptance Criteria |
|---|----------|-------------------|
| 3.5.1 | Unit tests: ScoringService calculations | Weighted average, multiplicative, normalization all tested |
| 3.5.2 | Integration tests: Framework + Scoring API | All endpoints tested |
| 3.5.3 | E2E: View framework → see mappings → calculate vendor score | Flow works end-to-end |

**Sprint 3 Gate**: Framework browser works. Scoring engine calculates correctly. Score displays on vendor detail. Portfolio view shows real data. Tests pass ≥80%.

---

## Sprint 4: Evidence Engine & AI Services (P0: ASM-03, ASM-04, VLM-02)

### 4.1 Evidence Data Layer
| # | Function | Acceptance Criteria |
|---|----------|-------------------|
| 4.1.1 | Evidence tables migration (evidence, extractions, control_mappings, versions) | Tables created, vector column for embeddings |
| 4.1.2 | Evidence models + schemas | File metadata, parsed content, mapping objects |
| 4.1.3 | EvidenceService — upload with presigned URL | Returns S3 presigned URL, creates evidence record |
| 4.1.4 | EvidenceService — process (parse document) | Extracts text, classifies document type, stores parsed content |
| 4.1.5 | EvidenceService — map to controls | Maps extracted content to framework controls with confidence |
| 4.1.6 | EvidenceService — list/get evidence | Returns evidence with extractions and mappings |

### 4.2 AI Service
| # | Function | Acceptance Criteria |
|---|----------|-------------------|
| 4.2.1 | AI Service — LLM abstraction (Anthropic primary, OpenAI fallback) | Provider-agnostic interface, cost tracking per call |
| 4.2.2 | AI Service — evidence parsing (SOC 2, ISO cert, pen test) | Extracts audit period, opinion, exceptions, control statuses |
| 4.2.3 | AI Service — questionnaire auto-fill | Pre-fills responses from evidence + prior responses, with citations |
| 4.2.4 | AI Service — risk narrative generation | Generates executive summary of vendor risk profile |
| 4.2.5 | AI Service — confidence scoring | 4-signal composite: retrieval relevance, source coverage, self-assessment, historical accuracy |
| 4.2.6 | Human-in-the-loop routing | High confidence → auto-approve. Low → review queue. Very low → manual |

### 4.3 Vendor Enrichment (VLM-02)
| # | Function | Acceptance Criteria |
|---|----------|-------------------|
| 4.3.1 | Vendor enrichment table migration | Table with per-source enrichment data |
| 4.3.2 | EnrichmentService — firmographic data (from domain/name) | Company size, industry, location, founding year |
| 4.3.3 | EnrichmentService — security rating lookup | External rating ingestion (mock for MVP, real integration later) |
| 4.3.4 | `POST /vendors/{id}/enrich` — trigger enrichment | Returns enrichment results |
| 4.3.5 | Vendor detail — enrichment display | Shows enriched data cards on vendor profile |

### 4.4 Evidence API
| # | Function | Acceptance Criteria |
|---|----------|-------------------|
| 4.4.1 | `POST /evidence/upload-url` — presigned upload | Returns signed URL for client-side upload |
| 4.4.2 | `POST /evidence/{id}/process` — trigger parsing | Kicks off AI parsing pipeline |
| 4.4.3 | `GET /evidence` — list evidence | Filterable by vendor, type, status |
| 4.4.4 | `GET /evidence/{id}` — evidence detail | Full detail with extractions and mappings |
| 4.4.5 | `GET /evidence/{id}/mappings` — control mappings | Shows which controls this evidence covers |
| 4.4.6 | `PUT /evidence/{id}/mappings/{id}` — verify/modify mapping | Analyst confirms/rejects AI mapping |

### 4.5 Evidence UI
| # | Function | Acceptance Criteria |
|---|----------|-------------------|
| 4.5.1 | Evidence list page | Data table with file name, type, vendor, status, upload date |
| 4.5.2 | Evidence upload — drag-and-drop | Drop zone, progress bar, auto-triggers processing |
| 4.5.3 | Evidence detail — parsed content viewer | Shows extracted fields, confidence scores, source highlights |
| 4.5.4 | Evidence detail — control mapping viewer | Shows mapped controls with coverage type and confidence |
| 4.5.5 | Evidence detail — verify/reject mappings | Analyst can approve/reject each mapping |
| 4.5.6 | AI review queue integration | Evidence needing review appears in review queue |

### 4.6 AI Module API
| # | Function | Acceptance Criteria |
|---|----------|-------------------|
| 4.6.1 | `POST /ai/auto-fill` — pre-fill assessment | Returns pre-filled responses with citations + confidence |
| 4.6.2 | `POST /ai/parse-evidence` — trigger evidence parsing | Kicks off parsing pipeline, returns job ID |
| 4.6.3 | `GET /ai/review-queue` — items needing review | Combined queue: evidence mappings + assessment responses |
| 4.6.4 | `PUT /ai/review-queue/{id}` — submit review decision | Accept/modify/reject with notes |
| 4.6.5 | `GET /ai/usage` — AI usage stats | Token counts, cost, provider breakdown |

### 4.7 Tests
| # | Function | Acceptance Criteria |
|---|----------|-------------------|
| 4.7.1 | Unit tests: EvidenceService, AIService | All methods tested, mock LLM responses |
| 4.7.2 | Integration tests: Evidence + AI API | Upload, parse, map, review flow tested |
| 4.7.3 | E2E: Upload SOC 2 → AI parses → maps to controls → analyst reviews | Full flow works |

**Sprint 4 Gate**: Evidence upload works with drag-drop. AI parses documents. Control mappings display. Review queue functional. Enrichment populates vendor profiles. Tests pass ≥80%.

---

## Sprint 5: Continuous Monitoring & Alerts (P0: MON-01, MON-02)

### 5.1 Monitoring Data Layer
| # | Function | Acceptance Criteria |
|---|----------|-------------------|
| 5.1.1 | Monitoring tables migration (configs, signals, alerts, rules, timeline) | Tables created |
| 5.1.2 | MonitoringService — signal ingestion | Accepts signals, deduplicates, stores |
| 5.1.3 | MonitoringService — alert creation from signals | Applies rules, creates P0-P4 alerts |
| 5.1.4 | MonitoringService — alert lifecycle (acknowledge, investigate, resolve, suppress) | State machine enforced |
| 5.1.5 | MonitoringService — vendor timeline | Chronological event aggregation |

### 5.2 Monitoring API
| # | Function | Acceptance Criteria |
|---|----------|-------------------|
| 5.2.1 | `GET /monitoring/alerts` — list alerts | Filterable by priority, status, vendor |
| 5.2.2 | `GET /monitoring/alerts/{id}` — alert detail | Full context: signals, vendor, impact assessment |
| 5.2.3 | `PUT /monitoring/alerts/{id}/acknowledge` | Transitions alert, records who/when |
| 5.2.4 | `PUT /monitoring/alerts/{id}/resolve` | Resolves with resolution notes |
| 5.2.5 | `GET /monitoring/vendors/{vendor_id}/timeline` | Vendor risk timeline |
| 5.2.6 | `GET /monitoring/alert-rules` — list rules | Available alert rules |
| 5.2.7 | `POST /monitoring/alert-rules` — create rule | Custom rule with conditions and actions |

### 5.3 Monitoring UI
| # | Function | Acceptance Criteria |
|---|----------|-------------------|
| 5.3.1 | Alerts page — alert list | Data table with priority color coding, status, vendor, date |
| 5.3.2 | Alert detail page | Signal context, vendor info, recommended actions |
| 5.3.3 | Alert actions — acknowledge, investigate, resolve | Each button works, transitions state, updates UI |
| 5.3.4 | Vendor detail — timeline tab (populated) | Shows all events chronologically with type icons |
| 5.3.5 | Alert rules configuration page (admin) | Create/edit rules with condition builder |

### 5.4 Tests
| # | Function | Acceptance Criteria |
|---|----------|-------------------|
| 5.4.1 | Unit tests: MonitoringService | Signal processing, alert creation, dedup tested |
| 5.4.2 | Integration tests: Monitoring API | All endpoints tested |
| 5.4.3 | E2E: Signal arrives → alert created → acknowledge → resolve | Full flow works |

**Sprint 5 Gate**: Alerts display with priority. Lifecycle transitions work. Timeline shows events. Rules engine works. Tests pass ≥80%.

---

## Sprint 6: Executive Dashboard & Reporting (P0: RPT-01, RPT-02)

### 6.1 Dashboard Data
| # | Function | Acceptance Criteria |
|---|----------|-------------------|
| 6.1.1 | Dashboard data aggregation service | Queries across vendors, assessments, findings, alerts |
| 6.1.2 | `GET /reports/dashboards/data/executive` | Returns all dashboard widget data in one call |
| 6.1.3 | Dashboard widget configs table + defaults | Default layout, per-user customization |

### 6.2 Dashboard UI
| # | Function | Acceptance Criteria |
|---|----------|-------------------|
| 6.2.1 | Executive dashboard — summary metrics row | Total vendors, active assessments, open findings, critical alerts. Animated counters |
| 6.2.2 | Risk heatmap (impact x likelihood) | Interactive, click cell → filtered vendor list |
| 6.2.3 | Vendor risk distribution chart | Bar/donut chart of vendors by risk tier |
| 6.2.4 | Risk trend chart (30/60/90 day) | Line chart with configurable time range |
| 6.2.5 | Top 10 highest-risk vendors table | Sorted by score, tier badge, trend indicator |
| 6.2.6 | Recent alerts feed | Latest alerts with priority badges, timestamp |
| 6.2.7 | Assessment pipeline status | Funnel: draft → distributed → in_progress → completed |
| 6.2.8 | Compliance posture widget | Framework coverage heatmap |

### 6.3 Report Generation
| # | Function | Acceptance Criteria |
|---|----------|-------------------|
| 6.3.1 | ReportService — generate PDF report | Compiles data, AI narrative, charts into PDF |
| 6.3.2 | `POST /reports/generate` — trigger report | Returns job ID, generates async |
| 6.3.3 | `GET /reports/{id}/download` — download report | Returns presigned S3 URL |
| 6.3.4 | Report generation UI | Select template → configure → generate → download |
| 6.3.5 | Report list page | Previous reports with download links |

### 6.4 Tests
| # | Function | Acceptance Criteria |
|---|----------|-------------------|
| 6.4.1 | Unit tests: Dashboard aggregation, report generation | Data aggregation correct, PDF generates |
| 6.4.2 | E2E: Dashboard loads with real data → generate report → download | Full flow works |

**Sprint 6 Gate**: Dashboard shows real data across all widgets. Interactive charts work. Report generates and downloads. Tests pass ≥80%.

---

## Sprint 7: Communications & Vendor Portal (P0: COM-01, COM-02, VPT-01)

### 7.1 Communications
| # | Function | Acceptance Criteria |
|---|----------|-------------------|
| 7.1.1 | Communications tables migration (notifications, preferences, templates, logs) | Tables created |
| 7.1.2 | NotificationService — in-app notifications | Creates notifications, marks read |
| 7.1.3 | NotificationService — email sending (SendGrid/SMTP) | Emails send with template content |
| 7.1.4 | `GET /communications/notifications` | User's notification list |
| 7.1.5 | `PUT /communications/notifications/{id}/read` | Marks as read |
| 7.1.6 | Notification bell in header | Badge count, dropdown list, mark read, mark all read |
| 7.1.7 | Email template management | List/create/edit templates |
| 7.1.8 | Automated assessment reminders (Day 7/14/21) | Scheduled emails trigger correctly |

### 7.2 Vendor Portal
| # | Function | Acceptance Criteria |
|---|----------|-------------------|
| 7.2.1 | Portal auth (token-based + authenticated access) | Vendor accesses portal via link, or login |
| 7.2.2 | `GET /portal/assessments` — vendor's assessments | Shows only assessments for this vendor |
| 7.2.3 | `GET /portal/assessments/{id}` — assessment with questions | Full questionnaire for vendor to complete |
| 7.2.4 | `POST /portal/assessments/{id}/responses` — submit responses | Vendor saves/submits responses |
| 7.2.5 | `POST /portal/assessments/{id}/evidence` — upload evidence | Vendor uploads supporting docs |
| 7.2.6 | Portal UI — assessment list | Vendor sees their pending/completed assessments |
| 7.2.7 | Portal UI — questionnaire workspace | Vendor answers questions, uploads evidence per question |
| 7.2.8 | Portal UI — findings view | Vendor sees findings with remediation guidance |

### 7.3 Tests
| # | Function | Acceptance Criteria |
|---|----------|-------------------|
| 7.3.1 | Unit tests: NotificationService, portal access | All methods tested |
| 7.3.2 | Integration tests: Communications + Portal API | All endpoints tested |
| 7.3.3 | E2E: Distribute assessment → vendor opens portal → completes → submits | Cross-system flow works |

**Sprint 7 Gate**: In-app notifications work. Email sends. Vendor portal accessible. Vendor can complete assessment through portal. Tests pass ≥80%.

---

## Sprint 8: Admin, RBAC & Audit (P0: ADM-01 through ADM-05)

### 8.1 Admin Features
| # | Function | Acceptance Criteria |
|---|----------|-------------------|
| 8.1.1 | User management — list, invite, deactivate | Admin can manage users |
| 8.1.2 | Role management — create custom roles, assign permissions | RBAC fully functional |
| 8.1.3 | Audit log — immutable, queryable, exportable | Every action logged, searchable, CSV export |
| 8.1.4 | Tenant settings page | All config types editable (scoring, workflows, escalation, notifications) |
| 8.1.5 | Integration management — configure external connections | List integrations, test connectivity |
| 8.1.6 | `GET /admin/audit-logs` — query audit trail | Filterable by user, action, date range, entity |
| 8.1.7 | `POST /admin/audit-logs/export` — export | CSV/JSON export with date range |

### 8.2 SSO/SAML/OIDC (ADM-03)
| # | Function | Acceptance Criteria |
|---|----------|-------------------|
| 8.2.1 | SAML 2.0 SSO flow | Redirect → IdP → callback → session created |
| 8.2.2 | OIDC flow | Standard OIDC auth code flow |
| 8.2.3 | SSO configuration UI (admin) | Enter IdP metadata URL, map attributes |

### 8.3 API-First (ADM-05)
| # | Function | Acceptance Criteria |
|---|----------|-------------------|
| 8.3.1 | OpenAPI 3.0 spec auto-generation | `/docs` serves complete Swagger UI |
| 8.3.2 | API key generation and management | Create/revoke API keys, rate limited |
| 8.3.3 | Webhook configuration | Register webhook URLs, event filtering |

### 8.4 Tests
| # | Function | Acceptance Criteria |
|---|----------|-------------------|
| 8.4.1 | Unit tests: Admin services | User management, role assignment, audit logging |
| 8.4.2 | Integration tests: RBAC enforcement | Users with different roles see different data/actions |
| 8.4.3 | E2E: Create user → assign role → verify access restrictions | Permissions enforced end-to-end |

**Sprint 8 Gate**: User/role management works. Audit trail complete. SSO flow functional. API keys work. Tests pass ≥80%.

---

## Sprint 9: Findings, Remediation & P1 Features

### 9.1 Findings Management (ASM-08, ASM-09)
| # | Function | Acceptance Criteria |
|---|----------|-------------------|
| 9.1.1 | Findings tables migration | Tables with severity, SLA, remediation tracking |
| 9.1.2 | FindingsService — auto-generate from assessment gaps | Creates findings with severity and remediation guidance |
| 9.1.3 | FindingsService — lifecycle (open → remediation → verified → closed) | State machine works |
| 9.1.4 | Findings list page | Data table with severity, vendor, status, SLA countdown |
| 9.1.5 | Finding detail — remediation tracker | Shows remediation steps, evidence, verification status |
| 9.1.6 | Vendor portal — remediation submission | Vendor submits evidence for finding remediation |

### 9.2 Onboarding/Offboarding Workflows (VLM-05, VLM-06)
| # | Function | Acceptance Criteria |
|---|----------|-------------------|
| 9.2.1 | Vendor onboarding workflow engine | Configurable multi-step: intake, assessment, approval |
| 9.2.2 | Vendor offboarding checklist | Access revocation, data return, decommission tracking |

### 9.3 Assessment Scheduling (ASM-10)
| # | Function | Acceptance Criteria |
|---|----------|-------------------|
| 9.3.1 | Automated assessment scheduling | Tier-based frequency (annual/biennial), auto-creates draft |

### 9.4 Monitoring Enhancements (MON-03, MON-04)
| # | Function | Acceptance Criteria |
|---|----------|-------------------|
| 9.4.1 | Vendor risk timeline (populated from all events) | Complete chronological view |
| 9.4.2 | Trend analysis with 30/60/90 day predictions | Trend lines on scoring charts |

### 9.5 FAIR Risk Quantification (SCR-05)
| # | Function | Acceptance Criteria |
|---|----------|-------------------|
| 9.5.1 | FAIR calculation service | Annual Loss Expectancy from frequency/magnitude |
| 9.5.2 | FAIR display on vendor detail + dashboard | Financial risk shown in currency |

### 9.6 Additional P1 Features
| # | Function | Acceptance Criteria |
|---|----------|-------------------|
| 9.6.1 | Score override with audit trail (SCR-06) | Override with justification, approval, expiry |
| 9.6.2 | Framework versioning and diffing (FRM-04) | Version comparison, affected assessment flagging |
| 9.6.3 | Custom framework support (FRM-05) | Admin creates custom framework |
| 9.6.4 | DORA Register of Information (FRM-06) | Auto-generated regulatory export |
| 9.6.5 | In-app collaboration — comments + @mentions (COM-03) | Threaded comments on vendors/assessments/findings |
| 9.6.6 | Escalation automation (COM-04) | Rule-based escalation chains |
| 9.6.7 | Regulatory compliance reports (RPT-03) | DORA, HIPAA, GDPR specific reports |
| 9.6.8 | Operational analytics dashboard (RPT-04) | Throughput, cycle time, SLA adherence |
| 9.6.9 | Vendor trust profiles (VPT-02) | Persistent, shareable trust profiles |
| 9.6.10 | Nth-party mapping (VLM-07) | Sub-processor graph, concentration risk |
| 9.6.11 | Portfolio risk aggregation with concentration (SCR-07) | Geo/industry/tech concentration analysis |
| 9.6.12 | Integration connectors — Jira, Slack, Teams (ADM-06) | Create Jira tickets from findings, Slack alerts |

### 9.7 Tests
| # | Function | Acceptance Criteria |
|---|----------|-------------------|
| 9.7.1 | Unit tests for all Sprint 9 features | ≥80% coverage |
| 9.7.2 | Integration tests for all new endpoints | All tested |
| 9.7.3 | E2E: Finding created → remediation submitted → verified → closed | Works end-to-end |

**Sprint 9 Gate**: Findings lifecycle complete. FAIR quantification works. All P1 features functional. Integration connectors work. Tests pass ≥80%.

---

## Sprint 10: Integration, Polish & Full QA

### 10.1 Cross-Feature Integration
| # | Function | Acceptance Criteria |
|---|----------|-------------------|
| 10.1.1 | Dashboard updates from all modules | Real-time data from vendors, assessments, findings, alerts, scores |
| 10.1.2 | Event bus — all events flow correctly | Vendor change → score recalc → timeline update → notification |
| 10.1.3 | All navigation cross-links work | Vendor → assessments → findings → evidence all interconnected |
| 10.1.4 | Command palette — search across all entities | Cmd+K finds vendors, assessments, findings, alerts |

### 10.2 Visual Polish
| # | Function | Acceptance Criteria |
|---|----------|-------------------|
| 10.2.1 | Premium micro-interactions | Score change animations, hover effects, smooth transitions |
| 10.2.2 | Loading states for all async operations | Skeleton/spinner on every API call |
| 10.2.3 | Empty states for all lists | Clean illustrations/messages, actionable CTAs |
| 10.2.4 | Responsive design (1024px+) | All pages usable on laptop screens |
| 10.2.5 | Navy theme applied consistently | Stripe-inspired navy, consistent tokens throughout |
| 10.2.6 | Typography and spacing audit | Consistent heading hierarchy, whitespace, alignment |

### 10.3 Security Hardening
| # | Function | Acceptance Criteria |
|---|----------|-------------------|
| 10.3.1 | OWASP Top 10 audit | No SQL injection, XSS, CSRF, etc |
| 10.3.2 | PII encryption verification | All PII fields encrypted at rest |
| 10.3.3 | RLS isolation tests | Cross-tenant data access impossible |
| 10.3.4 | Rate limiting verification | All endpoints rate limited |
| 10.3.5 | Secret scanning | Zero secrets in code |

### 10.4 Performance
| # | Function | Acceptance Criteria |
|---|----------|-------------------|
| 10.4.1 | API response time audit | p95 <200ms reads, <500ms writes |
| 10.4.2 | Dashboard load time | <2 seconds for 500 vendors |
| 10.4.3 | Database query optimization | No N+1 queries, proper indexes |
| 10.4.4 | Frontend bundle size audit | No unnecessary dependencies, code splitting |

### 10.5 Full Test Suite
| # | Function | Acceptance Criteria |
|---|----------|-------------------|
| 10.5.1 | Unit test coverage ≥80% across entire codebase | Coverage report generated |
| 10.5.2 | Integration tests for all API endpoints | All ~141 endpoints tested |
| 10.5.3 | E2E tests for all primary user journeys | All 4 personas' journeys automated |
| 10.5.4 | Security tests (prompt injection, PII scan) | Zero critical findings |
| 10.5.5 | Regression suite | All previous sprint tests pass |

**Sprint 10 Gate**: Every feature works end-to-end. Every button does something. Every page loads real data. Premium visual quality. Security hardened. Tests pass. Performance meets targets. READY FOR GATE 5.

---

## MCA Process Per Function

```
For EVERY function in every sprint:

1. MAKER (Nirmitya): Builds function + writes tests
   - Code follows Blueprint Section 10.1 (40 lines/function, 200 lines/class, 400 lines/file)
   - Tests follow Blueprint Section 10.3 (≥80% coverage)
   - Security follows Blueprint Section 10.4

2. CHECKER (Samikshon): Code review
   - Reviews code quality, patterns, security
   - Runs tests, verifies they pass
   - Checks no dead code, no mock data (after Sprint 0)

3. APPROVER (Tantron as CTO): Technical approval
   - Verifies function works end-to-end (DB→API→UI)
   - Checks architectural consistency
   - Tests the actual running app

If rejected → Developer fixes → Re-review → Re-approve
Multiple iterations until genuinely satisfactory
No moving to next function until current is approved
```

---

## Execution Tool Routing

| Sprint Type | Tool |
|-------------|------|
| Sprint 0 (foundation) | **Ralph** — sequential foundation setup |
| Sprint 1-9 (features) | **Ralph** — one vertical slice at a time |
| Hotfixes during sprint | **Aider** — single-file patches |
| Sprint 10 (integration) | **Ralph** — cross-cutting integration work |

Ralph runs with **NO iteration limits**. Iterate until clean.

---

## Summary

| Sprint | Focus | P0 Features | Key Deliverable |
|--------|-------|-------------|-----------------|
| 0 | Foundation | ADM-01, ADM-02 | Working app shell with auth + navigation |
| 1 | Vendors | VLM-01, VLM-03, VLM-04 | Vendor CRUD, import, tiering |
| 2 | Assessments | ASM-01, ASM-02, ASM-05, ASM-06, ASM-07 | Assessment lifecycle end-to-end |
| 3 | Frameworks + Scoring | FRM-01, FRM-02, FRM-03, SCR-01-04 | Framework browser, scoring engine |
| 4 | Evidence + AI | ASM-03, ASM-04, VLM-02 | Evidence parsing, AI services |
| 5 | Monitoring | MON-01, MON-02 | Alerts, monitoring, timeline |
| 6 | Dashboard + Reports | RPT-01, RPT-02 | Executive dashboard, PDF reports |
| 7 | Comms + Portal | COM-01, COM-02, VPT-01 | Notifications, vendor portal |
| 8 | Admin | ADM-03, ADM-04, ADM-05 | RBAC, audit, SSO, API |
| 9 | P1 Features | 12 P1 features | Findings, FAIR, integrations, workflows |
| 10 | Polish + QA | — | Integration, security, performance, full test suite |
