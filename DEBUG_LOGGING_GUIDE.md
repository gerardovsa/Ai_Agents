# Debug Logging Guide - Multi-Agent Dashboard
**Created:** November 21, 2025  
**Purpose:** Track thread loading, database queries, and location assignments

## Overview
Added comprehensive debug logging to track the entire flow from database → backend API → frontend loading → UI rendering.

---

## 🔍 What Was Added

### 1. Backend API Logging (`thread_routes.py`)
**File:** `AI_infrastructure/routes/thread_routes.py`  
**Endpoint:** `GET /api/threads/list`

**Logs Show:**
```
🔍 [THREAD API] /api/threads/list called
📊 [THREAD API] Parameters: user_id=14, limit=50
🗄️ [THREAD API] Database: Supabase
✅ [THREAD API] Query returned 12 rows
📍 [THREAD API] Location distribution: {'prime': 1, 'agent-1': 1, 'agent-2': 1, ...}
📤 [THREAD API] Returning 12 threads
   🧵 1763600801172: 'GAP 20ths 11am' → location=prime
   🧵 1763603287876: 'Agent Alpha' → location=agent-1
   🧵 1763649662447: 'Brwvo test' → location=agent-2
   ... and 9 more threads
```

**What to Check:**
- ✅ Query executes successfully
- ✅ Location distribution matches database
- ✅ All threads have location values (not null)

---

### 2. Frontend Thread Loading (`thread-manager-core.js`)
**File:** `UI/modules/thread-manager/thread-manager-core.js`  
**Function:** `loadThreadsFromBackend()`

**Logs Show:**
```
📥 [ThreadManager] Loading threads for user_id: 14
🌐 [ThreadManager] API URL: http://localhost:5001/api/threads/list?user_id=14
📡 [ThreadManager] Response status: 200 OK
📦 [ThreadManager] API response keys: ['success', 'data', 'message']
📦 [ThreadManager] Raw response: {success: true, data: {...}, message: '...'}
🔢 [ThreadManager] Extracted 12 threads from response
🔄 [ThreadManager] Processing 12 threads...
   📍 Thread 1: "GAP 20ths 11am" (1763600801172) → location="prime"
   📍 Thread 2: "Agent Alpha" (1763603287876) → location="agent-1"
   📍 Thread 3: "Brwvo test" (1763649662447) → location="agent-2"
✅ [ThreadManager] Threads loaded: 12
📊 [ThreadManager] Location distribution: {prime: 1, agent-1: 1, agent-2: 1, ...}
📋 [ThreadManager] All thread locations: ['1763600801172: prime', '1763603287876: agent-1', ...]
```

**What to Check:**
- ✅ API returns 200 status
- ✅ Response has correct structure
- ✅ Location values preserved during transformation
- ✅ Location distribution matches backend

---

### 3. Assignment Restoration (`thread-manager-assignment.js`)
**File:** `UI/modules/thread-manager/thread-manager-assignment.js`  
**Function:** `restoreThreadAssignments()`

**Logs Show:**
```
🔄 [Assignment] ========== RESTORING THREAD ASSIGNMENTS ==========
📊 [Assignment] Current threads in memory: 12
📍 [Assignment] Current locations: ['1763600801172→prime', '1763603287876→agent-1', ...]
👤 [Assignment] User ID: 14
🌐 [Assignment] Fetching from: http://localhost:5001/api/thread-assignments/list?user_id=14
📦 [Assignment] API response: {success: true, assignments: [...]}
✅ [Assignment] Restored 3 thread assignments
📋 [Assignment] Assignments: [{session_id: '1763603287876', location: 'agent-1'}, ...]
   🔄 Updated thread 1763603287876: "Agent Alpha" | agent-1 → agent-1
   🔄 Updated thread 1763649662447: "Brwvo test" | agent-2 → agent-2
✅ [Assignment] Updated 3/3 threads with locations

📍 [Assignment] ========== LOADING THREADS INTO AGENTS ==========
📍 [Assignment] 2 threads need to be loaded
   🎯 1763603287876: "Agent Alpha" → agent-1
   🎯 1763649662447: "Brwvo test" → agent-2
🔄 [Assignment] Loading "Agent Alpha" (1763603287876) into agent-1...
✅ [Assignment] Loaded thread "Agent Alpha" into agent-1
🔄 [Assignment] Loading "Brwvo test" (1763649662447) into agent-2...
✅ [Assignment] Loaded thread "Brwvo test" into agent-2
```

