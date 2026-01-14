# View Mode Persistence Fix - December 12, 2025

## Problem

View modes (all-collapsed, all-expanded, ai-collapsed, ai-expanded, ai-user) were applied when the user clicked the view mode button, but NEW messages arriving via streaming did not inherit the selected view mode.

**User Report:**
> "they work but only once when you apply them and if new messages come in they don't continue to follow the selected view mode... it is not just a button that changes things .. it changes the bubbles and then continues to do that view automatically for any new messages"

**Expected Behavior:**
When a user selects a view mode, ALL new messages should automatically be displayed according to that mode.

**Actual Behavior:**
View mode only applied to EXISTING messages when button was clicked. New messages used default expanded state.

---

## Root Cause

### View Mode System Architecture

**State Storage:** `viewModes[agentId]` tracks the current view mode per agent (stored in `agent-column.js`)

**5 View Modes:**
1. `'all-collapsed'` - Show all messages, tools collapsed
2. `'all-expanded'` - Show all messages, all expanded
3. `'ai-collapsed'` - Show AI only, collapsed tools (hide user/thinking)
4. `'ai-expanded'` - Show AI only, expanded tools (hide user/thinking)
5. `'ai-user'` - Show AI and user only (hide tools/thinking)

**Original Flow:**
```javascript
// User clicks view mode button
setViewMode(agentId, mode) {
    viewModes[agentId] = mode;  // Store mode
    applyViewModeToColumn(agentId, mode);  // Apply to ALL existing messages
}

// applyViewModeToColumn() iterates existing bubbles
const messages = messagesContainer.querySelectorAll('.ai-message');
messages.forEach(message => {
    // Apply CSS classes based on mode
});
```

**Missing Step:**
No code was applying view mode when NEW messages were created during streaming!

### Message Creation Points

New messages are created in **4 locations** during streaming:

1. **Thinking Bubble** (`agent-js.js` line ~3509)
   - Created with `thinkingBubble.classList.add('collapsed')`
   - Appended to `messagesContainer`
   - ❌ No view mode applied

2. **Tool Bubble** (`agent-js.js` line ~3641)
   - Created with `toolBubble.classList.add('collapsed')`
   - Appended to `messagesContainer`
   - ❌ No view mode applied

3. **Tool Result Bubble** (`agent-js.js` line ~3785)
   - Created with `toolResultBubble.classList.add('collapsed')`
   - Appended to `messagesContainer`
   - ❌ No view mode applied

4. **Text Bubble** (`agent-js.js` line ~3917)
   - Created and appended to `messagesContainer`
   - ❌ No view mode applied

5. **User Message** (`agent-js.js` line ~3130)
   - Created via `UnifiedMessageRenderer.render()`
   - ❌ No view mode applied

---

## Solution

Created a new function `applyViewModeToMessage(agentId, message)` that applies view mode to a SINGLE message element, then call it immediately after each message is appended.

### Implementation

#### Step 1: New Function in `agent-column.js`

**Location:** `UI/modules_internal/agents/agent-column.js` (lines 1616-1683)

```javascript
/**
 * Apply view mode to a single message bubble (called when new message arrives)
 * @param {number} agentId - Agent ID
 * @param {HTMLElement} message - The message element to apply view mode to
 */
function applyViewModeToMessage(agentId, message) {
    const mode = viewModes[agentId] || 'all-expanded'; // Default to all-expanded
    
    if (!message || !message.classList) return;

    const isAI = message.classList.contains('assistant');
    const isUser = message.classList.contains('user');
    const isThinking = message.classList.contains('thinking-bubble');
    const isTool = message.classList.contains('tool-bubble') || message.classList.contains('tool');

    // Reset classes and visibility
    message.classList.remove('expanded', 'collapsed');
    message.style.display = '';

    switch (mode) {
        case 'all-collapsed':
            // Show all - tools collapsed
            message.classList.add('collapsed');
            break;

        case 'all-expanded':
            // Show all - expand all
            message.classList.add('expanded');
            break;

        case 'ai-collapsed':
            // Show AI only - collapsed tools
            if (isAI) {
                message.classList.add('expanded');
            } else if (isTool) {
                message.classList.add('collapsed');
            } else if (isUser || isThinking) {
                message.style.display = 'none';
            }
            break;

        case 'ai-expanded':
            // Show AI only - expanded tools
            if (isAI || isTool) {
                message.classList.add('expanded');
            } else if (isUser || isThinking) {
                message.style.display = 'none';
            }
            break;

        case 'ai-user':
            // Show AI and user - no tools/no tool results
            if (isAI || isUser) {
                message.classList.add('expanded');
            } else if (isTool || isThinking) {
                message.style.display = 'none';
            }
            break;
    }
    
    console.log(`📐 [AgentColumn] Applied view mode '${mode}' to new message`, message.className);
}
```

