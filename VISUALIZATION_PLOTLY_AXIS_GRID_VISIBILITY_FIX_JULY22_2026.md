# Plotly Axis/Grid Visibility Fix — July 22, 2026

> **Purpose.** Documents the follow-on Plotly axis/grid/line invisibility bug
> that surfaced after the always-white canvas fix in
> `VISUALIZATION_CANVAS_BG_AND_FULLSCREEN_FIX_JULY22_2026.md`. Read that
> doc first for context.

## Overview

After the always-white canvas shipped in the previous fix, the user reported
that **3D scatter plot axes, plot lines, and the background grid were all
invisible**. Investigation showed two layered root causes:

1. **`gridColor = '#e1e4e8'` is invisible on `#ffffff`.** That colour is
   GitHub's "border-default" tone (~1.2:1 contrast ratio on pure white) — it
   reads as "very subtle hairline" on real charts and effectively disappears
   inside a Plotly chart where the surrounding UI border is also light grey.
   For chart axes and grid lines, we need a mid-tone slate with at least
   ~2.5:1 contrast.

2. **The 2D Cartesian branch of `applyEnhancedPlotlyTheme` had no axis
   theming at all.** `baseLayout` (L3151) only set `paper_bgcolor`,
   `plot_bgcolor`, and `legend` — never `xaxis` or `yaxis`. So bar, line,
   scatter, **box**, histogram, and area charts fell through to Plotly's
   `'#eee'` template default, which is also essentially invisible on white.
   This is also why the user's box-plot test rendered with invisible axes.

3. **`toggle3DView` did not set scene-axis colours.** When the user clicked
   "Switch to 3D View" on a 2D chart, the synthesised 3D scene only declared
   `{ title: '...' }` per axis — leaving grid/line/tick at Plotly defaults.
   For 3D specifically these defaults are different from 2D and they were
   similarly invisible on white.

4. **`updateTheme` / `updateChartTheme` did not touch `scene.*` paths.**
   Even if the user toggled the UI theme after a 3D chart had rendered, the
   `Plotly.relayout(...)` calls only set 2D `xaxis.*`/`yaxis.*` — 3D scene
   axes were stuck at whatever was originally drawn.

## Root Cause Analysis

### Cause 1 — `'#e1e4e8'` is too pale

Contrast ratios on `#ffffff` background:

| Colour | Hex | Contrast | Verdict |
|---|---|---|---|
| Pre-fix gridColor | `#e1e4e8` | ~1.18:1 | Invisible |
| Plotly template default | `#eeeeee` | ~1.17:1 | Invisible |
| New `gridColor` | `#94a3b8` (Tailwind slate-400) | ~2.85:1 | Clearly visible |
| New `axisLineColor` | `#7c8694` (slate-500-ish) | ~4.25:1 | Strongly visible |
| New `zeroLineColor` | `#cbd5e1` (slate-300) | ~1.7:1 | Soft, optional |

Chart axes and grid lines need to be **at least** ~2:1 contrast for users
to perceive them as deliberate markings (WCAG only requires 3:1 for
non-text UI components, but Plotly charts are dense enough that 2.5:1+
reads as crisp).

### Cause 2 — `baseLayout` had no Cartesian axis theming

Before this fix the Cartesian branch was:

```js
plotlyData.layout = {
    ...baseLayout,        // (A) no xaxis/yaxis in baseLayout
    ...plotlyData.layout, // (B) AI layout spread (only adds xaxis if AI provided one)
    margin: {...},
    height: 700,
    bargap: 0.15,
    bargroupgap: 0.05,
    ...
};
```

If the AI emitted `xaxis: { title: 'Month' }` with no colour specs, the
spread resulted in no colour overrides — Plotly filled in `'#eee'` from
its template. Adding `xaxis`/`yaxis` objects to `baseLayout` at A slots
the colours in BEFORE the AI's spec, so AI-provided colours still win
when present, and our defaults fill the gap when the AI omits them.

### Cause 3 — `toggle3DView` synthesised scene with no axis colours

Pre-fix code:
```js
const layout3D = {
    title: 'Interactive 3D Surface',
    scene: {
        xaxis: { title: 'X Axis (units)' },
        yaxis: { title: 'Y Axis (units)' },
        zaxis: { title: 'Z Axis (units)' }
    },
    paper_bgcolor: bgColor,
    font: { color: textColor },
    margin: { l: 0, r: 0, b: 0, t: 40, pad: 0 }
};
```

No `gridcolor`/`linecolor`/`tickcolor` per axis, no `scene.bgcolor`.
Fixed by adding the same colour object as the AI-3D path.

