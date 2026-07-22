# React Renderer Lucide-Icon Troubleshooting & Hand-off

**Date:** 2026-07-22
**Status:** Fix **NOT** deployed — production console still shows `ReferenceError: TrendingUp is not defined` and `Briefcase is not defined` from `about:srcdoc:293`.
**Priority:** P0 — this blocks every AI-built React dashboard that uses lucide icons without an explicit `import` statement.

---

## What is broken

AI agents emit React JSX like:
```jsx
function Dashboard() {
  return (
    <div>
      <TrendingUp size={28} className="text-blue-600" />
      <Briefcase />
      <Calendar />
      <DollarSign />
      <Users />
      <Activity />
      <BarChart3 />
      <Filter />
    </div>
  );
}
```
…with **no `import` statements** (because the AI lives in a no-build-step sandboxed iframe). The renderer's job is to make every PascalCase JSX tag resolve to either a React component from `window.Recharts` or a lucide icon component from `window.lucide`.

**Current state:** `window.lucide` is never defined in the iframe, so `TrendingUp`/`Briefcase`/etc. never get bound to the global scope → React throws `ReferenceError: TrendingUp is not defined` at first render → the ErrorBoundary catches it and the iframe goes white.

---

## Root cause

The renderer's library auto-detection (at `UI/visualisation_engine/react_renderer.js:104`):

```js
const usesLucide = /lucide|LucideIcon|import.*from.*['"](lucide|lucide-react)['"]|\b(ChevronRight|ChevronDown|Circle|Square|Triangle|Star|Heart|Home|User|Settings|Search|Bell|Mail|Check|X|Plus|Minus|Edit|Trash|Download|Upload|Eye|Lock|Unlock|ArrowRight|ArrowLeft|ArrowUp|ArrowDown)\b/.test(jsxContent);
```

This regex only triggers the lucide UMD injection if the user's JSX mentions one of ~30 hand-picked icon names (`ChevronRight`, `Circle`, `Square`, etc.). **None of the icons in the failing example are in that list.** `TrendingUp`, `Briefcase`, `Calendar`, `DollarSign`, `Users`, `Activity`, `BarChart3`, `Filter` — all common icons, none detected.

So `usesLucide === false`, the script tag `<script src="https://unpkg.com/lucide@latest/dist/umd/lucide.js"></script>` is never emitted (line 220-221), `window.lucide` is `undefined` when the identifier-hoist IIFE runs (line 266+), and the hoist's `sources = [window.lucide || {}, window.Recharts || {}]` uses an empty object — no icons get bound.

---

## What's already in place (NOT the problem)

The post-fix hoist code at lines 266-348 (from commit `221f1ed1`) is correct in structure:

```js
function makeIconComponent(name, descriptor) {
    var Icon = function (props) {
        // ... renders <svg> with descriptor children
    };
    Icon.displayName = name;
    return Icon;
}
Array.from([...referenced]).forEach(function (name) {
    for (var i = 0; i < sources.length; i++) {
        var src = sources[i];
        if (!src) continue;             // <-- this fires when window.lucide is undefined
        var v = src[name];
        // ...
    }
});
```

The catch-all lift (lines 334-348) also requires `window.lucide` to be populated. Without the script tag, both passes are no-ops.

---

## Two fix strategies

### Strategy A — Always inject the lucide UMD (~615 KB, cached)

**Change line 220-221:**

```js
const lucideScript = `
  <script src="https://unpkg.com/lucide@latest/dist/umd/lucide.js"><\/script>
`;
```

Delete the `usesLucide` conditional. The 615 KB payload is downloaded once per browser per CDN cache TTL (~24h on unpkg) and served from cache thereafter. With the catch-all lift at line 334-348 already in place, **every** PascalCase key from `window.lucide` becomes a globally available icon component.

**Pros:** Bulletproof. Future-proof. No more regex maintenance as lucide adds icons.
**Cons:** +615 KB initial iframe load for every React viz. Mitigated by browser cache; only matters on first visit per session per browser.

### Strategy B — Widen the regex to ~150 icons (no payload cost, fragile)

**Change line 104 to enumerate every common lucide icon**, e.g.:

```js
const usesLucide = /lucide|LucideIcon|import.*from.*['"](lucide|lucide-react)['"]|\b(TrendingUp|TrendingDown|Briefcase|Calendar|DollarSign|Users|Activity|BarChart3|BarChart|BarChart2|LineChart|PieChart|AreaChart|Filter|Search|Bell|Mail|Check|X|Plus|Minus|Edit|Trash|Download|Upload|Eye|Lock|Unlock|ArrowRight|ArrowLeft|ArrowUp|ArrowDown|ChevronRight|ChevronDown|ChevronUp|ChevronLeft|ChevronUpCircle|ChevronDownCircle|Home|User|Users|UserPlus|UserMinus|UserCheck|UserX|Settings|Star|Heart|Camera|Image|File|FileText|Folder|FolderOpen|Save|Printer|Share|Link|Globe|Map|MapPin|Phone|PhoneCall|MessageSquare|MessageCircle|Send|Paperclip|Bookmark|Tag|Flag|Calendar|Days|Clock|Watch|Timer|Sun|Moon|Cloud|CloudRain|CloudSnow|Wind|Droplet|Flame|Umbrella|Zap|Battery|BatteryCharging|Wifi|WifiOff|Volume|Volume2|VolumeX|Mic|MicOff|Play|Pause|SkipForward|SkipBack|Refresh|RotateCw|RotateCcw|RotateCcw|Repeat|Shuffle|Loader|Loader2|Circle|Square|Triangle|Hexagon|Octagon|Pentagon|Database|Server|HardDrive|Cpu|Monitor|Smartphone|Tablet|Laptop|Code|Terminal|GitBranch|GitCommit|GitMerge|GitPullRequest)\b/i.test(jsxContent);
```

**Pros:** Zero payload cost. Icons only load when actually used.
**Cons:** Brittle. Every new AI prompt that uses an icon outside the list reproduces the bug. Have to maintain a list of 150+ strings. Users will keep hitting edges.

### **Recommended: Strategy A** (always inject)

The robustness gain is worth the cached 615 KB. Lucide is already lazy — the user's browser caches it after the first React viz with any lucide icon. Strategy A is "fix it once, never touch it again."

---

## Exact edit (Strategy A)

**File:** `UI/visualisation_engine/react_renderer.js`

**Lines 220-221:**

```js
        const lucideScript = usesLucide
            ? `  <script src="https://unpkg.com/lucide@latest/dist/umd/lucide.js"><\/script>` : '';
```

**Replace with:**

```js
        // Always inject the lucide UMD. The detection regex below is brittle
        // (only ~30 hand-picked icons) and the AI emits PascalCase JSX tags
        // without explicit `import` statements, so by the time we know an
        // icon is needed, the hoist block has already run. The 615 KB
        // payload is cached by the browser; subsequent React viz loads are
        // O(ms). Strategy: always inject, always lift, always wrap as a
        // functional React component. See REACT_RENDERER_LUCIDE_TROUBLESHOOTING
        // _2026-07-22.md for the full rationale.
        const lucideScript = `
  <script src="https://unpkg.com/lucide@latest/dist/umd/lucide.js"><\/script>`;
```

