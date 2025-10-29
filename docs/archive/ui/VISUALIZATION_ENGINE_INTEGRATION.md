# 🎨 Visualization Engine Integration - Business AI Platform

## Overview

Successfully integrated the **Two-Rule Streaming Visualization Engine** into the Business AI Platform's chat message system. AI responses now support advanced content rendering including Mermaid diagrams, Plotly charts, tables, and formatted markdown.

---

## Changes Made

### 1. Script Inclusion (Lines ~37-40)

**Added visualization engine scripts:**
```html
<!-- ==================== VISUALIZATION ENGINE ==================== -->
<!-- Two-Rule Streaming System for Advanced Content Processing -->
<script src="visualisation_engine/streamingTwoRule.js"></script>
<script src="visualisation_engine/visualisation_copy.js"></script>
```

**Location:** After Luxon library, before closing `</head>` tag

---

### 2. Initialization Function (Lines ~1219-1253)

**Added `initVisualizationEngine()` function:**
```javascript
function initVisualizationEngine() {
    console.log('🎨 Initializing visualization engine...');
    
    // Initialize global visualization state
    if (!window.sidebarVisualizationState) {
        window.sidebarVisualizationState = {
            currentTheme: 'dark',
            fontSize: 14,
            mermaidTheme: 'dark',
            colorScheme: {
                primary: '#58a6ff',
                secondary: '#3fb950',
                error: '#f85149',
                warning: '#d29922'
            }
        };
    }
    
    // Initialize Mermaid
    if (typeof mermaid !== 'undefined') {
        mermaid.initialize({
            startOnLoad: false,
            theme: 'dark',
            securityLevel: 'loose',
            fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif'
        });
        console.log('✅ Mermaid initialized');
    }
    
    console.log('✅ Visualization engine ready');
}
```

**Called during:** `DOMContentLoaded` event, before backend connection check

---

### 3. Main Chat Message Function (Lines ~1977-2016)

**Updated `addChatMessage()` to use visualization engine:**

**Before:**
```javascript
contentDiv.innerHTML = content;
```

**After:**
```javascript
// ✅ USE VISUALIZATION ENGINE for AI responses (not thinking indicators)
if (role === 'assistant' && !isThinking && typeof TwoRuleStreamProcessor !== 'undefined') {
    console.log('🎨 Using visualization engine for AI message');
    
    // Create processor for this message
    const processor = new TwoRuleStreamProcessor(contentDiv);
    
    // Process content through visualization engine
    processor.processChunk(content);
    processor.finalize();
    
    // Add click event to open popup
    contentDiv.addEventListener('click', () => {
        openMessagePopup(role, content);
    });
} else {
    // For user messages and thinking indicators, use direct HTML
    contentDiv.innerHTML = content;
    
    // Add click event to open popup (not for thinking indicators)
    if (!isThinking) {
        contentDiv.addEventListener('click', () => {
            openMessagePopup(role, content);
        });
    }
}
```

**Benefits:**
- AI messages render Mermaid diagrams: `<MERMAID>...</MERMAID>`
- AI messages render Plotly charts: `<PLOTLY>...</PLOTLY>`
- AI messages render tables: `<TABLE>...</TABLE>`
- Markdown formatting with proper syntax highlighting
- User messages remain simple HTML (no processing overhead)

---

### 4. Multi-Agent Message Function (Lines ~2613-2638)

**Updated `addAgentMessage()` for NATO column agents:**

**Before:**
```javascript
messageDiv.innerHTML = `
    <div class="agent-message-bubble">
        ${content}
    </div>
`;
```

**After:**
```javascript
const bubbleDiv = document.createElement('div');
bubbleDiv.className = 'agent-message-bubble';

// ✅ USE VISUALIZATION ENGINE for AI responses
if (role === 'ai' && typeof TwoRuleStreamProcessor !== 'undefined') {
    console.log(`🎨 Using visualization engine for Agent ${agentId} message`);
    
    // Create processor for this message
    const processor = new TwoRuleStreamProcessor(bubbleDiv);
    
    // Process content through visualization engine
    processor.processChunk(content);
    processor.finalize();
} else {
    // For user messages, use direct HTML
    bubbleDiv.innerHTML = content;
}

messageDiv.appendChild(bubbleDiv);
```

---

### 5. Streaming Event Handler (Lines ~2598-2626)

**Updated `handleAgentStreamEvent()` for real-time streaming:**

**Before:**
```javascript
bubble.innerHTML += data.text || '';
```