### Cause 4 — `updateTheme` and `updateChartTheme` skipped 3D

Both called `Plotly.relayout(chartId, { ... 2D paths ... })`. Adding a
trace-type sniff (identical to `applyEnhancedPlotlyTheme`'s
`chartTypes.has('3d')` detection) lets us push `scene.*` paths only when
the chart actually uses a 3D trace type. This avoids pushing invalid paths
to 2D charts.

## Fixes

### Fix 1 — Strengthen grid/line/zero colours and add 3 explicit constants

In `applyEnhancedPlotlyTheme` (file `UI/visualisation_engine/visualisation_v3.js`):

```js
const bgColor = '#ffffff';
const textColor = '#24292f';
const gridColor = '#94a3b8';      // was '#e1e4e8' — too pale
const axisLineColor = '#7c8694';   // NEW: axis lines (darker than grid for separation)
const zeroLineColor = '#cbd5e1';   // NEW: zero reference line (lighter, optional accent)
```

### Fix 2 — Add 2D `xaxis`/`yaxis` to `baseLayout`

Same file, function `applyEnhancedPlotlyTheme`, the `baseLayout` constant:

```js
xaxis: {
    gridcolor: gridColor,
    linecolor: axisLineColor,
    tickcolor: axisLineColor,
    zerolinecolor: zeroLineColor,
    zerolinewidth: 1,
    tickfont: { color: textColor }
},
yaxis: {
    gridcolor: gridColor,
    linecolor: axisLineColor,
    tickcolor: axisLineColor,
    zerolinecolor: zeroLineColor,
    zerolinewidth: 1,
    tickfont: { color: textColor }
},
```

Spread order in the per-chart-type branches is `...baseLayout, ...plotlyData.layout`,
so AI-supplied `xaxis`/`yaxis` properties still win when present. Defaults
fill the gap when the AI omits them.

### Fix 3 — Add `zerolinecolor` and `showgrid` to scene axes

Same function, 3D branch:

```js
xaxis: {
    gridcolor: gridColor,
    linecolor: axisLineColor,
    tickcolor: axisLineColor,
    zerolinecolor: zeroLineColor,
    zerolinewidth: 2,
    showgrid: true,
    tickfont: { color: textColor, size: 10 },
    ...plotlyData.layout.scene?.xaxis   // AI's props still merged last
},
```

(yaxis and zaxis get the same treatment.)

### Fix 4 — `toggle3DView` synthesised scene now uses the same colours

Function `toggle3DView`, the `layout3D` object:

```js
const layout3D = {
    title: 'Interactive 3D Surface',
    scene: {
        bgcolor: bgColor,
        xaxis: { title: 'X Axis (units)', gridcolor, linecolor, tickcolor, zerolinecolor, zerolinewidth: 2, tickfont: { color: textColor } },
        yaxis: { title: 'Y Axis (units)', ... },
        zaxis: { title: 'Z Axis (units)', ... }
    },
    paper_bgcolor: bgColor,
    plot_bgcolor: bgColor,
    font: { color: textColor },
    margin: { l: 0, r: 0, b: 0, t: 40, pad: 0 }
};
```

### Fix 5 — `updateTheme` (theme-toggle retroactive recolor) now also relayouts scene.*

Function `updateTheme`, the `updateObj` literal:

```js
const is3D = Array.isArray(element.data) && element.data.some(trace => {
    const t = (trace?.type || 'scatter').toLowerCase();
    return ['scatter3d', 'surface', 'mesh3d', 'cone', 'streamtube', 'volume', 'isosurface'].includes(t);
});
if (is3D) {
    updateObj['scene.bgcolor'] = bgColor;
    ['xaxis', 'yaxis', 'zaxis'].forEach(axisKey => {
        updateObj[`scene.${axisKey}.gridcolor`] = gridColor;
        updateObj[`scene.${axisKey}.linecolor`] = axisLineColor;
        updateObj[`scene.${axisKey}.tickcolor`] = axisLineColor;
        updateObj[`scene.${axisKey}.zerolinecolor`] = zeroLineColor;
        updateObj[`scene.${axisKey}.tickfont.color`] = textColor;
    });
}
```

The trace-type sniff mirrors `applyEnhancedPlotlyTheme`'s `chartTypes.has('3d')`
detection — avoids pushing invalid paths to 2D charts.

### Fix 6 — `updateChartTheme` mirror

Function `updateChartTheme` got the same addition inside its `case 'plotly':`
block — including the trace-type sniff and the `scene: { ... }` relayout.

## Impact Analysis

