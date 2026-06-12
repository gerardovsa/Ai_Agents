# Three Production Warnings Analysis - January 19, 2026

## Summary

Three non-critical warnings appearing in production logs during agent execution:
1. ⚠️ **Missing user_id for tool execution** - Registry warning when executing authentication-required tools
2. 🚨 **Flask app context missing** - WebSocket broadcast failing due to background thread context
3. ⚠️ **WebSocket data missing user_id** - Broadcast payload lacks user_id field

**Impact:** Low - All are warnings, not errors. Agent execution continues successfully. WebSocket broadcasts fail silently.

---

## Warning 1: No user_id Available for Tool Execution

### Log Message
```
WARNING:tools.registry_v3: [EXECUTE_TOOL] No user_id available for tool '{tool_name}' - authentication-required tools may fail
```

### Analysis

**File:** [tools/registry_v3.py](tools/registry_v3.py#L663)

**Issue:** The tool registry can't find `user_id` when executing tools from background worker threads.

**Why It Happens:**
1. `execute_streaming_request()` runs in background thread (via combined_agent_worker.py)
2. Thread-local storage (`thread_context.user_id`) is set BUT
3. Registry tries to get user_id from Flask `g` context first (line 655)
4. Background threads don't have Flask request context → import fails
5. Falls back to thread-local storage, but warning already logged

**Current Code (lines 655-663):**
```python
try:
    from flask import g as flask_g
    flask_user_id = getattr(flask_g, 'user_id', None)
    if flask_user_id:
        user_id = flask_user_id
        logger.debug(f"[EXECUTE_TOOL] Using user_id={user_id} from Flask g context")
except (ImportError, RuntimeError):
    # Not in Flask context or outside request
    pass

# Log if user_id still not found (warning - tools may fail)
if not user_id:
    logger.warning(f"[EXECUTE_TOOL] No user_id available for tool '{tool_name}' - authentication-required tools may fail")
```

**Problem:** The warning is logged BEFORE checking thread-local storage.

**Expected Flow:**
1. Check Flask `g` context → fails (background thread)
2. Check thread-local storage → succeeds (user_id IS there)
3. Only warn if BOTH fail

**Current Flow:**
1. Check Flask `g` context → fails
2. Warning logged immediately ❌
3. Later code finds user_id in thread-local storage ✅ (but warning already shown)

### Fix

Move the warning check to AFTER all user_id retrieval attempts:

**File:** [tools/registry_v3.py](tools/registry_v3.py#L655-L675)

```python
# Try Flask g context first
try:
    from flask import g as flask_g
    flask_user_id = getattr(flask_g, 'user_id', None)
    if flask_user_id:
        user_id = flask_user_id
        logger.debug(f"[EXECUTE_TOOL] Using user_id={user_id} from Flask g context")
except (ImportError, RuntimeError):
    # Not in Flask context or outside request
    pass

# ✅ FIX: Check thread-local storage BEFORE warning
if not user_id:
    try:
        from AI_infrastructure.core.thread_context import thread_context
        thread_user_id = getattr(thread_context, 'user_id', None)
        if thread_user_id:
            user_id = thread_user_id
            logger.debug(f"[EXECUTE_TOOL] Using user_id={user_id} from thread-local storage")
    except (ImportError, AttributeError):
        pass

# Only warn if BOTH Flask g and thread-local failed
if not user_id:
    logger.warning(f"[EXECUTE_TOOL] No user_id available for tool '{tool_name}' - authentication-required tools may fail")
```

**Impact:** Eliminates false-positive warning when user_id IS available via thread-local storage.

---

## Warning 2: Flask Application Context Missing

### Log Message
```
[STREAM] ⚠️ Failed to broadcast agent_thread_updated: Working outside of application context.
This typically means that you attempted to use functionality that needed
the current application. To solve this, set up an application context
with app.app_context(). See the documentation for more information.
```

### Analysis

**File:** [AI_infrastructure/routes/agent_routes_v4.py](AI_infrastructure/routes/agent_routes_v4.py#L2015)

**Issue:** WebSocket broadcast code tries to access `current_app` from background thread without app context.

**Current Code (lines 1988-2015):**
```python
def _broadcast_agent_thread_updated(event_payload: Dict[str, Any]):
    """Best-effort Socket.IO broadcast to other Command Center clients."""
    try:
        # Ensure we're in application context
        from flask import has_app_context
        if not has_app_context():
            # If we're outside app context, push one
            with current_app.app_context():
                socketio_ext = getattr(current_app, 'extensions', {}).get('socketio')
                if socketio_ext:
                    # Broadcast to all clients in the Command Center room.
                    socketio_ext.emit(
                        'agent_thread_updated',
                        event_payload,
                        room='command_center',
                        namespace='/ws/synergy'
                    )
            return
        
        socketio_ext = getattr(current_app, 'extensions', {}).get('socketio')
        if not socketio_ext:
            return

        # Broadcast to all clients in the Command Center room.
        socketio_ext.emit(
            'agent_thread_updated',
            event_payload,
            room='command_center',
            namespace='/ws/synergy'
        )
    except Exception as e:
        # Never break the SSE stream because of a realtime broadcast failure
        print(f"[STREAM] ⚠️ Failed to broadcast agent_thread_updated: {e}")
```

**Problem:** The code checks `has_app_context()` and pushes context with `current_app.app_context()`, but `current_app` itself requires app context to access! Classic chicken-egg problem.

**Why Error Occurs:**
1. Background thread calls `_broadcast_agent_thread_updated()`
2. `has_app_context()` returns `False`
3. Code tries `with current_app.app_context():`
4. Accessing `current_app` REQUIRES app context → RuntimeError
5. Exception caught, warning logged, broadcast fails

### Fix

Store app reference in function closure OR use app instance directly:

**Option 1: Store app reference (preferred)**

```python
def _broadcast_agent_thread_updated(event_payload: Dict[str, Any]):
    """Best-effort Socket.IO broadcast to other Command Center clients."""
    try:
        # ✅ FIX: Get app instance before checking context
        from flask import current_app, has_app_context
        
        # Store app reference (accessible even without context)
        app_instance = current_app._get_current_object() if has_app_context() else None
        
        if not app_instance:
            # Fallback: Import app from flask_app module
            try:
                import sys
                from pathlib import Path
                sys.path.insert(0, str(Path(__file__).parent.parent))
                from flask_app import app as flask_app_instance
                app_instance = flask_app_instance
            except ImportError:
                logger.warning("[STREAM] Cannot access Flask app for WebSocket broadcast")
                return
        
        # Now push app context safely
        with app_instance.app_context():
            socketio_ext = getattr(app_instance, 'extensions', {}).get('socketio')
            if socketio_ext:
                socketio_ext.emit(
                    'agent_thread_updated',
                    event_payload,
                    room='command_center',
                    namespace='/ws/synergy'
                )
    except Exception as e:
        print(f"[STREAM] ⚠️ Failed to broadcast agent_thread_updated: {e}")
```

**Option 2: Pass app instance as parameter (cleaner)**

Modify function signature to accept app instance:

```python
def _broadcast_agent_thread_updated(event_payload: Dict[str, Any], app_instance=None):
    """Best-effort Socket.IO broadcast to other Command Center clients."""
    try:
        if not app_instance:
            from flask import current_app
            app_instance = current_app._get_current_object()
        
        with app_instance.app_context():
            socketio_ext = getattr(app_instance, 'extensions', {}).get('socketio')
            if socketio_ext:
                socketio_ext.emit(
                    'agent_thread_updated',
                    event_payload,
                    room='command_center',
                    namespace='/ws/synergy'
                )
    except Exception as e:
        print(f"[STREAM] ⚠️ Failed to broadcast agent_thread_updated: {e}")
```

Then at route level (where app context exists), pass `current_app`:

```python
# At top of route function (inside Flask request context)
from flask import current_app
app_for_broadcast = current_app._get_current_object()

# Later in generator:
_broadcast_agent_thread_updated(payload, app_instance=app_for_broadcast)
```

**Impact:** WebSocket broadcasts will work from background threads, Command Center will update in real-time.

---

## Warning 3: WebSocket Broadcast Missing user_id

### Log Message
```
WARNING:flask_app: [WARNING] [WS] Cannot broadcast agent message - no user_id in data
```

### Analysis

**File:** [AI_infrastructure/flask_app.py](AI_infrastructure/flask_app.py#L2019)

**Issue:** WebSocket event data doesn't include `user_id` field when broadcast is called.

**Current Code (lines 2010-2020):**
```python
if not thread_id or not message:
    log_warning(logger, "[WS] Invalid agent_message_sent - missing thread_id or message")
    return

# Get user_id from data (WebSocket data includes user_id)
user_id = data.get('user_id')

if not user_id:
    log_warning(logger, "[WS] Cannot broadcast agent message - no user_id in data")
    return
```

**Problem:** The event payload doesn't contain `user_id`.

**Where Event is Emitted:**
Looking at agent_routes_v4.py lines 2050-2070, the broadcast payload is:

```python
_broadcast_agent_thread_updated({
    'agent_id': agent_id,
    'thread_slug': thread_slug,
    'message_count': event.get('message_count'),
    'timestamp': int(datetime.utcnow().timestamp() * 1000)
})
# ❌ Missing: 'user_id' field
```

### Fix

Add `user_id` to broadcast payload:

**File:** [AI_infrastructure/routes/agent_routes_v4.py](AI_infrastructure/routes/agent_routes_v4.py#L2050-L2070)

```python
# When the backend finishes persisting the authoritative conversation, notify
# other browser sessions so they can refresh their agent columns.
if event_type == 'conversation_sync':
    _broadcast_agent_thread_updated({
        'agent_id': agent_id,
        'thread_slug': thread_slug,
        'message_count': event.get('message_count'),
        'timestamp': int(datetime.utcnow().timestamp() * 1000),
        'user_id': user_id  # ✅ FIX: Add user_id to payload
    })
    did_broadcast_update = True

# Fallback: if the worker never emitted conversation_sync but does emit complete,
# still notify other sessions that this thread changed.
if event_type == 'complete' and not did_broadcast_update:
    _broadcast_agent_thread_updated({
        'agent_id': agent_id,
        'thread_slug': thread_slug,
        'message_count': event.get('message_count'),
        'timestamp': int(datetime.utcnow().timestamp() * 1000),
        'user_id': user_id  # ✅ FIX: Add user_id to payload
    })
    did_broadcast_update = True
```

**Note:** Verify `user_id` variable is in scope at this point. It's set earlier in the route function from request args:

```python
user_id = request.args.get('user_id', type=int)
```

**Impact:** WebSocket broadcasts will properly route to user rooms, enabling multi-session collaboration.

---

## Implementation Priority

1. **HIGH:** Warning 1 (user_id check) - False positive cluttering logs
2. **MEDIUM:** Warning 2 (app context) - Breaks real-time updates in Command Center
3. **MEDIUM:** Warning 3 (missing user_id) - Breaks WebSocket routing to user rooms

All three are safe to fix - they only affect logging and real-time features, not core agent functionality.

---

## Testing Checklist

### Warning 1: user_id Check
- [ ] Start agent conversation from UI
- [ ] Execute tool that requires authentication (e.g., calculate_folded_flyers_shopify)
- [ ] Verify NO warning "No user_id available for tool"
- [ ] Verify tool executes successfully
- [ ] Check logs show `[EXECUTE_TOOL] Using user_id=X from thread-local storage`

### Warning 2: App Context
- [ ] Start agent conversation from UI
- [ ] Monitor logs for "Failed to broadcast agent_thread_updated"
- [ ] Verify NO app context errors
- [ ] Open Command Center in second browser tab
- [ ] Start conversation in first tab
- [ ] Verify second tab shows real-time update

### Warning 3: user_id in Payload
- [ ] Start agent conversation from UI
- [ ] Monitor logs for "Cannot broadcast agent message - no user_id in data"
- [ ] Verify NO missing user_id warnings
- [ ] Check WebSocket message payload includes `user_id` field
- [ ] Verify broadcasts route to correct user room

---

## Related Files

**Tool Execution:**
- `tools/registry_v3.py` - Tool discovery and execution
- `AI_infrastructure/core/thread_context.py` - Thread-local storage for user_id
- `AI_infrastructure/core/combined_agent_worker.py` - Background worker with thread context

**WebSocket Broadcasting:**
- `AI_infrastructure/routes/agent_routes_v4.py` - SSE streaming routes
- `AI_infrastructure/flask_app.py` - WebSocket event handlers
- `UI/business-ai-platform-v2.html` - WebSocket client listeners

---

## Git Commit Message

```
fix(websockets): resolve three production warnings for broadcasts and tool auth

Warning 1: Check thread-local storage before logging user_id warning
- Move warning to after thread_context.user_id check in registry_v3.py
- Prevents false-positive when user_id exists in thread-local storage

Warning 2: Fix Flask app context access in background threads
- Store app instance before pushing context in agent_routes_v4.py
- Prevents "Working outside of application context" error

Warning 3: Add user_id to WebSocket broadcast payloads
- Include user_id in agent_thread_updated events
- Enables proper WebSocket routing to user rooms

Impact: Cleaner logs, working real-time updates in Command Center
```

---

**Status:** Analysis complete, fixes ready to implement  
**Date:** January 19, 2026  
**Severity:** Low (warnings only, no functional impact)  
**Recommendation:** Implement all three fixes together in single commit
