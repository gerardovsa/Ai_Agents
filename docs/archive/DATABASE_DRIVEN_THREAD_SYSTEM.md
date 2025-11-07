# Database-Driven Thread Assignment System

**Created:** November 5, 2025  
**Status:** ✅ IMPLEMENTED

## Core Philosophy

**The database is the single source of truth.** All thread assignments are determined by what's stored in `sessions.db` → `users.metadata` → `thread_assignments` JSON.

---

## The Three Rules (ENFORCED IN DATABASE)

### RULE 1: Thread Exclusivity
**A thread can only be viewed in ONE location at a time:**
- Either in **Prime** (default)
- OR in **ONE agent column** (Alpha-1, Bravo-2, etc.)

**Enforcement:** When assigning a thread to a new location, the system automatically removes it from any previous location in the database.

### RULE 2: Agent Exclusivity  
**An agent column can only have ONE thread assigned:**
- If Agent Alpha-1 has Thread A
- And you assign Thread B to Alpha-1
- Thread A is automatically displaced and returns to Prime

**Enforcement:** When assigning a thread to an agent that already has a thread, the system removes the old thread from that agent in the database.

### RULE 3: Most Recent Wins
**The most recent assignment always wins:**
- Old/duplicate assignments are automatically removed
- Database is cleaned up on every assignment operation
- No manual cleanup needed

**Enforcement:** The `enforce_thread_assignment_rules()` function handles all cleanup atomically.

---

## Database Structure

**Location:** `C:\Users\gpoli\GIT\AI_agents\data\sessions.db`

**Table:** `users`

**Column:** `metadata` (TEXT, JSON format)

**JSON Structure:**
```json
{
  "thread_assignments": {
    "agent-1": "1762192838469",
    "agent-2": "1762193002345",
    "agent-3": "1762194123456"
  }
}
```

**Notes:**
- Only agent columns are stored
- **Prime is implicit** - any thread NOT in an agent is in Prime
- Storing `"location": "prime"` removes thread from all agents

---

## Backend Implementation

### File: `AI_infrastructure/routes/thread_assignment_routes.py`

### Core Function: `enforce_thread_assignment_rules()`

**Purpose:** Enforce all 3 rules atomically in database

**Logic:**
1. Load current assignments from database
2. Remove thread from any previous location (RULE 1)
3. If moving to Prime, remove from database and return
4. Remove any existing thread from target agent (RULE 2)
5. Assign thread to target location (RULE 3)
6. Save back to database

**Returns:**
```python
{
    'previous_location': 'agent-2',  # Where thread was before (or None)
    'displaced_thread': '1762193002345'  # Thread that was kicked out (or None)
}
```

### API Endpoint: `POST /api/thread-assignments/assign`

**Request:**
```json
{
  "user_id": 1,
  "session_id": "1762192838469",
  "location": "agent-1"  // or "prime"
}
```

**Response:**
```json
{
  "success": true,
  "assignment": {
    "session_id": "1762192838469",
    "location": "agent-1",
    "previous_location": "agent-2",  // null if thread was in Prime
    "displaced_thread": "1762193002345"  // null if agent was empty
  }
}
```

**Rules Enforced:**
- ✅ Thread removed from previous location
- ✅ Displaced thread (if any) returned to Prime
- ✅ Most recent assignment stored in database
- ✅ All operations atomic (single database transaction)

---

## Frontend Integration

### What the UI Should Do

**On Page Load:**
1. Call `GET /api/thread-assignments?user_id=1`
2. Get `{"agent-1": "threadId", "agent-2": "threadId", ...}`
3. Create agent columns for assigned agents
4. Load threads into those columns
5. Any thread NOT in an agent is in Prime

**On Drag-and-Drop:**
1. Call `POST /api/thread-assignments/assign` with new location
2. Backend enforces rules and returns what changed
3. UI updates based on response:
   - Clear thread from `previous_location`
   - Move `displaced_thread` to Prime (if any)
   - Render thread in new location
   - Update all thread badges

**On New Chat in Agent Column:**
1. Create new thread
2. Call `POST /api/thread-assignments/assign` to assign new thread to agent
3. Backend automatically displaces old thread
4. UI moves old thread to Prime
5. UI renders new thread in agent

**On Opening Thread in Prime:**
1. Show confirmation: "This will remove Alpha-1's tag. Continue?"
2. If yes: Call `POST /api/thread-assignments/assign` with `location: "prime"`
3. Backend removes thread from agent
4. UI clears agent column
5. UI renders thread in Prime

---

## What Gets Updated and When

### Database Updates (Automatic):
- **Every assignment** → Database updated
- **Every drag/drop** → Database updated
- **Every new chat** → Database updated
- **Moving to Prime** → Thread removed from database (Prime is implicit)

### UI Updates (Based on Database):
- **Page load** → Read database, render all assignments
- **After assignment** → Update UI based on API response
- **Thread badges** → Updated immediately after assignment
- **Agent columns** → Created/cleared based on database state

### No Manual Cleanup Needed:
- ❌ No need to manually remove duplicates
- ❌ No need to check for conflicts
- ❌ No need to validate assignments
- ✅ Database enforces rules automatically
- ✅ API returns what changed
- ✅ UI just reflects database state

---

## Example Scenarios

### Scenario 1: Drag Thread to Agent

**Action:** Drag Thread A (in Prime) to Alpha-1 (empty)

**Database Before:**
```json
{"thread_assignments": {}}
```

**API Call:**
```json
POST /api/thread-assignments/assign
{"session_id": "threadA", "location": "agent-1"}
```

