---
tags:
  - archeon
  - forgeon
  - product
  - product-velora
---

# Velora TPRM v2.0 -- Stage B: Dynamic Test Scenarios

> **Author**: Parikshika (QA Lead, Pantheon)
> **Version**: 1.0.0
> **Date**: 2026-03-27
> **Status**: Active
> **Classification**: Internal -- QA

---

## Overview

Stage B Dynamic Test Scenarios are product-specific, multi-step user journeys that test real workflows end-to-end. Each scenario simulates what a real user would do across the application, validating frontend rendering, API calls, state transitions, data persistence, and cross-module integration.

## Test Environment

- **Frontend**: http://localhost:3000 (Next.js)
- **Backend API**: http://localhost:8000/api/v1 (FastAPI)
- **Tenant**: Velora Demo (slug: `velora-demo`)
- **Tenant ID**: `00000000-0000-4000-a000-000000000001`

## Test Users

| Email | Password | Role | Permissions Summary |
|-------|----------|------|---------------------|
| admin@velora-demo.com | admin123 | Admin | Full access (all permissions) |
| admin2@velora-demo.com | admin123 | Admin | Full access (all permissions) |
| analyst@velora-demo.com | analyst123 | Risk Analyst | vendors.read, assessments.read/write, frameworks.read, scoring.read/write, monitoring.read, evidence.read/write, reports.read |
| analyst2@velora-demo.com | analyst123 | Risk Analyst | Same as analyst |

## Personas

| Persona | Name | Simulated By | Description |
|---------|------|--------------|-------------|
| TPRM Program Lead | Anya Kohli | admin@velora-demo.com | 420 vendors, needs <7 day assessment cycle |
| CISO | Marcus Chen | admin@velora-demo.com | 600+ vendors, board-ready reports, financial risk |
| GRC Analyst | Priya Nair | analyst@velora-demo.com | 180 vendors, AI-parsed evidence, control mapping |
| Vendor Responder | David Park | analyst2@velora-demo.com | 40-60 questionnaires/quarter |

## Seed Data Reference

15 seeded vendors across 4 tiers:

| Tier | Count | Vendors |
|------|-------|---------|
| Critical | 3 | Amazon Web Services, Salesforce, Workday |
| High | 4 | Stripe, Datadog, Okta, Snowflake |
| Medium | 5 | Zoom, Slack, HubSpot, Twilio, Cloudflare |
| Low | 3 | Calendly, Loom, Miro |

Seeded assessment templates: SIG Core, SIG Lite, CAIQ v4, Custom.
Seeded frameworks: SOC 2, ISO 27001, NIST CSF 2.0, PCI DSS 4.0, HIPAA, GDPR, DORA.

---

## Scenario 1: First-Time Admin Setup (Anya)

**Persona**: Anya Kohli -- TPRM Program Lead
**Objective**: Login, explore dashboard, manage vendors, add contact, calculate tier.
**Prerequisites**: Application running. Seed data loaded. No prior session.

| Step | Action | Route / API | Expected Result | Pass/Fail |
|------|--------|-------------|-----------------|-----------|
| 1 | Navigate to http://localhost:3000 | `/` | Redirects to `/login` page. Login form renders with email and password fields. | |
| 2 | Enter `admin@velora-demo.com` / `admin123` and click "Sign In" | `POST /api/v1/auth/login` | Login succeeds. JWT tokens returned. User redirected to `/dashboard`. | |
| 3 | Verify dashboard loads completely | `/dashboard` | Dashboard page renders. Navigation sidebar shows all menu items: Dashboard, Vendors, Assessments, Evidence, Findings, Frameworks, Monitoring, Reports, Communications, Admin. | |
| 4 | Verify dashboard stat cards display data | `/dashboard` | At least 4 stat cards visible (total vendors, active assessments, open findings, average risk score). Total vendors card shows "15". | |
| 5 | Click "Vendors" in sidebar navigation | `/vendors` | Vendor list page loads. Table displays 15 vendors. Columns include: Name, Domain, Industry, Tier, Status, Risk Score. Pagination shows correct total. | |
| 6 | Verify vendor tier badges render correctly | `/vendors` | Critical vendors (AWS, Salesforce, Workday) show red/critical badge. High tier shows orange. Medium shows yellow. Low shows green. | |
| 7 | Click "Add Vendor" / "New Vendor" button | `/vendors/new` | Vendor creation form renders with fields: Name, Domain, Industry, Country, Employee Count, Status, Tier, Data Classification, Business Criticality, Contract Value, Contract Start/End Date, Tags, Primary Contact Name, Primary Contact Email. | |
| 8 | Fill all fields: Name="Acme Security", Domain="acmesec.com", Industry="Cybersecurity", Country="US", Employee Count=500, Status="active", Tier="medium", Data Classification="confidential", Business Criticality="medium", Contract Value=75000, Tags="security,vendor" | `/vendors/new` | All form fields accept input. Validation indicators show all required fields are filled. No form errors. | |
| 9 | Click "Create Vendor" / "Save" | `POST /api/v1/vendors` | Success toast/notification appears. API returns 201. Redirects to vendor list or vendor detail page. | |
| 10 | Navigate to vendor list | `/vendors` | Newly created vendor "Acme Security" appears in the list. Total count is now 16. Tier badge shows "medium". | |
| 11 | Click on "Acme Security" in the vendor list | `/vendors/{id}` | Vendor detail page loads. Overview tab shows all entered data: name, domain, industry, country, tier badge, data classification, business criticality, contract value, contract dates. | |
| 12 | Navigate to Contacts tab on vendor detail | `/vendors/{id}` (contacts tab) | Contacts section renders. Empty state message shown (no contacts yet). "Add Contact" button is visible. | |
| 13 | Click "Add Contact" button. Fill: Name="John Doe", Email="john@acmesec.com", Role="Security Lead", Phone="+1-555-0100" | `/vendors/{id}` | Contact form renders. All fields accept input. | |
| 14 | Submit the contact form | `POST /api/v1/vendors/{id}/contacts` | API returns 201. Contact "John Doe" appears in the contacts list with correct role and email. | |
| 15 | Click "Calculate Tier" or "Recalculate Tier" button | `POST /api/v1/vendors/{id}/calculate-tier` | API returns vendor_id and calculated tier value. Tier badge on the page updates to reflect the calculated tier (may differ from manually set tier based on algorithm). | |
| 16 | Verify tier badge updated in the UI | `/vendors/{id}` | Tier badge displays the newly calculated tier. If changed, visual indicator (color, label) matches the new tier level. | |

---

## Scenario 2: Bulk Vendor Import (Anya)

**Persona**: Anya Kohli -- TPRM Program Lead
**Objective**: Import multiple vendors via CSV paste, verify all imported correctly.
**Prerequisites**: Logged in as admin@velora-demo.com. Base 15 vendors exist.

