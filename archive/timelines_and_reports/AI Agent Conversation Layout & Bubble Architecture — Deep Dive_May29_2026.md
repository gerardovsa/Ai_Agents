# AI Agent Conversation Layout & Bubble Architecture — Deep Dive
**Date: May 29, 2026**  
**Author: GitHub Copilot analysis of codebase**  
**Scope: Full UI, UX, layout, code locations, colours, behaviours, CSS, rendering pipelines**

---

## Table of Contents

1. [File Map — Where Everything Lives](#1-file-map--where-everything-lives)
2. [Two Conversation Systems — Overview](#2-two-conversation-systems--overview)
3. [AI Prime Panel — Full Layout](#3-ai-prime-panel--full-layout)
4. [Agent Column — Full Layout](#4-agent-column--full-layout)
5. [Shared Base Message Bubble Structure](#5-shared-base-message-bubble-structure)
6. [Full Bubble Type Catalogue — All 14 Types](#6-full-bubble-type-catalogue--all-14-types)
7. [Streaming Rendering Pipeline](#7-streaming-rendering-pipeline)
8. [Thread History Load Pipeline](#8-thread-history-load-pipeline)
9. [View Mode System (Agent Columns)](#9-view-mode-system-agent-columns)
10. [Input System — 4-State Sliding Input](#10-input-system--4-state-sliding-input)
11. [File Attachment UX](#11-file-attachment-ux)
12. [Prompt Chips UX](#12-prompt-chips-ux)
13. [Collapse / Expand States (Columns)](#13-collapse--expand-states-columns)
14. [CSS Variables & Theming Reference](#14-css-variables--theming-reference)
15. [Shared Utilities & Modules](#15-shared-utilities--modules)
16. [Key Design Tension: Streaming vs. History Render](#16-key-design-tension-streaming-vs-history-render)
17. [Error Recovery Bubble System](#17-error-recovery-bubble-system)
18. [Agent Interaction Bubbles (agents only)](#18-agent-interaction-bubbles-agents-only)
19. [Processing & Progress Indicators](#19-processing--progress-indicators)
20. [Auto-Scroll System](#20-auto-scroll-system)
21. [Pop-Out & Fullscreen Features](#21-pop-out--fullscreen-features)
22. [Complete Data Flow Diagram](#22-complete-data-flow-diagram)

---

## 1. File Map — Where Everything Lives

### Core JavaScript Files

| File | Path | Lines | Purpose |
|------|------|-------|---------|
| `message_renderer.js` | `UI/shared/utilities/message_renderer.js` | 1133 | **Unified renderer** — creates all standard message bubbles for both Prime and Agents |
| `prime_ai_chat.js` | `UI/modules_internal/agents/prime_ai_chat.js` | 2680 | Prime AI panel — SSE stream handler, input, sending, thread loading |
| `agent-js.js` | `UI/modules_internal/agents/agent-js.js` | 5901 | Multi-agent system — MultiAgent object, SSE streaming, thread management per agent |
| `agent-column.js` | `UI/modules_internal/agents/agent-column.js` | 2216 | Column DOM creation, collapse/expand, width toggle, view mode, resize, feedback widget |
| `agent-ui.js` | `UI/modules_internal/agents/agent-ui.js` | 247 | Lightweight UI helpers |
| `agent-input.js` | `UI/modules_internal/agents/agent-input.js` | ~n/a | Per-agent input handling, file dialogs, prompt library |
| `agent-input-manager.js` | `UI/modules_internal/agents/agent-input-manager.js` | ~n/a | Shared input state management |
| `agent-interaction-bubbles.js` | `UI/modules_internal/agents/agent-interaction-bubbles.js` | 442 | Interactive input request + progress bubbles (WebSocket events) |
| `agent-interaction-websocket.js` | `UI/modules_internal/agents/agent-interaction-websocket.js` | 267 | WebSocket bridge for agent interaction events |
| `error_recovery_manager.js` | `UI/modules_internal/agents/error_recovery_manager.js` | ~n/a | Auto-recovery logic + recovery bubble injection |
| `feedback-module.js` | `UI/modules_internal/agents/feedback-module.js` | ~n/a | FeedbackModule singleton — per-agent feedback widget |
| `message-fullscreen.js` | `UI/modules_internal/agents/message-fullscreen.js` | ~n/a | Fullscreen/popout handler for individual messages |

### CSS Files

| File | Path | Lines | Purpose |
|------|------|-------|---------|
| `agent-ui.css` | `UI/modules_internal/agents/agent-ui.css` | 1405 | Complete column layout, all bubble styles, states, responsive, themes |
| `agent-interaction-bubbles.css` | `UI/modules_internal/agents/agent-interaction-bubbles.css` | 368 | Interaction request + progress bubble styles, animations |

### HTML Entry Point

| File | Path | Purpose |
|------|------|---------|
| `business-ai-platform-v2.html` | `UI/business-ai-platform-v2.html` | Main SPA — contains `#ai-chat-panel` (Prime) and the agent columns section |

---

## 2. Two Conversation Systems — Overview

The platform runs **two parallel conversation rendering systems** that share a common renderer (`UnifiedMessageRenderer`) but have completely different container structures, scroll models, and input systems.

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Main Application Layout                          │
│                                                                      │
│  ┌──────────────────────────────┐  ┌────────────────────────────┐   │
│  │  MAIN CONTENT AREA           │  │  AI PRIME PANEL (#ai-chat- │   │
│  │  (tabs, modules, etc.)       │  │  panel) — right-side slide │   │
│  │                              │  │                            │   │
│  │  ┌──────────────────────┐    │  │  .ai-chat-messages         │   │
│  │  │  AGENT COLUMNS AREA  │    │  │  (scroll container)        │   │
│  │  │  (horizontal flex)   │    │  │                            │   │
│  │  │                      │    │  │  .ai-chat-input-container  │   │
│  │  │  [Col1][Col2][Col3]  │    │  │  (4-state sliding input)   │   │
│  │  └──────────────────────┘    │  └────────────────────────────┘   │
│  └──────────────────────────────┘                                    │
└─────────────────────────────────────────────────────────────────────┘
```

| Feature | AI Prime | Agent Columns |
|---------|----------|---------------|
| Container ID | `#ai-chat-panel` / `#ai-chat-messages` | `#agent-column-{id}` / `#agent-messages-{id}` |
| Script | `prime_ai_chat.js` | `agent-js.js` + `agent-column.js` |
| Stream endpoint | `/api/agent/stream/1?thread_slug=...` | `/api/agent/stream/{id}?thread_slug=...` |
| Max columns | 1 (fixed) | Up to 26 (Alpha–Zulu NATO) |
| Width | CSS `--chat-width` variable, resizable 300–800px | 400px default, 600px wide, 800px extra-wide, 60px collapsed |
| Input style | 4-state sliding, bottom of panel | 4-state sliding, bottom of each column |
| Collapse | Toggled via sidebar button / `toggleChat()` | `.collapsed` CSS class, 60px wide bar |
| Stop streaming | `#ai-chat-stop-btn` | `#agent-stop-btn-{id}` (created dynamically) |
| Interaction bubbles | ❌ Not implemented | ✅ `AgentInteractionBubbles` via WebSocket |
| Progress bubbles | ❌ Not implemented | ✅ `AgentInteractionBubbles.renderProgressBubble()` |
| View modes | 5 modes via `primeViewMode` | 5 modes via `AgentColumn.setViewMode()` |
| Resize | Left-edge drag, `--chat-width` CSS var | Right-edge `.agent-resize-handle` drag |
| Persist state | `localStorage` `ai_chat_panel_width` | `WorkspaceManager.save()` (width, collapsed, viewMode) |
| Pop-out agent | ❌ | ✅ `AgentColumn.popOut(agentId)` |

---

## 3. AI Prime Panel — Full Layout

### HTML Structure (in `business-ai-platform-v2.html`)

```
#ai-chat-panel                           flex-direction: column; right-side panel
│
├── .ai-chat-title                       header bar with AI icon + title
│     ├── .ai-icon                       atom icon, receives status CSS classes
│     │     status classes: status-thinking | status-tool-running | status-tool-success | status-writing
│     ├── "AI Prime"
│     ├── .ai-chat-autoscroll-btn        toggle autoscroll (active = enabled)
│     ├── .ai-chat-scroll-controls       top/bottom scroll buttons
│     └── .chat-close-btn                closes/collapses the panel
│
├── #ai-chat-messages (.ai-chat-messages)   THE SCROLL CONTAINER
│     ├── #prime-welcome-container           shown until first message
│     └── ...message bubbles appended here...
│
└── .ai-chat-input-container             4-state sliding input area
      ├── #ai-chat-attached-files         file chip previews (above textarea)
      ├── .ai-chat-input-controls
      │     ├── #ai-chat-input            textarea (auto-expands to max 300px)
      │     ├── .ai-chat-input-right-buttons
      │     │     ├── #ai-chat-stop-btn   red stop button (shown only during streaming)
      │     │     ├── #ai-chat-send-btn   paper-plane send button
      │     │     └── #ai-chat-attach-btn paperclip
      │     └── #ai-chat-file-input       hidden <input type="file">
      └── #message-popup-overlay          full-screen message detail modal
```

### Prime Input — 4 States

```javascript
// State 1 (default): Collapsed bar — height: auto (small)
// State 2: Hover over collapsed bar — subtle background change
// State 3: Clicked OR focused — expanded (inputContainer.classList.add('expanded'))
// State 4: Active with text — expanded + autoscroll fires on resize

// Key behavior:
input.addEventListener('focus', () => expandInputArea());
input.addEventListener('blur', () => {
    setTimeout(() => {
        if (document.activeElement !== input && input.value.trim() === '') {
            collapseInputArea();  // Only collapses if input is empty
        }
    }, LAYOUT_CONSTANTS.BLUR_DELAY /* 200ms */);
});
```

### Prime Layout Constants (`prime_ai_chat.js` lines ~22–32)

```javascript
const LAYOUT_CONSTANTS = {
    SCROLL_CLEARANCE:   50,   // Extra pixels scrollTop = scrollHeight + 50
    PADDING_BUFFER:     16,   // Space between input and last message
    SCROLL_THRESHOLD:   100,  // Distance from bottom to disable auto-scroll
    AUTO_SCROLL_DELAY:  50,   // ms wait after DOM render before scrolling
    SCROLL_DEBOUNCE:    50,   // ms debounce on scroll event handler
    BLUR_DELAY:         200,  // ms wait before collapsing input on blur
    MAX_INPUT_HEIGHT:   300   // px max textarea height
};
```

### Prime Scroll Detection

A `ResizeObserver` watches `.ai-chat-input-container` and calls `performAutoScroll()` whenever the input area changes size (prevents content going behind the expanding textarea).

User manual scroll up disables auto-scroll when `distanceFromBottom > 100px` and scroll direction is upward.

---

## 4. Agent Column — Full Layout

### HTML Structure (generated by `AgentColumn.create(agentId, agentName)` in `agent-column.js`)

```
.agent-column#agent-column-{id}           data-agent-id="{id}"
│  min-width: 400px / max-width: 400px (default)
│
├── .collapsed-column-bar                 ONLY visible when .collapsed class present
│     ├── .expand-btn                     chevron-right, onclick: AgentColumn.expand(id)
│     └── .agent-name-vertical            writing-mode: vertical-rl; rotate(180deg)
│
├── .agent-header                         background: var(--bg-tertiary); border-bottom
│   │
│   ├── .agent-header-top                 flex; justify-content: space-between
│   │     │
│   │     ├── .agent-header-left          Left controls group
│   │     │     ├── .collapse-btn         fa-chevron-down, 32x32px
│   │     │     ├── .view-mode-btn        fa-expand-alt, 32x32px  (id: view-mode-btn-{id})
│   │     │     └── .view-mode-dropdown   hidden dropdown (id: view-mode-menu-{id})
│   │     │           ├── [all-expanded]  fa-expand-arrows-alt
│   │     │           ├── [all-collapsed] fa-compress-arrows-alt
│   │     │           ├── [ai-expanded]   fa-brain
│   │     │           ├── [ai-collapsed]  fa-tools
│   │     │           └── [ai-user]       fa-comments
│   │     │
│   │     ├── .agent-title-wrapper        Center title (flex: 1; text-align: center)
│   │     │     ├── h2                    inline-flex; gap: 8px  — icon + name
│   │     │     └── .active-users-badge   id: agent-active-users-badge-{id}
│   │     │                               (hidden by default, shows when multi-session)
│   │     │
│   │     └── .agent-header-controls      Right controls group
│   │           ├── .agent-popout-btn     fa-external-link-alt — opens floating window
│   │           ├── .width-toggle-btn     fa-chevron-right — cycles 400→600→800px
│   │           └── .agent-hamburger-button  fa-ellipsis-v — opens menu dropdown
│   │
│   ├── .agent-menu-dropdown              id: menu-{id}; hidden until toggled
│   │     ├── New Thread                  fa-plus
│   │     ├── Refresh Thread              fa-sync-alt
│   │     ├── ── divider ──
│   │     ├── Thread History              fa-history
│   │     ├── ── divider ──
│   │     └── Close Agent                 fa-times (color: var(--accent-error))
│   │
│   └── #thread-info-{id}                Thread info container (title, slug, timestamps)
│
├── .agent-messages-container             id: agent-messages-{id}
│   │  flex: 1; overflow-y: auto; padding: var(--space-3); background: var(--bg-primary)
│   │
│   ├── .empty-state                      Shown when no thread loaded (👋 greeting)
│   ├── .loading-thread-state             Shown while thread is fetching (spinner + dots)
│   └── .agent-scroll-controls            id: scroll-controls-{id}
│         ├── .agent-scroll-top-btn       fa-angle-double-up
│         ├── .agent-scroll-bottom-btn    fa-angle-double-down
│         └── .agent-autoscroll-btn       fa-step-forward (rotated 90°), .active when on
│
├── .agent-resize-handle                  data-agent-id="{id}"; right-edge drag
│
└── .agent-input-container                data-agent-id="{id}"; display: none initially
      │  Same 4-state system as Prime
      │
      ├── #agent-feedback-{id}            FeedbackModule widget container
      │
      └── .agent-input-wrapper
            ├── #agent-attached-files-{id} File chips
            │
            └── .agent-input-controls
                  ├── .agent-input-center
                  │     └── textarea#agent-input-{id}    min-height: 80px; max-height: 200px
                  │
                  └── .agent-input-right-buttons         flex-direction: column; 6 buttons
                        ├── .agent-prompt-library-btn    fa-bolt (orange) — prompt library
                        ├── .agent-feedback-btn          fa-comment-dots — feedback widget
                        ├── .agent-mic-btn               fa-microphone — voice transcription
                        ├── .agent-attach-btn            fa-paperclip — file attach
                        ├── .agent-send-btn              fa-paper-plane (accent-primary)
                        └── #agent-stop-btn-{id}         fa-stop-circle (red #ef4444)
                                                          created dynamically, display:none default
```

### Agent Column Width States

| State | CSS Class | min/max-width | flex |
|-------|-----------|--------------|------|
| Default | (none) | 400px | 1 |
| Wide | `.wide` | 600px | 1.5 |
| Extra-Wide | `.extra-wide` | 800px | 2 |
| Collapsed | `.collapsed` | 60px | — |

Width persisted via `WorkspaceManager.save(agentId, 'columnWidth', value)` and restored on `create()`.

### Agent Icons Map (`agent-column.js` lines ~55–80)

```javascript
const AGENT_ICONS = {
    1: 'fa-crosshairs',        // Alpha-1    (precision)
    2: 'fa-thumbs-up',         // Bravo-2    (well done)
    3: 'fa-satellite-dish',    // Charlie-3  (comms)
    4: 'fa-rocket',            // Delta-4    (speed)
    5: 'fa-volume-up',         // Echo-5     (sound)
    6: 'fa-paw',               // Foxtrot-6  (fox)
    7: 'fa-golf-ball',         // Golf-7     (sport)
    8: 'fa-hotel',             // Hotel-8    (lodging)
    9: 'fa-flag',              // India-9    (nation)
    10: 'fa-female',           // Juliet-10  (character)
    11: 'fa-dumbbell',         // Kilo-11    (weight)
    12: 'fa-lemon',            // Lima-12    (citrus)
    13: 'fa-microphone',       // Mike-13    (audio)
    14: 'fa-calendar-alt',     // November-14(month)
    15: 'fa-award',            // Oscar-15   (award)
    16: 'fa-church',           // Papa-16    (Pope)
    17: 'fa-map-marked-alt',   // Quebec-17  (mapping)
    18: 'fa-heart',            // Romeo-18   (romance)
    19: 'fa-mountain',         // Sierra-19  (range)
    20: 'fa-music',            // Tango-20   (dance)
    21: 'fa-user-tie',         // Uniform-21 (professional)
    22: 'fa-trophy',           // Victor-22  (victory)
    23: 'fa-glass-whiskey',    // Whiskey-23 (drink)
    24: 'fa-x-ray',            // X-ray-24   (medical)
    25: 'fa-flag-usa',         // Yankee-25  (American)
    26: 'fa-shield'            // Zulu-26    (warrior)
};
```

### Empty State HTML (`agent-column.js` ~line 575)

```javascript
function renderEmptyState(agentId, agentName) {
    return `
        <div class="empty-state" style="display: flex; align-items: center; 
              justify-content: center; min-height: 50vh; text-align: center;">
            <div style="...">
                <div style="font-size: 2em; margin-bottom: 15px;">👋</div>
                <div style="font-size: 1.2em; ...">  ${agentName} Ready  </div>
                <div>No active thread, start a new chat or load from history</div>
                <!-- Quick Tip box: border-left: 3px solid var(--accent-primary) -->
                <!-- Start New Chat button + Thread History button -->
            </div>
        </div>
    `;
}
```

### Loading State HTML (`agent-column.js` ~line 620)

```javascript
function renderLoadingState(agentId, agentName) {
    // Shows: fa-spinner fa-spin + "Loading {name}..." + 3 animated dots
    // @keyframes loadingDot: scale 0.8→1.2→0.8 with staggered delays 0/0.2/0.4s
}
```

---

## 5. Shared Base Message Bubble Structure

**All** conversation bubbles — regardless of type, role, or system — are built on this common DOM skeleton:

```html
<div class="ai-message {role} {type-modifier} [collapsed]"
     data-raw-content="{escaped raw content string}"
     data-message-id="{db-id if available}">

  <!-- HEADER ROW -->
  <div class="ai-message-header">

    <!-- LEFT GROUP -->
    <div class="ai-message-header-left">
      <!--
        For 'user' role:   [toggle-btn] [actions] [avatar]  (avatar is LAST)
        For all AI roles:  [avatar] [toggle-btn] [actions]  (avatar is FIRST)
      -->
      <div class="ai-message-avatar">
        <i class="fas fa-{icon}"></i>
        <!-- avatar background set inline per type -->
      </div>
      <button class="ai-message-toggle">
        <i class="fas fa-chevron-down"></i>
      </button>
      <div class="ai-message-actions">
        <button class="ai-message-copy-btn" title="Copy rendered text">
          <i class="fas fa-copy"></i>
        </button>
        <button class="ai-message-copy-btn" title="Copy raw content">
          <i class="fas fa-code"></i>
        </button>
        <button class="ai-message-popout-btn" title="Open in pop-out view">
          <i class="fas fa-external-link-alt"></i>
        </button>
        <!-- Streaming bubbles also add: -->
        <button class="ai-message-copy-btn" title="Expand message fullscreen">
          <i class="fas fa-expand-alt"></i>
        </button>
      </div>
    </div>

    <!-- RIGHT GROUP (UnifiedMessageRenderer only) -->
    <div class="ai-message-header-right">
      <div class="ai-message-timestamp" title="{ISO-string}">
        Mon 13 Jan 14:35
      </div>
    </div>

  </div>

  <!-- CONTENT AREA -->
  <div class="ai-message-content">
    <!-- Populated by renderUserContent() | renderAssistantContent() | renderToolContent() -->
  </div>

</div>
```

### `.collapsed` Class Behaviour

When `.collapsed` is applied to `.ai-message`, the `.ai-message-content` is hidden via CSS. Clicking `.ai-message-toggle` calls `messageDiv.classList.toggle('collapsed')`. Collapsible bubbles (thinking, tool, tool-result, server-tool) are created with `.collapsed` pre-applied.

### `data-raw-content` Attribute

Set on every bubble at creation time. Contains:
- String content → stored as-is
- Array/object content → `JSON.stringify(content)`

Used by "Copy raw content" button and `openMessagePopout()`.

---

## 6. Full Bubble Type Catalogue — All 14 Types

### Bubble 1 — Human / User Message

| Property | Value |
|----------|-------|
| **CSS classes** | `ai-message user` |
| **Avatar icon** | `fas fa-user` |
| **Avatar position** | RIGHT (last in header-left) |
| **Avatar background** | default `var(--bg-tertiary)` |
| **Collapsed by default** | No |
| **Timestamp** | Yes (top-right) |
| **Trigger** | `UnifiedMessageRenderer.render(container, 'user', content)` |
| **Content renderer** | `renderUserContent()` |
| **File location** | `message_renderer.js` line ~860 |

**Content rendering logic:**

```javascript
function renderUserContent(contentDiv, content) {
    if (Array.isArray(content)) {
        // Iterates blocks:
        // block.type === 'tool_result'  → dark-bordered preview div, click to expand/collapse
        //   max-height: 120px collapsed; overflow: hidden → auto on expand
        //   border-left: 3px solid #e6edf3; background: rgba(230,237,243,0.08)
        //   header: fa-check-circle white icon + "Tool Result" + truncated tool_use_id
        //   content preview: first 200 chars, "Click to expand" green badge if truncated
        // block.type === 'text'  → <div class="content-block-text"> + textContent
    } else {
        contentDiv.textContent = extractTextContent(content);
    }
}
```

---

### Bubble 2 — AI Text Response (Streaming)

| Property | Value |
|----------|-------|
| **CSS classes** | `ai-message assistant text-bubble` |
| **Avatar icon** | `fa-solid fa-atom` |
| **Avatar position** | LEFT (first in header-left) |
| **Avatar background** | default `var(--bg-tertiary)` |
| **Collapsed by default** | No |
| **Timestamp** | Only via `addChatMessage()` path (history); streaming path omits it |
| **Trigger (streaming)** | SSE event `type: 'content_delta'` |
| **Trigger (history)** | `UnifiedMessageRenderer.render(container, 'assistant', content)` |
| **Content renderer** | `renderAssistantContent()` — async, uses `TwoRuleStreamProcessor` |
| **File location (Prime)** | `prime_ai_chat.js` line ~1300 (bubble creation) |
| **File location (Agent)** | `agent-js.js` line ~6307 (bubble creation) |

**Streaming bubble creation (Prime `prime_ai_chat.js` ~line 1220):**

```javascript
textBubble = document.createElement('div');
textBubble.className = 'ai-message assistant text-bubble';
// Header: atom avatar + toggle + copy + copy-raw + expand + fullscreen handler
// contentDiv: .ai-message-content  ← TwoRuleStreamProcessor attaches here
// textBubble._twoRuleProcessor = new TwoRuleStreamProcessor(contentDiv)

// Per chunk:
_processor.processChunk(data.text)  // Plotly/Mermaid/CAD visualization aware

// On 'complete' event:
await _finalProc.finalize()   // Flushes deferred renders
// Safeguard check: if visibleText.length < fullResponse.length * 0.5 → force markdown render
```

**Double-click handler (Prime):**

```javascript
contentDiv.addEventListener('dblclick', (e) => {
    openMessagePopup('assistant', fullResponse, contentDiv);
    // Clones live DOM → preserves all rendered visualizations
});
```

---

### Bubble 3 — Thinking Bubble

| Property | Value |
|----------|-------|
| **CSS classes** | `ai-message assistant thinking-bubble collapsed` |
| **Avatar icon** | `fa-solid fa-brain` |
| **Avatar position** | LEFT |
| **Avatar background** | `#8b5cf6` (purple) — set inline |
| **Collapsed by default** | **YES** |
| **Timestamp** | No (streaming creation); Yes (history via `UnifiedMessageRenderer`) |
| **Trigger (streaming)** | SSE event `type: 'thinking_block'` or `type: 'thinking'` |
| **Trigger (history)** | `createThinkingBlock(thinkingContent)` inside `renderAssistantContent()` |
| **Content renderer** | `marked.parse()` with `breaks: true, gfm: true` (NOT TwoRule) |
| **File location (Prime)** | `prime_ai_chat.js` line ~940 (bubble creation) |
| **File location (Agent)** | `agent-js.js` line ~6061 |
| **File location (history)** | `message_renderer.js` line ~358 `createThinkingBlock()` |

**Multi-round separator logic (Prime):**

```javascript
// When data.delta_type === 'start' AND existing thinking text present:
thinkingBubble._fullThinkingText += '\n\n---\n\n';   // Visual separator between rounds
```

**History path — creates `thinking-block` (different class, same visual):**

```javascript
function createThinkingBlock(thinkingContent) {
    return createCollapsibleBlock({
        blockClass:   'thinking-block',         // NOTE: not thinking-bubble
        iconClass:    'thinking-icon-toggle',
        headerClass:  'thinking-header',
        contentClass: 'thinking-content',
        icon:         'brain',
        title:        'AI Reasoning Process',
        content:      thinkingContent
    });
}
// Element: <div class="thinking-block collapsed">
//   <div class="thinking-icon-toggle"><i class="fas fa-brain"></i></div>
//   <div class="expanded-content" style="display:none">
//     <div class="thinking-header">...</div>
//     <div class="thinking-content">... rendered markdown ...</div>
//   </div>
// </div>
```

---

### Bubble 4 — Tool Use Bubble (AI calling a tool)

| Property | Value |
|----------|-------|
| **CSS classes** | `ai-message assistant tool-bubble collapsed tool-status-complete` |
| **Avatar icon** | `fas fa-cog` |
| **Avatar position** | LEFT |
| **Avatar background** | `#eab308` (amber/yellow) — set inline |
| **Collapsed by default** | **YES** |
| **Timestamp** | No |
| **Trigger** | SSE event `type: 'tool_use'` |
| **Update trigger** | SSE event `type: 'tool_input_complete'` — finds via `[data-tool-id]`, updates `<pre>` |
| **File location (Prime)** | `prime_ai_chat.js` line ~1100 (bubble creation) |
| **File location (Agent)** | `agent-js.js` line ~6129 |
| **History path** | `createToolUseBlock(toolBlock)` inside `renderAssistantContent()` |

**Content structure:**

```html
<div class="ai-message-content">
  <div style="margin-bottom: 8px;"><strong>Tool:</strong> {tool_name}</div>
  <pre style="background: rgba(0,0,0,0.3); padding: 12px; border-radius: 6px; overflow-x: auto;">
    {JSON.stringify(input, null, 2)}
  </pre>
</div>
```

**History path creates `tool-request-block` (different class):**

```javascript
function createToolUseBlock(toolBlock) {
    // Creates: <div class="tool-request-block collapsed">
    //   <div class="tool-icon-toggle"><i class="fas fa-wrench"></i></div>
    //   <div class="expanded-content" style="display:none">
    //     <div class="tool-request-header">
    //       <i class="fas fa-wrench"></i>
    //       <span class="tool-name">Using Tool: {name}</span>
    //       <span class="tool-id">#{id}</span>
    //     </div>
    //     <div class="tool-json-label">JSON</div>
    //     <button class="tool-copy-btn">...</button>
    //     <pre><code class="language-json">{JSON}</code></pre>
    //   </div>
    // </div>
}
```

---

### Bubble 5 — Tool Result Bubble

| Property | Value |
|----------|-------|
| **CSS classes** | `ai-message assistant tool-result-bubble collapsed` |
| **Avatar icon** | `fas fa-flag` |
| **Avatar position** | LEFT |
| **Avatar background (success)** | `#60A5FA` (blue) — inline |
| **Avatar background (error)** | `#ef4444` (red) — inline |
| **Collapsed by default** | **YES** |
| **Timestamp** | No |
| **Trigger** | SSE event `type: 'tool_result'` |
| **File location (Prime)** | `prime_ai_chat.js` line ~1600 |
| **File location (Agent)** | `agent-js.js` line ~6213–6302 |

**Content colour coding:**

```javascript
const isError = !data.success;
// Header: fa-times-circle (red) or fa-check-circle (blue/green)
// Pre tag colour: isError ? '#fca5a5' : '#86efac'  (red tones or green tones)
// Max-height: 400px with overflow-y: auto
```

**Special `ui_command` handler (both Prime and Agent):**

```javascript
if (parsedResult.ui_command === 'open_workflow') {
    const slug = parsedResult.slug;
    window.switchToTab('automation');
    setTimeout(async () => {
        await window.automationCanvas.loadWorkflowBySlug(slug);
    }, 300);
}
```

---

### Bubble 6 — Server Tool Bubble (Web Search / Webfetch)

| Property | Value |
|----------|-------|
| **CSS classes** | `ai-message assistant server-tool-bubble collapsed` |
| **Avatar icon** | `fas fa-search` (web_search) or `fas fa-globe` (webfetch) |
| **Avatar icon colour** | `#4ADE80` green (web_search) or `#60A5FA` blue (webfetch) |
| **Avatar position** | LEFT |
| **Avatar background** | inline on icon, not background |
| **Collapsed by default** | **YES** |
| **Trigger** | SSE event `type: 'server_tool_use'` |
| **File location (Prime)** | `prime_ai_chat.js` line ~1770 |

**Content while searching:**

```html
<strong style="color: #4ADE80;">[WEBSEARCH]</strong>
<strong>Query:</strong> {query text}
<i class="fas fa-spinner fa-spin"></i> Searching...
```

---

### Bubble 7 — Tool Usage Summary (legacy non-streaming)

| Property | Value |
|----------|-------|
| **CSS classes** | `ai-message tool` |
| **Avatar icon** | `fas fa-wrench` |
| **Avatar position** | LEFT |
| **Trigger** | `addToolUsageMessage(toolsUsed)` → `addChatMessage('tool', toolContent)` |
| **Path** | Non-streaming JSON response path when `data.tools_used` array present |
| **File location** | `prime_ai_chat.js` line ~2283 `addToolUsageMessage()` |

```javascript
function addToolUsageMessage(toolsUsed) {
    const toolContent = `Used tools: ${toolsUsed.map(t => t.name).join(', ')}`;
    addChatMessage('tool', toolContent, false);
}
```

---

### Bubble 8 — Thinking Placeholder (legacy)

| Property | Value |
|----------|-------|
| **CSS classes** | `ai-message thinking` |
| **Trigger** | `addChatMessage('assistant', content, isThinking=true)` |
| **Purpose** | Placeholder with pulsing animation while waiting for real content |
| **Lifecycle** | Created → `removeThinkingIndicator()` deletes it when first SSE content arrives |
| **Note** | Superseded by `showPrimeProcessingIndicator()` / `createProcessingIndicator()` in current code |

```javascript
function removeThinkingIndicator() {
    const thinking = document.querySelector('.ai-message.thinking');
    if (thinking) thinking.remove();
}
```

---

### Bubble 9 — System / Stop Message

| Property | Value |
|----------|-------|
| **CSS classes** | `message system-message` |
| **Structure** | Plain `<div>` with textContent — NO header, NO avatar, NO `.ai-message-content` |
| **Trigger (Prime)** | `addChatMessage('system', '⏸️ Response stopped by user', false, false)` in `stopAIStream()` |
| **Trigger (Agent)** | `systemMsg.className = 'message system-message'` in `stopAgentStream()` |
| **File location (Prime)** | `prime_ai_chat.js` line ~433 |
| **File location (Agent)** | `agent-js.js` line ~203 |

---

### Bubble 10 — Error Recovery Bubbles

| Variant | CSS Class | Border Colour | Background Gradient | Icon Colour |
|---------|-----------|---------------|---------------------|------------|
| Generic | `ai-message recovery` | `#3b82f6` blue | blue→purple rgba(59,130,246,0.1)→rgba(147,51,234,0.1) | `#3b82f6` |
| Structure fix | `recovery-structure-fix` | `#8b5cf6` purple | purple gradient | `#8b5cf6` |
| Tool fix | `recovery-tool-fix` | `#eab308` yellow | yellow gradient | `#eab308` |
| Context trim | `recovery-context-trim` | `#10b981` green | green gradient | `#10b981` |
| Rate limit | `recovery-rate-limit` | `#f59e0b` amber | amber gradient | `#f59e0b` |
| Overload | `recovery-overload` | `#f59e0b` amber | amber gradient | `#f59e0b` |
| Network | `recovery-network` | `#f59e0b` amber | amber gradient | `#f59e0b` |
| Auth error | `recovery-auth-error` | `#ef4444` red | red gradient | `#ef4444` |

**Shared structure:**

```css
.ai-message.recovery {
    border-left: 3px solid {colour};
    padding: 12px 16px;
    display: flex; align-items: center; gap: 12px;
    margin: 8px 0; border-radius: 8px;
    font-size: 13px;
}
.ai-message.recovery i.fa-spin {
    animation: spin 1s linear infinite;  /* custom spin, not FA spin */
}
```

**File location:** `agent-ui.css` lines 852–940; `error_recovery_manager.js`

---

### Bubble 11 — AI Interaction Request (Agents only)

| Property | Value |
|----------|-------|
| **CSS classes** | `ai-message ai-interaction-request waiting` (changes to `responded` / `cancelled` / `timeout`) |
| **Avatar icon** | `fas fa-hand-paper` |
| **Avatar background** | `var(--accent-orange, #ff9800)` |
| **Animation (waiting)** | `pulse-border-orange 2s infinite` + avatar `pulse-scale 1.5s infinite` |
| **Trigger** | WebSocket event `input_request` dispatched via `agent-interaction-websocket.js` |
| **File location** | `agent-interaction-bubbles.js` line ~30 `renderInputRequestBubble()` |
| **CSS file** | `agent-interaction-bubbles.css` |

**Bubble border states:**

```css
.ai-interaction-request.waiting   { border: 2px solid #ff9800; animation: pulse-border-orange 2s infinite; }
.ai-interaction-request.responded { border-color: #4caf50; box-shadow: 0 4px 12px rgba(76,175,80,0.2); }
.ai-interaction-request.timeout   { border-color: #f44336; opacity: 0.7; }
.ai-interaction-request.cancelled { border-color: var(--text-secondary); opacity: 0.6; }
```

**Input type variants:**

| `input_type` | UI rendered |
|---|---|
| `text` | `<input type="text">` + Cancel + Submit buttons |
| `password` | `<input type="password">` + Cancel + Submit |
| `2fa_code` | `<input type="text" maxlength="6" pattern="[0-9]{6}">` + buttons |
| `captcha` | `<input type="text">` + "Enter characters shown" placeholder |
| `choice` | N × `.interaction-choice-btn` buttons (vertical stack), each `translateX(4px)` on hover |

**State machine:**

```
WAITING ──submit──▶ RESPONDED (green badge "Submitted"; inputs disabled; value displayed)
        ──cancel──▶ CANCELLED (grey; opacity 0.6)
        ──timeout─▶ TIMEOUT   (red; opacity 0.7)
```

**Side effects on state change:**

```javascript
// WAITING → RESPONDED/CANCELLED:
enableAgentInput(agentId);         // Restores textarea + send button
updateQuickNavBadge(agentId, ...); // Orange pulsing badge → green → default
delete activeRequests[agentId];    // Clears tracking
sendInputResponse(agentId, requestId, value); // Sends to backend via WebSocket
```

**Screenshot support:** If `metadata.screenshot` is present, renders `<img src="data:image/png;base64,{data}">` inside the bubble above the input.

**Timeout countdown:** `startTimeoutCountdown(request_id, timeout_seconds)` updates `#timeout-{request_id}` every second.

---

### Bubble 12 — Progress Update (Agents only)

| Property | Value |
|----------|-------|
| **CSS classes** | `ai-message ai-progress-update` |
| **Avatar icon** | `fas fa-sync fa-spin` |
| **Avatar background** | `var(--accent-primary, #257bdd)` |
| **Update strategy** | **In-place reuse** — same `id="progress-{session_id}"` updated on every event |
| **Trigger** | WebSocket event `progress_update` |
| **File location** | `agent-interaction-bubbles.js` line ~170 `renderProgressBubble()` |

**Progress bar structure:**

```html
<div class="progress-bar-container">    /* height: 32px; border-radius: 16px; overflow: hidden */
  <div class="progress-bar-fill" style="width: {percent}%">
    /* background: linear-gradient(90deg, #257bdd, #1565c0); transition: width 0.5s ease */
  </div>
  <div class="progress-bar-text">{step} / {total} ({percent}%)</div>   /* absolute centered */
</div>
```

---

### Bubble 13 — Processing Indicator (Bouncing Dots)

| Property | Value |
|----------|-------|
| **CSS class** | `processing-indicator` (id: `processing-indicator-{agentId}`) |
| **Structure** | 3 bouncing dots + "Processing…" text label |
| **Animation** | `@keyframes bounce`: scale 0→1→0 with `animation-delay` -0.32s / -0.16s / 0s |
| **Dot colour (dark)** | `#677eea` (blue-purple) |
| **Dot colour (light)** | `#4f5db8` |
| **Border** | `1px solid var(--accent-primary)` |
| **Entry animation** | `@keyframes fadeIn`: opacity 0→1 + translateY(-10px→0), 0.3s ease |
| **Trigger** | `createProcessingIndicator(agentId)` inserted into `#agent-messages-{id}` |
| **Removal** | `removeProcessingIndicator(agentId)` when first SSE content arrives |
| **File location** | `agent-js.js` lines 1–30 |
| **Prime equivalent** | `showPrimeProcessingIndicator()` / `hidePrimeProcessingIndicator()` (separate, similar impl) |

```css
.processing-indicator {
    display: flex; align-items: center; gap: 12px;
    padding: 16px 20px;
    background: var(--bg-secondary);
    border: 1px solid var(--accent-primary);
    border-radius: 8px;
    margin: 12px 0;
    animation: fadeIn 0.3s ease;
}
.processing-dots .dot {
    width: 8px; height: 8px;
    background: var(--accent-primary);
    border-radius: 50%;
    animation: bounce 1.4s infinite ease-in-out both;
}
```

---

### Bubble 14 — Render Progress Indicator (Thread History Load)

| Property | Value |
|----------|-------|
| **CSS class** | `render-progress-indicator` (id: `render-progress-{agentId}`) |
| **Structure** | `fa-spinner fa-spin` + text "Loading messages… X of Y" + thin fill bar |
| **Fill bar colour** | `var(--accent-primary, #58a6ff)` |
| **Fill bar transition** | `width 0.15s ease` |
| **Position** | Sibling below `.agent-messages-container` (NOT sticky/absolute) |
| **Trigger** | Thread history load batch start |
| **Update** | `updateRenderProgressIndicator(agentId, current, total)` — called every N messages |
| **Removal** | `removeRenderProgressIndicator(agentId)` when all messages rendered |
| **File location** | `agent-js.js` lines ~30–80 |

```javascript
el.style.cssText = [
    'background: var(--bg-primary, #0d1117)',
    'border-top: 1px solid var(--border-color, #30363d)',
    'padding: 8px 16px',
    'display: flex', 'align-items: center', 'gap: 10px',
    'font-size: 12px', 'color: var(--text-secondary, #8b949e)',
    'z-index: 10', 'flex-shrink: 0',
].join('; ');
```

---

## 7. Streaming Rendering Pipeline

### Prime (`prime_ai_chat.js` `sendChatMessage()`)

```
User sends message
│
├── 1. UnifiedMessageRenderer.render('#ai-chat-messages', 'user', messageContent)
│       → Bubble 1 (user)
│
├── 2. showPrimeProcessingIndicator()
│       → Bouncing dots processing indicator
│
├── 3. POST /api/agent/agent/1/start
│       → Backend loads conversation from DB (no history sent)
│       → Returns conversation array for MessageStore sync
│
├── 4. GET /api/agent/stream/1?thread_slug={slug}
│       SSE stream with X-Socket-ID header (team collab echo prevention)
│
│   SSE events → DOM actions:
│   │
│   ├── 'thinking_block' / 'thinking'
│   │     → Create thinkingBubble (Bubble 3) on first delta
│   │     → Append delta to _fullThinkingText
│   │     → marked.parse(_fullThinkingText) → thinkingContent.innerHTML
│   │     → Insert '---' separator on new delta_type:'start' if existing content
│   │
│   ├── 'tool_use'
│   │     → Flush active TwoRule processors (forceFlush)
│   │     → Create toolBubble (Bubble 4) with data-tool-id attribute
│   │     → AgentStatusIndicator.update('tool-running')
│   │
│   ├── 'tool_input_complete'
│   │     → Find toolBubble by [data-tool-id="{tool_id}"]
│   │     → Update contentDiv innerHTML with complete JSON
│   │
│   ├── 'content_delta'
│   │     → On first delta: removeThinkingIndicator(); hidePrimeProcessingIndicator()
│   │     → If switching from non-delta event type: create new textBubble (Bubble 2)
│   │     → fullResponse += data.text
│   │     → _processor.processChunk(data.text)  [TwoRuleStreamProcessor]
│   │     → OR marked.parse(fullResponse) fallback
│   │     → textBubble.scrollIntoView()
│   │
│   ├── 'tool_result'
│   │     → Flush TwoRule processors
│   │     → Create toolResultBubble (Bubble 5, success blue or error red)
│   │     → Parse JSON result; handle ui_command if present
│   │
│   ├── 'server_tool_use'
│   │     → Create serverToolBubble (Bubble 6)
│   │
│   ├── 'conversation_sync'
│   │     → Replace AppState.chatMessages with backend's authoritative array
│   │     → Sync MessageStore
│   │
│   ├── 'complete'
│   │     → await _finalProc.finalize()  [flush deferred viz renders]
│   │     → Safeguard: if visibleText < 50% of fullResponse → force markdown render
│   │     → Prism.highlightElement() on all code blocks
│   │     → ThreadManager.updateCurrentThread(conversation_history)
│   │     → MessageStore.addMessage for streamed assistant response
│   │     → currentStreamController = null; isStreaming = false
│   │     → Hide stop btn; show send btn
│   │
│   └── 'error'
│         → 413 handler: remove last assistant msg; show notification; reload thread
│         → Other: show error HTML in last assistant bubble; show notification toast
│
└── 5. Stream ends → cleanup controllers, restore UI
```

### Agent (`agent-js.js` inside `MultiAgent`)

Identical SSE event processing. Key differences:
- Container: `document.getElementById('agent-messages-{id}')` vs `document.getElementById('ai-chat-messages')`
- Processing indicator: `createProcessingIndicator(agentId)` vs `showPrimeProcessingIndicator()`
- Stop: `MultiAgent.agentStreamControllers[agentId].abort()` vs `currentStreamController.abort()`
- Each agent has its own `AbortController` in `MultiAgent.agentStreamControllers[agentId]`

---

## 8. Thread History Load Pipeline

When a thread is loaded (user clicks thread, drag-drop, etc.):

```
ThreadManager.loadThread(threadSlug)
│
├── AgentColumn.renderLoadingState(agentId)  → Bubble 14 render-progress-indicator
│
├── Fetch thread messages from API
│
├── For each message in conversation array:
│   │
│   ├── msg.role === 'user'
│   │     → UnifiedMessageRenderer.render(container, 'user', msg.content, {
│   │           scrollToBottom: false,
│   │           checkDuplicates: false,
│   │           createdAt: msg.created_at
│   │       })
│   │       → renderUserContent() handles text + tool_result blocks
│   │
│   └── msg.role === 'assistant'
│         → UnifiedMessageRenderer.render(container, 'assistant', msg.content, {
│               scrollToBottom: false,
│               checkDuplicates: false,
│               createdAt: msg.created_at
│           })
│           → renderAssistantContent() handles:
│             - Array content: iterates blocks
│               • block.type='thinking'   → createThinkingBlock() [embedded in message]
│               • block.type='text'       → TwoRuleStreamProcessor.processChunk() + finalize()
│               • block.type='tool_use'   → createToolUseBlock() [embedded in message]
│             - String content:
│               → TwoRuleStreamProcessor.processChunk() + finalize() OR marked.parse()
│
├── updateRenderProgressIndicator(agentId, current, total)  [every N messages]
│
└── removeRenderProgressIndicator(agentId)  [when done]
```

**Key difference from streaming:** History loads embed thinking/tool blocks as children of a single `ai-message assistant` div, whereas streaming creates separate sibling bubble divs.

---

## 9. View Mode System (Agent Columns)

**State stored:** `viewModes[agentId]` in `agent-column.js` + persisted via `WorkspaceManager.save(agentId, 'viewMode', mode)`

**Dropdown (`AgentColumn.toggleViewModeMenu()`):**

| Mode ID | Icon | Label | Visibility Behaviour |
|---------|------|-------|---------------------|
| `all-expanded` | `fa-expand-arrows-alt` | All Expanded | All messages visible, all collapsed blocks can be toggled |
| `all-collapsed` | `fa-compress-arrows-alt` | All Collapsed | All messages visible, all blocks force-collapsed |
| `ai-expanded` | `fa-brain` | Thinking Collapsed | AI text + tools visible, thinking blocks force-collapsed |
| `ai-collapsed` | `fa-tools` | Tools Collapsed | AI text visible, tool/thinking blocks force-collapsed |
| `ai-user` | `fa-comments` | Messages Only | Only `ai-message.user` + `ai-message.assistant.text-bubble` shown; tools/results hidden |

**Active item highlight:** `data-mode="current-mode"` div gets class `active` in the dropdown.

---

## 10. Input System — 4-State Sliding Input

Applies to both Prime (`.ai-chat-input-container`) and each Agent (`.agent-input-container`).

```
State 1: Collapsed bar
├── height: determined by content (small, ~30px)
├── cursor: pointer
├── No visible textarea
└── Click → State 4

State 2: Hover
└── background: rgba(88,166,255,0.02) [very subtle]

State 3: Focus expand (same as State 4 visually)
└── Fired on: input.addEventListener('focus', expandInputArea)

State 4: Expanded
├── .expanded class applied
├── height: auto (grows with content)
├── padding: 20px
├── cursor: default
└── textarea visible, autoscroll compensates for layout shift
```

**Textarea auto-growth:**

```javascript
input.addEventListener('input', () => {
    input.style.height = 'auto';
    const newHeight = Math.min(input.scrollHeight, MAX_INPUT_HEIGHT /* 300px Prime, 200px Agent */);
    input.style.height = newHeight + 'px';
    if (inputContainer.classList.contains('expanded') && autoScrollEnabled) {
        setTimeout(() => performAutoScroll(), 0);
    }
});
```

**Keyboard shortcuts:**
- `Enter` → send message
- `Shift+Enter` → new line

**Drag & drop files onto textarea:**

```javascript
input.addEventListener('dragover', e => { e.preventDefault(); input.classList.add('drag-over'); });
input.addEventListener('drop',     e => { handleFileSelection(e.dataTransfer.files); });
// .drag-over CSS: border-color: var(--accent-primary); background: rgba(59,130,246,0.05)
```

---

## 11. File Attachment UX

**Supported MIME types (Prime `prime_ai_chat.js` ~line 280):**

```javascript
// NATIVE (sent as base64 to Claude directly):
const NATIVE_TYPES = new Set([
    'application/pdf',              // Max: 32 MB
    'image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp'  // Max: 5 MB
]);

// EXTRACTABLE (server-side text extraction, Max: 20 MB):
// .docx, .doc, .odt, .rtf, .xlsx, .xls, .csv, .pptx, .ppt
// .txt, .md, .json, .xml, .yaml, .py, .js, .ts, .html, .css, etc.
```

**File chip structure:**

```html
<!-- In #ai-chat-attached-files or #agent-attached-files-{id} -->
<div class="ai-chat-file-chip">
  <i class="fas fa-{icon}"></i>            <!-- fa-file-pdf / fa-image / fa-file-word etc. -->
  <span>{filename} ({size}KB / {size}MB)</span>
  <button class="ai-chat-file-chip-remove" data-index="{i}">x</button>
</div>
```

**Agent file chip CSS:**

```css
.agent-file-chip {
    display: inline-flex; align-items: center; gap: var(--space-2);
    background: var(--bg-tertiary);
    border: 1px solid var(--border-default);
    border-radius: 4px; padding: 4px 8px; font-size: 12px;
}
.agent-file-chip i { color: var(--accent-primary); }
.agent-file-chip-remove:hover { color: var(--accent-error); }
```

---

## 12. Prompt Chips UX

Prompt chips appear in `.agent-attached-prompts` area above the textarea when a prompt is dragged/selected from the library.

```css
.agent-attached-prompts {
    background: rgba(255, 165, 0, 0.05);
    border: 1px dashed rgba(255, 165, 0, 0.3);
    border-radius: 6px; padding: var(--space-2);
}
.attached-prompt-chip {
    background: linear-gradient(135deg, rgba(255,165,0,0.1), rgba(255,140,0,0.1));
    border: 1px solid rgba(255,165,0,0.4);
    border-radius: 4px; padding: 5px 10px; font-size: 12px; font-weight: 500;
    transition: all 0.2s ease;
}
.attached-prompt-chip:hover {
    transform: translateY(-1px);
    box-shadow: 0 2px 4px rgba(255, 165, 0, 0.2);
}
.prompt-type-badge {       /* "QUICK" or "FULL" label */
    background: rgba(255,165,0,0.2); color: #ff8c00;
    padding: 2px 6px; border-radius: 3px; font-size: 10px;
    font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;
}
```

**Drag support on chips:** `.dragging` (opacity: 0.5, scale 0.95) / `.drag-over` (border solid, scale 1.05)

**Hover tooltip preview:**

```css
.prompt-preview-tooltip {
    position: fixed; z-index: 10000;
    background: var(--bg-secondary);
    border: 2px solid rgba(255,165,0,0.6);
    border-radius: 8px; padding: 12px; max-width: 400px;
    box-shadow: 0 8px 16px rgba(0,0,0,0.4), 0 0 20px rgba(255,165,0,0.2);
    opacity: 0; transition: opacity 0.2s ease; pointer-events: none;
}
```

---

## 13. Collapse / Expand States (Columns)

### Column Level (`.agent-column.collapsed`)

```css
.agent-column.collapsed { min-width: 60px; max-width: 60px; }
.agent-column.collapsed .collapsed-column-bar { display: flex; }
/* All other column children are hidden via overflow:hidden */
```

The collapsed bar shows:
- `.expand-btn` (chevron-right, 32x32px)
- `.agent-name-vertical` (writing-mode: vertical-rl; rotate 180deg; font-size: 14px)

### Message Level (`.ai-message.collapsed`)

```css
/* Defined in agent-ui.css — content area hidden when parent has .collapsed */
.ai-message.collapsed .ai-message-content { display: none; }
/* Toggle button chevron rotates 180° when expanded */
```

The `.ai-message-toggle` button fires `messageDiv.classList.toggle('collapsed')`.

### Popout Window State

When `AgentColumn.popOut(agentId)` is called:
- Column gets `data-popped-out="true"`
- A floating overlay window `#agent-popout-{id}` is created
- Collapse changes window width to 60px; expand restores to current width state

---

## 14. CSS Variables & Theming Reference

Key variables used throughout the bubble system (`agent-ui.css`):

| Variable | Dark theme value | Usage |
|----------|-----------------|-------|
| `--bg-primary` | `#0d1117` | Messages container background |
| `--bg-secondary` | `#161b22` | Column background, processing indicator |
| `--bg-tertiary` | `#21262d` | Header background, dropdowns |
| `--bg-hover` | `rgba(255,255,255,0.05)` | Hover states |
| `--text-primary` | `#e5e7eb` | Main text |
| `--text-secondary` | `#9ca3af` | Secondary text, timestamps |
| `--text-tertiary` | (dim) | Thread info vertical in collapsed bar |
| `--border-default` | `#30363d` | All borders |
| `--accent-primary` | `#58a6ff` | Buttons, focus rings, badges |
| `--accent-primary-hover` | `#4a8edb` | Hover state for primary buttons |
| `--accent-error` | `#ef4444` | Close agent, error states, stop button |
| `--accent-orange` | `#ff9800` | Interaction request bubbles, prompt chips |
| `--accent-green` | `#4caf50` | Success states, responded badges |
| `--space-1` | `4px` | Tiny gap |
| `--space-2` | `8px` | Small gap |
| `--space-3` | `12px` | Medium gap/padding |
| `--font-primary` | system-ui / sans-serif | Body text |

**Light theme overrides:**

```css
[data-theme="light"] .agent-column { background: #ffffff; }
[data-theme="light"] .agent-header { background: #f9fafb; }
[data-theme="light"] .agent-input-group textarea {
    background: #ffffff; border-color: #d1d5db; color: #111827;
}
[data-theme="dark"] .ai-message.recovery { color: #e5e7eb; }
```

---

## 15. Shared Utilities & Modules

| Module | Role | Used by |
|--------|------|---------|
| `UnifiedMessageRenderer` | Creates Bubbles 1, 2 (history), 7, 8 + all embedded blocks | Both Prime & Agents |
| `TwoRuleStreamProcessor` | Streaming viz rendering (Plotly, Mermaid, CAD/SVG, tables) | Both |
| `MessageStore` | Deduplication + backend DB sync | Both |
| `ThreadManager` | Thread state, history load, thread switching | Both |
| `AgentStatusIndicator` | Icon CSS status classes (thinking/tool-running/writing/idle) | Both |
| `WorkspaceManager` | `save(agentId, key, val)` / `load(agentId, key, default)` via localStorage | Agents only |
| `FeedbackModule` | Singleton feedback widget, `createWidget(id, config)` | Agents only |
| `AgentInteractionBubbles` | Bubbles 11+12, WebSocket input/progress | Agents only |
| `ErrorRecoveryManager` | Auto-recovery, Bubble 10 injection | Both |
| `SynergyRealtime` | Socket.IO presence, `setPresenceScope()`, `socket.id` for X-Socket-ID header | Both |
| `BrowserContext` | Gathers browser metadata for user context | Prime |
| `ToolManager` | Tool registry, `availableTools`, `toolsByPlatform` | Both |
| `AppState` | Global state (`chatOpen`, `chatMessages`, `isConnected`, `currentTab`, `user`) | Prime |

---

## 16. Key Design Tension: Streaming vs. History Render

**The fundamental structural difference:**

### Streaming (Live)

Multiple **sibling** bubbles are created one after another in the container:

```
#agent-messages-{id}
  ├── <div class="ai-message assistant thinking-bubble collapsed">   ← created on thinking event
  ├── <div class="ai-message assistant tool-bubble collapsed">       ← created on tool_use event
  ├── <div class="ai-message assistant tool-result-bubble collapsed"> ← created on tool_result
  └── <div class="ai-message assistant text-bubble">                 ← created on content_delta
```

### History Load (Replay)

A **single** `ai-message assistant` bubble contains all blocks as embedded children:

```
#agent-messages-{id}
  └── <div class="ai-message assistant" data-raw-content="[{...}]">
          <div class="ai-message-header">...</div>
          <div class="ai-message-content">
            <div class="thinking-block collapsed">...</div>    ← embedded
            <div class="content-block-text">... text ...</div> ← embedded
            <div class="tool-request-block collapsed">...</div> ← embedded
          </div>
      </div>
```

This means the same conversation looks structurally different depending on whether it was streamed live vs. loaded from DB. Both visually approximate the same appearance (collapsible icons) but via different DOM structures.

---

## 17. Error Recovery Bubble System

**File:** `UI/modules_internal/agents/error_recovery_manager.js`

**Trigger conditions:**

```javascript
const isRecoverable = errorMsgLower.includes('invalid_request_error') ||
    errorMsgLower.includes('tool_use_id') ||
    errorMsgLower.includes('first block must be') ||
    errorMsgLower.includes('thinking') ||
    errorMsgLower.includes('rate limit') ||
    errorMsgLower.includes('context_length') ||
    errorMsgLower.includes('prompt is too long') ||
    errorMsgLower.includes('overloaded');
```

**Recovery type → bubble class mapping:**

```javascript
// In ErrorRecoveryManager:
'structure_fix'   → 'ai-message recovery recovery-structure-fix'   // conv structure repair
'tool_fix'        → 'ai-message recovery recovery-tool-fix'         // tool_use_id mismatch
'context_trim'    → 'ai-message recovery recovery-context-trim'     // truncated context
'rate_limit'      → 'ai-message recovery recovery-rate-limit'
'overload'        → 'ai-message recovery recovery-overload'
'network'         → 'ai-message recovery recovery-network'
'auth_error'      → 'ai-message recovery recovery-auth-error'
```

**Guard:** `window.isErrorRecoveryEnabled(errorType)` — checks settings before attempting auto-recovery. If disabled, rethrows error for normal error display.

**Recovery log export:** `recoveryManager.exportRecoveryLog()` — outputs full recovery history to console.

---

## 18. Agent Interaction Bubbles (Agents Only)

**File:** `UI/modules_internal/agents/agent-interaction-bubbles.js`  
**CSS:** `UI/modules_internal/agents/agent-interaction-bubbles.css`  
**WebSocket bridge:** `UI/modules_internal/agents/agent-interaction-websocket.js`

### Input Request Bubble (`renderInputRequestBubble`)

**Slide-in animation:**

```css
@keyframes slide-in-up {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0); }
}
```

**Waiting pulse animation:**

```css
@keyframes pulse-border-orange {
    0%, 100% { border-color: #ff9800; box-shadow: 0 4px 12px rgba(255,152,0,0.2); }
    50%       { border-color: rgba(255,152,0,0.6); box-shadow: 0 4px 20px rgba(255,152,0,0.4); }
}
```

**Choice button hover:**

```css
.interaction-choice-btn:hover {
    border-color: var(--accent-primary, #257bdd);
    transform: translateX(4px);  /* Slides right on hover */
}
```

**Error shake animation (invalid input attempt):**

```css
@keyframes shake {
    0%, 100% { transform: translateX(0); }
    25%       { transform: translateX(-10px); }
    75%       { transform: translateX(10px); }
}
.interaction-input-field.error { animation: shake 0.3s; }
```

### Progress Bubble (`renderProgressBubble`)

**In-place update strategy:**

```javascript
let bubble = document.getElementById(`progress-${session_id}`);
if (!bubble) {
    bubble = document.createElement('div');
    bubble.id = `progress-${session_id}`;
    // append to container
}
bubble.innerHTML = `...updated HTML with new percent...`;
```

Progress bar fill: `linear-gradient(90deg, #257bdd, #1565c0)` with `transition: width 0.5s ease`.

---

## 19. Processing & Progress Indicators

### Prime Processing Indicator

Called via `window.showPrimeProcessingIndicator()` / `window.hidePrimeProcessingIndicator()`.
- Appears between user message send and first SSE content arriving
- Hidden immediately when `firstContentReceived = true` in SSE handler

### Agent Processing Indicator (Bouncing Dots)

```javascript
// Creation (agent-js.js line ~1):
const indicator = document.createElement('div');
indicator.className = 'processing-indicator';
indicator.id = `processing-indicator-${agentId}`;
indicator.innerHTML = `
    <div class="processing-dots">
        <div class="dot"></div>
        <div class="dot"></div>
        <div class="dot"></div>
    </div>
    <span class="processing-text">Processing...</span>
`;

// Removal:
function removeProcessingIndicator(agentId) {
    const indicator = document.getElementById(`processing-indicator-${agentId}`);
    if (indicator) indicator.remove();
}
```

### Scroll Control Visibility (Agent)

A `MutationObserver` watches `#agent-messages-{id}` for child changes and calls `updateScrollControlsVisibility(agentId)`. Scroll controls (`#scroll-controls-{id}`) are shown/hidden based on whether messages exist.

---

## 20. Auto-Scroll System

### Prime

```javascript
let autoScrollEnabled = true;

function performAutoScroll() {
    if (!autoScrollEnabled) return;
    const messagesContainer = document.querySelector('.ai-chat-messages');
    setTimeout(() => {
        messagesContainer.scrollTop = messagesContainer.scrollHeight + 50; // SCROLL_CLEARANCE
    }, 50); // AUTO_SCROLL_DELAY
}

// Auto-disable: when user manually scrolls up AND distanceFromBottom > 100px
messagesContainer.addEventListener('scroll', throttled(() => {
    if (scrollUp && distanceFromBottom > SCROLL_THRESHOLD) {
        autoScrollEnabled = false;
    }
}, SCROLL_DEBOUNCE /* 50ms */));
```

`#ai-chat-autoscroll-btn` toggles `autoScrollEnabled` and has `.active` class when enabled.

### Agent

Each agent has its own `#agent-autoscroll-{id}` button and auto-scroll state.

`setupScrollDetection(agentId, messagesContainer)` attaches a throttled (150ms) scroll handler that:
1. Near top → calls `ThreadManager.loadOlderMessagesForAgent(agentId)` (pagination)
2. Not at bottom → adds `.user-scrolled` class to container (pauses autoscroll)
3. Back at bottom → removes `.user-scrolled`

---

## 21. Pop-Out & Fullscreen Features

### Message Pop-Out (bubble level)

**Trigger:** Clicking `.ai-message-popout-btn` (external-link icon) or double-clicking text content.

**Function:** `openMessagePopup(role, content, renderedEl)` in `prime_ai_chat.js`

```javascript
function openMessagePopup(role, content, renderedEl) {
    const overlay = document.getElementById('message-popup-overlay');
    // For assistant: clone renderedEl DOM (preserves live Plotly/Mermaid/CAD visualizations)
    const clone = renderedEl.cloneNode(true);
    clone.querySelectorAll('.viz-resize-handle').forEach(el => el.remove()); // strip resize handles
    body.appendChild(clone);
    overlay.classList.add('active');
}
```

**Message Fullscreen:** `window.openMessageFullscreen(messageElement)` via `message-fullscreen.js`. Double-click on `.ai-message-content` also triggers this for streaming text bubbles.

**Floating Popout (window level for agents):** `AgentColumn.popOut(agentId)` creates `#agent-popout-{id}` overlay window. The column is marked `data-popped-out="true"`. Width changes on collapse/expand sync to the floating window.

### UnifiedMessageRenderer Pop-Out Window

`UnifiedMessageRenderer.openMessagePopout(messageElement)` creates a draggable, resizable floating window with:
- Min width: 300px / Min height: 200px
- Z-index management: starts at 10000, increments, caps at `2147483647 - 1000`
- Multiple windows stack with 30px cascade offset from `POPOUT_CASCADE_OFFSET`
- Tracked in `activePopouts: Map` for cleanup
- Drag handlers: `createDragHandlers()` — mousedown → mousemove → mouseup with viewport clamping
- Resize handlers: `createResizeHandlers()`

---

## 22. Complete Data Flow Diagram

```
                        ┌─────────────────────────────────────────────────────────┐
                        │                RENDERING ENTRY POINTS                    │
                        └─────────────────────────────────────────────────────────┘

 LIVE STREAMING                           HISTORY LOAD                 INTERACTION
 ─────────────                            ────────────                 ───────────
 sendChatMessage()                        ThreadManager.loadThread()   WebSocket
        │                                        │                         │
        │ POST /api/agent/start                  │ GET /api/thread/...     │
        │ GET  /api/agent/stream (SSE)            │                         ▼
        │                                        │              AgentInteractionBubbles
        ▼                                        ▼                    │           │
 SSE event loop                    UnifiedMessageRenderer.render()    │           │
  thinking_block ──────────────── → [Bubble 3: thinking-bubble]       │           │
  tool_use ──────────────────────── [Bubble 4: tool-bubble]    renderInputRequest  renderProgress
  tool_input_complete ──(update)── → existing tool-bubble             │           │
  content_delta ──────────────── → [Bubble 2: text-bubble]           ▼           ▼
  tool_result ─────────────────── [Bubble 5: tool-result-bubble]  [Bubble 11]  [Bubble 12]
  server_tool_use ─────────────── [Bubble 6: server-tool-bubble]
  error ───────────────────────── → modifies last bubble HTML
  complete ────────────────────── → finalize() + force-render check

 USER SENDS MESSAGE                       STOP STREAMING
 ─────────────────                        ──────────────
 UnifiedMessageRenderer.render()          stopAIStream() / stopAgentStream()
 → [Bubble 1: user]                       AbortController.abort()
                                          → [Bubble 9: system-message]

 ERROR RECOVERY                           PROCESSING STATES
 ──────────────                           ─────────────────
 ErrorRecoveryManager.handleError()       Before first SSE content:
 → [Bubble 10: recovery-{type}]           → [Bubble 13: processing-indicator]
                                          Thread loading:
                                          → [Bubble 14: render-progress-indicator]

                    ┌─────────────────────────────────────────────────────────┐
                    │              CONTENT RENDERER SELECTION                  │
                    │                                                          │
                    │  assistant + streaming → TwoRuleStreamProcessor          │
                    │  assistant + history   → TwoRuleStreamProcessor + await  │
                    │  assistant + fallback  → marked.parse()                  │
                    │  user                  → textContent / tool_result blocks │
                    │  tool (legacy)         → renderToolContent() → <pre>JSON │
                    │  thinking              → marked.parse() only              │
                    └─────────────────────────────────────────────────────────┘
```

---

## Appendix A — `UnifiedMessageRenderer` Public API

```javascript
// message_renderer.js — exported as IIFE

UnifiedMessageRenderer.render(container, role, content, options)
// container: HTMLElement or CSS selector string
// role:      'user' | 'assistant' | 'ai' | 'tool'
// content:   string | object | array (Claude API format)
// options: {
//   isThinking:       boolean (default false) — legacy thinking placeholder
//   scrollToBottom:   boolean (default true)
//   threadId:         string  — for MessageStore dedup
//   syncToBackend:    boolean — whether to persist to DB
//   createdAt:        string  — ISO timestamp for display
//   checkDuplicates:  boolean (default true) — skip if MessageStore finds duplicate
//   messageId:        string  — DB message ID if known
// }
// Returns: Promise<HTMLElement|null>  (null = skipped/duplicate)

UnifiedMessageRenderer.copyRenderedText(messageElement, button)
// Copies .ai-message-content innerText to clipboard

UnifiedMessageRenderer.copyRawContent(messageElement, button)
// Copies data-raw-content attribute to clipboard

UnifiedMessageRenderer.updateThinkingMessage(messageDiv, content)
// Replaces thinking animation with real content (async)

UnifiedMessageRenderer.openMessagePopout(messageElement)
// Opens floating resizable/draggable pop-out window
```

---

## Appendix B — SSE Event Types Reference

| Event `type` | Created by | UI Action |
|---|---|---|
| `thinking_block` / `thinking` | Claude Extended Thinking | Create/append thinking-bubble (Bubble 3) |
| `tool_use` | Claude tool call | Create tool-bubble (Bubble 4) with `data-tool-id` |
| `tool_input_complete` | Backend | Update existing tool-bubble JSON `<pre>` |
| `content_delta` | Claude text streaming | Create/append text-bubble (Bubble 2) |
| `tool_result` | Backend tool execution | Create tool-result-bubble (Bubble 5), ui_command handler |
| `server_tool_use` | Anthropic server tools | Create server-tool-bubble (Bubble 6) |
| `conversation_sync` | Backend sync | Replace AppState.chatMessages + MessageStore |
| `complete` | Backend stream end | Finalize TwoRule, sync, cleanup |
| `error` | Backend error | 413 special handler or error HTML injection |

---

## Appendix C — Key Line Number Reference

| Location | File | Approx. Line |
|---|---|---|
| `UnifiedMessageRenderer.render()` main function | `message_renderer.js` | ~860 |
| `renderUserContent()` | `message_renderer.js` | ~620 |
| `renderAssistantContent()` | `message_renderer.js` | ~455 |
| `createThinkingBlock()` | `message_renderer.js` | ~358 |
| `createToolUseBlock()` | `message_renderer.js` | ~393 |
| `createMessageHeader()` | `message_renderer.js` | ~700 |
| `sendChatMessage()` Prime entry | `prime_ai_chat.js` | ~690 |
| `thinkingBubble` creation | `prime_ai_chat.js` | ~940 |
| `toolBubble` creation | `prime_ai_chat.js` | ~1100 |
| `textBubble` creation | `prime_ai_chat.js` | ~1220 |
| `toolResultBubble` creation | `prime_ai_chat.js` | ~1600 |
| `serverToolBubble` creation | `prime_ai_chat.js` | ~1770 |
| `addChatMessage()` | `prime_ai_chat.js` | ~2545 |
| `addToolUsageMessage()` | `prime_ai_chat.js` | ~2283 |
| `createProcessingIndicator()` | `agent-js.js` | ~1 |
| `createRenderProgressIndicator()` | `agent-js.js` | ~35 |
| `setupScrollDetection()` | `agent-js.js` | ~100 |
| `showAgentStopButton()` | `agent-js.js` | ~155 |
| `MultiAgent` object definition | `agent-js.js` | ~215 |
| Agent `thinkingBubble` creation | `agent-js.js` | ~6061 |
| Agent `toolBubble` creation | `agent-js.js` | ~6129 |
| Agent `toolResultBubble` creation | `agent-js.js` | ~6213 |
| Agent `textBubble` creation | `agent-js.js` | ~6307 |
| `AgentColumn.create()` | `agent-column.js` | ~145 |
| `renderEmptyState()` | `agent-column.js` | ~575 |
| `renderLoadingState()` | `agent-column.js` | ~620 |
| `AgentColumn.setViewMode()` | `agent-column.js` | ~(after 620) |
| `renderInputRequestBubble()` | `agent-interaction-bubbles.js` | ~30 |
| `renderProgressBubble()` | `agent-interaction-bubbles.js` | ~170 |
| Column CSS | `agent-ui.css` | ~25 |
| Processing indicator CSS | `agent-ui.css` | ~942 |
| Recovery bubble CSS | `agent-ui.css` | ~852 |
| Interaction bubble CSS | `agent-interaction-bubbles.css` | ~1 |