**What to Check:**
- ✅ Assignments API returns correct data
- ✅ Thread locations updated in memory
- ✅ MultiAgent.loadThreadIntoAgent() called for each agent
- ✅ No errors during loading

---

## 📍 Database Schema Reference

**Table:** `sessions.threads`  
**Key Column:** `location TEXT NULL`

**Valid Values:**
- `'prime'` - Main Prime agent
- `'agent-1'` through `'agent-26'` - Agent columns
- `'stock_ai'`, `'data_agent'`, `'single_viewer'` - Special agents

**Constraint:**
```sql
CHECK (
  (location = ANY(ARRAY['prime'::text, 'stock_ai'::text, 'data_agent'::text, 'single_viewer'::text]))
  OR (location ~ '^agent-([1-9]|1[0-9]|2[0-6])$'::text)
)
```

---

## 🐛 How to Use These Logs

### When Threads Don't Load:

1. **Open Browser Console** (F12)
2. **Refresh Page** (Ctrl+Shift+R)
3. **Check Logs in Order:**

   **Step 1: Backend API**
   ```
   Look for: 🔍 [THREAD API] /api/threads/list called
   Verify: Location distribution matches database
   ```

   **Step 2: Frontend Loading**
   ```
   Look for: 📥 [ThreadManager] Loading threads
   Verify: API response contains threads with locations
   Verify: Location distribution matches backend
   ```

   **Step 3: Assignment Restoration**
   ```
   Look for: 🔄 [Assignment] ========== RESTORING ==========
   Verify: Assignments fetched from API
   Verify: Threads updated with locations
   ```

   **Step 4: UI Loading**
   ```
   Look for: 📍 [Assignment] ========== LOADING THREADS INTO AGENTS ==========
   Verify: Each thread loaded into correct agent
   Verify: No errors during MultiAgent.loadThreadIntoAgent()
   ```

### Common Issues to Look For:

❌ **Location is NULL in database**
```
Look for: 📍 [THREAD API] Location distribution: {null: 5, ...}
Fix: Update database rows to set location column
```

❌ **Location lost during transformation**
```
Look for: 📍 Thread 1: "Title" → location="undefined"
Fix: Check thread-manager-core.js line 224 (location mapping)
```

❌ **Assignments API returns empty**
```
Look for: ✅ [Assignment] Restored 0 thread assignments
Fix: Check thread-assignments API endpoint
```

❌ **MultiAgent not ready**
```
Look for: ⏳ [Assignment] Waiting for MultiAgent to initialize...
Fix: Check MultiAgent module loading order
```

---

## 🔧 Server Terminal Logs

**Location:** Flask server terminal window (separate PowerShell)

**Look for:**
```
🔍 [THREAD API] /api/threads/list called
📊 [THREAD API] Parameters: user_id=14, limit=50
🗄️ [THREAD API] Database: Supabase
✅ [THREAD API] Query returned 12 rows
📍 [THREAD API] Location distribution: {'prime': 1, 'agent-1': 1, ...}
```

---

## 📝 Quick Reference

**Browser Console Logs:**
- ThreadManager loading: `📥 [ThreadManager]`
- Assignment restoration: `🔄 [Assignment]`
- Location updates: `📍 [Assignment]`
- Loading into agents: `🎯 [Assignment]`

**Server Terminal Logs:**
- API calls: `🔍 [THREAD API]`
- Database queries: `🗄️ [THREAD API]`
- Location distribution: `📍 [THREAD API]`

**Key Emojis:**
- 🔍 = Query/Search
- 📊 = Statistics
- 📍 = Location
- 🔄 = Update/Processing
- ✅ = Success
- ❌ = Error
- 📥 = Loading
- 📤 = Sending
- 🎯 = Target/Goal

---

## 🎯 Next Steps

1. **Refresh browser** (Ctrl+Shift+R)
2. **Open console** (F12)
3. **Look for the new logs**
4. **Report what you see** in the patterns above

**Expected Flow:**
```
Backend → Frontend Loading → Assignment Restoration → UI Rendering
   ↓            ↓                    ↓                      ↓
[THREAD API]  [ThreadManager]    [Assignment]      MultiAgent.load()
```

**If threads don't appear, check each step in order and report where it breaks.**

---

**Last Updated:** November 21, 2025
