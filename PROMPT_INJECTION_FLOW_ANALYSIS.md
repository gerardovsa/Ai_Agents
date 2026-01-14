# Prompt Injection Flow Analysis

## Overview
Analysis of how quick actions and detail prompts are injected into the AI request payload and system prompt.

---

## 🔄 Complete Flow

### 1️⃣ Frontend - Prompt Selection (UI/modules/prompt-library.js)

**User selects prompts from library:**
- Quick actions (lightning bolt icon) - e.g., "Expert Coder", "Detailed Analysis"
- Full prompts (document icon) - e.g., "SQL Expert", "Data Analyst"
- Stored in: `selectedPrompts` array

**Key Function:**
```javascript
// Line 1438 - Exposed to window for access by chat system
window.getSelectedPrompts = function () {
    return selectedPrompts;  // Array of prompt objects
};
```

**Each prompt object contains:**
```javascript
{
    id: 123,
    name: "expert_coder",
    type: "quick_action",  // or "full_prompt"
    prompt_text: "EXPERT CODING MODE ACTIVATED: ...",
    category: "development",
    ...
}
```

---

### 2️⃣ Frontend - Request Preparation (UI/business-ai-platform-v2.html)

**Location: Line 16520-16542 (sendUserMessage function)**

```javascript
// Get selected prompts from prompt library
let promptParams = '';
if (typeof window.getSelectedPrompts === 'function') {
    const selectedPrompts = window.getSelectedPrompts();
    if (selectedPrompts && selectedPrompts.length > 0) {
        // Separate by type
        const quickActions = selectedPrompts
            .filter(p => p.type === 'quick_action')
            .map(p => p.name);  // Extract just the name
        
        const libraryPrompts = selectedPrompts
            .filter(p => p.type === 'full_prompt')
            .map(p => p.name);  // Extract just the name
        
        // Build URL parameters
        if (quickActions.length > 0) {
            promptParams += `&quick_actions=${encodeURIComponent(quickActions.join(','))}`;
        }
        if (libraryPrompts.length > 0) {
            promptParams += `&library_prompts=${encodeURIComponent(libraryPrompts.join(','))}`;
        }
        
        console.log(`[PROMPT INJECTION] Quick Actions: ${quickActions.join(', ')}`);
        console.log(`[PROMPT INJECTION] Library Prompts: ${libraryPrompts.join(', ')}`);
    }
}

// Build stream URL with prompt parameters
const streamUrl = `${API_BASE_URL}/api/agent/stream/${agentId}?session_id=${sessionId}${promptParams}`;
```

**Example URL:**
```
http://localhost:5001/api/agent/stream/1?session_id=abc123&quick_actions=expert_coder,detailed_analysis&library_prompts=sql_expert
```

---

### 3️⃣ Backend - Request Reception (AI_infrastructure/routes/agent_routes_v4.py)

**⚠️ ISSUE IDENTIFIED:**

**Current Code (Line 928-931):**
```python
# Get injection parameters from request
quick_actions = request.json.get('quick_actions', []) if request.json else []
library_prompts = request.json.get('library_prompts', []) if request.json else []
custom_prompt = request.json.get('custom_prompt', None) if request.json else None
user_custom_prompts = request.json.get('user_custom_prompts', []) if request.json else []
```

**❌ Problem:** Looking for JSON body (`request.json`), but frontend sends URL parameters!

**✅ Should be:**
```python
# Get injection parameters from URL query string
quick_actions_str = request.args.get('quick_actions', '')
quick_actions = quick_actions_str.split(',') if quick_actions_str else []

library_prompts_str = request.args.get('library_prompts', '')
library_prompts = library_prompts_str.split(',') if library_prompts_str else []

custom_prompt = request.args.get('custom_prompt', None)
user_custom_prompts_str = request.args.get('user_custom_prompts', '')
user_custom_prompts = user_custom_prompts_str.split(',') if user_custom_prompts_str else []
```

---

### 4️⃣ Backend - Prompt Manager (AI_infrastructure/core/prompt_injection_manager.py)

**Initialization:**
```python
# Line 51 - Load built-in prompt definitions
self.quick_actions = self._load_quick_actions()
self.prompt_library = self._load_prompt_library()
```

**Quick Action Definitions (Line 137-348):**
```python
'expert_coder': {
    'name': 'Expert Coder',
    'icon': '💻',
    'category': 'development',
    'prompt': """EXPERT CODING MODE ACTIVATED:
- Write production-ready, optimized code
- Follow language-specific best practices
- Include comprehensive error handling
- Add detailed comments for complex logic
- Consider edge cases and performance"""
}
```

