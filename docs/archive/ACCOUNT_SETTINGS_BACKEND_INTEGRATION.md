# Account Settings Backend Integration Guide
**Date:** November 3, 2025  
**Status:** 🟢 UI COMPLETE - Backend Integration Guide

## Overview

The Account Settings UI is now complete with full localStorage persistence. Now we need to integrate it with the backend to:

1. ✅ UI stores settings in `localStorage` with key `accountSettings`
2. 🟡 Frontend sends settings with AI requests (needs implementation)
3. 🟡 Backend applies settings to agent execution (needs implementation)
4. 🟡 Backend validates and stores user preferences (needs implementation)

---

## Part 1: Frontend Integration (Minor)

The UI already saves settings locally. Now add to AI requests:

### In AI Agent Form Submission
**File:** `UI/business-ai-platform-v2.html`  
**Find:** The function that sends AI agent requests (look for `sendMessage()` or similar)

```javascript
// Get account settings
const accountSettings = getAccountSettings();

// Send with AI request
const payload = {
    message: userMessage,
    session_id: sessionId,
    user_id: userId,
    // NEW: Add settings to request
    ai_settings: {
        model: accountSettings.model,
        temperature: accountSettings.temperature,
        top_p: accountSettings.topP,
        enable_thinking: accountSettings.enableThinking,
        max_rounds: accountSettings.maxRounds,
        max_tokens: accountSettings.maxTokens,
        thinking_budget: accountSettings.thinkingBudget,
        enable_streaming: accountSettings.enableStreaming
    }
};

// Send to backend
fetch('/api/agent/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
});
```

---

## Part 2: Backend Routes (PRIMARY)

### Step 1: Accept Settings in Agent Routes

**File:** `AI_infrastructure/routes/agent_routes.py`

Update the `/api/agent/chat` endpoint to accept settings:

```python
@agent_bp.route('/api/agent/chat', methods=['POST'])
def chat_with_agent():
    """AI agent chat endpoint with account settings support"""
    
    data = request.json
    user_id = data.get('user_id')
    message = data.get('message', '')
    session_id = data.get('session_id')
    
    # NEW: Extract account settings from request
    ai_settings = data.get('ai_settings', {})
    
    # Apply settings or use defaults
    model = ai_settings.get('model', 'claude-sonnet-4-5-20250929')
    temperature = ai_settings.get('temperature', 1.0)
    top_p = ai_settings.get('top_p', 1.0)
    max_rounds = ai_settings.get('max_rounds', 20)
    max_tokens = ai_settings.get('max_tokens', 16000)
    thinking_budget = ai_settings.get('thinking_budget', 10000)
    enable_thinking = ai_settings.get('enable_thinking', False)
    enable_streaming = ai_settings.get('enable_streaming', True)
    
    # Create agent with settings
    agent = StreamingAgentWorker(
        model=model,
        temperature=temperature,
        top_p=top_p,
        max_rounds=max_rounds,
        max_tokens=max_tokens,
        thinking_budget=thinking_budget,
        enable_thinking=enable_thinking
    )
    
    # Execute with streaming
    return generate_stream(
        agent,
        session_id=session_id,
        user_prompt=message,
        user_id=user_id,
        enable_streaming=enable_streaming
    )
```

### Step 2: Update StreamingAgentWorker

**File:** `AI_infrastructure/core/streaming_agent_worker.py`

Update the `__init__` method to accept settings:

```python
class StreamingAgentWorker:
    def __init__(
        self,
        model: str = None,
        temperature: float = None,
        top_p: float = None,
        max_rounds: int = None,
        max_tokens: int = None,
        thinking_budget: int = None,
        enable_thinking: bool = False
    ):
        """Initialize agent with optional user-provided settings"""
        
        # Import defaults from constants
        from AI_infrastructure.config.constants import (
            CLAUDE_MODEL, TEMPERATURE, MAX_TURNS, 
            MAX_TOKENS, THINKING_BUDGET
        )
        
        # Use provided settings or fall back to defaults
        self.model = model or CLAUDE_MODEL
        self.temperature = temperature if temperature is not None else TEMPERATURE
        self.top_p = top_p if top_p is not None else 1.0
        self.max_rounds = max_rounds or MAX_TURNS
        self.max_tokens = max_tokens or MAX_TOKENS
        self.thinking_budget = thinking_budget or THINKING_BUDGET
        self.enable_thinking = enable_thinking
        
        print(f"🎛️ Agent initialized with settings:")
        print(f"   Model: {self.model}")
        print(f"   Temperature: {self.temperature}")
        print(f"   Max Rounds: {self.max_rounds}")
        print(f"   Max Tokens: {self.max_tokens}")
        print(f"   Extended Thinking: {self.enable_thinking}")
```

