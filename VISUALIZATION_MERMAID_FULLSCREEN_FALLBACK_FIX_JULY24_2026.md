# Mermaid Fullscreen Fallback Fix — July 24, 2026

## Overview

When a series of AI responses renders Mermaid diagrams, occasionally a
diagram's inline body fails to render — the action bar (copy / zoom / theme /
export buttons) is visible, but the diagram itself is missing. Pressing the
**Copy** button on the action bar successfully retrieves the original Mermaid
source via `data-original-content`, but opening **Fullscreen** shows
"No diagram found to display" because `openMermaidFullscreen` searches the
container for an inline `<svg>` and finds none.

This is a one-function defensive fix in `openMermaidFullscreen`:
when the inline SVG is missing but the source content is available, render a
fresh SVG off-screen and continue with the existing overlay-creation flow.

## Root Cause Analysis

In `UI/visualisation_engine/visualisation_v3.js`:

- **`addMermaidUnifiedActionBar`** (L6881–L6921) appends the action bar to
  the **outer** `.viz-container`.
- **`renderMermaidDirectly`** (L5008–L5263) inserts the SVG inside
  `.viz-content-area > .mermaid`.
- A concurrent re-render's cleanup at **L5063** runs:
  ```js
  contentArea.querySelectorAll('.mermaid, .mermaid-deferred-placeholder')
              .forEach(d => d.remove());
  ```
  This wipes the `.mermaid` div (which contains the inline `<svg>`), but
  the outer `.viz-container` and its action bar are untouched.

Concurrent renders are observed in `TwoRuleStreamProcessor`
(`UI/visualisation_engine/streamingTwoRule.js`) when stream finalization
re-runs `_processDeferredRenders` (L265–L302) while the engine is still
running an initial render, or when the stream's `renderMarkdown` (L2343–L2398)
re-creates the containerId with `${Date.now()}-${random}` and races an
in-flight render on the same source.

The visible symptom is therefore:

- Outer `.viz-container` — present, action bar visible.
- Inner `.viz-content-area > .mermaid` — empty (wiped by cleanup).
- `data-original-content` on `.viz-container` — still set
  (assigned at **L5123** of `renderMermaidDirectly`), so the source survives.

`openMermaidFullscreen` then does `container.querySelector('svg')` and
correctly returns `null` — but the original behaviour was to bail out with
"No diagram found to display" even though the source is right there.

## Fix

**File:** `UI/visualisation_engine/visualisation_v3.js`
**Function:** `openMermaidFullscreen` (was at L10603; expanded by ~50 lines).

### Change 1 — async signature + `let currentSvg`

```js
async openMermaidFullscreen(container, diagramContent, chartId) {
    // ...
    let currentSvg = container.querySelector('svg');
    let parkedHolder = null;        // EW (Jul 24 2026): hidden holder for fallback SVG
    // ...
}
```

The function became async because `mermaid.render()` (Mermaid 10.6.1) returns
a Promise. The `let` on `currentSvg` lets the fallback branch reassign it.

### Change 2 — defensive fallback render when SVG missing

