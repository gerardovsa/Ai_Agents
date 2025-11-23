# Supabase as Single Source of Truth - Architecture Fix (Nov 22, 2025)

## Problem Statement

**Current Issue:** Frontend is **INSERTING** threads and messages back to Supabase via UPSERT, causing:
- Phantom threads reappearing after deletion
- Duplicate messages
- Race conditions between frontend saves and backend creates
- Database bloat with redundant saves

**Root Cause:** Frontend treats Supabase as READ/WRITE storage instead of READ-ONLY cache.

---

## ✅ Correct Architecture: Backend Creates, Frontend Reads

### Data Flow (SHOULD BE):
```
User sends message
    ↓
Backend agent processes request
    ↓
Backend CREATES thread in Supabase (if new)
    ↓
Backend INSERTS messages to Supabase
    ↓
Backend sends conversation_sync to frontend
    ↓
Frontend READS and DISPLAYS
    ↓
Supabase Realtime pushes updates to other clients
    ↓
Frontend updates UI
```

### ❌ Current Broken Flow:
```
User sends message
    ↓
Backend processes
    ↓
Backend creates thread + messages ✅
    ↓
Frontend receives conversation_sync ✅
    ↓
Frontend calls ThreadManager.saveThreadToBackend() ❌
    ↓
Frontend UPSERTS thread to Supabase ❌
    ↓
Frontend INSERTS messages to Supabase ❌
    ↓
DUPLICATE DATA + PHANTOM THREADS 💀
```

---

## 🔧 What Needs to Change

### 1. Remove Frontend Thread/Message Creation

**Files to Fix:**

#### A. `agent-js.js` (lines 3620-3645)
```javascript
// ❌ CURRENT (WRONG):
const saveSuccess = await ThreadManager.saveThreadToBackend(threadForSaving);

// ✅ CORRECT:
// Backend already saved thread via conversation_sync
// Frontend should ONLY update thread metadata (location, title)
console.log(`[Agent ${agentId}] ✅ Thread already saved by backend via conversation_sync`);
```

#### B. `thread_loader.js` (lines 70-120)
```javascript
// ❌ CURRENT (WRONG):
async saveThreadToBackend(thread) {
    // STEP 1: UPSERT thread
    await fetch('/api/threads/upsert', { ... });
    
    // STEP 2: Save messages
    await this.saveMessagesToBackend(thread);
}

// ✅ CORRECT:
async saveThreadToBackend(thread) {
    // ONLY update metadata, NEVER insert/upsert
    await fetch('/api/threads/update-metadata', {
        method: 'PATCH',
        body: JSON.stringify({
            thread_slug: thread.id,
            location: thread.location,
            title: thread.title,
            tags: thread.tags
        })
    });
    
    // DO NOT save messages - backend already did that!
}
```

#### C. `thread-manager-messages.js` (lines 48-220)
```javascript
// ❌ CURRENT (WRONG):
async saveMessagesToBackend(thread) {
    // Saves all messages to database
}

// ✅ CORRECT:
async saveMessagesToBackend(thread) {
    // REMOVED - Backend creates messages during agent streaming
    // Frontend should NEVER save messages
    console.warn('[ThreadManager] saveMessagesToBackend is deprecated - backend handles this');
    return true;
}
```

---

## 🎯 When Frontend SHOULD Write to Supabase

### ✅ ALLOWED Operations:

1. **Thread Assignment (Location Change)**
   ```javascript
   // User drags thread from Prime to Alpha
   await fetch('/api/threads/assign', {
       method: 'PATCH',
       body: JSON.stringify({
           thread_slug: '1763722773406',
           location: 'agent-1'  // Change location only
       })
   });
   ```

2. **Thread Metadata Updates**
   ```javascript
   // User renames thread or updates tags
   await fetch('/api/threads/update-metadata', {
       method: 'PATCH',
       body: JSON.stringify({
           thread_slug: '1763722773406',
           title: 'New Name',
           tags: ['important', 'follow-up']
       })
   });
   ```

3. **Thread Archival**
   ```javascript
   // User archives thread
   await fetch('/api/threads/archive', {
       method: 'PATCH',
       body: JSON.stringify({
           thread_slug: '1763722773406',
           archived: true
       })
   });
   ```

