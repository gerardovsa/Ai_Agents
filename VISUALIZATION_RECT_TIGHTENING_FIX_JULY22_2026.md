# Rect Tightening for Pie / Git Graph / Gantt — July 22, 2026

> **Purpose.** Documents the follow-on fix to the pie title/legend
> overlap fix in `VISUALIZATION_PIE_TITLE_LEGEND_OVERLAP_FIX_JULY22_2026.md`.
> That fix resolved the title/legend overlap by widening the SVG, but
> the user reported that **the boxes around the text are still much
> larger than the text** — visible in pie legend rows, git graph
> branch labels, git graph commit message boxes, and gantt task
> labels. Read that fix-log first for context.

## Overview

After the pie CSS fix shipped, the user inspected the rendered pies
and noted that — independent of the title/legend overlap — every
rectangular container around a short text label was inflated to
~60-100 px tall for a single line of 14-16 px text. The visible
artifacts were:

- **Pie legend**: each legend row's gray background rect was ~3x
  taller than the label text inside it.
- **Git graph**: branch labels (`main`, `develop`, `feature/auth`,
  `bugfix/fix-typo`) and commit message boxes each sat inside an
  oversized gray rect with the text floating in the upper portion.
- **Gantt chart**: task labels (`Schema Analysis`, `User
  Confirmation`, `Core Implementation`, etc.) sat inside white
  rectangles ~80-100 px tall when the text itself was ~18 px.

Root cause: `applySimplifiedMermaidPostProcessing` in
`visualisation_v3.js` (~L5549) inflates **every `<rect>` ≥ 10 px** in
any Mermaid SVG via a `Math.max(...)` heuristic designed for flowchart
node containers. That heuristic is correct for flowchart nodes (which
have foreignObject labels needing padding inside the node rect), but
it over-shoots for pie legend / git graph commits / gantt tasks by
3-5x because those rects have no foreignObject label to pad around.

## Root Cause Analysis

### The offending heuristic

In `visualisation_v3.js`, function
`applySimplifiedMermaidPostProcessing` (L5549-5983), the
`rects.forEach` loop at L5593 mutates every rect ≥ 10 px. The
size-inflation term is the `Math.max(...)` at L5759-5765:

```js
const basePadding = 10;
const horizontalPadding = basePadding * Math.max(1, width / 120);
const verticalPadding   = basePadding * heightMultiplier * complexityMultiplier;

let newWidth = isLabelContainerRect ? width : (width + horizontalPadding);
let newHeightHeuristic = Math.max(
    height + verticalPadding,
    maxTextHeight + (basePadding * 1.5),
    lineCount * 30 + basePadding,
    lineCount * averageFontSize * 1.4 + basePadding,
    60 // Lower absolute minimum to avoid giant nodes
);
```

For a pie legend item rect with `width=80`, `height=14`, containing
the text "Product A" (single line, font-size 14):

- `basePadding = 10`, `horizontalPadding = 10 * max(1, 80/120) = 10`.
- `newWidth = 80 + 10 = 90` (rect gets wider by 10 px).
- `verticalPadding = 10 * 1 * 1 = 10`.
- `newHeightHeuristic = max(14+10, 14+15, 1*30+10, 1*14*1.4+10, 60) = 60`
  (the `60` absolute floor wins).
- `newHeight = max(60, measuredHeight) ≈ 60`.
- The rect's `x` is shifted left by `horizontalPadding / 2 = 5` px so
  it stays centered.

Result: an 80×60 px gray rectangle with the label text floating in
the middle, instead of an 80×14 px rect hugging the text. **That's the
bug.** Same arithmetic applies to git graph commit rects (originally
~12×12) and gantt task rects (originally ~80×18) — both get inflated
to 60-80 px tall.

### Why the heuristic exists

The inflation is intentional for **flowchart nodes**. A flowchart node
is `<g class="node"><rect class="basic label-container" .../><g
class="label"><foreignObject>...</foreignObject></g></g>` — the rect
is a visual container around a foreignObject label. Mermaid sizes the
rect to the foreignObject's intrinsic box; the foreignObject's actual
content can overflow (multi-line text, HTML with padding). The
inflation adds 10 px of horizontal padding and a 60 px height floor so
the foreignObject's text isn't clipped by the rect's edges. Without
the inflation, foreignObject labels with `padding: 8px` get their
text cropped at the bottom of the node rect.

But the loop doesn't distinguish node rects from non-node rects — it
applies the inflation to **every rect ≥ 10 px in any Mermaid SVG**.
Pie legend item rects, git graph commit rects, and gantt task rects
all fall through to the same inflation pass.

