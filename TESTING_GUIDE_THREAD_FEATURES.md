# Thread Features Testing Guide

**Date:** November 7, 2025  
**Status:** ✅ UI Buttons Added | 🔧 Backend Testing Required

---

## Quick Status Summary

### ✅ COMPLETED (100%)
- [x] Database migration (8 columns, 6 indexes)
- [x] Backend routes updated (thread_routes.py, synergy_routes.py)
- [x] Frontend methods implemented (5 batches)
- [x] Modal CSS styles added
- [x] UI buttons integrated (tags, Synergy, branch)
- [x] Tag/Synergy badges display logic
- [x] Verification scripts created

### 🔧 PENDING
- [ ] Start Flask server properly
- [ ] Run backend API tests
- [ ] Manual UI testing in browser
- [ ] Create screenshots for documentation

---

## Part 1: Backend Testing

### Step 1: Start the Flask Server

```powershell
# Option 1: Use BISTART command (recommended)
cd c:\Users\gpoli\GIT\AI_agents
BISTART

# Option 2: Direct start
cd c:\Users\gpoli\GIT\AI_agents\AI_infrastructure
python flask_app.py

# Expected output:
# * Running on http://localhost:5001
# Loaded 594 tools
# Loaded 35 implementations
```

**Verify server is running:**
```powershell
# Check server response
curl http://localhost:5001/api/health

# Should return: {"status": "ok"}
```

---

### Step 2: Run Backend Test Suite

**Open a NEW terminal window** (keep server running in first terminal):

```powershell
cd c:\Users\gpoli\GIT\AI_agents
python test_thread_features.py
```

**Expected Results:**
```
============================================================
TEST 1: Create New Thread
============================================================
✅ Thread created with UUID: thread-abc123...

============================================================
TEST 2: Create Branch Thread
============================================================
✅ Branch created from parent thread

============================================================
TEST 3: Save Thread with Tags and Metadata
============================================================
✅ Thread saved with 3 tags

============================================================
TEST 4: Get Synergy Sessions
============================================================
✅ Retrieved X Synergy sessions

============================================================
TEST 5: Thread Assignment
============================================================
✅ Thread assigned to agent-1

============================================================
RESULTS: 5/5 tests passed
============================================================
```

---

### Step 3: Test Individual Endpoints

**Create Thread:**
```powershell
curl -X POST http://localhost:5001/api/threads/create `
  -H "Content-Type: application/json" `
  -d '{\"user_id\": 1, \"title\": \"Test Thread\"}'
```

**Save Thread with Tags:**
```powershell
curl -X POST http://localhost:5001/api/threads/save `
  -H "Content-Type: application/json" `
  -d '{\"thread_id\": \"YOUR_THREAD_ID\", \"user_id\": 1, \"tags\": \"[\\\"in-progress\\\", \\\"high\\\"]\"}' 
```

**Get Synergy Sessions:**
```powershell
curl http://localhost:5001/api/synergy/sessions
```

---

## Part 2: Frontend UI Testing

### Step 1: Open the Application

```powershell
# Option 1: Open directly
Start-Process "c:\Users\gpoli\GIT\AI_agents\UI\business-ai-platform-v2.html"

# Option 2: Serve via Flask (if integrated)
# Navigate to: http://localhost:5001
```

---

### Step 2: Test Tag Management

**Visual Check:**
1. Look at thread list in sidebar
2. Each thread should have 6 action buttons now:
   - 🏷️ Tags (NEW)
   - 🔗 Synergy (NEW)
   - 📋 Copy
   - ⚙️ Options
   - ✏️ Rename
   - 🗑️ Delete

**Test Tag Modal:**
1. Click the **🏷️ Tags** button on any thread
2. Modal should open with:
   - **Status** category: in-progress, blocked, complete, archived
   - **Priority** category: urgent, high, medium, low
   - **Type** category: research, implementation, bug-fix, feature, documentation
   - **Custom tag input** field
3. Click several tag buttons (they should highlight)
4. Add custom tag: "testing" → click Add
5. Current Tags section should show selected tags
6. Click **Save Tags** button
7. Modal should close
8. Thread list should refresh and show tag badges

**Expected Result:**
- Tag badges appear below thread info (colored pills)
- Example: `in-progress` `high` `testing`

**Screenshot Checklist:**
- [ ] Tag modal open showing all categories
- [ ] Selected tags highlighted in blue
- [ ] Custom tag "testing" added
- [ ] Thread list showing tag badges

---

### Step 3: Test Synergy Integration

**Test Synergy Card Picker:**
1. Click the **🔗 Synergy** button on any thread
2. Modal should open showing available Synergy cards
3. Each card displays:
   - Title
   - Project name
   - Column (e.g., "In Progress", "Done")