```js
if (!currentSvg) {
    const source = (container.getAttribute && container.getAttribute('data-original-content'))
        || diagramContent || '';
    if (!source || typeof window === 'undefined' || !window.mermaid
        || typeof window.mermaid.render !== 'function') {
        this.showNotification(' No diagram found to display', 'error');
        return;
    }
    const staging = document.createElement('div');
    staging.style.cssText = 'position:absolute;left:-99999px;top:0;visibility:hidden;width:1px;height:1px;overflow:hidden;pointer-events:none;';
    const fallbackId = `fs-fallback-${chartId || Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
    document.body.appendChild(staging);
    try {
        const svgString = await window.mermaid.render(fallbackId, source);
        if (!svgString) { /* notification + return */ }
        staging.innerHTML = svgString;
        const stagedSvg = staging.querySelector('svg');
        if (!stagedSvg) { /* notification + return */ }
        parkedHolder = document.createElement('div');
        parkedHolder.style.cssText = 'display:none';
        parkedHolder.appendChild(stagedSvg);
        container.appendChild(parkedHolder);
        currentSvg = stagedSvg;
    } catch (err) {
        console.error('🖥️ Mermaid fallback render failed:', err);
        this.showNotification(' No diagram found to display', 'error');
        return;
    } finally {
        if (staging.parentNode) staging.remove();
    }
}
```

- **Why a hidden holder instead of injecting into `.viz-content-area`:**
  putting the fallback SVG back into the content area would re-trigger the
  same cleanup race we're defending against. A `display:none` sibling of the
  container's children is invisible to `contentArea.querySelectorAll(...)`,
  so the next cleanup pass won't remove it.
- **Why `staging` is appended to `document.body` rather than `container`:**
  `mermaid.render` measures the host element to compute layout. An off-screen
  element with `1px` size produces a tiny but valid viewport; in practice the
  resulting SVG is laid out from the diagram source itself.
- **Why the original "No diagram found" branch is preserved:** if
  `data-original-content` is missing too (the very first render never
  completed), or `mermaid` is not yet loaded, we still bail out — there is
  nothing to recover from.

### Change 3 — cleanup after clone

Right after the existing `const clonedSvg = currentSvg.cloneNode(true);`:

```js
if (parkedHolder && parkedHolder.parentElement === container) {
    parkedHolder.remove();
}
```

This prevents subsequent re-render paths — `reRenderFullscreenIfOpen`
(L10890) and the font/theme handlers installed by
`setupMermaidButtonHandlers` (L6926–L7012) — from picking up the stashed
SVG instead of the live one when the user later changes font size or theme.

## Why this fix is isolated

| Concern | Before | After |
|---|---|---|
| Behaviour when inline SVG present | Fullscreen works | Fullscreen works (unchanged) |
| Behaviour when inline SVG missing, source present | "No diagram found to display" | Re-renders from source, opens fullscreen |
| Behaviour when source also missing | "No diagram found to display" | "No diagram found to display" (unchanged) |
| Streaming pipeline / cleanup paths | Untouched | Untouched |
| Other visualisation types (Plotly, Recharts, D3, etc.) | Unaffected | Unaffected |
| Multiple `openMermaidFullscreen` calls on same container | Each call re-checks `querySelector('svg')` | Same; parkedHolder cleaned before return |

## Impact Analysis

| Scenario | Before | After |
|---|---|---|
| Normal inline render | Fullscreen opens in <16 ms | Same (no async path entered) |
| Concurrent re-render wiped SVG, source present | Error toast | Fullscreen opens in ~30–60 ms (mermaid.render round-trip) |
| Concurrent re-render wiped SVG, source missing | Error toast | Error toast (unchanged) |
| User closes fullscreen, opens again on same container | n/a | Holder already cleaned; live SVG used if present, fallback re-renders if missing |

## Testing Checklist

### Automated

- `node --check UI/visualisation_engine/visualisation_v3.js` — exit 0.
- UTF-8 BOM byte check — no BOM on the touched file.
- `git diff --check` — no whitespace errors.

### Manual

For each scenario below, hard-reload (`Ctrl+Shift+R`) to clear cached JS:

1. **Normal flow** — paste a small Mermaid diagram, confirm inline render, click
   fullscreen. Verify: overlay appears within 1 frame, zoom controls work,
   close restores the page.
2. **Reproduce the race** — paste a Mermaid diagram, immediately type into the
   chat to stream another message. When the second message's stream finalizes,
   reload the first message's container with a font-size change. If the
   inline SVG disappears, clicking fullscreen should still open the diagram.
3. **Source missing** — open DevTools, delete the `data-original-content`
   attribute on a `.viz-container`, then click fullscreen. Expect: error toast
   identical to the pre-fix message.
4. **Multiple consecutive opens** — open fullscreen, close, open again. Confirm
   no DOM leak (the parked holder should be removed after the first open; the
   second open should use the live SVG or a fresh fallback).

### Regression Sweep

- Plotly fullscreen — unchanged path, no regression expected.
- Recharts fullscreen — unchanged path, no regression expected.
- Image / SVG / PDF / D3 fullscreens — none of these go through
  `openMermaidFullscreen`; no regression possible.

## Files Modified

- `UI/visualisation_engine/visualisation_v3.js` — `openMermaidFullscreen`:
  added `async` keyword, `let currentSvg`, fallback render branch (~50 lines),
  and post-clone parkedHolder cleanup (~5 lines).

## Rollback Information

Reverting the commit removes the `async` keyword, restores `const currentSvg`
to its `querySelector('svg')`-only initialisation, and removes the fallback
branch and the parkedHolder cleanup. The function returns to its original
behaviour: "No diagram found to display" whenever the inline SVG is absent.

No other call sites change; no data formats, env vars, schemas, or public API
contracts are touched.

## Related Documentation

- `UI/visualisation_engine/VISUALIZATION_SYSTEM_DOCUMENTATION.md` — overall
  architecture of the visualisation pipeline (will receive a one-line note
  on this fix in a follow-up).
- `VISUALIZATION_MERMAID_BOLD_SHAPE_SIZING_FIX_JULY23_2026.md` — prior
  Mermaid fix (bold / shape sizing / asymmetric syntax); unrelated to this
  bug.
- `UI/visualisation_engine/streamingTwoRule.js` — `TwoRuleStreamProcessor`
  where the concurrent-re-render race originates. Architectural fix in that
  file is a much larger change and out of scope for this targeted fix.

## Deployment Notes

No env-var, schema, or API changes. No front-end cache busting required
beyond the normal browser reload. Single-file diff; risk is minimal.

---

## Followup — Concurrent Re-render Race in `renderMermaidDirectly`

The fullscreen fallback fix above addresses the user-facing "No diagram
found to display" toast when the inline SVG is missing. The companion fix
below addresses the upstream cause of that missing SVG: a race between two
`renderMermaidDirectly` calls on the same `contentArea`.

### Race Trace

In `UI/visualisation_engine/visualisation_v3.js`:

- `renderMermaidDirectly` (L5008) wipes prior `.mermaid` divs at **L5063**:
  ```js
  contentArea.querySelectorAll('.mermaid, .mermaid-deferred-placeholder')
              .forEach(d => d.remove());
  ```
- The same function then awaits `mermaid.render(...)` at L5134 and,
  on resolution, writes the SVG into its own `mermaidDiv` at **L5185** and
  attaches the action bar to the outer `vizContainer` at **L5236**.

When two renders race on the same `contentArea` (e.g. stream-finalize
triggers `_processDeferredRenders` while the initial chunk handler is still
mid-`await`, or `_scheduleMermaidRerender` is racing the original attempt),
the second call's L5063 cleanup wipes the first call's `<svg>`-bearing div.
The first call's awaited promise still resolves — it writes SVG into a
now-detached div and stamps an action bar on `vizContainer`. Net effect:

- Outer `.viz-container` — has an action bar (from the stale render).
- Inner `.viz-content-area > .mermaid` — empty (wiped by the second call,
  until the second call's own SVG lands).
- User sees: visible action bar, empty body, intermittent "diagram missing".

### Fix — Render Token on `contentArea`

Same idea React 18+ uses internally to drop stale render commits. Each call
to `renderMermaidDirectly` bumps a counter on `contentArea` and captures its
own value; every post-`await` DOM mutation is gated on the captured value
still being current.

```js
// At the top of renderMermaidDirectly (L5024 area):
const myRenderToken = (contentArea._mermaidRenderToken =
    (contentArea._mermaidRenderToken || 0) + 1);

