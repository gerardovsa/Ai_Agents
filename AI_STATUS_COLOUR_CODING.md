# AI Status Colour-Coding System

> Single source of truth for the four-state AI status palette.
> Last updated: 2026-07-28

## 1. The palette (canonical)

| Status        | Hex              | Meaning                         | JS class               |
|---------------|------------------|---------------------------------|------------------------|
| thinking      | `#8b5cf6` purple | Model is reasoning              | `status-thinking`      |
| writing       | `#ffffff` white  | Model is streaming tokens       | `status-writing`       |
| tool-running  | `#eab308` yellow | A tool is in flight             | `status-tool-running`  |
| tool-success  | `#60A5FA` blue   | A tool just returned            | `status-tool-success`  |

If a status needs a new colour, change it here **and** in the inline rules of
`UI/business-ai-platform-v2.html` (see §2). Never put the hex in a third place.

## 2. Where the palette lives

- **Inline production — `UI/business-ai-platform-v2.html`**
  - Prime icon ring: lines 6668-6694 (`.ai-icon.status-X::before`).
  - Agent icon ring (legacy): lines 12653-12681 (`.agent-header h2 i.status-X::after`).
  - Agent icon ring (new, added 2026-07-27): inserted after line 12681.
  - Panel border pulse (added 2026-07-27): inserted after agent icon ring.
  - Drag-over suppression (added 2026-07-27): inserted after panel pulse.

- **Dormant / colliding — `UI/shared/css/status-indicator.css`** (lines 104-200)
  - Different colours (`#3b82f6 / #10b981 / #f59e0b`), different keyframe
    (`pulse-ring`), only 3 of 4 statuses. These rules load but lose the cascade.
    See §8 for the Phase-2 cleanup plan.

- **Quick-nav badge — `UI/modules_internal/thread-manager/thread.css`**
  - `.agent-quick-nav-badge.status-X::before`, same palette as production.

- **JS driver — `UI/modules_internal/agent-status-indicator.js`**
  - Public: `update / clear / clearAll`.
  - Private: `_updatePrimeIcon / _updateAgentIcon / _updateQuickNavBadge / _updatePanel`.
  - Public helper: `AgentStatusIndicator.isPanelBusy(el)` (added 2026-07-27).

## 3. Visual model

A status class paints **three places in lock-step**:

1. The icon's ring (`statusPulse` keyframe: `scale(1.0 → 1.1)`, `opacity(1.0 → 0.6)`).
2. The wrapping panel: a static 1 px status-coloured **border** (paints all
   4 sides reliably — declared via the `border` shorthand in each
   `.status-X` rule, not `border-color`, so it works on `.ai-chat-panel`
   whose base only declares `border-left`).
3. The wrapping panel: a **4-layer pulse stack** that keeps the breath
   visible on all four edges even though children paint opaque backgrounds
   on top:
   - **Layer 1 — outer ring (2 px, constant).** Drawn via `0 0 0 2px
     <color>` spread. Visible on the left and right where the 12 px column
     gap gives it room; may be clipped at top/bottom by the parent
     `#multi-agent-container`'s `overflow:auto` (padding 0, height 100% —
     no free space there).
   - **Layer 2 — outer glow (4 → 8 px blur, alpha 0.4 → 0.95).** Visible
     at the sides; intentionally tuned to stay within the 12 px column gap
     so it does not bleed into the neighbour column. May be clipped
     top/bottom — see Layer 3.
   - **Layer 3 — inset atmospheric wash (3 → 11 px blur + 0 → 2 px spread,
     alpha 0.4 → 0.95, reduced 2026-07-27 from 4 → 14 px).** Inset
     box-shadow paints INSIDE the panel and is **never clipped by ancestor
     overflow**, but opaque child elements (`.agent-header` at the top,
     `.ai-chat-messages` filling the middle with `flex: 1` and
     `background: var(--bg-secondary)`) paint OVER it. It is visible only
     on the bottom of agent columns where no child occludes it. The 25 %
     reduction keeps the wash proportional to the visible footprint.
   - **Layer 4 — `::after` rim-glow overlay (new, 2026-07-27; tightened
     2026-07-28).** Painted ABOVE children via `position: absolute;
     inset: 0; z-index: 1; pointer-events: none;` and a radial-gradient
     vignette (`transparent 78% → status color 88% → 100%`). The vignette
     fades into the centre so the chat content stays readable; the rim
     glows uniformly on all four edges regardless of which child elements
     sit inside. The opacity oscillates `0.15 → 0.95` via the
     `panelStatusPulseOverlay` keyframe (synced to the Layer 3 timings).
     **Stop-choice rationale:** with `transparent 78%`, the colour sits in
     the outer ~22% of the ellipse only. For a typical 350×600 agent
     column (175 px half-width, 300 px half-height), the inward depth is
     ~38 px on the horizontal axis and ~66 px on the vertical axis — a
     tight rim glow rather than a wash. The earlier
     `transparent 55% / 95% / 100%` produced 40% of the panel radius
     (70-120 px) of smooth fade, which read as a wash rather than a rim.