### ❌ FORBIDDEN Operations:

1. **Thread Creation** - Backend creates during agent streaming
2. **Message Insertion** - Backend inserts during agent streaming
3. **UPSERT on threads** - Causes phantom threads
4. **Bulk message saves** - Backend already did this

---

## 📋 Implementation Plan

### Phase 1: Stop Frontend Saves (Immediate)

**File: `agent-js.js`**
```javascript
// Line 3636: Remove saveThreadToBackend call
// BEFORE:
const saveSuccess = await ThreadManager.saveThreadToBackend(threadForSaving);

// AFTER:
// Backend already saved via conversation_sync - no frontend save needed
console.log(`[Agent ${agentId}] ✅ Thread saved by backend (conversation_sync)`);
```

**File: `thread_loader.js`**
```javascript
// Line 82: Remove UPSERT call
// BEFORE:
const upsertResponse = await fetch('/api/threads/upsert', { ... });

// AFTER:
// Skip UPSERT - backend creates threads
console.log(`[ThreadLoader] Skipping UPSERT - backend creates threads`);
return true;
```

**File: `thread_loader.js`**
```javascript
// Line 122: Disable saveMessagesToBackend
// BEFORE:
async saveMessagesToBackend(thread) {
    // Saves messages to backend
}

// AFTER:
async saveMessagesToBackend(thread) {
    console.log(`[ThreadLoader] Backend handles message saves - skipping`);
    return true;
}
```

### Phase 2: Backend Creates Threads (Already Done!)

**Backend already does this:**
- ✅ `combined_agent_worker.py` sends `conversation_sync` with full conversation
- ✅ Threads auto-created on first message
- ✅ Messages inserted to `sessions.messages` table
- ✅ Thread updated with timestamp/message_count

### Phase 3: Frontend Reads Only

**What frontend SHOULD do:**
1. Load threads on page load via `/api/threads/list`
2. Load messages via `/api/threads/{slug}/messages`
3. Listen to Supabase Realtime for updates
4. Update UI when Realtime pushes changes
5. NEVER call UPSERT or INSERT

### Phase 4: Metadata Updates Only

**New endpoint needed:**
```python
# thread_routes.py
@thread_bp.route('/<thread_slug>/metadata', methods=['PATCH'])
def update_thread_metadata(thread_slug):
    """
    Update ONLY thread metadata (location, title, tags, archived)
    DOES NOT create threads or save messages
    """
    data = request.get_json()
    
    # Only allow specific fields
    allowed_fields = ['location', 'title', 'tags', 'archived', 'synergy_card_id']
    updates = {k: v for k, v in data.items() if k in allowed_fields}
    
    # UPDATE existing thread only
    conn = get_database_connection('sessions')
    cursor = conn.cursor()
    
    # Build UPDATE query dynamically
    set_clause = ', '.join([f"{k} = %s" for k in updates.keys()])
    values = list(updates.values()) + [thread_slug]
    
    cursor.execute(f"""
        UPDATE sessions.threads
        SET {set_clause}, updated_at = NOW()
        WHERE thread_slug = %s
    """, values)
    
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    
    if affected == 0:
        return error_response('Thread not found', 404)
    
    return success_response({'updated': affected})
```

---

## 🧪 Testing Plan

### Test 1: Delete All Data
```sql
TRUNCATE TABLE sessions.threads CASCADE;
TRUNCATE TABLE sessions.messages CASCADE;
```

```javascript
// Browser console
window.MessageStore.clear();
ThreadManager.threads = [];
AppState.agentThreads = {};
localStorage.clear();
sessionStorage.clear();
location.reload(true);
```