| Step | Action | Route / API | Expected Result | Pass/Fail |
|------|--------|-------------|-----------------|-----------|
| 1 | Navigate to Vendors page | `/vendors` | Vendor list loads. Note current vendor count (15 or 16 if Scenario 1 ran). | |
| 2 | Click "Bulk Import" or "Import" button | `/vendors` (import modal/page) | Bulk import interface appears. CSV paste area or file upload input visible. Format instructions/template shown. | |
| 3 | Paste CSV data with 5 vendors: `name,domain,industry\nNetSkope,netskope.com,Cloud Security\nCrowdStrike,crowdstrike.com,Endpoint Security\nPalo Alto Networks,paloaltonetworks.com,Network Security\nZscaler,zscaler.com,Zero Trust\nSentinelOne,sentinelone.com,XDR` | Import interface | CSV text accepted. Preview may show parsed rows. 5 rows detected. | |
| 4 | Click "Import" / "Submit" | `POST /api/v1/vendors/bulk-import` | API returns BulkImportResult. Success count = 5. Error count = 0. Success toast shows "5 vendors imported". | |
| 5 | Verify vendor list updated | `/vendors` | Total vendor count increased by 5. All 5 new vendors appear in the list: NetSkope, CrowdStrike, Palo Alto Networks, Zscaler, SentinelOne. | |
| 6 | Click on "NetSkope" in the list | `/vendors/{id}` | Vendor detail loads. Name = "NetSkope". Domain = "netskope.com". Industry = "Cloud Security". Status defaults to "active" or "pending". | |
| 7 | Click on "CrowdStrike" in the list | `/vendors/{id}` | Vendor detail loads. Name = "CrowdStrike". Domain = "crowdstrike.com". Industry = "Endpoint Security". | |
| 8 | Click on "Palo Alto Networks" in the list | `/vendors/{id}` | Vendor detail loads. Name = "Palo Alto Networks". Domain = "paloaltonetworks.com". Industry = "Network Security". | |
| 9 | Click on "Zscaler" in the list | `/vendors/{id}` | Vendor detail loads. Name = "Zscaler". Domain = "zscaler.com". Industry = "Zero Trust". | |
| 10 | Click on "SentinelOne" in the list | `/vendors/{id}` | Vendor detail loads. Name = "SentinelOne". Domain = "sentinelone.com". Industry = "XDR". | |
| 11 | Attempt duplicate import with same CSV | `POST /api/v1/vendors/bulk-import` | Import handles duplicates gracefully. Either skips duplicates (success=0, skipped=5) or returns appropriate error messages per row. No crash or 500 error. | |

---

## Scenario 3: Full Assessment Lifecycle (Priya)

**Persona**: Priya Nair -- GRC Analyst
**Objective**: Create, distribute, submit, review, and complete an assessment through all state transitions.
**Prerequisites**: Logged in as analyst@velora-demo.com. Vendors and templates seeded.

| Step | Action | Route / API | Expected Result | Pass/Fail |
|------|--------|-------------|-----------------|-----------|
| 1 | Navigate to Assessments page | `/assessments` | Assessment list page loads. Existing seeded assessments display (if any). Columns: Title, Vendor, Template, Status, Due Date, Created. | |
| 2 | Click "New Assessment" / "Create Assessment" | `/assessments/new` | Assessment creation form renders. Fields: Vendor (dropdown), Template (dropdown), Title (text), Due Date (date picker). | |
| 3 | Select vendor = "Amazon Web Services" from dropdown | `/assessments/new` | AWS selected. Vendor name displays in the field. | |
| 4 | Select template = "SIG Core" from dropdown | `/assessments/new` | SIG Core template selected. Template name displays. | |
| 5 | Enter title = "AWS Annual Assessment 2026" | `/assessments/new` | Title field accepts text input. | |
| 6 | Set due date = 30 days from today | `/assessments/new` | Date picker allows selection. Date displays correctly. | |
| 7 | Click "Create" / "Save" | `POST /api/v1/assessments` | API returns 201. Assessment created with status = "draft". Redirect to assessment detail or list page. Success notification shown. | |
| 8 | Verify assessment appears in list with "draft" status | `/assessments` | New assessment "AWS Annual Assessment 2026" appears in list. Status column shows "Draft" badge (grey or neutral color). Vendor column shows "Amazon Web Services". | |
| 9 | Click on the new assessment to open detail | `/assessments/{id}` | Assessment detail page loads. Shows: title, vendor name, template name, status = "draft", due date, created date. Action buttons visible: "Distribute", "Cancel". | |
| 10 | Click "Distribute" button | `POST /api/v1/assessments/{id}/distribute` | Confirmation dialog may appear. After confirm, API returns updated assessment. Status changes from "draft" to "distributed". Status badge updates in UI to "Distributed" (blue or active color). | |
| 11 | Verify status change persists on page reload | `/assessments/{id}` (reload) | After page refresh, status still shows "Distributed". No regression to "Draft". | |
| 12 | Click "Submit" to simulate vendor submission | `POST /api/v1/assessments/{id}/submit` | API returns updated assessment. Status changes from "distributed" to "submitted". Status badge updates to "Submitted" (orange or pending color). | |
| 13 | Click "Start Review" button | `POST /api/v1/assessments/{id}/start-review` | API returns updated assessment. Status changes to "in_review". Current user assigned as reviewer. Status badge shows "In Review" (purple or review color). | |
| 14 | Navigate to questionnaire responses | `GET /api/v1/assessments/{id}/responses` | Response list loads. Shows questionnaire items from SIG Core template. Each item has: question text, response text, confidence score, review status. | |
| 15 | Review a response: accept it (mark as approved) | `PUT /api/v1/assessments/{id}/responses/{response_id}` | API returns updated response. Review status changes to "accepted". Visual indicator (checkmark, green highlight) appears. | |
| 16 | Review another response: flag it for follow-up | `PUT /api/v1/assessments/{id}/responses/{response_id}` | API returns updated response. Review status changes to "flagged". Visual indicator (warning icon, yellow highlight) appears. | |
| 17 | Click "Complete Assessment" | `POST /api/v1/assessments/{id}/complete` | API returns updated assessment. Status changes to "completed". Status badge shows "Completed" (green). Final score may be calculated and displayed. | |
| 18 | Verify completed assessment in list view | `/assessments` | Assessment shows in list with "Completed" status. Cannot be further edited (distribute/submit/review buttons disabled or hidden). | |

---

## Scenario 4: Evidence Upload and Analysis (Priya)

**Persona**: Priya Nair -- GRC Analyst
**Objective**: Upload evidence document, trigger processing, review control mappings.
**Prerequisites**: Logged in as analyst@velora-demo.com. Vendors seeded.

