# AI Agent Integration Guide for Dev-Tools Module

## 🤖 Overview

The **Dev-Tools Module** is currently a **standalone code editor UI** with Monaco Editor integration. To enable **AI code generation**, it needs to be connected to your existing **AI Infrastructure backend** (`AI_infrastructure/flask_app.py`).

---

## 📋 Current Architecture

### **What Exists Now:**

```
dev-tools/
├── module-creator-enhanced.html  ← UI Entry Point
├── dev-tools-module.js          ← Monaco Editor + File Management
├── dev-tools-styles.css         ← Styling (FIXED ✅)
└── dev-tools-plugin.js          ← Auto-plugin system
```

### **What's Missing:**

- ❌ **AI Agent Connection** - No backend API calls to generate code
- ❌ **Streaming Integration** - No real-time AI response display
- ❌ **Tool Execution** - No ability to run tools/calculators
- ❌ **Session Management** - No conversation history tracking

---

## 🔌 Integration Architecture

### **Backend (AI Infrastructure)**

Your Flask backend at `AI_infrastructure/flask_app.py` already has:

✅ **Claude Sonnet 4 Integration** (`/api/agent/stream` endpoint)  
✅ **Tool Registry** (66+ tools via MCP)  
✅ **Session Management** (unified_session_manager)  
✅ **WebSocket Support** (SocketIO)  
✅ **Streaming Responses** (Server-Sent Events)

**Key Endpoint:**
```python
# AI_infrastructure/routes/agent_routes_v4.py (line 2144)
response = ai_client.client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=4096,
    system=system_prompt,
    messages=messages,
    tools=tools,  # 66+ MCP tools available
    stream=True   # Real-time streaming
)
```

### **Frontend (Dev-Tools Module)**

The dev-tools UI needs to:

1. **Send code generation requests** to Flask backend
2. **Stream AI responses** into Monaco Editor
3. **Display thinking/tool usage** in console panel
4. **Update file tabs** as AI writes code

---

## 🛠️ Implementation Plan

### **Step 1: Add AI Service to dev-tools-module.js**

Add a new `AIService` class to handle backend communication:

```javascript
// Add to dev-tools-module.js around line 100

class AIService {
    constructor(apiBase = 'http://localhost:5001') {
        this.apiBase = apiBase;
        this.sessionId = null;
    }

    /**
     * Generate code using AI agent
     * @param {string} prompt - User's code generation request
     * @param {string} moduleType - 'dashboard' | 'sidebar' | 'external'
     * @param {Object} context - Current module configuration
     * @param {Function} onChunk - Callback for streaming chunks
     * @param {Function} onThinking - Callback for thinking blocks
     * @param {Function} onToolUse - Callback for tool execution
     */
    async generateCode(prompt, moduleType, context, { onChunk, onThinking, onToolUse }) {
        const response = await fetch(`${this.apiBase}/api/agent/stream`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'text/event-stream'
            },
            body: JSON.stringify({
                agent_id: 'dev_tools_agent',
                message: this._buildPrompt(prompt, moduleType, context),
                session_id: this.sessionId,
                stream: true,
                enable_thinking: true
            })
        });

        if (!response.ok) {
            throw new Error(`AI request failed: ${response.statusText}`);
        }

        // Read streaming response
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop(); // Keep incomplete line

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = JSON.parse(line.slice(6));
                    
                    if (data.type === 'thinking') {
                        onThinking?.(data.content);
                    } else if (data.type === 'tool_use') {
                        onToolUse?.(data.tool_name, data.tool_input);
                    } else if (data.type === 'text') {
                        onChunk?.(data.content);
                    } else if (data.type === 'session_id') {
                        this.sessionId = data.session_id;
                    }
                }
            }
        }
    }

    _buildPrompt(userPrompt, moduleType, context) {
        return `Create a ${moduleType} module with the following requirements:

${userPrompt}

Current Module Configuration:
- ID: ${context.id}
- Name: ${context.name}
- Type: ${context.type}
- Icon: ${context.icon}
- Description: ${context.description}

Generate complete code for:
1. HTML file (module-${context.id}.html)
2. JavaScript file (module-${context.id}.js)
3. CSS file (module-${context.id}-styles.css)
4. Routes file (module-${context.id}-routes.py)
5. Manifest file (module-${context.id}-manifest.json)

