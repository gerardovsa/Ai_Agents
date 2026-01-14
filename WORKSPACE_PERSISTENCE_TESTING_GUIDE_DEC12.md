# 🧪 WORKSPACE PERSISTENCE - TESTING GUIDE
**Date:** December 12, 2025  
**Status:** ✅ IMPLEMENTATION COMPLETE - READY FOR TESTING  
**Implementation:** WORKSPACE_PERSISTENCE_IMPLEMENTATION_COMPLETE_DEC12.md

---

## 📋 TESTING CHECKLIST

### ✅ COMPLETED IMPLEMENTATION

1. **Database Schema**
   - ✅ Created `DATABASE_SCHEMA_USER_COMMAND_CENTER.sql`
   - ✅ Table: `sessions.user_command_center`
   - ✅ Columns: user_id, workspace_data (JSONB), timestamps
   - ✅ Indexes: user_id lookup, last_sync monitoring
   - ⚠️ **ACTION REQUIRED:** Execute SQL in Supabase

2. **JavaScript Persistence Manager**
   - ✅ Created `UI/shared/js/workspace-manager.js` (950 lines)
   - ✅ Added script tag to `business-ai-platform-v2.html` line 676
   - ✅ localStorage API implementation
   - ✅ Database sync with 2-second debouncing
   - ✅ Auto-initialization on window load

3. **Agent Column Integration**
   - ✅ Modified `collapse()` function (saves collapsed state)
   - ✅ Modified `expand()` function (saves collapsed state)
   - ✅ Modified `toggleWidth()` function (saves width state)
   - ✅ Modified `setViewMode()` function (saves view mode)
   - ✅ Modified `create()` function (loads stored settings on init)

4. **Resizable Column CSS**
   - ✅ Added `.resize-handle` styles to `agent-ui.css`
   - ✅ 10px drag zone on right edge
   - ✅ `cursor: ew-resize` on hover
   - ✅ Hover highlight effect
   - ✅ `.resizing` state class for drag operations

---

## 🧪 TEST SCENARIOS

### Test 1: View Mode Persistence (localStorage)

**Steps:**
1. Open Multi-Agent Dashboard
2. Create agent column (Agent Alpha)
3. Change view mode using button (e.g., "AI Collapsed")
4. **Verify:** localStorage updated immediately
   ```javascript
   // Open browser console and run:
   JSON.parse(localStorage.getItem('agent_1_settings'))
   // Should show: { "viewMode": "ai-collapsed", ... }
   ```
5. Refresh page (F5)
6. **EXPECTED:** Agent Alpha loads with "AI Collapsed" view mode
7. **STATUS:** 🟢 PASS / 🔴 FAIL

---

### Test 2: Column Width Persistence (localStorage)

**Steps:**
1. Open Multi-Agent Dashboard
2. Create agent column (Agent Bravo)
3. Click width toggle button (top-right icon)
4. **Verify:** Column cycles through: 400px → 600px → 800px → 400px
5. **Verify:** localStorage updated
   ```javascript
   JSON.parse(localStorage.getItem('agent_2_settings'))
   // Should show: { "columnWidth": "wide" or "extra-wide", ... }
   ```
6. Refresh page
7. **EXPECTED:** Agent Bravo loads with last selected width
8. **STATUS:** 🟢 PASS / 🔴 FAIL

---

### Test 3: Collapsed State Persistence (localStorage)

**Steps:**
1. Open Multi-Agent Dashboard
2. Create agent column (Agent Charlie)
3. Click collapse button (< icon)
4. **Verify:** Column collapses to 60px vertical bar
5. **Verify:** localStorage updated
   ```javascript
   JSON.parse(localStorage.getItem('agent_3_settings'))
   // Should show: { "collapsed": true, ... }
   ```
6. Refresh page
7. **EXPECTED:** Agent Charlie loads in collapsed state
8. Click vertical bar to expand
9. **EXPECTED:** Column expands and saves collapsed:false
10. **STATUS:** 🟢 PASS / 🔴 FAIL

