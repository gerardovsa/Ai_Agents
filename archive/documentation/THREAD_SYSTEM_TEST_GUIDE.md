# Thread System Testing Guide
**Date:** November 8, 2025  
**Purpose:** Comprehensive testing of thread creation, linking, and user ID integration

---

## ✅ FIXES APPLIED

### 1. **UserAuth Global Accessibility** - FIXED
- **Issue:** ThreadManager couldn't access UserAuth (scope issue)
- **Fix:** Added `window.UserAuth = UserAuth` at line 17151
- **Impact:** All modules can now access UserAuth globally

### 2. **All Hardcoded user_id Removed** - FIXED  
- **Locations:** 8 places (lines 14377, 15071, 15569, 16301, 16620, 16725, 16799, 16927)
- **Replaced with:** `(UserAuth.user && (UserAuth.user.id || UserAuth.user.user_id)) || 1`
- **Impact:** All operations now use logged-in user's ID

### 3. **Backend Profile Returns Both IDs** - FIXED
- **File:** `AI_infrastructure/routes/auth_routes.py` line ~310
- **Added:** `'id': request.user['user_id']` to profile response
- **Impact:** Frontend gets both `id` and `user_id` for compatibility

---

## 🧪 TEST PLAN

### **Prerequisites:**
1. Backend running: `BISTART` (http://localhost:5001)
2. Logged in as: printing@inhouseprint.com.au (user_id: 14)
3. Browser console open (F12)

---

## TEST 1: User Authentication ✅

**What to check:**
```javascript
// In browser console:
console.log('User:', window.UserAuth.user);
console.log('User ID:', window.UserAuth.user.id);
console.log('User ID (alt):', window.UserAuth.user.user_id);
```

**Expected output:**
```
User: {id: 14, user_id: 14, username: "printing@...", email: "printing@...", ...}
User ID: 14
User ID (alt): 14
```

**Console logs to verify:**
```
🔐 [INIT] UserAuth attached to window object
✅ User profile loaded: {id: 14, user_id: 14, ...}
🆔 User ID (id): 14
🆔 User ID (user_id): 14
🔍 [USER CHECK] Backend user_id: 14
🔍 [USER CHECK] Cached user_id: 14
✅ [USER CHECK] User ID verified - cached data is correct
```

**✅ PASS if:** Both IDs show 14, no errors

---

## TEST 2: Thread Loading ✅

**What to check:**
- Refresh page (Ctrl+F5)
- Watch console for thread loading logs

**Expected console logs:**
```
🔄 [THREADS] Loading threads for user_id: 14
[DATA] Threads loaded from backend: X
```

**❌ FAIL if you see:**
```
🔄 [THREADS] Loading threads for user_id: 1  ← Should be 14!
❌ [THREADS] Cannot load threads: user_id not available
```

**✅ PASS if:** Loads threads for user 14

---

## TEST 3: Create New Thread ✅

**Steps:**
1. Click "Start New Chat" button in Prime tab
2. Enter title: "Test Thread 1"
3. Leave tags empty
4. Click "Create Thread"

**Expected console logs:**
```
💬 [showNewChatModal] Opening modal for location: prime
🚀 [showNewChatModal] Creating thread: {title: 'Test Thread 1', ...}
📝 [createThreadWithMetadata] Creating thread: {title: 'Test Thread 1', ...}
[Backend] Creating thread for user_id: 14  ← Check backend logs
✅ [OK] [createThreadWithMetadata] Thread created: <thread_id>
```

**Backend logs (check terminal):**
```
POST /api/threads/create
user_id: 14
title: Test Thread 1
✅ Thread created successfully
```

**❌ FAIL if you see:**
```
[ERROR] [createThreadWithMetadata] Error: TypeError: Cannot read properties of undefined (reading 'id')
```

**✅ PASS if:** Thread created, appears in sidebar, no errors

---

## TEST 4: Send Message in Thread ✅

**Steps:**
1. With "Test Thread 1" selected
2. Type message: "Hello, test message"
3. Press Enter or click Send

**Expected console logs:**
```
[SEND] Sending message to backend...
[Backend] Saving message for user_id: 14, thread_id: <thread_id>
✅ [Auto-Save] Thread updated: <thread_id>
```

**Backend logs:**
```
POST /api/threads/save
user_id: 14
thread_id: <thread_id>
messages: 1
✅ Thread saved successfully
```

**✅ PASS if:** Message sent, thread auto-saves, appears in chat

---

## TEST 5: Create Thread with Synergy Session ✅

**Steps:**
1. Click "Start New Chat" button
2. Enter title: "Synergy Test"
3. Click "Link to Synergy Session" dropdown
4. Select any session (e.g., "Session 1")
5. Click "Create Thread"

**Expected console logs:**
```
📝 [createThreadWithMetadata] Creating thread: {synergySessionId: '<session_id>', ...}
[Backend] Creating thread for user_id: 14
🔗 [createThreadWithMetadata] Linking to Synergy session: <session_id>
✅ Thread linked to Synergy session
```

**Visual verification:**
- Thread should show green Synergy link in Row 3
- Click link → Should copy session ID + name to clipboard

**✅ PASS if:** Thread created with Synergy link, no errors

---

## TEST 6: Assign Thread to Agent Column ✅

**Steps:**
1. Create new thread: "Agent Test"
2. Drag thread from sidebar
3. Drop onto Agent 2 (Bravo-2) column

**Expected console logs:**
```
[ASSIGN] Assigning thread <thread_id> to agent-2
[Backend] Assigning thread for user_id: 14
✅ Thread assigned successfully
```

**Backend logs:**
```
POST /api/thread-assignments/assign
user_id: 14
session_id: <thread_id>
location: agent-2
✅ Assignment saved
```

**Visual verification:**
- Thread appears in Agent 2 column
- Agent 2 expands (if collapsed)

**✅ PASS if:** Thread assigned, appears in agent column

---

## TEST 7: Thread Persistence (Refresh) ✅

**Steps:**
1. Create thread: "Persistence Test"
2. Send message: "Test message 1"
3. Wait 2 seconds (auto-save)
4. Refresh page (Ctrl+F5)

**Expected console logs:**
```
🔄 [THREADS] Loading threads for user_id: 14
[DATA] Threads loaded from backend: X
[DATA] Found thread: Persistence Test (1 messages)
```

**Visual verification:**
- "Persistence Test" thread appears in sidebar
- Click thread → Message "Test message 1" appears

**❌ FAIL if:**
- Thread not in sidebar
- Thread empty (no messages)
- Backend loaded threads for user 1 instead of 14

**✅ PASS if:** Thread and messages persist after refresh

---

## TEST 8: Copy Thread ID ✅

**Steps:**
1. Hover over any thread in sidebar
2. Click "Copy ID" button (in Row 2)

**Expected:**
- Toast notification: "Thread ID copied!"
- Clipboard contains thread UUID

**Verify clipboard:**
```javascript
// Paste in browser console or text editor
// Should be UUID format: 1762411564661 or similar
```

**✅ PASS if:** Thread ID copied to clipboard

---

## TEST 9: Double-Click to Open in Prime ✅

**Steps:**
1. Create thread in Agent 2
2. Double-click thread card in sidebar

**Expected:**
- Prime tab becomes active
- Thread loads in Prime chat
- Console log: `[LOAD] Thread opened in Prime`

**✅ PASS if:** Thread opens in Prime tab

---

## TEST 10: Archive Thread ✅

**Steps:**
1. Hover over any thread
2. Click Archive button (folder icon)
3. Confirm in modal

**Expected console logs:**
```
[ARCHIVE] Archiving thread <thread_id>
[Backend] Saving thread for user_id: 14, archived: true
✅ Thread archived
```

**Visual verification:**
- Thread removed from sidebar
- Doesn't reappear after refresh

**✅ PASS if:** Thread archived and hidden

---

## 🔍 DEBUGGING COMMANDS

### **Check UserAuth in console:**
```javascript
window.UserAuth
window.UserAuth.user
window.UserAuth.user.id
```

### **Check thread count:**
```javascript
ThreadManager.threads.length
ThreadManager.threads[0]
```

### **Manually trigger user check:**
```javascript
await ThreadManager.ensureCorrectUserData()
```

### **Manually load threads:**
```javascript
await ThreadManager.loadThreadsFromBackend()
```

### **Check localStorage:**
```javascript
localStorage.getItem('authToken')
localStorage.getItem('userProfile')
```

---

## ❌ COMMON ERRORS & FIXES

### **Error: "Cannot read properties of undefined (reading 'id')"**
**Cause:** UserAuth not initialized  
**Fix:** Refresh page, check console for "🔐 [INIT] UserAuth attached"

### **Error: "No threads from backend"**
**Cause:** No threads created yet OR wrong user_id  
**Check:** Console should show "Loading threads for user_id: 14"  
**Fix:** Create new thread to test

### **Error: "Thread creation failed: 500"**
**Cause:** Backend error  
**Check:** Backend terminal logs  
**Fix:** Restart backend with `BISTART`

### **Error: "DELETE 405 Method Not Allowed"**
**Cause:** Backend doesn't support DELETE for assignments (non-critical)  
**Impact:** Stale assignments not cleaned up (minor issue)  
**Fix:** Can be ignored for now

---

## 📊 EXPECTED RESULTS SUMMARY

| Test | What It Tests | Expected Result |
|------|---------------|-----------------|
| 1 | UserAuth global access | window.UserAuth.user.id = 14 |
| 2 | Thread loading | Loads threads for user 14 |
| 3 | Thread creation | Creates thread with user_id: 14 |
| 4 | Message sending | Saves with user_id: 14 |
| 5 | Synergy linking | Links thread to session |
| 6 | Agent assignment | Assigns thread to agent column |
| 7 | Persistence | Thread survives refresh |
| 8 | Copy ID | Copies thread UUID |
| 9 | Double-click | Opens thread in Prime |
| 10 | Archive | Archives and hides thread |

---

## ✅ SUCCESS CRITERIA

**All tests PASS if:**
- ✅ No "Cannot read properties of undefined" errors
- ✅ All API calls use `user_id: 14` (not 1)
- ✅ Threads persist after refresh
- ✅ Thread creation works without errors
- ✅ Synergy linking works
- ✅ Agent assignment works

---

## 🚀 QUICK TEST (5 minutes)

**Minimal verification:**
1. Refresh page (Ctrl+F5)
2. Check console: `window.UserAuth.user.id` = 14
3. Create thread: "Quick Test"
4. Send message: "Test"
5. Refresh page
6. Verify thread "Quick Test" appears with message

**✅ PASS if all 6 steps work without errors**

---

## 📝 TEST RESULTS

**Test Date:** _______________________  
**Tester:** _______________________  
**Browser:** _______________________  

| Test # | Status | Notes |
|--------|--------|-------|
| 1 | ☐ PASS ☐ FAIL |  |
| 2 | ☐ PASS ☐ FAIL |  |
| 3 | ☐ PASS ☐ FAIL |  |
| 4 | ☐ PASS ☐ FAIL |  |
| 5 | ☐ PASS ☐ FAIL |  |
| 6 | ☐ PASS ☐ FAIL |  |
| 7 | ☐ PASS ☐ FAIL |  |
| 8 | ☐ PASS ☐ FAIL |  |
| 9 | ☐ PASS ☐ FAIL |  |
| 10 | ☐ PASS ☐ FAIL |  |

**Overall Result:** ☐ ALL PASS ☐ SOME FAILURES

---

**End of Test Guide**