Provide each file's content in a structured format with clear file markers.`;
    }
}
```

### **Step 2: Add AI Button to UI**

Update `_buildWorkspaceUI()` to include AI generation button:

```javascript
// In dev-tools-module.js, around line 400 (header-actions)

<div class="header-actions">
    <button id="ai-generate-btn" class="btn btn-ai" title="Generate with AI">
        <i class="fas fa-magic"></i> AI Generate
    </button>
    <button id="new-module-btn" class="btn btn-primary">
        <i class="fas fa-plus"></i> New
    </button>
    <button id="load-module-btn" class="btn btn-secondary">
        <i class="fas fa-folder-open"></i> Load
    </button>
    <button id="save-module-btn" class="btn btn-success">
        <i class="fas fa-save"></i> Save
    </button>
    <button id="validate-module-btn" class="btn btn-info">
        <i class="fas fa-check-circle"></i> Validate
    </button>
</div>
```

### **Step 3: Add AI Generation Modal**

Create a prompt dialog for AI requests:

```javascript
// Add to dev-tools-module.js

_buildAIPromptModal() {
    return `
        <div id="ai-prompt-modal" class="modal" style="display: none;">
            <div class="modal-content">
                <div class="modal-header">
                    <h3><i class="fas fa-magic"></i> AI Code Generator</h3>
                    <button class="close-modal">&times;</button>
                </div>
                <div class="modal-body">
                    <label for="ai-prompt-input">Describe what you want to build:</label>
                    <textarea 
                        id="ai-prompt-input" 
                        placeholder="Example: Create a user management dashboard with a data table showing users, search functionality, and inline editing capabilities..."
                        rows="8"
                    ></textarea>
                    
                    <div class="ai-options">
                        <label>
                            <input type="checkbox" id="ai-include-context" checked>
                            Include current module configuration
                        </label>
                        <label>
                            <input type="checkbox" id="ai-show-thinking" checked>
                            Show AI thinking process
                        </label>
                    </div>
                </div>
                <div class="modal-footer">
                    <button id="ai-generate-confirm" class="btn btn-primary">
                        <i class="fas fa-magic"></i> Generate
                    </button>
                    <button class="close-modal btn btn-secondary">Cancel</button>
                </div>
            </div>
        </div>
    `;
}
```

### **Step 4: Wire Up Event Handlers**

Connect AI generation to button clicks:

```javascript
// Add to _bindEvents() in dev-tools-module.js

_bindEvents() {
    // ... existing event handlers ...

    // AI Generation Button
    const aiBtn = document.getElementById('ai-generate-btn');
    if (aiBtn) {
        aiBtn.addEventListener('click', () => this._showAIPromptModal());
    }

    // AI Generate Confirm
    document.addEventListener('click', (e) => {
        if (e.target.id === 'ai-generate-confirm') {
            this._handleAIGeneration();
        }
    });
}

async _showAIPromptModal() {
    const modal = document.getElementById('ai-prompt-modal');
    if (!modal) {
        // Append modal to workspace
        this.container.insertAdjacentHTML('beforeend', this._buildAIPromptModal());
    }
    document.getElementById('ai-prompt-modal').style.display = 'flex';
}

async _handleAIGeneration() {
    const prompt = document.getElementById('ai-prompt-input').value.trim();
    if (!prompt) {
        this._logToConsole('⚠️ Please enter a prompt', 'warning');
        return;
    }

    // Close modal
    document.getElementById('ai-prompt-modal').style.display = 'none';

    // Show generating status
    this._logToConsole('🤖 AI generating code...', 'info');

    // Get current module context
    const context = {
        id: this.currentModule?.id || 'generated-module',
        name: this.currentModule?.name || 'Generated Module',
        type: this.currentModule?.type || 'dashboard',
        icon: this.currentModule?.icon || 'fa-code',
        description: this.currentModule?.description || 'AI Generated Module'
    };

    try {
        await this.aiService.generateCode(
            prompt,
            context.type,
            context,
            {
                onChunk: (text) => {
                    // Append to current file in Monaco Editor
                    this._appendToEditor(text);
                },
                onThinking: (thought) => {
                    // Show in console
                    this._logToConsole(`💭 ${thought}`, 'thinking');
                },
                onToolUse: (toolName, toolInput) => {
                    // Show tool execution
                    this._logToConsole(`🔧 Using tool: ${toolName}`, 'tool');
                }
            }
        );

        this._logToConsole('✅ Code generation complete!', 'success');
    } catch (error) {
        this._logToConsole(`❌ AI generation failed: ${error.message}`, 'error');
    }
}

