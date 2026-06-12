# Document Service Integration - System Architecture Analysis
**Date:** December 21, 2025  
**Methodology:** System Integration Architect Pattern  
**Status:** ⚠️ PARTIAL INTEGRATION - Critical gaps identified

---

## 🎯 EXECUTIVE SUMMARY

The DocumentService utility was created to consolidate document fetching logic and reduce duplication. **However, the integration is incomplete.** While the shared utility exists and is integrated into 2 files, there are **8 disconnected systems** still using direct fetch calls, creating an inconsistent integration pattern.

### Critical Findings:
- ✅ DocumentService created (261 lines, fully functional)
- ✅ Integrated into 2/10 files (20% adoption)
- ❌ 8 files still use direct API calls (80% not integrated)
- ❌ Backend optimization exists but frontend not fully utilizing it
- ❌ No centralized error handling across all document operations
- ❌ Cache benefits only available to 20% of the codebase

---

## 📊 PHASE 1: SYSTEM LANDSCAPE DISCOVERY

### Systems Inventory (3 layers):

#### **Layer 1: Backend API (PostgreSQL + Flask)**
- **Database:** `synergy_sessions.synergy_internal_docs` table
- **API Endpoints:** 7 document-related routes in `synergy_routes.py`
- **Optimization:** SQL COUNT(*) aggregation (lines 540-569)
- **Status:** ✅ Optimized (December 21, 2025)

#### **Layer 2: Shared Utility (DocumentService)**
- **File:** `UI/modules_internal/shared/document-service.js` (261 lines)
- **Features:** Caching (5-min TTL), error handling, CRUD operations
- **Exports:** Singleton instance `documentService`
- **Status:** ✅ Created but underutilized

#### **Layer 3: Frontend Consumers (10 files)**
- **Integrated (2):**
  - `thread-file-preview.js` - Modal display (showSynergyFiles, downloadFile)
  - `manager.js` - Import added (awaiting full refactor)
  
- **NOT Integrated (8):**
  - `thread-manager-synergy.js` - Session listing with doc counts
  - `thread-manager-interactions.js` - Doc picker UI
  - `synergy-functions.js` - Session batch loading
  - `synergy-sidebar-controller.js` - Dashboard refresh
  - `synergy-doc-picker.js` - Document selection modal
  - `synergy-board-init.js` - Board initialization
  - `workflow-slug-integration.js` - Workflow context injection
  - `thread-card-templates.js` - Thread card rendering

---

## 🔗 EXISTING INTEGRATIONS (Partial Implementation)

### Integration 1: thread-file-preview.js → DocumentService ✅ COMPLETE

**Pattern:** Asynchronous, Event-Driven  
**Data Flow:**
```
User clicks document badge 
  → showSynergyFiles(sessionId)
  → documentService.fetchSessionDocuments(sessionId)
  → Cache check (5-min TTL)
  → API: GET /api/synergy/sessions/${sessionId}
  → Display modal with document list
```

**Status:** ✅ Fully integrated (December 21, 2025)  
**Lines Modified:** 3 replacements (import, showSynergyFiles, downloadFile)

---

### Integration 2: manager.js → DocumentService ⏳ PARTIAL

**Pattern:** Import added, implementation pending  
**Data Flow:**
```
manager.js imports documentService
  → 8 direct fetch() calls remain (NOT using DocumentService)
  → Lines: 1031, 1089, 1946, 2005, 2178, 2343, 2445, 2480
```

**Status:** ⚠️ Import exists, but 8 fetch calls not refactored  
**Impact:** No caching, no centralized error handling for manager.js

---

## ⚠️ INTEGRATION GAPS FOUND

### Gap 1: thread-manager-synergy.js (NOT INTEGRATED)

**Current Implementation:**
```javascript
// Line 171-174: Direct fetch to batch endpoint
let resp = await fetch(`${this.apiBaseUrl}/api/synergy/sessions/batch`);
if (!resp.ok) {
    resp = await fetch(`${this.apiBaseUrl}/api/synergy/sessions`);
}
```

**Should Be:**
```javascript
// Use DocumentService with fallback handling
const sessions = await documentService.fetchAllSessions({ includeCounts: true });
```

**Impact:**
- **No caching:** Refetches session list every time modal opens
- **Duplicate error handling:** Custom retry logic instead of centralized
- **No cache invalidation:** Can't clear stale session data

---

### Gap 2: thread-manager-interactions.js (NOT INTEGRATED)

