---
tags:
  - archeon
  - forgeon
  - product
  - product-velora
---

# Velora TPRM — Allocation Plan v1.0

> Built by Harion. Archeon's first product build.
> Product: Velora TPRM — AI-first Third-Party Risk Management platform
> Date: 2026-03-27

---

## Team Assembly

### MCA Matrix by Phase

| Phase | Maker | Checker | Approver | Status |
|-------|-------|---------|----------|--------|
| **0. Intake + Setup** | Harion | — | — | DONE |
| **1. Ideation** | Darshika | Anveshon (market validation) | Rudron | PENDING |
| **2. PRD** | Darshika | Tantron (feasibility) + Rakshon (security req) | Rudron | PENDING |
| **3. HLD** | Rachnika | Tantron (arch review) + Rakshon (security arch) | Rudron | PENDING |
| **4. LLD** | Vinyason | Tantron (design review) | Rudron | PENDING |
| **4. UI/UX** | Rupika | Darshika (brand/product alignment) | Rudron | PENDING |
| **5. Research** | Anveshon | Darshika (validates against PRD) | Rudron | IN_PROGRESS |
| **5. Data Collection** | Sangraha | Anveshon (data quality) | Rudron | PENDING |
| **6. Sprint Plan** | Yojika | Tantron (tech validation) + Arthon (budget) | Rudron | PENDING |
| **7. Agent Setup** | Mantrius | Harion (orchestration fit) | Rudron | PENDING |
| **8. Code (Full-stack)** | Nirmitya | Samikshon (code review) + Rakshon (security) | Rudron | PENDING |
| **8. Code (Frontend)** | Drishyon | Samikshon (code review) + Parikshika (visual QA) | Rudron | PENDING |
| **8. Infrastructure** | Prasaron | Rakshon (security) + Tantron (arch alignment) | Rudron | PENDING |
| **8. Tech Docs** | Bodhika | Samikshon (accuracy) | Rudron | PENDING |
| **9. QA Report** | Parikshika | Dev agent (verifies fix feasibility) | Rudron | PENDING |
| **9. Security Audit** | Rakshon | Parikshika (cross-validates) | Rudron | PENDING |
| **Post: Content** | Kathika | Darshika (brand alignment) | Rudron | PENDING |
| **Post: Growth/SEO** | Vriddhon | Kathika (content alignment) | Rudron | PENDING |
| **Cross: Cost** | Arthon | Harion (validates against scope) | Rudron | ACTIVE (monitor-only) |

---

## Agent Allocation Summary

| Agent | Phases Involved | Primary Role |
|-------|----------------|--------------|
| **Harion** | All | Orchestrator |
| **Darshika** | 1, 2 | CPO — ideation, PRD |
| **Tantron** | 2, 3, 4, 6 | CTO — feasibility, arch review |
| **Anveshon** | 5 (parallel) | Domain researcher — TPRM market, frameworks, scoring |
| **Rachnika** | 3 | System architect — HLD |
| **Vinyason** | 4 | System designer — LLD |
| **Rupika** | 4 | UI/UX designer — premium light-theme executive design |
| **Yojika** | 6 | Sprint planner |
| **Mantrius** | 7 | Prompt engineer (if AI agents needed in product) |
| **Nirmitya** | 8 | Full-stack dev (Python/FastAPI + TypeScript/Next.js) |
| **Drishyon** | 8 | Frontend dev (if vanilla components needed) |
| **Prasaron** | 8, 9 | DevOps + infra |
| **Samikshon** | 8 | Code reviewer |
| **Parikshika** | 9 | QA engineer |
| **Rakshon** | 2, 3, 4, 8, 9 | CISO — security throughout |
| **Rudron** | All | Quality gate — approves every phase |
| **Arthon** | Cross-phase | Finance — MONITOR-ONLY mode |
| **Bodhika** | 8, 9 | Technical writer |
| **Kathika** | Post-launch | Content strategist |
| **Vriddhon** | Post-launch | Growth/SEO |
| **Sangraha** | 5, 8 | Data collection (framework ingestion pipelines) |
| **Lekhika** | Cross-phase | Doc sync daemon |
| **Yantrion** | Cross-phase | IT health daemon |

**Total agents allocated: 23/25** (Brahmica and Vartika not needed for this build)

---

## Gaps Identified

| Gap | Severity | Resolution |
|-----|----------|------------|
| None | — | Full roster covers all Blueprint phases |

---

## Special Directives

### Arthon — Monitor-Only Mode
Per Devam's directive (2026-03-27): Arthon tracks cost in real-time but does **NOT** auto-pause the pipeline on budget thresholds. Cost monitoring continues for visibility. No budget caps enforced for this build.

### Research Runs Parallel to Phase 1-2
Anveshon's research (Phase 5) runs in parallel with Darshika's ideation/PRD (Phase 1-2). Research findings feed into the PRD. Per Devam's feedback memory: cross-check the detailed brief against market research and suggest better alternatives where found.

### Cross-Check Mandate
Even though Devam provided a very detailed JSON metaprompt, all agents must:
1. Cross-check brief claims against market research
2. Suggest better tools/approaches/features where research supports them
3. Add features discovered through research that weren't in the original brief
4. Apply same cross-check to technical architecture decisions

---

## Estimated Token Budget (Phases 0-2-5)

| Phase | Agent | Model | Est. Tokens | Est. Cost |
|-------|-------|-------|-------------|-----------|
| 0 | Harion | Opus | ~8,000 | ~$0.72 |
| 5 | Anveshon (x3 parallel) | Opus | ~45,000 | ~$4.05 |
| 1 | Darshika | Opus | ~8,000 | ~$0.72 |
| 2 | Darshika | Opus | ~20,000 | ~$1.80 |
| 2 | Tantron (check) | Opus | ~5,000 | ~$0.45 |
| 2 | Rakshon (check) | Opus | ~5,000 | ~$0.45 |
| 2 | Rudron (approve) | Opus | ~3,000 | ~$0.27 |
| **Total** | | | **~94,000** | **~$8.46** |

**Budget mode: MONITOR-ONLY** — no auto-pause.

---

## Pipeline Execution Order

```
[DONE]    Phase 0: Intake + Setup (Harion)
[ACTIVE]  Phase 5: Research — 3 parallel agents (Anveshon)
[NEXT]    Phase 1: Ideation (Darshika) — starts when research completes
[NEXT]    Phase 2: PRD (Darshika + research integration)
[GATE 1]  → Notify Devam: Allocation Plan (this document)
[GATE 2]  → Notify Devam: Research + PRD complete
[THEN]    Phase 3: HLD (Rachnika)
[THEN]    Phase 4: LLD + UI/UX (Vinyason + Rupika)
[GATE 3]  → Notify Devam: Architecture + Design ready
[THEN]    Phase 6-8: Sprint → Execute (Yojika → Nirmitya/Drishyon)
[GATE 4]  → Notify Devam: Product built + QA passed
[AUDIT]   Pre-launch audit (5 agents parallel)
[GATE 5]  → Notify Devam: Release ready (NO auto-proceed)
```

---

## Version History

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-03-27 | Initial allocation plan |
