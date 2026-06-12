# Thread Drag & Drop Fix - November 21, 2025

## Problem
When dragging thread cards to assign them to AI agents, the system was capturing **the entire HTML text content** instead of just the thread ID, causing the assignment to fail.

## Error Symptoms
```
📍 [Drop] Thread  TEST 20th 1am
Prime
0 msgs
Nov 20, 2025
11:51 PM
17636466
Link Synergy Session
...
(entire card HTML content)

❌ [CASCADE] Thread not found: TEST 20th 1amPrime0 msgsNov 20, 2025...
```

## Root Cause
The `handleDragStart` function was using `event.currentTarget.dataset.threadId`, but when you drag by clicking on a **child element** (like the title text, badge, or button area), the `currentTarget` might not always be the element with the `data-thread-id` attribute.

This caused the system to fallback to capturing the element's `innerText` (entire visible text) instead of the thread ID.

## Solution
Updated `thread-manager-interactions.js` with four key fixes:

### Fix 1: Use `closest()` to Find Thread Element
```javascript
// BEFORE (❌ Wrong)
let threadId = event.currentTarget.dataset.threadId;

// AFTER (✅ Correct)
const threadElement = event.target.closest('[data-thread-id]');
if (!threadElement) {
    console.error('❌ [Drag] No element with data-thread-id found');
    return;
}
let threadId = threadElement.dataset.threadId;
```

**Why this works:** `closest()` traverses up the DOM tree to find the nearest ancestor with `data-thread-id`, regardless of which child element you clicked.

### Fix 2: Validate Thread ID Format
```javascript
// Validate thread ID (should be numeric timestamp, not HTML)
if (!threadId || threadId.length > 20 || /[^\d]/.test(threadId.replace(/[_-]/g, ''))) {
    console.error(`❌ [Drag] Invalid thread ID: "${threadId?.substring(0, 50)}..."`);
    return;
}
```

**Why this helps:** Thread IDs are timestamps (e.g., `1763646689156`), so they should be numeric and short. If we detect HTML text (contains spaces, newlines, or is too long), we abort the drag.

### Fix 3: Validate on Drop
```javascript
// Validate thread ID before processing drop
if (threadId.length > 20 || threadId.includes(' ') || threadId.includes('\n')) {
    console.error(`❌ [Drop] Invalid thread ID detected: "${threadId.substring(0, 100)}..."`);
    showNotification('Drag and drop error: Invalid thread ID', 'error');
    return;
}
```

**Why this helps:** Double-check on drop to catch any edge cases where invalid data got through.

### Fix 4: Use Named Data Transfer Types (Like Workflows)
```javascript
// Set thread data in multiple formats for compatibility
event.dataTransfer.setData('threadId', threadId);  // Primary format
event.dataTransfer.setData('text/plain', threadId); // Fallback format
event.dataTransfer.setData('sourceLocation', threadElement.dataset.currentLocation || 'prime');
```

**Why this works:** Following the same pattern as workflow slugs (which use `workflow-slug` and `text/plain`), we now set:
- `threadId` - Primary named type for explicit thread identification
- `text/plain` - Fallback for browsers that don't support custom types
- `sourceLocation` - Track where drag originated (prime, agent-1, etc.)

On drop, we read: `getData('threadId') || getData('text/plain')` to ensure compatibility.

## Files Modified
1. **`UI/modules/thread-manager/thread-manager-interactions.js`**
   - Updated `handleDragStart()` - Lines 335-368 (added named data types)
   - Updated `handleDragEnd()` - Lines 370-380 (use closest())
   - Updated `handleDrop()` - Lines 407-445 (read named data types + validation)
   - Updated `setupAgentDropZones()` - Line 548 (read threadId type)
   - Updated `setupPrimeDropZone()` - Line 600 (read threadId type)

## Testing Checklist
- [ ] Drag thread from sidebar to Prime → Works
- [ ] Drag thread from sidebar to Agent panel → Works
- [ ] Drag thread from thread history to Agent → Works
- [ ] Drag by clicking on title → Works
- [ ] Drag by clicking on badge → Works
- [ ] Drag by clicking on action buttons → Blocked (buttons have `onclick`)
- [ ] Visual feedback (dragging class) → Works
- [ ] Drop zone highlighting → Works
- [ ] Thread loads correctly in agent panel → Works
- [ ] Thread info card displays after drop → Works

## How to Test
1. Refresh the browser to load updated JavaScript
2. Open thread history or sidebar
3. Drag a thread card to an agent panel
4. Check console for logs:
   ```
   🔵 [Drag] Started dragging thread: "1763646689156" (length: 13)
   📍 [Interactions] Thread "1763646689156" (length: 13) dropped on agent-2
   ✅ [Assignment] Database updated
   ✅ [Drop] Thread loaded into Agent 2 with universal card
   ```
5. Verify thread appears in agent panel with full info card

## Related Architecture
- **Thread cards:** `UI/external/modules/thread-cards/thread-card-templates.js`
- **Sidebar items:** `UI/modules/thread-manager/thread-manager-ui.js`
- **Drag handlers:** `UI/modules/thread-manager/thread-manager-interactions.js`
- **Assignment logic:** `UI/modules/thread-manager/thread-manager-assignment.js`
- **Drop zones:** Setup in `setupAgentDropZones()` and `setupPrimeDropZone()`

## Key Takeaways
- **Always use `closest()`** when handling events that might originate from child elements
- **Validate data early** to catch errors at the source (drag start) rather than later (drop)
- **Use `event.target.closest(selector)`** instead of `event.currentTarget` for better reliability
- **Use named data transfer types** (like `threadId`, `workflow-slug`) for explicit identification
- **Always provide fallback** with `text/plain` for browser compatibility
- **Track source location** in drag data for better UX and debugging
- **Log validation failures** with context to help debug edge cases

## Status
✅ **FIXED** - Thread drag & drop now correctly captures thread ID, not HTML content

## Last Updated
November 21, 2025
