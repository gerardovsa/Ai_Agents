# Test Plan: Quote Calculator Constructor Fix

**Date:** October 31, 2025  
**Tester:** [Your Name]  
**Module:** Quote Calculator (`quote-calculator`)

---

## Pre-Test Checklist

- [ ] Browser: Chrome/Edge/Firefox (latest version)
- [ ] Developer Console open (F12)
- [ ] Network tab visible
- [ ] Console tab visible

---

## Test 1: Module Loads Without Errors

### Steps
1. Navigate to: `file:///C:/Users/gpoli/GIT/AI_agents/UI/business-ai-platform-v2.html`
2. Wait for page to fully load (3-5 seconds)
3. Open Developer Console (F12)
4. Check Console tab for errors

### Expected Result
**Console output should include:**
```
✅ Quote Calculator module constructed
✅ BaseModule created for quote-calculator (path: calculator-module)
✅ Loading manifest for quote-calculator from: external/modules/calculator-module/manifest.json
✅ Manifest loaded for quote-calculator
✅ Creating UI structure for quote-calculator...
✅ Quote Calculator module registered
✅ Module initialized: Quote Calculator
```

**Should NOT see:**
```
❌ GET http://localhost:5001/external/modules/quote-calculator/manifest.json 404
❌ Failed to load manifest for quote-calculator
❌ Container not found for module: quote-calculator
```

### Pass/Fail: [ ]

---

## Test 2: Manifest Loads from Correct Path

### Steps
1. In Developer Console, go to **Network** tab
2. Filter by: `manifest`
3. Look for manifest.json requests
4. Check the path for `quote-calculator`

### Expected Result
**Network request should show:**
```
✅ GET external/modules/calculator-module/manifest.json [200 OK]
```

**Should NOT show:**
```
❌ GET external/modules/quote-calculator/manifest.json [404 Not Found]
```

### Pass/Fail: [ ]

---

## Test 3: Module Icon Appears in Sidebar

### Steps
1. Look at left sidebar
2. Find calculator icon (orange/yellow color)
3. Hover over icon to see tooltip

