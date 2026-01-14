# Multi-Agent Unified Streaming & Rendering Implementation

**Date:** November 4, 2025  
**Status:** 🚧 In Progress

---

## 🎯 **Goal**

Connect multi-agent columns to use the **same streaming and rendering pathway** as Prime chat panel, enabling:
- ✅ Thinking blocks visualization
- ✅ Tool call rendering with collapsible sections
- ✅ Markdown formatting
- ✅ Character-by-character text streaming
- ✅ Mermaid diagrams
- ✅ Code syntax highlighting
- ✅ All visualisation_copy.js features

---

## 📊 **Current State**

### **Prime Chat Panel (AI Chat):**
```javascript
// ✅ Uses full SSE streaming pipeline
POST /api/agent/agent/1/start → GET /api/agent/stream/1
  ↓
SSE Events:
  - thinking_block → Creates thinking bubble
  - tool_use → Creates tool call bubble
  - text → Character-by-character in text bubble
  - complete → Finalizes
  ↓
Renders via inline handlers in business-ai-platform-v2.html
```

###  **Multi-Agent Columns (Alpha-1, Bravo-2, Charlie-3):**
```javascript
// ❌ Uses basic streaming (no rich rendering)
POST /api/agent/agent/2/start → GET /api/agent/stream/2
  ↓
SSE Events received but not properly handled
  ↓
Uses addAgentMessage() - basic text only
  ↓
NO thinking blocks, NO tool calls, NO markdown
```

---

## 🔧 **Solution Architecture**

### **Create Universal SSE Stream Handler**

```javascript
/**
 * Universal SSE Stream Handler
 * Works for BOTH Prime and Multi-Agent columns
 */
async function handleUniversalStream(agentId, sessionId, containerId) {
    const streamUrl = `${API_BASE_URL}/api/agent/stream/${agentId}?session_id=${sessionId}`;
    const response = await fetch(streamUrl);
    
    if (!response.ok) {
        throw new Error(`Stream error! status: ${response.status}`);
    }
    
    // Get container (different for Prime vs columns)
    const container = document.getElementById(containerId);
    if (!container) {
        throw new Error(`Container ${containerId} not found`);
    }
    
    // Tracking variables
    let thinkingBubble = null;
    let textBubble = null;
    let toolBubbles = [];
    let fullResponse = '';
    
    // SSE Reader
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    
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
                    const data = JSON.parse(line.substring(6).trim());
                    
                    // Handle different event types
                    switch (data.type) {
                        case 'thinking':
                        case 'thinking_block':
                            thinkingBubble = handleThinkingEvent(data, container, thinkingBubble);
                            break;
                            
                        case 'tool_use':
                            const toolBubble = handleToolEvent(data, container);
                            toolBubbles.push(toolBubble);
                            break;
                            
                        case 'tool_result':
                            handleToolResultEvent(data, toolBubbles);
                            break;
                            
                        case 'text':
                            textBubble = handleTextEvent(data, container, textBubble);
                            fullResponse += data.content || '';
                            break;
                            
                        case 'complete':
                            handleCompleteEvent(container, thinkingBubble);
                            return { fullResponse, toolBubbles, thinkingBubble };
                            
                        case 'error':
                            handleErrorEvent(data, container);
                            throw new Error(data.error || 'Stream error');
                    }
                }
            }
        }
    }
}

/**
 * Handle thinking block events
 */
function handleThinkingEvent(data, container, existingBubble) {
    const thinkingText = data.content || data.thinking || '';
    if (!thinkingText.trim()) return existingBubble;
    
    if (!existingBubble) {
        // Create new thinking bubble
        existingBubble = document.createElement('div');
        existingBubble.className = 'ai-thinking-bubble';
        existingBubble.innerHTML = `
            <div class="thinking-header">
                <span class="thinking-icon">🧠</span>
                <span class="thinking-label">AI Thinking...</span>
                <button class="thinking-toggle" onclick="this.closest('.ai-thinking-bubble').classList.toggle('collapsed')">
                    <i class="fas fa-chevron-down"></i>
                </button>
            </div>
            <div class="thinking-content"></div>
        `;
        container.appendChild(existingBubble);
    }
    
    // Append thinking content
    const thinkingContent = existingBubble.querySelector('.thinking-content');
    thinkingContent.textContent += thinkingText;
    
    // Scroll to bottom
    container.scrollTop = container.scrollHeight;
    
    return existingBubble;
}

/**
 * Handle tool use events
 */
function handleToolEvent(data, container) {
    const toolBubble = document.createElement('div');
    toolBubble.className = 'tool-use-bubble';
    toolBubble.dataset.toolId = data.tool_use_id;
    toolBubble.innerHTML = `
        <div class="tool-header">
            <span class="tool-icon">🔧</span>
            <span class="tool-name">${data.tool_name}</span>
            <span class="tool-status pending">⏳ Running...</span>
            <button class="tool-toggle" onclick="this.closest('.tool-use-bubble').classList.toggle('collapsed')">
                <i class="fas fa-chevron-down"></i>
            </button>
        </div>
        <div class="tool-input">
            <strong>Input:</strong>
            <pre>${JSON.stringify(data.tool_input, null, 2)}</pre>
        </div>
        <div class="tool-output" style="display:none;">
            <strong>Output:</strong>
            <div class="tool-output-content"></div>
        </div>
    `;
    
    container.appendChild(toolBubble);
    container.scrollTop = container.scrollHeight;
    
    return toolBubble;
}

/**
 * Handle tool result events
 */
function handleToolResultEvent(data, toolBubbles) {
    const toolBubble = toolBubbles.find(b => 
        b.dataset.toolId === data.tool_use_id
    );
    
    if (toolBubble) {
        const status = toolBubble.querySelector('.tool-status');
        const outputDiv = toolBubble.querySelector('.tool-output');
        const outputContent = toolBubble.querySelector('.tool-output-content');
        
        if (data.is_error) {
            status.className = 'tool-status error';
            status.textContent = '❌ Error';
            outputContent.textContent = data.content || 'Unknown error';
        } else {
            status.className = 'tool-status success';
            status.textContent = '✅ Complete';
            outputContent.textContent = data.content || 'Success';
        }
        
        outputDiv.style.display = 'block';
    }
}

/**
 * Handle text streaming events
 */
function handleTextEvent(data, container, existingBubble) {
    const textContent = data.content || data.text || '';
    if (!textContent) return existingBubble;
    
    if (!existingBubble) {
        // Create new text bubble
        existingBubble = document.createElement('div');
        existingBubble.className = 'ai-text-bubble';
        existingBubble.innerHTML = '<div class="text-content"></div>';
        container.appendChild(existingBubble);
    }
    
    // Append text (character-by-character streaming effect)
    const textDiv = existingBubble.querySelector('.text-content');
    textDiv.textContent += textContent;
    
    // Apply markdown rendering (if visualisation_copy.js loaded)
    if (typeof renderMarkdown === 'function') {
        textDiv.innerHTML = renderMarkdown(textDiv.textContent);
    }
    
    // Scroll to bottom
    container.scrollTop = container.scrollHeight;
    
    return existingBubble;
}

/**
 * Handle stream completion
 */
function handleCompleteEvent(container, thinkingBubble) {
    // Collapse thinking bubble on completion
    if (thinkingBubble) {
        thinkingBubble.classList.add('collapsed');
        const label = thinkingBubble.querySelector('.thinking-label');
        if (label) label.textContent = 'Thinking Complete';
    }
    
    console.log('✅ Stream complete');
}

/**
 * Handle error events
 */
function handleErrorEvent(data, container) {
    const errorBubble = document.createElement('div');
    errorBubble.className = 'ai-error-bubble';
    errorBubble.innerHTML = `
        <div class="error-icon">❌</div>
        <div class="error-message">${data.error || 'Unknown error occurred'}</div>
    `;
    container.appendChild(errorBubble);
    console.error('❌ Stream error:', data.error);
}
```

