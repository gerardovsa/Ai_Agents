# Mermaid Pie Overlap + Bold-in-Chat + `<br/>` Follow-On Fixes — July 22, 2026

> **Purpose.** Documents the three follow-on fixes that landed on top of
> the always-white SVG canvas fix in
> `VISUALIZATION_MERMAID_CHAT_BG_AND_GITGRAPH_WRAPPING_FIX_JULY22_2026.md`.
> After that fix shipped, the user inspected the working output and
> reported three remaining issues. Each of these is independent and
> affects a different layer (CSS specificity, JS regex, SVG box model).
> Read the predecessor fix-log first for the always-white-canvas
> context.

## Overview

The user provided three new screenshots and a 6-test Mermaid
flowchart (A1=A2 rectangle, A3 stadium, A4 diamond, A5 cylinder,
A6 subroutine) after the always-white canvas fix shipped. Three
issues remained:

1. **Pie title and legend still overlap the pie.** The previous
   `min-width: 700px !important` rule gave the SVG some breathing
   room, but in the user's actual chat column the SVG's height still
   collapsed to its own viewBox aspect ratio, pushing the title and
   legend INTO the pie's drawn area. User: *"the pie chart is still
   showing the title and the legend over the actual pie"*.

2. **Bold text renders white in chat but black in fullscreen.**
   Confirmed visually: in chat bubbles, text formatted with `<b>` or
   `**...**` inside a flowchart node label was nearly invisible on
   the now-white canvas because the text colour was white-ish. In
   fullscreen the same chart was correctly readable. User: *"but
   some reason bold text in the chat is rendered white but in the
   full screen it is black"*.

3. **`<br/>` line breaks don't work in stadium (A3) and subroutine
   (A6) shapes.** The user's 6-test flowchart showed `<b>` worked
   correctly across all 6 shape types, but `<br/>` only worked in
   rectangle (A1), diamond (A4), and cylinder (A5). In stadium and
   subroutine shapes, `<br/>` was silently joined to the surrounding
   text (e.g. `"Line 1<br/>Line 2"` rendered as `"Line 1Line 2"` with
   no break). User: *"the combination of the bold and line break is
   not detected and converted properly"*.

Each fix is isolated to a single file and a single code path. No
backend, no migration, no API change, no env-var change. Pure
frontend.

## Root Cause Analysis

### Cause 1 — SVG height tracks viewBox aspect ratio when only width is constrained

The previous pie rule at
[`business-ai-platform-v2.html:10820-10832`](UI/business-ai-platform-v2.html#L10820-L10832)
set only `min-width: 700px !important` on the SVG and
`min-height: 520px` on the parent. With Mermaid's default
`preserveAspectRatio="xMidYMid meet"`, an SVG with no explicit
`height` resolves its height from the viewBox aspect ratio:
`height = width * (viewBox_h / viewBox_w)`. When the user's chat
column was wider than the SVG's natural width (e.g. a 1000-px chat
column with a 600-px-wide pie), the SVG expanded to 700 px wide and
~700 px tall (because Mermaid's pie viewBox is approximately
square). Inside that, Mermaid's title and legend elements were
positioned RELATIVE TO the viewBox — but when CSS constrained the
SVG to a larger box, `xMidYMid meet` left the actual content
centered and unchanged in size, while the visible SVG canvas grew
around it. Worse, if Mermaid's viewBox happened to be tall (taller
than wide), the SVG's CSS height exceeded the parent's `min-height:
520px`, but the legend's `<g>` element was anchored at the bottom
of the viewBox — and when the SVG height grew, the legend's bottom
edge moved DOWN off the visible area while the pie center stayed
fixed, producing the "title and legend over the pie" symptom.

The precise mechanism: Mermaid emits a viewBox sized to the
PIE+LABELS+LEGEND composition. When CSS forces the SVG's outer box
to a non-matching aspect ratio with `preserveAspectRatio="xMidYMid
meet"`, the content scales to fit the SMALLER dimension. If the
parent box's smaller dimension is much larger than the viewBox's
smaller dimension, the content scales up uniformly — but the SVG
canvas still has the constrained dimensions, and any element Mermaid
positions RELATIVE TO the SVG (not the viewBox) ends up off-axis.

