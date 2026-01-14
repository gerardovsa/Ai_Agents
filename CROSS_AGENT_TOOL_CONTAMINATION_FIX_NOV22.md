# Cross-Agent Tool Contamination Bug Fix - November 22, 2025

## **THE PROBLEM** 🚨

**Critical Cross-Contamination Bug:**
- Agent 1 sends message requiring tool use
- Agent 1 calls tools and gets results
- **AI Prime's UI receives Agent 1's tool events!**
- AI Prime shows repeated tool blocks (30 times)
- Agent 1 never gets completion signal
- Agent 1 hits "max 30 rounds exceeded" error

## **USER'S DESCRIPTION OF THE BUG**

```
1) Started conversation in AI Prime → finished successfully ✅
2) Reloaded UI → conversation persisted correctly ✅
3) Created new thread in Agent 1 → worked ✅
4) Sent simple request in Agent 1 → responded correctly ✅
5) Sent request in Agent 1 that needed tools → used tools and responded ✅
6) Then repeated tool use blocks started appearing in AI PRIME ❌
7) Repeated until 30 rounds → "max rounds exceeded" error in Agent 1 ❌
8) AI Prime was getting Agent 1's tool requests and results! ❌
```

**Key Insight from User:**
> "somehow AI prime chat message container got Agent 1 tool request in it and it got the result BUT maybe since this was in the wrong AI panel, Agent 1 did not get the close or complete? OR it triggered some kind of request retry in agent 1 but because it was going into AI prime it kept retrying"

---

## **ROOT CAUSE ANALYSIS**

### The Bug Flow

```
Agent 1 (agent-js.js):
  ✅ Correct URL: /api/agent/stream/1?thread_slug=thread_abc123
  → Sends to backend with agent_id=1
  → Backend streams to Agent 1's specific session
  
AI Prime (prime_ai_chat copy.js):
  ❌ WRONG URL: /api/agent/stream?session_id=session_xyz789&message=...
  → Missing agent_id parameter!
  → URL doesn't match backend route pattern
  → Either 404 or hits wrong endpoint
  → Receives events meant for other agents!
```

### Backend Route (Correct)

**File:** `AI_infrastructure/routes/agent_routes_v4.py`

```python
@agent_bp.route('/stream/<agent_id>', methods=['GET'])
def stream_agent(agent_id):
    """
    FIXED: Database as source of truth for streaming
    
    Loads conversation from DB instead of trusting frontend state
    """
    thread_slug = request.args.get('thread_slug') or request.args.get('session_id')
    # ... streaming logic
```

**Expected URL Pattern:** `/api/agent/stream/<agent_id>?thread_slug=...`

### Frontend Code

**Agent 1 (Correct) - `UI/modules/agents/agent-js.js` line 2929:**
```javascript
const streamUrl = `${window.API_BASE_URL || 'http://localhost:5001'}/api/agent/stream/${agentId}?thread_slug=${threadSlug}`;
```
✅ Includes `${agentId}` parameter  
✅ Uses `thread_slug` parameter  
✅ Matches backend route pattern

**AI Prime (WRONG) - `UI/modules/agents/prime_ai_chat copy.js` line 2831:**
```javascript
// BEFORE FIX (WRONG):
const eventSource = new EventSource(
    `${API_BASE_URL}/api/agent/stream?session_id=${sessionId}&message=${encodeURIComponent(message)}${promptParams}`
);
```
❌ Missing `agent_id` parameter!  
❌ Uses `session_id` instead of `thread_slug`  
❌ Includes `message` in URL (unnecessary for GET)  
❌ Doesn't match backend route pattern

---

## **THE FIX**

### Changed File: `UI/modules/agents/prime_ai_chat copy.js`

**Line 2831-2834:**

```javascript
// BEFORE (WRONG - Cross-contamination bug):
const eventSource = new EventSource(
    `${API_BASE_URL}/api/agent/stream?session_id=${sessionId}&message=${encodeURIComponent(message)}${promptParams}`
);

// AFTER (CORRECT - Agent-specific streaming):
const eventSource = new EventSource(
    `${API_BASE_URL}/api/agent/stream/prime?thread_slug=${sessionId}${promptParams}`
);
```

**Key Changes:**
1. ✅ Added `/prime` agent_id parameter
2. ✅ Changed `session_id` to `thread_slug` (matches backend)
3. ✅ Removed `&message=...` from URL (message loaded from database)
4. ✅ Kept `promptParams` for quick actions/library prompts

---

## **WHY THIS HAPPENED**

### URL Routing Mismatch

