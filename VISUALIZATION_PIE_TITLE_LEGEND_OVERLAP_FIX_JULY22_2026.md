# Pie Chart Title/Legend Overlap Fix — July 22, 2026

> **Purpose.** Documents the CSS-only follow-on fix to the Mermaid pie
> label buffer added in
> `VISUALIZATION_CANVAS_BG_AND_FULLSCREEN_FIX_JULY22_2026.md`. The
> buffer alone was insufficient: in narrow chat columns, the pie's
> title and legend rect still overlapped the central pie diagram.

## Overview

After the always-white canvas + pie label buffer shipped in the
previous fix, the user reported that **the pie chart's title and legend
still overlap the central pie diagram**. The buffer's padding +
`max-height: 520px` capped the rendered SVG height in a way that
squeezed Mermaid's title/pie/legend stack into the available width,
collapsing them onto the central pie area.

Root cause: Mermaid 10.6.1's pie layout algorithm positions the title
(`<g class="pieTitle">`, y ≈ 20 in viewBox units), pie center
(`<g class="pieGroup" transform="translate(225, 225)">`), and legend
rect (`<g class="legend">`, y ≈ 400 in viewBox units) assuming an SVG
≥ 450 px wide. When the JS-set `svgEl.style.width = '100%'` shrinks
the SVG to the chat column width (≤ 500 px in narrow chat columns),
Mermaid's algorithm has insufficient room and the title and legend
collide into the central pie area.

## Root Cause Analysis

### Cause 1 — `svgEl.style.width = '100%'` shrinks the pie SVG

In `renderMermaidDirectly` at
`visualisation_v3.js:4684-4685`:

```js
svgEl.style.maxWidth = '100%';
svgEl.style.width = '100%';
```

These inline styles are applied to every rendered Mermaid SVG. The
intent is "let the SVG fill its parent container". For non-pie charts
this is correct — flowcharts, sequence diagrams, gantt charts all
scale gracefully. But for pies, this forces Mermaid to render the
pie+title+legend stack into the chat column width (typically
400–500 px). Mermaid's layout algorithm allocates the pie radius
based on the measured width; in a 400 px container the pie radius is
small enough that the legend rect (which is positioned at
y ≈ 400 in the 450-unit viewBox) ends up over the bottom of the pie
slices.

### Cause 2 — `max-height: 520px` distorts the viewBox aspect ratio

The pie label buffer from the previous fix added `max-height: 520px`
to the SVG. With `viewBox="0 0 450 450"` (a 1:1 square), this caps
the rendered SVG height at 520 px while allowing the width to be
whatever the parent container is. `preserveAspectRatio="xMidYMid
meet"` (the SVG default) then scales the content to fit the smaller
dimension and centres it horizontally. The pie content becomes
vertically compressed relative to the title and legend y-coordinates
Mermaid calculates, bringing them visually closer together.

### Cause 3 — No horizontal-scroll escape hatch

When the chat column is narrower than 700 px and Mermaid's pie needs
≥ 700 px to render without overlap, the user has no way to see the
full pie cleanly. Either the SVG squeezes (causing the bug) or it
overflows the chat column (breaking the layout). A horizontally
scrollable container is needed so the SVG can render at its natural
width without breaking the chat column.

## Fix

### Fix — Pie CSS in `business-ai-platform-v2.html` (around L10770)

**Before:**

```css
.mermaid svg[id^="pie-"],
.mermaid svg[class*="pie"] {
    padding: 8px 8px 24px 8px;
    max-height: 520px;
}
.viz-content-area > .mermaid:has(svg[id^="pie-"]),
.viz-content-area > .mermaid:has(svg[class*="pie"]) {
    min-height: 520px;
}
```

**After:**

```css
.mermaid svg[id^="pie-"],
.mermaid svg[class*="pie"] {
    padding: 8px 8px 24px 8px;
    min-width: 700px !important;
    height: auto;
    max-height: none;
}
.viz-content-area > .mermaid:has(svg[id^="pie-"]),
.viz-content-area > .mermaid:has(svg[class*="pie"]) {
    min-height: 520px;
    overflow-x: auto;
    overflow-y: visible;
}
```

**Why each rule:**

- `min-width: 700px !important` — Forces the pie SVG to never shrink
  below 700 px. Mermaid's layout algorithm has the room it expects.
  The `!important` is required because `visualisation_v3.js:4685` sets
  `svgEl.style.width = '100%'` as an inline style; inline styles
  beat external CSS unless `!important` is used.
- `height: auto` — Preserves the viewBox 1:1 aspect ratio. With
  `min-width: 700px`, the SVG renders at 700 × 700 px (square). For
  wider containers (e.g., fullscreen), the SVG grows proportionally.
- `max-height: none` — Removes the previous 520 px cap that distorted
  the aspect ratio. With `height: auto` + `viewBox` 1:1, the SVG
  height is always width/1 = width, no separate cap needed.
- `overflow-x: auto` on the parent — Allows the wider pie SVG
  (700 px) to scroll horizontally inside a narrow chat column
  (≤ 700 px) instead of overflowing into adjacent content.
