# 👁️ VISUAL TEST GUIDE - Unlink & Unload Buttons

## 🎯 Quick Test Checklist (5 Minutes)

### Step 1: Refresh the Page
1. Open browser to AI Agents platform
2. Press **Ctrl + Shift + R** (hard refresh)
3. Wait for page to fully load

---

### Step 2: Test in Agent Column (UNLOAD Button)

**What to look for:**
- Thread-info card in Agent-1, Agent-2, or Agent-3 column
- Look at **bottom-right corner** of the card
- Should see **📤 button** (sign-out icon)

**Visual Check:**
- [ ] Button is **28x28 pixels** (small, icon-only)
- [ ] Button has **red border** (1px solid)
- [ ] Background is **transparent** (see-through)
- [ ] Icon is **white**
- [ ] **Hover test:** Move mouse over button
  - [ ] Background turns **solid red**
  - [ ] Border becomes **darker red**
- [ ] Tooltip shows: **"Unload thread and Return to Prime"**

**Click Test:**
- [ ] Click the 📤 button
- [ ] Confirmation dialog appears:
```
⚠️  Unload from Agent 2?

This will return the thread to Prime Agent.

• Thread will be unassigned from Agent 2 column
• Synergy link will be preserved

Continue?
```
- [ ] Click **Cancel** (don't actually unload yet)

---

### Step 3: Test in Synergy Card (UNLINK Button)

**What to look for:**
- Open a Synergy session that has linked threads
- Look at the **linked threads section**
- Each thread card should show **🔗 button** (broken link icon)

**Visual Check:**
- [ ] Button is **28x28 pixels** (small, icon-only)
- [ ] Button has **red border** (1px solid)
- [ ] Background is **transparent** (see-through)
- [ ] Icon is **white**
- [ ] **Hover test:** Move mouse over button
  - [ ] Background turns **solid red**
  - [ ] Border becomes **darker red**
- [ ] Tooltip shows: **"Unlink from Synergy Session"**

**Click Test:**
- [ ] Click the 🔗 button
- [ ] Confirmation dialog appears:
```
⚠️  Unlink from Synergy Session?

This will remove the thread from:
"Q4 Marketing Campaign"

• Synergy context will no longer be included in AI responses
• Thread will remain in Agent 2

Continue?
```
- [ ] Click **Cancel** (don't actually unlink yet)

---

### Step 4: Test in Thread Sidebar (BOTH Buttons)

**What to look for:**
- Open thread list sidebar
- Find a thread that is:
  - In an agent column (Agent-1/2/3)
  - AND has a Synergy link

**Visual Check:**
- [ ] **Two buttons** visible at bottom-right corner
- [ ] 🔗 UNLINK button (left)
- [ ] 📤 UNLOAD button (right)
- [ ] Both buttons have **red border**, **transparent background**, **white icon**
- [ ] **4px gap** between the two buttons
- [ ] **Hover test:** Each button independently turns red

**Different Thread States:**

**Thread in Agent + Synergy link:**
```
┌─────────────────────────────────────┐
│ Campaign Planning         [Agent 2] │
│ 🔗 Q4 Marketing           [🔗][📤] │ ← BOTH buttons
└─────────────────────────────────────┘
```
- [ ] Shows BOTH buttons ✅

**Thread in Prime + Synergy link:**
```
┌─────────────────────────────────────┐
│ Budget Analysis             [Prime] │
│ 🔗 Q4 Marketing             [🔗]   │ ← UNLINK only
└─────────────────────────────────────┘
```
- [ ] Shows UNLINK only ✅ (no unload - already in Prime)

**Thread in Agent + No Synergy:**
```
┌─────────────────────────────────────┐
│ Email Draft               [Agent 1] │
│ 8 msg • Nov 10              [📤]   │ ← UNLOAD only
└─────────────────────────────────────┘
```
- [ ] Shows UNLOAD only ✅ (no unlink - no Synergy)

**Thread in Prime + No Synergy:**
```
┌─────────────────────────────────────┐
│ Meeting Notes               [Prime] │
│ 3 msg • Nov 09                     │ ← No buttons
└─────────────────────────────────────┘
```
- [ ] Shows NO buttons ✅ (already in Prime, no Synergy link)

---

## 🎨 Visual Specifications

### Button Style Reference

```
┌──────────────────────────────┐
│ Normal State:                │
│ ┌────┐                       │
│ │ 🔗 │ ← White icon           │
│ └────┘    Red border         │
│         Transparent bg        │
└──────────────────────────────┘

┌──────────────────────────────┐
│ Hover State:                 │
│ ┌────┐                       │
│ │ 🔗 │ ← White icon           │
│ └────┘    Darker red border  │
│         Solid RED bg          │
└──────────────────────────────┘
```

**Exact Colors:**
- Border: `#dc3545` (Bootstrap danger red)
- Hover Background: `#dc3545` (same red)
- Hover Border: `#c82333` (darker red)
- Icon: `white`

**Exact Dimensions:**
- Width: `28px`
- Height: `28px`
- Border: `1px solid`
- Border Radius: `4px`
- Icon Size: `14px`
- Gap between buttons: `4px`

**Position:**
- Absolute positioned
- Bottom: `8px` from container edge
- Right: `8px` from container edge

---

## 🔍 Common Issues to Look For

### ❌ Button Not Showing
**Possible Causes:**
1. Thread doesn't meet visibility criteria
   - Unlink: Thread has no `synergy_card_id`
   - Unload: Thread is in Prime (not an agent)
2. Wrong context
   - Agent column shouldn't show UNLINK
   - Synergy card shouldn't show UNLOAD

**Fix:** This is correct behavior (context-dependent)

---

### ❌ Button Style Wrong
**Possible Causes:**
1. CSS not loaded (hard refresh needed)
2. CSS class conflict with other `.thread-action-btn` rules

**Fix:** Check browser console for CSS errors

---

### ❌ Button Not Clickable
**Possible Causes:**
1. Z-index issue (button behind other elements)
2. Pointer-events disabled

**Fix:** Check browser dev tools, inspect element

---

### ❌ Confirmation Dialog Not Appearing
**Possible Causes:**
1. JavaScript error (check console)
2. Function not found (ThreadManager not loaded)

**Fix:** Check browser console for errors

---

### ❌ Action Not Working After Confirm
**Possible Causes:**
1. Backend API not responding
2. Network error

**Fix:** Check Network tab in dev tools

---

## 🧪 Full Test Scenario (End-to-End)

### Scenario: Move Thread from Agent to Prime

**Setup:**
1. Have a thread in Agent-2 with Synergy link

**Steps:**
1. Go to Agent-2 column
2. Click **📤 UNLOAD** button on thread-info card
3. Read confirmation dialog
4. Click **OK**

**Expected Results:**
- [ ] Thread disappears from Agent-2 column
- [ ] Agent-2 column shows "No thread loaded"
- [ ] Thread appears in Prime's thread list
- [ ] Thread still shows Synergy badge (🔗 preserved)
- [ ] All thread-info cards update to show [Prime] badge
- [ ] No errors in console

---

### Scenario: Unlink Thread from Synergy

**Setup:**
1. Have a Synergy session with linked thread

**Steps:**
1. Open Synergy session card
2. Look at "Linked Threads" section
3. Find a thread card
4. Click **🔗 UNLINK** button
5. Read confirmation dialog
6. Click **OK**

**Expected Results:**
- [ ] Thread disappears from Synergy's linked threads list
- [ ] Thread's Synergy badge disappears everywhere
- [ ] Thread stays in its current agent location
- [ ] No more Synergy context in AI responses
- [ ] No errors in console

---

## 📸 Screenshot Checklist

Take screenshots of:
1. [ ] Agent column with UNLOAD button visible
2. [ ] Synergy card with UNLINK button on thread
3. [ ] Sidebar with BOTH buttons visible
4. [ ] Hover state (red background)
5. [ ] UNLINK confirmation dialog
6. [ ] UNLOAD confirmation dialog

---

## ✅ Sign-Off Checklist

Before marking as "tested":
- [ ] All buttons appear in correct contexts
- [ ] Button styling matches specifications
- [ ] Hover effects work correctly
- [ ] Tooltips show correct text
- [ ] Confirmation dialogs appear
- [ ] Confirmation dialogs have correct text
- [ ] UNLINK removes Synergy link
- [ ] UNLOAD moves thread to Prime
- [ ] No JavaScript errors in console
- [ ] No CSS rendering issues

---

**Test Duration:** ~5 minutes  
**Recommended Browser:** Chrome/Edge (latest)  
**Test Date:** _____________  
**Tester:** _____________  
**Result:** ⬜ PASS / ⬜ FAIL  
**Notes:** _____________________________________________

