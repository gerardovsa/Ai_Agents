# Visualization Mermaid Rendering Fix — July 22, 2026

## Overview

Critical fix to the Mermaid 10.x render path so that pie charts and flowcharts
render with a positive SVG viewBox on the first attempt, instead of emitting
`viewBox="0 0 0 450"` (pies) or throwing `Could not find a suitable point for
the given distance` from `calcLabelPosition` (flowcharts).

**Problem:** The visualisation engine's SPA-level global CSS rule
`body > [id^="dmermaid"] { display: none !important; }` was originally added to
hide "any mermaid syntax-error elements injected outside viz-containers". The
selector accidentally matched Mermaid's *legitimate render-staging element*
(`d{renderId}`), not just error overlays. With `display: none`, the staging
div's `getBoundingClientRect()` collapsed to `{ width: 0, height: 0 }`, so
Mermaid computed geometry against a zero-width canvas.

**Symptom:**
- Pies emitted `viewBox="0 0 0 450"` (450 is Mermaid's hard-coded default pie
  height; width collapsed to 0). The visualisation engine's bounded retry
  pipeline (MAX_MERMAID_RETRIES=2) then surfaced a real error via
  `showMermaidError()` after three attempts.
- Flowcharts threw "Could not find a suitable point for the given distance"
  from `calcLabelPosition` because edge routing had no horizontal room.

**Fix:** Replace the SPA-level `display: none` rule with an
*off-screen-but-measurable* positioning block so Mermaid can still read the
staging div's bounding rect without ever painting it to the visible viewport.
Also revert the Phase 3 (`pie: { useMaxWidth: false }`) attempt — `useMaxWidth`
only governs post-render CSS scaling, not the viewBox itself.

---

## Root Cause Analysis

Mermaid 10.x's render pipeline:

```
mermaid.render(id, source)
  → creates a body-level <div id="d{id}">   (staging element)
  → measures staging element's bounding rect
  → runs d3-shape / dagre layout against that rect
  → writes final SVG into the visible container
```

The visible SVG is then auto-scaled to fit via the `useMaxWidth: true` flag
(which only affects post-render CSS — `max-width: 100%` on the resulting SVG
element — not the viewBox itself).

`display: none` collapses the staging element to `{0, 0, 0, 0}`. Mermaid's
d3-shape pie layout collapses the radius to 0 and emits a 0-width viewBox.
Mermaid's dagre flowchart layout cannot find horizontal room for edge labels
and throws `calcLabelPosition` constraint-failure.

**Why V7_MustCare did not hit this:** V7_MustCare does not have any SPA-level
CSS that matches `[id^="dmermaid"]` or `[id^="d-mermaid"]`. The defensive rule
in `business-ai-platform-v2.html` is unique to this project.

**Why Phase 3 (`pie: { useMaxWidth: false }`) did not work:** `useMaxWidth`
governs only the post-render `max-width: 100%` CSS on the resulting SVG. It
does **not** affect the viewBox value Mermaid computes during the layout step.
If the staging element is 0-wide, the viewBox is 0-wide regardless of
`useMaxWidth`. Phase 3 was reverted on July 22, 2026.

---

## Fix #1: Off-Screen-But-Measurable Staging CSS

### **Location:** `UI/business-ai-platform-v2.html` lines ~10730-10755

### **Before:**
```css
body > [id^="dmermaid"] {
    display: none !important;
}
```

### **After:**
```css
/*
 * Mermaid 10.x creates a body-level staging element with id `d{renderId}`
 * while `mermaid.render()` measures layout. `display: none` collapses that
 * staging div to 0x0, causing pies to emit `viewBox="0 0 0 450"` and
 * flowcharts to throw "Could not find a suitable point for the given
 * distance" from `calcLabelPosition`. The staging div MUST remain in the
 * layout tree with a measurable width. Keep it off-screen but measurable
 * so it is never visible to the user but Mermaid can still read its
 * bounding rect.
 */
body > [id^="dmermaid"] {
    position: fixed !important;
    top: -10000px !important;
    left: -10000px !important;
    visibility: hidden !important;
    pointer-events: none !important;
    min-width: 700px !important;
    display: block !important;
}

/* Hide orphan .mermaid containers that escaped a viz-container. */
body > .mermaid:not(.viz-container .mermaid) {
    display: none !important;
}
```

