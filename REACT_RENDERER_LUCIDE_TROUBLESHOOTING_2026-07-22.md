# React Renderer Troubleshooting — Lucide / Babel / Recharts

**Date:** 2026-07-22 → 2026-07-28 (live doc; appended as new evidence lands)
**Status:** Lucide + Recharts hoist works. Babel `makeWeakCache` corruption fixed. **`t.has is not a function`** fixed in 3 patch rounds (§12). `window.Recharts` race fixed by §13 polling. **New bug 2026-07-28**: Lucide UMD icons (PieChart, BarChart, LineChart, Brush, Bar, …) overwrote Recharts components on `window` — fixed in §14 by adding a `RECHARTS_PRIORITY_NAMES` allowlist that swaps source order in the first pass and skips Lucide entirely in the second pass.
**Priority:** P3 — all 3 production dashboards (Advanced Analytics, Sales Analytics, Project Portfolio) verified rendering correctly on 2026-07-28.

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
| `8c50daeb` / `25c27cc1` / `20e6994d` | Round 1–3 patches: `vn._intern` guard in `Recharts.js` | ✅ `t.has is not a function` no longer fires for ComposedChart + dual YAxes + conditional children |
| `TBD (Round 4)` | Round 4: `rechartsSetup` polls for `window.Recharts` + assigns defined values only | ✅ `Element type is invalid: … got: undefined` no longer fires for ResponsiveContainer/Cell/etc. |
| `bf6b3454` | **Round 5**: `RECHARTS_PRIORITY_NAMES` allowlist resolves Lucide ↔ Recharts name collision in `identifierHoist` | ✅ PieChart / BarChart / LineChart / Brush / Bar now resolve to the Recharts component, not the Lucide icon descriptor. All three production dashboards verified rendering 2026-07-28. |
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
- **`bf6b3454` (2026-07-28, §14) — Lucide ↔ Recharts name collision.** The `makeIconComponent` factory at `221f1ed1` is what made the collision catastrophic: when `identifierHoist` wrapped a Lucide icon descriptor that shared a name with a Recharts component, the wrapped function silently replaced the real component on `window`. The Round 5 fix in §14 adds a `RECHARTS_PRIORITY_NAMES` allowlist that prevents this. **If you re-touch `identifierHoist`, re-read §14 first.**

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

---

## 13. Round 4 — `window.Recharts` race / `Element type is invalid` (#130)

**Status:** Fixed in commit `TBD` (cache-buster `20260724_1800` in both `react_renderer.js` URL inside `business-ai-platform-v2.html:808` and the inner `prop-types.js` / `Recharts.js` URLs inside `react_renderer.js:322`).

### 13.1 Symptom

After deploying §12, the original `t.has is not a function` error disappeared, but a new error appeared in the iframe:

```
Error: Element type is invalid: expected a string (for built-in components)
or a class/function (for composite components) but got: undefined.
…
Check the render method of `App`.
```

The component stack ended at the user's `App` component, so the failing JSX was inside the user's chart. The post-execution snapshot taken from the same iframe showed:

```json
{
  "hasRecharts":   "undefined",
  "hasBarChart":   "function",
  "hasScatter":    "function",
  "hasLineChart":  "function",
  "hasPieChart":   "function",
  "hasResponsive": "undefined",
  "hasBriefcase":  "function",
  "hasDollarSign": "function",
  …
}
```

This is internally contradictory: `hasBarChart: "function"` implies `window.Recharts.BarChart` was readable by *something* (either the `rechartsSetup` IIFE or the `identifierHoist` IIFE, both of which source from `window.Recharts || {}`), but `hasRecharts: "undefined"` says `window.Recharts` is undefined at snapshot time. The reconciliation:

1. The `rechartsSetup` IIFE ran when `window.Recharts` was defined (so BarChart, ScatterChart, LineChart, PieChart were copied to `window.*`).
2. Something — a UMD evaluation race in some browsers, a slow prop-types.js response, or a defensive cleanup path — caused the snapshot to observe `window.Recharts === undefined` even though the component-by-component copy succeeded.