**Backend expects:**
```
/api/agent/stream/<agent_id>?thread_slug=<thread_slug>
                   ↑
                   Required path parameter
```

**AI Prime was sending:**
```
/api/agent/stream?session_id=<session_id>&message=<message>
                 ↑
                 Missing agent_id!
```

### Possible Scenarios

**Scenario 1: 404 Error (but handled by fallback)**
- AI Prime's request hits 404
- Flask fallback serves some generic response
- Or old chat_routes.py endpoint catches it

**Scenario 2: EventSource Sharing**
- Both AI Prime and Agent 1 using same EventSource connection pool
- Browser reuses connection for similar URLs
- Events broadcast to all connected clients

**Scenario 3: Server-Side Event Routing Bug**
- SSE (Server-Sent Events) not properly scoped to agent_id
- Events sent to all active EventSource connections
- No isolation between agent streams

---

## **VERIFICATION STEPS**

### Test 1: AI Prime Isolation
1. Open AI Prime panel
2. Send a message
3. Verify AI Prime receives ONLY its own events
4. Check browser console: `/api/agent/stream/prime?thread_slug=...`
5. Check no tool events from other agents appear

### Test 2: Agent 1 Isolation
1. Open Agent 1 panel
2. Send message requiring tools (e.g., "Search my emails")
3. Verify Agent 1 receives ONLY its own tool events
4. Check browser console: `/api/agent/stream/1?thread_slug=...`
5. Check AI Prime doesn't show Agent 1's tool calls

### Test 3: Concurrent Usage
1. Open both AI Prime and Agent 1
2. Send message in Agent 1 with tools
3. **Verify AI Prime remains idle** (no cross-contamination)
4. Send message in AI Prime
5. **Verify Agent 1 remains idle** (no cross-contamination)

### Test 4: Tool Loop Prevention
1. Send message in Agent 1 that uses 3-5 tools
2. Verify Agent 1 completes successfully
3. Check terminal logs: Should NOT see "Round 30" messages
4. Verify no "max rounds exceeded" error
5. Check AI Prime: Should show NO tool events

---

## **EXPECTED BEHAVIOR AFTER FIX**

### AI Prime Streaming
```
Browser: GET /api/agent/stream/prime?thread_slug=thread_abc123
    ↓
Backend: stream_agent(agent_id='prime')
    ↓
Loads conversation from sessions.messages WHERE thread_slug='thread_abc123'
    ↓
Streams AI Prime's response ONLY to AI Prime's EventSource
    ↓
AI Prime UI: Shows response ✅
Agent 1 UI: Shows nothing (isolated) ✅
```

### Agent 1 Streaming
```
Browser: GET /api/agent/stream/1?thread_slug=thread_xyz789
    ↓
Backend: stream_agent(agent_id='1')
    ↓
Loads conversation from sessions.messages WHERE thread_slug='thread_xyz789'
    ↓
Streams Agent 1's response ONLY to Agent 1's EventSource
    ↓
Agent 1 UI: Shows response with tool calls ✅
AI Prime UI: Shows nothing (isolated) ✅
```

---

## **RELATED FIXES**

### Conversation History Fix (Same Session)
This bug was discovered while fixing the conversation history persistence bug. Both issues were related to data flow between frontend and backend.

**Previous Fix:** `CONVERSATION_HISTORY_BUG_FIX_NOV22.md`
- Problem: Assistant messages not saving to database
- Cause: Python list passed instead of JSON string
- Fix: Added `json.dumps()` serialization

**This Fix:** `CROSS_AGENT_TOOL_CONTAMINATION_FIX_NOV22.md`
- Problem: Tool events bleeding between agents
- Cause: Missing `agent_id` in SSE URL
- Fix: Updated AI Prime URL format

---

## **TECHNICAL DETAILS**

### SSE (Server-Sent Events) Architecture

**How SSE Works:**
1. Client opens EventSource connection: `new EventSource(url)`
2. Server keeps connection open and streams events
3. Events are text/event-stream format
4. Client receives events via event listeners

**Critical for Isolation:**
- Each EventSource needs unique URL
- Server must route events to correct client
- URL must include agent_id for scoping

### Backend Route Pattern

```python
# Blueprint registration
app.register_blueprint(agent_bp, url_prefix='/api/agent')

# Route definition
@agent_bp.route('/stream/<agent_id>', methods=['GET'])
def stream_agent(agent_id):
    # <agent_id> is a path parameter (required)
    # thread_slug is a query parameter (optional)
    pass
```

