# Communication Hub - Testing Guide

**Purpose:** Step-by-step testing instructions for all Tabulator enhancements  
**Date:** November 10, 2025  
**Status:** Ready for Testing

---

## 🚀 QUICK START

### 1. Start the AI Agent Server
```powershell
cd C:\Users\gpoli\GIT\AI_agents
BISTART
```

### 2. Open InHouse Print
- Navigate to `http://localhost:5001` (or your InHouse Print URL)
- Click the **Communication Hub** icon in sidebar (chat bubble icon)

### 3. Click "Unified Inbox" Tab
- You should see the stat cards and toolbar

### 4. Click "Refresh" Button
- This will load your emails (does NOT auto-load for performance)

---

## ✅ FEATURE TESTING CHECKLIST

### Test 1: Stat Cards (Top of Page)

**What to Look For:**
- 4 cards in a grid:
  - **Total Emails** (envelope icon, blue)
  - **Gmail** (Google icon, green)
  - **Outlook** (Microsoft icon, blue)
  - **Unread** (open envelope icon, orange)

**Expected Behavior:**
- On first load: All show "-"
- After clicking Refresh: Numbers update to real counts

**Screenshot Location:**
```
stats-grid
├── stat-card (Total Emails)
├── stat-card (Gmail)
├── stat-card (Outlook)
└── stat-card (Unread)
```

---

### Test 2: Tag Buttons (Toolbar)

**What to Test:**
1. Select 1 or more emails (click checkboxes)
2. Click **Clear** button (gray)
   - Expected: Selected rows lose tag
3. Click **Green** button
   - Expected: Rows get light green background + green left border
4. Click **Orange** button
   - Expected: Rows get light orange background + orange left border
5. Click **Red** button
   - Expected: Rows get light red background + red left border

**Visual Check:**
- All tag buttons should have **border-radius: 6px** (soft corners)
- Button colors:
  - Clear: `#6c757d` (gray)
  - Green: `#2e7d32` (dark green)
  - Orange: `#e65100` (dark orange)
  - Red: `#c62828` (dark red)

**Code Verification:**
- Check console for: `[Communication Hub] Tagged X emails with [color]`

---

### Test 3: Selection Checkboxes

**What to Test:**
1. Click header checkbox (top-left)
   - Expected: All visible rows selected
2. Click individual row checkboxes
   - Expected: Row highlights, selected count updates
3. Look at "Selected: X" text in toolbar
   - Expected: Updates in real-time

**Visual Check:**
- Checkboxes in first column (frozen)
- Header checkbox selects/deselects all

---

### Test 4: Export Buttons

**What to Test:**
1. Click **Excel** button
   - Expected: Downloads `emails_export_YYYY-MM-DD.xlsx`
2. Click **CSV** button
   - Expected: Downloads `emails_export_YYYY-MM-DD.csv`
3. Click **PDF** button
   - Expected: Downloads `emails_export_YYYY-MM-DD.pdf`

**File Verification:**
- Open files in Excel/Notepad/PDF viewer
- Verify all columns are included
- Check data integrity

**Console Check:**
```
[Communication Hub] Exported X emails as excel
```

---

### Test 5: Header Filters

**What to Test:**

**Provider Filter (Select Dropdown):**
1. Click dropdown below "Provider" header
2. Select "Gmail"
   - Expected: Only Gmail emails visible
3. Select "Outlook"
   - Expected: Only Outlook emails visible
4. Select "All"
   - Expected: All emails visible

**Text Filters:**
1. Type in "From" header filter
   - Expected: Filters sender names in real-time
2. Type in "Subject" header filter
   - Expected: Filters email subjects
3. Type in "Preview" header filter
   - Expected: Filters email content/snippets

**Status Filter (Select Dropdown):**
1. Select "Unread"
   - Expected: Only unread emails visible
2. Select "Read"
   - Expected: Only read emails visible

**Visual Check:**
- Input fields have placeholder text:
  - "Search sender..."
  - "Search subject..."
  - "Search content..."

---

### Test 6: Tooltips

**What to Test:**
1. Hover over **Tag** column
   - Expected: Tooltip shows tag color name or "No tag"
2. Hover over **Provider** column
   - Expected: Tooltip shows "Gmail" or "Outlook"
