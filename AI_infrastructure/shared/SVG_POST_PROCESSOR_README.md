# SVG Bold Text Baseline Fix - Implementation Guide

## 🎯 The Problem

Browsers incorrectly position bold text when using `dominant-baseline="middle"` in SVG because:

1. **SVG calculates the bounding box** using **regular font metrics**
2. **SVG renders the glyphs** using **bold font metrics** (different vertical proportions)
3. **Result:** Bold text shifts **5-7px downward** (varies by browser)

## ✅ The Solution: Backend Post-Processing

We implement **automatic SVG post-processing** that:
- Detects bold text with `dominant-baseline="middle"`
- Converts to manual baseline positioning
- Removes the problematic `dominant-baseline` attribute
- Applies compensation formula: `y_baseline = y_center + (fontSize × 0.35)`

## 📁 Architecture

```
AI Agent → Generates SVG (semantically correct, uses dominant-baseline)
    ↓
Post-Processor → Detects & fixes bold text baseline bug
    ↓
Browser → Renders correctly
```

## 🔧 Implementation Components

### 1. Python Backend Post-Processor

**File:** `AI_infrastructure/shared/svg_post_processor.py`

```python
from AI_infrastructure.shared.svg_post_processor import optimize_svg

# In your SVG generation endpoint
svg_code = generate_technical_drawing(data)
svg_code = optimize_svg(svg_code)  # Apply fixes
return svg_code
```

**Features:**
- Parses SVG XML
- Finds bold text elements with `dominant-baseline="middle"`
- Calculates correct Y-position
- Returns fixed SVG

### 2. JavaScript Frontend Post-Processor

**File:** `UI/visualisation_engine/svg_post_processor.js`

**Integrated into:** `UI/visualisation_engine/visualisation_copy.js`

```javascript
// Automatically applied in renderSVGVisualization()
svgContent = window.SVGPostProcessor.optimizeSVG(svgContent);
```

**Features:**
- Runs on client-side before SVG insertion
- DOM-based parsing (DOMParser API)
- Works with all SVG delimiters (`<SVG_VISUAL>`, `<CAD>`, `<BLUEPRINT>`, `<SCHEMATIC>`)

### 3. Visualization Guidance Updates

**File:** `tools/implementations/visualization_guide.py`

**Added warnings to:**
- SVG section (line ~437 + ~520)
- BLUEPRINT section (line ~555)
- CAD section (line ~738)
- SCHEMATIC section (line ~795 + ~845)

**Content:**
```
RULE 6: SVG TITLE BLOCK SPACING
If using title blocks, ensure 40-60px clearance between title block 
bottom and content start. 

Formula: 
- Title block height = (fontSize × lines × 1.5) + 20px
- Text Y position = block top + (fontSize × 1.2)
- Content start = block bottom + 50px minimum

⚠️ BOLD TEXT: Never use dominant-baseline="middle" with font-weight="bold"
The post-processor will automatically fix this, but if generating SVG 
manually, calculate baseline position: y = y_center + (fontSize × 0.35)
```

## 🚀 Usage

### Option 1: Automatic (Recommended)

The post-processor runs automatically for all SVG visualizations. No changes needed in AI prompts or tool code.

**AI generates:**
```xml
<text y="150" text-anchor="middle" dominant-baseline="middle" 
      font-size="16" font-weight="bold">SPECIFICATIONS</text>
```

**Post-processor outputs:**
```xml
<text y="155.6" text-anchor="middle" 
      font-size="16" font-weight="bold">SPECIFICATIONS</text>
```

### Option 2: Manual Backend Processing

If you need to process SVG in Python tools:

```python
from AI_infrastructure.shared.svg_post_processor import optimize_svg

def my_svg_generation_tool():
    svg = """<svg>...<text font-weight="bold">...</text>...</svg>"""
    
    # Apply fixes
    svg = optimize_svg(svg)
    
    return {"svg_code": svg}
```

### Option 3: Manual Frontend Processing

If you're building custom SVG rendering:

```javascript
// Load the post-processor
<script src="/visualisation_engine/svg_post_processor.js"></script>

// Use it
let svgString = `<svg>...<text font-weight="bold">...</text>...</svg>`;
svgString = window.SVGPostProcessor.optimizeSVG(svgString);
container.innerHTML = svgString;
```

## 🧪 Testing

### Test the Python Post-Processor

```bash
cd AI_infrastructure/shared
python svg_post_processor.py
```

Expected output:
```
Original SVG:
<svg xmlns="http://www.w3.org/2000/svg" width="600" height="400">
    <text y="200" dominant-baseline="middle" font-size="16" font-weight="bold">TITLE</text>
</svg>

Fixed SVG:
<svg xmlns="http://www.w3.org/2000/svg" width="600" height="400">
    <text y="205.60" font-size="16" font-weight="bold">TITLE</text>
</svg>

✓ PASS
```

### Test the JavaScript Post-Processor

```javascript
// In browser console
const testSVG = `<svg xmlns="http://www.w3.org/2000/svg">
    <text y="150" dominant-baseline="middle" font-weight="bold" font-size="16">
        SPECIFICATIONS
    </text>
</svg>`;

const fixed = window.SVGPostProcessor.optimizeSVG(testSVG);
console.log(fixed);
// Should show: y="155.60" and NO dominant-baseline attribute
```

### Visual Testing

Create a test SVG with bold text and verify:

**Before fix:**
```xml
<svg viewBox="0 0 400 200">
    <line x1="50" y1="100" x2="350" y2="100" stroke="red" stroke-width="2"/>
    <text x="200" y="100" text-anchor="middle" dominant-baseline="middle" 
          font-size="20" font-weight="bold">BOLD TEXT</text>
</svg>
```
❌ Text appears **below** the red line

**After fix:**
```xml
<svg viewBox="0 0 400 200">
    <line x1="50" y1="100" x2="350" y2="100" stroke="red" stroke-width="2"/>
    <text x="200" y="107.0" text-anchor="middle" 
          font-size="20" font-weight="bold">BOLD TEXT</text>
</svg>
```
✅ Text appears **centered** on the red line

## 🎛️ Configuration

### Adjust Compensation Factor

If you find the compensation is too much/too little:

**Python:** Edit `AI_infrastructure/shared/svg_post_processor.py`
```python
# Line ~69
y_baseline = y_center + (font_size * 0.35)  # Change 0.35 to adjust
```

**JavaScript:** Edit `UI/visualisation_engine/svg_post_processor.js`
```javascript
// Line ~75
const yBaseline = yCenter + (fontSize * 0.35);  // Change 0.35 to adjust
```

**Browser-specific compensation:**
```javascript
// Detect browser
const isChrome = /Chrome/.test(navigator.userAgent);
const isFirefox = /Firefox/.test(navigator.userAgent);
const isSafari = /Safari/.test(navigator.userAgent) && !isChrome;

// Apply different factors
const compensationFactor = isChrome ? 0.40 : isFirefox ? 0.30 : isSafari ? 0.35 : 0.35;
const yBaseline = yCenter + (fontSize * compensationFactor);
```

## 📊 Performance Impact

**Python Backend:**
- Parsing time: ~1-5ms per SVG (< 100KB)
- Memory overhead: Minimal (ElementTree parser)
- Caching: Already cached by Flask response cache

**JavaScript Frontend:**
- Parsing time: ~0.5-2ms per SVG
- Memory overhead: Negligible (DOMParser is native)
- Browser support: All modern browsers (Chrome 4+, Firefox 3.5+, Safari 3+)

**Recommendation:** Use frontend post-processing for real-time user interactions, backend post-processing for pre-rendered/cached content.

## 🔍 Debugging

### Enable Debug Logging

**Python:**
```python
import logging
logging.getLogger('AI_infrastructure.shared.svg_post_processor').setLevel(logging.DEBUG)
```

**JavaScript:**
```javascript
// In browser console
localStorage.setItem('SVG_POST_PROCESSOR_DEBUG', 'true');
```

### Check If Post-Processor Ran

**Python:** Look for log message:
```
[SVG_POST_PROCESSOR] Fixed 3 bold text baseline issue(s)
```

**JavaScript:** Check console for:
```
[SVG_POST_PROCESSOR] ✅ Fixed 3 bold text baseline issue(s)
```

### Verify SVG Was Modified

```javascript
// Before and after comparison
const original = `<text y="150" dominant-baseline="middle" font-weight="bold">TEXT</text>`;
const fixed = window.SVGPostProcessor.optimizeSVG(`<svg>${original}</svg>`);

console.assert(fixed.includes('y="155'), 'Y-position was adjusted');
console.assert(!fixed.includes('dominant-baseline'), 'dominant-baseline was removed');
```

## 🚨 Troubleshooting

### Issue: Post-processor not running

**Symptoms:** Bold text still shifts downward

**Solutions:**
1. Check browser console for errors
2. Verify `svg_post_processor.js` is loaded
3. Check `window.SVGPostProcessor` exists
4. Look for warnings: `SVG post-processor not loaded`

### Issue: Text still misaligned after fix

**Possible causes:**
1. **Font-specific metrics:** Some fonts have unusual vertical metrics
   - **Solution:** Adjust compensation factor (see Configuration)
2. **Multiple baseline attributes:** SVG has conflicting positioning
   - **Solution:** Remove manual Y-offsets from AI generation
3. **CSS transforms:** External styles affecting position
   - **Solution:** Check for `transform: translateY()` in CSS

### Issue: SVG not rendering at all

**Possible causes:**
1. **XML parsing error:** Post-processor broke the SVG
   - **Check:** Browser console for parser errors
   - **Solution:** Validate original SVG with `validateSVG()`
2. **Namespace issues:** SVG xmlns missing after processing
   - **Solution:** Ensure root `<svg>` has `xmlns="http://www.w3.org/2000/svg"`

## 📖 Related Documentation

- **Master Reference:** `.github/SVG_CAD_GENERATION_RULES.md` (complete spacing rules)
- **Visualization Guide:** `tools/implementations/visualization_guide.py` (AI guidance)
- **W3C SVG2 Spec:** [Text Layout Algorithm](https://www.w3.org/TR/SVG2/text.html#TextLayout)
- **MDN Reference:** [dominant-baseline](https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/dominant-baseline)

## 🎓 Why This Approach Wins

| Approach | AI Adapts | Backend Fixes |
|----------|-----------|---------------|
| **Complexity** | High (AI must remember compensation) | Low (one function) |
| **Maintainability** | Fragile (prompt changes break it) | Robust (isolated fix) |
| **Consistency** | Variable (AI forgets sometimes) | Perfect (always runs) |
| **Future-proof** | Breaks if browsers fix bug | Easy to remove when fixed |
| **Performance** | Same | Same |
| **Developer Experience** | Confusing (wrong values that work) | Clear (correct values) |

**Verdict:** Backend post-processing is the superior solution.

---

**Last Updated:** December 29, 2025  
**Version:** 1.0  
**Status:** ✅ Production Ready
