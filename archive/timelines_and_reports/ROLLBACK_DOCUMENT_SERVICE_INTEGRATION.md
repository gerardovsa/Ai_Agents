# Rollback Guide - Document Service Integration
**Date:** December 21, 2025  
**Purpose:** Complete rollback instructions for DocumentService integration

---

## 🔄 Quick Rollback Commands

### Option 1: Git Rollback (If Committed)
```powershell
# View changes
git diff HEAD~1

# Rollback last commit (keeps changes as uncommitted)
git reset --soft HEAD~1

# Rollback and discard changes
git reset --hard HEAD~1
```

### Option 2: Manual Rollback (Use sections below)

---

## 📁 FILES MODIFIED (In Order)

### 1. document-service.js - EXTENDED API
**File:** `UI/modules_internal/shared/document-service.js`  
**Changes:** Added 3 new methods  
**Lines:** ~270-350 (appended after existing methods)

**Rollback:** Remove the following methods:
- `fetchSessionsBatch(sessionIds = null)`
- `fetchAllDocuments(filters = {})`
- `invalidateSession(sessionId)`

### 2. manager.js - 8 FETCH REPLACEMENTS
**File:** `UI/modules_internal/internal_docs/manager.js`  
**Changes:** Replaced 8 direct fetch() calls with documentService calls

**Modified Lines:**
- Line ~1031: createDocument() - Changed fetch to documentService.createDocument()
- Line ~1089: Get document - Changed fetch to documentService.fetchDocument()
- Line ~1946: Get document - Changed fetch to documentService.fetchDocument()
- Line ~2178: Update document - Changed fetch to documentService.updateDocument()
- Line ~2343: Update document - Changed fetch to documentService.updateDocument()
- Line ~2445: Delete document - Changed fetch to documentService.deleteDocument()
- Line ~2480: Update document - Changed fetch to documentService.updateDocument()

**Rollback Pattern:**
```javascript
// REVERT THIS:
const doc = await documentService.fetchDocument(docId);

// BACK TO THIS:
const response = await fetch(`${this.apiBaseUrl}/api/synergy/internal-doc/${docId}`, {
    method: 'GET',
    credentials: 'include'
});
const doc = await response.json();
```

### 3. thread-manager-synergy.js - SESSION BATCH FETCH
**File:** `UI/modules_internal/thread-manager/thread-manager-synergy.js`  
**Changes:** Replaced batch fetch logic  
**Lines:** ~171-180

**Rollback:**
```javascript
// REVERT THIS:
import { documentService } from '../shared/document-service.js';
const sessions = await documentService.fetchSessionsBatch();

// BACK TO THIS:
let resp = await fetch(`${this.apiBaseUrl}/api/synergy/sessions/batch`);
if (!resp.ok) {
    resp = await fetch(`${this.apiBaseUrl}/api/synergy/sessions`);
}
const data = await resp.json();
```

### 4. thread-manager-interactions.js - DOC LIST FETCH
**File:** `UI/modules_internal/thread-manager/thread-manager-interactions.js`  
**Changes:** Replaced doc list fetch  
**Lines:** ~1560-1570

**Rollback:**
```javascript
// REVERT THIS:
import { documentService } from '../shared/document-service.js';
const docs = await documentService.fetchAllDocuments({ session_id: sessionId });

// BACK TO THIS:
const response = await fetch(`${this.apiBaseUrl}/api/synergy/internal-docs/list`, {
    method: 'GET',
    credentials: 'include'
});
const docs = await response.json();
```

### 5. synergy-doc-picker.js - DOC LIST FETCH
**File:** `UI/modules_internal/synergy/synergy-doc-picker.js`  
**Changes:** Replaced doc list fetch  
**Lines:** ~194-205

**Rollback:**
```javascript
// REVERT THIS:
import { documentService } from '../shared/document-service.js';
const docs = await documentService.fetchAllDocuments();

// BACK TO THIS:
const response = await fetch(`${this.API_BASE_URL}/api/synergy/internal-docs/list`, {
    method: 'GET',
    credentials: 'include'
});
const docs = await response.json();
```

### 6. synergy-board-init.js - BATCH FETCH (2 places)
**File:** `UI/modules_internal/synergy/synergy-board-init.js`  
**Changes:** Replaced 2 batch fetch calls  
**Lines:** ~367 and ~550

**Rollback:**
```javascript
// REVERT THIS:
import { documentService } from '../shared/document-service.js';
const sessions = await documentService.fetchSessionsBatch(sessionIds);

// BACK TO THIS:
const response = await fetch(`${this.apiBaseUrl}/api/synergy/sessions/batch`, {
    method: 'GET',
    credentials: 'include'
});
const sessions = await response.json();
```

### 7. synergy-functions.js - BATCH FETCH
**File:** `UI/modules_internal/synergy/synergy-functions.js`  
**Changes:** Replaced batch fetch  
**Lines:** ~24

**Rollback:**
```javascript
// REVERT THIS:
import { documentService } from '../shared/document-service.js';
const data = await documentService.fetchSessionsBatch();

// BACK TO THIS:
const response = await fetch(`${API_BASE_URL}/api/synergy/sessions/batch`);
const data = await response.json();
```

### 8. synergy-sidebar-controller.js - BATCH FETCH
**File:** `UI/modules_internal/synergy/synergy-sidebar-controller.js`  
**Changes:** Replaced batch fetch  
**Lines:** ~120

**Rollback:**
```javascript
// REVERT THIS:
import { documentService } from '../shared/document-service.js';
const data = await documentService.fetchSessionsBatch();

// BACK TO THIS:
const response = await fetch(`${this.API_BASE_URL}/api/synergy/sessions/batch`);
const data = await response.json();
```

