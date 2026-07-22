# Visualisation — Always-White Canvas, Pie Label Buffer, Fullscreen Single-Fit (July 22, 2026)

**Status:** Shipped in this commit, pending push to `gerardo v11`.
**Branch:** `v11`
**Touched files (4):**
- `UI/visualisation_engine/visualisation_v3.js`
- `UI/business-ai-platform-v2.html`
- `UI/visualisation_engine/VISUALIZATION_SYSTEM_DOCUMENTATION.md`
- This file (new).

**Related:**
- `VISUALIZATION_MERMAID_RENDERING_FIX_JULY22_2026.md` — staging-CSS fix (commits `3671ef9d`, `1b94a677`); the prerequisite that made this follow-on work tractable.
- `VISUALIZATION_STREAMING_FIXES_APRIL9_2026.md` — April 9 precedent for the dated fix-log format.

---

## 1. Overview

The July 22 staging-CSS fix (already on `gerardo v11`) made Mermaid pies and flowcharts render with a positive viewBox on the first attempt. Once the user could see working output, four follow-on issues became visible:

1. **Chart canvas background was inconsistent and unreadable in dark mode.** Some paths produced a transparent canvas, others a theme-aware opaque canvas. When the page was in dark mode, axis lines, grid lines, and titles were dark text on a dark canvas — they blended in.
2. **AI-picked chart colours only worked in one theme.** When the AI generated Mermaid/Plotly source it sometimes chose axis/grid/title colours that read fine on a white canvas in light mode but vanished on a dark canvas in dark mode.
3. **Image export was inconsistent with render.** Mermaid PNG export was hard-coded white; Plotly export honoured `paper_bgcolor`, so the chat-area path exported a transparent PNG.
4. **Pie labels sat close to or overlapped the pie** in narrow chat columns, and the fullscreen overlay fired its resize fit three times in rapid succession producing a visible race in the console log (4.458 → 0.803 → 4.458).

This fix addresses all four. After this commit, **every chart canvas is always `#ffffff` regardless of UI theme**, pie labels have a CSS buffer to keep them clear of the slice edges, and the fullscreen overlay fits exactly once on open (with a `ResizeObserver` for live resize).

---

## 2. Root Cause Analysis

### 2.1 Theme-aware canvas split

There were three independent rendering paths, each with its own canvas colour strategy:

| Path | File:line | `bgColor` strategy |
|---|---|---|
| `applyEnhancedPlotlyTheme` (chat-area Plotly) | `visualisation_v3.js:3092-3095` | `'rgba(0,0,0,0)'` (transparent) |
| `toggle3DView` (dedicated/calculator Plotly) | `visualisation_v3.js:4267` | `isDark ? '#0d1117' : '#ffffff'` (theme-aware) |
| `updateTheme` / `updateChartTheme` (theme-toggle retroactive recolor) | `visualisation_v3.js:9389`, `9428` | `isDark ? '#0d1117' : '#ffffff'` (theme-aware) |
| `mermaid.initialize()` per-render | `visualisation_v3.js:4475`, `4810`, `6443`, `6637`, `6869` | `theme: isDark ? 'dark' : 'base'` + `themeVariables.backgroundColor` (theme-aware) |

The chat-area path was transparent; the dedicated path was opaque; Mermaid flipped `theme` to `'dark'` but the per-render block at L4475 used `'base'`, overriding the engine-wide `'dark'` inconsistently. Net result: in dark mode, the chat-area Plotly path was transparent (chat-bubble bg showing through), the dedicated path was `#0d1117`, and Mermaid depended on whether `theme: 'dark'` actually applied. When the AI picked dark text/grid colours for a chart, they disappeared on the dark canvas.

### 2.2 AI-picked colours

The model emits `axis.ticks.color = '#374151'` or `themeVariables.textColor = '#374151'` because that's what reads against a white page. When the platform's dark mode flips the canvas to `#0d1117`, that same `#374151` becomes near-invisible. The model has no signal about the platform's theme, so it cannot make the right choice at generation time.

