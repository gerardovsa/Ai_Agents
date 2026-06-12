# Workspace Manager Schema Fix - December 14, 2025

## 🐛 **The Problem**

**Error in Console:**
```
POST https://ryoicrdifiqhqpsnjmdo.supabase.co/rest/v1/user_command_center?on_conflict=user_id 406 (Not Acceptable)
❌ [WorkspaceManager] Database sync failed: {code: 'PGRST106', message: 'The schema must be one of the following: public, graphql_public'}
```

**Root Cause:** 
The `workspace-manager.js` was using `.schema('sessions')` to access the `sessions.user_command_center` table, but Supabase's PostgREST API only allows access to `public` and `graphql_public` schemas via the REST API.

---

## ✅ **The Fix**

### **Changes Made**

1. **Modified:** `UI/shared/js/workspace-manager.js`
   - Replaced `.schema('sessions').from('user_command_center')` with RPC calls
   - Changed `syncToDatabase()` to use `supabase.rpc('upsert_workspace_settings', {...})`
   - Changed `loadFromDatabase()` to use `supabase.rpc('get_workspace_settings', {...})`

2. **Created:** `AI_infrastructure/database/migrations/workspace_rpc_functions.sql`
   - `public.get_workspace_settings(p_user_id)` - Fetch workspace data
   - `public.upsert_workspace_settings(p_user_id, p_workspace_data)` - Save workspace data
   - Both functions use `SECURITY DEFINER` to access `sessions` schema

---

## 📋 **How to Apply**

### **Step 1: Run the SQL Migration**

Connect to your Supabase database and run:

```bash
cd AI_infrastructure/database/migrations
psql -h ryoicrdifiqhqpsnjmdo.supabase.co -U postgres -d postgres -f workspace_rpc_functions.sql
```

Or via Supabase Dashboard:
1. Go to SQL Editor
2. Copy contents of `workspace_rpc_functions.sql`
3. Run the query

### **Step 2: Verify Functions Created**

```sql
-- Check functions exist
SELECT proname, proargtypes 
FROM pg_proc 
WHERE proname IN ('get_workspace_settings', 'upsert_workspace_settings');

-- Test get function (should return NULL if no data)
SELECT public.get_workspace_settings(14);

-- Test upsert function
SELECT public.upsert_workspace_settings(
    14,
    '{"agents": {}, "prime": {}, "columnOrder": []}'::jsonb
);

-- Verify data saved
SELECT * FROM sessions.user_command_center WHERE user_id = 14;
```

### **Step 3: Reload Your App**

Hard refresh (Ctrl+Shift+R) to load the updated `workspace-manager.js`

---

## 🧪 **Testing**

After applying the fix, test these scenarios:

1. **Toggle agent column width** (should sync to database without errors)
2. **Check console** (should see `✅ [WorkspaceManager] Synced to database successfully`)
3. **Reload page** (should restore workspace settings from database)
4. **Open in new tab** (should load same workspace layout)

---

## 📊 **Before vs After**

### **Before (Broken)**
```javascript
const { data, error } = await supabase
    .schema('sessions')  // ❌ Not allowed by PostgREST
    .from('user_command_center')
    .upsert({...});
```

**Result:** `406 Not Acceptable - schema must be public or graphql_public`

### **After (Fixed)**
```javascript
const { data, error } = await supabase
    .rpc('upsert_workspace_settings', {  // ✅ RPC bypasses schema restriction
        p_user_id: userId,
        p_workspace_data: workspace
    });
```

**Result:** ✅ Data saved successfully to `sessions.user_command_center`

---

## 🔍 **Why This Works**

1. **RPC functions run on the database server** (not through PostgREST)
2. **SECURITY DEFINER** allows the function to access `sessions` schema even though the API user can't
3. **Public schema is accessible** via PostgREST, so RPC calls work
4. **Functions act as a bridge** between the public API and the sessions schema

---

## 🎯 **Related Files**

- `UI/shared/js/workspace-manager.js` - Frontend workspace management
- `AI_infrastructure/database/migrations/workspace_rpc_functions.sql` - Database functions
- `sessions.user_command_center` table - Workspace storage

---

## 💡 **Alternative Solutions (Not Used)**

1. **Add sessions to API schemas** - Requires Supabase config change (less secure)
2. **Create view in public schema** - Would expose sessions data (security risk)
3. **Move table to public schema** - Would break other code expecting sessions schema

**Why RPC is Best:** Secure, isolated, no config changes needed, works with existing table structure.

---

**Status:** ✅ **READY TO DEPLOY**
**Apply SQL migration and hard refresh browser to fix workspace sync errors.**