| Step | Action | Route / API | Expected Result | Pass/Fail |
|------|--------|-------------|-----------------|-----------|
| 1 | Navigate to Evidence page | `/evidence` | Evidence list page loads. Table with columns: Document Name, Vendor, Type, Status, Upload Date. May be empty or show seeded evidence. | |
| 2 | Click "Upload Evidence" / "Upload" button | `/evidence` (upload modal/form) | Upload form appears. Fields: Vendor (dropdown), Document Type (dropdown: SOC 2, ISO 27001, Pen Test, Policy, Other), File Name (text), Description (text). File upload or presigned URL flow. | |
| 3 | Select vendor = "Salesforce" | Upload form | Salesforce selected in vendor dropdown. | |
| 4 | Select document type = "SOC 2" | Upload form | SOC 2 selected. Type displays correctly. | |
| 5 | Enter file name = "Salesforce_SOC2_Type2_2025.pdf" and description = "Annual SOC 2 Type II report" | Upload form | Fields accept input. | |
| 6 | Submit the upload | `POST /api/v1/evidence/upload-url` | API returns 201 with evidence_id and presigned_url (or mock upload confirmation). Evidence record created with status = "uploaded" or "pending_processing". | |
| 7 | Verify evidence appears in list | `/evidence` | New evidence "Salesforce_SOC2_Type2_2025.pdf" appears in list. Status = "uploaded" or "pending". Vendor = "Salesforce". Type = "SOC 2". | |
| 8 | Click on the evidence item to view detail | `/evidence` (detail view/modal) | Evidence detail page/modal loads. Shows: file name, vendor, document type, status, upload date, uploader, description. "Process" button visible. | |
| 9 | Click "Process" / "Analyze" button | `POST /api/v1/evidence/{id}/process` | API triggers AI processing. Status changes to "processing" then "processed" (may be async). Loading indicator shown during processing. | |
| 10 | Verify extracted fields display after processing | `GET /api/v1/evidence/{id}` | Evidence detail shows extracted metadata: audit period, opinion type, auditor name, report date. "Extracted Fields" section populated. | |
| 11 | View control mappings | `GET /api/v1/evidence/{id}/mappings` | Control mappings section shows list of mapped controls. Each mapping has: control_id, framework name, clause reference, confidence score, verification status. | |
| 12 | Approve a control mapping (verify = true) | `PUT /api/v1/evidence/{id}/mappings/{mapping_id}` with `verified: true` | API returns updated mapping. Verification status changes to "verified". Visual indicator (checkmark, green) appears next to the mapping. | |
| 13 | Reject a control mapping (verify = false) | `PUT /api/v1/evidence/{id}/mappings/{mapping_id}` with `verified: false` | API returns updated mapping. Verification status changes to "rejected". Visual indicator (X mark, red) appears. | |
| 14 | Verify changes persist on reload | `/evidence` (reload detail) | After page refresh, approved mapping still shows "verified", rejected mapping still shows "rejected". No state loss. | |

---

## Scenario 5: CISO Dashboard Review (Marcus)

**Persona**: Marcus Chen -- CISO
**Objective**: Review executive dashboard, verify all widgets, interact with data.
**Prerequisites**: Logged in as admin@velora-demo.com. Full seed data loaded (vendors, assessments, findings, monitoring alerts).

| Step | Action | Route / API | Expected Result | Pass/Fail |
|------|--------|-------------|-----------------|-----------|
| 1 | Navigate to Dashboard | `/dashboard` | Dashboard page loads. `GET /api/v1/reports/dashboards/data/executive` called. Loading skeleton shown, then data populates. | |
| 2 | Verify stat cards display | `/dashboard` | Stat cards visible: Total Vendors (15), Active Assessments (count >= 0), Open Findings (count >= 0), Average Risk Score (numeric value). All cards show actual numbers, not "0" or "N/A" unless data genuinely empty. | |
| 3 | Verify Risk Distribution chart renders | `/dashboard` | Pie chart or donut chart showing vendor distribution by risk tier: Critical, High, Medium, Low. Chart has legend. Segments are interactive (hover shows count). | |
| 4 | Verify Assessment Status chart renders | `/dashboard` | Bar chart or progress chart showing assessments by status: Draft, Distributed, Submitted, In Review, Completed. Chart renders with at least one non-zero status. | |
| 5 | Verify Risk Trend chart renders | `/dashboard` | Line chart showing risk score trend over time. X-axis = dates, Y-axis = score. At least one data point present. | |
| 6 | Verify Top-10 Vendors by Risk table renders | `/dashboard` | Table showing up to 10 vendors sorted by risk score (highest first). Columns: Vendor Name, Risk Score, Tier, Status. AWS, Salesforce, Workday should appear near top. | |
| 7 | Click on a vendor name in the Top-10 table (e.g., "Amazon Web Services") | `/vendors/{aws_id}` | Navigation triggers to vendor detail page. AWS vendor detail loads with correct data. Back button or breadcrumb allows return. | |
| 8 | Navigate back to Dashboard | `/dashboard` | Dashboard loads again. All widgets re-render with same data. No stale or missing data. | |
| 9 | Verify Open Findings widget | `/dashboard` | Shows count or mini-list of open findings by severity (critical, high, medium, low). Counts match the findings module data. | |
| 10 | Verify Monitoring Alerts widget | `/dashboard` | Shows recent alerts or alert count by priority (P0, P1, P2, P3). At least seeded alerts display. | |
| 11 | Hover over chart elements | `/dashboard` | Tooltips appear on hover showing data values. No JavaScript errors. Charts respond to mouse interaction. | |

---

## Scenario 6: Alert Investigation and Resolution (Marcus)

**Persona**: Marcus Chen -- CISO
**Objective**: Find a critical alert, acknowledge it, resolve it, verify vendor timeline.
**Prerequisites**: Logged in as admin@velora-demo.com. Monitoring alerts seeded.

| Step | Action | Route / API | Expected Result | Pass/Fail |
|------|--------|-------------|-----------------|-----------|
| 1 | Navigate to Monitoring page | `/monitoring` | Alert list page loads. `GET /api/v1/monitoring/alerts` called. Table shows alerts with columns: Title, Vendor, Priority, Status, Created. | |
| 2 | Filter alerts by priority = P0 or P1 | `/monitoring?priority=P0` | Filter applied. Only P0/P1 alerts display. URL updates with query parameter. Count reflects filtered results. | |
| 3 | Identify a P0 or P1 alert with status = "open" | `/monitoring` | At least one open P0/P1 alert visible in the list. Note the alert title, vendor, and created date. | |
| 4 | Click on the alert to open detail | `/monitoring/{alert_id}` | Alert detail page loads. Shows: title, description, priority badge, status = "open", vendor name, source, created timestamp. Action buttons: "Acknowledge", "Resolve", "Suppress". | |
| 5 | Click "Acknowledge" button | `PUT /api/v1/monitoring/alerts/{id}/acknowledge` | API returns updated alert. Status changes from "open" to "acknowledged". Status badge updates in UI. "Acknowledged by" field shows current user. Timestamp recorded. | |
| 6 | Verify status change on the detail page | `/monitoring/{alert_id}` | Status badge shows "Acknowledged" (yellow/orange). Acknowledge timestamp displayed. "Resolve" button still available. "Acknowledge" button disabled or hidden. | |
| 7 | Click "Resolve" button | Resolve form/modal | Resolution form appears with "Notes" text area. | |
| 8 | Enter resolution notes = "Investigated. Vendor patched affected system. Verified fix via external scan. No data exposure confirmed." | Resolve form | Text area accepts input. | |
| 9 | Submit resolution | `PUT /api/v1/monitoring/alerts/{id}/resolve` with notes | API returns updated alert. Status changes to "resolved". Resolution notes saved. Resolved timestamp recorded. | |
| 10 | Verify final status = "resolved" on detail page | `/monitoring/{alert_id}` | Status badge shows "Resolved" (green). Resolution notes display. Both acknowledge and resolve timestamps shown. Action buttons disabled or hidden. | |
| 11 | Navigate to the associated vendor's timeline | `GET /api/v1/monitoring/vendors/{vendor_id}/timeline` | Vendor timeline loads. The alert event appears in the timeline. Shows: alert title, priority, status transitions (open -> acknowledged -> resolved), timestamps. | |
| 12 | Verify timeline is chronological | Vendor timeline | Events sorted by timestamp (newest first or oldest first, consistent). Alert events interleave with other vendor events (assessments, evidence uploads, etc.). | |