The correct answer is **not** to teach the model to branch on theme (it can't see the theme), but to give it a constant canvas so its one-time colour choices are always legible.

### 2.3 Plotly export honoured `paper_bgcolor`

`Plotly.downloadImage` (L9050-9057) and `Plotly.toImage` (L9179-9184) honour the current `paper_bgcolor`. With the chat-area path using `'rgba(0,0,0,0)'`, the downloaded PNG had alpha-channel transparency. Users expected an opaque image and got a "ghost" PNG that pasted invisibly into slides.

### 2.4 Pie label positioning

Mermaid 10.6.1 emits pie labels outside the pie with leader lines; the labels sit at the edges of the pie's natural 450×450 viewBox. In a narrow chat column, the SVG can be CSS-scaled down and the labels get close to the slice edges, sometimes overlapping. Mermaid exposes no built-in knob to reposition pie labels — `pie: { useMaxWidth: false }` was tried (Jul 21) and reverted (Jul 22) because `useMaxWidth` only governs post-render CSS scaling, not the viewBox itself.

### 2.5 Fullscreen resize race

`initFullscreenControls` (`visualisation_v3.js:10210-10397`) chained three `setTimeout(fitToScreen, 100/500/1000)` after an immediate `updateTransform()` with `scale = 0.8`. Plus the caller added its own `setTimeout(..., 300)` at L10093. The user observed in their console: **4.458 → 0.803 → 4.458**. The middle 0.803 is the *normal* `Math.min(scaleX, scaleY)` calculation at L10278 — it just happens to land while the layout is transiently narrower mid-CSS. There was also no resize listener on the overlay, so a window resize after open required manual `#fit-screen` clicks.

---

## 3. Fixes

### Fix 1 — Always-white canvas

**File:** `UI/visualisation_engine/visualisation_v3.js`
**Files touched (4 lines ranges):**

#### 3.1.1 Chat-area Plotly — `applyEnhancedPlotlyTheme` (L3092-3095)

```js
// BEFORE
const isDark = this.options.theme === 'dark';
const bgColor = 'rgba(0,0,0,0)'; /* TRANSPARENT */
const textColor = isDark ? '#ffffff' : '#24292f';
const gridColor = isDark ? 'rgba(255,255,255,0.15)' : '#e1e4e8';

// AFTER
// EW (Jul 22 2026): Always-white canvas. The AI picks axis/grid/text
// colours that read against white in either UI theme; exporting to
// PNG produces an opaque white image (matches Mermaid PNG export).
const bgColor = '#ffffff';
const textColor = '#24292f';
const gridColor = '#e1e4e8';
```

`isDark` is now unused in this function; the declaration was removed to keep the diff small and avoid linter warnings.

#### 3.1.2 Dedicated/calculator Plotly — `toggle3DView` (L4266-4280)

```js
// BEFORE
const bgColor = isDark ? '#0d1117' : '#ffffff';

// AFTER
const bgColor = '#ffffff';
```

#### 3.1.3 Theme-toggle retroactive recolor — `updateTheme` (L9389), `updateChartTheme` (L9428)

Same pattern as 3.1.2: `bgColor = '#ffffff'`, `textColor = '#24292f'`, `gridColor = '#e1e4e8'`, regardless of `isDark`.

#### 3.1.4 Per-render `mermaid.initialize()` — 5 call sites

**Why:** `theme: 'dark'` would invert Mermaid's internal palette and produce dark text on dark fills inside colored theme nodes. `theme: 'base'` + light text colours produces a white canvas with dark Mermaid-internal elements.

- `renderMermaidDirectly` (L4472-4515): force `theme: 'base'` and white background.
- `popup/fullscreen mermaid.initialize` (L4810-4864): same.
- `direction-toggle mermaid.initialize` (L6443-6460): minimal site, force `theme: 'base'`.
- `applyMermaidColorTheme` (L6637-6712): flip `theme`, `backgroundColor`, `lineColor`, `edgeLabelBackground` to light constants. **Keep** `#ffffff` text forces — load-bearing for themed coloured nodes.
- `applyMermaidFontSize` (L6869-6892): symmetric edit to applyMermaidColorTheme.

#### 3.1.5 `applySimplifiedMermaidPostProcessing` (L5470-5507)

```js
// BEFORE
function applySimplifiedMermaidPostProcessing(svgElement, isDark) {
    // ...
    text.setAttribute('fill', isDark ? '#e6edf3' : '#24292f');
    // ...
}

// AFTER
function applySimplifiedMermaidPostProcessing(svgElement) {
    // ...
    text.setAttribute('fill', '#24292f');
    // ...
}
```

All 6 call sites updated with `replace_all`: L4614, L6477, L6770, L6958, L7472, L7686. The 2 that previously broke with `ReferenceError: isDark is not defined` (after their enclosing `isDark` declarations were removed) are now fixed by the parameter drop.

**Why keep `#ffffff` text forces in `applyMermaidColorTheme` and `applyMermaidFontSize`?** Those are the *themed* entry points where the user explicitly picks a colour palette (forest/neutral/dark via `getMermaidColorThemes()`). The palette paints the node fills in saturated colours, and the `#ffffff` text forces give white text maximum contrast against those fills. They are load-bearing for the themed-coloured-nodes design and are **NOT** removed — only `theme`, `backgroundColor`, `lineColor`, `edgeLabelBackground` are flipped to light-mode constants.

### Fix 2 — Plotly export consistency

**No code change needed.** After Fix 1, `paper_bgcolor` is always `'#ffffff'`. `Plotly.downloadImage` and `Plotly.toImage` honour this, so exported PNGs are always opaque white. This matches Mermaid's hard-coded-white PNG export (`visualisation_v3.js:7740`, `7778-7779`, `7862`, `7962`). Verified by exporting a chat-area chart after Fix 1.

### Fix 3 — Pie chart label buffer

**File:** `UI/business-ai-platform-v2.html` (added after the staging CSS block, around L10755)

```css
/*
 * EW (Jul 22 2026): Pie chart label buffer. Mermaid 10.6.1 emits
 * pie labels outside the pie with leader lines; in narrow chat
 * columns the SVG can be CSS-scaled down so the labels sit close
 * to the slice edges. Give the SVG vertical room so labels are
 * not clipped at the bottom of the chat container, and give the
 * pie+labels composition horizontal room so leader lines have
 * somewhere to go. Mermaid's default pie viewBox is 450x450; 520
 * leaves 70 px of breathing room. Scoped via :has() so only pies
 * get the buffer (other Mermaid types are unaffected).
 *
 * Cross-references:
 *   - VISUALIZATION_SYSTEM_DOCUMENTATION.md, section "Always-white
 *     canvas + pie label buffer (added July 22, 2026)".
 *   - VISUALIZATION_CANVAS_BG_AND_FULLSCREEN_FIX_JULY22_2026.md.
 */
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

- `padding: 8px 8px 24px 8px` — buffer below so leader-line labels aren't clipped.
- `max-height: 520px` — Mermaid's default pie viewBox is 450×450; 520 gives 70 px of breathing room for labels.
- `:has()` selector keeps the buffer scoped to pies only — other Mermaid types are unaffected.

### Fix 4 — Fullscreen single-fit + ResizeObserver

**File:** `UI/visualisation_engine/visualisation_v3.js`

#### 3.4.1 `initFullscreenControls` end (L10422-10425)

Replaced the three-setTimeout chain (`setTimeout(fitToScreen, 100/500/1000)`) with a single rAF + ResizeObserver:

```js
// EW (Jul 22 2026): Single-fit, ResizeObserver-driven. The previous
// setTimeout(100/500/1000) chain produced a visible 3-step race (the
// user's console log: 4.458 -> 0.803 -> 4.458) because the viewport
// was transiently narrower mid-CSS-layout during the middle fit.
// Now: wait for the first frame the viewport is measurable, fit
// exactly once, then keep fitting on real size changes only.
const initialFit = () => {
    const r = viewport.getBoundingClientRect();
    if (r.width <= 0 || r.height <= 0) {
        requestAnimationFrame(initialFit);  // viewport still settling
        return;
    }
    fitToScreen();
};
requestAnimationFrame(initialFit);

// Live resize support — the overlay previously had no resize listener.
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

#### 3.4.2 `reRenderFullscreenIfOpen` (L10228-10233)

Replaced `setTimeout(() => fitButton.click(), 100)` with double-rAF:

```js
// BEFORE
setTimeout(() => fitButton.click(), 100);

// AFTER
requestAnimationFrame(() => requestAnimationFrame(() => fitButton.click()));
```

Two frames (~32 ms at 60 fps) is enough for the SVG insertion + style flush to settle before the click, replacing the magic 100 ms number with a frame-driven primitive.

#### 3.4.3 `closeFullscreen` (L10354-10361)

Extended try block to disconnect `_fullscreenResizeObserver` and cancel `_fullscreenResizeRaf`:

```js
if (this._fullscreenResizeObserver) {
    this._fullscreenResizeObserver.disconnect();
    this._fullscreenResizeObserver = null;
}
if (this._fullscreenResizeRaf) {
    cancelAnimationFrame(this._fullscreenResizeRaf);
    this._fullscreenResizeRaf = null;
}
```

Without this, every fullscreen open would leak an observer that pins the closed overlay in memory and fires `fitToScreen` calls after close.

---

## 4. Impact Analysis

### 4.1 Dark-mode readability

| | Before | After |
|---|---|---|
| Chat-area Plotly | Transparent (chat-bubble showing through) | Always white |
| Dedicated/calculator Plotly | `#0d1117` (dark) in dark mode | Always white |
| Mermaid `theme: 'dark'` (engine-wide) | Theme-aware palette | `theme: 'base'` always |
| AI-picked axis/grid/title colours | Vanish on dark canvas | Always legible on white |
| Mermaid post-processing text fill | `isDark ? '#e6edf3' : '#24292f'` | Always `#24292f` |

### 4.2 Export consistency

| | Before | After |
|---|---|---|
| Mermaid PNG export | Opaque white (unchanged) | Opaque white (unchanged) |
| Plotly PNG export | Transparent (chat-area) or dark (dedicated) | Opaque white |

### 4.3 Pie label clarity

| | Before | After |
|---|---|---|
| Pie label clipping at narrow chat columns | Sometimes overlapping slice edges | 24px bottom buffer, 520px max-height |
| Pie buffer scope | (no buffer) | `:has()`-scoped to pies only |

### 4.4 Fullscreen resize race

| | Before | After |
|---|---|---|
| First-open fit attempts | 3 (immediate + setTimeout 100/500/1000) + caller's 300 ms | 1 (rAF when viewport measurable) |
| Window resize after open | Required manual `#fit-screen` click | Auto-fit via ResizeObserver |
| Observer leak per open/close | N/A (no observer existed) | Disconnected in closeFullscreen |

---

## 5. Testing Checklist

1. `node --check UI/visualisation_engine/visualisation_v3.js` — confirms no JS syntax error. (Run before commit.)
2. UTF-8 no-BOM check on touched files. (Run scoped PowerShell byte-check; do not run `.vscode/fix-bom.ps1` — it's hard-coded to a different checkout.)
3. Serve `UI/` locally and open `UI/visualisation_engine/test_visualizations_live.html`:
   - Load the `mermaid-pie` sample → confirm white canvas, dark labels with leader lines, labels not clipped.
   - Load a `flowchart TD` with 3+ nodes → confirm white canvas, dark text, edges visible.
   - Load a Plotly bar chart sample → confirm white paper, dark axis/grid.
   - Toggle to dark theme via the existing theme switcher → confirm charts are still white-canvas with dark text (not dark-canvas).
4. Open fullscreen on the Mermaid pie → confirm the resize race is gone (only one "🎯 Fitting to screen" log entry per fit, no 4.458 → 0.803 → 4.458).
5. Resize the browser window with fullscreen open → confirm the diagram re-fits (ResizeObserver wired correctly).
6. Export the Plotly chart as PNG → confirm downloaded PNG has a white background.
7. Export a Mermaid chart as PNG → confirm already white (unchanged, sanity check).
8. Inspect `git diff --check`, the focused diff, and `git status` to ensure unrelated modified/untracked files remain untouched. The user's `routes/organisation_credentials_routes.py`, `UI/modules_internal/components/user_auth.js`, and the test-log files in `AI_infrastructure/tests/` and `UI/tests/` must NOT be staged.
9. Watch browser console for any theme-toggle regression — the per-render `theme: 'base'` change should not break existing flows.

---

## 6. Files Modified

| File | Lines | Change |
|---|---|---|
| `UI/visualisation_engine/visualisation_v3.js` | 3092-3095 | `applyEnhancedPlotlyTheme`: bgColor/textColor/gridColor forced to light-mode constants |
| `UI/visualisation_engine/visualisation_v3.js` | 4266-4280 | `toggle3DView`: bgColor forced to `'#ffffff'` |
| `UI/visualisation_engine/visualisation_v3.js` | 9389 | `updateTheme`: bgColor/textColor/gridColor forced to light-mode constants |
| `UI/visualisation_engine/visualisation_v3.js` | 9428 | `updateChartTheme`: bgColor/textColor/gridColor forced to light-mode constants |
| `UI/visualisation_engine/visualisation_v3.js` | 4472-4515 | `renderMermaidDirectly mermaid.initialize`: `theme: 'base'` + light palette |
| `UI/visualisation_engine/visualisation_v3.js` | 4810-4864 | Popup/fullscreen `mermaid.initialize`: same |
| `UI/visualisation_engine/visualisation_v3.js` | 6443-6460 | Direction-toggle `mermaid.initialize`: `theme: 'base'` |
| `UI/visualisation_engine/visualisation_v3.js` | 6637-6712 | `applyMermaidColorTheme`: flip theme/background/line/edge to light, keep `#ffffff` text |
| `UI/visualisation_engine/visualisation_v3.js` | 6869-6892 | `applyMermaidFontSize`: symmetric edit |
| `UI/visualisation_engine/visualisation_v3.js` | 5470-5507 | `applySimplifiedMermaidPostProcessing`: drop `isDark` parameter; text fill always `#24292f` |
| `UI/visualisation_engine/visualisation_v3.js` | 4614, 6477, 6770, 6958, 7472, 7686 | `applySimplifiedMermaidPostProcessing` 6 call sites: drop `, isDark` arg |
| `UI/visualisation_engine/visualisation_v3.js` | 10228-10233 | `reRenderFullscreenIfOpen`: `setTimeout(..., 100)` → double-rAF |
| `UI/visualisation_engine/visualisation_v3.js` | 10354-10361 | `closeFullscreen`: disconnect ResizeObserver, cancel rAF |
| `UI/visualisation_engine/visualisation_v3.js` | 10422-10425 | `initFullscreenControls` end: replace 3-setTimeout chain with rAF + ResizeObserver |
| `UI/business-ai-platform-v2.html` | 10755-10780 | Pie label buffer CSS (`:has()`-scoped) |
| `UI/visualisation_engine/VISUALIZATION_SYSTEM_DOCUMENTATION.md` | after "Off-screen-but-measurable staging CSS" | New sections "Always-white canvas + pie label buffer" and "Fullscreen single-fit + ResizeObserver" |
| `VISUALIZATION_CANVAS_BG_AND_FULLSCREEN_FIX_JULY22_2026.md` | (new) | This file |

---

## 7. Rollback Information

**Revert command:** `git revert HEAD` (single-commit revert will undo all 4 fixes cleanly).

**Partial rollback by file:**
- To keep the fullscreen fix but revert the canvas fix: `git checkout HEAD~1 -- UI/visualisation_engine/visualisation_v3.js` then re-apply only the `initFullscreenControls`/`reRenderFullscreenIfOpen`/`closeFullscreen` blocks.
- To keep the canvas fix but revert the pie buffer: `git checkout HEAD~1 -- UI/business-ai-platform-v2.html` then re-apply only the staging CSS (no re-application needed — pie buffer is purely additive).

**Risk of partial rollback:**
- Reverting the canvas fix re-introduces dark-on-dark in dark mode for the chat-area path.
- Reverting the fullscreen fix re-introduces the 4.458 → 0.803 → 4.458 race.
- Reverting the pie buffer is purely a cosmetic regression.

**Pre-existing behaviour restored on full revert:**
- Chart canvases return to theme-aware (transparent in chat-area, `#0d1117` in dedicated, `theme: 'dark'` in Mermaid engine-wide).
- Mermaid PNG export stays white (was already hard-coded white).
- Plotly PNG export returns to transparent-on-transparent-bubble.
- Fullscreen returns to 3-fit race and no resize listener.

---

## 8. Deployment Notes

- Deploy branch: `v11`. Push target: `gerardo v11:v11`. Render auto-deploys on push.
- Render cold-start unaffected: no new dependencies, no new env vars, no DB migrations.
- No RLS / auth / credentials / data-shape changes.
- Production behaviour change is **additive** (canvas becomes more consistent, fullscreen becomes smoother) — no breaking API changes.

---

## 9. Related Documentation

- `VISUALIZATION_MERMAID_RENDERING_FIX_JULY22_2026.md` — staging-CSS fix that made this work tractable.
- `VISUALIZATION_SYSTEM_DOCUMENTATION.md` — master doc; sections "Mermaid Render Lifecycle", "Staging vs. visible width", "Off-screen-but-measurable staging CSS", "Always-white canvas + pie label buffer (added July 22, 2026)", "Fullscreen single-fit + ResizeObserver (added July 22, 2026)".
- `VISUALIZATION_STREAMING_FIXES_APRIL9_2026.md` — April 9 precedent for the dated fix-log format.
- `AI_infrastructure/core/unified_ai_client.py` — AI provider dispatch (unaffected by this change).