### Step 3: Apply Settings to Anthropic API Call

**File:** `AI_infrastructure/core/streaming_agent_worker.py`

Update the `execute_with_streaming()` method where Claude API is called:

```python
# In execute_with_streaming() where you call Anthropic API
response = client.messages.create(
    model=self.model,  # Use user's model preference
    max_tokens=self.max_tokens,  # Use user's max tokens
    temperature=self.temperature,  # Use user's temperature
    top_p=self.top_p,  # Use user's top_p
    thinking={
        "type": "enabled",
        "budget_tokens": self.thinking_budget
    } if self.enable_thinking else None,
    system=system_prompt,
    messages=formatted_messages,
    tools=tools,
    betas=ANTHROPIC_BETA_HEADERS
)
```

---

## Part 3: Settings Persistence (Optional but Recommended)

### Store User Preferences in Database

**File:** `AI_infrastructure/routes/settings_routes.py` (NEW)

Create a new route file:

```python
"""
User Account Settings Routes

Handles storage and retrieval of user preferences
"""

from flask import Blueprint, request, jsonify
from AI_infrastructure.auth.credential_injector import get_db_connection
import json

settings_bp = Blueprint('settings', __name__, url_prefix='/api/settings')

@settings_bp.route('/save', methods=['POST'])
def save_user_settings():
    """Save user account settings to database"""
    
    data = request.json
    user_id = data.get('user_id')
    settings = data.get('settings', {})
    
    if not user_id:
        return {'error': 'user_id required'}, 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Save settings as JSON
        settings_json = json.dumps(settings)
        
        cursor.execute("""
            INSERT OR REPLACE INTO user_settings (user_id, ai_settings, updated_at)
            VALUES (?, ?, datetime('now'))
        """, (user_id, settings_json))
        
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'message': 'Settings saved',
            'settings': settings
        }, 200
        
    except Exception as e:
        return {'error': str(e)}, 500

@settings_bp.route('/get/<int:user_id>', methods=['GET'])
def get_user_settings(user_id):
    """Retrieve user settings"""
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT ai_settings FROM user_settings
            WHERE user_id = ?
        """, (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            settings = json.loads(row[0])
            return {'settings': settings}, 200
        else:
            # Return defaults if no settings found
            return {
                'settings': {
                    'model': 'claude-sonnet-4-5-20250929',
                    'temperature': 1.0,
                    'max_rounds': 20,
                    'max_tokens': 16000
                }
            }, 200
            
    except Exception as e:
        return {'error': str(e)}, 500
```

### Database Table

Add to `AI_infrastructure/database/schema.sql`:

```sql
CREATE TABLE IF NOT EXISTS user_settings (
    user_id INTEGER PRIMARY KEY,
    ai_settings JSON DEFAULT NULL,
    ui_settings JSON DEFAULT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_user_settings_updated_at 
ON user_settings(updated_at);
```

### Register Route Blueprint

**File:** `AI_infrastructure/flask_app.py`

```python
from AI_infrastructure.routes.settings_routes import settings_bp

# Register blueprint
app.register_blueprint(settings_bp)
```

---

## Part 4: Frontend-Backend Integration

### Update Frontend to Send Settings

**File:** `UI/business-ai-platform-v2.html`

Add to the message sending function:

```javascript
async function sendAIMessage(userMessage) {
    // Get current settings
    const settings = getAccountSettings();
    
    // Prepare payload
    const payload = {
        message: userMessage,
        session_id: getCurrentSessionId(),
        user_id: UserAuth.user?.id,
        ai_settings: settings  // Include settings
    };
    
    // Send to backend
    const response = await fetch('/api/agent/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${UserAuth.token}`
        },
        body: JSON.stringify(payload)
    });
    
    // Handle response...
}
```

### Load User Settings on Login

**File:** `UI/business-ai-platform-v2.html`

Update `loadUserProfile()`:

```javascript
async function loadUserProfile() {
    // Existing profile loading...
    
    // NEW: Load user's saved settings from backend
    if (UserAuth.user?.id) {
        try {
            const response = await fetch(`/api/settings/get/${UserAuth.user.id}`, {
                headers: { 'Authorization': `Bearer ${UserAuth.token}` }
            });
            
            if (response.ok) {
                const data = await response.json();
                // Merge backend settings with localStorage
                const backendSettings = data.settings || {};
                const localSettings = getAccountSettings();
                
                // Prefer backend settings if available
                const mergedSettings = { ...localSettings, ...backendSettings };
                localStorage.setItem('accountSettings', JSON.stringify(mergedSettings));
                
                console.log('✅ User settings loaded from backend');
            }
        } catch (error) {
            console.log('⚠️ Could not load backend settings:', error);
            // Fall back to localStorage
        }
    }
}
```

---

## Implementation Checklist

### Phase 1: Basic Integration (Next Steps)
- [ ] Update `/api/agent/chat` route to accept `ai_settings`
- [ ] Modify `StreamingAgentWorker.__init__()` to accept settings
- [ ] Apply settings to Claude API call in `execute_with_streaming()`
- [ ] Test with manual settings in request payload
- [ ] Verify settings apply correctly (check model, temperature, max_tokens)

### Phase 2: Frontend Integration
- [ ] Locate message sending function in UI
- [ ] Add `getAccountSettings()` call to include settings in request
- [ ] Verify settings sent with each AI request
- [ ] Test UI flow: Change setting → Save → Send message → Verify applied

### Phase 3: Database Persistence (Optional)
- [ ] Create `user_settings` table in database
- [ ] Add settings routes (`/api/settings/save` and `/api/settings/get`)
- [ ] Register blueprint in Flask app
- [ ] Load user settings on login
- [ ] Sync frontend with backend on startup

---

## Testing Guide

### Test 1: Basic Settings Application
```bash
# Send request with custom settings
curl -X POST http://localhost:5001/api/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "message": "Hello",
    "ai_settings": {
      "model": "claude-haiku-3-20250307",
      "temperature": 0.5,
      "max_rounds": 10,
      "max_tokens": 1000
    }
  }'

# Verify: Check response uses settings
```

### Test 2: Default Settings Fallback
```bash
# Send request WITHOUT settings - should use defaults
curl -X POST http://localhost:5001/api/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "message": "Hello"
  }'

# Verify: Uses defaults from constants.py
```

### Test 3: UI Settings Flow
1. Open UI at http://localhost:5001
2. Click user menu → Account Settings
3. Change Temperature to 0.3
4. Set Max Rounds to 5
5. Click Close
6. Send AI message
7. Verify settings applied (check logs, response speed)

---

## Configuration Defaults (From constants.py)

| Setting | Default | Min | Max |
|---------|---------|-----|-----|
| Model | claude-sonnet-4-5-20250929 | - | - |
| Temperature | 1.0 | 0.0 | 1.0 |
| Top P | 1.0 | 0.0 | 1.0 |
| Max Rounds | 20 | 1 | 50 |
| Max Tokens | 16000 | 1000 | 64000 |
| Thinking Budget | 10000 | 0 | 20000 |
| Enable Thinking | false | - | - |
| Enable Streaming | true | - | - |

---

## Error Handling

### Invalid Settings
```python
# Validate settings in route
def validate_settings(settings):
    temperature = settings.get('temperature')
    if temperature is not None and not (0.0 <= temperature <= 1.0):
        raise ValueError(f"Temperature must be 0.0-1.0, got {temperature}")
    
    max_rounds = settings.get('max_rounds')
    if max_rounds is not None and not (1 <= max_rounds <= 50):
        raise ValueError(f"Max rounds must be 1-50, got {max_rounds}")
    
    return True
```

---

## Next Steps

1. **Phase 1 (Today):** Implement basic settings acceptance in routes
2. **Phase 2 (Tomorrow):** Connect frontend to send settings
3. **Phase 3 (Optional):** Add database persistence

The UI is complete and saves to localStorage. Backend just needs to:
1. Accept the settings from requests
2. Pass them to agent initialization
3. Apply them in Claude API calls

---

## Current Status

✅ **UI Complete**
- Account Settings modal with 3 collapsible sections
- localStorage persistence
- Real-time value updates with sliders
- Save/Reset functionality

🟡 **Backend Integration Needed**
- Accept settings in `/api/agent/chat` route
- Pass to StreamingAgentWorker
- Apply in Claude API calls

🟡 **Database Persistence (Optional)**
- Store settings per user
- Load on login
- Sync between devices

---

## Files to Modify

1. `AI_infrastructure/routes/agent_routes.py` - Accept settings
2. `AI_infrastructure/core/streaming_agent_worker.py` - Apply settings
3. `UI/business-ai-platform-v2.html` - Send settings (optional)
4. `AI_infrastructure/routes/settings_routes.py` - NEW for persistence

All changes maintain backward compatibility (settings are optional).
