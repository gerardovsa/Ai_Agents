# Timeline Toggle Debug Guide

**File:** `focused_timeline_detailed.html`  
**Feature:** Technical ↔️ Business View Toggle  
**Status:** ✅ Comprehensive logging added

---

## 🔍 How to Debug

### Step 1: Open the Timeline
```powershell
# Open in your browser
start focused_timeline_detailed.html
```

### Step 2: Open Browser Console
- Press **F12** (or right-click → Inspect → Console tab)
- You should see initial logs immediately

### Step 3: Check Initial Load Logs

**Expected Console Output on Page Load:**
```
📅 Timeline script loaded - View toggle ENABLED
   Open browser console (F12) to see detailed logs

🚀 DOM CONTENT LOADED
  Saved view: null (or 'business' if previously saved)
  ℹ️  Using default technical view
  Toggle button found: true
  Button text: Switch to Business View
  📊 Elements with data attributes:
    Bars: [number] Sidebar: [number] Legend: [number]
  📝 Sample bar: { category: "...", technical: "...", business: "..." }
```

### Step 4: Click the Toggle Button

**Expected Console Output When Clicking:**
```
🔄 TOGGLE VIEW CLICKED
  Before toggle - isBusinessView: false
  After toggle - isBusinessView: true
  Button element found: true
  ✅ Switching to BUSINESS view
  Button classes: toggle-btn business
  💾 Saved to localStorage: business

🏷️  UPDATE LABELS called with mode: business
  📊 Component bars found: [number]
  Bar 1: { category: "...", technical: "...", business: "...", selected: "..." }
  Bar 2: { category: "...", technical: "...", business: "...", selected: "..." }
  Bar 3: { category: "...", technical: "...", business: "...", selected: "..." }
  ✅ Updated [number] bar tooltips
  📝 Sidebar items found: [number]
  Sidebar 1: { technical: "...", business: "...", selected: "..." }
  Sidebar 2: { technical: "...", business: "...", selected: "..." }
  Sidebar 3: { technical: "...", business: "...", selected: "..." }
  ✅ Updated [number] sidebar items
  📋 Legend items found: [number]
  Legend 1: { technical: "...", business: "...", selected: "..." }
  Legend 2: { technical: "...", business: "...", selected: "..." }
  Legend 3: { technical: "...", business: "...", selected: "..." }
  ✅ Updated [number] legend items
🏁 UPDATE LABELS complete
```

---

## 🐛 Troubleshooting

### Issue 1: No Logs Appear

**Symptoms:**
- Console is empty
- No initial logs on page load

**Solution:**
1. Check browser console is open (F12)
2. Refresh the page
3. Check Console tab (not Elements or Network)
4. Try different browser (Chrome, Edge, Firefox)

---

### Issue 2: Button Doesn't Respond

**Symptoms:**
- Clicking button does nothing
- No "TOGGLE VIEW CLICKED" log appears

**Check:**
1. Is button visible on page?
2. Does clicking show any JavaScript errors in console?
3. Try right-click → Inspect Element on button
4. Check if button has `onclick="toggleView()"` attribute

**Debug in Console:**
```javascript
// Check if button exists
document.getElementById('viewToggle')

// Check if function exists
typeof toggleView

// Manually trigger toggle
toggleView()
```

---

### Issue 3: Labels Don't Change

**Symptoms:**
- Button changes color/text
- But labels stay the same
- "UPDATE LABELS" logs appear but nothing changes

**Check logs for:**
```
📊 Component bars found: 0       ← ❌ Should be > 0
📝 Sidebar items found: 0        ← ❌ Should be > 0
📋 Legend items found: 0         ← ❌ Should be > 0
```

**If counts are 0:**
- Elements don't have data attributes
- Need to regenerate HTML: `python create_focused_timeline.py`

**If counts are > 0 but no updates:**
```
✅ Updated 0 bar tooltips         ← ❌ Should match bars found
✅ Updated 0 sidebar items        ← ❌ Should match sidebar found
✅ Updated 0 legend items         ← ❌ Should match legend found
```

**Debug in Console:**
```javascript
// Check if bars have data attributes
document.querySelector('.component-bar').dataset.technical
document.querySelector('.component-bar').dataset.business

// Check if sidebar items have data attributes
document.querySelector('.subcategory-item').dataset.technical

// Check if spans exist
document.querySelector('.component-bar .tooltip-label')
document.querySelector('.subcategory-item .subcat-label')
document.querySelector('.legend-subcategory .legend-label')
```

---

### Issue 4: Data Attributes Missing

**Symptoms:**
```
Sample bar: { category: undefined, technical: undefined, business: undefined }
```

**Solution:**
```powershell
# Regenerate HTML with updated Python script
cd C:\Users\gpoli\GIT\AI_agents
python create_focused_timeline.py
```

