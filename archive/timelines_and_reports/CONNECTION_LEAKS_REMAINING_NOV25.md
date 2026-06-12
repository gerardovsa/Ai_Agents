# Connection Leaks - Remaining Issues (November 25, 2025)

## Summary
After fixing the 2 major leaks in `thread_assignment_routes.py` and `auth_routes.py`, we discovered **18 additional leaks** across 3 files.

## Database Schema Context
The leaks affect two PostgreSQL schemas in Supabase:

### `sessions` schema (Connection Pool #1 - max 2 connections)
- **`sessions.threads`** - Thread metadata (id, thread_slug, user_id, name, location, etc.)
- **`sessions.messages`** - Thread messages (id, thread_id, role, content, etc.)
- **`sessions.thread_shares`** - Thread sharing permissions
- **`sessions.thread_users`** - Thread user access

### `ai_infrastructure` schema (Connection Pool #2 - max 2 connections)
- **`ai_infrastructure.users`** - User accounts
- **`ai_infrastructure.oauth_tokens`** - OAuth credentials (Google, Microsoft)
- **`ai_infrastructure.user_sessions`** - JWT session tokens

**Connection Pool Limits:**
- Each schema has a **dedicated pool with max 2 connections**
- After 2 leaked connections, pool is exhausted → all requests fail
- Original error: `"Leaked connections: 2"` = pool completely exhausted

## Leak Detection Tool
Created `check_with_block_returns.py` - Automatically scans for `return` statements inside `with get_*connection()` blocks.

## Remaining Leaks (18 total)

### 1. message_operations.py (8 leaks)
**Pattern**: Early returns for error cases and success responses  
**Database**: `sessions` schema (threads, messages tables)  
**Pool Impact**: Exhausts sessions connection pool (max 2)

**Lines with leaks:**
- Line 66: `return error_response("Thread not found", 404)` - Query: `sessions.threads`
- Line 138: `return success_response({...})` - Inserts: `sessions.threads`, `sessions.messages`
- Line 182: `return error_response("Thread not found", 404)` - Query: `sessions.threads`
- Line 250: `return success_response({...})` - Inserts: `sessions.threads`, `sessions.messages`
- Line 299: `return success_response({...})` - Updates: `sessions.threads`
- Line 377: `return success_response({...})` - Updates: `sessions.threads.name`
- Line 410: `return error_response("Thread not found", 404)` - Query: `sessions.threads`
- Line 458: `return success_response(...)` - Queries: `sessions.threads`, `sessions.messages`

**Fix Pattern:**
```python
# ❌ WRONG (current code)
with get_database_connection('sessions') as conn:
    cursor = conn.cursor()
    
    if not thread:
        return error_response("Thread not found", 404)  # LEAK!
    
    # ... process data ...
    
    return success_response({...})  # LEAK!

# ✅ CORRECT (fixed code)
response_data = None
status_code = 200

with get_database_connection('sessions') as conn:
    cursor = conn.cursor()
    
    if not thread:
        response_data = error_response("Thread not found", 404)
        status_code = 404
    else:
        # ... process data ...
        response_data = success_response({...})
        status_code = 200

# Return AFTER with block
return response_data, status_code
```

### 2. thread_assignment_routes.py (5 leaks)
**Pattern**: Early returns in Flask route handlers  
**Database**: `sessions` schema (threads table) + `ai_infrastructure` schema (users.metadata)  
**Pool Impact**: Exhausts sessions connection pool (max 2)

**Lines with leaks:**
- Line 251: `return jsonify({...})` - Query: `ai_infrastructure.users.metadata` (thread assignments)
- Line 267: `return jsonify({...})` - Query: `ai_infrastructure.users.metadata`
- Line 360: `return jsonify({...})` - Updates: `sessions.threads.location`, `ai_infrastructure.users.metadata`
- Line 531: `return jsonify({...})` - Updates: `sessions.threads.location`, `ai_infrastructure.users.metadata`
- Line 539: `return jsonify({...})` - Updates: `sessions.threads.location`

**Fix Pattern:**
```python
# ❌ WRONG
with get_db_connection() as conn:
    cursor = conn.cursor()
    
    # ... query database ...
    
    return jsonify({'success': True, ...})  # LEAK!

# ✅ CORRECT
response_data = None

with get_db_connection() as conn:
    cursor = conn.cursor()
    
    # ... query database ...
    
    response_data = {'success': True, ...}

return jsonify(response_data)
```

### 3. thread_routes.py (5 leaks)
**Pattern**: Early error returns in route handlers  
**Database**: `sessions` schema (threads table)  
**Pool Impact**: Exhausts sessions connection pool (max 2) - **HIGHEST PRIORITY**