**Database After:**
```json
{"thread_assignments": {"agent-1": "threadA"}}
```

**UI Result:**
- Thread A removed from Prime
- Thread A rendered in Alpha-1
- Thread A badge shows "Alpha-1"

---

### Scenario 2: Drag Thread to Occupied Agent

**Action:** Drag Thread B to Alpha-1 (has Thread A)

**Database Before:**
```json
{"thread_assignments": {"agent-1": "threadA"}}
```

**API Call:**
```json
POST /api/thread-assignments/assign
{"session_id": "threadB", "location": "agent-1"}
```

**API Response:**
```json
{
  "displaced_thread": "threadA",
  "previous_location": null
}
```

**Database After:**
```json
{"thread_assignments": {"agent-1": "threadB"}}
```

**UI Result:**
- Thread A cleared from Alpha-1, moved to Prime
- Thread B rendered in Alpha-1
- Thread A badge shows "Prime"
- Thread B badge shows "Alpha-1"

---

### Scenario 3: Move Thread Between Agents

**Action:** Drag Thread A from Alpha-1 to Bravo-2

**Database Before:**
```json
{"thread_assignments": {"agent-1": "threadA"}}
```

**API Call:**
```json
POST /api/thread-assignments/assign
{"session_id": "threadA", "location": "agent-2"}
```

**API Response:**
```json
{
  "previous_location": "agent-1",
  "displaced_thread": null
}
```

**Database After:**
```json
{"thread_assignments": {"agent-2": "threadA"}}
```

**UI Result:**
- Alpha-1 cleared (shows empty/welcome)
- Thread A rendered in Bravo-2
- Thread A badge shows "Bravo-2"

---

### Scenario 4: New Chat in Agent

**Action:** Click "New Chat" in Alpha-1 (has Thread A)

**Database Before:**
```json
{"thread_assignments": {"agent-1": "threadA"}}
```

**API Call:**
```json
POST /api/thread-assignments/assign
{"session_id": "newThreadB", "location": "agent-1"}
```

**API Response:**
```json
{
  "displaced_thread": "threadA",
  "previous_location": null
}
```

**Database After:**
```json
{"thread_assignments": {"agent-1": "newThreadB"}}
```

**UI Result:**
- Thread A moved to Prime
- New Thread B created in Alpha-1
- Thread A badge shows "Prime"
- Thread B badge shows "Alpha-1"

---

### Scenario 5: Open Thread in Prime

**Action:** Click thread in Prime that's assigned to Alpha-1

**Database Before:**
```json
{"thread_assignments": {"agent-1": "threadA"}}
```

**Show Confirmation:**
> "This thread is assigned to Alpha-1. Opening it here will remove Alpha's tag. Continue?"

**If Yes:**
```json
POST /api/thread-assignments/assign
{"session_id": "threadA", "location": "prime"}
```

**Database After:**
```json
{"thread_assignments": {}}
```

**UI Result:**
- Alpha-1 cleared (empty)
- Thread A rendered in Prime
- Thread A badge shows "Prime"

---

## Testing the System

### Test 1: Clean Database State
```bash
# Check current assignments
curl http://localhost:5001/api/thread-assignments?user_id=1

# Expected: {"success": true, "assignments": {...}}
```

### Test 2: Assign Thread
```bash
curl -X POST http://localhost:5001/api/thread-assignments/assign \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "session_id": "test123", "location": "agent-1"}'

# Expected: {"success": true, "assignment": {...}}
```

### Test 3: Verify Database
```bash
cd C:\Users\gpoli\GIT\AI_agents
python -c "import sqlite3, json; conn = sqlite3.connect('data/sessions.db'); cursor = conn.cursor(); cursor.execute('SELECT metadata FROM users WHERE id = 1'); row = cursor.fetchone(); print(json.loads(row[0]) if row and row[0] else 'No data')"

# Expected: {"thread_assignments": {"agent-1": "test123"}}
```

### Test 4: Displace Thread
```bash
curl -X POST http://localhost:5001/api/thread-assignments/assign \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "session_id": "test456", "location": "agent-1"}'

# Expected: {"displaced_thread": "test123", ...}
```

---

## Files Modified

### Backend:
- ✅ `AI_infrastructure/routes/thread_assignment_routes.py`
  - Added `enforce_thread_assignment_rules()` function
  - Enhanced `assign_thread()` endpoint to use enforcement
  - Logs all rule applications

### Frontend (Already Working):
- ✅ `UI/business-ai-platform-v2.html`
  - `ThreadManager.sendToAgent()` - Calls API (line 12596)
  - `MultiAgent.loadThreadIntoAgent()` - Uses `addAgentMessage()` (line 9965)
  - `addAgentMessage()` - Proper rendering with TwoRuleStreamProcessor (line 10719)
  - `restoreThreadAssignments()` - Loads from database on page load (line 12730)

---

## Summary

**Database = Truth:**
- All assignments stored in one place
- Rules enforced automatically
- No duplicate assignments possible
- No conflicts possible

**UI = Reflection:**
- Reads database on load
- Updates based on API responses
- Shows current database state
- No local state conflicts

**API = Enforcer:**
- Validates all assignments
- Applies 3 rules atomically
- Returns what changed
- Database always consistent

**Result:**
- ✅ Simple, predictable system
- ✅ No race conditions
- ✅ No duplicate assignments
- ✅ No manual cleanup needed
- ✅ UI always matches database
- ✅ Scales to any number of agents/threads

---

**Status:** Backend enforcement implemented and ready to test. Frontend already wired up correctly. System should work end-to-end now.
