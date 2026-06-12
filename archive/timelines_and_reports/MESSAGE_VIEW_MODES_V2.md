# Message View Modes V2 - 5 Display Options

**Date:** December 3, 2025  
**Status:** ✅ Complete

## Overview
Implemented a **single-button view mode cycler** with 5 distinct display options for messages in both Prime chat and Agent columns.

## 🎛️ The 5 View Modes

### 1. **All Collapsed** (📄 `fa-list`)
- **Shows:** All messages (AI, User, Tools, Thinking)
- **Expand state:** All collapsed
- **Use case:** Quick scan of conversation structure
- **Tooltip:** "All Collapsed → All Expanded"

### 2. **All Expanded** (🔽 `fa-expand-alt`)
- **Shows:** All messages (AI, User, Tools, Thinking)
- **Expand state:** All expanded
- **Use case:** Full detail view, see everything
- **Tooltip:** "All Expanded → AI Collapsed"
- **DEFAULT MODE**

### 3. **AI Collapsed** (🤖 `fa-robot`)
- **Shows:** AI messages (expanded) + Tools (collapsed)
- **Hides:** User messages, Thinking bubbles
- **Use case:** Focus on AI responses, tools minimized
- **Tooltip:** "AI Collapsed → AI Expanded"

### 4. **AI Expanded** (⚡ `fa-bolt`)
- **Shows:** AI messages + Tools (both expanded)
- **Hides:** User messages, Thinking bubbles
- **Use case:** AI + Tools detailed view
- **Tooltip:** "AI Expanded → AI+User Only"

### 5. **AI + User Only** (👥 `fa-users`)
- **Shows:** AI messages + User messages (both expanded)
- **Hides:** Tools, Tool results, Thinking bubbles
- **Use case:** Clean conversation without technical details
- **Tooltip:** "AI+User → All Collapsed"

## 🔄 Cycle Order
```
All Collapsed → All Expanded → AI Collapsed → AI Expanded → AI+User → [Loop]
```

## 📍 UI Implementation

### Single Button Header
**Agent Columns:**
```
[Collapse ▼] [🤖 Agent Name]  [🔽] [⟨⟩] [☰]
                               view  width menu
```

**Prime Chat:**
```
[⚛️ AI Prime]                [🔽] [≫≫]
                              view  close
```

## 🔧 Implementation Details

### State Tracking

**Agent Columns (per-agent):**
```javascript
const viewModes = {}; // viewModes[agentId] = 'all-collapsed' | 'all-expanded' | etc.
```

**Prime Chat (single):**
```javascript
let primeViewMode = 'all-expanded'; // Default view mode
```

### Mode Configuration
```javascript
const modes = ['all-collapsed', 'all-expanded', 'ai-collapsed', 'ai-expanded', 'ai-user'];

const modeLabels = {
    'all-collapsed': { icon: 'fa-list', title: 'All Collapsed → All Expanded' },
    'all-expanded': { icon: 'fa-expand-alt', title: 'All Expanded → AI Collapsed' },
    'ai-collapsed': { icon: 'fa-robot', title: 'AI Collapsed → AI Expanded' },
    'ai-expanded': { icon: 'fa-bolt', title: 'AI Expanded → AI+User Only' },
    'ai-user': { icon: 'fa-users', title: 'AI+User → All Collapsed' }
};
```

### View Mode Logic

#### Mode 1: All Collapsed
```javascript
case 'all-collapsed':
    message.classList.add('collapsed');
    break;
```

#### Mode 2: All Expanded
```javascript
case 'all-expanded':
    message.classList.add('expanded');
    break;
```

#### Mode 3: AI Collapsed
```javascript
case 'ai-collapsed':
    if (isAI) {
        message.classList.add('expanded');
    } else if (isTool) {
        message.classList.add('collapsed');
    } else if (isUser || isThinking) {
        message.style.display = 'none';
    }
    break;
```

#### Mode 4: AI Expanded
```javascript
case 'ai-expanded':
    if (isAI || isTool) {
        message.classList.add('expanded');
    } else if (isUser || isThinking) {
        message.style.display = 'none';
    }
    break;
```

#### Mode 5: AI + User Only
```javascript
case 'ai-user':
    if (isAI || isUser) {
        message.classList.add('expanded');
    } else if (isTool || isThinking) {
        message.style.display = 'none';
    }
    break;
```

## 📦 Files Modified

### JavaScript
1. **agent-column.js**
   - Changed from 2 buttons to 1 button
   - Updated state tracking: `viewModes` replaces `expandModes` and `thinkingToolVisibility`
   - `cycleExpandMode()` - Cycles through 5 modes
   - `applyViewModeToColumn()` - Applies mode logic
   - `toggleThinkingToolBubbles()` - Legacy function, now calls `cycleExpandMode()`