**Lines with leaks:**
- Line 269: `return error_response(f'Thread {thread_id} not found for user {user_id}', 404)` - Query: `sessions.threads WHERE id = ? AND user_id = ?`
- Line 855: `return error_response(f"Thread {thread_id} not found", 404)` - Query: `sessions.threads WHERE thread_slug = ?`
- Line 914: `return error_response(f"Thread {thread_id} not found", 404)` - Query: `sessions.threads WHERE thread_slug = ?`
- Line 1483: `return error_response(f'Thread {thread_id} not found', 404)` - Query: `sessions.threads WHERE id = ?`
- Line 1932: `return error_response('Thread not found', 404)` - Query: `sessions.threads WHERE thread_slug = ?`

**⚠️ CRITICAL:** These are the most frequently called endpoints (thread loading, status checks). These leaks likely caused the original "Leaked connections: 2" error.

**Fix Pattern:**
```python
# ❌ WRONG
with get_database_connection('sessions') as conn:
    cursor = conn.cursor()
    
    # ... query ...
    
    if not thread:
        return error_response("Thread not found", 404)  # LEAK!
    
    # ... more processing ...

# ✅ CORRECT
response_data = None
status_code = 200

with get_database_connection('sessions') as conn:
    cursor = conn.cursor()
    
    # ... query ...
    
    if not thread:
        response_data = error_response("Thread not found", 404)
        status_code = 404
    else:
        # ... more processing ...
        response_data = success_response({...})
        status_code = 200

return response_data, status_code
```

## Critical Rule
**NEVER use `return` inside a `with get_*connection()` block!**

### Why This Causes Leaks:
1. `with` statement creates a context manager
2. Connection is acquired from pool when entering `with` block
3. Connection should be returned to pool when exiting `with` block
4. Early `return` exits the function BEFORE `with` block closes
5. Connection never returned to pool → LEAK

### The Fix (3 steps):
1. **BEFORE with block**: Initialize result variable(s)
2. **INSIDE with block**: Set result values, NEVER return
3. **AFTER with block**: Return the result

## Testing
Run the leak detector:
```bash
cd C:\Users\gpoli\GIT\AI_agents
python check_with_block_returns.py
```

Expected output after all fixes:
```
[OK] No connection leaks detected
```

## Priority Fixes (Based on Schema Analysis)

### 🔴 CRITICAL (Immediate Risk)
**thread_routes.py (5 leaks)** - `sessions` schema pool
- **Why Critical**: These endpoints are called on EVERY thread load/interaction
- **Affected Queries**: 
  - `SELECT * FROM sessions.threads WHERE thread_slug = ?` (3 occurrences)
  - `SELECT * FROM sessions.threads WHERE id = ?` (2 occurrences)
- **Risk**: Pool exhausts after 2 failed thread lookups → entire UI breaks
- **Endpoints**: `load_thread()`, `get_thread()`, `get_thread_sharing_status()`, `delete_thread()`, `get_lock_status()`

### 🟡 HIGH (Heavy Operations)
**message_operations.py (8 leaks)** - `sessions` schema pool
- **Why High**: Bulk INSERT/UPDATE operations hold connections longer
- **Affected Tables**: `sessions.threads`, `sessions.messages` (can be 100+ rows)
- **Risk**: Connection held during message copying → blocks other requests
- **Endpoints**: `fork_thread()`, `clone_thread()`, `merge_branch()`, `export_thread()`

### 🟢 MEDIUM (Infrequent)
**thread_assignment_routes.py (5 leaks)** - `sessions` + `ai_infrastructure` schemas
- **Why Medium**: These endpoints called only during thread moves (rare)
- **Affected Tables**: `sessions.threads.location`, `ai_infrastructure.users.metadata`
- **Risk**: Low frequency = low probability of pool exhaustion
- **Endpoints**: `get_thread_assignments()`, `update_thread_assignment()`, `unassign_thread()`

## Schema Impact Analysis

### Sessions Pool (max 2 connections)
**Tables Affected:**
- `sessions.threads` (primary key: `id`, unique: `thread_slug`)
- `sessions.messages` (foreign key: `thread_id`)
- `sessions.thread_shares`
- `sessions.thread_users`

**Leak Severity:**
- **18 total leaks** across 3 files can exhaust this pool
- Most critical: `thread_routes.py` (5 leaks in hot paths)
- Original error: "Leaked connections: 2" = sessions pool exhausted

### AI Infrastructure Pool (max 2 connections)
**Tables Affected:**
- `ai_infrastructure.users` (metadata JSONB column for thread assignments)
- `ai_infrastructure.oauth_tokens` (already fixed in `auth_routes.py`)

