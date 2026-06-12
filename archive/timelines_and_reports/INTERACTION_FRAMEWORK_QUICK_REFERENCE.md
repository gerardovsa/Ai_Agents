# 🚀 Two-Way Interaction Framework - Quick Reference

## 📦 Import

```python
from AI_infrastructure.core.streaming_manager import (
    get_streaming_manager,
    StreamingSession,
    SessionState,
    MessageType
)
```

## 🎯 Basic Usage

### Create Session

```python
manager = get_streaming_manager()
session = manager.create_session(
    task_name="My Long Task",
    created_by="user_123"
)
```

### Progress Updates

```python
await session.stream_progress(
    current=2,
    total=5,
    message="Processing data...",
    metadata={"file": "data.csv"}
)
```

### User Input (Blocks Until Response)

```python
# Text input
value = await session.request_user_input(
    prompt="Enter filename:",
    input_type="text"
)

# 2FA Code
code = await session.request_user_input(
    prompt="Enter 2FA code:",
    input_type="2fa_code",
    timeout_seconds=300
)

# Choice
choice = await session.request_user_input(
    prompt="Select option:",
    input_type="choice",
    options=["Option A", "Option B", "Option C"]
)

# Password
password = await session.request_user_input(
    prompt="Enter password:",
    input_type="password"
)
```

### Pause/Resume

```python
# Pause
await session.pause(reason="User requested pause")

# Check if paused (call this periodically in task)
await session.wait_if_paused()

# Resume
await session.resume()
```

### Screenshot Streaming

```python
await session.stream_screenshot(
    screenshot_data="base64_encoded_image...",
    description="Current browser state",
    metadata={"url": "https://example.com"}
)
```

### Action Streaming

```python
# Action started
await session.stream_action(
    action_type="form_fill",
    status="started",
    description="Filling search form"
)

# Action completed
await session.stream_action(
    action_type="form_fill",
    status="completed",
    description="Form submitted",
    result={"fields_filled": 5}
)
```

### Logging

```python
await session.log("Processing completed", level="info")
await session.log("Warning: slow response", level="warning")
await session.log("Error occurred", level="error")
```

### Complete/Fail

```python
# Success
await session.complete(result={
    "status": "success",
    "items_processed": 100
})

# Failure
try:
    # ... task code ...
except Exception as e:
    await session.fail(e)
```

## 🌐 WebSocket Integration

### FastAPI

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

@app.websocket("/ws/streaming/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    
    manager = get_streaming_manager()
    session = manager.get_session(session_id)
    
    participant_id = await session.add_participant(websocket)
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if data['type'] == 'input_response':
                await session.provide_input(data['value'], participant_id)
            elif data['type'] == 'pause':
                await session.pause(data.get('reason'))
            elif data['type'] == 'resume':
                await session.resume()
    
    except WebSocketDisconnect:
        session.remove_participant(participant_id)
```

### Flask-SocketIO

```python
from flask import Flask
from flask_socketio import SocketIO, emit, join_room

app = Flask(__name__)
socketio = SocketIO(app)

@socketio.on('join_session')
def handle_join(data):
    session_id = data['session_id']
    join_room(session_id)
    
    manager = get_streaming_manager()
    session = manager.get_session(session_id)
    
    emit('joined', {'state': session.state.value})

@socketio.on('input_response')
def handle_input(data):
    session_id = data['session_id']
    value = data['value']
    
    manager = get_streaming_manager()
    session = manager.get_session(session_id)
    
    asyncio.run(session.provide_input(value, "user"))
```

## 💻 Frontend (JavaScript)

### Connect

```javascript
const ws = new WebSocket(`ws://localhost:8000/ws/streaming/${sessionId}`);

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    handleMessage(data);
};
```

### Handle Messages

```javascript
function handleMessage(data) {
    switch(data.type) {
        case 'progress':
            updateProgress(data.current_step, data.total_steps, data.message);
            break;
        
        case 'input_request':
            showInputModal(data.prompt, data.input_type, data.options);
            break;
        
        case 'screenshot':
            displayScreenshot(data.screenshot_data, data.description);
            break;
        
        case 'session_completed':
            handleCompletion(data.result);
            break;
        
        case 'session_failed':
            handleFailure(data.error);
            break;
    }
}
```

### Send Input Response

```javascript
function submitInput(value) {
    ws.send(JSON.stringify({
        type: 'input_response',
        value: value
    }));
}
```

### Pause/Resume

```javascript
function pause() {
    ws.send(JSON.stringify({
        type: 'pause',
        reason: 'User requested pause'
    }));
}