---

### Test 4: Resizable Column (Drag Right Edge)

**Steps:**
1. Open Multi-Agent Dashboard
2. Create agent column (Agent Delta)
3. Hover over right edge of column
4. **VERIFY:** Cursor changes to ↔ (ew-resize)
5. **VERIFY:** Right edge highlights on hover
6. Drag right edge to resize column
7. **EXPECTED:** Column width changes dynamically
8. **VERIFY:** localStorage updated with custom width
   ```javascript
   JSON.parse(localStorage.getItem('agent_4_settings'))
   // Should show: { "customWidth": 650, ... } (or whatever px value)
   ```
9. Refresh page
10. **EXPECTED:** Agent Delta loads with custom width
11. **STATUS:** 🟢 PASS / 🔴 FAIL

---

### Test 5: Database Sync (2-Second Debounce)

**Steps:**
1. Open Multi-Agent Dashboard
2. Create agent column (Agent Echo)
3. Make 5 rapid changes:
   - Change view mode
   - Toggle width
   - Collapse/expand 2x
   - Change view mode again
4. **VERIFY:** localStorage updates after EACH change
5. Wait 3 seconds (to allow 2-second debounce)
6. **VERIFY:** Database updated ONCE with final state
   ```sql
   -- Run in Supabase SQL Editor:
   SELECT workspace_data 
   FROM sessions.user_command_center 
   WHERE user_id = 'YOUR_USER_ID';
   
   -- Should show:
   {
     "agents": {
       "5": {
         "viewMode": "final-mode",
         "columnWidth": "final-width",
         "collapsed": false
       }
     }
   }
   ```
7. **STATUS:** 🟢 PASS / 🔴 FAIL

---

### Test 6: Cross-Device Sync (Database → localStorage)

**Steps:**
1. **Device 1 (Chrome):**
   - Open Multi-Agent Dashboard
   - Create Agent Foxtrot
   - Set view mode to "AI User"
   - Set width to "wide"
   - Wait 3 seconds for database sync
   - **VERIFY:** Database updated in Supabase

2. **Device 2 (Firefox/Incognito):**
   - Login with SAME user account
   - Open Multi-Agent Dashboard
   - Create Agent Foxtrot
   - **EXPECTED:** Agent loads with:
     - View mode: "AI User"
     - Column width: 600px (wide)
   - **VERIFY:** localStorage populated from database
     ```javascript
     JSON.parse(localStorage.getItem('agent_6_settings'))
     // Should match Device 1 settings
     ```

3. **STATUS:** 🟢 PASS / 🔴 FAIL

---

### Test 7: Multiple Agents (Isolated Settings)

**Steps:**
1. Open Multi-Agent Dashboard
2. Create 3 agent columns (Alpha, Bravo, Charlie)
3. Configure each differently:
   - Alpha: AI Collapsed, 400px, expanded
   - Bravo: All Expanded, 600px, expanded
   - Charlie: AI User, 800px, collapsed
4. **VERIFY:** localStorage has 3 separate keys:
   ```javascript
   localStorage.getItem('agent_1_settings') // Alpha
   localStorage.getItem('agent_2_settings') // Bravo
   localStorage.getItem('agent_3_settings') // Charlie
   ```
5. Refresh page
6. **EXPECTED:** All 3 agents load with their individual settings
7. **STATUS:** 🟢 PASS / 🔴 FAIL

---

### Test 8: Prime Chat Settings (Separate from Agents)

**Steps:**
1. Open Prime Chat (main chat interface)
2. Change view mode in Prime
3. **VERIFY:** localStorage updated with separate key:
   ```javascript
   JSON.parse(localStorage.getItem('prime_settings'))
   // Should show: { "viewMode": "...", ... }
   ```
