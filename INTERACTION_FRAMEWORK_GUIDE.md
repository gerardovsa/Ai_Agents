# 🎯 Two-Way Interaction Framework - Integration Guide

**Created:** December 16, 2025  
**Purpose:** Show how modules use the StreamingManager for live AI-human interaction

---

## 📋 Overview

The **Two-Way Interaction Framework** enables real-time bidirectional communication between AI agents and humans during long-running tasks. This is a **CORE PLATFORM FEATURE** available to all modules.

### Key Capabilities

✅ **Live Progress Streaming** - Real-time updates as tasks execute  
✅ **User Input Prompts** - AI can pause and ask humans for input (2FA, CAPTCHA, choices)  
✅ **Pause/Resume** - Users can pause tasks, review progress, and resume  
✅ **Screenshot/Action Streaming** - Live view of browser automation  
✅ **Multi-Participant** - Support for observers, collaborators, and AI agents  
✅ **Session Persistence** - Recovery from disconnections  

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Your Module                              │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  Task Function (async)                                    │ │
│  │  - Get StreamingSession                                   │ │
│  │  - Stream progress updates                                │ │
│  │  - Request user input when needed                         │ │
│  │  - Check for pause state                                  │ │
│  │  - Stream screenshots/actions                             │ │
│  │  - Complete with result                                   │ │
│  └──────────────────────────────────────────────────────────┘ │
│                     ↓                                           │
└─────────────────────┼───────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────────────┐
│              StreamingManager (Global Service)                  │
│                                                                 │
│  ┌────────────────────────────────────────────┐                │
│  │  StreamingSession                          │                │
│  │  - WebSocket connections                   │                │
│  │  - Progress state                          │                │
│  │  - Input request/response queue            │                │
│  │  - Pause/resume events                     │                │
│  │  - Participant management                  │                │
│  └────────────────────────────────────────────┘                │
│                     ↓                                           │
└─────────────────────┼───────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────────────┐
│                  Frontend (WebSocket Client)                    │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  UI Components                                            │ │
│  │  - Progress bar                                           │ │
│  │  - Status messages                                        │ │
│  │  - Input prompts (modal dialogs)                         │ │
│  │  - Pause/Resume controls                                 │ │
│  │  - Screenshot viewer                                     │ │
│  │  - Action log                                            │ │
│  └──────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📚 Core Components

### 1. StreamingManager (Singleton)

Global service that manages all streaming sessions.

```python
from AI_infrastructure.core.streaming_manager import get_streaming_manager

manager = get_streaming_manager()

# Create a new session
session = manager.create_session(
    task_name="Credential Verification",
    created_by="user_123"
)

# Get existing session
session = manager.get_session(session_id)

# List active sessions
active_sessions = manager.get_active_sessions()

# Cleanup old sessions
await manager.cleanup_inactive_sessions(max_age_hours=24)
```

### 2. StreamingSession

Represents a single task execution with live interaction.

```python
# Progress streaming
await session.stream_progress(
    current=2,
    total=5,
    message="Verifying GitHub profile...",
    metadata={"github_username": "john_doe"}
)

# User input request (BLOCKS until user responds)
code = await session.request_user_input(
    prompt="Enter your 2FA code:",
    input_type="2fa_code",
    timeout_seconds=300
)

# Pause/resume
await session.pause(reason="User requested pause")
await session.resume()

# Check if paused (tasks should call this periodically)
await session.wait_if_paused()

# Screenshot streaming
await session.stream_screenshot(
    screenshot_data="base64_encoded_image...",
    description="Credential search form",
    metadata={"url": "https://registry.example.com"}
)

# Action streaming (for computer use tasks)
await session.stream_action(
    action_type="form_fill",
    status="completed",
    description="Filled in candidate details",
    result={"fields_filled": 5}
)

# Logging
await session.log("Verification completed successfully", level="info")

# Complete
await session.complete(result={"verified": True, "risk_score": 15})

# Or fail
await session.fail(Exception("Network timeout"))
```

---

## 🎬 Usage Examples

### Example 1: Professional Verification with 2FA