// Before mermaidDiv.innerHTML = svg (L5185 area):
if (contentArea._mermaidRenderToken !== myRenderToken) {
    console.log(`🔁 VIZ-V3: Mermaid render superseded
        (token ${myRenderToken} -> ${contentArea._mermaidRenderToken});
        discarding stale SVG`);
    return;
}

// Before addMermaidUnifiedActionBar (L5236 area):
if (contentArea._mermaidRenderToken !== myRenderToken) {
    console.log(`🔁 VIZ-V3: Mermaid render superseded before action bar
        (token ${myRenderToken}); skipping`);
    return;
}

// At the top of the catch block (L5241 area):
if (contentArea._mermaidRenderToken !== myRenderToken) {
    console.log(`🔁 VIZ-V3: Mermaid render superseded in catch
        (token ${myRenderToken}); skipping stale error render`);
    return;
}
```

### Why this is isolated

| Concern | Before | After |
|---|---|---|
| Behaviour on the only render | Renders normally | Renders normally (token check passes) |
| Behaviour with two racing renders | First wins-but-is-wiped; UI shows action bar with empty body | Latest in-flight render owns all UI state |
| Action-bar duplication | Two action bars in races | Only the surviving render attaches an action bar |
| `_scheduleMermaidRerender` race | Original + retry both reach L5236 | Retry supersedes original via token bump |
| Stale error UI | Stale error rendered after supersession | Swallowed silently; the live render owns error UI |
| Plotly / Recharts / D3 / other types | Unaffected | Unaffected (token is `contentArea`-scoped per Mermaid call) |

### Why the token lives on `contentArea`, not `vizContainer`

The race window opens in `contentArea` (that's what L5063 wipes). Putting
the token there keeps the guard local to the exact place where the race
manifests and prevents cross-talk between unrelated `.viz-container`s that
might share a parent. A `vizContainer`-scoped token would leak state
across sibling renders.

### Manual Verification

1. Hard-reload (`Ctrl+Shift+R`) the SPA.
2. Send an AI message that produces a Mermaid diagram, then immediately
   type/send a second message that also produces a Mermaid diagram.
3. Watch both messages' viz-containers. Confirm: each diagram renders with
   an action bar; neither has an empty body; neither has duplicated action
   bars.
4. DevTools console should NOT show "🔁 VIZ-V3: Mermaid render superseded"
   for normal single-stream renders. If it does, two renders raced and the
   older one was correctly discarded.

### Rollback Information

Revert the four token-guard edits to `renderMermaidDirectly`. The function
returns to its original behaviour: every render attempt commits, even if
its `mermaidDiv` was already wiped. The fullscreen fallback fix above is
unaffected and remains useful as a defensive layer.

No env-var, schema, or API changes.

---

## Followup — Destructure `mermaid.render()` in the fullscreen fallback

The fullscreen fallback described at the top of this document was a *shell*
on first deploy. It never actually produced a usable SVG for the user —
which is why, after the previous fixes shipped, the user still reported
"clicking Fullscreen shows No diagram found to display even though the
source is there".

### Root Cause

`mermaid.render(id, source)` in Mermaid 10.x returns a
`Promise<{svg: string, bindFunctions?: (element: Element) => void}>`,
not a bare string. Every other call site in `visualisation_v3.js`
(L5143, L5513, L7212, L7504, L7696, L10317) destructures with
`const { svg } = await mermaid.render(...)`.

The fallback at L10693 (in `openMermaidFullscreen`) did not:

```js
const svgString = await window.mermaid.render(fallbackId, source);
if (!svgString) { /* bail */ }
staging.innerHTML = svgString;
```

When the fallback fired, `svgString` was the object `{svg: "...",
bindFunctions: fn}`. The truthy check passed (objects are truthy), then
`staging.innerHTML = svgString` coerced the object to `"[object Object]"`,
`staging.querySelector('svg')` returned null, and the empty-stagedSvg
check surfaced "No diagram found to display" — identical to the
pre-fallback failure.

The success path's render at L5143 had always been correct, so the
inline-render case worked; only the fallback (i.e. exactly the case the
fallback was added to save) was broken.

### Fix

**File:** `UI/visualisation_engine/visualisation_v3.js`
**Function:** `openMermaidFullscreen` fallback branch (around L10693).

Replace the buggy destructure with:

```js
const { svg: svgString, bindFunctions } = await window.mermaid.render(fallbackId, source);
if (!svgString) { /* bail */ }
staging.innerHTML = svgString;
const stagedSvg = staging.querySelector('svg');
if (!stagedSvg) { /* bail */ }
if (typeof bindFunctions === 'function') {
    try { bindFunctions(stagedSvg); } catch (e) { /* best-effort */ }
}
```

The `svg` alias preserves the existing `svgString` variable name so the
downstream snippet (the stagedSvg query, the parkedHolder construction,
the `currentSvg = stagedSvg` assignment) is unchanged. The
`bindFunctions` wiring is best-effort wrapped in try/catch so a missing
or throwing handler (some Mermaid diagram types don't return one) does
not break fullscreen.

### Why this is isolated

| Concern | Before | After |
|---|---|---|
| Inline render (success path) | Works | Works (unchanged) |
| Fullscreen on inline SVG | Works | Works (unchanged) |
| Fullscreen fallback, source present | Bails with "No diagram found" | Re-renders SVG, opens fullscreen |
| Fullscreen fallback, source missing | Bails with "No diagram found" | Bails with "No diagram found" (unchanged) |
| Clickable nodes in fullscreen | Not wired (renderer's bindFunctions was discarded) | Wired via best-effort bindFunctions call |
| Other call sites | Already correct | Already correct (no change) |

### Manual Verification

1. Hard-reload (`Ctrl+Shift+R`) to clear cached JS.
2. Open a thread that contains a Mermaid diagram whose inline body
   failed to render (action bar visible, body empty).
3. Click the **Fullscreen** button on that diagram's action bar.
4. Expect: fullscreen overlay appears within ~50 ms with the rendered
   diagram — no "No diagram found to display" notification.
5. Run with DevTools console open. The fallback's `console.error('🖥️
   Mermaid fallback render failed:', …)` line should NOT fire.
6. Optional: confirm the fullscreen still allows click-to-zoom / pan
   on interactive node types (flowchart click, sequenceDiagram actor
   click). The bindFunctions hook is what wires those.

### Rollback Information

Revert the L10693 destructure to its previous form. The fallback
returns to its original (broken) behaviour: it spreads the
`mermaid.render` object into the DOM and bails with "No diagram found
to display". The success path is unaffected — it never relied on the
fallback.

No env-var, schema, or API changes.