| Chart type | Before this fix | After this fix |
|---|---|---|
| 2D box plot | axes invisible (Plotly `#eee` on white) | axes/grid/tick clearly visible |
| 2D bar/line/scatter | axes invisible (Plotly `#eee` on white) | axes/grid/tick clearly visible |
| 2D histogram / area | axes invisible (Plotly `#eee` on white) | axes/grid/tick clearly visible |
| 3D scatter (AI emits minimal scene) | scene axes invisible | scene axes/grid/tick/zero-line clearly visible |
| 3D surface (synthesised by `toggle3DView`) | scene axes invisible | scene axes/grid/tick/zero-line clearly visible |
| 3D chart, theme toggled | scene axes stuck at original | scene axes update on next relayout |
| Polar / Ternary / Geo / Hierarchical | unchanged | unchanged (their branches had `gridcolor` etc.) |

## Testing Checklist

1. AI-generated 3D scatter (the user's example) — confirm axes/gridlines
   are clearly visible in both light and dark UI mode (canvas stays white
   either way, dark text/lines on it).
2. AI-generated box plot with 3+ categories — confirm box outlines,
   median lines, and axis ticks/gridlines are all legible.
3. Click "Switch to 3D View" on a 2D chart → confirm the synthesised
   3D scene has visible axes and grid on the white canvas.
4. Toggle UI theme with a 3D chart open → confirm the scene axes get
   re-themed (relayout wired).
5. Toggle UI theme with a box plot open → confirm 2D axes get
   re-themed (use the existing `updateTheme` path).
6. Export a 3D chart to PNG → confirm exported PNG has white canvas
   and dark visible axes (Plotly's `paper_bgcolor`/`plot_bgcolor`
   export still wins; our grid colours apply to the rendered SVG).
7. `node --check UI/visualisation_engine/visualisation_v3.js` → confirm no syntax errors.
8. BOM byte-check on the touched file → `BOM_FREE`.
9. `git status` shows only the targeted file modified (no
   unrelated staged/unstaged work).

## Files Modified

| File | Lines | Change |
|---|---|---|
| `UI/visualisation_engine/visualisation_v3.js` | L3092-3108 | Added 3 colour constants + comment block |
| `UI/visualisation_engine/visualisation_v3.js` | L3151-3202 | Added `xaxis`/`yaxis` to `baseLayout` |
| `UI/visualisation_engine/visualisation_v3.js` | L3266-3326 | Strengthened scene-axis theming (zerolinecolor + showgrid) |
| `UI/visualisation_engine/visualisation_v3.js` | L4295-4337 | `toggle3DView` adds `scene.*` colours |
| `UI/visualisation_engine/visualisation_v3.js` | L9460-9558 | `updateTheme` adds scene relayout + colour refresh |
| `UI/visualisation_engine/visualisation_v3.js` | L9483-9567 | `updateChartTheme` adds scene relayout + colour refresh |

(Six logical edits, all in the same file. Net: +170 lines, -18 lines.)

## Rollback Information

`git revert <sha>` of the commit, or `git reset --hard HEAD~1` if the
fix isn't yet pushed. No data migration; no DB migration; no schema
change; no API change. Pure client-side JS colour tweaks.

If the new grid colour `#94a3b8` reads as too dark in your monitor's
calibration, bump it down to `#aab2bd` (slate-300-ish) — same fix shape.
The new colours are all literal hex, so a single-line tweak is enough.

## Related Documentation

- `VISUALIZATION_CANVAS_BG_AND_FULLSCREEN_FIX_JULY22_2026.md` — predecessor,
  established the always-white canvas and removed the `isDark` parameter
  crash. Read first for context.
- `VISUALIZATION_MERMAID_RENDERING_FIX_JULY22_2026.md` — earlier, fixed
  the Mermaid staging-element rendering crash.
- `UI/visualisation_engine/VISUALIZATION_SYSTEM_DOCUMENTATION.md` — master
  doc; bumped with a cross-reference to this file.
- Plotly docs — scene axes use `scene.xaxis.*` paths, NOT `layout.xaxis.*`.
  This was the conceptual trap behind the original bug.

## Deployment Notes

- No backend change. Pure frontend JS.
- No migration. No API change. No env-var change.
- Deploy via `git push gerardo v11:v11` (Render auto-deploys).
- After deploy, refresh the browser tab hard (Ctrl+Shift+R) to clear the
  cached `visualisation_v3.js`.

---

**Author:** AI coding agent (Claude)
**Date:** July 22, 2026
**Pair-fix with:** `VISUALIZATION_CANVAS_BG_AND_FULLSCREEN_FIX_JULY22_2026.md`