function resume() {
    ws.send(JSON.stringify({
        type: 'resume'
    }));
}
```

## 🎬 Complete Example

```python
from AI_infrastructure.core.streaming_manager import get_streaming_manager
import asyncio

async def my_long_task(session_id: str, input_data: dict):
    """Example task with full interaction"""
    
    manager = get_streaming_manager()
    session = manager.get_session(session_id)
    
    try:
        session.state = SessionState.RUNNING
        session.started_at = datetime.now()
        
        # Step 1
        await session.wait_if_paused()
        await session.stream_progress(1, 4, "Loading data...")
        data = load_data(input_data['file'])
        
        # Step 2
        await session.wait_if_paused()
        await session.stream_progress(2, 4, "Processing...")
        
        # Need user input
        choice = await session.request_user_input(
            prompt="Found duplicates. How should we handle them?",
            input_type="choice",
            options=["Skip", "Merge", "Keep both"]
        )
        
        result = process_data(data, duplicate_strategy=choice)
        
        # Step 3
        await session.wait_if_paused()
        await session.stream_progress(3, 4, "Validating...")
        validation = validate(result)
        
        # Step 4
        await session.wait_if_paused()
        await session.stream_progress(4, 4, "Saving...")
        save(result)
        
        await session.complete({
            "records_processed": len(result),
            "duplicates_handled": choice
        })
        
    except Exception as e:
        await session.fail(e)
        raise
```

## 📊 Message Types Reference

| Type | Direction | Purpose |
|------|-----------|---------|
| `progress` | Server → Client | Progress update |
| `input_request` | Server → Client | Request user input |
| `input_response` | Client → Server | User's input |
| `screenshot` | Server → Client | Browser screenshot |
| `action_started` | Server → Client | Action began |
| `action_completed` | Server → Client | Action finished |
| `session_paused` | Server → Client | Session paused |
| `session_resumed` | Server → Client | Session resumed |
| `session_completed` | Server → Client | Task completed |
| `session_failed` | Server → Client | Task failed |
| `log` | Server → Client | Log message |
| `pause` | Client → Server | Pause request |
| `resume` | Client → Server | Resume request |

## ✅ Best Practices

1. **Always check pause state:**
   ```python
   await session.wait_if_paused()  # Before each major step
   ```

2. **Set timeouts for user input:**
   ```python
   code = await session.request_user_input(
       prompt="Enter code:",
       timeout_seconds=300  # Don't wait forever
   )
   ```

3. **Granular progress updates:**
   ```python
   # GOOD ✅
   await session.stream_progress(1, 5, "Parsing resume...")
   await session.stream_progress(2, 5, "Verifying GitHub...")
   
   # BAD ❌
   await session.stream_progress(1, 1, "Processing...")
   ```

4. **Handle disconnections gracefully:**
   ```python
   try:
       await session.broadcast(message)
   except Exception:
       pass  # Task continues even if no one is watching
   ```

5. **Clean up resources:**
   ```python
   try:
       # ... use resources ...
   finally:
       cleanup_resources()
   ```

## 📞 Full Documentation

- [INTERACTION_FRAMEWORK_GUIDE.md](./INTERACTION_FRAMEWORK_GUIDE.md) - Complete guide
- [AI_infrastructure/core/streaming_manager.py](./AI_infrastructure/core/streaming_manager.py) - Source code
- [TWO_WAY_INTERACTION_FRAMEWORK_COMPLETE.md](./TWO_WAY_INTERACTION_FRAMEWORK_COMPLETE.md) - Implementation summary

---

**Built for the AI Agent Platform - December 16, 2025** 🚀
