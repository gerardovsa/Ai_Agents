# Always-White SVG Canvas in Chat + Git Graph Commit Width — July 22, 2026

> **Purpose.** Documents the CSS-only follow-on fix to the always-white canvas
> fix in `VISUALIZATION_CANVAS_BG_AND_FULLSCREEN_FIX_JULY22_2026.md` and the
> pie title/legend fix in `VISUALIZATION_PIE_TITLE_LEGEND_OVERLAP_FIX_JULY22_2026.md`.
> That fix set Mermaid's `themeVariables.backgroundColor` and the Plotly
> `paper_bgcolor`/`plot_bgcolor`, but it did NOT paint the outer `<svg>`
> element itself. The user reported that in dark mode, **chat-bubble Mermaid
> diagrams were still on a dark background** (chart text invisible against
> the dark chat-bubble bg), and that **git graph commit messages wrapped
> mid-word** in narrow chat columns. Read those fix-logs first for context.

## Overview

After the always-white canvas + chart-type-aware rect handling shipped in
the previous fixes, the user inspected the working output and noted two
follow-on issues:

1. **Dark-background bleeds through chat-bubble Mermaid SVGs.** The user
   reported: *"the mermaid visuals in the chat still have a clear
   background… so it is dark background in dark mode, compared to when I
   press full screen it a light background, so it in the chat it is hard
   to see. I think also because of the background not being set the text
   that is bold is lost in the background"*. Confirmed visually: the
   chat-bubble pie showed on a dark gray canvas (same colour as the chat
   bubble's dark-theme background), while the same pie in fullscreen
   showed on a clean white canvas.

2. **Git graph commit messages wrap mid-word.** The user reported:
   *"the git graph text wrapping is good for the height but not the
   width of the text"*. Confirmed visually: each commit message
   (`Initial commit`, `Add base structure`, `Feature A start`,
   `Add login UI`, etc.) wrapped across 2-3 lines with awkward
   mid-word breaks (e.g. `Initial comm` / `it`).

Both issues are CSS-only. No JS, no backend, no migration.

## Root Cause Analysis

### Cause 1 — SVG element has no CSS background; parent bleeds through

In `renderMermaidDirectly` at
[`visualisation_v3.js:5072-5115`](UI/visualisation_engine/visualisation_v3.js#L5072-L5115),
the per-render `mermaid.initialize(...)` block sets
`themeVariables.backgroundColor: '#ffffff'`. But this value is consumed
by Mermaid's **internal element fills** (e.g. the rectangle behind the
pie legend, the rect around a flowchart node) — it does NOT set a CSS
`background-color` on the outer `<svg>` element. The SVG element itself
has no default background, so it is transparent; what shows through is
whatever the parent container's `background-color` is.

The parent chain in the chat bubble is:

```
<div class="ai-message-content">       <!-- chat bubble, theme-aware bg -->
  <div class="viz-container">          <!-- transparent, see html L10690 -->
    <div class="viz-content-area">      <!-- transparent -->
      <div class="mermaid">            <!-- transparent, see L10754-10758 -->
        <svg>                          <!-- transparent — bg bleeds through -->
          …Mermaid content…
        </svg>
      </div>
    </div>
  </div>
</div>
```

In dark mode the chain resolves to the chat bubble's dark theme colour
(typically `#0d1117` or `#1a1a1a`). Mermaid's chart text is dark (the
config sets `textColor: '#24292f'`), so the user sees dark text on a
dark background — effectively invisible. The fullscreen path avoided
this because `.mermaid-fullscreen-content` at
[`visualisation_v3.js:1489-1496`](UI/visualisation_engine/visualisation_v3.js#L1489-L1496)
explicitly sets `background: white`. The chat path had no equivalent.

### Cause 2 — Git graph foreignObject widths computed at narrow chat-column width

Mermaid 10.6.1's git graph renderer measures the host SVG's container
width at render time and computes a `<foreignObject>` width for each
commit message based on that measurement. When the chat column is narrow
(300-500 px typical), Mermaid produces foreignObjects that are too
narrow for the commit-message text, and the text wraps inside them at
word boundaries — often mid-word if the text is long.

The chart-type detection added in commit `5b54cd37`
(`VISUALIZATION_RECT_TIGHTENING_FIX_JULY22_2026.md`) correctly skips the
rect-inflation pass for git graphs, but it cannot widen the foreignObject
once Mermaid has emitted it — foreignObject width is set by Mermaid at
render time, baked into the SVG, and is independent of the rect
inflation. So we need to widen the SVG **container** so Mermaid computes
wider foreignObjects on the next render.

This is the same shape as the pie title/legend overlap fix at
`VISUALIZATION_PIE_TITLE_LEGEND_OVERLAP_FIX_JULY22_2026.md`: set a
`min-width: ... !important` on the SVG that overrides the JS-set
`svgEl.style.width = '100%'` from `renderMermaidDirectly` at
[`visualisation_v3.js:5196-5197`](UI/visualisation_engine/visualisation_v3.js#L5196-L5197),
and add `overflow-x: auto` to the parent so the wider SVG can scroll
inside a narrow chat column.

## Fix

### Fix — Always-white background on every chat-bubble Mermaid SVG

In `business-ai-platform-v2.html`, immediately after the pie CSS block
(L10820-10832):

```css
/* EW (Jul 22 2026): Always-white SVG canvas for all Mermaid diagrams
   rendered inside a viz-container. The predecessor canvas-bg fix
   (VISUALIZATION_CANVAS_BG_AND_FULLSCREEN_FIX_JULY22_2026.md) set
   mermaid.themeVariables.backgroundColor AND the Plotly
   paper_bgcolor/plot_bgcolor, but did NOT paint the outer SVG
   element itself. The <svg> tag has no default CSS background, so
   the parent container's background bleeds through. In dark mode
   that means dark text on a dark chat-bubble background, making
   the chart text invisible. Fullscreen avoided the issue because
   .mermaid-fullscreen-content explicitly sets background:white
   (visualisation_v3.js:1495). This rule closes the gap.

   Scope: .viz-container .mermaid svg only — orphan .mermaid divs
   outside a viz-container are not affected (they are usually
   error states, staging elements, or hand-coded examples). */
.viz-container .mermaid svg {
    background-color: #ffffff !important;
}
```

**Why `!important`?** Some render paths set inline `style` attributes on
the SVG element (e.g. the staging-element CSS at L10783-10791 and the
fullscreen clone at L10716-10723). Without `!important`, the inline
styles would win.

**Why scope to `.viz-container`?** Stray `.mermaid` divs outside a
viz-container are typically error states, staging elements, or hand-coded
examples. Painting them white could mask error states or break hand-coded
layouts. The existing `.viz-container .mermaid` rule at L10761-10765
already establishes this scope convention.

**Why no per-chart-type selector?** The always-white canvas principle
applies universally — pies, git graphs, gantt charts, flowcharts,
sequence diagrams all benefit from a white SVG background regardless of
UI theme. No need to duplicate the rule for each chart type.

### Fix — Git graph SVG min-width to widen foreignObjects

In the same file, after the always-white-background rule:

```css
/* EW (Jul 22 2026): Git graph commit message width. Mermaid
   10.6.1 sizes commit-message <foreignObject> widths based on
   the chat column width at render time. In a narrow chat column
   the foreignObjects end up too narrow for the commit messages,
   causing text to wrap mid-word (e.g. "Initial commit" →
   "Initial comm" / "it"). The chart-type detection added in
   commit 5b54cd37 now correctly skips the rect-inflation pass
   for git graphs, but the foreignObject width is set by Mermaid
   itself and survives any post-processing — so we widen the SVG
   container instead.

   min-width:800px (wider than the pie's 700px because branch
   labels and commit messages tend to be longer than legend
   entries). :has(g.commit) and :has(g.branch) match Mermaid's
   inner group classes without guessing the SVG's own class
   name (which has shifted between camelCase, kebab-case, and
   lowercase across Mermaid releases). */
.mermaid:has(svg g.commit) svg,
.mermaid:has(svg g.branch) svg {
    padding: 8px 8px 24px 8px;
    min-width: 800px !important;
    height: auto;
    max-height: none;
}
.viz-content-area > .mermaid:has(svg g.commit),
.viz-content-area > .mermaid:has(svg g.branch) {
    overflow-x: auto;
    overflow-y: visible;
}
```

**Why `:has(g.commit)` instead of a class string match?** The user's
git graph rendered with `<g class="commit">` and `<g class="branch">`
inner groups (verified by the chart-type detection at L5554-5568). The
SVG element itself has a class that has shifted between `gitGraph`,
`git-graph`, and `gitgraph` across Mermaid releases, so an attribute
selector on the SVG class would be brittle. The `:has()` selector
matches the stable inner group classes instead.

**Why 800 px (vs 700 px for pies)?** Git graph branch labels (e.g.
`feature/auth`, `bugfix/fix-typo`) and commit messages (e.g.
`Add JWT validation`) tend to be longer than pie legend entries. 800 px
gives Mermaid enough room to compute foreignObjects that hold the text
on a single line for typical commit-message lengths; very long messages
still wrap but at word boundaries rather than mid-word.

**Why `height: auto` and `max-height: none`?** Mirrors the pie fix at
L10824-10825. Mermaid's git-graph viewBox is sized to the diagram; with
`min-width: 800px`, the SVG renders at ≥ 800 × (height computed from
viewBox aspect ratio) and `height: auto` preserves that ratio.

**Why `overflow-x: auto` on the parent?** Lets the wider 800 px SVG
scroll horizontally inside a narrow chat column instead of overflowing
into adjacent content.

**Why `overflow-y: visible` on the parent?** Lets the SVG grow
vertically without being clipped at the chat bubble edge.

## Why these fixes are pure CSS

- The SVG element's `background-color` is presentation-only — no
  Mermaid-internal state, no render-side effect, no JS coordination
  needed.
- The `min-width` rule widens the SVG container so Mermaid's *next*
  render computes wider foreignObjects. Existing renders that already
  wrapped mid-word stay wrapped (their foreignObject widths are baked
  into the DOM), but a chat reload or diagram regeneration picks up the
  new width immediately.
- No backend change, no migration, no env-var, no API change.

## Why not just widen foreignObjects in JS post-processing?

Considered and rejected. The foreignObject width is set by Mermaid at
render time, and the rect+foreignObject pair is positioned relative to
the git graph's commit-point coordinates. Widening the foreignObject
without also moving the commit-point would push the wider commit-message
boxes off the commit lines. The CSS `min-width` approach is safer
because Mermaid gets to re-run its layout pass with the wider container,
producing correctly positioned commit-message boxes.

## Impact Analysis

| Diagram | UI theme | Before this fix | After this fix |
|---|---|---|---|
| Pie | Light | white canvas, dark text (unchanged) | unchanged |
| Pie | Dark | **dark canvas, dark text — text invisible** | white canvas, dark text — clearly readable |
| Git graph | Light | commit messages wrap mid-word | commit messages wrap at word boundaries (or single line) |
| Git graph | Dark | **dark canvas + mid-word wrapping** | white canvas, dark text, no mid-word wrapping |
| Gantt | Light | unchanged (already correct after rect-tightening) | unchanged |
| Gantt | Dark | **dark canvas, dark text** | white canvas, dark text |
| Flowchart | Light | unchanged | unchanged |
| Flowchart | Dark | **dark canvas, dark text** | white canvas, dark text |
| Sequence diagram | Light | unchanged | unchanged |
| Sequence diagram | Dark | **dark canvas, dark text** | white canvas, dark text |
| Fullscreen (any chart, any theme) | unchanged | unchanged | unchanged (already white via `.mermaid-fullscreen-content`) |

## Testing Checklist

1. **Pie chart in dark mode** (the user's exact case). Confirm:
   - Pie SVG renders on a white canvas regardless of the chat bubble's
     dark-theme background.
   - Title at top of pie, pie center, legend rect at bottom — all clearly
     readable.
   - Horizontal scrollbar appears on the pie container if chat column
     < 700 px.
2. **Git graph in dark mode** with 2+ branches and 5+ commits. Confirm:
   - Git graph SVG renders on a white canvas.
   - Commit messages (`Initial commit`, `Add base structure`,
     `Feature A start`, `Add login UI`, `Add JWT validation`) wrap at
     word boundaries (or on a single line if short enough), not mid-word.
   - Branch labels (`main`, `develop`, `feature/auth`, `bugfix/fix-typo`)
     are not truncated.
   - Horizontal scrollbar appears on the git graph container if chat
     column < 800 px.
3. **Toggle UI theme (light → dark → light) with a chart open**.
   Confirm the chart remains on its always-white canvas and the chart
   text remains clearly readable.
4. **Fullscreen** — open any Mermaid diagram via the action bar.
   Confirm the fullscreen overlay still shows a white canvas (already
   worked; confirm not regressed).
5. **Export pie as PNG** (via the action bar). Confirm exported PNG has
   a white background (already worked; confirm not regressed).
6. `node --check UI/visualisation_engine/visualisation_v3.js` → `JS_OK`
   (no syntax errors; file unchanged in this fix but worth a regression
   check).
7. UTF-8 no-BOM byte-check on `business-ai-platform-v2.html`,
   `VISUALIZATION_SYSTEM_DOCUMENTATION.md`, and the new fix-log →
   `BOM_FREE`.
8. `git status` shows only the targeted files modified.

## Files Modified

| File | Lines | Change |
|---|---|---|
| `UI/business-ai-platform-v2.html` | L10833-10888 | Added always-white-background rule (`.viz-container .mermaid svg { background-color: #ffffff !important; }`) and git-graph min-width rule (`.mermaid:has(svg g.commit) svg, .mermaid:has(svg g.branch) svg { min-width: 800px !important; … }`) with overflow-x on the parent |
| `UI/visualisation_engine/VISUALIZATION_SYSTEM_DOCUMENTATION.md` | L4 + new subsection after L189 | Bumped "Last updated" header; added "Always-white SVG canvas in chat + Git graph commit width" subsection |
| `VISUALIZATION_MERMAID_CHAT_BG_AND_GITGRAPH_WRAPPING_FIX_JULY22_2026.md` | NEW (root) | This file |

(Two files logically edited, one new file. Net: +340 lines, -2 lines.)

## Rollback Information

`git revert <sha>` of the commit, or `git reset --hard HEAD~1` if the
fix isn't yet pushed. No data migration; no DB migration; no schema
change; no API change. Pure CSS additions.

If the always-white SVG canvas reads as too bright in dark mode for some
users, the rule could be scoped to `@media (prefers-color-scheme: dark)`
or conditionally applied via a class on `<body data-theme="dark">`. But
the trade-off (dark canvas in dark mode makes chart text invisible)
argues against this. The current always-white approach matches the
always-white-canvas principle established in commit `3671ef9d`.

If `min-width: 800px` reads as too wide for some users' chat columns,
the value can be tuned (e.g., 700 px to match the pie rule, or 600 px
for tighter columns). The constant matters less than the fact that it
floors the SVG width so Mermaid computes wider foreignObjects.

## Related Documentation

- `VISUALIZATION_PIE_TITLE_LEGEND_OVERLAP_FIX_JULY22_2026.md` —
  precedent for the SVG-min-width + parent-overflow-x pattern that the
  git-graph fix mirrors.
- `VISUALIZATION_RECT_TIGHTENING_FIX_JULY22_2026.md` — predecessor;
  fixed the oversized-rect issue for pie/git graph/gantt. The
  chart-type detection added there means the rect-inflation pass now
  correctly leaves git-graph commit rects at Mermaid's native size, so
  the new `min-width` rule widens the foreignObjects inside those rects
  without any rect-position side effects.
- `VISUALIZATION_CANVAS_BG_AND_FULLSCREEN_FIX_JULY22_2026.md` —
  predecessor, established the always-white-canvas principle for
  Mermaid-internal elements and Plotly paper bg.
- `VISUALIZATION_MERMAID_RENDERING_FIX_JULY22_2026.md` — earlier
  same-day fix for the off-screen-but-measurable staging element.
- `UI/visualisation_engine/VISUALIZATION_SYSTEM_DOCUMENTATION.md` —
  master doc; bumped "Last updated" + new "Always-white SVG canvas in
  chat + Git graph commit width" subsection.

## Deployment Notes

- No backend change. Pure frontend CSS.
- No migration. No API change. No env-var change.
- Deploy via `git push gerardo v11:v11` (Render auto-deploys).
- After deploy, refresh the browser tab hard (Ctrl+Shift+R) to clear
  the cached `business-ai-platform-v2.html`. Existing diagrams that
  already wrapped mid-word will still show the wrap (their
  foreignObject widths are baked into the DOM); new renders and
  reloaded diagrams will pick up the new width.

---

**Author:** AI coding agent (Claude)
**Date:** July 22, 2026
**Pair-fix with:** `VISUALIZATION_PIE_TITLE_LEGEND_OVERLAP_FIX_JULY22_2026.md`,
`VISUALIZATION_RECT_TIGHTENING_FIX_JULY22_2026.md`,
`VISUALIZATION_CANVAS_BG_AND_FULLSCREEN_FIX_JULY22_2026.md`