#### Step 2: Export Function

**Location:** `UI/modules_internal/agents/agent-column.js` (lines 1761-1789)

```javascript
return {
    // ... existing exports ...
    applyViewModeToMessage  // ✅ NEW: Apply view mode to single message
};
```

#### Step 3: Apply to Thinking Bubbles

**Location:** `UI/modules_internal/agents/agent-js.js` (lines 3509-3520)

```javascript
thinkingBubble.classList.add('collapsed'); // Start collapsed
messagesContainer.appendChild(thinkingBubble);

// ✅ APPLY VIEW MODE TO NEW BUBBLE
if (typeof AgentColumn !== 'undefined' && typeof AgentColumn.applyViewModeToMessage === 'function') {
    AgentColumn.applyViewModeToMessage(agentId, thinkingBubble);
}

// Add fullscreen double-click handler
if (typeof window.addMessageFullscreenHandler === 'function') {
    window.addMessageFullscreenHandler(thinkingBubble);
}
```

#### Step 4: Apply to Tool Bubbles

**Location:** `UI/modules_internal/agents/agent-js.js` (lines 3641-3652)

```javascript
toolBubble.classList.add('collapsed'); // Start collapsed
messagesContainer.appendChild(toolBubble);

// ✅ APPLY VIEW MODE TO NEW BUBBLE
if (typeof AgentColumn !== 'undefined' && typeof AgentColumn.applyViewModeToMessage === 'function') {
    AgentColumn.applyViewModeToMessage(agentId, toolBubble);
}

// Add fullscreen double-click handler
if (typeof window.addMessageFullscreenHandler === 'function') {
    window.addMessageFullscreenHandler(toolBubble);
}
```

#### Step 5: Apply to Tool Result Bubbles

**Location:** `UI/modules_internal/agents/agent-js.js` (lines 3785-3796)

```javascript
toolResultBubble.classList.add('collapsed'); // Start collapsed
messagesContainer.appendChild(toolResultBubble);

// ✅ APPLY VIEW MODE TO NEW BUBBLE
if (typeof AgentColumn !== 'undefined' && typeof AgentColumn.applyViewModeToMessage === 'function') {
    AgentColumn.applyViewModeToMessage(agentId, toolResultBubble);
}

// Add fullscreen double-click handler
if (typeof window.addMessageFullscreenHandler === 'function') {
    window.addMessageFullscreenHandler(toolResultBubble);
}
```

#### Step 6: Apply to Text Bubbles

**Location:** `UI/modules_internal/agents/agent-js.js` (lines 3917-3927)

```javascript
messagesContainer.appendChild(textBubble);
console.log(`[Agent ${agentId}] Text bubble created`);

// ✅ APPLY VIEW MODE TO NEW BUBBLE
if (typeof AgentColumn !== 'undefined' && typeof AgentColumn.applyViewModeToMessage === 'function') {
    AgentColumn.applyViewModeToMessage(agentId, textBubble);
}

// Add fullscreen double-click handler
if (typeof window.addMessageFullscreenHandler === 'function') {
    window.addMessageFullscreenHandler(textBubble);
}
```

#### Step 7: Apply to User Messages

**Location:** `UI/modules_internal/agents/agent-js.js` (lines 3130-3142)

```javascript
const userMessageDiv = UnifiedMessageRenderer.render(
    `#agent-messages-${agentId}`,
    'user',
    displayMessage,
    {
        threadId: currentThread.id,
        syncToBackend: false
    }
);
console.log(`[Agent ${agentId}] User message rendered`);

// ✅ APPLY VIEW MODE TO USER MESSAGE
if (userMessageDiv && typeof AgentColumn !== 'undefined' && typeof AgentColumn.applyViewModeToMessage === 'function') {
    AgentColumn.applyViewModeToMessage(agentId, userMessageDiv);
}