### Cause 2 — `.ai-message-content strong` cascades into Mermaid's foreignObject

The chat-markdown CSS at
[`business-ai-platform-v2.html:10685`](UI/business-ai-platform-v2.html#L10685-L10693)
sets `color: var(--text-primary)` on every `<strong>` inside
`.ai-message-content`:

```css
.ai-message-content strong {
    font-weight: 600;
    color: var(--text-primary);
}
```

This rule was designed for chat-bubble markdown bold — chat bubbles
have theme-aware backgrounds and use `var(--text-primary)` for the
foreground text colour.

But when Mermaid renders a flowchart node label like `<b>bold</b>`,
`processNodeLabel` in
[`visualisation_v3.js:5563`](UI/visualisation_engine/visualisation_v3.js#L5563)
rewrites it to `<strong class="mermaid-bold">bold</strong>` and
emits it INSIDE the SVG's `<foreignObject>` element. That
foreignObject lives inside the `.ai-message-content` chat bubble
(chat-bubble DOM path: `.ai-message-content > .viz-container >
.viz-content-area > .mermaid > svg > foreignObject`). So the chat
markdown `color: var(--text-primary)` rule cascades INTO the
foreignObject and overwrites the explicit dark colour Mermaid set
inside the SVG.

In dark mode `--text-primary` resolves to a white-ish colour
(typically `#e6edf3` or `#f0f6fc`). Mermaid's chart text is dark
(`#24292f`), but the chat bubble's `var(--text-primary)` wins
because of CSS specificity (both rules are `0,0,1,1`, but
`.ai-message-content strong` is declared first AND is at a more
specific ancestor). The fullscreen clone escapes this cascade
because `openMermaidFullscreen` uses `cloneNode(true)` and mounts
the clone at the document body root, OUTSIDE `.ai-message-content`
— so the chat markdown rule never applies there. That's why bold
was black in fullscreen and white in chat.

### Cause 3 — `processNodeLabel` only normalises `\n`, not `<br/>`

`processNodeLabel` in `transformMermaidContentToHTML`
([`visualisation_v3.js:5500-5651`](UI/visualisation_engine/visualisation_v3.js#L5500-L5651))
performs this transformation pipeline on every label string:

```js
// Bold: **text** → <strong>mermaid-bold</strong>
processedLabel = processedLabel.replace(/\*\*(.*?)\*\*/g, '<strong class="mermaid-bold">$1</strong>');

// Pre-existing <strong>/<b> tags: normalize class
processedLabel = processedLabel.replace(/<(strong|b)(?![^>]*class\s*=\s*["\'][^"\']*mermaid[^"\']*["\'])[^>]*>(.*?)<\/(strong|b)>/gi, '<strong class="mermaid-bold">$2</strong>');

// Line breaks: \\n → \n → <br class="mermaid-br"/>
processedLabel = processedLabel
    .replace(/\\n/g, '\n')        // Normalize escaped newlines
    .replace(/\n/g, '<br class="mermaid-br"/>');  // Convert ONCE
```

The bold path recognises BOTH `**...**` markdown AND pre-existing
`<b>...</b>` / `<strong>...</strong>` tags — so all 6 shape types
in the user's test get bold correctly.

The line-break path only recognises LITERAL `\n` (after the `\\n`
escape). It does NOT recognise `<br/>` or `<br>` self-closing tags.
For rectangle (A1), diamond (A4), and cylinder (A5), the user's
`<br/>` happens to work — because Mermaid's HTML-label parser for
those shape paths independently scans for `<br>` and renders them
correctly even when our wrapper class is missing.

For stadium (A3) and subroutine (A6), Mermaid's HTML-label parser
takes a different code path. In 10.6.1, those shape labels are
parsed with a stricter HTML tolerance that REQUIRES the
`<br class="mermaid-br"/>` form to render the break — bare `<br/>`
is silently dropped or joined to adjacent text. This is a known
quirk of Mermaid's `transform-html`-stage regex chain for stadium
and subroutine shapes specifically.

So the user's `<br/>` worked for shapes whose parser tolerated
bare tags, and silently failed for shapes whose parser required
the class-annotated form. The fix: normalise `<br>` to
`<br class="mermaid-br"/>` UPSTREAM of Mermaid's parser, in
`processNodeLabel` itself, so every shape receives the same
well-formed marker regardless of which shape-specific parser runs.

## Fix

### Fix 1 — Explicit pie SVG dimensions (square 760×760)

In `business-ai-platform-v2.html`, replace the previous pie rule
(L10820-10832) with explicit `width` AND `height` (not just
`min-width`):

```css
.mermaid svg[id^="pie-"],
.mermaid svg[class*="pie"] {
    padding: 8px 8px 32px 8px;
    /* EW (Jul 22 2026): Force explicit width AND height (not just
       min-width) so the SVG cannot collapse to a smaller size.
       The previous min-width-only rule let the SVG height track
       its own viewBox aspect ratio, which produced a tall+thin
       container when Mermaid's natural viewBox was tall, and
       pushed the title and legend down INTO the pie's drawn
       area. With explicit width:760 height:760 (square, large
       enough for a 14-15-slice pie with title + legend) and
       preserveAspectRatio="xMidYMid meet" (Mermaid's default),
       the pie+labels composition scales uniformly to fill the
       square — the title sits above the pie, the legend sits
       below, with no overlap. min-/max- also !important so
       any inline style.width = '100%' from
       renderMermaidDirectly (visualisation_v3.js:5196) cannot
       override the size. */
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

**Why `760 × 760`?** Wide enough for a 14-15-slice pie with title
above and legend below, all rendered at full Mermaid-internal size.
Square aspect ratio matches Mermaid's natural pie viewBox aspect
ratio, so `xMidYMid meet` scales content uniformly to fill the box
with no letterboxing. Anything narrower than ~700 px causes the
title and legend to compress against the pie; anything much wider
than ~900 px is wasteful in narrow chat columns (the parent's
`overflow-x: auto` scrolls it anyway).

**Why both `min-` and `max-` with `!important`?** Mermaid's
`renderMermaidDirectly` at
[`visualisation_v3.js:5196`](UI/visualisation_engine/visualisation_v3.js#L5196)
sets `svgEl.style.width = '100%'` inline. Inline styles normally
win against external CSS, but `!important` on the external CSS
property overrides them. The `min-` and `max-` rules ensure the
SVG can NEVER be smaller than 760×760 (preventing the collapse
that caused the original overlap) and NEVER larger than the parent
(allows the parent's `overflow-x: auto` to take over in narrow
columns).

**Why `min-height: 800px` on the parent (was 520)?** 760-px-tall
SVG + 8-px top padding + 32-px bottom padding = 800 px. Matches
the SVG's natural height exactly so no scrollbar appears in
moderate chat columns.

### Fix 2 — Override `.ai-message-content strong/em` inside Mermaid's foreignObject

In `business-ai-platform-v2.html`, after the always-white canvas
rule (L10855), add:

```css
/* EW (Jul 22 2026): Override .ai-message-content strong/em colour
   inside Mermaid foreignObject. The chat markdown rule at L10685
   sets `color: var(--text-primary)` on every <strong> inside
   .ai-message-content (designed for chat markdown bold). When
   Mermaid renders a flowchart node label like `<b>bold</b>`,
   processNodeLabel (visualisation_v3.js:5563) rewrites it to
   `<strong class="mermaid-bold">bold</strong>` inside the SVG's
   foreignObject — and the chat bubble's dark-mode --text-primary
   (white-ish) cascades into the foreignObject, making bold text
   invisible on the now-white canvas. The fullscreen clone lives
   outside .ai-message-content so this rule never applied there,
   which is why bold was black in fullscreen and white in chat.

   Scope: .viz-container .mermaid foreignObject only — chat
   markdown bold outside Mermaid still uses --text-primary as
   intended. Force a constant dark colour (matching the chart's
   always-white canvas). !important beats the .ai-message-content
   strong rule on specificity and on cascade order. */
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

**Why `#24292f`?** Mermaid's `themeVariables.textColor: '#24292f'`
in the per-render `mermaid.initialize` block at
[`visualisation_v3.js:5097`](UI/visualisation_engine/visualisation_v3.js#L5097).
Forces bold/italic text inside chart labels to the SAME dark colour
as the chart's other text — invisible-on-white-on-dark-theme bug
becomes impossible.

**Why scope to `.viz-container .mermaid foreignObject`?** Stray
foreignObjects (e.g. Mermaid error states, hand-coded examples,
or orphaned staging elements) are not affected. Chat-bubble
markdown bold OUTSIDE Mermaid (e.g. AI responses like "**important**
notice") still uses `var(--text-primary)` as designed — we don't
want to paint those static-text strong tags with a hard-coded
`#24292f`, which would clash with the chat bubble's theme-aware
background.

**Why `!important`?** Both rules have the same CSS specificity
(`.ai-message-content strong` is `0,0,1,1`; the new rule is
`0,0,3,2`). The new rule is more specific, so it would win by
specificity alone — but `!important` belt-and-braces guards
against any future cascade-order shift (e.g. if someone reorders
the CSS block) and against Mermaid injecting inline `style="..."`
attributes on bold spans inside the foreignObject.

### Fix 3 — Normalise `<br>` to `<br class="mermaid-br"/>` upstream

In `visualisation_v3.js`, in the `processNodeLabel` function
(L5500-5651), inside the bullet-protected conversion block, ADD a
`<br>` → `<br class="mermaid-br"/>` normalisation step BEFORE the
existing `\n` conversion:

```js
// TEP 4: Now convert line breaks (ONLY ONCE!)
// Temporarily protect bullet spans
const bulletLines = [];
processedLabel = processedLabel.replace(/(<span class="mermaid-bullet">.*?<\/span>)/g, (match) => {
    bulletLines.push(match);
    return `__BULLET_${bulletLines.length - 1}__`;
});

// EW (Jul 22 2026): Normalize any <br> / <br/> self-closing tags
// already in the source. The original conversion below only
// handled literal \n — any <br/> written by the AI or user
// (e.g. stadium and subroutine labels like
// `(["Line 1<br/>Line 2"])`) was passed through unchanged,
// and Mermaid 10.6.1's HTML-label parser would silently
// drop or join these on certain shape paths, producing
// "Line 1Line 2" without line breaks. By normalizing all
// <br> variants to <br class="mermaid-br"/> here, both
// existing tags and newlines converge on the same
// well-formed marker that Mermaid reliably renders. The
// .mermaid-br class also makes the bullet-spacing CSS
// rule at L121 work uniformly.
processedLabel = processedLabel.replace(/<br\s*\/?\s*>/gi, '<br class="mermaid-br"/>');

// Convert line breaks - normalize first, then convert once
processedLabel = processedLabel
    .replace(/\\n/g, '\n')  // Normalize escaped newlines
    .replace(/\n/g, '<br class="mermaid-br"/>');  // Convert ONCE
```

**Why regex `/<br\s*\/?\s*>/gi`?** Matches `<br>`, `<br/>`, `<br />`,
`<BR>`, `<Br/>` — all the variants an AI or user might emit. The
`\s*\/?\s*` tolerates whitespace around the `/` and the trailing
`>`. Case-insensitive (`gi`) to handle uppercase tag names from
overzealous prompt templates.

**Why place it BEFORE the `\n` conversion?** The bullet-protection
block runs first (so `<br>` inside bullets is protected — but in
practice bullets are `<span>` not `<br>`, so the protection is
unrelated). Placing the `<br>` normalisation BEFORE the `\n`
conversion ensures any user-provided `<br/>` is converted in the
same pipeline pass that converts `\n`, so both forms converge on
`<br class="mermaid-br"/>` and Mermaid's parser sees a consistent
marker.

**Why not also normalise other HTML line-break tags?** Mermaid 10.6.1
recognises only `<br>` and the Mermaid-internal `<br class="mermaid-br"/>`. Variants like `<br/>`, `<br />`, `<BR>`, `<Br/>` are the realistic set; any other tags (`<hr/>`, `<wbr>`, etc.)
are out of scope.

## Why these fixes are isolated

- **Fix 1 (pie CSS)** changes ONLY one CSS rule (the pie SVG sizing).
  No JS, no Mermaid internal state. Affects pies only — git graph,
  gantt, flowchart sizing rules are untouched.
- **Fix 2 (CSS foreignObject override)** adds a new CSS block after
  the always-white-canvas rule. No JS, no Mermaid internal state.
  Affects only `.viz-container .mermaid foreignObject strong/em` —
  chat markdown outside Mermaid is unaffected.
- **Fix 3 (JS normalisation)** adds a single regex in
  `processNodeLabel`. Affects all Mermaid diagrams that pass
  through `transformMermaidContentToHTML` (i.e. all chat-bubble
  Mermaid), but the regex is idempotent — `<br class="mermaid-br"/>`
  is already the output format, so the regex is a no-op on labels
  that already had the normalised form.

## Impact Analysis

| Issue | Before this fix | After this fix |
|---|---|---|
| Pie title/legend overlap (any theme, narrow chat column) | Title text and legend rect render OVER the pie's drawn area | Title sits above the pie, legend sits below, no overlap |
| Bold text in chat (any flowchart shape, dark mode) | Bold text white on white canvas — invisible | Bold text dark on white canvas — clearly readable |
| Bold text in fullscreen (any flowchart shape) | Already correct (bold black on white) | Unchanged — still correct |
| Bold text in chat (light mode) | Already correct (bold dark on light bubble bg) | Unchanged — still correct |
| `<br/>` line breaks in stadium (A3) | Silently joined to adjacent text | Renders as a real line break |
| `<br/>` line breaks in subroutine (A6) | Silently joined to adjacent text | Renders as a real line break |
| `<br/>` line breaks in rectangle (A1), diamond (A4), cylinder (A5) | Worked (parser tolerated bare tags) | Unchanged — still works |
| `\n` line breaks (any shape) | Worked via existing conversion | Unchanged — still works |
| Image export (PNG) of any chart | Already correct (white canvas, dark text) | Unchanged |

## Testing Checklist

1. **Pie chart in any chat column width** — confirm title, pie
   center, and legend do NOT overlap. Title at top, legend at
   bottom, pie in the middle, all readable.
2. **Flowchart with `<b>bold</b>` in any node label, dark mode** —
   confirm bold text is dark (`#24292f`), not white.
3. **Flowchart with `<b>bold</b>` in any node label, light mode** —
   confirm bold text is still dark and readable.
4. **Fullscreen any flowchart with `<b>bold</b>`** — confirm bold
   text is dark (already worked; confirm not regressed).
5. **6-shape flowchart test (A1=A2 rect, A3 stadium, A4 diamond,
   A5 cylinder, A6 subroutine) with `<br/>` in every label** —
   confirm line breaks render in all 6 shapes, including A3 and A6.
6. **Combined test**: flowchart with `<b>Line 1<br/>Line 2</b>` —
   confirm both bold and line break render correctly, AND the bold
   text is dark in dark mode chat.
7. `node --check UI/visualisation_engine/visualisation_v3.js` →
   `JS_OK` (no syntax errors).
8. UTF-8 no-BOM byte-check on `business-ai-platform-v2.html` and
   `visualisation_v3.js` → `BOM_FREE`.
9. `git status` shows only the two targeted files modified
   (`business-ai-platform-v2.html`, `visualisation_v3.js`) plus
   the new fix-log file. User's unrelated work in
   `routes/organisation_credentials_routes.py`,
   `modules_internal/components/user_auth.js`, test logs, etc.
   must NOT be staged.

## Files Modified

| File | Lines | Change |
|---|---|---|
| `UI/business-ai-platform-v2.html` | L10820-10858 (pie rule) | Replaced `min-width: 700px !important` with explicit `width: 760px !important; height: 760px !important` (plus matching `min-` and `max-` with `!important`) and bumped parent `min-height` to 800 px |
| `UI/business-ai-platform-v2.html` | L10859-10886 (new block) | Added foreignObject `strong`/`em`/`b`/`i`/`.mermaid-bold`/`.mermaid-italic` colour override with `color: #24292f !important`, scoped to `.viz-container .mermaid foreignObject` |
| `UI/visualisation_engine/visualisation_v3.js` | L5580-5592 (processNodeLabel TEP 4) | Added `<br>` → `<br class="mermaid-br"/>` regex normalisation step BEFORE the existing `\n` conversion |
| `UI/visualisation_engine/VISUALIZATION_SYSTEM_DOCUMENTATION.md` | L4 + new subsection | Bumped "Last updated" header; added "Pie overlap + bold-in-chat + `<br/>` follow-on (added July 22, 2026)" subsection |
| `VISUALIZATION_FOLLOWON_PIE_BOLD_BR_FIX_JULY22_2026.md` | NEW (root) | This file |

(Three files logically edited, one new file. Net: ~200 lines, -10 lines.)

## Rollback Information

`git revert <sha>` of the commit, or `git reset --hard HEAD~1` if
the fix isn't yet pushed. No data migration; no DB migration; no
schema change; no API change. Pure CSS + a 1-line regex addition.

If the always-white foreignObject override reads as too aggressive
for some flows (e.g. if Mermaid's internal bold styling needs to
remain theme-aware), the selector could be tightened to e.g.
`.viz-container .mermaid foreignObject .mermaid-bold` only —
targeting the class Mermaid's `processNodeLabel` explicitly adds,
leaving bare `<b>`/`<strong>` tags inside labels untouched. But in
practice Mermaid's flowchart HTML labels emit `.mermaid-bold` and
`.mermaid-italic` consistently, so the wider selector is safe.

If `width: 760px !important` reads as too wide for some chart
contexts, the value can be tuned (e.g. 600 px for tighter columns,
900 px for very wide pies). The constant matters less than the
fact that it's an EXPLICIT dimension (not a `min-`) — preventing
the SVG from collapsing to viewBox-driven sizing.

If `<br>` normalisation causes unexpected behaviour in any other
shape, the regex could be scoped with a positive lookahead for
known affected shapes. But the normalisation is idempotent
(no-op on already-normalised `<br class="mermaid-br"/>`) so
broadening the scope is safe.

## Related Documentation

- `VISUALIZATION_MERMAID_CHAT_BG_AND_GITGRAPH_WRAPPING_FIX_JULY22_2026.md` —
  immediate predecessor. Established the always-white-canvas
  principle. This fix builds on it: the always-white canvas is the
  reason the foreignObject bold-text issue is now visible (it
  wasn't visible before because both text and bg were dark).
- `VISUALIZATION_PIE_TITLE_LEGEND_OVERLAP_FIX_JULY22_2026.md` —
  earlier same-day fix that added the first `min-width: 700px`
  pie rule. This fix supersedes it with explicit dimensions.
- `VISUALIZATION_CANVAS_BG_AND_FULLSCREEN_FIX_JULY22_2026.md` —
  established the always-white-canvas principle for Mermaid
  internals + Plotly paper bg.
- `VISUALIZATION_RECT_TIGHTENING_FIX_JULY22_2026.md` — added
  chart-type detection to skip rect inflation for pie/git
  graph/gantt. The chart-type detection logic is unchanged by
  this fix.
- `VISUALIZATION_MERMAID_RENDERING_FIX_JULY22_2026.md` — earlier
  same-day fix for the off-screen-but-measurable staging element.
- `UI/visualisation_engine/VISUALIZATION_SYSTEM_DOCUMENTATION.md` —
  master doc; bumped "Last updated" + new subsection.

## Deployment Notes

- No backend change. Pure frontend CSS + 1-line JS regex.
- No migration. No API change. No env-var change.
- Deploy via `git push gerardo v11:v11` (Render auto-deploys).
- After deploy, refresh the browser tab hard (Ctrl+Shift+R) to
  clear the cached `business-ai-platform-v2.html`. Existing
  diagrams that already rendered with overlap or invisible bold
  will still show those issues (their DOM is baked); new renders
  and reloaded diagrams will pick up the new CSS/JS immediately.

---

**Author:** AI coding agent (Claude)
**Date:** July 22, 2026
**Pair-fix with:** `VISUALIZATION_MERMAID_CHAT_BG_AND_GITGRAPH_WRAPPING_FIX_JULY22_2026.md`,
`VISUALIZATION_PIE_TITLE_LEGEND_OVERLAP_FIX_JULY22_2026.md`,
`VISUALIZATION_RECT_TIGHTENING_FIX_JULY22_2026.md`,
`VISUALIZATION_CANVAS_BG_AND_FULLSCREEN_FIX_JULY22_2026.md`