---

## Scenario 7: Finding Remediation Workflow (Priya)

**Persona**: Priya Nair -- GRC Analyst
**Objective**: Find a critical finding, add remediation action, close the finding.
**Prerequisites**: Logged in as analyst@velora-demo.com. Findings seeded.

| Step | Action | Route / API | Expected Result | Pass/Fail |
|------|--------|-------------|-----------------|-----------|
| 1 | Navigate to Findings page | `/findings` | Findings list page loads. `GET /api/v1/findings` called. Table shows: Title, Vendor, Severity, Status, Created. | |
| 2 | Filter by severity = "critical" | `/findings?severity=critical` | Filter applied. Only critical findings display. Count reflects filtered results. | |
| 3 | Identify a critical finding with status = "open" | `/findings` | At least one open critical finding visible. Note the finding title and vendor. | |
| 4 | Click on the finding to open detail | `/findings/{id}` | Finding detail page loads. Shows: title, description, severity badge (critical = red), status = "open", vendor name, assessment reference, remediation guidance text. | |
| 5 | Review the remediation guidance section | `/findings/{id}` | Remediation guidance text is present and readable. May include: recommended actions, priority, SLA deadline, references. | |
| 6 | Click "Add Remediation Action" button | `/findings/{id}` (remediation form) | Remediation action form appears. Fields: Title, Description, Assignee, Due Date, Priority. | |
| 7 | Fill remediation action: Title = "Implement MFA enforcement", Description = "Enable mandatory MFA for all admin accounts on vendor platform", Due Date = 14 days from today | Remediation form | All fields accept input. | |
| 8 | Submit the remediation action | `POST /api/v1/findings/{id}/remediation` | API returns 201. Remediation action created. Action appears in the remediation actions list on the finding detail page. Status of action = "open" or "pending". | |
| 9 | Verify remediation action displays in list | `/findings/{id}` | Remediation actions section shows the new action: "Implement MFA enforcement" with correct due date and status. | |
| 10 | Click "Close Finding" button | `/findings/{id}` (close form) | Close form appears. Fields: Resolution Status (dropdown: verified_closed, risk_accepted, false_positive), Notes. | |
| 11 | Select resolution = "verified_closed", enter notes = "Vendor confirmed MFA enforced across all admin accounts. Verified via SOC 2 report update." | Close form | Fields accept input. | |
| 12 | Submit the close action | `POST /api/v1/findings/{id}/close` with `status: "verified_closed"` | API returns updated finding. Status changes to "verified_closed". Finding detail shows closed status with resolution notes and timestamp. | |
| 13 | Navigate back to Findings list | `/findings` | Finding no longer appears when filtered by status = "open". Shows up when filtered by status = "verified_closed" or when no status filter applied. | |
| 14 | Filter by status = "open" | `/findings?status=open` | The closed finding does NOT appear in the filtered results. Only open findings display. | |

---

## Scenario 8: Framework Exploration (Priya)

**Persona**: Priya Nair -- GRC Analyst
**Objective**: Browse frameworks, explore clause tree, view cross-framework mappings.
**Prerequisites**: Logged in as analyst@velora-demo.com. Frameworks seeded.

| Step | Action | Route / API | Expected Result | Pass/Fail |
|------|--------|-------------|-----------------|-----------|
| 1 | Navigate to Frameworks page | `/frameworks` | Frameworks list page loads. `GET /api/v1/frameworks` called. Cards or table showing: SOC 2, ISO 27001, NIST CSF 2.0, PCI DSS 4.0, HIPAA, GDPR, DORA. | |
| 2 | Verify all seeded frameworks display | `/frameworks` | 7 frameworks visible. Each shows: name, version, description, clause count. | |
| 3 | Click on "SOC 2" card/row | `/frameworks/{soc2_id}` | Framework detail page loads. Shows: name = "SOC 2", full description, version, total clauses, categories. | |
| 4 | Verify clause tree renders | `GET /api/v1/frameworks/{id}/clauses` | Hierarchical clause tree displays. Top-level categories (Trust Service Criteria) expandable. Sub-clauses nested underneath. Tree is navigable (expand/collapse). | |
| 5 | Expand a top-level category | `/frameworks/{soc2_id}` | Child clauses appear. Each clause shows: clause ID, title, description snippet. | |
| 6 | Click on a specific clause | `/frameworks/{soc2_id}` (clause detail) | Clause detail shows: full description, control requirements. "Cross-Framework Mappings" section visible. | |
| 7 | View cross-framework mappings for selected clause | `GET /api/v1/frameworks/{id}/clauses/{clause_id}/mappings` | Mappings list shows related clauses from other frameworks. Each mapping has: target framework name, target clause ID, target clause title, mapping confidence score (percentage or label). | |
| 8 | Find an ISO 27001 mapping in the list | Mappings section | At least one mapping to ISO 27001 visible. Shows the ISO 27001 clause reference (e.g., "A.9.1.1") with confidence score. | |
| 9 | Verify mapping confidence displays | Mappings section | Confidence score shown as percentage (e.g., "92%") or label (e.g., "High"). Color-coded: high = green, medium = yellow, low = red. | |
| 10 | Navigate to Unified Controls tab/page | `/frameworks` (unified controls) or `GET /api/v1/frameworks/unified-controls` | Unified control library loads. Shows deduplicated controls aggregated across all frameworks. Each control shows: control name, mapped framework count, description. | |
| 11 | Verify unified controls show deduplication | Unified controls page | Controls that appear in multiple frameworks show combined view. E.g., "Access Control" mapped to SOC 2, ISO 27001, NIST CSF. Framework badges visible per control. | |

---

## Scenario 9: Role-Based Access Control (All Personas)

**Persona**: All -- testing RBAC enforcement
**Objective**: Verify that each role can only perform authorized actions.
**Prerequisites**: All test users exist. Application running.

### Part A: Viewer Role (Simulated -- no seeded Viewer user, test via API with limited permissions)

