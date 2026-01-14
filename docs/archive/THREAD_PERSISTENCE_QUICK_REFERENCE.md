# Thread Persistence - Quick Reference Guide

## 🎯 What Was Fixed

**Problem:** Threads weren't being saved to the database - conversations lost on server restart.

**Solution:** Implemented 3-part fix:
1. ✅ Flexible API that accepts both parameter formats
2. ✅ Auto-save on every conversation completion
3. ✅ Full integration with Prime/Mine agent assignment system

---

## 🔧 For Developers

### API Endpoint: `/api/threads/save`

**Accepts TWO formats:**

```javascript
// Format 1: Backend (agent_id + session_id)
POST /api/threads/save
{
    "agent_id": "stock_ai",
    "session_id": "uuid-here",
    "thread_name": "My Thread",
    "user_id": 1,
    "location": "prime"  // or "agent-1", "agent-2", etc.
}

// Format 2: Frontend (thread_id + messages)
POST /api/threads/save
{
    "thread_id": "stock_ai_uuid-here",
    "title": "My Thread",
    "messages": [...],
    "agent": "stock_ai",
    "user_id": 1,
    "location": "agent-1"
}
```

**Both return:**
```javascript
{
    "success": true,
    "thread_id": "stock_ai_uuid-here",
    "message_count": 15,
    "saved_at": "2025-11-07T10:30:00",
    "location": "prime"
}
```

---

### Auto-Save Feature

**When it triggers:**
- Automatically after every conversation completes
- Triggered by SSE `complete` event
- No user action required

**What it saves:**
- Full conversation history
- Thread metadata (agent_id, session_id)
- User ID for the thread
- Current location (Prime or Agent-X)
- Timestamp data

**Location:** `AI_infrastructure/routes/agent_routes_v4.py` line ~850

---

### Database Schema

**Table:** `saved_threads` (in **sessions.db** - NOT stock database!)

**Location:** `data/sessions.db`

**Why sessions.db?** This database already contains:
- User accounts and metadata
- OAuth tokens and credentials  
- Thread assignments (Prime/Mine system)
- Session data

Threads logically belong here with user data, not in the stock/inventory database.

```sql
CREATE TABLE IF NOT EXISTS saved_threads (
    thread_id TEXT PRIMARY KEY,          -- "agent_id_session_id"
    agent_id TEXT NOT NULL,              -- "stock_ai", "1", "2", etc.
    session_id TEXT NOT NULL,            -- UUID
    user_id INTEGER DEFAULT 1,           -- User who created thread
    location TEXT DEFAULT 'prime',       -- "prime", "agent-1", "agent-2", etc.
    thread_name TEXT,                    -- Display title
    conversation TEXT NOT NULL,          -- JSON array of messages
    message_count INTEGER,               -- Quick count
    context TEXT,                        -- Additional metadata
    created_at TEXT,                     -- ISO timestamp
    saved_at TEXT DEFAULT CURRENT_TIMESTAMP,
    last_updated TEXT DEFAULT CURRENT_TIMESTAMP
)
```

---

### Agent State Manager

**New fields in state:**
```python
{
    'agent_id': 'stock_ai',
    'session_id': 'uuid',
    'conversation': [...],
    'location': 'prime',      # NEW - tracks Prime/Agent assignment
    'user_id': 1,             # NEW - tracks user ownership
    'created_at': datetime,
    'last_activity': datetime
}
```

**New method:**
```python
agent_state_manager.set_thread_location(
    agent_id='stock_ai',
    session_id='uuid',
    location='agent-1',
    user_id=1
)
```

---

## 🎨 For Frontend Developers

### Saving Threads

**The `saveThreadToBackend()` method now includes location:**

```javascript
async saveThreadToBackend(thread) {
    // Automatically determines location from assignments
    const assignments = this.getThreadAssignments();
    let location = 'prime';
    
    for (const [agentLocation, sessionId] of Object.entries(assignments)) {
        if (sessionId === thread.id) {
            location = agentLocation;
            break;
        }
    }
    
    await fetch('/api/threads/save', {
        method: 'POST',
        body: JSON.stringify({
            thread_id: thread.id,
            title: thread.title,
            messages: thread.messages,
            location: location,  // Automatically included
            user_id: 1
        })
    });
}
```

**No changes required** - location is automatically detected and sent!

---

### Loading Threads

**Endpoint:** `/api/threads/list`