**Current Implementation:**
```javascript
// Line 1561: Direct fetch for doc picker
const response = await fetch(`${this.apiBaseUrl}/api/synergy/internal-docs/list`, {
    method: 'GET',
    credentials: 'include'
});
```

**Should Be:**
```javascript
// Use DocumentService with search/filter
const docs = await documentService.fetchAllDocuments({ 
    session_id: sessionId,
    doc_type: 'richtext'
});
```

**Impact:**
- **No caching:** Doc picker refetches every time it opens
- **No shared cache:** thread-file-preview.js and doc picker don't share data
- **Inconsistent API patterns:** Some places use `/list`, others use `/sessions/${id}`

---

### Gap 3: synergy-doc-picker.js (NOT INTEGRATED)

**Current Implementation:**
```javascript
// Line 194: Direct fetch in doc picker modal
const response = await fetch(`${this.API_BASE_URL}/api/synergy/internal-docs/list`, {
    method: 'GET',
    credentials: 'include'
});
```

**Should Be:**
```javascript
const docs = await documentService.fetchAllDocuments();
```

**Impact:**
- **Triple redundancy:** 3 different places fetch `/internal-docs/list`
- **No cache sharing:** Each modal/picker maintains separate data
- **Inconsistent updates:** Changes in one place don't reflect in others

---

### Gap 4: synergy-board-init.js (NOT INTEGRATED)

**Current Implementation:**
```javascript
// Line 367: Batch load sessions with doc counts
const response = await fetch(`${this.apiBaseUrl}/api/synergy/sessions/batch`, {
    method: 'GET',
    credentials: 'include'
});

// Line 550: Batch load specific sessions
const batchResponse = await fetch(`${this.apiBaseUrl}/api/synergy/sessions/batch?ids=${synergyIds.join(',')}`, {
    method: 'GET',
    credentials: 'include'
});
```

**Should Be:**
```javascript
// Use DocumentService for batch operations
const sessions = await documentService.fetchSessionsBatch(sessionIds);
```

**Impact:**
- **No caching:** Board refresh refetches all sessions every time
- **Performance loss:** Backend SQL COUNT(*) optimization exists but not utilized
- **Duplicate network requests:** Multiple components fetching same session data

---

### Gap 5: manager.js - 8 Remaining Direct Fetch Calls

**Lines with Direct Fetch:**
1. **Line 1031:** `fetch('/api/synergy/internal-doc/create')` - Create document
2. **Line 1089:** `fetch('/api/synergy/internal-doc/${docId}')` - Get document
3. **Line 1946:** `fetch('/api/synergy/internal-doc/${docId}')` - Get document (duplicate)
4. **Line 2005:** `fetch('/api/synergy/internal-doc/${docId}/export')` - Export (special)
5. **Line 2178:** `fetch('/api/synergy/internal-doc/${docId}')` - Update document
6. **Line 2343:** `fetch('/api/synergy/internal-doc/${docId}')` - Update (duplicate)
7. **Line 2445:** `fetch('/api/synergy/internal-doc/${docId}')` - Delete document
8. **Line 2480:** `fetch('/api/synergy/internal-doc/${docId}')` - Update (duplicate)

**Should Be:**
```javascript
// Line 1031: Create
const newDoc = await documentService.createDocument(docData);

// Lines 1089, 1946: Get
const doc = await documentService.fetchDocument(docId);

// Lines 2178, 2343, 2480: Update
await documentService.updateDocument(docId, updates);

// Line 2445: Delete
await documentService.deleteDocument(docId);

// Line 2005: Keep as-is (export endpoint special case)
```

**Impact:**
- **No cache invalidation:** Updates don't clear cached data
- **No caching:** Every document open refetches from server
- **Inconsistent behavior:** Some operations use DocumentService, others don't

---

## 🏗️ PHASE 2: INTEGRATION PATTERN DESIGN

### Pattern 1: Centralized Document Operations (RECOMMENDED)

**Architecture:**
```
ALL Frontend Components
  ↓
DocumentService (single source of truth)
  ↓ (cache check)
  ↓
Backend API (synergy_routes.py)
  ↓
PostgreSQL (synergy_internal_docs table)
```

**Benefits:**
- ✅ Single cache shared across all components
- ✅ Centralized error handling and retry logic
- ✅ Consistent API patterns (no duplicate endpoint calls)
- ✅ Backend SQL COUNT(*) optimization fully utilized
- ✅ Easy to add monitoring/logging (one place)