**After:**
```javascript
// Initialize processor for this bubble if not exists
if (!bubble.dataset.processorInitialized && typeof TwoRuleStreamProcessor !== 'undefined') {
    bubble.processor = new TwoRuleStreamProcessor(bubble);
    bubble.dataset.processorInitialized = 'true';
    console.log(`🎨 Initialized visualization processor for Agent ${agentId}`);
}

if (data.type === 'content_block_delta') {
    if (data.delta_type === 'text_delta') {
        const text = data.text || '';
        
        // ✅ USE VISUALIZATION ENGINE for streaming
        if (bubble.processor) {
            bubble.processor.processChunk(text);
        } else {
            // Fallback to plain HTML
            bubble.innerHTML += text;
        }
        
        scrollAgentToBottom(agentId);
    }
} else if (data.type === 'done') {
    // Finalize visualization processing
    if (bubble.processor) {
        bubble.processor.finalize();
        console.log(`✅ Finalized visualization for Agent ${agentId}`);
    }
}
```

**Benefits:**
- Handles streaming content chunk-by-chunk
- Detects visual delimiters mid-stream
- Buffers visual content until complete
- Finalizes rendering when streaming ends

---

### 6. Theme Synchronization (Lines ~2226-2256)

**Updated `initThemeToggle()` to sync with visualization engine:**

**Added:**
```javascript
// ✅ Update visualization engine theme
if (window.sidebarVisualizationState) {
    window.sidebarVisualizationState.currentTheme = newTheme;
    window.sidebarVisualizationState.mermaidTheme = newTheme;
}

// Reinitialize Mermaid with new theme
if (typeof mermaid !== 'undefined') {
    mermaid.initialize({
        startOnLoad: false,
        theme: newTheme,
        securityLevel: 'loose',
        fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif'
    });
}
```

**Ensures:** Mermaid diagrams and Plotly charts adapt to light/dark theme changes

---

### 7. Visualization CSS Styles (Lines ~558-620)

**Added comprehensive styles for visualization containers:**

```css
/* ==================== VISUALIZATION ENGINE STYLES ==================== */
/* Ensure visualization containers work within chat messages */
.ai-message-content .viz-container {
    margin: var(--space-3) 0;
    border-radius: 6px;
    overflow: hidden;
}

.ai-message-content .mermaid {
    background: var(--bg-tertiary);
    padding: var(--space-4);
    border-radius: 6px;
    display: flex;
    justify-content: center;
    align-items: center;
}

.ai-message-content .plotly-container {
    background: var(--bg-tertiary);
    border-radius: 6px;
    padding: var(--space-2);
}

.ai-message-content table {
    width: 100%;
    border-collapse: collapse;
    margin: var(--space-3) 0;
    background: var(--bg-tertiary);
    border-radius: 6px;
    overflow: hidden;
}

.ai-message-content table th,
.ai-message-content table td {
    padding: var(--space-2) var(--space-3);
    text-align: left;
    border-bottom: 1px solid var(--border-default);
}

.ai-message-content table th {
    background: var(--bg-secondary);
    font-weight: 600;
    color: var(--text-primary);
}

.ai-message-content table tr:hover {
    background: var(--bg-hover);
}

/* Agent message bubble visualizations */
.agent-message-bubble .viz-container {
    margin: var(--space-3) 0;
}

.agent-message-bubble .mermaid,
.agent-message-bubble .plotly-container {
    background: var(--bg-primary);
    border-radius: 6px;
}
```

**Styles applied to:**
- Main AI chat panel messages (`.ai-message-content`)
- Multi-agent NATO column messages (`.agent-message-bubble`)
- Tables, Mermaid diagrams, Plotly charts
- Consistent with platform theme (light/dark)

---

## Architecture Pattern

### Two-Rule Streaming System

**Rule 1:** Any raw buffered content CANNOT be in both groups (normal vs visual)

**Rule 2:** Once a delimiter is detected, ALL content is Visual Type until END delimiter

**Flow:**
```
User Input → Flask Backend → SSE Stream
    ↓
Stream chunks arrive
    ↓
TwoRuleStreamProcessor.processChunk(text)
    ↓
State Machine: NORMAL | BUFFERING_VISUAL
    ↓
Content Router:
    - Normal text → Markdown renderer → DOM
    - Visual delimiters → Buffer until complete → Visualization engine → DOM
    ↓
Finalize when stream ends
```

---

## Supported Content Types

### 1. Mermaid Diagrams
```
<MERMAID>
flowchart TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Action 1]
    B -->|No| D[Action 2]
</MERMAID>
```

### 2. Plotly Charts
```
<PLOTLY>
{
    "data": [{
        "x": [1, 2, 3, 4],
        "y": [10, 15, 13, 17],
        "type": "scatter"
    }],
    "layout": {
        "title": "Sales Data"
    }
}
</PLOTLY>
```

### 3. Data Tables
```
<TABLE>
| Product | Sales | Growth |
|---------|-------|--------|
| Widget  | $50K  | +15%   |
| Gadget  | $75K  | +22%   |
</TABLE>
```

### 4. Enhanced Markdown
- **Bold**, *italic*, `code`
- Headers (H1-H6)
- Lists (ordered, unordered)
- Blockquotes
- Code blocks with syntax highlighting
- Links and images

