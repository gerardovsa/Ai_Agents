# Database Tables Explained - What Are We Actually Using?

**Date:** November 8, 2025  
**User:** gerardo@vetsuccessacademy.com (User ID: 1)  
**Status:** ✅ Cleanup Complete - Legacy table deleted

---

## 🎯 Quick Answer

**YOU ARE USING:**
1. **`threads` table** - Main thread storage (6 threads currently)
2. **`messages` table** - Message storage (460 messages currently)
3. **`users.metadata` JSON** - Thread assignments (which agent column each thread is in)

**YOU ARE NOT USING:**
- ~~`saved_threads` table~~ - ❌ DELETED (legacy system)
- ~~`sessions` table~~ - Different purpose (browser sessions, not threads)

---

## 📊 Table Breakdown

### ✅ ACTIVE TABLES (Current System)

#### 1. `threads` table - PRIMARY STORAGE
**Purpose:** Store all conversation threads

**Key Columns:**
- `id` - Auto-increment ID
- `thread_slug` - Unique thread identifier (used in frontend)
- `user_id` - Owner of the thread
- `workspace_id` - Which workspace it belongs to
- `name` - Thread title
- `location` - Which agent column (agent-1, agent-2, prime, etc.)
- `synergy_card_id` - Link to Synergy Kanban card
- `tags` - Thread categories (JSON array)
- `created_at` / `updated_at` - Timestamps
- `metadata` - Additional JSON data

**Current Data:**
- 6 threads for User 1
- All in 'prime' location
- 4 linked to Synergy cards

**Example:**
```
thread_slug: 1762533505022
name: "Outlook - Email Quotes"
location: "prime"
synergy_card_id: "sess_20251107_2211_email_thread_quote_processing_"
```

---

#### 2. `messages` table - MESSAGE STORAGE
**Purpose:** Store individual messages within threads

**Key Columns:**
- `id` - Auto-increment ID
- `thread_id` - Foreign key to threads.id
- `user_id` - Message author
- `role` - 'user' or 'assistant'
- `content` - Message text
- `tool_calls` - AI tool usage data
- `tokens_used` - Token count
- `response_time_ms` - Response latency
- `created_at` / `updated_at` - Timestamps

**Current Data:**
- 460 messages for User 1
- Linked to threads via `thread_id`

**Relationship:**
```
threads (1) ──── (many) messages
  |                      |
  id                thread_id
```

---

#### 3. `users` table - USER DATA
**Purpose:** Store user accounts and metadata

**Key Columns:**
- `id` - User ID
- `username` - Login name
- `email` - Email address
- `metadata` - JSON blob for thread assignments

**metadata JSON format:**
```json
{
  "thread_assignments": {
    "agent-1": "1761874725424",
    "agent-3": "1762487380532",
    "agent-4": "1761988423247"
  }
}
```

**Current Data:**
- 1 user: gerardo@vetsuccessacademy.com
- 3 thread assignments stored in metadata

---

### 🔧 OTHER TABLES (Different Purpose)

#### 4. `sessions` table - BROWSER SESSIONS
**Purpose:** Track browser session state (NOT threads!)

**Key Columns:**
- `session_id` - Browser session ID
- `ui_context` - UI state
- `agent_id` - Active agent
- `conversation` - Temporary conversation data

**Current Data:** 160 browser sessions

**NOTE:** This is for session management, NOT thread storage. Don't confuse with threads!

---

#### 5. `api_sessions` table - API SESSION TRACKING
**Purpose:** Track API calls and sessions

**Current Data:** 0 records

---

#### 6. `workspaces` table - WORKSPACE MANAGEMENT
**Purpose:** Store workspace information

**Current Data:** 1 workspace

---

### ❌ DELETED TABLES (Legacy System)

#### ~~`saved_threads` table~~ - REMOVED
**Previous Purpose:** Old thread storage system

**Status:** ✅ **DELETED** (November 8, 2025)

**Why deleted:**
- Legacy system (replaced by `threads` table)
- Had 1 old record
- No longer used by frontend or backend
- Backup saved: `sessions_backup_cleanup_legacy_threads.db`

---

## 🔄 How It All Works Together