```python
from AI_infrastructure.core.streaming_manager import get_streaming_manager
from AI_infrastructure.core.computer_use_executor import get_computer_use_executor
import anthropic

async def verify_candidate_credentials(
    session_id: str,
    candidate_data: dict
):
    """
    Verify candidate credentials using live interaction framework.
    
    This task:
    - Parses resume
    - Verifies GitHub (may need 2FA)
    - Searches credential registry (browser automation)
    - Compiles risk report
    """
    
    # Get session
    manager = get_streaming_manager()
    session = manager.get_session(session_id)
    
    if not session:
        raise ValueError("Session not found")
    
    try:
        session.started_at = datetime.now()
        session.state = SessionState.RUNNING
        
        # ===== STEP 1: Parse Resume =====
        await session.wait_if_paused()  # Check if user paused
        await session.stream_progress(1, 5, "Parsing resume...")
        
        resume_data = parse_resume(candidate_data['resume_path'])
        
        await session.log(f"Extracted {len(resume_data['claims'])} claims from resume")
        
        # ===== STEP 2: Verify GitHub =====
        await session.wait_if_paused()
        await session.stream_progress(2, 5, "Verifying GitHub profile...")
        
        github_url = resume_data.get('github_url')
        if github_url:
            github_result = await verify_github_profile(github_url)
            
            # GitHub may require 2FA
            if github_result.get('needs_2fa'):
                await session.log("GitHub requires 2FA authentication")
                
                # REQUEST USER INPUT - This blocks until user provides code
                code = await session.request_user_input(
                    prompt="GitHub requires a 2FA code. Please enter the code from your authenticator app:",
                    input_type="2fa_code",
                    required=True,
                    timeout_seconds=300  # 5 minutes
                )
                
                await session.log(f"Received 2FA code, authenticating...")
                
                # Continue verification with the code
                github_result = await verify_github_with_2fa(github_url, code)
        
        await session.log(f"GitHub verification: {github_result['status']}")
        
        # ===== STEP 3: Check Credential Registry (Browser Automation) =====
        await session.wait_if_paused()
        await session.stream_progress(3, 5, "Searching credential registry...")
        
        # Get browser container for computer use
        executor = get_computer_use_executor()
        container_id = await executor.get_browser_container()
        
        # Stream action: Navigate to registry
        await session.stream_action(
            action_type="navigate",
            status="started",
            description="Navigating to AHPRA registry search"
        )
        
        # Use Anthropic Computer Use to automate the search
        registry_result = await search_credential_registry_with_computer_use(
            session=session,  # Pass session for streaming
            container_id=container_id,
            candidate_data=candidate_data
        )
        
        await session.stream_action(
            action_type="navigate",
            status="completed",
            description="Registry search completed",
            result=registry_result
        )
        
        # Release container
        executor.release_container(container_id)
        
        # ===== STEP 4: Cross-check Business Registry =====
        await session.wait_if_paused()
        await session.stream_progress(4, 5, "Verifying company registration...")
        
        company_result = await verify_company_abn(candidate_data.get('company_abn'))
        
        # ===== STEP 5: Compile Results =====
        await session.wait_if_paused()
        await session.stream_progress(5, 5, "Compiling verification report...")
        
        # Calculate risk score
        risk_score = calculate_risk_score({
            'github': github_result,
            'credentials': registry_result,
            'company': company_result
        })
        
        # Final result
        result = {
            'verified': risk_score < 20,
            'risk_score': risk_score,
            'github_verification': github_result,
            'credential_verification': registry_result,
            'company_verification': company_result,
            'recommendation': 'APPROVED' if risk_score < 20 else 'NEEDS_REVIEW'
        }
        
        await session.complete(result)
        
    except Exception as e:
        await session.fail(e)
        raise


async def search_credential_registry_with_computer_use(
    session,
    container_id: str,
    candidate_data: dict
):
    """
    Use Anthropic Computer Use to search credential registry.
    Streams screenshots and actions to session.
    """
    
    anthropic_client = anthropic.Anthropic()
    executor = get_computer_use_executor()
    
    messages = [{
        "role": "user",
        "content": f"""
Search the AHPRA practitioner registry for:
- Name: {candidate_data['name']}
- Profession: {candidate_data['profession']}
- Registration Number: {candidate_data.get('registration_number', 'Not provided')}

Website: https://www.ahpra.gov.au/registration/registers-of-practitioners.aspx

Steps:
1. Navigate to the website
2. Find the search form
3. Enter the practitioner details
4. Extract the registration status and details
5. Take screenshots at each step
"""
    }]
    
    tools = [{
        "type": "computer_20241022",
        "name": "computer",
        "display_width_px": 1920,
        "display_height_px": 1080
    }]
    
    while True:
        # Call Claude with computer use tools
        response = anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            tools=tools,
            messages=messages
        )
        
        # Handle tool use
        if response.stop_reason == "tool_use":
            tool_results = []
            
            for block in response.content:
                if block.type == "tool_use" and block.name == "computer":
                    action = block.input.get("action")
                    
                    # Stream action to session
                    await session.stream_action(
                        action_type=action,
                        status="started",
                        description=f"Claude executing: {action}",
                        metadata=block.input
                    )
                    
                    # Execute the computer action
                    result = await executor.execute_computer_action(
                        container_id,
                        block.input
                    )
                    
                    # If screenshot, stream it to session
                    if action == "screenshot":
                        await session.stream_screenshot(
                            screenshot_data=result['source']['data'],
                            description="Current browser state"
                        )
                    
                    await session.stream_action(
                        action_type=action,
                        status="completed",
                        description=f"Action completed: {action}",
                        result=result
                    )
                    
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result) if isinstance(result, dict) else result
                    })
            
            # Continue conversation
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})
            
        elif response.stop_reason == "end_turn":
            # Extract final result from Claude's response
            final_text = ""
            for block in response.content:
                if block.type == "text":
                    final_text += block.text
            
            await session.log(f"Registry search completed: {final_text[:200]}...")
            
            # Parse result (Claude should return JSON with findings)
            return parse_registry_result(final_text)
```

