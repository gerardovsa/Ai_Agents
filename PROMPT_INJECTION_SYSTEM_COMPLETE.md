# Prompt Injection System - Complete Documentation

## Overview

The Prompt Injection System allows users to dynamically inject custom prompts into the AI's system prompt, enabling personalized AI behavior without modifying core code.

## Features

### 1. **Quick Actions** (Lightning Strike Buttons)
Short, focused prompt modifiers that change AI behavior instantly.

**Categories:**
- **Development** (⚡): expert_coder, code_reviewer, debugger
- **Analysis** (📊): detailed_analysis, step_by_step, critical_thinking
- **Data** (🗄️): sql_expert, data_analyst
- **Style** (💬): concise, eli5, professional
- **Business** (💼): quote_assistant, efficiency_optimizer
- **Creative** (✍️): creative_writer, email_composer

### 2. **Prompt Library** (Dropdown Selection)
Extended, specialized prompt enhancements for deep focus areas.

**Available Prompts:**
- system_architect - High-level system design and architecture
- security_analyst - Security and vulnerability assessment
- business_intelligence - KPI tracking and BI analysis
- technical_writer - Documentation and guides
- performance_engineer - Optimization and profiling
- ux_consultant - User experience and accessibility

### 3. **User Custom Prompts**
Users can save their own prompts for reuse.

### 4. **Prompt Preferences**
Save combinations of prompts for quick recall.

---

## Backend Integration

### Installation

1. **Files Created:**
   - `AI_infrastructure/core/prompt_injection_manager.py` - Core manager
   - `AI_infrastructure/routes/prompt_library_routes.py` - API routes

2. **Database Tables Created Automatically:**
   - `user_custom_prompts` - User's custom prompts
   - `user_prompt_preferences` - Saved prompt combinations

3. **Integration Point:**
   - `AI_infrastructure/routes/agent_routes_v4.py` (lines 896-930)

### Usage in Chat Requests

Send these parameters in the `/api/agent/chat-streaming` request:

```json
{
  "message": "Create a React component for user login",
  "quick_actions": ["expert_coder", "code_reviewer"],
  "library_prompts": ["system_architect"],
  "custom_prompt": "Use TypeScript and Material-UI"
}
```

---

## API Endpoints

### List Quick Actions
```http
GET /api/prompts/quick-actions?category=development
```

**Response:**
```json
{
  "success": true,
  "quick_actions": [
    {
      "key": "expert_coder",
      "name": "Expert Coder",
      "icon": "⚡",
      "category": "development"
    }
  ]
}
```

### List Library Prompts
```http
GET /api/prompts/library?category=data
```

### Create User Custom Prompt
```http
POST /api/prompts/user-custom
Content-Type: application/json

{
  "name": "My TypeScript Focus",
  "prompt_text": "Always use TypeScript with strict mode. Include comprehensive type definitions.",
  "category": "development",
  "is_quick_action": false
}
```

### Save Prompt Preference
```http
POST /api/prompts/preferences
Content-Type: application/json

{
  "preference_name": "My Coding Setup",
  "quick_actions": ["expert_coder", "debugger"],
  "library_prompts": ["system_architect"],
  "custom_prompt": "Focus on scalability"
}
```

### Get Saved Preference
```http
GET /api/prompts/preferences/My%20Coding%20Setup
```

---

## Frontend Integration (UI Examples)

### 1. Lightning Strike Buttons (Quick Actions)

