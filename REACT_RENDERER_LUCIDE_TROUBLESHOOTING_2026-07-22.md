# React Renderer Troubleshooting — Lucide / Babel / Recharts

**Date:** 2026-07-22 → 2026-07-23 (live doc; appended as new evidence lands)
**Status:** Lucide + Recharts hoist works. Babel `makeWeakCache` corruption fixed. **One remaining bug**: `ComposedChart` with dual YAxes + conditional `<Area>/<Bar>/<Line>` throws `TypeError: t.has is not a function` from `Recharts.js:2:121494`. Single-axis Recharts renders fine.
**Priority:** P1 — Recharts with `LineChart`/`PieChart`/`BarChart` (single-axis) works, but the AI commonly emits `ComposedChart` for combined dashboards, so this still blocks a major class of visualizations.

---

## 1. Timeline of commits (chronological)

| Date / commit | Goal | Result |
|---|---|---|
| `77a83c91` | Self-host babel/react/react-dom/recharts/prop-types | ✅ All libs now load from `visualisation_engine/libs/` — no more CDN race for Recharts |
| `03889d34` | Pin `@babel/standalone@7.24.7`, revert prior lucide experiments | ✅ Stable Babel baseline |
| `1874dba1` | Capture full failing JSX on Babel error for offline analysis | ✅ New globals `window.parent.__lastBadJsx`, `__lastBadFences` |
| `a23a4e2f` | Babel.transform fence probes (F0–F3) to isolate `makeWeakCache` bug | ✅ Probes installed; **pinpointed the bug** |
| `6bd07a12` | SSE heartbeat / broken-pipe handlers / 502 retry | ✅ Streaming no longer dies silently |
| `b0ceea21` | Snapshot between script-append and auto-mount | ✅ Post-exec snapshot on `window.parent.__lastExecSnap` |
| `90ed3cf1` | Page-level diagnostic sink for blank-iframe triage | ✅ `__renderSnapshots__`/`__renderFences__`/`__renderErrors__` |
| `67a17e56` | Replace literal `'\n'` in fence catch with `String.fromCharCode(10)` | ✅ Fixed a templated-comment bug |
| `8e5e5294` | Hoist `__babelFence` via function declaration | ✅ Function hoisting bypassed the temporal dead zone |
| `9ff3fc0b` | Move `identifierHoist` IIFE AFTER `Babel.transform` | ✅ Resolved the `e.get is not a function` at `babel.min.js:1:925003` |
| `REACT_RENDERER_LUCIDE_TROUBLESHOOTING_2026-07-22.md` (this doc, original) | Wrote the always-inject-lucide plan (Strategy A) | ✅ Strategy A applied; verification confirms lucide is fully hoisted |

---

## 2. What was broken, what was fixed

### Bug 1 — Lucide icons not detected → `ReferenceError: TrendingUp is not defined`

**Symptom:** AI emits JSX like `<TrendingUp />` without an `import`. Renderer didn't inject the lucide UMD script. Iframe went white.

