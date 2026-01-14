# AI Agent Inline Interaction System - Integration Guide

**Date:** December 16, 2025  
**Status:** ✅ Core Implementation Complete

## 📋 Overview

This system provides **ChatGPT-style inline interaction** for AI agents to request user input during task execution. Unlike modal popups, interaction bubbles appear **directly in the agent's message container**, maintaining context and workflow continuity.

## 🎯 Key Features

- ✅ **Inline message bubbles** - No modal overlays
- ✅ **Multiple input types** - Text, password, choice, 2FA, CAPTCHA
- ✅ **Progress updates** - Real-time task progress with percentage bars
- ✅ **Visual states** - Waiting (orange pulsing), responded (green), timeout (red)
- ✅ **Quick-nav badge integration** - Orange pulsing when waiting for input
- ✅ **Notification system** - Alerts user when input is needed
- ✅ **Input disable/enable** - Prevents regular messages while AI waits
- ✅ **Timeout handling** - Auto-cleanup with countdown timer
- ✅ **WebSocket integration** - Real-time two-way communication

## 📦 Files Created

### 1. **agent-interaction-bubbles.js** (530 lines)
Core JavaScript module for rendering inline interaction bubbles.

**Location:** `UI/modules_internal/agents/agent-interaction-bubbles.js`

**Public API:**
```javascript
window.AgentInteractionBubbles = {
  renderInputRequestBubble(agentId, data),
  renderProgressBubble(agentId, data),
  submitInput(agentId, requestId),
  submitChoice(agentId, requestId, choice),
  cancelInput(agentId, requestId)
}
```

### 2. **agent-interaction-bubbles.css** (400+ lines)
Complete styling for interaction bubbles with animations.

**Location:** `UI/modules_internal/agents/agent-interaction-bubbles.css`

**Key Styles:**
- `.ai-interaction-request` - Base bubble container
- `.waiting`, `.responded`, `.timeout` - State classes
- `.pulsing-orange` - Avatar animation
- `.interaction-input-field` - Text/password inputs
- `.interaction-choice-btn` - Choice buttons
- `.progress-bar-container` - Progress bar
- `.agent-quick-nav-badge.waiting` - Badge state

### 3. **agent-interaction-websocket.js** (300+ lines)
WebSocket client for real-time communication with StreamingManager backend.

**Location:** `UI/modules_internal/agents/agent-interaction-websocket.js`

**Public API:**
```javascript
window.AgentInteractionWebSocket = {
  connect(agentId, sessionId, wsUrl),
  disconnect(agentId),
  sendMessage(agentId, message),
  sendInputResponse(agentId, requestId, value),
  isConnected(agentId),
  getConnection(agentId)
}
```

## 🚀 Integration Steps

### Step 1: Add Script Tags to HTML

Add these scripts to your agent UI HTML file (e.g., `agent-column.html` or main HTML):

```html
<!-- Inline Interaction System -->
<link rel="stylesheet" href="modules_internal/agents/agent-interaction-bubbles.css">
<script src="modules_internal/agents/agent-interaction-bubbles.js"></script>
<script src="modules_internal/agents/agent-interaction-websocket.js"></script>
```

**Load Order:** CSS → Bubbles JS → WebSocket JS

### Step 2: Initialize WebSocket Connection

When agent starts or user logs in, connect to StreamingManager:

```javascript
// Example: Initialize when agent column is created
function initializeAgentWebSocket(agentId, sessionId) {
    const wsUrl = 'ws://localhost:8080/ws/streaming'; // Your backend URL
    
    AgentInteractionWebSocket.connect(agentId, sessionId, wsUrl);
    
    console.log(`Agent ${agentId} connected to WebSocket`);
}

// Call when agent is ready
initializeAgentWebSocket(1, 'session-abc-123');
```

### Step 3: Backend Integration

Your backend (StreamingManager) should send messages in this format:

#### Input Request Message
```python
# streaming_manager.py
def request_user_input(self, prompt, input_type='text', choices=None, 
                      required=True, timeout_seconds=300, metadata=None):
    message = {
        'type': 'input_request',
        'request_id': str(uuid.uuid4()),
        'prompt': prompt,
        'input_type': input_type,  # text, password, choice, 2fa_code, captcha
        'choices': choices,  # For choice type
        'required': required,
        'timeout_seconds': timeout_seconds,
        'metadata': metadata or {}  # Can include screenshot, captcha_url
    }
    await self.websocket.send(json.dumps(message))
```

#### Progress Update Message
```python
def stream_progress(self, message, current_step, total_steps):
    percent = int((current_step / total_steps) * 100)
    message = {
        'type': 'progress_update',
        'message': message,
        'current_step': current_step,
        'total_steps': total_steps,
        'percent': percent
    }
    await self.websocket.send(json.dumps(message))
```

#### Receiving User Input
```python
async def handle_message(self, message):
    data = json.loads(message)
    
    if data['type'] == 'provide_input':
        request_id = data['request_id']
        input_value = data['input_value']
        
        # Resume AI task with user input
        self.resume(input_value)
```