Animation durations match across icon, panel box-shadow, and rim overlay:

- `thinking` / `writing`: `2s ease-in-out infinite`
- `tool-running` / `tool-success`: `1.5s ease-in-out infinite`

## 4. Pulse-width rationale

- Icon ring geometric pulse: `scale(1.0 → 1.1)` on a ~36 px outer ring ≈ 3.6 px outward reach.
- Badge ring reference: 2 px positioned `::before` border + 5 % scale ≈ ~4.2 px outward reach.
- Panel pulse: 2 px outer ring (constant) + 3 → 6 px outer glow (matches badge reach) + 3 → 11 px inset wash + radial-gradient rim overlay (alpha 0.15 → 0.95) visible on all 4 edges regardless of parent overflow or child occlusion.
- The 6 px peak outer glow reach stays inside the 12 px column gap so the
  glow does not bleed into the neighbour. The inset layer + rim overlay
  together compensate on the clipped top/bottom edges and the child-painted
  sides. Tune the per-class `--status-glow-rest` / `--status-glow-peak`
  variables to adjust; do not fork the keyframe.

## 5. Hover behaviour

- **Prime panel** (`UI/business-ai-platform-v2.html:3165-3182`): the whole
  left border lights in `var(--accent-primary)` on hover. The 6 px resize strip
  overlays on top via `z-index: 10` so the user can still grab it.
- **Agent column** (`UI/business-ai-platform-v2.html:12511-12513`): the full
  border lights in `var(--accent-primary)` on hover.

## 6. Drop-while-busy behaviour (added 2026-07-27)

When a panel is in any active status:

- **Drop affordance is suppressed** via CSS overrides (`.status-X.drag-over` /
  `.status-X.prime-drag-over` selectors at `(0,4,0)` specificity).
- **Drop is rejected by JS** at three coordinated points:
  - `dragenter` — skips the `.drag-over` / `.prime-drag-over` class addition
    so the visual cue never appears.
  - `dragover` — sets `dropEffect = 'none'` so the OS cursor signals
    "this won't accept the drop".
  - `drop` — final defensive guard. Even if the affordance slipped through
    somehow, the swap is rejected and the active thread stays.
- Visually the user sees the status pulse continue; the absence of a drop
  indicator signals "the AI is busy — try again later".

Drop handlers live in `UI/modules_internal/thread-manager/thread-manager-interactions.js`
(lines 1142-1188 for agent columns, 1210-1264 for Prime).

## 7. Precedence (highest wins last)

- Default border loses to status.
- Hover (left-edge accent) coexists with status — both are visible.
- `.drag-over` / `.prime-drag-over` are **suppressed** by status (AI is busy).
- `.locked-by-other` wins — red `!important` border is a critical signal that
  another user has the thread open; do not let status pulse hide it.
- `.popped-out-placeholder` wins — blue `!important` border + shimmer indicate
  the panel has been popped into its own window.

## 8. Dormant file consolidation (Phase-2 follow-up, NOT in this PR)

`UI/shared/css/status-indicator.css` lines 104-200 are dead and collide on
selectors with the inline production rules. A future PR should:

1. Delete lines 104-200 of the dormant file.
2. Keep the bottom-left `.status-indicator` toast (lines 1-103 + 201-254) and
   its JS at `UI/shared/js/status-indicator.js` — that is a separate feature
   (different colours, different keyframe, different selector scope).
3. Do **not** replace colours in the dormant file — identical selectors would
   re-introduce the cascade conflict.

## 9. Do NOT

- Do NOT edit the four colour hex values in more than one place. They are
  listed in §1; if a new shade is needed, change the inline rules in
  `business-ai-platform-v2.html` and update §1 here.
- Do NOT add a 5th status without updating §1, the JS `ALL_STATUS_CLASSES`
  constant, all four status rules in CSS, and the panel-pulse rules.
- Do NOT move the palette into global CSS variables —
  `business-ai-platform-v2.html` does not use custom properties for theme
  colours, and adding `--status-purple` etc. would create a second source of
  truth. The new `--status-color` and `--status-glow` are *per-component*
  variables used only inside the panel-pulse block.
- Do NOT touch the bottom-left `.status-indicator` toast. Different feature,
  different colours, different keyframe.