```html
<!-- Quick Action Buttons (above message input) -->
<div class="quick-actions-bar">
  <button class="quick-action-btn" data-action="expert_coder">
    <span class="icon">⚡</span>
    <span class="label">Expert Coder</span>
  </button>
  
  <button class="quick-action-btn" data-action="debugger">
    <span class="icon">🐛</span>
    <span class="label">Debugger</span>
  </button>
  
  <button class="quick-action-btn" data-action="detailed_analysis">
    <span class="icon">📊</span>
    <span class="label">Detailed</span>
  </button>
  
  <button class="quick-action-btn" data-action="concise">
    <span class="icon">⚡</span>
    <span class="label">Concise</span>
  </button>
  
  <button class="quick-action-btn" data-action="sql_expert">
    <span class="icon">🗄️</span>
    <span class="label">SQL Expert</span>
  </button>
</div>

<style>
.quick-actions-bar {
  display: flex;
  gap: 8px;
  padding: 8px;
  background: #f5f5f5;
  border-radius: 8px;
  margin-bottom: 12px;
  overflow-x: auto;
}

.quick-action-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  background: white;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.quick-action-btn:hover {
  background: #007bff;
  color: white;
  border-color: #007bff;
}

.quick-action-btn.active {
  background: #007bff;
  color: white;
  border-color: #007bff;
  font-weight: 600;
}

.quick-action-btn .icon {
  font-size: 16px;
}

.quick-action-btn .label {
  font-size: 13px;
}
</style>

<script>
// Track active quick actions
let activeQuickActions = [];

document.querySelectorAll('.quick-action-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    const action = btn.dataset.action;
    
    // Toggle active state
    if (activeQuickActions.includes(action)) {
      activeQuickActions = activeQuickActions.filter(a => a !== action);
      btn.classList.remove('active');
    } else {
      activeQuickActions.push(action);
      btn.classList.add('active');
    }
  });
});

// When sending message, include active quick actions
function sendMessage(messageText) {
  fetch('/api/agent/chat-streaming', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      message: messageText,
      quick_actions: activeQuickActions,  // Include this!
      session_id: currentSessionId
    })
  });
}
</script>
```

### 2. Prompt Library Modal

```html
<!-- Library Button (next to send button) -->
<button class="prompt-library-btn" onclick="openPromptLibrary()">
  <span>📚</span> Prompt Library
</button>

<!-- Prompt Library Modal -->
<div id="promptLibraryModal" class="modal" style="display: none;">
  <div class="modal-content">
    <div class="modal-header">
      <h2>Prompt Library</h2>
      <button onclick="closePromptLibrary()">×</button>
    </div>
    
    <div class="modal-body">
      <!-- Category Tabs -->
      <div class="category-tabs">
        <button class="tab-btn active" data-category="all">All</button>
        <button class="tab-btn" data-category="development">Development</button>
        <button class="tab-btn" data-category="data">Data & SQL</button>
        <button class="tab-btn" data-category="creative">Creative</button>
      </div>
      
      <!-- Prompt Cards -->
      <div class="prompt-cards" id="promptCards">
        <!-- Dynamically loaded -->
      </div>
    </div>
    
    <div class="modal-footer">
      <button onclick="closePromptLibrary()">Cancel</button>
      <button onclick="applySelectedPrompts()">Apply Selected</button>
    </div>
  </div>
</div>

<script>
let selectedLibraryPrompts = [];

async function openPromptLibrary() {
  // Load library prompts
  const response = await fetch('/api/prompts/library');
  const data = await response.json();
  
  const cards = document.getElementById('promptCards');
  cards.innerHTML = data.library_prompts.map(prompt => `
    <div class="prompt-card" data-key="${prompt.key}">
      <input type="checkbox" id="prompt-${prompt.key}">
      <label for="prompt-${prompt.key}">
        <h3>${prompt.name}</h3>
        <span class="category-badge">${prompt.category}</span>
      </label>
    </div>
  `).join('');
  
  document.getElementById('promptLibraryModal').style.display = 'block';
}

function applySelectedPrompts() {
  // Get checked prompts
  selectedLibraryPrompts = Array.from(
    document.querySelectorAll('#promptCards input:checked')
  ).map(input => input.id.replace('prompt-', ''));
  
  // Show indicator that prompts are active
  document.querySelector('.prompt-library-btn').classList.add('active');
  
  closePromptLibrary();
}

// Include in message send
function sendMessage(messageText) {
  fetch('/api/agent/chat-streaming', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      message: messageText,
      quick_actions: activeQuickActions,
      library_prompts: selectedLibraryPrompts,  // Include this!
      session_id: currentSessionId
    })
  });
}
</script>
```

### 3. Custom Prompt Input