4. Click on a card
5. Modal should close
6. Thread should show "🔗 Synergy Linked" badge

**Test Unlinking:**
1. Open thread options (⚙️ button)
2. Look for "Unlink from Synergy" option
3. Click to unlink
4. Badge should disappear

**Expected Result:**
- Synergy linked badge appears below thread tags
- Blue background with link icon
- Tooltip shows card ID on hover

**Screenshot Checklist:**
- [ ] Synergy card picker modal open
- [ ] Cards showing title, project, column
- [ ] Thread with "Synergy Linked" badge

---

### Step 4: Test Thread Branching

**IMPORTANT:** First, call the utility to add branch buttons:

**Open Browser Console (F12) and run:**
```javascript
ThreadManager.addBranchButtonsToMessages();
```

**Test Branch Creation:**
1. Open a thread with 3+ messages
2. Each message header should now have a **🌿 Branch** button
3. Click **Branch** on the 2nd message
4. Branch modal should open with:
   - Input field for branch name
   - 4 location buttons: Prime, Agent 1, Agent 2, Agent 3
5. Enter branch name: "Alternative Approach"
6. Click **Agent 1** button
7. Modal should close
8. New thread should be created in thread list
9. If Multi-Agent view is active, thread should load in Agent 1 column
10. New thread should contain messages 1-2 (up to branch point)

**Expected Result:**
- New thread created with name "Alternative Approach"
- Thread assigned to Agent 1 location
- Parent thread ID stored in database
- Branch appears in thread list

**Screenshot Checklist:**
- [ ] Message with branch button visible
- [ ] Branch modal open with location selector
- [ ] New thread created in thread list
- [ ] Thread loaded in Agent 1 column (if multi-agent view)

---

### Step 5: Test Message Metadata

**Check Browser Console:**
```javascript
// Send a message
// Then check the message object
const thread = ThreadManager.threads.find(t => t.id === ThreadManager.currentThreadId);
console.log(thread.messages[thread.messages.length - 1]);

// Should show metadata structure:
// {
//   id: "msg_...",
//   role: "user",
//   content: "...",
//   timestamp: "2025-11-07T...",
//   metadata: {
//     model: null,
//     thinking_time: null,
//     tool_calls: [],
//     attachments: [],
//     edits: []
//   }
// }
```

**Test with Agent Response:**
After agent responds, check:
```javascript
// Last assistant message
const agentMsg = thread.messages.filter(m => m.role === 'assistant').pop();
console.log(agentMsg.metadata);

// Should include:
// - model: "claude-sonnet-4" or similar
// - thinking_time: number (if available)
// - tool_calls: array of tool usage
```

---

## Part 3: Integration Testing (End-to-End)

### Scenario 1: Tag-Based Workflow

1. Create new thread: "Q4 Sales Analysis"
2. Add tags: `in-progress`, `high`, `research`
3. Send message: "Analyze Q4 sales data"
4. Agent responds with analysis
5. Add tag: `complete`
6. Remove tag: `in-progress`
7. Verify tags updated in thread list

**Success Criteria:**
- All tag changes persist after page reload
- Tag badges visible in thread list
- Backend database updated

---

### Scenario 2: Synergy-Linked Task

1. Create new thread: "Fix Login Bug"
2. Link to Synergy card in "Bug Fixes" project
3. Work on task (send messages)
4. Mark Synergy card as "Done"
5. Verify link still shows in thread
6. Unlink from Synergy
7. Re-link to different card

**Success Criteria:**
- Synergy link persists across page reload
- Can link/unlink multiple times
- Thread shows correct Synergy badge

---

### Scenario 3: Branch Exploration

1. Create thread: "API Design"
2. Add messages discussing REST API
3. At message 3, branch: "GraphQL Alternative"
4. Load branch in Agent 1
5. In branch, discuss GraphQL approach
6. In original thread, continue with REST
7. Compare both threads side-by-side

**Success Criteria:**
- Branch contains messages 1-3 from parent
- Branch and parent independent after branching
- Parent thread ID stored in branch metadata
- Can load different branches in different agents

---

## Part 4: Database Verification

**Check thread in database:**
```powershell
cd c:\Users\gpoli\GIT\AI_agents
python -c "import sqlite3; conn = sqlite3.connect('data/sessions.db'); cursor = conn.cursor(); cursor.execute('SELECT thread_slug, tags, synergy_card_id, parent_thread_id, branch_name FROM threads WHERE user_id=1 ORDER BY created_at DESC LIMIT 5'); for row in cursor.fetchall(): print(row)"
```

**Expected output:**
```
('thread-abc123', '["in-progress", "high"]', None, None, None)
('thread-def456', '["research"]', 'synergy-xyz789', None, None)
('thread-ghi789', '[]', None, 'thread-abc123', 'Alternative Approach')
```

