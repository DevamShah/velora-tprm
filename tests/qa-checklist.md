---
tags:
  - archeon
  - forgeon
  - product
  - product-velora
---

# Velora TPRM v2.0 — Stage A QA Checklist

> **Author**: Parikshika (QA Lead, Pantheon)
> **Date**: 2026-03-27
> **Status**: Active — Pre-Gate 5
> **Derived from**: PRD v1.0.0, Sprint Plan v2.0, Design System
> **Total Items**: 312
> **Test Users**: devam@velora.io (Admin), manager@velora.io (Manager), analyst@velora.io (Analyst), viewer@velora.io (Viewer)
> **Backend**: localhost:8000 | **Frontend**: localhost:3000

---

## Legend

| Category | Code |
|----------|------|
| Authentication | AUTH |
| Navigation | NAV |
| Vendor Module | VENDOR |
| Assessment Module | ASSESSMENT |
| Framework Module | FRAMEWORK |
| Scoring Module | SCORING |
| Evidence Module | EVIDENCE |
| Monitoring Module | MONITORING |
| Finding Module | FINDING |
| Reporting Module | REPORT |
| Communications Module | COMMS |
| Admin Module | ADMIN |
| Loading & Error States | LOADING |
| Role-Based Access Control | ROLE |
| Responsive & Visual | RESPONSIVE |
| API Direct | API |
| Security | SEC |
| Performance | PERF |

---

## 1. Authentication (AUTH)

- [ ] **AUTH-001** | AUTH | Login with devam@velora.io / devam123 | Expected: Successful login, redirect to /dashboard, JWT stored
- [ ] **AUTH-002** | AUTH | Login with manager@velora.io / manager123 | Expected: Successful login, redirect to /dashboard
- [ ] **AUTH-003** | AUTH | Login with analyst@velora.io / analyst123 | Expected: Successful login, redirect to /dashboard
- [ ] **AUTH-004** | AUTH | Login with viewer@velora.io / viewer123 | Expected: Successful login, redirect to /dashboard
- [ ] **AUTH-005** | AUTH | Login with correct email, wrong password | Expected: 401 error, descriptive toast "Invalid credentials", no redirect
- [ ] **AUTH-006** | AUTH | Login with non-existent email address | Expected: 401 error, generic message (no user enumeration), no redirect
- [ ] **AUTH-007** | AUTH | Login with empty email field | Expected: Client-side validation error, form not submitted
- [ ] **AUTH-008** | AUTH | Login with empty password field | Expected: Client-side validation error, form not submitted
- [ ] **AUTH-009** | AUTH | Login with both fields empty | Expected: Client-side validation errors on both fields
- [ ] **AUTH-010** | AUTH | Login with malformed email (no @) | Expected: Client-side validation "Invalid email format"
- [ ] **AUTH-011** | AUTH | Logout clears session completely | Expected: Token removed from storage, redirect to /login, /auth/me returns 401
- [ ] **AUTH-012** | AUTH | Visit /dashboard when not authenticated | Expected: Redirect to /login
- [ ] **AUTH-013** | AUTH | Visit /vendors when not authenticated | Expected: Redirect to /login
- [ ] **AUTH-014** | AUTH | Visit /admin/users when not authenticated | Expected: Redirect to /login
- [ ] **AUTH-015** | AUTH | Visit /assessments when not authenticated | Expected: Redirect to /login
- [ ] **AUTH-016** | AUTH | GET /auth/me returns correct user profile for admin | Expected: 200 with email, name, roles, permissions
- [ ] **AUTH-017** | AUTH | GET /auth/me returns correct user profile for analyst | Expected: 200 with analyst role and limited permissions
- [ ] **AUTH-018** | AUTH | Token refresh works after access token expires | Expected: New access token issued, old refresh token rotated
- [ ] **AUTH-019** | AUTH | Refresh with revoked refresh token fails | Expected: 401, redirect to login
- [ ] **AUTH-020** | AUTH | After logout, refresh token is invalidated | Expected: POST /auth/refresh returns 401
- [ ] **AUTH-021** | AUTH | Login form shows password visibility toggle | Expected: Eye icon toggles between masked and visible password
- [ ] **AUTH-022** | AUTH | Login button shows loading state during API call | Expected: Spinner or disabled state while authenticating
- [ ] **AUTH-023** | AUTH | Multiple rapid login clicks do not create duplicate requests | Expected: Button disabled after first click

---

## 2. Navigation (NAV)

