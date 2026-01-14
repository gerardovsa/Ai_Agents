# Database Constraint Fix - prime-loaded Location (Nov 24, 2025)

## 🚨 **Critical Issue Found**

**ERROR:**
```
new row for relation "threads" violates check constraint "chk_location_valid"
DETAIL: Failing row contains (..., prime-loaded, ...)
```

**Root Cause:** The Supabase database CHECK constraint **does not include `prime-loaded`** as a valid location!

---

## 📊 **What's Wrong**

### Current Database Constraint:
```sql
CHECK (
    location IN ('prime', 'stock_ai', 'data_agent', 'single_viewer')
    OR location ~ '^agent-([1-9]|1[0-9]|2[0-6])$'
)
```
❌ **Missing `prime-loaded`**

### Schema File (Correct):
```sql
CHECK (
    location IN ('prime', 'prime-loaded', 'stock_ai', 'data_agent', 'single_viewer')
    OR location ~ '^agent-([1-9]|1[0-9]|2[0-6])$'
)
```
✅ **Has `prime-loaded`**

### The Problem:
- Schema file was updated ✅
- Migration file exists ✅
- **Migration was NEVER RUN** ❌
- Database constraint still rejects `prime-loaded`

---

## ✅ **Fix Available - 2 Options**

### **Option 1: Quick Fix via Supabase Dashboard** (RECOMMENDED)

**Steps:**
1. Go to: https://supabase.com/dashboard
2. Select your project
3. Click **SQL Editor** (left sidebar)
4. Click **New Query**
5. Copy entire contents of `FIX_PRIME_LOADED_CONSTRAINT.sql`
6. Paste into SQL Editor
7. Click **RUN** (or Ctrl+Enter)
8. Verify success message

**Time:** 2 minutes ⏱️

---

### **Option 2: PowerShell Script** (If psql CLI installed)

**Steps:**
1. Open PowerShell in project root
2. Run:
   ```powershell
   .\APPLY_PRIME_LOADED_FIX.ps1
   ```
3. Follow prompts

**Requirements:**
- PostgreSQL CLI (psql) installed
- Supabase connection credentials

---

## 📝 **What The Fix Does**

### Step 1: Find & Drop Existing Constraint
```sql
-- Searches for all CHECK constraints containing 'location'
-- Drops them dynamically (handles name variations)
```

### Step 2: Add Corrected Constraint
```sql
ALTER TABLE sessions.threads
ADD CONSTRAINT chk_location_valid
CHECK (
    location IN ('prime', 'prime-loaded', ...)  -- ✅ prime-loaded added
    OR location ~ '^agent-...'
);
```

### Step 3: Create Performance Indexes
```sql
CREATE INDEX idx_threads_location ON sessions.threads(location);
CREATE INDEX idx_threads_prime_loaded ON sessions.threads(location) 
WHERE location = 'prime-loaded';
```

### Step 4: Verify Success
```sql
-- Shows the new constraint definition
SELECT conname, pg_get_constraintdef(oid) 
FROM pg_constraint WHERE conname = 'chk_location_valid';
```

---

## 🧪 **Testing After Fix**

### Test 1: Drag Thread to Prime
```
1. Open Thread History menu
2. Drag any thread to Prime drop zone
3. Should see: ✅ "Thread loaded in Prime"
4. Console: ✅ "Thread assigned to prime-loaded: [id]"
```

### Test 2: Database Update
```sql
-- This should now succeed without error:
UPDATE sessions.threads 
SET location = 'prime-loaded' 
WHERE thread_slug = '1763856372531';
```

### Test 3: Page Reload
```
1. Refresh browser (Ctrl+F5)
2. Prime-loaded thread should auto-load
3. Thread info card should display
```

---

## 📂 **Files Created**

1. **`FIX_PRIME_LOADED_CONSTRAINT.sql`**
   - Complete SQL migration
   - Safe to run multiple times (uses IF EXISTS)
   - Includes verification query

2. **`APPLY_PRIME_LOADED_FIX.ps1`**
   - PowerShell helper script
   - Auto-detects psql CLI
   - Provides manual instructions if needed

---

## 🎯 **Expected Results**

**Before Fix:**
```
❌ DROP thread on Prime → 500 Error
❌ Console: "violates check constraint chk_location_valid"
❌ Thread doesn't load
```

**After Fix:**
```
✅ DROP thread on Prime → Success
✅ Console: "Thread assigned to prime-loaded: [id]"
✅ Thread loads with messages
✅ Thread info card displays
✅ Page reload auto-loads thread
```

---

## ⚡ **Quick Start**

**Fastest way to fix:**
```powershell
# 1. Copy SQL file contents
cat FIX_PRIME_LOADED_CONSTRAINT.sql | clip

# 2. Open Supabase SQL Editor
start https://supabase.com/dashboard

# 3. Paste and run (Ctrl+V, then Ctrl+Enter)

# 4. Refresh browser
# Done! ✅
```

---

## 🔍 **Verification Checklist**

After running the fix:
- [ ] SQL execution shows "Dropped constraint: ..." message
- [ ] SQL execution shows constraint added successfully
- [ ] Verification query returns constraint with 'prime-loaded'
- [ ] Browser refresh (Ctrl+F5) clears cache
- [ ] Drag thread to Prime works without 500 error
- [ ] Console shows "Thread assigned to prime-loaded"
- [ ] Thread loads in Prime chat area
- [ ] Thread info card displays correctly

---

## 💡 **Why This Happened**

1. **Schema updated** → `data/sessions_schema.sql` has `prime-loaded` ✅
2. **Migration created** → `migrations/add_prime_loaded_location.sql` exists ✅
3. **Migration NEVER RUN** → Database still has old constraint ❌

**Lesson:** Always verify migrations are applied to production database!

---

## 🚀 **Next Steps**

1. **Run the SQL fix** (2 minutes)
2. **Refresh browser** (Ctrl+F5)
3. **Test thread drop** (should work now)
4. **Verify page reload** (thread auto-loads)

---

**Status:** 🔧 **FIX READY TO APPLY**  
**Impact:** 🔴 **CRITICAL** (Blocks core feature)  
**Difficulty:** 🟢 **EASY** (2-minute SQL execution)  
**Risk:** 🟢 **LOW** (Safe migration, idempotent)
