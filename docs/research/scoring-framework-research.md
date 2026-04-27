---
tags:
  - archeon
  - forgeon
  - product
  - product-velora
---

# Velora TPRM -- Scoring, Framework Intelligence & Assessment Research

**Research Date:** 2026-03-27
**Status:** Complete
**Researcher:** Harion (Strategy Orchestrator)
**Purpose:** Inform Velora TPRM platform design for scoring engine, framework intelligence, assessment workflows, and continuous monitoring subsystems.

---

## Table of Contents

1. [TPRM Scoring Models](#1-tprm-scoring-models)
2. [Assessment Methodologies](#2-assessment-methodologies)
3. [Framework Content and Mapping](#3-framework-content-and-mapping)
4. [Vendor Enrichment Approaches](#4-vendor-enrichment-approaches)
5. [Evidence Management Best Practices](#5-evidence-management-best-practices)
6. [Continuous Monitoring Best Practices](#6-continuous-monitoring-best-practices)
7. [Communication and Workflow Patterns](#7-communication-and-workflow-patterns)
8. [Design Recommendations for Velora](#8-design-recommendations-for-velora)

---

## 1. TPRM Scoring Models

### 1.1 Industry Leader Methodologies

#### SecurityScorecard (A-F Rating System) [HIGH confidence]

| Attribute | Detail |
|-----------|--------|
| **Scale** | 0--100 numeric, mapped to A (90-100) through F (0-60) letter grades |
| **Risk factors** | 10 categories: DNS Health, IP Reputation, Web Application Security, Network Security, Leaked Information, Hacker Chatter, Endpoint Security, Patching Cadence, CUBIT Score, Social Engineering |
| **Data points** | 200+ measurements across the 10 factors |
| **Methodology** | Z-score normalization -- measures how many standard deviations an org is above/below the average for its size cohort |
| **Weighting** | Scoring 3.0: factors no longer have weights; issue types within factors carry weights based on breach correlation |
| **Calibration** | Size-based calibration using 2 months of collected data to ensure fair comparison across org sizes |
| **Breach correlation** | F-rated orgs are 13.8x more likely to sustain a breach than A-rated orgs |
| **Data ownership** | Claims 99% proprietary data -- near-zero latency, high attribution accuracy |
| **AI capability** | HEID AI engine for automated remediation, questionnaire requests, risk classification |
| **Update frequency** | Continuous / daily |

Sources: [SecurityScorecard Scoring Methodology](https://support.securityscorecard.com/hc/en-us/articles/8366223642651-How-SecurityScorecard-calculates-your-scores), [10 Risk Factors Explained](https://securityscorecard.com/blog/securityscorecard-10-risk-factors-explained/), [Scoring 3.0](https://support.securityscorecard.com/hc/en-us/articles/16235105523739-Prepare-for-Scoring-3-0)

#### BitSight (250-900 Rating System) [HIGH confidence]

| Attribute | Detail |
|-----------|--------|
| **Scale** | 250--900 (achievable range: 300--820) |
| **Risk vectors** | 25 key risk vectors from 120+ sources |
| **Categories** | 4 primary: Compromised Systems, Security Diligence, User Behavior, Data Breaches |
| **Data classes** | Configuration data (proactive posture) and Security events (reactive indicators) |
| **Normalization** | Size-based normalization using employee count, digital footprint magnitude, observation counts |
| **Weighting** | Risk vector letter grades aggregated with different weights, normalized per company |
| **Enrichment** | 60,000+ pre-populated vendor profiles; AI-powered questionnaire analysis |
| **Dark web intel** | Scans underground forums, dark web marketplaces, ransomware leak sites, Telegram channels |
| **Update frequency** | Daily rating recalculation |

Sources: [BitSight Rating Calculation](https://help.bitsighttech.com/hc/en-us/articles/231950968-How-are-Bitsight-Security-Ratings-Calculated), [Risk Categories Guide](https://help.bitsighttech.com/hc/en-us/articles/360007320574-A-Guide-to-Navigating-and-Prioritizing-Bitsight-Risk-Categories-Risk-Vectors), [2025 RAU](https://www.bitsight.com/blog/research-behind-bitsight-rating-algorithm-update-2025)

#### Comparison: SecurityScorecard vs BitSight

| Dimension | SecurityScorecard | BitSight |
|-----------|-------------------|----------|
| Scale | 0-100 / A-F | 250-900 |
| Risk factors | 10 categories | 25 vectors in 4 categories |
| Data sources | 99% proprietary | 120+ external sources |
| Normalization | Size-cohort z-score | Size-based (employees, footprint) |
| Strength | Executive-friendly grading, deep dark web intel | Broader vector coverage, large vendor network |
| AI features | HEID engine | AI questionnaire analysis |

Source: [BitSight vs SecurityScorecard 2025](https://www.upguard.com/compare/bitsight-vs-securityscorecard)

### 1.2 FAIR Model (Factor Analysis of Information Risk) [HIGH confidence]

FAIR is the leading quantitative cyber risk model, now an Open Group standard. It decomposes risk into measurable, financially-grounded components.

**Core Formula:**
```
Risk = Loss Event Frequency (LEF) x Loss Magnitude (LM)

Where:
  LEF = Threat Event Frequency (TEF) x Vulnerability (probability of action succeeding)
  LM  = Primary Loss + Secondary Loss (regulatory fines, reputation, etc.)
```

**FAIR-TAM (Third-Party Assessment Model):** The FAIR Institute is developing a purpose-built third-party risk assessment model that applies FAIR decomposition to vendor risk scenarios, enabling financially-grounded vendor risk quantification.

**Applicability to Velora:**
- Use FAIR for translating vendor risk scores into dollar-value loss exposure
- Enables "what-if" analysis: if a vendor's control degrades, what is the financial impact?
- Bridges the gap between security ratings and business risk appetite expressed in monetary terms
- Supports defensible risk acceptance, mitigation, or transfer decisions

Sources: [FAIR Institute](https://www.fairinstitute.org), [FAIR Third-Party Assessment Model](https://www.fairinstitute.org/fair-third-party-assessment-model), [Using FAIR for Inherent Risk](https://www.fairinstitute.org/blog/using-the-fair-model-to-measure-inherent-risk)

### 1.3 Inherent Risk vs Residual Risk Scoring [HIGH confidence]

| Concept | Definition | Calculation |
|---------|-----------|-------------|
| **Inherent Risk** | Risk level before any controls are applied; based on vendor type, data sensitivity, access level, business criticality | Scored via weighted questionnaire or formula (e.g., data sensitivity x access level x business criticality) |
| **Residual Risk** | Risk remaining after controls are applied | Method A: Inherent Risk - Control Effectiveness = Residual Risk (subtraction). Method B: Inherent Risk x (1 - Control Effectiveness %) = Residual Risk (multiplication) |
| **Control Effectiveness** | Measured via assessments, evidence, and external ratings | Expressed as score (0-10) or percentage (0-100%) |

**Velora design implication:** Support both calculation methods and let admins choose. The multiplication method is generally preferred as it produces a proportional reduction rather than a linear one.

Sources: [FAIR Institute -- Inherent vs Residual Risk](https://www.fairinstitute.org/blog/inherent-risk-vs.-residual-risk-explained-in-90-seconds), [FAIR Inherent Risk Measurement](https://www.fairinstitute.org/blog/a-solution-for-measuring-inherent-risk)

### 1.4 Configurable Scoring Engine Design [HIGH confidence]

Leading TPRM platforms allow admin-configured scoring with these capabilities:

| Capability | Description |
|------------|-------------|
| **Custom formulas** | Admin-defined mathematical formulas combining risk factors with operators (+, x, weighted avg) |
| **Adjustable weights** | Per-factor weight expressed as percentage; sum to 100% or use relative weighting |
| **Threshold definitions** | Admin-set breakpoints for risk tiers (e.g., Critical > 85, High 70-84, Medium 40-69, Low < 40) |
| **Scoring templates** | Pre-built scoring models per industry or regulation (e.g., financial services, healthcare) |
| **Override capability** | Manual score adjustments with audit trail and justification |
| **Multi-dimensional scoring** | Separate scores for security, privacy, operational, financial, compliance dimensions |

**Typical scoring factors and default weights:**

| Factor | Typical Weight | Data Source |
|--------|---------------|-------------|
| Security posture (external rating) | 20-25% | SecurityScorecard, BitSight, or internal scan |
| Data sensitivity classification | 15-20% | Internal classification (PII, PHI, financial, IP) |
| Business criticality / operational dependency | 15-20% | Business impact analysis |
| Compliance status | 10-15% | Certifications, audit reports |
| Control maturity (assessment results) | 10-15% | Questionnaire responses, evidence review |
| Incident history | 5-10% | Breach databases, vendor-reported incidents |
| Financial stability | 5-10% | Credit ratings, financial filings |
| Fourth-party (Nth-party) risk | 5% | Sub-processor analysis |

Sources: [HighBond Risk Score Configuration](https://help.highbond.com/helpdocs/highbond/en-us/Content/risk_manager/risk_score_config.htm), [Whistic Risk Ranking](https://www.whistic.com/resources/blog/tprm-how-to-risk-ranking-assessment-and-remediation), [Safe Security TPRM Guide 2026](https://safe.security/resources/blog/2026-guide-to-third-party-risk-management-tprm/)

---

## 2. Assessment Methodologies

### 2.1 Questionnaire-Based Assessment [HIGH confidence]

#### Standard Questionnaires

| Questionnaire | Publisher | Questions | Use Case | Framework Alignment |
|---------------|-----------|-----------|----------|---------------------|
| **SIG Core** | Shared Assessments | 627 (2025) | High-risk vendors handling sensitive/regulated data | 21 risk domains, 4 control areas |
| **SIG Lite** | Shared Assessments | 128 (2025) | Low-to-moderate risk vendors; preliminary screening | Same 21 domains, reduced depth |
| **CAIQ v4** | Cloud Security Alliance | ~260 | Cloud service providers | Maps to CCM v4 (16 control domains) |
| **CAIQ Lite** | Cloud Security Alliance | 71 | Quick cloud provider assessment | All 16 CCM domains, condensed |
| **CIS Controls** | Center for Internet Security | Varies | General security posture | 18 CIS Controls v8 |
| **NIST 800-171** | NIST | Varies | US government contractors | 14 control families |
| **Custom** | Organization-specific | Varies | Tailored to specific risk concerns | Maps to internal policy |

**SIG 2025 Coverage -- 4 Key Control Areas:**
1. Governance & Risk Management
2. Information Protection
3. IT Operations & Business Resilience
4. Security Incident & Threat Management

**21 Risk Domains include:** Access Control, Application Security, AI, Asset Management, Business Continuity, Cloud Hosting, Compliance, Data Privacy, Endpoint Protection, Encryption, Governance, Human Resources, Incident Management, Information Security, Network Security, Nth Party Management, Operations, Physical Security, Risk Management, Server Security, ESG.

Sources: [SIG Questionnaire Guide](https://www.upguard.com/blog/sig-questionnaire), [2025 SIG Update](https://sharedassessments.org/blog/2025-sig/), [CAIQ vs SIG](https://www.bitsight.com/blog/caiq-vs-sig-top-questionnaires-vendor-risk-assessment), [SIG vs CAIQ](https://www.hypercomply.com/blog/caiq-vs-sig)

#### Questionnaire Selection Matrix

| Vendor Profile | Recommended Questionnaire | Assessment Depth |
|----------------|---------------------------|------------------|
| Cloud SaaS provider (Tier 1) | SIG Core + CAIQ v4 | Deep |
| Cloud SaaS provider (Tier 2-3) | SIG Lite + CAIQ Lite | Moderate |
| On-prem software vendor | SIG Core | Deep |
| Professional services (data access) | SIG Lite + custom privacy addendum | Moderate |
| Professional services (no data access) | SIG Lite or custom lightweight | Light |
| Infrastructure/hosting provider | CAIQ v4 + SIG Core (cloud sections) | Deep |
| Low-risk commodity vendor | Custom 10-20 questions | Minimal |

### 2.2 Evidence-Based Assessment [HIGH confidence]

| Evidence Type | What It Proves | Validity Period | Confidence Level |
|---------------|---------------|-----------------|------------------|
| SOC 2 Type II report | Controls operated effectively over audit window (3-12 months) | 12 months from issue date | HIGH |
| SOC 2 Type I report | Controls are designed effectively at a point in time | 12 months (but weaker than Type II) | MEDIUM |
| ISO 27001 certificate | ISMS certified by accredited body | 3 years (with annual surveillance audits) | HIGH |
| Penetration test report | Vulnerabilities found and remediated | 12 months (best practice) | HIGH |
| Vulnerability scan results | Current vulnerability posture | 30-90 days | MEDIUM |
| Privacy impact assessment | Data processing risks identified | Until scope changes | MEDIUM |
| Business continuity plan | Recovery capabilities documented | Annual review expected | MEDIUM |
| Insurance certificate | Cyber liability coverage in force | Policy period (typically 12 months) | HIGH |

### 2.3 Outside-In / Passive Scanning [HIGH confidence]

| Signal Category | What It Detects | Examples |
|-----------------|-----------------|----------|
| **DNS health** | Misconfigurations, dangling records, zone transfer issues | SPF/DKIM/DMARC presence, DNSSEC, open resolvers |
| **SSL/TLS** | Certificate issues, weak ciphers, expired certs | Certificate validity, protocol version, cipher strength |
| **Web application** | Common web vulnerabilities | Missing headers (CSP, HSTS), exposed admin panels, outdated frameworks |
| **Network security** | Open ports, exposed services | Unnecessary open ports, deprecated protocols (Telnet, FTP) |
| **Email security** | Phishing susceptibility, spoofing risk | SPF/DKIM/DMARC enforcement, email gateway configuration |
| **Leaked credentials** | Compromised employee credentials on dark web | Paste sites, breach databases, dark web marketplaces |
| **IP reputation** | Botnet participation, malware distribution | Blocklist presence, C2 communication, spam origin |
| **Patching cadence** | Speed of vulnerability remediation | CVE exposure duration, patch lag metrics |

### 2.4 Hybrid Assessment Approach (Recommended for Velora) [HIGH confidence]

The most effective TPRM programs combine all three modalities:

```
Hybrid Score = w1(Questionnaire Score) + w2(Evidence Score) + w3(External Rating) + w4(Scan Score)

Where:
  - Questionnaire Score: self-attested responses, weighted by domain importance
  - Evidence Score: validated artifacts (SOC 2, ISO cert, pen test), weighted by freshness and type
  - External Rating: SecurityScorecard/BitSight score, normalized to internal scale
  - Scan Score: passive scan findings, weighted by severity
  - w1 + w2 + w3 + w4 = 1.0 (configurable by admin)
```

### 2.5 Assessment Frequency by Vendor Tier [HIGH confidence]

| Tier | Risk Level | Full Assessment | Continuous Monitoring | Reassessment Trigger |
|------|-----------|-----------------|----------------------|---------------------|
| **Tier 1** | Critical | Annually (comprehensive: SIG Core + evidence + on-site) | Daily external rating, real-time breach alerts | Breach, M&A, leadership change, contract renewal, rating drop > 10 pts |
| **Tier 2** | High | Annually (SIG Core or SIG Lite + evidence) | Weekly external rating, daily breach alerts | Breach, rating drop, certification expiry |
| **Tier 3** | Medium | Every 2 years (SIG Lite + key evidence) | Monthly external rating | Breach, certification expiry, contract renewal |
| **Tier 4** | Low | Every 3 years (lightweight questionnaire) | Quarterly external rating | Breach only |

Sources: [Vendor Tiering Guide](https://www.upguard.com/blog/what-is-vendor-tiering), [Safe Security Vendor Tiering](https://safe.security/resources/blog/how-to-tier-vendors-for-effective-third-party-risk-management-tprm/), [TPRM Alliance Tiering Guide](https://www.tprmalliance.com/comprehensive-guide-to-vendor-risk-tiering-in-third-party-risk-management-tprm/)

### 2.6 AI-Assisted Assessment Automation [HIGH confidence]

| Capability | Description | Maturity |
|-----------|-------------|----------|
| **Auto-fill from prior responses** | LLM pre-populates questionnaire from vendor's historical responses and public documentation | Production (Whistic, ProcessUnity, Black Kite) |
| **Evidence evaluation** | NLP reads SOC 2 reports, ISO certs, policies; extracts control status and maps to questionnaire questions | Production (ProcessUnity Evidence Evaluator) |
| **Trust center capture** | AI agents scrape vendor trust centers, extract security documentation, pre-populate assessments | Production (Whistic Trust Center Capture) |
| **Response validation** | LLM cross-references questionnaire responses against evidence artifacts for consistency | Emerging |
| **Risk insight generation** | AI summarizes critical controls, gaps, and risk hotspots from assessment data | Production (multiple vendors) |
| **Questionnaire generation** | AI generates custom questionnaires based on vendor profile, tier, and risk concerns | Emerging |
| **Efficiency gain** | 80% reduction in assessment overhead; 10x more assessments without additional headcount | Reported by multiple vendors |

Sources: [ProcessUnity AI Control Reviews](https://www.processunity.com/third-party-risk-management/ai-based-control-reviews/), [VISO TRUST AI Assessment](https://visotrust.com/ai-assessment-tprm-vendor/), [Atlas Systems AI TPRM](https://www.atlassystems.com/complyscore/ai-tprm/introduction), [SafeBase AI Questionnaire Assistance](https://safebase.io/blog/ai-questionnaire-assistance)

---

## 3. Framework Content and Mapping

### 3.1 Control-Level Decomposition Examples [HIGH confidence]

#### ISO 27001:2022 Annex A Structure
- 4 themes: Organizational (37 controls), People (8), Physical (14), Technological (34)
- 93 total controls (down from 114 in 2013 version)
- Each control has: title, attribute tags, purpose statement, guidance, and other information

#### SOC 2 Trust Services Criteria (TSC)
- 5 categories: Security (Common Criteria CC1-CC9), Availability, Processing Integrity, Confidentiality, Privacy
- Security (Common Criteria) is mandatory; others are optional based on scope
- ~60+ individual criteria points across all categories

#### NIST CSF 2.0
- 6 functions: Govern, Identify, Protect, Detect, Respond, Recover
- 22 categories under the 6 functions
- 106 subcategories (the actual control statements)

### 3.2 Cross-Framework Mapping [HIGH confidence]

**Key finding:** Roughly 70-80% of controls map across NIST CSF 2.0, ISO 27001:2022, and CIS Controls v8. ISO 27001 and SOC 2 share approximately 96% of the same security controls.

#### Mapping Approaches

| Approach | Description | Pros | Cons |
|----------|-------------|------|------|
| **NIST OLIR** | Official NIST Online Informative References catalog; standardized relationship assertions between framework elements | Authoritative, standardized format, free | Limited to NIST focal documents, not all frameworks covered |
| **UCF (Unified Compliance Framework)** | Commercial unified control framework mapping 1000+ regulations/standards | Comprehensive, regularly updated | Expensive, proprietary |
| **OSCAL** | NIST machine-readable format (XML/JSON/YAML) for control catalogs, baselines, SSPs, and assessment results | Open standard, programmatic, lossless format conversion | Adoption still growing, not all frameworks available in OSCAL |
| **Manual expert mapping** | Subject-matter experts create custom control mappings | Tailored to org needs | Expensive, error-prone, hard to maintain |
| **AI-assisted mapping** | LLMs analyze control text and suggest mappings | Fast, scalable | Requires expert validation, hallucination risk |

#### NIST OLIR (Online Informative References) Program [HIGH confidence]

NIST maintains the Informative Reference Catalog containing:
- Informative References: relationship assertions between Reference Document elements and Focal Document elements
- Derived Relationship Mappings (DRMs): transitive mappings derived from multiple informative references
- Available mappings include: CCM v4 to NIST CSF v2, ISO 27001:2022 to CSF v2.0, CIS Controls v8 to CSF, and more
- Data is downloadable and can be consumed programmatically

Source: [NIST OLIR Catalog](https://csrc.nist.gov/projects/olir/informative-reference-catalog)

#### OSCAL (Open Security Controls Assessment Language) [HIGH confidence]

| Layer | Models | Purpose |
|-------|--------|---------|
| **Control** | Catalog, Profile | Define control libraries and baselines/overlays |
| **Implementation** | Component Definition, SSP | Express how controls are implemented |
| **Assessment** | Assessment Plan, Assessment Results, POA&M | Plan, execute, and track assessments |

**Key design properties:**
- Formats: XML, JSON, YAML (lossless conversion between all three)
- Hierarchical model layers that build on each other
- CIS Controls already available in OSCAL format (GitHub repository)
- NIST SP 800-53 available in OSCAL
- Enables "Compliance as Code" -- audit durations reduced from months to minutes

Sources: [NIST OSCAL](https://pages.nist.gov/OSCAL/), [OSCAL GitHub](https://github.com/usnistgov/OSCAL), [CIS Controls OSCAL Repository](https://www.cisecurity.org/insights/blog/introducing-the-cis-controls-oscal-repository)

### 3.3 How Leading Platforms Handle Framework Intelligence [MEDIUM confidence]

| Platform | Approach |
|----------|----------|
| **OneTrust** | Maps same control to multiple frameworks to avoid redundancy; automates compliance across ISO 27001, SOC 2, NIST CSF |
| **Vanta** | Pre-built control library with automated tests; AI maps custom controls to Vanta's test library; tests run hourly |
| **Drata** | "Compliance as Code" -- translates compliance requirements into automated, code-driven workflows integrated with dev environments; continuous monitoring and dynamic evidence collection |
| **Sprinto** | Entity-level controls mapped to multiple compliance standards; automated evidence collection |

**Velora design implication:** Build a unified internal control library where each control is tagged with its framework source(s). Use OSCAL format internally for machine-readability. Provide a mapping engine that can import NIST OLIR mappings and allow manual/AI-assisted custom mappings.

Sources: [Vanta vs OneTrust vs Drata](https://drata.com/blog/vanta-vs-onetrust-vs-drata), [Sprinto Comparison](https://sprinto.com/blog/secureframe-vs-vanta-vs-drata/)

### 3.4 Framework Update Monitoring [MEDIUM confidence]

| Technique | Description |
|-----------|-------------|
| **RSS/Atom feeds** | Subscribe to NIST, ISO, CSA, CIS update feeds |
| **OSCAL catalog diffing** | Compare OSCAL catalog versions programmatically to identify added/changed/removed controls |
| **Regulatory intelligence services** | UCF, Thomson Reuters, OneTrust maintain curated update feeds |
| **Manual review cadence** | Quarterly review of major framework publishers' announcements |
| **AI monitoring** | LLM-based scanning of regulatory body publications for material changes |

---

## 4. Vendor Enrichment Approaches

### 4.1 Public Data Sources for Vendor Intelligence [HIGH confidence]

| Source Category | Examples | Data Retrieved | API Available |
|----------------|----------|---------------|---------------|
| **Company intelligence** | Clearbit (now HubSpot), ZoomInfo, Crunchbase, Apollo | Firmographics, employee count, industry, revenue, tech stack | Yes |
| **Security ratings** | SecurityScorecard, BitSight, UpGuard, RiskRecon | External security posture score, risk factors | Yes |
| **Breach databases** | Have I Been Pwned, breach intelligence feeds | Historical breach records, exposed credentials | Yes (HIBP API) |
| **Certification registries** | IAF CertSearch, UKAS CertCheck, ANAB directory | ISO 27001/27701 certification status, certifying body, validity | Partial (web scrape) |
| **Corporate registries** | SEC EDGAR, Companies House (UK), state SOS databases | Incorporation, financial filings, officers | Yes (some) |
| **Domain/DNS intelligence** | WHOIS, DNS records, Certificate Transparency logs | Domain ownership, hosting, SSL certificates | Yes |
| **Dark web monitoring** | Recorded Future, Flashpoint, BitSight dark web intel | Leaked credentials, threat actor chatter, ransomware targeting | Yes (commercial) |
| **News/media** | Google News API, media monitoring services | Breach news, regulatory actions, leadership changes | Yes |
| **Privacy/legal** | Privacy policy URLs, DPA status, sub-processor lists | Data handling practices, legal compliance posture | Scrape |

### 4.2 Trust Center Scraping and Analysis [MEDIUM confidence]

| Platform | Capability |
|----------|-----------|
| **Whistic Trust Center Capture** | AI agents automatically collect vendor security documentation from trust centers; production-ready |
| **SafeBase** | Enterprise trust center platform; Chrome extension detects portal-based questions and auto-populates answers; 1000+ companies |
| **Custom scraping** | Parse vendor security/trust pages for: certifications listed, compliance badges, security whitepapers, DPA links, sub-processor lists |

**Trust center data extraction targets:**
- Certifications and their validity dates
- SOC 2 report availability and type (I vs II)
- Penetration testing recency
- Data processing locations
- Sub-processor lists
- Encryption standards
- Incident response contact information
- Bug bounty program presence

### 4.3 Certification Registry Lookups [MEDIUM confidence]

| Registry | Coverage | Access Method |
|----------|----------|---------------|
| **IAF CertSearch** | Global ISO certification database | Web portal, no public API |
| **UKAS CertCheck** | UK-accredited certifications | Web portal (certcheck.ukas.com) |
| **ANAB Directory** | US-accredited certification bodies | Web portal |
| **CSA STAR Registry** | Cloud security certifications (CSA STAR Level 1, 2) | Web portal, downloadable |
| **SOC report registries** | No centralized public registry exists | Must request directly from vendor |

**Velora design implication:** Build integrations with commercial enrichment APIs (Clearbit/ZoomInfo for firmographics, SecurityScorecard/BitSight for ratings). For certification validation, implement a combination of registry scraping, vendor self-attestation with evidence upload, and trust center capture.

Sources: [IAF CertSearch](https://www.iafcertsearch.org), [UKAS CertCheck](https://certcheck.ukas.com/), [ANAB ISO 27001 CBs](https://anab.ansi.org/accreditation/iso-iec-27001-information-security/)

---

## 5. Evidence Management Best Practices

### 5.1 Evidence Artifact Types and Parsing [HIGH confidence]

| Artifact | Parsing Approach | Key Extraction Targets |
|----------|-----------------|----------------------|
| **SOC 2 Type II report** | PDF/structured parsing; NLP for control status extraction | Audit period, opinion type (qualified/unqualified), exceptions noted, control descriptions, complementary user entity controls (CUECs) |
| **ISO 27001 certificate** | OCR + structured extraction | Certifying body, scope, certificate number, issue date, expiry date, surveillance audit dates |
| **Penetration test report** | NLP summarization | Test date, scope, critical/high findings count, remediation status, tester identity |
| **Vulnerability scan report** | Structured data extraction | Scan date, critical/high/medium/low counts, CVSS scores, remediation recommendations |
| **Privacy policy** | NLP analysis | Data types collected, processing purposes, retention periods, third-party sharing, rights mechanisms |
| **Insurance certificate** | OCR + field extraction | Coverage type, limits, policy period, insurer |
| **Business continuity plan** | NLP summarization | RTO/RPO, testing frequency, last test date, results |

### 5.2 Evidence-to-Control Mapping [HIGH confidence]

**Mapping strategy:** Each evidence artifact should map to one or more framework controls. The mapping defines what the evidence proves.

```
Evidence Artifact
  |-- Maps to: [Control 1, Control 2, ... Control N]
  |-- Coverage: Full | Partial | Supportive
  |-- Freshness: Valid | Stale | Expired
  |-- Confidence: High | Medium | Low
  |-- Source: Vendor-provided | Third-party attested | Independently verified
```

**Example mappings:**

| Evidence | Controls Covered | Coverage |
|----------|-----------------|----------|
| SOC 2 Type II (unqualified) | CC1.1-CC9.9 (all common criteria) | Full |
| ISO 27001 certificate | All Annex A controls in scope | Full (for certified scope) |
| Pen test report (annual) | CC7.1, CC7.2, A.12.6 (vulnerability management) | Partial |
| MFA screenshot | CC6.1, A.8.5 (access control) | Supportive |
| Encryption policy doc | CC6.1, CC6.7, A.8.24 (cryptography) | Partial |

### 5.3 Evidence Freshness and Expiry Tracking [HIGH confidence]

| Evidence Type | Validity Period | Stale Threshold | Expired Threshold | Action on Expiry |
|---------------|----------------|-----------------|-------------------|-----------------|
| SOC 2 Type II | 12 months from issue | 9 months | 12 months | Request new report; flag risk increase |
| SOC 2 Type I | 12 months from issue | 9 months | 12 months | Encourage upgrade to Type II |
| ISO 27001 certificate | 3 years (with annual surveillance) | 2.5 years | 3 years | Verify surveillance audit completed |
| Penetration test | 12 months (best practice) | 9 months | 12 months | Request new test |
| Vulnerability scan | 30-90 days | 60 days | 90 days | Request new scan |
| Insurance certificate | Policy period (typically 12 months) | 30 days before expiry | Expiry date | Request renewal confirmation |
| Privacy policy | Until material change | N/A | On material change | Re-review |

### 5.4 Evidence Confidence Scoring [MEDIUM confidence]

| Factor | High Confidence | Medium Confidence | Low Confidence |
|--------|----------------|-------------------|----------------|
| **Source** | Independent third-party attested (SOC 2, ISO cert) | Vendor-provided with supporting detail | Vendor self-attested only |
| **Recency** | Within 6 months | 6-12 months | Over 12 months |
| **Completeness** | Full scope coverage | Partial scope | Limited or unclear scope |
| **Consistency** | Aligns with external rating and other evidence | Minor discrepancies | Contradicts other evidence |
| **Verification** | Independently verifiable (registry lookup, public cert) | Verifiable with effort | Cannot be independently verified |

**Confidence score formula:**
```
Confidence = (Source_weight x Source_score) + (Recency_weight x Recency_score) +
             (Completeness_weight x Completeness_score) + (Consistency_weight x Consistency_score) +
             (Verification_weight x Verification_score)

Default weights: Source 30%, Recency 25%, Completeness 20%, Consistency 15%, Verification 10%
```

Sources: [SOC 2 Report Validity](https://secureframe.com/hub/soc-2/report-validity), [SOC 2 Evidence Collection](https://scytale.ai/center/soc-2/soc-2-evidence-collection/), [SOC 2 Evidence Templates 2026](https://www.konfirmity.com/blog/soc-2-evidence-collection-templates)

---

## 6. Continuous Monitoring Best Practices

### 6.1 Monitoring Signals by Priority [HIGH confidence]

| Priority | Signal | Source | Why It Matters |
|----------|--------|--------|---------------|
| **P0 -- Immediate** | Active data breach involving your data | Vendor notification, breach intel feeds | Direct impact to your organization |
| **P0 -- Immediate** | Ransomware attack on vendor | Dark web intel, news, vendor comms | Service disruption, data at risk |
| **P1 -- Urgent** | Critical CVE affecting vendor's stack | CVE databases, NVD, vendor advisories | Exploitable vulnerability window |
| **P1 -- Urgent** | Leaked credentials (vendor employees) | Dark web monitoring, paste sites | Unauthorized access risk |
| **P1 -- Urgent** | Significant rating drop (>15 points) | SecurityScorecard/BitSight | Deteriorating security posture |
| **P2 -- High** | SSL/TLS certificate expiry | Certificate monitoring | Service disruption, MITM risk |
| **P2 -- High** | DNS configuration changes | DNS monitoring | Domain hijacking, routing issues |
| **P2 -- High** | New regulatory action against vendor | News monitoring, regulatory feeds | Compliance exposure |
| **P3 -- Medium** | Moderate rating drop (5-15 points) | External ratings | Gradual posture degradation |
| **P3 -- Medium** | Certification expiry approaching | Evidence tracking | Compliance gap approaching |
| **P3 -- Medium** | Key personnel departure (CISO, CTO) | News, LinkedIn monitoring | Security leadership continuity |
| **P4 -- Low** | Minor rating fluctuation (<5 points) | External ratings | Normal variance, track trend |
| **P4 -- Low** | Vendor website/technology stack changes | Web scanning | Potential new attack surface |

### 6.2 Monitoring Frequency by Vendor Tier [HIGH confidence]

| Monitoring Activity | Tier 1 (Critical) | Tier 2 (High) | Tier 3 (Medium) | Tier 4 (Low) |
|--------------------|--------------------|----------------|------------------|---------------|
| External security rating check | Daily | Weekly | Monthly | Quarterly |
| Breach/incident alert monitoring | Real-time | Real-time | Daily | Weekly |
| Dark web credential monitoring | Daily | Weekly | Monthly | Quarterly |
| DNS/SSL monitoring | Daily | Weekly | Monthly | N/A |
| News/media monitoring | Daily | Weekly | Monthly | Quarterly |
| CVE exposure scanning | Weekly | Bi-weekly | Monthly | Quarterly |
| Financial health check | Monthly | Quarterly | Semi-annually | Annually |
| Certification status verification | Monthly | Quarterly | Semi-annually | Annually |

### 6.3 Alert Prioritization and Deduplication [MEDIUM confidence]

| Technique | Description |
|-----------|-------------|
| **Severity-based routing** | P0/P1 alerts go to incident response team immediately; P2/P3 go to TPRM analyst queue; P4 aggregated weekly |
| **Deduplication** | Match alerts by vendor + signal type + time window; merge duplicates within 24-hour window |
| **Correlation** | Multiple P2/P3 signals from same vendor within 48 hours elevate to P1 |
| **Suppression** | Known false positives suppressed with documented justification and periodic re-review |
| **Context enrichment** | Attach vendor tier, data sensitivity, contract value to every alert for triage context |
| **Trend detection** | Flag vendors with consistent downward rating trend over 30/60/90 days even if no single drop triggers alert |

### 6.4 Threat Intelligence Integration [MEDIUM confidence]

| Feed Type | Examples | Integration Method |
|-----------|---------|-------------------|
| **Commercial threat intel** | Recorded Future, Flashpoint, Mandiant | API integration, structured IOC feeds |
| **Open-source threat intel** | MITRE ATT&CK, AlienVault OTX, abuse.ch | API/download, STIX/TAXII format |
| **Security rating APIs** | SecurityScorecard, BitSight, UpGuard | REST API, webhook notifications |
| **Breach notification services** | Have I Been Pwned, breach databases | API polling |
| **Regulatory feeds** | SEC, ICO, state AG offices | RSS/web scraping |
| **Dark web monitoring** | Vendor-specific services | API integration |

Sources: [BitSight Continuous Monitoring](https://www.bitsight.com/products/continuous-monitoring), [BitSight Breach Intelligence](https://www.bitsight.com/blog/breach-intelligence-dark-web-intelligence-supply-chains), [SecurityScorecard Ratings](https://securityscorecard.com/why-securityscorecard/security-ratings/)

---

## 7. Communication and Workflow Patterns

### 7.1 Vendor Outreach Best Practices [HIGH confidence]

| Phase | Activity | Best Practice |
|-------|----------|---------------|
| **Initial outreach** | Questionnaire distribution | Personalized email from procurement/security contact; clear deadline (21-30 days for SIG Core, 14 days for SIG Lite); portal link for submission |
| **Reminder cadence** | Follow-up on non-response | Day 7: gentle reminder. Day 14: escalation to vendor's manager. Day 21: final notice with consequence statement. Day 28+: escalate to internal procurement |
| **Evidence request** | Request specific artifacts | Itemized list with clear descriptions; upload portal; acceptance criteria stated upfront |
| **Clarification** | Follow up on incomplete/unclear responses | Specific questions referencing exact questionnaire items; 7-day response window |
| **Results sharing** | Communicate findings back to vendor | Summary of gaps/findings; remediation requests with severity and deadline; remediation tracking portal |

### 7.2 Internal Escalation Patterns [HIGH confidence]

| Trigger | Escalation Path | SLA |
|---------|----------------|-----|
| Vendor non-response (>30 days) | TPRM analyst -> procurement lead -> business owner -> CISO | Each level: 5 business days |
| Critical finding in assessment | TPRM analyst -> CISO -> business owner | 24 hours to acknowledge, 5 days for remediation plan |
| Active vendor breach | TPRM analyst -> incident response team -> CISO -> legal -> executive team | Immediate (within 1 hour) |
| Rating drop below threshold | Automated alert -> TPRM analyst -> vendor relationship manager | 48 hours to investigate and respond |
| Certification expiry (no renewal) | Automated alert -> TPRM analyst -> vendor -> procurement | 30 days before expiry |
| Risk acceptance request | Business owner -> TPRM analyst -> risk committee -> CISO | 10 business days |

### 7.3 Renewal and Reassessment Scheduling [HIGH confidence]

| Event | Trigger | Lead Time | Action |
|-------|---------|-----------|--------|
| Contract renewal | Calendar-based | 90 days before renewal | Full reassessment based on tier; update risk score before renewal decision |
| Annual reassessment | Calendar-based | 60 days before due date | Distribute questionnaire; request updated evidence |
| Certification expiry | Evidence tracking | 60 days before expiry | Request updated certificate; verify with registry |
| SOC 2 report refresh | Evidence tracking | 30 days before current report goes stale | Request latest report |
| Event-triggered reassessment | Breach, M&A, rating drop, scope change | Immediately | Fast-track assessment (SIG Lite + critical evidence) |
| Post-remediation verification | Finding resolution | Per remediation plan deadline | Verify fix; update risk score |

### 7.4 SLA Tracking for Vendor Responses [HIGH confidence]

| Metric | Target SLA | Measurement |
|--------|-----------|-------------|
| Questionnaire completion (SIG Core) | 30 calendar days | Submission date - distribution date |
| Questionnaire completion (SIG Lite) | 14 calendar days | Submission date - distribution date |
| Evidence artifact upload | 14 calendar days | Upload date - request date |
| Remediation plan submission | 14 calendar days from finding notification | Plan date - notification date |
| Critical remediation completion | 30 calendar days from plan approval | Completion date - approval date |
| High remediation completion | 60 calendar days from plan approval | Completion date - approval date |
| Medium remediation completion | 90 calendar days from plan approval | Completion date - approval date |
| Clarification response | 7 calendar days | Response date - question date |
| Breach notification | Per contract (typically 24-72 hours) | Notification date - discovery date |

Sources: [ProcessUnity TPRM Workflows](https://www.processunity.com/resources/blogs/implementing-advanced-third-party-risk-management-workflows-to-mature-your-program/), [Venminder SLA Tracking](https://www.venminder.com/blog/tracking-vendor-performance-service-level-agreements), [Neotas TPRM Questionnaire](https://www.neotas.com/glossary/tprm-questionnaire/)

---

## 8. Design Recommendations for Velora

### 8.1 Scoring Engine Architecture

**Recommendation:** Build a configurable, multi-dimensional scoring engine.

```
Velora Risk Score = f(Inherent Risk, Control Effectiveness, External Posture, Monitoring Signals)

Where:
  Inherent Risk       = f(data_sensitivity, access_level, business_criticality, regulatory_exposure)
  Control Effectiveness = f(questionnaire_score, evidence_score, evidence_confidence)
  External Posture    = f(security_rating, scan_results, breach_history)
  Monitoring Signals  = f(recent_alerts, trend_direction, credential_exposure)

  All weights admin-configurable. All thresholds admin-configurable.
  Support FAIR-based monetary loss quantification as optional overlay.
```

**Key design decisions:**
1. Store scoring formulas as configurable rules (JSON/YAML), not hardcoded logic
2. Support both additive (weighted average) and multiplicative (inherent x control factor) models
3. Allow per-tier, per-industry, and per-regulation scoring templates
4. Provide audit trail for every score change (what changed, when, why)
5. Include manual override with mandatory justification
6. Normalize external ratings (SecurityScorecard A-F, BitSight 250-900) to internal 0-100 scale

### 8.2 Framework Intelligence Layer

**Recommendation:** Build on OSCAL as the internal representation format.

1. **Control catalog store:** Import NIST SP 800-53, CSF 2.0, ISO 27001, SOC 2 TSC, CIS Controls in OSCAL JSON format
2. **Cross-mapping engine:** Import NIST OLIR mappings; allow admin/AI-assisted custom mappings; store as relationship assertions with confidence levels
3. **Framework update pipeline:** Monitor publisher feeds; diff new OSCAL catalogs against current; flag added/modified/removed controls for review
4. **Assessment template generator:** Given a vendor's applicable frameworks, auto-generate a questionnaire covering the union of mapped controls with deduplication
5. **Evidence mapping:** Link evidence artifacts to controls with coverage type (full/partial/supportive)

### 8.3 Assessment Workflow Engine

**Recommendation:** Tiered, hybrid assessment with AI acceleration.

1. **Vendor onboarding:** Auto-classify tier based on inherent risk questionnaire (5-10 questions)
2. **Assessment selection:** Auto-select questionnaire type + evidence requirements based on tier
3. **AI pre-population:** Use LLM to pre-fill questionnaire from vendor trust center, prior responses, and public documentation
4. **Distribution and tracking:** Portal-based distribution with automated reminders at Day 7/14/21
5. **AI-assisted review:** LLM validates response consistency, flags gaps, cross-references evidence
6. **Scoring:** Auto-score based on configurable rules; analyst review for Tier 1/2
7. **Findings management:** Auto-generate findings with severity, remediation guidance, and deadlines
8. **Continuous monitoring:** Layer external ratings and monitoring signals on top of periodic assessments

### 8.4 Evidence Management Subsystem

**Recommendation:** Centralized evidence vault with intelligent processing.

1. **Upload and ingest:** Accept PDF, images (OCR), structured data; extract metadata automatically
2. **AI parsing:** LLM-based extraction of key fields from SOC 2 reports, ISO certs, pen test reports
3. **Control mapping:** Auto-map evidence to controls using AI + admin rules
4. **Freshness engine:** Track validity periods per evidence type; auto-alert on approaching expiry
5. **Confidence scoring:** Auto-calculate confidence based on source, recency, completeness, consistency, verification factors
6. **Evidence reuse:** One evidence artifact can satisfy controls across multiple frameworks (deduplication)
7. **Chain of custody:** Full audit trail of who uploaded, when, who reviewed, approval status

### 8.5 Continuous Monitoring Hub

**Recommendation:** Multi-signal aggregation with intelligent alerting.

1. **Signal ingestion:** APIs for SecurityScorecard, BitSight, breach feeds, dark web monitoring, CVE databases
2. **Alert engine:** Priority-based routing per Section 6.1; deduplication per Section 6.3
3. **Vendor risk timeline:** Visual timeline showing rating changes, assessments, evidence updates, alerts, and remediation activities
4. **Trend analysis:** 30/60/90-day trend detection; flag vendors with persistent downward trajectory
5. **Impact correlation:** When a new CVE is published, auto-identify which vendors are likely affected based on known tech stack
6. **Frequency calibration:** Monitoring frequency auto-adjusts based on vendor tier per Section 6.2

### 8.6 Communication and Workflow

**Recommendation:** Embedded communication with full audit trail.

1. **Vendor portal:** Self-service portal for questionnaire completion, evidence upload, finding remediation
2. **Automated outreach:** Template-based emails with dynamic content (vendor name, deadline, specific requests)
3. **Reminder engine:** Configurable reminder cadence with escalation rules
4. **SLA dashboard:** Real-time visibility into vendor response times vs SLA targets
5. **Internal collaboration:** Threaded comments on assessments, findings, and evidence with @mentions
6. **Notification hub:** Configurable notification preferences per user role (TPRM analyst, business owner, CISO)

---

## Appendix A: Key Data Model Entities

```
Vendor
  |-- Tier (1-4)
  |-- Inherent Risk Score
  |-- Residual Risk Score
  |-- External Rating (normalized)
  |-- Monitoring Score
  |-- Composite Risk Score
  |-- Assessments[] -> Assessment
  |-- Evidence[] -> Evidence Artifact
  |-- Alerts[] -> Monitoring Alert
  |-- Findings[] -> Finding
  |-- Contacts[] -> Vendor Contact

Assessment
  |-- Type (SIG Core, SIG Lite, CAIQ, Custom)
  |-- Status (Draft, Distributed, In Progress, Submitted, Under Review, Complete)
  |-- Due Date
  |-- Completion Date
  |-- Score
  |-- Responses[] -> Questionnaire Response
  |-- Evidence[] -> Evidence Artifact

Evidence Artifact
  |-- Type (SOC 2 Type II, ISO Cert, Pen Test, etc.)
  |-- Upload Date
  |-- Valid From / Valid To
  |-- Freshness Status (Valid, Stale, Expired)
  |-- Confidence Score
  |-- Control Mappings[] -> Control
  |-- Coverage Type (Full, Partial, Supportive)

Control
  |-- Framework (ISO 27001, SOC 2, NIST CSF, etc.)
  |-- Control ID
  |-- Title
  |-- Description
  |-- Cross-Mappings[] -> Control (other frameworks)

Finding
  |-- Severity (Critical, High, Medium, Low)
  |-- Status (Open, Remediation In Progress, Verified Closed, Risk Accepted)
  |-- Remediation Deadline
  |-- Assigned To (vendor contact)
  |-- Internal Owner (business owner)

Monitoring Alert
  |-- Priority (P0-P4)
  |-- Signal Type
  |-- Source
  |-- Status (New, Acknowledged, Investigating, Resolved, Suppressed)
  |-- Vendor Impact Assessment
```

---

## Appendix B: Source Reference Index

### Scoring and Ratings
- [SecurityScorecard Scoring Methodology](https://support.securityscorecard.com/hc/en-us/articles/8366223642651-How-SecurityScorecard-calculates-your-scores)
- [SecurityScorecard 10 Risk Factors](https://securityscorecard.com/blog/securityscorecard-10-risk-factors-explained/)
- [SecurityScorecard Scoring 3.0](https://support.securityscorecard.com/hc/en-us/articles/16235105523739-Prepare-for-Scoring-3-0)
- [BitSight Rating Calculation](https://help.bitsighttech.com/hc/en-us/articles/231950968-How-are-Bitsight-Security-Ratings-Calculated)
- [BitSight Risk Categories Guide](https://help.bitsighttech.com/hc/en-us/articles/360007320574-A-Guide-to-Navigating-and-Prioritizing-Bitsight-Risk-Categories-Risk-Vectors)
- [BitSight vs SecurityScorecard 2025](https://www.upguard.com/compare/bitsight-vs-securityscorecard)
- [FAIR Institute](https://www.fairinstitute.org)
- [FAIR Third-Party Assessment Model](https://www.fairinstitute.org/fair-third-party-assessment-model)
- [FAIR Inherent Risk Measurement](https://www.fairinstitute.org/blog/using-the-fair-model-to-measure-inherent-risk)
- [FAIR Inherent vs Residual Risk](https://www.fairinstitute.org/blog/inherent-risk-vs.-residual-risk-explained-in-90-seconds)
- [Safe Security TPRM Guide 2026](https://safe.security/resources/blog/2026-guide-to-third-party-risk-management-tprm/)
- [HighBond Risk Score Configuration](https://help.highbond.com/helpdocs/highbond/en-us/Content/risk_manager/risk_score_config.htm)

### Assessment Methodologies
- [SIG Questionnaire Guide (UpGuard)](https://www.upguard.com/blog/sig-questionnaire)
- [2025 SIG Update (Shared Assessments)](https://sharedassessments.org/blog/2025-sig/)
- [CAIQ vs SIG (BitSight)](https://www.bitsight.com/blog/caiq-vs-sig-top-questionnaires-vendor-risk-assessment)
- [CAIQ vs SIG (HyperComply)](https://www.hypercomply.com/blog/caiq-vs-sig)
- [Vendor Tiering (UpGuard)](https://www.upguard.com/blog/what-is-vendor-tiering)
- [Vendor Tiering (Safe Security)](https://safe.security/resources/blog/how-to-tier-vendors-for-effective-third-party-risk-management-tprm/)
- [TPRM Alliance Tiering Guide](https://www.tprmalliance.com/comprehensive-guide-to-vendor-risk-tiering-in-third-party-risk-management-tprm/)

### AI and Automation
- [ProcessUnity AI Control Reviews](https://www.processunity.com/third-party-risk-management/ai-based-control-reviews/)
- [VISO TRUST AI Assessment](https://visotrust.com/ai-assessment-tprm-vendor/)
- [Atlas Systems AI TPRM](https://www.atlassystems.com/complyscore/ai-tprm/introduction)
- [SafeBase AI Questionnaire Assistance](https://safebase.io/blog/ai-questionnaire-assistance)
- [Black Kite AI Questionnaire Management](https://blackkite.com/platform/ai-questionnaire-management)

### Framework and Mapping
- [NIST OSCAL](https://pages.nist.gov/OSCAL/)
- [OSCAL GitHub Repository](https://github.com/usnistgov/OSCAL)
- [CIS Controls OSCAL Repository](https://www.cisecurity.org/insights/blog/introducing-the-cis-controls-oscal-repository)
- [NIST OLIR Catalog](https://csrc.nist.gov/projects/olir/informative-reference-catalog)
- [ISO 27001 to NIST CSF Mapping](https://csrc.nist.gov/projects/olir/informative-reference-catalog/details?referenceId=154)
- [Cross-Mapping NIST, ISO, CIS](https://ridgelinecyber.com/blog/cross-mapping-nist-iso-cis-frameworks/)
- [Vanta vs OneTrust vs Drata](https://drata.com/blog/vanta-vs-onetrust-vs-drata)

### Evidence Management
- [SOC 2 Report Validity (Secureframe)](https://secureframe.com/hub/soc-2/report-validity)
- [SOC 2 Evidence Collection (Scytale)](https://scytale.ai/center/soc-2/soc-2-evidence-collection/)
- [SOC 2 Evidence Templates 2026](https://www.konfirmity.com/blog/soc-2-evidence-collection-templates)
- [SOC 2 Documentation (Secureframe)](https://secureframe.com/hub/soc-2/compliance-documentation)

### Continuous Monitoring
- [BitSight Continuous Monitoring](https://www.bitsight.com/products/continuous-monitoring)
- [BitSight Breach Intelligence](https://www.bitsight.com/blog/breach-intelligence-dark-web-intelligence-supply-chains)
- [SecurityScorecard Security Ratings](https://securityscorecard.com/why-securityscorecard/security-ratings/)

### Vendor Enrichment
- [UKAS CertCheck](https://certcheck.ukas.com/)
- [ANAB ISO 27001 Accreditation](https://anab.ansi.org/accreditation/iso-iec-27001-information-security/)
- [Whistic Trust Center Capture](https://www.whistic.com/)
- [SafeBase Trust Center Platform](https://safebase.io/)

### Communication and Workflow
- [ProcessUnity TPRM Workflows](https://www.processunity.com/resources/blogs/implementing-advanced-third-party-risk-management-workflows-to-mature-your-program/)
- [Venminder SLA Tracking](https://www.venminder.com/blog/tracking-vendor-performance-service-level-agreements)
- [Neotas TPRM Questionnaire](https://www.neotas.com/glossary/tprm-questionnaire/)
- [LearnTPRM Platform Comparison 2026](https://learntprm.com/blog/securityscorecard-bitsight-upguard-comparison-2026)
