# 🗄️ Database Tables - Usage Analysis

**Date:** November 10, 2025  
**Total Databases:** 5  
**Total Tables:** 62  
**Unused Tables Found:** 19  

---

## ⚠️ CRITICAL ISSUE: sessions.db is CORRUPTED

```
sessions.db: ERROR - database disk image is malformed
```

**This is a serious problem!** The sessions database needs to be restored from backup or migrated to Supabase immediately.

---

## 📊 Summary by Database

| Database | Total Tables | Empty Tables | Unused Tables | Status |
|----------|--------------|--------------|---------------|--------|
| `ai_infrastructure.db` | 12 | 6 | 4 | ⚠️ Cleanup needed |
| `sessions.db` | ? | ? | ? | 🔴 **CORRUPTED** |
| `synergy_sessions.db` | 1 | 0 | 0 | ✅ Good |
| `kanban_analytics.db` | 14 | 4 | 4 | ⚠️ Cleanup needed |
| `stock_data.db` | 35 | 10 | 11 | ⚠️ Cleanup needed |

---

## 🔴 UNUSED TABLES (Safe to Delete)

### ai_infrastructure.db - 4 unused tables

#### 1. `account_link_requests` (0 rows)
- **Status:** UNUSED - No code references
- **Purpose:** Appears to be for account linking requests
- **Recommendation:** ✅ **DELETE** (0 rows, no code uses it)
- **Related:** May have been replaced by OAuth flow

#### 2. `thread_assignments` (0 rows)
- **Status:** UNUSED - Table exists but data stored in JSON instead
- **Purpose:** Originally for assigning threads to agents
- **Code Reference:** `thread_assignment_routes.py` uses `metadata['thread_assignments']` JSON instead
- **Recommendation:** ✅ **DELETE** (redundant, JSON approach used instead)

#### 3. `user_gmail_accounts` (0 rows)
- **Status:** DEPRECATED - Migrated to oauth_tokens
- **Purpose:** Stored Gmail addresses
- **Migration:** See `migrate_oauth_final_consolidation.py` line 78-90
- **Recommendation:** ✅ **DELETE** (data migrated to oauth_tokens table)

#### 4. `user_platform_credentials` (0 rows)
- **Status:** DEPRECATED - Replaced by oauth_tokens
- **Purpose:** Key-value OAuth storage
- **References:** Only in migration script (`migrate_oauth_final_consolidation.py`)
- **Recommendation:** ✅ **DELETE** (redundant, oauth_tokens is the source of truth)

---

### kanban_analytics.db - 4 unused tables

#### 5. `ai_predictions` (0 rows)
- **Status:** UNUSED - Feature not implemented
- **Purpose:** Store AI predictions for job completion
- **Code Reference:** Queried in `kanban_analytics_routes.py` line 252 but never populated
- **Recommendation:** ⚠️ **KEEP IF PLANNED**, otherwise DELETE

#### 6. `custom_job_notes` (0 rows)
- **Status:** UNUSED - Feature exists but no data
- **Purpose:** Store custom notes on job tickets
- **Code Reference:** Has INSERT/UPDATE/SELECT queries in `kanban_analytics_routes.py`
- **Recommendation:** ✅ **KEEP** (actively coded, just not used yet)

#### 7. `job_performance` (0 rows)
- **Status:** UNUSED - Feature not implemented
- **Purpose:** Track job performance metrics
- **Code Reference:** Queried in `kanban_analytics_routes.py` line 157, 467
- **Recommendation:** ⚠️ **KEEP IF PLANNED**, otherwise DELETE

#### 8. `job_tags` (0 rows)
- **Status:** UNUSED - Feature exists but no data
- **Purpose:** Tag jobs with custom tags
- **Code Reference:** Has INSERT/DELETE queries in `kanban_analytics_routes.py`
- **Recommendation:** ✅ **KEEP** (actively coded, just not used yet)

---

### stock_data.db - 11 unused tables

#### 9. `ClickCostHistory` (0 rows)
- **Status:** UNUSED
- **Purpose:** Historical click cost data
- **Recommendation:** ❓ Check if needed for analytics, otherwise DELETE

#### 10. `ConsumableTransactions` (0 rows)
- **Status:** UNUSED
- **Purpose:** Track consumable inventory transactions
- **Related:** `ConsumableInventory` has 7 rows
- **Recommendation:** ⚠️ **KEEP** (related table has data)

#### 11. `EventProcessingLog` (0 rows)
- **Status:** UNUSED
- **Purpose:** Log event processing
- **Recommendation:** ✅ **DELETE** (no events logged)

#### 12. `JobTickets` (0 rows) ⚠️ **SUSPICIOUS**
- **Status:** SUSPICIOUS - Referenced in code but 0 rows in stock_data.db
- **Code References:** 
  - `flask_app.py` lines 819, 835, 903, 916
  - `kanban_db_sync.py` line 380, 530
