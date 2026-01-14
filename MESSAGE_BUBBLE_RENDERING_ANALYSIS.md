# Message Bubble Rendering Analysis: AI Prime vs Agent Columns

**Generated:** November 23, 2025  
**Issue:** Agent columns don't display different AI response events (thinking, tool_use, text) properly compared to AI Prime

---

## Executive Summary

**ROOT CAUSE IDENTIFIED:**

Agent columns use `UnifiedMessageRenderer.render()` for the INITIAL message creation, but then **switch to manual bubble creation** in `handleAgentStreamEvent()` and `renderStructuredAgentMessage()` for streaming responses. This creates **inconsistent HTML structures** that don't match AI Prime's superior design.

**AI Prime** creates all bubbles (thinking, tool, text) **inline during streaming** with full structure (header, avatar, toggle, actions).

**Agent columns** create a simple bubble via `UnifiedMessageRenderer`, then **completely ignore** that structure when handling streaming events.

---

## Architecture Comparison

### AI Prime (CORRECT Implementation)

**File:** `prime_ai_chat.js` (2224 lines)

**Flow:**
1. User message → `UnifiedMessageRenderer.render()` ✅
2. Create typing indicator ✅
3. **Stream handling** → **Inline bubble creation** for each event type:
   - `thinking_block` → Creates `ai-message assistant thinking-bubble`
   - `tool_use` → Creates `ai-message assistant tool-bubble`
   - `content_block_delta` (text) → Creates `ai-message assistant text-bubble`
4. Each bubble has full structure:
   - `ai-message-header` (avatar + toggle + actions)
   - `ai-message-content` (with TwoRuleStreamProcessor)

**Streaming Handler:** Lines 772-1300 (528 lines of inline bubble creation)

**Key Code Pattern (Prime - Thinking Bubble):**
```javascript
// Lines 816-895 in prime_ai_chat.js
if (data.type === 'thinking_block' || data.type === 'thinking') {
    if (!thinkingBubble) {
        thinkingBubble = document.createElement('div');
        thinkingBubble.className = 'ai-message assistant thinking-bubble';
        
        // CREATE FULL HEADER STRUCTURE
        const headerDiv = document.createElement('div');
        headerDiv.className = 'ai-message-header';
        
        const avatar = document.createElement('div');
        avatar.className = 'ai-message-avatar';
        avatar.style.background = '#8b5cf6';
        avatar.innerHTML = '<i class="fa-solid fa-brain" style="color: white;"></i>';
        
        const toggleBtn = document.createElement('button');
        toggleBtn.className = 'ai-message-toggle';
        toggleBtn.innerHTML = '<i class="fas fa-chevron-down"></i>';
        toggleBtn.addEventListener('click', (e) => {
            thinkingBubble.classList.toggle('collapsed');
        });
        
        headerDiv.appendChild(avatar);
        headerDiv.appendChild(toggleBtn);
        
        // CREATE ACTION BUTTONS
        const actionsDiv = document.createElement('div');
        actionsDiv.className = 'ai-message-actions';
        
        const copyBtn = document.createElement('button');
        copyBtn.className = 'ai-message-copy-btn';
        copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
        // ... copy handler
        
        actionsDiv.appendChild(copyBtn);
        headerDiv.appendChild(actionsDiv);
        
        // CREATE CONTENT DIV
        const contentDiv = document.createElement('div');
        contentDiv.className = 'ai-message-content';
        
        thinkingBubble.appendChild(headerDiv);
        thinkingBubble.appendChild(contentDiv);
        thinkingBubble.classList.add('collapsed');
        chatMessages.appendChild(thinkingBubble);
        // INITIALIZE PROCESSOR HERE
    }
    // Update thinking content...
}
```