**Root cause:** `usesLucide` regex on [react_renderer.js:187](UI/visualisation_engine/react_renderer.js#L187) only matched ~30 hand-picked icon names. `TrendingUp`/`Briefcase`/`Calendar`/`DollarSign`/`Users`/`Activity`/`BarChart3`/`Filter` all slipped past it.

**Fix:** Strategy A from the original doc — unconditional lucide UMD injection at [react_renderer.js:312-313](UI/visualisation_engine/react_renderer.js#L312). Comment block cites this doc.

**Verified:** Today the diagnostic snapshot shows
```
hasBriefcase: "function"
hasDollarSign: "function"
hasTarget: "function"
hasUsers: "function"
hasWallet: "function"
hasCreditCard: "function"
```
and the log shows
```
[REACT_RENDERER] hoisted identifiers from lucide/Recharts:
  TrendingUp, Calendar, DollarSign, Users, Activity, BarChart3, Filter,
  ResponsiveContainer, ComposedChart, CartesianGrid, XAxis, YAxis, Tooltip,
  Legend, Area, Bar, Line, PieChart, Pie, Cell
```
The lucide catch-all lift at [react_renderer.js:429-440](UI/visualisation_engine/react_renderer.js#L429) is reading from `window.lucide` directly (the UMD exposes icons at the top level), so my earlier concern that it needed `window.lucide.icons` was wrong — that was based on reading the lucide UMD source without testing. The current path works.

### Bug 2 — `e.get is not a function` at `babel.min.js:1:925003`

**Symptom:** After the lucide fix, the very first fence (F0) passed but the F3 fence (after Recharts globals + before the real `Babel.transform` call) failed with this error. Same error propagated to the real transform.

**Root cause:** The `identifierHoist` IIFE, executed between Babel's initial probe and the real `Babel.transform(rawSource, ...)`, was corrupting Babel's internal `makeWeakCache` (`function NI(e,t,r)` in the minified bundle at offset 925003). The cache is a `WeakMap`-backed plugin resolution map; when the IIFE allocates new function instances in the same execution frame, something throws when Babel tries `n=e.get(t)` on its own internal slot.

**Diagnosis:** The fence probes (F0–F3) bracketed the renderer setup so each step could be isolated. F0/F1/F2 succeeded identically, F3 was the first to touch `Babel.transform` AFTER the `identifierHoist` IIFE — diff narrowed it to the hoist.

**Fix (commit `9ff3fc0b`):** Move the `${identifierHoist}` injection from its previous position (before F3) to a new spot AFTER the real `Babel.transform` call succeeds, BEFORE the classic-`<script>` append. See [react_renderer.js:642-656](UI/visualisation_engine/react_renderer.js#L642). Babel's syntax pass doesn't need `window.BarChart`, but the executed code does — placement matters.

**Verified:** Today the diagnostic shows
```
fencesSummary: "F0=OK, F1=OK, F2=OK, F3=OK"
```
All four fences pass. The actual transform on the 12,028-char source also succeeds (`outLen: 13702`).

### Bug 3 — `TypeError: t.has is not a function` in Recharts (CURRENT, OPEN)

**Symptom:** The Advanced Analytics dashboard with `ComposedChart`, dual YAxes (`yAxisId="left"` and `"right"`), and conditional `{showRevenue && (<Area ... />)}`/`{showUsers && (<Bar ... />)}`/`{showConversion && (<Line ... />)}` children throws:

```
TypeError: t.has is not a function
    at mn (Recharts.js:2:121494)
    at vn.has (Recharts.js:2:121339)
    at On.o.domain (Recharts.js:2:122031)
    at r.domain (Recharts.js:2:122831)
    at Recharts.js:2:341845
    at Array.reduce (<anonymous>)
    at _m (Recharts.js:2:341026)
    at Recharts.js:2:442130
    at Array.forEach (<anonymous>)
    at b (Recharts.js:2:442104)
    at Recharts.js:2:460818
    at tf (react-dom.production.min.js:117:145)
    at uf (react-dom.production.min.js:119:366)
    ...
```

This surfaces inside the ErrorBoundary (`componentDidCatch`) as the visible
```
⚠ Render error:
t.has is not a function
```
banner inside the iframe.

**Reproduces:** Every test that combines ≥2 chart types in a `ComposedChart` with dual YAxes. The simpler Sales Dashboard (separate `LineChart`, `PieChart`, `BarChart` per view) renders fine.

**Not yet diagnosed.** Working hypothesis in §3 below.

---

## 3. Open investigation: ComposedChart `t.has is not a function`

### Why the fence diagnostic can't catch this
The fences only probe `Babel.transform(...)` syntax-pass health. Recharts's `t.has` is a runtime error inside the **React render phase**, after `Babel.transform` has succeeded and the script has executed. Fences see `ok=true` at all four checkpoints because Babel is healthy — the bug is downstream.

### Hypotheses (in order of likelihood)

**H1 — Recharts `ComposedChart` + dual YAxis scale-resolution bug.**
The trace shape (`r.domain` → `On.o.domain` → `vn.has` → `mn`) is characteristic of Recharts scale plumbing. `vn.has()` looks like a scale's `.has(value)` check used during domain merging. With `yAxisId="left"` shared by `<Area>` (dataKey="revenue") and `<Bar>` (dataKey="users"), and `yAxisId="right"` for `<Line>` (dataKey="conversion"), Recharts must merge domains per axisId. If the merged-domain step receives a non-array (e.g. a string, an `undefined`, or one of the values), it calls `t.has` on it.

In the AI's source:
- `revenue` range: 45,000–105,000
- `users` range: 4,200–9,100
- `conversion` range: 2.9–5.1

The left axis has to combine revenue (large) and users (small) — large dynamic range. Recharts uses `LinearScale` here. The `t.has` call in the error is being made on a value that's not the scale.

**H2 — Conditional children destabilise Recharts's per-axis registry.**
The pattern `{showX && (<Component .../>)}` is officially supported by Recharts, but the registry that Recharts builds at first mount (which maps child `<XAxis yAxisId="...">` ↔ its data siblings) is computed once. If a child is conditionally absent at first mount, the registry may contain an entry that points at `undefined`. The next render then dereferences `.has` on that undefined slot.

**H3 — `<defs>` + `<linearGradient>` inside `<ComposedChart>`.**
The AI emits `<defs><linearGradient id="colorRevenue" .../></defs>` as a child of `<ResponsiveContainer>` in the second test. While this is fine in `AreaChart`, `ComposedChart` may walk children it does not understand and choke. However the trace shows the throw is in scale logic, not SVG handling, so this is weaker.

**H4 — Recharts version mismatch / UMD wrapping bug.**
The renderer self-hosts `visualisation_engine/libs/Recharts.js`. If that build was made with a Babel config that doesn't handle a particular ES2018 feature (object rest/spread in JSX props), the bundle could be subtly broken in scale code. Less likely because the single-axis charts work fine in the same bundle.

### Recommended next diagnostic

1. **Reduce the failing source to the minimal repro.** Take the AI's full ComposedChart JSX and delete things one at a time:
   - First, delete the conditional wrapping (`{showX && ...}`) — render `<Area>`+`<Bar>`+`<Line>` unconditionally.
   - Then, drop `<Bar>` (keep only Area+Line).
   - Then, drop one YAxis (single-axis).
   - Then, drop `<defs>` + `<linearGradient>`.
   Each deletion either makes the chart render or narrows the bug.

2. **Patch `__babelFence` to probe more aggressively.** Add a fence at "after auto-mount start" that does
   ```js
   try { ReactDOM.createRoot(document.createElement('div')).render(
       React.createElement(window.Recharts.ComposedChart, { data: [{a:1}], width: 200, height: 200 },
           React.createElement(window.Recharts.Area, { dataKey: 'a' }))
   ); fences.push({label:'F4-Recharts-probe', ok:true});
   } catch(e) { fences.push({label:'F4-Recharts-probe', ok:false, err:e.message, stackHead:e.stack.split('\n').slice(0,4).join(' | ')}); }
   ```
   If this fails the same way (`t.has is not a function`), the bug is in Recharts itself, not in anything the AI emitted. If it succeeds, the bug is in the AI's source — most likely the conditional children (H2).

3. **Try a different Recharts import.** If self-hosted `Recharts.js` proves to be the issue, swap it for the official UMD on unpkg (`https://unpkg.com/recharts@2/umd/Recharts.js`). Same self-hosted loading pattern as Babel.

4. **Try Recharts `defaultShowTooltip` / explicit `domain` props.** If `r.domain` is the trigger, providing `domain={[0, 'auto']}` on each YAxis might bypass the dynamic-merging logic.

---

## 4. Diagnostic infrastructure (now in place)

Every React iframe the renderer creates posts three messages to its parent (`window` of the SPA):

| Message type | Fields | Purpose |
|---|---|---|
| `react-render-fences` | `id`, `fences[]` | Babel fence results from F0–F3 (and any future fences) |
| `react-render-snapshot` | `id`, `snap` | Post-execution runtime snapshot — every `typeof` we care about, plus DOM checks |
| `react-render-error` | `id`, `message`, `stack` | Caught by `componentDidCatch` in the ErrorBoundary |

The parent listener at [react_renderer.js:42-84](UI/visualisation_engine/react_renderer.js#L42) caches everything on `window.__renderSnapshots__`/`__renderFences__`/`__renderErrors__`. DevTools console can probe:

```js
__renderFences__['two-rule-react-1784797846996']   // see F0/F1/F2/F3 ok booleans
__renderSnapshots__['two-rule-react-1784797846996'] // see the full runtime state
__renderErrors__['two-rule-react-1784797846897']    // see the latest runtime error
```

This means a blank-iframe investigation can be done from a single DevTools console without attaching to each sandboxed child iframe.

---

## 5. Verification (after every fix)

1. Hard-reload SPA (Ctrl+Shift+R).
2. Trigger a React viz (or paste the failing repro into chat).
3. Open DevTools → Console. Look for:
   - `[REACT_RENDERER_PARENT_DIAG] fences for <id>` — should show all `ok: true`.
   - `[REACT_RENDERER_DIAG] post-exec snapshot` — check `hasRecharts: "object"`, `hasLucide: "object"`, all hooks `"function"`, the icons in use `"function"`, `fencesSummary: "F0=OK, F1=OK, F2=OK, F3=OK"`.
   - No `runtime error for <id>` red lines.
4. If the iframe still shows ⚠ Render error, paste the `t.has is not a function` line (and the `stackHead` that follows it) into chat — the diagnostic infrastructure now captures it cleanly.

---

## 6. Files involved

- [UI/visualisation_engine/react_renderer.js](UI/visualisation_engine/react_renderer.js) — the only file being modified for these fixes
- `UI/visualisation_engine/libs/Recharts.js` — self-hosted UMD (currently the version we ship — bug investigation may need to bump)
- `UI/visualisation_engine/libs/babel.min.js` — `@babel/standalone@7.24.7` (pinned)
- `UI/visualisation_engine/libs/react.production.min.js`, `react-dom.production.min.js` — React 18
- `UI/visualisation_engine/libs/prop-types.js` — Recharts runtime dep
- `UI/business-ai-platform-v2.html` — calls the renderer; has a `?v=<date>` cache-buster for `react_renderer.js`

---

## 7. Cache-busting

The SPA loads `react_renderer.js?v=<YYYYMMDD_HHMM>`. After every renderer edit, bump this. Search pattern: `react_renderer.js?v=`. Bump both the SPA HTML AND any callers that bypass the cache-buster.

---

## 8. Related history (older fixes, preserved for context)

- `b24cc2ac` — ErrorBoundary + initial lucide/Recharts auto-hoist.
- `048132a6` — Dropped dangling `${lucideSetup}` reference.
- `221f1ed1` — Wrapped hoisted lucide arrays as React SVG components (`makeIconComponent` factory).
- `c8078410` — AST-based module strip.
- The original doc (now superseded by §1–§5 above) identified that the hoist block was correct but the lucide UMD never loaded for many AI-emitted icons. **That bug is now fixed via Strategy A; see §2 Bug 1.**

---

## 9. Quick reference: the failing example (still open)

```jsx
<ResponsiveContainer width="100%" height="100%">
  <ComposedChart data={filteredData}>
    <defs>
      <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
        <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8} />
        <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.2} />
      </linearGradient>
    </defs>
    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
    <XAxis dataKey="month" stroke="#64748b" />
    <YAxis yAxisId="left" orientation="left" stroke="#64748b" />
    <YAxis yAxisId="right" orientation="right" stroke="#64748b" />
    <Tooltip />
    <Legend />
    {showRevenue && (
      <Area yAxisId="left" type="monotone" dataKey="revenue"
            fill="url(#colorRevenue)" stroke="#3b82f6" name="Revenue ($)" />
    )}
    {showUsers && (
      <Bar yAxisId="left" dataKey="users" fill="#10b981" name="Users" />
    )}
    {showConversion && (
      <Line yAxisId="right" type="monotone" dataKey="conversion"
            stroke="#ef4444" strokeWidth={3} name="Conversion (%)" dot={{ r: 5 }} />
    )}
  </ComposedChart>
</ResponsiveContainer>
```

To triage, delete the `{showX && (...)}` wrappers first (force all children to render) and see if the error goes away. If yes → H2 (conditional children). If no → drop `<Bar>` next; if still failing → H1/H4.

---

## 10. Hand-off

If you're reading this in a new session and the user pastes a fresh `t.has is not a function` error:

1. Re-read §3 — the bug is open and the diagnostic plan is laid out.
2. Run the minimal-repro reduction in §3 step 1 — that will tell you whether it's H1/H4 or H2 in 2 minutes.
3. Don't touch the lucide hoist or Babel fences — both are working.
4. If you decide to swap the self-hosted `Recharts.js` for an unpkg UMD, do it as its own commit so the diff is reviewable. Remember to bump the cache-buster.

---

## 12. Recharts `vn` class `_intern` guard — patch landed (2026-07-24)

**Status:** Patched in 3 rounds (`8c50daeb` → `25c27cc1` → `20e6994d`). The `t.has is not a function` error from §3 should no longer occur for ComposedChart-with-dual-YAxes + conditional children, ScatterChart-with-Cell-children, or any pattern that exercises Recharts' `On.o.domain` re-evaluation.

### 12.1 Root cause (confirmed by reading the bundle)

`Recharts.js` line 121183 contains a `class vn extends Map` whose constructor sets `_intern = new Map()` via `Object.defineProperties`. Three free functions destructure `this._intern` and call methods on it:

```js
function mn({_intern:t, _key:e}, r) { return (t && t.has) ? t.has(e(r)) ? t.get(e(r)) : r : r }   // read
function bn({_intern:t, _key:e}, r) { return (t && t.has) ? t.has(e(r)) ? t.get(e(r)) : (t.set(e(r), r), r) : r }   // write
function gn({_intern:t, _key:e}, r) { return (t && t.has) ? t.has(e(r)) && (r = t.get(e(r)), t.delete(e(r)), r) : r }   // delete
```

When AI-authored charts use `ComposedChart` with conditional `<Area>/<Bar>/<Line>` children or `ScatterChart` with mapped `<Cell>` children, the `On.o.domain` factory at line 121725 does `t = new vn` and then loops `t.has(n) || t.set(n, ...)`. The constructor's `Object.defineProperties` makes `_intern` non-writable, non-configurable, non-enumerable — so on a properly-constructed `vn` it can never be reassigned. **The actual upstream bug** (still open in Recharts: issues [#1988](https://github.com/recharts/recharts/issues/1988), [#4923](https://github.com/recharts/recharts/issues/4923), [#6246](https://github.com/recharts/recharts/issues/6246), [#3442](https://github.com/recharts/recharts/issues/3442)) is that some code paths create Map-like objects inheriting `vn.prototype` without running the constructor — leaving `_intern` undefined.

### 12.2 Three-round patch history

| Commit | What it patches | Bytes added | Layer |
|---|---|---|---|
| `8c50daeb` | `mn()` normalizer — `(t && t.has)` guard | +12 | Normalizer (defense-in-depth) |
| `25c27cc1` | `bn()` + `gn()` normalizers — same guard | +24 | Normalizer (defense-in-depth) |
| `20e6994d` | `vn.prototype.{get,has,set,delete}` — `this._intern ? super.X(mn(this,t)) : super.X(t)` | +109 | Public API (primary guard) |

Cumulative file size: 502,946 → 503,091 bytes (+145 total). The normalizer guards catch the failure if any non-prototype call path slips through; the prototype guards catch all four standard methods at the upstream-most point possible.

### 12.3 CRITICAL: do NOT overwrite `Recharts.js` without re-applying these patches

`UI/visualisation_engine/libs/Recharts.js` is a **patched** minified bundle. If you replace it with a fresh `recharts@2.x` UMD from unpkg, all three rounds of guards disappear and the bug returns. If you must upgrade Recharts, do this:

1. `cp UI/visualisation_engine/libs/Recharts.js /tmp/Recharts.js.before-patch`
2. Replace the file with the new UMD
3. Re-apply all three guards using `grep -bo` to find the new byte offsets
4. Bump both cache-busters (`react_renderer.js` URL in SPA HTML + `Recharts.js`/`prop-types.js` URLs in the renderer template)
5. Test with the same ComposedChart + dual YAxes + conditional children pattern

If the upgrade is to Recharts 3.x, the class is no longer named `vn` and the minified layout is different — redo the analysis from §12.1 (search for the new class name and the new `_intern`-equivalent slot). The same vulnerability class (destructured-Map-slot method call) likely persists.

### 12.4 Verification

- ComposedChart with dual YAxes + `{showRevenue && <Area .../>}` + `{showUsers && <Bar .../>}` + `{showConversion && <Line .../>}` should now render
- ScatterChart with `<Cell>` children inside `<Scatter>` should now render
- Single-axis LineChart/BarChart/PieChart (which already worked) continue to work
- All other Recharts patterns are unaffected — the guards are at the `vn` class only