**Full URL Pattern:**
```
/api/agent/stream/<agent_id>?thread_slug=<thread_slug>&param1=value1
│         │      │           │            │
│         │      │           │            └─ Optional query params
│         │      │           └────────────── Required query param
│         │      └────────────────────────── Required path param
│         └───────────────────────────────── Blueprint prefix
└─────────────────────────────────────────── Base URL
```

### Frontend EventSource Pattern

```javascript
// CORRECT PATTERN:
const agentId = 'prime'; // or '1', '2', etc.
const threadSlug = 'thread_abc123';
const url = `${API_BASE_URL}/api/agent/stream/${agentId}?thread_slug=${threadSlug}`;
const eventSource = new EventSource(url);

// Event listeners
eventSource.addEventListener('content_block_delta', (e) => {
    // Handle text chunks
});

eventSource.addEventListener('tool_use', (e) => {
    // Handle tool calls
});

eventSource.addEventListener('complete', (e) => {
    // Handle completion
    eventSource.close();
});
```

---

## **LESSONS LEARNED**

### Key Takeaways

1. **URL Consistency is Critical**
   - Frontend URLs must match backend route patterns EXACTLY
   - Path parameters (e.g., `<agent_id>`) are required, not optional
   - Query parameters can be optional but should match expectations

2. **Agent Isolation**
   - Each agent must have unique stream endpoint
   - Use agent_id in URL path for proper routing
   - Never share EventSource connections between agents

3. **SSE Debugging**
   - Check browser Network tab for actual URLs called
   - Verify EventSource connection URLs
   - Look for 404 errors or wrong endpoints
   - Monitor cross-contamination in console logs

4. **Testing Multi-Agent Systems**
   - Always test agents in isolation first
   - Then test concurrent usage
   - Watch for event bleeding between agents
   - Check terminal logs for routing issues

### Recommended Improvements

**1. Add URL validation:**
```javascript
function createAgentStreamUrl(agentId, threadSlug, params = {}) {
    if (!agentId) throw new Error('agent_id required for streaming');
    if (!threadSlug) throw new Error('thread_slug required for streaming');
    
    const queryParams = new URLSearchParams({
        thread_slug: threadSlug,
        ...params
    });
    
    return `${API_BASE_URL}/api/agent/stream/${agentId}?${queryParams}`;
}
```

**2. Add backend route validation:**
```python
@agent_bp.route('/stream/<agent_id>', methods=['GET'])
def stream_agent(agent_id):
    # Validate agent_id
    valid_agents = ['prime', '1', '2', '3', '4', '5']
    if agent_id not in valid_agents:
        return error_response(f"Invalid agent_id: {agent_id}", 400)
    
    # Validate thread_slug
    thread_slug = request.args.get('thread_slug')
    if not thread_slug:
        return error_response("thread_slug required", 400)
    
    # ... streaming logic
```

**3. Add EventSource connection logging:**
```javascript
console.log(`[STREAM] Opening EventSource for agent ${agentId}, thread ${threadSlug}`);
const eventSource = new EventSource(url);

eventSource.addEventListener('open', () => {
    console.log(`[STREAM] Connected to agent ${agentId}`);
});

eventSource.addEventListener('error', (e) => {
    console.error(`[STREAM] Error for agent ${agentId}:`, e);
});
```

---

## **STATUS**

**Fix Applied:** ✅ November 22, 2025  
**Files Changed:** 1 (`UI/modules/agents/prime_ai_chat copy.js`)  
**Lines Changed:** 1 (line 2832)  
**Tested:** 🔄 Ready for user testing  
**Deployed:** ⏳ Requires Flask restart

**Next Steps:**
1. Clear browser cache (F5 or Ctrl+Shift+R)
2. Test AI Prime streaming (check URL in Network tab)
3. Test Agent 1 with tools (verify no cross-contamination)
4. Test concurrent usage (both agents active)
5. Monitor terminal logs for "Round 30" messages
6. Close ticket if all tests pass

---

## **DEBUG CHECKLIST**

If the bug persists, check:

- [ ] Browser cache cleared (hard refresh: Ctrl+Shift+R)
- [ ] Flask server restarted with latest code
- [ ] Browser Network tab shows correct URL: `/api/agent/stream/prime?thread_slug=...`
- [ ] No 404 errors in Network tab
- [ ] Terminal logs show agent_id in stream requests
- [ ] No "Round 30" messages in terminal
- [ ] EventSource connections closed properly after completion
- [ ] No shared EventSource instances between agents

---

**Document Created:** November 22, 2025  
**Author:** GitHub Copilot (Claude Sonnet 4.5)  
**Issue:** Tool events bleeding between AI Prime and Agent 1  
**Resolution:** Missing agent_id in AI Prime's SSE URL - added `/prime` parameter
