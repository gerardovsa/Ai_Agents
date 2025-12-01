# Prime Thread Loading Diagnostic Guide

**Issue:** Threads not loading into Prime AI chat container after double-clicking thread cards  
**Date:** December 1, 2025

## Quick Diagnosis Steps

### 1. Open Browser Console (F12)

### 2. Check if ThreadCardTemplates is loaded:
```javascript
console.log('ThreadCardTemplates:', typeof window.ThreadCardTemplates);
console.log('ThreadManager:', typeof window.ThreadManager);
console.log('loadThreadInPrime:', typeof window.ThreadManager?.loadThreadInPrime);
```

**Expected Output:**
```
ThreadCardTemplates: object
ThreadManager: object  
loadThreadInPrime: function
```

### 3. Test double-click handler manually:
```javascript
// Replace THREAD_ID with actual thread ID
ThreadManager.handleThreadDoubleClick('THREAD_ID', 'prime');
```

### 4. Check for script loading errors:
Look for red error messages in console like:
- ❌ `ThreadCardTemplates is not defined`
- ❌ `Cannot read property 'compactCard' of undefined`
- ❌ `loadThreadInPrime is not a function`

### 5. Verify thread card HTML has ondblclick:
```javascript
// Check any thread card
const card = document.querySelector('[data-thread-id]');
console.log('Has ondblclick:', card?.getAttribute('ondblclick'));
```

**Expected:** Should see `ThreadManager.handleThreadDoubleClick('...', '...')`

## Root Cause Analysis

### Possible Issue 1: ThreadCardTemplates Not Loaded
**Symptom:** Console shows `ThreadCardTemplates is not defined`  
**Cause:** Script failed to load or wrong path  
**Fix:** Check `business-ai-platform-v2.html` line 220:
```html
<script src="modules_internal/thread-cards/thread-card-templates.js?v=20251129"></script>
```

### Possible Issue 2: Old Cached Script
**Symptom:** Double-click does nothing, no console errors  
**Cause:** Browser cached old version without ondblclick attribute  
**Fix:** 
1. Hard refresh: `CTRL + SHIFT + R`
2. Clear cache: `CTRL + SHIFT + DELETE` → Clear Everything
3. Update version query param: `?v=20251201`

### Possible Issue 3: Script Load Order
**Symptom:** `ThreadManager.handleThreadDoubleClick is not a function`  
**Cause:** thread-manager-interactions.js loaded before thread-manager-core.js  
**Check:** View Network tab → JS files → Load order  
**Fix:** Ensure proper script order in HTML:
```html
<!-- Core must load first -->
<script src="modules_internal/thread-manager/thread-manager-core.js"></script>
<!-- Then interactions -->
<script src="modules_internal/thread-manager/thread-manager-interactions.js"></script>
```

### Possible Issue 4: Method Not Bound to ThreadManager
**Symptom:** Method exists but throws `this` errors when called  
**Cause:** Method not bound in thread-manager-core.js  
**Check:** Look in `thread-manager-core.js` line ~263:
```javascript
const methodsToProxy = [
    // ... other methods ...
    'loadThreadInPrime', 'handleThreadDoubleClick',  // ← These MUST be here
    // ...
];
```

## The Critical Flow (When Working Correctly)

```
1. User double-clicks thread card
   ↓
2. HTML ondblclick="ThreadManager.handleThreadDoubleClick('123', 'agent-1')"
   ↓
3. thread-manager-interactions.js → handleThreadDoubleClick()
   ↓
4. Calls: await this.loadThreadInPrime(threadId)
   ↓
5. thread-manager-interactions.js → loadThreadInPrime()
   ↓
6. Fetches thread data from backend
   ↓
7. Updates AppState.sessionId and AppState.chatMessages
   ↓
8. Calls: await this.assignThread(threadId, 'prime-loaded')
   ↓
9. thread-manager-assignment.js → assignThread()
   ↓
10. Updates database: SET location='prime-loaded'
    ↓
11. Calls: this.updatePrimeHeader(threadId)
    ↓
12. thread-manager-ui.js → updatePrimeHeader()
    ↓
13. Finds container: #prime-thread-info
    ↓
14. Calls: this.renderThreadInfoContainer('prime-loaded', threadId, false)
    ↓
15. thread-manager-ui.js → renderThreadInfoContainer()
    ↓
16. Calls: window.ThreadCardTemplates.compactCard(thread, 'prime', agent, meta, slug)
    ↓
17. thread-card-templates.js → compactCard()
    ↓
18. Returns HTML string with thread info card
    ↓
19. Sets: primeThreadInfo.innerHTML = cardHtml
    ↓
20. ✅ Thread card appears in Prime container!
```

## Manual Test Commands

### Test 1: Check if scripts loaded
```javascript
console.log({
    ThreadCardTemplates: !!window.ThreadCardTemplates,
    ThreadManager: !!window.ThreadManager,
    loadThreadInPrime: typeof ThreadManager?.loadThreadInPrime,
    handleThreadDoubleClick: typeof ThreadManager?.handleThreadDoubleClick,
    compactCard: typeof ThreadCardTemplates?.compactCard
});
```

