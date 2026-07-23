# Visualization System Architecture Documentation

**Date:** November 15, 2025
**Last updated:** July 23, 2026 (Pie overlap (explicit dims) + Bold-in-chat (foreignObject override) + `<br/>` normalisation in `processNodeLabel`; Always-white SVG canvas in chat + Git graph commit width; Rect tightening for pie/git graph/gantt; Pie title/legend overlap fix; Fullscreen single-fit + ResizeObserver; Plotly axis/grid colour-strengthening; Native bold/`<br/>` label preservation + Stadium/Cylinder/Hexagon SVG sizing + Mermaid asymmetric-shape syntax guidance)
**Purpose:** Complete guide to understanding how streamingTwoRule.js and visualisation_v3.js work together
**Use Case:** Integrating visualization rendering into Tiptap document containers

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Pattern](#architecture-pattern)
3. [File Responsibilities](#file-responsibilities)
4. [Integration Flow](#integration-flow)
5. [Tiptap Integration Guide](#tiptap-integration-guide)
6. [API Reference](#api-reference)
7. [Usage Examples](#usage-examples)

---

## System Overview

The visualization system consists of **two complementary files** that work together to render mixed content (text + visualizations) in real-time streaming scenarios:

### streamingTwoRule.js (107 KB, 2,545 lines)
**Role:** Content Parser & Stream Controller  
**Responsibility:** Parse incoming AI content streams, classify content as markdown or visualization, manage rendering lifecycle

### visualisation_v3.js (~441 KB, 10,398 lines)
**Role:** Visualization Rendering Engine
**Responsibility:** Actually render visualizations (Mermaid, Plotly, etc.) with proper styling, export, and interactive features

### Relationship
```
AI Stream → streamingTwoRule.js → visualisation_v3.js → Rendered Output
           (Parser/Controller)      (Rendering Engine)
```

### Mermaid Render Lifecycle (added July 20, 2026)

Mermaid 10.x is sensitive about its temporary staging element. When `mermaid.render(id, source)` is called, the library creates a body-level element with `id="d" + id` and measures it to compute the SVG geometry. Three invariants must be preserved:

1. **Do not `display:none` the staging element.** Hiding it mid-render collapses its bounding rect to 0x0, which makes pies emit `viewBox="0 0 0 450"` and flowcharts throw `Could not find a suitable point for the given distance` from `calcLabelPosition`. The engine keeps the staging element off-screen but measurable via a global rule in `business-ai-platform-v2.html` (`position: fixed; top: -10000px; left: -10000px; visibility: hidden; min-width: 700px; display: block`).
2. **Do not strip, sanitize, or remove any node whose id starts with `dmermaid` while a render is in flight.** The engine's `_installMermaidStyleGuard()` therefore does NOT match `#d?mermaid…` selectors and does NOT remove `dmermaid*` nodes from a `MutationObserver`; Mermaid owns the staging-node lifecycle and cleans it up after `render()` settles.
3. **Retry attempts are bounded.** If the visible container starts at 0-px wide (deferred thread, hidden tab, collapsed panel), the engine parses the SVG and rejects any viewBox whose width or height is non-positive. It then schedules a re-render with a fresh chart id, but caps retries at `MAX_MERMAID_RETRIES = 2`. Retry chart ids are always `<originalBase>-retry-<N>` (never timestamped, never chained off a previous retry id) so the id space stays bounded. If the final attempt still has a broken viewBox, the engine surfaces a real error via `showMermaidError()` instead of looping.

The container's own responsive sizing also matters: `.mermaid-container` uses `min-width: 0` and `box-sizing: border-box` so Mermaid can render correctly inside a narrow chat column without overflowing its parent.

### Staging vs. visible width (added July 20, 2026)

Mermaid's render pipeline decouples *layout width* from *visible width*. `mermaid.render()` measures the body-level staging element (`#d<id>`) for layout — node positions, edge routing, label placement, pie radius — and the resulting SVG is then placed into the visible container with `useMaxWidth: true` scaling it to fit. The engine exploits this: it gives the **staging** element a `min-width: 700px` (via the global rule above) so Mermaid's `calcLabelPosition` has enough horizontal room to find non-colliding offsets for edge labels in a narrow chat column, while the **visible** `.mermaid-container` stays narrow-friendly. If the staging canvas is too narrow, Mermaid emits `Could not find a suitable point for the given distance` (a constraint failure in `calcLabelPosition`); in that case the engine's catch block translates the error into a user-facing hint suggesting `LR` direction, shorter labels, or a wider panel. The rule is scoped to Mermaid staging ids only — Plotly, Apex and CAD use different id conventions and are unaffected.

### Off-screen-but-measurable staging CSS (added July 22, 2026)

The historical SPA-level rule `body > [id^="dmermaid"] { display: none !important }` was meant to hide "any mermaid syntax error elements injected outside viz-containers", but the selector actually matches **Mermaid's legitimate render-staging element** (`d{id}`), not just error overlays. With `display: none`, the staging div's `getBoundingClientRect()` collapses to `{ width: 0, height: 0 }`, so:

- Pie: `viewBox="0 0 0 450"` — height is Mermaid's hard-coded default pie height, width collapses to 0.
- Flowchart: `calcLabelPosition` throws "Could not find a suitable point for the given distance" because edge routing has no horizontal room.

The fix is in `business-ai-platform-v2.html` (around L10730) and replaces `display: none` with `position: fixed; visibility: hidden; top: -10000px; left: -10000px; min-width: 700px; display: block; pointer-events: none;`. The element stays in the layout tree so Mermaid can read its bounding rect, but is never visible to the user. The orphan-`.mermaid`-container selector (`body > .mermaid:not(.viz-container .mermaid)`) is retained as-is — that one matches genuine orphans, not staging nodes. `pie: { useMaxWidth: false }` was tried (Jul 21) and reverted (Jul 22) because `useMaxWidth` only governs post-render CSS scaling, not the viewBox itself — it cannot rescue a 0-wide staging element.

### Always-white canvas + pie label buffer (added July 22, 2026)

Every chart canvas (Mermaid `themeVariables.backgroundColor`, Plotly `paper_bgcolor`) is forced to **`#ffffff`** regardless of UI theme. The UI theme still controls the surrounding chrome — chat-bubble backgrounds, sidebar, etc. — but the chart canvas itself is constant white.

Why:

- **AI-generated chart colours** (axis, grid, title, line) often pick dark colours that read fine against a white canvas in light mode but vanish against a dark canvas in dark mode. A constant white canvas means every AI-picked colour combination is legible regardless of light/dark UI mode.
- **Plotly export consistency.** `Plotly.downloadImage` / `Plotly.toImage` honours `paper_bgcolor`; with a transparent chat-area bg the downloaded PNG had alpha-channel transparency, and with a dark-canvas dedicated path the export was a dark-mode PNG. A white `paper_bgcolor` always yields an opaque white PNG that matches Mermaid's hard-coded-white PNG export.
- **One mental model for "what colour will my chart sit on"** — there is only one: white.

Implementation lives in `visualisation_v3.js`:

- `applyEnhancedPlotlyTheme` (chat-area Plotly path): `bgColor = '#ffffff'`, `textColor = '#24292f'`, `gridColor = '#94a3b8'`, `axisLineColor = '#7c8694'`, `zeroLineColor = '#cbd5e1'` — no `isDark` branching.
- `toggle3DView` (dedicated/calculator Plotly path): same constants — no `isDark` branching.
- `updateTheme` + `updateChartTheme` (theme-toggle retroactive recolor): same constants — no `isDark` branching.
- All 5 `mermaid.initialize()` call sites (chat-area renderer, popup/fullscreen renderer, direction-toggle renderer, `applyMermaidColorTheme`, `applyMermaidFontSize`, `updateChartTheme` mermaid re-init): `theme: 'base'` + always-light `themeVariables` (`primaryColor: '#f0f0f0'`, `nodeBkg: '#f0f0f0'`, `textColor: '#24292f'`, `nodeTextColor: '#24292f'`, `backgroundColor: '#ffffff'`, `lineColor: '#656d76'`).
- `applySimplifiedMermaidPostProcessing`: `text.setAttribute('fill', '#24292f')` always (was: `isDark ? '#e6edf3' : '#24292f'`). The `isDark` parameter has been removed from the function signature; existing callers that still pass it harmlessly ignore.

**Why the `applyMermaidColorTheme` and `applyMermaidFontSize` blocks retain their `primaryTextColor: '#ffffff'`, `textColor: '#ffffff'`, etc.:** those functions are the *themed* entry points where the user explicitly picks a colour palette (forest/neutral/dark via `getMermaidColorThemes()`). The palette paints the node fills in saturated colours, and the `#ffffff` text forces give white text maximum contrast against those fills. They are load-bearing for the themed-coloured-nodes design and are NOT removed — only `theme`, `backgroundColor`, `lineColor`, `edgeLabelBackground` are flipped to light-mode constants.

**Companion fix — pie chart label buffer:** Mermaid 10.6.1 emits pie labels outside the pie with leader lines; in narrow chat columns the SVG can be CSS-scaled down so the labels sit close to the slice edges. The fix is in `business-ai-platform-v2.html` (right after the staging CSS, around L10760):

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

The `:has()` selector keeps the buffer scoped to pies only — other Mermaid types are unaffected. Mermaid's default pie viewBox is 450×450; `max-height: 520px` leaves 70 px of breathing room for the labels.

### Pie title/legend overlap fix (added July 22, 2026)

The pie label buffer above was not enough: in narrow chat columns (≤500 px) the title (`<g class="pieTitle">`, y ≈ 20 in viewBox units) and the legend rect (`<g class="legend">`, y ≈ 400) ended up overlapping the central pie (`<g class="pieGroup" transform="translate(225, 225)">`). Root cause: Mermaid 10.6.1's pie layout positions title, pie center, and legend assuming an SVG ≥ 450 px wide. When the JS-set `svgEl.style.width = '100%'` (see `visualisation_v3.js:4685`) shrinks the SVG to the chat column width, Mermaid's algorithm has insufficient room and elements collide into the central pie area.

**Fix shape:** force `min-width: 700px !important` on the pie SVG itself, so Mermaid always gets the width its layout expects. The parent `.mermaid` container gets `overflow-x: auto` so the wider pie SVG scrolls horizontally inside narrow chat columns; `overflow-y: visible` lets it grow vertically without being clipped at the chat bubble edge. `height: auto` preserves the viewBox 1:1 aspect ratio; the previous `max-height: 520px` cap was removed because it distorted the aspect ratio and forced `preserveAspectRatio="xMidYMid meet"` to shrink the pie content.

Why `!important`: the JS at `visualisation_v3.js:4684-4685` sets `svgEl.style.maxWidth = '100%'` and `svgEl.style.width = '100%'` as inline styles. Inline styles beat external CSS unless `!important` is used in the external rule. Without `!important`, our pie-specific `min-width` would be silently overridden by the JS for all charts including pies.

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

Behaviour:

| Chat column width | Pie SVG width | Notes |
|---|---|---|
| ≤ 700 px | 700 px | SVG overflows parent horizontally; `overflow-x: auto` shows a horizontal scrollbar |
| 700–∞ px | 100% of container | SVG grows with container (e.g., fullscreen) |

The `pie: { useMaxWidth: false }` option was considered (and rejected on Jul 21 — see the staging-fix section above). `useMaxWidth` only governs post-render CSS scaling, not Mermaid's internal layout calculations; the `min-width: 700px !important` CSS-only approach addresses the root cause without changing the Mermaid config.

Full historical record: see `VISUALIZATION_CANVAS_BG_AND_FULLSCREEN_FIX_JULY22_2026.md` at the repo root.

### Rect tightening for pie / git graph / gantt (added July 22, 2026)

After the pie title/legend overlap fix above, the user reported that **the boxes around the text are still much larger than the text** — visible across:

- **Pie charts** — each legend row sits inside a huge gray rectangle (the legend item rect inflated to ~60-100 px tall for a single line of label text).
- **Git graphs** — branch labels (`main`, `develop`, `feature/auth`, `bugfix/fix-typo`) and commit message boxes have oversized gray backgrounds extending well past the text.
- **Gantt charts** — task labels (`Schema Analysis`, `User Confirmation`, etc.) sit in white rectangles that are 80-100 px tall instead of hugging the 18 px text inside.

Root cause: `applySimplifiedMermaidPostProcessing` in `visualisation_v3.js` (~L5549) inflates **every `<rect>` ≥ 10 px** in any Mermaid SVG via a `Math.max(...)` heuristic that includes a hard `60` floor and a width-scaling horizontal padding term. That heuristic is correct for **flowchart nodes** (where `foreignObject` labels need generous padding inside the node rect), but it's catastrophic for pie legend rects, git graph commit rects, and gantt task rects — Mermaid already sizes those correctly and they have no foreignObject label to pad around.

Specifically the offending terms (file `visualisation_v3.js`, in `applySimplifiedMermaidPostProcessing`):

- L5754 — `horizontalPadding = basePadding * Math.max(1, width / 120)` — pads wider rects even more.
- L5762 — `lineCount * 30 + basePadding` — single-line text becomes 40 px tall.
- L5764 — `60` absolute minimum floor — every rect is forced to ≥ 60 px tall regardless of content.
- L5843 + L5921 — `minRectH = 50` for label-container compaction (flowchart-only — not affected by the new skip).

For a legend item rect 80 × 14 px containing the text "Product A", the heuristic gives `max(14+10, 14+15, 1*30+10, 1*14*1.4+10, 60) = 60`, then adds width-scaling horizontal padding (`80*10/120 ≈ 7` px), then shifts the rect's `x` left by `horizontalPadding/2`. Result: an 80 × 60 px gray rectangle with the label text floating in the middle — the exact bug in the user's image.

**Fix shape — chart-type detection at the top of `applySimplifiedMermaidPostProcessing`.** Sniff the SVG's group classes to determine the chart type, then `return` early inside the rect `forEach` for non-flowchart diagrams so the size inflation is skipped while stroke styling still applies (preserving the always-white canvas fix).

```js
// EW (Jul 22 2026): Chart-type detection
const isPieChart = !!svgElement.querySelector('g.pieGroup');
const isGitGraph = !!svgElement.querySelector('g.commit, g.branch, [class*="commit-"]');
const isGantt = !!svgElement.querySelector('g.section, g.task, [class*="section-"], [class*="task-"]');
const skipRectInflation = isPieChart || isGitGraph || isGantt;

// ... inside the rects.forEach, after isLabelContainerRect check:
if (skipRectInflation) {
    if (!isLabelContainerRect) {
        rect.setAttribute('stroke', '#cccccc');
        rect.setAttribute('stroke-width', '1');
    }
    return; // skip size/position mutation, move to next rect
}
```

Why this is safe:

- **Flowchart nodes** (`g.node` with `g.label` foreignObject) still get the full inflation pass — those rects legitimately need the padding to avoid clipping their foreignObject labels. None of the sniffed chart-type selectors (`pieGroup`, `commit`, `branch`, `section`, `task`) match flowchart classes, so the skip is precise.
- **`applySubgraphSpacingStyles`** at L5972 (separate pass for `g.cluster` / `g.subgraph` backgrounds) is unaffected by the skip — its selectors don't match pie/git graph/gantt elements, and gantt's `<g class="section">` is not in the targeted selector list, so the section-background rectangles keep their existing light-mode fills.
- **Circle / polygon / sanitize passes** at L5950-5980 still run as before — they don't depend on the rect-inflation logic.
- **Stroke styling is preserved** for the skipped diagrams (light gray `#cccccc` on white canvas), so the always-white canvas fix is not regressed.

Behaviour table after the fix:

| Diagram type | Rect inflation | Stroke styling | Subgraph spacing |
|---|---|---|---|
| Flowchart | ON (unchanged) | ON (unchanged) | ON (unchanged) |
| Pie | SKIPPED | ON (`#cccccc`, 1 px) | unaffected (no `.cluster`/`.subgraph` matches) |
| Git graph | SKIPPED | ON | unaffected |
| Gantt | SKIPPED | ON | unaffected (`g.section` not in selectors) |
| Sequence diagram | unchanged (not in skip list — uses plain text actor labels, no foreignObject, no inflation regression observed) | unchanged | unaffected |

Full historical record: see `VISUALIZATION_RECT_TIGHTENING_FIX_JULY22_2026.md` at the repo root.

### Always-white SVG canvas in chat + Git graph commit width (added July 22, 2026)

Two follow-on issues surfaced once the rect-tightening fix landed:

1. **Chat-bubble Mermaid SVGs were still on a dark background in dark mode.** The always-white canvas fix in `VISUALIZATION_CANVAS_BG_AND_FULLSCREEN_FIX_JULY22_2026.md` set `mermaid.themeVariables.backgroundColor = '#ffffff'` AND the Plotly `paper_bgcolor`/`plot_bgcolor`, but it did NOT paint the outer `<svg>` element itself. Mermaid's SVG has no default CSS background, so the parent container's background bleeds through — in dark mode that means dark text on a dark chat-bubble background, making the chart text invisible. Fullscreen avoided the issue because `.mermaid-fullscreen-content` at `visualisation_v3.js:1495` explicitly sets `background: white`. The chat path had no equivalent.

   **Fix** — CSS-only, scoped to `.viz-container .mermaid svg` (the same scope as the existing `.viz-container .mermaid` rule at `business-ai-platform-v2.html:10761-10765`, so stray Mermaid divs outside a viz-container are not affected):
   ```css
   .viz-container .mermaid svg {
       background-color: #ffffff !important;
   }
   ```
   `!important` is required because some render paths set inline `style` attributes on the SVG element.

2. **Git graph commit messages wrapped mid-word in narrow chat columns.** Mermaid 10.6.1 sizes commit-message `<foreignObject>` widths based on the chat column width at render time. In a narrow chat column the foreignObjects ended up too narrow for the commit messages, causing text to wrap mid-word (e.g. "Initial commit" → "Initial comm" / "it"). The chart-type detection added above correctly skips the rect-inflation pass for git graphs, but the foreignObject width is set by Mermaid itself and survives any post-processing — so we widen the SVG container instead. This mirrors the pie-fix pattern (`min-width: 700px` for pies, `min-width: 800px` here because git-graph branch labels and commit messages tend to be longer than pie legend entries).

   **Fix** — CSS-only, scoped to Mermaid diagrams that contain git-graph inner groups (`g.commit`, `g.branch`). The `:has()` selector matches Mermaid's inner group classes without guessing the SVG's own class name (which has shifted between camelCase, kebab-case, and lowercase across Mermaid releases):
   ```css
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

Why both fixes are pure CSS:

- The SVG element's `background-color` is presentation-only — no Mermaid-internal state, no render-side effect, no JS coordination needed.
- The `min-width` rule widens the SVG so Mermaid's *next* render computes wider foreignObjects (Mermaid measures the SVG's container width before laying out the diagram). Existing renders that already wrapped mid-word stay wrapped, but a chat reload or diagram regeneration picks up the new width immediately.
- No backend change, no migration, no env-var, no API change. Pure CSS additions to `business-ai-platform-v2.html`.

Behaviour table after this fix:

| UI theme | Chat-bubble pie | Chat-bubble git graph | Chat-bubble flowchart | Fullscreen |
|---|---|---|---|---|
| Light | white canvas, dark text (unchanged) | white canvas, dark text, no mid-word wrapping | unchanged | unchanged (already white via `.mermaid-fullscreen-content`) |
| Dark | **white canvas, dark text** (was: dark canvas, invisible text) | **white canvas, dark text, no mid-word wrapping** (was: dark canvas + clipped text) | **white canvas** (was: dark canvas) | unchanged |

Full historical record: see `VISUALIZATION_MERMAID_CHAT_BG_AND_GITGRAPH_WRAPPING_FIX_JULY22_2026.md` at the repo root.

### Pie explicit dims + Bold-in-chat foreignObject override + `<br/>` normalisation (added July 22, 2026)

Three follow-on issues surfaced once the always-white canvas + git-graph commit width fix landed:

1. **Pie title and legend still overlapped the pie** after the previous `min-width: 700px !important` rule. The root cause was that with `min-width` but no `width` / `height`, the SVG's height tracked its own viewBox aspect ratio. In some chat columns that produced a tall-narrow render that pushed Mermaid's title (`<g class="pieTitle">`) and legend rect (`<g class="legend">`) INTO the pie's drawn area. The fix in `business-ai-platform-v2.html` (replacing the previous pie rule around L10820) uses explicit `width` AND `height` (both 760 px, square) with `!important` on every size-related property so the SVG cannot collapse to viewBox-driven sizing:

   ```css
   .mermaid svg[id^="pie-"],
   .mermaid svg[class*="pie"] {
       padding: 8px 8px 32px 8px;
       width: 760px !important;
       height: 760px !important;
       min-width: 760px !important;
       min-height: 760px !important;
       max-width: none !important;
       max-height: none !important;
   }
   .viz-content-area > .mermaid:has(svg[id^="pie-"]),
   .viz-content-area > .mermaid:has(svg[class*="pie"]) {
       min-height: 800px;
       overflow-x: auto;
       overflow-y: visible;
   }
   ```

   Square 760×760 matches Mermaid's natural pie viewBox aspect ratio, so `preserveAspectRatio="xMidYMid meet"` scales content uniformly to fill the box with no letterboxing — title sits above the pie, legend sits below, geometric overlap impossible. The `min-` and `max-` `!important` overrides are required because `renderMermaidDirectly` at `visualisation_v3.js:5196` sets `svgEl.style.width = '100%'` inline; without `!important` the inline style wins.

2. **Bold text rendered white in chat bubbles but black in fullscreen.** Root cause: the chat-markdown CSS at `business-ai-platform-v2.html:10685` sets `color: var(--text-primary)` on every `<strong>` inside `.ai-message-content`. In dark mode `--text-primary` resolves to a white-ish colour. Mermaid's `processNodeLabel` rewrites `<b>bold</b>` to `<strong class="mermaid-bold">bold</strong>` inside the SVG's `<foreignObject>`, which lives inside `.ai-message-content` (chat-bubble DOM path: `.ai-message-content > .viz-container > .viz-content-area > .mermaid > svg > foreignObject`). So the chat markdown rule cascades INTO the foreignObject and overwrites Mermaid's explicit dark colour. The fullscreen clone escapes the cascade because `openMermaidFullscreen` uses `cloneNode(true)` and mounts the clone at the document body root, OUTSIDE `.ai-message-content`. The fix (added to `business-ai-platform-v2.html` right after the always-white canvas rule, around L10859) overrides the cascade with a more-specific selector and `!important`:

   ```css
   .viz-container .mermaid foreignObject strong,
   .viz-container .mermaid foreignObject b,
   .viz-container .mermaid foreignObject .mermaid-bold {
       color: #24292f !important;
   }
   .viz-container .mermaid foreignObject em,
   .viz-container .mermaid foreignObject i,
   .viz-container .mermaid foreignObject .mermaid-italic {
       color: #24292f !important;
   }
   ```

   `#24292f` matches `themeVariables.textColor` from `mermaid.initialize()` at `visualisation_v3.js:5097` — forces bold/italic inside chart labels to the SAME dark colour as the chart's other text. Scoped to `.viz-container .mermaid foreignObject` so chat markdown OUTSIDE Mermaid still uses `var(--text-primary)` as designed.

3. **`<br/>` line breaks silently failed in stadium (A3) and subroutine (A6) shapes** while working correctly in rectangle (A1=A2), diamond (A4), and cylinder (A5). Root cause: `processNodeLabel` in `visualisation_v3.js:5500-5651` had bold handling that recognised BOTH `**...**` markdown AND pre-existing `<b>...</b>`/`<strong>...</strong>` tags, but its line-break handling only recognised literal `\n` (after `\\n` escape). It did NOT recognise `<br/>` or `<br>` self-closing tags. Mermaid 10.6.1's HTML-label parser takes different code paths for stadium and subroutine shapes vs. the other shapes, and those paths require the `<br class="mermaid-br"/>` annotated form to render the break — bare `<br/>` is silently joined to adjacent text. The fix (in `processNodeLabel` TEP 4, around L5580) adds a normalisation step BEFORE the existing `\n` conversion:

   ```js
   // EW (Jul 22 2026): Normalize any <br> / <br/> self-closing tags
   // already in the source.
   processedLabel = processedLabel.replace(/<br\s*\/?\s*>/gi, '<br class="mermaid-br"/>');
   ```

   The regex `/<br\s*\/?\s*>/gi` matches `<br>`, `<br/>`, `<br />`, `<BR>`, `<Br/>` — every realistic variant. The `.mermaid-br` class is idempotent (the regex is a no-op on already-normalised tags), so broadening the scope is safe. After this normalisation, all shape parsers receive the same well-formed `<br class="mermaid-br"/>` marker, so line breaks render consistently across all 6 shape types.

Each fix is isolated to a single file: pie sizing is one CSS rule, the foreignObject override is a new CSS block, the `<br>` normalisation is one regex in `processNodeLabel`. No backend change, no migration, no API change, no env-var change. The fixes also interoperate safely: the always-white canvas (previous fix) + the explicit pie dimensions (fix 1) + the foreignObject colour override (fix 2) compose into a deterministic "white canvas, dark text everywhere" presentation regardless of UI theme, and the `<br>` normalisation (fix 3) affects only line-break rendering — it doesn't change colours, dimensions, or layout.

Full historical record: see `VISUALIZATION_FOLLOWON_PIE_BOLD_BR_FIX_JULY22_2026.md` at the repo root.

### Native bold/`<br/>` label preservation + Node-shape sizing + Asymmetric-syntax doc (added July 23, 2026)

Three follow-on issues surfaced during continued testing of the always-white canvas + foreignObject bold-colour fix. Each is documented in `VISUALIZATION_MERMAID_BOLD_SHAPE_SIZING_FIX_JULY23_2026.md` at the repo root with full investigation detail. Brief summaries:

1. **Bold appeared to "leak" past a `<br/>` into the next line in rectangle-shaped nodes.** Working: `<b>bold</b><br/>plain` (bold correctly resets). Failing: `text<b>bold</b><br/>plain` (bold persists into "plain"); `line1<br/><b>bold</b>line2<br/>line3` (lines 1 and 2 merge). Investigation found no Mermaid-side bold state machine — Mermaid 10.6.1 inserts labels via `.html(...)` into a `<foreignObject><div>` and lets the browser's HTML parser tokenise them. The regression was caused by our own Jul-22 normalisation: `processNodeLabel` rewrote every `<strong>` to `<strong class="mermaid-bold">` and every `<br>` to `<br class="mermaid-br"/>`. The class-bearing tags interacted badly with Mermaid's downstream label-tokenisation pass, which walks the innerHTML after `.html(...)` and may treat `<br>` as a line separator while tolerating bold markup as plain text content. Fix in `processNodeLabel` (visualisation_v3.js:5571-5588) preserves native `<b>`/`<strong>` tags as-is, and emits plain `<br/>` (no class) when bold markup is present:

   ```js
   // TEP 3: Process bold. EW (Jul 23 2026): preserve native
   // <b>/<strong> tags as-is when the user already wrote them.
   if (!/<(?:strong|b)\b/i.test(processedLabel)) {
       processedLabel = processedLabel.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
   }
   const hasBoldMarkup = /<(?:strong|b)\b/i.test(processedLabel);
   ```

   ```js
   // TEP 4: <br> normalisation — conditional on hasBoldMarkup
   processedLabel = processedLabel.replace(/<br\s*\/?\s*>/gi,
       hasBoldMarkup ? '<br/>' : '<br class="mermaid-br"/>');
   processedLabel = processedLabel
       .replace(/\\n/g, '\n')
       .replace(/\n/g, hasBoldMarkup ? '<br/>' : '<br class="mermaid-br"/>');
   ```

   Non-bold labels keep the `.mermaid-br` class so the bullet-spacing cleanup at TEP 5 still works. The foreignObject colour override (previous subsection) targets bare `strong` AND `.mermaid-bold` so both code paths remain styled correctly.

2. **Stadium, cylinder, and hexagon shapes had CRITICAL text clipping/overflow in multi-line labels.** Plain rectangles and rounded rectangles had only minor cosmetic padding issues. The root cause is that Mermaid 10.6.1's default `<svg>` sizing uses natural-aspect-ratio scaling via `preserveAspectRatio="xMidYMid meet"`, which can produce containers too small for curved or angled shapes that have wider/taller label areas than rectangles. Fix in `business-ai-platform-v2.html` (inserted after the pie rule at L10850, before the always-white canvas rule) uses per-shape `:has()` selectors to force explicit width AND height — same principle as the pie fix at L10820-L10850:

   ```css
   .mermaid svg:has(rect.label-container[rx][ry]),     /* stadium (and rounded rect) */
   .mermaid svg:has(path.label-container),              /* cylinder */
   .mermaid svg:has(polygon.label-container) {           /* hexagon */
       max-width: none !important;
       max-height: none !important;
   }
   .mermaid svg:has(rect.label-container[rx][ry]) { width: 560px; height: 300px; ... }
   .mermaid svg:has(path.label-container) { width: 600px; height: 360px; ... }
   .mermaid svg:has(polygon.label-container) { width: 580px; height: 320px; ... }
   ```

   DOM selectors verified against Mermaid 10.6.1's emitted SVG. `!important` overrides the inline `style.width = '100%'` set by `renderMermaidDirectly` at visualisation_v3.js:5196. Plain rounded rectangles share the `rect[rx][ry]` selector with stadium; the 560×300 size is within rounded rectangle's natural range so no regression is expected. If mixed-shape SVGs (one stadium + one cylinder in the same diagram) produce source-order surprises, consolidate all three shapes to a single shared dimension.

3. **`A>Asymmetric Right"]` does not render.** Root cause: `>` is NOT a recognised Mermaid 10.6.1 shape delimiter. The closest equivalents are `A[/Asymmetric Right/]` (lean_right), `A[\Asymmetric Left\]` (lean_left), `A{Odd Shape}` (rect_left_inv_arrow), `A[/Trapezoid one\]` (trapezoid), and `A[\Trapezoid alt/]` (inv_trapezoid). Auto-correcting malformed input would be unsafe because we cannot infer the user's intended shape, so the fix is documentation only. A source-level reference comment was added above `transformMermaidContentToHTML(content)` at `visualisation_v3.js:5500` so future contributors do not re-discover this gap or attempt a runtime repair.

Each fix is isolated to a single file or comment block. The bold fix is one TEP step in `processNodeLabel`; the shape sizing is one CSS block; the asymmetric doc is a comment. No backend change, no migration, no API change, no env-var change. The fixes interoperate safely with the prior Jul-22 work: the always-white canvas + foreignObject colour override still apply uniformly across all shape types, the pie sizing rule is unaffected (its selectors are shape-specific), and the bullet-spacing cleanup at TEP 5 still works because non-bold labels still get the `.mermaid-br` class.

Full historical record: see `VISUALIZATION_MERMAID_BOLD_SHAPE_SIZING_FIX_JULY23_2026.md` at the repo root.

### Fullscreen single-fit + ResizeObserver (added July 22, 2026)

The fullscreen view in `initFullscreenControls` (`visualisation_v3.js`) previously fired three `setTimeout(fitToScreen, 100/500/1000)` after first opening, producing a visible race in the console (the user's log: 4.458 → 0.803 → 4.458 — the middle fit landed while the viewport was transiently narrower mid-CSS-layout, and then a third fit corrected it). There was also no resize listener on the fullscreen overlay, so a window resize after open required the user to manually click `#fit-screen`.

The fix replaces the three-setTimeout chain with:

```js
const initialFit = () => {
    const r = viewport.getBoundingClientRect();
    if (r.width <= 0 || r.height <= 0) {
        requestAnimationFrame(initialFit);  // viewport still settling
        return;
    }
    fitToScreen();
};
requestAnimationFrame(initialFit);

// Live resize support
if (typeof ResizeObserver !== 'undefined') {
    const ro = new ResizeObserver(() => {
        if (this._fullscreenResizeRaf) cancelAnimationFrame(this._fullscreenResizeRaf);
        this._fullscreenResizeRaf = requestAnimationFrame(fitToScreen);
    });
    ro.observe(viewport);
    this._fullscreenResizeObserver = ro;
}
```

The observer is stored on the class instance (`this._fullscreenResizeObserver`) so `closeFullscreen` can disconnect it cleanly — without that disconnect, every fullscreen open would leak an observer that pins the closed overlay in memory.

The companion `reRenderFullscreenIfOpen` (theme-toggle / colour-theme / font-size re-render path) also switched from `setTimeout(() => fitButton.click(), 100)` to `requestAnimationFrame(() => requestAnimationFrame(() => fitButton.click()))` — double-rAF is enough (~32 ms at 60 fps) for the SVG insertion + style flush to settle before the click, replacing the magic 100 ms number.

Full historical record: see `VISUALIZATION_CANVAS_BG_AND_FULLSCREEN_FIX_JULY22_2026.md` at the repo root.

### Plotly axis/grid colour-strengthening (added July 22, 2026)

After the always-white canvas shipped, the user reported that **3D scatter plot axes, plot lines, and the background grid were all invisible** — the same complaint appeared for box plots. Investigation surfaced four layered causes documented as a single fix in `VISUALIZATION_PLOTLY_AXIS_GRID_VISIBILITY_FIX_JULY22_2026.md` (repo root):

1. **`gridColor = '#e1e4e8'` was too pale** (~1.18:1 contrast on white, essentially invisible). Replaced with `#94a3b8` (Tailwind slate-400, ~2.85:1). Also introduced two new constants: `axisLineColor = '#7c8694'` (~4.25:1, used for axis lines and ticks — darker than grid for visual separation) and `zeroLineColor = '#cbd5e1'` (~1.7:1, soft accent for the zero reference line).

2. **`baseLayout` had no 2D `xaxis`/`yaxis` properties** — only polar/3D/geo/ternary branches themed their axes; the Cartesian branch (bar/line/scatter/**box**/histogram/area) fell through to Plotly's `'#eee'` template default. Added `xaxis` and `yaxis` defaults at the top of `baseLayout`. The spread order in the per-chart-type branches is `...baseLayout, ...plotlyData.layout`, so AI-supplied axis properties still win when present — our defaults only fill the gap when the AI omits them.

3. **`toggle3DView` synthesised scene had no per-axis colours** — only `{title: '...'}`. Added full per-axis `gridcolor`/`linecolor`/`tickcolor`/`zerolinecolor`/`zerolinewidth: 2` plus `scene.bgcolor` to match the AI-3D path.

4. **`updateTheme` and `updateChartTheme` did not push `scene.*` relayout paths** — even when the user toggled UI theme on an existing 3D chart, the scene axes were stuck at their original values. Added a trace-type sniff (same `'scatter3d' | 'surface' | 'mesh3d' | ...` set used by `applyEnhancedPlotlyTheme`'s `chartTypes.has('3d')`) so 3D charts get the scene relayout and 2D charts don't get invalid paths pushed.

**Conceptual trap that caused cause 4:** in Plotly, 2D axes use `layout.xaxis.*` / `layout.yaxis.*` paths, but 3D scene axes use `scene.xaxis.*` / `scene.yaxis.*` / `scene.zaxis.*` — they do NOT inherit from 2D. Setting `xaxis.gridcolor` does NOT change `scene.xaxis.gridcolor`. This is what hid the scene axes when only the 2D relayout paths fired.

**Why darker is better than subtler:** the previous `#e1e4e8` was right for soft UI borders but wrong for chart axes — axis lines and gridlines have to be *perceived* by a user scanning a dense chart, so ~3:1+ contrast reads as crisp on white without being harsh. The new slate-400 / slate-500 gradient (grid → line) also gives Plotly's "axis vs grid" distinction that the old monochrome grey collapsed.

Impact summary:

- 2D box / bar / line / scatter / area / histogram: axes/grid/tick/zero-line now clearly visible on white canvas.
- 3D scatter (AI minimal-defaults path): scene axes/grid/tick/zero-line/zeroline clearly visible.
- 3D surface (synthesised by `toggle3DView`): same — was totally default before, now matches the AI path.
- 3D charts after theme toggle: scene axes now re-themed by relayout (previously stuck).
- Dark mode UI: unchanged for plotly charts — the chart canvas is still forced white, dark text/grid/lines always render correctly regardless of UI theme.

Full historical record: see `VISUALIZATION_PLOTLY_AXIS_GRID_VISIBILITY_FIX_JULY22_2026.md` at the repo root.

---

## Architecture Pattern

### Two-Rule Streaming System (streamingTwoRule.js)

**Core Principle:** BLACK AND WHITE content classification

#### Rule 1: Content Cannot Belong to Both Groups
Any buffered content is EITHER:
- **Type 1 (Markdown):** Regular text, headings, lists, tables, formatted text
- **Type 2 (Visual):** Mermaid diagrams, Plotly charts, code blocks with visualization delimiters

#### Rule 2: Once Delimiter Detected, ALL Content is Visual Until END Delimiter
When `<visualization>` or similar delimiter is found, everything until `</visualization>` is treated as visual content.

### Flow Diagram
```
Stream Input
    ↓
Raw Buffer (append-only)
    ↓
Content Parser (state machine)
    ↓
Package Creation (markdown or visual)
    ↓
Controlled Release (ordered rendering)
    ↓
UI Append (never re-render existing content)
```

### State Machine
```javascript
States:
- NORMAL: Parsing regular markdown content
- BUFFERING_VISUAL: Accumulating visual content between delimiters

Transitions:
NORMAL → BUFFERING_VISUAL: When delimiter detected
BUFFERING_VISUAL → NORMAL: When end delimiter found
```

---

## File Responsibilities

### streamingTwoRule.js

#### Primary Classes

**1. TwoRuleStreamProcessor**
```javascript
class TwoRuleStreamProcessor {
    constructor(container)  // Initialize with target DOM container
    
    // Core Methods
    async processChunk(newContent)       // Process incoming stream chunks
    forceFlush()                         // Force release buffered content
    async releaseReadyPackages()         // Release completed packages
    async renderPackage(pkg)             // Render individual package
    async renderVisualization(type, content, container)  // Route to viz engine
    
    // Package Management
    packageMarkdownContent(content, startPosition)
    packageVisualContent(content, type)
    
    // State Management
    parseNormalState()
    parseBufferingState()
}
```

**Key Features:**
- **Delimiter Detection:** Recognizes `<visualization>`, `<mermaid>`, `<plotly>`, etc.
- **Position Tracking:** Maintains stream position for ordered rendering
- **Deduplication:** Uses content hashing to prevent duplicate renders
- **Code Fence Safety:** Won't flush incomplete code blocks
- **Markdown Container Management:** Creates/reuses containers for text content
- **Append-Only Rendering:** Never re-renders existing content

#### Global State
```javascript
let globalTwoRuleProcessor = null;        // Singleton instance
let streamingMessageElement = null;        // Current message container
let streamingState = {
    isFirstContent: true,
    lastProcessedLength: 0,
    renderedComponents: [],
    lastActivityTs: 0
};
```

#### Helper Functions
```javascript
removeAllThinkingIndicators(container)    // Clean up loading indicators
cleanMarkdownHTML(html)                   // Legacy HTML cleaning
```

---

### visualisation_v3.js

#### Primary Classes

**1. MermaidFontController**
```javascript
class MermaidFontController {
    constructor()
    
    // Font Size Management
    setFontSize(container, sizeName)      // Apply font size preset
    increaseFontSize(container)           // Increase by one step
    decreaseFontSize(container)           // Decrease by one step
    getCurrentSize(container)             // Get current size name
    
    // User Preferences
    saveUserPreference(sizeName)
    loadUserPreference()
    applyUserPreference(container)
}
```

**Available Font Sizes:**
- tiny (10px, scale 0.8)
- small (12px, scale 0.9)
- normal (14px, scale 1.0) - default
- medium (16px, scale 1.1)
- large (18px, scale 1.2)
- huge (22px, scale 1.4)
- giant (26px, scale 1.6)

**2. VisualizationEngine**
```javascript
class VisualizationEngine {
    constructor()
    async init()                          // Initialize libraries (Mermaid, Plotly)
    
    // Rendering Methods
    async renderVisualizationDirectly(item, container, chartId)
    async renderVisualization(item, container, chartId)
    async renderMermaidDirectly(item, container, chartId)
    async renderPlotlyDirectly(item, container, chartId)
    
    // Container Management
    createVisualizationContainer(type)    // Create styled wrapper
    
    // Export Functions
    async exportToSVG(containerId)
    async exportToPNG(containerId)
    async exportToHTML(containerId)
    async exportToMarkdown(containerId)
    
    // Theme Management
    getMermaidTheme()
    applyTheme(theme)
}
```

**Key Features:**
- **Mermaid Rendering:** Flowcharts, sequence diagrams, Gantt charts, etc.
- **Plotly Rendering:** Interactive charts with zoom, pan, hover
- **Export Support:** SVG, PNG, HTML, Markdown formats
- **Theme Support:** Light/dark mode integration
- **Font Control:** Per-diagram font size adjustment
- **Responsive Design:** Auto-resize on window changes
- **HTML Formatting:** Support for bold, italic, code in Mermaid labels

#### Export Utilities
```javascript
window.MermaidExportCSS()                 // Get export-specific CSS
embedStyleIntoSvg(svgEl, cssText)        // Embed CSS in SVG for export
stripBreaksAroundBullets(root)           // Clean up bullet formatting
hardenSvgForExport(svgEl, options)       // Normalize SVG for export
```

---

## Integration Flow

### Step-by-Step Process

#### 1. Initialization
```javascript
// Create processor instance
const processor = new TwoRuleStreamProcessor(containerElement);

// Initialize visualization engine (if not already global)
if (!window.vizEngine) {
    window.vizEngine = new VisualizationEngine();
    await window.vizEngine.init();
}
```

#### 2. Stream Processing
```javascript
// As AI content arrives in chunks
processor.processChunk(newContentChunk);

// On stream complete
processor.forceFlush();
```

#### 3. Content Classification
**streamingTwoRule.js automatically:**
- Detects delimiters (`<mermaid>`, `<plotly>`, etc.)
- Classifies content as markdown or visual
- Creates packages with metadata (position, type, content)
- Queues packages for ordered release

#### 4. Package Release
**streamingTwoRule.js:**
- Releases packages in stream order
- Creates visualization containers with proper structure
- Routes visual packages to visualization engine

#### 5. Visualization Rendering
**visualisation_v3.js:**
- Receives visualization request with type, content, container
- Applies font preferences
- Renders using appropriate library (Mermaid/Plotly)
- Adds interactive controls (export, font size, etc.)
- Returns rendered visualization in container

---

## Tiptap Integration Guide

### Overview
To render AI-generated content (markdown + visualizations) inside a Tiptap editor, you need to:
1. Extract content from Tiptap editor
2. Process through streamingTwoRule.js
3. Render visualizations via visualisation_v3.js
4. Insert results back into Tiptap

### Integration Pattern

#### Option 1: Real-Time Streaming (AI Response)

```javascript
// 1. Create processor for Tiptap content area
const tiptapContainer = document.querySelector('.tiptap-content-area');
const processor = new TwoRuleStreamProcessor(tiptapContainer);

// 2. Initialize viz engine
if (!window.vizEngine) {
    window.vizEngine = new VisualizationEngine();
    await window.vizEngine.init();
}

// 3. Process AI stream as it arrives
aiStream.on('data', (chunk) => {
    processor.processChunk(chunk);
});

aiStream.on('end', () => {
    processor.forceFlush();
});
```

#### Option 2: Static Content Rendering (Existing Document)

```javascript
// 1. Extract content from Tiptap
const tiptapContent = editor.getHTML(); // or editor.getText()

// 2. Create temporary container
const tempContainer = document.createElement('div');
const processor = new TwoRuleStreamProcessor(tempContainer);

// 3. Process entire content at once
await processor.processChunk(tiptapContent);
await processor.forceFlush();

// 4. Wait for all rendering to complete
await new Promise(resolve => setTimeout(resolve, 500));

// 5. Extract rendered visualizations
const visualizations = tempContainer.querySelectorAll('.viz-container');

// 6. Insert into Tiptap at appropriate positions
visualizations.forEach(viz => {
    const position = parseInt(viz.getAttribute('data-stream-position'));
    editor.commands.insertContentAt(position, viz.outerHTML);
});
```

#### Option 3: Custom Node Extension (Recommended)

Create a custom Tiptap node for visualizations:

```javascript
import { Node } from '@tiptap/core';
import { VueNodeViewRenderer } from '@tiptap/vue-3';
import VisualizationNodeView from './VisualizationNodeView.vue';

export const VisualizationNode = Node.create({
    name: 'visualization',
    
    group: 'block',
    
    atom: true, // Don't allow editing
    
    addAttributes() {
        return {
            type: { default: 'mermaid' },
            content: { default: '' },
            chartId: { default: null }
        };
    },
    
    parseHTML() {
        return [{ tag: 'div.viz-container' }];
    },
    
    renderHTML({ node, HTMLAttributes }) {
        return ['div', { class: 'viz-container', ...HTMLAttributes }];
    },
    
    addNodeView() {
        return VueNodeViewRenderer(VisualizationNodeView);
    }
});
```

**VisualizationNodeView.vue:**
```vue
<template>
    <div ref="vizContainer" class="viz-node-wrapper">
        <!-- Visualization renders here -->
    </div>
</template>

<script>
export default {
    props: ['node'],
    
    async mounted() {
        // Initialize viz engine if needed
        if (!window.vizEngine) {
            window.vizEngine = new VisualizationEngine();
            await window.vizEngine.init();
        }
        
        // Render visualization
        const item = {
            type: this.node.attrs.type,
            content: this.node.attrs.content
        };
        
        await window.vizEngine.renderVisualizationDirectly(
            item,
            this.$refs.vizContainer,
            this.node.attrs.chartId || `viz-${Date.now()}`
        );
    }
};
</script>
```

**Using the extension:**
```javascript
import { Editor } from '@tiptap/core';
import { VisualizationNode } from './VisualizationNode';

const editor = new Editor({
    extensions: [
        // ... other extensions
        VisualizationNode
    ],
    content: `
        <p>Here's a diagram:</p>
        <div class="viz-container" 
             data-type="mermaid" 
             data-content="graph LR\nA-->B">
        </div>
    `
});
```

### Content Extraction Patterns

#### From AI Stream to Tiptap

```javascript
class TiptapStreamIntegration {
    constructor(editor) {
        this.editor = editor;
        this.processor = null;
        this.currentPosition = 0;
    }
    
    async startStream() {
        // Create processor with temp container
        const tempContainer = document.createElement('div');
        this.processor = new TwoRuleStreamProcessor(tempContainer);
        
        // Store reference to editor position
        this.currentPosition = this.editor.state.doc.content.size;
    }
    
    async processChunk(chunk) {
        await this.processor.processChunk(chunk);
        
        // Extract newly rendered content
        const renderedContent = this.extractNewContent();
        
        // Insert into Tiptap at current position
        if (renderedContent) {
            this.editor.commands.insertContentAt(
                this.currentPosition,
                renderedContent
            );
            this.currentPosition += renderedContent.length;
        }
    }
    
    async endStream() {
        await this.processor.forceFlush();
        
        // Final content extraction
        const finalContent = this.extractNewContent();
        if (finalContent) {
            this.editor.commands.insertContentAt(
                this.currentPosition,
                finalContent
            );
        }
    }
    
    extractNewContent() {
        // Extract HTML from processor container
        const container = this.processor.container;
        
        // Get markdown content
        const markdownElements = container.querySelectorAll('.two-rule-markdown-content');
        
        // Get visualization containers
        const vizElements = container.querySelectorAll('.viz-container');
        
        // Build ordered content array
        const allElements = [...markdownElements, ...vizElements]
            .sort((a, b) => {
                const posA = parseInt(a.getAttribute('data-stream-position') || '0');
                const posB = parseInt(b.getAttribute('data-stream-position') || '0');
                return posA - posB;
            });
        
        // Convert to Tiptap JSON or HTML
        return allElements.map(el => el.outerHTML).join('');
    }
}

// Usage
const integration = new TiptapStreamIntegration(editor);
await integration.startStream();

aiStream.on('data', chunk => integration.processChunk(chunk));
aiStream.on('end', () => integration.endStream());
```

---

## API Reference

### streamingTwoRule.js API

#### TwoRuleStreamProcessor

**Constructor:**
```javascript
new TwoRuleStreamProcessor(container: HTMLElement)
```

**Methods:**

```javascript
// Process incoming stream chunk
async processChunk(newContent: string): Promise<void>

// Force flush buffered content
forceFlush(): void

// Release packages that are ready to render
async releaseReadyPackages(): Promise<void>

// Render a specific package
async renderPackage(pkg: Package): Promise<void>

// Route visualization to engine
async renderVisualization(
    type: string,           // 'mermaid', 'plotly', etc.
    content: string,        // Visualization code/data
    container: HTMLElement  // Target container
): Promise<void>

// Get processing statistics
getStats(): {
    chunksProcessed: number,
    totalProcessingTime: number,
    markdownPackages: number,
    visualPackages: number,
    packagesReleased: number
}
```

**Package Structure:**
```javascript
{
    id: number,               // Unique package ID
    type: 'markdown' | 'visual',
    subType?: string,         // For visual: 'mermaid', 'plotly'
    content: string,          // Actual content
    contentHash: string,      // Deduplication hash
    position: number,         // Stream position
    ready: boolean,           // Ready to render?
    timestamp: number         // Creation time
}
```

---

### visualisation_v3.js API

#### VisualizationEngine

**Constructor:**
```javascript
new VisualizationEngine()
```

**Initialization:**
```javascript
async init(): Promise<void>  // Initialize Mermaid, Plotly, etc.
```

**Rendering Methods:**
```javascript
// Main rendering method
async renderVisualizationDirectly(
    item: {
        type: string,      // 'mermaid', 'plotly', etc.
        content: string    // Visualization code
    },
    container: HTMLElement,
    chartId: string
): Promise<void>

// Mermaid-specific
async renderMermaidDirectly(
    item: { type: string, content: string },
    container: HTMLElement,
    chartId: string
): Promise<void>

// Plotly-specific
async renderPlotlyDirectly(
    item: { type: string, content: string },
    container: HTMLElement,
    chartId: string
): Promise<void>
```

**Container Creation:**
```javascript
createVisualizationContainer(type: string): HTMLElement
// Returns a styled container with:
// - .viz-container wrapper
// - .viz-header with title/controls
// - .viz-content-area for actual rendering
// - .viz-footer with metadata
```

**Export Methods:**
```javascript
async exportToSVG(containerId: string): Promise<void>
async exportToPNG(containerId: string): Promise<void>
async exportToHTML(containerId: string): Promise<void>
async exportToMarkdown(containerId: string): Promise<void>
```

**Theme Management:**
```javascript
getMermaidTheme(): string  // 'default' or 'dark'
applyTheme(theme: 'light' | 'dark'): void
```

#### MermaidFontController

```javascript
const fontController = new MermaidFontController();

// Set specific size
fontController.setFontSize(container, 'large');

// Adjust incrementally
fontController.increaseFontSize(container);
fontController.decreaseFontSize(container);

// Get current
const currentSize = fontController.getCurrentSize(container);

// Preferences
fontController.saveUserPreference('large');
const preferred = fontController.loadUserPreference();
fontController.applyUserPreference(container);
```

---

## Usage Examples

### Example 1: Simple Streaming Setup

```javascript
// Initialize
const container = document.getElementById('chat-messages');
const processor = new TwoRuleStreamProcessor(container);

// Ensure viz engine exists
if (!window.vizEngine) {
    window.vizEngine = new VisualizationEngine();
    await window.vizEngine.init();
}

// Process stream
async function handleAIStream(streamSource) {
    for await (const chunk of streamSource) {
        await processor.processChunk(chunk);
    }
    processor.forceFlush();
}
```

### Example 2: Mixed Content Rendering

```javascript
const mixedContent = `
# Project Overview

Here's our system architecture:

<mermaid>
graph TD
    A[Client] --> B[Server]
    B --> C[Database]
    B --> D[Cache]
</mermaid>

## Performance Metrics

<plotly>
{
    "data": [{
        "x": ["Jan", "Feb", "Mar"],
        "y": [10, 15, 13],
        "type": "bar"
    }],
    "layout": {"title": "Monthly Sales"}
}
</plotly>

That's the complete picture.
`;

// Process all at once
const processor = new TwoRuleStreamProcessor(container);
await processor.processChunk(mixedContent);
processor.forceFlush();
```

### Example 3: Tiptap Document with Visualizations

```javascript
// Create Tiptap editor with visualization support
const editor = new Editor({
    element: document.querySelector('#editor'),
    extensions: [
        StarterKit,
        VisualizationNode.configure({
            renderFunction: async (node, container) => {
                if (!window.vizEngine) {
                    window.vizEngine = new VisualizationEngine();
                    await window.vizEngine.init();
                }
                
                await window.vizEngine.renderVisualizationDirectly(
                    { type: node.attrs.type, content: node.attrs.content },
                    container,
                    node.attrs.chartId
                );
            }
        })
    ],
    content: `
        <p>System architecture:</p>
        <visualization type="mermaid" content="graph LR\nA-->B"></visualization>
    `
});

// Insert new visualization
editor.chain()
    .focus()
    .insertContent({
        type: 'visualization',
        attrs: {
            type: 'mermaid',
            content: 'graph TD\nA-->B',
            chartId: `viz-${Date.now()}`
        }
    })
    .run();
```

### Example 4: Export Visualization from Tiptap

```javascript
// Find visualization node in Tiptap
const vizNodes = editor.state.doc.descendants((node, pos) => {
    if (node.type.name === 'visualization') {
        return { node, pos };
    }
});

// Export first visualization as SVG
if (vizNodes.length > 0) {
    const { node } = vizNodes[0];
    const chartId = node.attrs.chartId;
    
    await window.vizEngine.exportToSVG(chartId);
}
```

### Example 5: Font Size Control

```javascript
// Initialize font controller
const fontController = new MermaidFontController();

// Apply to all visualizations
document.querySelectorAll('.viz-container').forEach(container => {
    fontController.applyUserPreference(container);
});

// Add UI controls
document.getElementById('increase-font').addEventListener('click', () => {
    const activeViz = document.querySelector('.viz-container.active');
    if (activeViz) {
        fontController.increaseFontSize(activeViz);
    }
});

document.getElementById('decrease-font').addEventListener('click', () => {
    const activeViz = document.querySelector('.viz-container.active');
    if (activeViz) {
        fontController.decreaseFontSize(activeViz);
    }
});
```

---

## Key Concepts Summary

### Content Types
- **Type 1 (Markdown):** Text that flows and concatenates
- **Type 2 (Visual):** Discrete visualization blocks

### Delimiters
Recognized patterns:
- `<mermaid>...</mermaid>`
- `<plotly>...</plotly>`
- `<visualization type="...">...</visualization>`
- `\`\`\`mermaid ... \`\`\``
- `\`\`\`plotly ... \`\`\``

### Rendering Order
1. Parse → 2. Package → 3. Queue → 4. Release → 5. Render

### Container Structure
```html
<div class="viz-container" data-package-id="123" data-stream-position="456">
    <div class="viz-header">
        <span class="viz-title">Mermaid Diagram</span>
        <div class="viz-controls">
            <!-- Export, font controls -->
        </div>
    </div>
    <div class="viz-content-area">
        <!-- Actual Mermaid/Plotly render -->
    </div>
    <div class="viz-footer">
        <span class="viz-metadata">Created: ...</span>
    </div>
</div>
```

### Deduplication
Uses SHA-256 hash of content to prevent duplicate renders during streaming.

### Error Handling
- Container validation before rendering
- Retry logic for Plotly (up to 3 attempts)
- Graceful fallback to error display
- Loading indicators during processing

---

## Best Practices

### 1. Always Initialize Engine
```javascript
if (!window.vizEngine) {
    window.vizEngine = new VisualizationEngine();
    await window.vizEngine.init();
}
```

### 2. Wait for DOM Attachment
```javascript
await new Promise(resolve => requestAnimationFrame(resolve));
if (!document.contains(container)) {
    throw new Error('Container not in DOM');
}
```

### 3. Use Ordered Positioning
Always respect `data-stream-position` attributes for insertion order.

### 4. Don't Re-Render Existing Content
Check for existing containers before rendering:
```javascript
const existing = container.querySelector(`[data-package-id="${pkg.id}"]`);
if (existing) {
    console.log('Already rendered, skipping');
    return;
}
```

### 5. Handle Async Properly
Always await rendering:
```javascript
await processor.processChunk(chunk);
await processor.forceFlush();
```

### 6. Clean Up Resources
```javascript
// Remove observers when destroying
plotlyResizeObservers.delete(element);
```

---

## Troubleshooting

### Visualization Not Rendering

**Check:**
1. Is `window.vizEngine` initialized?
2. Is container attached to DOM?
3. Are libraries loaded (Mermaid, Plotly)?
4. Check console for errors

```javascript
console.log('VizEngine exists:', !!window.vizEngine);
console.log('Container in DOM:', document.contains(container));
console.log('Mermaid loaded:', !!window.mermaid);
console.log('Plotly loaded:', !!window.Plotly);
```

### Duplicate Visualizations

**Solution:** Enable deduplication
```javascript
// Content hashing is enabled by default
// Check package contentHash matches
```

### Incorrect Rendering Order

**Solution:** Verify position attributes
```javascript
const elements = container.querySelectorAll('[data-stream-position]');
elements.forEach(el => {
    console.log('Position:', el.getAttribute('data-stream-position'));
});
```

### Tiptap Integration Issues

**Check:**
1. Custom node extension properly registered?
2. Node view component mounted?
3. Content format matches node schema?

```javascript
// Verify extension loaded
console.log('Extensions:', editor.extensionManager.extensions.map(e => e.name));

// Check node exists in schema
console.log('Has visualization node:', !!editor.schema.nodes.visualization);
```

---

## Performance Considerations

### Streaming Performance
- Chunks processed in <10ms typically
- DOM operations batched in `requestAnimationFrame`
- Duplicate detection via content hashing

### Memory Management
- WeakMaps for resize observers (auto garbage collection)
- Package cleanup after rendering
- Temp container cleanup after Tiptap insertion

### Rendering Optimization
- Mermaid renders asynchronously
- Plotly uses responsive config (no manual resize)
- CSS isolation prevents style conflicts

---

## Related Documentation

- `streamingTwoRule.js` - Two-Rule streaming processor source
- `visualisation_v3.js` - Visualization engine source (an older snapshot remains at `visualisation_copy.js` for reference; do not edit it)
- Tiptap Documentation: https://tiptap.dev/
- Mermaid Documentation: https://mermaid.js.org/
- Plotly Documentation: https://plotly.com/javascript/

---

**Last Updated:** November 15, 2025  
**Version:** 1.0  
**Maintainers:** AI Agents Platform Team
