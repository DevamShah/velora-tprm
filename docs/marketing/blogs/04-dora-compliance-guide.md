# DORA Compliance for Third-Party Risk: A Practical Guide

*Published by Velora | Third-Party Risk Management*

---

## DORA is Here. Your TPRM Program Isn't Ready.

The Digital Operational Resilience Act (DORA) entered into force on January 17, 2025. If you're a financial entity operating in the EU --- or a technology provider serving one --- DORA fundamentally changes how you manage third-party ICT risk.

This isn't another checkbox regulation. DORA mandates specific, testable requirements for how financial institutions identify, assess, monitor, and report on their ICT third-party service providers. And it has teeth: non-compliance can result in fines up to 1% of average daily global turnover, imposed daily until remediation.

Most TPRM programs built for SOC 2 and ISO 27001 compliance are structurally incapable of meeting DORA requirements. Here's what you need to know and how to close the gap.

---

## What DORA Requires for Third-Party ICT Risk

DORA's third-party risk requirements span Articles 28 through 30, with additional technical standards (RTS/ITS) published by the European Supervisory Authorities. Here's what matters for your TPRM program:

### Article 28: General Principles for ICT Third-Party Risk

**Key requirements:**

1. **Proportionate risk management.** Financial entities must manage ICT third-party risk as an integral component of their overall ICT risk management framework --- not as a separate compliance exercise.

2. **Strategy for ICT third-party risk.** You need a documented strategy that includes policies for assessing, monitoring, and managing ICT third-party risk throughout the lifecycle --- from selection through exit.

3. **Exit strategies.** Every critical ICT third-party arrangement must have a documented exit plan. Not a vague "we'll migrate" --- a specific, tested transition plan with data portability guarantees.

4. **Concentration risk.** You must identify and manage concentration risk --- the danger of over-reliance on a single ICT provider or a small number of providers. If your entire infrastructure runs on one cloud provider, DORA wants you to understand and mitigate that risk.

### Article 28a: Register of Information

This is the requirement that catches most organizations off guard.

**You must maintain a complete register of ALL ICT third-party arrangements.** Not just critical ones. All of them. The register must include:

- Full identification of each ICT third-party service provider
- The services provided and their classification (critical or important)
- The contractual arrangements in place
- The locations where data is processed and stored
- Sub-outsourcing chains (your vendor's vendors)
- Date of last audit or assessment
- Risk assessment results

This register must be:
- **Machine-readable** (not a PDF or Word document)
- **Reportable to supervisory authorities on request**
- **Updated continuously** (not annually)
- **Inclusive of sub-outsourcing** (your vendor's third parties)

If your current register is an Excel spreadsheet updated quarterly, you're not compliant.

### Article 29: Assessment of ICT Third-Party Risk

**Before entering any ICT third-party arrangement, you must:**

1. Assess whether the arrangement concerns a critical or important function
2. Evaluate whether supervisory conditions for outsourcing are met
3. Identify and assess all relevant risks, including concentration risk
4. Conduct due diligence on the provider's ability to meet DORA requirements
5. Identify conflicts of interest

**For critical or important functions, you must additionally:**

1. Verify the provider's operational resilience capabilities
2. Assess the provider's ICT security posture
3. Evaluate the provider's incident reporting capabilities
4. Confirm the provider supports your own resilience testing obligations
5. Assess the provider's exit planning and data portability capabilities

### Article 30: Contractual Requirements

Every ICT third-party contract must include specific provisions:

- **Service level descriptions** with precise quantitative and qualitative performance targets
- **Incident notification** requirements (the provider must report ICT incidents to you)
- **Audit rights** --- you and your supervisory authority must have the right to audit the provider
- **Exit provisions** including transition periods and data portability
- **Data location** requirements --- where data is processed and stored
- **Sub-outsourcing** conditions --- the provider must notify you of any sub-outsourcing arrangements

For critical providers, contracts must additionally include:
- Full access to audit and inspection
- Termination rights if the provider fails to meet requirements
- Participation in your resilience testing (including threat-led penetration testing)

---

## The Timeline and Enforcement Reality

| Date | Event |
|------|-------|
| Jan 17, 2025 | DORA entered into force |
| Jan-Jun 2025 | ESAs published technical standards (RTS/ITS) |
| 2025-2026 | Supervisory authorities begin assessments |
| Ongoing | Enforcement actions for non-compliance |

**Who's affected:**

- Credit institutions (banks)
- Investment firms
- Insurance and reinsurance undertakings
- Payment institutions
- Electronic money institutions
- Crypto-asset service providers
- Central securities depositories
- Trading venues
- ICT third-party service providers designated as "critical" by ESAs

**Who's indirectly affected:**

Every technology vendor serving financial institutions. If your customers are subject to DORA, they will impose DORA-aligned requirements on you through contracts, assessments, and audit demands.

---

## Why Legacy TPRM Tools Can't Handle DORA

DORA's requirements expose the structural weaknesses of traditional TPRM platforms:

### 1. The Register of Information Problem

DORA requires a continuously updated, machine-readable register of ALL ICT third-party arrangements. Legacy TPRM tools store vendor information in assessment-centric data models --- you have to complete an assessment to create a vendor record. DORA requires the register to exist independently of assessments, updated in real time, and exportable in structured formats.

### 2. The Sub-Outsourcing Problem

DORA requires you to track your vendors' vendors. If your cloud provider uses a third-party for DNS, and that DNS provider has a sub-contractor for DDoS mitigation, DORA wants you to know about it. Legacy TPRM tools have no concept of supply chain depth. They track direct relationships only.

### 3. The Continuous Monitoring Problem

DORA doesn't accept annual assessments as sufficient. You need continuous monitoring of your ICT third-party providers' risk posture. Legacy tools are built around periodic assessment cycles --- annual or quarterly. They have no real-time monitoring infrastructure.

### 4. The Concentration Risk Problem

DORA requires explicit analysis of concentration risk. If 60% of your critical functions depend on AWS, that's a concentration risk that needs to be identified, quantified, and reported. Legacy TPRM tools assess vendors individually. They have no portfolio-level risk analysis.

### 5. The Reporting Problem

DORA requires you to report your register of information to supervisory authorities on request, in their specified format. Legacy tools generate PDF reports designed for human reading, not structured data exports for regulatory submission.

---

## How Velora Automates DORA Compliance

Velora was designed with regulatory frameworks like DORA in mind. Here's how each DORA requirement maps to Velora capabilities:

### Register of Information

Velora maintains a **living register** of all ICT third-party arrangements, updated in real time as vendor information changes. The register includes:

- Automated vendor discovery and classification
- Service mapping (which vendor supports which business function)
- Criticality classification (critical, important, standard)
- Contractual metadata (dates, terms, SLAs)
- Sub-outsourcing chains (populated through vendor assessments and public data)
- Data location tracking (processing and storage jurisdictions)
- Exportable in machine-readable formats (JSON, CSV, XML) matching ESA templates

### Continuous Assessment and Monitoring

Velora's AI continuously monitors vendor risk posture:

- **Evidence expiration tracking:** SOC 2 reports, certifications, and pen tests are tracked with expiration dates. When evidence ages out, re-assessment is triggered automatically.
- **Real-time alerts:** Changes in vendor security posture, breach notifications, and regulatory actions generate immediate alerts.
- **Automated re-assessment:** When material changes are detected, Velora initiates a targeted re-assessment focused on affected controls.

### Concentration Risk Analysis

Velora's portfolio-level analytics identify concentration risk:

- **Provider dependency mapping:** Which business functions depend on which providers?
- **Single points of failure:** If Provider X goes down, which functions are affected?
- **Geographic concentration:** Are too many providers in the same jurisdiction?
- **Technology concentration:** Are too many providers dependent on the same infrastructure?

Concentration risk is quantified using FAIR methodology, translated into financial exposure, and reported at the portfolio level.

### DORA-Specific Assessment Templates

Velora includes pre-built assessment templates aligned with DORA requirements:

- **DORA ICT Risk Assessment:** Maps to Articles 28-30 requirements
- **DORA Exit Strategy Assessment:** Validates exit planning for critical providers
- **DORA Incident Reporting Assessment:** Validates provider incident notification capabilities
- **DORA Resilience Testing Assessment:** Validates provider participation in resilience testing

Each template includes AI pre-population from existing vendor data, confidence scoring, and gap analysis against DORA requirements.

### Regulatory Reporting

When the supervisory authority requests your register of information, Velora generates it in minutes:

- Structured data export in ESA-specified formats
- Complete vendor inventory with classification and risk scores
- Sub-outsourcing chains
- Assessment history and findings
- Concentration risk analysis
- Gap analysis against DORA requirements

---

## A Practical DORA Compliance Roadmap

### Phase 1: Inventory (Weeks 1-4)

1. Import your vendor inventory into Velora (CSV import or manual entry)
2. Classify each vendor as Critical, Important, or Standard
3. Map vendors to business functions and data flows
4. Identify sub-outsourcing relationships where known
5. Generate your initial Register of Information

### Phase 2: Gap Assessment (Weeks 5-8)

1. Run DORA-specific assessments for all Critical and Important vendors
2. Identify gaps in contractual provisions (audit rights, exit plans, SLAs)
3. Identify gaps in vendor resilience capabilities
4. Quantify concentration risk at the portfolio level
5. Generate gap analysis report with remediation priorities

### Phase 3: Remediation (Weeks 9-16)

1. Initiate contract amendments for missing DORA provisions
2. Request exit strategies from critical providers
3. Implement continuous monitoring for all critical and important providers
4. Establish incident notification requirements with providers
5. Develop concentration risk mitigation plans

### Phase 4: Ongoing Compliance (Continuous)

1. Maintain living Register of Information
2. Run continuous monitoring and re-assessments
3. Update concentration risk analysis as portfolio changes
4. Generate regulatory reports on demand
5. Conduct annual DORA-aligned resilience testing with critical providers

---

## The Cost of Non-Compliance

DORA non-compliance isn't a theoretical risk:

- **Financial penalties:** Up to 1% of average daily global turnover, per day, until remediation
- **Supervisory actions:** Regulators can require termination of ICT third-party arrangements
- **Reputational damage:** Public disclosure of supervisory findings
- **Operational risk:** Without proper TPRM, you're exposed to the very disruptions DORA was designed to prevent

For a mid-size financial institution with EUR 500M in annual revenue, a 1% daily fine is EUR 13,700 per day --- nearly EUR 100,000 per week of non-compliance.

The cost of compliance is a fraction of that. The cost of non-compliance is open-ended.

---

## Start Now

DORA is not a future requirement. It's current law. Supervisory authorities are building their enforcement capabilities. Early movers who demonstrate compliance now will have a significant advantage when regulatory scrutiny intensifies.

The financial entities that built their TPRM programs on spreadsheets and annual assessments have a structural problem. DORA demands continuous, comprehensive, quantified third-party risk management. That requires purpose-built technology.

---

*Velora includes pre-built DORA compliance templates, automated Register of Information, concentration risk analysis, and regulatory reporting. Start your DORA compliance program at velora.io.*