4. **VERIFY:** Agent settings NOT affected:
   ```javascript
   localStorage.getItem('agent_1_settings') // Should be unchanged
   ```
5. Refresh page
6. **EXPECTED:** Prime loads with its view mode, agents load with theirs
7. **STATUS:** 🟢 PASS / 🔴 FAIL

---

### Test 9: Global Layout Settings

**Steps:**
1. Open Multi-Agent Dashboard
2. Create 4 agents in specific order
3. **VERIFY:** Layout saved to localStorage:
   ```javascript
   JSON.parse(localStorage.getItem('command_center_layout'))
   // Should show: { "agentOrder": [1, 2, 3, 4], "lastActiveAgent": 4 }
   ```
4. Refresh page
5. **EXPECTED:** Agents appear in same order
6. **STATUS:** 🟢 PASS / 🔴 FAIL

---

### Test 10: Error Handling (Database Offline)

**Steps:**
1. Open Multi-Agent Dashboard
2. Create agent column
3. Simulate database failure:
   - Open browser DevTools → Network tab
   - Set to "Offline" mode
4. Change view mode 3x
5. **EXPECTED BEHAVIOR:**
   - ✅ localStorage updates work (instant)
   - ⚠️ Database sync fails silently (logged to console)
   - ⚠️ User sees NO error messages
6. Re-enable network
7. Wait 3 seconds
8. **EXPECTED:** Database syncs with latest state
9. **STATUS:** 🟢 PASS / 🔴 FAIL

---

## 🛠️ DEBUGGING TOOLS

### Browser Console Commands

```javascript
// ==================== READ SETTINGS ====================

// Get agent settings
JSON.parse(localStorage.getItem('agent_1_settings'))

// Get Prime settings
JSON.parse(localStorage.getItem('prime_settings'))

// Get layout settings
JSON.parse(localStorage.getItem('command_center_layout'))

// List all workspace keys
Object.keys(localStorage).filter(k => k.includes('agent_') || k.includes('prime_') || k.includes('command_center_'))


// ==================== MODIFY SETTINGS ====================

// Force set agent width
WorkspaceManager.saveAgentSettings(1, { columnWidth: 'extra-wide', customWidth: 900 })

// Force set view mode
WorkspaceManager.saveAgentSettings(1, { viewMode: 'ai-user' })

// Force database sync NOW (bypass 2s debounce)
WorkspaceManager.syncToDatabase()


// ==================== CLEAR SETTINGS ====================

// Clear specific agent
localStorage.removeItem('agent_1_settings')

// Clear all agents
Object.keys(localStorage).filter(k => k.startsWith('agent_')).forEach(k => localStorage.removeItem(k))

// Clear everything (CAUTION: includes user auth)
localStorage.clear()


// ==================== INSPECT DATABASE ====================
// (Run in Supabase SQL Editor)

-- View all workspace data
SELECT 
    user_id,
    workspace_data,
    last_sync_at,
    created_at
FROM sessions.user_command_center;

-- View specific user
SELECT workspace_data 
FROM sessions.user_command_center 
WHERE user_id = 'YOUR_USER_ID';

-- View agent-specific settings
SELECT 
    user_id,
    workspace_data -> 'agents' -> '1' AS agent_1_settings,
    workspace_data -> 'prime' AS prime_settings
FROM sessions.user_command_center;

-- Check sync timestamps
SELECT 
    user_id,
    last_sync_at,
    NOW() - last_sync_at AS time_since_sync
FROM sessions.user_command_center
ORDER BY last_sync_at DESC;
```

---

## 🐛 COMMON ISSUES & FIXES

### Issue 1: Settings Not Persisting After Refresh

**Symptoms:**
- View mode resets to default
- Column width resets to 400px
- Collapsed state resets to expanded

**Diagnosis:**
```javascript
// Check if localStorage saving works
WorkspaceManager.saveAgentSettings(1, { test: 'value' })
JSON.parse(localStorage.getItem('agent_1_settings'))
// Should show: { "test": "value", ... }
```