The chart's JSX uses `<ResponsiveContainer>`, `<Cell>`, `<CartesianGrid>`, `<XAxis>`, `<YAxis>`, `<Tooltip>`, `<Bar>`, `<Area>`, `<Line>`, `<Legend>` — none of which are checked by the snapshot, but they all went through the same `rechartsSetup`/`identifierHoist` paths. The most likely failure mode: the rechartsSetup IIFE did `window[n] = r[n]` blindly, and for the names that were **not** in the user's `referenced` set passed to `identifierHoist`, the only writer was rechartsSetup. If rechartsSetup's `r = window.Recharts || {}` evaluated to `{}` (because the UMD hadn't run yet), those names were silently set to `undefined`. The render-time `<ResponsiveContainer />` then crashed with `Element type is invalid: … got: undefined`.

### 13.2 Fix

Two changes in `react_renderer.js`:

**a) `rechartsSetup` (line ~340) now polls for `window.Recharts` and only assigns defined values:**

```js
(function () {
    var names = ['BarChart','Bar','LineChart', … /* 33 names */ ];
    var assigned = [];
    function tryAssign() {
        var r = window.Recharts;
        if (!r || typeof r !== 'object') return false;
        for (var i = 0; i < names.length; i++) {
            var n = names[i], v = r[n];
            if (typeof v === 'function' || typeof v === 'object') {
                if (window[n] !== v) { window[n] = v; assigned.push(n); }
            }
        }
        return true;
    }
    if (!tryAssign()) {
        var waited = 0;
        var poll = setInterval(function () {
            waited += 50;
            if (tryAssign() || waited >= 3000) {
                clearInterval(poll);
                if (waited >= 3000 && !window.Recharts) {
                    console.error('[REACT_RENDERER] window.Recharts never appeared within 3 s. ' +
                        'prop-types.js may have failed to load (Recharts UMD factory needs it). …');
                }
            }
        }, 50);
    }
})();
```

**b) Cache-buster bump `20260724_1605 → 20260724_1800`** in:
- `business-ai-platform-v2.html:808` (the `<script src="visualisation_engine/react_renderer.js?v=…">` tag)
- `react_renderer.js:322` (the `<script src="visualisation_engine/libs/{prop-types,Recharts}.js?v=…">` template)

### 13.3 Updated console helpers

**Constraint:** Never `location.reload()` from a helper — it logs the SPA out (see memory `never-reload-in-devtools-diagnostics`). Use `fetch(url, {cache:'no-store'})` for freshness checks.

**Helper R1 — confirm Round 4 is deployed (cache-buster should be `20260724_1800`):**

```js
(async () => {
    const r = await fetch('/visualisation_engine/react_renderer.js', {cache:'no-store'});
    const t = await r.text();
    const m = t.match(/libs\/Recharts\.js\?v=(\d{8})_(\d{4})/);
    if (!m) { console.log('CACHE-BUSTER NOT FOUND — old build?'); return; }
    const stamp = parseInt(m[1] + m[2], 10);
    const target = 20260724 * 1e4 + 1800;
    console.log(stamp === target
        ? `OK: Round 4 deployed (cache-buster ${m[1]}_${m[2]})`
        : `STALE: Round 4 target ${target}, server has ${stamp}`);
    return { serverCacheBuster: `${m[1]}_${m[2]}`, target, isCurrent: stamp === target };
})();
```

**Helper R2 — find the latest chart iframe and report the fence results:**

```js
(() => {
    const iframes = Array.from(document.querySelectorAll('iframe'));
    const diag = iframes.filter(f => f.id && /^react-/.test(f.id));
    if (!diag.length) { console.log('No react iframes found. Render a chart in the playground first.'); return; }
    const latest = diag[diag.length - 1];
    console.log('Found', diag.length, 'react iframes; latest id =', latest.id);
    return { id: latest.id, count: diag.length };
})();
```

**Helper R3 — read the fence results from the parent-side cache (set by the iframe's inline script):**

```js
(() => {
    const fences = window.__babelFences || (window.parent && window.parent.__babelFences);
    if (!fences) { console.log('No fences captured yet. Re-render any chart first.'); return; }
    console.table(fences);
    return fences;
})();
```

**Helper R4 — read the post-exec snapshot from the latest iframe (no reload required):**

```js
(() => {
    const snap = window.__lastExecSnap;
    if (!snap) { console.log('No post-exec snapshot yet. Render any chart first.'); return; }
    console.log('[REACT_RENDERER_DIAG] post-exec snapshot:', JSON.stringify(snap, null, 2));
    return snap;
})();
```

**Helper R5 — directly probe a live chart iframe's window for Recharts (run from inside the iframe's DevTools context):**