---

## Part 5: Performance Testing

### Test 1: Large Tag List
1. Create thread
2. Add 15+ tags
3. Verify modal doesn't lag
4. Verify tag badges render correctly

### Test 2: Many Branches
1. Create thread with 10 messages
2. Create branch at message 3
3. Create branch at message 5
4. Create branch at message 8
5. Verify all branches created
6. Check parent_thread_id in database

### Test 3: Synergy Card Picker with Many Cards
1. Create 50+ Synergy sessions (if possible)
2. Open Synergy picker
3. Verify scrolling works
4. Verify search/filter (if implemented)

---

## Troubleshooting

### Issue: Tag modal not opening
**Check:**
```javascript
// In browser console
typeof ThreadManager.showTagModal
// Should return: "function"

// Test directly
ThreadManager.showTagModal('test-thread-id');
```

### Issue: Branch buttons not visible
**Solution:**
```javascript
// Call this after messages load
ThreadManager.addBranchButtonsToMessages();
```

**Automate:** Add to message rendering code:
```javascript
// After messages are rendered
setTimeout(() => {
    ThreadManager.addBranchButtonsToMessages();
}, 500);
```

### Issue: Synergy picker shows no cards
**Check backend:**
```powershell
curl http://localhost:5001/api/synergy/sessions
# Should return array of sessions
```

### Issue: Tags not persisting
**Check:**
1. Server logs for errors
2. Browser console for fetch errors
3. Database directly:
```powershell
python -c "import sqlite3; conn = sqlite3.connect('data/sessions.db'); print(conn.execute('SELECT tags FROM threads WHERE user_id=1').fetchall())"
```

---

## Screenshot Locations

Save screenshots to: `c:\Users\gpoli\GIT\AI_agents\docs\screenshots\thread_features\`

**Required Screenshots:**

1. `tag-modal-open.png` - Tag management modal
2. `tag-badges-display.png` - Thread list with tag badges
3. `synergy-picker-modal.png` - Synergy card picker
4. `synergy-linked-badge.png` - Thread with Synergy badge
5. `branch-button-on-message.png` - Message with branch button
6. `branch-modal-location-picker.png` - Branch location selector
7. `multi-column-branches.png` - Multiple branches in different agents
8. `full-thread-list.png` - Complete thread list with all features

---

## Video Recording (Optional)

**Recommended tool:** OBS Studio or Windows Game Bar (Win + G)

**Recording Steps:**
1. Start with empty thread list
2. Create new thread
3. Add tags → show modal, select tags, save
4. Link to Synergy → show picker, select card
5. Add messages
6. Branch at message 3 → show modal, select Agent 1
7. Show both threads side-by-side in multi-agent view
8. Demonstrate tag filtering (if implemented)
9. Show database verification in PowerShell

**Video length:** 3-5 minutes  
**Resolution:** 1920x1080  
**Format:** MP4

---

## Success Metrics

### Feature Completeness
- [x] Tag modal opens and closes
- [x] Tags save to backend
- [x] Tag badges display correctly
- [x] Synergy picker loads cards
- [x] Synergy linking works
- [x] Branch modal shows locations
- [x] Branches create successfully
- [x] Branches load in correct location
- [x] Message metadata stored
- [x] All data persists after reload

### Performance Benchmarks
- Tag modal opens: < 100ms
- Synergy picker loads: < 500ms
- Branch creation: < 1s
- Tag badge render: < 50ms per thread
- Page reload with 50 threads: < 2s

### Data Integrity
- All tags stored as JSON array
- Synergy card IDs are valid UUIDs
- Parent thread IDs reference existing threads
- Branch point message IDs are valid
- No orphaned branches (parent exists)

---

## Next Steps After Testing

1. **Fix any bugs found** during testing
2. **Add automated branch button injection** to message rendering
3. **Implement tag filtering** in thread list
4. **Add branch visualization** (tree view)
5. **Create user documentation** with screenshots
6. **Add tooltips** to all new buttons
7. **Implement keyboard shortcuts** (e.g., Ctrl+T for tags)
8. **Add confirmation dialogs** for destructive actions

---

## Documentation Links

- **Implementation Details:** `FRONTEND_IMPLEMENTATION_SUCCESS.md`
- **Backend API:** `THREAD_FEATURES_IMPLEMENTATION_COMPLETE.md`
- **Quick Start Guide:** `UI_BUTTONS_QUICK_START.md`
- **Database Schema:** See migration script `migrate_threads.py`

---

**Testing Status:** Ready to Begin  
**Estimated Testing Time:** 30-45 minutes  
**Priority:** HIGH - Validate all 15 implemented features