### Step 4: Test with Mock Data (Optional)

Test the system without backend WebSocket:

```javascript
// Test input request bubble
AgentInteractionBubbles.renderInputRequestBubble(1, {
    request_id: 'test-123',
    prompt: 'Enter your 2FA authentication code',
    input_type: '2fa_code',
    required: true,
    timeout_seconds: 300,
    metadata: {}
});

// Test progress bubble
AgentInteractionBubbles.renderProgressBubble(1, {
    message: 'Processing documents...',
    current_step: 3,
    total_steps: 10,
    percent: 30
});
```

## 📖 Usage Examples

### Example 1: Text Input Request
```javascript
// AI agent needs user to provide file path
AgentInteractionBubbles.renderInputRequestBubble(1, {
    request_id: 'file-path-123',
    prompt: 'Please enter the path to the configuration file',
    input_type: 'text',
    required: true,
    timeout_seconds: 180
});
```

**Result:**
- Inline bubble appears in agent's message container
- Text input field with focus
- "Waiting for your response" orange badge
- Quick-nav badge turns orange and pulses
- Notification: "Alpha needs your input"
- Regular input disabled

### Example 2: Multiple Choice
```javascript
// AI agent needs user to choose deployment environment
AgentInteractionBubbles.renderInputRequestBubble(2, {
    request_id: 'env-choice-456',
    prompt: 'Select the deployment environment',
    input_type: 'choice',
    choices: ['Development', 'Staging', 'Production'],
    required: true,
    timeout_seconds: 120
});
```

**Result:**
- Inline bubble with 3 choice buttons
- User clicks button → marked as responded
- Green checkmark shows selected choice
- Regular input re-enabled
- Quick-nav badge returns to green

### Example 3: 2FA Code with Screenshot
```javascript
// AI agent shows 2FA QR code and needs user to enter code
AgentInteractionBubbles.renderInputRequestBubble(3, {
    request_id: '2fa-789',
    prompt: 'Scan the QR code and enter your 2FA authentication code',
    input_type: '2fa_code',
    required: true,
    timeout_seconds: 600,
    metadata: {
        screenshot: 'iVBORw0KGgoAAAANSUhEUgAA...'  // Base64 QR code image
    }
});
```

**Result:**
- Inline bubble with QR code image
- 6-digit input field (auto-focus)
- 10-minute timeout countdown
- Submit button validates 6 digits

### Example 4: Live Progress Updates
```javascript
// AI agent shows real-time progress
AgentInteractionBubbles.renderProgressBubble(1, {
    message: 'Downloading dependencies...',
    current_step: 5,
    total_steps: 20,
    percent: 25
});

// Update progress (reuses same bubble)
setTimeout(() => {
    AgentInteractionBubbles.renderProgressBubble(1, {
        message: 'Installing packages...',
        current_step: 10,
        total_steps: 20,
        percent: 50
    });
}, 2000);
```

**Result:**
- Inline progress bubble with animated bar
- Updates in-place without creating new bubbles
- Shows: "5 / 20 (25%)" → "10 / 20 (50%)"
- Spinning sync icon in avatar

## 🎨 Visual States

### Waiting State (Default)
- **Border:** Orange pulsing animation
- **Badge:** "Waiting for your response" with clock icon
- **Avatar:** Orange pulsing hand icon
- **Quick-nav badge:** Orange with pulsing animation
- **Notification:** "Agent needs your input"
- **Input:** Regular agent input disabled

### Responded State
- **Border:** Green solid
- **Badge:** "You responded: [value]" with checkmark
- **Avatar:** Static (no animation)
- **Quick-nav badge:** Brief green, then returns to has-thread
- **Input:** Regular agent input re-enabled

### Timeout State
- **Border:** Red solid
- **Badge:** "Request timed out" with exclamation icon
- **Avatar:** Static red
- **Opacity:** 70% (faded)
- **Input:** Regular agent input re-enabled

### Cancelled State
- **Border:** Gray solid
- **Badge:** "Cancelled by user"
- **Opacity:** 60% (faded)
- **Input:** Regular agent input re-enabled

## 🔧 Customization

### Change Timeout Duration
```javascript
// Default: 300 seconds (5 minutes)
AgentInteractionBubbles.renderInputRequestBubble(1, {
    // ...
    timeout_seconds: 600  // 10 minutes
});
```

### Custom Input Validation
Edit `submitInput()` function in `agent-interaction-bubbles.js`:

```javascript
function submitInput(agentId, requestId) {
    const input = document.querySelector(`input[data-request-id="${requestId}"]`);
    const value = input.value.trim();
    
    // Add custom validation
    if (value.length < 3) {
        input.classList.add('error');
        showNotification('Input must be at least 3 characters', 'warning');
        return;
    }
    
    // ... rest of submit logic
}
```

### Custom Choice Button Styling
Edit `.interaction-choice-btn` in `agent-interaction-bubbles.css`:

```css
.interaction-choice-btn {
    padding: 16px 20px;  /* Larger buttons */
    font-size: 16px;
    background: linear-gradient(135deg, #1a1d2e, #252837);
}
```

## 🐛 Troubleshooting

### Issue: Bubbles not appearing
**Check:**
1. Scripts loaded in correct order (CSS → Bubbles JS → WebSocket JS)
2. `AgentInteractionBubbles` exists in `window` object
3. Messages container exists: `#agent-messages-1` (or correct agent ID)
4. Console errors for missing elements

### Issue: WebSocket not connecting
**Check:**
1. Backend StreamingManager running
2. Correct WebSocket URL (check port, protocol)
3. Session ID valid
4. Console logs for connection errors
5. CORS settings on backend

### Issue: Input not submitting
**Check:**
1. `AgentInteractionWebSocket` module loaded
2. WebSocket connection open (`isConnected(agentId)` returns true)
3. Request ID matches
4. Console logs for send errors

### Issue: Quick-nav badge not updating
**Check:**
1. Badge element exists: `.agent-quick-nav-badge` for agent
2. CSS loaded: `.waiting` class defined
3. `updateQuickNavBadge()` function called

### Issue: Timeout not working
**Check:**
1. `startTimeoutCountdown()` called with correct seconds
2. Interval not cleared prematurely
3. Bubble element still exists in DOM

## 📊 Data Flow

```
┌─────────────────┐
│  AI Agent Task  │
│   (Backend)     │
└────────┬────────┘
         │
         │ 1. Needs user input
         ▼
┌─────────────────────────┐
│  StreamingManager       │
│  request_user_input()   │
└──────────┬──────────────┘
           │
           │ 2. WebSocket message
           │    (input_request)
           ▼
┌─────────────────────────────┐
│  AgentInteractionWebSocket  │
│  handleInputRequest()       │
└──────────┬──────────────────┘
           │
           │ 3. Render inline bubble
           ▼
┌──────────────────────────────┐
│  AgentInteractionBubbles     │
│  renderInputRequestBubble()  │
└──────────┬───────────────────┘
           │
           │ 4. Display in messages container
           │    - Orange pulsing avatar
           │    - Input field
           │    - Timeout countdown
           │    - Disable regular input
           │    - Update badge
           │    - Send notification
           ▼
┌─────────────────┐
│  User sees      │
│  inline bubble  │
│  and responds   │
└────────┬────────┘
         │
         │ 5. User clicks Submit
         ▼
┌───────────────────────┐
│  submitInput()        │
│  → sendInputResponse()│
└────────┬──────────────┘
         │
         │ 6. WebSocket message
         │    (provide_input)
         ▼
┌─────────────────────────┐
│  StreamingManager       │
│  provide_input()        │
└──────────┬──────────────┘
           │
           │ 7. Resume AI task
           ▼
┌─────────────────┐
│  AI Agent Task  │
│  continues...   │
└─────────────────┘
```

## ✅ Completion Checklist

- [x] **Core JavaScript logic** (`agent-interaction-bubbles.js`)
  - [x] Input request rendering
  - [x] Progress update rendering
  - [x] Submit/cancel handlers
  - [x] Timeout countdown
  - [x] Input disable/enable
  - [x] Badge state management

- [x] **CSS Styling** (`agent-interaction-bubbles.css`)
  - [x] Bubble styles with state classes
  - [x] Pulsing animations
  - [x] Input field styling
  - [x] Choice button styling
  - [x] Progress bar styling
  - [x] Quick-nav badge states

- [x] **WebSocket Integration** (`agent-interaction-websocket.js`)
  - [x] Connection management
  - [x] Message handlers
  - [x] Send input response
  - [x] Reconnection logic
  - [x] Error handling

- [ ] **Backend Integration** (Pending)
  - [ ] Update StreamingManager to send messages
  - [ ] Handle provide_input messages
  - [ ] Test end-to-end flow

- [ ] **HTML Integration** (Pending)
  - [ ] Add script tags to agent UI
  - [ ] Initialize WebSocket connections
  - [ ] Test with multiple agents

- [ ] **Testing** (Pending)
  - [ ] Test all input types
  - [ ] Test timeout handling
  - [ ] Test cancel functionality
  - [ ] Test multiple concurrent requests
  - [ ] Test reconnection

## 🚀 Next Steps

1. **Add script tags to agent UI HTML**
   - Link CSS and JS files
   - Ensure correct load order

2. **Initialize WebSocket connections**
   - Get session IDs from backend
   - Call `AgentInteractionWebSocket.connect()` for each agent

3. **Update backend StreamingManager**
   - Send `input_request` messages
   - Handle `provide_input` responses
   - Test with Python backend

4. **Test with real data**
   - Run agent tasks that need user input
   - Verify inline bubbles appear correctly
   - Check WebSocket message flow

5. **Polish and optimize**
   - Add loading states
   - Improve error messages
   - Add analytics/logging

## 📞 Support

**Created by:** GitHub Copilot  
**Date:** December 16, 2025  
**Status:** Ready for integration testing

**Questions?** Check console logs for detailed debugging information.