- **Issue:** Code queries this table but it's empty
- **Likely Cause:** JobTickets might be in kanban_analytics.db instead (119 rows there)
- **Recommendation:** ⚠️ **INVESTIGATE** - May have duplicate tables across databases

#### 13. `PurchaseOrderItems` (0 rows)
- **Status:** UNUSED
- **Purpose:** Purchase order line items
- **Related:** `PurchaseOrders` also empty
- **Recommendation:** ⚠️ **KEEP IF PLANNED**, otherwise DELETE

#### 14. `PurchaseOrders` (0 rows)
- **Status:** UNUSED
- **Purpose:** Track purchase orders
- **Recommendation:** ⚠️ **KEEP IF PLANNED**, otherwise DELETE

#### 15. `QuoteMaterialRequirements` (0 rows)
- **Status:** UNUSED
- **Purpose:** Material requirements for quotes
- **Recommendation:** ⚠️ **KEEP IF PLANNED**, otherwise DELETE

#### 16. `ReorderAlerts` (0 rows)
- **Status:** UNUSED
- **Purpose:** Alert when stock needs reordering
- **Recommendation:** ⚠️ **KEEP IF PLANNED** (inventory feature)

#### 17. `custom_events` (0 rows)
- **Status:** UNUSED
- **Purpose:** Custom event tracking
- **Recommendation:** ✅ **DELETE** (no events)

#### 18. `shopify_analytics_cache` (0 rows)
- **Status:** UNUSED
- **Purpose:** Cache Shopify analytics
- **Related:** Other Shopify tables have data
- **Recommendation:** ⚠️ **KEEP** (cache tables start empty)

#### 19. `shopify_price_parity` (0 rows)
- **Status:** UNUSED
- **Purpose:** Track price parity
- **Recommendation:** ❓ Check if needed, otherwise DELETE

#### 20. `shopify_product_mapping` (0 rows)
- **Status:** UNUSED
- **Purpose:** Map Shopify products to internal
- **Recommendation:** ⚠️ **KEEP IF PLANNED**, otherwise DELETE

#### 21. `shopify_stock_usage` (0 rows)
- **Status:** UNUSED
- **Purpose:** Track stock usage from Shopify
- **Recommendation:** ⚠️ **KEEP IF PLANNED**, otherwise DELETE

#### 22. `shopify_webhook_events` (0 rows)
- **Status:** UNUSED
- **Purpose:** Log webhook events
- **Related:** Other Shopify tables populated
- **Recommendation:** ⚠️ **KEEP** (webhooks may start firing)

---

## ✅ SAFE TO DELETE NOW (4 tables)

These tables have **0 rows** and **no active code references**:

1. ✅ `ai_infrastructure.db` → `account_link_requests`
2. ✅ `ai_infrastructure.db` → `thread_assignments` (data in JSON instead)
3. ✅ `ai_infrastructure.db` → `user_gmail_accounts` (migrated to oauth_tokens)
4. ✅ `ai_infrastructure.db` → `user_platform_credentials` (replaced by oauth_tokens)

---

## ⚠️ INVESTIGATE FURTHER (3 tables)

These tables might be duplicates or misplaced:

1. ⚠️ `stock_data.db` → `JobTickets` (0 rows, but kanban_analytics.db has 119 rows)
2. ⚠️ `stock_data.db` → `ClickCostHistory` (check if needed)
3. ⚠️ `stock_data.db` → `custom_events` (check if needed)

---

## 🔧 KEEP BUT MONITOR (12 tables)

These tables are empty but have active code or may be needed:

**Features with code but no data yet:**
- `kanban_analytics.db` → `custom_job_notes` (has INSERT/UPDATE code)
- `kanban_analytics.db` → `job_tags` (has INSERT/DELETE code)
- `kanban_analytics.db` → `ai_predictions` (queried in code)
- `kanban_analytics.db` → `job_performance` (queried in code)

**Planned/Future features:**
- `stock_data.db` → `PurchaseOrders` + `PurchaseOrderItems`
- `stock_data.db` → `QuoteMaterialRequirements`
- `stock_data.db` → `ReorderAlerts`
- `stock_data.db` → `ConsumableTransactions`
- `stock_data.db` → `shopify_product_mapping`
- `stock_data.db` → `shopify_stock_usage`

**Cache/Event tables (start empty):**
- `stock_data.db` → `shopify_analytics_cache`
- `stock_data.db` → `shopify_webhook_events`

---

## 🚨 URGENT ACTIONS NEEDED

### 1. Fix Corrupted sessions.db (CRITICAL)

```powershell
# Option 1: Restore from Supabase (RECOMMENDED)
cd C:\Users\gpoli\GIT\AI_agents
python Supabase/supabase_toolkit.py export sessions.db

# Option 2: Try to recover
cd data
sqlite3 sessions.db ".recover" | sqlite3 sessions_recovered.db

# Option 3: Rebuild from scratch (if no critical data)
rm sessions.db
# Let Flask recreate it on next startup
```