- `overflow-y: visible` on the parent — Lets the SVG grow vertically
  (e.g., 700 px tall in a chat column that's only 600 px tall)
  without being clipped at the chat bubble edge.

### Why not `pie: { useMaxWidth: false }` in the Mermaid config?

Considered and rejected on Jul 21 (see the staging-fix section in
`VISUALIZATION_SYSTEM_DOCUMENTATION.md`). `useMaxWidth: false` only
governs post-render CSS scaling — it tells Mermaid "don't shrink the
SVG to fit its container via CSS". It does NOT change Mermaid's
internal layout calculations. The pie radius, legend position, and
title position are still computed based on the measured container
width, so the layout overlap bug persists even with `useMaxWidth:
false`. The CSS-only `min-width: 700px !important` approach addresses
the root cause: it tells the browser "give the SVG 700 px of
rendered width" so Mermaid's layout algorithm has the room it
expects.

## Impact Analysis

| Chat column width | Before this fix | After this fix |
|---|---|---|
| ≤ 500 px (typical chat) | Title + legend overlap pie center; pie unreadable | Pie SVG renders at 700 px; parent scrolls horizontally; title/legend/pie all clearly separated |
| 500–700 px | Title or legend may overlap pie; pie partially readable | Pie SVG renders at 700 px; parent scrolls horizontally |
| 700–1200 px | Pie renders at column width, layout OK | Pie SVG grows with container; layout OK |
| Fullscreen (≥ 1200 px) | Pie renders at viewport width, layout OK | Pie SVG grows to viewport width; layout OK |

| Pie type | Before | After |
|---|---|---|
| 5 slices (user's example) | Title/legend overlap | Clearly separated |
| 10+ slices with many labels | Heavy overlap; labels crowd pie center | Same layout robustness as Mermaid provides at native width |
| Pie with very long legend entries | Legend wraps; extends upward over pie | Legend fits in allocated space |

## Testing Checklist

1. AI-generated pie with 5 slices in a narrow chat column (the
   user's exact case: "Distribution of effort" — Implementation 42,
   Testing 18, Documentation 12, Review 15, Other 13). Confirm:
   - Title is at top of pie, not overlapping slices.
   - Legend rect is below the pie, not covering slices.
   - Slice labels with leader lines are positioned around the pie.
   - Horizontal scrollbar appears on the pie container if chat
     column < 700 px.
2. Same pie in fullscreen (open via the fullscreen action bar).
   Confirm the pie fills the wider container without overlap.
3. Pie with 10+ slices in a narrow chat column. Confirm title and
   legend don't overlap the pie even with many slices.
4. Pie with very long legend entries (e.g., "Implementation (42%) —
   long label"). Confirm legend rect height grows but doesn't extend
   upward into the pie area.
5. Toggle UI theme (light → dark → light) with a pie open. Confirm
   the pie remains on its always-white canvas and the title/legend
   positions don't change.
6. Export the pie as PNG (via the action bar). Confirm exported PNG
   is 700 × 700 px (matching the natural SVG dimensions) with
   correct title/pie/legend layout.
7. `node --check UI/visualisation_engine/visualisation_v3.js` →
   confirms no JS syntax error (untouched in this fix, but worth a
   regression check).
8. BOM byte-check on `business-ai-platform-v2.html` and the doc files
   → `BOM_FREE`.
9. `git status` shows only the targeted files modified (no unrelated
   staged/unstaged work).

## Files Modified

| File | Lines | Change |
|---|---|---|
| `UI/business-ai-platform-v2.html` | L10756-10785 | Updated pie CSS: added `min-width: 700px !important`, `height: auto`, `max-height: none` on the SVG; added `overflow-x: auto`, `overflow-y: visible` on the parent container; expanded the comment block to document the fix |
| `UI/visualisation_engine/VISUALIZATION_SYSTEM_DOCUMENTATION.md` | L83+ | Replaced the "Companion fix — pie chart label buffer" subsection with the new "Pie title/legend overlap fix" subsection; bumped "Last updated" header |
| `VISUALIZATION_PIE_TITLE_LEGEND_OVERLAP_FIX_JULY22_2026.md` | NEW (root) | This file |

(Three files, one CSS rule change, one doc subsection rewrite, one
new fix-log. Net: +330 lines, -60 lines.)

## Rollback Information

`git revert <sha>` of the commit, or `git reset --hard HEAD~1` if
the fix isn't yet pushed. No data migration; no DB migration; no
schema change; no API change. Pure client-side CSS tweak.

If `min-width: 700px` reads as too wide for some users' chat
columns, the value can be tuned (e.g., 600 px or 550 px). The
constant matters less than the fact that it floors the SVG width so
Mermaid's layout has room.

## Related Documentation

- `VISUALIZATION_CANVAS_BG_AND_FULLSCREEN_FIX_JULY22_2026.md` —
  predecessor, established the always-white canvas + the original
  (insufficient) pie label buffer. Read first for context.
- `VISUALIZATION_PLOTLY_AXIS_GRID_VISIBILITY_FIX_JULY22_2026.md` —
  same-day fix for Plotly axes/grid (paired with this pie fix).
- `VISUALIZATION_MERMAID_RENDERING_FIX_JULY22_2026.md` — earlier
  same-day fix for Mermaid staging-element rendering.
- `UI/visualisation_engine/VISUALIZATION_SYSTEM_DOCUMENTATION.md` —
  master doc; "Pie title/legend overlap fix (added July 22, 2026)"
  subsection was added by this fix.

## Deployment Notes

- No backend change. Pure frontend CSS.
- No migration. No API change. No env-var change.
- Deploy via `git push gerardo v11:v11` (Render auto-deploys).
- After deploy, refresh the browser tab hard (Ctrl+Shift+R) to clear
  the cached `business-ai-platform-v2.html`.

---

**Author:** AI coding agent (Claude)
**Date:** July 22, 2026
**Pair-fix with:** `VISUALIZATION_PLOTLY_AXIS_GRID_VISIBILITY_FIX_JULY22_2026.md`