```js
(() => {
    return {
        windowRecharts:        typeof window.Recharts,
        windowPropTypes:       typeof window.PropTypes,
        windowReact:           typeof window.React,
        windowBarChart:        typeof window.BarChart,
        windowScatterChart:    typeof window.ScatterChart,
        windowResponsiveContainer: typeof window.ResponsiveContainer,
        windowCell:            typeof window.Cell,
        windowCartesianGrid:   typeof window.CartesianGrid,
        windowXAxis:           typeof window.XAxis,
        windowYAxis:           typeof window.YAxis,
        windowTooltip:         typeof window.Tooltip,
        windowLegend:          typeof window.Legend,
        windowComposedChart:   typeof window.ComposedChart,
        rechartsKeys:          window.Recharts ? Object.keys(window.Recharts).sort() : null
    };
})();
```

Run R5 from inside an active chart iframe (DevTools > Sources > top > select the iframe > Console panel). All `function`/`object` = Round 4 worked. Any `undefined` = that name was never assigned, which is the symptom §13 was designed to eliminate.

### 13.4 Verification

- ComposedChart with dual YAxes + `<Area>` / `<Bar>` / `<Line>` children should now render without React error #130.
- ScatterChart with mapped `<Cell>` children should now render.
- The `[REACT_RENDERER] rechartsSetup resolved synchronously:` (or `after N ms:`) console line confirms the polling path was taken.
- If `window.Recharts never appeared within 3 s` appears, check the Network tab for `visualisation_engine/libs/prop-types.js` — a 4xx/5xx/CORS error there is the most likely cause (the Recharts UMD factory needs PropTypes to evaluate without throwing).

---

## 14. Round 5 — Lucide ↔ Recharts name collision (commit `bf6b3454`, 2026-07-28)

**Status:** Fixed in commit `bf6b3454` (cache-buster `20260728_1600` in `business-ai-platform-v2.html:808`). All three previously-failing production dashboards (Advanced Analytics, Sales Analytics, Project Portfolio) now render real Recharts charts.

### 14.1 Symptom

