# Prompt Library Timeout Fix

**Date:** November 19, 2025  
**Issue:** Statement timeout during prompt_library table initialization  
**Status:** ✅ FIXED

## Problem

During Flask startup, the `init_prompt_library` function was experiencing timeout errors:

```
ERROR:init_prompt_library:❌ Failed to initialize prompt_library table: canceling statement due to statement timeout
CONTEXT:  while inserting index tuple (20,18) in relation "pg_class_relname_nsp_index"

INFO:flask_app: [SUCCESS] Prompt library table initialized in Supabase
```

The operation eventually succeeded, but the timeout error was confusing and indicated a race condition.

## Root Cause

1. **Default timeout too short**: Connection pool sets `statement_timeout = '60s'` for all connections
2. **DDL operations slow**: CREATE TABLE + 4 indexes in single transaction can exceed 60s on slow connections
3. **Lock contention**: System catalog locks (pg_class_relname_nsp_index) during index creation
4. **No graceful handling**: Code didn't handle partial success (table created, indexes timeout)

## Solution

### 1. Extended Timeout (init_prompt_library.py)

```python
# Set longer timeout for DDL operations (120 seconds)
with conn.cursor() as cursor:
    cursor.execute("SET statement_timeout = '120s'")
conn.commit()
```

### 2. Separated Operations

**Before:** Single transaction for table + 4 indexes  
**After:** Separate transactions:
- Transaction 1: CREATE TABLE
- Transaction 2: Index 1
- Transaction 3: Index 2
- Transaction 4: Index 3
- Transaction 5: Index 4

This prevents lock contention and allows partial success.

### 3. Graceful Error Handling

```python
try:
    cursor.execute(create_table_sql)
    conn.commit()
    logger.info("✅ Table created")
except Exception as table_error:
    # Verify table exists anyway
    cursor.execute("SELECT 1 FROM prompt_library LIMIT 1")
    logger.info("✅ Table exists despite creation warning")
```

### 4. Non-Critical Index Creation

```python
for idx_name, column in indexes:
    try:
        cursor.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON prompt_library({column})")
        conn.commit()
    except Exception as idx_error:
        # Non-critical: indexes are performance optimization
        logger.warning(f"⚠️ Index {idx_name} creation warning (non-critical)")
```

## Files Modified

### 1. AI_infrastructure/init_prompt_library.py
- Added `SET statement_timeout = '120s'`
- Split operations into separate transactions
- Added graceful error handling
- Made index creation non-critical

### 2. migrations/create_prompt_library_table.sql (NEW)
- Manual migration SQL for troubleshooting
- Can be run directly in Supabase SQL editor
- Sets 120s timeout explicitly

### 3. test_prompt_library_init.py (NEW)
- Comprehensive test suite
- Verifies table structure
- Tests indexes
- Validates insert/select operations

## Testing

Run the test script:

```powershell
cd C:\Users\gpoli\GIT\AI_agents
python test_prompt_library_init.py
```

Expected output:
```
✅ Table initialization reported success
✅ Table exists: prompt_library
✅ Table has 13 columns
✅ Found 5 indexes (primary + 4 custom)
✅ Insert/select operations working
✅ ALL TESTS PASSED
```

## Manual Migration (If Needed)

If automatic initialization still fails, run the SQL migration manually:

1. Open Supabase SQL Editor
2. Copy contents of `migrations/create_prompt_library_table.sql`
3. Execute the SQL
4. Restart Flask app

## Performance Impact

**Before:**
- 60s timeout → frequent timeouts on slow connections
- Single transaction → all-or-nothing (blocks if any index fails)
- No error recovery → confusing error messages

**After:**
- 120s timeout → sufficient for DDL operations
- Separate transactions → partial success allowed
- Graceful recovery → table works even if indexes timeout
- Better logging → clear status of each operation

## Timeout Hierarchy

1. **Pool creation:** `connect_timeout=30s` (connection establishment)
2. **Default queries:** `statement_timeout=60s` (set by pool)
3. **DDL operations:** `statement_timeout=120s` (overridden in init_prompt_library)

## Monitoring

Check Flask startup logs for:

```
✅ prompt_library table structure verified
⚠️ Index idx_X creation warning (non-critical)  # Optional warnings
✅ prompt_library table initialized (N existing prompts)
```

## Rollback (If Needed)

To revert to old behavior:

```python
# In init_prompt_library.py, change:
cursor.execute("SET statement_timeout = '120s'")
# Back to:
# (use default 60s timeout)
```

## Related Issues

- Similar timeout issues may occur in other DDL operations
- Consider applying same pattern to other table initialization functions
- Connection pool statement_timeout can be increased globally if needed (line 263 of database_utils.py)

## References

- PostgreSQL statement_timeout: https://www.postgresql.org/docs/current/runtime-config-client.html
- Supabase performance: https://supabase.com/docs/guides/platform/performance
- psycopg2 connection pooling: https://www.psycopg.org/docs/pool.html

---

**Last Updated:** November 19, 2025  
**Status:** Production Ready  
**Impact:** High (fixes startup errors)