**Why this works:**
- `position: fixed` removes the element from normal flow but keeps it in the
  layout tree.
- `top: -10000px; left: -10000px;` parks it well outside the visible viewport.
- `visibility: hidden` ensures no paint flash on slow renders.
- `pointer-events: none` blocks any accidental mouse interaction.
- `min-width: 700px` gives Mermaid enough horizontal room for flowchart edge
  routing and pie label placement even in a narrow chat column.
- `display: block` overrides Mermaid's `display: inline` default so the box
  actually takes a measurable width.

**Why the orphan-`.mermaid` selector is still safe:**
`body > .mermaid:not(.viz-container .mermaid)` matches a `.mermaid`-class
element that escaped a `.viz-container` wrapper — that is genuinely an orphan
and should be hidden. It does NOT match Mermaid's staging element (which uses
an `id`, not a `class`). The two rules serve distinct purposes and neither
cancels the other.

---

## Fix #2: Revert Phase 3 `pie: { useMaxWidth: false }`

### **Location:** `UI/visualisation_engine/visualisation_v3.js` lines ~4474-4492 (removed)

The Phase 3 attempt (commit `38fb9493`) configured `pie: { useMaxWidth: false }`
inside `mermaid.initialize()` based on a hypothesis that the post-render
`useMaxWidth` rescale was collapsing pie width to 0. This was incorrect:
`useMaxWidth` only governs the post-render CSS scale, not the layout-time
viewBox. The 17-line block (14 lines of comment + 3 lines of config) was
removed; the engine now relies on Fix #1 (the staging CSS) to make the
viewBox positive on the first render.

---

## Container Architecture (For Understanding)

```
mermaid.render(id, source)
  → creates staging element  body > div#d{id}     (kept off-screen, measurable)
  → writes final SVG       into #viz-container-{id} > .viz-content-area
                              ├── <svg viewBox="0 0 W H">   ← now W > 0, H > 0
                              └── useMaxWidth: true scales visible SVG to fit
```

**Before:** staging element was `display:none` → `viewBox="0 0 0 H"` → validator
rejected → bounded retry → `showMermaidError()`.
**After:** staging element is measurable → `viewBox="0 0 W H"` with W > 0 →
valid on the first attempt → no retry needed.

---

## Impact Analysis

### **Before Fix:**
- Pies: 🔴 **`viewBox="0 0 0 450"` on first render** → retry storm → error
- Flowcharts (TD): 🔴 **`calcLabelPosition` failure** → retry storm → error
- Flowcharts (LR): 🟡 Apparently rendered (because LR's layout path uses a
  separate chart-id prefix that did not hit the validator) — masking the bug
- Other diagram types (sequence, gantt, class): 🟡 Intermittently broken

### **After Fix:**
- Pies: 🟢 **Renders on first attempt** with positive viewBox
- Flowcharts (TD and LR): 🟢 **Renders on first attempt**, no `calcLabelPosition`
- All diagram types: 🟢 First-attempt success
- Retry pipeline: 🟢 Idempotent safety net (still capped at 2 retries, but
  rarely needed)

---

## Testing Checklist

### **Quick Test (Browser Console):**
1. Open any thread containing a Mermaid pie or flowchart.
2. Inspect the rendered SVG: `viewBox` should start with two positive numbers
   (e.g. `viewBox="0 0 450 450"` for pies, or `viewBox="0 0 800 600"` for
   flowcharts).
3. Watch the console for `calcLabelPosition` errors — should NOT appear.
4. Watch the console for retry messages — should NOT see more than 0-1 retries.

### **Full Test Scenarios:**

#### **Test 1: Pie chart**
1. Send a message containing a `pie` diagram (any valid Mermaid pie).
2. ✅ SVG renders with a positive viewBox.
3. ✅ Slices are visible and colored.
4. ✅ No console errors.