```html
<!-- Custom Prompt Textarea (collapsible) -->
<div class="custom-prompt-section">
  <button onclick="toggleCustomPrompt()">
    ➕ Add Custom Instructions
  </button>
  
  <textarea 
    id="customPromptInput" 
    placeholder="Add any custom instructions (e.g., 'Use Python 3.11 syntax', 'Focus on security')"
    style="display: none;"
  ></textarea>
</div>

<script>
function toggleCustomPrompt() {
  const textarea = document.getElementById('customPromptInput');
  textarea.style.display = textarea.style.display === 'none' ? 'block' : 'none';
}

// Include in message send
function sendMessage(messageText) {
  const customPrompt = document.getElementById('customPromptInput').value;
  
  fetch('/api/agent/chat-streaming', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      message: messageText,
      quick_actions: activeQuickActions,
      library_prompts: selectedLibraryPrompts,
      custom_prompt: customPrompt || null,  // Include this!
      session_id: currentSessionId
    })
  });
}
</script>
```

---

## Example Use Cases

### Use Case 1: Expert Code Review
**User Action:**
1. Click "Expert Coder" ⚡ quick action
2. Click "Code Reviewer" 🔍 quick action
3. Type: "Review this React component"

**Result:** AI becomes an expert code reviewer with strict production standards

### Use Case 2: SQL Performance Analysis
**User Action:**
1. Click "SQL Expert" 🗄️ quick action
2. Open Prompt Library → Select "Performance Engineer"
3. Type: "Optimize this query: SELECT * FROM..."

**Result:** AI analyzes query with performance optimization focus

### Use Case 3: Business Email
**User Action:**
1. Click "Professional" 💼 quick action
2. Click "Email Composer" 📧 quick action
3. Type: "Write email to client about delayed shipment"

**Result:** AI writes professional, empathetic business email

### Use Case 4: Detailed Analysis
**User Action:**
1. Click "Detailed Analysis" 📊 quick action
2. Click "Step by Step" 📝 quick action
3. Type: "Explain how OAuth 2.0 works"

**Result:** AI provides comprehensive, step-by-step explanation

---

## Testing

### Test the API
```bash
# List quick actions
curl http://localhost:5001/api/prompts/quick-actions

# Test chat with injections
curl -X POST http://localhost:5001/api/agent/chat-streaming \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Write a Python function",
    "quick_actions": ["expert_coder"],
    "custom_prompt": "Use type hints"
  }'
```

### Test Quick Actions
1. Start AI agent server: `BISTART`
2. Open UI
3. Click quick action buttons
4. Send message
5. Verify AI behavior changes

---

## Benefits

1. **No Code Changes Required** - Users customize AI without editing system files
2. **Reusable** - Save favorite prompt combinations
3. **Discoverable** - Users can explore available modifiers
4. **Flexible** - Combine multiple prompts for nuanced behavior
5. **Per-User** - Each user can have their own custom prompts
6. **Context-Specific** - Different prompts for different tasks

---

## Future Enhancements

1. **Prompt Marketplace** - Share prompts with community
2. **AI-Suggested Prompts** - AI recommends prompts based on query
3. **Prompt Analytics** - Track which prompts are most effective
4. **Prompt Templates** - Pre-built combinations for common tasks
5. **Voice Activation** - "Use expert coder mode"
6. **Hotkeys** - Keyboard shortcuts for quick actions

---

## Troubleshooting

### Issue: Prompts not applying
**Solution:** Check browser console for errors, verify API endpoint is registered

### Issue: Custom prompt not saved
**Solution:** Verify user_id is being passed, check database connection

### Issue: Quick actions not toggling
**Solution:** Check JavaScript console, verify event listeners attached

---

## Architecture

```
┌─────────────────────────────────────────────┐
│           USER INTERFACE                    │
│  ┌──────────────┐  ┌──────────────┐        │
│  │ Quick Actions│  │ Prompt Library│        │
│  │   Buttons    │  │    Modal      │        │
│  └──────────────┘  └──────────────┘        │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│         Flask Routes                        │
│  /api/agent/chat-streaming                  │
│  /api/prompts/*                             │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│    PromptInjectionManager                   │
│  - inject_prompts()                         │
│  - get_quick_action()                       │
│  - get_library_prompt()                     │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│         System Prompt Assembly              │
│  Base + Context + Synergy + INJECTIONS     │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│             AI Model                        │
│         (Claude, GPT, etc.)                 │
└─────────────────────────────────────────────┘
```

---

## Status

✅ **Backend Complete** - All files created and integrated
✅ **API Routes Complete** - 6 endpoints ready
✅ **Database Schema Complete** - Tables auto-created
⏳ **Frontend Integration** - Needs UI implementation
⏳ **Testing** - Needs end-to-end testing

**Ready for UI development!**