**Key Code Pattern (Prime - Text Bubble with TwoRuleStreamProcessor):**
```javascript
// Lines 1073-1145 in prime_ai_chat.js
if (data.type === 'content_block_delta' && data.delta_type === 'text_delta') {
    if (!textBubble) {
        textBubble = document.createElement('div');
        textBubble.className = 'ai-message assistant text-bubble';
        
        // SAME FULL HEADER STRUCTURE (avatar, toggle, actions)
        // ...
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'ai-message-content';
        textBubble.appendChild(contentDiv);
        chatMessages.appendChild(textBubble);
        
        // ✅ CRITICAL: Initialize TwoRuleStreamProcessor here
        if (typeof TwoRuleStreamProcessor !== 'undefined') {
            const _proc = new TwoRuleStreamProcessor(contentDiv);
            textBubble._twoRuleProcessor = _proc;
            window._twoRuleProcessors = window._twoRuleProcessors || new Set();
            window._twoRuleProcessors.add(_proc);
        }
    }
    
    // Process chunk with TwoRuleStreamProcessor
    const _processor = textBubble._twoRuleProcessor;
    if (_processor && typeof _processor.processChunk === 'function') {
        _processor.processChunk(data.text);
    }
}
```

---

### Agent Columns (INCORRECT Implementation)

**File:** `agent-js.js` (4674 lines)

**Flow:**
1. User message → `UnifiedMessageRenderer.render()` ✅
2. Create **simple** AI message via `UnifiedMessageRenderer.render()` with `isTyping: true` ❌
3. **Stream handling** → `handleAgentStreamEvent()` function (lines 3862-3928)
4. **Problem:** Only handles `content_block_delta` (text), **ignores** thinking/tool events ❌
5. **Problem:** Uses existing bubble from step 2 instead of creating proper structure ❌

**Streaming Handler:** Lines 3862-3928 (66 lines - much simpler than Prime)

**Key Code Pattern (Agent - WRONG):**
```javascript
// Lines 2857-2865 in agent-js.js
// ❌ PROBLEM: Creates generic "isTyping" bubble instead of proper structure
const aiMessageDiv = UnifiedMessageRenderer.render(
    `#agent-messages-${agentId}`,
    'assistant',
    '',
    { 
        threadId: currentThread.id,
        syncToBackend: false,
        isTyping: true  // ❌ This creates EMPTY content div
    }
);
```

**Agent Stream Handler (INCOMPLETE):**
```javascript
// Lines 3862-3928 in agent-js.js
function handleAgentStreamEvent(agentId, data, bubble) {
    // Initialize processor (OK)
    if (!bubble.dataset.processorInitialized && typeof TwoRuleStreamProcessor !== 'undefined') {
        const _p = new TwoRuleStreamProcessor(bubble);
        bubble._twoRuleProcessor = _p;
        // ...
    }
    
    // ❌ PROBLEM 1: Only handles text_delta, no thinking/tool events
    if (data.type === 'content_block_delta') {
        if (data.delta_type === 'text_delta') {
            const text = data.text || '';
            
            // Process with TwoRuleStreamProcessor
            const _agentProc = bubble._twoRuleProcessor || bubble.processor;
            if (_agentProc && bubble.dataset.processorInitialized === 'true') {
                _agentProc.processChunk(text);
            } else {
                // Fallback to plain HTML
                bubble.innerHTML += text.replace(/</g, '&lt;').replace(/>/g, '&gt;');
            }
        }
    } else if (data.type === 'done') {
        // Finalize (OK)
        const _agentFinal = bubble._twoRuleProcessor;
        if (_agentFinal && typeof _agentFinal.finalize === 'function') {
            _agentFinal.finalize();
        }
    }
    
    // ❌ PROBLEM 2: No handling for:
    //    - thinking_block
    //    - tool_use
    //    - tool_result
    //    - content_block_start
}
```

**Agent Loaded Messages (renderStructuredAgentMessage - Lines 3940-4300):**
This function **does** create proper bubble structures for loaded messages, BUT:
- ❌ Not used during streaming (only for loading from database)
- ❌ Creates inconsistent HTML compared to streaming
- ✅ Has proper structure for thinking, tool, text bubbles

---

## HTML Structure Comparison

### AI Prime Bubble Structure (CORRECT)

```html
<!-- Thinking Bubble -->
<div class="ai-message assistant thinking-bubble collapsed">
    <div class="ai-message-header">
        <div class="ai-message-avatar" style="background: #8b5cf6;">
            <i class="fa-solid fa-brain" style="color: white;"></i>
        </div>
        <button class="ai-message-toggle">
            <i class="fas fa-chevron-down"></i>
        </button>
        <div class="ai-message-actions">
            <button class="ai-message-copy-btn" title="Copy thinking content">
                <i class="fas fa-copy"></i>
            </button>
        </div>
    </div>
    <div class="ai-message-content">
        <!-- Thinking content rendered with markdown -->
    </div>