---

## 🎨 **CSS Styles Needed**

```css
/* Thinking Bubble */
.ai-thinking-bubble {
    background: rgba(59, 130, 246, 0.1);
    border: 1px solid rgba(59, 130, 246, 0.3);
    border-radius: 8px;
    padding: 12px;
    margin: 8px 0;
    transition: max-height 0.3s ease;
}

.ai-thinking-bubble.collapsed .thinking-content {
    display: none;
}

.thinking-header {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 600;
    color: #3b82f6;
}

.thinking-toggle {
    margin-left: auto;
    background: transparent;
    border: none;
    cursor: pointer;
    color: #3b82f6;
}

.thinking-content {
    margin-top: 8px;
    padding: 8px;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 4px;
    font-family: monospace;
    font-size: 12px;
    white-space: pre-wrap;
    color: rgba(255, 255, 255, 0.8);
}

/* Tool Use Bubble */
.tool-use-bubble {
    background: rgba(34, 197, 94, 0.1);
    border: 1px solid rgba(34, 197, 94, 0.3);
    border-radius: 8px;
    padding: 12px;
    margin: 8px 0;
}

.tool-header {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 600;
}

.tool-name {
    color: #22c55e;
    font-family: monospace;
}

.tool-status {
    margin-left: auto;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
}

.tool-status.pending {
    background: rgba(234, 179, 8, 0.2);
    color: #eab308;
}

.tool-status.success {
    background: rgba(34, 197, 94, 0.2);
    color: #22c55e;
}

.tool-status.error {
    background: rgba(239, 68, 68, 0.2);
    color: #ef4444;
}

/* Text Bubble */
.ai-text-bubble {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    padding: 12px;
    margin: 8px 0;
    color: #ffffff;
}

.text-content {
    line-height: 1.6;
}

/* Error Bubble */
.ai-error-bubble {
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.3);
    border-radius: 8px;
    padding: 12px;
    margin: 8px 0;
    display: flex;
    align-items: center;
    gap: 8px;
}

.error-icon {
    font-size: 20px;
}

.error-message {
    color: #ef4444;
    flex: 1;
}
```

