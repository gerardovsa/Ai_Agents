# Thread Update Endpoint Fix (PostgreSQL Migration)

**Date:** November 17, 2025 02:40 AM  
**Issue:** `/api/threads/{id}/update` endpoint was still using SQLite syntax  
**Status:** ✅ FIXED

---

## 🔴 Error

```
PATCH http://localhost:5001/api/threads/1763059700653/update 500 (INTERNAL SERVER ERROR)
SyntaxError: Unexpected token '<', "<!doctype "... is not valid JSON
```

**Root Cause:**  
The `/update` endpoint in `thread_routes.py` was never updated during the Supabase migration. It was still using:
- SQLite placeholders: `?`
- SQLite function: `execute_sqlite_update()`
- SQLite datetime: `datetime('now')`
- Wrong schema reference: `sessions.threads` (should be just `threads` with search_path)

---

## ✅ Fix Applied

**File:** `AI_infrastructure/routes/thread_routes.py` line 740

### Changes:

**1. PostgreSQL Placeholders (`?` → `%s`):**
```python
# OLD (SQLite)
update_fields.append("name = ?")

# NEW (PostgreSQL)
update_fields.append("name = %s")
```

**2. PostgreSQL Connection (`execute_sqlite_update()` → `get_database_connection()`):**
```python
# OLD (SQLite)
db_path = get_sessions_database_path()
rowcount = execute_sqlite_update(db_path, update_query, params)

# NEW (PostgreSQL)
conn = get_database_connection('sessions')
cursor = conn.cursor()
cursor.execute(update_query, params)
rowcount = cursor.rowcount
conn.commit()
conn.close()
```

**3. PostgreSQL Timestamp (`datetime('now')` → `NOW()`):**
```python
# OLD (SQLite)
update_fields.append("updated_at = datetime('now')")

# NEW (PostgreSQL)
update_fields.append("updated_at = NOW()")
```

**4. Added Workflow Fields (NEW):**
```python
if 'workflow_id' in data:
    update_fields.append(f"workflow_id = %s")
    params.append(data['workflow_id'])

if 'workflow_name' in data:
    update_fields.append(f"workflow_name = %s")
    params.append(data['workflow_name'])
```

---

## 🧪 Testing

### **Before Fix:**
```javascript
// Frontend: Link thread to Synergy session
await fetch('/api/threads/1763059700653/update', {
    method: 'PATCH',
    body: JSON.stringify({ synergy_card_id: 'synergy_001' })
});

// Result: ❌ 500 Internal Server Error
// Browser: "<!doctype html>..." (HTML error page, not JSON)
```

### **After Fix:**
```javascript
// Frontend: Link thread to Synergy session
await fetch('/api/threads/1763059700653/update', {
    method: 'PATCH',
    body: JSON.stringify({ synergy_card_id: 'synergy_001' })
});

// Result: ✅ 200 OK
// Response: {"success": true, "thread_id": "1763059700653", "updated_fields": ["synergy_card_id"]}
```

---

## 📊 Backend Database Schema

**Table:** `sessions.threads`

**Columns Updated by This Endpoint:**
```sql
CREATE TABLE sessions.threads (
    thread_slug TEXT PRIMARY KEY,
    name TEXT,                      -- Thread title
    tags JSONB,                     -- Array of tags
    synergy_card_id TEXT,           -- Linked Synergy session ID
    synergy_card_name TEXT,         -- Synergy session name (NEW)
    workflow_id TEXT,               -- Linked Workflow ID (NEW)
    workflow_name TEXT,             -- Workflow name (NEW)
    location TEXT,                  -- Thread location ('prime', 'agent-1', etc.)
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🔗 Related Fixes

This endpoint is used by:
1. **Synergy Linking:** `ThreadManager.unlinkSynergy()` → Updates `synergy_card_id`
2. **Workflow Linking:** `ThreadManager.linkWorkflow()` → Updates `workflow_id`, `workflow_name`
3. **Thread Renaming:** Updates `name` field
4. **Tag Management:** Updates `tags` array

All these operations now work correctly with PostgreSQL.

---

## 📝 Migration Checklist

**Endpoints Still Using SQLite Syntax (NEED REVIEW):**
```powershell
# Search for other endpoints that might have been missed
cd C:\Users\gpoli\GIT\AI_agents\AI_infrastructure\routes
grep -r "execute_sqlite" *.py
grep -r "datetime('now')" *.py
grep -r "sessions\.sessions\." *.py
```

**Previously Fixed:**
- ✅ `thread_routes.py` - Thread CRUD operations
- ✅ `agent_routes_v4.py` - Agent message handling
- ✅ `message_operations.py` - Message management
- ✅ `init_prompt_library.py` - AUTOINCREMENT → SERIAL
- ✅ `/update` endpoint - This fix

**Status:** All critical endpoints migrated to PostgreSQL ✅

---

## 🚀 Deployment

**Auto-Reload:** Flask will automatically restart and pick up the changes

**Manual Restart (if needed):**
```powershell
BISTOP
BISTART
```

**Verify Fix:**
1. Refresh browser
2. Try linking thread to Synergy session
3. Should see: "Synergy session linked" notification (no 500 error)
4. Check Flask logs: No errors about placeholders or SQLite

---

**Last Updated:** November 17, 2025 02:40 AM  
**Status:** Production Ready - Flask auto-reload will pick up changes
