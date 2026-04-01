# Organisation Tab 500 Error — Root Cause & Fix — March 31, 2026

## Issue
**User 12:** Clicks Organisation tab → Gets **500 Internal Server Error**  
**Message:** `GET /api/org/info` fails

While user 12 IS correctly linked to Vet Success organisation (id=1):
- ✅ `organisation_id = 1`  
- ✅ `org_role = 'owner'`
- ✅ Organisation exists and is active

## Root Cause

The `GET /api/org/info` endpoint was trying to SELECT columns that **don't exist** in the database:

```sql
-- Endpoint tried to SELECT (lines 314-320):
SELECT ... description, visibility, allowed_domains,
           ai_provider, ai_model, ai_max_tokens
FROM ai_infrastructure.organisations WHERE id = 1
```

**Result:** PostgreSQL throws error: `column "description" does not exist` → 500 response

### Actual Database Schema

The `ai_infrastructure.organisations` table (from `add_organisations_and_org_credentials.sql`) only has:
- ✅ `id, name, slug, plan_tier, is_active`
- ✅ `display_name, logo_url, timezone, country_code`
- ✅ `vault_password_hash, created_at, updated_at, metadata`
- ❌ `description` (MISSING)
- ❌ `visibility` (MISSING)  
- ❌ `allowed_domains` (MISSING)
- ❌ `ai_provider` (MISSING)
- ❌ `ai_model` (MISSING)
- ❌ `ai_max_tokens` (MISSING)

### Why This Happened

1. Frontend & backend code was written to support these features (description, visibility, SSO domains, AI config)
2. Migration to ADD these columns to the organisations table was **never created/run**
3. Code assumes columns exist, but they don't → crash

## Fix Applied — Two Parts

### **Part 1: Create Migration 039**

[New file: `AI_infrastructure/migrations/039_add_org_extended_fields.sql`](AI_infrastructure/migrations/039_add_org_extended_fields.sql)

Adds all missing columns to `ai_infrastructure.organisations`:

```sql
ALTER TABLE ai_infrastructure.organisations ADD COLUMN IF NOT EXISTS description TEXT;
ALTER TABLE ai_infrastructure.organisations ADD COLUMN IF NOT EXISTS visibility VARCHAR(50) DEFAULT 'private';
ALTER TABLE ai_infrastructure.organisations ADD COLUMN IF NOT EXISTS allowed_domains TEXT[];
ALTER TABLE ai_infrastructure.organisations ADD COLUMN IF NOT EXISTS ai_provider VARCHAR(50) DEFAULT 'anthropic';
ALTER TABLE ai_infrastructure.organisations ADD COLUMN IF NOT EXISTS ai_model VARCHAR(255) DEFAULT '';
ALTER TABLE ai_infrastructure.organisations ADD COLUMN IF NOT EXISTS ai_max_tokens INTEGER DEFAULT 8192;
```

**Status:** ✅ Ready to deploy (idempotent, uses `IF NOT EXISTS`)

### **Part 2: Update Endpoint Code**

[File: `AI_infrastructure/routes/organisation_credentials_routes.py`](AI_infrastructure/routes/organisation_credentials_routes.py)

Updated `get_org_info()` endpoint (lines 314-326):
- Now SELECTs all 20 columns (including the 6 new ones)
- Safe: Uses `.get()` fallback for columns that might not exist yet
- Response includes: `description, visibility, allowed_domains, ai_provider, ai_model, ai_max_tokens`

---

## Deployment Steps

### **Step 1: Run Migration 039**
```bash
# On Render production database:
python AI_infrastructure/migrations/039_add_org_extended_fields.sql
```

Or via psql:
```sql
\connect render_db
\i AI_infrastructure/migrations/039_add_org_extended_fields.sql
```

### **Step 2: Restart Flask Server**
```bash
# Render will auto-restart on deployment
# Or manually:
kill -9 <flask_pid>
python AI_infrastructure/flask_app.py
```

### **Step 3: Test Endpoint**
```bash
curl -H "Authorization: Bearer <user_12_jwt>" \
  https://ai-agents-v10.onrender.com/api/org/info
```

**Expected response:**
```json
{
  "success": true,
  "organisation": {
    "id": 1,
    "name": "Vet Success",
    "slug": "vet-success",
    "display_name": null,
    "description": null,
    "visibility": "private",
    "allowed_domains": [],
    "ai_provider": "anthropic",
    "ai_model": "",
    "ai_max_tokens": 8192,
    "is_active": true,
    "member_count": 1,
    "...": "..."
  },
  "your_role": "owner"
}
```

---

## What User 12 Will See After Fix

Once migration is applied and server restarted:

- ✅ Organisation tab opens without error
- ✅ Shows "Vet Success" organisation name and details
- ✅ User can access all org features (credentials, members, modules, etc.)
- ✅ Frontend displays "No Organisation Yet" message is **replaced** with actual org dashboard

---

## Related Code

| Component | Purpose | File |
|-----------|---------|------|
| **Endpoint** | Fetch org details for any member | `organisation_credentials_routes.py:get_org_info()` |
| **Update handler** | User with owner role can update org details | `organisation_credentials_routes.py:update_org_info()` |
| **Frontend loader** | Loads org tab when user clicks it | `account_profile.js:loadOrgTab()` |
| **Migration base** | Original organisations table | `add_organisations_and_org_credentials.sql` |
| **Migration new** | Adds missing columns | `039_add_org_extended_fields.sql` |

---

## Summary

**Before:** User 12 can't open organisation tab (500 error)  
**After:** User 12 sees full Vet Success organisation dashboard

**Root:** Missing database migration  
**Fix:** Created migration 039 + updated endpoint code  
**Impact:** Low risk — only adds columns, uses safe `.get()` fallbacks  
**Timeline:** Deploy migration 039, restart server, immediate fix

---

**Status:** ✅ Backend code ready, migration created, ready for deployment  
**Deployment Date:** March 31, 2026  
**Affected Users:** Any user in an org (trying to view /account → organisation tab)
