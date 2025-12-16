# AI Agent Integration - Visual Architecture

## 🎯 Quick Answer: Where's the AI Agent?

**The AI agent lives in your Flask backend** at `AI_infrastructure/flask_app.py`, NOT in the dev-tools UI. The dev-tools module is just a **client** that sends requests to the AI backend.

---

## 📍 Current State (Before Integration)

```
┌─────────────────────────────────────────────────┐
│  Dev-Tools UI (Standalone Editor)              │
│  Location: dev-tools/module-creator-enhanced.html│
│                                                 │
│  ┌─────────────┐    ┌─────────────┐           │
│  │ Config      │    │ Monaco      │           │
│  │ Panel       │    │ Editor      │           │
│  │             │    │             │           │
│  │ - Module ID │    │ - HTML Tab  │           │
│  │ - Name      │    │ - JS Tab    │           │
│  │ - Type      │    │ - CSS Tab   │           │
│  └─────────────┘    └─────────────┘           │
│                                                 │
│  ❌ NO AI CONNECTION                            │
│  ❌ User types code manually                    │
│  ❌ No code generation                          │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  AI Infrastructure Backend (Flask)              │
│  Location: AI_infrastructure/flask_app.py       │
│                                                 │
│  ✅ Claude Sonnet 4 API Integration             │
│  ✅ 66+ MCP Tools (via Tool Registry)           │
│  ✅ Streaming Endpoints (/api/agent/stream)     │
│  ✅ Session Management                          │
│                                                 │
│  Currently used by:                             │
│  - triple_agent.html                            │
│  - single_viewer.html                           │
│  - data_agent.html                              │
└─────────────────────────────────────────────────┘

❌ NO CONNECTION BETWEEN THEM
```

---

## 📍 Target State (After Integration)

```
┌─────────────────────────────────────────────────────────────┐
│  Dev-Tools UI (AI-Powered Code Generator)                  │
│  Location: dev-tools/module-creator-enhanced.html           │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ Header Bar                                            │ │
│  │                                                       │ │
│  │  [🤖 AI Generate] [New] [Load] [Save] [Validate]    │ │
│  │        ↑                                              │ │
│  │        │ NEW BUTTON                                   │ │
│  └────────┼───────────────────────────────────────────────┘ │
│           │                                                 │
│           │ Click opens modal                               │
│           ▼                                                 │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ AI Prompt Modal                                       │ │
│  │                                                       │ │
│  │  "Create a task management dashboard with           │ │
│  │   drag-and-drop kanban board..."                    │ │
│  │                                                       │ │
│  │  [✓] Include current module context                 │ │
│  │  [✓] Show AI thinking process                       │ │
│  │                                                       │ │
│  │      [Generate Code]  [Cancel]                       │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐   │
│  │ Config      │    │ Monaco      │    │ Console     │   │
│  │ Panel       │    │ Editor      │    │ Panel       │   │
│  │             │    │             │    │             │   │
│  │ Module ID   │    │ HTML Tab ✨ │    │ 💭 Planning │   │
│  │ Name        │    │ JS Tab   ✨ │    │ 🔧 Tools    │   │
│  │ Type        │    │ CSS Tab  ✨ │    │ ✅ Complete │   │
│  └─────────────┘    └─────────────┘    └─────────────┘   │
│                           ↑                    ↑            │
│                           │                    │            │
│                           │ AI writes here     │ AI status  │
└───────────────────────────┼────────────────────┼────────────┘
                            │                    │
                            │ HTTP POST          │
                            │ /api/agent/stream  │
                            │                    │
                            ▼                    │
┌─────────────────────────────────────────────────┼────────────┐
│  AI Infrastructure Backend (Flask)              │            │
│  Location: AI_infrastructure/flask_app.py       │            │
│                                                 │            │
│  ┌──────────────────────────────────────────┐  │            │
│  │ AIService in dev-tools-module.js         │  │            │
│  │                                          │  │            │
│  │ fetch('/api/agent/stream', {            │  │            │
│  │   method: 'POST',                       │  │            │
│  │   body: JSON.stringify({                │  │            │
│  │     agent_id: 'dev_tools_agent',        │  │            │
│  │     message: prompt,                    │  │            │
│  │     stream: true                        │  │            │
│  │   })                                    │  │            │
│  │ })                                      │  │            │
│  └──────────────────────────────────────────┘  │            │
│                                                 │            │
│  ┌──────────────────────────────────────────┐  │            │
│  │ agent_routes_v4.py                       │  │            │
│  │                                          │  │            │
│  │ @agent_bp.route('/api/agent/stream')    │  │            │
│  │ def stream_agent_response():            │  │            │
│  │                                          │  │            │
│  │   # 1. Parse request                    │  │            │
│  │   agent_id = 'dev_tools_agent'          │  │            │
│  │   message = request.json['message']     │  │            │
│  │                                          │  │            │
│  │   # 2. Build system prompt              │  │            │
│  │   system = "You are a full-stack dev    │  │            │
│  │            assistant..."                 │  │            │
│  │                                          │  │            │
│  │   # 3. Call Claude API                  │  │            │
│  │   response = anthropic.messages.create( │  │            │
│  │     model='claude-sonnet-4',            │  │            │
│  │     messages=[{                         │  │            │
│  │       'role': 'user',                   │  │            │
│  │       'content': message                │  │            │
│  │     }],                                 │  │            │
│  │     stream=True                         │  │            │
│  │   )                                     │  │            │
│  │                                          │  │            │
│  │   # 4. Stream chunks back to UI         │  │            │
│  │   for chunk in response:                │  │            │
│  │     if chunk.type == 'thinking':        │──┼────────────┘
│  │       yield f"data: {thinking_json}\n"  │  │  Thinking
│  │     elif chunk.type == 'text':          │  │  blocks
│  │       yield f"data: {text_json}\n"      │──┼─→ Code chunks
│  │     elif chunk.type == 'tool_use':      │  │  to Monaco
│  │       yield f"data: {tool_json}\n"      │  │  Editor
│  └──────────────────────────────────────────┘  │
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │ Tool Registry (66+ MCP Tools)            │  │
│  │                                          │  │
│  │ - validate_module_schema                │  │
│  │ - format_javascript_code                │  │
│  │ - test_module_syntax                    │  │
│  │ - generate_css_variables                │  │
│  └──────────────────────────────────────────┘  │
│                                                 │
│  ✅ Claude Sonnet 4 Connected                   │
│  ✅ Streaming Enabled                           │
│  ✅ Tool Execution Available                    │
└─────────────────────────────────────────────────┘
```