### Thread Creation Flow
```
1. User creates thread in UI
   ↓
2. Frontend: POST /api/threads/save
   ↓
3. Backend saves to threads table:
   - thread_slug: unique ID
   - name: thread title
   - user_id: 1
   - location: "prime" (default)
   ↓
4. Messages saved to messages table:
   - thread_id: links to threads.id
   - role: "user" or "assistant"
   - content: message text
   ↓
5. Thread appears in UI
```

---

### Thread Assignment Flow
```
1. User drags thread to Agent-3 column
   ↓
2. Frontend: POST /api/thread-assignments/assign
   {
     "user_id": 1,
     "session_id": "1762533505022",
     "location": "agent-3"
   }
   ↓
3. Backend updates users.metadata:
   {
     "thread_assignments": {
       "agent-3": "1762533505022"
     }
   }
   ↓
4. Thread appears in Agent-3 column
```

---

### Thread Loading Flow (Page Refresh)
```
1. User refreshes browser (F5)
   ↓
2. Frontend: GET /api/threads/list?user_id=1
   ↓
3. Backend queries threads table:
   SELECT * FROM threads WHERE user_id = 1
   ↓
4. Returns 6 threads
   ↓
5. Frontend: GET /api/thread-assignments?user_id=1
   ↓
6. Backend queries users.metadata:
   {"agent-1": "...", "agent-3": "...", "agent-4": "..."}
   ↓
7. Frontend applies assignments to threads
   ↓
8. Threads appear in correct agent columns
```

---

## ⚠️ WHY THREADS NOT LOADING FOR printing@inhouseprint.com.au

**ISSUE:** User printing@inhouseprint.com.au doesn't exist in database!

**Diagnosis:**
```sql
SELECT id, username, email FROM users;
-- Result: Only 1 user: gerardo@vetsuccessacademy.com (ID: 1)
```

**Root Cause:**
- Frontend may be passing wrong user_id
- Or user was never created in database
- All threads are associated with User ID 1 (gerardo@vetsuccessacademy.com)

**Solution:**

### Option A: Create printing@inhouseprint.com.au user
```sql
INSERT INTO users (username, email, role, created_at, metadata)
VALUES ('printing', 'printing@inhouseprint.com.au', 'user', CURRENT_TIMESTAMP, '{}');
```

### Option B: Check what user_id frontend is using
```javascript
// In browser console (F12)
localStorage.getItem('user_id')
// Or check what user_id is sent in API calls
```

### Option C: Frontend hardcoded to User ID 1
```javascript
// Check business-ai-platform-v2.html
// Search for: user_id=1 or userId: 1
// May need to change to dynamic user ID
```

---

## 🧪 Testing Commands

### Check threads for User 1
```powershell
curl "http://localhost:5001/api/threads/list?user_id=1"
```

### Check thread assignments for User 1
```powershell
curl "http://localhost:5001/api/thread-assignments?user_id=1"
```

### Check database directly
```powershell
sqlite3 data/sessions.db "SELECT thread_slug, name, location FROM threads WHERE user_id = 1;"
```

### Check messages for a thread
```powershell
sqlite3 data/sessions.db "SELECT role, content FROM messages WHERE thread_id = 1 LIMIT 5;"
```

---

## 📋 Summary

**WHAT YOU'RE USING:**
```
✅ threads table      → Main thread storage (6 threads)
✅ messages table     → Message storage (460 messages)  
✅ users.metadata     → Thread assignments (3 assignments)
```

**WHAT YOU'RE NOT USING:**
```
❌ saved_threads      → DELETED (legacy, no longer used)
🔧 sessions          → Browser sessions (different purpose)
🔧 api_sessions      → API tracking (different purpose)
```

**WHY THREADS NOT LOADING:**
```
⚠️  User "printing@inhouseprint.com.au" doesn't exist in database
   - Only user is: gerardo@vetsuccessacademy.com (ID: 1)
   - All 6 threads belong to User ID 1
   - Frontend may be using wrong user_id or user was never created
```

**NEXT STEPS:**
```
1. Check which user_id frontend is using
2. Create printing@inhouseprint.com.au user if needed
3. Or update frontend to use correct user_id
```

---

**Backup Location:** `data/sessions_backup_cleanup_legacy_threads.db`  
**Last Updated:** November 8, 2025  
**Status:** ✅ Database cleaned up, ready to use