**Possible Causes:**
1. ❌ workspace-manager.js not loaded
   - **Fix:** Verify script tag in business-ai-platform-v2.html line 676
2. ❌ localStorage disabled in browser
   - **Fix:** Enable cookies/storage in browser settings
3. ❌ Incognito mode (localStorage cleared on close)
   - **Fix:** Use normal browsing mode for persistent testing

---

### Issue 2: Database Not Syncing

**Symptoms:**
- localStorage updates work
- Database `workspace_data` column stays empty/old

**Diagnosis:**
```sql
-- Check if table exists
SELECT * FROM sessions.user_command_center LIMIT 1;

-- Check RLS policies
SELECT * FROM pg_policies WHERE tablename = 'user_command_center';
```

**Possible Causes:**
1. ❌ SQL schema not executed
   - **Fix:** Run `DATABASE_SCHEMA_USER_COMMAND_CENTER.sql` in Supabase
2. ❌ User not authenticated
   - **Fix:** Verify `supabaseClient.auth.getUser()` returns user ID
3. ❌ RLS policies blocking writes
   - **Fix:** Check policy allows INSERT/UPDATE for authenticated users
4. ❌ Database connection offline
   - **Fix:** Check browser console for network errors

---

### Issue 3: Resize Handle Not Working

**Symptoms:**
- Cursor doesn't change to ↔ on right edge
- Dragging doesn't resize column

**Diagnosis:**
```javascript
// Check if CSS loaded
const column = document.getElementById('agent-column-1')
const handle = column.querySelector('.resize-handle')
console.log(handle) // Should be HTMLElement, not null
console.log(getComputedStyle(handle).cursor) // Should be "ew-resize"
```

**Possible Causes:**
1. ❌ CSS not applied
   - **Fix:** Verify agent-ui.css loaded (check DevTools → Network)
   - **Fix:** Hard refresh (Ctrl+Shift+R) to clear CSS cache
2. ❌ .resize-handle element not created
   - **Fix:** Check agent-column.js `create()` function generates div
3. ❌ z-index conflict
   - **Fix:** Increase `.resize-handle { z-index: 100; }` to higher value

---

### Issue 4: Cross-Device Sync Not Working

**Symptoms:**
- Device 1 saves settings
- Device 2 doesn't load settings

**Diagnosis:**
```sql
-- Verify data in database
SELECT workspace_data FROM sessions.user_command_center 
WHERE user_id = 'YOUR_USER_ID';
```

**Possible Causes:**
1. ❌ Different user accounts
   - **Fix:** Login with SAME email/password on both devices
2. ❌ Database not synced yet
   - **Fix:** Wait 3+ seconds after changes before checking Device 2
3. ❌ localStorage overriding database
   - **Fix:** Clear localStorage on Device 2, then reload:
     ```javascript
     localStorage.clear()
     location.reload()
     ```

---

## 📊 SUCCESS METRICS

### ✅ PASSING CRITERIA

Test passes if:
1. **localStorage:** All changes saved immediately (< 100ms)
2. **Database:** Changes synced within 2-5 seconds
3. **Persistence:** Settings survive page refresh/browser restart
4. **Cross-Device:** Settings sync across different browsers/devices
5. **Performance:** No lag/freezing during save operations
6. **Isolation:** Agent settings don't interfere with each other
7. **UI:** Resize handles visible and functional
8. **Errors:** No JavaScript errors in console

---

## 📝 TEST RESULTS TEMPLATE

Copy this template for reporting test results:

```markdown
## WORKSPACE PERSISTENCE TEST RESULTS
**Date:** YYYY-MM-DD  
**Tester:** [Your Name]  
**Browser:** Chrome/Firefox/Safari [Version]  
**Environment:** Development/Production

### Test 1: View Mode Persistence
- **Status:** 🟢 PASS / 🔴 FAIL
- **Notes:** [Any observations]

### Test 2: Column Width Persistence
- **Status:** 🟢 PASS / 🔴 FAIL
- **Notes:** [Any observations]

### Test 3: Collapsed State Persistence
- **Status:** 🟢 PASS / 🔴 FAIL
- **Notes:** [Any observations]

### Test 4: Resizable Column
- **Status:** 🟢 PASS / 🔴 FAIL
- **Notes:** [Any observations]

### Test 5: Database Sync
- **Status:** 🟢 PASS / 🔴 FAIL
- **Notes:** [Any observations]

### Test 6: Cross-Device Sync
- **Status:** 🟢 PASS / 🔴 FAIL
- **Notes:** [Any observations]

### Test 7: Multiple Agents
- **Status:** 🟢 PASS / 🔴 FAIL
- **Notes:** [Any observations]

### Test 8: Prime Chat Settings
- **Status:** 🟢 PASS / 🔴 FAIL
- **Notes:** [Any observations]

### Test 9: Global Layout
- **Status:** 🟢 PASS / �4 FAIL
- **Notes:** [Any observations]

### Test 10: Error Handling
- **Status:** 🟢 PASS / 🔴 FAIL
- **Notes:** [Any observations]

### OVERALL RESULT
- **Pass Rate:** X/10 tests passed
- **Critical Issues:** [List any blocking issues]
- **Recommendations:** [Next steps]
```

---

## 🚀 DEPLOYMENT STEPS

### Step 1: Execute SQL Schema (REQUIRED)

1. Login to Supabase Dashboard
2. Go to SQL Editor
3. Open `DATABASE_SCHEMA_USER_COMMAND_CENTER.sql`
4. Execute script
5. **Verify:**
   ```sql
   SELECT * FROM sessions.user_command_center LIMIT 1;
   -- Should return empty table (no error)
   ```

### Step 2: Deploy Files (COMPLETED)

✅ `UI/shared/js/workspace-manager.js` - Created  
✅ `UI/modules_internal/agents/agent-column.js` - Modified  
✅ `UI/modules_internal/agents/agent-ui.css` - Modified  
✅ `UI/business-ai-platform-v2.html` - Modified (line 676)

### Step 3: Test localStorage (Manual)

1. Clear browser cache: Ctrl+Shift+Delete
2. Hard refresh: Ctrl+Shift+R
3. Run Test 1-4 from checklist above
4. **Expected:** All localStorage tests pass

### Step 4: Test Database Sync (Manual)

1. Run Test 5 from checklist
2. **Expected:** Database updates after 2-3 seconds
3. Verify in Supabase SQL Editor

### Step 5: Test Cross-Device Sync (Manual)

1. Run Test 6 from checklist
2. **Expected:** Settings sync across devices

### Step 6: Monitor Production (Ongoing)

```sql
-- Daily check: How many users have workspace data?
SELECT COUNT(DISTINCT user_id) AS users_with_workspaces
FROM sessions.user_command_center;

-- Weekly check: Most active syncs
SELECT 
    user_id,
    last_sync_at,
    JSONB_ARRAY_LENGTH(workspace_data -> 'agents') AS agent_count
FROM sessions.user_command_center
ORDER BY last_sync_at DESC
LIMIT 10;
```

---

## 📞 SUPPORT

**Implementation Docs:** `WORKSPACE_PERSISTENCE_IMPLEMENTATION_COMPLETE_DEC12.md`  
**Database Schema:** `DATABASE_SCHEMA_USER_COMMAND_CENTER.sql`  
**Code Files:**
- `UI/shared/js/workspace-manager.js` (persistence manager)
- `UI/modules_internal/agents/agent-column.js` (integration)
- `UI/modules_internal/agents/agent-ui.css` (resize handle styles)

**Questions?** Check implementation docs first, then test with browser console debugging commands above.

---

**END OF TESTING GUIDE** ✅
