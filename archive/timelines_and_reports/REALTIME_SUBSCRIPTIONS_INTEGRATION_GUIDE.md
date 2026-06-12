# Supabase Real-time Subscriptions Integration Guide

## 🎯 Purpose

This guide explains how to enable comprehensive Supabase real-time subscriptions across all application modules for live, multi-tab synchronized updates.

## ✅ What's Been Completed

### 1. Centralized Subscription Manager Created
**File:** `UI/shared/js/realtime-subscriptions-init.js`

This new module handles ALL real-time subscriptions in one place:
- ✅ **Heartbeat** - Server health monitoring (60s interval)
- ✅ **Workspace** - Cross-tab sync (user_command_center table)
- ✅ **Threads** - Thread updates (saved_threads table)
- ✅ **Synergy** - Kanban board updates (4 tables: sessions, milestones, tasks, subtasks)
- ✅ **Credentials** - OAuth token updates (user_platform_credentials table)
- ✅ **Sessions** - User session updates (user_sessions table)

### 2. User Authentication Updated
**File:** `UI/modules_internal/components/user_auth.js` (after line 505)

Added initialization call during app startup:
```javascript
// Initialize ALL real-time subscriptions
if (window.RealtimeSubscriptionsInit) {
    await window.RealtimeSubscriptionsInit.initialize();
    const activeSubs = window.RealtimeSubscriptionsInit.getActiveSubscriptions();
    console.log(`✅ [AUTH] Real-time subscriptions initialized (${activeSubs.length} active):`, activeSubs);
}
```

## 📋 Next Steps: Load the New Script

### Option 1: Add to LazyLoader/ModuleManager
If your app uses the lazy-loading module system mentioned in the conversation summary, register the new script:

**File:** `UI/shared/js/module-loader.js` or equivalent
```javascript
// Add to shared scripts list
const sharedScripts = [
    'UI/shared/js/supabase-connection-manager.js',
    'UI/shared/js/supabase-realtime-manager.js',
    'UI/shared/js/realtime-subscriptions-init.js',  // ← NEW
    // ... other shared scripts
];
```

### Option 2: Add to HTML Template (if exists)
If you have an HTML file that loads scripts, add before `user_auth.js`:

```html
<!-- Supabase Infrastructure -->
<script src="/UI/shared/js/supabase-connection-manager.js"></script>
<script src="/UI/shared/js/supabase-realtime-manager.js"></script>
<script src="/UI/shared/js/realtime-subscriptions-init.js"></script>  <!-- NEW -->

<!-- Authentication (will call RealtimeSubscriptionsInit.initialize()) -->
<script src="/UI/modules_internal/components/user_auth.js"></script>
```

### Option 3: Dynamic Import (if using ES modules)
```javascript
// In your main initialization file
await import('./UI/shared/js/realtime-subscriptions-init.js');
await window.RealtimeSubscriptionsInit.initialize();
```

## 🔍 Verification Steps

After loading the script and reloading the page, you should see these console logs:

### Step 1: Script Loaded
```
✅ RealtimeSubscriptionsInit loaded successfully
```

### Step 2: Initialization Started
```
🔄 [AUTH] Initializing real-time subscriptions...
🔄 [Realtime Init] Initializing all subscriptions...
📡 [Realtime Init] Setting up subscriptions for user 14...
```

### Step 3: Individual Subscriptions
```
💓 [Realtime Init] Subscribing to heartbeat...
✅ [Realtime Init] Heartbeat subscription active

🗂️ [Realtime Init] Subscribing to workspace updates...
✅ [Realtime Init] Workspace subscription active

💬 [Realtime Init] Subscribing to thread updates...
✅ [Realtime Init] Threads subscription active

📋 [Realtime Init] Subscribing to Synergy (Kanban) updates...
✅ [Realtime Init] Synergy subscriptions active (4 tables)

🔑 [Realtime Init] Subscribing to credential updates...
✅ [Realtime Init] Credentials subscription active

🔐 [Realtime Init] Subscribing to session updates...
✅ [Realtime Init] Sessions subscription active
```

### Step 4: Completion Summary
```
✅ [Realtime Init] All subscriptions initialized successfully
📊 [Realtime Init] Active subscriptions: 7
✅ [AUTH] Real-time subscriptions initialized (7 active): ['heartbeat', 'workspace', 'threads', 'synergy-synergy_sessions', 'synergy-milestones', 'synergy-tasks', 'synergy-subtasks', 'credentials', 'sessions']
```

## 📊 What This Enables

### 1. **Cross-Tab Sync** (Workspace)
- Open 2 browser tabs
- Change agent column width in Tab 1
- Tab 2 updates automatically (no refresh needed)

### 2. **Live Thread Updates** (ThreadManager)
- Create/edit/delete threads
- All open tabs see changes immediately
- Thread list stays synchronized

### 3. **Live Kanban Updates** (Synergy Dashboard)
- Move task to different milestone
- All collaborators see the move in real-time
- No page refresh needed

