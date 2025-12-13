# Thread Card Expansion - Isolation Fixes (Dec 13, 2025)

## Summary
Fixed three critical issues with thread info card expansion and user interaction isolation across AI Agent columns, Prime Chat panel, and Thread History sidebar.

---

## Issue #1: Expand in Thread History Affecting Agent Column

### Problem
When user clicked the expand chevron on a thread card in the Thread History sidebar, the thread card would expand in the **AI Agent Column** instead of staying in the Thread History panel.

### Root Cause
The `findCardElement(threadId)` function used `document.querySelector()` which returns the **first matching element**. When the same thread was loaded in both Thread History AND an Agent column:
```javascript
const card = document.querySelector(`.ai-chat-header-info[data-thread-id="${threadId}"]`);
// Returns: First match in DOM = Agent column card (if it appears before History card)
// NOT: The History card that user actually clicked
```

### Solution
Modified `toggleCard()` to use `event.target.closest()` to find the **exact card user clicked**:

```javascript
toggleCard(event, threadId) {
    // ✅ FIX: Use event.target to find the ACTUAL clicked card
    let card = null;
    if (event && event.target) {
        card = event.target.closest('.ai-chat-header-info, .agent-thread-card');
    }
    
    // Fallback to old method if event.target didn't work
    if (!card) {
        card = this.findCardElement(threadId);
    }
    
    // ... rest of logic
}
```

**Benefits**:
- Expansion always happens in the correct location
- No ambiguity even when same thread in multiple locations
- Location-aware expansion without DOM order dependency

**Files Modified**:
- `UI/modules_internal/thread-cards/thread-card-expansion.js` (lines 41-80)

---

## Issue #2: Prime Chat Panel Thread Info Card Not Expanding

