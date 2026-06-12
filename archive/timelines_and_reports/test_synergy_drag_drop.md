# Synergy Drag & Drop Debugging Guide

## Issue
User reports: "drag and drop - drag and drop a thread into synergy suite is not working"

## Current Implementation Status

### ✅ Drop Zones ARE Set Up

**Location 1: `.linked-threads-list` section (lines 28545-28625)**
- `dragover` event: Prevents default, adds visual feedback
- `dragleave` event: Removes visual feedback
- `drop` event: Handles thread linking with backend API

**Location 2: `#threads-section-${session.session_id}` (line 28982)**
- HTML attributes:
  - `ondrop="synergyBoard.handleThreadDrop(event, '${session.session_id}')"`
  - `ondragover="event.preventDefault(); event.currentTarget.classList.add('drag-over')"`
  - `ondragleave="event.currentTarget.classList.remove('drag-over')"`

### ✅ Drag Source IS Set Up

**Thread items (line 28816):**
- `draggable="true"`
- `data-thread-id="${thread.id}"`
- `ondragstart="ThreadManager.handleDragStart(event)"`
- `ondragend="ThreadManager.handleDragEnd(event)"`

### ✅ Handler Function EXISTS

**`handleThreadDrop(event, synergyId)` (lines 30691-30747)**
- Prevents default behavior
- Gets thread ID from `event.dataTransfer`
- Calls API endpoint `/api/synergy/${synergyId}/link-thread`
- Shows success/error notification
- Reloads cards to update UI

## Possible Issues

### Issue 1: Duplicate Drop Zones Conflict
The code has TWO drop zone setups:
1. JavaScript event listeners on `.linked-threads-list` (lines 28545-28625)
2. Inline HTML attributes on `#threads-section-` (line 28982)

**These might be conflicting!**

### Issue 2: Event Propagation
Both drop zones call `e.stopPropagation()`, which could prevent the other from firing.

### Issue 3: CSS Selector Issue
The `.linked-threads-list` class might not exist or be visible when card is collapsed.

### Issue 4: API Endpoint
Need to verify `/api/synergy/${synergyId}/link-thread` exists and works.

## Testing Steps

### Test 1: Check Console for Errors
1. Open Synergy Suite tab
2. Open browser console (F12)
3. Try dragging a thread to a Synergy card
4. Look for errors:
   - `[SYNERGY] No thread ID in drop event`
   - `[SYNERGY] Failed to link thread`
   - 404 Not Found
   - CORS errors

### Test 2: Verify Drag Data
Add debug logging to `handleDragStart`:
```javascript
handleDragStart(event) {
    const threadId = event.currentTarget.dataset.threadId;
    console.log('[DEBUG DRAG] Starting drag:', threadId);
    event.dataTransfer.setData('text/plain', threadId);
    console.log('[DEBUG DRAG] DataTransfer set:', event.dataTransfer.getData('text/plain'));
    // ... rest of function
}
```

### Test 3: Verify Drop Zone
Add debug to drop zone:
```javascript
ondragover="console.log('[DEBUG DROP] Dragover on synergy card'); event.preventDefault(); ..."
ondrop="console.log('[DEBUG DROP] Drop on synergy card'); synergyBoard.handleThreadDrop(event, '${session.session_id}')"
```

### Test 4: Check if Element is Receiving Events
```javascript
// In browser console:
const dropZone = document.querySelector('[data-synergy-id]');
console.log('Drop zone found:', dropZone);
console.log('Has ondrop:', dropZone.ondrop);
```

## Recommended Fix

### Option A: Remove Duplicate Drop Zone (Simplify)

Remove the JavaScript event listeners and keep only the inline HTML attributes:

**Delete lines 28545-28625** (the JavaScript listeners on `.linked-threads-list`)

Keep lines 28982 (inline HTML attributes).

### Option B: Make Drop Zones Complementary

The JavaScript listeners apply to `.linked-threads-list` (when card is expanded).
The inline attributes apply to `#threads-section-` (container).

**Change**: Make sure `.linked-threads-list` doesn't call `stopPropagation`:

```javascript
// Line ~28567 - REMOVE e.stopPropagation()
linkedThreadsSection.addEventListener('drop', async (e) => {
    e.preventDefault();
    // e.stopPropagation(); // <-- REMOVE THIS LINE
    linkedThreadsSection.style.background = '';
    // ... rest
});
```

### Option C: Check API Endpoint Exists

Verify the backend has this route:
```python
@app.route('/api/synergy/<session_id>/link-thread', methods=['POST'])
def link_thread_to_synergy(session_id):
    # Implementation
```

## Quick Test Script

Run in browser console while on Synergy Suite:
```javascript
// Test 1: Check if drop zones exist
console.log('Drop zones:', document.querySelectorAll('[data-synergy-id]').length);

// Test 2: Check if threads are draggable
console.log('Draggable threads:', document.querySelectorAll('[draggable="true"]').length);

// Test 3: Test drag-drop manually
const thread = document.querySelector('[draggable="true"]');
const dropZone = document.querySelector('[data-synergy-id]');
if (thread && dropZone) {
    console.log('✅ Both thread and drop zone found');
    console.log('Thread ID:', thread.dataset.threadId);
    console.log('Drop zone synergy ID:', dropZone.dataset.synergyId);
} else {
    console.error('❌ Missing elements:', {thread, dropZone});
}

// Test 4: Check if handler function exists
console.log('handleThreadDrop exists:', typeof synergyBoard.handleThreadDrop);
```

## Next Steps

1. Run quick test script in browser console
2. Try dragging with console open to see logs
3. Check Network tab for failed API calls
4. Based on results, apply Option A, B, or C above