### Expected Result
- ✅ Calculator icon visible in sidebar
- ✅ Icon color: Orange (#ffb347)
- ✅ Tooltip shows: "Quote Calculator"
- ✅ Icon is clickable (cursor changes to pointer)

### Pass/Fail: [ ]

---

## Test 4: Module Opens Successfully

### Steps
1. Click calculator icon in sidebar
2. Wait for module to open (1-2 seconds)
3. Check main content area

### Expected Result
- ✅ Main content area shows "Quote Calculator" header
- ✅ Sub-tabs visible at top:
  - Business Cards
  - Flyers & Leaflets
  - Perfect Bound Books
  - Booklets
  - Query Library
- ✅ Content area shows calculator interface
- ✅ No blank screens or "Loading..." stuck messages

### Pass/Fail: [ ]

---

## Test 5: Sub-Tabs Work Correctly

### Steps
1. Click "Business Cards" tab
2. Verify content appears
3. Click "Flyers & Leaflets" tab
4. Verify content switches
5. Click "Query Library" tab
6. Verify content switches

### Expected Result
- ✅ Each tab click updates content area
- ✅ Active tab highlighted
- ✅ No console errors when switching tabs
- ✅ Content specific to each calculator type

### Pass/Fail: [ ]

---

## Test 6: Module Colors Applied

### Steps
1. Inspect module header (right-click → Inspect)
2. Check computed styles
3. Look for orange/yellow colors

### Expected Result
- ✅ Module header border: Orange (#ffb347)
- ✅ Primary buttons: Orange background
- ✅ Active tab indicator: Orange color
- ✅ Module icon: Orange color

### Pass/Fail: [ ]

---

## Test 7: No JavaScript Errors

### Steps
1. Keep Developer Console open during all tests
2. Monitor Console tab for any red error messages
3. Test all interactions (clicks, tab switches, etc.)

### Expected Result
- ✅ Zero JavaScript errors in console
- ✅ Only informational logs (blue/gray text)
- ✅ No warning messages about missing files
- ✅ No "undefined" or "null" errors

### Pass/Fail: [ ]

---

## Test 8: Module Registry Check

### Steps
1. Open Developer Console
2. Type in Console: `window.ModuleRegistry['quote-calculator']`
3. Press Enter
4. Check output

### Expected Result
```javascript
QuoteCalculatorModule {
    moduleId: "quote-calculator"
    modulePath: "calculator-module"
    manifest: {id: "quote-calculator", name: "Quote Calculator", ...}
    container: div#tab-quote-calculator
    // ... other properties
}
```

**Should NOT be:**
```javascript
undefined  // ❌ Module not registered
class QuoteCalculatorModule  // ❌ Class not instantiated
```

### Pass/Fail: [ ]

---

## Test 9: Manifest Structure Validation

### Steps
1. In Developer Console, type: `window.ModuleRegistry['quote-calculator'].manifest`
2. Press Enter
3. Expand the object

### Expected Result
```javascript
{
    id: "quote-calculator",
    name: "Quote Calculator",
    version: "1.0.0",
    description: "Professional printing quote calculator...",
    icon: "fas fa-calculator",
    color: "#ffb347",
    tabs: [
        {id: "business-cards", label: "Business Cards", ...},
        {id: "flyers", label: "Flyers & Leaflets", ...},
        // ... more tabs
    ]
}
```

### Pass/Fail: [ ]

---

## Test 10: Module State Check

### Steps
1. In Developer Console, type: `window.ModuleRegistry['quote-calculator'].modulePath`
2. Press Enter

### Expected Result
```
"calculator-module"  // ✅ Correct folder path
```

**Should NOT be:**
```
"quote-calculator"  // ❌ Would cause 404 errors
undefined  // ❌ Property missing
```

### Pass/Fail: [ ]

---

## Summary

### Test Results

| Test # | Test Name | Status |
|--------|-----------|--------|
| 1 | Module Loads Without Errors | [ ] Pass [ ] Fail |
| 2 | Manifest Loads from Correct Path | [ ] Pass [ ] Fail |
| 3 | Module Icon Appears in Sidebar | [ ] Pass [ ] Fail |
| 4 | Module Opens Successfully | [ ] Pass [ ] Fail |
| 5 | Sub-Tabs Work Correctly | [ ] Pass [ ] Fail |
| 6 | Module Colors Applied | [ ] Pass [ ] Fail |
| 7 | No JavaScript Errors | [ ] Pass [ ] Fail |
| 8 | Module Registry Check | [ ] Pass [ ] Fail |
| 9 | Manifest Structure Validation | [ ] Pass [ ] Fail |
| 10 | Module State Check | [ ] Pass [ ] Fail |

**Total Passed:** _____ / 10  
**Total Failed:** _____ / 10

---

## Notes

**Issues Found:**
```
[List any issues discovered during testing]
```

**Performance Observations:**
```
[Note any slowness, delays, or performance issues]
```

**Browser Compatibility:**
- [ ] Chrome
- [ ] Edge
- [ ] Firefox
- [ ] Safari

---

## Sign-off

**Tested by:** ___________________  
**Date:** ___________________  
**Status:** [ ] Passed [ ] Failed [ ] Needs Fixes

---

## Quick Debug Commands

If tests fail, use these console commands for debugging:

```javascript
// Check module is registered
window.ModuleRegistry['quote-calculator']

// Check module paths
console.log('Module ID:', window.ModuleRegistry['quote-calculator'].moduleId);
console.log('Module Path:', window.ModuleRegistry['quote-calculator'].modulePath);

// Check manifest loaded
console.log('Manifest:', window.ModuleRegistry['quote-calculator'].manifest);

// Check container exists
console.log('Container:', document.getElementById('tab-quote-calculator'));

// Force reload manifest
window.ModuleRegistry['quote-calculator'].loadManifest();

// Re-initialize module
window.ModuleRegistry['quote-calculator'].initialize();
```