### Test 2: List all thread IDs
```javascript
console.log('Available threads:', ThreadManager.threads.map(t => ({
    id: t.id,
    title: t.title,
    location: t.location
})));
```

### Test 3: Manually load a thread
```javascript
// Replace with real thread ID from Test 2
const threadId = 'YOUR_THREAD_ID_HERE';
ThreadManager.loadThreadInPrime(threadId)
    .then(() => console.log('✅ Thread loaded successfully'))
    .catch(err => console.error('❌ Failed to load thread:', err));
```

### Test 4: Check Prime container exists
```javascript
const primeContainer = document.getElementById('prime-thread-info');
console.log('Prime container:', {
    exists: !!primeContainer,
    innerHTML: primeContainer?.innerHTML?.length || 0,
    hasThread: primeContainer?.dataset?.threadId || 'none'
});
```

## Recent Changes That Could Affect This

### November 29, 2025 Changes:
1. ✅ Updated pill naming: "Automated Workflows" / "Workflows"
   - Changed: `thread-card-templates.js` lines 627-676
   - Impact: **SAFE** - Only changed text labels, not functionality

2. ✅ Deleted outdated duplicates:
   - Removed: `components/thread-cards-external/` 
   - Removed: `modules/thread-manager/thread-manager-ui.js`
   - Impact: **SAFE IF** browser uses correct file from `modules_internal/`

3. ✅ Created new modal systems:
   - Added: `workflow-link-modal.js`
   - Added: `automation-link-modal.js`
   - Added: `internal-docs-link-modal.js`
   - Impact: **SAFE** - New files, don't affect existing thread loading

### Potential Impact:
**IF** browser cached the OLD file from `components/thread-cards-external/thread-card-templates.js` (now deleted), it might not have the correct `ondblclick` handlers.

## Fix Steps (If Broken)

### Fix 1: Force Browser Refresh
```
1. Close all browser tabs with the app
2. Open new tab
3. Press CTRL + SHIFT + DELETE
4. Select "All time"
5. Check "Cached images and files"
6. Click "Clear data"
7. Navigate to http://localhost:5001
8. Hard refresh: CTRL + SHIFT + R
```

### Fix 2: Update Script Version Tag
In `business-ai-platform-v2.html` line 220, change:
```html
<!-- OLD -->
<script src="modules_internal/thread-cards/thread-card-templates.js?v=20251129"></script>

<!-- NEW -->
<script src="modules_internal/thread-cards/thread-card-templates.js?v=20251201"></script>
```

### Fix 3: Verify Method Binding
Check `thread-manager-core.js` around line 263:
```javascript
const methodsToProxy = [
    'renderThreadList', 'renderThreadHistory', 'renderThreadInfoContainer',
    'updatePrimeHeader', 'syncAppState', 'closeThreadMenu', 'renderEmptyState',
    'assignThread', 'unassignThread', 'loadThreadInAgent', 'refreshThreadData',
    'setupPrimeDropZone', 'handleThreadDoubleClick', 'handleDragStart', 'handleDragEnd', 'handleDrop',
    'loadThreadInPrime',  // ← Must be here
    // ...
];
```

### Fix 4: Restart Flask Server
Sometimes the issue is server-side:
```powershell
cd C:\Users\gpoli\GIT\AI_agents
Get-Process python | Where-Object { $_.Path -match "AI_agents" } | Stop-Process -Force
BISTART
```

## Success Indicators

✅ **Working correctly when:**
1. Console shows: `ThreadCardTemplates: object`
2. Double-clicking thread card shows notification: "Thread loaded in Prime"
3. Prime container (#prime-thread-info) updates with thread info
4. Console shows log: `📖 [Interactions] Loading thread "..." in Prime via double-click`
5. Console shows log: `✅ [renderThreadInfoContainer] Generated card HTML`

❌ **Still broken if:**
1. Double-click does nothing (no console logs)
2. Console error: `ThreadCardTemplates is not defined`
3. Console error: `handleThreadDoubleClick is not a function`
4. Thread info appears but immediately disappears
5. Prime container stays empty after double-click

## Contact Points for Further Investigation

If still broken after all fixes:

1. **Check script loading:**
   - Network tab → Filter: JS → Look for 404 errors
   - Check if `thread-card-templates.js` loads successfully
   
2. **Check method existence:**
   - Console: `Object.keys(ThreadManager)` → Should include `loadThreadInPrime`
   
3. **Check DOM:**
   - Console: `document.querySelectorAll('[ondblclick*="handleThreadDoubleClick"]').length`
   - Should return number > 0

4. **Check backend:**
   - Look for 500 errors in Network tab when double-clicking
   - Check Flask console for errors

---

**Last Updated:** December 1, 2025  
**Author:** AI Agent Diagnostics System  
**Status:** Active troubleshooting guide
