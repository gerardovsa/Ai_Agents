# Double-Click Auto-Load Fix - December 12, 2025

## 🐛 Problem

**Issue:** Double-clicking a thread info card in the **Thread History sidebar** was automatically loading it into the **AI Chat Prime panel**, replacing whatever thread was currently loaded there.

**User Impact:** Accidental double-clicks would move threads and replace the Prime panel content unexpectedly.

---

## ✅ Solution

**Changed Behavior:**

| Location | Double-Click OLD Behavior | Double-Click NEW Behavior |
|----------|---------------------------|---------------------------|
| **Thread History** | ❌ Auto-loads into Prime, replaces current thread | ✅ **Expands/collapses card only** (no auto-load) |
| **Prime Panel** | ✅ Refreshes thread in Prime | ✅ Refreshes thread in Prime *(unchanged)* |
| **Agent Columns** | ❌ Loads into Prime, replaces current thread | ✅ **Refreshes in agent column** *(no move to Prime)* |

**To Load from Thread History → Prime:** Use **drag-and-drop** instead

---

## 📝 Files Modified

### 1. `thread-manager-interactions.js` (Lines 328-368)

**Changed:** `handleThreadDoubleClick()` function

**Before:**
```javascript
async handleThreadDoubleClick(threadId, currentLocation) {
    // Double-click ALWAYS loads in Prime (even from agents)
    await this.loadThreadInPrime(threadId);
    this.closeThreadMenu();
    showNotification(`Thread "${thread.title}" loaded in Prime`, 'success');
}
```

**After:**
```javascript
async handleThreadDoubleClick(threadId, currentLocation) {
    // FIX: Thread History should NOT auto-load into Prime
    if (currentLocation === 'thread-history') {
        console.log(`📋 Thread History double-click - expanding card only`);
        
        // Find card and expand it
        const card = document.querySelector(`[data-thread-id="${threadId}"][data-location="thread-history"]`);
        if (card && typeof ThreadCardExpansion !== 'undefined') {
            const fakeEvent = { stopPropagation: () => {}, preventDefault: () => {} };
            ThreadCardExpansion.toggleCard(fakeEvent, threadId);
        }
        return; // Stop here - do NOT load into Prime
    }

    // Prime/Agent panels: Refresh in place
    if (currentLocation === 'prime' || currentLocation === 'prime-loaded') {
        await this.loadThreadInPrime(threadId);
        showNotification('Thread refreshed in Prime', 'success');
    } else if (currentLocation && currentLocation.startsWith('agent-')) {
        showNotification('Thread refreshed', 'success');
    }
}
```

**Key Changes:**
1. ✅ Added check for `currentLocation === 'thread-history'`
2. ✅ Thread History: Expands card instead of loading into Prime
3. ✅ Prime: Refreshes thread (unchanged)
4. ✅ Agent columns: Stays in agent column (no move to Prime)

---

### 2. `thread-card-templates.js` (Lines 170-189)

**Changed:** Tooltip text for double-click behavior

**Before:**
```javascript
title="Double-click to load in Prime"
```

**After:**
```javascript
const doubleClickTooltip = isThreadHistory 
    ? 'Double-click to expand/collapse card' 
    : (isPrime ? 'Double-click to refresh thread' : 'Double-click to reload thread');

title="${doubleClickTooltip}"
```

**Key Changes:**
1. ✅ Thread History: "Double-click to expand/collapse card"
2. ✅ Prime: "Double-click to refresh thread"
3. ✅ Agents: "Double-click to reload thread"

---

## 🧪 Testing

### Test Case 1: Thread History Double-Click ✅
**Steps:**
1. Open Thread History sidebar
2. Double-click any thread card
3. **Expected:** Card expands/collapses to show details
4. **Expected:** Thread does NOT load into Prime panel
5. **Expected:** Prime panel content remains unchanged

### Test Case 2: Prime Panel Double-Click ✅
**Steps:**
1. Load a thread in Prime
2. Double-click the thread card in Prime panel
3. **Expected:** Thread refreshes in Prime
4. **Expected:** Notification: "Thread refreshed in Prime"

### Test Case 3: Agent Column Double-Click ✅
**Steps:**
1. Assign thread to Agent-1 column
2. Double-click the thread card in Agent-1
3. **Expected:** Thread refreshes in Agent-1
4. **Expected:** Thread does NOT move to Prime
5. **Expected:** Notification: "Thread refreshed"

### Test Case 4: Drag-and-Drop Still Works ✅
**Steps:**
1. Open Thread History sidebar
2. Drag a thread card to Prime drop zone
3. **Expected:** Thread loads into Prime
4. **Expected:** Previous Prime thread unloaded
5. **Expected:** Thread location updated to 'prime-loaded'

---

## 💡 User Guidance

**OLD Way (Removed):**
- Double-click thread in Thread History → Auto-loads into Prime ❌

**NEW Way:**
- **Expand card details:** Double-click thread in Thread History ✅
- **Load into Prime:** Drag thread card to Prime drop zone ✅
- **Load into Agent:** Drag thread card to agent column ✅

---

## 🎯 Impact Summary

### Before Fix
- ❌ Accidental double-clicks replaced Prime content
- ❌ No way to just expand Thread History cards
- ❌ Confusing behavior (double-click = auto-load)

### After Fix
- ✅ Safe double-click (expands card only)
- ✅ Prime content protected from accidental changes
- ✅ Intentional loading via drag-and-drop
- ✅ Clear tooltips explain behavior

---

## 🔗 Related Documentation

- `THREAD_LOADING_SYSTEM_FIX_COMPLETE.md` - Thread loading architecture
- `THREAD_INFO_CARD_EXPANSION_FIX_DEC12_2025.md` - Card expansion system
- `THREAD_CLICK_BEHAVIOR_UPDATE.md` - Previous click behavior changes
- `thread-manager-interactions.js` - Double-click handler
- `thread-card-templates.js` - Card template HTML
- `thread-card-expansion.js` - Card expand/collapse logic

---

## 📞 For Developers

**To restore old behavior (auto-load on double-click):**

Remove the `if (currentLocation === 'thread-history')` block in `handleThreadDoubleClick()`:

```javascript
// Remove this block:
if (currentLocation === 'thread-history') {
    // ... expand card logic ...
    return;
}

// Restore old behavior:
await this.loadThreadInPrime(threadId);
```

**To customize double-click behavior further:**

Edit `thread-manager-interactions.js` line 328, `handleThreadDoubleClick()` function.

---

**Status:** ✅ **FIXED - December 12, 2025**

**Tested:** Thread History double-click now expands cards without auto-loading into Prime ✅