| Step | Action | Route / API | Expected Result | Pass/Fail |
|------|--------|-------------|-----------------|-----------|
| 1 | Login as analyst@velora-demo.com (Risk Analyst) | `POST /api/v1/auth/login` | Login succeeds. Token returned. | |
| 2 | Navigate to Vendors page | `/vendors` | Vendor list loads (has vendors.read). All 15 vendors visible. | |
| 3 | Attempt to access "Add Vendor" page | `/vendors/new` | Page may render but submit should fail: analyst has assessments.write but NOT vendors.write. API returns 403 Forbidden on `POST /api/v1/vendors`. | |
| 4 | Attempt to delete a vendor via API | `DELETE /api/v1/vendors/{id}` | API returns 403 Forbidden. Analyst role does not have vendors.delete permission. | |
| 5 | Navigate to Admin > Users page | `/admin/users` | Page loads but API call `GET /api/v1/admin/users` returns 403. Analyst does not have admin.users permission. Error state displayed. | |
| 6 | Navigate to Admin > Audit Log | `/admin/audit-log` | API call returns 403. Analyst does not have admin.audit permission. | |
| 7 | Verify analyst CAN create assessments | `/assessments/new` | Assessment creation form loads. Can select vendor and template. Submit succeeds (has assessments.write). | |
| 8 | Verify analyst CAN view frameworks | `/frameworks` | Framework list loads successfully. All frameworks visible (has frameworks.read). | |
| 9 | Verify analyst CAN upload evidence | `/evidence` | Upload form accessible. Submit succeeds (has evidence.write). | |
| 10 | Verify analyst CANNOT generate reports | `POST /api/v1/reports/generate` | API returns 403. Analyst role does not have reports.generate permission. | |

### Part B: Admin Role

| Step | Action | Route / API | Expected Result | Pass/Fail |
|------|--------|-------------|-----------------|-----------|
| 11 | Logout and login as admin@velora-demo.com | `POST /api/v1/auth/login` | Login succeeds. Full Admin token returned. | |
| 12 | Navigate to Admin > Users | `/admin/users` | User list loads. Shows all seeded users. API returns 200. | |
| 13 | Navigate to Admin > Audit Log | `/admin/audit-log` | Audit log page loads. Entries visible. API returns 200. | |
| 14 | Create a new vendor | `POST /api/v1/vendors` | API returns 201. Vendor created (has vendors.write). | |
| 15 | Delete a vendor | `DELETE /api/v1/vendors/{id}` | API returns 204. Vendor soft-deleted (has vendors.delete). | |
| 16 | Generate a report | `POST /api/v1/reports/generate` | API returns 201. Report generated (has reports.generate). | |
| 17 | Access communications templates | `/communications` | Templates load. API returns 200 (has admin.settings). | |
| 18 | Access monitoring write operations | `PUT /api/v1/monitoring/alerts/{id}/acknowledge` | API returns 200. Alert acknowledged (has monitoring.write). | |

---

## Scenario 10: Communication and Notification Flow

**Persona**: Admin
**Objective**: Verify notification system, communication logs, email templates.
**Prerequisites**: Logged in as admin@velora-demo.com. Notifications seeded or generated from prior actions.

| Step | Action | Route / API | Expected Result | Pass/Fail |
|------|--------|-------------|-----------------|-----------|
| 1 | Check notification bell icon in top navigation | Header/navbar | Notification bell icon visible. Badge shows unread count (numeric). If count > 0, badge is colored. | |
| 2 | Click notification bell to open dropdown | Header notification dropdown | Dropdown opens. Shows list of recent notifications. Each notification has: title, message preview, timestamp, read/unread indicator. | |
| 3 | Verify unread notifications have visual distinction | Notification dropdown | Unread notifications have bold text or dot indicator. Read notifications appear dimmer or normal weight. | |
| 4 | Click on a notification to mark as read | `PUT /api/v1/communications/notifications/{id}/read` | API returns updated notification with `read_at` timestamp. Visual indicator changes from unread to read. Badge count decreases by 1. | |
| 5 | Verify badge count decreased | Header/navbar | Notification badge number = previous count - 1. If all read, badge may disappear. | |
| 6 | Navigate to Communications page | `/communications` | Communications page loads. Tabs visible: Notifications, Templates, Logs (or similar layout). | |
| 7 | Verify Notifications tab renders | `/communications` (notifications tab) | Full notification list with pagination. Shows all notifications for current user. Columns: Title, Message, Date, Status (read/unread). | |
| 8 | Verify Email Templates tab renders | `/communications` (templates tab) | `GET /api/v1/communications/templates` called. Email templates list shows seeded templates. Each template has: name, subject, channel, last updated. | |
| 9 | Verify Communication Logs tab renders | `/communications` (logs tab) | `GET /api/v1/communications/logs` called. Log entries show: recipient, channel (email/in-app/slack), status (sent/failed/pending), timestamp. | |
| 10 | Click "Mark All as Read" button (if available) | `PUT /api/v1/communications/notifications/read-all` | API returns count of marked-read notifications. All notifications now show as read. Badge count = 0. | |

---

## Scenario 11: Report Generation

**Persona**: Marcus Chen -- CISO
**Objective**: Generate a report, verify it appears in the report list.
**Prerequisites**: Logged in as admin@velora-demo.com. Report templates seeded.

| Step | Action | Route / API | Expected Result | Pass/Fail |
|------|--------|-------------|-----------------|-----------|
| 1 | Navigate to Reports page | `/reports` | Reports page loads. May show previously generated reports or empty state. "Generate Report" button visible. | |
| 2 | Click "Generate Report" button | `/reports` (generate form/modal) | Report generation form appears. Fields: Template (dropdown), Title (text), Format (dropdown: PDF, CSV, XLSX). | |
| 3 | Select template (e.g., "Executive Summary") | Generate form | Template selected. May show template description or preview. | |
| 4 | Enter title = "Q1 2026 Executive Risk Report" | Generate form | Title field accepts input. | |
| 5 | Select format = "PDF" | Generate form | PDF selected from format dropdown. | |
| 6 | Click "Generate" / "Submit" | `POST /api/v1/reports/generate` | API returns 201. Report object returned with id, title, status = "pending" or "completed", format = "pdf". Success notification shown. | |
| 7 | Verify report appears in list | `/reports` | Report "Q1 2026 Executive Risk Report" appears in the report list. Status column shows "pending" (if async) or "completed". Format shows "PDF". | |
| 8 | Wait for report completion (if async) | `/reports` (poll or auto-refresh) | Status transitions from "pending" to "completed". | |
| 9 | Verify download link appears for completed report | `/reports` | Download button/link appears next to the completed report. Clicking it triggers download or opens in new tab. | |
| 10 | Verify report detail accessible | `GET /api/v1/reports/{id}` | Report detail shows: title, template used, format, generation date, generated by, status, file size (if applicable). | |

---

## Scenario 12: Admin User Management

**Persona**: Anya Kohli -- TPRM Program Lead (Admin)
**Objective**: Invite a new user, edit role, deactivate user.
**Prerequisites**: Logged in as admin@velora-demo.com.