**Then refresh browser and check logs again.**

---

### Issue 5: Button Changes But Labels Don't

**Symptoms:**
- Button text changes to "Switch to Technical View"
- Button turns purple
- But sidebar/tooltips show same labels

**Check Sample Output:**
Look for these logs:
```
Bar 1: { technical: "API Routes", business: "Server APIs", selected: "Server APIs" }
```

If `selected` shows business label but page doesn't change:
- **Cause:** Spans not being updated
- **Fix:** Check if `.tooltip-label`, `.subcat-label`, `.legend-label` classes exist

**Debug in Console:**
```javascript
// Manually update a label to test
const bar = document.querySelector('.component-bar');
const tooltipLabel = bar.querySelector('.tooltip-label');
console.log('Tooltip label element:', tooltipLabel);
console.log('Current text:', tooltipLabel?.textContent);

// Try changing it manually
if (tooltipLabel) {
    tooltipLabel.textContent = 'TEST CHANGE';
}
```

---

## ✅ Expected Behavior

### Technical View (Default)
- Button: White with text "Switch to Business View"
- Tooltips show: "Frontend: API Routes", "Testing: Python Testing"
- Sidebar shows: "API Routes", "Python Testing", "Data Migrations"
- Legend shows: "API Routes", "Python Testing", "Data Migrations"

### Business View (After Toggle)
- Button: Purple gradient with text "Switch to Technical View"
- Tooltips show: "Frontend: Server APIs", "Testing: Quality Assurance"
- Sidebar shows: "Server APIs", "Quality Assurance", "Database Updates"
- Legend shows: "Server APIs", "Quality Assurance", "Database Updates"

---

## 🔧 Manual Testing Steps

### Test 1: Initial State
1. Open `focused_timeline_detailed.html`
2. Check console shows "DOM CONTENT LOADED"
3. Check button says "Switch to Business View"
4. Check button is white (not purple)

### Test 2: Toggle to Business
1. Click button
2. Check console shows "TOGGLE VIEW CLICKED"
3. Check console shows "Switching to BUSINESS view"
4. Check button says "Switch to Technical View"
5. Check button is purple
6. Hover over a bar - tooltip should show business label

### Test 3: Toggle Back
1. Click button again
2. Check console shows "Switching to TECHNICAL view"
3. Check button says "Switch to Business View"
4. Check button is white
5. Hover over a bar - tooltip should show technical label

### Test 4: Persistence
1. Toggle to Business View
2. Refresh page (F5)
3. Check console shows "Auto-switching to business view"
4. Check button starts as purple with "Switch to Technical View"

### Test 5: Clear Preference
1. In console, run: `localStorage.removeItem('timelineView')`
2. Refresh page
3. Should start in Technical View (white button)

---

## 📋 Debug Checklist

- [ ] Browser console is open (F12)
- [ ] Initial load logs appear
- [ ] Button element is found
- [ ] Data attribute counts are > 0
- [ ] Sample bar shows all 3 attributes (category, technical, business)
- [ ] Clicking button shows "TOGGLE VIEW CLICKED"
- [ ] Button text changes
- [ ] Button color changes (white ↔️ purple)
- [ ] UPDATE LABELS is called
- [ ] Bar tooltips are updated
- [ ] Sidebar items are updated
- [ ] Legend items are updated
- [ ] Hovering shows changed labels
- [ ] LocalStorage is saved
- [ ] Refresh preserves preference

---

## 💡 Quick Console Commands

```javascript
// Check current view state
isBusinessView

// Check localStorage
localStorage.getItem('timelineView')

// Count elements
document.querySelectorAll('.component-bar').length
document.querySelectorAll('.subcategory-item').length
document.querySelectorAll('.legend-subcategory').length

// Check data attributes
const bar = document.querySelector('.component-bar');
console.log(bar.dataset);

// Manually trigger toggle
toggleView()

// Reset to technical view
isBusinessView = false;
updateLabels('technical');

// Force business view
isBusinessView = true;
updateLabels('business');

// Clear saved preference
localStorage.removeItem('timelineView');
location.reload();
```

---

## 🎯 What to Report

If the toggle still doesn't work, report these details:

1. **Browser & Version:** Chrome 120, Edge 118, Firefox 119, etc.
2. **Initial Load Logs:** Copy first 10 lines from console
3. **Click Logs:** Copy logs after clicking button
4. **Element Counts:** How many bars/sidebar/legend items found?
5. **Data Attributes:** Do sample elements have technical/business attributes?
6. **Visual Changes:** Does button change color? Does text change?
7. **Label Changes:** Do you see any labels change when toggling?

---

**Created:** November 8, 2025  
**Purpose:** Debug timeline toggle view feature  
**Status:** Comprehensive logging added - ready for testing