---

## 🔄 Request/Response Flow

### **Step-by-Step Interaction:**

```
1. USER ACTION
   ├─ User clicks [🤖 AI Generate] button
   └─ Modal opens with textarea

2. USER INPUT
   ├─ User types: "Create a user profile dashboard with avatar upload"
   └─ User clicks [Generate Code]

3. FRONTEND (dev-tools-module.js)
   ├─ AIService.generateCode() called
   ├─ Build request body:
   │  {
   │    agent_id: "dev_tools_agent",
   │    message: "Create a user profile dashboard...",
   │    session_id: "session_123456",
   │    stream: true,
   │    enable_thinking: true
   │  }
   ├─ POST to http://localhost:5001/api/agent/stream
   └─ Open EventSource stream

4. BACKEND (Flask - agent_routes_v4.py)
   ├─ Receive request
   ├─ Extract agent_id, message, session_id
   ├─ Load system prompt for 'dev_tools_agent'
   ├─ Call Claude API:
   │  anthropic.messages.create(
   │    model="claude-sonnet-4-20250514",
   │    max_tokens=8000,
   │    system="You are a full-stack dev assistant...",
   │    messages=[{role: "user", content: message}],
   │    stream=True,
   │    tools=[66+ MCP tools]
   │  )
   └─ Start streaming response

5. STREAMING CHUNKS (Real-time)
   
   ┌─────────────────────────────────────────┐
   │ Chunk 1: Session ID                     │
   │ data: {"type":"session_id","id":"123"}  │
   └─────────────────────────────────────────┘
                    ↓
   ┌─────────────────────────────────────────┐
   │ Chunk 2: Thinking Block                 │
   │ data: {"type":"thinking",               │
   │       "content":"I'll create 5 files    │
   │                  for this module..."}   │
   └─────────────────────────────────────────┘
                    ↓
   Console shows: 💭 I'll create 5 files...
                    ↓
   ┌─────────────────────────────────────────┐
   │ Chunk 3: Tool Use                       │
   │ data: {"type":"tool_use",               │
   │       "tool_name":"validate_module",    │
   │       "tool_input":{...}}               │
   └─────────────────────────────────────────┘
                    ↓
   Console shows: 🔧 Using tool: validate_module
                    ↓
   ┌─────────────────────────────────────────┐
   │ Chunk 4-100: Code Content               │
   │ data: {"type":"text",                   │
   │       "content":"<!-- FILE: user-       │
   │                  profile.html -->\n"}   │
   │                                         │
   │ data: {"type":"text",                   │
   │       "content":"<div class="}          │
   │                                         │
   │ data: {"type":"text",                   │
   │       "content":"\"profile-container    │
   └─────────────────────────────────────────┘
                    ↓
   Monaco Editor shows code appearing letter-by-letter
                    ↓
   ┌─────────────────────────────────────────┐
   │ Chunk 101: Stream End                   │
   │ data: {"type":"done"}                   │
   └─────────────────────────────────────────┘
                    ↓
   Console shows: ✅ Code generation complete!

6. RESULT
   ├─ HTML Tab: Complete HTML structure
   ├─ JS Tab: Complete JavaScript code
   ├─ CSS Tab: Complete styles
   ├─ Routes Tab: Flask routes
   ├─ Manifest Tab: Module configuration
   └─ User can now edit/save/test the module
```