_appendToEditor(text) {
    if (!this.editor) return;
    
    const model = this.editor.getModel();
    const lastLine = model.getLineCount();
    const lastColumn = model.getLineMaxColumn(lastLine);
    
    this.editor.executeEdits('ai-generation', [{
        range: new monaco.Range(lastLine, lastColumn, lastLine, lastColumn),
        text: text
    }]);
}
```

### **Step 5: Add CSS Styling for AI Elements**

Add to `dev-tools-styles.css`:

```css
/* AI Generation Button */
.btn-ai {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    animation: ai-pulse 2s infinite;
}

.btn-ai:hover {
    background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    transform: translateY(-2px);
}

@keyframes ai-pulse {
    0%, 100% {
        box-shadow: 0 0 0 0 rgba(102, 126, 234, 0.7);
    }
    50% {
        box-shadow: 0 0 20px 5px rgba(102, 126, 234, 0.3);
    }
}

/* AI Prompt Modal */
.modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10000;
}

.modal-content {
    background: var(--dev-tools-bg-primary);
    border: 1px solid var(--dev-tools-border);
    border-radius: 12px;
    width: 90%;
    max-width: 600px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px;
    border-bottom: 1px solid var(--dev-tools-border);
}

.modal-body {
    padding: 20px;
}

.modal-body textarea {
    width: 100%;
    padding: 12px;
    border: 1px solid var(--dev-tools-border);
    border-radius: 6px;
    background: var(--dev-tools-bg-secondary);
    color: var(--dev-tools-text-primary);
    font-size: 14px;
    resize: vertical;
    font-family: 'Consolas', 'Monaco', monospace;
}