The iframe would render successfully (no Babel error, no React error #130, fences F0–F3 all `OK`, post-exec snapshot showed `hasBarChart: "function"`, `hasPieChart: "function"`, etc.), **but** the chart visually rendered as a **giant Lucide pie-chart SVG icon** instead of a Recharts pie chart.

For Advanced Analytics specifically:
- The KPI cards rendered fine.
- The "Performance Trends" `<ComposedChart>` rendered fine.
- The "Product Mix" `<PieChart>` rendered as a giant black-on-white Lucide pie icon — occupying the whole `<ResponsiveContainer>` height — with NO slices, NO labels, NO legend.

Same shape affected Sales Analytics (`Customer Segments` donut), and indirectly Project Portfolio (`Budget vs Spent` bars). The `[REACT_RENDERER_PARENT_DIAG]` log showed the hoist succeeded:

```
[REACT_RENDERER] hoisted identifiers from lucide/Recharts:
  PieChart, Pie, Cell, BarChart, Bar, LineChart, Line, Brush, …
```

…yet the rendered output was the icon, not the chart. This contradicted the snapshot, which showed `hasPieChart: "function"`.

### 14.2 Root cause

The Lucide UMD (`window.lucide`) exports icons as **PascalCase-named keys** at the top level. Several of those names overlap with Recharts component names:

| Lucide icon | Also a Recharts component |
|---|---|
| `PieChart` | yes — Recharts pie-chart container |
| `BarChart` | yes — Recharts bar-chart container |
| `LineChart` | yes — Recharts line-chart container |
| `Brush` | yes — Recharts brush tool |
| `Bar` | yes — Recharts bar primitive |
| `Line` | yes — Recharts line primitive |
| `Area` | yes — Recharts area primitive |
| `Pie` | yes — Recharts pie primitive |
| `Cell` | yes — Recharts cell primitive |
| `Radar` | yes — Recharts radar primitive |
| `Scatter` | yes — Recharts scatter primitive |
| `ComposedChart`, `RadarChart`, `AreaChart`, `ScatterChart`, `RadialBarChart`, `FunnelChart`, `Treemap` | yes — Recharts chart containers |
| `XAxis`, `YAxis`, `ZAxis`, `CartesianGrid`, `Tooltip`, `Legend`, `PolarAngleAxis`, `PolarRadiusAxis`, `PolarGrid`, `ReferenceLine`, `ReferenceArea`, `ReferenceDot`, `ErrorBar`, `Label`, `LabelList` | yes — Recharts axis/decor primitives |
| `ResponsiveContainer` | yes — Recharts layout container |

The lucide icon-descriptor values are **arrays of `[tagName, attrs]` tuples**, e.g. `window.lucide.PieChart === [["path", { d: "M21 12a9 9 0 1 1-9-9c2.5 0 4.8 1 6.5 2.7l-3.5 3.5…" }]]`. When the renderer's `identifierHoist` IIFE saw `Array.isArray(v)`, it wrapped the descriptor in `makeIconComponent(name, v)` — producing a real React component that renders an `<svg>` of the icon.

The bug was in `identifierHoist`'s **two-pass design**:

1. **First pass** (lines 804-826) — for each identifier the user's code references (`PieChart`, `BarChart`, etc.), it walked `[L, R]` (lucide first, recharts second) and took the first hit. So `<PieChart>` in user code resolved to **`makeIconComponent('PieChart', window.lucide.PieChart)`** — a giant SVG icon.
2. **Second pass** (lines 834-845) — for *every* PascalCase key on `window.lucide`, it lifted onto `window` with `L[k]`. For names that were also Recharts components, this overwrote the real component that `rechartsSetup` had placed on `window` one IIFE earlier. So even if a name wasn't in the user's referenced set, the second pass silently corrupted it.

The net effect: **no matter what the AI's source contained, `window.PieChart` was always the Lucide icon component** by the time the user's JSX ran.

The `hasPieChart: "function"` line in the snapshot was technically true (the wrapped component IS a function), so the snapshot couldn't catch this — it lied to us.

### 14.3 Fix — `RECHARTS_PRIORITY_NAMES` allowlist

Two surgical changes in `identifierHoist` at [react_renderer.js:732-851](UI/visualisation_engine/react_renderer.js#L732):

**a) Define a `RECHARTS_PRIORITY_NAMES` constant** at line 738 — an **exact mirror** of the `names` list used by `rechartsSetup` at line 667:

```js
const RECHARTS_PRIORITY_NAMES = [
    'BarChart','Bar','LineChart','Line','PieChart','Pie','Cell',
    'AreaChart','Area','ScatterChart','Scatter','XAxis','YAxis','ZAxis',
    'CartesianGrid','Tooltip','Legend','ResponsiveContainer',
    'RadarChart','Radar','PolarAngleAxis','PolarRadiusAxis','PolarGrid',
    'ComposedChart','RadialBarChart','RadialBar','Treemap','FunnelChart','Funnel',
    'LabelList','ReferenceLine','ReferenceArea','ReferenceDot',
    'Brush','ErrorBar','Label'
];
```

The constant is interpolated into the `identifierHoist` template literal at line 759 via `JSON.stringify(RECHARTS_PRIORITY_NAMES)`.

**b) In the first pass (line 808)** — swap the source order for priority names so Recharts resolves BEFORE Lucide:

```js
var sources = priorityNames.indexOf(name) >= 0 ? [R, L] : [L, R];
```

**c) In the second pass (line 837)** — skip priority names entirely so Lucide cannot overwrite Recharts on the second walk:

```js
if (priorityNames.indexOf(k) >= 0) return;
```

Both passes consult the same constant, so the two patches stay in lockstep — you can't fix one without the other.

### 14.4 Mirror-rule maintenance note

The `RECHARTS_PRIORITY_NAMES` constant MUST stay in sync with the `names` array inside `rechartsSetup` at line 667. If you add a new Recharts component name to `rechartsSetup`, you must add it to `RECHARTS_PRIORITY_NAMES` too. The two arrays currently have **36 entries, identical, in the same order**. A future lint check could enforce this — for now it's a manual invariant.

**Audit recipe** (run from `react_renderer.js` repo root):

```js
// 1. Extract the rechartsSetup names block
var setupStart = editorBuffer.indexOf("var names = [");
var setupEnd = editorBuffer.indexOf("];", setupStart);
// 2. Extract the RECHARTS_PRIORITY_NAMES block
var priStart = editorBuffer.indexOf("const RECHARTS_PRIORITY_NAMES = [");
var priEnd = editorBuffer.indexOf("];", priStart);
// 3. JSON.parse both, sort, diff
// (skip in production — this is a one-time audit)
```

If you bump Recharts to a new major version and the component API gains a new chart type (e.g. `SankeyChart`), update **both** lists before the chart can ever be referenced in user code.

