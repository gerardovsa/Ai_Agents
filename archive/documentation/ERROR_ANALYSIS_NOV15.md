# Critical Error Analysis - November 15, 2025

## 🔴 Error Summary

Your AI agent system is experiencing **THREE critical errors** that are preventing it from functioning properly:

---

## Error 1: Tool Use/Result Mismatch (MOST CRITICAL)

### Error Message:
```
anthropic.BadRequestError: Error code: 400
messages.1: `tool_use` ids were found without `tool_result` blocks immediately after: 
toolu_012i9mTS5RqeZo7ipniGwnSg, toolu_0164Xftp1dMkcjqkQ8BJE6Qq, ...
Each `tool_use` block must have a corresponding `tool_result` block in the next message.
```

### What This Means:
The AI agent made **8 tool calls** (like searching for documents, querying databases, etc.), but when sending the conversation back to Claude API, the tool results were **missing or incorrectly formatted**.

### Why It's Happening:
The `validate_conversation_history()` function in `combined_agent_worker.py` is **removing or misplacing** tool_result blocks during message validation.

### Impact:
- ❌ AI agent conversations fail immediately
- ❌ No tools can be executed
- ❌ User requests fail with 400 errors

### Root Cause Location:
```python
File: AI_infrastructure/core/combined_agent_worker.py
Line: ~268-380 (validate_conversation_history function)
Line: ~1052 (where error occurs when sending to Claude)
```

### What Should Happen:
```
Message 1 (user): "Find document test-doic"
Message 2 (assistant): [tool_use: synergy_get_internal_doc]
Message 3 (user): [tool_result: document data]  ← THIS IS MISSING!
Message 4 (assistant): "Here's the document..."
```

### What's Actually Happening:
```
Message 1 (user): "Find document test-doic"
Message 2 (assistant): [tool_use: synergy_get_internal_doc]
Message 3 (user): [EMPTY or MISSING]  ← ERROR!
```

---

## Error 2: Prompt Injection Content-Type Error

### Error Message:
```
[Stream 1] Error applying prompt injections: 415 Unsupported Media Type
Did not attempt to load JSON data because the request Content-Type was not 'application/json'
```

### What This Means:
Your user preferences are trying to be injected into the system prompt:
- Presentations: microsoft_powerpoint_* (NOT google_slides_*)
- Team Chat: microsoft_teams_* (NOT google_chat_*)
- Tasks: microsoft_todo_* (NOT google_tasks_*)
- Communication Style: casual
- Detail Level: comprehensive

But the HTTP request format is wrong.

### Why It's Happening:
The request being sent to the prompt injection system doesn't have the correct `Content-Type: application/json` header.

### Impact:
- ⚠️ Your Microsoft tool preferences aren't being applied
- ⚠️ AI uses Google tools instead of Microsoft tools
- ⚠️ Communication style defaults to formal instead of casual

### Root Cause Location:
```python
File: AI_infrastructure/routes/agent_routes_v4.py
Line: ~925-947 (prompt injection application)
```

### Fix Needed:
Ensure the request has proper headers:
```python
headers = {
    'Content-Type': 'application/json'
}
```

---

## Error 3: Missing Database Table

### Error Message:
```
[THREADS] Warning: Could not fetch agent assignments: no such table: thread_assignments
```

### What This Means:
The code is trying to query a table called `thread_assignments` to see which AI agent is assigned to which conversation thread, but the table doesn't exist in the database.

### Why It's Happening:
Database migration didn't create the table, or it was accidentally dropped.

### Impact:
- ⚠️ Agent assignments can't be tracked
- ⚠️ Multi-agent system can't route threads correctly
- ⚠️ Thread details API returns incomplete data

### Root Cause Location:
```python
File: AI_infrastructure/routes/thread_assignment_routes.py (or similar)
Database: data/ai_infrastructure.db
Missing Table: thread_assignments
```

### Expected Table Schema:
```sql
CREATE TABLE IF NOT EXISTS thread_assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_id TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    agent_id TEXT,
    agent_name TEXT,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

## 🎯 Priority Fix Order

### IMMEDIATE (Fix Now):
1. **Tool Use/Result Mismatch** - System is completely broken without this
   - Check why `validate_conversation_history()` is removing tool_results
   - Verify tool_result blocks are being inserted correctly in user messages
   - Add debug logging to trace where tool_results disappear

### HIGH (Fix Today):
2. **Prompt Injection Error** - Your preferences aren't working
   - Fix Content-Type header in prompt injection requests
   - Verify Microsoft tool preferences are being applied

### MEDIUM (Fix This Week):
3. **Missing Table** - Feature is broken but system still works
   - Create `thread_assignments` table
   - Add migration script
   - Test agent assignment tracking

---

## 🔍 Debug Steps to Take

### For Tool Use/Result Error:

1. **Add debug logging before sending to Claude:**
```python
# In combined_agent_worker.py around line 1050
print("[DEBUG] Messages being sent to Claude:")
for idx, msg in enumerate(messages):
    print(f"  Message {idx} ({msg['role']}):")
    if isinstance(msg['content'], list):
        for block in msg['content']:
            print(f"    - {block.get('type')}: {block.get('id', 'N/A')[:20]}")
