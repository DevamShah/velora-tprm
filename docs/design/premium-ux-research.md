# Premium SaaS UX Research Brief

> **Purpose**: Actionable design intelligence extracted from the best SaaS products of 2025-2026
> **Scope**: Linear, Vercel, Stripe, Notion, Raycast, Mercury, Ramp, Figma
> **Date**: 2026-03-27
> **Feeds into**: Velora TPRM frontend rebuild

---

## 1. Color Palette Recommendation

### The Problem with Generic SaaS Color

Most enterprise tools default to cold indigo/blue (#6366F1, #4F46E5). This reads as "another Tailwind default" and fails to differentiate. The best tools in 2025-2026 are moving toward **warm neutrals with restrained, purposeful accent color**.

### What the Top Tools Do

| Tool | Base Palette | Accent Strategy |
|------|-------------|----------------|
| **Linear** | Warm gray (moved away from blue-ish hue), near-black #16161D (Woodsmoke) | Minimal bold color; monochrome black/white with few accents |
| **Vercel** | Pure black #000000 / pure white #FFFFFF | Near-zero color; relies on typography and spacing |
| **Stripe** | Deep navy #0A2540 (Downriver), light gray #F6F9FC | Purple accent #635BFF (Cornflower Blue) |
| **Notion** | Warm off-white backgrounds, subtle neutral tones | Muted, almost pastel category colors |
| **Mercury** | Clean whites, sophisticated neutral grays | Minimal accent; financial confidence through restraint |
| **Ramp** | Neutral grays, clean white space | Green accents for financial positive states |

### Recommended Palette: "Warm Authority"

A warm, sophisticated palette that avoids both cold corporate blue AND generic indigo.

```
-- BACKGROUNDS --
bg-primary:       #0C0A09    -- Warm near-black (stone-950, NOT blue-black)
bg-secondary:     #1C1917    -- Warm dark (stone-900)
bg-tertiary:      #292524    -- Warm elevated (stone-800)
bg-surface:       #44403C    -- Card/panel surface (stone-700)
bg-hover:         #57534E    -- Hover state (stone-600)

-- LIGHT MODE BACKGROUNDS --
bg-light:         #FAFAF9    -- Warm off-white (stone-50, NOT pure white)
bg-light-surface: #F5F5F4    -- Card surface light (stone-100)
bg-light-hover:   #E7E5E4    -- Hover light (stone-200)

-- TEXT --
text-primary:     #FAFAF9    -- Primary text dark mode (stone-50)
text-secondary:   #A8A29E    -- Secondary text (stone-400)
text-tertiary:    #78716C    -- Tertiary/muted (stone-500)
text-light-primary: #1C1917  -- Primary text light mode (stone-900)
text-light-secondary: #57534E -- Secondary text light (stone-600)

-- ACCENT: AMBER (warm, premium, NOT blue) --
accent-primary:   #F59E0B    -- Amber-500: primary actions, key CTA
accent-hover:     #D97706    -- Amber-600: hover state
accent-muted:     #FEF3C7    -- Amber-100: subtle highlights, badges
accent-subtle:    #78350F    -- Amber-900: dark mode subtle accent bg

-- SEMANTIC --
success:          #10B981    -- Emerald-500 (NOT green-500, warmer)
success-muted:    #D1FAE5    -- Emerald-100
warning:          #F59E0B    -- Amber-500
warning-muted:    #FEF3C7    -- Amber-100
danger:           #EF4444    -- Red-500
danger-muted:     #FEE2E2    -- Red-100
info:             #8B5CF6    -- Violet-500 (premium feel, NOT blue)
info-muted:       #EDE9FE    -- Violet-100

-- BORDERS --
border-default:   #292524    -- Stone-800 (dark mode)
border-subtle:    #1C1917    -- Stone-900 (barely visible)
border-light:     #E7E5E4    -- Stone-200 (light mode)
```

### Why This Works

- **Stone over Slate/Zinc**: Stone has warm undertones (slight yellow/brown). Slate is blue-cool. Zinc is pure neutral. Stone reads as "luxury leather" while Slate reads as "enterprise software."
- **Amber over Blue**: Amber conveys warmth, premium quality, and confidence. It pairs beautifully with warm grays and avoids the "generic SaaS" trap.
- **Violet for info**: Instead of the standard blue info state, violet adds sophistication and distinguishes from commodity patterns.

---

## 2. Typography

### What Premium Tools Use

| Tool | Primary Font | Weight Strategy |
|------|-------------|----------------|
| **Linear** | Inter, system stack (-apple-system, SF Pro) | Minimal weights: 400, 500, 600 |
| **Vercel** | Geist Sans (custom), Geist Mono | Tight tracking, deliberate weight |
| **Stripe** | Custom (Stripe-specific), system fallback | Clear hierarchy, generous line-height |
| **Notion** | System fonts, custom serif for content | Mix of sans-serif UI + serif content |
| **Raycast** | SF Pro, Inter fallback | Medium weight dominant |

### Recommendation

```
-- FONT STACK --
primary:     "Inter", -apple-system, BlinkMacSystemFont, system-ui, sans-serif
mono:        "JetBrains Mono", "Fira Code", ui-monospace, monospace

-- SCALE (based on Linear's 8px grid) --
text-xs:     12px / 16px (0.75rem)   -- Labels, metadata
text-sm:     14px / 20px (0.875rem)  -- Body text, table cells
text-base:   16px / 24px (1rem)      -- Default body
text-lg:     18px / 28px (1.125rem)  -- Section headers
text-xl:     20px / 28px (1.25rem)   -- Page sub-headers
text-2xl:    24px / 32px (1.5rem)    -- Page headers
text-3xl:    30px / 36px (1.875rem)  -- Dashboard hero metrics

-- WEIGHT USAGE --
400 (regular):  Body text, descriptions, table cells
500 (medium):   Labels, navigation items, secondary emphasis
600 (semibold): Headings, metric values, primary emphasis
700 (bold):     NEVER in UI (too heavy; reserve for marketing only)

-- TRACKING --
-0.01em:  Body text (slightly tighter than browser default)
-0.02em:  Headings (tighter for display sizes)
-0.03em:  Hero metrics (tight tracking on large numbers)
```

### Key Principle

Linear and Vercel prove that **fewer weights used with more intention** creates a more premium feel than using many weights. Limit to 3 weights maximum (400, 500, 600).

---

## 3. Animation Patterns (Framer Motion)

### Core Philosophy

Extracted from Linear, Vercel, and Stripe: **Animation should be felt, not seen.** The best SaaS tools use animation to communicate state changes and spatial relationships, never for decoration.

### Performance Rule

Stick to `transform` and `opacity` only. These properties animate on the GPU compositor thread and maintain 60fps. Never animate `width`, `height`, `margin`, or `padding`.

### Pattern 1: Page/View Transitions

```tsx
// Wrap route content with AnimatePresence
import { AnimatePresence, motion } from "motion/react";

const pageVariants = {
  initial: { opacity: 0, y: 8 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -4 },
};

const pageTransition = {
  type: "tween",
  ease: [0.25, 0.1, 0.25, 1], // cubic-bezier (same as CSS ease)
  duration: 0.2,
};

<AnimatePresence mode="wait">
  <motion.div
    key={pathname}
    variants={pageVariants}
    initial="initial"
    animate="animate"
    exit="exit"
    transition={pageTransition}
  >
    {children}
  </motion.div>
</AnimatePresence>
```

### Pattern 2: Staggered List/Card Entry

```tsx
// Container orchestrates children
const containerVariants = {
  hidden: {},
  visible: {
    transition: {
      staggerChildren: 0.04,  // 40ms between each child
      delayChildren: 0.1,     // 100ms before first child
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 12 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      type: "spring",
      stiffness: 300,
      damping: 24,
    },
  },
};

<motion.div variants={containerVariants} initial="hidden" animate="visible">
  {items.map((item) => (
    <motion.div key={item.id} variants={itemVariants}>
      <Card {...item} />
    </motion.div>
  ))}
</motion.div>
```

### Pattern 3: Metric Card Number Animation

```tsx
// Animate numbers counting up (dashboard KPIs)
import { useMotionValue, useTransform, animate } from "motion/react";
import { useEffect } from "react";

function AnimatedMetric({ value }: { value: number }) {
  const count = useMotionValue(0);
  const rounded = useTransform(count, (v) => Math.round(v));

  useEffect(() => {
    const controls = animate(count, value, {
      duration: 0.8,
      ease: [0.25, 0.1, 0.25, 1],
    });
    return controls.stop;
  }, [value]);

  return <motion.span>{rounded}</motion.span>;
}
```

### Pattern 4: Hover Micro-interactions

```tsx
// Button hover: subtle scale + shadow lift
<motion.button
  whileHover={{ scale: 1.02, y: -1 }}
  whileTap={{ scale: 0.98 }}
  transition={{ type: "spring", stiffness: 400, damping: 17 }}
>
  {children}
</motion.button>

// Card hover: lift with shadow
<motion.div
  whileHover={{
    y: -2,
    boxShadow: "0 8px 30px rgba(0, 0, 0, 0.12)",
  }}
  transition={{ type: "spring", stiffness: 300, damping: 20 }}
>
  <Card />
</motion.div>

// Table row hover: background fade
<motion.tr
  whileHover={{ backgroundColor: "rgba(255, 255, 255, 0.03)" }}
  transition={{ duration: 0.15 }}
/>
```

### Pattern 5: Expandable Panels / Accordions

```tsx
// Smooth height animation with layout
<motion.div
  layout
  initial={{ opacity: 0, height: 0 }}
  animate={{ opacity: 1, height: "auto" }}
  exit={{ opacity: 0, height: 0 }}
  transition={{
    height: { type: "spring", stiffness: 300, damping: 30 },
    opacity: { duration: 0.2 },
  }}
/>
```

### Pattern 6: Skeleton Loading Transition

```tsx
// Skeleton pulse + content fade-in
const skeletonVariants = {
  loading: {
    opacity: [0.4, 0.7, 0.4],
    transition: { duration: 1.5, repeat: Infinity, ease: "easeInOut" },
  },
};

const contentVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { duration: 0.3, ease: "easeOut" },
  },
};
```

### Pattern 7: Sidebar Collapse

```tsx
// Sidebar width transition
<motion.aside
  animate={{ width: collapsed ? 60 : 240 }}
  transition={{ type: "spring", stiffness: 300, damping: 30 }}
>
  <motion.span
    animate={{ opacity: collapsed ? 0 : 1 }}
    transition={{ duration: collapsed ? 0.1 : 0.2, delay: collapsed ? 0 : 0.1 }}
  >
    {label}
  </motion.span>
</motion.aside>
```

### Accessibility

```tsx
// Always respect reduced motion preference
import { MotionConfig } from "motion/react";

<MotionConfig reducedMotion="user">
  <App />
</MotionConfig>
```

### Bundle Optimization

```tsx
// Use LazyMotion to cut bundle size (~15kb instead of ~30kb)
import { LazyMotion, domAnimation, m } from "motion/react";

<LazyMotion features={domAnimation}>
  <m.div animate={{ opacity: 1 }} />
</LazyMotion>
```

---

## 4. Key Design Principles from Top Tools

### 4.1 Linear: "Calm Density"

- **Reduces visual weight** of non-primary elements. Navigation sidebars are slightly dimmer than main content.
- **8px spacing grid** creates consistent rhythm across all components.
- **Monochrome-first**: Color is earned, not default. Most of the UI is grayscale; color only appears for status, priority, or interactive elements.
- **Keyboard-first**: Command palette (Cmd+K) is the primary navigation pattern for power users.
- **Custom design system (Orbiter)**: Modular components designed for specific content formats rather than generic layouts.

### 4.2 Vercel: "Brutal Simplicity"

- **Near-zero decoration**: No gradients, no shadows, no rounded corners on most elements. Typography and spacing do all the work.
- **Semantic color tokens**: Colors are named by function (positive, negative, warning), not appearance. This makes dark/light mode switching trivial.
- **Geist font family**: Custom-designed for UI density. Tighter tracking than Inter at small sizes.
- **Data-forward**: Deployment status, build logs, and metrics are immediately visible. Zero clicks to see status.

### 4.3 Stripe: "Trust Through Craft"

- **Deep navy (#0A2540)** as primary background communicates financial trust.
- **Accessible by design**: Built an entire accessible color system ensuring all text/icon colors pass WCAG 2.0 with consistent visual weight across hues.
- **Progressive disclosure**: Complex financial data is layered. Summary view is always one click away from detail view.
- **Micro-animations on charts**: Data visualizations animate on entry, drawing the eye to the most important metrics.

### 4.4 Notion: "Elegant Neutrality"

- **Content is the interface**: The chrome disappears. Minimal UI elements, maximum content area.
- **Warm typography**: Uses serif fonts for content (creating a "paper" feel) with sans-serif for UI controls.
- **Monochrome empty states**: Simple illustrations that blend into the interface rather than demanding attention.
- **Slash-command pattern**: Type "/" to access any block type. Reduces toolbar clutter to near zero.

### 4.5 Figma: "Floating UI"

- **Bottom toolbar**: Primary tools float at the bottom of the viewport, not top. Maximizes canvas area.
- **Panel resizing**: Side panels are resizable and collapsible independently.
- **Quick Actions (Cmd+/)**: Command palette as primary navigation for power users.
- **Context-sensitive UI**: Right panel changes entirely based on selection, reducing permanent UI weight.

### 4.6 Mercury: "Financial Confidence"

- **Extreme whitespace**: Financial data needs room to breathe. Dense tables are broken by generous padding.
- **Premium card metaphors**: Physical card rendered with metallic shimmer, subtle morphing animations.
- **One-click workflows**: Bill pay, transfers, and approvals designed for minimal friction.

---

## 5. Component Patterns

### 5.1 Cards

**What premium tools do differently from generic templates:**

```
-- PREMIUM CARD (Linear/Stripe style) --
background:     bg-surface (warm gray, NOT white)
border:         1px solid border-subtle (barely visible, NOT gray-300)
border-radius:  8px (NOT 12px+ which reads as "playful")
padding:        20px (generous, NOT cramped 12px)
shadow:         none at rest (shadow only on hover/elevation)
hover:          translateY(-2px) + subtle shadow fade-in

-- GENERIC TEMPLATE CARD (what to avoid) --
background:     white
border:         1px solid #e5e7eb (too visible)
border-radius:  16px (too rounded)
padding:        12px (too tight)
shadow:         always-on drop shadow (flat hierarchy)
hover:          just color change (no spatial movement)
```

**Key differences:**
- Premium cards use **elevation changes on interaction** (y-translate + shadow) rather than static shadows
- Border radius is restrained: 6-8px, not 12-16px
- Borders are barely visible or absent in dark mode; surface color differentiation handles separation
- Internal spacing is generous (20-24px) creating breathing room

### 5.2 Data Tables

**Premium table patterns (from Linear, Stripe, Ramp):**

```
-- STRUCTURE --
Header:         Sticky, slightly darker background, uppercase text-xs, font-500, letter-spacing: 0.05em
Row height:     44-48px (enough for comfortable click targets)
Row hover:      Subtle background shift (150ms transition), no delay
Row border:     Bottom border only, barely visible (border-subtle)
Cell padding:   12px horizontal, vertically centered

-- INTERACTIONS --
Sortable:       Header text + subtle chevron icon, bold on active sort
Selectable:     Checkbox column (left), appears on hover OR always visible
Inline actions: Appear on row hover (right-aligned), max 2-3 icons
Bulk actions:   Sticky bar appears at bottom when rows selected

-- ADVANCED --
Virtual scroll:  Mandatory for 100+ rows
Frozen columns:  First column (name/identifier) stays fixed on horizontal scroll
Empty state:     Centered illustration + single CTA, not "No data found" text
Loading:         Skeleton rows (3-5 rows of animated gray bars), NOT spinner
```

### 5.3 Navigation Sidebar

**Premium pattern (Linear/Notion style):**

```
-- LAYOUT --
Width:           240px expanded, 60px collapsed
Background:      Slightly darker than main content (1-2 steps darker)
Collapse:        Spring animation (stiffness: 300, damping: 30)
Icon-only mode:  Tooltips on hover when collapsed

-- ITEMS --
Item height:     36px
Item padding:    8px 12px
Item radius:     6px
Active state:    Filled background (accent-muted), filled icon variant
Hover state:     Subtle background (bg-hover), 150ms transition
Icon size:       18px (NOT 24px -- smaller icons feel more refined)
Icon-label gap:  10px
Font:            text-sm, font-500

-- SECTIONS --
Section label:   text-xs, font-500, uppercase, text-tertiary, letter-spacing: 0.05em
Section gap:     16px between sections
Dividers:        None (spacing handles separation, NOT lines)

-- BOTTOM --
User profile:    Avatar + name at bottom
Settings:        Gear icon, secondary emphasis
Collapse toggle: Chevron icon at bottom or top
```

### 5.4 Buttons

```
-- PRIMARY --
bg:              accent-primary (amber-500)
text:            #0C0A09 (dark text on amber, NOT white)
padding:         8px 16px
radius:          6px
font:            text-sm, font-500
hover:           accent-hover + scale(1.02) + translateY(-1px)
active:          scale(0.98)
transition:      spring (stiffness: 400, damping: 17)

-- SECONDARY --
bg:              transparent
border:          1px solid border-default
text:            text-primary
hover:           bg-hover background

-- GHOST --
bg:              transparent
border:          none
text:            text-secondary
hover:           bg-hover background, text-primary color

-- DESTRUCTIVE --
bg:              danger
text:            white
hover:           danger darkened 10%
```

### 5.5 Metric Cards (Dashboard KPIs)

```
-- LAYOUT --
Grid:            3-4 cards per row, equal width
Padding:         24px
Gap:             16px between cards

-- CONTENT --
Label:           text-xs, font-500, text-secondary, uppercase tracking-wide
Value:           text-3xl, font-600, text-primary, tracking-tight
Trend:           text-sm, font-500, success/danger color, with arrow icon
Sparkline:       Optional, 48px height, accent color, no axis labels
Sub-text:        text-xs, text-tertiary, "vs last period"

-- ANIMATION --
Number:          Count-up animation on mount (0.8s, ease-out)
Card:            Stagger entry (40ms between cards, spring)
Trend arrow:     Fade-in with slight translateY
```

### 5.6 Empty States

**Premium approach (Notion/Linear style):**

```
-- LAYOUT --
Centered vertically and horizontally in the content area
Max-width: 400px

-- CONTENT --
Illustration:   Monochrome, simple, brand-consistent (NOT colorful stock art)
Heading:        text-lg, font-600, text-primary
Description:    text-sm, text-secondary, 1-2 sentences max
CTA:            Primary button, single clear action
Secondary:      Text link for "learn more" (optional)

-- WHAT TO AVOID --
"No data found" with no illustration
Multiple CTAs competing for attention
Generic placeholder icons
```

### 5.7 Loading States

```
-- SKELETON SCREENS (primary pattern) --
Shape:          Matches the content it replaces (rounded rect for text, circle for avatar)
Color:          bg-surface with subtle pulse animation
Pulse:          opacity oscillates between 0.4 and 0.7 over 1.5s
Rows:           Show 3-5 skeleton rows (NOT full page of skeletons)
Transition:     Skeleton fades out (200ms) as real content fades in (300ms)

-- NEVER USE --
Full-page spinners (feels broken)
Loading text without visual indicator
Skeleton that doesn't match actual content layout
```

---

## 6. What Differentiates "Premium" from "Generic"

### The 10 Signals of Premium SaaS UI

1. **Warm neutrals over cold grays**: Stone/warm-gray base instead of slate/zinc/cool-gray. This single change transforms the entire feel.

2. **Restrained color**: Color is earned. 90% of the interface is grayscale. Color appears only for: status indicators, interactive elements, and data visualization. Generic templates color everything.

3. **Spatial micro-interactions**: Premium tools move elements in space (translateY, scale) on hover. Generic templates only change color. The physical metaphor of "lifting" a card creates perceived depth and quality.

4. **Typography does the heavy lifting**: Premium tools differentiate hierarchy through weight and size, NOT through color or decoration. Fewer weights (3 max), used consistently.

5. **Generous spacing**: Premium tools use 20-24px card padding, 16-24px section gaps. Generic templates use 12px padding and feel cramped. Whitespace is the single highest-leverage "premium" signal.

6. **Invisible borders**: In dark mode, surface color differentiation replaces visible borders. In light mode, borders are 1px and barely visible (stone-200, not gray-300).

7. **Skeleton loading over spinners**: Every premium tool uses skeleton screens that match content layout. Spinners feel like 2015.

8. **Spring physics over linear easing**: `type: "spring"` with appropriate stiffness/damping feels organic and alive. `transition: 0.3s ease` feels robotic.

9. **Progressive disclosure**: Settings, advanced options, and configuration are hidden behind intentional actions (command palette, expandable sections). The default view is clean.

10. **Keyboard-first design**: Command palette (Cmd+K), keyboard shortcuts for all major actions, focus indicators. Power users should never need the mouse for navigation.

### The Anti-Patterns (What Generic Templates Do Wrong)

- Visible borders on everything (creates a "cage" feel)
- 12-16px border radius on cards (reads as "toy")
- Always-on drop shadows (flattens hierarchy)
- Blue accent color on everything (#6366F1 is the new Bootstrap blue)
- Spinner-only loading states
- 12px internal padding on cards (cramped)
- Bold (700) weight in UI text (too heavy)
- Colorful sidebar with bright active states (distracting)
- Generic "No data" empty states without illustration
- Linear easing (ease, ease-in-out) instead of spring physics

---

## 7. Tailwind CSS Implementation Notes

### Custom Animation Utilities (Tailwind v4)

```css
@theme {
  /* Skeleton pulse */
  --animate-skeleton: skeleton 1.5s ease-in-out infinite;

  /* Fade in up (card entry) */
  --animate-fade-in-up: fade-in-up 0.3s ease-out forwards;

  /* Slide in from right (panel) */
  --animate-slide-in-right: slide-in-right 0.2s ease-out forwards;

  /* Count up shimmer (metric values) */
  --animate-shimmer: shimmer 2s linear infinite;

  @keyframes skeleton {
    0%, 100% { opacity: 0.4; }
    50% { opacity: 0.7; }
  }

  @keyframes fade-in-up {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
  }

  @keyframes slide-in-right {
    from { opacity: 0; transform: translateX(16px); }
    to { opacity: 1; transform: translateX(0); }
  }

  @keyframes shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
  }
}
```

### shadcn/ui Customization Strategy

1. **Override the default color tokens** with the warm Stone palette above (replace default Zinc/Slate)
2. **Reduce default border-radius** from 0.5rem to 0.375rem (6px) for a more professional feel
3. **Use tweakcn** or the official theme editor to generate CSS variables, then hand-tune
4. **Extend with custom variants**: Add `data-[state=active]` styles for sidebar items, `data-[loading]` for skeleton states
5. **Tailwind v4 compatibility**: shadcn/ui CLI auto-detects Tailwind version as of early 2026

### Recommended shadcn/ui Component Overrides

```css
/* globals.css - key overrides */
:root {
  --radius: 0.375rem;              /* 6px, down from default 0.5rem */
  --background: 28 25% 3%;         /* stone-950 in HSL */
  --foreground: 60 9% 98%;         /* stone-50 */
  --card: 20 14% 10%;              /* stone-900 */
  --card-foreground: 60 9% 98%;    /* stone-50 */
  --primary: 38 92% 50%;           /* amber-500 */
  --primary-foreground: 20 14% 4%; /* dark text on amber */
  --muted: 24 6% 16%;              /* stone-800 */
  --muted-foreground: 24 6% 63%;   /* stone-400 */
  --border: 24 6% 16%;             /* stone-800, subtle */
  --ring: 38 92% 50%;              /* amber-500 focus ring */
}
```

---

## 8. Motion Library Decision

### Recommendation: Framer Motion (motion/react) v12.x

**Why:**
- De facto standard for React/Next.js animation (largest ecosystem)
- Variants system perfectly matches component-driven architecture
- AnimatePresence solves exit animations (critical for page transitions)
- Spring physics built-in (no manual bezier curves)
- LazyMotion cuts bundle to ~15kb
- `MotionConfig reducedMotion="user"` for automatic a11y compliance
- Rebranded to `motion` (import from `motion/react` as of late 2024)

**Bundle strategy:**
- Use `LazyMotion` with `domAnimation` feature set (~15kb)
- Only import `domMax` (~30kb) if layout animations are needed
- Use `m` components inside LazyMotion instead of `motion` components

**Spring presets to standardize:**

```ts
export const springs = {
  snappy:  { type: "spring", stiffness: 400, damping: 17 },  // buttons, toggles
  smooth:  { type: "spring", stiffness: 300, damping: 24 },  // cards, panels
  gentle:  { type: "spring", stiffness: 200, damping: 20 },  // page transitions
  bouncy:  { type: "spring", stiffness: 500, damping: 15 },  // playful (use sparingly)
} as const;

export const durations = {
  instant: { duration: 0.1 },   // hover color changes
  fast:    { duration: 0.15 },  // tooltips, dropdowns
  normal:  { duration: 0.2 },   // panels, modals
  slow:    { duration: 0.3 },   // page transitions
} as const;
```

---

## 9. Implementation Priority

### Phase 1: Foundation (Immediate Impact)
1. Replace color tokens with warm Stone palette + Amber accent
2. Set border-radius to 6px globally
3. Add `MotionConfig` wrapper with reduced motion support
4. Implement skeleton loading components
5. Standardize typography scale (3 weights: 400, 500, 600)

### Phase 2: Interactions (Perceived Quality)
1. Staggered entry animations on lists/grids
2. Card hover micro-interactions (translateY + shadow)
3. Page transition animations with AnimatePresence
4. Button hover/tap spring animations
5. Sidebar collapse animation

### Phase 3: Polish (Premium Feel)
1. Animated metric counters on dashboard
2. Chart entry animations
3. Empty state illustrations (monochrome, brand-consistent)
4. Command palette (Cmd+K) for power users
5. Keyboard shortcut indicators on tooltips

---

## Sources

- [Linear UI Refresh (March 2026)](https://linear.app/changelog/2026-03-12-ui-refresh)
- [Linear Design Refresh - Behind the Scenes](https://linear.app/now/behind-the-latest-design-refresh)
- [Linear Design: The SaaS Trend (LogRocket)](https://blog.logrocket.com/ux-design/linear-design/)
- [Linear Design System (Figma)](https://www.figma.com/community/file/1222872653732371433/linear-design-system)
- [Vercel Geist Colors](https://vercel.com/geist/colors)
- [Vercel Geist Design System (Figma)](https://www.figma.com/community/file/1330020847221146106/geist-design-system-vercel)
- [Stripe Accessible Color Systems](https://stripe.com/blog/accessible-color-systems)
- [Stripe Brand Colors (Mobbin)](https://mobbin.com/colors/brand/stripe)
- [Mercury Dashboard (SaaSFrame)](https://www.saasframe.io/examples/mercury-dashboard)
- [Mercury Design Analysis (UX Planet)](https://uxplanet.org/captivating-design-of-the-mercury-fintech-app-d472bc0288bb)
- [Figma UI3 Design Approach](https://www.figma.com/blog/our-approach-to-designing-ui3/)
- [Framer Motion Complete Guide 2026](https://inhaq.com/blog/framer-motion-complete-guide-react-nextjs-developers)
- [Motion.dev Documentation](https://motion.dev/)
- [SaaS UI Design Trends 2026](https://www.saasui.design/blog/7-saas-ui-design-trends-2026)
- [SaaS Dashboard Design 2026 (SaaSFrame)](https://www.saasframe.io/blog/the-anatomy-of-high-performance-saas-dashboard-design-2026-trends-patterns)
- [Premium SaaS Color Palettes (Produkto)](https://produkto.io/color-palettes/saas)
- [shadcn/ui Theming](https://ui.shadcn.com/docs/theming)
- [tweakcn Theme Editor](https://tweakcn.com/)
- [Tailwind CSS Animation Utilities](https://tailwindcss.com/docs/animation)
- [Data Table UX Patterns (Pencil & Paper)](https://www.pencilandpaper.io/articles/ux-pattern-analysis-enterprise-data-tables)
- [Sidebar Design Best Practices 2026](https://www.alfdesigngroup.com/post/improve-your-sidebar-design-for-web-apps)
- [Micro-interactions in Web Design 2025](https://www.stan.vision/journal/micro-interactions-2025-in-web-design)
- [SaaS Design Trends 2026 (DesignStudioUIUX)](https://www.designstudiouiux.com/blog/top-saas-design-trends/)
- [Design System Trends 2026](https://designsignal.ai/articles/design-systems-trends-2026)