3. Hover over **From** column
   - Expected: Tooltip shows full sender email
4. Hover over **Subject** column
   - Expected: Tooltip shows full subject line
5. Hover over **Preview** column
   - Expected: Tooltip shows full snippet
6. Hover over **Date** column
   - Expected: Tooltip shows full date/time (e.g., "11/10/2025, 2:30:45 PM")

**Visual Check:**
- Tooltips appear on hover
- Text is readable (white on dark background)

---

### Test 7: Cell Click Handlers

**What to Test:**

**Selection Checkbox:**
1. Click checkbox in first column
   - Expected: Row selects, event doesn't bubble to row click

**Action Buttons:**
1. Click **robot icon** (AI button)
   - Expected: Email sent to AI chat
   - Console: `[Communication Hub] Sending email to AI Prime`
2. Click **reply icon** (Reply button)
   - Expected: Opens compose tab with reply
   - Console: `[Communication Hub] Reply to email: [id]`

**Row Click:**
1. Click anywhere else on row
   - Expected: Opens email preview panel (slide-out)

**Double-Click:**
1. Double-click a cell with long content (e.g., Subject)
   - Expected: Popup overlay appears with full content

---

### Test 8: Row Tagging (Visual)

**What to Test:**
1. Tag 3 emails with different colors (green, orange, red)
2. Verify visual changes:
   - **Background:** Light tint of tag color
   - **Left Border:** 4px solid border in tag color

**Color Values to Verify:**
- Green background: `rgba(46, 125, 50, 0.1)`
- Green border: `#2e7d32`
- Orange background: `rgba(230, 81, 0, 0.1)`
- Orange border: `#e65100`
- Red background: `rgba(198, 40, 40, 0.1)`
- Red border: `#c62828`

**Persistence Test:**
1. Tag some emails
2. Filter/search/paginate
3. Verify tags persist on tagged rows

---

### Test 9: Tag Column (Icon Display)

**What to Test:**
1. Look at **Tag** column (2nd column, frozen)
2. Verify icon colors match row tags:
   - **No tag:** Gray circle (`#6c757d`)
   - **Green tag:** Green circle (`#2e7d32`)
   - **Orange tag:** Orange circle (`#e65100`)
   - **Red tag:** Red circle (`#c62828`)

**Icon Size:**
- Font size: `10px`
- Icon: `fas fa-circle`

---

### Test 10: Pagination Controls

**What to Test:**

**Page Navigation:**
1. Click **First Page** button (double left arrow)
   - Expected: Jump to page 1
2. Click **Previous Page** button (single left arrow)
   - Expected: Go back one page
3. Click **Next Page** button (single right arrow)
   - Expected: Go forward one page
4. Click **Last Page** button (double right arrow)
   - Expected: Jump to last page

**Page Info:**
- Verify text updates: "Page X of Y"

**Page Size Selector:**
1. Change dropdown from "50 per page" to "25 per page"
   - Expected: Table reloads with 25 rows per page
2. Change to "100 per page"
   - Expected: Table reloads with 100 rows per page

**Button States:**
- On page 1: First/Prev buttons disabled
- On last page: Next/Last buttons disabled
- Middle pages: All buttons enabled

---

### Test 11: Height 100% (Full Vertical Fill)

**What to Test:**
1. Resize browser window vertically
   - Expected: Table height adjusts to fill container
2. Open browser dev tools (F12)
   - Expected: Table shrinks to accommodate dev tools
3. Close dev tools
   - Expected: Table expands back to full height

**Code Check:**
- Table config has `height: "100%"`
- Container has `min-height: 500px`

---

### Test 12: Three-State Loading System

**What to Test:**

**State 1 - Ready (Initial):**
1. Open Unified Inbox tab for first time
2. Verify display:
   - Info icon (blue)
   - Text: "Click the **Refresh** button to load your emails"
   - Subtext: "Select account filter and click Refresh"

**State 2 - Loading:**
1. Click **Refresh** button
2. Verify display:
   - Spinner animation (spinning icon)
   - Text: "Loading emails..."

**State 3 - Table (Data Loaded):**
1. After API response
2. Verify display:
   - Tabulator table with data
   - Stat cards updated
   - Pagination controls visible