### Problem
Clicking the expand chevron on the thread info card in Prime Chat panel (#prime-thread-info) had **no visual effect** - the card would not expand.

### Root Cause
The CSS rule for Prime expansion was incomplete:
```css
/* Only this rule existed */
#prime-thread-info.expanded .thread-expand-on-hover {
    /* ... */
}

/* But code might add .expanded class to CARD, not CONTAINER */
.ai-chat-header-info.expanded { /* No rule! */ }
```

The `getExpandableElement()` function determines what element gets the `.expanded` class based on context:
- If card is inside `#prime-thread-info` container → adds class to **container**
- If card is NOT in container → adds class to **card itself**

But CSS only had rule for container, not for card.

### Solution
Added CSS selector to handle expansion on both container and card:

```css
#prime-thread-info .thread-expand-on-hover {
    opacity: 0;
    max-height: 0;
    overflow: hidden;
}

/* Show expanded content ONLY when clicked - Container OR Card */
#prime-thread-info.expanded .thread-expand-on-hover,
#prime-thread-info .ai-chat-header-info.expanded .thread-expand-on-hover {
    opacity: 1;
    max-height: 500px;
}

/* Chevron rotation - Container OR Card */
#prime-thread-info.expanded .chevron-icon,
#prime-thread-info .ai-chat-header-info.expanded .chevron-icon {
    transform: rotate(180deg);
}
```

**Benefits**:
- Prime card expands smoothly with animation
- Works whether container or card has `.expanded` class
- Chevron rotates 180° when expanded

**Files Modified**:
- `UI/modules_internal/thread-cards/thread-card-styles.css` (lines 290-312)

---

## Issue #3: Agent Column Not Showing Welcome Screen After Unload

### Problem
When user clicked "Unload" on a thread in Thread History (moving it from Agent column back to Prime):
1. ✅ Thread was moved to Prime
2. ❌ Agent column messages were cleared
3. ❌ **Welcome screen did NOT appear** - agent column stayed blank

### Root Cause
The `unloadThread()` function in thread-manager-interactions.js manually cleared the messages container:
```javascript
// Old code - just clears innerHTML
const messagesContainer = document.getElementById(`agent-messages-${agentId}`);
if (messagesContainer) {
    messagesContainer.innerHTML = '';  // ❌ Just empties it
}
```

But it never called `AgentColumn.unloadThread()` which:
1. Renders the proper welcome screen HTML with empty state message
2. Shows quick tip cards
3. Shows "Start New Chat" and "Thread History" buttons
4. Resets scroll controls visibility

### Solution
Changed to call the proper cleanup function:

```javascript
// ✅ FIX: Use AgentColumn.unloadThread() for proper empty state
if (typeof AgentColumn !== 'undefined' && typeof AgentColumn.unloadThread === 'function') {
    AgentColumn.unloadThread(agentId);
    console.log(`✅ [unloadThread] Called AgentColumn.unloadThread(${agentId}) for proper reset`);
} else {
    // Fallback if AgentColumn not available
    const messagesContainer = document.getElementById(`agent-messages-${agentId}`);
    if (messagesContainer) {
        messagesContainer.innerHTML = '';
    }
}
```

**Benefits**:
- Agent column properly shows welcome screen after unload
- Users see empty state with helpful tips
- Can load new thread or access history
- Scroll controls properly hidden when no messages

**Files Modified**:
- `UI/modules_internal/thread-manager/thread-manager-interactions.js` (lines 410-432)

---

## How It All Works Together

### Before Fixes ❌

**Thread History Expand Issue**:
```
User clicks expand in Thread History
  ├─ Event fires on History card
  ├─ toggleCard() calls findCardElement()
  │  └─ querySelector returns Agent card (first match)
  └─ Agent card expands ❌ (wrong location)
```

**Prime Expand Issue**:
```
User clicks expand in Prime
  ├─ Event fires on Prime card
  ├─ toggleCard() finds Prime card ✓
  ├─ getExpandableElement() returns Prime card ✓
  ├─ Adds .expanded class to Prime card ✓
  └─ CSS doesn't match selector ❌ (no rule for card)
```

**Unload Issue**:
```
User clicks Unload in Thread History
  ├─ unloadThread() called
  ├─ Clears messages with innerHTML = '' ✓
  └─ No welcome screen rendered ❌
```

### After Fixes ✅

**Thread History Expand Issue**:
```
User clicks expand in Thread History
  ├─ Event fires on History card
  ├─ toggleCard() uses event.target.closest()
  │  └─ Finds exact History card clicked ✓
  └─ History card expands ✓ (correct location)
```

**Prime Expand Issue**:
```
User clicks expand in Prime
  ├─ Event fires on Prime card
  ├─ toggleCard() finds Prime card ✓
  ├─ getExpandableElement() returns Prime card ✓
  ├─ Adds .expanded class to Prime card ✓
  └─ CSS now matches #prime-thread-info .ai-chat-header-info.expanded ✓
```

**Unload Issue**:
```
User clicks Unload in Thread History
  ├─ unloadThread() called
  ├─ Calls AgentColumn.unloadThread() ✓
  ├─ Renders welcome screen with empty state HTML ✓
  └─ Shows tips, buttons, scroll controls hidden ✓
```

---

## Testing Checklist

- [ ] **Thread History Expansion**
  - [ ] Click expand on thread in History sidebar
  - [ ] Verify card expands IN History (not in Agent column)
  - [ ] Details slide down within History card

- [ ] **Agent Column Expansion**
  - [ ] Click expand on thread in Agent column
  - [ ] Verify card expands IN Agent column (not in History)
  - [ ] Agent column only shows this card's details

- [ ] **Prime Panel Expansion**
  - [ ] Load thread into Prime Chat
  - [ ] Click expand chevron on thread info card
  - [ ] Verify card expands smoothly with animation
  - [ ] Chevron rotates 180°

- [ ] **Unload to Welcome Screen**
  - [ ] Load thread into Agent-1 column
  - [ ] Click Unload button in Thread History
  - [ ] Verify Agent-1 shows welcome screen (not blank)
  - [ ] See "Agent-1 Ready" message
  - [ ] See "Start New Chat" button
  - [ ] Scroll controls hidden (no messages)

---

## Code Changes Summary

| File | Change | Impact |
|------|--------|--------|
| thread-card-expansion.js | Use event.target.closest() instead of querySelector() | Expansion happens at correct location |
| thread-card-styles.css | Add CSS for #prime-thread-info .ai-chat-header-info.expanded | Prime card expands with animation |
| thread-manager-interactions.js | Call AgentColumn.unloadThread() instead of manual clearing | Welcome screen appears after unload |

---

## Performance Impact
- **No negative impact** - all changes are event-driven and use existing functions
- **toggleCard()** - Slightly faster with event.target (direct DOM match vs. selector search)
- **CSS** - Added 3 new selectors (negligible impact)
- **unloadThread()** - Now calls proper cleanup function (same performance, better result)

---

## Related Issues
- Thread info card DOM structure across 3 locations: `THREAD_INFO_CARD_DOM_STRUCTURE_AND_ISOLATION.md`
- Workspace persistence: Stores expand/collapse state per user per location
- Scroll controls visibility: MutationObserver tracks message changes