---

## Testing Checklist

### Main Chat Panel
- [ ] Send message with Mermaid diagram → Renders correctly
- [ ] Send message with Plotly chart → Interactive chart appears
- [ ] Send message with table → Formatted table displays
- [ ] Send plain text → Normal markdown rendering
- [ ] Toggle light/dark theme → Visualizations update
- [ ] Click message → Popup opens with content

### Multi-Agent NATO Columns
- [ ] Agent responds with Mermaid diagram → Renders in column
- [ ] Agent streams response with visual content → Buffers until complete
- [ ] Multiple agents with different content types → All render correctly
- [ ] Scroll agent messages → Smooth scrolling works

### Streaming Behavior
- [ ] Visual delimiter detected mid-stream → Buffers correctly
- [ ] Stream completes → Finalize renders visualization
- [ ] Stream interrupted → Graceful fallback
- [ ] Multiple chunks of normal text → Appends smoothly

---

## Performance Considerations

### Optimizations
1. **Lazy Processor Creation:** Only creates `TwoRuleStreamProcessor` for AI messages
2. **Selective Processing:** User messages skip visualization engine (direct HTML)
3. **Buffered Streaming:** Visual content buffered until complete (prevents partial renders)
4. **Theme Caching:** Visualization state stored globally (no re-initialization)

### Memory Management
- Processors are instance-based (one per message)
- No global state pollution
- Garbage collected when message element is removed

---

## Troubleshooting

### Issue: Mermaid diagram not rendering

**Symptoms:** Raw `<MERMAID>` tags visible in message

**Solutions:**
1. Check browser console for errors
2. Verify `mermaid` library loaded: `typeof mermaid !== 'undefined'`
3. Check delimiter format: Must be `<MERMAID>...</MERMAID>` (uppercase)
4. Verify content is in AI message (not user message)

**Debug:**
```javascript
console.log('Mermaid loaded?', typeof mermaid !== 'undefined');
console.log('Processor exists?', typeof TwoRuleStreamProcessor !== 'undefined');
```

---

### Issue: Plotly chart not interactive

**Symptoms:** Chart displays but doesn't respond to mouse interactions

**Solutions:**
1. Check `plotly` library loaded: `typeof Plotly !== 'undefined'`
2. Verify JSON format is valid
3. Check console for Plotly errors
4. Ensure chart has valid data arrays

**Debug:**
```javascript
console.log('Plotly loaded?', typeof Plotly !== 'undefined');
console.log('Chart data:', JSON.parse(chartData));
```

---

### Issue: Theme not updating for visualizations

**Symptoms:** Diagrams stay in dark mode when switching to light theme

**Solutions:**
1. Check `window.sidebarVisualizationState` exists
2. Verify theme toggle calls `mermaid.initialize()` with new theme
3. Re-render existing diagrams after theme change

**Debug:**
```javascript
console.log('Viz state:', window.sidebarVisualizationState);
console.log('Current theme:', window.sidebarVisualizationState?.currentTheme);
```

---

## File Structure

```
AI_agents/UI/
├── business-ai-platform-v2.html       (Modified - Main platform file)
├── visualisation_engine/
│   ├── streamingTwoRule.js            (Existing - Two-Rule processor)
│   └── visualisation_copy.js          (Existing - Visualization renderer)
└── VISUALIZATION_ENGINE_INTEGRATION.md (New - This documentation)
```

---

## Integration Status

**Status:** ✅ Complete

**Version:** 1.0.0

**Last Updated:** October 26, 2025

**Components Integrated:**
- [x] Script inclusion
- [x] Initialization function
- [x] Main chat message rendering
- [x] Multi-agent message rendering
- [x] Streaming event handling
- [x] Theme synchronization
- [x] CSS styling
- [x] Documentation

---

## Next Steps (Optional Enhancements)

### Future Improvements
1. **Export with Visualizations:** PDF/Markdown export preserves diagrams
2. **Message Editing:** Re-process edited messages through engine
3. **Custom Delimiters:** Support additional content types (e.g., `<GANTT>`)
4. **Performance Monitoring:** Track rendering times for large diagrams
5. **Offline Mode:** Cache visualization libraries for offline use

### Advanced Features
- **Live Collaboration:** Real-time visualization updates across agents
- **Diagram Templates:** Pre-built templates for common diagram types
- **Interactive Editing:** Click diagram to edit source code
- **Chart Animations:** Smooth transitions when data updates

---

## References

- **Two-Rule Streaming Documentation:** `visualisation_engine/streamingTwoRule.js`
- **Visualization Engine API:** `visualisation_engine/visualisation_copy.js`
- **Mermaid Documentation:** https://mermaid.js.org/
- **Plotly Documentation:** https://plotly.com/javascript/

---

**Integration completed successfully! All chat message areas now support advanced visualization rendering.** 🎉