### 4. **OAuth Token Refresh** (Credentials)
- When OAuth token auto-refreshes
- Account sidebar shows updated status immediately
- No need to reload page

### 5. **Session Monitoring** (Sessions)
- New login detected across tabs
- Session list updates in real-time
- Multi-device awareness

### 6. **Server Health Monitoring** (Heartbeat)
- Every 60 seconds, check if Supabase is alive
- Detect disconnections early
- Auto-reconnect when server comes back

## 🔧 Module Integration (Optional Enhancement)

The subscription manager sends events to modules if they implement a `handleRealtimeUpdate()` method:

### ThreadManager Example
**File:** `UI/modules_internal/thread-manager/thread-manager-core.js`

```javascript
class ThreadManager {
    // ... existing code ...

    /**
     * Handle real-time thread updates from Supabase
     * Called by RealtimeSubscriptionsInit when thread changes detected
     */
    handleRealtimeUpdate(payload) {
        console.log('🔔 [ThreadManager] Real-time update:', payload);

        const eventType = payload.eventType;  // 'INSERT', 'UPDATE', or 'DELETE'
        const newData = payload.new;  // New row data
        const oldData = payload.old;  // Old row data (for DELETE)

        if (eventType === 'INSERT') {
            // New thread created (possibly in another tab)
            this.addThread(newData);
        } else if (eventType === 'UPDATE') {
            // Thread metadata changed
            this.updateThread(newData);
        } else if (eventType === 'DELETE') {
            // Thread deleted
            this.removeThread(oldData.id);
        }

        // Refresh UI
        this.refreshThreadList();
    }

    // ... existing code ...
}
```

### SynergyManager Example
**File:** `UI/modules_internal/synergy/synergy-manager.js`

```javascript
class SynergyManager {
    /**
     * Handle real-time Synergy updates from Supabase
     * @param {string} table - 'synergy_sessions', 'milestones', 'tasks', or 'subtasks'
     * @param {object} payload - Event payload with eventType, new, old
     */
    handleRealtimeUpdate(table, payload) {
        console.log(`🔔 [SynergyManager:${table}] Real-time update:`, payload);

        if (table === 'milestones') {
            this.handleMilestoneUpdate(payload);
        } else if (table === 'tasks') {
            this.handleTaskUpdate(payload);
        } else if (table === 'subtasks') {
            this.handleSubtaskUpdate(payload);
        }
    }

    handleMilestoneUpdate(payload) {
        if (payload.eventType === 'INSERT') {
            // New milestone added
            this.addMilestoneColumn(payload.new);
        } else if (payload.eventType === 'UPDATE') {
            // Milestone renamed or reordered
            this.updateMilestoneColumn(payload.new);
        } else if (payload.eventType === 'DELETE') {
            // Milestone deleted
            this.removeMilestoneColumn(payload.old.id);
        }
    }

    // Similar handlers for tasks and subtasks...
}
```

### AccountSidebar Example
**File:** `UI/modules_internal/components/account_profile.js`

```javascript
class AccountSidebar {
    /**
     * Handle real-time credential updates
     */
    handleRealtimeUpdate(payload) {
        console.log('🔔 [AccountSidebar] Credential update:', payload);

        if (payload.eventType === 'UPDATE') {
            // OAuth token refreshed
            const platform = payload.new.platform;
            this.updateCredentialBadge(platform, 'connected');
        }
    }

    /**
     * Handle real-time session updates
     */
    refreshSessions() {
        console.log('🔄 [AccountSidebar] Refreshing session list...');
        // Reload session list from database
        this.loadSessions();
    }
}
```

## 🗄️ Database Setup (Optional - For DELETE Events)

If you want full row data in DELETE events, enable REPLICA IDENTITY on Supabase tables:

```sql
-- Run in Supabase SQL Editor
ALTER TABLE sessions.user_command_center REPLICA IDENTITY FULL;
ALTER TABLE sessions.saved_threads REPLICA IDENTITY FULL;
ALTER TABLE synergy_sessions.synergy_sessions REPLICA IDENTITY FULL;
ALTER TABLE synergy_sessions.milestones REPLICA IDENTITY FULL;
ALTER TABLE synergy_sessions.tasks REPLICA IDENTITY FULL;
ALTER TABLE synergy_sessions.subtasks REPLICA IDENTITY FULL;
ALTER TABLE ai_infrastructure.user_platform_credentials REPLICA IDENTITY FULL;
ALTER TABLE sessions.user_sessions REPLICA IDENTITY FULL;
```

**Note:** Without this, DELETE events only include primary key in `payload.old`. With REPLICA IDENTITY FULL, you get the full row data.

## 🧪 Testing Real-time Subscriptions

