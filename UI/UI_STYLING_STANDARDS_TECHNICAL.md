# UI Styling Standards - Technical Specification

**Version:** 1.0.0  
**Last Updated:** November 15, 2025  
**Status:** Production Standard  
**Scope:** All UI components across AI Agents platform

---

## Table of Contents

1. [Spacing System](#spacing-system)
2. [Z-Index Layering](#z-index-layering)
3. [Component Dimensions](#component-dimensions)
4. [Color System](#color-system)
5. [Typography Scale](#typography-scale)
6. [Animation & Transitions](#animation--transitions)
7. [Touch Targets & Accessibility](#touch-targets--accessibility)
8. [Layout Grid System](#layout-grid-system)
9. [Component-Specific Standards](#component-specific-standards)
10. [Responsive Breakpoints](#responsive-breakpoints)

---

## 1. Spacing System

### Base Unit: 8px Grid

**Principle:** All spacing MUST be multiples of 4px or 8px (Material Design standard)

**Rationale:**
- Industry standard used by Google Material, Atlassian, Bootstrap, GitHub Primer
- Ensures visual consistency across components
- Simplifies responsive design calculations
- Improves alignment across different screen densities

### Spacing Scale (CSS Custom Properties)

```css
/* BASE UNIT */
--space-base: 8px;

/* MICRO SPACING (0px - 8px) - Use for compact UI */
--space-0: 0px;
--space-025: 2px;   /* 25% of base (icons, borders) */
--space-050: 4px;   /* 50% of base (tight padding) */
--space-075: 6px;   /* 75% of base (small gaps) */
--space-100: 8px;   /* 100% base unit */

/* SMALL SPACING (12px - 24px) - Use for standard UI */
--space-150: 12px;  /* 150% of base (button padding) */
--space-200: 16px;  /* 200% of base (card padding) */
--space-250: 20px;  /* 250% of base (section gaps) */
--space-300: 24px;  /* 300% of base (large padding) */

/* MEDIUM SPACING (32px - 48px) - Use for layout */
--space-400: 32px;  /* 400% of base (section spacing) */
--space-500: 40px;  /* 500% of base (page margins) */
--space-600: 48px;  /* 600% of base (large sections) */

/* LARGE SPACING (64px - 80px) - Use for major layout */
--space-800: 64px;  /* 800% of base (major sections) */
--space-1000: 80px; /* 1000% of base (page headers) */

/* NEGATIVE SPACING (for optical adjustments) */
--space-neg-025: -2px;
--space-neg-050: -4px;
--space-neg-100: -8px;
--space-neg-200: -16px;
```

### Usage Guidelines

#### Micro Spacing (0-8px)
**Use for:**
- Icon-text gaps: `--space-050` (4px) or `--space-075` (6px)
- Small component padding: badges, tags, pills
- Border widths: `--space-025` (2px)
- Tight button groups
- Table cell padding: `--space-075` (6px) to `--space-100` (8px)
- Input field internal padding: `--space-100` (8px)

```css
/* Example: Badge */
.badge {
    padding: var(--space-050) var(--space-100); /* 4px 8px */
    gap: var(--space-050); /* 4px between icon and text */
}
```

#### Small Spacing (12-24px)
**Use for:**
- Button padding: `--space-150` (12px) to `--space-200` (16px)
- Card internal padding: `--space-200` (16px) to `--space-300` (24px)
- List item gaps: `--space-150` (12px)
- Form field spacing: `--space-200` (16px)
- Dropdown menu padding: `--space-150` (12px)

```css
/* Example: Button */
.btn-primary {
    padding: var(--space-150) var(--space-300); /* 12px 24px */
}

/* Example: Card */
.card {
    padding: var(--space-300); /* 24px all sides */
    gap: var(--space-200); /* 16px between elements */
}
```

#### Medium Spacing (32-48px)
**Use for:**
- Section spacing between major UI blocks
- Page content margins
- Modal dialog padding
- Sidebar padding: `--space-400` (32px)
- Header/footer heights: `--space-600` (48px)

```css
/* Example: Page Section */
.page-section {
    padding: var(--space-400) 0; /* 32px top/bottom */
    margin-bottom: var(--space-500); /* 40px between sections */
}
```

#### Large Spacing (64-80px)
**Use for:**
- Major page sections (hero to content)
- Empty state padding
- Full-page modal margins
- Dashboard panel spacing

```css
/* Example: Hero Section */
.hero {
    padding: var(--space-800) 0; /* 64px top/bottom */
}
```

### Negative Spacing
**Use for:**
- Breaking out of container padding (Bleed effect)
- Overlapping elements (e.g., avatar on card edge)
- Optical adjustments for visual balance

```css
/* Example: Overlapping Avatar */
.avatar-overlap {
    margin-left: var(--space-neg-200); /* -16px overlap */
}
```

---

## 2. Z-Index Layering

### Industry Standard Stack (Bootstrap Model)

**Principle:** Use predefined z-index values in increments of 10-100 to allow for future insertions

**Rationale:**
- Prevents z-index wars ("just add 99999")
- Maintains clear visual hierarchy
- Allows for intermediate layers if needed
- Based on Bootstrap 5.3 standard (battle-tested)

### Z-Index Scale

```css
/* BASE LAYER (0-10) - Page content */
--z-base: 0;
--z-content: 1;        /* Main content area */
--z-elevated: 2;       /* Slightly raised elements (hover states) */
--z-focus: 3;          /* Focused/active elements */

/* NAVIGATION LAYER (1000-1099) - Primary UI */
--z-dropdown: 1000;    /* Dropdown menus */
--z-sticky: 1020;      /* Sticky headers/footers */
--z-fixed: 1030;       /* Fixed position elements */
--z-sidebar: 1040;     /* Side panels/drawers */

/* OVERLAY LAYER (2000-2099) - Temporary UI */
--z-overlay-backdrop: 2040; /* Semi-transparent backdrop */
--z-overlay-panel: 2045;    /* Overlay panels (prompt library) */
--z-modal-backdrop: 2050;   /* Modal backdrop */
--z-modal: 2055;            /* Modal dialogs */

/* NOTIFICATION LAYER (3000-3099) - Highest priority */
--z-popover: 3070;     /* Popovers */
--z-tooltip: 3080;     /* Tooltips */
--z-toast: 3090;       /* Toast notifications */
--z-alert: 3095;       /* Critical alerts */

/* DEBUG LAYER (9999) - Development only */
--z-debug: 9999;       /* Debug overlays (remove in production) */
```

### Component-to-Layer Mapping

| Component Type | Z-Index Value | CSS Variable | Use Case |
|---------------|---------------|--------------|----------|
| **Main chat interface** | 0 | `--z-base` | Base content layer |
| **Hover cards/tooltips (inline)** | 2-3 | `--z-elevated` / `--z-focus` | Small contextual hints |
| **Dropdown menus** | 1000 | `--z-dropdown` | Navigation dropdowns |
| **Sticky headers** | 1020 | `--z-sticky` | Headers that stick on scroll |
| **Sidebar (Prompt Library)** | 1040 | `--z-sidebar` | Side panels, drawers |
| **Backdrop (dimmed overlay)** | 2040 | `--z-overlay-backdrop` | Semi-transparent layer behind modals |
| **Overlay panels** | 2045 | `--z-overlay-panel` | Additional panels over sidebar |
| **Modal dialogs** | 2055 | `--z-modal` | Full modal windows |
| **Tooltips** | 3080 | `--z-tooltip` | Contextual tooltips |
| **Toast notifications** | 3090 | `--z-toast` | Success/error messages |

### Implementation Rules

#### Rule 1: Never Use Arbitrary Values
```css
/* ❌ BAD - Magic numbers */
.my-sidebar {
    z-index: 9999; /* What does this mean? */
}

/* ✅ GOOD - Semantic variables */
.my-sidebar {
    z-index: var(--z-sidebar); /* Clear intent */
}
```

#### Rule 2: Layer Relationships
```css
/* Backdrop must be below modal */
.modal-backdrop {
    z-index: var(--z-modal-backdrop); /* 2050 */
}

.modal-content {
    z-index: var(--z-modal); /* 2055 */
}
```

#### Rule 3: Stacking Context Awareness
When sidebar is open, overlay panels shift position but maintain z-index:

```css
/* Sidebar at 1040 */
.prompt-sidebar {
    z-index: var(--z-sidebar);
    position: fixed;
    right: 0;
}

/* Overlay at 2045 (higher than sidebar) */
.overlay-panel {
    z-index: var(--z-overlay-panel);
    position: fixed;
    right: 0; /* Default: right edge */
}

/* When sidebar is open, shift overlay left (not change z-index) */
.prompt-sidebar.show ~ .overlay-panel {
    right: 450px; /* Sidebar width */
    /* z-index stays at 2045 - doesn't change! */
}
```

---

## 3. Component Dimensions

### Standard Component Heights

**Principle:** Use consistent heights based on 4px/8px grid for vertical rhythm

```css
/* INPUT ELEMENTS */
--height-input-sm: 32px;   /* Small input (4 × 8px) */
--height-input-md: 40px;   /* Medium input (5 × 8px) */
--height-input-lg: 48px;   /* Large input (6 × 8px) */

/* BUTTONS */
--height-btn-sm: 32px;     /* Small button */
--height-btn-md: 40px;     /* Medium button (default) */
--height-btn-lg: 48px;     /* Large button */

/* NAVIGATION */
--height-navbar: 64px;     /* Top navigation bar (8 × 8px) */
--height-subnav: 48px;     /* Sub-navigation bar (6 × 8px) */
--height-tab-bar: 40px;    /* Tab bar height (5 × 8px) */

/* CARDS & PANELS */
--height-card-header: 56px; /* Card header (7 × 8px) */
--height-list-item-sm: 40px; /* Compact list item */
--height-list-item-md: 56px; /* Standard list item */
--height-list-item-lg: 72px; /* Large list item with subtitle */

/* STATUS INDICATORS */
--height-badge: 20px;      /* Badge height */
--height-tag: 24px;        /* Tag height (3 × 8px) */
--height-avatar-sm: 24px;  /* Small avatar */
--height-avatar-md: 32px;  /* Medium avatar */
--height-avatar-lg: 40px;  /* Large avatar */
--height-avatar-xl: 56px;  /* Extra large avatar */
```

### Standard Component Widths

```css
/* SIDEBARS & PANELS */
--width-sidebar-narrow: 280px;  /* Narrow sidebar (35 × 8px) */
--width-sidebar-standard: 450px; /* Standard sidebar (56.25 × 8px, GitHub Primer) */
--width-sidebar-wide: 600px;    /* Wide sidebar/overlay (75 × 8px) */

/* MODALS */
--width-modal-sm: 400px;   /* Small modal */
--width-modal-md: 600px;   /* Medium modal */
--width-modal-lg: 800px;   /* Large modal */
--width-modal-xl: 1000px;  /* Extra large modal */

/* DROPDOWNS */
--width-dropdown-min: 200px; /* Minimum dropdown width */
--width-dropdown-max: 400px; /* Maximum dropdown width */

/* INPUTS */
--width-input-sm: 120px;   /* Small input (e.g., zip code) */
--width-input-md: 240px;   /* Medium input (e.g., first name) */
--width-input-lg: 360px;   /* Large input (e.g., email) */
--width-input-full: 100%;  /* Full-width input */
```

### Touch Target Minimums (Accessibility)

**Material Design Standard:** 48×48 dp minimum

```css
/* MINIMUM TOUCH TARGETS */
--touch-target-min: 48px;  /* Minimum for any interactive element */
--touch-target-icon: 44px; /* Icon button minimum */

/* Examples */
.icon-button {
    width: var(--touch-target-icon);   /* 44px */
    height: var(--touch-target-icon);  /* 44px */
    padding: var(--space-100);         /* 8px internal padding */
}

.icon-button svg {
    width: 20px;  /* Visible icon size */
    height: 20px;
}
```

**Rule:** If visible element is smaller than 48px, expand clickable area with padding/margin:

```css
/* Visual: 32×32px, but touch target: 48×48px */
.small-button {
    width: 32px;
    height: 32px;
    padding: var(--space-100); /* +8px all sides = 48px touch area */
}
```

---

## 4. Color System

### Color Token Architecture

**Principle:** Use semantic color tokens, not raw hex values

**Three-Tier System:**
1. **Primitive tokens** - Base palette (hex values)
2. **Semantic tokens** - Purpose-based colors
3. **Component tokens** - Component-specific overrides

### Primitive Color Palette (GitHub Dark Theme Reference)

```css
/* GRAYS (GitHub Dark Scale) */
--gray-0: #f0f6fc;   /* Lightest */
--gray-1: #c9d1d9;   /* Light text */
--gray-2: #b1bac4;   /* Muted text */
--gray-3: #8b949e;   /* Subtle text */
--gray-4: #6e7681;   /* Placeholder */
--gray-5: #484f58;   /* Border */
--gray-6: #30363d;   /* Elevated surface */
--gray-7: #21262d;   /* Elevated surface darker */
--gray-8: #161b22;   /* Background secondary */
--gray-9: #0d1117;   /* Background primary (darkest) */

/* ACCENT COLORS (GitHub Primer) */
--blue: #58a6ff;     /* Primary actions, links */
--green: #3fb950;    /* Success, positive */
--yellow: #d29922;   /* Warning, caution */
--orange: #f78166;   /* Moderate warning */
--red: #f85149;      /* Danger, destructive */
--purple: #bc8cff;   /* Special, highlight */
--pink: #f778ba;     /* Creative, secondary */
```

### Semantic Color Tokens

```css
/* BACKGROUNDS */
--bg-primary: var(--gray-9);     /* #0d1117 - Main background */
--bg-secondary: var(--gray-8);   /* #161b22 - Secondary areas */
--bg-elevated: var(--gray-7);    /* #21262d - Cards, modals */
--bg-elevated-hover: var(--gray-6); /* #30363d - Hover states */

/* TEXT */
--text-primary: var(--gray-0);   /* #f0f6fc - Primary text */
--text-secondary: var(--gray-1); /* #c9d1d9 - Secondary text */
--text-muted: var(--gray-3);     /* #8b949e - Muted text */
--text-placeholder: var(--gray-4); /* #6e7681 - Placeholder text */

/* BORDERS */
--border-default: var(--gray-5); /* #484f58 - Default borders */
--border-muted: var(--gray-6);   /* #30363d - Subtle borders */
--border-strong: var(--gray-4);  /* #6e7681 - Strong borders */

/* ACCENTS (Semantic) */
--accent-primary: var(--blue);       /* Primary actions */
--accent-success: var(--green);      /* Success states */
--accent-warning: var(--yellow);     /* Warning states */
--accent-danger: var(--red);         /* Error/destructive states */
--accent-info: var(--purple);        /* Informational */
--accent-highlight: var(--pink);     /* Special highlights */

/* STATE COLORS (with alpha transparency) */
--color-success-bg: rgba(63, 185, 80, 0.1);   /* Light green bg */
--color-warning-bg: rgba(210, 153, 34, 0.1);  /* Light yellow bg */
--color-danger-bg: rgba(248, 81, 73, 0.1);    /* Light red bg */
--color-info-bg: rgba(88, 166, 255, 0.1);     /* Light blue bg */

/* OVERLAYS */
--overlay-backdrop: rgba(1, 4, 9, 0.6);       /* Semi-transparent black */
--overlay-backdrop-strong: rgba(1, 4, 9, 0.8); /* Darker backdrop */
```

### Component-Specific Color Tokens

```css
/* BUTTONS */
--btn-primary-bg: var(--accent-primary);
--btn-primary-text: var(--text-primary);
--btn-primary-hover: #4493e8; /* Slightly darker blue */

--btn-danger-bg: var(--accent-danger);
--btn-danger-text: var(--text-primary);
--btn-danger-hover: #e03c34; /* Slightly darker red */

/* CATEGORY COLORS (Prompt Library) */
--category-development: #58a6ff;  /* Blue */
--category-analysis: #3fb950;     /* Green */
--category-data: #d29922;         /* Orange */
--category-style: #bc8cff;        /* Purple */
--category-business: #f85149;     /* Red */
--category-creative: #f778ba;     /* Pink */
```

### Usage Rules

#### Rule 1: Always Use Semantic Tokens in Components
```css
/* ❌ BAD - Direct primitive reference */
.card {
    background: #161b22;
    color: #c9d1d9;
}

/* ✅ GOOD - Semantic tokens */
.card {
    background: var(--bg-secondary);
    color: var(--text-secondary);
}
```

#### Rule 2: State Variations Use Alpha Transparency
```css
/* Backgrounds for state indicators */
.success-banner {
    background: var(--color-success-bg); /* rgba with 10% opacity */
    border-left: 3px solid var(--accent-success);
    color: var(--accent-success);
}
```

#### Rule 3: Category Colors Use Border, Not Background
```css
/* ✅ GOOD - Subtle border accent */
.prompt-item.category-development {
    border-left: 3px solid var(--category-development);
}

/* ❌ BAD - Heavy background color */
.prompt-item.category-development {
    background: var(--category-development); /* Too strong */
}
```

---

## 5. Typography Scale

### Font Stack

```css
--font-family-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", 
                    "Noto Sans", Helvetica, Arial, sans-serif, 
                    "Apple Color Emoji", "Segoe UI Emoji";

--font-family-mono: ui-monospace, SFMono-Regular, "SF Mono", 
                    Menlo, Consolas, "Liberation Mono", monospace;
```

### Type Scale (Modular Scale: 1.25 ratio)

```css
/* FONT SIZES (4px baseline grid) */
--font-size-xs: 11px;    /* Extra small (help text, meta) */
--font-size-sm: 12px;    /* Small (labels, badges) */
--font-size-base: 14px;  /* Base size (body text) */
--font-size-md: 16px;    /* Medium (prominent text) */
--font-size-lg: 18px;    /* Large (section headers) */
--font-size-xl: 20px;    /* Extra large (page titles) */
--font-size-2xl: 24px;   /* Headings */
--font-size-3xl: 32px;   /* Major headings */
--font-size-4xl: 40px;   /* Hero text */

/* LINE HEIGHTS (unitless multipliers) */
--line-height-tight: 1.2;   /* Headings */
--line-height-normal: 1.5;  /* Body text */
--line-height-relaxed: 1.75; /* Long-form content */

/* FONT WEIGHTS */
--font-weight-normal: 400;
--font-weight-medium: 500;
--font-weight-semibold: 600;
--font-weight-bold: 700;
```

### Typography Component Classes

```css
/* HEADINGS */
.heading-1 {
    font-size: var(--font-size-3xl);  /* 32px */
    font-weight: var(--font-weight-bold);
    line-height: var(--line-height-tight);
    margin-bottom: var(--space-300); /* 24px */
}

.heading-2 {
    font-size: var(--font-size-2xl);  /* 24px */
    font-weight: var(--font-weight-bold);
    line-height: var(--line-height-tight);
    margin-bottom: var(--space-200); /* 16px */
}

.heading-3 {
    font-size: var(--font-size-xl);   /* 20px */
    font-weight: var(--font-weight-semibold);
    line-height: var(--line-height-tight);
    margin-bottom: var(--space-150); /* 12px */
}

/* BODY TEXT */
.body-large {
    font-size: var(--font-size-md);   /* 16px */
    line-height: var(--line-height-relaxed);
}

.body-default {
    font-size: var(--font-size-base); /* 14px */
    line-height: var(--line-height-normal);
}

.body-small {
    font-size: var(--font-size-sm);   /* 12px */
    line-height: var(--line-height-normal);
}

/* UTILITY CLASSES */
.text-muted {
    color: var(--text-muted);
}

.text-bold {
    font-weight: var(--font-weight-bold);
}

.text-mono {
    font-family: var(--font-family-mono);
}
```

---

## 6. Animation & Transitions

### Timing Functions (Easing)

```css
/* STANDARD EASINGS */
--ease-in: cubic-bezier(0.4, 0, 1, 1);         /* Accelerate */
--ease-out: cubic-bezier(0, 0, 0.2, 1);        /* Decelerate (recommended for most UI) */
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);   /* Smooth start/end */
--ease-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55); /* Bounce effect */

/* DURATIONS (Material Design Standard) */
--duration-instant: 100ms;   /* Immediate feedback */
--duration-fast: 150ms;      /* Quick transitions (hover) */
--duration-normal: 200ms;    /* Standard transitions (default) */
--duration-slow: 300ms;      /* Deliberate animations */
--duration-slower: 400ms;    /* Panel slides */
--duration-slowest: 500ms;   /* Major transitions */
```

### Animation Standards by Use Case

#### Hover States (Fast)
```css
.button {
    transition: background-color var(--duration-fast) var(--ease-out),
                transform var(--duration-fast) var(--ease-out);
}

.button:hover {
    background-color: var(--btn-primary-hover);
    transform: translateY(-1px); /* Subtle lift */
}
```

#### Panel Slides (Slow)
```css
.sidebar {
    transition: transform var(--duration-slower) var(--ease-out);
    transform: translateX(100%); /* Hidden */
}

.sidebar.show {
    transform: translateX(0); /* Visible */
}
```

#### Modal Fades (Normal)
```css
.modal {
    transition: opacity var(--duration-normal) var(--ease-out);
    opacity: 0;
}

.modal.show {
    opacity: 1;
}
```

#### Micro-Interactions (Instant)
```css
.checkbox {
    transition: border-color var(--duration-instant) var(--ease-out);
}

.checkbox:checked {
    border-color: var(--accent-primary);
}
```

### Keyframe Animations

```css
/* PULSE (for notifications, badges) */
@keyframes pulse {
    0%, 100% {
        opacity: 1;
        transform: scale(1);
    }
    50% {
        opacity: 0.8;
        transform: scale(1.05);
    }
}

.badge-new {
    animation: pulse var(--duration-slow) var(--ease-in-out) 3;
}

/* FADE IN UP (for toast notifications) */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.toast {
    animation: fadeInUp var(--duration-normal) var(--ease-out);
}

/* SPIN (for loading indicators) */
@keyframes spin {
    from {
        transform: rotate(0deg);
    }
    to {
        transform: rotate(360deg);
    }
}

.spinner {
    animation: spin 1s linear infinite;
}
```

### Reduced Motion (Accessibility)

```css
/* Respect user's motion preferences */
@media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}
```

---

## 7. Touch Targets & Accessibility

### WCAG 2.1 AA Standards

#### Minimum Touch Target Size

**Standard:** 44×44 CSS pixels (WCAG 2.1 Level AAA recommends 44×44, Level AA requires 24×24)

**Best Practice:** Use 48×48px (Material Design standard)

```css
/* COMPLIANT: Icon button with proper touch area */
.icon-btn {
    width: var(--touch-target-min);  /* 48px */
    height: var(--touch-target-min); /* 48px */
    display: flex;
    align-items: center;
    justify-content: center;
}

.icon-btn svg {
    width: 20px;  /* Visual icon size */
    height: 20px;
}
```

#### Spacing Between Touch Targets

**Minimum:** 8px gap between interactive elements

```css
.button-group {
    display: flex;
    gap: var(--space-100); /* 8px between buttons */
}
```

### Focus States (Keyboard Navigation)

```css
/* VISIBLE FOCUS RING (WCAG 2.1 Required) */
*:focus-visible {
    outline: 2px solid var(--accent-primary);
    outline-offset: 2px;
}

/* Remove focus outline on mouse click, keep for keyboard */
*:focus:not(:focus-visible) {
    outline: none;
}

/* High-contrast focus for dark backgrounds */
.dark-bg *:focus-visible {
    outline-color: var(--gray-0); /* White outline */
}
```

### Color Contrast (WCAG AA)

**Minimum Ratios:**
- Normal text (< 18px): 4.5:1
- Large text (≥ 18px or ≥ 14px bold): 3:1
- UI components and graphics: 3:1

```css
/* COMPLIANT: Text on background */
.card {
    background: var(--bg-secondary);  /* #161b22 */
    color: var(--text-primary);       /* #f0f6fc - Ratio: 14.4:1 ✅ */
}

/* COMPLIANT: Button contrast */
.btn-primary {
    background: var(--accent-primary); /* #58a6ff */
    color: #000000;                    /* Black text - Ratio: 8.1:1 ✅ */
}
```

### Screen Reader Support

```css
/* VISUALLY HIDDEN (SR-only) */
.sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
}
```

---

## 8. Layout Grid System

### 12-Column Responsive Grid

```css
/* CONTAINER */
.container {
    width: 100%;
    max-width: 1280px;
    margin: 0 auto;
    padding: 0 var(--space-300); /* 24px side padding */
}

/* GRID */
.grid {
    display: grid;
    grid-template-columns: repeat(12, 1fr);
    gap: var(--space-300); /* 24px gap */
}

/* COLUMN SPANS */
.col-1 { grid-column: span 1; }
.col-2 { grid-column: span 2; }
.col-3 { grid-column: span 3; }
.col-4 { grid-column: span 4; }
.col-6 { grid-column: span 6; }
.col-8 { grid-column: span 8; }
.col-12 { grid-column: span 12; }
```

### Flexbox Utilities

```css
/* FLEX CONTAINERS */
.flex {
    display: flex;
}

.flex-col {
    flex-direction: column;
}

/* ALIGNMENT */
.items-center {
    align-items: center;
}

.justify-between {
    justify-content: space-between;
}

.justify-center {
    justify-content: center;
}

/* GAPS */
.gap-1 { gap: var(--space-100); }  /* 8px */
.gap-2 { gap: var(--space-200); }  /* 16px */
.gap-3 { gap: var(--space-300); }  /* 24px */
.gap-4 { gap: var(--space-400); }  /* 32px */
```

---

## 9. Component-Specific Standards

### Sidebar (Prompt Library)

```css
.prompt-sidebar {
    position: fixed;
    top: 0;
    right: 0;
    width: var(--width-sidebar-standard); /* 450px */
    height: 100vh;
    background: var(--bg-secondary);
    border-left: 1px solid var(--border-default);
    z-index: var(--z-sidebar); /* 1040 */
    transform: translateX(100%);
    transition: transform var(--duration-slower) var(--ease-out);
    padding: var(--space-300); /* 24px */
}

.prompt-sidebar.show {
    transform: translateX(0);
}
```

### Modal Dialog

```css
.modal-backdrop {
    position: fixed;
    inset: 0;
    background: var(--overlay-backdrop); /* rgba(1,4,9,0.6) */
    z-index: var(--z-modal-backdrop); /* 2050 */
    opacity: 0;
    transition: opacity var(--duration-normal) var(--ease-out);
}

.modal-backdrop.show {
    opacity: 1;
}

.modal-content {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%) scale(0.95);
    width: 90%;
    max-width: var(--width-modal-md); /* 600px */
    background: var(--bg-elevated);
    border: 1px solid var(--border-default);
    border-radius: 8px;
    padding: var(--space-400); /* 32px */
    z-index: var(--z-modal); /* 2055 */
    opacity: 0;
    transition: opacity var(--duration-normal) var(--ease-out),
                transform var(--duration-normal) var(--ease-out);
}

.modal-content.show {
    opacity: 1;
    transform: translate(-50%, -50%) scale(1);
}
```

### Button Variants

```css
/* PRIMARY BUTTON */
.btn-primary {
    height: var(--height-btn-md); /* 40px */
    padding: 0 var(--space-200); /* 0 16px */
    background: var(--accent-primary);
    color: #000000;
    border: none;
    border-radius: 6px;
    font-size: var(--font-size-base); /* 14px */
    font-weight: var(--font-weight-medium);
    cursor: pointer;
    transition: background-color var(--duration-fast) var(--ease-out),
                transform var(--duration-fast) var(--ease-out);
}

.btn-primary:hover {
    background: #4493e8;
    transform: translateY(-1px);
}

.btn-primary:active {
    transform: translateY(0);
}

/* DANGER BUTTON */
.btn-danger {
    background: var(--accent-danger);
    color: var(--text-primary);
}

.btn-danger:hover {
    background: #e03c34;
}

/* GHOST BUTTON (outline) */
.btn-ghost {
    background: transparent;
    color: var(--text-secondary);
    border: 1px solid var(--border-default);
}

.btn-ghost:hover {
    background: var(--bg-elevated-hover);
    border-color: var(--border-strong);
}
```

### Card Component

```css
.card {
    background: var(--bg-elevated);
    border: 1px solid var(--border-default);
    border-radius: 8px;
    padding: var(--space-300); /* 24px */
}

.card-header {
    height: var(--height-card-header); /* 56px */
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 var(--space-300);
    border-bottom: 1px solid var(--border-muted);
}

.card-body {
    padding: var(--space-300); /* 24px */
}

.card-footer {
    padding: var(--space-200); /* 16px */
    border-top: 1px solid var(--border-muted);
    display: flex;
    justify-content: flex-end;
    gap: var(--space-150); /* 12px */
}
```

### Dropdown Menu

```css
.dropdown {
    position: relative;
}

.dropdown-menu {
    position: absolute;
    top: calc(100% + var(--space-050)); /* 4px below trigger */
    left: 0;
    min-width: var(--width-dropdown-min); /* 200px */
    max-width: var(--width-dropdown-max); /* 400px */
    background: var(--bg-elevated);
    border: 1px solid var(--border-default);
    border-radius: 6px;
    padding: var(--space-075) 0; /* 6px 0 */
    z-index: var(--z-dropdown); /* 1000 */
    opacity: 0;
    transform: translateY(-10px);
    transition: opacity var(--duration-fast) var(--ease-out),
                transform var(--duration-fast) var(--ease-out);
    pointer-events: none;
}

.dropdown-menu.show {
    opacity: 1;
    transform: translateY(0);
    pointer-events: auto;
}

.dropdown-item {
    display: block;
    width: 100%;
    padding: var(--space-100) var(--space-200); /* 8px 16px */
    text-align: left;
    font-size: var(--font-size-base); /* 14px */
    color: var(--text-secondary);
    background: none;
    border: none;
    cursor: pointer;
    transition: background-color var(--duration-fast) var(--ease-out);
}

.dropdown-item:hover {
    background: var(--bg-elevated-hover);
    color: var(--text-primary);
}
```

---

## 10. Responsive Breakpoints

### Breakpoint Scale (Bootstrap/Tailwind Standard)

```css
/* BREAKPOINTS (mobile-first) */
--breakpoint-xs: 0px;      /* Extra small devices (phones) */
--breakpoint-sm: 640px;    /* Small devices (large phones) */
--breakpoint-md: 768px;    /* Medium devices (tablets) */
--breakpoint-lg: 1024px;   /* Large devices (laptops) */
--breakpoint-xl: 1280px;   /* Extra large devices (desktops) */
--breakpoint-2xl: 1536px;  /* 2X large devices (large desktops) */
```

### Media Query Usage

```css
/* MOBILE FIRST (default styles for mobile) */
.sidebar {
    width: 100%;
    padding: var(--space-200);
}

/* TABLET AND UP */
@media (min-width: 768px) {
    .sidebar {
        width: var(--width-sidebar-standard); /* 450px */
        padding: var(--space-300);
    }
}

/* DESKTOP AND UP */
@media (min-width: 1024px) {
    .sidebar {
        padding: var(--space-400);
    }
}
```

### Responsive Typography

```css
/* FLUID TYPE SCALING */
.heading-1 {
    font-size: clamp(
        var(--font-size-2xl),  /* Min: 24px */
        5vw,                    /* Fluid: 5% of viewport */
        var(--font-size-4xl)   /* Max: 40px */
    );
}
```

---

## 11. Implementation Checklist

### For New Components

- [ ] Uses spacing from `--space-*` variables
- [ ] Uses z-index from `--z-*` variables
- [ ] Uses colors from semantic tokens (not hex)
- [ ] Follows 8px grid for dimensions
- [ ] Touch targets ≥ 48×48px
- [ ] Proper focus states (`:focus-visible`)
- [ ] Color contrast ≥ 4.5:1 for text
- [ ] Animations use standard durations/easings
- [ ] Respects `prefers-reduced-motion`
- [ ] Responsive breakpoints follow standard scale
- [ ] Typography uses `--font-size-*` scale

### Code Review Standards

**Reject if:**
- Magic numbers for spacing (e.g., `padding: 13px`)
- Arbitrary z-index values (e.g., `z-index: 9999`)
- Hard-coded hex colors (e.g., `color: #FF5733`)
- Touch targets < 44px
- No focus states
- Animations without reduced-motion handling

**Approve if:**
- All values use CSS custom properties
- Spacing aligned to 4px/8px grid
- Z-index uses semantic layer system
- Colors use semantic tokens
- Accessibility standards met

---

## 12. Migration Guide (Existing Code)

### Step 1: Add CSS Variables to Root

```css
:root {
    /* Copy all variables from sections 1-6 above */
}
```

### Step 2: Replace Hard-Coded Values

**Before:**
```css
.sidebar {
    padding: 24px;
    background: #161b22;
    z-index: 9999;
}
```

**After:**
```css
.sidebar {
    padding: var(--space-300);
    background: var(--bg-secondary);
    z-index: var(--z-sidebar);
}
```

### Step 3: Update Component Classes

Use utility classes where applicable:

```css
/* Before */
.card {
    display: flex;
    gap: 16px;
    align-items: center;
}

/* After */
.card {
    @extend .flex;
    @extend .items-center;
    @extend .gap-2;
}
```

---

## 13. Resources & References

### Industry Standards Referenced

- **Material Design 3** - Google's design system
- **GitHub Primer** - GitHub's design system
- **Bootstrap 5.3** - Popular CSS framework
- **Atlassian Design System** - Enterprise design patterns
- **Tailwind CSS** - Utility-first CSS framework

### Tools for Validation

- **Color Contrast Checker:** [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- **Touch Target Analyzer:** Chrome DevTools Mobile Emulation
- **Spacing Visualizer:** Use browser DevTools to overlay grid
- **Accessibility Auditor:** axe DevTools browser extension

### Documentation

- [Material Design Spacing](https://m2.material.io/design/layout/spacing-methods.html)
- [Bootstrap Z-Index](https://getbootstrap.com/docs/5.3/layout/z-index/)
- [GitHub Primer Tokens](https://primer.style/design/foundations/color)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | Nov 15, 2025 | Initial technical specification based on industry research |

---

**Maintained by:** AI Agents Platform Team  
**Last Review:** November 15, 2025  
**Next Review:** Quarterly (February 2026)