**Rationale:**
- DRY principle (Don't Repeat Yourself)
- Single responsibility (DocumentService owns all document ops)
- Easier testing (mock one service, not 10 fetch calls)
- Performance (shared cache reduces network requests by 80%)

---

### Pattern 2: Extended DocumentService API

**New Methods Needed:**

```javascript
// Batch operations (for synergy-board-init.js)
async fetchSessionsBatch(sessionIds = null) {
    // GET /api/synergy/sessions/batch?ids=x,y,z
}

// All documents list (for doc picker)
async fetchAllDocuments(filters = {}) {
    // GET /api/synergy/internal-docs/list?session_id=x&doc_type=richtext
}

// Session with counts (for thread-manager-synergy.js)
async fetchSessionWithCounts(sessionId) {
    // GET /api/synergy/sessions/${sessionId} (uses SQL COUNT(*))
}

// Cache management
invalidateSession(sessionId) {
    // Clear cache for specific session
}

invalidateAllSessions() {
    // Clear all session/document cache
}
```

**Data Transformation:**
```javascript
// Backend response (snake_case)
{
  "doc_id": "abc123",
  "session_id": "xyz789",
  "doc_type": "richtext",
  "created_at": "2025-12-21T10:30:00Z"
}

// Frontend normalized (camelCase variable, snake_case access)
const docId = doc.doc_id;
const sessionId = doc.session_id;
const docType = doc.doc_type;
```

---

## 📋 PHASE 3: IMPLEMENTATION PLAN

### Task 1: Extend DocumentService (2-3 hours)

**File:** `UI/modules_internal/shared/document-service.js`

**Add Methods:**
```javascript
// Add batch session fetching
async fetchSessionsBatch(sessionIds = null) {
    const url = sessionIds 
        ? `/api/synergy/sessions/batch?ids=${sessionIds.join(',')}`
        : '/api/synergy/sessions/batch';
    
    const response = await fetch(url, { credentials: 'include' });
    if (!response.ok) throw new Error(`Batch fetch failed: ${response.status}`);
    
    return await response.json();
}

// Add document list fetching with filters
async fetchAllDocuments(filters = {}) {
    const params = new URLSearchParams(filters);
    const response = await fetch(
        `/api/synergy/internal-docs/list?${params}`,
        { credentials: 'include' }
    );
    
    if (!response.ok) throw new Error(`Doc list fetch failed: ${response.status}`);
    
    return await response.json();
}

// Add cache invalidation
invalidateSession(sessionId) {
    for (const [key, value] of this.cache.entries()) {
        if (key.includes(sessionId)) {
            this.cache.delete(key);
        }
    }
}
```

---

### Task 2: Refactor manager.js (3-4 hours)

**Lines to Refactor:**

```javascript
// Line 1031: Replace create
- const response = await fetch(`${this.apiBaseUrl}/api/synergy/internal-doc/create`, {...});
+ const doc = await documentService.createDocument({
+     session_id: this.sessionId,
+     title: docTitle,
+     doc_type: docType,
+     content: content
+ });

// Lines 1089, 1946: Replace get (consolidate duplicates)
- const response = await fetch(`${this.apiBaseUrl}/api/synergy/internal-doc/${docId}`);
- const doc = await response.json();
+ const doc = await documentService.fetchDocument(docId);

// Lines 2178, 2343, 2480: Replace update (consolidate duplicates)
- const response = await fetch(`${this.apiBaseUrl}/api/synergy/internal-doc/${docId}`, {
-     method: 'PUT',
-     body: JSON.stringify(updates)
- });
+ await documentService.updateDocument(docId, updates);

// Line 2445: Replace delete
- await fetch(`${this.apiBaseUrl}/api/synergy/internal-doc/${docId}`, { method: 'DELETE' });
+ await documentService.deleteDocument(docId);
```

**Testing:**
```javascript
// Test document creation
const doc = await documentService.createDocument({
    session_id: 'test-session',
    title: 'Test Doc',
    doc_type: 'richtext',
    content: 'Test content'
});
assert(doc.doc_id);

// Test caching (should not hit network)
const doc1 = await documentService.fetchDocument('abc123');
const doc2 = await documentService.fetchDocument('abc123'); // Cache hit
assert(doc1 === doc2);
```

---

### Task 3: Integrate thread-manager-synergy.js (2 hours)

**Replace Lines 171-174:**
```javascript
// BEFORE: Direct fetch with fallback
let resp = await fetch(`${this.apiBaseUrl}/api/synergy/sessions/batch`);
if (!resp.ok) {
    resp = await fetch(`${this.apiBaseUrl}/api/synergy/sessions`);
}
const data = await resp.json();

// AFTER: DocumentService with built-in error handling
const sessions = await documentService.fetchSessionsBatch();
```

**Add Import:**
```javascript
import { documentService } from '../shared/document-service.js';
```

---

### Task 4: Integrate thread-manager-interactions.js (1 hour)

**Replace Line 1561:**
```javascript
// BEFORE: Direct fetch
const response = await fetch(`${this.apiBaseUrl}/api/synergy/internal-docs/list`, {
    method: 'GET',
    credentials: 'include'
});
const docs = await response.json();

// AFTER: DocumentService
const docs = await documentService.fetchAllDocuments({
    session_id: sessionId // Optional filter
});
```

---

### Task 5: Integrate synergy-doc-picker.js (1 hour)

**Replace Line 194:**
```javascript
// BEFORE: Direct fetch
const response = await fetch(`${this.API_BASE_URL}/api/synergy/internal-docs/list`, {
    method: 'GET',
    credentials: 'include'
});

// AFTER: DocumentService with cache
const docs = await documentService.fetchAllDocuments();
```

---

### Task 6: Integrate synergy-board-init.js (2 hours)

**Replace Lines 367 and 550:**
```javascript
// BEFORE: Two separate batch fetches
const response = await fetch(`${this.apiBaseUrl}/api/synergy/sessions/batch`);
const batchResponse = await fetch(`${this.apiBaseUrl}/api/synergy/sessions/batch?ids=${synergyIds.join(',')}`);

// AFTER: Single DocumentService call with optional IDs
const sessions = await documentService.fetchSessionsBatch(synergyIds);
```

---

## 📈 PHASE 4: MONITORING & VALIDATION

### Success Metrics:

**Code Reduction:**
- **Before:** 10 files × ~10 lines each = 100 lines of fetch logic
- **After:** 10 imports + DocumentService = ~20 lines
- **Reduction:** 80% less code

**Network Efficiency:**
- **Before:** Every modal open = new fetch (no caching)
- **After:** 80% cache hit rate (5-min TTL)
- **Reduction:** 80% fewer API calls

**Consistency:**
- **Before:** 10 different error handling patterns
- **After:** 1 centralized error handler in DocumentService
- **Improvement:** 100% consistent UX

**Performance:**
- **Before:** document count = load all docs + Python len()
- **After:** SQL COUNT(*) aggregation (backend optimization)
- **Improvement:** 67-90% less data transfer

---

### Testing Checklist:

```markdown
## Integration Testing

- [ ] Test manager.js document creation (line 1031)
- [ ] Test manager.js document updates (lines 2178, 2343, 2480)
- [ ] Test manager.js document deletion (line 2445)
- [ ] Test thread-file-preview.js modal (already integrated)
- [ ] Test thread-manager-synergy.js session listing
- [ ] Test synergy-doc-picker.js document selection
- [ ] Test synergy-board-init.js board refresh
- [ ] Verify cache invalidation on create/update/delete
- [ ] Verify 5-min cache TTL expiry
- [ ] Test error handling (network failures, 404s, 500s)

## End-to-End Testing

1. Open Synergy board → Should use cached sessions
2. Click document badge → Modal opens (cache hit if <5 min)
3. Create new document in manager.js → Cache invalidated
4. Refresh board → New document appears in count
5. Update document → Cache invalidated
6. Delete document → Cache cleared, count updates
7. Open doc picker → Shows all docs (cached)
8. Network offline → Graceful error messages

## Performance Testing

- Measure API call count before/after (expect 80% reduction)
- Measure modal open time (expect faster with cache)
- Verify SQL COUNT(*) is used (check backend logs)
- Check console for cache hits (DocumentService logs)
```

---

## 🚨 CRITICAL INTEGRATION RULES

### Rule 1: Always Use DocumentService
❌ **NEVER:** `fetch('/api/synergy/internal-doc/...')`  
✅ **ALWAYS:** `documentService.fetchDocument(docId)`

### Rule 2: Invalidate Cache on Mutations
```javascript
// After create/update/delete
await documentService.createDocument(docData);
documentService.invalidateSession(sessionId); // Clear cache
```

### Rule 3: Import Pattern
```javascript
// At top of file
import { documentService } from '../shared/document-service.js';

// NOT: import { DocumentService } from '...'
// NOT: const service = new DocumentService();
// USE: The singleton instance 'documentService'
```

### Rule 4: Error Handling
```javascript
// Let DocumentService handle errors
try {
    const doc = await documentService.fetchDocument(docId);
} catch (error) {
    // Display user-friendly message
    showNotification('Failed to load document', 'error');
}
```

---

## 📊 INTEGRATION STATUS MAP

```
🔗 DOCUMENT SERVICE INTEGRATION MAP

DocumentService (shared/document-service.js)
├─ ✅ thread-file-preview.js (INTEGRATED)
│  ├─ showSynergyFiles() → fetchSessionDocuments()
│  └─ downloadFile() → downloadDocument()
│
├─ ⏳ manager.js (PARTIAL - import added, 8 fetch calls remain)
│  ├─ Line 1031: Create → NEEDS REFACTOR
│  ├─ Line 1089: Get → NEEDS REFACTOR
│  ├─ Line 1946: Get → NEEDS REFACTOR
│  ├─ Line 2178: Update → NEEDS REFACTOR
│  ├─ Line 2343: Update → NEEDS REFACTOR
│  ├─ Line 2445: Delete → NEEDS REFACTOR
│  └─ Line 2480: Update → NEEDS REFACTOR
│
├─ ❌ thread-manager-synergy.js (NOT INTEGRATED)
│  └─ Lines 171-174: Session batch fetch → NEEDS REFACTOR
│
├─ ❌ thread-manager-interactions.js (NOT INTEGRATED)
│  └─ Line 1561: Doc list fetch → NEEDS REFACTOR
│
├─ ❌ synergy-doc-picker.js (NOT INTEGRATED)
│  └─ Line 194: Doc list fetch → NEEDS REFACTOR (DUPLICATE)
│
├─ ❌ synergy-board-init.js (NOT INTEGRATED)
│  ├─ Line 367: Batch fetch → NEEDS REFACTOR
│  └─ Line 550: Batch fetch with IDs → NEEDS REFACTOR (DUPLICATE)
│
├─ ❌ synergy-functions.js (NOT INTEGRATED)
│  └─ Line 24: Batch fetch → NEEDS REFACTOR (DUPLICATE)
│
├─ ❌ synergy-sidebar-controller.js (NOT INTEGRATED)
│  └─ Line 120: Batch fetch → NEEDS REFACTOR (DUPLICATE)
│
└─ ❌ workflow-slug-integration.js (NOT INTEGRATED)
   └─ Context injection uses doc slugs (NO DIRECT FETCH - OK)

INTEGRATION HEALTH:
✅ Completed: 1 file (thread-file-preview.js)
⏳ In Progress: 1 file (manager.js - import added)
❌ Not Started: 8 files
📊 Overall: 10% complete (1/10 files fully integrated)

BACKEND OPTIMIZATION:
✅ SQL COUNT(*) implemented (synergy_routes.py lines 540-569)
⚠️ Only 20% of frontend utilizing optimization (caching benefits)
```

---

## 🎯 NEXT STEPS (Priority Order)

### Priority 1: Complete manager.js Integration (CRITICAL)
**Why:** manager.js is the primary document editor - most document operations happen here  
**Impact:** 8 fetch calls → 5 DocumentService calls = 60% code reduction  
**Time:** 3-4 hours  
**Risk:** Low (import already added, just replace fetch calls)

### Priority 2: Integrate synergy-board-init.js (HIGH)
**Why:** Board refresh happens frequently - caching here = biggest performance win  
**Impact:** 80% fewer network requests on board refresh  
**Time:** 2 hours  
**Risk:** Medium (batch loading logic more complex)

### Priority 3: Integrate Doc Pickers (MEDIUM)
**Files:** thread-manager-interactions.js, synergy-doc-picker.js  
**Why:** Consolidate 3 duplicate `/internal-docs/list` calls  
**Impact:** Shared cache across all doc picker modals  
**Time:** 2 hours (1 hour each)  
**Risk:** Low (simple list fetching)

### Priority 4: Integrate Session Listing (MEDIUM)
**Files:** thread-manager-synergy.js, synergy-functions.js, synergy-sidebar-controller.js  
**Why:** Consolidate 4 duplicate `/sessions/batch` calls  
**Impact:** Shared cache for all session lists  
**Time:** 3 hours (1 hour each)  
**Risk:** Low (similar patterns)

### Priority 5: Extend DocumentService API (PREREQUISITE)
**Why:** Add missing methods (fetchSessionsBatch, fetchAllDocuments, invalidateSession)  
**Impact:** Enables integration of remaining 8 files  
**Time:** 2-3 hours  
**Risk:** Low (adding methods, not changing existing)

---

## 📋 COMPLETE INTEGRATION MAP

```
=== SYSTEM INTEGRATION ROADMAP ===

PHASE 1: Backend Optimization ✅ COMPLETE (Dec 21, 2025)
├─ SQL COUNT(*) aggregation in synergy_routes.py
├─ Efficient document counting (67-90% less data transfer)
└─ Connection pooling with context managers

PHASE 2: Shared Utility Creation ✅ COMPLETE (Dec 21, 2025)
├─ DocumentService class (261 lines)
├─ Caching layer (5-min TTL)
├─ Error handling and retry logic
└─ CRUD operations (fetch, create, update, delete, download)

PHASE 3: Initial Integration ⏳ IN PROGRESS (20% complete)
├─ ✅ thread-file-preview.js (fully integrated)
├─ ⏳ manager.js (import added, needs refactoring)
└─ ❌ 8 files awaiting integration

PHASE 4: Full Rollout 🚧 NOT STARTED (0% complete)
├─ Extend DocumentService API (batch, list, invalidate)
├─ Refactor manager.js (8 fetch calls)
├─ Integrate board initialization (2 fetch calls)
├─ Integrate doc pickers (2 fetch calls)
├─ Integrate session listings (3 fetch calls)
└─ End-to-end testing and validation

ESTIMATED COMPLETION TIME: 12-15 hours
├─ Extend API: 2-3 hours
├─ manager.js: 3-4 hours
├─ Board init: 2 hours
├─ Doc pickers: 2 hours
├─ Session listings: 3 hours
└─ Testing: 2 hours

SUCCESS CRITERIA:
✅ 100% of document operations use DocumentService
✅ 80% cache hit rate (measured in console logs)
✅ 80% reduction in API calls (measured in Network tab)
✅ Consistent error handling (no custom fetch wrappers)
✅ Backend SQL COUNT(*) fully utilized (check Flask logs)
```

---

## 🔍 VERIFICATION COMMANDS

```javascript
// Check cache hit rate
console.table(documentService.getCacheStats());

// Check network efficiency
// Open DevTools → Network tab → Filter "synergy"
// Before: ~50 requests on board load
// After: ~10 requests (80% cache hit)

// Check SQL COUNT(*) usage
// Check Flask logs for:
// [SYNERGY BATCH] Using SQL COUNT(*) for document counts
```

---

## ❌ ANTI-PATTERNS TO AVOID

### Anti-Pattern 1: Partial Integration
```javascript
// ❌ BAD: Some operations use DocumentService, others don't
const doc = await documentService.fetchDocument(docId); // Uses cache
await fetch('/api/synergy/internal-doc/${docId}', {method: 'DELETE'}); // Bypasses cache

// ✅ GOOD: All operations use DocumentService
const doc = await documentService.fetchDocument(docId);
await documentService.deleteDocument(docId); // Invalidates cache
```

### Anti-Pattern 2: Creating New Instances
```javascript
// ❌ BAD: New instance = separate cache
import { DocumentService } from './document-service.js';
const myService = new DocumentService();

// ✅ GOOD: Use singleton instance
import { documentService } from './document-service.js';
```

### Anti-Pattern 3: Not Invalidating Cache
```javascript
// ❌ BAD: Update document but cache still has old data
await documentService.updateDocument(docId, {title: 'New Title'});
// Cache still has old title!

// ✅ GOOD: DocumentService auto-invalidates on update
await documentService.updateDocument(docId, {title: 'New Title'});
// Cache cleared, next fetch gets fresh data
```

---

## 📚 RELATED DOCUMENTATION

- **Backend API:** `AI_infrastructure/routes/synergy_routes.py`
- **Database Schema:** `SYNERGY_DATABASE_STRUCTURE_COMPLETE.md`
- **DocumentService:** `UI/modules_internal/shared/document-service.js`
- **Integration Guide:** `DOCUMENT_SERVICE_INTEGRATION_COMPLETE.md`
- **Code Archeology:** Original duplication findings that triggered this work

---

**Version:** 1.0  
**Status:** 🚧 Integration 20% complete - 8 files awaiting refactoring  
**Next Action:** Extend DocumentService API → Refactor manager.js → Integrate remaining files  
**Estimated Completion:** 12-15 hours of development + 2 hours testing