| Step | Action | Route / API | Expected Result | Pass/Fail |
|------|--------|-------------|-----------------|-----------|
| 1 | Navigate to Admin > Users | `/admin/users` | User management page loads. `GET /api/v1/admin/users` returns user list. Shows: Name, Email, Role(s), Status (active/inactive), Last Login. | |
| 2 | Verify seeded users display | `/admin/users` | 4 users visible: Admin Primary, Admin Secondary, Analyst Primary, Analyst Secondary. All show status = "Active". | |
| 3 | Click "Invite User" / "Add User" button | `/admin/users` (invite form) | User creation form appears. Fields: Email, First Name, Last Name, Role (dropdown). | |
| 4 | Fill: Email = "newuser@velora-demo.com", First Name = "Test", Last Name = "Manager", Role = "TPRM Manager" | Invite form | All fields accept input. Role dropdown shows all available roles. | |
| 5 | Submit the user invitation | `POST /api/v1/admin/users` | API returns 201. New user created. User appears in the user list. Status = "Active". Role = "TPRM Manager". | |
| 6 | Verify new user in the list | `/admin/users` | "Test Manager" appears in the list. Email shows (possibly masked). Role = "TPRM Manager". Total user count = 5. | |
| 7 | Click on the new user to edit | `/admin/users` (edit form) | Edit form loads with current values pre-filled. Role field editable. | |
| 8 | Change role from "TPRM Manager" to "Risk Analyst" | Edit form | Role dropdown allows selection of "Risk Analyst". | |
| 9 | Save the role change | `PUT /api/v1/admin/users/{id}` or `POST /api/v1/admin/users/{id}/roles` + `DELETE` old role | API returns 200. Role updated successfully. User list reflects new role = "Risk Analyst". | |
| 10 | Verify role change persists | `/admin/users` (reload) | After page refresh, user "Test Manager" still shows role = "Risk Analyst". | |
| 11 | Click "Deactivate" on the user | `/admin/users` (deactivate action) | Confirmation dialog appears: "Are you sure you want to deactivate Test Manager?" | |
| 12 | Confirm deactivation | `DELETE /api/v1/admin/users/{id}` | API returns 204. User status changes to "Inactive" in the list. User row may be greyed out or moved to inactive section. | |
| 13 | Verify deactivated user cannot login | `POST /api/v1/auth/login` with deactivated credentials | Login attempt returns 401 or specific "account deactivated" error. User cannot access the application. | |

---

## Scenario 13: Vendor 360-Degree View

**Persona**: Anya Kohli -- TPRM Program Lead (Admin)
**Objective**: Explore full vendor detail across all tabs, edit and verify persistence.
**Prerequisites**: Logged in as admin@velora-demo.com. AWS vendor seeded with contacts and timeline events.

| Step | Action | Route / API | Expected Result | Pass/Fail |
|------|--------|-------------|-----------------|-----------|
| 1 | Navigate to Vendors page | `/vendors` | Vendor list loads. | |
| 2 | Click on "Amazon Web Services" (critical tier) | `/vendors/{aws_id}` | Vendor detail page loads. | |
| 3 | Verify Overview tab displays complete data | `/vendors/{aws_id}` (overview) | Shows: Name = "Amazon Web Services", Domain = "aws.amazon.com", Industry = "Cloud Infrastructure", Country = "US", Employee Count = 1,500,000, Status = "active", Tier badge = "Critical" (red), Data Classification = "restricted", Business Criticality = "critical", Contract Value = $2,400,000, Contract Start = 2024-01-01, Contract End = 2027-12-31. | |
| 4 | Verify risk score displays | `/vendors/{aws_id}` | Inherent risk score = 85.0 (or calculated score). Score visualization (gauge, number, color indicator) renders. | |
| 5 | Verify tier badge is correct color and label | `/vendors/{aws_id}` | "Critical" badge with red background. Clearly visible. | |
| 6 | Verify tags display | `/vendors/{aws_id}` | Tags shown: "cloud", "infrastructure", "critical". Each tag is a chip/badge. | |
| 7 | Switch to Contacts tab | `/vendors/{aws_id}` (contacts tab) | `GET /api/v1/vendors/{id}/contacts` called. Contacts list loads. Shows primary contact: "Enterprise Support" with email. | |
| 8 | Verify contact data displays | Contacts tab | Contact name, role, email (possibly masked), phone visible. | |
| 9 | Switch to Timeline tab | `/vendors/{aws_id}` (timeline tab) | `GET /api/v1/monitoring/vendors/{id}/timeline` called. Timeline renders. Shows chronological events: vendor created, assessments, alerts, evidence uploads. | |
| 10 | Verify timeline events have correct format | Timeline tab | Each event shows: event type icon, title, description, timestamp, actor. Events sorted chronologically. | |
| 11 | Click "Edit" button on vendor detail | `/vendors/{aws_id}` (edit mode) | Edit form loads with current values pre-populated. Fields are editable. | |
| 12 | Change Industry from "Cloud Infrastructure" to "Cloud Infrastructure & AI" | Edit form | Industry field accepts new text. | |
| 13 | Click "Save" | `PUT /api/v1/vendors/{aws_id}` | API returns 200. Success notification. Industry field now shows "Cloud Infrastructure & AI". | |
| 14 | Reload the page | `/vendors/{aws_id}` (hard refresh) | Industry still shows "Cloud Infrastructure & AI". Change persisted to database. | |

---

## Scenario 14: AI Auto-Fill Assessment

**Persona**: Priya Nair -- GRC Analyst
**Objective**: Use AI auto-fill on a draft assessment, review AI-generated responses.
**Prerequisites**: Logged in as analyst@velora-demo.com. At least one draft assessment exists (create one if needed).

| Step | Action | Route / API | Expected Result | Pass/Fail |
|------|--------|-------------|-----------------|-----------|
| 1 | Navigate to Assessments page | `/assessments` | Assessment list loads. | |
| 2 | Find or create a draft assessment | `/assessments` or `/assessments/new` | At least one assessment with status = "draft" available. Note its ID and vendor. | |
| 3 | Open the draft assessment detail | `/assessments/{id}` | Assessment detail loads. Status = "draft". "AI Auto-Fill" button visible (or in actions menu). | |
| 4 | Click "AI Auto-Fill" button | `POST /api/v1/ai/auto-fill` with `assessment_id` | API call triggers. Loading indicator shown ("AI is analyzing..."). Response returned with auto-fill results: total_questions, filled_count, flagged_count. | |
| 5 | Verify responses are pre-populated | `GET /api/v1/assessments/{id}/responses` | Questionnaire responses now have AI-generated answer text. Previously empty responses now contain content. | |
| 6 | Verify AI confidence scores display | Assessment responses view | Each AI-filled response shows a confidence score (0-100% or high/medium/low). Scores are visible next to each response. | |
| 7 | Verify flagged items appear in review queue | `/assessments/review-queue` or `GET /api/v1/ai/review-queue` | Review queue shows items with low confidence that need human review. Each item has: question, AI response, confidence score, reason for flagging. | |
| 8 | Open a flagged item from review queue | Review queue detail | Flagged item detail shows: original question, AI-generated response, confidence score, source citations (if any), "Accept" and "Reject" buttons. | |
| 9 | Accept a flagged item | `PUT /api/v1/ai/review-queue/{item_id}` with decision = "accepted" | API returns success. Item removed from review queue. Response marked as human-reviewed. | |
| 10 | Reject a flagged item and provide manual answer | `PUT /api/v1/ai/review-queue/{item_id}` with decision = "rejected" | API returns success. Item removed from review queue. Can enter manual replacement response. | |