### 2. Delete Unused Tables (ai_infrastructure.db)

```sql
-- Run in SQLite or create migration
DROP TABLE IF EXISTS account_link_requests;
DROP TABLE IF EXISTS thread_assignments;
DROP TABLE IF EXISTS user_gmail_accounts;
DROP TABLE IF EXISTS user_platform_credentials;
```

**Or via Python:**

```powershell
python -c "import sqlite3; conn = sqlite3.connect('data/ai_infrastructure.db'); conn.execute('DROP TABLE IF EXISTS account_link_requests'); conn.execute('DROP TABLE IF EXISTS thread_assignments'); conn.execute('DROP TABLE IF EXISTS user_gmail_accounts'); conn.execute('DROP TABLE IF EXISTS user_platform_credentials'); conn.commit(); print('Deleted 4 unused tables'); conn.close()"
```

### 3. Investigate JobTickets Duplicate

```powershell
# Check if JobTickets exists in multiple databases
python -c "import sqlite3; print('kanban_analytics:', sqlite3.connect('data/kanban_analytics.db').execute('SELECT COUNT(*) FROM job_tickets').fetchone()[0], 'rows'); print('stock_data:', sqlite3.connect('data/stock_data.db').execute('SELECT COUNT(*) FROM JobTickets').fetchone()[0], 'rows')"
```

---

## 📈 Storage Savings

**Current database sizes:**
- `ai_infrastructure.db`: 412 KB
- `sessions.db`: 332 KB (corrupted)
- `synergy_sessions.db`: 92 KB
- `kanban_analytics.db`: 640 KB
- `stock_data.db`: 8.8 MB

**Estimated savings from cleanup:**
- Removing 4 empty tables: ~40-80 KB
- Fixing sessions.db corruption: May reduce size significantly
- Overall impact: Minor (but improves clarity)

---

## 🎯 Recommendations

### Immediate (Today)

1. ✅ **Fix sessions.db corruption** (restore from Supabase)
2. ✅ **Delete 4 safe unused tables** from ai_infrastructure.db
3. ⚠️ **Investigate JobTickets duplicate** (stock_data vs kanban_analytics)

### Short-term (This Week)

4. ✅ **Create Supabase migration** for table deletions
5. ✅ **Document which tables are planned features** vs abandoned
6. ⚠️ **Review stock_data.db empty tables** (11 tables with 0 rows)

### Long-term (This Month)

7. ✅ **Consolidate databases** (consider merging into Supabase schemas)
8. ✅ **Add row count monitoring** (alert if tables stay empty for 30+ days)
9. ✅ **Database optimization** (VACUUM, reindex)

---

## 📝 Migration Script Template

For deleting the 4 safe unused tables:

```sql
-- ============================================================================
-- Migration Number: 004
-- Description: Remove deprecated OAuth tables (migrated to oauth_tokens)
-- Date: 2025-11-10
-- Author: Gerardo
-- Database: ai_infrastructure.db (local) + Supabase
-- ============================================================================

-- ============================================================================
-- UP MIGRATION (Apply changes)
-- ============================================================================

BEGIN;

-- These tables are unused and have been migrated/deprecated
DROP TABLE IF EXISTS account_link_requests;      -- 0 rows, no code references
DROP TABLE IF EXISTS thread_assignments;          -- 0 rows, using JSON instead
DROP TABLE IF EXISTS user_gmail_accounts;         -- Migrated to oauth_tokens
DROP TABLE IF EXISTS user_platform_credentials;   -- Replaced by oauth_tokens

COMMIT;

-- ============================================================================
-- DOWN MIGRATION (Rollback)
-- ============================================================================

BEGIN;

-- Recreate tables if needed (schemas from original)
CREATE TABLE IF NOT EXISTS account_link_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    platform TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS thread_assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_id TEXT NOT NULL,
    agent_id TEXT NOT NULL,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_gmail_accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    gmail_address TEXT NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_platform_credentials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    platform TEXT NOT NULL,
    credential_key TEXT NOT NULL,
    credential_value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMIT;
```

---

## ✅ Summary

**Total tables analyzed:** 62  
**Empty tables:** 20 (32%)  
**Safe to delete now:** 4  
**Need investigation:** 3  
**Keep but monitor:** 12  

**Biggest issue:** sessions.db corruption (needs immediate fix)  
**Quick win:** Delete 4 unused tables from ai_infrastructure.db  
**Long-term:** Migrate everything to Supabase and eliminate SQLite

---

**Next Steps:**
1. Fix sessions.db corruption
2. Run cleanup script for ai_infrastructure.db
3. Create Supabase migration for deletions
4. Document planned vs abandoned features

**Last Updated:** November 10, 2025  
**Status:** Analysis Complete - Action Required