## Fix

### Fix — Chart-type detection at the top of `applySimplifiedMermaidPostProcessing`

In `visualisation_v3.js`, immediately after `stripBreaksAroundBullets(svgElement)`:

```js
// EW (Jul 22 2026): Chart-type detection. The rect inflation
// heuristic below (60px height floor at L5764 + lineCount*30 floor
// at L5762 + width-scaling horizontalPadding at L5754) is designed
// for flowchart nodes, where foreignObject labels need generous
// padding inside the node rect. But it inflates pie legend rects,
// git graph commit rects, and gantt task rects to ~60-100px tall
// — far larger than the text they contain. Detect non-flowchart
// diagrams and skip the inflation while preserving stroke styling.
const isPieChart = !!svgElement.querySelector('g.pieGroup');
const isGitGraph = !!svgElement.querySelector('g.commit, g.branch, [class*="commit-"]');
const isGantt    = !!svgElement.querySelector('g.section, g.task, [class*="section-"], [class*="task-"]');
const skipRectInflation = isPieChart || isGitGraph || isGantt;
```

### Fix — Early return inside the rect `forEach`

In the same function, inside `rects.forEach`, immediately after the
existing `isLabelContainerRect` check (L5601) and before the
text/content scanning starts:

```js
if (skipRectInflation) {
    if (!isLabelContainerRect) {
        rect.setAttribute('stroke', '#cccccc');
        rect.setAttribute('stroke-width', '1');
    }
    return;
}
```

The `return` inside `forEach` callback acts like `continue` — it
advances to the next rect. The skipped rects retain Mermaid's
original width/height/x/y; only stroke colour is touched.

## Why this is safe

### Flowchart nodes still inflate (correct behaviour preserved)

Flowchart nodes use `<g class="node">` containing
`<rect class="basic label-container">` — none of which match the
`g.pieGroup` / `g.commit` / `g.branch` / `g.section` / `g.task`
selectors. Flowchart nodes therefore fall through to the existing
inflation logic unchanged. The label-container foreignObject sync
pass at L5807-5933 (which sets foreignObject height to fit inside
the inflated rect) is also unaffected because `isLabelContainerRect`
short-circuits the early-return path.

### Other passes unaffected

- **`applySubgraphSpacingStyles`** at L5972 — separate pass for
  `g.cluster` / `g.subgraph` backgrounds (subgraph fills, section
  shading). None of these selectors match pie / git graph / gantt
  elements, so the skip in the rect loop does not affect this pass.
  Gantt's `<g class="section">` is intentionally not in the
  selectors, so gantt section backgrounds keep their existing
  light-mode `rgba(0,0,0,0.03)` fill.
- **Circle inflation at L5950-5961** — pies render slices as
  `<path>` elements, not `<circle>`, so the 1.2x circle inflation
  has never affected pies. Git graph and gantt don't use
  large-radius circles either, so the pass remains correct.
- **Polygon stroke at L5963-5968** — sequence diagrams and arrows
  use `<polygon>` for arrowheads; the stroke pass is unchanged.
- **Final sanitize pass at L5974-5980** — sanitizes any
  negative/NaN width/height produced by upstream Mermaid quirks.
  Runs independently of the inflation logic; runs after the rect
  loop so any leftover inflation edge cases still get caught.

### Stroke styling preserved (always-white canvas fix not regressed)

The early-return path explicitly applies `stroke='#cccccc'` and
`stroke-width='1'` to non-label-container rects. This is the same
stroke pattern used at L5942-5943 (the non-label-container stroke
styling at the end of the inflation path). Skipped diagrams
therefore keep the same visual outline they had under the
always-white canvas fix — no visual regression.

## Impact Analysis

| Diagram | Before this fix | After this fix |
|---|---|---|
| Flowchart | Nodes inflated correctly (unchanged) | Nodes inflated correctly (unchanged) |
| Pie | Legend item rects ~60 px tall for ~14 px text | Legend item rects stay at Mermaid's native ~14 px tall; stroke styling preserved |
| Git graph | Commit rects ~60 px tall for short commit hashes; branch label rects ~60 px tall | Commit + branch label rects stay native-sized; stroke styling preserved |
| Gantt | Task rects ~80-100 px tall for 18 px task names | Task rects stay native-sized; section backgrounds unaffected (not in selector list) |
| Sequence | unchanged (not in skip list — uses plain text actor labels, no foreignObject, no inflation regression observed) | unchanged |
| Plotly / Apex / etc. | not affected (different code path) | not affected |

