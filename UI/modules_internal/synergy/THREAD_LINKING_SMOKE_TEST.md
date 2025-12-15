# 🧪 Synergy Thread Linking - Complete Smoke Test

**Date:** 2025-12-15  
**Feature:** Drag-and-drop thread linking to Synergy sessions

## 📋 Test Checklist

### ✅ 1. Module Loading & Initialization

**Files to Check:**
- [x] `synergy-thread-drag-drop.js` - Main drag-drop logic
- [x] `synergy-thread-drag-drop.css` - Visual styling
- [x] `synergy-sidebar-renderer-v2-FLAT.js` - UI rendering with [+] button
- [x] `synergy-inline-edit.js` - Button click handlers
- [x] `synergy_routes.py` - Backend API endpoints

**Browser Console Test:**
```javascript
// Check if module loaded
console.log('Drag-drop module:', window.SynergyThreadDragDrop);
console.log('Instance:', window.synergyThreadDragDrop);
// Expected: [class SynergyThreadDragDrop] and instance object

// Check if renderer has button
document.querySelector('.synergy-open-thread-history-btn');
// Expected: <button class="synergy-flat-action-btn synergy-open-thread-history-btn">
```

---

### ✅ 2. UI Components Present

**Elements to Verify:**

1. **[+] Button in Linked Threads Section**
   - Location: Synergy sidebar → Expand any session card → Linked Threads section header
   - Class: `synergy-open-thread-history-btn`
   - Icon: `fa-plus`
   - Title: "Open Thread History"

2. **Thread History Sidebar**
   - Element ID: `thread-menu-overlay`
   - Should contain thread cards with class: `thread-info-card` or `thread-card-item`

3. **Drop Zone**
   - Class: `synergy-linked-threads-container`
   - Has `data-session-id` attribute
   - Empty state shows: "No linked threads" with drag-drop hint

**Visual Test:**
```javascript
// Count drop zones
document.querySelectorAll('.synergy-linked-threads-container').length;
// Expected: 1 per expanded Synergy card

// Count thread cards
document.querySelectorAll('.thread-info-card, .thread-card-item').length;
// Expected: > 0 (all available threads)
```

---

### ✅ 3. [+] Button Click Handler

**Test Steps:**
1. Open Synergy sidebar
2. Expand a Synergy session card
3. Scroll to "Linked Threads" section
4. Click the `[+]` button

**Expected Behavior:**
- Thread history sidebar (`#thread-menu-overlay`) toggles open/close
- Console log: `[SYNERGY] Thread history sidebar toggled for thread linking`

**Browser Console Test:**
```javascript
// Manual trigger
const btn = document.querySelector('.synergy-open-thread-history-btn');
btn.click();

// Check sidebar state
const threadMenu = document.getElementById('thread-menu-overlay');
console.log('Thread menu collapsed?', threadMenu.classList.contains('collapsed'));
// Expected: false (open) or true (closed) - toggles on each click
```

---

### ✅ 4. Drag-and-Drop Initialization

**Test Steps:**
1. Open thread history sidebar
2. Inspect any thread card

**Expected:**
- Thread cards have `draggable="true"` attribute
- Cursor changes to `grab` on hover
- Cards have data attributes: `data-thread-id`, `data-thread-slug`, `data-thread-name`

**Browser Console Test:**
```javascript
// Check if cards are draggable
const cards = document.querySelectorAll('.thread-info-card, .thread-card-item');
const draggableCount = Array.from(cards).filter(c => c.draggable).length;
console.log(`${draggableCount} / ${cards.length} cards are draggable`);
// Expected: All cards draggable

// Check drop zone initialization
const zones = document.querySelectorAll('.synergy-linked-threads-container');
const initCount = Array.from(zones).filter(z => z.hasAttribute('data-drop-initialized')).length;
console.log(`${initCount} / ${zones.length} drop zones initialized`);
// Expected: All zones initialized
```