**Error State (Bonus):**
1. Disconnect network or use invalid credentials
2. Click Refresh
3. Verify error display:
   - Red exclamation icon
   - Text: "Failed to load emails"
   - Error message
   - **Retry** button

---

### Test 13: Cell Popup Viewer

**What to Test:**
1. Find an email with long subject or preview (100+ characters)
2. Double-click the cell
3. Verify popup:
   - Centered overlay
   - Dark backdrop
   - Scrollable content
   - Close button (X)
   - Column name as header
   - Full cell content displayed

**Close Methods:**
1. Click **X** button
   - Expected: Popup closes
2. Click outside popup (on backdrop)
   - Expected: Popup closes

---

## 🎨 VISUAL REGRESSION CHECKLIST

### Colors

| Element | Expected Color | Actual |
|---------|---------------|--------|
| Tag Clear Button | `#6c757d` | ✅ |
| Tag Green Button | `#2e7d32` | ✅ |
| Tag Orange Button | `#e65100` | ✅ |
| Tag Red Button | `#c62828` | ✅ |
| Primary Button | `#0078d4` | ✅ |
| Background | `#1a1f2e` | ✅ |
| Border | `#2a3142` | ✅ |

### Spacing

| Element | Expected Value | Actual |
|---------|---------------|--------|
| Toolbar Padding | `16px 20px` | ✅ |
| Button Gap | `6px` | ✅ |
| Tag Button Padding | `4px 10px` | ✅ |
| Tag Button Border Radius | `6px` | ✅ |
| Stat Card Gap | `var(--space-4)` | ✅ |

### Typography

| Element | Font Size | Font Weight |
|---------|-----------|-------------|
| Card Title | `24px` | N/A |
| Card Subtitle | Default | N/A |
| Toolbar Text | `12px` | N/A |
| Stat Value | `var(--font-size-xl)` | `var(--font-weight-bold)` |
| Stat Label | `var(--font-size-sm)` | N/A |

---

## 🐛 KNOWN ISSUES / EDGE CASES

### Issue 1: Export Requires Tabulator Extensions
**Symptom:** Export buttons don't work  
**Cause:** Tabulator download modules not loaded  
**Solution:** Add to manifest.json dependencies:
```json
"https://unpkg.com/tabulator-tables@5.5.2/dist/js/modules/download.min.js"
```

### Issue 2: Tags Not Persisting After Reload
**Symptom:** Tags disappear after page refresh  
**Cause:** Tags stored in memory only  
**Solution:** Implement localStorage or backend persistence (future enhancement)

### Issue 3: Cell Popup Scrollbar Styling
**Symptom:** Scrollbar doesn't match theme  
**Cause:** Browser default scrollbar styles  
**Solution:** Add CSS scrollbar styling (optional)

---

## 📊 PERFORMANCE CHECKLIST

- [ ] Table renders with 50 emails in < 500ms
- [ ] Filtering updates in < 100ms
- [ ] Pagination navigation in < 100ms
- [ ] Tag button response in < 50ms
- [ ] Export to Excel completes in < 2s
- [ ] No memory leaks after 5 min usage
- [ ] Smooth scrolling with 200+ rows

---

## ✅ ACCEPTANCE CRITERIA

### Must Pass:
- [ ] All 14 features work as described
- [ ] No console errors
- [ ] No visual glitches
- [ ] Responsive on desktop (1920x1080)
- [ ] Works in Chrome, Edge, Firefox

### Should Pass:
- [ ] Smooth animations
- [ ] Consistent styling with Stock Management
- [ ] Professional appearance
- [ ] Intuitive UX

### Nice to Have:
- [ ] Dark mode compatible
- [ ] Mobile responsive (future)
- [ ] Keyboard shortcuts

---

## 🎉 FINAL SIGN-OFF

**Tested By:** ___________________  
**Date:** ___________________  
**Browser:** ___________________  
**Resolution:** ___________________  

**Overall Status:**
- [ ] ✅ **PASS** - Ready for production
- [ ] ⚠️ **PASS WITH NOTES** - Minor issues (document below)
- [ ] ❌ **FAIL** - Major issues (document below)

**Notes:**
```
[Add any notes here]
```

---

**Testing Complete!** 🎊

Return this checklist to development team with results.
