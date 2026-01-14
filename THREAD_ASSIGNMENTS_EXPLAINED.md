# Thread Assignments - Complete System Overview

**Date:** November 17, 2025  
**Location:** AI_infrastructure/routes/thread_assignment_routes.py

## Overview

Thread assignments track which conversation thread is open in which agent location (Prime, Agent-1, Agent-2, etc.).

## Storage Location

**❌ NOT stored in a dedicated table**  
**✅ Stored in JSON format in `users.metadata` column**

### Current Implementation:

```
Database: ai_infrastructure (schema)
Table: users
Column: metadata (JSON/TEXT)
Format: {"thread_assignments": {"agent-1": "thread-id", "agent-2": "thread-id"}}
```

**Example metadata:**
```json
{
  "thread_assignments": {
    "agent-1": "1731843567890",
    "agent-2": "1731843892345",
    "agent-3": "1731844123456"
  }
}
```

**Note:** Prime is IMPLICIT - any thread NOT in the assignments object is in Prime.

## Why Two `thread_assignments` Tables Exist (But Aren't Used)

From your schema audit:
- `ai_infrastructure.thread_assignments` - 0 rows (empty, unused)
- `sessions.thread_assignments` - 0 rows (empty, unused)

These tables were created for a **table-based storage approach** but the system **actually uses JSON storage** in `users.metadata` instead. The tables can be safely dropped.

## Assignment Rules

The system enforces 3 strict rules via `enforce_thread_assignment_rules()`:

### Rule 1: One Location Per Thread
- A thread can only be in ONE location at a time
- If thread is assigned to a new location, it's removed from the old location
- Example: Moving thread from agent-1 to agent-2 removes it from agent-1

### Rule 2: One Thread Per Agent
- Each agent location can only have ONE thread
- If a new thread is assigned to an agent, the old thread is displaced
- Displaced thread goes back to Prime (implicit)
- Example: Assigning thread B to agent-1 displaces thread A (which was in agent-1)

### Rule 3: Most Recent Assignment Wins
- Latest assignment operation takes precedence
- Conflicting assignments are resolved by timestamp
- Example: Two quick assignments to same agent → second one wins

## API Endpoints

### 1. GET /api/thread-assignments/list
**Get all thread assignments for a user**

```javascript
GET /api/thread-assignments/list?user_id=14

Response:
{
  "success": true,
  "assignments": {
    "agent-1": "1731843567890",
    "agent-2": "1731843892345"
  }
}
```

### 2. POST /api/thread-assignments
**Save thread assignments (bulk update)**

```javascript
POST /api/thread-assignments
Body: {
  "user_id": 14,
  "assignments": {
    "agent-1": "1731843567890",
    "agent-2": "1731843892345"
  }
}

Response:
{
  "success": true,
  "message": "Thread assignments saved"
}
```

### 3. POST /api/thread-assignments/assign
**Assign a specific thread to a location**

```javascript
POST /api/thread-assignments/assign
Body: {
  "user_id": 14,
  "session_id": "1731843567890",
  "location": "agent-1"
}

Response:
{
  "success": true,
  "previous_location": "agent-2",
  "displaced_thread": "1731843892345"
}
```

### 4. POST /api/thread-assignments/clear/{location}
**Clear a specific location (move thread back to Prime)**

```javascript
POST /api/thread-assignments/clear/agent-1
Body: {
  "user_id": 14
}

Response:
{
  "success": true,
  "message": "Cleared agent-1"
}
```

### 5. GET /api/thread-assignments/location/{session_id}
**Find which location a thread is in**

```javascript
GET /api/thread-assignments/location/1731843567890?user_id=14

Response:
{
  "success": true,
  "location": "agent-1"
}
```

### 6. POST /api/thread-assignments/validate
**Validate thread assignment (checks for conflicts)**

```javascript
POST /api/thread-assignments/validate
Body: {
  "user_id": 14,
  "session_id": "1731843567890",
  "location": "agent-1"
}

Response:
{
  "success": true,
  "valid": true,
  "conflicts": []
}
```

## Database Schema Issue

### The Duplicate Tables Problem:

Your Supabase has **two unused `thread_assignments` tables**:

1. **`ai_infrastructure.thread_assignments`** (0 rows)
   - Structure: id, user_id, session_id, location, agent_name, created_at, updated_at
   - Status: Empty, unused by current code

2. **`sessions.thread_assignments`** (0 rows)
   - Structure: Similar to above
   - Status: Empty, unused by current code

### Why They Exist:

These tables were likely created for a **relational approach** to storing thread assignments, but the system was refactored to use **JSON storage in users.metadata** instead.

### Should They Be Dropped?

**YES - Safe to drop both tables:**

```sql
-- Run in Supabase SQL Editor
DROP TABLE IF EXISTS ai_infrastructure.thread_assignments CASCADE;
DROP TABLE IF EXISTS sessions.thread_assignments CASCADE;
```

**Reason:** The current code doesn't use these tables at all. It uses `users.metadata` JSON column.

## How Frontend Uses Thread Assignments

From `UI/business-ai-platform-v2.html` (ThreadManager):

```javascript
// Load assignments on startup
async function loadThreadAssignments() {
    const response = await fetch(`/api/thread-assignments/list?user_id=${userId}`);
    const data = await response.json();
    
    // data.assignments = {"agent-1": "thread-id", "agent-2": "thread-id"}
    applyAssignments(data.assignments);
}

// Assign thread to agent
async function assignThreadToAgent(threadId, location) {
    await fetch('/api/thread-assignments/assign', {
        method: 'POST',
        body: JSON.stringify({
            user_id: userId,
            session_id: threadId,
            location: location
        })
    });
}
```

## Code Flow

### Thread Creation:
```
1. User creates new thread
2. Thread created in sessions.threads table
3. Thread automatically in Prime (no assignment record)
```

### Thread Assignment:
```
1. User drags thread to Agent-1
2. Frontend calls POST /api/thread-assignments/assign
3. Backend updates users.metadata JSON:
   - Removes thread from any previous location (Rule 1)
   - Displaces any thread in Agent-1 (Rule 2)
   - Assigns thread to Agent-1 (Rule 3)
4. Frontend updates UI
```

### Thread Lookup:
```
1. Frontend needs to know which threads are where
2. Calls GET /api/thread-assignments/list
3. Backend reads users.metadata JSON
4. Returns: {"agent-1": "thread-id", ...}
5. Frontend displays threads in correct columns
```

## Current Issues

Based on your schema audit:

1. **✅ No duplicate data** - Both thread_assignments tables are empty
2. **✅ Current code works** - Uses JSON storage correctly
3. **⚠️ Unused tables exist** - Can be dropped for cleanup

## Recommended Actions

### 1. Drop Unused Tables (Optional Cleanup)
```sql
-- Supabase SQL Editor
DROP TABLE IF EXISTS ai_infrastructure.thread_assignments CASCADE;
DROP TABLE IF EXISTS sessions.thread_assignments CASCADE;
```

### 2. Verify JSON Storage Works
```sql
-- Check users.metadata for thread assignments
SELECT 
    id, 
    username, 
    email,
    metadata->>'thread_assignments' as assignments
FROM ai_infrastructure.users
WHERE metadata IS NOT NULL
    AND metadata->>'thread_assignments' IS NOT NULL;
```

### 3. Monitor for Issues
- Check Render logs for thread assignment errors
- Verify assignments persist across sessions
- Test drag-and-drop thread assignment in UI

## Summary

**Storage Method:** JSON in `users.metadata` column  
**Database:** `ai_infrastructure` schema  
**Table:** `users`  
**Column:** `metadata` (JSON/TEXT)  
**Unused Tables:** 2 (both can be dropped)  
**API Endpoints:** 6 endpoints  
**Rules:** 3 strict rules enforced  
**Status:** ✅ Working correctly, uses JSON storage  

**Key Insight:** Despite having `thread_assignments` tables in the schema, the system **doesn't use them**. Everything is stored in `users.metadata` as JSON for simplicity and flexibility.

---

**Files Referenced:**
- `AI_infrastructure/routes/thread_assignment_routes.py` - Main logic
- `AI_infrastructure/flask_app.py` - Blueprint registration
- `UI/business-ai-platform-v2.html` - Frontend ThreadManager
- `data/ai_infrastructure.db` (local) or Supabase ai_infrastructure schema (production)