---

## Scenario 15: Cross-Module Navigation Flow

**Persona**: Anya Kohli -- TPRM Program Lead (Admin)
**Objective**: Navigate across modules following natural data links, verify breadcrumbs and back navigation.
**Prerequisites**: Logged in as admin@velora-demo.com. Full seed data loaded. At least one finding with vendor link.

| Step | Action | Route / API | Expected Result | Pass/Fail |
|------|--------|-------------|-----------------|-----------|
| 1 | Start on Dashboard | `/dashboard` | Dashboard loads with all widgets. | |
| 2 | Click "Open Findings" stat card (or findings count) | `/findings` or `/findings?status=open` | Navigates to Findings list page. Filter pre-set to "open" status. Findings list loads. | |
| 3 | Verify the findings list filtered correctly | `/findings` | Only open findings displayed. Status column shows "open" for all visible rows. | |
| 4 | Click on a finding to view detail | `/findings/{id}` | Finding detail page loads. Shows severity, vendor name (as clickable link), description, remediation guidance. | |
| 5 | Click on the vendor name link within the finding | `/vendors/{vendor_id}` | Navigation to vendor detail page. Vendor detail loads with correct data matching the vendor referenced in the finding. | |
| 6 | Verify vendor detail loaded correctly | `/vendors/{vendor_id}` | Vendor name matches what was shown in the finding. All vendor data displays. | |
| 7 | Click "Assessments" tab on vendor detail (or navigate to assessments filtered by this vendor) | `/vendors/{vendor_id}` (assessments tab) or `/assessments?vendor_id={id}` | Shows assessments for this specific vendor. May be empty or show existing assessments. | |
| 8 | Use browser back button or breadcrumb to go back | Browser back / breadcrumb | Returns to previous page (vendor detail, then finding detail, then findings list). State preserved. No data loss or reload glitches. | |
| 9 | Verify breadcrumb navigation works (if implemented) | Breadcrumb trail | Breadcrumbs show: Dashboard > Findings > Finding Detail > Vendor Detail. Clicking "Findings" in breadcrumb returns to findings list. | |
| 10 | Navigate from vendor detail to monitoring timeline | `/vendors/{vendor_id}` -> timeline tab | Vendor timeline loads. Shows events related to this vendor. | |

---

## Scenario 16: Scoring Recalculation

**Persona**: Marcus Chen -- CISO (Admin)
**Objective**: Recalculate a vendor's risk score, verify update propagation.
**Prerequisites**: Logged in as admin@velora-demo.com. Vendors and scoring model seeded.

| Step | Action | Route / API | Expected Result | Pass/Fail |
|------|--------|-------------|-----------------|-----------|
| 1 | Navigate to vendor detail for "Stripe" | `/vendors/{stripe_id}` | Vendor detail loads. Note current risk score (inherent_risk_score = 72.0 from seed, or calculated score). | |
| 2 | Record the current risk score value | `/vendors/{stripe_id}` | Note exact score number for comparison. | |
| 3 | Click "Recalculate Score" button (if on vendor page) or navigate to scoring | `POST /api/v1/scoring/calculate/{vendor_id}` | API triggers score calculation. Returns ScoreBreakdown with: overall_score, category_scores, scoring_model_id, calculated_at timestamp. | |
| 4 | Verify score updates in the UI | `/vendors/{stripe_id}` | Risk score display reflects the newly calculated value. Score visualization (number, gauge, color) updates. | |
| 5 | Check score history | `GET /api/v1/scoring/vendors/{vendor_id}/history` | Score history shows at least the new data point. History list shows: score value, calculated_at, scoring_model used. | |
| 6 | Verify score history chart (if rendered) | Vendor detail (scoring tab) | Chart shows historical data points plotted over time. New calculation appears as latest point. | |
| 7 | Navigate to Dashboard | `/dashboard` | Dashboard loads. Average risk score in stat card should reflect the recalculated value (if it changed from seed default). | |
| 8 | Check portfolio summary | `GET /api/v1/scoring/portfolio` | Portfolio summary returns aggregate stats: average_score, score_distribution, vendors_by_risk_level. Values consistent with current vendor scores. | |

---

## Scenario 17: Admin Audit Trail Verification

**Persona**: Anya Kohli -- TPRM Program Lead (Admin)
**Objective**: Perform actions, verify they appear in audit log, test filtering and export.
**Prerequisites**: Logged in as admin@velora-demo.com.

| Step | Action | Route / API | Expected Result | Pass/Fail |
|------|--------|-------------|-----------------|-----------|
| 1 | Create a new vendor: Name = "AuditTest Corp", Domain = "audittest.com" | `POST /api/v1/vendors` | Vendor created. 201 returned. | |
| 2 | Note the timestamp of creation | N/A | Record current UTC time for audit log verification. | |
| 3 | Update the vendor: change Industry to "Testing" | `PUT /api/v1/vendors/{id}` | Vendor updated. 200 returned. | |
| 4 | Delete the vendor | `DELETE /api/v1/vendors/{id}` | Vendor soft-deleted. 204 returned. | |
| 5 | Navigate to Admin > Audit Log | `/admin/audit-log` | Audit log page loads. `GET /api/v1/admin/audit-logs` called. Log entries display in reverse chronological order. | |
| 6 | Verify "vendor.create" action appears | `/admin/audit-log` | Log entry shows: action = "vendor.create" (or similar), entity_type = "vendor", entity_id = the created vendor's UUID, user = admin@velora-demo.com, timestamp near recorded time. | |
| 7 | Verify "vendor.update" action appears | `/admin/audit-log` | Log entry shows: action = "vendor.update", entity_type = "vendor", same entity_id, includes change details (industry changed). | |
| 8 | Verify "vendor.delete" action appears | `/admin/audit-log` | Log entry shows: action = "vendor.delete", entity_type = "vendor", same entity_id. | |
| 9 | Filter by action type = "vendor.create" | `/admin/audit-log?action=vendor.create` | Only vendor.create entries display. Other action types hidden. Results include the entry from step 6. | |
| 10 | Filter by entity_type = "vendor" | `/admin/audit-log?entity_type=vendor` | Only vendor-related audit entries display. All 3 entries from steps 1-4 appear. | |
| 11 | Click "Export" / "Export CSV" | `POST /api/v1/admin/audit-logs/export` | Export triggers. Response contains audit log data in exportable format. Browser download initiates (CSV or JSON). | |
| 12 | Verify exported data contains the recent entries | Downloaded file | Exported file includes the 3 audit entries created during this scenario. Fields match what was displayed in the UI. | |

