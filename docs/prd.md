---
tags:
  - archeon
  - forgeon
  - product
  - product-velora
---

# Velora TPRM -- Product Requirements Document

> **Product**: Velora TPRM (Third-Party Risk Management)
> **Author**: Darshika (Chief Product Officer, Pantheon)
> **Version**: 1.0.0
> **Date**: 2026-03-27
> **Status**: Draft -- Pending MCA Review
> **Classification**: Internal -- Product Strategy

---

## Table of Contents

1. [Product Overview and Vision](#1-product-overview-and-vision)
2. [Problem Statement](#2-problem-statement)
3. [Target Users and Personas](#3-target-users-and-personas)
4. [User Journeys](#4-user-journeys)
5. [Value Hypothesis](#5-value-hypothesis)
6. [Competitive Landscape Analysis](#6-competitive-landscape-analysis)
7. [Moat Analysis](#7-moat-analysis)
8. [AI Resilience Assessment](#8-ai-resilience-assessment)
9. [Feature Requirements](#9-feature-requirements)
10. [Non-Functional Requirements](#10-non-functional-requirements)
11. [Success Metrics](#11-success-metrics)
12. [Go-to-Market Strategy](#12-go-to-market-strategy)
13. [Pricing and Business Model](#13-pricing-and-business-model)
14. [Risk Assessment](#14-risk-assessment)
15. [Dependencies and Constraints](#15-dependencies-and-constraints)
16. [Timeline and Milestones](#16-timeline-and-milestones)
17. [Open Questions](#17-open-questions)
18. [Appendices](#18-appendices)
19. [Brief Cross-Check Report](#19-brief-cross-check-report)

---

## 1. Product Overview and Vision

### What Velora TPRM Is

Velora TPRM is an AI-native third-party risk management platform that unifies the entire vendor risk lifecycle -- discovery, classification, assessment, onboarding, continuous monitoring, reassessment, and offboarding -- in a single, config-driven product. It replaces the fragmented stack of security ratings tools, questionnaire platforms, and legacy GRC modules that organizations currently stitch together.

### Why It Exists

The TPRM market is approximately $9.5B in 2025 and growing at 14-17% CAGR toward $20B by 2030 (Grand View Research, Liminal, MarketsandMarkets consensus). Yet the industry suffers from a structural failure: 73% of institutions have two or fewer full-time employees managing vendor risk across 286+ vendors (Ncontracts 2025 Survey). Nearly 30% of breaches in 2024 involved a third-party supplier -- double the previous year (Verizon 2025 DBIR). Regulatory pressure from DORA, NIS2, SEC cyber rules, and GDPR Art 28 enforcement is accelerating faster than existing tools can adapt.

Current platforms fall into narrow categories -- ratings-only (SecurityScorecard, BitSight), questionnaire-only (Whistic), compliance-add-on (Vanta, Drata), or heavyweight GRC (ServiceNow, Archer, OneTrust) -- each leaving significant gaps. No platform today is simultaneously AI-native, full-lifecycle, config-driven, and vendor-collaborative.

### Vision Statement

Velora TPRM delivers autonomous, continuous third-party risk intelligence where AI handles the assessment burden and humans focus on decisions. Within 18 months, organizations using Velora should assess 10x more vendors with the same headcount, reduce assessment cycle time from weeks to hours, and express vendor risk in financial terms their boards understand.

### Design Philosophy

- **AI-first, human-confirmed**: AI infers, enriches, and scores; humans review and decide.
- **Config-driven**: Every scoring model, workflow, escalation rule, and questionnaire is admin-configurable without code.
- **Premium light-theme executive design**: Information-dense but visually clean; built for board presentations and daily analyst work alike.
- **Vendor-collaborative, not adversarial**: Vendors participate through a trust portal; evidence shared once serves all requesting customers.

---

## 2. Problem Statement

### Primary Problems (Evidence-Backed)

**Problem 1: Catastrophic understaffing against growing vendor portfolios.**
73% of institutions have 2 or fewer FTEs managing vendor risk (Ncontracts 2025). Average vendor count is 286 and rising 21% year-over-year. Assessment teams spend 37.4 hours per week on assessments -- up 14 hours from prior year (Whistic 2025 Impact Report). The math does not work: there are not enough humans to assess this volume at the depth regulators demand.

**Problem 2: Questionnaire-based assessment is broken but irreplaceable.**
75% of vendors either fail to respond to questionnaires or respond untimely (Whistic 2025). Only 4% of organizations trust that questionnaire responses reflect real security posture (Whistic). Yet questionnaires remain the primary method because regulators expect documented due diligence. The industry needs a way to maintain the rigor of questionnaires while eliminating the burden.

**Problem 3: Point-in-time assessments create dangerous blind spots.**
Annual or quarterly assessments leave months of unmonitored exposure. Breach data on underground forums increased 43% in 2024 (BitSight Trace). Organizations that rely on annual assessments have no mechanism to detect when a vendor's posture degrades between cycles. Continuous monitoring exists in ratings tools but is disconnected from assessment workflows.

**Problem 4: Tool fragmentation forces compromise.**
Organizations need ratings (SecurityScorecard/BitSight), assessment workflows (ProcessUnity/Prevalent), evidence management, and GRC integration. No single tool covers all four well. Mid-market organizations cannot afford the $200K-$500K+ stacks that large enterprises assemble. This forces teams onto spreadsheets and email for the gaps.

**Problem 5: Regulatory velocity outpaces tool adaptation.**
DORA (Jan 2025), NIS2 (Oct 2024-2026), SEC cyber rules (2023), PCI DSS 4.0 (Mar 2025), and the EU Cyber Resilience Act are all imposing new third-party requirements. Framework version lag is a persistent problem -- tools are slow to update cross-framework mappings when standards like ISO 27001:2022, NIST CSF 2.0, and PCI DSS 4.0 release new versions.

---

## 3. Target Users and Personas

### Persona 1: Anya Kohli -- TPRM Program Lead

- **Title**: Director of Third-Party Risk Management
- **Organization**: 3,000-employee financial services firm
- **Team size**: 3 analysts (herself + 2 reports)
- **Vendor portfolio**: 420 active vendors, 85 classified as Tier 1/2
- **Current tools**: ServiceNow GRC (hates it), SecurityScorecard (likes scores, hates fragmentation), Excel for tracking
- **Daily reality**: Spends 60% of her week chasing vendor responses and manually reviewing SOC 2 reports. Needs to demonstrate DORA compliance to the board by Q3 2026.
- **Pain points**: Cannot scale beyond current vendor count without hiring; assessment cycle takes 45+ days; no single view of risk; board asks for financial impact data she cannot produce.
- **Success criteria for Velora**: Reduce assessment cycle to under 7 days for standard vendors; automatically parse SOC 2 and ISO 27001 evidence; produce DORA-ready Register of Information; dashboard her CEO can read.

### Persona 2: Marcus Chen -- CISO

- **Title**: Chief Information Security Officer
- **Organization**: 8,000-employee healthcare company
- **Vendor portfolio**: 600+ vendors including critical EHR, cloud hosting, and claims processing
- **Current tools**: Archer (legacy, painful), BitSight (monitoring only)
- **Daily reality**: Oversees TPRM program but delegates execution. Needs risk metrics for quarterly board reports. Under pressure from audit committee on HIPAA vendor compliance.
- **Pain points**: Archer is expensive, slow, and his team dreads using it. BitSight gives scores but not remediation workflows. He cannot quantify vendor risk in dollar terms. Audit findings cite incomplete vendor assessments.
- **Success criteria for Velora**: Board-ready risk quantification in financial terms; HIPAA and SOC 2 framework mapping that auditors accept; reduce Archer dependency; fewer audit findings.

### Persona 3: Priya Nair -- GRC Analyst

- **Title**: Senior GRC Analyst
- **Organization**: 1,200-employee SaaS company
- **Vendor portfolio**: 180 vendors, growing 30% YoY with company growth
- **Current tools**: Vanta (compliance), spreadsheets (TPRM)
- **Daily reality**: Manually reviews every vendor questionnaire response. Spends hours cross-referencing SOC 2 reports against questionnaire answers. Responsible for ISO 27001 and SOC 2 compliance for her own company and assessing the same from vendors.
- **Pain points**: Vanta handles compliance but vendor risk is an afterthought. No automated evidence parsing. Questionnaire responses are inconsistent and unverifiable. She knows there are gaps but cannot quantify them.
- **Success criteria for Velora**: AI-parsed evidence with control-to-framework mapping; automated inconsistency detection between vendor responses and evidence; one tool instead of Vanta + spreadsheets for VRM.

### Persona 4: David Park -- Vendor Security Responder (Vendor-Side)

- **Title**: Security Compliance Manager at a 200-person SaaS vendor
- **Organization**: Responds to 40-60 security questionnaires per quarter from customers
- **Current tools**: SafeBase trust center, manual copy-paste from prior responses
- **Daily reality**: Each customer sends a different questionnaire format. He spends 3-4 hours per questionnaire copying answers from prior responses, adapting wording, and gathering updated evidence. The process is repetitive and error-prone.
- **Pain points**: Repetitive work across overlapping questionnaires; no way to share evidence once and have it consumed by multiple customers; every customer's portal is different.
- **Success criteria for Velora**: Vendor trust portal where he uploads evidence once; AI pre-fills questionnaire responses from his published trust profile; customers consume his data without requiring unique submissions each time.

---

## 4. User Journeys

### Journey 1: First Login and Organization Setup (Anya)

1. Anya signs up, authenticates via SSO (SAML/OIDC), and creates her organization.
2. Velora prompts her through a 4-step org setup wizard: company profile (AI infers industry, size, regulatory exposure from domain), regulatory framework selection (defaults suggested based on industry), scoring model configuration (default 5x5 matrix pre-loaded, customizable), and team role assignment.
3. AI enriches the org profile from public data -- Anya reviews and confirms inferences rather than filling forms manually.
4. Velora offers bulk vendor import (CSV, API integration with procurement systems, or SSO/OAuth discovery). Anya uploads her vendor list.
5. For each vendor, AI performs initial enrichment: firmographics, security rating (if SecurityScorecard/BitSight integration is active), certification status lookup, trust center detection.
6. AI auto-suggests inherent risk tier for each vendor based on data sensitivity, access level, and business criticality. Anya reviews and adjusts tiers.
7. Time to first meaningful risk view: under 2 hours for a portfolio of 400 vendors.

### Journey 2: Vendor Assessment Workflow (Priya)

1. Priya selects a Tier 1 cloud SaaS vendor for annual reassessment.
2. Velora auto-selects assessment template based on vendor tier and applicable frameworks (SIG Core + CAIQ v4, mapped to SOC 2 and ISO 27001).
3. AI pre-populates the questionnaire from: (a) vendor's prior responses, (b) vendor's trust center/published documentation, (c) public information and enrichment data.
4. Velora sends the assessment to the vendor portal with a 30-day deadline. Automated reminders fire at Day 7, 14, 21 (escalating tone and recipients).
5. Vendor (David) receives the assessment, sees AI pre-filled answers with citations, reviews and corrects where needed, uploads current SOC 2 Type II report and ISO 27001 certificate.
6. Velora's evidence engine parses the SOC 2 report: extracts audit period, opinion type, exceptions, individual control statuses. Maps controls to questionnaire responses. Flags inconsistencies (e.g., vendor claims MFA is enforced, but SOC 2 report notes an exception on MFA for a subset of systems).
7. AI generates a risk score combining questionnaire responses, evidence confidence, and external rating. Items below confidence threshold route to Priya's review queue.
8. Priya reviews 12 flagged items (out of 180 total controls), accepts 8, modifies 3, escalates 1 for CISO review. Total time: 90 minutes instead of the previous 3 days.
9. Findings with remediation guidance auto-generate for gaps identified. Vendor receives prioritized remediation plan with SLA deadlines through the portal.

### Journey 3: Continuous Monitoring and Incident Response (Marcus)

1. At 2:14 AM, Velora's monitoring engine detects a P0 signal: a critical SaaS vendor's credentials appear on a dark web marketplace. Within the same 30-minute monitoring cycle, a security rating drop of 18 points is detected.
2. Alert engine correlates both signals, elevates to P0, and auto-creates an investigation ticket.
3. Marcus receives an SMS alert and email with structured context: vendor name, tier, data sensitivity, signal details, recommended immediate actions.
4. Velora's AI generates an impact assessment: what data this vendor accesses, which regulatory obligations are affected (HIPAA, SOC 2), estimated financial exposure using FAIR methodology.
5. Marcus triggers an event-driven reassessment directly from the alert -- Velora sends a fast-track SIG Lite questionnaire plus requests for updated pen test results and incident response details.
6. All actions, communications, and decisions log to the vendor's risk timeline for audit purposes.

### Journey 4: Board Reporting (Marcus)

1. Marcus opens the executive dashboard. Real-time portfolio risk summary shows: 420 vendors assessed, 12 critical findings open, aggregate portfolio risk trending down 8% QoQ, 3 vendors with DORA compliance gaps.
2. He generates a board report: Velora produces a PDF with risk heatmap, top-10 riskiest vendors, financial exposure estimates (FAIR-based), regulatory compliance posture by framework, and trend analysis.
3. The report includes AI-generated narrative summaries for each section. Marcus reviews and approves in 15 minutes.
4. He exports DORA Register of Information in the regulatory-mandated format.

---

## 5. Value Hypothesis

### Why Users Switch

| Current State | Velora Value | Switching Trigger |
|--------------|-------------|-------------------|
| 2-3 fragmented tools (ratings + assessment + GRC) | Unified platform covering full lifecycle | Contract renewal of any existing tool |
| 45+ day assessment cycles | Under 7-day cycle with AI pre-fill and auto-scoring | Audit finding citing assessment backlog |
| Manual SOC 2 / ISO cert review (3-4 hours each) | AI parsing in minutes with control-to-framework mapping | Scaling past 200 vendors with existing headcount |
| Spreadsheet-based vendor tracking | Real-time dashboard with continuous monitoring | Board or regulator demands real-time risk posture |
| No financial risk quantification | FAIR-based dollar-value risk estimates | Board requests quantified risk exposure |
| No DORA/NIS2 support | Native DORA and NIS2 compliance modules | Regulatory deadline approaching |

### Why Users Stay

1. **Data gravity**: Assessment history, evidence library, vendor profiles, and scoring calibrations accumulate over time -- switching cost increases with usage.
2. **Vendor network effect**: As more vendors populate their trust profiles on Velora's exchange, the assessment burden decreases for all customers -- creating mutual lock-in.
3. **Workflow embedding**: Escalation rules, approval chains, notification preferences, and custom scoring models become organizational knowledge encoded in the platform.
4. **Regulatory continuity**: Audit trails and compliance records in Velora become the system of record for regulatory examination -- migration risks data integrity.

---

## 6. Competitive Landscape Analysis

### Competitive Comparison Matrix

| Capability | Velora TPRM | OneTrust | ProcessUnity | SecurityScorecard | BitSight | Vanta | Drata | SAFE Security | Whistic |
|-----------|-------------|----------|-------------|-------------------|----------|-------|-------|---------------|---------|
| AI-native architecture | Yes | Bolt-on (2025) | Bolt-on | Limited | Limited | Emerging | Emerging | Yes | Yes (claims 90%) |
| Full vendor lifecycle | Yes | Yes | Yes | Partial | Partial | Partial | Partial | Partial | Partial |
| Questionnaire automation | AI pre-fill + parse | AI-assisted | AI autofill + exchange | Limited | Limited | AI reviews | AI agent | GenAI analysis | AI-first |
| Evidence parsing (SOC 2, ISO) | AI extraction + mapping | Manual | AI evaluator | No | No | Partial | Partial | Partial | Partial |
| Continuous monitoring | Multi-signal hub | Basic | Via CyberGRX | Core strength | Core strength | Basic | Basic | Yes | Native (30-min) |
| Outside-in scanning | Integrated | Basic | Via CyberGRX | Core strength | Core strength | No | No | Yes | Via RiskRecon |
| FAIR risk quantification | Native | No | No | No | No | No | No | Yes | No |
| Config-driven scoring | Full admin control | Limited | Limited | Proprietary | Proprietary | Limited | Limited | Proprietary | Unknown |
| Vendor portal / trust exchange | Native | Limited | CyberGRX Exchange | No | Limited | Trust Center | No | No | Trust Center Exchange |
| DORA/NIS2 native modules | Yes | Yes | Partial | No | Partial | No | No | Partial | No |
| Cross-framework mapping | AI + OSCAL + OLIR | Manual | Limited | No | No | Pre-built | Pre-built | Limited | Limited |
| Nth-party visibility | 4th-party mapping | Yes | 4th-party | Limited | Limited | No | No | Partial | No |
| Time to value | Hours | Months | Weeks-Months | Days | Days | Days | Days | Weeks | Days |
| Target segment | Mid-market to Enterprise | Enterprise | Enterprise | Mid-Ent | Enterprise | SMB-Mid | SMB-Mid | Mid-Ent | Mid-market |
| Price range (annual) | $30K-$250K | $44K-$500K+ | Custom (high) | $22K+ (escalates) | $22K+ (escalates) | $11K-$80K | $7.5K-$100K+ | Custom | Custom |

### Key Competitive Insights

1. **ProcessUnity** is the current Forrester Wave Leader (2026) with the most complete dedicated TPRM platform post-CyberGRX merger. Its CyberGRX Exchange (14,000 attested assessments, data on 250,000+ companies) is a significant data moat. Velora must build a competing vendor trust network.

2. **SAFE Security** is the closest philosophical competitor -- also positioning as AI-autonomous with FAIR-based quantification. However, SAFE is newer and unproven at scale. Velora should match SAFE on FAIR integration while delivering superior UX, configurability, and framework depth.

3. **Vanta and Drata** own the SMB-mid-market compliance segment and are expanding into TPRM. Their VRM modules are add-ons, not core products, limiting depth. Velora targets above them (mid-market to enterprise) where these tools fall short.

4. **SecurityScorecard and BitSight** dominate outside-in ratings but are not full lifecycle TPRM platforms. Velora should integrate their APIs as data sources rather than competing on scanning infrastructure.

---

## 7. Moat Analysis

### Three-Tier Moat Model

**Tier 1: Data Moat (12-18 months to build)**
- Vendor trust profiles accumulate assessment history, evidence libraries, and enrichment data that improve AI accuracy over time.
- Cross-customer vendor data (anonymized) enables population-level benchmarking ("vendors in your industry with similar profiles have an average risk score of X").
- Framework intelligence corpus -- clause-level embeddings, cross-framework mappings, assessment-to-control linkages -- becomes more accurate with every assessment processed.
- **Strength**: Medium-High. Network effects compound. Requires critical mass of vendor profiles (target: 10,000 vendor trust profiles within 18 months).

**Tier 2: Workflow Moat (6-12 months to build)**
- Customer-specific scoring models, escalation rules, approval chains, custom questionnaires, and notification preferences encode organizational knowledge.
- Integration depth with customer's existing systems (SSO, ITSM, procurement, SIEM) raises switching cost.
- Audit trail and regulatory evidence history become the compliance system of record.
- **Strength**: High. Workflow moats are the most durable in enterprise SaaS because switching means re-encoding institutional knowledge.

**Tier 3: Network Moat (18-36 months to build)**
- Vendor trust exchange where vendors share security posture once and customers consume without redundant assessments.
- ProcessUnity/CyberGRX has 14,000 attested assessments in their exchange; Whistic and Vanta have competing trust networks. Velora must build its own.
- Strategy: Incentivize vendor participation by reducing their assessment burden (AI pre-fills from their trust profile), making the vendor experience superior to competitors.
- **Strength**: Highest long-term, but slowest to build. Network moats are defensible once established.

### Moat Durability Assessment

The workflow moat is the most defensible because it does not depend on proprietary AI capability (which commoditizes) but on accumulated organizational configuration and compliance history that is painful to migrate. The data moat strengthens the AI accuracy advantage over time. The network moat provides the longest-term defensibility but requires deliberate investment in vendor-side experience.

---

## 8. AI Resilience Assessment

### The 10x LLM Test

**Question**: If a competitor deployed a language model 10x more capable than Velora's underlying LLM, would Velora become obsolete?

**Answer**: No. Here is why:

1. **AI is an accelerator, not the product.** Velora's value is in the assembled system: framework intelligence corpus, vendor trust profiles, cross-customer benchmarking data, and encoded workflow logic. A better LLM improves the system but does not replace it. Velora can (and will) swap LLM providers as capabilities improve.

2. **Data moat is LLM-independent.** The vendor enrichment data, assessment history, evidence corpus, framework mappings (OSCAL + OLIR), and trust exchange profiles are proprietary to Velora's platform, not to any AI model.

3. **Workflow moat is LLM-independent.** Customer-configured scoring models, escalation chains, approval workflows, and integration connections persist regardless of AI capability.

4. **Regulatory trust is earned, not computed.** Auditors trust platforms with demonstrated accuracy and audit trail completeness. A new AI-powered competitor must earn this trust over years of proven assessments.

5. **Where AI improvement helps Velora:** Better LLMs improve evidence parsing accuracy, questionnaire pre-fill quality, and predictive scoring -- these improvements benefit Velora equally because the platform is LLM-agnostic by architecture (abstracted through platform-core/llm-abstraction).

### Vulnerability Zones

- If a major platform player (Google, Microsoft, ServiceNow) builds native TPRM into their existing ecosystems with superior AI, the distribution advantage could be significant. Mitigation: Velora must achieve workflow moat and data moat before this occurs (18-month window).
- If vendor trust networks consolidate around a single exchange (e.g., CyberGRX becomes universal), Velora's network moat becomes harder to build. Mitigation: Interoperability with existing exchanges and superior vendor experience.

---

## 9. Feature Requirements

### Module 1: Vendor Lifecycle Management

| ID | Feature | Priority | Description |
|----|---------|----------|-------------|
| VLM-01 | Vendor inventory with bulk import | P0 | CSV upload, API import from procurement systems (Coupa, SAP Ariba), SSO/OAuth-based discovery. Each vendor record stores: name, domain, industry, size, tier, contacts, contracts, risk scores. |
| VLM-02 | AI-powered vendor enrichment | P0 | On vendor creation, auto-enrich from public sources: firmographics (Clearbit/ZoomInfo), security ratings (SecurityScorecard/BitSight API integration), certification lookups (IAF CertSearch, UKAS), trust center detection, breach history (HIBP). AI infers industry, size, tech stack from company domain. |
| VLM-03 | Inherent risk tiering engine | P0 | Auto-classify vendors into 4 tiers based on weighted factors: data sensitivity classification (PII/PHI/financial/IP), access level (network, application, data, physical), business criticality (revenue dependency, operational dependency), regulatory exposure. Admin-configurable factor weights and tier thresholds. |
| VLM-04 | Vendor profile management | P0 | 360-degree vendor view: enrichment data, risk scores (inherent, residual, external, composite), assessment history, evidence library, monitoring timeline, findings, contacts, contracts. |
| VLM-05 | Vendor onboarding workflow | P1 | Configurable multi-step workflow: intake request, inherent risk assessment, approval routing (based on tier), contract review checklist, DPA tracking, access provisioning checklist. |
| VLM-06 | Vendor offboarding workflow | P1 | Checklist-driven: access revocation verification, data return/destruction confirmation, integration decommission, risk register update, closure documentation. |
| VLM-07 | Fourth-party (Nth-party) mapping | P1 | Track vendor sub-processors and critical sub-contractors. Auto-detect from vendor DPA/sub-processor lists (AI extraction). Visualize supply chain graph. Concentration risk analysis: identify vendors that share critical Nth-party dependencies. |
| VLM-08 | Automated vendor discovery | P2 | Discover shadow IT vendors from: SSO/IdP logs (Okta, Azure AD), financial systems (expense reports, AP systems), browser extension (optional). |
| VLM-09 | Multi-entity vendor management | P2 | Support parent-subsidiary structures where the same vendor may be assessed differently by different business units or regions. Per-entity risk views with consolidated parent view. |

### Module 2: Assessment Engine

| ID | Feature | Priority | Description |
|----|---------|----------|-------------|
| ASM-01 | Framework-aware questionnaire engine | P0 | Pre-built questionnaire templates mapped to SIG Core (627 questions), SIG Lite (128), CAIQ v4 (~260), CAIQ Lite (71), custom templates. Each question linked to framework clause(s). Auto-select template based on vendor tier and applicable frameworks. |
| ASM-02 | AI questionnaire pre-population | P0 | LLM pre-fills questionnaire from: vendor's prior responses, trust center documentation, public information, evidence artifacts. Each pre-filled answer includes citation and confidence score. Low-confidence answers flagged for vendor review. |
| ASM-03 | Evidence parsing and extraction | P0 | Upload SOC 2 reports, ISO 27001 certificates, pen test reports, policies. AI extracts: audit period, opinion type, control statuses, exceptions, certificate validity, findings. Uses Azure Document Intelligence for PDF layout analysis + LLM for semantic extraction. |
| ASM-04 | Evidence-to-control mapping | P0 | Auto-map parsed evidence to framework controls with coverage type (full/partial/supportive) and confidence score. SOC 2 Type II maps to CC1-CC9 (full), ISO 27001 cert maps to Annex A controls (full for certified scope), pen test maps to vulnerability management controls (partial). |
| ASM-05 | Hybrid risk scoring | P0 | Composite score = weighted combination of: questionnaire score, evidence score (weighted by freshness and confidence), external rating (normalized from SecurityScorecard A-F or BitSight 250-900 to internal 0-100), scan results. All weights admin-configurable. |
| ASM-06 | Assessment distribution and tracking | P0 | Send assessments to vendor portal with configurable deadlines (default: 30 days SIG Core, 14 days SIG Lite). SLA timer with automated reminder cadence (Day 7/14/21). Escalation rules when SLA breached. |
| ASM-07 | AI-assisted review queue | P0 | AI validates response consistency (cross-references answers against evidence, flags contradictions). Routes items below confidence threshold to human review queue. Role-based assignment. Reviewer accepts/modifies/rejects with justification. |
| ASM-08 | Findings management | P1 | Auto-generate findings from assessment gaps. Each finding: severity (Critical/High/Medium/Low), description, remediation guidance (AI-generated), deadline (based on severity SLA: Critical 30d, High 60d, Medium 90d), assignment to vendor contact and internal owner. |
| ASM-09 | Remediation tracking and verification | P1 | Vendors submit remediation evidence through portal. AI verifies remediation addresses the finding. Status tracking: Open, Remediation In Progress, Submitted for Verification, Verified Closed, Risk Accepted. |
| ASM-10 | Assessment scheduling automation | P1 | Calendar-based reassessment triggers: annual for Tier 1/2, biennial for Tier 3, triennial for Tier 4. Event-triggered fast-track assessment on breach, M&A, rating drop >10pts, certification expiry. Contract renewal reassessment at 90-day lead time. |
| ASM-11 | Natural language risk Q&A | P2 | "Ask Velora" interface: users query vendor risk in plain language (e.g., "Which vendors have access to PHI and have not completed a SOC 2 assessment in the last 12 months?"). LLM translates to structured query, returns results with citations. |
| ASM-12 | Contract risk analysis | P2 | AI extracts risk-relevant clauses from vendor contracts: data processing terms, liability caps, indemnification, breach notification requirements, termination/exit provisions. Flags missing standard provisions. Research-identified gap: contract analysis is "barely present" in current TPRM tools. |

### Module 3: Framework Intelligence

| ID | Feature | Priority | Description |
|----|---------|----------|-------------|
| FRM-01 | Framework library | P0 | Pre-loaded: SOC 2 TSC (~60 criteria), ISO 27001:2022 (93 Annex A controls), NIST CSF 2.0 (106 subcategories), HIPAA Security Rule (~50 standards), PCI DSS 4.0 (250+ requirements), GDPR (key articles), DORA (64 articles), NIS2 (46 articles). Internal storage format: OSCAL JSON for machine-readability. |
| FRM-02 | Cross-framework mapping engine | P0 | Import NIST OLIR mappings as baseline. AI-assisted mapping for pairs not covered by OLIR. Store mappings with confidence score and human verification status. Key pairs: SOC 2 to ISO 27001 (~96% overlap), NIST CSF to ISO 27001 (~80%), SOC 2 to HIPAA (~60%), ISO 27001 to GDPR Art 32 (~65%). |
| FRM-03 | Unified control library | P0 | Single internal control taxonomy where each control is tagged with its framework source(s). Enables: one questionnaire response satisfies multiple frameworks, one evidence artifact covers controls across frameworks. Eliminates redundant assessment for multi-framework vendors. |
| FRM-04 | Framework versioning and diffing | P1 | When frameworks release new versions, clause-level diff computed (added/modified/removed controls). Affected assessments and mappings flagged. Tenants notified of impacts. |
| FRM-05 | Custom framework support | P1 | Admins create custom questionnaire frameworks for organization-specific requirements. Custom frameworks can reference and map to standard framework controls. |
| FRM-06 | DORA Register of Information | P1 | Auto-generate DORA-mandated Register of Information from vendor data. Export in regulatory format. Map vendor assessments to DORA articles. Concentration risk analysis per DORA requirements. |
| FRM-07 | Regulatory change intelligence | P2 | Monitor framework publisher feeds (RSS, OSCAL catalog diffs, regulatory body announcements). AI assesses impact of regulatory changes on existing vendor assessments. Auto-flag vendors affected by new requirements. |

### Module 4: Scoring Engine

| ID | Feature | Priority | Description |
|----|---------|----------|-------------|
| SCR-01 | Configurable scoring engine | P0 | Admin-defined scoring models stored as JSON rules. Support weighted average and multiplicative models. Default 5x5 inherent risk matrix (likelihood x impact). Configurable thresholds for risk tiers (Critical >85, High 70-84, Medium 40-69, Low <40). Per-industry and per-regulation scoring templates. |
| SCR-02 | Multi-dimensional risk scoring | P0 | Separate scores for: security posture (20-25% default weight), data sensitivity (15-20%), business criticality (15-20%), compliance status (10-15%), control maturity (10-15%), incident history (5-10%), financial stability (5-10%), Nth-party risk (5%). All weights admin-configurable. |
| SCR-03 | Inherent-to-residual risk calculation | P0 | Support both calculation methods: (a) Inherent Risk - Control Effectiveness = Residual Risk (subtraction), (b) Inherent Risk x (1 - Control Effectiveness%) = Residual Risk (multiplication, recommended default). Admin chooses method per scoring template. |
| SCR-04 | External rating normalization | P0 | Normalize SecurityScorecard (A-F / 0-100), BitSight (250-900), and RiskRecon ratings to Velora's internal 0-100 scale. Configurable normalization curves. |
| SCR-05 | FAIR-based financial risk quantification | P1 | Translate vendor risk scores into estimated dollar-value loss exposure using FAIR methodology. Loss Event Frequency x Loss Magnitude = Annual Loss Expectancy. Enables "what-if" analysis and supports risk acceptance/transfer decisions in financial terms. |
| SCR-06 | Score override with audit trail | P1 | Manual score adjustment with mandatory justification field. Full audit log: who overrode, when, previous score, new score, reasoning. Override expires on next assessment unless renewed. |
| SCR-07 | Portfolio-level risk aggregation | P1 | Aggregate individual vendor scores into portfolio risk metrics: average risk, risk distribution, concentration risk (single-vendor dependency, geographic concentration), trend analysis (30/60/90-day). |
| SCR-08 | Peer benchmarking | P2 | Anonymized cross-customer benchmarking: "Your portfolio risk score is X vs. industry median of Y." Requires sufficient data volume to preserve anonymity. |

### Module 5: Continuous Monitoring

| ID | Feature | Priority | Description |
|----|---------|----------|-------------|
| MON-01 | Multi-signal monitoring hub | P0 | Aggregate signals from: security ratings APIs (SecurityScorecard, BitSight), breach databases (HIBP, Breachsense), dark web monitoring (commercial feeds), news/media, certificate transparency logs, DNS monitoring. Configurable monitoring frequency by vendor tier (critical: 4-hour, high: daily, standard: weekly, low: monthly). |
| MON-02 | Alert engine with prioritization | P0 | Priority classification: P0 (active breach involving your data, ransomware attack), P1 (critical CVE, leaked credentials, rating drop >15pts), P2 (cert expiry, DNS changes, regulatory action), P3 (moderate rating drop 5-15pts, cert expiry approaching, key personnel departure), P4 (minor fluctuation). Deduplication within 24-hour windows. Correlation: multiple P2/P3 from same vendor within 48h elevates to P1. |
| MON-03 | Vendor risk timeline | P1 | Visual chronological view per vendor: rating changes, assessments completed, evidence uploaded, alerts triggered, findings opened/closed, remediation activities. Enables pattern recognition and audit storytelling. |
| MON-04 | Trend analysis and prediction | P1 | 30/60/90-day trend detection. Flag vendors with persistent downward trajectory even if no single drop triggers an alert. AI-powered predictive risk signals: based on behavioral patterns, predict which vendors are most likely to experience a security incident. |
| MON-05 | CVE impact correlation | P2 | When new CVEs publish, auto-identify which monitored vendors are likely affected based on known technology stack (from enrichment data). Generate proactive outreach to affected vendors. |

### Module 6: Vendor Portal and Trust Exchange

| ID | Feature | Priority | Description |
|----|---------|----------|-------------|
| VPT-01 | Vendor self-service portal | P0 | White-labeled portal for vendors to: receive and complete assessments, upload evidence, view findings and remediation requests, track SLA status, communicate with requesting organization. No Velora account required for basic portal access. |
| VPT-02 | Vendor trust profile | P1 | Vendors create a persistent trust profile: certifications, SOC 2 report availability, security documentation, sub-processor list, data processing locations. Profile is shareable with multiple Velora customers. Vendors update once; all connected customers see updates. |
| VPT-03 | Trust exchange marketplace | P2 | Vendors proactively publish their security posture. Customers browse and consume trust profiles without initiating full assessments. Reduces assessment burden for both sides. Competitive with CyberGRX Exchange and Whistic Trust Center Exchange. |

### Module 7: Reporting and Dashboards

| ID | Feature | Priority | Description |
|----|---------|----------|-------------|
| RPT-01 | Executive dashboard | P0 | Real-time portfolio summary: total vendors by tier and risk level, aggregate risk score with trend, top-10 riskiest vendors, open findings by severity, assessment completion rates, regulatory compliance posture heatmap. |
| RPT-02 | Board-ready report generation | P0 | Automated PDF/PPTX report with: risk heatmap, vendor portfolio analysis, financial exposure estimates, regulatory posture summary, trend analysis, AI-generated narrative sections. Configurable templates. |
| RPT-03 | Regulatory compliance reports | P1 | Framework-specific reports: DORA Register of Information, HIPAA vendor compliance matrix, GDPR Article 28 processor assessment summary, PCI DSS third-party compliance status. Export in regulatory-expected formats. |
| RPT-04 | Operational analytics | P1 | Internal metrics: assessment throughput, average cycle time, vendor response rates, SLA adherence, analyst productivity, AI automation rate. |
| RPT-05 | Scheduled report delivery | P2 | Auto-generate and email reports on configurable schedule (weekly, monthly, quarterly). Different report types to different stakeholders. |

### Module 8: Communications Engine

| ID | Feature | Priority | Description |
|----|---------|----------|-------------|
| COM-01 | Automated vendor outreach | P0 | Template-based email with dynamic content (vendor name, deadline, specific requests, portal link). Configurable sender identity. Reminder cadence engine: Day 7, 14, 21 with escalating recipients. |
| COM-02 | Internal notifications | P0 | Configurable per user role: in-app, email, Slack/Teams webhook, SMS (P0 alerts only via Twilio). Notification preferences per alert priority. |
| COM-03 | In-app collaboration | P1 | Threaded comments on assessments, findings, evidence, and vendor profiles. @mentions for assignment and awareness. Full audit trail of all communications. |
| COM-04 | Escalation automation | P1 | Rule-based escalation: non-response > 30d escalates from analyst to procurement lead to business owner to CISO (5 business days per level). Critical finding escalates to CISO within 24h. Active vendor breach triggers incident response chain within 1h. |

### Module 9: Platform and Administration

| ID | Feature | Priority | Description |
|----|---------|----------|-------------|
| ADM-01 | Multi-tenant isolation | P0 | Row-Level Security on PostgreSQL with tenant_id on every table. JWT-based tenant context. Tiered isolation options: shared schema (standard), schema-per-tenant (premium), database-per-tenant (enterprise). |
| ADM-02 | RBAC with ABAC overlay | P0 | 8 core roles: Super Admin, TPRM Manager, Risk Analyst, Vendor Relationship Manager, Auditor (read-only + evidence), Executive (dashboards + reports), Vendor Portal User, API Service Account. ABAC dynamic policies for conditional access (e.g., critical vendors require CISO approval). Custom role creation. |
| ADM-03 | SSO/SAML/OIDC authentication | P0 | Enterprise SSO integration. SAML 2.0 and OIDC support. MFA enforcement configurable per tenant. Session management with configurable timeout (default 30 min). |
| ADM-04 | Complete audit trail | P0 | Every action logged: actor, action, resource, changes (old/new values), IP address, timestamp. Immutable audit log partitioned by month. Exportable for regulatory examination. Retention policy: minimum 7 years (configurable). |
| ADM-05 | API-first architecture | P0 | RESTful API with OpenAPI 3.0 spec. All UI functionality available via API. API key management with scoping. Rate limiting per tenant. Webhook support for event-driven integrations. |
| ADM-06 | Integration marketplace | P1 | Pre-built integrations: SecurityScorecard, BitSight, Jira, ServiceNow, Slack, Teams, Okta, Azure AD, AWS SSO, Coupa, SAP Ariba. Webhook-based custom integrations. |
| ADM-07 | Data residency controls | P2 | Region-specific database deployments for data sovereignty (EU, US, APAC). Tenant-level data residency configuration. |

### Research-Driven Features Not in Original Brief

| ID | Feature | Priority | Rationale |
|----|---------|----------|-----------|
| RDF-01 | Cross-vendor pattern analysis | P2 | Research gap: no current tool identifies systemic risks across vendor portfolios (e.g., 15 vendors all depend on the same cloud provider, creating concentration risk). Market research identifies this as "absent" in current tools. |
| RDF-02 | Regulatory change impact assessment | P2 | Research gap: when new regulations publish, auto-assess which existing vendor assessments are affected and what gaps are created. Identified as "absent" in current tools. |
| RDF-03 | Automated vendor discovery from SSO/financial systems | P2 | Multiple research sources cite shadow IT as a major gap. UpGuard offers automated discovery as a differentiator. Velora should match this. |
| RDF-04 | Vendor relationship health scoring | P2 | Research insight: assessment processes damage vendor relationships (identified as pain point). Track vendor responsiveness, collaboration quality, and communication health as a relationship metric alongside risk. |
| RDF-05 | AI-generated remediation plans | P1 | Research gap: tools identify risks but do not generate specific, prioritized remediation plans. AI should generate concrete remediation steps with effort estimates and priority ranking. |

---

## 10. Non-Functional Requirements

### Performance

| Metric | Target | Measurement |
|--------|--------|-------------|
| API response time (p95) | < 200ms for read operations, < 500ms for write operations | Application Performance Monitoring |
| Dashboard load time | < 2 seconds for executive dashboard with 500 vendors | Real User Monitoring |
| Search latency | < 50ms for vendor/control/evidence search | Typesense query metrics |
| Evidence parsing throughput | Process 100-page SOC 2 report in < 3 minutes | Job completion metrics |
| Concurrent users per tenant | 50+ simultaneous users without degradation | Load testing |
| Vendor portal response | < 1 second page load for vendor-facing portal | RUM |

### Security

| Requirement | Standard | Implementation |
|-------------|----------|----------------|
| Encryption in transit | TLS 1.3 (minimum TLS 1.2) | Mandatory on all connections |
| Encryption at rest | AES-256 | PostgreSQL TDE / RDS encryption, S3 SSE-KMS |
| Field-level encryption | AES-256-GCM | PII fields, credentials, API keys |
| Key management | AWS KMS or HashiCorp Vault | Centralized, audited key rotation |
| Authentication | SAML 2.0, OIDC, MFA | Per-tenant configuration |
| Authorization | RBAC + ABAC hybrid | 8 core roles + dynamic attribute policies |
| Data isolation | Row-Level Security | tenant_id on every table, RLS policies |
| Audit logging | Immutable, complete | Every action, every actor, every change |
| Vulnerability management | OWASP Top 10 compliance | Pre-deployment scanning, dependency auditing |
| Penetration testing | Annual by accredited firm | Mandatory before GA and annually thereafter |
| SOC 2 Type II | Self-certification | Velora must achieve SOC 2 Type II within 12 months of GA |
| GDPR compliance | Full | Data processing agreements, right to erasure, data portability |

### Scalability

| Dimension | Target (Year 1) | Target (Year 3) |
|-----------|-----------------|-----------------|
| Tenants | 500 | 5,000 |
| Vendors per tenant | 1,000 | 10,000 |
| Assessments per month (platform-wide) | 10,000 | 500,000 |
| Evidence documents stored | 500,000 | 10,000,000 |
| Monitoring signals processed per day | 100,000 | 5,000,000 |
| API requests per day | 1,000,000 | 50,000,000 |

### Availability

| Metric | Target |
|--------|--------|
| Uptime SLA | 99.9% (8.76 hours maximum downtime per year) |
| RPO (Recovery Point Objective) | < 1 hour |
| RTO (Recovery Time Objective) | < 4 hours |
| Backup frequency | Continuous WAL archiving + daily snapshots |
| Disaster recovery | Multi-AZ deployment, cross-region backup |

### Compliance

Velora TPRM must be certifiable under: SOC 2 Type II, ISO 27001, GDPR (as processor), HIPAA (BAA-capable). The platform stores customer data about their vendors -- it must meet the same standards it helps customers enforce.

---

## 11. Success Metrics

### Primary Metrics (First 12 Months Post-GA)

| Metric | Target | Failure Threshold | Measurement |
|--------|--------|-------------------|-------------|
| Assessment cycle time | < 7 days median for standard vendors (from distribution to scored completion) | > 14 days median | Platform analytics |
| AI automation rate | > 70% of questionnaire fields pre-filled without human modification | < 50% | Field-level tracking |
| Evidence parsing accuracy | > 85% control extraction accuracy (validated by human review sample) | < 75% | Quarterly accuracy audit |
| Time to first value | < 4 hours from signup to first vendor risk view (with 100+ vendors imported) | > 1 business day | Onboarding funnel analytics |
| Customer activation rate | > 60% of signed customers active (assessed 10+ vendors) within 30 days | < 40% | Product analytics |
| Net Revenue Retention | > 120% at month 12 (expansion > churn) | < 100% | Revenue analytics |
| Customer count | 50 paying customers by month 12 | < 20 | CRM |
| ARR | $2M by month 12 | < $750K | Revenue analytics |

### Secondary Metrics

| Metric | Target | Failure Threshold | Measurement |
|--------|--------|-------------------|-------------|
| Vendor response rate | > 80% of questionnaires completed within SLA (vs. industry average 25%) | < 50% | Platform analytics |
| NPS | > 50 | < 30 | Quarterly survey |
| Vendor trust profiles created | 10,000 within 18 months | < 3,000 | Platform analytics |
| Framework coverage accuracy | > 95% clause-level accuracy on cross-framework mappings | < 90% | Expert audit |
| Mean time to alert (monitoring) | < 30 minutes from signal detection to stakeholder notification | > 2 hours | Alert pipeline metrics |
| Audit finding reduction | Customers report 50%+ reduction in TPRM-related audit findings within first audit cycle | < 25% reduction | Customer survey |

### Leading Indicators (Tracked Weekly)

- Weekly active users per tenant
- Assessments initiated per week
- Evidence documents uploaded per week
- Vendor portal logins per week
- AI confidence scores trending (are they improving with more data?)
- Support ticket volume and category breakdown

---

## 12. Go-to-Market Strategy

### Target Segments (Ordered by Priority)

**Segment 1: Mid-market regulated industries (200-5,000 employees)**
- Financial services firms under DORA pressure
- Healthcare organizations with HIPAA vendor compliance mandates
- SaaS companies managing growing vendor portfolios with small teams
- **Why first**: Large enough to pay $30K-$80K/year, small enough to implement in weeks (not months), pain is acute (understaffed, regulatory pressure), dissatisfied with current tools.

**Segment 2: Enterprise organizations (5,000-25,000 employees)**
- Companies outgrowing Vanta/Drata but unwilling to buy ServiceNow GRC
- Organizations replacing legacy Archer deployments
- Multi-framework compliance requirements (SOC 2 + ISO 27001 + DORA + HIPAA)
- **Why second**: Higher ACV ($80K-$250K), longer sales cycle (3-6 months), requires more integration depth and configurability.

### Launch Approach

**Phase 1 (Months 1-3 post-GA): Design Partners**
- 10-15 design partner customers at discounted pricing (50% off first year).
- Weekly feedback sessions. Direct engineering access.
- Target: mid-market financial services and healthcare.
- Goal: validate core workflows, tune AI accuracy, generate case studies.

**Phase 2 (Months 4-8): Early Adopter**
- Open to broader mid-market. Content-led inbound marketing.
- Publish assessment accuracy benchmarks, framework coverage documentation, and integration guides.
- Launch vendor trust exchange with incentives for vendor participation.
- Target: 30-40 additional customers.

**Phase 3 (Months 9-18): Growth**
- Enterprise motion: outbound sales, channel partnerships, analyst engagement.
- Seek inclusion in Gartner Market Guide and Forrester Wave.
- Conference presence (RSA, Black Hat, GRC Summit).
- Target: 50+ total customers, $2M+ ARR.

### Channel Strategy

- **Direct sales**: Primary for enterprise ($80K+ ACV).
- **Self-serve with sales-assist**: Mid-market ($30K-$80K ACV). Free trial -> guided onboarding -> conversion.
- **Channel partners**: GRC consulting firms, MSSPs, Big Four advisory. Partners resell and implement.
- **Integration partnerships**: SecurityScorecard, BitSight (data partners), Jira/ServiceNow (workflow partners).

---

## 13. Pricing and Business Model

### Pricing Philosophy

Based on market research, per-vendor pricing is falling out of favor because it penalizes customers for good hygiene (assessing more vendors). Velora adopts a **platform subscription with unlimited vendor assessments** as the core pricing differentiator.

### Pricing Tiers

| Tier | Target | Annual Price | Includes |
|------|--------|-------------|----------|
| **Professional** | SMB / small mid-market (< 500 employees) | $30,000 - $45,000 | Up to 5 admin users, 300 vendors, core assessment + monitoring, 3 frameworks, AI pre-fill, vendor portal, standard dashboards |
| **Business** | Mid-market (500-5,000 employees) | $50,000 - $100,000 | Up to 20 admin users, unlimited vendors, all frameworks, FAIR quantification, advanced reporting, SSO, API access, custom scoring models |
| **Enterprise** | Large enterprise (5,000+ employees) | $120,000 - $250,000 | Unlimited users, multi-entity support, dedicated instance option (schema/DB isolation), custom integrations, SLA guarantees, dedicated CSM, data residency controls |

### Revenue Model

- **Subscription revenue**: Primary (90%+ of revenue). Annual contracts with quarterly billing option. Multi-year discounts: 10% for 2-year, 20% for 3-year.
- **Consumption add-ons**: API call volume beyond included tier, premium monitoring data sources (advanced dark web intelligence), additional data residency regions.
- **Professional services**: Implementation assistance, custom integration development, framework mapping consulting. Target: < 15% of revenue (minimize services dependency).

### Unit Economics Targets

| Metric | Target |
|--------|--------|
| Average Contract Value (ACV) | $65,000 (blended across tiers) |
| Gross margin | > 80% |
| CAC payback period | < 18 months |
| LTV:CAC ratio | > 3:1 |
| Net revenue retention | > 120% |

---

## 14. Risk Assessment

### Market Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **Crowded market with well-funded incumbents** | High | High | Differentiate on AI-native architecture + config-driven flexibility + vendor collaboration. Avoid competing on features incumbents already own (outside-in scanning). Instead, integrate their APIs. |
| **Enterprise sales cycles extend to 9-12 months** | High | Medium | Start with mid-market where cycles are 1-3 months. Use mid-market traction as proof points for enterprise. Offer pilot programs. |
| **Vendor trust exchange fails to achieve network effects** | Medium | High | Incentivize vendor participation aggressively (free trust profiles, AI questionnaire pre-fill, reduced assessment burden). Consider importing public vendor data (trust centers, certifications) to bootstrap the exchange. |
| **Pricing pressure from Vanta/Drata downmarket expansion** | Medium | Medium | Compete on capability depth, not price. Vanta/Drata are compliance-first with VRM as add-on; Velora is TPRM-first with superior depth. |

### Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **AI accuracy below threshold for enterprise trust** | Medium | Critical | Extensive accuracy benchmarking before GA. Confidence-based human-in-the-loop ensures no low-confidence output reaches customers without review. Publish accuracy metrics transparently. |
| **Evidence parsing fails on non-standard document formats** | Medium | Medium | Support graceful degradation: if parsing fails, flag for manual review. Build feedback loop where manual corrections improve parser. Start with well-structured documents (SOC 2, ISO certs) before expanding. |
| **Framework mapping errors create compliance exposure** | Low | Critical | Human verification for all high-stakes mappings. Use authoritative sources (NIST OLIR, OSCAL catalogs) as baseline. Expert review of all cross-framework mappings before release. |
| **Multi-tenant data leakage** | Low | Critical | PostgreSQL Row-Level Security as defense-in-depth. Automated RLS testing in CI/CD. Penetration testing focused on tenant isolation. Bug bounty program. |

### Regulatory Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **AI regulation (EU AI Act) imposes constraints on AI-driven risk scoring** | Medium | Medium | Design AI outputs as recommendations requiring human confirmation, not autonomous decisions. Maintain explainability for all AI outputs (citations, confidence scores, reasoning traces). |
| **Framework versioning lag creates compliance gaps** | Medium | Medium | Invest in automated framework update monitoring (RSS, OSCAL diffing). Commit to framework updates within 30 days of publication. |
| **Data sovereignty requirements limit deployment flexibility** | Medium | Low | Multi-region deployment architecture from day one. Data residency controls per tenant. |

### Operational Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **Dependency on third-party data APIs (SecurityScorecard, BitSight)** | Medium | High | Abstract integrations behind provider-agnostic interfaces. Support multiple rating providers. Ensure platform functions without external ratings (degraded but operational). |
| **LLM provider outage or API changes** | Medium | Medium | LLM abstraction layer (platform-core/llm-abstraction) enables provider switching. Queue-based processing with retry logic. Cache LLM outputs for repeated queries. |

---

## 15. Dependencies and Constraints

### Must Be True for Launch

1. **LLM abstraction layer** in platform-core must support at minimum two LLM providers (OpenAI GPT-4o + Anthropic Claude) with failover.
2. **SecurityScorecard or BitSight API access** must be secured for external rating integration. At least one provider is mandatory for continuous monitoring launch.
3. **SOC 2 report parsing accuracy** must exceed 85% on a validation set of 100 diverse SOC 2 Type II reports before GA.
4. **Framework content** for SOC 2, ISO 27001, NIST CSF 2.0, and HIPAA must be loaded and cross-mapped with >95% clause-level accuracy before GA. DORA and NIS2 within 60 days of GA.
5. **Velora itself must pass security assessment** -- customers will assess Velora before buying. SOC 2 Type II audit must begin within 6 months of GA.

### External Dependencies

| Dependency | Risk Level | Mitigation |
|-----------|-----------|------------|
| LLM API availability (OpenAI/Anthropic) | Medium | Dual-provider with failover |
| Security rating APIs (SecurityScorecard/BitSight) | Medium | Support both; degrade gracefully if one unavailable |
| Azure Document Intelligence (evidence parsing) | Low | Fallback to AWS Textract |
| Breach intelligence feeds (Breachsense/SpyCloud/HIBP) | Medium | Multiple providers; cache results |
| Enrichment APIs (Clearbit/ZoomInfo) | Low | Non-critical; manual entry fallback |

### Constraints

- **Budget**: Per Archeon cost controls, product development budget is capped. Sprint-level budget caps enforced by Arthon.
- **Team**: Initial build team defined by Harion's allocation matrix. Specialized hires needed for: GRC domain expertise (framework accuracy), enterprise sales.
- **Timeline**: Market window is 12-18 months before incumbents close AI capability gap. First-mover advantage on AI-native TPRM is time-limited.
- **Compliance recursion**: Velora must be SOC 2 Type II certifiable -- this means building with auditable controls from day one, not retrofitting.

---

## 16. Timeline and Milestones

### Phase 1: Foundation (Weeks 1-8)

| Week | Milestone | Deliverables |
|------|-----------|-------------|
| 1-2 | Architecture and HLD | System architecture document, data model, API design, infrastructure decisions |
| 3-4 | Core platform scaffold | Multi-tenant PostgreSQL with RLS, authentication (SSO/SAML/OIDC), RBAC, audit logging, API gateway |
| 5-6 | Vendor lifecycle MVP | Vendor CRUD, bulk import, AI enrichment pipeline, inherent risk tiering |
| 7-8 | Framework intelligence foundation | Framework data model (OSCAL), load SOC 2 + ISO 27001 + NIST CSF, cross-framework mapping engine |

### Phase 2: Assessment Engine (Weeks 9-16)

| Week | Milestone | Deliverables |
|------|-----------|-------------|
| 9-10 | Questionnaire engine | Template builder, SIG Core/Lite/CAIQ templates, assessment distribution, vendor portal (basic) |
| 11-12 | AI assessment capabilities | Questionnaire pre-fill from evidence/trust centers, confidence scoring, human review queue |
| 13-14 | Evidence management | Upload, parse (SOC 2 + ISO 27001 extractors), evidence-to-control mapping, freshness tracking |
| 15-16 | Scoring engine | Configurable scoring models, hybrid risk score, inherent/residual calculation, dashboard MVP |

### Phase 3: Monitoring and Reporting (Weeks 17-22)

| Week | Milestone | Deliverables |
|------|-----------|-------------|
| 17-18 | Continuous monitoring | External rating integration (SecurityScorecard/BitSight), breach monitoring, alert engine, notification delivery |
| 19-20 | Reporting and dashboards | Executive dashboard, board report generation, regulatory compliance reports (DORA/HIPAA) |
| 21-22 | Communications engine | Automated vendor outreach, reminder cadence, escalation automation, in-app collaboration |

### Phase 4: Hardening and Launch (Weeks 23-28)

| Week | Milestone | Deliverables |
|------|-----------|-------------|
| 23-24 | Security hardening | Penetration testing, RLS validation suite, encryption audit, OWASP Top 10 compliance |
| 25-26 | Beta with design partners | 10-15 design partners onboarded; feedback collection; accuracy benchmarking |
| 27-28 | GA preparation | Performance optimization, documentation, onboarding flows, support playbooks, launch materials |

### Post-GA Roadmap

| Quarter | Focus |
|---------|-------|
| Q1 post-GA | FAIR risk quantification, vendor trust profiles, 4th-party mapping, 3 additional frameworks |
| Q2 post-GA | Trust exchange launch, natural language Q&A, contract analysis, automated vendor discovery |
| Q3 post-GA | Predictive risk scoring, cross-vendor pattern analysis, regulatory change intelligence |
| Q4 post-GA | Enterprise features (multi-entity, dedicated instances), advanced analytics, channel partner tools |

---

## 17. Open Questions

| ID | Question | Impact | Owner | Decision Needed By |
|----|----------|--------|-------|-------------------|
| OQ-01 | Should Velora build its own outside-in scanning infrastructure or exclusively consume third-party APIs (SecurityScorecard/BitSight)? Building own scanning increases cost and complexity but reduces API dependency and improves margins. | Architecture | Devam + Harion | Week 2 (HLD) |
| OQ-02 | What is the minimum viable set of frameworks for GA? Research recommends SOC 2 + ISO 27001 + NIST CSF + HIPAA at minimum. DORA and NIS2 are high-demand but add complexity. | Scope | Darshika | Week 3 |
| OQ-03 | Should the vendor trust exchange be open (any vendor can create a profile without being assessed) or closed (vendor profiles only created through customer assessments)? Open bootstraps faster but risks data quality. | Product Strategy | Darshika + Devam | Week 8 |
| OQ-04 | What is the pricing strategy for vendor-side features? Free vendor portal (to maximize adoption) vs. premium vendor trust profiles (to monetize both sides)? | Revenue | Devam | Week 10 |
| OQ-05 | Should Velora pursue SOC 2 Type II certification on its own before GA, or immediately after? Customers will ask for it during sales. | Compliance | Devam | Week 4 |
| OQ-06 | Which LLM provider(s) should be primary for GA? OpenAI GPT-4o offers widest enterprise acceptance; Anthropic Claude offers stronger document analysis. Both through platform-core/llm-abstraction. | Technical | Harion | Week 2 |
| OQ-07 | Should Velora integrate with existing trust exchanges (CyberGRX, Whistic) for data or build exclusively its own? Integration provides immediate data but creates dependency on competitor networks. | Strategy | Devam | Week 8 |

---

## 18. Appendices

### Appendix A: Market Data Summary

| Data Point | Value | Source | Confidence |
|-----------|-------|--------|------------|
| Global TPRM market size (2025) | $8.5-9.5B | Grand View, Liminal, MarketsandMarkets consensus | HIGH |
| Market CAGR | 14-17% | Multiple analyst firms | HIGH |
| Market size (2030) | $19-21B | Analyst consensus | HIGH |
| SAM for Velora | $3.5-4.5B | Estimated (mid-market + enterprise, NA + EU) | MEDIUM |
| SOM (3-5 year) | $50-150M | Estimated | LOW |
| Average vendor count per org | 286 (up 21% YoY) | Ncontracts 2025 | HIGH |
| TPRM FTEs (73% of orgs) | 2 or fewer | Ncontracts 2025 | HIGH |
| Assessment hours per week | 37.4 (up 14h from prior year) | Whistic 2025 | HIGH |
| Vendor questionnaire response rate | 25% timely | Whistic 2025 | HIGH |
| Trust in questionnaire accuracy | 4% high confidence | Whistic 2025 | HIGH |
| Third-party breaches (% of total) | ~30% (doubled YoY) | Verizon 2025 DBIR | HIGH |
| Dark web breach postings (YoY growth) | +43% | BitSight Trace 2024 | HIGH |
| Fourth-party monitoring adoption | 64% of organizations | EY 2025 | MEDIUM |

### Appendix B: Competitor Pricing Reference

| Vendor | Segment | Estimated Annual Cost |
|--------|---------|----------------------|
| Vanta | SMB-Mid | $11K-$80K |
| Drata | SMB-Mid | $7.5K-$100K+ |
| Thoropass | SMB | ~$30K median |
| SecurityScorecard | Mid-Ent | $22K+ base, +$1.5-2K/vendor |
| BitSight | Enterprise | $22K+ base, +$1.5-2K/vendor |
| OneTrust | Enterprise | $44K+ (TPRM module) |
| ServiceNow GRC | Enterprise | $50K-$500K+ |
| ProcessUnity | Enterprise | Custom (high) |
| Archer | Enterprise | Custom + professional services |

### Appendix C: Framework Coverage Matrix

| Framework | Clause Count | GA? | Cross-Mapping Status |
|-----------|-------------|-----|---------------------|
| SOC 2 TSC | ~60 criteria | Yes | Mapped to ISO 27001, HIPAA, NIST CSF |
| ISO 27001:2022 | 93 Annex A controls | Yes | Mapped to SOC 2, NIST CSF, GDPR Art 32 |
| NIST CSF 2.0 | 106 subcategories | Yes | NIST OLIR mappings to ISO, CIS, CCM |
| HIPAA Security Rule | ~50 standards | Yes | Mapped to SOC 2, ISO 27001 |
| PCI DSS 4.0 | 250+ requirements | Post-GA (Q1) | Mapped to NIST 800-53 |
| GDPR | Key articles | Yes (partial) | Mapped to ISO 27001 (Art 32) |
| DORA | 64 articles | Post-GA (60 days) | Mapped to NIST 800-53, ISO 27001 |
| NIS2 | 46 articles | Post-GA (60 days) | Mapped to NIST CSF, ISO 27001 |
| SIG Core/Lite | 627/128 questions | Yes (templates) | Maps to 21 risk domains |
| CAIQ v4/Lite | ~260/71 questions | Yes (templates) | Maps to CCM v4 |

### Appendix D: Technical Stack Summary

```
Frontend:       Next.js 15 + TypeScript + Tailwind CSS + shadcn/ui
Backend:        FastAPI (Python 3.12+) + Pydantic v2
Database:       PostgreSQL 16+ (RLS) + pgvector
Cache:          Redis 7+ (distributed) + in-process cache
Search:         Typesense
Jobs:           BullMQ (simple) + Temporal (complex workflows)
Storage:        AWS S3 / MinIO (dev/self-hosted)
Real-time:      SSE (primary) + WebSockets (collaborative)
AI/ML:          LangChain/LlamaIndex via platform-core/llm-abstraction
Vector:         pgvector (start) -> Qdrant (scale)
Document Parse: Azure Document Intelligence (primary) + AWS Textract (fallback)
Monitoring:     Prometheus + Grafana
Logging:        Structured JSON -> ELK or Loki
CI/CD:          GitHub Actions + Docker + Kubernetes
```

### Appendix E: Research Sources

- Market Research: `/forgeon/velora/tprm/docs/research/market-research.md`
- Technical Architecture Research: `/forgeon/velora/tprm/docs/research/technical-architecture-research.md`
- Scoring, Framework & Assessment Research: `/forgeon/velora/tprm/docs/research/scoring-framework-research.md`

---

## 19. Brief Cross-Check Report

This section cross-references every major feature and approach from Devam's product brief against the three research documents. Each item is rated as CONFIRMS (research validates the brief), ENHANCES (research provides better or additional approaches), or CHALLENGES (research suggests a different direction).

### AI-First Architecture

**Brief**: AI-native platform where AI infers and enriches, humans review and confirm.
**Research verdict**: **CONFIRMS**. Market research identifies AI-native architecture as the #1 "next-gen" TPRM requirement. Current leaders (ProcessUnity, OneTrust) have AI bolted on. Only SAFE Security and Whistic are AI-native, creating a window of opportunity. Technical research confirms FastAPI + LangChain as the optimal stack for AI-first SaaS.

### Config-Driven Design

**Brief**: Everything customizable -- scoring, workflows, escalation rules, questionnaires.
**Research verdict**: **CONFIRMS and ENHANCES**. Research validates that enterprise customers demand custom risk taxonomies, multi-entity support, and workflow orchestration. Research adds: use JSON Schema as single source of truth for validation, UI generation, and runtime behavior. Store scoring formulas as configurable rules, not hardcoded logic. Use Temporal for complex workflows and a lightweight custom rule engine for scoring/escalation (not heavyweight frameworks like Drools).

### Default 5x5 Scoring Matrix

**Brief**: Default 5x5 matrix (likelihood x impact) configurable by admin.
**Research verdict**: **ENHANCES**. Research confirms configurable scoring is essential but recommends a more sophisticated multi-dimensional model. The default should include 8 weighted factors (security posture, data sensitivity, business criticality, compliance status, control maturity, incident history, financial stability, Nth-party risk) with admin-configurable weights. The 5x5 matrix is fine for inherent risk; residual risk should use the multiplication method (Inherent Risk x (1 - Control Effectiveness%)). Additionally, FAIR-based financial quantification should be a first-class feature, not an add-on -- SAFE Security already offers this as a differentiator.

### Framework-Aware Questionnaires

**Brief**: Questionnaires mapped to frameworks (SOC 2, ISO 27001, GDPR, HIPAA, etc).
**Research verdict**: **CONFIRMS and ENHANCES**. Research confirms and adds critical detail: use SIG Core (627 questions) and SIG Lite (128) as standard templates alongside CAIQ v4 (~260) for cloud vendors. Build on OSCAL as internal representation format. Import NIST OLIR cross-framework mappings as authoritative baseline. Research identifies that SOC 2 and ISO 27001 share ~96% control overlap -- the unified control library approach (one control tagged to multiple frameworks) eliminates redundant assessment work, which is a major competitive differentiator.

### Evidence Parsing and Traceability

**Brief**: AI parses SOC 2 reports, ISO certificates, pen test results. Evidence maps to controls.
**Research verdict**: **CONFIRMS**. Research validates this as a major market gap -- "most tools still require manual review" of evidence documents. Recommends Azure Document Intelligence as primary parser (best layout analysis for SOC 2 report tables). Adds evidence confidence scoring formula based on 5 factors: source (30%), recency (25%), completeness (20%), consistency (15%), verification (10%). Also adds evidence freshness tracking with specific validity periods per document type and expiry alert cadence (90/60/30/14/7 days).

### Continuous Monitoring (Breach, Dark Web, News, Threats)

**Brief**: Multi-signal continuous monitoring with configurable frequency.
**Research verdict**: **CONFIRMS and ENHANCES**. Research validates and provides critical prioritization structure: P0 (active breach, ransomware), P1 (critical CVE, leaked credentials, rating drop >15pts), P2 (cert expiry, DNS changes), P3 (moderate rating drop, approaching expiry, key personnel departure), P4 (minor fluctuation). Research adds: deduplication within 24-hour windows, correlation (multiple P2/P3 from same vendor within 48h elevates to P1), and trend detection (flag persistent downward trajectory even without single-event trigger). Monitoring frequency should be tier-based: critical vendors at 4-hour cycles, not just daily.

### Vendor Portal for Evidence Upload

**Brief**: Vendor-facing portal for questionnaire completion and evidence upload.
**Research verdict**: **CONFIRMS and ENHANCES**. Research validates but elevates this to a trust exchange model. Whistic Trust Center Exchange and CyberGRX Exchange (14,000 attested assessments, 250,000+ vendor profiles) demonstrate that vendor trust networks create powerful network effects. Brief focuses on portal for individual assessments; research recommends evolving toward a persistent vendor trust profile that vendors maintain independently and share with multiple customers. This is the strongest long-term moat.

### Automated Communications and Follow-ups

**Brief**: Template-based vendor outreach with automated reminders.
**Research verdict**: **CONFIRMS**. Research provides specific SLA benchmarks: SIG Core 30 calendar days, SIG Lite 14 days, evidence upload 14 days. Reminder cadence: Day 7 (gentle), Day 14 (escalation to vendor's manager), Day 21 (final notice with consequence statement), Day 28+ (escalate to internal procurement). Research adds internal escalation patterns and specific SLA targets for remediation (Critical 30d, High 60d, Medium 90d).

### Premium Light-Theme Executive Design

**Brief**: Premium, clean, information-dense design suitable for board presentations.
**Research verdict**: **CONFIRMS**. Research identifies poor UX as a top user complaint: "legacy platforms (Archer, ServiceNow GRC, even OneTrust) are complex, require training, and feel like tools built for GRC consultants, not practitioners." Vanta is cited as having "excellent UX -- modern, intuitive interface" and is winning deals partly on UX. Superior design is a confirmed competitive differentiator.

### Multi-Tenant, API-First

**Brief**: Multi-tenant architecture, API-first design.
**Research verdict**: **CONFIRMS**. Technical research recommends PostgreSQL 16+ with Row-Level Security as the optimal multi-tenant pattern, with tiered isolation (shared schema standard, schema-per-tenant premium, database-per-tenant enterprise). API-first with OpenAPI 3.0 auto-generation from FastAPI enables automatic TypeScript client generation.

### Features NOT in Brief but Identified Through Research

| Feature | Research Source | Priority Recommendation |
|---------|---------------|------------------------|
| **FAIR-based financial risk quantification** | Scoring research: FAIR is the leading quantitative model; SAFE Security already offers it | P1 -- differentiator for board-level communication |
| **Cross-vendor pattern analysis** | Market research: "absent" in current tools | P2 -- identifies systemic portfolio risks |
| **Regulatory change impact assessment** | Market research: "absent" in current tools; framework versioning lag cited as persistent problem | P2 -- auto-flag when new regulations affect existing assessments |
| **Contract risk clause analysis** | Market research: "barely present" in current tools | P2 -- AI extracts risk-relevant clauses from vendor contracts |
| **Automated vendor discovery** | Market research: UpGuard differentiator; shadow IT cited as gap | P2 -- discover vendors from SSO logs, financial systems |
| **Peer benchmarking** | Scoring research: SecurityScorecard and BitSight offer size-cohort comparison | P2 -- anonymized cross-customer portfolio comparison |
| **OSCAL as internal format** | Technical + scoring research: NIST standard for machine-readable compliance | P0 (architecture decision) -- enables programmatic framework management |
| **Evidence confidence scoring** | Scoring research: 5-factor weighted formula | P1 -- differentiates from binary accept/reject evidence evaluation |
| **Predictive risk scoring** | Market research: "major differentiator -- predict breaches before they happen" | P2 -- behavioral pattern analysis for incident prediction |
| **Natural language risk Q&A** | Market research: Vanta offers "Vendor AI Answers"; identified as high-value emerging capability | P2 -- plain-language querying of vendor risk data |

### Where Brief Diverges from Research

1. **Brief omits FAIR quantification**: The brief mentions scoring and dashboards but does not explicitly call for financial risk quantification. Research strongly recommends this as a P1 feature -- it is SAFE Security's core differentiator and bridges the gap between security ratings and board-level risk communication.

2. **Brief underspecifies framework mapping depth**: The brief mentions framework support but does not describe the cross-framework mapping engine. Research reveals that 70-80% of controls map across major frameworks, and a unified control library with OSCAL + NIST OLIR integration would eliminate redundant assessments -- a major competitive advantage.

3. **Brief does not mention vendor trust exchange**: The brief describes a vendor portal for assessments but not a persistent trust profile or exchange marketplace. Research identifies trust exchanges (CyberGRX, Whistic) as the strongest network moat in TPRM. This should be on the roadmap from the start, even if the exchange launches post-GA.

4. **Brief does not address contract analysis**: Research identifies contract risk analysis as "barely present" in current tools and a significant opportunity. AI extraction of risk-relevant contract clauses would differentiate Velora from every competitor.

---

*Document prepared by Darshika (CPO) based on Devam's product brief and three research reports (market, technical architecture, scoring/framework). All claims reference specific research findings with confidence levels. No TBDs remain. Ready for MCA review.*
