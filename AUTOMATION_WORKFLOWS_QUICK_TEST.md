# Automation Workflows - Quick Test Guide

**Date:** November 23, 2025  
**Status:** ✅ Fixes Implemented - Ready for Testing

---

## 🚀 Quick Start (5 Minutes)

### Option 1: Test Isolated Environment (Recommended First)

```powershell
# 1. Open test page in browser
start UI/test_automation_canvas.html

# 2. Open browser console (F12)
# 3. Look for green checkmarks: ✓ [AUTOMATION] messages
# 4. Try dragging shapes from left palette to canvas
# 5. Click "Test Create Shape" button in debug panel
```

**Expected:** Shapes drag and drop, test button works, debug panel shows status.

---

### Option 2: Test Full Application

```powershell
# 1. Start backend (if not running)
BISTART

# 2. Test backend is responding
./test_automation_backend.ps1

# 3. Open main app
start UI/business-ai-platform-v2.html

# 4. Click purple automation workflows icon in sidebar
# 5. Open browser console (F12)
# 6. Try dragging shapes from left palette to canvas
```

**Expected:** Same as Option 1, plus workflow loading from backend works.

---

## ✅ Success Indicators

### In Browser Console:
```
✓ [AUTOMATION] DOM loaded, checking for canvas wrapper...
✓ [AUTOMATION] Canvas wrapper found, initializing AutomationCanvas...
✓ [AUTOMATION] Constructor called - initializing properties...
✓ [AUTOMATION] Found 6 draggable shape items
✓ [AUTOMATION] Canvas wrapper found, attaching drop handlers
✓ [AUTOMATION] AutomationCanvas initialized and assigned to window.automationCanvas
```

### Visual Indicators:
- ✓ Debug panel appears in bottom-right corner
- ✓ Shape palette visible on left side with 6 shapes
- ✓ Canvas grid visible in center
- ✓ Cursor changes to "grab" when hovering over shapes
- ✓ Shapes appear on canvas when dropped

### Console Tests:
```javascript
window.automationCanvas  // Should return object, not undefined
window.testAutomationCanvas()  // Should dump debug info
window.automationCanvas.testCreateShape()  // Should create shape
```

---

## ❌ Failure Indicators

### In Browser Console:
```
✗ Uncaught TypeError: Cannot read property 'shapes' of undefined
✗ [AUTOMATION] Canvas wrapper not found in DOM
✗ Uncaught ReferenceError: AutomationCanvas is not defined
```

### Visual Indicators:
- ✗ No debug panel appears
- ✗ Shapes don't drag or cursor doesn't change
- ✗ Canvas is blank or not visible
- ✗ Clicking buttons does nothing

### Console Tests:
```javascript
window.automationCanvas  // Returns: undefined
typeof AutomationCanvas  // Returns: "undefined"
```

---

## 🔧 Quick Fixes

### Issue: Backend Not Running
```powershell
# Check if running
Test-NetConnection localhost -Port 5001

# If not running
cd C:\Users\gpoli\GIT\AI_agents
BISTART

# Verify
curl http://localhost:5001/health
```

---

### Issue: window.automationCanvas is undefined
```javascript
// In browser console:

// 1. Check if class exists
typeof AutomationCanvas  // Should be "function"

// 2. Check if wrapper exists
document.getElementById('automation-canvas-wrapper')  // Should be element

// 3. Manually initialize
window.initializeAutomationCanvas()

// 4. Verify
window.automationCanvas  // Should now be object
```

---

### Issue: Shapes Not Draggable
```javascript
// In browser console:

// 1. Check draggable items
document.querySelectorAll('.floating-shape-item').length  // Should be 6

// 2. Check if they have draggable attribute
document.querySelectorAll('.floating-shape-item[draggable="true"]').length  // Should be 6

// 3. Check if palette is visible
getComputedStyle(document.querySelector('.floating-shape-palette')).display  // Should be "flex"
```

---

### Issue: Canvas Not Visible
```javascript
// In browser console:

// 1. Check canvas wrapper
const wrapper = document.getElementById('automation-canvas-wrapper');
wrapper  // Should be element, not null

// 2. Check display
getComputedStyle(wrapper).display  // Should be "block", not "none"

// 3. Check parent container
getComputedStyle(document.getElementById('tab-automation')).display  // Should be "block"

// 4. Force visibility
wrapper.style.display = 'block';
document.getElementById('tab-automation').classList.add('active');
```