---

## 🗂️ File Structure (What Changes Where)

```
AI_agents/
├── dev-tools/
│   ├── module-creator-enhanced.html  ← ✅ Already exists (UI entry)
│   ├── dev-tools-module.js          ← 🔧 MODIFY: Add AIService class
│   │                                   │   + Add AI button handler
│   │                                   │   + Add streaming logic
│   │                                   │   + Add modal dialog
│   ├── dev-tools-styles.css         ← 🔧 MODIFY: Add AI button styles
│   │                                   │   + Add modal styles
│   │                                   │   + Add console log colors
│   └── AI_AGENT_INTEGRATION_GUIDE.md ← ✅ NEW (this document)
│
├── AI_infrastructure/
│   ├── flask_app.py                 ← ✅ Already exists (runs backend)
│   ├── routes/
│   │   └── agent_routes_v4.py       ← 🔧 MODIFY: Add dev_tools_agent
│   │                                   │   system prompt
│   ├── core/
│   │   ├── unified_ai_client.py     ← ✅ Already exists (Claude client)
│   │   └── unified_session_manager.py ← ✅ Already exists (sessions)
│   └── tools/
│       └── registry_v3.py           ← ✅ Already exists (66+ tools)
│
└── UI/
    └── triple_agent.html            ← 📚 REFERENCE (existing AI UI)
                                        Shows how streaming works
```

---

## 🎨 Visual Code Flow

### **Where AI Code Appears in UI:**

```
┌────────────────────────────────────────────────────────────┐
│  Module Creator UI                                         │
│                                                            │
│  ┌────────────────────────────────────────────────────┐   │
│  │ Header: [🤖 AI Generate] [New] [Load] [Save]      │   │
│  └────────────────────────────────────────────────────┘   │
│                                                            │
│  ┌──────────┐  ┌─────────────────────────┐  ┌──────────┐ │
│  │ Config   │  │ Monaco Editor           │  │ Preview  │ │
│  │          │  │                         │  │          │ │
│  │ Module ID│  │ ┌─────────────────────┐ │  │ Console  │ │
│  │ Name     │  │ │ [HTML][JS][CSS]     │ │  │          │ │
│  │ Type     │  │ └─────────────────────┘ │  │ 💭 AI is │ │
│  │ Icon     │  │                         │  │ thinking │ │
│  │ Desc     │  │ <!-- FILE: user-        │  │          │ │
│  │          │  │  profile.html -->       │  │ 🔧 Using │ │
│  │ [Deploy] │  │ <div class="profile-    │  │ validate │ │
│  │          │  │   container">           │  │          │ │
│  │          │  │   <div class="avatar-   │  │ 📝 Code  │ │
│  │          │  │     upload">            │  │ appears! │ │
│  │          │  │     <input type=        │  │          │ │
│  │          │  │       "file" ...>       │  │ ✅ Done! │ │
│  │          │  │   </div>                │  │          │ │
│  │          │  │ </div>                  │  │          │ │
│  │          │  │                         │  │          │ │
│  │          │  │ ← Code streams in       │  │          │ │
│  │          │  │   character-by-char     │  │          │ │
│  └──────────┘  └─────────────────────────┘  └──────────┘ │
└────────────────────────────────────────────────────────────┘
```