- [ ] **NAV-001** | NAV | Sidebar link: Dashboard → /dashboard | Expected: Page loads, sidebar item highlighted
- [ ] **NAV-002** | NAV | Sidebar link: Vendors → /vendors | Expected: Page loads, sidebar item highlighted
- [ ] **NAV-003** | NAV | Sidebar link: Assessments → /assessments | Expected: Page loads, sidebar item highlighted
- [ ] **NAV-004** | NAV | Sidebar link: Frameworks → /frameworks | Expected: Page loads, sidebar item highlighted
- [ ] **NAV-005** | NAV | Sidebar link: Evidence → /evidence | Expected: Page loads, sidebar item highlighted
- [ ] **NAV-006** | NAV | Sidebar link: Monitoring → /monitoring | Expected: Page loads, sidebar item highlighted
- [ ] **NAV-007** | NAV | Sidebar link: Findings → /findings | Expected: Page loads, sidebar item highlighted
- [ ] **NAV-008** | NAV | Sidebar link: Reports → /reports | Expected: Page loads, sidebar item highlighted
- [ ] **NAV-009** | NAV | Sidebar link: Communications → /communications | Expected: Page loads, sidebar item highlighted
- [ ] **NAV-010** | NAV | Sidebar link: Users (Admin) → /admin/users | Expected: Page loads, sidebar item highlighted
- [ ] **NAV-011** | NAV | Sidebar link: Roles (Admin) → /admin/roles | Expected: Page loads, sidebar item highlighted
- [ ] **NAV-012** | NAV | Sidebar link: Audit Log (Admin) → /admin/audit-log | Expected: Page loads, sidebar item highlighted
- [ ] **NAV-013** | NAV | Sidebar link: Settings (Admin) → /admin/settings | Expected: Page loads, sidebar item highlighted
- [ ] **NAV-014** | NAV | Sidebar link: Integrations (Admin) → /admin/integrations | Expected: Page loads, sidebar item highlighted
- [ ] **NAV-015** | NAV | Zero 404 errors across all 25 routes | Expected: Every route renders a page, none show "Not Found"
- [ ] **NAV-016** | NAV | Breadcrumbs on /vendors show "Home > Vendors" | Expected: Correct breadcrumb path
- [ ] **NAV-017** | NAV | Breadcrumbs on /vendors/{id} show "Home > Vendors > {name}" | Expected: Vendor name in breadcrumb
- [ ] **NAV-018** | NAV | Breadcrumbs on /assessments/{id} show correct path | Expected: "Home > Assessments > {assessment name/id}"
- [ ] **NAV-019** | NAV | Breadcrumbs on /frameworks/{id} show correct path | Expected: "Home > Frameworks > {framework name}"
- [ ] **NAV-020** | NAV | Breadcrumbs on /monitoring/{id} show correct path | Expected: "Home > Monitoring > Alert #{id}"
- [ ] **NAV-021** | NAV | Breadcrumbs on /findings/{id} show correct path | Expected: "Home > Findings > {finding id}"
- [ ] **NAV-022** | NAV | Breadcrumbs on /admin/* pages show correct paths | Expected: "Home > Admin > {section}"
- [ ] **NAV-023** | NAV | Back button on /vendors/new returns to /vendors | Expected: Navigates back to vendor list
- [ ] **NAV-024** | NAV | Back button on /vendors/{id} returns to /vendors | Expected: Navigates back to vendor list
- [ ] **NAV-025** | NAV | Back button on /assessments/new returns to /assessments | Expected: Navigates back to assessment list
- [ ] **NAV-026** | NAV | Back button on /assessments/{id} returns to /assessments | Expected: Navigates back to assessment list
- [ ] **NAV-027** | NAV | Cmd+K opens command palette | Expected: Modal/overlay opens with search input
- [ ] **NAV-028** | NAV | Command palette search finds pages (e.g., type "vendor") | Expected: Vendor-related pages appear in results
- [ ] **NAV-029** | NAV | Command palette Escape key closes | Expected: Palette dismissed
- [ ] **NAV-030** | NAV | Browser back button works after navigation | Expected: Returns to previous page
- [ ] **NAV-031** | NAV | Browser forward button works after back | Expected: Goes forward to page
- [ ] **NAV-032** | NAV | Active sidebar item visually highlighted on all pages | Expected: Current page link has active styling
- [ ] **NAV-033** | NAV | Admin section collapsed for non-admin users | Expected: Admin sidebar group not visible to analyst/viewer
- [ ] **NAV-034** | NAV | Sidebar sections expand/collapse | Expected: Section groups toggle visibility
- [ ] **NAV-035** | NAV | Direct URL navigation to /vendors/{id} works | Expected: Page loads correctly without navigating through list first
- [ ] **NAV-036** | NAV | Direct URL navigation to /assessments/{id} works | Expected: Page loads correctly
- [ ] **NAV-037** | NAV | Navigating to non-existent route shows 404 page | Expected: Custom 404 page, not a crash

---

## 3. Vendor Module (VENDOR)

- [ ] **VENDOR-001** | VENDOR | Vendor list loads with seeded vendors (15+) | Expected: Table populated with vendor rows, no loading stuck
- [ ] **VENDOR-002** | VENDOR | Vendor list columns: name, tier, risk score, status, last assessed | Expected: All columns visible with correct data
- [ ] **VENDOR-003** | VENDOR | Search by vendor name (debounced input) | Expected: Results filter as user types, 300ms+ debounce
- [ ] **VENDOR-004** | VENDOR | Search with no matching results | Expected: Empty state message "No vendors match your search"
- [ ] **VENDOR-005** | VENDOR | Filter by status: Active | Expected: Only active vendors shown
- [ ] **VENDOR-006** | VENDOR | Filter by status: Inactive | Expected: Only inactive vendors shown
- [ ] **VENDOR-007** | VENDOR | Filter by status: Under Review | Expected: Only under-review vendors shown
- [ ] **VENDOR-008** | VENDOR | Filter by tier: Critical | Expected: Only critical-tier vendors shown
- [ ] **VENDOR-009** | VENDOR | Filter by tier: High | Expected: Only high-tier vendors shown
- [ ] **VENDOR-010** | VENDOR | Filter by tier: Medium | Expected: Only medium-tier vendors shown
- [ ] **VENDOR-011** | VENDOR | Filter by tier: Low | Expected: Only low-tier vendors shown
- [ ] **VENDOR-012** | VENDOR | Combined filters: status=Active + tier=Critical | Expected: Only vendors matching both criteria
- [ ] **VENDOR-013** | VENDOR | Clear all filters resets list | Expected: Full vendor list restored, filter controls cleared
- [ ] **VENDOR-014** | VENDOR | Sort by name ascending | Expected: Alphabetical A-Z order
- [ ] **VENDOR-015** | VENDOR | Sort by name descending | Expected: Alphabetical Z-A order
- [ ] **VENDOR-016** | VENDOR | Sort by risk score ascending | Expected: Lowest score first
- [ ] **VENDOR-017** | VENDOR | Sort by risk score descending | Expected: Highest score first
- [ ] **VENDOR-018** | VENDOR | Sort by tier | Expected: Sorted by tier severity
- [ ] **VENDOR-019** | VENDOR | Sort by last assessed date | Expected: Chronological order
- [ ] **VENDOR-020** | VENDOR | Pagination: default page size (10 or 25) | Expected: Correct number of rows per page
- [ ] **VENDOR-021** | VENDOR | Pagination: change to 10 per page | Expected: 10 rows shown, page count adjusts
- [ ] **VENDOR-022** | VENDOR | Pagination: change to 25 per page | Expected: 25 rows shown
- [ ] **VENDOR-023** | VENDOR | Pagination: change to 50 per page | Expected: 50 rows shown (or all if fewer)
- [ ] **VENDOR-024** | VENDOR | Pagination: next page works | Expected: Shows next set of vendors
- [ ] **VENDOR-025** | VENDOR | Pagination: previous page works | Expected: Shows previous set
- [ ] **VENDOR-026** | VENDOR | Pagination: page count display correct | Expected: "Page X of Y" accurate
- [ ] **VENDOR-027** | VENDOR | Click vendor row navigates to /vendors/{id} | Expected: Detail page loads for clicked vendor
- [ ] **VENDOR-028** | VENDOR | "Add Vendor" button navigates to /vendors/new | Expected: Create vendor form displayed
- [ ] **VENDOR-029** | VENDOR | Create vendor: fill all required fields, submit | Expected: Success toast, redirect to vendor list or detail, vendor appears in list
- [ ] **VENDOR-030** | VENDOR | Create vendor: submit with empty name | Expected: Validation error "Name is required"
- [ ] **VENDOR-031** | VENDOR | Create vendor: submit with empty required fields | Expected: Validation errors for each missing field
- [ ] **VENDOR-032** | VENDOR | Create vendor: duplicate name handling | Expected: Error or warning about existing vendor
- [ ] **VENDOR-033** | VENDOR | Vendor detail: overview tab renders all data | Expected: Name, tier, status, risk score, description, dates, tags visible
- [ ] **VENDOR-034** | VENDOR | Vendor detail: contacts tab shows contacts list | Expected: Contact cards/rows with name, email, role
- [ ] **VENDOR-035** | VENDOR | Vendor detail: timeline tab shows events | Expected: Chronological list of vendor events
- [ ] **VENDOR-036** | VENDOR | Vendor detail: tab switching works | Expected: Click each tab, content changes, no page reload
- [ ] **VENDOR-037** | VENDOR | Add contact dialog: open, fill fields, save | Expected: Dialog opens, new contact appears in list, success toast
- [ ] **VENDOR-038** | VENDOR | Add contact: empty required fields shows validation | Expected: Validation errors prevent submission
- [ ] **VENDOR-039** | VENDOR | Edit vendor: pre-populated form loads | Expected: All existing fields filled in
- [ ] **VENDOR-040** | VENDOR | Edit vendor: change name, save | Expected: Name updated, success toast, reflected on page
- [ ] **VENDOR-041** | VENDOR | Delete vendor: confirmation dialog appears | Expected: "Are you sure?" modal with vendor name
- [ ] **VENDOR-042** | VENDOR | Delete vendor: confirm → vendor deleted | Expected: Vendor removed, redirect to /vendors, vendor gone from list
- [ ] **VENDOR-043** | VENDOR | Delete vendor: cancel → no deletion | Expected: Dialog closes, vendor still exists
- [ ] **VENDOR-044** | VENDOR | Bulk import: upload valid CSV | Expected: File accepted, preview shown, import succeeds
- [ ] **VENDOR-045** | VENDOR | Bulk import: drag-and-drop CSV | Expected: Drop zone accepts file, preview renders
- [ ] **VENDOR-046** | VENDOR | Bulk import: preview shows first 5 rows | Expected: Table with CSV data preview
- [ ] **VENDOR-047** | VENDOR | Bulk import: results screen shows success/failure counts | Expected: "X created, Y failed" with details
- [ ] **VENDOR-048** | VENDOR | Bulk import: CSV with invalid rows shows per-row errors | Expected: Error details per failed row
- [ ] **VENDOR-049** | VENDOR | Bulk import: upload non-CSV file | Expected: Error "Invalid file type"
- [ ] **VENDOR-050** | VENDOR | Calculate tier button on vendor detail | Expected: Tier recalculated, badge updates, breakdown shown
- [ ] **VENDOR-051** | VENDOR | Tier badge colors: Critical=red | Expected: Red badge/pill
- [ ] **VENDOR-052** | VENDOR | Tier badge colors: High=orange | Expected: Orange badge/pill
- [ ] **VENDOR-053** | VENDOR | Tier badge colors: Medium=yellow | Expected: Yellow badge/pill
- [ ] **VENDOR-054** | VENDOR | Tier badge colors: Low=green | Expected: Green badge/pill
- [ ] **VENDOR-055** | VENDOR | Vendor list empty state (if all deleted) | Expected: "No vendors found" with "Add Vendor" CTA button

---

## 4. Assessment Module (ASSESSMENT)

- [ ] **ASSESS-001** | ASSESSMENT | Assessment list loads with 5+ seeded assessments | Expected: Table populated, no stuck loading
- [ ] **ASSESS-002** | ASSESSMENT | Assessment list columns: vendor, template, status, progress, dates | Expected: All columns render correctly
- [ ] **ASSESS-003** | ASSESSMENT | Status badges show correct colors (draft=grey, in_progress=blue, completed=green, etc.) | Expected: Color-coded status pills
- [ ] **ASSESS-004** | ASSESSMENT | Filter by status: Draft | Expected: Only draft assessments shown
- [ ] **ASSESS-005** | ASSESSMENT | Filter by status: In Progress | Expected: Only in-progress assessments
- [ ] **ASSESS-006** | ASSESSMENT | Filter by status: Completed | Expected: Only completed assessments
- [ ] **ASSESS-007** | ASSESSMENT | Filter by status: Under Review | Expected: Only under-review assessments
- [ ] **ASSESS-008** | ASSESSMENT | Filter by vendor name | Expected: Assessments for selected vendor only
- [ ] **ASSESS-009** | ASSESSMENT | Sort by date | Expected: Chronological ordering
- [ ] **ASSESS-010** | ASSESSMENT | Sort by status | Expected: Grouped by status
- [ ] **ASSESS-011** | ASSESSMENT | Click assessment row navigates to /assessments/{id} | Expected: Detail page loads
- [ ] **ASSESS-012** | ASSESSMENT | Create assessment wizard: Step 1 — select vendor | Expected: Vendor dropdown/search populated with active vendors
- [ ] **ASSESS-013** | ASSESSMENT | Create assessment wizard: Step 2 — select template | Expected: Template list shown with descriptions
- [ ] **ASSESS-014** | ASSESSMENT | Create assessment wizard: Step 3 — enter details and submit | Expected: Assessment created, success toast, redirect
- [ ] **ASSESS-015** | ASSESSMENT | Create assessment: skip required step | Expected: Cannot proceed without selecting vendor/template
- [ ] **ASSESS-016** | ASSESSMENT | Create assessment: back button between wizard steps | Expected: Returns to previous step with selections preserved
- [ ] **ASSESS-017** | ASSESSMENT | Assessment detail: overview tab shows status, dates, scores | Expected: All metadata visible, action buttons present
- [ ] **ASSESS-018** | ASSESSMENT | Assessment detail: questionnaire tab shows questions | Expected: Question list with response status indicators
- [ ] **ASSESS-019** | ASSESSMENT | Assessment detail: findings tab shows findings | Expected: Findings list (may be empty for new assessments)
- [ ] **ASSESS-020** | ASSESSMENT | Action button: Distribute (from draft) | Expected: Status transitions to "distributed", success toast
- [ ] **ASSESS-021** | ASSESSMENT | Action button: Submit (from in_progress) | Expected: Status transitions to "submitted"
- [ ] **ASSESS-022** | ASSESSMENT | Action button: Start Review (from submitted) | Expected: Status transitions to "under_review"
- [ ] **ASSESS-023** | ASSESSMENT | Action button: Complete (from under_review) | Expected: Status transitions to "completed", final score calculated
- [ ] **ASSESS-024** | ASSESSMENT | Action button: Cancel | Expected: Confirmation dialog, status transitions to "cancelled"
- [ ] **ASSESS-025** | ASSESSMENT | Invalid state transition blocked (e.g., complete from draft) | Expected: Button disabled or not shown for invalid transitions
- [ ] **ASSESS-026** | ASSESSMENT | Review queue (/assessments/review-queue) loads | Expected: Items needing analyst review listed
- [ ] **ASSESS-027** | ASSESSMENT | Review queue sorted by priority | Expected: Highest priority items first
- [ ] **ASSESS-028** | ASSESSMENT | Review queue: click item navigates to assessment detail | Expected: Assessment detail loads in review context
- [ ] **ASSESS-029** | ASSESSMENT | Assessment list pagination works | Expected: Page navigation functions correctly
- [ ] **ASSESS-030** | ASSESSMENT | Assessment empty state | Expected: "No assessments" with "Create Assessment" CTA

---

## 5. Framework Module (FRAMEWORK)

- [ ] **FW-001** | FRAMEWORK | Framework cards grid loads 4 frameworks | Expected: 4 cards rendered (SOC 2, ISO 27001, NIST CSF, PCI DSS or similar)
- [ ] **FW-002** | FRAMEWORK | Framework card shows name, version, clause count | Expected: Key info visible on each card
- [ ] **FW-003** | FRAMEWORK | Click framework card navigates to /frameworks/{id} | Expected: Framework detail page loads
- [ ] **FW-004** | FRAMEWORK | Framework detail: Clauses tab shows clause tree | Expected: Hierarchical tree of framework clauses
- [ ] **FW-005** | FRAMEWORK | Clause tree expand/collapse works | Expected: Click expands children, click again collapses
- [ ] **FW-006** | FRAMEWORK | Clause tree: multiple levels of nesting | Expected: Parent > Child > Grandchild structure renders
- [ ] **FW-007** | FRAMEWORK | Framework detail: Mappings tab shows cross-framework mappings | Expected: Mapping table/visualization loads
- [ ] **FW-008** | FRAMEWORK | Select a clause → shows mapped clauses in other frameworks | Expected: Related clauses highlighted or listed
- [ ] **FW-009** | FRAMEWORK | Framework detail: Controls tab shows unified controls | Expected: Control list with framework coverage indicators
- [ ] **FW-010** | FRAMEWORK | Tab switching on framework detail works | Expected: Each tab loads correct content
- [ ] **FW-011** | FRAMEWORK | Framework cards grid empty state (if no frameworks) | Expected: "No frameworks loaded" message
- [ ] **FW-012** | FRAMEWORK | Framework search/filter on cards page | Expected: Cards filter by search term if available

---

## 6. Scoring Module (SCORING)

- [ ] **SCORE-001** | SCORING | Score gauge renders on vendor detail page | Expected: Circular/radial gauge with numeric score
- [ ] **SCORE-002** | SCORING | Score gauge color reflects risk level (red/orange/yellow/green) | Expected: Appropriate color for score range
- [ ] **SCORE-003** | SCORING | Dimension chart (radar/spider) renders on vendor detail | Expected: Multi-axis chart showing dimension scores
- [ ] **SCORE-004** | SCORING | Dimension chart has labeled axes | Expected: Each dimension labeled (e.g., Technical, Organizational, Compliance)
- [ ] **SCORE-005** | SCORING | Score trend chart renders (line chart over time) | Expected: Historical scores plotted on timeline
- [ ] **SCORE-006** | SCORING | Score trend chart shows data points on hover | Expected: Tooltip with date and score value
- [ ] **SCORE-007** | SCORING | Recalculate score button on vendor detail | Expected: Score updates, gauge refreshes, success toast
- [ ] **SCORE-008** | SCORING | Portfolio summary on dashboard shows aggregate data | Expected: Average score, distribution, trend
- [ ] **SCORE-009** | SCORING | Score breakdown shows weighted dimensions | Expected: Each dimension with weight and score visible

---

## 7. Evidence Module (EVIDENCE)

- [ ] **EVID-001** | EVIDENCE | Evidence list page loads | Expected: Table/cards of uploaded evidence files
- [ ] **EVID-002** | EVIDENCE | Evidence list shows file name, type, upload date, status | Expected: All columns populated
- [ ] **EVID-003** | EVIDENCE | Upload dialog opens from "Upload" button | Expected: Modal with file drop zone
- [ ] **EVID-004** | EVIDENCE | File drop zone accepts drag-and-drop | Expected: File highlight on drag, upload on drop
- [ ] **EVID-005** | EVIDENCE | File upload via file picker works | Expected: Click browse, select file, upload starts
- [ ] **EVID-006** | EVIDENCE | Upload progress indicator shown | Expected: Progress bar or percentage during upload
- [ ] **EVID-007** | EVIDENCE | Upload completes with success toast | Expected: File appears in evidence list
- [ ] **EVID-008** | EVIDENCE | Upload invalid file type | Expected: Error message, file rejected
- [ ] **EVID-009** | EVIDENCE | Evidence detail drawer/page shows AI extractions | Expected: Extracted controls, findings, metadata displayed
- [ ] **EVID-010** | EVIDENCE | Control mappings display on evidence detail | Expected: Mapped controls listed with confidence scores
- [ ] **EVID-011** | EVIDENCE | Verify mapping button works | Expected: Mapping status changes to "verified"
- [ ] **EVID-012** | EVIDENCE | Reject mapping button works | Expected: Mapping status changes to "rejected"
- [ ] **EVID-013** | EVIDENCE | Evidence list pagination | Expected: Page navigation works
- [ ] **EVID-014** | EVIDENCE | Evidence list empty state | Expected: "No evidence uploaded" with upload CTA
- [ ] **EVID-015** | EVIDENCE | Filter evidence by type | Expected: Filtered list of matching evidence

---

## 8. Monitoring Module (MONITORING)

- [ ] **MON-001** | MONITORING | Alert list loads with 5+ seeded alerts | Expected: Table populated with alert rows
- [ ] **MON-002** | MONITORING | Alert list columns: vendor, priority, type, status, timestamp | Expected: All columns render
- [ ] **MON-003** | MONITORING | Priority badges: P0 (red), P1 (orange), P2 (yellow), P3 (blue), P4 (grey) | Expected: Correct colors per priority
- [ ] **MON-004** | MONITORING | Filter by priority: P0 | Expected: Only P0 alerts shown
- [ ] **MON-005** | MONITORING | Filter by priority: P1 | Expected: Only P1 alerts shown
- [ ] **MON-006** | MONITORING | Filter by status: Open | Expected: Only open alerts shown
- [ ] **MON-007** | MONITORING | Filter by status: Acknowledged | Expected: Only acknowledged alerts
- [ ] **MON-008** | MONITORING | Filter by status: Resolved | Expected: Only resolved alerts
- [ ] **MON-009** | MONITORING | Combined filters: priority + status | Expected: Both criteria applied
- [ ] **MON-010** | MONITORING | Click alert row navigates to /monitoring/{id} | Expected: Alert detail page loads
- [ ] **MON-011** | MONITORING | Alert detail shows full context (vendor, signals, timeline) | Expected: All alert data rendered
- [ ] **MON-012** | MONITORING | Acknowledge button on alert detail | Expected: Status changes to "acknowledged", success toast
- [ ] **MON-013** | MONITORING | Resolve button opens notes dialog | Expected: Modal with text area for resolution notes
- [ ] **MON-014** | MONITORING | Resolve with notes → alert resolved | Expected: Status changes to "resolved", notes saved
- [ ] **MON-015** | MONITORING | Suppress button works | Expected: Alert suppressed, success toast
- [ ] **MON-016** | MONITORING | Alert timeline shows event history | Expected: Chronological log of actions on alert
- [ ] **MON-017** | MONITORING | Rules tab on /monitoring shows alert rules | Expected: List of monitoring rules
- [ ] **MON-018** | MONITORING | Create alert rule works | Expected: New rule created, appears in rules list
- [ ] **MON-019** | MONITORING | Edit alert rule works | Expected: Rule updated, changes reflected
- [ ] **MON-020** | MONITORING | Delete alert rule with confirmation | Expected: Confirmation dialog, rule removed
- [ ] **MON-021** | MONITORING | Alert list pagination | Expected: Page navigation works
- [ ] **MON-022** | MONITORING | Alert list empty state | Expected: "No alerts" message

---

## 9. Finding Module (FINDING)

- [ ] **FIND-001** | FINDING | Finding list loads with seeded findings | Expected: Table populated
- [ ] **FIND-002** | FINDING | Finding list columns: title, vendor, severity, status, due date | Expected: All columns render
- [ ] **FIND-003** | FINDING | Severity badges: Critical (red), High (orange), Medium (yellow), Low (green), Info (blue) | Expected: Correct colors
- [ ] **FIND-004** | FINDING | Filter by severity: Critical | Expected: Only critical findings shown
- [ ] **FIND-005** | FINDING | Filter by severity: High | Expected: Only high findings
- [ ] **FIND-006** | FINDING | Filter by severity: Medium | Expected: Only medium findings
- [ ] **FIND-007** | FINDING | Filter by status: Open | Expected: Only open findings
- [ ] **FIND-008** | FINDING | Filter by status: In Remediation | Expected: Only in-remediation findings
- [ ] **FIND-009** | FINDING | Filter by status: Closed | Expected: Only closed findings
- [ ] **FIND-010** | FINDING | Combined filters: severity + status | Expected: Both criteria applied
- [ ] **FIND-011** | FINDING | Click finding row navigates to /findings/{id} | Expected: Finding detail loads
- [ ] **FIND-012** | FINDING | Finding detail: description, affected controls, guidance visible | Expected: All sections rendered
- [ ] **FIND-013** | FINDING | Finding detail: remediation actions list | Expected: Remediation steps displayed
- [ ] **FIND-014** | FINDING | Add remediation action works | Expected: Action added, appears in list
- [ ] **FIND-015** | FINDING | Close finding button works | Expected: Confirmation, status changes to "closed"
- [ ] **FIND-016** | FINDING | Close finding requires notes/reason | Expected: Cannot close without entering resolution
- [ ] **FIND-017** | FINDING | Finding list pagination | Expected: Page navigation works
- [ ] **FIND-018** | FINDING | Finding list empty state | Expected: "No findings" message
- [ ] **FIND-019** | FINDING | Sort by severity | Expected: Ordered by severity level
- [ ] **FIND-020** | FINDING | Sort by due date | Expected: Chronological order

---

## 10. Reporting & Dashboard Module (REPORT)

- [ ] **REPORT-001** | REPORT | Dashboard (/dashboard) loads with real aggregate data | Expected: All widgets populated, no placeholder text
- [ ] **REPORT-002** | REPORT | Dashboard stat cards show correct numbers | Expected: Vendor count, assessment count, finding count, risk score match backend data
- [ ] **REPORT-003** | REPORT | Risk heatmap renders | Expected: Color-coded matrix visible
- [ ] **REPORT-004** | REPORT | Risk heatmap cells are interactive (hover shows details) | Expected: Tooltip or popup on hover
- [ ] **REPORT-005** | REPORT | Vendor distribution donut chart renders | Expected: Donut/pie chart with tier distribution
- [ ] **REPORT-006** | REPORT | Donut chart shows legend | Expected: Legend with tier names and counts
- [ ] **REPORT-007** | REPORT | Trend line chart renders (risk over time) | Expected: Line chart with data points
- [ ] **REPORT-008** | REPORT | Trend chart has proper axis labels | Expected: X-axis: dates, Y-axis: score
- [ ] **REPORT-009** | REPORT | Top 10 vendors table shows data | Expected: 10 rows with vendor name, tier, score
- [ ] **REPORT-010** | REPORT | Top 10 vendors table sorted by risk (highest first) | Expected: Descending risk order
- [ ] **REPORT-011** | REPORT | Recent alerts feed shows latest alerts | Expected: 5+ recent alerts with priority badges
- [ ] **REPORT-012** | REPORT | Assessment pipeline bar/chart shows status distribution | Expected: Visual breakdown of assessment statuses
- [ ] **REPORT-013** | REPORT | Report list page (/reports) loads | Expected: Table of generated reports
- [ ] **REPORT-014** | REPORT | Generate report dialog opens | Expected: Modal with report type selection, date range, format
- [ ] **REPORT-015** | REPORT | Generate report: submit creates report | Expected: Report generation initiated, success toast
- [ ] **REPORT-016** | REPORT | Download generated report | Expected: File downloads (PDF or CSV)
- [ ] **REPORT-017** | REPORT | Report list empty state | Expected: "No reports generated" with generate CTA
- [ ] **REPORT-018** | REPORT | Dashboard widgets refresh on navigation back | Expected: Data is current, not stale
- [ ] **REPORT-019** | REPORT | Chart tooltips display on hover | Expected: Data values shown in tooltip

---

## 11. Communications Module (COMMS)

- [ ] **COMMS-001** | COMMS | Notifications tab loads on /communications | Expected: List of notifications rendered
- [ ] **COMMS-002** | COMMS | Read/unread styling visible | Expected: Unread = bold/highlighted, Read = normal weight
- [ ] **COMMS-003** | COMMS | Click notification marks it as read | Expected: Styling changes, unread count decreases
- [ ] **COMMS-004** | COMMS | "Mark all read" button works | Expected: All notifications become read, counter resets to 0
- [ ] **COMMS-005** | COMMS | Email templates tab loads | Expected: Template list with name, subject, last modified
- [ ] **COMMS-006** | COMMS | Email template preview works | Expected: Template content displayed
- [ ] **COMMS-007** | COMMS | Communication logs tab loads | Expected: Log entries with timestamps, recipients, status
- [ ] **COMMS-008** | COMMS | Header notification bell icon visible | Expected: Bell icon in header/toolbar
- [ ] **COMMS-009** | COMMS | Notification bell shows unread count badge | Expected: Numeric badge (e.g., "3") when unread exist
- [ ] **COMMS-010** | COMMS | Notification bell badge hidden when 0 unread | Expected: No badge or "0" not shown
- [ ] **COMMS-011** | COMMS | Click notification bell opens dropdown | Expected: Dropdown/popover with recent notifications
- [ ] **COMMS-012** | COMMS | Notification dropdown shows latest 5-10 notifications | Expected: Recent items with timestamps
- [ ] **COMMS-013** | COMMS | "View all" in notification dropdown navigates to /communications | Expected: Full communications page loads
- [ ] **COMMS-014** | COMMS | Notifications tab pagination | Expected: Page navigation for large notification lists
- [ ] **COMMS-015** | COMMS | Communication logs tab filtering by status | Expected: Filter by sent/failed/pending
- [ ] **COMMS-016** | COMMS | Tab switching on /communications works | Expected: Each tab loads correct content

---

## 12. Admin Module (ADMIN)

- [ ] **ADMIN-001** | ADMIN | User list (/admin/users) loads with seeded users | Expected: Table with user rows (4 test users minimum)
- [ ] **ADMIN-002** | ADMIN | User list columns: name, email, role, status, last login | Expected: All columns populated
- [ ] **ADMIN-003** | ADMIN | Invite user dialog opens | Expected: Modal with email, name, role fields
- [ ] **ADMIN-004** | ADMIN | Invite user: fill fields, submit | Expected: User created, appears in list, success toast
- [ ] **ADMIN-005** | ADMIN | Invite user: duplicate email handled | Expected: Error "Email already exists"
- [ ] **ADMIN-006** | ADMIN | Edit user: change role | Expected: Role updated, success toast
- [ ] **ADMIN-007** | ADMIN | Edit user: change name | Expected: Name updated, reflected in list
- [ ] **ADMIN-008** | ADMIN | Deactivate user | Expected: Confirmation dialog, user status changes to "inactive"
- [ ] **ADMIN-009** | ADMIN | Deactivated user cannot login | Expected: Login returns 401/403 for deactivated user
- [ ] **ADMIN-010** | ADMIN | Role list (/admin/roles) shows 8 default roles | Expected: 8 roles rendered with permission counts
- [ ] **ADMIN-011** | ADMIN | Role detail shows permissions matrix | Expected: Permission checkboxes/toggles visible
- [ ] **ADMIN-012** | ADMIN | Create custom role works | Expected: New role created, appears in list
- [ ] **ADMIN-013** | ADMIN | Create custom role with permissions | Expected: Selected permissions saved correctly
- [ ] **ADMIN-014** | ADMIN | Edit role permissions works | Expected: Permission changes saved
- [ ] **ADMIN-015** | ADMIN | Cannot delete default system roles | Expected: Delete disabled or error on default roles
- [ ] **ADMIN-016** | ADMIN | Audit log (/admin/audit-log) loads with entries | Expected: Log entries rendered with timestamp, user, action, resource
- [ ] **ADMIN-017** | ADMIN | Audit log: filter by action type | Expected: Filtered list of matching actions
- [ ] **ADMIN-018** | ADMIN | Audit log: filter by user | Expected: Only selected user's actions shown
- [ ] **ADMIN-019** | ADMIN | Audit log: filter by date range | Expected: Only entries within range
- [ ] **ADMIN-020** | ADMIN | Audit log: export functionality | Expected: CSV/JSON file downloads
- [ ] **ADMIN-021** | ADMIN | Audit log pagination | Expected: Page navigation works
- [ ] **ADMIN-022** | ADMIN | Settings: General tab renders | Expected: Organization name, timezone, language settings visible
- [ ] **ADMIN-023** | ADMIN | Settings: Scoring tab renders | Expected: Scoring model configuration visible
- [ ] **ADMIN-024** | ADMIN | Settings: Workflow tab renders | Expected: Workflow configuration options visible
- [ ] **ADMIN-025** | ADMIN | Settings: Notifications tab renders | Expected: Notification preferences visible
- [ ] **ADMIN-026** | ADMIN | Settings: save changes works | Expected: Settings persisted, success toast
- [ ] **ADMIN-027** | ADMIN | Settings: tab switching works | Expected: Each tab loads correct content
- [ ] **ADMIN-028** | ADMIN | Integrations (/admin/integrations) shows integration cards | Expected: Cards for available integrations
- [ ] **ADMIN-029** | ADMIN | Integration card shows status (connected/disconnected) | Expected: Visual status indicator
- [ ] **ADMIN-030** | ADMIN | Integration card configure button works | Expected: Configuration dialog or page opens

---

## 13. Loading & Error States (LOADING)

- [ ] **LOAD-001** | LOADING | /dashboard shows loading skeleton during API fetch | Expected: Skeleton placeholders visible before data loads
- [ ] **LOAD-002** | LOADING | /vendors shows loading skeleton during API fetch | Expected: Table skeleton visible
- [ ] **LOAD-003** | LOADING | /assessments shows loading skeleton during API fetch | Expected: Table skeleton visible
- [ ] **LOAD-004** | LOADING | /frameworks shows loading skeleton during API fetch | Expected: Card skeletons visible
- [ ] **LOAD-005** | LOADING | /evidence shows loading skeleton during API fetch | Expected: Skeleton visible
- [ ] **LOAD-006** | LOADING | /monitoring shows loading skeleton during API fetch | Expected: Table skeleton visible
- [ ] **LOAD-007** | LOADING | /findings shows loading skeleton during API fetch | Expected: Table skeleton visible
- [ ] **LOAD-008** | LOADING | /reports shows loading skeleton during API fetch | Expected: Skeleton visible
- [ ] **LOAD-009** | LOADING | /communications shows loading skeleton | Expected: Skeleton visible
- [ ] **LOAD-010** | LOADING | /admin/users shows loading skeleton | Expected: Table skeleton visible
- [ ] **LOAD-011** | LOADING | /admin/audit-log shows loading skeleton | Expected: Table skeleton visible
- [ ] **LOAD-012** | LOADING | Vendor detail page shows loading skeleton | Expected: Skeleton for all sections
- [ ] **LOAD-013** | LOADING | Assessment detail page shows loading skeleton | Expected: Skeleton for all sections
- [ ] **LOAD-014** | LOADING | API error on /vendors shows error toast, no crash | Expected: Toast message, page remains functional
- [ ] **LOAD-015** | LOADING | API error on /dashboard shows error toast, no crash | Expected: Toast or error boundary, not white screen
- [ ] **LOAD-016** | LOADING | API error on /assessments shows error state | Expected: Graceful degradation
- [ ] **LOAD-017** | LOADING | API error on /admin/users shows error state | Expected: Error message, retry option if available
- [ ] **LOAD-018** | LOADING | Network timeout (>10s) does not crash | Expected: Timeout message or retry, no infinite spinner
- [ ] **LOAD-019** | LOADING | API 500 error shows user-friendly message | Expected: "Something went wrong" not raw error
- [ ] **LOAD-020** | LOADING | API 403 error shows access denied message | Expected: "You don't have permission" message
- [ ] **LOAD-021** | LOADING | Empty state on /vendors when no vendors exist | Expected: "No vendors yet" with "Add Vendor" CTA
- [ ] **LOAD-022** | LOADING | Empty state on /assessments when no assessments | Expected: "No assessments" with "Create Assessment" CTA
- [ ] **LOAD-023** | LOADING | Empty state on /evidence when no evidence | Expected: "No evidence uploaded" with upload CTA
- [ ] **LOAD-024** | LOADING | Empty state on /monitoring when no alerts | Expected: "No alerts" message
- [ ] **LOAD-025** | LOADING | Empty state on /findings when no findings | Expected: "No findings" message
- [ ] **LOAD-026** | LOADING | Empty state on /reports when no reports | Expected: "No reports" with generate CTA
- [ ] **LOAD-027** | LOADING | Submit button disabled during form submission | Expected: No double-submit possible
- [ ] **LOAD-028** | LOADING | Loading indicators on all action buttons (distribute, resolve, etc.) | Expected: Spinner shown while API call in progress

---

## 14. Role-Based Access Control (ROLE)

### Admin (devam@velora.io)
- [ ] **ROLE-001** | ROLE | Admin sees all sidebar items including Admin section | Expected: Full sidebar with all 15+ links
- [ ] **ROLE-002** | ROLE | Admin can access /admin/users | Expected: Page loads with user management
- [ ] **ROLE-003** | ROLE | Admin can access /admin/roles | Expected: Page loads with role management
- [ ] **ROLE-004** | ROLE | Admin can access /admin/audit-log | Expected: Page loads with audit entries
- [ ] **ROLE-005** | ROLE | Admin can access /admin/settings | Expected: Page loads with settings
- [ ] **ROLE-006** | ROLE | Admin can access /admin/integrations | Expected: Page loads with integration cards
- [ ] **ROLE-007** | ROLE | Admin can create vendors | Expected: "Add Vendor" button visible, form works
- [ ] **ROLE-008** | ROLE | Admin can delete vendors | Expected: Delete button visible, deletion works
- [ ] **ROLE-009** | ROLE | Admin can create assessments | Expected: "Create Assessment" button visible
- [ ] **ROLE-010** | ROLE | Admin can manage users (invite, edit, deactivate) | Expected: All user management actions available
- [ ] **ROLE-011** | ROLE | Admin can export audit log | Expected: Export button visible and functional

### TPRM Manager (manager@velora.io)
- [ ] **ROLE-012** | ROLE | Manager sees management pages (vendors, assessments, frameworks) | Expected: Core module links visible
- [ ] **ROLE-013** | ROLE | Manager can create vendors | Expected: "Add Vendor" button visible and works
- [ ] **ROLE-014** | ROLE | Manager can create assessments | Expected: "Create Assessment" visible and works
- [ ] **ROLE-015** | ROLE | Manager can distribute assessments | Expected: Distribute button works
- [ ] **ROLE-016** | ROLE | Manager can complete assessments | Expected: Complete button works
- [ ] **ROLE-017** | ROLE | Manager can access reports | Expected: Report generation works
- [ ] **ROLE-018** | ROLE | Manager cannot access /admin/users | Expected: Redirect, 403, or sidebar link hidden
- [ ] **ROLE-019** | ROLE | Manager cannot access /admin/settings | Expected: Redirect or 403
- [ ] **ROLE-020** | ROLE | Manager cannot modify roles | Expected: Role management unavailable

### Risk Analyst (analyst@velora.io)
- [ ] **ROLE-021** | ROLE | Analyst sees analysis pages (vendors, assessments, evidence, findings) | Expected: Core analysis links visible
- [ ] **ROLE-022** | ROLE | Analyst can view vendors | Expected: Vendor list loads
- [ ] **ROLE-023** | ROLE | Analyst can view assessments | Expected: Assessment list loads
- [ ] **ROLE-024** | ROLE | Analyst can review assessment responses | Expected: Review queue accessible
- [ ] **ROLE-025** | ROLE | Analyst can add findings | Expected: Finding creation available
- [ ] **ROLE-026** | ROLE | Analyst cannot delete vendors | Expected: Delete button hidden or disabled
- [ ] **ROLE-027** | ROLE | Analyst cannot access admin pages | Expected: Admin sidebar section hidden
- [ ] **ROLE-028** | ROLE | Analyst cannot manage users | Expected: /admin/users inaccessible

### Viewer (viewer@velora.io)
- [ ] **ROLE-029** | ROLE | Viewer can see dashboard | Expected: Dashboard loads with data
- [ ] **ROLE-030** | ROLE | Viewer can see vendor list | Expected: Vendor list loads (read-only)
- [ ] **ROLE-031** | ROLE | Viewer cannot create vendors | Expected: "Add Vendor" button hidden or disabled
- [ ] **ROLE-032** | ROLE | Viewer cannot edit vendors | Expected: Edit button hidden or disabled
- [ ] **ROLE-033** | ROLE | Viewer cannot delete vendors | Expected: Delete button hidden or disabled
- [ ] **ROLE-034** | ROLE | Viewer cannot create assessments | Expected: "Create Assessment" hidden or disabled
- [ ] **ROLE-035** | ROLE | Viewer cannot upload evidence | Expected: Upload button hidden or disabled
- [ ] **ROLE-036** | ROLE | Viewer cannot resolve alerts | Expected: Action buttons hidden or disabled
- [ ] **ROLE-037** | ROLE | Viewer cannot access admin pages | Expected: Admin section not in sidebar
- [ ] **ROLE-038** | ROLE | Viewer can view reports | Expected: Report list loads (read-only)
- [ ] **ROLE-039** | ROLE | Viewer can view findings (read-only) | Expected: Finding detail loads, no action buttons
- [ ] **ROLE-040** | ROLE | Direct URL to /admin/users by viewer blocked | Expected: Redirect to dashboard or 403 page

---

## 15. Responsive & Visual (RESPONSIVE)

- [ ] **VIS-001** | RESPONSIVE | Sidebar collapses on narrow screens (<1024px) | Expected: Sidebar becomes icon-only or hamburger menu
- [ ] **VIS-002** | RESPONSIVE | Tables scroll horizontally on narrow screens | Expected: Horizontal scroll bar, no content truncation
- [ ] **VIS-003** | RESPONSIVE | Navy theme (#0A2540) applied to sidebar | Expected: Deep navy background, not black or grey
- [ ] **VIS-004** | RESPONSIVE | Sidebar text is legible against navy background | Expected: White or light text, sufficient contrast
- [ ] **VIS-005** | RESPONSIVE | All badge colors correct (tier, severity, priority, status) | Expected: Consistent color coding across all modules
- [ ] **VIS-006** | RESPONSIVE | Animations/transitions on page navigation | Expected: Smooth fade or slide transitions
- [ ] **VIS-007** | RESPONSIVE | Hover effects on interactive elements (buttons, rows, cards) | Expected: Visual feedback on hover
- [ ] **VIS-008** | RESPONSIVE | Focus states on form inputs | Expected: Visible focus ring/border on tab navigation
- [ ] **VIS-009** | RESPONSIVE | No visual overflow or clipping on any page | Expected: Content contained within boundaries
- [ ] **VIS-010** | RESPONSIVE | Modal/dialog overlays have backdrop | Expected: Dimmed background behind modals
- [ ] **VIS-011** | RESPONSIVE | Toast notifications position correctly (top-right or bottom-right) | Expected: Consistent positioning, auto-dismiss
- [ ] **VIS-012** | RESPONSIVE | Charts resize on window resize | Expected: Charts adapt to container width
- [ ] **VIS-013** | RESPONSIVE | Typography hierarchy consistent | Expected: H1 > H2 > H3 > body text sizing
- [ ] **VIS-014** | RESPONSIVE | Spacing and padding consistent across pages | Expected: Uniform margins, card padding
- [ ] **VIS-015** | RESPONSIVE | Icons render correctly (no broken/missing icons) | Expected: All icons visible, correct size
- [ ] **VIS-016** | RESPONSIVE | Form layouts responsive | Expected: Fields stack on narrow, side-by-side on wide
- [ ] **VIS-017** | RESPONSIVE | Dashboard widgets stack on narrow screens | Expected: Grid becomes single column
- [ ] **VIS-018** | RESPONSIVE | No horizontal scrollbar on full-width pages (desktop) | Expected: Content fits viewport
- [ ] **VIS-019** | RESPONSIVE | Dark text on light backgrounds, light text on dark backgrounds | Expected: Sufficient contrast ratios (WCAG AA)
- [ ] **VIS-020** | RESPONSIVE | Velora logo/branding visible in sidebar or header | Expected: Brand identity present

---

## 16. API Direct Tests (API)

- [ ] **API-001** | API | GET /health returns 200 | Expected: Health check passes
- [ ] **API-002** | API | POST /auth/login with valid credentials returns JWT | Expected: 200 with access_token and refresh_token
- [ ] **API-003** | API | POST /auth/login with invalid credentials returns 401 | Expected: 401 with error message
- [ ] **API-004** | API | GET /vendors without auth header returns 401 | Expected: 401 Unauthorized
- [ ] **API-005** | API | GET /vendors with valid token returns vendor list | Expected: 200 with paginated results
- [ ] **API-006** | API | POST /vendors with valid payload returns 201 | Expected: Created vendor object
- [ ] **API-007** | API | POST /vendors with invalid payload returns 422 | Expected: Validation error details (RFC 7807)
- [ ] **API-008** | API | GET /vendors/{invalid-id} returns 404 | Expected: 404 Not Found
- [ ] **API-009** | API | DELETE /vendors/{id} returns 204 | Expected: No content, vendor soft-deleted
- [ ] **API-010** | API | GET /assessments returns assessment list | Expected: 200 with paginated results
- [ ] **API-011** | API | POST /assessments creates assessment | Expected: 201 with assessment object
- [ ] **API-012** | API | POST /assessments/{id}/distribute transitions state | Expected: 200 with updated status
- [ ] **API-013** | API | GET /frameworks returns framework list | Expected: 200 with frameworks
- [ ] **API-014** | API | GET /frameworks/{id} returns framework detail with clauses | Expected: 200 with nested clause tree
- [ ] **API-015** | API | GET /monitoring/alerts returns alert list | Expected: 200 with paginated alerts
- [ ] **API-016** | API | POST /monitoring/alerts/{id}/acknowledge works | Expected: 200, status updated
- [ ] **API-017** | API | POST /monitoring/alerts/{id}/resolve works | Expected: 200, status updated
- [ ] **API-018** | API | GET /findings returns finding list | Expected: 200 with paginated findings
- [ ] **API-019** | API | GET /communications/notifications returns notifications | Expected: 200 with notification list
- [ ] **API-020** | API | POST /communications/notifications/mark-all-read works | Expected: 200, all marked read
- [ ] **API-021** | API | GET /admin/users returns user list (admin only) | Expected: 200 with users
- [ ] **API-022** | API | GET /admin/users with analyst token returns 403 | Expected: 403 Forbidden
- [ ] **API-023** | API | GET /admin/audit-log returns audit entries | Expected: 200 with paginated log
- [ ] **API-024** | API | POST /reports/generate creates report | Expected: 200/201 with report object
- [ ] **API-025** | API | GET /dashboard returns aggregate data | Expected: 200 with dashboard metrics
- [ ] **API-026** | API | POST /evidence/upload accepts file | Expected: 200/201 with evidence object
- [ ] **API-027** | API | GET /scoring/vendor/{id} returns score data | Expected: 200 with score breakdown
- [ ] **API-028** | API | POST /scoring/calculate triggers recalculation | Expected: 200 with updated scores
- [ ] **API-029** | API | Rate limiting returns 429 on excessive requests | Expected: 429 Too Many Requests after threshold
- [ ] **API-030** | API | CORS allows frontend origin | Expected: Access-Control headers present for localhost:3000

---

## 17. Security (SEC)

- [ ] **SEC-001** | SEC | Passwords not visible in API responses | Expected: No password field in /auth/me or /admin/users responses
- [ ] **SEC-002** | SEC | JWT tokens have reasonable expiry (15-60 min access, hours-days refresh) | Expected: Token exp claim within range
- [ ] **SEC-003** | SEC | SQL injection attempt in search field | Expected: No SQL error, input sanitized
- [ ] **SEC-004** | SEC | XSS attempt in vendor name field | Expected: Script tags escaped, not executed
- [ ] **SEC-005** | SEC | Cross-tenant data isolation | Expected: User cannot access another tenant's vendors/assessments
- [ ] **SEC-006** | SEC | API returns appropriate error codes (not stack traces) | Expected: RFC 7807 errors, no internal details leaked
- [ ] **SEC-007** | SEC | Sensitive headers not exposed (X-Powered-By, Server version) | Expected: Headers stripped or generic
- [ ] **SEC-008** | SEC | HTTPS/TLS enforced (if deployed) | Expected: HTTP redirects to HTTPS
- [ ] **SEC-009** | SEC | Authentication tokens stored securely (httpOnly cookies or secure storage) | Expected: Not in localStorage as plain text if cookies used
- [ ] **SEC-010** | SEC | Audit log captures all write operations | Expected: Create/update/delete actions logged with user and timestamp

---

## 18. Performance (PERF)

- [ ] **PERF-001** | PERF | Dashboard loads within 3 seconds | Expected: All widgets rendered under 3s
- [ ] **PERF-002** | PERF | Vendor list loads within 2 seconds | Expected: Table rendered under 2s
- [ ] **PERF-003** | PERF | Assessment list loads within 2 seconds | Expected: Table rendered under 2s
- [ ] **PERF-004** | PERF | Page navigation (sidebar click) completes within 1 second | Expected: New page visible under 1s
- [ ] **PERF-005** | PERF | Search debounce does not block UI | Expected: Typing remains smooth, no jank
- [ ] **PERF-006** | PERF | Charts render without blocking page interaction | Expected: Page interactive while charts load
- [ ] **PERF-007** | PERF | File upload for evidence does not freeze UI | Expected: Progress bar updates, page remains responsive
- [ ] **PERF-008** | PERF | Pagination changes load within 1 second | Expected: New page of results appears quickly
- [ ] **PERF-009** | PERF | No memory leaks on repeated navigation (check browser devtools) | Expected: Memory usage stable over time
- [ ] **PERF-010** | PERF | No console errors in browser devtools during normal usage | Expected: Clean console, zero red errors

---

## Execution Tracker

| Category | Total | Pass | Fail | Skip | Blocked |
|----------|-------|------|------|------|---------|
| AUTH | 23 | | | | |
| NAV | 37 | | | | |
| VENDOR | 55 | | | | |
| ASSESSMENT | 30 | | | | |
| FRAMEWORK | 12 | | | | |
| SCORING | 9 | | | | |
| EVIDENCE | 15 | | | | |
| MONITORING | 22 | | | | |
| FINDING | 20 | | | | |
| REPORT | 19 | | | | |
| COMMS | 16 | | | | |
| ADMIN | 30 | | | | |
| LOADING | 28 | | | | |
| ROLE | 40 | | | | |
| RESPONSIVE | 20 | | | | |
| API | 30 | | | | |
| SEC | 10 | | | | |
| PERF | 10 | | | | |
| **TOTAL** | **396** | | | | |

---

## Sign-Off

| Role | Agent | Status | Date |
|------|-------|--------|------|
| Maker | Parikshika (QA Lead) | CREATED | 2026-03-27 |
| Checker | Samikshon (QA Engineer) | PENDING | |
| Approver | Rudron (QA Gate) | PENDING | |