**Expected:** No threads appear (database empty, frontend doesn't create)

### Test 2: Send Message to Agent
1. Send "Hello" to Alpha agent
2. Wait for response

**Expected:**
- ✅ Backend creates thread in `sessions.threads`
- ✅ Backend inserts messages to `sessions.messages`
- ✅ Frontend receives `conversation_sync` event
- ✅ Frontend displays thread
- ❌ Frontend does NOT call UPSERT
- ❌ Frontend does NOT insert messages

**Verify:**
```sql
SELECT COUNT(*) FROM sessions.threads;  -- Should be 1
SELECT COUNT(*) FROM sessions.messages; -- Should be 2 (user + assistant)
```

### Test 3: Reload Page
1. Ctrl+F5 (hard refresh)
2. Check thread list

**Expected:**
- ✅ Thread loads from Supabase
- ❌ No duplicate threads created
- ❌ No messages re-inserted

**Verify:**
```sql
SELECT COUNT(*) FROM sessions.threads;  -- Still 1
SELECT COUNT(*) FROM sessions.messages; -- Still 2
```

### Test 4: Change Thread Location
1. Drag thread from Alpha to Bravo
2. Check database

**Expected:**
- ✅ Thread location updated to `agent-2`
- ❌ No new thread created
- ❌ No messages duplicated

**Verify:**
```sql
SELECT location FROM sessions.threads WHERE thread_slug = '...';
-- Should show 'agent-2'
```

---

## 📊 Impact Analysis

### Before Fix:
- ❌ Frontend creates phantom threads
- ❌ Messages saved twice (backend + frontend)
- ❌ UPSERT on every page load
- ❌ Database grows with duplicates
- ❌ Threads reappear after deletion

### After Fix:
- ✅ Backend is single source of truth
- ✅ Messages saved once by backend
- ✅ Frontend reads from Supabase
- ✅ Metadata updates only when needed
- ✅ No phantom threads
- ✅ Clean database

---

## 🔑 Key Principles

### 1. Backend Creates, Frontend Displays
- Backend creates threads during agent streaming
- Backend inserts messages during agent processing
- Frontend receives updates via `conversation_sync`
- Frontend displays data from Supabase

### 2. Supabase is Source of Truth
- All thread data stored in `sessions.threads`
- All messages stored in `sessions.messages`
- Frontend caches in memory only
- Realtime keeps frontend synchronized

### 3. Frontend Updates Metadata Only
- Location changes (thread assignment)
- Title/name changes
- Tags updates
- Archive status
- NEVER creates threads or messages

### 4. Cache is Ephemeral
- `MessageStore` is in-memory cache only
- `ThreadManager.threads` is display cache only
- Clear cache on page load to force Supabase read
- Never save cache back to database

---

## ✅ Implementation Checklist

- [ ] Remove UPSERT call from `thread_loader.js` line 82
- [ ] Disable `saveMessagesToBackend()` in `thread_loader.js` line 122
- [ ] Remove `saveThreadToBackend()` call from `agent-js.js` line 3636
- [ ] Create `/api/threads/<slug>/metadata` PATCH endpoint
- [ ] Update thread assignment to use PATCH instead of UPSERT
- [ ] Clear frontend caches on page load
- [ ] Add warning logs when deprecated save methods called
- [ ] Test with empty database
- [ ] Test with existing data
- [ ] Document new architecture in code comments

---

## 🚀 Quick Fix (Immediate)

**To stop phantom threads RIGHT NOW:**

1. **Comment out UPSERT in thread_loader.js:**
```javascript
// Line 82-95
// const upsertResponse = await fetch(`/api/threads/upsert`, { ... });
// const upsertData = await upsertResponse.json();
console.log(`[ThreadLoader] UPSERT disabled - backend creates threads`);
```

2. **Comment out message save in thread_loader.js:**
```javascript
// Line 104
// const saveResult = await this.saveMessagesToBackend(thread);
console.log(`[ThreadLoader] Message save disabled - backend handles this`);
return true;
```

3. **Comment out save in agent-js.js:**
```javascript
// Line 3636
// const saveSuccess = await ThreadManager.saveThreadToBackend(threadForSaving);
console.log(`[Agent ${agentId}] Save disabled - backend already saved via conversation_sync`);
```

4. **Clear everything:**
```sql
TRUNCATE TABLE sessions.threads CASCADE;
TRUNCATE TABLE sessions.messages CASCADE;
```

```javascript
window.MessageStore.clear();
ThreadManager.threads = [];
AppState.agentThreads = {};
localStorage.clear();
sessionStorage.clear();
location.reload(true);
```

5. **Test:** Send message to agent - should create thread ONCE (by backend only)

---

**Status:** Architecture defined - Implementation pending  
**Priority:** HIGH - Fixes phantom thread issue  
**Effort:** 2-3 hours to implement + test  
**Risk:** LOW - Backend already creates threads, just removing redundant frontend saves