---

### ✅ 5. Drag Visual Feedback

**Test Steps:**
1. Start dragging a thread card
2. Drag over Synergy linked threads container
3. Release drag

**Expected Visual States:**

**On Drag Start:**
- Dragged card opacity: `0.5`
- Cursor: `grabbing`
- Body class: `dragging-thread` added

**During Drag Over Drop Zone:**
- Drop zone: Dashed outline appears (2px blue)
- Background: Light blue tint
- Drop zone class: `drag-over` added

**On Drag End:**
- Card opacity: back to `1`
- Cursor: back to `grab`
- Body class: `dragging-thread` removed
- Drop zone class: `drag-over` removed

**Browser Console Test:**
```javascript
// Monitor drag events
const card = document.querySelector('.thread-info-card');
card.addEventListener('dragstart', () => console.log('🎯 DRAG START'));
card.addEventListener('dragend', () => console.log('🎯 DRAG END'));

const zone = document.querySelector('.synergy-linked-threads-container');
zone.addEventListener('dragover', (e) => { e.preventDefault(); console.log('🎯 DRAG OVER'); });
zone.addEventListener('drop', (e) => { e.preventDefault(); console.log('🎯 DROP'); });
```

---

### ✅ 6. Backend API Call

**Test Steps:**
1. Drag a thread card onto a Synergy session's linked threads container
2. Drop it

**Expected Backend Request:**

```http
POST /api/synergy/{session_id}/link-thread
Content-Type: application/json

{
  "thread_id": "thread_abc123",
  "thread_slug": "thread_abc123",
  "thread_name": "My Thread Title"
}
```

**Expected Backend Response:**
```json
{
  "success": true,
  "session_id": "session_xyz",
  "session_name": "My Synergy Session",
  "thread_ids": ["thread_abc123"],
  "message": "Thread thread_abc123 linked successfully"
}
```

**Browser Network Tab:**
- Filter: `link-thread`
- Status: `200 OK`
- Response JSON should have `success: true`

**Browser Console Test:**
```javascript
// Manual API test
const sessionId = 'test-session-id'; // Use real session ID from sidebar
const testData = {
    thread_id: 'test-thread-123',
    thread_slug: 'test-thread-123',
    thread_name: 'Test Thread'
};

fetch(`/api/synergy/${sessionId}/link-thread`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(testData)
})
.then(r => r.json())
.then(data => console.log('API Response:', data))
.catch(err => console.error('API Error:', err));
```

---

### ✅ 7. Database Updates (Bidirectional)

**After successful drop, verify database:**

**Synergy Sessions Table:**
```sql
SELECT session_id, title, thread_ids 
FROM synergy_sessions 
WHERE session_id = 'session_xyz';
```
Expected: `thread_ids` should be JSON array: `["thread_abc123"]`

**Threads Table:**
```sql
SELECT id, thread_slug, synergy_card_id, synergy_card_name
FROM sessions.threads 
WHERE id = 'thread_abc123' OR thread_slug = 'thread_abc123';
```
Expected: 
- `synergy_card_id`: `'session_xyz'`
- `synergy_card_name`: `'My Synergy Session'`

---

### ✅ 8. UI Updates After Linking

**Test Steps:**
1. Complete a drag-drop operation successfully
2. Watch for UI changes

**Expected Behavior:**

1. **Toast Notification:**
   - Shows: "Linking 'Thread Name' to Synergy session..."
   - Then: "Thread 'Thread Name' linked successfully!"
   - Color: Blue → Green
   - Duration: 3 seconds

2. **Linked Threads Section Refresh:**
   - Section automatically reloads
   - New thread card appears in linked threads list
   - Thread count updates: "X threads"

3. **Thread Card Badge (if implemented):**
   - Original thread card shows Synergy link icon
   - Badge indicates which session it's linked to