2. **prime_ai_chat.js**
   - Changed from 2 buttons to 1 button
   - Updated state tracking: `primeViewMode` replaces separate states
   - `cycleExpandModePrime()` - Cycles through 5 modes
   - `applyViewModeToPrime()` - Applies mode logic
   - `toggleThinkingToolBubblesPrime()` - Legacy function

### CSS
3. **agent-ui.css**
   - Renamed `.expand-cycle-btn, .visibility-btn` → `.view-mode-btn`
   - Removed `.visibility-btn.hiding` active state (no longer needed)
   - Simplified hover states

4. **business-ai-platform-v2.html**
   - Updated HTML: removed second button
   - Renamed `expand-cycle-btn` → `view-mode-btn`
   - Updated CSS class names
   - Simplified styles (removed `.hiding` states)

## 🎯 Message Type Detection

```javascript
const isAI = message.classList.contains('assistant');
const isUser = message.classList.contains('user');
const isThinking = message.classList.contains('thinking-bubble');
const isTool = message.classList.contains('tool-bubble') || message.classList.contains('tool');
```

## 🔄 Reset Logic

Before applying any mode, messages are reset:
```javascript
message.classList.remove('expanded', 'collapsed');
message.style.display = '';
```

This ensures clean state transitions between modes.

## 📋 Use Case Matrix

| Mode | AI | User | Tools | Thinking | Expand State |
|------|-----|------|-------|----------|--------------|
| All Collapsed | ✅ | ✅ | ✅ | ✅ | Collapsed |
| All Expanded | ✅ | ✅ | ✅ | ✅ | Expanded |
| AI Collapsed | ✅ | ❌ | ✅ | ❌ | AI:Exp Tools:Col |
| AI Expanded | ✅ | ❌ | ✅ | ❌ | All Expanded |
| AI + User | ✅ | ✅ | ❌ | ❌ | All Expanded |

## 🎨 Icon Legend

| Icon | Class | Meaning |
|------|-------|---------|
| 📄 | `fa-list` | All Collapsed (list view) |
| 🔽 | `fa-expand-alt` | All Expanded (full expansion) |
| 🤖 | `fa-robot` | AI Collapsed (AI focus, tools minimized) |
| ⚡ | `fa-bolt` | AI Expanded (AI + tools power view) |
| 👥 | `fa-users` | AI + User (conversation only) |

## 🔧 API

### Agent Columns
```javascript
AgentColumn.cycleExpandMode(agentId)
```

### Prime Chat
```javascript
PrimeAI.cycleExpandMode()
```

### Legacy Support
```javascript
// These still work but just call cycleExpandMode()
AgentColumn.toggleThinkingToolBubbles(agentId)
PrimeAI.toggleThinkingToolBubbles()
```

## 📝 Console Logging

```javascript
console.log(`📐 [AgentColumn] View mode for agent ${agentId}: ${nextMode}`);
console.log(`📐 [PrimeAI] View mode: ${nextMode}`);
```

## ✅ Testing Checklist

- [ ] Test mode 1: All Collapsed - all messages visible, all collapsed
- [ ] Test mode 2: All Expanded - all messages visible, all expanded (default)
- [ ] Test mode 3: AI Collapsed - only AI + tools visible, AI expanded, tools collapsed
- [ ] Test mode 4: AI Expanded - only AI + tools visible, both expanded
- [ ] Test mode 5: AI + User - only AI + user visible, no tools/thinking
- [ ] Verify icon changes correctly for each mode
- [ ] Verify tooltip updates correctly
- [ ] Test cycling through all 5 modes and back to mode 1
- [ ] Test in Agent column (multiple agents)
- [ ] Test in Prime chat
- [ ] Verify with different message combinations

## 🎯 User Benefits

1. **Simplified UI** - Single button instead of two
2. **More options** - 5 modes instead of 9 combinations (3×3)
3. **Clear icons** - Each mode has distinct, meaningful icon
4. **Logical order** - Modes progress from most detail to least
5. **Persistent state** - Each agent/Prime remembers its view mode
6. **Flexible viewing** - Choose the exact level of detail needed

## 🔮 Future Enhancements

Potential improvements:
- Add keyboard shortcut (e.g., `V` key to cycle views)
- Persist mode to localStorage
- Add mode indicator in chat (e.g., "Viewing: AI + User")
- Add quick mode selector dropdown (instead of cycling)
- Animate transitions between modes
- Add per-message expand/collapse override

## 📚 Related Documentation

- `MESSAGE_BUBBLE_TOGGLE_IMPLEMENTATION.md` - Original 2-button implementation
- `AGENT_SEND_BUTTON_FIX.md` - Send button element ID fix