### Example 2: Simple Task with Progress Updates

```python
from AI_infrastructure.core.streaming_manager import get_streaming_manager

async def process_documents(session_id: str, document_paths: list):
    """
    Simple document processing task with progress streaming.
    """
    
    manager = get_streaming_manager()
    session = manager.get_session(session_id)
    
    try:
        session.state = SessionState.RUNNING
        total = len(document_paths)
        
        for i, doc_path in enumerate(document_paths, 1):
            # Check if user paused
            await session.wait_if_paused()
            
            # Stream progress
            await session.stream_progress(
                current=i,
                total=total,
                message=f"Processing {doc_path.name}...",
                metadata={"file_size": doc_path.stat().st_size}
            )
            
            # Process document
            result = process_single_document(doc_path)
            
            await session.log(f"Processed {doc_path.name}: {result['pages']} pages")
        
        await session.complete({"processed_count": total})
        
    except Exception as e:
        await session.fail(e)
```

### Example 3: User Choice Prompt

```python
async def resolve_ambiguity(session: StreamingSession, candidates: list):
    """
    Ask user to choose when AI encounters ambiguity.
    """
    
    choice = await session.request_user_input(
        prompt="Multiple matching records found. Which one is correct?",
        input_type="choice",
        options=[
            f"{c['name']} - Registered {c['year']}" for c in candidates
        ],
        timeout_seconds=300
    )
    
    selected_candidate = candidates[choice]
    await session.log(f"User selected: {selected_candidate['name']}")
    
    return selected_candidate
```

---

## 🌐 WebSocket Integration (Backend)

### FastAPI WebSocket Endpoint

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from AI_infrastructure.core.streaming_manager import get_streaming_manager

app = FastAPI()