```

2. **Check tool_result insertion:**
```python
# After tool execution (around line 1080-1100)
print(f"[DEBUG] Tool results to insert: {len(tool_results)}")
for tr in tool_results:
    print(f"  - tool_use_id: {tr.get('tool_use_id')}")
    print(f"  - has content: {'content' in tr}")
```

3. **Verify validation doesn't remove tool_results:**
```python
# In validate_conversation_history function
print(f"[DEBUG] Before validation: {len(messages)} messages")
# ... validation code ...
print(f"[DEBUG] After validation: {len(validated_messages)} messages")
```

### For Prompt Injection Error:

1. **Check request format:**
```python
# In agent_routes_v4.py around line 920
print(f"[DEBUG] Request content type: {request.content_type}")
print(f"[DEBUG] Request has JSON: {request.is_json}")
print(f"[DEBUG] Quick actions: {quick_actions}")
```

2. **Verify headers:**
```python
print(f"[DEBUG] Request headers: {dict(request.headers)}")
```

### For Missing Table:

1. **Check if table exists:**
```sql
SELECT name FROM sqlite_master 
WHERE type='table' AND name='thread_assignments';
```

2. **Create the table:**
```sql
CREATE TABLE IF NOT EXISTS thread_assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_id TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    agent_id TEXT,
    agent_name TEXT,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 📊 Error Impact Assessment

| Error | Severity | Impact | Users Affected | System State |
|-------|----------|--------|----------------|--------------|
| Tool Use/Result Mismatch | 🔴 CRITICAL | Complete failure | ALL | BROKEN |
| Prompt Injection | 🟡 HIGH | Wrong tools used | ALL | DEGRADED |
| Missing Table | 🟢 MEDIUM | Missing feature | Multi-agent users | FUNCTIONAL |

---

## 🛠️ Recommended Fix Approach

### Step 1: Fix Tool Use/Result (30 minutes)
1. Add extensive debug logging to trace tool_result lifecycle
2. Run a simple test: "Find document int_doc_1763133421684"
3. Watch console for where tool_results disappear
4. Fix validation function to preserve tool_results
5. Test again

### Step 2: Fix Prompt Injection (15 minutes)
1. Check request Content-Type in agent_routes_v4.py
2. Ensure JSON parsing happens before accessing request.json
3. Add try/catch to prevent failures
4. Test with your Microsoft tool preferences

### Step 3: Create Missing Table (10 minutes)
1. Create migration script: `add_thread_assignments_table.py`
2. Run migration
3. Verify table exists
4. Test thread assignment tracking

---

## 💡 Quick Test to Verify Fixes

After implementing fixes, run this test:

```python
# Test tool execution
import requests

response = requests.post(
    'http://localhost:5001/api/agent/chat',
    json={
        'message': 'Find document int_doc_1763133421684',
        'user_id': 14,
        'thread_id': '1763055807954'
    },
    headers={'Content-Type': 'application/json'}
)

print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
```

**Expected:** Should return document details WITHOUT 400 error

---

## 📝 Your User Preferences (Currently Not Working)

These should be injected into the system prompt but aren't due to Error #2:

```yaml
Platform Preferences:
  - Presentations: microsoft_powerpoint_* (NOT google_slides_*)
  - Team Chat: microsoft_teams_* (NOT google_chat_*)
  - Tasks: microsoft_todo_* (NOT google_tasks_*)

Communication Style: casual
Detail Level: comprehensive
```

**Once fixed, the AI will:**
- ✅ Always use PowerPoint instead of Google Slides
- ✅ Always use Teams instead of Google Chat
- ✅ Always use Microsoft To Do instead of Google Tasks
- ✅ Respond in a casual, friendly tone
- ✅ Provide comprehensive, detailed answers

---

**Last Updated:** November 15, 2025  
**Status:** CRITICAL ERRORS - IMMEDIATE FIX REQUIRED  
**Affected System:** AI Agent Backend (Flask + Claude API)
