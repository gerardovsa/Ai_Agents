# AI Status Colour-Coding System

> Single source of truth for the four-state AI status palette.
> Last updated: 2026-07-27

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
2. The wrapping panel's full border (solid colour).
3. The wrapping panel's inset glow (`panelStatusPulse` keyframe: 4 → 8 px blur).

Animation durations match across icon and panel:

- `thinking` / `writing`: `2s ease-in-out infinite`
- `tool-running` / `tool-success`: `1.5s ease-in-out infinite`

Panel pulse uses an *inset* box-shadow so the panel's outer box does not grow
into its neighbours during the breath.

## 4. Pulse-width rationale

- Icon ring geometric pulse: `scale(1.0 → 1.1)` on a ~36 px outer ring ≈ 3.6 px outward reach.
- Panel pulse: 4 → 8 px inset box-shadow blur on a ~400 px column.
- The panel is ~10× the icon's footprint, so the visual perceived amplitude is
  roughly half the icon ring's reach — matching the "about 50 %" requirement.
  Tune the per-class `--status-glow` variable to adjust; do not fork the keyframe.

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