#### **Test 2: Flowchart TD**
1. Send a message containing a `flowchart TD` with at least 3 nodes.
2. ✅ Edges route correctly between nodes.
3. ✅ No `calcLabelPosition` error in console.
4. ✅ Renders on first attempt (no retry storm).

#### **Test 3: Flowchart LR (regression)**
1. Send a `flowchart LR` with 3+ nodes.
2. ✅ Layout switches to left-right.
3. ✅ Edges route correctly.
4. ✅ Positive viewBox.

#### **Test 4: Hidden staging element**
1. Open browser DevTools → Elements tab.
2. Trigger a Mermaid render.
3. Inspect the DOM: there should be a `body > div#d{mermaid-...}` element
   with `position: fixed; top: -10000px; visibility: hidden;` — confirm it
   exists and is NOT visible.
4. After the render settles, Mermaid removes the staging element itself
   (verify it disappears from the DOM without us having to clean it up).

---

## Files Modified

| File | Lines | Changes |
|------|-------|---------|
| `UI/business-ai-platform-v2.html` | ~10730-10755 | Replaced `display:none` with off-screen-but-measurable positioning for `body > [id^="dmermaid"]` |
| `UI/visualisation_engine/visualisation_v3.js` | ~4474-4492 (removed) | Reverted `pie: { useMaxWidth: false }` block + 14-line comment |
| `UI/visualisation_engine/visualisation_v3.js` | ~895 (added) | Header comment above `mermaid.initialize()` documenting the staging-element invariant |
| `UI/visualisation_engine/VISUALIZATION_SYSTEM_DOCUMENTATION.md` | L4 | Bumped "Last updated" → July 22, 2026 |
| `UI/visualisation_engine/VISUALIZATION_SYSTEM_DOCUMENTATION.md` | L40-61 | Rewrote "Mermaid Render Lifecycle" (now 3 invariants), renamed "Staging vs. visible width" → "Off-screen-but-measurable staging CSS" |

---

## Rollback Information

If a behavioural regression occurs (e.g. a future agent reintroduces the
`display: none` rule on `[id^="dmermaid"]`):

```bash
# Revert all changes from this fix
git checkout 3671ef9d~1 -- UI/business-ai-platform-v2.html
git checkout 3671ef9d~1 -- UI/visualisation_engine/visualisation_v3.js
git checkout 3671ef9d~1 -- UI/visualisation_engine/VISUALIZATION_SYSTEM_DOCUMENTATION.md

# Or surgically revert just the SPA CSS rule (line ~10739):
# Replace the entire body > [id^="dmermaid"] { ... } block with:
#     body > [id^="dmermaid"] { display: none !important; }
# (This restores the bug; only do this as a temporary stop-gap while a
#  proper fix is developed.)
```

The fix is low-risk to roll back because no API, schema, or environment
variable changed.

---

## Related Documentation

- [Visualization System Architecture Documentation](UI/visualisation_engine/VISUALIZATION_SYSTEM_DOCUMENTATION.md) — the centralised master doc (long-form reference).
- [Visualization Streaming Fixes — April 9, 2026](VISUALIZATION_STREAMING_FIXES_APRIL9_2026.md) — the precedent for this dated fix-log format.
- [Mermaid 10.x official docs on render lifecycle](https://mermaid.js.org/) — external reference for the `mermaid.render(id, source)` signature.

---

## Deployment Notes

✅ **Safe to deploy immediately:**
- No API changes
- No schema migrations needed
- No breaking changes to existing visualizations
- Backward compatible with all renderer implementations
- The fix is a pure CSS + comment-rewrite change in 3 files

✅ **Monitor after deployment:**
- Browser console: `calcLabelPosition` errors should disappear.
- Browser console: retry-pipeline messages should appear 0-1 times instead of 2-3.
- Network panel: no new requests (pure client-side fix).
- Visual: pies and flowcharts should render correctly on the first attempt.

---

**Date:** July 22, 2026
**Status:** ✅ Complete and Pushed to `gerardo v11`
**Commit:** [`3671ef9d`](https://github.com/gerardovsa/Ai_Agents/commit/3671ef9d) — *fix(visualisation): keep Mermaid staging element measurable via off-screen positioning*
**Severity:** Critical (fixes broken pie and flowchart rendering in production)