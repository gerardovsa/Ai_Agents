# Message Bubble Display Toggle Controls Implementation

**Date:** December 3, 2025  
**Status:** ✅ Complete

## Overview
Implemented message bubble display toggle controls for both Prime chat and Agent columns, giving users powerful control over message visibility and detail level.

## Features Implemented

### 1️⃣ Expand/Collapse Toggle (`cycleExpandMode`)
**Purpose:** Controls whether message bubbles show expanded or collapsed content

**Modes (cycles through):**
- **All** → All messages expanded (show full content)
- **AI Only** → AI messages expanded, others collapsed
- **None** → All messages collapsed

**Button Icons:**
- `all`: 🔽 `fa-expand-alt` - "Cycle expand: All → AI Only → None"
- `ai`: 🤖 `fa-robot` - "Cycle expand: AI Only → None → All"
- `none`: 🔼 `fa-compress-alt` - "Cycle expand: None → All → AI Only"

**Implementation:**
- Agent columns: `AgentColumn.cycleExpandMode(agentId)`
- Prime chat: `PrimeAI.cycleExpandMode()`
- Adds/removes `.expanded` and `.collapsed` classes on `.ai-message` elements

### 2️⃣ Visibility Toggle (`toggleThinkingToolBubbles`)
**Purpose:** Show/hide specific message types (User, Thinking, Tool bubbles)

**Modes (toggles between):**
- **Visible** → Show all message types
- **Hidden** → Hide User/Thinking/Tool messages (show AI only)

**Button States:**
- Showing all: 👁️ `fa-eye` - "Show AI only (hide user/thinking/tool)"
- AI only: 🙈 `fa-eye-slash` - "Show all messages"
- Active state uses `.hiding` class (blue background)

**Implementation:**
- Agent columns: `AgentColumn.toggleThinkingToolBubbles(agentId)`
- Prime chat: `PrimeAI.toggleThinkingToolBubbles()`
- Sets `display: none` on `.user`, `.thinking-bubble`, `.tool-bubble`, `.tool` messages

## Files Modified

### JavaScript Files
1. **agent-column.js** (1051 → 1189 lines)
   - Added state tracking: `expandModes`, `thinkingToolVisibility`
   - Added functions: `cycleExpandMode()`, `applyExpandModeToColumn()`, `toggleThinkingToolBubbles()`
   - Updated public API exports
   - Added buttons to column header HTML template

2. **prime_ai_chat.js** (2339 → 2453 lines)
   - Added state tracking: `primeExpandMode`, `primeThinkingToolVisibility`
   - Added functions: `cycleExpandModePrime()`, `applyExpandModeToPrime()`, `toggleThinkingToolBubblesPrime()`
   - Created `PrimeAI` namespace object
   - Exported to `window.PrimeAI`

### CSS Files
3. **agent-ui.css**
   - Added `.expand-cycle-btn`, `.visibility-btn` base styles
   - Added hover states
   - Added `.visibility-btn.hiding` active state (blue background)

4. **business-ai-platform-v2.html**
   - Added buttons to Prime chat header
   - Added Prime-specific button CSS styles
   - Added `.hiding` active state styles

## UI Layout

### Agent Column Header
```
[Collapse ▼] [Agent Icon + Name]  [🔽] [👁️] [⟨⟩] [☰]
                                   expand vis width menu
```

### Prime Chat Header
```
[AI Prime Icon + Title]           [🔽] [👁️] [≫≫]
                                   expand vis  close
```

## Message Types Affected

### Visibility Toggle (`👁️` button):
- `.ai-message.user` - User messages
- `.ai-message.thinking-bubble` - AI thinking process
- `.ai-message.tool-bubble` - Tool execution results
- `.ai-message.tool` - Tool messages

### Expand Toggle (`🔽` button):
- All `.ai-message` elements
- Adds/removes `.expanded` or `.collapsed` classes

## Use Cases

1. **Clean view:** Hide technical details (tools, thinking) → Show AI responses only
2. **Compact view:** Collapse all bubbles to see conversation overview
3. **AI focus:** Expand only AI responses, collapse user messages
4. **Full detail:** Show everything expanded (default state)

## State Tracking

### Agent Columns (per-agent tracking)
```javascript
const expandModes = {}; // expandModes[agentId] = 'all' | 'ai' | 'none'
const thinkingToolVisibility = {}; // thinkingToolVisibility[agentId] = 'visible' | 'hidden'
```

### Prime Chat (single state)
```javascript
let primeExpandMode = 'all'; // 'all' | 'ai' | 'none'
let primeThinkingToolVisibility = 'visible'; // 'visible' | 'hidden'
```

## Button Location

### Agent Columns
- Location: `.agent-header-top` → `.agent-header-controls`
- Order: Expand → Visibility → Width → Menu
- Added before width toggle and hamburger menu

### Prime Chat
- Location: `.ai-chat-header-row` → `.chat-header-actions`
- Order: Expand → Visibility → Close
- Added before chat close button

## Technical Details

### CSS Classes
```css
.expand-cycle-btn, .visibility-btn {
    width: 28px;
    height: 28px;
    border: 1px solid var(--border-default);
    background: var(--bg-secondary);
    color: var(--text-secondary);
    border-radius: 4px;
    font-size: 12px;
}

.visibility-btn.hiding {
    background: var(--accent-primary);
    color: var(--bg-primary);
}
```

### Event Handlers
- Agent columns: `onclick="event.stopPropagation(); AgentColumn.cycleExpandMode(${agentId})"`
- Prime chat: `onclick="event.stopPropagation(); PrimeAI.cycleExpandMode()"`

## Testing Checklist

- [ ] Test expand cycle: All → AI Only → None → All
- [ ] Test visibility toggle: Show All ↔ AI Only
- [ ] Verify button icons change correctly
- [ ] Verify button tooltips update
- [ ] Test in Agent column (multiple agents)
- [ ] Test in Prime chat
- [ ] Verify `.hiding` class applies blue background
- [ ] Verify messages expand/collapse correctly
- [ ] Verify user/thinking/tool messages hide/show
- [ ] Test with no messages loaded
- [ ] Test with mixed message types

## Console Logging

Functions log their state changes:
```javascript
console.log(`📐 [AgentColumn] Expand mode for agent ${agentId}: ${nextMode}`);
console.log(`👁️ [AgentColumn] Message visibility for agent ${agentId}: ${nextState}`);
console.log(`📐 [PrimeAI] Expand mode: ${nextMode}`);
console.log(`👁️ [PrimeAI] Message visibility: ${nextState}`);
```

## Reference Source

Implementation based on `data_agent_chat.html` which had similar toggle controls for expand modes and message visibility.

## Future Enhancements

Potential improvements:
- Persist state to localStorage
- Add keyboard shortcuts (e.g., `Ctrl+E` for expand, `Ctrl+V` for visibility)
- Animate transitions (fade in/out, height animations)
- Add "Collapse All Agents" button to header
- Add per-message-type toggles (separate buttons for user, thinking, tool)
- Add "Focus Mode" that combines both toggles (AI only, expanded)