</div>

<!-- Tool Bubble -->
<div class="ai-message assistant tool-bubble collapsed" data-tool-id="tool_123">
    <div class="ai-message-header">
        <div class="ai-message-avatar" style="background: #eab308;">
            <i class="fas fa-cog" style="color: white;"></i>
        </div>
        <button class="ai-message-toggle">
            <i class="fas fa-chevron-down"></i>
        </button>
        <div class="ai-message-actions">
            <button class="ai-message-copy-btn">
                <i class="fas fa-copy"></i>
            </button>
        </div>
    </div>
    <div class="ai-message-content">
        <div><strong>Tool:</strong> gmail_send_email</div>
        <pre>{"to": "user@example.com", ...}</pre>
    </div>
</div>

<!-- Text Bubble (Main Response) -->
<div class="ai-message assistant text-bubble">
    <div class="ai-message-header">
        <div class="ai-message-avatar">
            <i class="fa-solid fa-atom"></i>
        </div>
        <button class="ai-message-toggle">
            <i class="fas fa-chevron-down"></i>
        </button>
        <div class="ai-message-actions">
            <button class="ai-message-copy-btn" title="Copy rendered text">
                <i class="fas fa-copy"></i>
            </button>
            <button class="ai-message-copy-btn" title="Copy raw markdown">
                <i class="fas fa-code"></i>
            </button>
        </div>
    </div>
    <div class="ai-message-content">
        <!-- Content rendered by TwoRuleStreamProcessor -->
        <!-- Supports Plotly charts, Mermaid diagrams, code blocks, etc. -->
    </div>
</div>
```

### Agent Column Bubble Structure (WRONG - Current)

```html
<!-- Created by UnifiedMessageRenderer with isTyping: true -->
<div class="ai-message assistant thinking">
    <div class="ai-message-header">
        <div class="ai-message-avatar">
            <i class="fa-solid fa-atom"></i>
        </div>
        <button class="ai-message-toggle">
            <i class="fas fa-chevron-down"></i>
        </button>
        <div class="ai-message-actions">
            <button class="ai-message-copy-btn">
                <i class="fas fa-copy"></i>
            </button>
            <button class="ai-message-copy-btn">
                <i class="fas fa-code"></i>
            </button>
        </div>
    </div>
    <div class="ai-message-content">
        <!-- ❌ PROBLEM: Empty or filled with streamed text -->
        <!-- ❌ No separate bubbles for thinking/tools/text -->
        <!-- ❌ All content goes into ONE bubble -->
    </div>
</div>
```

**What happens during streaming:**
1. `UnifiedMessageRenderer` creates ONE bubble with empty content
2. `handleAgentStreamEvent()` fills that SAME bubble with all text
3. ❌ Thinking content mixed with text content
4. ❌ Tool events ignored (not rendered)
5. ❌ No visual separation of response events

---

## CSS Classes Comparison

### AI Prime Classes (CORRECT - All Used)

```css
/* Base message */
.ai-message { /* Base styles */ }
.ai-message.assistant { /* Assistant message */ }
.ai-message.user { /* User message */ }