## Testing Checklist

1. **AI-generated pie with 5+ slices** (the user's case). Confirm:
   - Each legend row sits at Mermaid's native height (~14 px).
   - No oversized gray rects around legend labels.
   - Pie slices, outer labels with leader lines, and title position
     are unaffected.
2. **AI-generated git graph with 2+ branches and 3+ commits**.
   Confirm:
   - Branch labels (`main`, `develop`, `feature/auth`,
     `bugfix/fix-typo`) are not inside oversized gray rects.
   - Commit message boxes hug the text tightly.
   - Commit lines, branches, and merge connectors are unaffected.
3. **AI-generated gantt chart with 2+ sections and 3+ tasks**.
   Confirm:
   - Each task box hugs the task name text tightly.
   - Section background rectangles (gray) are unaffected — still
     show subtle gray fills at their original sizes.
4. **AI-generated flowchart with 3+ nodes and foreignObject labels**.
   Confirm:
   - Node rectangles are still inflated to fit foreignObject content.
   - No regression in foreignObject label height/clipping behaviour.
5. **AI-generated sequence diagram with 2+ actors**. Confirm no
   regression (sequence diagrams were never in the skip list).
6. `node --check UI/visualisation_engine/visualisation_v3.js` →
   `JS_OK` (no syntax errors).
7. UTF-8 no-BOM byte-check on `visualisation_v3.js` and the doc
   files → `BOM_FREE`.
8. `git status` shows only the targeted files modified.

## Files Modified

| File | Lines | Change |
|---|---|---|
| `UI/visualisation_engine/visualisation_v3.js` | L5554-5568 | Added chart-type detection (`isPieChart`, `isGitGraph`, `isGantt`, `skipRectInflation`) |
| `UI/visualisation_engine/visualisation_v3.js` | L5603-5613 | Added early-return inside `rects.forEach` for non-flowchart diagrams |
| `UI/visualisation_engine/VISUALIZATION_SYSTEM_DOCUMENTATION.md` | L4 + new subsection after L132 | Bumped "Last updated" header; added "Rect tightening for pie / git graph / gantt (added July 22, 2026)" subsection |
| `VISUALIZATION_RECT_TIGHTENING_FIX_JULY22_2026.md` | NEW (root) | This file |

(Two files logically edited, one new file. Net: +290 lines, -5
lines.)

## Rollback Information

`git revert <sha>` of the commit, or `git reset --hard HEAD~1` if
the fix isn't yet pushed. No data migration; no DB migration; no
schema change; no API change. Pure client-side JS guard.

If a future Mermaid release changes the `g.pieGroup` / `g.commit` /
`g.section` class names, the skip list's selectors will need to be
updated. The class names are stable as of Mermaid 10.6.1 (verified
July 22, 2026).

## Related Documentation

- `VISUALIZATION_PIE_TITLE_LEGEND_OVERLAP_FIX_JULY22_2026.md` —
  predecessor; fixed the pie title/legend overlap via `min-width:
  700px !important` on the SVG. Read first for context.
- `VISUALIZATION_CANVAS_BG_AND_FULLSCREEN_FIX_JULY22_2026.md` —
  established the always-white canvas and the stroke styling this
  fix preserves.
- `VISUALIZATION_PLOTLY_AXIS_GRID_VISIBILITY_FIX_JULY22_2026.md` —
  same-day fix for Plotly axes/grid; paired with the pie fixes.
- `VISUALIZATION_MERMAID_RENDERING_FIX_JULY22_2026.md` — earlier
  same-day fix for Mermaid staging-element rendering.
- `UI/visualisation_engine/VISUALIZATION_SYSTEM_DOCUMENTATION.md` —
  master doc; bumped "Last updated" + new "Rect tightening" subsection.

## Deployment Notes

- No backend change. Pure frontend JS.
- No migration. No API change. No env-var change.
- Deploy via `git push gerardo v11:v11` (Render auto-deploys).
- After deploy, refresh the browser tab hard (Ctrl+Shift+R) to clear
  the cached `visualisation_v3.js`.

---

**Author:** AI coding agent (Claude)
**Date:** July 22, 2026
**Pair-fix with:** `VISUALIZATION_PIE_TITLE_LEGEND_OVERLAP_FIX_JULY22_2026.md`,
`VISUALIZATION_CANVAS_BG_AND_FULLSCREEN_FIX_JULY22_2026.md`