### Test 1: Workspace Cross-Tab Sync
1. Open 2 tabs of your app
2. In Tab 1, open browser console: `F12`
3. Run: `WorkspaceManager.saveSetting('test_column_width', 500)`
4. In Tab 2 console, you should see:
   ```
   🔔 [Workspace] Update received: {eventType: 'INSERT', new: {key: 'test_column_width', value: 500}}
   ```

### Test 2: Thread Real-time Updates
1. Open 2 tabs
2. In Tab 1, create a new thread
3. In Tab 2 console, you should see:
   ```
   🔔 [Threads] Update received: {eventType: 'INSERT', new: {id: 123, title: 'New Thread', ...}}
   ```

### Test 3: Heartbeat
Wait 60 seconds and check console:
```
💓 [RealtimeManager] Heartbeat received: {status: 'ok'}
```

## 🚨 Troubleshooting

### Issue: No console logs after page reload
**Solution:** The script wasn't loaded. Check step "Load the New Script" above.

### Issue: "RealtimeSubscriptionsInit is not defined"
**Solution:** Script loaded after `user_auth.js`. Ensure loading order:
1. supabase-connection-manager.js
2. supabase-realtime-manager.js
3. **realtime-subscriptions-init.js** ← Must load before user_auth
4. user_auth.js

### Issue: Subscriptions initialize but no events received
**Solution:** Check Supabase Realtime is enabled:
1. Go to: https://supabase.com/dashboard
2. Select your project → Database → Replication
3. Enable real-time for tables: `saved_threads`, `user_command_center`, `milestones`, etc.

### Issue: "User ID not found - skipping subscriptions"
**Solution:** User not logged in. Subscriptions only initialize after successful login.

## 📝 API Reference

### `RealtimeSubscriptionsInit.initialize()`
Initialize all real-time subscriptions (called automatically by `user_auth.js`).

**Returns:** `Promise<boolean>` - `true` if successful, `false` if dependencies missing

**Example:**
```javascript
const success = await RealtimeSubscriptionsInit.initialize();
if (success) {
    console.log('All subscriptions active!');
}
```

### `RealtimeSubscriptionsInit.getActiveSubscriptions()`
Get list of currently active subscription names.

**Returns:** `Array<string>` - Subscription names

**Example:**
```javascript
const subs = RealtimeSubscriptionsInit.getActiveSubscriptions();
console.log('Active:', subs);
// Output: ['heartbeat', 'workspace', 'threads', 'synergy-milestones', ...]
```

### `RealtimeSubscriptionsInit.unsubscribeAll()`
Unsubscribe from all subscriptions (called automatically on logout).

**Example:**
```javascript
// Called when user logs out
RealtimeSubscriptionsInit.unsubscribeAll();
console.log('All subscriptions cleared');
```

## 🔗 Related Files

- `UI/shared/js/supabase-realtime-manager.js` - Low-level real-time manager
- `UI/shared/js/realtime-subscriptions-init.js` - **NEW** - High-level subscription orchestrator
- `UI/modules_internal/components/user_auth.js` - Calls initialization after login
- `UI/shared/js/workspace-manager.js` - Uses workspace subscription for cross-tab sync

## 📚 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      User Logs In                           │
│                  (user_auth.js line 507)                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│        RealtimeSubscriptionsInit.initialize()               │
│          (realtime-subscriptions-init.js)                   │
└─┬─┬─┬─┬─┬─┬────────────────────────────────────────────────┘
  │ │ │ │ │ │
  │ │ │ │ │ └──► Subscribe to Sessions
  │ │ │ │ └────► Subscribe to Credentials
  │ │ │ └──────► Subscribe to Synergy (4 tables)
  │ │ └────────► Subscribe to Threads
  │ └──────────► Subscribe to Workspace
  └────────────► Subscribe to Heartbeat
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│           SupabaseRealtimeManager                           │
│         (supabase-realtime-manager.js)                      │
│  - Manages WebSocket connections                            │
│  - Handles reconnection logic                               │
│  - Dispatches events to subscribers                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼ (Database changes detected)
┌─────────────────────────────────────────────────────────────┐
│              Module Handlers (if implemented)               │
│  - ThreadManager.handleRealtimeUpdate()                     │
│  - SynergyManager.handleRealtimeUpdate()                    │
│  - AccountSidebar.handleRealtimeUpdate()                    │
│  → Update UI with new data                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## ✅ Summary

1. **Created:** `UI/shared/js/realtime-subscriptions-init.js` (centralized subscription manager)
2. **Updated:** `UI/modules_internal/components/user_auth.js` (calls initialization on login)
3. **Next:** Load the new script (see "Next Steps" section)
4. **Test:** Reload page, check console for subscription logs
5. **Verify:** Open 2 tabs, test cross-tab sync

**Expected Result:** After completing these steps, all 7 real-time subscriptions (heartbeat, workspace, threads, synergy×4, credentials, sessions) will be active and providing live updates across your application.

---

**Created:** December 14, 2025  
**Author:** AI Agent  
**Status:** Ready for integration testing