**Leak Severity:**
- Only 5 leaks affect this pool (thread_assignment_routes.py)
- Lower risk due to infrequent usage

## Next Steps
1. Fix all 18 leaks using the pattern above
2. Run `check_with_block_returns.py` to verify
3. Restart Flask and test with multiple requests
4. Monitor connection pool stats for `Leaked: 0`

## SQL Query Patterns in Leaking Code

### Thread Lookup Pattern (5 leaks in thread_routes.py)
```python
# ❌ LEAKING CODE
with get_database_connection('sessions') as conn:
    cursor = conn.cursor()
    
    # Query sessions.threads table
    cursor.execute("""
        SELECT id, thread_slug, user_id, name, location, 
               created_at, updated_at, metadata, tags
        FROM sessions.threads 
        WHERE thread_slug = %s::text AND user_id = %s
    """, (thread_id, user_id))
    
    thread = cursor.fetchone()
    
    if not thread:
        return error_response("Thread not found", 404)  # ❌ LEAK!
    
    # ... process thread data ...
```

**Tables Queried:**
- `sessions.threads` - Main thread metadata
- Columns: `id`, `thread_slug` (unique), `user_id`, `name`, `location`, `metadata`, `tags`

### Bulk Message Operations (8 leaks in message_operations.py)
```python
# ❌ LEAKING CODE
with get_database_connection('sessions') as conn:
    cursor = conn.cursor()
    
    # 1. Query thread
    cursor.execute("SELECT * FROM sessions.threads WHERE id = %s", (thread_id,))
    thread = cursor.fetchone()
    
    if not thread:
        return error_response("Thread not found", 404)  # ❌ LEAK!
    
    # 2. Query messages (can be 100+ rows)
    cursor.execute("""
        SELECT id, thread_id, role, content, created_at, metadata
        FROM sessions.messages 
        WHERE thread_id = %s 
        ORDER BY created_at ASC
    """, (thread_id,))
    messages = cursor.fetchall()
    
    # 3. Insert new thread
    cursor.execute("""
        INSERT INTO sessions.threads 
        (thread_slug, name, user_id, location, metadata, created_at)
        VALUES (%s, %s, %s, %s, %s, NOW())
        RETURNING id
    """, (new_slug, name, user_id, location, metadata))
    
    # 4. Copy messages (loop with 100+ INSERTs)
    for msg in messages:
        cursor.execute("""
            INSERT INTO sessions.messages 
            (thread_id, role, content, created_at)
            VALUES (%s, %s, %s, %s)
        """, (new_thread_id, msg['role'], msg['content'], msg['created_at']))
    
    conn.commit()
    
    return success_response({...})  # ❌ LEAK!
```

**Tables Modified:**
- `sessions.threads` - INSERT new threads
- `sessions.messages` - Bulk INSERT (can be 100+ rows)

### Thread Assignment Updates (5 leaks in thread_assignment_routes.py)
```python
# ❌ LEAKING CODE
with get_db_connection() as conn:
    cursor = conn.cursor()
    
    # 1. Query user metadata (JSONB column)
    cursor.execute("""
        SELECT metadata FROM ai_infrastructure.users WHERE id = %s
    """, (user_id,))
    
    # 2. Update thread location
    cursor.execute("""
        UPDATE sessions.threads 
        SET location = %s, updated_at = CURRENT_TIMESTAMP
        WHERE thread_slug = %s::text AND user_id = %s
    """, (location, thread_slug, user_id))
    
    # 3. Update user metadata (thread assignments)
    cursor.execute("""
        UPDATE ai_infrastructure.users 
        SET metadata = %s, last_active = CURRENT_TIMESTAMP
        WHERE id = %s
    """, (json.dumps(metadata), user_id))
    
    conn.commit()
    
    return jsonify({'success': True, ...})  # ❌ LEAK!
```

**Tables Modified:**
- `sessions.threads.location` - Thread location update
- `ai_infrastructure.users.metadata` - JSONB column with thread assignments

## Files Fixed So Far
✅ `thread_assignment_routes.py` - `enforce_thread_assignment_rules()` function (Lines 82-200)
✅ `auth_routes.py` - `revoke_tokens()` function (Lines 405-550)

## Files Still Need Fixing
❌ `message_operations.py` - 8 leaks (Lines: 66, 138, 182, 250, 299, 377, 410, 458)
❌ `thread_assignment_routes.py` - 5 additional leaks (Lines: 251, 267, 360, 531, 539)
❌ `thread_routes.py` - 5 leaks (Lines: 269, 855, 914, 1483, 1932)