---

## 🧩 Code Integration Points

### **1. AIService Class (New)**

```javascript
// Location: dev-tools-module.js (add at top, around line 50)

class AIService {
    constructor(apiBase) { ... }
    async generateCode(prompt, moduleType, context, callbacks) { ... }
    _buildPrompt(userPrompt, moduleType, context) { ... }
}
```

### **2. DevToolsModule Class (Modify)**

```javascript
// Location: dev-tools-module.js (existing class)

class DevToolsModule {
    constructor(config) {
        // ... existing code ...
        this.aiService = new AIService(config.apiBase); // ← ADD THIS
    }

    _buildWorkspaceUI() {
        // Add AI button to header-actions
        return `
            <div class="header-actions">
                <button id="ai-generate-btn" ...>AI Generate</button>
                <!-- existing buttons -->
            </div>
        `;
    }

    _bindEvents() {
        // ... existing events ...
        
        // ADD AI button handler
        document.getElementById('ai-generate-btn')
            .addEventListener('click', () => this._showAIPromptModal());
    }

    async _handleAIGeneration() {
        // NEW METHOD
        const prompt = document.getElementById('ai-prompt-input').value;
        await this.aiService.generateCode(
            prompt,
            this.currentModule.type,
            this.currentModule,
            {
                onChunk: (text) => this._appendToEditor(text),
                onThinking: (thought) => this._logToConsole(`💭 ${thought}`),
                onToolUse: (tool) => this._logToConsole(`🔧 ${tool}`)
            }
        );
    }
}
```

### **3. Backend Endpoint (Modify)**

```python
# Location: AI_infrastructure/routes/agent_routes_v4.py

@agent_bp.route('/api/agent/stream', methods=['POST'])
def stream_agent_response():
    data = request.json
    agent_id = data.get('agent_id')  # 'dev_tools_agent'
    
    # System prompts for different agents
    SYSTEM_PROMPTS = {
        'dev_tools_agent': """You are a full-stack dev assistant.
        Generate complete module code with clear file boundaries.""",
        # ... other agents ...
    }
    
    system_prompt = SYSTEM_PROMPTS.get(agent_id)
    
    # Stream response from Claude
    response = anthropic.messages.create(
        model='claude-sonnet-4',
        stream=True,
        messages=[...],
        system=system_prompt
    )
    
    # Yield chunks to frontend
    for chunk in response:
        yield f"data: {json.dumps(chunk)}\n\n"
```

---

## 🚀 Quick Start Implementation

### **Minimal Working Version (30 minutes):**

1. **Add AIService to dev-tools-module.js** (100 lines)
2. **Add AI button to header** (5 lines)
3. **Add click handler** (10 lines)
4. **Add console logging** (20 lines)
5. **Test with simple prompt** ("Create hello world module")

### **Full Implementation (2 hours):**

1. ✅ Minimal version (above)
2. Add modal dialog (50 lines)
3. Add streaming to Monaco Editor (30 lines)
4. Add thinking/tool displays (40 lines)
5. Add file parsing (split AI output into tabs) (80 lines)
6. Add error handling (30 lines)
7. Add progress indicators (20 lines)
8. Test with complex prompts

---

## ❓ FAQ

**Q: Where is the AI agent code?**  
A: In `AI_infrastructure/flask_app.py` - it's a Flask backend with Claude API integration.

**Q: Why isn't the AI in the dev-tools UI?**  
A: The UI is just a client. The AI (Claude) runs in the backend because it requires API keys and needs to access tools/databases.

**Q: How does code get into Monaco Editor?**  
A: Via streaming HTTP response - AI sends chunks, JavaScript appends them to editor.

**Q: Can I use a different AI model?**  
A: Yes - modify `unified_ai_client.py` to use OpenAI GPT-4, DeepSeek, or any other model.

**Q: What if the backend isn't running?**  
A: The AI Generate button will show an error. Backend must be running on port 5001.

**Q: Can I test this without the backend?**  
A: No - you need the Flask backend to process AI requests. But you can test the UI layout without it.

---

**Status:** 📋 **Visual Architecture Complete** - Shows exactly where AI agent connects to UI

**Next:** Implement `AIService` class and test with backend
