# REACT VISUALISATION ENGINE — MASTER TECHNICAL DOCUMENT

> **Status.** Authoritative single-source-of-truth for the React/JSX visualisation
> engine. **Date: 2026-07-28** (Tuesday). Last verified against git head
> `bf6b3454` ("fix(visualisation): resolve Lucide/Recharts name collisions in
> identifierHoist") and `bbb60bad` ("feat(viz): identity-check snapshot detects
> Lucide-vs-Recharts collisions"). Production: `https://ai-agents-v10.onrender.com`.
>
> **Companion documents.**
>
> | Document | Purpose |
> |---|---|
> | `REACT_RENDERER_LUCIDE_TROUBLESHOOTING_2026-07-22.md` | Round-by-round postmortem of the Lucide-vs-Recharts name-collision saga. **Read this** if you are investigating a specific bug. |
> | `CLAUDE.md` (repo root) | Repo-wide conventions. Only the sections on caching, encoding, and the diag opt-out flag cross-reference this engine. |
> | `UI/visualisation_engine/visualisation_v3.js` | The 12,000-line controller that owns the rendering pipeline, popups, and toolbars. Only the React-relevant sections are summarised here. |
>
> **Audience.** A future AI (or human) who needs to modify, debug, or extend the
> engine without breaking it. This document was written to be the **only** thing
> you need to read end-to-end before opening any of the source files. Every
> claim cites the line or commit that backs it.

---

## Table of Contents

1. [What the engine is and is not](#1-what-the-engine-is-and-is-not)
2. [High-level architecture](#2-high-level-architecture)
3. [File map](#3-file-map)
4. [The render pipeline (end-to-end)](#4-the-render-pipeline-end-to-end)
5. [The sandboxed iframe model](#5-the-sandboxed-iframe-model)
6. [Source-cleaning pipeline (Babel prep)](#6-source-cleaning-pipeline-babel-prep)
7. [Babel transform: imports, exports, and the {flag && JSX} rewrite](#7-babel-transform-imports-exports-and-the-flag--jsx-rewrite)
8. [Library auto-detection (Recharts, Lucide, Tailwind)](#8-library-auto-detection-recharts-lucide-tailwind)
9. [The identifierHoist pipeline](#9-the-identifierhoist-pipeline)
10. [The Lucide-vs-Recharts name collision (Round 5–6)](#10-the-lucid-vs-recharts-name-collision-round-56)
11. [Post-transform safety: pre-parse + script.onerror](#11-post-transform-safety-pre-parse--scriptonerror)
12. [Auto-mount + ErrorBoundary (the BoundaryClass)](#12-auto-mount--errorboundary-the-boundaryclass)
13. [Diagnostic system v1–v9](#13-diagnostic-system-v1v9)
14. [The diagnostic kebab UI (addIframeDiagToolbar)](#14-the-diagnostic-kebab-ui-addiframediagtoolbar)
15. [Recharts bundle patches (the 3-round _intern saga)](#15-recharts-bundle-patches-the-3-round-_intern-saga)
16. [The Map shim (and why it is defensive-in-depth)](#16-the-map-shim-and-why-it-is-defensive-in-depth)
17. [The export hook (PNG / PDF / CSV / save)](#17-the-export-hook-png--pdf--csv--save)
18. [Auto-resize (postMessage 'iframe-resize')](#18-auto-resize-postmessage-iframe-resize)
19. [Public surface: what callers may rely on](#19-public-surface-what-callers-may-rely-on)
20. [Convention contract: cache-bust, BOM, no-emoji](#20-convention-contract-cache-bust-bom-no-emoji)
21. [Edge cases the engine handles silently](#21-edge-cases-the-engine-handles-silently)
22. [History of fixes (commit timeline)](#22-history-of-fixes-commit-timeline)
23. [How to add a new Recharts/Lucide name to the allowlist](#23-how-to-add-a-new-rechartslucide-name-to-the-allowlist)
24. [How to disable the diagnostic kebab](#24-how-to-disable-the-diagnostic-kebab)
25. [Failure-mode catalogue](#25-failure-mode-catalogue)
26. [Outstanding risks and "do not touch" zones](#26-outstanding-risks-and-do-not-touch-zones)
27. [Glossary](#27-glossary)

---

## 1. What the engine is and is not

**It is:**

- A **runtime JSX-to-React renderer** that runs inside a sandboxed iframe.
- Auto-mounted: the AI only writes a function component (no boilerplate, no
  imports, no createRoot calls). Everything else is injected.
- Self-contained: **no build step**. UMD bundles for React, ReactDOM, Recharts,
  Lucide, Babel Standalone, and Tailwind are loaded directly from
  `UI/visualisation_engine/libs/`.
- Heavily instrumented: 9 generations of diagnostic instrumentation (v1–v9) live
  alongside the renderer to make every blank-canvas failure debuggable from the
  parent console.

**It is not:**

- A build pipeline. No webpack, no Babel CLI, no TypeScript compilation. JSX is
  transpiled at runtime inside the iframe by `@babel/standalone`.
- A full Recharts app. Only the chart and axis components are auto-hoisted onto
  `window`; user code is expected to use them as if they were globally
  available.
- A general-purpose React sandbox. It optimises for **dashboard charts** (one
  function component per iframe, auto-mount, common-library auto-detect). It
  does **not** support React Router, multiple roots, Suspense for data fetching,
  or any kind of state persistence across renders.

---

## 2. High-level architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│  Parent SPA (business-ai-platform-v2.html)                               │
│  ────────────────────────────────────────                                │
│  visualisation_v3.js renderReact(item) ──┐                               │
│  ┌────────────────────────────────────┐ │                               │
│  │ ReactRenderer.render(item, area,   │ │                               │
│  │                       chartId)     │ │                               │
│  │   buildReactSrcdoc(jsx, chartId)   │ │                               │
│  │   iframe.srcdoc = srcdoc           │ │                               │
│  │   iframe.sandbox = allow-scripts   │ │                               │
│  │   iframe.allow = clipboard-write   │ │                               │
│  └────────────────────────────────────┘ │                               │
│                                         ▼                               │
│  postMessage listeners:                                                  │
│    'iframe-resize'         ── height auto-fit                           │
│    'react-render-snapshot' ── runtime state (Round 4)                    │
│    'react-render-fences'   ── Babel fence probes F0-F3 (Round 4)        │
│    'react-render-error'    ── componentDidCatch (Round 4)               │
│    'react-render-babel-output'  ── Babel output (Round 6)               │
│    'react-render-babel-error'   ── Babel throws (Round 6)               │
│    'react-render-pre-transform' ── cleaned JSX (Round 6)                │
│    'react-render-console-batch' ── iframe console buffer (Round 9)      │
│    'react-render-script-error'   ── new Function() parse error (H1)     │
│                                                                          │
│  addIframeActionBar() ───────────────────────────────────────────┐      │
│    ┌─────────────────────────────────────────────────────────┐   │      │
│    │ Panel button    ─ open in side panel (vizPopupManager)  │   │      │
│    │ Float button    ─ open in floating window               │   │      │
│    │ Tier-1 kebab    ─ PNG/PDF/CSV/Copy/Fullscreen/Save       │   │      │
│    │ Diag kebab      ─ Babel output, runtime snapshot, ...   │◄──┘      │
│    │   (controlled by window.__REACT_VIZ_DIAG__)             │          │
│    └─────────────────────────────────────────────────────────┘          │
│                                                                          │
│  window globals populated by the page-level sink                         │
│  (react_renderer.js installReactRendererDiagSink):                       │
│    __renderSnapshots__[chartId], __renderFences__[chartId],              │
│    __renderErrors__[chartId], __renderScriptErrors__[chartId],           │
│    __babelOutputs__[chartId], __babelErrors__[chartId],                  │
│    __preTransform__[chartId], __renderConsoleBatches__[chartId]          │
│    __lastChartRaw__, __lastChartOut__ (most-recent cross-chart pointers) │
└──────────────────────────────────────────────────────────────────────────┘
                                   │ postMessage('iframe-resize', ...)
                                   ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  Sandboxed iframe (sandbox=allow-scripts allow-forms ...)                │
│  ────────────────────────────────────────────                            │
│  srcdoc template body:                                                   │
│    <script> Pre-React Map shim v2 (Round 11) </script>                   │
│    <script src=react.production.min.js>   React 18 UMD                   │
│    <script src=react-dom.production.min.js>                              │
│    <script src=prop-types.js + Recharts.js>   (auto-injected if used)    │
│    <script src=babel.min.js>                Babel Standalone 7.24.7      │
│    <script src=lucide.min.js>               (auto-injected if used)      │
│    <style> Tailwind PLAY CDN </style>          (auto-injected if used)   │
│    <script>                                                       ───┐   │
│      installDiagConsoleCapture()  (Round 9)                           │   │
│      pre-exec diagnostic postMessage                                 │   │
│      __babelFence('F0')                                              │   │
│      window.React = React; window.ReactDOM = ReactDOM;              │   │
│      [hooks].forEach -> window[hook] = React[hook];                  │   │
│      __babelFence('F1')                                              │   │
│      rechartsSetup IIFE       (assigns 36 Recharts exports to window)│   │
│      __babelFence('F2')                                              │   │
│      __babelFence('F3')                                              │   │
│      rawSource = cleanedJSX;                                        │   │
│      out = Babel.transform(rawSource, ...).code;  (AST-strip import) │   │
│      postMessage('react-render-babel-output', ...)                   │   │
│      identifierHoist IIFE   (PascalCase -> window.X = Recharts.X    │   │
│                              or wrapped Lucide icon component)       │   │
│      pre-parse with new Function(out)  ── catches script-body SyntaxErr│  │
│      append <script>{out}</script>     ── runs the transformed code  │   │
│      post-exec snapshot IIFE   (incl. identityClashReport, Round 6)   │   │
│      BoundaryClass auto-mount    (ErrorBoundary wraps root component) │   │
│    </script>                                                         ───┘   │
│    <script> resizeScript </script>                                     │
└──────────────────────────────────────────────────────────────────────────┘
```

**Key invariant:** the parent page is **never** same-origin to the iframe
(`sandbox` lacks `allow-same-origin`). Every cross-iframe data exchange goes
through `postMessage` with `'*'` origin (anonymous, sandbox-safe).

---

## 3. File map

| Path | Lines | Role |
|---|---|---|
| `UI/visualisation_engine/react_renderer.js` | 1,959 | All the React-specific machinery: iframe construction, srcdoc template, Babel orchestration, hoist, diagnostics, export hook. |
| `UI/visualisation_engine/visualisation_v3.js` | 11,984 | The full visualisation controller. Sections 2150–2650 cover React iframes (action bar + Tier-1 + diag kebab). |
| `UI/visualisation_engine/libs/react.production.min.js` | self-hosted | React 18 UMD. Cache-bust `?v=20260727_1820`. |
| `UI/visualisation_engine/libs/react-dom.production.min.js` | self-hosted | ReactDOM 18 UMD. Cache-bust `?v=20260727_1820`. |
| `UI/visualisation_engine/libs/prop-types.js` | self-hosted | Recharts peer dep. Cache-bust `?v=20260727_1640`. |
| `UI/visualisation_engine/libs/Recharts.js` | 2 lines, 502 KB | **Self-hosted, patched** Recharts 2.x UMD. Carries 3 rounds of `_intern` guards (see §15). Cache-bust `?v=20260727_1640`. |
| `UI/visualisation_engine/libs/babel.min.js` | self-hosted | `@babel/standalone` 7.24.7. No cache-bust (it never changes). |
| `UI/visualisation_engine/libs/lucide.min.js` | (loaded from `unpkg.com/lucide@latest`) | Lucide icons. Not self-hosted because the export surface is huge and dynamic. |
| `UI/visualisation_engine/_probe_production_renderer.html` | 169 | Local-only probe that loads the production renderer and mirrors the user's failing dashboard. |
| `UI/visualisation_engine/_probe_combined_app.html` | 263 | Local probe for the multi-iframe case. |
| `UI/visualisation_engine/_probe_pie_cell.html` | 256 | Local probe for the PieChart + Cell regression. |
| `UI/visualisation_engine/_demo_real.html` | 546 | Local demo harness. |
| `UI/visualisation_engine/_demo_fix.html`, `_demo_resize.html` | misc | Older probes. |
| `UI/business-ai-platform-v2.html` | ~30,000 lines | The SPA. Cache-bust line 808: `react_renderer.js?v=20260728_1630`. Line 813: `visualisation_v3.js?v=20260728_1430`. |

---

## 4. The render pipeline (end-to-end)

The render path is **fully synchronous on the parent side** until `iframe.srcdoc = srcdoc`. Everything after that runs inside the iframe and is observable only via `postMessage`.

1. **Caller** — `visualisation_v3.js renderReact(item, contentArea, chartId)`
   (line 3787 of `visualisation_v3.js`). The `item.type` is `'react'` or
   `'execute_react'`. The `item.content` is the raw JSX from the AI.
2. **Lazy init** — `waitForRenderer('ReactRenderer', 'react_renderer.js')`
   resolves when `window.ReactRenderer` is defined.
3. **Construct** — `new window.ReactRenderer(this)` (the engine instance is
   retained as `this.vizEngine`).
4. **render()** — `ReactRenderer.render(item, contentArea, chartId)`:
   - Strips outer `<EXECUTE_REACT>` delimiters.
   - Calls `buildReactSrcdoc(jsxContent, chartId)` to assemble the full HTML
     document as a string.
   - Creates the iframe, sets `sandbox`, `allow`, CSS, `srcdoc`.
   - Attaches a `MutationObserver` to clean up the message listener when the
     iframe leaves the DOM.
   - `contentArea.appendChild(iframe)`.
5. **Inside the iframe** (after `srcdoc` parses):
   - The Map shim installs (Round 11 — see §16).
   - React, ReactDOM, hooks, optional Recharts/Lucide/Tailwind load.
   - `installDiagConsoleCapture()` patches `console.*` into a 50-entry ring
     buffer (Round 9).
   - Babel fences F0–F3 probe Babel health at each seam (Round 4).
   - `rechartsSetup` assigns 36 Recharts exports to `window`.
   - The cleaned JSX is transpiled by Babel.
   - `identifierHoist` lifts every PascalCase identifier the user referenced
     onto `window`, with Recharts-priority names taking precedence over Lucide
     (Round 5).
   - Pre-parse with `new Function(out)` catches script-body SyntaxErrors before
     they kill the iframe (Round 12, H1).
   - Appended `<script>` runs the user code; `BoundaryClass` mounts the user's
     root component inside an error boundary.
6. **Telemetry** — Every step in §5 produces `postMessage` payloads that the
   page-level sink in `installReactRendererDiagSink` writes to `window.*`
   globals.

---

## 5. The sandboxed iframe model

The iframe is created at `react_renderer.js:200–221`:

```js
iframe.sandbox = 'allow-scripts allow-forms allow-modals allow-pointer-lock allow-downloads';
// (no allow-same-origin — iframe is opaque-origin)
iframe.allow = 'clipboard-write';
```

**Why this exact sandbox string:**

| Token | Purpose |
|---|---|
| `allow-scripts` | Required to run React/Recharts/Babel. **Always present.** |
| `allow-forms` | User charts that have `<input>`/`<form>` (rare, but supported). |
| `allow-modals` | `window.alert`/`confirm`/`prompt` from chart code (rarely used). |
| `allow-pointer-lock` | Pointer-lock for fullscreen-style chart interactions. |
| `allow-downloads` | `<a download>` fallback for CSV/PDF when clipboard is unavailable. |
| **(absent)** `allow-same-origin` | **Critical.** Without this, the iframe JS is isolated from the parent. With it, a malicious chart could read the user's auth tokens from `window.parent.localStorage`. |
| **(absent)** `allow-popups` | Charts must not open arbitrary windows. |
| **(absent)** `allow-top-navigation` | Charts must not navigate the top frame. |

**Clipboard.** The Clipboard API requires an explicit Permissions Policy grant
via the `allow` attribute. Without `clipboard-write`, charts that have a "Copy
to clipboard" button silently fail. The fix is the `iframe.allow =
'clipboard-write'` line at `react_renderer.js:208`. (See memory:
[[never-reload-in-diagnostics]].)

**Cross-origin consequences.** Because the iframe is opaque-origin, **direct
DOM access from the parent is forbidden**:

- `iframe.contentWindow.React` → throws SecurityError.
- `iframe.contentDocument` → throws SecurityError.
- `window.parent.__lastChartOut__ = ...` (from inside the iframe) → silently
  fails.
- `window.parent.postMessage({...}, '*')` (from inside the iframe) → **works**.

This is why **every** diagnostic capture from inside the iframe uses
`postMessage`, and every read on the parent side reads `window.__lastXxx__`
globals that were written by the page-level sink.

---

## 6. Source-cleaning pipeline (Babel prep)

`buildReactSrcdoc()` calls a series of regex transforms on the raw JSX from the
AI before handing it to Babel. The transforms (in order) live at
`react_renderer.js:280–600`. Each is justified by a specific AI failure mode.

| Transform | Pattern | Purpose |
|---|---|---|
| Strip outer `<EXECUTE_REACT>` | `replace(/<\/?EXECUTE_REACT>/gi, '')` | The AI sometimes wraps its code in those delimiters when output is fenced. |
| Trim whitespace | `.trim()` | Cosmetic. |
| Strip `import` declarations (regex) | 14+ regex passes for: `import 'side.css'`, `import Foo from 'bar'`, `import {a,b} from 'bar'`, `import * as Foo from 'bar'`, `import default as Foo from 'bar'`, multi-line, comments-inside, `import.meta`, dynamic `import(...)`, `export * from`, `export { a, b }`, `export default`, `export class`, `export function`, `await` at top-level. | Babel Standalone's transformScriptTags does NOT strip ES module keywords; surviving keywords trigger `appendChild on 'Node': Cannot use import statement outside a module`. |
| `{flag && JSX}` rewrite | `rewriteShortCircuitJSX(src)` — walker that converts `{flag && <X/>}` to `{flag ? <X/> : null}` for 6 AI patterns (see §7). | Recharts builds its axis registry via `React.Children.toArray()`; a literal `false` child becomes a placeholder text fiber, corrupting the registry. |
| **F5 — id-shadow rename** (2026-07-29) | Pre-pass over `rawSource` that detects `([id, X])` destructuring inside `.map(...)` callbacks and rewrites every `id` reference in that callback body to `__entryId__`. Regex `(?<![.\w])id(?!\w)(?!:)` skips `node.id`, `idempotent`, and `id:` property keys. State machine skips strings (`'...'`, `"..."`, template literals), line and block comments, and counts brace depth to find the callback body. | Babel Standalone 7.24.7 has a silent scope-shadow bug: when JSX contains BOTH `<X id="..."/>` and a nested `.map(([id, X]) => {…})`, the destructured `id` parameter is dropped from the emitted scope and React throws `ReferenceError: id is not defined` at runtime. The error hides inside the iframe sandbox (the parent console sees nothing), so prompt-level workarounds ("rename your destructured id") would be required to keep React parity with Mermaid. F5 fixes it in the renderer instead. |
| `safeJsString(s)` | escape `</script` → `<\/script` for srcdoc embedding. | Without this, a literal `</script>` in the AI's JSX (e.g. inside a `<Tooltip>` or `dangerouslySetInnerHTML`) terminates the enclosing `<script>` tag mid-string. |
| Library auto-detect | `usesRecharts = /(BarChart|LineChart|PieChart|…)/.test(jsx)`; same for `usesLucide`, `usesTailwind`. | If the AI uses Recharts, the Recharts script tags are included; otherwise they're omitted to keep the iframe lean. |

**Why regex and not AST.** Babel Standalone's `transform()` only runs *after*
the source has been assigned to a `<script>` tag (or passed via `transform()`
API). We call `Babel.transform()` directly with an inline plugin that strips
import/export AST nodes — see §7 for the full story.

---

## 7. Babel transform: imports, exports, and the {flag && JSX} rewrite

```js
out = Babel.transform(rawSource, {
    presets: [['react', { runtime: 'classic' }]]
}).code;
```

**Why `runtime: 'classic'`.** It emits `React.createElement(...)` calls
instead of `import { jsx } from 'react/jsx-runtime'`. With the classic runtime
the transformed code never references an ES module, which means it survives
injection into a classic `<script>` tag (no `import` statements survive
transpile).

**AST plugin to strip imports/exports.** Lives at `react_renderer.js:1140+`
as inline source passed to `Babel.transform`. Walks the AST and removes every
`Import*Declaration` and `Export*Declaration` node. Bulletproof because it
catches shapes regex on source-text misses (`'import side.css'`, multi-line
with comments, `import.meta`, dynamic `import(...)`, `'export * from
somewhere'`).

**JSX attr array wrap fixup (Round 12).** AI emits
`<ComposedChart data=[{...}, {...}] />` where JSX grammar requires either a
quoted string or a curly-brace expression. The fixup regex at
`react_renderer.js:1196–1213` wraps the `[...]` in `{...}`:

```js
var __fixedSrc = rawSource.replace(
    /(=\\s*)\\[((?:[^\\[\\]]|\\[[^\\[\\]]*\\])*)\\]/g,
    function (_m, _eq, _arr) { return _eq + '{' + _arr + '}'; }
);
```

The doubled backslashes are deliberate — see the inline comment at line
1184–1195: JavaScript template literals silently strip unrecognized escape
sequences like `\s`, `\[`, `\]` at parse time, turning `/(=\s*)\[...\]/g`
into `/(=s*)[...]/g` at runtime — a regex that matches literal `s` and literal
`[`/`]` instead of the intended metacharacters. Doubling every `\` leaves
exactly one `\` after template literal evaluation, which is the regex source we
want.

**AST plugin for `{flag && <JSX/>}`.** Originally added in commit `df3d99a7`,
widened in `c8f81bc3` to cover 6 AI patterns, then **disabled entirely in
commit `a8cc5796`**. Rationale (verbatim from the inline comment at lines
1138–1159):

> Defensive v4 (2026-07-25): the AST plugin is DISABLED entirely. Rationale:
> the previous rewrite (cond && X -> cond ? X : null) is sound for the
> simple-identifier case the regex already covers, but its expansion to handle
> complex right-hand sides and even its 2-type JSXElement/JSXFragment
> restriction still produced SyntaxError-at-script-time output for at least
> one real-world chart pattern that bypassed every locally-tested case. The
> iframe would render blank with no recoverable state because new Function()
> (function-body parse) is more permissive than the <script> parser the
> browser actually uses to execute the code (script-body parse). Without a
> plugin, Babel.transform only emits standard React.createElement output that
> the <script> parser is guaranteed to accept.

**Trade-off:** the `{complexCond && (<JSX/>)}` pattern reverts to the original
Recharts bug (`a.set is not a function` / `i.set is not a function` on axis
registry falsy-placeholder). The user will see the chart render with a visible
runtime error in DevTools instead of a completely blank iframe — a much
better failure mode than blank-canvas. The **simple-identifier regex** at
`react_renderer.js:300+` still handles `{flag && (<JSX/>)}` which is the most
common Recharts offender.

---

## 8. Library auto-detection (Recharts, Lucide, Tailwind)

Three regex detectors decide what to inject:

```js
const usesRecharts = /(BarChart|LineChart|PieChart|...)/.test(jsx);
const usesLucide   = /(lucide|<[A-Z][a-z]+Icon\b)/.test(jsx);
const usesTailwind = /(?:className=)["'`][^"'`]*\b(?:flex|grid|p-\d|m-\d|text-(?:xs|sm|base|lg|xl)|bg-(?:blue|red|...))\b/.test(jsx);
```

The Tailwind detector at `react_renderer.js:680+` was hardened in `02e113c4`
to cover all 4 className forms (`"..."`, `'...'`, `` `...` ``, `{...}`) and
to ignore non-className strings that happen to contain the word "flex".

**Recharts setup** (the `rechartsSetup` IIFE, lines 663–709):

```js
(function rechartsSetup() {
    function assign(name) {
        if (window.Recharts && window.Recharts[name]) {
            window[name] = window.Recharts[name];
        }
    }
    var names = [ 'BarChart', 'LineChart', 'PieChart', ..., /* 36 entries */ ];
    // 3-second poll because the Recharts UMD exposes window.Recharts
    // asynchronously after prop-types loads. Without the poll, window[name] = ...
    // may run before Recharts is attached and silently miss every component.
    var deadline = Date.now() + 3000;
    var i = 0;
    (function tick() {
        if (window.Recharts) {
            names.forEach(assign);
            return;
        }
        if (Date.now() > deadline) return;
        setTimeout(tick, 50);
    })();
})();
```

**Lucide.** When `usesLucide` is true, the iframe injects `<script
src="https://unpkg.com/lucide@latest">`. Lucide is the only library that
ships a single UMD with every icon — self-hosting it is impractical.

**Tailwind.** When `usesTailwind` is true, the iframe injects
`<link rel="stylesheet" href="https://cdn.tailwindcss.com">` (the PLAY CDN).
The PLAY CDN injects styles into a bare `<style>` element with no
`[data-tailwind]` marker; the snapshot detects Tailwind by scanning all
`<style>` elements for `.bg-blue-500` or `.flex { display: flex }` (fixed in
commit `02e113c4` — the previous selector returned false-negatives every
render).

---

## 9. The identifierHoist pipeline

`identifierHoist` is the IIFE that lifts every PascalCase identifier the user
referenced in their JSX onto `window`, so the transformed source can call
`BarChart` instead of `Recharts.BarChart`. Lives at
`react_renderer.js:748–851`.

**Algorithm (two-pass):**

```js
(function identifierHoist() {
    var lucide = window.lucide;
    var recharts = window.Recharts;

    function makeIconComponent(name, descriptor) {
        // descriptor is a [tag, attrs] array — Lucide's export shape.
        // Wrap as a React component that returns an <svg {...attrs}/>.
        return function IconComponent(props) {
            return React.createElement(descriptor[0],
                Object.assign({}, descriptor[1], props));
        };
    }

    // First pass: identifiers the user REFERENCED, with priority source swap.
    var referenced = new Set(/* every <Ident> and Ident( in rawSource */);
    referenced.forEach(function (name) {
        if (RECHARTS_PRIORITY_NAMES.indexOf(name) !== -1 && recharts && recharts[name]) {
            window[name] = recharts[name];      // Recharts wins
        } else if (lucide && lucide[name]) {
            window[name] = makeIconComponent(name, lucide[name]);  // wrapped icon
        } else if (recharts && recharts[name]) {
            window[name] = recharts[name];
        }
    });

    // Second pass: every Lucide key (skipping priority names).
    // This is what makes <Bar dataKey="..." /> style code work even if the user
    // didn't reference <Bar> directly but used <BarChart><Bar/></BarChart>.
    Object.keys(lucide || {}).forEach(function (name) {
        if (RECHARTS_PRIORITY_NAMES.indexOf(name) !== -1) return;  // skip
        window[name] = makeIconComponent(name, lucide[name]);
    });
})();
```

**The `identifierRe` walker** at `react_renderer.js:721`:

```js
var identifierRe = /<([A-Z][A-Za-z0-9_]*)\b|\b([A-Z][A-Za-z0-9_]*)\(/g;
```

This regex captures every JSX element start (`<PascalCase`) and every PascalCase
function call (`PascalCase(`). Combined into a `Set`, it becomes the "what does
the user actually use?" list.

**Why two passes?** First pass handles explicit references; second pass handles
implicit references (e.g. `<Bar dataKey="..."/>` inside `<BarChart>` — the
user did not write `<Bar>` directly, but the JSX grammar forces the hoist to
provide it). The skip-priority-names guard on the second pass is what prevents
the Lucide icon from clobbering Recharts — see §10.

---

## 10. The Lucide-vs-Recharts name collision (Round 5–6)

**The bug.** Lucide exports icons at the top level with the same names as many
Recharts components: `PieChart`, `BarChart`, `LineChart`, `Brush`, `Bar`,
`Area`, `Line`, `Pie`, `Cell`, `ComposedChart`, etc. (36 names in total.) When
the identifier hoist wraps a Lucide array descriptor as a React component, the
wrapped function **renders a giant monochrome Lucide-shaped SVG icon** instead
of a chart. Recognisable signatures: pie → wedge, bar → three vertical bars,
line → zig-zag.

**Why the snapshot lied.** `typeof window.PieChart === 'function'` cannot
distinguish the wrapped Lucide icon from the real Recharts component. Both
are functions, so the snapshot showed all expected names as `'function'` and
the bug hid until visual confirmation.

**The fix (commit `bf6b3454`, Round 5).** Add `RECHARTS_PRIORITY_NAMES`
constant at `react_renderer.js:738`. First pass swaps source order
(`[R, L]` for priority names); second pass skips priority names entirely.

**The mirror rule (critical).** `RECHARTS_PRIORITY_NAMES` at line 738 MUST be
an exact mirror (same order, same entries) of the `names` list inside
`rechartsSetup` at line 663. Today both have 36 entries, identical. If you add
a new Recharts chart type to `rechartsSetup`, add it to
`RECHARTS_PRIORITY_NAMES` in the same position. A future lint check could
enforce this; for now it's a manual invariant. (See §23 for the procedure.)

**The Round 6 verification (`bbb60bad`).** `identityClashReport` field in the
post-exec snapshot walks the same 36 names and emits:

```js
{
    clashCount: 0,             // how many names are wrapped Lucide not Recharts
    total: 36,                 // how many names were checked
    rows: [
        { name: 'PieChart', hasFn: true, matchesRecharts: true  },
        { name: 'Bar',      hasFn: true, matchesRecharts: true  },
        { name: 'XAxis',    hasFn: true, matchesRecharts: true  },
        ...
    ]
}
```

The check is identity (`window[name] === window.Recharts[name]`), not typeof.
`hasFn: true` AND `matchesRecharts: false` is the signature of a clash. See
`REACT_RENDERER_LUCIDE_TROUBLESHOOTING_2026-07-22.md` §15 for the full
postmortem.

---

## 11. Post-transform safety: pre-parse + script.onerror

`react_renderer.js:1397–1469` is the post-transform safety net. Two layers:

**Layer 1: `new Function(out)`** — Pre-parse the Babel output as a function
body. `new Function()` uses **function-body parse**, which is *more permissive*
than the `<script>` parser that actually runs the code (script-body parse).
If `new Function()` throws, the catch paints a red diagnostic in the iframe,
posts `react-render-script-error` to the parent, and returns. The user sees
an actionable error instead of a blank canvas.

**Layer 2: `script.onerror`** — Backup for the rare case where the two parsers
disagree (strict-mode-only constructs, top-level await, etc.). If the appended
`<script>` fires an `error` event, the handler paints a red diagnostic, posts
`react-render-script-error` with `source: 'script-onerror'`, and returns.

**The bug this defends against (H1, 2026-07-26).** V8 fires parse errors on
appended `<script>` as `error` events, not exceptions — the catch block could
not see them, leaving the iframe blank. This was the most common production
failure mode for two days before the pre-parse + `onerror` net was added.

---

## 12. Auto-mount + ErrorBoundary (the BoundaryClass)

After the transformed script runs, the renderer tries to find the user's root
component (`react_renderer.js:1580–1852`):

```js
var rootComponent =
    typeof window.App       !== 'undefined' ? window.App       :
    typeof window.Component !== 'undefined' ? window.Component :
    typeof window.Dashboard !== 'undefined' ? window.Dashboard :
    null;
```

If found, it mounts inside `BoundaryClass` — a hand-rolled error boundary:

```js
function BoundaryClass() {}
BoundaryClass.prototype = Object.create(window.React.Component.prototype);
BoundaryClass.prototype.constructor = BoundaryClass;
BoundaryClass.prototype.render = function () {
    if (this.state && this.state.err) {
        // Render a yellow hint panel for the three known Recharts internal
        // bugs (see below), or a red panel for everything else.
    }
    return window.React.createElement(rootComponent, null);
};
BoundaryClass.getDerivedStateFromError = function (err) { return { err: err }; };
BoundaryClass.prototype.componentDidCatch = function (err, info) { /* postMessage */ };
```

**Why prototype assignment, not ES2015 `class extends`?** Babel Standalone does
not reliably transpile class fields across all configs. Prototype chains are
bulletproof. (See `react_renderer.js:1596–1598` inline comment.)

**The three yellow hint panels:**

1. **`t.has is not a function` + ComposedChart source.** Verified Recharts
   bug: class `vn` / class `On` internal Map extension dereferences a missing
   `_intern` slot during domain merging. (Offets 121494 / 122031 / 122831 on
   2026-07-24.)
2. **`a.set is not a function` + `Recharts.` in source.** Companion bug:
   react-dom's child-map builder `d()` (function inside `mapIntoArray`)
   throws because Recharts internal Map extension has no `_intern` slot.
   Verified 2026-07-26 with a single `<BarChart><Bar/></BarChart>` (no
   ComposedChart, no multi-axis).
3. **`a.set is not a function` + ComposedChart source.** React commit-phase
   corruption from a `LogicalExpression` JSX child of `<ComposedChart>` that
   the regex rewriter missed.

Each panel renders an **actionable workaround**: "Ask for the dashboard as
separate single-axis charts" with an example prompt the user can paste back to
the AI.

---

## 13. Diagnostic system v1–v9

The renderer ships nine generations of diagnostic instrumentation. Each one
addresses a specific class of bug that the previous generation could not
diagnose. They are cumulative — all are live.

| Gen | Date | Bug it diagnosed | What it captures |
|---|---|---|---|
| **v1** | 2026-07-22 | First iframe scaffolding — Tier-1 export hook added. | `iframe-svg`, `iframe-data` postMessages. |
| **v2** | 2026-07-22 | Tier-1 toolbar (PNG / PDF / CSV / copy / fullscreen / save). | `addIframeTier1Toolbar` at `visualisation_v3.js:2242`. |
| **v3** | 2026-07-23 | Babel fences F0–F3 — bracket Babel setup steps to find which seam corrupts the plugin cache. (Superseded conceptually by F5 — the id-shadow pre-pass — but F0–F3 still run as Babel-health probes.) | `react-render-fences` postMessage. |
| **v4** | 2026-07-23 | Post-exec snapshot — "transform succeeded but iframe blank" class of bug. | `react-render-snapshot` postMessage. |
| **v5** | 2026-07-25 | Parent-side raw capture. Even when the iframe script dies, parent has both inputs (raw JSX + Babel output) synchronously. | `window.parent.__lastChartRaw__`, `window.parent.__lastChartOut__`. |
| **v6** | 2026-07-25 | In-iframe `__lastChartRaw__` mirror. Same data on `window.parent` inside the iframe (often fails silently in srcdoc sandbox). | n/a — superseded by v7. |
| **v7** | 2026-07-26 | Entry-point log on `buildReactSrcdoc`. Catches the case where the function itself crashes before the iframe is even created. | `console.log` at line 200. |
| **v8** | 2026-07-26 | Cross-origin-safe Babel output. `postMessage` survives srcdoc opacity. Four messages: `react-render-babel-output`, `react-render-babel-error`, `react-render-pre-transform`, `react-render-script-error`. | All four postMessages populated. |
| **v9** | 2026-07-27 | Iframe console capture. 50-entry ring buffer of `console.{log,warn,error,info,debug}`, forwarded to the real `console.*` (no double-log). Parent requests via `react-render-console-request`; iframe replies `react-render-console-batch`. | `window.__DIAG_CONSOLE_BUFFER__()` (inside iframe). `window.__renderConsoleBatches__[chartId]` (parent). |
| **v10** | 2026-07-29 | F5 id-shadow rename counter. Surfaces the F5 pre-pass outcome on every render so the diag kebab can show how many destructured `[id, X]` bindings were rewritten — even on success, even when Babel throws *after* F5 rewrote the source. | `window.parent.__lastIdShadowFixApplied`, `window.parent.__lastIdShadowFixRenames`. Same fields on the `react-render-babel-error` postMessage payload. |

**Plus three later rounds:**

| Round | Commit | What it added |
|---|---|---|
| 5 (diag kebab) | `ef578137` | The 8-item diag popover in `addIframeActionBar()`. |
| 6 (identity check) | `bbb60bad` | `identityClashReport` field in post-exec snapshot. |
| 7–8 (diag UX) | `765edcaa`, `521ecd24`, `abac1918` | Refresh buttons on open, chartId fallback, labeled paste. |
| 9 (Tailwind) | `02e113c4` | Tailwind detector covers 4 className forms. |
| 10 (Map shim) | `dfc5ffc7` | `Map.prototype.set` shim before react-dom loads. |
| 11 (Map shim v2) | `910c05fe` | Accessor properties defeat late Map corruption. |
| 12 (regex double-escape) | `72855b99` | Backslashes survive template-literal embedding. |
| 13 (srcdoc escaping) | `d3f516bc`, `3e69f121`, `f0caa3be` | `</script>`, backticks, apostrophes all escaped. |

---

## 14. The diagnostic kebab UI (addIframeDiagToolbar)

`visualisation_v3.js:2394–2650`. A separate popover next to the Tier-1 kebab
in the iframe action bar. **Opt-out:** `window.__REACT_VIZ_DIAG__ = false`
removes the trigger button.

**Layout** (8 simple items + 2 composites):

| # | Label | Source |
|---|---|---|
| 1 | Babel output | `window.__babelOutputs__[chartId].babelOut` |
| 2 | Cleaned JSX (raw) | `window.__preTransform__[chartId].rawSource` |
| 3 | Runtime snapshot | `window.__renderSnapshots__[chartId]` |
| 4 | Babel fences (F0–F3) | `window.__renderFences__[chartId]` |
| 5 | Runtime errors | `window.__renderErrors__[chartId]` (componentDidCatch) |
| 6 | Babel transform errors | `window.__babelErrors__[chartId]` |
| 7 | Script-parse errors | `window.__renderScriptErrors__[chartId]` |
| 8 | Cache stats + iframe console | composite (5s timeout) |
| — | Copy ALL diagnostics | aggregate all 8 with labeled paste |

Each item shows `(N bytes · captured HH:MM:SS)` and is **disabled with "no data"**
when its entry is empty. The `_pick()` helper prefers the current chartId but
falls back to the most-recent key.

**Refresh on open** (`refreshButtons()` at `visualisation_v3.js:2554`):
the initial popover.innerHTML pass bakes in the disabled state at creation
time — if the iframe's diagnostic postMessage fires AFTER the kebab is wired
but BEFORE the user opens it (the common case), the user would see permanent
"no data" buttons. Refresh on every open.

**Clipboard** (`_diagCopyText` at `visualisation_v3.js:2695+`):
`navigator.clipboard.writeText()` with `document.execCommand('copy')` fallback
for unfocused windows.

**Labeled paste format** (`_diagLabelWrap` at `visualisation_v3.js:2673+`):
each copy is wrapped in a self-documenting header:

```
=== AI Agents Visualization Diagnostic ===
chartId: <id>
capturedAt: <ISO>
section: <label>
source: <where>
bytes: <N>
=========================================

<raw content>

=== /<label> ===
```

---

## 15. Recharts bundle patches (the 3-round _intern saga)

`UI/visualisation_engine/libs/Recharts.js` is **not** the upstream UMD. It is
the UMD with three rounds of surgical guards layered onto it. The file is 2
lines, 502 KB; the only way to read it is via `git log --follow` or the
patches themselves.

**Why patched.** Recharts 2.x ships with internal `Map` subclasses (class `vn`
/ `bn` / `gn` / `mn`) that dereference a missing `_intern` slot during domain
merging. Result: `t.has is not a function`, `a.set is not a function`,
`i.set is not a function`. These throw deep inside Recharts' internals and
Recharts has not fixed them in the version we ship. The patched bundle
guards the missing slot at three levels.

**Patch round 1 — `8c50daeb` (2026-07-22).** Add `mn()` normalizer: if the
incoming data array has no `_intern` field, synthesise one before any
internal Map lookup. Verified at offset 121494 of the bundle.

**Patch round 2 — `25c27cc1` (2026-07-23).** Extend the same pattern to
`bn()` and `gn()` — Recharts' series-child registration helpers. Both throw
the same class of error.

**Patch round 3 — `20e6994d` (2026-07-23).** Defense-in-depth: wrap
`vn.prototype.{get,has,set,delete}` with guards that fall back to the
native `Map.prototype` operations when `_intern` is missing.

**Net effect.** Single-axis LineChart, BarChart, PieChart, AreaChart, and
ComposedChart-with-single-axis all render. ComposedChart-with-multi-axis
still triggers `t.has` for the chart with multiple YAxes (Round 7 unfixed,
workaround: render as separate single-axis charts — see §12).

**Important invariant (memory [[recharts-patched-bundle-warning]]):** replacing
this file with a fresh UMD silently re-introduces `t.has is not a function`.
The 7 surgical `_intern` guards in the bundle are load-bearing. If you
regenerate the bundle, **either re-apply the patches or do not ship**.

---

## 16. The Map shim (and why it is defensive-in-depth)

`react_renderer.js:898–912` installs a `Map.prototype` shim **before** React
loads. The shim has been through two versions.

**v1 (`dfc5ffc7`, 2026-07-23).** Restored `Map.prototype.set` if it was
broken AT iframe load. Useless — the corruption happens between mount and
the first hover/scroll re-render.

**v2 (`910c05fe`, 2026-07-23).** Unconditionally installs an accessor
(getter/setter) pair on `Map.prototype.{set,get,has,delete}`. The getter
always returns the saved native (or a `__m_<key>` storage fallback if the
native was already broken at load), and the silent setter absorbs any later
`Map.prototype.set = somethingElse` assignment. Also wraps `window.Map` with
an accessor so reassigning the global Map constructor is absorbed too.
Survives polyfill overrides that happen AFTER iframe load.

**Why this is needed.** react-dom 18.3.1 commit-phase child-fiber mapper
(function `d` inside `Dh`) does `for(a=new Map;...) a.set(b.index,b)`. If
`Map.prototype.set` is missing or non-callable, every re-render crashes with
`a.set is not a function` deep in react-dom. The shim guarantees the
function exists and is callable no matter what happens later.

**What it does NOT defend against.** If the user code itself assigns to
`Map.prototype.set`, the shim's setter silently absorbs it (the new value
goes nowhere). This is intentional — losing the override is better than
crashing every re-render. If a future Recharts version genuinely needs to
override `Map.prototype.set`, this shim must be revisited.

---

## 17. The export hook (PNG / PDF / CSV / save)

`react_renderer.js:1898–1956` installs `window.__REACT_RENDERER__` as an
additive postMessage API. The protocol:

```
parent → child : { type: 'iframe-export-svg',  id: <chartId> }
parent → child : { type: 'iframe-export-data', id: <chartId> }
child  → parent: { type: 'iframe-svg',  id: <chartId>, svg: <string|null> }
child  → parent: { type: 'iframe-data', id: <chartId>, payload: <obj> }
```

**Default behaviour.** When the child receives `iframe-export-svg`, it
serialises the first `<svg>` it finds via `XMLSerializer`. When it receives
`iframe-export-data`, it returns `window.__EXPORT_DATA__` (or `{error: 'no
__EXPORT_DATA__ set'}`).

**Opt-in custom handlers.** Child code can register a custom export via
`window.__EXPORT_HANDLER__ = { svg: function() { ... }, data: function() {
... } }`. Used by Recharts-heavy charts that need to manually serialise the
SVG with the correct viewBox.

**Idempotency guard.** `if (window.__REACT_RENDERER__) return;` at line 1899
prevents double-installation if `react_renderer.js` is loaded twice (e.g. by
a hot-reload during development).

**Chart-id scoping.** The hook stores `chartId` at install time and discards
any postMessage whose `id` doesn't match. This is what allows multiple
iframes to coexist with their own kebab without cross-talk.

---

## 18. Auto-resize (postMessage 'iframe-resize')

Every error path and every successful mount posts
`{ type: 'iframe-resize', id: <chartId>, height: <N> }` to the parent. The
parent listener (`react_renderer.js:224–251`) clamps the height to
`[200, 900]` and updates the iframe's CSS height. This is how error panels
automatically grow to fit their content instead of overflowing.

The clamp range prevents pathological charts from hijacking the viewport.

---

## 19. Public surface: what callers may rely on

**Parent-side globals that any code in the SPA may read:**

| Global | Type | Read when |
|---|---|---|
| `window.ReactRenderer` | constructor | After `react_renderer.js` loads (`defer`). |
| `window.__renderSnapshots__[chartId]` | runtime snapshot object | After iframe posts `react-render-snapshot`. |
| `window.__renderFences__[chartId]` | array of `{label, ok, err?}` | After iframe posts `react-render-fences`. |
| `window.__renderErrors__[chartId]` | `{id, message, stack, rawSource}` | After iframe posts `react-render-error`. |
| `window.__renderScriptErrors__[chartId]` | `{id, source, message, outTail?}` | After iframe posts `react-render-script-error`. |
| `window.__babelOutputs__[chartId]` | `{babelOut, babelOutLen, rawSource, rawSourceLen, babelFences}` | After iframe posts `react-render-babel-output`. |
| `window.__babelErrors__[chartId]` | `{errorMessage, rawSource, rawSourceLen, babelFences}` | After iframe posts `react-render-babel-error`. |
| `window.__preTransform__[chartId]` | `{rawSource, rawSourceLen, fencesAtStart}` | After iframe posts `react-render-pre-transform`. |
| `window.__renderConsoleBatches__[chartId]` | `{entries: [{t, level, msg}, ...]}` | After iframe posts `react-render-console-batch`. |
| `window.__lastRenderSnapshotId` etc. | string (most-recent chartId) | Same as above; convenience pointer. |
| `window.__lastChartRaw__`, `window.__lastChartOut__` | string | Most-recent capture; cross-chart. |
| `window.__lastBadJsx`, `window.__lastBadMsg` etc. | string / object | Most-recent Babel failure. |
| `window.__lastFailingSource` | string (4KB head of raw JSX) | Most-recent runtime failure. |

**Iframe-side globals that user code may rely on (after auto-mount):**

| Global | Type | Set by |
|---|---|---|
| `window.React` | React 18 namespace | `react_renderer.js:1055` |
| `window.ReactDOM` | ReactDOM 18 namespace | `react_renderer.js:1056` |
| `window.useState`, `window.useEffect`, etc. (10 hooks) | function | `react_renderer.js:1057–1063` |
| `window.Fragment` | React.Fragment | `react_renderer.js:1064` |
| `window.Recharts` | Recharts namespace | Recharts UMD |
| `window.<ChartName>` (36 names) | function | `rechartsSetup` IIFE + `identifierHoist` IIFE |
| `window.lucide` | icon map | Lucide UMD |
| `window.<IconName>` (every Lucide key) | wrapped React component | `identifierHoist` IIFE (skipping 36 priority names) |
| `window.__EXPORT_HANDLER__` | `{svg?, data?}` | opt-in by user code |
| `window.__EXPORT_DATA__` | object | opt-in by user code |
| `window.__DIAG_CONSOLE_BUFFER__` | function returning array | Round 9 IIFE |

**postMessage types that may be safely sent to the parent:**

```
'iframe-resize', 'iframe-svg', 'iframe-data'
'react-render-snapshot', 'react-render-fences', 'react-render-error',
'react-render-script-error', 'react-render-babel-output',
'react-render-babel-error', 'react-render-pre-transform',
'react-render-console-batch', 'react-render-diagnostic'
```

---

## 20. Convention contract: cache-bust, BOM, no-emoji

**Cache-bust.** Every script tag that loads a renderer file uses
`?v=YYYYMMDD_HHMM`. Current values:

| File | Cache-bust |
|---|---|
| `react_renderer.js` | `?v=20260728_1630` |
| `visualisation_v3.js` | `?v=20260728_1430` |
| `react.production.min.js` | `?v=20260727_1820` |
| `react-dom.production.min.js` | `?v=20260727_1820` |
| `prop-types.js`, `Recharts.js` | `?v=20260727_1640` |
| `babel.min.js` | none (never changes) |

Bump both `react_renderer.js` and `visualisation_v3.js` whenever the renderer
contract changes (a new postMessage type, a new global). Bump the libs only
when the bundle itself changes.

**UTF-8 no BOM.** Every renderer file must be BOM-free. `.vscode/fix-bom.ps1`
runs before every commit. PowerShell-based edits routinely re-introduce BOM —
run the fix script before declaring "done."

**No emoji in source literals.** UI titles and labels use plain text. Emoji
are acceptable in tooltips only. CLAUDE.md §5 mandates this — the renderer's
error panels use `String.fromCharCode(9888)` (= ⚠) instead of a literal `⚠`
in the JSX.

---

## 21. Edge cases the engine handles silently

These are the "no, you do not need to special-case that" assertions:

| Case | How it's handled |
|---|---|
| AI emits literal `</script>` in their JSX (inside a `<Tooltip>`) | `safeJsString()` escapes it to `<\/script` (line 282). |
| AI emits bare-array JSX attribute (`data=[…]`) | The 2026-07-28 regex wrap fixup turns it into `data={[…]}` (line 1196). |
| AI emits `{flag && (<X/>)}` inside `<ComposedChart>` | The simple-identifier regex (line 300+) rewrites it to `{flag ? (<X/>) : null}`. |
| AI emits `{complexCond && (<X/>)}` inside `<ComposedChart>` | **Not** rewritten. May trigger Recharts internal bug. The yellow hint panel in `BoundaryClass` surfaces a workaround. |
| `Map.prototype.set` gets corrupted mid-session | The v2 Map shim's silent setter absorbs the assignment. |
| Babel's plugin cache gets corrupted by a previous `Babel.transform` call | Cannot be detected at runtime; the F3 fence catches it. If F3 fails, the diagnostic panel shows "F3 failed". |
| Recharts UMD exposes `window.Recharts` asynchronously | `rechartsSetup`'s 3-second poll waits for it. |
| User code references an identifier not in Recharts, Lucide, or any library | `<Ident>` becomes a React DOM warning. The chart renders the React error in the iframe. |
| User code defines `App`, `Component`, and `Dashboard` | `App` wins. |
| User code defines none of them | The root `#root` div is painted with a red `<p>` asking the user to define a root component. |
| Same JSX is rendered twice (same chartId) | The previous iframe is overwritten. The postMessage listener is cleaned up by the `MutationObserver` (line 255–261). |
| Sandboxed iframe hits a script-body SyntaxError | The pre-parse `new Function(out)` catches it, paints a red diagnostic, posts `react-render-script-error`, returns. The user sees the error in DevTools. |

---

## 22. History of fixes (commit timeline)

From May 2026 to present (2026-07-28). Only commits affecting
`UI/visualisation_engine/` and the cache-bust lines on the SPA HTML.

| Commit | Date | Round | Subject |
|---|---|---|---|
| `9ff3fc0b` | 2026-07-22 | (early) | move identifierHoist IIFE after Babel.transform |
| `4f2fa0ab` | 2026-07-22 | (early) | convert {X && JSX} to ternary for ComposedChart compat |
| `d185788d` | 2026-07-22 | (early) | capture rawSource in snapshot + error postMessage |
| `0c8e9252` | 2026-07-22 | (early) | capture rawSourceTail4k in snapshot for chart-JSX visibility |
| `df3d99a7` | 2026-07-22 | (early) | transform {cond && <JSX/>} to ternary for Recharts compat |
| `17847ca0` | 2026-07-22 | (early) | graceful fallback for Recharts ComposedChart bug |
| `8c50daeb` | 2026-07-22 | Recharts R1 | defensively guard Recharts mn() against missing _intern |
| `cce2ddcf` | 2026-07-22 | (Mermaid) | defensive fallback render when Mermaid fullscreen finds no inline SVG |
| `25c27cc1` | 2026-07-23 | Recharts R2 | patch bn() + gn() to close Recharts series-child registration |
| `20e6994d` | 2026-07-23 | Recharts R3 | defense-in-depth patch on vn.prototype.{get,has,set,delete} |
| `e3940b89` | 2026-07-23 | Recharts setup | poll for window.Recharts before assigning components |
| `630bf8f4` | 2026-07-23 | Recharts patch | repair gn normalizer parens in patched Recharts.js |
| `d1ac2f44` | 2026-07-23 | (Mermaid) | drop empty .mermaid div before showing deferred placeholder |
| `af1cd2a4` | 2026-07-23 | (Mermaid) | destructure mermaid.render in fullscreen fallback |
| `8db96fb3` | 2026-07-23 | (Mermaid) | rename fallback render vars + log mermaid result shape |
| `6bc6314a` | 2026-07-23 | (streaming) | use pkg.position for fence-guard check |
| `b4dd12ac` | 2026-07-23 | (early) | rewrite cond && X for all renderable types + ErrorBoundary fallback |
| `27d6e3e5` | 2026-07-23 | (early) | revert recharts plugin to 2-type + add parse-check safety net |
| `92bf2a84` | 2026-07-23 | (early) | remove backticks from JS comment that broke renderer load |
| `a8cc5796` | 2026-07-24 | AST plugin disable | disable AST plugin that produced script-body SyntaxError |
| `6fed9886` | 2026-07-24 | diag v5 | unconditionally capture raw + babel output on parent |
| `c6957bb0` | 2026-07-24 | diag v6 | capture raw chart source on parent BEFORE srcdoc |
| `77e0d5f2` | 2026-07-24 | diag v7 | add v7 unconditional entry-point log to buildReactSrcdoc |
| `c14b57b0` | 2026-07-25 | diag v8 | v8 cross-origin-safe Babel output capture |
| `77abfb76` | 2026-07-25 | hardening | react-renderer hardening + popup sandbox/sanitisation |
| `f0caa3be` | 2026-07-25 | srcdoc | escape backticks inside srcdoc template literal comment |
| `3e69f121` | 2026-07-25 | srcdoc | double-escape apostrophes in srcdoc string + harden error banners |
| `d3f516bc` | 2026-07-25 | srcdoc | escape `</script>` in srcdoc strings + surface a.set Recharts bug |
| `02e113c4` | 2026-07-25 | diag v9 tailwind | detect Tailwind in all 4 className forms + accurate style-injected snapshot |
| `c8f81bc3` | 2026-07-26 | short-circuit widen | widen {flag && JSX} rewrite to cover 6 common AI chart patterns |
| `ef578137` | 2026-07-26 | diag kebab | diag kebab menu in React iframe action bar |
| `521ecd24` | 2026-07-26 | diag kebab | diag popover chartId fallback + harden Recharts _intern guard |
| `765edcaa` | 2026-07-26 | diag UX | refresh diag popover buttons on every open |
| `dfc5ffc7` | 2026-07-26 | Map shim v1 | shim Map.prototype.set before react-dom loads |
| `910c05fe` | 2026-07-26 | Map shim v2 | shim v2 — accessor properties defeat late Map corruption |
| `abac1918` | 2026-07-26 | diag UX | label diag copies with source + add 'Copy ALL' 9th button |
| `72855b99` | 2026-07-26 | regex escape | double-escape fixup regex so backslashes survive srcdoc embedding |
| `bf6b3454` | 2026-07-26 | Round 5 (hoist) | resolve Lucide/Recharts name collisions in identifierHoist |
| `bbb60bad` | 2026-07-28 | Round 6 (verify) | identity-check snapshot detects Lucide-vs-Recharts collisions |
| `TBD` | 2026-07-29 | F5 (id shadow) | pre-pass renames destructured `([id, X]) => {…}` callbacks to `__entryId__`; fixes Babel Standalone scope-shadow that hid `ReferenceError: id is not defined` inside the iframe sandbox. Surface via `window.parent.__lastIdShadowFixRenames`. |

---

## 23. How to add a new Recharts/Lucide name to the allowlist

When you upgrade Recharts to a new major version (or Lucide to a new bundle),
audit the new icon/component exports for name overlap. If a new collision is
found:

1. Add the new name to the `names` array inside `rechartsSetup` at
   `react_renderer.js:663`. Same order as the canonical chart-type list in
   Recharts' documentation.
2. Add the same name to `RECHARTS_PRIORITY_NAMES` at `react_renderer.js:738`,
   in the **same position**.
3. Verify with the post-deploy smoke test:
   - Render a chart that uses the new name.
   - Check `window.__renderSnapshots__[chartId].identityClashReport.rows` for
     the new name. `matchesRecharts: true` is required.
4. Bump cache-busters: `business-ai-platform-v2.html:808` (the `<script
   src="visualisation_engine/react_renderer.js?v=…">` tag).
5. Update `REACT_VISUALISATION_MASTER_DOCUMENT.md` §10 to reflect the new count.

If a future lint check enforces the mirror invariant, it would compare the
arrays' `.length` and check that `Array.from(new Set([...names, ...priority]))`
equals `names` (no extras, no missing).

---

## 24. How to disable the diagnostic kebab

**At runtime (no deploy).** In DevTools console of the parent page:

```js
window.__REACT_VIZ_DIAG__ = false;
location.reload();  // or just open a new chart
```

The button stops appearing in newly rendered iframes. Existing ones keep it
until they re-render.

**Permanent.** Single commit removing:

1. The 4th button HTML in `addIframeActionBar` at `visualisation_v3.js:2189`.
2. The `addIframeDiagToolbar()` call at `visualisation_v3.js:2221`.
3. The `addIframeDiagToolbar()` function definition at `visualisation_v3.js:2394–2650`.
4. The `_diagCopyText`, `_diagCopyComposite`, `_diagCopyAll`,
   `_diagLabelWrap` helpers (around lines 2670–2900).
5. The console-capture IIFE in `react_renderer.js:966–1009`.
6. The 2 sink cases (`react-render-console-batch`) in
   `installReactRendererDiagSink` (`react_renderer.js:156–175`).

(Or `git revert` the diagnostic commit — multi-file revert.)

---

## 25. Failure-mode catalogue

This is the catalogue of every blank-canvas / blank-error symptom that has
been observed in production, with the diagnostic that surfaces it and the fix
that resolves it.

| Symptom | Diagnostic | Root cause | Fix |
|---|---|---|---|
| Iframe blank, no console error | `__renderSnapshots__[chartId].rootElChildren === 0` | User forgot to define root component | Yellow panel asks for App/Component/Dashboard |
| Iframe blank, no console error, fence F3 fails | `__renderFences__[chartId][3].ok === false` | Babel plugin cache corrupted | Run identifyHoist earlier (fixed 2026-07-23) |
| Chart renders giant monochrome icon | `__renderSnapshots__[chartId].identityClashReport.clashCount > 0` | Lucide clobbered Recharts | Reorder hoist priority (Round 5 fix) |
| `t.has is not a function` | Runtime error in `__renderErrors__[chartId]` | Multi-axis ComposedChart | Yellow hint panel + workaround |
| `a.set is not a function` | Runtime error in `__renderErrors__[chartId]` | Recharts internal Map extension | Yellow hint panel + workaround |
| Babel throws on AI JSX | `__babelErrors__[chartId]` | AI syntax error | Red panel with Babel message + first 800 chars of source |
| `new Function(out)` throws | `__renderScriptErrors__[chartId].source === 'pre-parse'` | Babel output invalid in script-body parse | Red panel with parse message |
| Iframe script dies | `__renderScriptErrors__[chartId].source === 'script-onerror'` | V8 strict-mode-only construct | Red panel + parent fallback |
| `import` keyword in user JSX | Babel throws "Cannot use import statement outside a module" | AST plugin missed it | AST plugin re-audit (already exhaustive) |
| `</script>` in user JSX | srcdoc terminates early | Not escaped | `safeJsString()` at line 282 |
| Bare-array JSX attribute | Babel throws "JSX value should be either..." | AI emits `data=[...]` not `data={[...]}` | Regex wrap fixup (Round 12) |
| `Map.prototype.set is not a function` | Recharts runtime error | Native Map broken | v2 Map shim at line 898 |
| `window.Recharts` undefined at hoist time | All charts undefined | UMD async load | 3-second poll in `rechartsSetup` |
| `ReferenceError: id is not defined` | Runtime error in `__renderErrors__[chartId]` | Babel Standalone 7.24.7 drops destructured `id` parameter from scope when JSX also has `id="..."` attributes | F5 id-shadow rename pre-pass (2026-07-29) |

---

## 26. Outstanding risks and "do not touch" zones

1. **The patched Recharts bundle.** `libs/Recharts.js` carries 7 surgical
   `_intern` guards. Replacing it with a fresh UMD silently re-introduces
   `t.has is not a function`. See §15.

2. **The Lucide-vs-Recharts mirror rule.** `RECHARTS_PRIORITY_NAMES` at
   line 738 MUST be an exact mirror of `rechartsSetup`'s `names` at line 663.
   See §10 and §23.

3. **The Map shim's silent setter.** Reassigning `Map.prototype.set` later in
   the session is silently absorbed (the new value goes nowhere). This is
   intentional but easy to misread as a bug.

4. **The AST plugin for `{cond && JSX}` is disabled.** It produced
   script-body SyntaxError for at least one real-world chart pattern. Don't
   re-enable it without the regression test that covers that pattern.

5. **The cache-bust format.** Every script tag that loads a renderer file
   MUST have `?v=YYYYMMDD_HHMM`. If you ship without bumping, prod users see
   the old bundle. Bump both `react_renderer.js` and `visualisation_v3.js`
   together — they're loaded as a pair.

6. **The `sandbox` attribute.** Do NOT add `allow-same-origin` to the iframe
   sandbox attribute. See §5.

7. **The pre-parse + onerror net.** Removing either layer re-opens the
   blank-canvas failure mode for strict-mode constructs.

8. **The Map shim ordering.** It MUST run before `react-dom.production.min.js`
   loads, otherwise the commit-phase mapper sees an already-broken Map. The
   ordering is enforced by placing the shim `<script>` first in the srcdoc
   template body (line 912).

9. **The identifierHoist placement.** It MUST run AFTER `Babel.transform` but
   BEFORE the transformed script is appended. Running it before Babel corrupts
   Babel's makeWeakCache plugin cache (the F3 fence caught this). Running it
   after the script append is too late — the user code has already executed.

10. **The postMessage origins.** Always `'*'`. The iframe is opaque-origin;
    `'*'` is the only safe target.

11. **The console-capture ring buffer size.** 50 entries. Larger means more
    memory per iframe; smaller means losing the most recent error to a
    transient that immediately fills the buffer. Do not change without
    consulting usage data.

12. **The BoundaryClass render-time fallbacks.** Three Recharts-specific yellow
    panels exist. If a NEW Recharts internal bug is found (e.g. new
    `*.has is not a function` pattern), add a new panel — but only with a
    verified reproducer.

13. **The F5 id-shadow rename heuristic.** The pre-pass detects `([id, X]) =>
    {…}` callbacks by scanning for the literal `([id,` token and counting
    brace depth. **It does NOT parse JS.** If the AI emits destructuring with
    comments or whitespace between the bracket and the `id` (e.g.
    `([/* comment */ id, X] => …`), F5 misses it and Babel may still drop the
    binding. The state machine also bails out for implicit-return single-
    expression arrows (no `{` body) and unbalanced braces — these fall
    through to Babel unmodified. Verified by `f5_smoke.py` (7/7 sanity
    checks) before deploy.

---

## 27. Glossary

| Term | Meaning |
|---|---|
| **Babel fence** | A probe `Babel.transform()` call at a known seam in the run-engine. Records whether Babel is healthy at that point. F0 = initial, F1 = after React hooks, F2 = after Recharts globals, F3 = before actual transform. |
| **F5 fence** | A source-cleaning pre-pass (NOT a Babel probe) that rewrites destructured `([id, X]) => {…}` callbacks to use `__entryId__` instead of `id`. Works around Babel Standalone 7.24.7's silent scope-shadow bug when JSX contains both `<X id="..."/>` and nested `.map(([id, X]) => {…})`. Records the rename count via `__idShadowFixRenames` (captured on parent as `window.parent.__lastIdShadowFixRenames`). |
| **BoundaryClass** | Hand-rolled error boundary used to wrap the user's root component. Uses prototype assignment (not `class extends`) for transpiler independence. |
| **Cache-bust** | `?v=YYYYMMDD_HHMM` suffix on every script tag that loads a renderer file. Bumped whenever the file changes. |
| **Chart id** | Unique identifier for each iframe. Used as the key in every `window.__Xxx__[chartId]` global and every `postMessage` payload. |
| **Diag kebab** | The 4th button in the iframe action bar (`addIframeDiagToolbar`). 8 copy-actions for runtime state + 1 composite + 1 copy-all. Opt-out: `window.__REACT_VIZ_DIAG__ = false`. |
| **Hoist** | `identifierHoist` IIFE that lifts PascalCase identifiers onto `window` so the transformed code can use them as globals. Two-pass design with priority source swap (Round 5). |
| **Iframe-resize** | postMessage type `{type: 'iframe-resize', id, height}` sent from iframe to parent. Parent clamps to [200, 900]. |
| **Identity check** | `window[name] === window.Recharts?.[name]`. The only signal that distinguishes a wrapped Lucide icon from a real Recharts component (both are functions). |
| **idShadowFixRenames** | Counter on the F5 fence indicating how many `id` bindings were rewritten to `__entryId__`. Surfaces on `window.parent.__lastIdShadowFixRenames` for both success and failure captures, plus on the `react-render-babel-error` postMessage payload so the diag kebab can show how many destructured bindings the AI emitted even when Babel throws. |
| **Page-level sink** | `installReactRendererDiagSink` IIFE at line 42. Registers a single `window.message` listener that captures every `react-render-*` postMessage. |
| **Priority names** | 36 PascalCase identifiers that exist in BOTH Recharts and Lucide. Listed in `RECHARTS_PRIORITY_NAMES`. Recharts always wins the hoist for these names. |
| **Sandbox string** | `allow-scripts allow-forms allow-modals allow-pointer-lock allow-downloads`. Note the absence of `allow-same-origin`. |
| **Srcdoc** | The full HTML document string passed to `iframe.srcdoc`. Built by `buildReactSrcdoc()`. |
| **Tier-1 kebab** | The 3rd button in the iframe action bar (`addIframeTier1Toolbar`). 6 export actions (PNG/PDF/CSV/Copy/Fullscreen/Save). Always present. |
| **UMD** | Universal Module Definition. A bundle format that exposes globals. Recharts and Lucide ship UMDs; the engine uses them directly via `<script src=...>`. |
| **Window globals** | The `window.__renderSnapshots__`, `__renderFences__`, etc. maps. Keyed by chart id. Populated by the page-level sink from `postMessage` payloads. |

---

## Hand-off checklist for the next session

If you are reading this for the first time, you should:

1. Read `REACT_RENDERER_LUCIDE_TROUBLESHOOTING_2026-07-22.md` §14 (the
   postmortem of the Round 5 fix) and §15 (the Round 6 verification).
2. Skim `UI/visualisation_engine/react_renderer.js` end-to-end (~2k lines).
   Focus on §6–§12 of this document for context as you go.
3. Run `python -c "from tools.registry_v3 import RegistryV3; ..."` smoke check
   to confirm the rest of the platform still works.
4. Bump the cache-bust on `business-ai-platform-v2.html:808` if you change
   anything in `react_renderer.js`.
5. **Never** edit the patched Recharts bundle, the `RECHARTS_PRIORITY_NAMES`
   constant, the `sandbox` attribute, or the Map shim without explicit
   confirmation from the user.

---

**End of master document. Last revised 2026-07-28.**