.ai-options {
    margin-top: 15px;
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.ai-options label {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
    cursor: pointer;
}

.modal-footer {
    padding: 20px;
    border-top: 1px solid var(--dev-tools-border);
    display: flex;
    gap: 10px;
    justify-content: flex-end;
}

/* Console log types */
.console-line.thinking {
    color: #60A5FA;
    font-style: italic;
}

.console-line.tool {
    color: #4ADE80;
}

.console-line.success {
    color: #22c55e;
    font-weight: 600;
}

.console-line.warning {
    color: #f59e0b;
}
```

---

## 🚀 Usage Workflow

### **User Interaction Flow:**

1. **User clicks "AI Generate" button** in dev-tools UI
2. **Modal opens** with prompt textarea
3. **User describes module:** "Create a task management dashboard with drag-and-drop kanban board"
4. **AI streams response:**
   - Thinking blocks show in console: "💭 Planning module structure..."
   - Tool usage shows: "🔧 Using tool: validate_module_schema"
   - Code appears in Monaco Editor in real-time
5. **Files auto-populate:**
   - HTML tab shows generated HTML
   - JS tab shows generated JavaScript
   - CSS tab shows generated styles
   - Routes tab shows Flask routes
   - Manifest tab shows module config
6. **User can edit/save/test** the generated code

---

## 🔧 Backend Configuration

### **Create Dev-Tools Agent Endpoint**

Add to `AI_infrastructure/routes/agent_routes_v4.py`:

```python
@agent_bp.route('/api/agent/stream', methods=['POST', 'OPTIONS'])
@cross_origin()
def stream_agent_response():
    """
    Universal streaming endpoint for AI agents
    Supports dev-tools module, triple-agent, data-agent, etc.
    """
    if request.method == 'OPTIONS':
        return '', 204

    try:
        data = request.json or {}
        agent_id = data.get('agent_id', 'dev_tools_agent')
        message = data.get('message', '')
        session_id = data.get('session_id')
        enable_thinking = data.get('enable_thinking', True)
        
        # System prompts by agent type
        SYSTEM_PROMPTS = {
            'dev_tools_agent': """You are a full-stack development assistant specializing in creating modular UI components.

Your task is to generate complete, production-ready code for web modules including:
- HTML structure with semantic markup
- JavaScript with ES6+ best practices
- CSS with modern layouts (Grid, Flexbox)
- Python Flask routes for backend APIs
- JSON manifest files for module configuration

Always provide:
1. Clear file boundaries with comments
2. Reusable, maintainable code
3. Responsive design patterns
4. Accessibility considerations (ARIA labels)
5. Error handling and validation

Format output as:
```html
<!-- FILE: module-example.html -->
<div class="module-container">
...
</div>
```

```javascript
// FILE: module-example.js
(function() {
...
})();
```

Continue for each file type."""
        }
        
        system_prompt = SYSTEM_PROMPTS.get(agent_id, SYSTEM_PROMPTS['dev_tools_agent'])
        
        # ... rest of streaming implementation (existing code) ...
```

---

## 📊 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────┐
│         Dev-Tools UI (module-creator-enhanced.html)    │
│                                                         │
│  ┌──────────────┐   ┌──────────────┐  ┌─────────────┐│
│  │ Config Panel │   │ Monaco Editor│  │Preview Panel││
│  │  - Module ID │   │  - HTML Tab  │  │  - Live UI  ││
│  │  - Name      │   │  - JS Tab    │  │  - Console  ││
│  │  - Type      │   │  - CSS Tab   │  │             ││
│  └──────┬───────┘   └──────┬───────┘  └─────────────┘│
│         │                  │                           │
│         └──────────┬───────┘                           │
│                    │                                    │
│       ┌────────────▼──────────────┐                   │
│       │   [AI Generate Button]    │                   │
│       └────────────┬──────────────┘                   │
└────────────────────┼────────────────────────────────┘
                     │
                     │ HTTP POST
                     │ /api/agent/stream
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│      AI Infrastructure Backend (Flask + Claude)        │
│                                                         │
│  ┌──────────────────────────────────────────────────┐ │
│  │ agent_routes_v4.py                               │ │
│  │                                                  │ │
│  │  1. Receive prompt + context                    │ │
│  │  2. Build system prompt (dev_tools_agent)       │ │
│  │  3. Call Claude Sonnet 4 API                    │ │
│  │  4. Stream response chunks                      │ │
│  │     - Thinking blocks  → Console                │ │
│  │     - Tool usage       → Console                │ │
│  │     - Code content     → Monaco Editor          │ │
│  └──────────────────────────────────────────────────┘ │
│                                                         │
│  ┌──────────────────────────────────────────────────┐ │
│  │ Tool Registry (66+ MCP Tools)                    │ │
│  │  - validate_module_schema                        │ │
│  │  - test_module_credentials                       │ │
│  │  - format_javascript_code                        │ │
│  └──────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                     │
                     │ SSE Stream
                     │ (Server-Sent Events)
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Dev-Tools UI (Real-time Updates)          │
│                                                         │
│  💭 Console: "Planning module architecture..."         │
│  🔧 Console: "Using tool: validate_module_schema"      │
│  📝 Monaco Editor: Code appears character-by-character │
│  ✅ Console: "Module generation complete!"             │
└─────────────────────────────────────────────────────────┘
```

---

## ✅ Testing Checklist

- [ ] Flask backend running (`python flask_app.py` on port 5001)
- [ ] ANTHROPIC_API_KEY set in environment
- [ ] Dev-tools UI loads without errors
- [ ] AI Generate button visible in header
- [ ] Clicking button opens modal
- [ ] Entering prompt and clicking Generate triggers API call
- [ ] Console shows streaming status updates
- [ ] Monaco Editor receives code chunks
- [ ] File tabs update with generated content
- [ ] Error handling works (network failures, API errors)

---

## 🎯 Next Steps

1. **Implement AIService class** in dev-tools-module.js
2. **Add UI button and modal** for AI generation
3. **Wire up event handlers** to trigger generation
4. **Test with simple prompt** ("Create a hello world module")
5. **Add file parsing logic** to split AI output into tabs
6. **Implement advanced features:**
   - Code diffing (show changes)
   - Regeneration (refine existing code)
   - Multi-turn conversation (ask follow-up questions)
   - Version history (save iterations)

---

## 📚 Related Files

- **Backend:** `AI_infrastructure/routes/agent_routes_v4.py`
- **AI Client:** `AI_infrastructure/core/unified_ai_client.py`
- **Session Manager:** `AI_infrastructure/core/unified_session_manager.py`
- **Frontend UI:** `UI/triple_agent.html` (reference implementation)
- **Dev-Tools Module:** `dev-tools/dev-tools-module.js`

---

**Status:** 📋 **Integration Guide Complete** - Ready for implementation

**Next Action:** Implement `AIService` class and add AI Generate button to UI