---

## 🔄 **Integration Steps**

### **Step 1: Add Universal Handler to HTML**

Insert before closing `</script>` tag in business-ai-platform-v2.html:

```javascript
// ==================== UNIVERSAL SSE STREAM HANDLER ====================
// (Insert handleUniversalStream function here)
```

### **Step 2: Update sendAgentMessage() for Multi-Agent**

Replace current streaming in `sendAgentMessage()`:

```javascript
async function sendAgentMessage(agentId) {
    // ... existing code ...
    
    try {
        // Start agent
        const response = await fetch(`${API_BASE_URL}/api/agent/agent/${agentId}/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                session_id: sessionId,
                conversation_history: conversationHistory
            })
        });
        
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        // Use universal stream handler
        updateAgentStatus(agentId, 'working', 'Responding...');
        
        const result = await handleUniversalStream(
            agentId,
            sessionId,
            `messages-${agentId}`  // Container ID for this agent
        );
        
        // Save to thread
        const agentName = getAgentName(agentId);
        const thread = ThreadManager.getThreadByAgent(agentName);
        if (thread) {
            thread.messages.push({
                role: 'user',
                content: message
            });
            thread.messages.push({
                role: 'assistant',
                content: result.fullResponse
            });
            ThreadManager.saveThreads();
        }
        
        updateAgentStatus(agentId, 'ready', 'Ready');
        
    } catch (error) {
        console.error(`[Agent ${agentId}] Error:`, error);
        updateAgentStatus(agentId, 'error', error.message);
    }
}
```

### **Step 3: Update sendChatMessage() for Prime**

Replace Prime streaming code with universal handler:

```javascript
// In sendChatMessage() around line 7640
// REPLACE existing SSE handling with:
const result = await handleUniversalStream(
    '1',  // Prime uses agent_id = '1'
    sessionId,
    'ai-chat-messages'  // Prime container ID
);

// Save to history
AppState.chatMessages.push({
    role: 'assistant',
    content: result.fullResponse,
    timestamp: new Date().toISOString()
});
```

---

## ✅ **Expected Results**

### **After Implementation:**

**Multi-Agent Columns will show:**
- ✅ 🧠 Thinking blocks (collapsible)
- ✅ 🔧 Tool calls with input/output (collapsible)
- ✅ ✨ Character-by-character text streaming
- ✅ 📝 Markdown formatting (bold, italic, lists, code)
- ✅ 📊 Mermaid diagrams (if in response)
- ✅ 💻 Code syntax highlighting
- ✅ ❌ Error bubbles

**Identical to Prime chat panel!**

---

## 🧪 **Testing Checklist**

After implementation:

- [ ] Send message in Alpha-1 → See thinking block appear
- [ ] Request tool use → See tool call bubble with status
- [ ] Verify text streams character-by-character
- [ ] Check markdown renders (try `**bold**`, `*italic*`)
- [ ] Try mermaid diagram (request flowchart)
- [ ] Verify tool calls show input/output correctly
- [ ] Check thinking block collapses on complete
- [ ] Test error handling (send invalid request)
- [ ] Compare Alpha-1 rendering to Prime → Should be identical

---

## 📊 **Architecture Diagram**

```
┌─────────────────────────────────────────────────────────────┐
│                    USER SENDS MESSAGE                        │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┴───────────────┐
        │                               │
┌───────▼────────┐            ┌─────────▼────────┐
│  PRIME (AI-1)  │            │ BRAVO-2 (Agent-2)│
│  Container:    │            │  Container:       │
│  ai-chat-msgs  │            │  messages-2       │
└───────┬────────┘            └─────────┬────────┘
        │                               │
        └───────────────┬───────────────┘
                        │
            ┌───────────▼───────────┐
            │ handleUniversalStream()│
            │  Unified SSE Handler  │
            └───────────┬───────────┘
                        │
        ┌───────────────┴───────────────┐
        │                               │
┌───────▼────────┐            ┌─────────▼────────┐
│ Backend Stream │            │   Event Router   │
│ /api/agent/    │────────────▶  thinking → 🧠   │
│ stream/{id}    │            │  tool_use → 🔧   │
└────────────────┘            │  text → ✨       │
                              │  complete → ✅    │
                              └──────────┬────────┘
                                         │
                              ┌──────────▼──────────┐
                              │  Render to Container│
                              │  (Prime or Column)  │
                              └─────────────────────┘
```

---

## 🎯 **Benefits**

1. **Code Reuse:** One streaming handler for both Prime and columns
2. **Consistency:** Identical UX across all chat interfaces
3. **Maintainability:** Fix/enhance in one place, applies everywhere
4. **Feature Parity:** Multi-agent gets ALL Prime features instantly
5. **Future-Proof:** New streaming features automatically work in columns

---

## 📝 **Implementation Files**

- `UI/business-ai-platform-v2.html` - Add universal handler + update sendAgentMessage()
- `UI/visualisation_engine/visualisation_copy.js` - Already has rendering functions (no changes needed)

**Status:** 🚧 Ready to implement - All architecture defined!