---

## 📋 Test Checklist

Copy and paste this into your testing notes:

```
BACKEND TESTS:
[ ] Backend running (BISTART)
[ ] Health endpoint responds (curl http://localhost:5001/health)
[ ] Automation list responds (curl http://localhost:5001/api/automation/list)

INITIALIZATION TESTS:
[ ] Page loads without errors
[ ] Console shows [AUTOMATION] messages
[ ] Debug panel appears in bottom-right
[ ] window.automationCanvas is defined
[ ] window.automationCanvas instanceof AutomationCanvas is true

UI TESTS:
[ ] Shape palette visible on left
[ ] 6 shapes visible (TRIGGER, ACTION, DECISION, WAIT, LOOP, END)
[ ] Cursor changes to "grab" on hover
[ ] Canvas grid visible in center
[ ] Toolbar buttons visible at top

DRAG AND DROP TESTS:
[ ] Can drag TRIGGER shape
[ ] Console shows: [AUTOMATION] Drag start: trigger
[ ] Can drop on canvas
[ ] Console shows: [AUTOMATION] Drop event triggered
[ ] Shape appears on canvas at drop location
[ ] Debug panel updates shape count

PROGRAMMATIC TESTS:
[ ] window.testAutomationCanvas() works
[ ] window.automationCanvas.testCreateShape() works
[ ] Shape appears on canvas
[ ] Debug panel updates count
[ ] window.automationCanvas.shapes.length increases

WORKFLOW TESTS:
[ ] Click "New Workflow" button works
[ ] Modal appears
[ ] Can enter workflow title
[ ] Slug auto-generates
[ ] Can save workflow
[ ] Workflow appears in list
```

---

## 🎯 One-Command Test

```powershell
# Run all tests at once:
./test_automation_backend.ps1; start UI/test_automation_canvas.html
```

This will:
1. Test backend connectivity
2. Open test page in browser
3. You can then verify drag-and-drop manually

---

## 📞 Quick Debug Commands

Paste these into browser console:

```javascript
// Full diagnostic
window.testAutomationCanvas()

// Create test shape
window.automationCanvas.testCreateShape()

// Check initialization
console.log('Canvas:', !!window.automationCanvas);
console.log('Wrapper:', !!document.getElementById('automation-canvas-wrapper'));
console.log('Palette:', !!document.querySelector('.floating-shape-palette'));
console.log('Shapes:', document.querySelectorAll('.floating-shape-item').length);

// Force initialization
window.initializeAutomationCanvas()

// Check drag handlers
const items = document.querySelectorAll('.floating-shape-item');
items.forEach((item, i) => {
    console.log(`Shape ${i + 1}: draggable=${item.draggable}, type=${item.dataset.shape}`);
});
```

---

## 🎉 Success Criteria

**You know it's working when:**

1. ✅ Browser console shows 15+ [AUTOMATION] log messages
2. ✅ Debug panel appears and shows "Initialized: YES"
3. ✅ You can drag shapes from palette to canvas
4. ✅ Shapes appear where you drop them
5. ✅ Debug panel shape count increases
6. ✅ Test buttons in debug panel work
7. ✅ `window.automationCanvas` returns an object

**If ALL 7 are true:** ✅ **IT'S WORKING!**

---

## 📚 Related Files

- **Main Implementation:** `UI/external/modules/automation-workflows/automation-workflows.js`
- **Main HTML:** `UI/business-ai-platform-v2.html`
- **Test Page:** `UI/test_automation_canvas.html`
- **Backend Test:** `test_automation_backend.ps1`
- **Full Documentation:** `AUTOMATION_WORKFLOWS_FIX_COMPLETE.md`

---

## ⏱️ Time Estimate

- **Backend test:** 30 seconds
- **Test page verification:** 2 minutes
- **Full app testing:** 3 minutes
- **Total:** ~5 minutes

---

**Status:** ✅ ALL FIXES IMPLEMENTED - READY TO TEST!

**Next Action:** Run `./test_automation_backend.ps1` then open `UI/test_automation_canvas.html`