@app.websocket("/ws/streaming/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for streaming sessions.
    
    Clients connect here to receive live updates and send input responses.
    """
    await websocket.accept()
    
    manager = get_streaming_manager()
    session = manager.get_session(session_id)
    
    if not session:
        await websocket.send_json({"type": "error", "message": "Session not found"})
        await websocket.close()
        return
    
    # Add participant to session
    participant_id = await session.add_participant(websocket, participant_type="user")
    
    try:
        while True:
            # Receive messages from client
            data = await websocket.receive_json()
            message_type = data.get("type")
            
            if message_type == "input_response":
                # User provided input
                await session.provide_input(
                    input_value=data.get("value"),
                    from_participant=participant_id
                )
            
            elif message_type == "pause":
                await session.pause(reason=data.get("reason", "User requested pause"))
            
            elif message_type == "resume":
                await session.resume()
            
            elif message_type == "ping":
                await websocket.send_json({"type": "pong"})
    
    except WebSocketDisconnect:
        session.remove_participant(participant_id)
        await session.broadcast({
            "type": "participant_left",
            "participant_id": participant_id
        })
```

### Flask-SocketIO Integration (Alternative)

```python
from flask import Flask
from flask_socketio import SocketIO, emit, join_room
from AI_infrastructure.core.streaming_manager import get_streaming_manager

app = Flask(__name__)
socketio = SocketIO(app)

@socketio.on('join_session')
def handle_join_session(data):
    session_id = data.get('session_id')
    
    manager = get_streaming_manager()
    session = manager.get_session(session_id)
    
    if session:
        join_room(session_id)
        emit('session_joined', {
            'session_id': session_id,
            'state': session.state.value
        })
    else:
        emit('error', {'message': 'Session not found'})

@socketio.on('input_response')
def handle_input_response(data):
    session_id = data.get('session_id')
    value = data.get('value')
    
    manager = get_streaming_manager()
    session = manager.get_session(session_id)
    
    if session:
        asyncio.run(session.provide_input(value, from_participant="user"))
```

---

## 🎨 Frontend Integration

### JavaScript WebSocket Client

```javascript
class StreamingClient {
    constructor(sessionId) {
        this.sessionId = sessionId;
        this.ws = null;
        this.handlers = {};
    }
    
    connect() {
        this.ws = new WebSocket(`ws://localhost:8000/ws/streaming/${this.sessionId}`);
        
        this.ws.onopen = () => {
            console.log('Connected to streaming session');
            this.updateStatus('connected');
        };
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
        };
        
        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.updateStatus('error');
        };
        
        this.ws.onclose = () => {
            console.log('Disconnected from streaming session');
            this.updateStatus('disconnected');
        };
    }
    
    handleMessage(data) {
        const type = data.type;
        
        if (type === 'progress') {
            this.updateProgress(data.current_step, data.total_steps, data.message);
        }
        else if (type === 'input_request') {
            this.showInputPrompt(data);
        }
        else if (type === 'screenshot') {
            this.displayScreenshot(data.screenshot_data, data.description);
        }
        else if (type === 'action_started' || type === 'action_completed') {
            this.logAction(data.action_type, data.status, data.description);
        }
        else if (type === 'log') {
            this.addLogEntry(data.level, data.message);
        }
        else if (type === 'session_completed') {
            this.handleCompletion(data.result);
        }
        else if (type === 'session_failed') {
            this.handleFailure(data.error);
        }
        
        // Call registered handlers
        if (this.handlers[type]) {
            this.handlers[type](data);
        }
    }
    
    updateProgress(current, total, message) {
        const percentage = (current / total) * 100;
        const progressBar = document.getElementById('progress-bar');
        const progressText = document.getElementById('progress-text');
        
        if (progressBar) {
            progressBar.style.width = `${percentage}%`;
            progressBar.setAttribute('aria-valuenow', percentage);
        }
        
        if (progressText) {
            progressText.textContent = `${current}/${total}: ${message}`;
        }
    }
    
    showInputPrompt(request) {
        const modal = document.getElementById('input-modal');
        const prompt = document.getElementById('input-prompt');
        const inputField = document.getElementById('input-field');
        const submitBtn = document.getElementById('input-submit');
        
        prompt.textContent = request.prompt;
        inputField.value = '';
        inputField.type = request.input_type === 'password' ? 'password' : 'text';
        
        modal.style.display = 'block';
        inputField.focus();
        
        submitBtn.onclick = () => {
            this.sendInputResponse(inputField.value);
            modal.style.display = 'none';
        };
    }
    
    sendInputResponse(value) {
        this.ws.send(JSON.stringify({
            type: 'input_response',
            value: value
        }));
    }
    
    pause(reason) {
        this.ws.send(JSON.stringify({
            type: 'pause',
            reason: reason || 'User requested pause'
        }));
    }
    
    resume() {
        this.ws.send(JSON.stringify({
            type: 'resume'
        }));
    }
    
    displayScreenshot(base64Data, description) {
        const img = document.getElementById('screenshot-img');
        const caption = document.getElementById('screenshot-caption');
        
        if (img) {
            img.src = `data:image/png;base64,${base64Data}`;
        }
        
        if (caption) {
            caption.textContent = description;
        }
    }
    
    logAction(action, status, description) {
        const log = document.getElementById('action-log');
        const entry = document.createElement('div');
        entry.className = `log-entry log-${status}`;
        entry.textContent = `[${action}] ${status}: ${description}`;
        log.appendChild(entry);
        log.scrollTop = log.scrollHeight;
    }
    
    addLogEntry(level, message) {
        const log = document.getElementById('console-log');
        const entry = document.createElement('div');
        entry.className = `log-entry log-${level}`;
        entry.textContent = `[${level.toUpperCase()}] ${message}`;
        log.appendChild(entry);
        log.scrollTop = log.scrollHeight;
    }
    
    handleCompletion(result) {
        this.updateStatus('completed');
        console.log('Task completed:', result);
        
        // Show result modal or redirect
        alert('Task completed successfully!');
    }
    
    handleFailure(error) {
        this.updateStatus('failed');
        console.error('Task failed:', error);
        
        alert(`Task failed: ${error}`);
    }
    
    on(eventType, handler) {
        this.handlers[eventType] = handler;
    }
    
    updateStatus(status) {
        const statusEl = document.getElementById('session-status');
        if (statusEl) {
            statusEl.textContent = status;
            statusEl.className = `status status-${status}`;
        }
    }
}

// Usage
const client = new StreamingClient('session-id-here');
client.connect();

// Custom handlers
client.on('progress', (data) => {
    console.log(`Progress: ${data.message}`);
});

// Pause/Resume controls
document.getElementById('pause-btn').onclick = () => client.pause();
document.getElementById('resume-btn').onclick = () => client.resume();
```

### HTML UI Template

```html
<!DOCTYPE html>
<html>
<head>
    <title>Task Streaming</title>
    <style>
        .progress-container {
            width: 100%;
            background: #f0f0f0;
            border-radius: 5px;
            margin: 20px 0;
        }
        
        .progress-bar {
            height: 30px;
            background: #4CAF50;
            border-radius: 5px;
            transition: width 0.3s;
        }
        
        .status {
            padding: 5px 10px;
            border-radius: 3px;
            display: inline-block;
        }
        
        .status-connected { background: #4CAF50; color: white; }
        .status-paused { background: #FFC107; color: black; }
        .status-completed { background: #2196F3; color: white; }
        .status-failed { background: #F44336; color: white; }
        
        #action-log, #console-log {
            height: 200px;
            overflow-y: auto;
            border: 1px solid #ddd;
            padding: 10px;
            font-family: monospace;
            font-size: 12px;
        }
        
        .log-entry {
            margin: 2px 0;
        }
        
        .log-started { color: #2196F3; }
        .log-completed { color: #4CAF50; }
        .log-failed { color: #F44336; }
        
        #screenshot-img {
            max-width: 100%;
            border: 1px solid #ddd;
        }
        
        #input-modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 1000;
        }
        
        .modal-content {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            padding: 30px;
            border-radius: 5px;
            min-width: 400px;
        }
    </style>
</head>
<body>
    <h1>Task Streaming Demo</h1>
    
    <div>
        Status: <span id="session-status" class="status">connecting</span>
        <button id="pause-btn">Pause</button>
        <button id="resume-btn">Resume</button>
    </div>
    
    <div class="progress-container">
        <div id="progress-bar" class="progress-bar" style="width: 0%"></div>
    </div>
    <div id="progress-text">Initializing...</div>
    
    <h2>Action Log</h2>
    <div id="action-log"></div>
    
    <h2>Console Log</h2>
    <div id="console-log"></div>
    
    <h2>Current Screenshot</h2>
    <img id="screenshot-img" alt="No screenshot yet">
    <p id="screenshot-caption"></p>
    
    <!-- Input Modal -->
    <div id="input-modal">
        <div class="modal-content">
            <h3 id="input-prompt">Enter input:</h3>
            <input type="text" id="input-field" style="width: 100%; padding: 10px; margin: 10px 0;">
            <button id="input-submit">Submit</button>
        </div>
    </div>
    
    <script src="streaming-client.js"></script>
</body>
</html>
```

---

## 🚀 Best Practices

### 1. Always Check for Pause State

Tasks should periodically check if the user has paused:

```python
async def long_running_task(session):
    for step in steps:
        await session.wait_if_paused()  # ← Add this before each step
        await do_step(step)
```

### 2. Granular Progress Updates

Update progress at meaningful milestones:

```python
# GOOD ✅
await session.stream_progress(1, 5, "Parsing resume...")
await session.stream_progress(2, 5, "Verifying GitHub...")

# BAD ❌ - Too coarse
await session.stream_progress(1, 1, "Processing...")
```

### 3. Timeout User Input Requests

Always set reasonable timeouts:

```python
# GOOD ✅
code = await session.request_user_input(
    prompt="Enter 2FA code:",
    input_type="2fa_code",
    timeout_seconds=300  # 5 minutes
)

# BAD ❌ - No timeout (waits forever)
code = await session.request_user_input(
    prompt="Enter 2FA code:",
    input_type="2fa_code"
)
```

### 4. Handle Disconnections Gracefully

WebSocket disconnections should not break tasks:

```python
try:
    await session.broadcast(message)
except Exception as e:
    logger.warning(f"Broadcast failed: {e}")
    # Task continues even if no one is watching
```

### 5. Clean Up Resources

Release containers and cleanup sessions:

```python
try:
    container_id = await executor.get_browser_container()
    # ... use container ...
finally:
    executor.release_container(container_id)
```

---

## ✅ Complete Integration Checklist

### Backend

- [ ] Import `get_streaming_manager` in your module
- [ ] Create session when task starts
- [ ] Add WebSocket endpoint for frontend connection
- [ ] Implement progress streaming at key steps
- [ ] Add user input requests where needed
- [ ] Implement pause/resume checks
- [ ] Stream screenshots for computer use tasks
- [ ] Complete/fail session appropriately
- [ ] Cleanup sessions after completion

### Frontend

- [ ] Create WebSocket client connection
- [ ] Implement progress bar UI
- [ ] Add input prompt modal
- [ ] Add pause/resume controls
- [ ] Display screenshots and action log
- [ ] Handle session completion/failure
- [ ] Implement reconnection logic
- [ ] Add error handling

### Testing

- [ ] Test basic progress streaming
- [ ] Test user input flow (2FA, CAPTCHA)
- [ ] Test pause/resume functionality
- [ ] Test screenshot streaming
- [ ] Test multi-participant sessions
- [ ] Test disconnection/reconnection
- [ ] Test timeout handling
- [ ] Load test with multiple concurrent sessions

---

## 📞 Need Help?

See:
- [streaming_manager.py](../AI_infrastructure/core/streaming_manager.py) - Full implementation
- [computer_use_executor.py](../AI_infrastructure/core/computer_use_executor.py) - Browser automation
- [Professional Verification Module](../UI/modules_external/professional-verification/) - Real-world example

---

**Remember:** The Two-Way Interaction Framework is a **PLATFORM FEATURE** - use it whenever your module has long-running tasks that need user oversight or input! 🎯