**Browser Console Test:**
```javascript
// Check if loadLinkedThreads was called
window.synergySidebar?.loadLinkedThreads('session_xyz');

// Monitor UI update events
document.addEventListener('thread-linked-to-synergy', (e) => {
    console.log('🔗 Thread linked event:', e.detail);
});
```

---

### ✅ 9. Edge Cases & Error Handling

**Test Scenarios:**

1. **Drop on Wrong Element:**
   - Drag thread card to non-drop-zone area
   - Expected: No API call, card returns to original position

2. **Missing Session ID:**
   - Drop on container without `data-session-id`
   - Expected: Console error + toast notification: "Error: Cannot determine Synergy session"

3. **Invalid Thread Data:**
   - Manually trigger drop with bad data
   - Expected: Toast notification: "Error: Invalid thread data"

4. **Already Linked Thread:**
   - Link same thread twice to same session
   - Expected: Backend prevents duplicate, returns success with existing thread_ids

5. **Backend Error:**
   - Stop Flask server, try to link thread
   - Expected: Toast notification: "Error: Failed to fetch" or network error

**Browser Console Test:**
```javascript
// Test missing session ID
const zone = document.querySelector('.synergy-linked-threads-container');
zone.removeAttribute('data-session-id');
// Now drag-drop should fail with error message

// Test invalid drag data
const fakeEvent = new DragEvent('drop', {
    dataTransfer: new DataTransfer()
});
fakeEvent.dataTransfer.setData('text/plain', 'invalid json');
zone.dispatchEvent(fakeEvent);
// Expected: Error toast
```

---

### ✅ 10. Performance & Memory

**Test Steps:**
1. Open/close thread history sidebar 10 times
2. Drag-drop 5 different threads to same session
3. Expand/collapse multiple Synergy cards

**Check for:**
- Memory leaks (growing heap size)
- Event listener buildup (duplicate listeners)
- Console warnings/errors

**Browser Console Test:**
```javascript
// Check event listener count (before/after operations)
getEventListeners(document.querySelector('.thread-info-card'));

// Check drop zone re-initialization
document.querySelectorAll('.synergy-linked-threads-container[data-drop-initialized]').length;
// Should match total drop zones (no duplicates)
```

---

## 🔍 Complete Data Flow Trace