---

## Scenario 18: Error Handling and Edge Cases

**Persona**: Various
**Objective**: Verify the application handles errors, invalid input, and edge cases gracefully.
**Prerequisites**: Logged in as admin@velora-demo.com.

### 18a: 404 Handling

| Step | Action | Route / API | Expected Result | Pass/Fail |
|------|--------|-------------|-----------------|-----------|
| 1 | Navigate to `/vendors/00000000-0000-0000-0000-000000000000` (nonexistent UUID) | `/vendors/00000000-...` | 404 error page or "Vendor not found" message displayed. No blank page or unhandled exception. Application remains navigable. | |
| 2 | Navigate to `/assessments/nonexistent-id` (invalid UUID format) | `/assessments/nonexistent-id` | Error handled gracefully. Either 400 (invalid UUID format) or 404 page. No server crash. | |
| 3 | Navigate to `/completely-fake-route` | `/completely-fake-route` | Next.js 404 page renders. Shows "Page not found" or similar. Navigation sidebar still functional. | |

### 18b: Form Validation

| Step | Action | Route / API | Expected Result | Pass/Fail |
|------|--------|-------------|-----------------|-----------|
| 4 | Go to New Vendor form. Submit with all fields empty | `/vendors/new` -> Submit | Client-side validation fires. Error messages appear on required fields (Name is required, Domain is required, etc.). Form does NOT submit. No API call made. | |
| 5 | Enter only Name = "Test". Submit | `/vendors/new` -> Submit | Validation errors on remaining required fields. Partial data not submitted. | |
| 6 | Enter invalid email format in contact form: "not-an-email" | Vendor contact form | Email field shows validation error: "Invalid email format". Form does not submit. | |
| 7 | Enter negative number in Employee Count field | `/vendors/new` | Field rejects negative input or shows validation error. Does not accept negative values. | |
| 8 | Enter contract end date before contract start date | `/vendors/new` | Validation error: "End date must be after start date" or similar. Form does not submit. | |

### 18c: Duplicate and Conflict Handling

| Step | Action | Route / API | Expected Result | Pass/Fail |
|------|--------|-------------|-----------------|-----------|
| 9 | Create a vendor with name = "Amazon Web Services" (already exists) | `POST /api/v1/vendors` | API returns 409 Conflict or 400 Bad Request with message "Vendor with this name already exists". UI shows error notification. | |
| 10 | Attempt to distribute an already-completed assessment | `POST /api/v1/assessments/{id}/distribute` | API returns 409 Conflict: "Cannot distribute assessment with status completed". UI shows error message. | |

### 18d: Double-Submit Prevention

| Step | Action | Route / API | Expected Result | Pass/Fail |
|------|--------|-------------|-----------------|-----------|
| 11 | On New Vendor form with valid data, rapidly click "Create" button twice | `POST /api/v1/vendors` | Only ONE vendor created. Button disables after first click (loading state). Second click is a no-op. No duplicate vendor in the database. | |
| 12 | On assessment distribute, rapidly click "Distribute" twice | `POST /api/v1/assessments/{id}/distribute` | Only one state transition occurs. Second call returns 409 (already distributed) or is blocked by UI. | |

### 18e: Page Refresh State Preservation

| Step | Action | Route / API | Expected Result | Pass/Fail |
|------|--------|-------------|-----------------|-----------|
| 13 | Navigate to vendor detail page. Hard refresh (Cmd+Shift+R / Ctrl+Shift+R) | `/vendors/{id}` | Page reloads and re-fetches data. All vendor data displays correctly. No "undefined" or missing data. User remains authenticated. | |
| 14 | Navigate to assessment detail page mid-review. Refresh. | `/assessments/{id}` | Assessment data reloads. Current review status preserved. No lost progress on server-side state. | |
| 15 | Apply filters on vendor list (tier=critical). Refresh page. | `/vendors?tier=critical` | URL preserves filter parameters. After refresh, filter is still applied (depends on URL-based state management). | |

### 18f: Session and Auth Edge Cases

| Step | Action | Route / API | Expected Result | Pass/Fail |
|------|--------|-------------|-----------------|-----------|
| 16 | Let JWT access token expire (wait or manually clear). Make an API call. | Any authenticated endpoint | API returns 401. Frontend detects and either auto-refreshes token (via refresh token) or redirects to login page. | |
| 17 | Manually corrupt the auth token in browser storage. Navigate. | Any page | Application detects invalid token. Redirects to login page. No sensitive data exposed. | |
| 18 | Login with correct email but wrong password | `POST /api/v1/auth/login` | API returns 401: "Invalid email or password". No information leakage about whether email exists. | |
| 19 | Login with non-existent email | `POST /api/v1/auth/login` | API returns 401: "Invalid email or password". Same error message as wrong password (no user enumeration). | |

---

## Execution Summary Template

| Scenario | Name | Steps | Passed | Failed | Blocked | Notes |
|----------|------|-------|--------|--------|---------|-------|
| 1 | First-Time Admin Setup | 16 | | | | |
| 2 | Bulk Vendor Import | 11 | | | | |
| 3 | Full Assessment Lifecycle | 18 | | | | |
| 4 | Evidence Upload & Analysis | 14 | | | | |
| 5 | CISO Dashboard Review | 11 | | | | |
| 6 | Alert Investigation & Resolution | 12 | | | | |
| 7 | Finding Remediation Workflow | 14 | | | | |
| 8 | Framework Exploration | 11 | | | | |
| 9 | Role-Based Access Control | 18 | | | | |
| 10 | Communication & Notification Flow | 10 | | | | |
| 11 | Report Generation | 10 | | | | |
| 12 | Admin User Management | 13 | | | | |
| 13 | Vendor 360-Degree View | 14 | | | | |
| 14 | AI Auto-Fill Assessment | 10 | | | | |
| 15 | Cross-Module Navigation Flow | 10 | | | | |
| 16 | Scoring Recalculation | 8 | | | | |
| 17 | Admin Audit Trail Verification | 12 | | | | |
| 18 | Error Handling & Edge Cases | 19 | | | | |
| **TOTAL** | | **231** | | | | |

---

## Pass Criteria

- **All scenarios**: 100% of steps must pass for scenario to pass
- **Overall**: All 18 scenarios must pass for Stage B sign-off
- **Blocking defects**: Any P0/P1 defect found during execution blocks Stage B sign-off
- **Non-blocking defects**: P2/P3 defects are logged as findings but do not block sign-off

## Defect Logging Format

For any failing step, log:

```
DEFECT-{NNN}
Scenario: {number} - {name}
Step: {step number}
Severity: P0 / P1 / P2 / P3
Summary: {one-line description}
Expected: {what should happen}
Actual: {what actually happened}
Screenshot: {path or link}
API Response: {status code and body if relevant}
```

---

*Document generated by Parikshika (QA Lead) as part of Velora TPRM v2.0 Phase 9 Full QA pipeline.*
