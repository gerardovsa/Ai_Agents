# Thread Slug Fix - Agent Message Isolation (Nov 19, 2025)

## Problem

Agent Delta's responses were appearing in AI Prime's chat window. This was caused by thread ID collision:

**Root Cause:**
- Backend was using `thread_id` (numeric timestamp like "1763479637070") for thread identification
- Multiple threads can have the same numeric `thread_id` value
- The database has `thread_slug` (globally unique UUID) that should be used instead
- Result: Messages from Agent 4 appeared in Agent 1's chat because they shared the same numeric ID

## Solution

Changed backend to use `thread_slug` instead of `thread_id` for unique thread identification.

**Database Schema:**
```sql
sessions.threads table:
  - id (integer) - Auto-incrementing: 1, 2, 3, 4...
  - thread_slug (text) - Unique UUID: "1763479637070", "1763479326677", etc.
  - name (text) - Thread title
  - user_id (integer) - Owner
```

**Key Insight:**
- `thread_slug` is the UNIQUE identifier (timestamp-based UUID from thread creation)
- `id` is just a sequential counter (can collide across different threads)
- Backend state manager uses `{agent_id}_{thread_slug}` as the state key

## Backend Changes (Commit 858eb5d)

### Files Modified:
- `AI_infrastructure/routes/agent_routes_v4.py`

### Changes Made:

**1. Start Agent Endpoint (`/api/agent/agent/<id>/start`):**
```python
# BEFORE (WRONG):
thread_id = data.get('thread_id') or session_id  
state = agent_state_manager.get_or_create_state(agent_id, thread_id)

# AFTER (CORRECT):
thread_slug = data.get('thread_slug') or data.get('thread_id') or session_id
state = agent_state_manager.get_or_create_state(agent_id, thread_slug)
```

**2. Stream Endpoint (`/api/agent/stream/<agent_id>`):**
```python
# BEFORE (WRONG):
session_id = request.args.get('session_id')
thread_id = session_id
state = agent_state_manager.get_or_create_state(agent_id, thread_id)

# AFTER (CORRECT):
thread_slug = request.args.get('thread_slug') or request.args.get('session_id')
state = agent_state_manager.get_or_create_state(agent_id, thread_slug)
```

**3. Status/Messages/Clear Endpoints:**
All updated to use `thread_slug` instead of `thread_id`.

## Frontend Changes Required

### CRITICAL: Update API Calls

**1. Start Agent Request:**
```typescript
// BEFORE (WRONG):
await axios.post(`/api/agent/agent/${agentId}/start`, {
  message: userMessage,
  session_id: threadId,  // ❌ This is actually thread_slug!
  thread_id: threadId,   // ❌ Redundant and ambiguous
  conversation_history: [...],
  // ...
});

// AFTER (CORRECT):
await axios.post(`/api/agent/agent/${agentId}/start`, {
  message: userMessage,
  thread_slug: threadSlug,  // ✅ Use thread_slug explicitly
  session_id: threadId,     // Keep for backward compatibility
  conversation_history: [...],
  // ...
});
```

**2. Stream Connection:**
```typescript
// BEFORE (WRONG):
const eventSource = new EventSource(
  `/api/agent/stream/${agentId}?session_id=${threadId}`
);

// AFTER (CORRECT):
const eventSource = new EventSource(
  `/api/agent/stream/${agentId}?thread_slug=${threadSlug}`
);
```

### Where to Get thread_slug

From the thread data returned by `/api/threads/create`:

```typescript
// Thread creation response:
{
  "success": true,
  "thread": {
    "id": "1763479637070",  // This is the thread_slug!
    "title": "New Chat",
    "created": "2025-11-19T01:27:17.070Z",
    "agent_id": "4"
  }
}

// Use thread.id as thread_slug:
const threadSlug = thread.id;  // "1763479637070"
```

### Frontend State Management

Update your thread state to explicitly track `thread_slug`:

```typescript
interface Thread {
  id: number;              // Database auto-increment (1, 2, 3...)
  thread_slug: string;     // Unique UUID ("1763479637070")
  title: string;
  agent_id: string;
  created: string;
}

// When creating a new thread:
const thread = {
  thread_slug: response.data.thread.id,  // Use API response 'id' as thread_slug
  title: "New Chat",
  agent_id: currentAgent.id,
  // ...
};
```

## Testing Instructions

### Test Case 1: Single Agent, Multiple Threads
1. Open Agent Delta
2. Create Thread 1, send message "Hello from thread 1"
3. Create Thread 2, send message "Hello from thread 2"
4. Switch back to Thread 1
5. **EXPECTED**: Thread 1 shows "Hello from thread 1", not thread 2's message