**Injection Method (Line 450-515):**
```python
def inject_prompts(
    self,
    base_prompt: str,
    quick_actions: Optional[List[str]] = None,
    library_prompts: Optional[List[str]] = None,
    custom_prompt: Optional[str] = None,
    user_id: Optional[int] = None,
    user_custom_prompts: Optional[List[str]] = None
) -> str:
    """
    Inject prompts into the base system prompt
    """
    injections = []
    
    # Add quick actions
    if quick_actions:
        quick_action_text = "\n\n".join([
            self.get_quick_action(action) 
            for action in quick_actions 
            if self.get_quick_action(action)
        ])
        if quick_action_text:
            injections.append(
                f"\n\n{'='*80}\n"
                f"QUICK ACTION MODIFIERS:\n"
                f"{'='*80}\n"
                f"{quick_action_text}"
            )
    
    # Add library prompts
    if library_prompts:
        library_text = "\n\n".join([
            self.get_library_prompt(prompt_key)
            for prompt_key in library_prompts
            if self.get_library_prompt(prompt_key)
        ])
        if library_text:
            injections.append(
                f"\n\n{'='*80}\n"
                f"SPECIALIZATION PROMPTS:\n"
                f"{'='*80}\n"
                f"{library_text}"
            )
    
    # Add custom prompt
    if custom_prompt and custom_prompt.strip():
        injections.append(
            f"\n\n{'='*80}\n"
            f"CUSTOM INSTRUCTIONS:\n"
            f"{'='*80}\n"
            f"{custom_prompt.strip()}"
        )
    
    # Combine base prompt + all injections
    if injections:
        return base_prompt + "".join(injections)
    else:
        return base_prompt
```

---

### 5️⃣ Backend - Final System Prompt Assembly

**Application (Line 935-944):**
```python
if quick_actions or library_prompts or custom_prompt or user_custom_prompts:
    prompt_manager = get_prompt_manager()
    system_prompt = prompt_manager.inject_prompts(
        base_prompt=system_prompt,
        quick_actions=quick_actions,
        library_prompts=library_prompts,
        custom_prompt=custom_prompt,
        user_id=user_id,
        user_custom_prompts=user_custom_prompts
    )
    
    print(f"[Stream {agent_id}] ⚡ Prompt injections applied:")
    if quick_actions:
        print(f"  - Quick Actions: {quick_actions}")
    if library_prompts:
        print(f"  - Library Prompts: {library_prompts}")
```

---

## 📊 Example Final System Prompt

**Base System Prompt:**
```
You are an AI assistant with access to 604 tools across 20+ platforms...
[Base instructions continue...]
```

**After Injection:**
```
You are an AI assistant with access to 604 tools across 20+ platforms...
[Base instructions continue...]

================================================================================
QUICK ACTION MODIFIERS:
================================================================================
EXPERT CODING MODE ACTIVATED:
- Write production-ready, optimized code
- Follow language-specific best practices
- Include comprehensive error handling
- Add detailed comments for complex logic
- Consider edge cases and performance

DETAILED ANALYSIS MODE ACTIVATED:
- Provide comprehensive explanations
- Break down complex topics step-by-step
- Include examples and use cases
- Show the reasoning process
- Anticipate follow-up questions

================================================================================
SPECIALIZATION PROMPTS:
================================================================================
SQL EXPERT MODE ACTIVATED:
- Write optimized, performant SQL queries
- Use proper indexing strategies
- Include query execution plans (EXPLAIN)
- Handle edge cases (NULL values, duplicates)
- Add comments explaining complex joins
```

---

## 🐛 Current Bug

**Issue:** Backend expects JSON body but frontend sends URL parameters

**Impact:** Prompt injections are NOT being applied - they're silently ignored

**Frontend sends:**
```
GET /api/agent/stream/1?session_id=abc&quick_actions=expert_coder&library_prompts=sql_expert
```

**Backend looks for:**
```python
request.json.get('quick_actions', [])  # Always returns [] because no JSON body!
```

---

## ✅ Fix Required

**File:** `AI_infrastructure/routes/agent_routes_v4.py`  
**Lines:** 928-931

**Change from:**
```python
quick_actions = request.json.get('quick_actions', []) if request.json else []
library_prompts = request.json.get('library_prompts', []) if request.json else []
```

**Change to:**
```python
# Parse URL parameters (comma-separated values)
quick_actions_str = request.args.get('quick_actions', '')
quick_actions = [q.strip() for q in quick_actions_str.split(',') if q.strip()]

library_prompts_str = request.args.get('library_prompts', '')
library_prompts = [p.strip() for p in library_prompts_str.split(',') if p.strip()]

custom_prompt = request.args.get('custom_prompt', None)

user_custom_prompts_str = request.args.get('user_custom_prompts', '')
user_custom_prompts = [u.strip() for u in user_custom_prompts_str.split(',') if u.strip()]
```

---

## 📝 Summary

### How It Works (When Fixed):
1. User selects prompts from library UI
2. Frontend extracts prompt names and adds to URL: `?quick_actions=expert_coder,detailed_analysis`
3. Backend parses URL parameters: `['expert_coder', 'detailed_analysis']`
4. Prompt Manager looks up each prompt by name
5. Prompt text is appended to system prompt with section headers
6. Enhanced system prompt is sent to Claude API
7. Claude responds with behavior modifications from injected prompts

### Available Prompt Types:
- **Quick Actions:** Concise behavior modifiers (expert_coder, detailed_analysis, concise, eli5)
- **Library Prompts:** Full specialized prompts (sql_expert, data_analyst, technical_writer)
- **Custom Prompts:** User-defined reusable prompts (stored in database)
- **Ad-hoc Custom:** One-time custom instructions via text field

### Injection Format:
```
[BASE SYSTEM PROMPT]

================================================================================
QUICK ACTION MODIFIERS:
================================================================================
[Quick action prompt text 1]

[Quick action prompt text 2]

================================================================================
SPECIALIZATION PROMPTS:
================================================================================
[Library prompt text 1]

[Library prompt text 2]

================================================================================
CUSTOM INSTRUCTIONS:
================================================================================
[Custom prompt text]
```

---

**Date:** November 17, 2025  
**Status:** Analysis Complete - Bug Identified - Fix Required