**Optional cleanup — delete the now-unused `usesLucide` regex (line 104).** Keep the variable for one release cycle so the rest of the file still compiles (it's referenced at line 220 currently — replaced above). After this change, line 104 is dead code but harmless; remove in a follow-up commit.

**No other code changes required.** The existing hoist block (lines 266-348), the `makeIconComponent` factory, the catch-all lift loop, and the `__EXPORT_DATA__`/`__EXPORT_HANDLER__` extensions all work unchanged.

---

## Verification

After applying the fix:

1. **Hard reload** the SPA in Chrome (Ctrl+Shift+R).
2. **Open DevTools → Console.** Clear it.
3. **Paste this minimal repro into a chat** (or open an existing failing dashboard):

   ```jsx
   <div style="display:flex;gap:16px;padding:24px;">
     <TrendingUp size={32} color="#3b82f6" />
     <Briefcase size={32} color="#10b981" />
     <Calendar size={32} color="#f59e0b" />
     <DollarSign size={32} color="#ef4444" />
     <Users size={32} color="#8b5cf6" />
     <Activity size={32} color="#06b6d4" />
     <BarChart3 size={32} color="#84cc16" />
     <Filter size={32} color="#ec4899" />
   </div>
   ```

4. **Confirm:**
   - No `ReferenceError: TrendingUp is not defined` in console.
   - Iframe renders 8 icons in a row.
   - `[REACT_RENDERER] hoisted identifiers from lucide/Recharts: [...]` log shows ~1500 entries from the catch-all lift.
5. **Open Network tab.** Confirm `lucide.js` loaded once (status 200). Reload — confirm cached (status 200 from disk cache).
6. **Click the iframe's "panel" button** (existing viz-popup-manager). Confirm the popup also renders icons correctly (popup re-uses the same srcdoc).

### If still broken

If the icon ReferenceErrors persist after the fix:

1. **Confirm `lucide.js` is being requested.** DevTools → Network → filter `lucide`. If absent, the renderer's srcdoc was cached — hard-reload again or close-and-reopen the tab.
2. **Confirm `window.lucide` exists inside the iframe.** Open DevTools → Console, find the iframe via Elements panel, type in the console (with the iframe context selected): `Object.keys(window.lucide).length`. Should return >1000.
3. **Confirm hoist ran.** Check console for `[REACT_RENDERER] hoisted identifiers from lucide/Recharts: …`.
4. **Confirm the AI's exact JSX is what you expect.** If the AI emitted `import { TrendingUp } from 'lucide-react'` (i.e. it tried to import), Babel will throw because `import` is stripped but the named export `TrendingUp` was never bound. Mitigation: the hoist block in the renderer should still bind `window.TrendingUp = makeIconComponent('TrendingUp', window.lucide.TrendingUp)`. If it doesn't, check the regex on line ~104 — `import.*from.*['"](lucide|lucide-react)['"]` should make `usesLucide` true, but with Strategy A we no longer rely on it.
5. **Check the cache-buster.** `business-ai-platform-v2.html:808` loads `react_renderer.js?v=<date>`. If you bumped the renderer but not the SPA, the SPA serves a stale iframe. Bump both in the same commit.

---

## Rollout checklist

- [ ] Apply Strategy A edit to `UI/visualisation_engine/react_renderer.js`.
- [ ] Bump cache-buster on the SPA: `UI/business-ai-platform-v2.html:808` → `?v=20260722_1200` (or later).
- [ ] Run `./.vscode/fix-bom.ps1`.
- [ ] Run `node --check UI/visualisation_engine/react_renderer.js`.
- [ ] Commit: `git commit -m "fix(react-renderer): always inject lucide UMD so all PascalCase icons resolve"`.
- [ ] Push: `git push gerardo v11:v11`.
- [ ] Wait ~60s for Render deploy.
- [ ] Hard-reload SPA in Chrome.
- [ ] Run the verification block above.

---

## Related history

- `b24cc2ac` — ErrorBoundary + initial lucide/Recharts auto-hoist.
- `048132a6` — Dropped dangling `${lucideSetup}` reference.
- `221f1ed1` — Wrapped hoisted lucide arrays as React SVG components (`makeIconComponent` factory).
- `c8078410` — AST-based module strip.
- This doc — identifies that the hoist block is correct, but the lucide UMD never loads for many AI-emitted icons due to brittle detection regex.

---

## Hand-off instructions for the next agent

If you're reading this because the user gave you a session where `ReferenceError: TrendingUp is not defined` is back:

1. Read this doc end-to-end before touching the renderer.
2. Don't add a new regex pattern to `usesLucide` — that's Strategy B and it's a maintenance trap.
3. Apply Strategy A (always inject) and verify with the test JSX above.
4. If the user is on Strategy B and wants to keep payload small, walk them through the tradeoff in this doc.
5. The broader Tier-1 toolbar + viz_snapshots + AI tools plan lives in `REACT_ENHANCEMENT_TODO_2026-07-22.md` and is independent of this fix. Once the renderer works, that plan is the next priority.

---

## Open questions / risks

1. **CDN availability.** `unpkg.com` is reliable but not guaranteed. Consider pinning to `https://unpkg.com/lucide@0.460.0/dist/umd/lucide.js` (or whatever the latest stable is at deploy time) to avoid breaking-changes from a `@latest` bump. **Add this if Strategy A is kept long-term.**
2. **CDN dependency for production.** If unpkg is blocked in some deployment environments (corporate firewalls, Render region restrictions), the iframe goes blank. Mitigation: self-host `lucide.js` from `/static/` and update the script src.
3. **Bundle size impact.** 615 KB is non-trivial for low-bandwidth users. Browser cache mitigates after first load. If this becomes a real complaint, fall back to Strategy B with a deliberately-maintained icon-allowlist.
4. **lucide-react vs lucide.** `lucide@latest/dist/umd/lucide.js` is the vanilla (non-React) UMD — exports raw icon descriptor arrays. `lucide-react` is the npm package that wraps them in React components. We want the former (UMD), because the renderer's `makeIconComponent` factory does the React wrapping itself. Confirm via `head -1 $(curl -s https://unpkg.com/lucide@latest/dist/umd/lucide.js)` — should show a UMD banner, not an ES module.

---

## Quick reference: the failing example

```jsx
function App() {
  return (
    <div style={{padding: 24}}>
      <h1>Sales Dashboard</h1>
      <div style={{display:'flex',gap:16}}>
        <TrendingUp size={28} className="text-blue-600" />
        <Briefcase />
        <Calendar />
        <DollarSign />
        <Users />
        <Activity />
        <BarChart3 />
        <Filter />
      </div>
    </div>
  );
}
```

This is the exact AI-emitted JSX that fails today. Strategy A fixes it without further code changes.