### Test Case 2: Multiple Agents, Same Thread Number
1. Open AI Prime (Agent 1), create thread (gets thread_slug "1763479637070")
2. Open Agent Delta (Agent 4), create thread (gets thread_slug "1763479326677")
3. Send message to AI Prime: "This is for Prime"
4. Send message to Agent Delta: "This is for Delta"
5. **EXPECTED**: Prime's chat shows only "This is for Prime"
6. **EXPECTED**: Delta's chat shows only "This is for Delta"

### Test Case 3: Backward Compatibility
1. Frontend still sending `session_id` but NOT `thread_slug`
2. Backend should use `session_id` as fallback
3. **EXPECTED**: Messages still work, but use `session_id` value as thread identifier

## Deployment Checklist

### Backend (DONE ✅):
- [x] Updated `agent_routes_v4.py` to use `thread_slug`
- [x] Committed and pushed to v6 branch (commit 858eb5d)
- [x] Backend gracefully handles both `thread_slug` and `thread_id` for backward compatibility

### Frontend (TODO ⚠️):
- [ ] Update agent message sending to include `thread_slug`
- [ ] Update stream connection to use `thread_slug` query param
- [ ] Update thread state management to track `thread_slug`
- [ ] Test multi-agent, multi-thread scenarios
- [ ] Deploy frontend changes

## Backward Compatibility

The backend now accepts BOTH `thread_slug` and `thread_id`:

```python
# Priority order:
thread_slug = (
    data.get('thread_slug') or      # ✅ Preferred (unique)
    data.get('thread_id') or        # ⚠️  Fallback (may collide)
    session_id                      # ⚠️  Last resort
)
```

**Migration Path:**
1. Deploy backend first (DONE)
2. Update frontend to send `thread_slug`
3. Once frontend is updated, can eventually remove `thread_id` fallback

## Technical Details

### State Manager Key Format

```python
# State keys are now:
state_key = f"{agent_id}_{thread_slug}"

# Examples:
"1_1763479637070"  # AI Prime, thread 1763479637070
"4_1763479326677"  # Agent Delta, thread 1763479326677

# OLD (WRONG) - could collide:
"1_1"  # AI Prime, thread 1
"4_1"  # Agent Delta, thread 1  # ❌ COLLISION!
```

### Debugging

To debug thread isolation issues:

```python
# Backend logs show:
[START] thread_slug: 1763479637070
[START] State key: 4_1763479637070 (using thread_slug for isolation)

# Stream endpoint logs:
[Stream 4] Thread Slug: 1763479637070
[Stream 4] 🔍 DEBUG State Manager:
  - All state keys in manager: ['1_1763349948359', '1_1763479326677', '4_1763479637070']
  - ✅ State exists for key: 4_1763479637070
```

### Database Query

To verify thread slugs in database:

```sql
SELECT 
  id, 
  thread_slug, 
  name, 
  user_id,
  created_at
FROM sessions.threads
WHERE user_id = 14
ORDER BY created_at DESC;

-- Example results:
-- id | thread_slug     | name            | user_id
-- 4  | 1763479637070   | Agent Delta Chat| 14
-- 3  | 1763479326677   | AI Prime Chat   | 14
-- 2  | 1763349948359   | Test Thread     | 14
```

## Related Issues

- **Issue**: Agent Delta responses appearing in AI Prime chat
- **Symptom**: `thread_id: 1763479637070` used for both Agent 1 and Agent 4
- **Root Cause**: Numeric `thread_id` not globally unique
- **Fix**: Use `thread_slug` (globally unique UUID from database)

## Rollback Plan

If issues arise:

1. **Revert backend commit:**
```bash
git revert 858eb5d
git push origin v6
```

2. **Or use fallback:** Backend still accepts `thread_id` via fallback logic, so old frontend will continue working (with potential cross-contamination bug).

## Next Steps

1. **Frontend team**: Update API calls to send `thread_slug`
2. **Test locally**: Verify multi-agent, multi-thread scenarios
3. **Deploy**: Push frontend changes to production
4. **Monitor**: Check logs for `[START] thread_slug:` to verify correct values
5. **Cleanup**: After frontend is stable, remove `thread_id` fallback from backend

---

**Status**: Backend fix deployed (commit 858eb5d), frontend changes pending  
**Priority**: HIGH - Affects all multi-agent conversations  
**Owner**: Backend fixed by AI Assistant, frontend needs developer update  
**Date**: November 19, 2025