/* Bubble types (separate visuals) */
.ai-message.thinking-bubble { background: linear-gradient(135deg, #f3e8ff, #fce7f3); }
.ai-message.tool-bubble { background: linear-gradient(135deg, #fef3c7, #fed7aa); }
.ai-message.text-bubble { background: linear-gradient(135deg, #dbeafe, #e0e7ff); }
.ai-message.tool-result-bubble { background: linear-gradient(135deg, #d1fae5, #fef3c7); }

/* States */
.ai-message.collapsed .ai-message-content { display: none; }
.ai-message.collapsed .ai-message-toggle i { transform: rotate(-90deg); }

/* Components */
.ai-message-header { /* Flex container for avatar + toggle + actions */ }
.ai-message-avatar { /* Circular avatar with icon */ }
.ai-message-toggle { /* Collapse/expand button */ }
.ai-message-actions { /* Copy buttons container */ }
.ai-message-content { /* Content area with markdown/viz */ }
```

### Agent Columns Classes (INCOMPLETE Usage)

Same CSS classes exist, but:
- ❌ Only `.ai-message.assistant` used (no bubble type classes)
- ❌ No `.thinking-bubble`, `.tool-bubble` during streaming
- ❌ All content rendered as generic assistant message

---

## Event Type Handling Comparison

### Anthropic API Streaming Events

| Event Type | AI Prime | Agent Columns | Notes |
|-----------|----------|---------------|-------|
| `thinking_block` | ✅ Full bubble | ❌ Ignored | Purple brain icon, collapsible |
| `tool_use` | ✅ Full bubble | ❌ Ignored | Yellow cog icon, shows input |
| `tool_result` | ✅ Full bubble | ❌ Ignored | Green checkmark, shows output |
| `content_block_delta` (text) | ✅ Full bubble | ⚠️ Partial | Agent adds to existing bubble |
| `content_block_start` | ✅ Handled | ❌ Ignored | Initializes content block |
| `done` | ✅ Finalize | ✅ Finalize | Both call processor.finalize() |

---

## TwoRuleStreamProcessor Integration

### AI Prime (CORRECT)

```javascript
// Create bubble FIRST
const textBubble = document.createElement('div');
textBubble.className = 'ai-message assistant text-bubble';

// Create content div
const contentDiv = document.createElement('div');
contentDiv.className = 'ai-message-content';
textBubble.appendChild(contentDiv);

// THEN initialize processor on contentDiv
const _proc = new TwoRuleStreamProcessor(contentDiv);
textBubble._twoRuleProcessor = _proc;

// Later, when text arrives:
_proc.processChunk(data.text);
```

**Result:** Plotly charts, Mermaid diagrams, code blocks all render correctly.

### Agent Columns (WRONG)

```javascript
// Create bubble via UnifiedMessageRenderer (which initializes processor internally)
const aiMessageDiv = UnifiedMessageRenderer.render(..., '', { isTyping: true });

// Later, handleAgentStreamEvent tries to initialize processor AGAIN
if (!bubble.dataset.processorInitialized) {
    const _p = new TwoRuleStreamProcessor(bubble); // ❌ Wrong: should be on content div
    bubble._twoRuleProcessor = _p;
}

// Process chunk
_p.processChunk(text);
```

**Problems:**
1. ❌ Processor initialized on wrong element (bubble instead of content div)
2. ❌ `UnifiedMessageRenderer` may have already initialized processor
3. ❌ Duplicate initialization causes conflicts
4. ❌ No thinking/tool bubbles created, so all content mixed together

---

## UnifiedMessageRenderer Issues

**File:** `UI/modules/shared/message_renderer.js` (417 lines)

**Purpose:** Provide unified message rendering for both Prime and Agent columns.

**PROBLEM:** `isThinking` option creates EMPTY content div:

```javascript
// Lines 93-98 in message_renderer.js
if (isThinking) {
    // Skip rendering thinking animation (doesn't display properly)
    // Content will be replaced when actual response arrives
    contentDiv.innerHTML = '';  // ❌ EMPTY!
} else if (role === 'assistant' || role === 'ai') {
    renderAssistantContent(contentDiv, content);
    // ✅ Initializes TwoRuleStreamProcessor here
}
```

**Issue:** Agent columns call with `isTyping: true`, creating empty bubble. Then `handleAgentStreamEvent()` tries to fill it, but:
- No separate bubbles for different event types
- Processor may be double-initialized
- Inconsistent with Prime's approach

---

## Root Cause Analysis

### Why Agent Columns Fail

1. **Architectural Mismatch:**
   - Agent columns use `UnifiedMessageRenderer` for initial message
   - Prime creates bubbles **inline** during streaming
   - Agent's `handleAgentStreamEvent()` doesn't create new bubbles
   
2. **Incomplete Event Handling:**
   - `handleAgentStreamEvent()` only handles `content_block_delta` (text)
   - Ignores `thinking_block`, `tool_use`, `tool_result`
   - All content goes into ONE bubble instead of separate bubbles
   
3. **Processor Confusion:**
   - `UnifiedMessageRenderer` initializes processor on content div
   - `handleAgentStreamEvent()` tries to initialize on bubble element
   - Duplicate/conflicting initialization
   
4. **CSS Not Applied:**
   - No `.thinking-bubble`, `.tool-bubble` classes during streaming
   - Generic `.ai-message.assistant` used for everything
   - No visual differentiation of event types

---

## Solution: Two Approaches

### Option 1: Make Agent Columns Match Prime (RECOMMENDED)

**Replace `handleAgentStreamEvent()` with Prime's approach:**

1. **Remove** `UnifiedMessageRenderer.render()` call for AI response
2. **Add** inline bubble creation in streaming handler (like Prime)
3. **Handle** all event types:
   - `thinking_block` → Create thinking-bubble
   - `tool_use` → Create tool-bubble
   - `tool_result` → Create tool-result-bubble
   - `content_block_delta` → Create text-bubble
4. **Initialize** TwoRuleStreamProcessor per bubble
5. **Apply** proper CSS classes

**Code changes needed:**
- `agent-js.js` lines 2857-2865: Remove `UnifiedMessageRenderer` call
- `agent-js.js` lines 3862-3928: Replace with Prime's streaming logic
- Copy Prime's bubble creation code (lines 816-1300)

**Estimated effort:** 3-4 hours

---

### Option 2: Enhance UnifiedMessageRenderer (COMPLEX)

**Make `UnifiedMessageRenderer` handle streaming events:**

1. Add `renderStreamingEvent(container, eventType, data, options)` method
2. Create separate bubbles based on event type
3. Maintain bubble references for updates
4. Initialize processors correctly

**Code changes needed:**
- `message_renderer.js`: Add 200+ lines for event-based rendering
- `agent-js.js`: Call `UnifiedMessageRenderer.renderStreamingEvent()`
- Test both Prime and Agent columns

**Estimated effort:** 6-8 hours

**Problem:** Prime already works perfectly. Why change it?

---

## Recommendation

**✅ Option 1: Make Agent Columns Match Prime**

**Reasoning:**
1. Prime's code is proven to work correctly
2. No need to complicate `UnifiedMessageRenderer`
3. Consistent architecture across all columns
4. Easier to maintain (single pattern)
5. All visual features work (thinking, tools, viz)

**Implementation Plan:**

### Step 1: Update agent-js.js sendAgentMessage()
```javascript
// REMOVE this:
const aiMessageDiv = UnifiedMessageRenderer.render(
    `#agent-messages-${agentId}`,
    'assistant',
    '',
    { isTyping: true }
);

// REPLACE with typing indicator (optional):
// (Will be removed when first content arrives)
```

### Step 2: Replace handleAgentStreamEvent()
```javascript
// Copy Prime's streaming logic (lines 772-1300)
// Adapt for agent columns:
// - Change `chatMessages` to `agentMessages-${agentId}`
// - Change `fullResponse` to agent-specific variable
// - Keep same bubble creation code
```

### Step 3: Test all event types
- Thinking block display
- Tool use display
- Tool result display
- Text streaming with TwoRuleStreamProcessor
- Plotly charts
- Mermaid diagrams

---

## Code Examples

### Current Agent Code (WRONG)

**File:** `agent-js.js` lines 2857-2865
```javascript
// ❌ WRONG: Creates generic bubble that doesn't match event structure
const aiMessageDiv = UnifiedMessageRenderer.render(
    `#agent-messages-${agentId}`,
    'assistant',
    '',
    { 
        threadId: currentThread.id,
        syncToBackend: false,
        isTyping: true  // Creates empty content div
    }
);
```

**File:** `agent-js.js` lines 3888-3910
```javascript
// ❌ INCOMPLETE: Only handles text, ignores thinking/tools
if (data.type === 'content_block_delta') {
    if (data.delta_type === 'text_delta') {
        const text = data.text || '';
        const _agentProc = bubble._twoRuleProcessor;
        if (_agentProc && bubble.dataset.processorInitialized === 'true') {
            _agentProc.processChunk(text);
        }
    }
}
// No handling for thinking_block, tool_use, tool_result!
```

---

### Proposed Agent Code (CORRECT - Based on Prime)

**File:** `agent-js.js` - New streaming handler (replaces handleAgentStreamEvent)
```javascript
async function handleAgentStream(agentId, reader) {
    const container = document.getElementById(`agent-messages-${agentId}`);
    const decoder = new TextDecoder();
    let buffer = '';
    
    let fullResponse = '';
    let thinkingBubble = null;
    let textBubble = null;
    let firstContentReceived = false;
    
    while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        buffer += decoder.decode(value, { stream: true });
        const messages = buffer.split('\n\n');
        buffer = messages.pop() || '';
        
        for (const message of messages) {
            const lines = message.split('\n');
            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const jsonStr = line.substring(6).trim();
                    if (!jsonStr) continue;
                    
                    const data = JSON.parse(jsonStr);
                    
                    // THINKING BLOCK
                    if (data.type === 'thinking_block' || data.type === 'thinking') {
                        if (!thinkingBubble) {
                            thinkingBubble = document.createElement('div');
                            thinkingBubble.className = 'ai-message assistant thinking-bubble collapsed';
                            
                            // Create full header structure (same as Prime)
                            const headerDiv = createAgentMessageHeader('thinking', thinkingBubble);
                            
                            const contentDiv = document.createElement('div');
                            contentDiv.className = 'ai-message-content';
                            
                            thinkingBubble.appendChild(headerDiv);
                            thinkingBubble.appendChild(contentDiv);
                            container.appendChild(thinkingBubble);
                            
                            thinkingBubble._fullThinkingText = '';
                        }
                        
                        // Update thinking content
                        const thinkingText = data.content || '';
                        thinkingBubble._fullThinkingText += thinkingText;
                        
                        const contentDiv = thinkingBubble.querySelector('.ai-message-content');
                        if (window.marked) {
                            contentDiv.innerHTML = marked.parse(thinkingBubble._fullThinkingText);
                        } else {
                            contentDiv.textContent = thinkingBubble._fullThinkingText;
                        }
                    }
                    
                    // TOOL USE
                    else if (data.type === 'tool_use') {
                        const toolBubble = document.createElement('div');
                        toolBubble.className = 'ai-message assistant tool-bubble collapsed';
                        toolBubble.setAttribute('data-tool-id', data.tool_id || data.id);
                        
                        const headerDiv = createAgentMessageHeader('tool', toolBubble);
                        
                        const contentDiv = document.createElement('div');
                        contentDiv.className = 'ai-message-content';
                        contentDiv.innerHTML = `
                            <div><strong>Tool:</strong> ${data.name || data.tool_name}</div>
                            <pre>${JSON.stringify(data.input || data.tool_input, null, 2)}</pre>
                        `;
                        
                        toolBubble.appendChild(headerDiv);
                        toolBubble.appendChild(contentDiv);
                        container.appendChild(toolBubble);
                    }
                    
                    // TEXT DELTA
                    else if (data.type === 'content_block_delta' && data.delta_type === 'text_delta') {
                        if (!textBubble) {
                            textBubble = document.createElement('div');
                            textBubble.className = 'ai-message assistant text-bubble';
                            
                            const headerDiv = createAgentMessageHeader('text', textBubble);
                            
                            const contentDiv = document.createElement('div');
                            contentDiv.className = 'ai-message-content';
                            
                            textBubble.appendChild(headerDiv);
                            textBubble.appendChild(contentDiv);
                            container.appendChild(textBubble);
                            
                            // Initialize TwoRuleStreamProcessor
                            if (typeof TwoRuleStreamProcessor !== 'undefined') {
                                const _proc = new TwoRuleStreamProcessor(contentDiv);
                                textBubble._twoRuleProcessor = _proc;
                            }
                        }
                        
                        fullResponse += data.text;
                        
                        // Process chunk with TwoRuleStreamProcessor
                        const _processor = textBubble._twoRuleProcessor;
                        if (_processor && typeof _processor.processChunk === 'function') {
                            _processor.processChunk(data.text);
                        } else {
                            const contentDiv = textBubble.querySelector('.ai-message-content');
                            if (window.marked) {
                                contentDiv.innerHTML = marked.parse(fullResponse);
                            } else {
                                contentDiv.textContent = fullResponse;
                            }
                        }
                    }
                    
                    // DONE
                    else if (data.type === 'done') {
                        if (textBubble && textBubble._twoRuleProcessor) {
                            if (typeof textBubble._twoRuleProcessor.finalize === 'function') {
                                textBubble._twoRuleProcessor.finalize();
                            }
                        }
                    }
                }
            }
        }
    }
}

// Helper function to create message headers (same structure for all bubbles)
function createAgentMessageHeader(type, bubble) {
    const headerDiv = document.createElement('div');
    headerDiv.className = 'ai-message-header';
    
    const avatar = document.createElement('div');
    avatar.className = 'ai-message-avatar';
    
    if (type === 'thinking') {
        avatar.style.background = '#8b5cf6';
        avatar.innerHTML = '<i class="fa-solid fa-brain" style="color: white;"></i>';
    } else if (type === 'tool') {
        avatar.style.background = '#eab308';
        avatar.innerHTML = '<i class="fas fa-cog" style="color: white;"></i>';
    } else {
        avatar.innerHTML = '<i class="fa-solid fa-atom"></i>';
    }
    
    const toggleBtn = document.createElement('button');
    toggleBtn.className = 'ai-message-toggle';
    toggleBtn.innerHTML = '<i class="fas fa-chevron-down"></i>';
    toggleBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        bubble.classList.toggle('collapsed');
    });
    
    headerDiv.appendChild(avatar);
    headerDiv.appendChild(toggleBtn);
    
    const actionsDiv = document.createElement('div');
    actionsDiv.className = 'ai-message-actions';
    
    const copyBtn = document.createElement('button');
    copyBtn.className = 'ai-message-copy-btn';
    copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
    copyBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        const content = bubble.querySelector('.ai-message-content').textContent;
        navigator.clipboard.writeText(content).then(() => {
            copyBtn.innerHTML = '<i class="fas fa-check"></i>';
            setTimeout(() => { copyBtn.innerHTML = '<i class="fas fa-copy"></i>'; }, 2000);
        });
    });
    
    actionsDiv.appendChild(copyBtn);
    headerDiv.appendChild(actionsDiv);
    
    return headerDiv;
}
```

---

## Testing Checklist

After implementing Option 1, verify:

- [ ] **Thinking blocks display** with purple brain icon
- [ ] **Thinking blocks collapse/expand** on click
- [ ] **Tool use blocks display** with yellow cog icon
- [ ] **Tool input shows formatted JSON**
- [ ] **Tool result blocks display** with results
- [ ] **Text responses stream correctly**
- [ ] **TwoRuleStreamProcessor renders:**
  - [ ] Plotly charts (interactive)
  - [ ] Mermaid diagrams
  - [ ] Code blocks with syntax highlighting
  - [ ] Tables
  - [ ] Lists and markdown
- [ ] **Copy buttons work** (rendered + raw)
- [ ] **Multiple agent columns work** (agent-1, agent-2, etc.)
- [ ] **Message persistence** (reload preserves structure)
- [ ] **Performance** (no memory leaks)

---

## Performance Considerations

### Current Issue

**Agent columns leak TwoRuleStreamProcessor instances:**
```javascript
// agent-js.js line 3874
if (window._twoRuleProcessors.size > 50) {
    console.warn(`[PERFORMANCE] ${window._twoRuleProcessors.size} active TwoRule processors`);
}
```

**Root cause:** Creating processors on wrong element, not cleaning up properly.

### Solution

**Proper cleanup after finalize:**
```javascript
if (data.type === 'done') {
    if (textBubble && textBubble._twoRuleProcessor) {
        textBubble._twoRuleProcessor.finalize();
        
        // Cleanup processor reference
        if (window._twoRuleProcessors) {
            window._twoRuleProcessors.delete(textBubble._twoRuleProcessor);
        }
        
        textBubble._twoRuleProcessor = null;
    }
}
```

---

## Summary

**Current State:**
- ✅ AI Prime: Perfect rendering with all event types
- ❌ Agent Columns: Only text renders, no thinking/tools

**Root Cause:**
- Agent columns use `UnifiedMessageRenderer` for initial message
- Stream handler (`handleAgentStreamEvent`) only processes text
- No inline bubble creation like Prime
- Missing event type handlers

**Solution:**
- Copy Prime's streaming logic to agent columns
- Create separate bubbles for each event type
- Initialize TwoRuleStreamProcessor correctly per bubble
- Remove reliance on `UnifiedMessageRenderer` for streaming

**Effort:** 3-4 hours

**Result:** Agent columns will match Prime's visual quality with thinking blocks, tool displays, and proper visualization rendering.

---

**Last Updated:** November 23, 2025  
**Status:** Analysis Complete - Ready for Implementation