### 14.5 Behavioural verification (Node.js)

A standalone Node.js smoke test (using `vm.runInNewContext` to mock `window.lucide` and `window.Recharts` with collision-shaped fixtures) confirmed:

- `window.PieChart === Recharts.PieChart` (identity preserved, not a wrapped icon)
- `window.BarChart === Recharts.BarChart`
- `window.LineChart === Recharts.LineChart`
- `window.Brush === Recharts.Brush`
- `window.Bar === Recharts.Bar`
- Non-colliding Lucide icons (`DollarSign`, `TrendingUp`, `Users`) still resolve to wrapped icon components
- `[REACT_RENDERER] hoisted identifiers from lucide/Recharts:` log lists all 36 priority names + the user's references
- The second-pass skip correctly leaves `window.PieChart` as the Recharts component even when lucide's array descriptor is present in `L`

10/10 assertions green. Test was deleted after success (per the no-leftover-tmp-files rule).

### 14.6 Render verification

The user's screenshots after deploy (`bf6b3454`) confirmed:
- **Advanced Analytics** — Performance Trends `<ComposedChart>` + Product Mix `<PieChart>` both render real charts
- **Sales Analytics** — Revenue Trend `<LineChart>` + Customer Segments `<PieChart>` donut both render real charts
- **Project Portfolio** — Overview (priority bars + budget vs spent) + Timeline (Gantt) both render real charts
- No `Element type is invalid` errors, no `t.has is not a function`, no console errors
- All buttons (tab/filter toggles) update the charts reactively

### 14.7 How to recognise this bug if it ever returns

1. **Visual:** A chart iframe renders, but a specific chart (always one that uses a name from the priority list above) renders as a **giant Lucide-shaped SVG icon** instead of a chart. The icon will be monochrome and recognisable — e.g. pie chart → wedge-shaped SVG; bar chart → three vertical bars; line chart → zig-zag line.
2. **Diagnostic:** `[REACT_RENDERER] hoisted identifiers from lucide/Recharts:` log shows the priority names appear there. The post-exec snapshot shows `hasPieChart: "function"`, `hasBarChart: "function"`, etc. — i.e. the snapshot LIES about the bug. The real check is:
   ```js
   // Run from inside the iframe's DevTools console
   ({ lucidePieChart: window.lucide.PieChart, rechartsPieChart: window.Recharts.PieChart, windowPieChart: window.PieChart, isIcon: Array.isArray(window.PieChart) || (window.PieChart && window.PieChart.displayName === 'PieChart' && Array.isArray(window.lucide.PieChart)) })
   ```
   If `window.PieChart` is a function but `window.lucide.PieChart` is an array (and `window.Recharts.PieChart` is a different function), the collision is happening — the priority allowlist is missing or stale.
3. **Re-introduction vectors** to watch for:
   - Adding a new Recharts chart component to `rechartsSetup` without also adding it to `RECHARTS_PRIORITY_NAMES`
   - Bumping the Lucide UMD to a new version (check whether the new bundle exports any new colliding names)
   - Bumping the Recharts UMD (a new chart type — add it to both lists)
   - Rewriting `identifierHoist` without porting the priority logic

### 14.8 Files changed in this fix

| File | Change | Lines |
|---|---|---|
| [UI/visualisation_engine/react_renderer.js](UI/visualisation_engine/react_renderer.js) | Added `RECHARTS_PRIORITY_NAMES` constant, swapped source order in first pass, skipped priority names in second pass | +35 / −2 |
| [UI/business-ai-platform-v2.html](UI/business-ai-platform-v2.html) | Cache-buster bump `?v=20260728_1430` → `?v=20260728_1600` | 1 line |

No new dependencies, no DB changes, no API changes, no env-var changes.

### 14.9 Why the snapshot couldn't catch this

§4's `react-render-snapshot` message captures `typeof window[name]` for the names it cares about. The wrapped `makeIconComponent('PieChart', lucideArray)` IS a function — `typeof window.PieChart === 'function'` is true, so the snapshot reports `hasPieChart: "function"` and the bug hides. The snapshot doesn't dereference the identity — it never asks "is this the Recharts PieChart or a wrapped Lucide icon?"

A future improvement could add an identity check: `({ name, type: typeof window[name], identityMatchesRecharts: window[name] === (window.Recharts || {})[name] })`. That would have caught this bug in §4. Tracked for a future round; not part of `bf6b3454`.