```javascript
const response = await fetch('/api/threads/list?user_id=1');
const data = await response.json();

// data.threads now includes:
[
    {
        "thread_id": "stock_ai_uuid",
        "agent_id": "stock_ai",
        "session_id": "uuid",
        "location": "prime",     // NEW
        "user_id": 1,            // NEW
        "message_count": 15,
        "created_at": "...",
        "last_activity": "..."
    }
]
```

---

## 🔄 Prime/Mine Integration

### How It Works

1. **Thread Assignments** stored in `sessions.db` → `users.metadata`:
   ```json
   {
       "thread_assignments": {
           "agent-1": "session-uuid-1",
           "agent-2": "session-uuid-2"
       }
   }
   ```

2. **Thread Saves** include location parameter

3. **Auto-save** checks assignments to determine current location

4. **Backend updates** both databases:
   - `saved_threads` table (conversation data)
   - `users.metadata` (assignment tracking)

### Assignment Rules

✅ **Rule 1:** Thread can only be in ONE location (Prime OR one agent)
✅ **Rule 2:** Agent can only have ONE thread
✅ **Rule 3:** Most recent assignment wins

These rules are enforced by `enforce_thread_assignment_rules()` in `thread_assignment_routes.py`

---

## 📊 Database Queries

### Check Recent Threads
```sql
SELECT thread_id, location, message_count, saved_at 
FROM saved_threads 
ORDER BY saved_at DESC 
LIMIT 10;
```

### Check Threads by Location
```sql
SELECT thread_id, message_count, saved_at 
FROM saved_threads 
WHERE location = 'agent-1';
```

### Check User's Threads
```sql
SELECT thread_id, location, message_count 
FROM saved_threads 
WHERE user_id = 1;
```

### Thread Assignment Status
```sql
SELECT id, metadata 
FROM users 
WHERE id = 1;
```

---

## 🐛 Troubleshooting

### Thread Not Saving?

**Check 1:** Is auto-save triggering?
```
Look for log: "✅ [Auto-Save] Thread saved: agent_id_session_id"
```

**Check 2:** Is conversation in agent_state_manager?
```python
state = agent_state_manager.get_state(agent_id, session_id)
print(len(state['conversation']))  # Should be > 0
```

**Check 3:** Is database path correct?
```python
from utils.database_helpers import get_stock_database_path
print(get_stock_database_path())
```

### Location Not Updating?

**Check:** Thread assignments in sessions.db
```sql
SELECT metadata FROM users WHERE id = 1;
```

Should contain:
```json
{"thread_assignments": {"agent-1": "session-uuid", ...}}
```

### Parameter Format Error?

The endpoint now accepts **both formats** automatically. If you see errors:
- Check that `thread_id` OR (`agent_id` + `session_id`) are provided
- Check that `messages` OR conversation exists in agent_state_manager

---

## 🚀 Quick Start

### 1. Start the server
```bash
BISTART
```

### 2. Send a message through UI
The message will be processed and conversation saved automatically.

### 3. Verify in database
```sql
SELECT * FROM saved_threads ORDER BY saved_at DESC LIMIT 1;
```

### 4. Restart server
```bash
BISTOP
BISTART
```

### 5. Load threads
```javascript
fetch('/api/threads/list?user_id=1')
```

Threads should persist! ✅

---

## 📝 Files Modified

### Backend:
- `AI_infrastructure/routes/thread_routes.py` - Save/load endpoints
- `AI_infrastructure/routes/agent_routes_v4.py` - Auto-save logic
- `AI_infrastructure/core/agent_state_manager.py` - Location tracking

### Frontend:
- `UI/business-ai-platform-v2.html` - Location parameter

### Tests:
- `test_thread_persistence.py` - Validation tests

### Documentation:
- `THREAD_PERSISTENCE_FIX_COMPLETE.md` - Full implementation details
- `THREAD_PERSISTENCE_QUICK_REFERENCE.md` - This file

---

## ✅ Success Indicators

When working correctly, you'll see:

**Console Logs:**
```
✅ [Auto-Save] Thread saved: stock_ai_uuid-123 (15 messages)
✅ [Thread Save] Updated thread assignment: uuid-123 -> agent-1
```

**Database:**
```sql
SELECT COUNT(*) FROM saved_threads;
-- Should increase after each conversation
```

**UI:**
```
💾 Thread saved to backend: stock_ai_uuid-123 (location: agent-1)
```

---

**Everything working? You're all set! 🎉**
