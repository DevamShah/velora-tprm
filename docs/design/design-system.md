---
tags:
  - archeon
  - forgeon
  - product
  - product-velora
---

# Velora TPRM -- Design System & Screen Specifications

> **Product**: Velora TPRM (Third-Party Risk Management)
> **Author**: Rupika (UI/UX Product Designer, Pantheon)
> **Version**: 1.0.0
> **Date**: 2026-03-27
> **Status**: Draft -- Pending MCA Review
> **Classification**: Internal -- Design
> **Inputs**: PRD v1.0.0 (Darshika), HLD v1.0.0 (Rachnika), Devam's Design Brief

---

## Table of Contents

1. [Design Philosophy](#1-design-philosophy)
2. [Color Palette](#2-color-palette)
3. [Typography](#3-typography)
4. [Spacing and Grid](#4-spacing-and-grid)
5. [Elevation and Shadows](#5-elevation-and-shadows)
6. [Border Radius](#6-border-radius)
7. [Iconography](#7-iconography)
8. [Component Library](#8-component-library)
9. [Page Layouts and Key Screens](#9-page-layouts-and-key-screens)
10. [Interaction Patterns](#10-interaction-patterns)
11. [Accessibility](#11-accessibility)
12. [Responsive Behavior](#12-responsive-behavior)
13. [Motion and Animation](#13-motion-and-animation)
14. [Design Tokens Summary](#14-design-tokens-summary)

---

## 1. Design Philosophy

Velora TPRM is a premium, AI-first executive platform. Every design decision serves four principles:

**Principle 1: Executive Elegance.** This is a boardroom-grade product, not an admin panel. Generous whitespace, restrained color, and typographic hierarchy communicate authority and trust. The interface should feel like opening a well-made portfolio, not a cluttered control room.

**Principle 2: AI Transparency.** Every AI-generated output is visually distinguished, editable before confirmation, and traceable to sources. Users must always know what the machine inferred versus what a human verified. Confidence is shown, not hidden.

**Principle 3: Progressive Disclosure.** Complex workflows (assessment lifecycle, scoring configuration, evidence parsing) feel guided, not overwhelming. Information is layered: summary first, detail on demand, configuration behind intent. The analyst sees depth; the executive sees clarity.

**Principle 4: Consistent Rhythm.** Every module shares the same layout patterns, interaction models, component vocabulary, and visual grammar. A user who learns the vendor list can navigate findings, assessments, and monitoring without relearning the interface.

---

## 2. Color Palette

### 2.1 Primary Colors

The primary palette uses a refined indigo-to-deep-teal spectrum that conveys security, intelligence, and premium positioning. Indigo anchors the brand; teal provides warmth and differentiation from commodity blue SaaS products.

| Token | Hex | Usage |
|-------|-----|-------|
| `primary-900` | `#1B1F4B` | Sidebar background, darkest brand anchor |
| `primary-800` | `#252A6B` | Sidebar hover states, deep headers |
| `primary-700` | `#2F3688` | Primary button background, active navigation |
| `primary-600` | `#3B44A6` | Primary button hover, link active state |
| `primary-500` | `#4A54C4` | Primary brand color, default links, active accents |
| `primary-400` | `#6B74D4` | Icon accents, secondary interactive elements |
| `primary-300` | `#8E95E0` | Tag backgrounds, light interactive highlights |
| `primary-200` | `#B5BAEC` | Hover backgrounds, subtle highlights |
| `primary-100` | `#DCDFF5` | Light badge backgrounds, notification dots |
| `primary-50` | `#F0F1FA` | Page section backgrounds, selected row tint |

### 2.2 Secondary / Accent Colors

A warm teal-gold accent pair provides visual warmth and is used sparingly for emphasis and premium calls-to-action.

| Token | Hex | Usage |
|-------|-----|-------|
| `accent-teal-700` | `#0F5B5E` | Accent button background |
| `accent-teal-600` | `#147377` | Accent button hover |
| `accent-teal-500` | `#1A9199` | Accent links, secondary CTAs |
| `accent-teal-400` | `#3AB4BC` | Accent icon, subtle highlight |
| `accent-teal-100` | `#D4F0F2` | Accent badge background |
| `accent-teal-50` | `#EDF9FA` | Accent section background |
| `accent-gold-600` | `#9A7B2F` | Premium badge outline, tier indicator |
| `accent-gold-500` | `#BF9B3B` | Star ratings, premium iconography |
| `accent-gold-400` | `#D4B44E` | Hover state for gold accents |
| `accent-gold-100` | `#F5EDCF` | Gold badge background |

### 2.3 Semantic Colors

| Token | Hex | Usage |
|-------|-----|-------|
| `success-700` | `#15613C` | Success text on light backgrounds |
| `success-600` | `#1A7A4B` | Success icon color |
| `success-500` | `#22A05E` | Success badge, positive indicators |
| `success-100` | `#D4F5E2` | Success background tint |
| `success-50` | `#EDFBF3` | Success row/card background |
| `warning-700` | `#7A5A0B` | Warning text on light backgrounds |
| `warning-600` | `#9A7112` | Warning icon color |
| `warning-500` | `#C4901A` | Warning badge, caution indicators |
| `warning-100` | `#FDF0CC` | Warning background tint |
| `warning-50` | `#FEF8E8` | Warning row/card background |
| `error-700` | `#8B1A1A` | Error text on light backgrounds |
| `error-600` | `#B02424` | Error icon color |
| `error-500` | `#D93636` | Error badge, destructive actions |
| `error-100` | `#FCDCDC` | Error background tint |
| `error-50` | `#FEF0F0` | Error row/card background |
| `info-700` | `#1A4B7A` | Info text on light backgrounds |
| `info-600` | `#2264A0` | Info icon color |
| `info-500` | `#2D82C7` | Info badge, informational indicators |
| `info-100` | `#D4E8F7` | Info background tint |
| `info-50` | `#EDF5FC` | Info row/card background |

### 2.4 Risk Tier Colors

Each risk tier has a distinct color. Colors are chosen for instant visual parsing and color-blind accessibility (each tier also uses a distinct shape/pattern -- see Section 11).

| Tier | Badge Hex | Background Hex | Text Hex | Shape Marker |
|------|-----------|----------------|----------|-------------|
| **Critical** | `#D93636` | `#FEF0F0` | `#8B1A1A` | Double diamond |
| **High** | `#E67A1A` | `#FEF4E8` | `#7A4009` | Triangle up |
| **Medium** | `#C4901A` | `#FEF8E8` | `#7A5A0B` | Square |
| **Low** | `#22A05E` | `#EDFBF3` | `#15613C` | Circle |
| **Very Low** | `#2D82C7` | `#EDF5FC` | `#1A4B7A` | Rounded square |

### 2.5 Confidence Level Colors

| Level | Badge Hex | Background Hex | Text Hex | Dot Pattern |
|-------|-----------|----------------|----------|-------------|
| **High** (>85%) | `#22A05E` | `#EDFBF3` | `#15613C` | 3 filled dots |
| **Medium** (60-85%) | `#C4901A` | `#FEF8E8` | `#7A5A0B` | 2 filled + 1 empty dot |
| **Low** (<60%) | `#D93636` | `#FEF0F0` | `#8B1A1A` | 1 filled + 2 empty dots |

### 2.6 AI Indicator Colors

| State | Badge Hex | Background Hex | Border Hex |
|-------|-----------|----------------|------------|
| **AI-generated** | `#7B61FF` | `#F3F0FF` | `#D4CCFF` |
| **AI-assisted** | `#4A54C4` | `#F0F1FA` | `#DCDFF5` |
| **Human-verified** | `#22A05E` | `#EDFBF3` | `#B8E6CC` |
| **Needs review** | `#C4901A` | `#FEF8E8` | `#F0D88A` |

### 2.7 Neutral Grays

| Token | Hex | Usage |
|-------|-----|-------|
| `gray-950` | `#0D0F1C` | Primary text, headings |
| `gray-900` | `#1A1D2E` | Body text |
| `gray-800` | `#2A2E42` | Secondary text, strong labels |
| `gray-700` | `#3E4359` | Tertiary text |
| `gray-600` | `#555B73` | Placeholder text, muted labels |
| `gray-500` | `#6E7590` | Disabled text, icons |
| `gray-400` | `#8C92AA` | Subtle icons, dividers |
| `gray-300` | `#AEB3C7` | Borders, separators |
| `gray-200` | `#D0D4E2` | Input borders, table lines |
| `gray-150` | `#DFE2EC` | Card borders |
| `gray-100` | `#ECEEF5` | Dividers, subtle separators |
| `gray-75` | `#F2F3F8` | Table row alternate, subtle background |
| `gray-50` | `#F7F8FB` | Page background, sidebar hover |
| `gray-25` | `#FBFBFD` | Card background, input background |
| `white` | `#FFFFFF` | Primary surface, content area background |

---

## 3. Typography

### 3.1 Font Families

| Role | Family | Fallback Stack | Rationale |
|------|--------|----------------|-----------|
| **Heading** | `Inter` | `-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif` | Clean, authoritative, excellent at display sizes. Variable font with optical sizing for premium rendering. |
| **Body** | `Inter` | `-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif` | Legible at small sizes, harmonizes with headings. x-height optimized for data-dense layouts. |
| **Monospace** | `JetBrains Mono` | `'SF Mono', 'Fira Code', 'Cascadia Code', monospace` | Used for scores, IDs, code snippets, configuration editors. Distinguishable characters (0/O, 1/l). |

### 3.2 Type Scale

Based on a 1.250 ratio (Major Third) with a 16px base, providing clear hierarchy without excessive size jumps.

| Token | Size | Weight | Line Height | Letter Spacing | Usage |
|-------|------|--------|-------------|----------------|-------|
| `display-lg` | 36px / 2.25rem | 700 | 44px / 1.22 | -0.02em | Dashboard hero metrics (portfolio risk score) |
| `display-sm` | 30px / 1.875rem | 700 | 38px / 1.27 | -0.015em | Page titles |
| `heading-h1` | 24px / 1.5rem | 600 | 32px / 1.33 | -0.01em | Section headers |
| `heading-h2` | 20px / 1.25rem | 600 | 28px / 1.40 | -0.005em | Card headers, modal titles |
| `heading-h3` | 17px / 1.0625rem | 600 | 24px / 1.41 | 0 | Sub-section headers, table group headers |
| `heading-h4` | 15px / 0.9375rem | 600 | 22px / 1.47 | 0 | Widget titles, tab labels |
| `body-lg` | 16px / 1rem | 400 | 24px / 1.5 | 0 | Primary body text, descriptions |
| `body-md` | 14px / 0.875rem | 400 | 20px / 1.43 | 0 | Table cells, form labels, secondary body |
| `body-sm` | 13px / 0.8125rem | 400 | 18px / 1.38 | 0.005em | Metadata, timestamps, hints |
| `caption` | 12px / 0.75rem | 400 | 16px / 1.33 | 0.01em | Badge labels, chart labels, footnotes |
| `overline` | 11px / 0.6875rem | 600 | 16px / 1.45 | 0.08em | Overline labels, section dividers (uppercase) |
| `mono-md` | 14px / 0.875rem | 400 | 20px / 1.43 | 0 | Risk scores, vendor IDs, config values |
| `mono-sm` | 12px / 0.75rem | 400 | 18px / 1.5 | 0 | Evidence hashes, timestamps in logs |

### 3.3 Font Weight Definitions

| Weight | Value | Usage |
|--------|-------|-------|
| Regular | 400 | Body text, table cells, descriptions |
| Medium | 500 | Emphasized body text, active navigation items, form values |
| Semibold | 600 | All headings, button labels, table headers, badges |
| Bold | 700 | Display metrics only (dashboard hero numbers) |

### 3.4 Responsive Typography Adjustments

| Breakpoint | Adjustment |
|-----------|------------|
| Desktop (1280px+) | Full type scale as defined |
| Tablet (768px-1279px) | `display-lg` reduces to 30px, `display-sm` to 24px. Body sizes unchanged. |
| Mobile (< 768px) | `display-lg` reduces to 24px, `display-sm` to 20px, `heading-h1` to 20px. Minimum touch target: 44px. |

---

## 4. Spacing and Grid

### 4.1 Spacing Scale (8px Base)

| Token | Value | Usage |
|-------|-------|-------|
| `space-0` | 0px | Reset |
| `space-px` | 1px | Borders |
| `space-0.5` | 2px | Micro adjustments (icon-to-text gap inside badges) |
| `space-1` | 4px | Inner padding for badges, chips |
| `space-1.5` | 6px | Tight internal gaps |
| `space-2` | 8px | Default icon-to-label gap, compact padding |
| `space-3` | 12px | Small component internal padding |
| `space-4` | 16px | Standard component padding, form field gap |
| `space-5` | 20px | Medium section padding |
| `space-6` | 24px | Card internal padding, section gaps |
| `space-8` | 32px | Between card groups, section dividers |
| `space-10` | 40px | Major section separation |
| `space-12` | 48px | Page-level section gaps |
| `space-16` | 64px | Hero area padding |
| `space-20` | 80px | Page top padding |

### 4.2 Page Layout Grid

```
Desktop (1280px+):
+----------------------------------------------------------+
| Top Bar (56px height)                                    |
+----------+-----------------------------------------------+
| Sidebar  | Main Content Area                             |
| 240px    | Fluid (min 960px, max 1440px, centered)       |
| (coll:   |                                               |
|  64px)   | Content padding: 32px                         |
|          |                                               |
| Fixed    | Grid: 12 columns                              |
| left     | Column gap: 24px                              |
|          | Max content width: 1440px                     |
+----------+-----------------------------------------------+
```

**Sidebar behavior:**
- Expanded: 240px wide. Shows icon + label for each navigation item.
- Collapsed: 64px wide. Shows icon only with tooltip on hover.
- Toggle via chevron at bottom of sidebar or keyboard shortcut (`[`).
- Collapsed state persists in user preference.

**Content area grid:**
- 12-column fluid grid with 24px gutters.
- Dashboard widgets snap to grid: full-width (12 cols), half (6 cols), third (4 cols), quarter (3 cols).
- Detail pages use an asymmetric layout: primary content (8 cols) + contextual sidebar (4 cols).

### 4.3 Responsive Breakpoints

| Token | Min Width | Layout Change |
|-------|-----------|---------------|
| `breakpoint-xl` | 1440px | Max content width, centered |
| `breakpoint-lg` | 1280px | Full desktop layout |
| `breakpoint-md` | 1024px | Sidebar collapses to 64px by default |
| `breakpoint-sm` | 768px | Sidebar becomes overlay drawer, tables become card lists |
| `breakpoint-xs` | 480px | Single column, simplified dashboards |

---

## 5. Elevation and Shadows

A premium shadow system using soft, layered shadows with a subtle cool tint (matching the indigo primary). No harsh or heavy shadows.

| Token | CSS Value | Usage |
|-------|-----------|-------|
| `shadow-xs` | `0 1px 2px 0 rgba(27, 31, 75, 0.04)` | Subtle lift for buttons in default state |
| `shadow-sm` | `0 1px 3px 0 rgba(27, 31, 75, 0.06), 0 1px 2px -1px rgba(27, 31, 75, 0.04)` | Cards at rest, input focus ring outer |
| `shadow-md` | `0 4px 8px -2px rgba(27, 31, 75, 0.06), 0 2px 4px -2px rgba(27, 31, 75, 0.04)` | Elevated cards, hovered cards |
| `shadow-lg` | `0 12px 24px -4px rgba(27, 31, 75, 0.08), 0 4px 8px -4px rgba(27, 31, 75, 0.03)` | Dropdowns, popovers, floating toolbars |
| `shadow-xl` | `0 20px 40px -8px rgba(27, 31, 75, 0.10), 0 8px 16px -4px rgba(27, 31, 75, 0.04)` | Modals, command palette |
| `shadow-2xl` | `0 32px 64px -12px rgba(27, 31, 75, 0.14)` | Full-page overlays, onboarding wizard |
| `shadow-inner` | `inset 0 1px 2px 0 rgba(27, 31, 75, 0.05)` | Inset inputs, pressed button state |
| `shadow-ring` | `0 0 0 3px rgba(74, 84, 196, 0.15)` | Focus ring for keyboard navigation |

---

## 6. Border Radius

| Token | Value | Usage |
|-------|-------|-------|
| `radius-none` | 0px | Full-bleed elements |
| `radius-sm` | 4px | Badges, chips, small tags |
| `radius-md` | 6px | Buttons, inputs, select dropdowns |
| `radius-lg` | 8px | Cards, table containers, popovers |
| `radius-xl` | 12px | Modals, large cards, wizard panels |
| `radius-2xl` | 16px | Command palette, onboarding panels |
| `radius-full` | 9999px | Avatars, status dots, pill badges |

---

## 7. Iconography

| Property | Specification |
|----------|---------------|
| Library | Lucide Icons (consistent with shadcn/ui ecosystem) |
| Default size | 20px (matches `body-md` optical center) |
| Small size | 16px (table cells, badges, inline indicators) |
| Large size | 24px (navigation sidebar, empty states) |
| Stroke weight | 1.75px (slightly heavier than Lucide default 1.5px for clarity at small sizes) |
| Color | Inherits text color by default; `gray-500` for decorative, `primary-500` for interactive |
| Touch target | Minimum 36px for desktop, 44px for touch devices |

Module-specific icons (sidebar navigation):

| Module | Icon | Description |
|--------|------|-------------|
| Dashboard | `LayoutDashboard` | Grid-style overview |
| Vendors | `Building2` | Building representing organizations |
| Assessments | `ClipboardCheck` | Clipboard with checkmark |
| Evidence | `FileSearch` | Document with magnifier |
| Monitoring | `RadarIcon` | Radar sweep for continuous surveillance |
| Findings | `AlertTriangle` | Triangle alert for issues |
| Reports | `BarChart3` | Analytics chart |
| Frameworks | `Library` | Structured library |
| Admin | `Settings` | Configuration gear |
| Portal | `ExternalLink` | External-facing link |

---

## 8. Component Library

### 8.1 Navigation

#### Global Sidebar

```
+-----------------------------------------------------+
| EXPANDED (240px)              | COLLAPSED (64px)     |
+-----------------------------------------------------+
| [Velora Logo + Wordmark]      | [V Logo]             |
| 32px top padding              | 32px top padding     |
|                               |                      |
| -- MAIN ---                   |                      |
| [icon] Dashboard              | [icon]               |
| [icon] Vendors          (42)  | [icon] (42)          |
| [icon] Assessments       (8)  | [icon] (8)           |
| [icon] Evidence               | [icon]               |
| [icon] Monitoring       (3!)  | [icon] (3!)          |
| [icon] Findings         (12)  | [icon] (12)          |
| [icon] Reports                | [icon]               |
|                               |                      |
| -- CONFIGURE ---              |                      |
| [icon] Frameworks             | [icon]               |
| [icon] Admin                  | [icon]               |
|                               |                      |
| -------(spacer)--------       |                      |
|                               |                      |
| [icon] Help & Docs            | [icon]               |
| [avatar] Anya Kohli    v     | [avatar]             |
|   Role: TPRM Manager         |                      |
|   Org: FinCorp Inc            |                      |
| [<< collapse]                 | [>> expand]          |
+-----------------------------------------------------+
```

**States:**
- **Default**: `gray-400` icon + `gray-700` label on `primary-900` background
- **Hover**: `gray-200` icon + `white` label on `primary-800` background; 200ms transition
- **Active**: `white` icon + `white` label on `primary-700` background; left 3px accent border in `accent-teal-400`
- **Badge counts**: `caption` size, `white` text on `primary-500` rounded pill (right-aligned). Alert badges (monitoring/findings) use `error-500` background.
- **Collapsed tooltips**: On icon hover, tooltip appears to the right with module name + count. Uses `shadow-lg`, `gray-950` background, `white` text, `radius-md`.

#### Top Bar

```
+------------------------------------------------------------------------+
| [Breadcrumb: Dashboard > Vendors > Acme Corp]     [Cmd+K] [Bell] [?]  |
+------------------------------------------------------------------------+
```

- Height: 56px
- Background: `white` with 1px `gray-100` bottom border
- Breadcrumb: `body-sm`, `gray-600` for path segments, `gray-900` for current (last) segment, `/` separator in `gray-400`
- Right section: Command palette trigger (`Cmd+K` shown in `gray-300` border pill), notification bell (with red dot if unread), help icon
- On scroll, top bar gains `shadow-sm` for subtle elevation cue

#### Breadcrumbs

- Pattern: `Module > Page > Sub-page > Detail`
- Separator: chevron-right icon, 12px, `gray-400`
- Path links: `body-sm`, `gray-600`, underline on hover
- Current (last) segment: `body-sm`, `gray-900`, font-weight 500, no link
- Truncation: If breadcrumb exceeds 4 levels, middle segments collapse to `...` with dropdown on click
- Example: `Vendors > Acme Corp > Assessment #214 > Review Queue`

#### Command Palette (Cmd+K)

```
+------------------------------------------------------+
| [Search icon]  Search vendors, actions, pages...     |
|------------------------------------------------------|
| RECENT                                               |
|   [Building] Acme Corp                     Vendor    |
|   [Clipboard] Assessment #214              Assessment|
|                                                      |
| ACTIONS                                              |
|   [Plus] Add new vendor                    Cmd+N     |
|   [Clipboard] Start assessment             Cmd+Shift+A|
|   [FileText] Generate report               Cmd+R     |
|                                                      |
| NAVIGATION                                           |
|   [LayoutDashboard] Dashboard              Cmd+1     |
|   [Building2] Vendor List                  Cmd+2     |
|   [Settings] Admin Settings                          |
+------------------------------------------------------+
```

- Overlay: centered horizontally, 120px from top, 560px wide, max 480px tall
- Background: `white`, `radius-2xl`, `shadow-2xl`
- Backdrop: `rgba(13, 15, 28, 0.5)` with backdrop-blur 8px
- Search input: no border, 48px height, `heading-h3` size, `gray-950` text, `gray-500` placeholder
- Result groups: `overline` style headers in `gray-600`
- Result rows: 40px height, `body-md` name, `caption` type tag right-aligned in `gray-500`
- Hover: `primary-50` background
- Active/selected: `primary-100` background with `primary-500` left 2px border
- Keyboard navigation: arrow keys move selection, Enter activates, Escape closes
- Type-ahead: results filter live as user types, 100ms debounce

### 8.2 Data Display

#### Data Tables

The primary data presentation pattern. All list pages use this component.

```
+------------------------------------------------------------------------+
| [Filter icon] Filters (3)  | [Search input]    | [Column icon] [Export]|
|------------------------------------------------------------------------|
| [ ] | Vendor Name ^    | Risk Score | Tier     | Status    | Last Assess|
|------------------------------------------------------------------------|
| [ ] | Acme Corp        | 78 [HIGH]  | Tier 1   | Active    | 12 Mar 26  |
|     | acmecorp.com     |            | Critical | [3 findings]          |
|------------------------------------------------------------------------|
| [ ] | CloudSync Ltd    | 42 [MED]   | Tier 2   | Active    | 08 Feb 26  |
|     | cloudsync.io     |            | Medium   | [0 findings]          |
|------------------------------------------------------------------------|
| ... |                  |            |          |           |            |
|------------------------------------------------------------------------|
| Showing 1-25 of 420 vendors          | [< Prev] [1] [2] ... [17] [Next >]|
+------------------------------------------------------------------------+
```

**Structure:**
- Container: `white` background, `radius-lg`, `shadow-sm`, 1px `gray-150` border
- Header row: `gray-75` background, `body-sm` text, `gray-800` color, font-weight 600, 44px height
- Data rows: `white` background, 56px height (accommodates two-line cells), 1px `gray-100` bottom border
- Alternating rows: optional (`gray-75` alternate), off by default for cleaner look
- Row hover: `primary-50` background, 150ms transition
- Selected row: `primary-100` background with `primary-500` left 3px border
- Cell text: `body-md`, `gray-900` for primary data, `body-sm` `gray-600` for secondary line

**Sort behavior:** Click column header to sort. Active sort column shows arrow indicator and `primary-500` text color. Shift+click for multi-column sort.

**Filter bar:**
- Positioned above table header row
- Filter chips: `radius-full`, `gray-75` background, `gray-800` text, `body-sm`, 32px height
- Active filter chip: `primary-50` background, `primary-700` text, `primary-200` border
- Filter dropdown: `shadow-lg`, `white` background, `radius-lg`, max 320px wide
- Search-within-filter for columns with many values (e.g., vendor names)

**Bulk actions toolbar:** Appears when 1+ rows selected. Fixed to top of table. `primary-900` background, `white` text. Actions: "Assign," "Export," "Change status," "Delete" (red). Shows count: "3 vendors selected."

**Pagination:** Right-aligned below table. `body-sm` text. Showing `{start}-{end} of {total}`. Page buttons: 32px square, `radius-md`, `gray-100` default, `primary-500` active.

**Row expansion:** Clicking the expand chevron (right side of row or double-click row) expands an inline detail panel below the row, 1px `gray-100` top border, `gray-50` background, `space-6` padding. Contains quick-view summary.

**Empty state:** Centered in table body area. Illustration (line-art style, `gray-300` tone). `heading-h3` title. `body-md` `gray-600` description. Primary action button. Example: "No vendors yet. Import your vendor portfolio to get started." + [Import Vendors] button.

#### Risk Score Badge

A compact, color-coded badge displaying the numeric risk score and tier label.

```
  +------------------------+
  | [shape] 78  HIGH       |
  +------------------------+
```

- Layout: inline-flex, 28px height, `radius-full`, `space-2` horizontal padding
- Score number: `mono-md`, font-weight 600
- Tier label: `caption`, font-weight 600, uppercase
- Shape marker: 8px, positioned before score number (see Risk Tier Colors in Section 2.4)
- Color scheme: uses Risk Tier Colors (text color on background tint)
- Sizes: `sm` (24px height, `mono-sm` + `caption`) for table cells, `md` (28px) default, `lg` (36px, `body-md` + `body-sm`) for vendor profile header

#### Confidence Indicators

```
  High:    [*][*][*]  HIGH    96%
  Medium:  [*][*][ ]  MEDIUM  74%
  Low:     [*][ ][ ]  LOW     43%
```

- Dot pattern: 3 circles, 6px each, 3px gap
- Filled dot: uses confidence level color (badge hex)
- Empty dot: `gray-200`
- Label: `caption`, font-weight 600, uppercase, uses confidence level text color
- Percentage: `mono-sm`, `gray-700`
- Tooltip on hover: "Confidence: 96%. Based on: SOC 2 Type II report (primary), vendor questionnaire response (corroborating), SecurityScorecard rating (supportive)."

#### AI Attribution Badges

```
  [sparkle-icon] AI-generated     (purple badge)
  [sparkle-icon] AI-assisted      (indigo badge)
  [check-icon]   Human-verified   (green badge)
  [alert-icon]   Needs review     (amber badge)
```

- Layout: inline-flex, 24px height, `radius-sm`, `space-1.5` horizontal padding
- Icon: 14px, left of text
- Text: `caption`, font-weight 500
- Colors: see AI Indicator Colors in Section 2.6
- The sparkle icon (Lucide `Sparkles`) is the universal AI indicator across the platform
- Badge is interactive: clicking opens the Evidence Drawer (see Section 8.4)

#### Status Pills

Used for assessment status, finding status, vendor lifecycle status.

| Status Category | Values |
|----------------|--------|
| **Vendor status** | Active (`success-500` on `success-50`), Under Review (`warning-500` on `warning-50`), Offboarding (`error-500` on `error-50`), Pending Onboarding (`info-500` on `info-50`) |
| **Assessment status** | Draft (`gray-500` on `gray-75`), Distributed (`info-500` on `info-50`), In Progress (`warning-500` on `warning-50`), Submitted (`accent-teal-500` on `accent-teal-50`), Under Review (`primary-500` on `primary-50`), Completed (`success-500` on `success-50`), Overdue (`error-500` on `error-50`) |
| **Finding status** | Open (`error-500` on `error-50`), Remediation In Progress (`warning-500` on `warning-50`), Submitted for Verification (`info-500` on `info-50`), Verified Closed (`success-500` on `success-50`), Risk Accepted (`gray-500` on `gray-75`) |

- Layout: inline-flex, 24px height, `radius-full`, `space-2` horizontal padding
- Text: `caption`, font-weight 500
- Leading dot: 6px filled circle matching text color, `space-1.5` right margin

#### Timeline Component

Used for vendor activity history and monitoring events.

```
  [dot]--+-- 27 Mar 2026, 14:32
         |   Assessment #214 completed
         |   Composite risk score: 78 (HIGH) -- up from 65
         |   [View assessment ->]
         |
  [dot]--+-- 25 Mar 2026, 09:15
         |   [AI badge] Vendor enrichment updated
         |   SecurityScorecard rating: B (was B+)
         |   Confidence: HIGH
         |
  [dot]--+-- 20 Mar 2026, 11:00
         |   Evidence uploaded: SOC 2 Type II Report
         |   [View evidence ->]
         |
```

- Vertical line: 2px wide, `gray-200`, centered on dots
- Dot: 10px circle, `gray-300` border, `white` fill. For alerts: `error-500` fill (P0/P1), `warning-500` fill (P2/P3), `info-500` fill (P4)
- Date: `body-sm`, `gray-600`
- Event title: `body-md`, `gray-900`, font-weight 500
- Details: `body-sm`, `gray-700`
- Action link: `body-sm`, `primary-500`, with right-arrow icon
- Spacing: `space-6` between events

#### Score Gauge

Used for composite risk scores on vendor profiles and executive dashboards.

```
         Critical
           /
      .-'  HIGH  '-.
    /'      78       '\
   |    ______|____    |
   |   /      |    \   |
   |  /       |     \  |
   '-'--------|------'-'
   Low            Medium
```

- Type: Semi-circular gauge (180 degrees), rendered as SVG
- Size: `lg` (200px diameter for vendor profile header), `md` (120px for dashboard widgets), `sm` (64px for table inline)
- Track: 12px wide (`lg`), 8px (`md`), 4px (`sm`), `gray-100` color
- Fill arc: colored by risk tier (uses gradient from current tier color to next tier color at boundaries)
- Center number: `display-lg` for `lg`, `heading-h1` for `md`, `mono-md` for `sm`. Font-weight 700. Color matches risk tier.
- Tier label: Below center number, `body-sm`, font-weight 600, uppercase, tier color
- Trend arrow: Small inline arrow next to score showing direction (up = risk increasing = `error-500`, down = risk decreasing = `success-500`), with percentage in `caption`

#### Trend Indicators

```
  [arrow-up-right] +12%   (red -- risk increasing)
  [arrow-down-right] -8%   (green -- risk decreasing)
  [minus] 0%               (gray -- stable)
```

- Arrow icon: 16px, color-coded
- Percentage: `body-sm`, font-weight 500, same color as arrow
- Risk context: increasing risk is bad (red), decreasing risk is good (green). This is the inverse of typical financial indicators.
- Tooltip on hover: "Risk score changed from 66 to 78 (+12%) over the last 30 days"

#### Framework Coverage Bars

```
  SOC 2 TSC       ||||||||||||||||||||     92%  (45/49 controls)
  ISO 27001:2022  ||||||||||||||||||       85%  (79/93 controls)
  NIST CSF 2.0    |||||||||||||           62%  (66/106 controls)
  HIPAA           ||||||||||               55%  (28/50 controls)
```

- Bar track: full width of container, 8px height, `gray-100` background, `radius-full`
- Bar fill: `radius-full`, color based on coverage percentage (>80% `success-500`, 60-80% `warning-500`, <60% `error-500`)
- Framework name: `body-sm`, `gray-900`, font-weight 500, left-aligned above bar
- Percentage: `mono-sm`, font-weight 600, right-aligned, color matches bar fill
- Control count: `caption`, `gray-600`, right-aligned after percentage
- Spacing: `space-4` between each framework row

### 8.3 Forms and Input

#### Standard Input Field

```
  Label *
  +----------------------------------------------+
  |  Placeholder text                             |
  +----------------------------------------------+
  Helper text or validation message
```

- Label: `body-sm`, `gray-800`, font-weight 500. Required indicator: `error-500` asterisk.
- Input: 40px height, `radius-md`, 1px `gray-200` border, `space-3` horizontal padding, `body-md` text, `gray-950` value, `gray-500` placeholder
- Focus: `primary-500` border (2px), `shadow-ring` outer glow
- Error: `error-500` border (2px), error message below in `caption`, `error-600`
- Disabled: `gray-75` background, `gray-500` text, no border change, `not-allowed` cursor
- Helper text: `caption`, `gray-600`, below input, `space-1` gap

#### AI-Assisted Input Field

The signature interaction pattern of Velora. Used wherever AI pre-fills or suggests values.

```
  Vendor Industry *                              [sparkle] AI-suggested
  +----------------------------------------------+
  |  Financial Services - Banking      [Edit]    |
  +----------------------------------------------+
  [***] HIGH confidence | Source: Clearbit enrichment, SEC filings
  [View sources]
```

**Structure:**
- Same base input styling as standard field
- AI indicator: `Sparkles` icon + "AI-suggested" text in `caption`, right-aligned to label, using `ai-generated` badge color (`#7B61FF` text)
- Input value: pre-filled by AI, `gray-950` text, editable
- Edit button: `body-sm`, `primary-500`, right-padded inside input. On click, input becomes fully editable with cursor focus.
- Below input:
  - Confidence indicator (dots + level + percentage, see Section 8.2)
  - Source summary: `caption`, `gray-600`, pipe-separated source names
  - "View sources" link: `caption`, `primary-500`, opens Evidence Drawer

**States:**
- **AI pre-filled, unreviewed**: Left 3px border in `#7B61FF` (AI purple). Background `#F3F0FF`.
- **AI pre-filled, human-confirmed**: Left 3px border in `success-500`. Background `success-50`. Badge changes to "Human-verified."
- **AI pre-filled, human-modified**: Left 3px border in `accent-teal-500`. Badge shows "AI-assisted" (human edited AI output).
- **Low confidence (<60%)**: Left 3px border in `warning-500`. Background `warning-50`. Amber pulse animation (subtle, 2s period).
- **Manual entry (no AI)**: Standard input styling, no left border, no AI badges.

#### Evidence Upload Zone

```
  +------------------------------------------------------+
  |                                                      |
  |        [Upload cloud icon]                           |
  |                                                      |
  |   Drag and drop evidence files here                  |
  |   or click to browse                                 |
  |                                                      |
  |   Supported: PDF, DOCX, XLSX, PNG, JPG               |
  |   Maximum: 50MB per file                             |
  |                                                      |
  +------------------------------------------------------+
```

- Container: dashed 2px `gray-300` border, `radius-lg`, `gray-50` background, 160px min-height, centered content
- Drag-over: dashed 2px `primary-400` border, `primary-50` background, icon animates (lift + color change)
- Icon: `CloudUpload`, 48px, `gray-400` default, `primary-500` on drag-over
- Title: `body-md`, `gray-900`
- Subtitle: `body-sm`, `gray-600`
- File type list: `caption`, `gray-500`

**Upload progress (per file):**
```
  [FileText] SOC_2_Report_2025.pdf        Parsing...  [====>    ] 67%
  [FileText] ISO_27001_Cert.pdf           Complete    [==========] 100%  [View]
  [FileText] PenTest_Q4_2025.pdf          Error       [x] Retry
```
- File row: 48px height, `gray-75` background, `radius-md`, `space-3` padding
- Progress bar: 4px height, `primary-500` fill, `gray-200` track
- Status text: `caption`, color by state (processing: `info-500`, complete: `success-500`, error: `error-500`)
- Post-upload: file row shows detected document type badge, auto-classification confidence, and "View parsed" link

#### Questionnaire Builder (Admin)

Used by admins to create custom questionnaire templates.

```
  +------------------------------------------------------+
  | Custom Assessment Template                    [Save] |
  |------------------------------------------------------|
  | Template Name: [Annual SaaS Vendor Review        ]   |
  | Base Framework: [SOC 2 TSC          v] + [Add]       |
  |------------------------------------------------------|
  | SECTION 1: Access Control                            |
  |   Q1: [Describe your access control policies...  ]   |
  |       Type: [Long text v]  Required: [x]  Weight: [3]|
  |       Mapped to: [CC6.1, CC6.2, CC6.3]               |
  |   [+ Add question]                                   |
  |                                                      |
  | SECTION 2: Data Protection                           |
  |   ...                                                |
  |                                                      |
  | [+ Add section]                                      |
  +------------------------------------------------------+
```

- Container: `white` card, `shadow-sm`, `radius-lg`
- Section headers: `heading-h3`, `gray-900`, collapsible accordion pattern
- Question rows: drag-handle (6 dots) left for reordering, question number auto-incremented
- Type selector: dropdown with options (Short text, Long text, Single select, Multi select, Yes/No/NA, File upload, Date, Numeric)
- Framework mapping: multi-select chips showing linked framework clauses, searchable

#### Config Editors (Scoring Model, Escalation Rules, Workflows)

Visual editors for admin configuration. No code required.

**Scoring Model Editor:**
```
  +----------------------------------------------------------+
  | Scoring Model: Default Risk Assessment         [Save]    |
  |----------------------------------------------------------|
  | Method: [Weighted Average v]                              |
  |                                                          |
  | FACTORS                          WEIGHT     PREVIEW      |
  | [drag] Security Posture         [===|====] 25%   Score: 72|
  | [drag] Data Sensitivity         [==|=====] 20%   Score: 85|
  | [drag] Business Criticality    [==|=====] 20%   Score: 60|
  | [drag] Compliance Status       [=|======] 15%   Score: 90|
  | [drag] Control Maturity        [=|======] 10%   Score: 45|
  | [drag] Incident History        [|=======]  5%   Score: 88|
  | [drag] Financial Stability     [|=======]  5%   Score: 70|
  |                                         ----             |
  |                         Total:          100%   = 71.65   |
  |                                                          |
  | THRESHOLDS                                               |
  | Critical: [85+]  High: [70-84]  Medium: [40-69]  Low: [<40]|
  |                                                          |
  | [Preview with sample vendor v]                           |
  +----------------------------------------------------------+
```

- Weight sliders: horizontal, 200px wide, `primary-500` fill, `gray-200` track, draggable handle
- Real-time preview: score recalculates live as weights adjust
- Validation: total weight must sum to 100% (shown in `error-500` if not)

**Escalation Rule Builder:**
```
  IF [vendor non-response v] for [30 v] days
  THEN [escalate to v] [Procurement Lead v]
  WAIT [5 v] business days
  THEN [escalate to v] [CISO v]
```

- Condition/action rows in card format
- Dropdowns with searchable options
- Drag-to-reorder escalation steps
- Visual timeline preview of the escalation chain

#### Multi-Select with Search

```
  Applicable Frameworks
  +----------------------------------------------+
  | [x SOC 2 TSC] [x ISO 27001:2022] [search...]|
  +----------------------------------------------+
  | [x] SOC 2 TSC                                |
  | [x] ISO 27001:2022                           |
  | [ ] NIST CSF 2.0                             |
  | [ ] HIPAA Security Rule                      |
  | [ ] PCI DSS 4.0                              |
  | [ ] GDPR                                     |
  | [ ] DORA                                     |
  +----------------------------------------------+
```

- Selected items shown as chips inside the input: `radius-full`, `primary-50` background, `primary-700` text, `caption` size, 24px height, with `x` remove button
- Dropdown: `shadow-lg`, `white` background, `radius-lg`, max 320px wide, max 280px height with scroll
- Search input at top of dropdown, live filtering
- Checkbox items: 36px height, `body-sm` text, checkbox in `primary-500` when checked

### 8.4 Feedback and Overlays

#### Toast Notifications

```
  +----------------------------------------------------+
  | [success-icon]  Assessment #214 completed           |
  |                 Risk score calculated: 78 (HIGH)    |
  |                                        [Dismiss] X |
  +----------------------------------------------------+
```

- Position: bottom-right, 24px from edges, stacked (newest on top, max 3 visible)
- Container: 400px max-width, `white` background, `shadow-lg`, `radius-lg`, 1px border matching semantic color
- Left accent bar: 4px wide, semantic color
- Icon: 20px, semantic color
- Title: `body-md`, `gray-900`, font-weight 500
- Description: `body-sm`, `gray-700`
- Auto-dismiss: success after 5s, info after 7s, warning persists, error persists
- Animation: slide-in from right (300ms ease-out), fade-out on dismiss (200ms)
- Dismiss: `x` button, `gray-400`, hover `gray-700`

#### Evidence Drawer

The primary mechanism for AI transparency. Slides in from right when user clicks any "View sources," AI badge, or confidence indicator.

```
+------------------------------------------------------------------------+
| Main Content (shrinks)              | Evidence Drawer (480px)          |
|                                     |                                  |
|                                     | SOURCES FOR: Vendor Industry     |
|                                     | ================================|
|                                     |                                  |
|                                     | SOURCE 1: Clearbit Enrichment    |
|                                     | Confidence: HIGH (94%)           |
|                                     | Retrieved: 27 Mar 2026           |
|                                     | +------------------------------+ |
|                                     | | "Acme Corp is classified as  | |
|                                     | |  a FINANCIAL SERVICES        | |
|                                     | |  company, specifically in    | |
|                                     | |  the BANKING sub-sector..."  | |
|                                     | +------------------------------+ |
|                                     |                                  |
|                                     | SOURCE 2: SEC EDGAR Filing       |
|                                     | Confidence: HIGH (91%)           |
|                                     | Retrieved: 15 Mar 2026           |
|                                     | +------------------------------+ |
|                                     | | "The Company operates as a   | |
|                                     | |  bank holding company..."    | |
|                                     | +------------------------------+ |
|                                     |                                  |
|                                     | [Accept value] [Edit value]      |
|                                     |                        [Close X] |
+------------------------------------------------------------------------+
```

- Width: 480px (fixed), slides from right edge
- Background: `white`, `shadow-2xl` on left edge
- Header: `heading-h3`, `gray-950`, with close button (`x`, `gray-400`)
- "Sources for" label: `overline` style, `gray-600`, uppercase
- Source cards: `gray-50` background, `radius-md`, `space-4` padding, 1px `gray-150` border
- Source name: `body-md`, `gray-900`, font-weight 500
- Extracted text: `body-sm`, `gray-800`, within a bordered quote block. Highlighted keywords in `warning-100` background.
- Action buttons at bottom: "Accept value" (primary button), "Edit value" (secondary button)
- Animation: slide-in from right (350ms ease-out), main content area compresses to accommodate

#### Confirmation Modals

For destructive or significant actions (delete vendor, override score, accept risk).

```
  +----------------------------------------------+
  |   [Warning icon]                             |
  |                                              |
  |   Delete Vendor: Acme Corp?                  |
  |                                              |
  |   This will permanently remove the vendor    |
  |   profile, including 12 assessments, 8       |
  |   evidence documents, and 3 active findings. |
  |   This action cannot be undone.              |
  |                                              |
  |   Type "Acme Corp" to confirm:               |
  |   [                                    ]     |
  |                                              |
  |            [Cancel]    [Delete Vendor]        |
  +----------------------------------------------+
```

- Overlay: `rgba(13, 15, 28, 0.5)` backdrop, backdrop-blur 4px
- Modal: centered, 480px max-width, `white` background, `radius-xl`, `shadow-2xl`
- Padding: `space-8`
- Icon: 48px, `warning-500` for caution, `error-500` for destructive
- Title: `heading-h2`, `gray-950`
- Body: `body-md`, `gray-700`
- Confirmation input (for destructive actions): requires typing entity name
- Buttons: right-aligned, `space-3` gap. Cancel: secondary. Confirm: `error-500` background for destructive, `primary-700` for standard.
- Animation: fade-in backdrop (200ms), scale-up modal from 95% to 100% (250ms ease-out)

#### Progress Indicators

**Multi-step workflow progress:**
```
  (1)-----(2)-----(3)-----(4)-----(5)
  Setup   Enrich  Assess  Review  Complete
  [done]  [done]  [curr]  [next]  [next]
```

- Horizontal stepper for 3-7 step flows
- Step circles: 32px, `primary-500` fill + `white` number for completed, `primary-500` border + `white` fill + `primary-500` number for current, `gray-300` border + `white` fill + `gray-500` number for future
- Connector lines: 2px, `primary-500` for completed connections, `gray-200` for future
- Labels: `body-sm`, `gray-900` for current, `gray-600` for others
- Checkmark icon replaces number for completed steps

**Enrichment/parsing progress:**
```
  Enriching vendor profile...
  [====>                    ]  35%
  Step 3/7: Fetching certification data
```

- Bar: full-width, 6px height, `primary-500` fill, `gray-100` track, `radius-full`
- Animated stripes on fill for active processing
- Percentage: `mono-sm`, right-aligned
- Step description: `body-sm`, `gray-600`

#### Empty States

```
  +----------------------------------------------+
  |                                              |
  |           [illustration]                     |
  |                                              |
  |      No assessments in progress              |
  |                                              |
  |   Start an assessment to evaluate vendor     |
  |   risk against your chosen frameworks.       |
  |                                              |
  |         [Start Assessment]                   |
  |                                              |
  +----------------------------------------------+
```

- Illustration: line-art style, monochromatic using `gray-300` and `gray-200`, 120px max height, contextual (different for each module)
- Title: `heading-h2`, `gray-900`, centered
- Description: `body-md`, `gray-600`, centered, max 360px wide
- CTA: primary button, centered
- No sad faces, no apologetic language. Tone: direct and action-oriented.

### 8.5 Buttons

| Variant | Background | Text | Border | Usage |
|---------|-----------|------|--------|-------|
| **Primary** | `primary-700` | `white` | none | Main CTA per page/modal |
| **Primary hover** | `primary-600` | `white` | none | |
| **Primary active** | `primary-800` | `white` | none | |
| **Primary disabled** | `gray-200` | `gray-500` | none | |
| **Secondary** | `white` | `gray-800` | 1px `gray-200` | Secondary actions |
| **Secondary hover** | `gray-50` | `gray-900` | 1px `gray-300` | |
| **Ghost** | transparent | `gray-700` | none | Tertiary actions, icon buttons |
| **Ghost hover** | `gray-75` | `gray-900` | none | |
| **Destructive** | `error-600` | `white` | none | Delete, remove, revoke actions |
| **Destructive hover** | `error-700` | `white` | none | |
| **Link** | transparent | `primary-500` | none | Inline text actions |
| **Link hover** | transparent | `primary-600` | underline | |

**Sizes:**
| Size | Height | Padding (h) | Font | Icon |
|------|--------|-------------|------|------|
| `sm` | 32px | 12px | `body-sm`, 500 | 16px |
| `md` | 36px | 16px | `body-md`, 500 | 18px |
| `lg` | 40px | 20px | `body-md`, 600 | 20px |
| `xl` | 48px | 24px | `body-lg`, 600 | 20px |

- Border radius: `radius-md` for all sizes
- Transition: background 150ms ease, transform 100ms ease
- Active: `scale(0.98)` transform
- Focus: `shadow-ring` outline
- Icon + text: `space-2` gap between icon and label
- Loading state: text replaced by spinner (16px, `white` for primary, `gray-600` for secondary), button width locked to prevent layout shift

---

## 9. Page Layouts and Key Screens

### 9.1 Executive Dashboard

The landing page for all users. Designed for both 60-second executive scan and analyst deep-dive.

```
+------------------------------------------------------------------------+
| SIDEBAR | TOP BAR: Dashboard                    [Cmd+K] [Bell] [?]    |
|         |--------------------------------------------------------------|
|         | PORTFOLIO RISK OVERVIEW                    Period: [30d v]   |
|         |                                                              |
|         | +----------+ +----------+ +----------+ +----------+          |
|         | | RISK     | | VENDORS  | | OPEN     | | ASSESSMENT|          |
|         | | SCORE    | | BY TIER  | | FINDINGS | | COMPLETION|          |
|         | |          | |          | |          | |           |          |
|         | |   [Gauge]| | Crit: 12 | | Crit: 3 | |  [=====]  |          |
|         | |    64    | | High: 28 | | High: 9 | |   87%     |          |
|         | |  MEDIUM  | | Med: 185 | | Med: 18 | | 156/180   |          |
|         | |  -8% QoQ | | Low: 195 | | Low: 22 | | due       |          |
|         | +----------+ +----------+ +----------+ +----------+          |
|         |                                                              |
|         | +-------------------------------+ +------------------------+ |
|         | | RISK HEATMAP                  | | TOP 10 RISKIEST        | |
|         | | (5x5: Likelihood x Impact)    | | VENDORS                | |
|         | |                               | |                        | |
|         | |  5 |  .  .  .  2  1           | | 1. Acme Corp    78 [H] | |
|         | |  4 |  .  .  3  4  .           | | 2. DataSync     76 [H] | |
|         | |  3 |  .  1  8  2  .           | | 3. CloudNet     74 [H] | |
|         | |  2 |  2  5  12 1  .           | | 4. InfoSec Ltd  72 [H] | |
|         | |  1 |  8  15 3  .  .           | | 5. TechVend     71 [H] | |
|         | |    +--1--2--3--4--5            | | ...                    | |
|         | |    Impact ->                  | | [View all vendors ->]  | |
|         | +-------------------------------+ +------------------------+ |
|         |                                                              |
|         | +-------------------------------+ +------------------------+ |
|         | | RISK TREND (30/60/90d)        | | RECENT ALERTS          | |
|         | | [Line chart]                  | | [P1] Acme Corp breach  | |
|         | |     ___                       | |   2h ago               | |
|         | |    /   \___                   | | [P2] CloudNet cert exp | |
|         | |   /        \___              | |   5h ago               | |
|         | |  /              \___         | | [P3] DataSync rating   | |
|         | | 90d   60d   30d   Now        | |   1d ago               | |
|         | +-------------------------------+ | [View all alerts ->]   | |
|         |                                  +------------------------+ |
|         |                                                              |
|         | QUICK ACTIONS                                                |
|         | [+ Add Vendor]  [Start Assessment]  [Generate Report]       |
+------------------------------------------------------------------------+
```

**Layout specification:**

- **Metric cards** (top row): 4 cards in a row (3 columns each on 12-col grid). `white` background, `shadow-sm`, `radius-lg`, `space-6` internal padding.
  - Primary metric: `display-lg` size, font-weight 700, color matches context (risk tier color for risk score, `gray-950` for counts)
  - Label: `overline` style, `gray-600`
  - Secondary metric: `body-sm`, `gray-700` (e.g., "-8% QoQ" with trend indicator)
  - Score gauge: embedded `md` gauge in the risk score card

- **Risk heatmap** (left, 7 cols): 5x5 grid rendered as SVG or CSS grid.
  - Cell size: equal squares, 48px minimum
  - Color intensity: gradient from `success-100` (bottom-left, low risk) through `warning-100` (center) to `error-100` (top-right, high risk)
  - Cell number: `mono-md`, `gray-900` (vendor count in that cell)
  - Empty cells: `gray-75` background
  - Axis labels: `caption`, `gray-600`
  - Clickable cells: on click, shows list of vendors in that risk cell

- **Top 10 vendors** (right, 5 cols): Mini-table format.
  - Rank number: `mono-sm`, `gray-500`
  - Vendor name: `body-md`, `gray-900`, truncated with ellipsis at 180px
  - Risk score badge: compact `sm` size
  - Row height: 40px, 1px `gray-100` separator
  - "View all" link at bottom: `body-sm`, `primary-500`

- **Risk trend chart** (left, 7 cols): Line chart.
  - Background: `white` card
  - Line: 2px, `primary-500`, with filled area below using `primary-500` at 10% opacity
  - Data points: 6px circles on hover, `primary-500` fill, `white` 2px border
  - Axes: `caption`, `gray-600`. Y-axis: risk score (0-100). X-axis: date labels.
  - Tooltip on hover: date, score, change from previous data point
  - Reference lines: dashed horizontal lines at tier thresholds (40, 70, 85) in respective tier colors at 20% opacity

- **Recent alerts** (right, 5 cols): Alert list.
  - Priority badge: colored dot (P0/P1: `error-500`, P2: `warning-500`, P3: `info-500`, P4: `gray-400`)
  - Vendor name: `body-md`, `gray-900`, font-weight 500
  - Time: `caption`, `gray-600`
  - Max 5 alerts visible, "View all" link at bottom

- **Quick actions** (bottom, full width): Row of ghost-style buttons with leading icons. `body-md`, `gray-700`. Hover: `gray-75` background. This row is optional and hidden in collapsed view.

### 9.2 Vendor List

```
+------------------------------------------------------------------------+
| SIDEBAR | TOP BAR: Vendors                      [Cmd+K] [Bell] [?]    |
|         |--------------------------------------------------------------|
|         | Vendor Portfolio                                    [+ Add]   |
|         | 420 vendors across 4 tiers                                   |
|         |                                                              |
|         | [Table] [Cards] [Kanban]    [Filter v] [Search...] [Export]  |
|         |                                                              |
|         | +----------------------------------------------------------+ |
|         | | [ ] Vendor       | Score | Tier | Status  | Assess. | ..| |
|         | |----------------------------------------------------------| |
|         | | [ ] Acme Corp    | 78[H] | T1   | Active  | 12 Mar  |   | |
|         | |     acme.com     |       | Crit | 3 find. |         |   | |
|         | |----------------------------------------------------------| |
|         | | [ ] CloudSync    | 42[M] | T2   | Active  | 08 Feb  |   | |
|         | |     cloudsync.io |       | Med  | 0 find. |         |   | |
|         | |----------------------------------------------------------| |
|         | | ...                                                      | |
|         | +----------------------------------------------------------+ |
|         |                                                              |
|         | Showing 1-25 of 420       [< Prev] [1] [2] ... [17] [Next >] |
+------------------------------------------------------------------------+
```

**View toggles:**

- **Table view** (default): Standard data table as specified in Section 8.2. Columns: checkbox, vendor name (with domain subtitle), risk score badge, tier, status pill, last assessment date, actions (three-dot menu).

- **Card view**: 3 columns on desktop, 2 on tablet, 1 on mobile. Each card:
  ```
  +----------------------------------+
  | [Logo/Initial] Acme Corp    [..] |
  | acmecorp.com                     |
  | Financial Services - Banking     |
  |                                  |
  | Risk: [Gauge 64px] 78 HIGH      |
  | Tier: [badge] Critical (Tier 1) |
  | Status: [pill] Active           |
  |                                  |
  | Findings: 3 open (1 critical)   |
  | Last assessed: 12 Mar 2026      |
  |                                  |
  | [View Profile]  [Start Assess]  |
  +----------------------------------+
  ```
  - Card: `white` background, `shadow-sm`, `radius-lg`, `space-6` padding, hover `shadow-md`
  - Logo area: 40px square, `radius-md`, `gray-100` background if no logo, vendor initial in `primary-500`

- **Kanban view**: Columns grouped by vendor status (Pending Onboarding, Active, Under Review, Offboarding). Cards are compact (name + score + tier only). Drag-and-drop between columns to change status (triggers confirmation modal).

**Quick-view panel:** Clicking a vendor row (in any view) opens a slide-over panel from the right (480px, similar to Evidence Drawer) showing vendor summary without navigating away. Panel contains: risk gauge, tier, key contacts, recent assessment summary, "Open Full Profile" button.

### 9.3 Vendor Profile (Single Vendor)

```
+------------------------------------------------------------------------+
| SIDEBAR | TOP BAR: Vendors > Acme Corp          [Cmd+K] [Bell] [?]    |
|         |--------------------------------------------------------------|
|         | +----------------------------------------------------------+ |
|         | | VENDOR HEADER                                            | |
|         | | [Logo]  Acme Corp                    [Edit] [Actions v] | |
|         | |         acmecorp.com                                    | |
|         | |         Financial Services - Banking  [AI badge]        | |
|         | |                                                          | |
|         | | [Gauge 200px]   Tier: Critical (T1)  Status: Active     | |
|         | |      78         Since: 15 Jan 2024   Owner: Anya Kohli  | |
|         | |     HIGH        Last assessed: 12 Mar 2026              | |
|         | |   +12% (30d)                                            | |
|         | +----------------------------------------------------------+ |
|         |                                                              |
|         | [Overview] [Assessments] [Evidence] [Monitoring] [Findings] |
|         | [Communications] [Timeline]                                  |
|         |                                                              |
|         | === OVERVIEW TAB (default) ===                               |
|         |                                                              |
|         | +---------------------------+ +---------------------------+  |
|         | | RISK BREAKDOWN            | | KEY CONTACTS              |  |
|         | | Security:     72  [====]  | | John Smith, CISO          |  |
|         | | Data Sens:    85  [=====] | | jane@acme.com             |  |
|         | | Bus. Crit:    60  [===]   | | Portal: Last login 3d ago |  |
|         | | Compliance:   90  [=====] | +---------------------------+  |
|         | | Control Mat:  45  [==]    |                                |
|         | | Incident:     88  [=====] | +---------------------------+  |
|         | | Financial:    70  [====]  | | FRAMEWORK COVERAGE        |  |
|         | | Nth-party:    65  [===]   | | SOC 2:       92%  [=====] |  |
|         | +---------------------------+ | ISO 27001:   85%  [====]  |  |
|         |                              | HIPAA:       55%  [===]   |  |
|         | +---------------------------+ +---------------------------+  |
|         | | ENRICHED PROFILE          |                                |
|         | | [AI] Industry: Banking    |                                |
|         | | [AI] Employees: 2,400     |                                |
|         | | [AI] Revenue: $180M       |                                |
|         | | [AI] Tech stack: AWS,     |                                |
|         | |   Cloudflare, Salesforce  |                                |
|         | | SecurityScorecard: B (78) |                                |
|         | | Breach history: 1 (2019)  |                                |
|         | | [View all enrichment ->]  |                                |
|         | +---------------------------+                                |
+------------------------------------------------------------------------+
```

**Vendor header:**
- Full-width card, `white` background, `shadow-sm`, `radius-lg`
- Logo: 56px square, `radius-md`, `gray-100` fallback with initial
- Vendor name: `display-sm`, `gray-950`
- Domain: `body-md`, `gray-600`, clickable (opens in new tab)
- Industry: `body-md`, `gray-700`, with AI badge if inferred
- Score gauge: `lg` size (200px), left-aligned
- Metadata columns: 3-column layout to the right of gauge (Tier, Status, Since, Owner, Last assessed)
- Actions dropdown: Edit Profile, Start Assessment, Generate Report, Export Data, Offboard Vendor

**Tab navigation:**
- Horizontal tabs, flush below header card
- Tab label: `heading-h4`, `gray-600` default, `primary-500` active with 2px bottom border
- Tab count badges: `caption`, `gray-500` background pill (e.g., "Findings (3)")
- Smooth horizontal scroll on mobile/tablet

**Overview tab layout:**
- Two-column: primary (8 cols) + sidebar (4 cols)
- Risk breakdown card: horizontal bar chart showing each scoring dimension with score and bar
- Enriched profile card: each field shows AI badge with confidence dot, clickable for Evidence Drawer
- Framework coverage card: stacked horizontal bars (see Section 8.2)
- Key contacts card: name, email, phone, portal login status
- Relationship health indicator: based on vendor responsiveness and collaboration quality

**Assessments tab:**
- Table of assessments: assessment name, status pill, framework, score, date, assigned analyst
- Active assessments at top with progress bar
- Historical assessments below with completion date

**Evidence tab:**
- Grid of evidence documents: thumbnail/icon, name, type badge, upload date, freshness indicator, confidence
- Expiring evidence highlighted with `warning-100` background and countdown badge

**Monitoring tab:**
- Alert timeline (see Timeline Component in Section 8.2)
- Rating trend chart (line chart, same style as dashboard)
- Signal history table: signal type, source, severity, timestamp, status (new/reviewed/dismissed)

**Findings tab:**
- Table: finding title, severity badge, status pill, assigned to, deadline, days remaining
- Overdue findings: `error-50` row background, "Overdue by X days" in `error-600`
- Finding detail: click to expand with description, AI-generated remediation guidance, evidence links

**Communications tab:**
- Threaded conversation view (similar to email thread)
- Each message: sender, timestamp, content, attachments
- @mentions highlighted in `primary-100` background

**Timeline tab:**
- Full chronological timeline (see Timeline Component)
- Filter by event type: assessments, evidence, monitoring, findings, communications
- Date range selector

### 9.4 Assessment Workspace

The primary working environment for analysts conducting vendor assessments.

```
+------------------------------------------------------------------------+
| SIDEBAR | TOP BAR: Vendors > Acme Corp > Assessment #214  [Cmd+K]     |
|         |--------------------------------------------------------------|
|         | Assessment: Annual SOC 2 + ISO Review     Status: Under Review|
|         | Vendor: Acme Corp   Due: 15 Apr 2026   Progress: [====] 82%  |
|         |                                                              |
|         | +-------------------------++---------------------------------+|
|         | | QUESTION LIST           || ANSWER & EVIDENCE PANEL         ||
|         | |                         ||                                 ||
|         | | Search questions...     || Q: CC6.1 - Logical Access       ||
|         | |                         ||                                 ||
|         | | SECTION: Access Control  || VENDOR RESPONSE                 ||
|         | |                         || [AI badge] [***] HIGH 94%       ||
|         | | [x] CC6.1 Logical Acc   || "We implement role-based        ||
|         | | [x] CC6.2 Auth Mech.    ||  access controls using Okta     ||
|         | | [~] CC6.3 Access Rev.   ||  with MFA enforced for all      ||
|         | | [ ] CC6.4 Network Sec   ||  production systems..."         ||
|         | | [ ] CC6.5 Encryption    || [Edit response]                 ||
|         | |                         ||                                 ||
|         | | SECTION: Data Protection || EVIDENCE                       ||
|         | | [ ] CC7.1 Monitoring    || [SOC 2 Report] CC6.1: Pass      ||
|         | | [ ] CC7.2 Incident      || [ISO Cert] A.9.2: Certified     ||
|         | | ...                     || [+ Attach evidence]              ||
|         | |                         ||                                 ||
|         | | 148/180 answered        || AI VALIDATION                    ||
|         | | 12 flagged for review   || [check] Response consistent     ||
|         | |                         ||   with SOC 2 findings           ||
|         | | [Skip with reason]      || [warn] MFA exception noted      ||
|         | | [Send to vendor]        ||   in SOC 2 Appendix B           ||
|         | |                         || [View full analysis ->]          ||
|         | |                         ||                                 ||
|         | |                         || [Accept] [Modify] [Reject]      ||
|         | +-------------------------++---------------------------------+|
+------------------------------------------------------------------------+
```

**Split-pane layout:**
- Left panel: 360px fixed width, scrollable question list
- Right panel: fluid width, answer/evidence detail
- Divider: 1px `gray-200`, draggable for resize (min 280px left, min 480px right)

**Question list (left panel):**
- Search input at top: compact, 36px height
- Sections: collapsible accordion, `heading-h4` title, `gray-100` background header
- Question items: 44px min-height, `body-sm` text
  - [x] completed (check icon, `success-500`): `gray-900` text
  - [~] flagged for review (warning icon, `warning-500`): `warning-700` text, `warning-50` background
  - [ ] unanswered (circle outline, `gray-300`): `gray-600` text
  - Active question: `primary-50` background, `primary-500` left 3px border
- Progress: `body-sm`, `gray-600`, at bottom of list. "148/180 answered, 12 flagged"
- Action links: "Skip with reason" opens a small reason capture modal. "Send to vendor" sends reminder for unanswered items.

**Answer/evidence panel (right panel):**
- Question header: `heading-h3`, framework clause ID + title
- Vendor response: AI-assisted input field pattern (see Section 8.3). Shows AI pre-filled answer with confidence and sources.
- Evidence section: cards for each linked evidence document. Shows document type badge, control mapping, coverage type (Full/Partial), and confidence.
- "+ Attach evidence" link: opens file picker or evidence library browser
- AI validation section: bulleted list of validation checks.
  - Check items: `check-circle` icon in `success-500` + description
  - Warning items: `alert-triangle` icon in `warning-500` + description (inconsistencies, exceptions)
  - Error items: `x-circle` icon in `error-500` + description (contradictions)
- Review actions: three buttons at bottom. "Accept" (`success-600`), "Modify" (opens edit mode, `primary-700`), "Reject" (`error-600`). Each requires justification text (inline textarea that expands on action click).

**Keyboard navigation:** Arrow up/down moves between questions. Enter opens answer panel. Tab moves between response, evidence, and review actions. `A` to accept, `M` to modify, `R` to reject (when focused on review actions).

### 9.5 Evidence Viewer

Full-page document viewer for detailed evidence examination.

```
+------------------------------------------------------------------------+
| SIDEBAR | TOP BAR: Evidence > SOC 2 Type II - Acme Corp   [Cmd+K]     |
|         |--------------------------------------------------------------|
|         | +-------------------------------------++-----------------------+|
|         | | DOCUMENT VIEWER                     || EXTRACTED DATA       ||
|         | |                                     ||                      ||
|         | | [Toolbar: Zoom, Rotate, Download]   || DOCUMENT INFO        ||
|         | |                                     || Type: SOC 2 Type II  ||
|         | | +-------------------------------+   || Auditor: Deloitte    ||
|         | | |                               |   || Period: Jan-Dec 2025 ||
|         | | |   [Rendered PDF page]          |   || Opinion: Unqualified ||
|         | | |                               |   || [AI] Confidence: 98% ||
|         | | |   Highlighted: "The Company   |   ||                      ||
|         | | |   implements [multi-factor     |   || CONTROL MAPPINGS     ||
|         | | |   authentication] for all..."  |   || CC6.1: Pass [Full]   ||
|         | | |                               |   || CC6.2: Pass [Full]   ||
|         | | |                               |   || CC6.3: Exception [!] ||
|         | | |                               |   ||   "MFA not enforced  ||
|         | | |                               |   ||    for legacy VPN"   ||
|         | | +-------------------------------+   || CC7.1: Pass [Full]   ||
|         | |                                     || ...                  ||
|         | | Page [3] of 84     [< Prev] [Next >]||                      ||
|         | |                                     || APPROVAL WORKFLOW    ||
|         | |                                     || [ ] Accept all HIGH  ||
|         | |                                     || [Review] 3 items     ||
|         | |                                     || [Reject] 0 items     ||
|         | +-------------------------------------++-----------------------+|
+------------------------------------------------------------------------+
```

**Document viewer (left, 8 cols):**
- Toolbar: zoom in/out, fit width/page, rotate, download original, page navigation
- PDF rendered in iframe or PDF.js canvas
- Highlighted regions: `warning-100` background with `warning-500` 2px border around extracted text passages
- Click on a highlight: right panel scrolls to corresponding extracted data point

**Extracted data panel (right, 4 cols):**
- Scrollable, independent of document viewer
- Document info card: type badge, auditor, period, opinion, confidence
- Control mappings: list format, each showing framework clause ID, status (Pass/Fail/Exception), coverage type badge, confidence dots
- Exception items: `warning-50` background, expanded to show exception text
- Click on a control mapping: document viewer scrolls to and highlights the relevant section

**Approval workflow:** Batch review at bottom of panel.
- "Accept all HIGH confidence" button: accepts all items with >85% confidence in one click
- Review items: count of items between 60-85% confidence, opens review list
- Reject items: count of items below 60% confidence, each requires manual review

### 9.6 Report Builder

```
+------------------------------------------------------------------------+
| SIDEBAR | TOP BAR: Reports > New Report          [Cmd+K] [Bell] [?]   |
|         |--------------------------------------------------------------|
|         | +-------------------------++-----------------------------------+|
|         | | TEMPLATE & SECTIONS     || LIVE PREVIEW                     ||
|         | |                         ||                                   ||
|         | | Template:               || +-------------------------------+ ||
|         | | [Board Risk Summary v]  || | VELORA TPRM                   | ||
|         | |                         || | Board Risk Summary            | ||
|         | | SECTIONS                || | Q1 2026                       | ||
|         | | [drag] [x] Exec Summary || |                               | ||
|         | | [drag] [x] Risk Heatmap || | Executive Summary             | ||
|         | | [drag] [x] Top Vendors  || | [AI-generated narrative...]   | ||
|         | | [drag] [x] FAIR Exposure|| |                               | ||
|         | | [drag] [ ] Framework    || | Risk Heatmap                  | ||
|         | |             Coverage    || | [5x5 grid visualization]      | ||
|         | | [drag] [x] Trend Chart  || |                               | ||
|         | | [drag] [ ] Remediation  || | Top 10 Riskiest Vendors       | ||
|         | |             Status      || | [table]                       | ||
|         | | [+ Add section]         || |                               | ||
|         | |                         || | ...                           | ||
|         | | PARAMETERS              || +-------------------------------+ ||
|         | | Date range: [Q1 2026 v] ||                                   ||
|         | | Vendor scope: [All v]   ||                                   ||
|         | | Include: [x] AI narr.   || [Regenerate] [Export PDF] [PPTX]  ||
|         | |          [x] Financial  ||                                   ||
|         | +-------------------------++-----------------------------------+|
+------------------------------------------------------------------------+
```

**Template selector:**
- Dropdown at top left with template previews on hover
- Pre-built templates: Board Risk Summary, Regulatory Compliance (DORA, HIPAA, etc.), Vendor Assessment Detail, Portfolio Overview, Operational Metrics
- Custom template creation: users can save current configuration as new template

**Section list (left panel):**
- Drag-to-reorder sections (drag handle icon on left)
- Checkbox to include/exclude each section
- Click section name to open section configuration (date range, vendor filter, chart type, etc.)
- "+ Add section" opens section picker with available report widgets

**Preview pane (right panel):**
- Live-rendered preview in a simulated document view (white pages with subtle shadow)
- AI-generated narratives shown with AI badge, editable inline
- Charts and tables rendered at print quality
- Page breaks shown as subtle dashed lines

**Export options:**
- PDF: high-resolution, print-ready with Velora branding (or white-labeled)
- PPTX: slide-per-section with speaker notes from AI narratives
- CSV: raw data export for custom analysis
- Scheduled delivery: configure email recipients and frequency

### 9.7 Admin Configuration

```
+------------------------------------------------------------------------+
| SIDEBAR | TOP BAR: Admin                         [Cmd+K] [Bell] [?]   |
|         |--------------------------------------------------------------|
|         | Settings                                                      |
|         |                                                              |
|         | +----------------+ +--------------------------------------+  |
|         | | ADMIN NAV      | | CONTENT AREA                        |  |
|         | |                | |                                      |  |
|         | | Organization   | | Scoring Models                      |  |
|         | |   Profile      | |                                      |  |
|         | |   Branding     | | +----------------------------------+ |  |
|         | |                | | | Default Risk Assessment   [Edit] | |  |
|         | | Assessment     | | | Method: Weighted Average         | |  |
|         | |   Scoring      | | | Factors: 8 | Threshold: Standard | |  |
|         | |   Workflows    | | | Last modified: 12 Mar 2026       | |  |
|         | |   Templates    | | +----------------------------------+ |  |
|         | |                | | | DORA Financial    [Edit] [Clone] | |  |
|         | | Monitoring     | | | Method: Multiplicative           | |  |
|         | |   Escalation   | | | Factors: 6 | Threshold: Strict   | |  |
|         | |   Schedules    | | +----------------------------------+ |  |
|         | |                | |                                      |  |
|         | | Access         | | [+ Create Scoring Model]            |  |
|         | |   Roles        | |                                      |  |
|         | |   Users        | |                                      |  |
|         | |   SSO          | |                                      |  |
|         | |                | |                                      |  |
|         | | Integrations   | |                                      |  |
|         | |   Ratings      | |                                      |  |
|         | |   ITSM         | |                                      |  |
|         | |   Messaging    | |                                      |  |
|         | |                | |                                      |  |
|         | | Data           | |                                      |  |
|         | |   Import       | |                                      |  |
|         | |   Export       | |                                      |  |
|         | |   Audit Log    | |                                      |  |
|         | +----------------+ +--------------------------------------+  |
+------------------------------------------------------------------------+
```

**Admin layout:**
- Secondary left navigation (within content area): 220px wide, `gray-50` background, grouped sections
- Content area: fluid width
- Each admin page follows a consistent pattern: list of configured items (as cards) + create/edit action

**Scoring model editor:** See Section 8.3 config editor specification.

**Workflow editor:** Visual step builder.
```
  [Intake] --> [Inherent Risk] --> [Approval] --> [Assessment] --> [Review] --> [Complete]
      |            |                   |               |              |
    Config      Config             Routing          Config         Config
```
- Each step is a card connected by arrows
- Click step to configure: name, assignee rules, SLA, required actions, transition conditions
- Add step: click `+` between existing steps
- Remove step: hover to reveal delete button (with confirmation)

**Role & permission matrix:**
- Table with roles as columns, permissions as rows
- Checkbox grid for permission assignment
- Custom role creation: clone existing role and modify

**Integration settings:**
- Card per integration: icon, name, status (Connected/Disconnected), last sync time
- Click to configure: API key input, webhook URL, sync frequency, mapping rules
- Test connection button with real-time feedback

### 9.8 Vendor Portal (External)

The vendor-facing experience. White-labeled with customer's branding.

```
+------------------------------------------------------------------------+
| [Customer Logo]  Vendor Security Portal          [Help] [Profile] [Logout]
|------------------------------------------------------------------------|
|                                                                        |
| Welcome, David Park                                                    |
| CloudSync Ltd -- Trust Profile                                         |
|                                                                        |
| +--------------------------------------------------------------------+ |
| | PENDING ASSESSMENTS                                                 | |
| |                                                                     | |
| | +--------------------------------------------------------------+   | |
| | | Annual SOC 2 + ISO Review        Due: 15 Apr 2026 (18 days)  |   | |
| | | Requesting org: FinCorp Inc                                    |   | |
| | | Progress: [=======                   ] 42% (76/180 questions) |   | |
| | | [Continue Assessment ->]                                      |   | |
| | +--------------------------------------------------------------+   | |
| | | Quarterly SIG Lite Review         Due: 30 Apr 2026 (33 days) |   | |
| | | Requesting org: HealthCo                                      |   | |
| | | Progress: [                          ] 0% (not started)       |   | |
| | | [Start Assessment ->]                                         |   | |
| | +--------------------------------------------------------------+   | |
| +--------------------------------------------------------------------+ |
|                                                                        |
| +--------------------------------------------------------------------+ |
| | OPEN FINDINGS & REMEDIATION                                         | |
| | 2 findings require remediation                                      | |
| |                                                                     | |
| | [!] Critical: MFA enforcement gap    Due: 15 Apr 2026 (18 days)    | |
| |     [Upload remediation evidence ->]                                | |
| | [!] Medium: Incident response SLA    Due: 30 May 2026 (63 days)    | |
| |     [Upload remediation evidence ->]                                | |
| +--------------------------------------------------------------------+ |
|                                                                        |
| +--------------------------------------------------------------------+ |
| | TRUST PROFILE                                                       | |
| | Manage your shared security profile                                 | |
| |                                                                     | |
| | Certifications: ISO 27001 (valid), SOC 2 Type II (valid)           | |
| | Sub-processors: 8 listed                                            | |
| | Last updated: 20 Mar 2026                                          | |
| | [Edit Trust Profile ->]                                             | |
| +--------------------------------------------------------------------+ |
+------------------------------------------------------------------------+
```

**Portal design:**
- Clean, single-column layout (max-width 960px, centered)
- Customer branding: logo from tenant config, primary color from tenant branding (applied to buttons, links, accent elements)
- No sidebar -- simple top navigation with minimal items
- Typography and components follow the same design system but with the customer's primary color replacing `primary-500`
- Assessment workspace within portal: same split-pane pattern as internal assessment workspace (Section 9.4) but simplified (no admin actions, no scoring visibility, no other vendor data)
- Evidence upload: drag-and-drop zone (see Section 8.3) with progress indicators
- Finding remediation: each finding shows description, severity, guidance, deadline. Upload button for remediation evidence.
- Trust profile editor: form-based, section-by-section (certifications, sub-processors, data processing locations, security documentation links)

---

## 10. Interaction Patterns

### 10.1 AI Interaction Model

Every AI output across Velora follows a consistent three-layer pattern:

**Layer 1: Output + Confidence**
- The AI-generated value is displayed in context (inline in a form, as a cell in a table, as a paragraph in a report).
- Confidence badge (HIGH/MEDIUM/LOW with dot pattern and percentage) is displayed adjacent to the value.
- AI attribution badge ("AI-generated," "AI-assisted," or "Human-verified") is displayed.

**Layer 2: Source References**
- Below or adjacent to the output, source names are listed in `caption` text.
- Each source name is a clickable link.
- Clicking opens the Evidence Drawer (Section 8.4) showing the source text with highlighted relevant passages.

**Layer 3: Edit / Accept / Reject**
- Every AI output has an "Edit" affordance (pencil icon or "Edit" link).
- In review flows (assessment workspace), full Accept/Modify/Reject buttons with justification capture.
- Low-confidence items (<60%) are visually elevated with amber border + pulse animation, requiring explicit human review before proceeding.

**Batch review pattern:**
- When many AI items need review (e.g., assessment with 180 pre-filled answers), a batch action toolbar appears:
  - "Accept all HIGH confidence (142 items)" -- single click, with confirmation modal showing summary
  - "Review MEDIUM confidence (26 items)" -- opens sequential review mode, one item at a time
  - "Review LOW confidence (12 items)" -- mandatory individual review
- Batch acceptance is logged as a single auditable action with the count and confidence threshold noted.

### 10.2 Progressive Disclosure

**Level 1: Dashboard.** Aggregate metrics, trend indicators, top-level alerts. One glance tells the story. Every metric is clickable to drill into detail.

**Level 2: Module list.** Filtered, sortable tables/cards of entities (vendors, assessments, findings). Bulk actions and quick-view panels available.

**Level 3: Entity detail.** Full profile with tabbed organization. Primary information visible immediately, secondary information in tabs.

**Level 4: Action/workspace.** Focused workspace for a specific task (assessment, evidence review, report building). Full attention, minimal distraction.

**Complex forms:**
- Forms with more than 6 fields are split into wizard steps (onboarding wizard: 4 steps; assessment configuration: 3 steps; scoring model: 2 steps).
- Each step has a descriptive title and brief helper text.
- Progress stepper shown at top.
- "Back" and "Continue" buttons. Final step has "Review and Confirm."
- Review step shows a summary of all entered data with "Edit" links per section.

**Advanced options:**
- Hidden behind an "Advanced" accordion at the bottom of forms/configs.
- Accordion closed by default. Label: "Advanced options" with chevron.
- `body-sm`, `gray-600` label, `gray-100` background when expanded.
- Common for: scoring thresholds, SLA overrides, notification preferences, custom field mapping.

**Contextual help:**
- Info icon (`info` lucide, 16px, `gray-400`) next to complex labels.
- Hover shows a tooltip: `shadow-lg`, `gray-950` background, `white` text, `body-sm`, `radius-md`, max 280px wide.
- First-time user experience: optional guided tour overlay (step-by-step spotlight with "Next" / "Skip tour" buttons). Spotlighted element gets a 4px `primary-500` ring + `shadow-2xl`. Tour state persisted per user.

### 10.3 Data Loading States

**Skeleton screens:** Used for initial page loads. Gray shimmer rectangles (`gray-100` to `gray-75` animation, 1.5s loop) mimicking the layout of the actual content. Never show blank white screens while loading.

**Inline loading:** For actions (button click, form submit), the button enters loading state (spinner replaces text, width locked). Adjacent content remains interactive.

**Streaming AI output:** For AI-generated narratives (report sections, remediation guidance), text streams in character-by-character (50ms per token) to indicate active generation. "Generating..." label with animated dots above the text area.

**Stale data indicator:** If data is older than the expected refresh interval, a subtle "Last updated: 5 min ago" label appears with a refresh button.

### 10.4 Error Handling

**Form validation:** Real-time validation on blur (not on keystroke). Error message appears below the field in `caption`, `error-600`. Error border on the input.

**API errors:** Toast notification (error variant) with brief message. "Retry" action in the toast for retriable errors. Non-retriable errors show "Contact support" with error ID.

**Empty search results:** "No results for [query]. Try adjusting your filters or search terms." with link to clear all filters.

**Permission denied:** Toast notification: "You don't have permission to [action]. Contact your admin for access."

---

## 11. Accessibility

### 11.1 WCAG 2.1 AA Compliance Targets

| Criterion | Target | Implementation |
|-----------|--------|----------------|
| 1.1.1 Non-text content | All images and icons have text alternatives | `aria-label` on icon buttons, `alt` on images, `aria-hidden="true"` on decorative icons |
| 1.3.1 Info and relationships | Structure conveyed through semantic HTML | Proper heading hierarchy (h1-h6), landmark regions, table headers |
| 1.4.1 Use of color | Information not conveyed by color alone | Risk tiers use shape markers + labels alongside color. Confidence uses dot patterns + text. Status uses text labels. |
| 1.4.3 Contrast (minimum) | 4.5:1 for normal text, 3:1 for large text | All color combinations verified. `gray-600` on `white` = 5.74:1. `primary-500` on `white` = 4.56:1. |
| 1.4.11 Non-text contrast | 3:1 for UI components | All interactive element borders, focus indicators, and form controls meet 3:1 minimum. |
| 2.1.1 Keyboard | All functionality available via keyboard | Tab order follows visual layout. Focus ring (`shadow-ring`) on all interactive elements. Escape closes modals/drawers. |
| 2.4.3 Focus order | Logical and meaningful sequence | Tab order: sidebar nav -> top bar -> main content -> modals/drawers (trapped focus). Skip-to-content link as first focusable element. |
| 2.4.7 Focus visible | Focus indicator always visible | `shadow-ring` (3px `primary-500` at 15% opacity) on all focusable elements. Never `outline: none` without alternative. |
| 3.2.2 On input | No unexpected context changes | Form submissions require explicit button click. Dropdowns filter but do not navigate. Selections do not auto-submit. |
| 4.1.2 Name, role, value | Assistive tech can determine component purpose | ARIA roles, labels, and states on all custom components. Live regions for dynamic updates (toasts, loading states). |

### 11.2 Keyboard Navigation Map

| Key | Context | Action |
|-----|---------|--------|
| `Tab` | Global | Move focus to next interactive element |
| `Shift+Tab` | Global | Move focus to previous interactive element |
| `Escape` | Modal/Drawer/Dropdown | Close overlay, return focus to trigger |
| `Enter` | Button/Link | Activate |
| `Space` | Checkbox/Toggle | Toggle state |
| `Arrow Up/Down` | Dropdown/List | Navigate items |
| `Arrow Left/Right` | Tabs | Switch between tabs |
| `Cmd+K` | Global | Open command palette |
| `[` | Global | Toggle sidebar |
| `?` | Global (when no input focused) | Open keyboard shortcut help |

### 11.3 Screen Reader Considerations

- Risk score gauges: `role="meter"` with `aria-valuemin="0"`, `aria-valuemax="100"`, `aria-valuenow="{score}"`, `aria-valuetext="Risk score: {score}, tier: {tier}"`
- Risk heatmap: `role="grid"` with cell-level `aria-label` ("Likelihood 4, Impact 3: 8 vendors")
- Progress bars: `role="progressbar"` with `aria-valuenow` and `aria-valuetext`
- AI badges: announce via `aria-label` ("AI-generated, high confidence, 94 percent, click to view sources")
- Timeline: ordered list `<ol>` with `aria-label="Vendor activity timeline"`
- Toasts: `role="alert"` with `aria-live="polite"` (info/success) or `aria-live="assertive"` (error/warning)
- Skeleton loaders: `aria-busy="true"` on container, `aria-label="Loading content"`

### 11.4 Color-Blind Accessibility

Every color-dependent indicator has a secondary non-color differentiator:

| Indicator | Color | Non-Color Differentiator |
|-----------|-------|--------------------------|
| Risk tier | Red/Orange/Amber/Green/Blue | Shape marker (double-diamond, triangle, square, circle, rounded-square) + text label |
| Confidence | Green/Amber/Red | Dot fill pattern (3/3, 2/3, 1/3) + percentage + text label |
| Status pills | Various | Leading dot pattern varies (filled, half, empty) + text label |
| AI badge | Purple/Indigo/Green/Amber | Different icon (sparkle, sparkle, checkmark, alert) + text label |
| Trend indicators | Red/Green/Gray | Arrow direction (up-right, down-right, horizontal) + percentage sign (+/-) |
| Heatmap cells | Green-to-Red gradient | Cell contains numeric count; tooltip provides full context |

---

## 12. Responsive Behavior

### 12.1 Desktop (1280px+)

Full experience as specified throughout this document. Sidebar expanded by default (collapsible). 12-column grid. All features available.

### 12.2 Tablet (768px - 1279px)

| Component | Adaptation |
|-----------|------------|
| Sidebar | Collapsed to 64px by default. Expand overlays content (does not push). |
| Data tables | Horizontal scroll for tables with 5+ columns. Priority columns (name, score, status) remain fixed. |
| Dashboard widgets | 2-column grid instead of 4 (metric cards stack 2x2). |
| Split-pane layouts | Stack vertically: question list above, answer panel below. Toggle between panels on smaller tablets. |
| Cards (vendor list) | 2-column card grid. |
| Evidence viewer | Document viewer full-width, extracted data panel collapses to bottom sheet. |
| Modals | Full-width with `space-6` horizontal margin. |
| Command palette | 90% viewport width, max 560px. |

### 12.3 Mobile (< 768px)

Mobile is read-only dashboard mode. No full assessment or admin workflows on mobile.

| Component | Adaptation |
|-----------|------------|
| Sidebar | Hidden. Hamburger menu in top-left opens overlay navigation. |
| Dashboard | Single-column. Metric cards stack vertically. Risk gauge `sm` size. Heatmap replaced by sorted risk tier list. |
| Vendor list | Card view only. Single column. Score badge and status pill visible. |
| Vendor profile | Single-column, tab navigation becomes horizontal scroll or dropdown selector. |
| Alerts | List view with swipe actions (acknowledge, snooze). |
| Tables | Replaced by card lists. Each "row" becomes a card with key fields. |
| Navigation | Bottom tab bar for primary sections: Dashboard, Vendors, Alerts, Profile. |
| Touch targets | Minimum 44px height/width for all interactive elements. |

---

## 13. Motion and Animation

All animations serve functional purposes (provide feedback, indicate state change, maintain spatial orientation). No decorative animation.

| Animation | Duration | Easing | Trigger |
|-----------|----------|--------|---------|
| Button hover | 150ms | ease | Mouse enter/leave |
| Button active (scale) | 100ms | ease-in | Mouse down/up |
| Card hover (shadow) | 200ms | ease-out | Mouse enter/leave |
| Sidebar expand/collapse | 250ms | ease-in-out | Toggle click |
| Drawer slide-in | 350ms | cubic-bezier(0.16, 1, 0.3, 1) | Open trigger |
| Drawer slide-out | 250ms | ease-in | Close trigger |
| Modal backdrop | 200ms | ease | Open/close |
| Modal scale | 250ms | cubic-bezier(0.16, 1, 0.3, 1) | Open |
| Toast slide-in | 300ms | cubic-bezier(0.16, 1, 0.3, 1) | Notification trigger |
| Toast fade-out | 200ms | ease-in | Dismiss |
| Dropdown open | 150ms | ease-out | Click trigger |
| Dropdown close | 100ms | ease-in | Click/escape |
| Progress bar fill | 300ms | ease-out | Value change |
| Skeleton shimmer | 1500ms | linear (loop) | Loading state |
| Low-confidence pulse | 2000ms | ease-in-out (loop) | State indication |
| Score gauge fill | 800ms | cubic-bezier(0.16, 1, 0.3, 1) | Initial render |
| Tab switch content | 150ms | ease | Tab click |
| Tooltip appear | 100ms | ease-out | Hover (200ms delay) |
| Tooltip disappear | 75ms | ease-in | Mouse leave |

**Reduced motion:** Respect `prefers-reduced-motion: reduce`. When enabled: disable skeleton shimmer, pulse animations, gauge fill animation. Reduce all transitions to instant (0ms) or 100ms maximum. Drawers and modals still animate at reduced duration (150ms).

---

## 14. Design Tokens Summary

All tokens are organized for export to Tailwind CSS config and CSS custom properties.

### 14.1 Token Naming Convention

```
--velora-{category}-{property}-{variant}

Examples:
--velora-color-primary-500
--velora-color-risk-critical-badge
--velora-font-size-heading-h1
--velora-spacing-6
--velora-shadow-md
--velora-radius-lg
```

### 14.2 Tailwind CSS Integration

```javascript
// tailwind.config.ts (excerpt)
{
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#F0F1FA',
          100: '#DCDFF5',
          200: '#B5BAEC',
          300: '#8E95E0',
          400: '#6B74D4',
          500: '#4A54C4',
          600: '#3B44A6',
          700: '#2F3688',
          800: '#252A6B',
          900: '#1B1F4B',
        },
        'accent-teal': {
          50: '#EDF9FA',
          100: '#D4F0F2',
          400: '#3AB4BC',
          500: '#1A9199',
          600: '#147377',
          700: '#0F5B5E',
        },
        'accent-gold': {
          100: '#F5EDCF',
          400: '#D4B44E',
          500: '#BF9B3B',
          600: '#9A7B2F',
        },
        gray: {
          25: '#FBFBFD',
          50: '#F7F8FB',
          75: '#F2F3F8',
          100: '#ECEEF5',
          150: '#DFE2EC',
          200: '#D0D4E2',
          300: '#AEB3C7',
          400: '#8C92AA',
          500: '#6E7590',
          600: '#555B73',
          700: '#3E4359',
          800: '#2A2E42',
          900: '#1A1D2E',
          950: '#0D0F1C',
        },
        success: {
          50: '#EDFBF3',
          100: '#D4F5E2',
          500: '#22A05E',
          600: '#1A7A4B',
          700: '#15613C',
        },
        warning: {
          50: '#FEF8E8',
          100: '#FDF0CC',
          500: '#C4901A',
          600: '#9A7112',
          700: '#7A5A0B',
        },
        error: {
          50: '#FEF0F0',
          100: '#FCDCDC',
          500: '#D93636',
          600: '#B02424',
          700: '#8B1A1A',
        },
        info: {
          50: '#EDF5FC',
          100: '#D4E8F7',
          500: '#2D82C7',
          600: '#2264A0',
          700: '#1A4B7A',
        },
        ai: {
          purple: '#7B61FF',
          'purple-light': '#F3F0FF',
          'purple-border': '#D4CCFF',
        },
      },
      fontFamily: {
        heading: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
        body: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
        mono: ['JetBrains Mono', 'SF Mono', 'Fira Code', 'Cascadia Code', 'monospace'],
      },
      fontSize: {
        'display-lg': ['2.25rem', { lineHeight: '2.75rem', fontWeight: '700', letterSpacing: '-0.02em' }],
        'display-sm': ['1.875rem', { lineHeight: '2.375rem', fontWeight: '700', letterSpacing: '-0.015em' }],
        'heading-h1': ['1.5rem', { lineHeight: '2rem', fontWeight: '600', letterSpacing: '-0.01em' }],
        'heading-h2': ['1.25rem', { lineHeight: '1.75rem', fontWeight: '600', letterSpacing: '-0.005em' }],
        'heading-h3': ['1.0625rem', { lineHeight: '1.5rem', fontWeight: '600' }],
        'heading-h4': ['0.9375rem', { lineHeight: '1.375rem', fontWeight: '600' }],
        'body-lg': ['1rem', { lineHeight: '1.5rem', fontWeight: '400' }],
        'body-md': ['0.875rem', { lineHeight: '1.25rem', fontWeight: '400' }],
        'body-sm': ['0.8125rem', { lineHeight: '1.125rem', fontWeight: '400', letterSpacing: '0.005em' }],
        'caption': ['0.75rem', { lineHeight: '1rem', fontWeight: '400', letterSpacing: '0.01em' }],
        'overline': ['0.6875rem', { lineHeight: '1rem', fontWeight: '600', letterSpacing: '0.08em' }],
      },
      spacing: {
        'px': '1px',
        '0.5': '2px',
        '1': '4px',
        '1.5': '6px',
        '2': '8px',
        '3': '12px',
        '4': '16px',
        '5': '20px',
        '6': '24px',
        '8': '32px',
        '10': '40px',
        '12': '48px',
        '16': '64px',
        '20': '80px',
      },
      borderRadius: {
        'none': '0px',
        'sm': '4px',
        'md': '6px',
        'lg': '8px',
        'xl': '12px',
        '2xl': '16px',
        'full': '9999px',
      },
      boxShadow: {
        'xs': '0 1px 2px 0 rgba(27, 31, 75, 0.04)',
        'sm': '0 1px 3px 0 rgba(27, 31, 75, 0.06), 0 1px 2px -1px rgba(27, 31, 75, 0.04)',
        'md': '0 4px 8px -2px rgba(27, 31, 75, 0.06), 0 2px 4px -2px rgba(27, 31, 75, 0.04)',
        'lg': '0 12px 24px -4px rgba(27, 31, 75, 0.08), 0 4px 8px -4px rgba(27, 31, 75, 0.03)',
        'xl': '0 20px 40px -8px rgba(27, 31, 75, 0.10), 0 8px 16px -4px rgba(27, 31, 75, 0.04)',
        '2xl': '0 32px 64px -12px rgba(27, 31, 75, 0.14)',
        'inner': 'inset 0 1px 2px 0 rgba(27, 31, 75, 0.05)',
        'ring': '0 0 0 3px rgba(74, 84, 196, 0.15)',
      },
    },
  },
}
```

### 14.3 CSS Custom Properties (Root)

```css
:root {
  /* Sidebar */
  --velora-sidebar-width-expanded: 240px;
  --velora-sidebar-width-collapsed: 64px;

  /* Top bar */
  --velora-topbar-height: 56px;

  /* Content */
  --velora-content-max-width: 1440px;
  --velora-content-padding: 32px;

  /* Grid */
  --velora-grid-columns: 12;
  --velora-grid-gap: 24px;

  /* Z-index scale */
  --velora-z-dropdown: 100;
  --velora-z-sticky: 200;
  --velora-z-drawer: 300;
  --velora-z-modal-backdrop: 400;
  --velora-z-modal: 500;
  --velora-z-popover: 600;
  --velora-z-command-palette: 700;
  --velora-z-toast: 800;
  --velora-z-tooltip: 900;

  /* Transitions */
  --velora-transition-fast: 100ms ease;
  --velora-transition-base: 150ms ease;
  --velora-transition-slow: 250ms ease-in-out;
  --velora-transition-drawer: 350ms cubic-bezier(0.16, 1, 0.3, 1);
}
```

---

*End of Design System. This document provides the complete specification for implementing the Velora TPRM user interface. Every hex code, spacing value, and component state is defined for direct translation to code using Next.js 15, shadcn/ui, Tailwind CSS, and Radix UI primitives.*