---

## 🔍 VERIFICATION AFTER ROLLBACK

```powershell
# 1. Check syntax of all files
node --check UI\modules_internal\shared\document-service.js
node --check UI\modules_internal\internal_docs\manager.js
node --check UI\modules_internal\thread-manager\thread-manager-synergy.js
node --check UI\modules_internal\thread-manager\thread-manager-interactions.js
node --check UI\modules_internal\synergy\synergy-doc-picker.js
node --check UI\modules_internal\synergy\synergy-board-init.js
node --check UI\modules_internal\synergy\synergy-functions.js
node --check UI\modules_internal\synergy\synergy-sidebar-controller.js

# 2. Start Flask server
cd AI_infrastructure
python flask_app.py

# 3. Test in browser
# - Open Synergy board
# - Click document badge (should work)
# - Open doc picker (should work)
# - Refresh board (should work)
```

---

## 📊 ROLLBACK DECISION TREE

### If Everything Works:
✅ Keep changes - no rollback needed

### If Caching Issues:
1. Clear browser cache (Ctrl+Shift+Delete)
2. Hard refresh (Ctrl+F5)
3. Check console for cache errors
4. If persist → Rollback document-service.js extended API only

### If Fetch Errors (404, 500):
1. Check Flask logs for endpoint errors
2. Verify API_BASE_URL is correct
3. If endpoints broken → Rollback specific file causing issue

### If Syntax Errors:
1. Run `node --check` on failed file
2. Check console for import errors
3. Rollback that specific file

### If Performance Degraded:
1. Check Network tab (should show fewer requests)
2. If more requests → Rollback all, investigate cache issue
3. If slower → Check for blocking await calls

---

## 🚨 EMERGENCY FULL ROLLBACK

```powershell
# 1. Stop Flask server
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# 2. Restore all files (if using Git)
git checkout HEAD -- UI/modules_internal/shared/document-service.js
git checkout HEAD -- UI/modules_internal/internal_docs/manager.js
git checkout HEAD -- UI/modules_internal/thread-manager/thread-manager-synergy.js
git checkout HEAD -- UI/modules_internal/thread-manager/thread-manager-interactions.js
git checkout HEAD -- UI/modules_internal/synergy/synergy-doc-picker.js
git checkout HEAD -- UI/modules_internal/synergy/synergy-board-init.js
git checkout HEAD -- UI/modules_internal/synergy/synergy-functions.js
git checkout HEAD -- UI/modules_internal/synergy/synergy-sidebar-controller.js

# 3. Clear browser cache
# Ctrl+Shift+Delete → Clear all

# 4. Restart Flask server
cd AI_infrastructure
python flask_app.py

# 5. Test in browser
# Should be back to pre-integration state
```

---

## 📝 ROLLBACK LOG

Use this section to track partial rollbacks:

### Rollback Entry Template:
```
Date: YYYY-MM-DD HH:MM
File: [filename]
Reason: [why rolled back]
Status: [success/failed]
Notes: [additional context]
```

---

## 🔧 SELECTIVE ROLLBACK (File by File)

### Keep DocumentService Extended API + thread-file-preview.js (PROVEN STABLE)
Rollback everything except:
- ✅ `document-service.js` - Keep extended API
- ✅ `thread-file-preview.js` - Keep integration (already tested Dec 21)

### Rollback Only manager.js (If Issues There)
```powershell
git checkout HEAD -- UI/modules_internal/internal_docs/manager.js
```

### Rollback Only Board Files (If Performance Issues)
```powershell
git checkout HEAD -- UI/modules_internal/synergy/synergy-board-init.js
git checkout HEAD -- UI/modules_internal/synergy/synergy-functions.js
git checkout HEAD -- UI/modules_internal/synergy/synergy-sidebar-controller.js
```

---

## 📈 SUCCESS METRICS (To Verify Rollback Needed)

**Before deciding to rollback, check these metrics:**

### Network Efficiency (Chrome DevTools → Network)
- **Expected:** 80% fewer requests (cache working)
- **If seeing MORE requests:** Rollback needed

### Console Errors
- **Expected:** No errors, cache hit logs
- **If seeing errors:** Investigate first, rollback if critical

### User Experience
- **Expected:** Faster modal opens, same functionality
- **If slower or broken:** Rollback immediately

### Backend Logs
- **Expected:** Fewer `/api/synergy/internal-doc` calls
- **If same or more:** Cache not working, rollback

---

## 🎯 PARTIAL ROLLBACK STRATEGIES

### Strategy 1: Keep Core, Rollback Extensions
- ✅ Keep: `document-service.js` (original), `thread-file-preview.js`
- 🔄 Rollback: All 7 other files

### Strategy 2: Keep DocumentService, Rollback manager.js Only
- ✅ Keep: Extended API + 6 integration files
- 🔄 Rollback: manager.js (if issues there)

### Strategy 3: Rollback Everything, Rebuild Incrementally
- 🔄 Rollback: All 8 files
- ✅ Rebuild: One file at a time, test each

---

## 📞 SUPPORT CHECKLIST

Before asking for help, check:
- [ ] Ran syntax validation (`node --check`)
- [ ] Checked browser console for errors
- [ ] Checked Flask logs for API errors
- [ ] Cleared browser cache
- [ ] Hard refreshed page (Ctrl+F5)
- [ ] Tried rollback of specific file
- [ ] Verified Git history available
- [ ] Documented exact error message
- [ ] Noted which file/line causing issue

---

**Remember:** All changes are tracked in this document. If you need to rollback, follow the sections above based on what's broken.