### Forward Flow (User → Backend → Database)

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. USER ACTION                                                  │
│    Click [+] button in Linked Threads section                  │
│    → synergy-inline-edit.js line 1046                          │
│    → Toggles #thread-menu-overlay sidebar                      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 2. DRAG START                                                   │
│    User drags .thread-info-card                                │
│    → synergy-thread-drag-drop.js line 69                       │
│    → Sets draggedThreadId, draggedThreadSlug, draggedThreadName│
│    → Adds 'dragging-thread' class to body                      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 3. DRAG OVER DROP ZONE                                         │
│    → synergy-thread-drag-drop.js line 123                      │
│    → Adds 'drag-over' class to zone                            │
│    → Shows visual feedback (outline, background tint)          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 4. DROP EVENT                                                   │
│    → synergy-thread-drag-drop.js line 133                      │
│    → Extracts sessionId from drop zone                         │
│    → Parses thread data from dataTransfer                      │
│    → Calls linkThreadToSession()                               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 5. API CALL                                                     │
│    → synergy-thread-drag-drop.js line 175                      │
│    POST /api/synergy/{sessionId}/link-thread                   │
│    Body: { thread_id, thread_slug, thread_name }              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 6. BACKEND PROCESSING                                           │
│    → synergy_routes.py line 1825                               │
│    ✅ Get current thread_ids from synergy_sessions             │
│    ✅ Append new thread_id to array                            │
│    ✅ UPDATE synergy_sessions SET thread_ids = JSON array      │
│    ✅ UPDATE sessions.threads SET synergy_card_id = sessionId  │
│    ✅ UPDATE sessions.threads SET synergy_card_name            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 7. DATABASE WRITES                                              │
│    Table: synergy_sessions                                     │
│      - thread_ids: ["thread1", "thread2"]                      │
│      - last_active: 2025-12-15T...                             │
│    Table: sessions.threads                                     │
│      - synergy_card_id: "session_xyz"                          │
│      - synergy_card_name: "My Synergy Session"                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 8. RESPONSE & UI UPDATE                                         │
│    → synergy-thread-drag-drop.js line 197                      │
│    ✅ Show success toast                                        │
│    ✅ Call synergySidebar.loadLinkedThreads(sessionId)         │
│    ✅ Dispatch 'thread-linked-to-synergy' event                │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 9. RENDER UPDATED UI                                            │
│    → synergy-sidebar-renderer-v2-FLAT.js line 666              │
│    ✅ Fetch /api/synergy/{sessionId}/linked-threads            │
│    ✅ Render thread cards in linked threads section            │
│    ✅ Update thread count badge                                │
└─────────────────────────────────────────────────────────────────┘
```

### Backward Flow (Database → UI)

```
┌─────────────────────────────────────────────────────────────────┐
│ DATABASE STATE                                                  │
│   synergy_sessions.thread_ids = ["thread1", "thread2"]         │
│   sessions.threads.synergy_card_id = "session_xyz"             │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ SYNERGY SIDEBAR EXPANSION                                       │
│    User expands Synergy card                                   │
│    → synergy-sidebar-renderer-v2-FLAT.js line 666              │
│    → Calls loadLinkedThreads(sessionId)                        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ API REQUEST                                                     │
│    GET /api/synergy/{sessionId}/linked-threads                 │
│    → synergy_routes.py (endpoint to be verified)               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ BACKEND QUERY                                                   │
│    SELECT thread_ids FROM synergy_sessions WHERE ...           │
│    Parse JSON array of thread IDs                              │
│    Fetch thread details from sessions.threads                  │
│    Return: { threads: [...] }                                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ RENDER LINKED THREADS                                           │
│    → synergy-sidebar-renderer-v2-FLAT.js line 700              │
│    ✅ Update count badge                                        │
│    ✅ Render thread cards with:                                │
│       - Agent badge (Prime/Agent X)                            │
│       - Thread title                                            │
│       - Message count                                           │
│       - Created date (time ago)                                │
│    ✅ Make cards clickable to switch thread                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Quick Smoke Test Script

Run this in browser console for fast validation:

```javascript
(async function synergyThreadLinkingSmokeTest() {
    console.log('🧪 Starting Synergy Thread Linking Smoke Test...\n');
    
    const results = {
        passed: 0,
        failed: 0,
        warnings: 0
    };
    
    function test(name, condition, severity = 'error') {
        const symbol = condition ? '✅' : (severity === 'warn' ? '⚠️' : '❌');
        console.log(`${symbol} ${name}`);
        if (condition) results.passed++;
        else if (severity === 'warn') results.warnings++;
        else results.failed++;
        return condition;
    }
    
    // 1. Module Loading
    test('SynergyThreadDragDrop class exists', !!window.SynergyThreadDragDrop);
    test('Instance initialized', !!window.synergyThreadDragDrop);
    
    // 2. UI Components
    test('[+] Button exists', document.querySelector('.synergy-open-thread-history-btn') !== null, 'warn');
    test('Thread menu overlay exists', !!document.getElementById('thread-menu-overlay'));
    test('Drop zones present', document.querySelectorAll('.synergy-linked-threads-container').length > 0, 'warn');
    
    // 3. Thread Cards
    const threadCards = document.querySelectorAll('.thread-info-card, .thread-card-item');
    test(`Thread cards found (${threadCards.length})`, threadCards.length > 0, 'warn');
    
    const draggableCards = Array.from(threadCards).filter(c => c.draggable);
    test(`Cards are draggable (${draggableCards.length}/${threadCards.length})`, 
         draggableCards.length === threadCards.length || threadCards.length === 0, 'warn');
    
    // 4. Drop Zones Initialized
    const dropZones = document.querySelectorAll('.synergy-linked-threads-container');
    const initZones = Array.from(dropZones).filter(z => z.hasAttribute('data-drop-initialized'));
    test(`Drop zones initialized (${initZones.length}/${dropZones.length})`,
         initZones.length === dropZones.length || dropZones.length === 0, 'warn');
    
    // 5. Event Handlers
    const plusBtn = document.querySelector('.synergy-open-thread-history-btn');
    test('Plus button click handler works', () => {
        if (!plusBtn) return false;
        const threadMenu = document.getElementById('thread-menu-overlay');
        if (!threadMenu) return false;
        const wasClosed = threadMenu.classList.contains('collapsed');
        plusBtn.click();
        const nowClosed = threadMenu.classList.contains('collapsed');
        plusBtn.click(); // Toggle back
        return wasClosed !== nowClosed;
    }(), 'warn');
    
    // Summary
    console.log('\n📊 Test Results:');
    console.log(`   ✅ Passed: ${results.passed}`);
    console.log(`   ❌ Failed: ${results.failed}`);
    console.log(`   ⚠️  Warnings: ${results.warnings}`);
    
    if (results.failed === 0 && results.warnings === 0) {
        console.log('\n🎉 All tests passed! Module is fully operational.');
    } else if (results.failed === 0) {
        console.log('\n⚠️  Core functionality OK, but some components not visible (may need user interaction)');
    } else {
        console.log('\n❌ Some tests failed. Check module loading and initialization.');
    }
    
    return results;
})();
```

---

## 🐛 Common Issues & Solutions

### Issue 1: "SynergyThreadDragDrop is not defined"
**Cause:** Module script not loaded  
**Fix:** Check `business-ai-platform-v2.html` line 472 has correct script tag  
**Verify:** Restart Flask, hard refresh browser (Ctrl+F5)

### Issue 2: Thread cards not draggable
**Cause:** Cards loaded before drag-drop initialization  
**Fix:** Dispatch 'thread-cards-loaded' event after loading threads  
**Verify:** `document.dispatchEvent(new CustomEvent('thread-cards-loaded'))`

### Issue 3: Drop zone not accepting drops
**Cause:** Drop zone missing `data-session-id` attribute  
**Fix:** Ensure Synergy card renderer includes `data-session-id="${sessionId}"`  
**Verify:** Inspect drop zone element in DevTools

### Issue 4: Backend 404 error
**Cause:** Session ID not found in database  
**Fix:** Use valid session ID from sidebar  
**Verify:** Check console log for actual session ID being used

### Issue 5: Database not updating
**Cause:** Schema prefix mismatch (synergy_sessions.synergy_sessions)  
**Fix:** Already fixed - using bare table names  
**Verify:** Check `synergy_routes.py` line 1850 uses `synergy_sessions` not `synergy_sessions.synergy_sessions`

---

## ✅ Final Checklist

- [ ] Flask server running (`BISTART`)
- [ ] Browser cache cleared (Ctrl+F5)
- [ ] Synergy sidebar opens
- [ ] At least one Synergy session exists
- [ ] Thread history sidebar has threads
- [ ] [+] button appears in Linked Threads section
- [ ] Clicking [+] toggles thread history sidebar
- [ ] Thread cards are draggable (cursor: grab)
- [ ] Drop zone shows blue outline when dragging
- [ ] Dropping thread shows success toast
- [ ] Linked thread appears in section
- [ ] Backend logs show SQL updates
- [ ] Database has updated `thread_ids` and `synergy_card_id`

---

**Test Completed:** ____________  
**Tester:** ____________  
**Result:** ⬜ PASS  ⬜ FAIL  
**Notes:** _______________________________________________