scrollAgentToBottom(agentId);
```

---

## Technical Details

### View Mode Logic

The `applyViewModeToMessage()` function uses the same logic as `applyViewModeToColumn()` but operates on a SINGLE message element:

1. **Retrieve stored mode:** `viewModes[agentId]` or default to `'all-expanded'`
2. **Detect message type:** Check CSS classes (`.assistant`, `.user`, `.thinking-bubble`, `.tool-bubble`, `.tool`)
3. **Reset state:** Remove existing `.expanded`/`.collapsed` classes and visibility
4. **Apply mode:**
   - `all-collapsed`: Add `.collapsed` to ALL messages
   - `all-expanded`: Add `.expanded` to ALL messages
   - `ai-collapsed`: Show AI expanded, tools collapsed, hide user/thinking
   - `ai-expanded`: Show AI and tools expanded, hide user/thinking
   - `ai-user`: Show AI and user expanded, hide tools/thinking

### CSS Classes Applied

**Expansion State:**
- `.expanded` - Message content visible with full details
- `.collapsed` - Message content minimized/collapsed

**Visibility:**
- `style.display = ''` - Visible (default)
- `style.display = 'none'` - Hidden

### Message Type Detection

```javascript
const isAI = message.classList.contains('assistant');
const isUser = message.classList.contains('user');
const isThinking = message.classList.contains('thinking-bubble');
const isTool = message.classList.contains('tool-bubble') || message.classList.contains('tool');
```

---

## Testing

### Test Case 1: all-collapsed Mode
1. Select "All Collapsed" view mode
2. Send a message to agent
3. ✅ User message should appear collapsed
4. ✅ AI thinking should appear collapsed
5. ✅ Tool use should appear collapsed
6. ✅ Tool result should appear collapsed
7. ✅ Text response should appear collapsed

### Test Case 2: all-expanded Mode
1. Select "All Expanded" view mode
2. Send a message to agent
3. ✅ All messages should appear expanded

### Test Case 3: ai-collapsed Mode
1. Select "AI + Tools Collapsed" view mode
2. Send a message to agent
3. ✅ User message should be hidden
4. ✅ AI thinking should be hidden
5. ✅ Tool use should appear collapsed
6. ✅ Tool result should appear collapsed
7. ✅ Text response should appear expanded

### Test Case 4: ai-expanded Mode
1. Select "AI + Tools Expanded" view mode
2. Send a message to agent
3. ✅ User message should be hidden
4. ✅ AI thinking should be hidden
5. ✅ Tool use should appear expanded
6. ✅ Tool result should appear expanded
7. ✅ Text response should appear expanded

### Test Case 5: ai-user Mode
1. Select "AI + User Only" view mode
2. Send a message to agent
3. ✅ User message should appear expanded
4. ✅ AI thinking should be hidden
5. ✅ Tool use should be hidden
6. ✅ Tool result should be hidden
7. ✅ Text response should appear expanded

### Test Case 6: Mode Persistence
1. Select any view mode
2. Send message → Verify new messages follow mode
3. Switch to different view mode
4. Send another message → Verify new messages follow NEW mode
5. ✅ View mode persists across multiple messages

---

## Files Modified

### 1. `UI/modules_internal/agents/agent-column.js`
- **Added:** `applyViewModeToMessage(agentId, message)` function (67 lines)
- **Modified:** Exports to include new function
- **Lines:** 1616-1683 (new function), 1789 (export)

### 2. `UI/modules_internal/agents/agent-js.js`
- **Modified:** Thinking bubble creation (lines ~3509-3520)
- **Modified:** Tool bubble creation (lines ~3641-3652)
- **Modified:** Tool result bubble creation (lines ~3785-3796)
- **Modified:** Text bubble creation (lines ~3917-3927)
- **Modified:** User message rendering (lines ~3130-3142)
- **Total:** 5 integration points

---

## Backward Compatibility

✅ **Fully Compatible** - No breaking changes

- Existing `setViewMode()` function unchanged
- Existing `applyViewModeToColumn()` function unchanged
- New function only ADDS functionality
- Graceful fallback if `AgentColumn` not loaded
- Type checks prevent errors: `typeof AgentColumn !== 'undefined'`

---

## Performance

**Impact:** Negligible

- Function called once per message (lightweight operation)
- Simple class manipulation and CSS property changes
- No DOM queries (operates on passed element)
- Console log can be removed in production

**Optimization:**
```javascript
// Optional: Remove console.log in production
// console.log(`📐 [AgentColumn] Applied view mode '${mode}' to new message`, message.className);
```

---

## Related Issues

### Issue #1: Thread Info Card Expansion
**Fixed:** December 12, 2025  
**Documentation:** `THREAD_INFO_CARD_EXPANSION_FIX_DEC12_2025.md`  
**Summary:** Thread info cards in Thread History sidebar with agent assignments now expand correctly

### Issue #2: View Mode Persistence
**Fixed:** December 12, 2025 (THIS FIX)  
**Summary:** View modes now automatically apply to new messages as they arrive

---

## Summary

**Problem:** View modes only applied when button clicked, new messages ignored view mode setting

**Solution:** Created `applyViewModeToMessage()` function and called it after every message creation

**Impact:** View modes now work as expected - they automatically apply to ALL new messages

**Status:** ✅ COMPLETE - Ready for Testing

---

**Fix Date:** December 12, 2025  
**Issue Reported By:** User  
**Root Cause:** Missing view mode application at message creation points  
**Solution:** Apply view mode immediately after each new message is appended  
**Testing:** 6 test cases covering all 5 view modes and persistence
