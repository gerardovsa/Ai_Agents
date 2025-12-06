# 🔧 Database Cursor Management - Quick Reference

## ✅ CORRECT Patterns

### Pattern 1: Default cursor() [RECOMMENDED]
```python
with get_database_connection('sessions') as conn:
    cursor = conn.cursor()  # ← NO ARGS - Returns DatabaseCursor
    cursor.execute("SELECT * FROM table")
    rows = cursor.fetchall()
# ✅ Connection + Cursor both auto-closed
```

**Why this works**:
- `conn.cursor()` without args → Returns `DatabaseCursor` wrapper
- `DatabaseCursor` inherits from psycopg2 cursor
- Returns dict-like rows (same as `RealDictCursor`)
- Auto-closes when out of scope
- **NO manual `cursor.close()` needed**

---

### Pattern 2: Explicit cursor close [IF NEEDED]
```python
with get_database_connection('sessions') as conn:
    cursor = conn.cursor(cursor_factory=CustomCursor)
    try:
        cursor.execute("SELECT * FROM table")
        rows = cursor.fetchall()
    finally:
        cursor.close()  # ← REQUIRED
# ✅ Connection + Cursor both closed
```

**When to use**:
- You need a custom cursor class
- You need specific cursor behavior
- **ALWAYS close manually with try/finally**

---

## ❌ INCORRECT Patterns

### Anti-Pattern 1: cursor_factory without close
```python
# ❌ LEAKS CURSOR
with get_database_connection('sessions') as conn:
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM table")
    rows = cursor.fetchall()
# Connection closed, CURSOR LEAKED
```

**Why this fails**:
- `cursor_factory=X` bypasses `DatabaseCursor` wrapper
- Returns raw psycopg2 cursor
- Raw cursor does NOT auto-close
- Cursor holds server-side resources
- Connection appears "free" but is actually busy

---

### Anti-Pattern 2: Conditional close
```python
# ❌ MAY LEAK CURSOR
with get_database_connection('sessions') as conn:
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM table")
    if some_condition:
        cursor.close()  # ← May not execute
```

**Why this fails**:
- If condition is False, cursor leaks
- Use try/finally instead (Pattern 2)

---

## 📊 Architecture Reference

```
Connection Pool Hierarchy:
┌────────────────────────────────────────────────┐
│ SimpleConnectionPool (2-5 per schema)          │
│   psycopg2.Connection (raw)                    │
│     ↓                                           │
│   PooledConnection (pool management)           │
│     ↓                                           │
│   DatabaseConnection (SQL conversion)          │
│     ↓                                           │
│     .cursor() method:                          │
│     ├─ NO ARGS    → DatabaseCursor (managed)   │
│     └─ WITH ARGS  → psycopg2.cursor (raw)      │
└────────────────────────────────────────────────┘
```

---

## 🔍 How to Check for Leaks

### Search codebase for unsafe patterns:
```bash
# Find all cursor_factory usage
grep -r "cursor_factory" AI_infrastructure/

# Find all conn.cursor() calls
grep -r "conn.cursor(" AI_infrastructure/
```

### Monitor pool stats:
```python
from shared.database_utils import get_pool_stats

stats = get_pool_stats()
print(f"Acquired: {stats['connections_acquired']}")
print(f"Returned: {stats['connections_returned']}")
leaked = stats['connections_acquired'] - stats['connections_returned']
print(f"LEAKED: {leaked}")  # Should be 0
```

### Check PostgreSQL connections:
```sql
SELECT 
    datname,
    count(*) as connections,
    max(backend_start) as oldest_connection
FROM pg_stat_activity
WHERE datname = 'postgres'
GROUP BY datname;
```

**Expected**:
- Connections: 2-5 (stable)
- Oldest connection: Should be recent (< 1 hour)

**Warning signs**:
- Connections: 40-60 (growing)
- Oldest connection: Hours/days old
- → You have a leak!

---

## 🚨 Symptoms of Cursor Leaks

1. **Pool exhaustion errors**:
   ```
   ConnectionError: Connection pool exhausted for 'sessions'
   Leaked connections: 2+
   ```

2. **Slow response times**:
   - First 20 requests: Fast
   - Next 20 requests: Slow
   - After 40+: Timeouts

3. **PostgreSQL connection growth**:
   ```sql
   -- Check connection count over time
   SELECT count(*) FROM pg_stat_activity;
   -- Grows steadily instead of staying stable
   ```

4. **Server-side cursor errors**:
   ```
   ERROR: cursor "cursor_name" does not exist
   ERROR: too many cursors open
   ```

---

## ✅ Fix Checklist

When fixing cursor leaks:

- [ ] Find all `conn.cursor(cursor_factory=X)` calls
- [ ] Replace with `conn.cursor()` (no args)
- [ ] OR add explicit `cursor.close()` in try/finally
- [ ] Remove unused `RealDictCursor` imports
- [ ] Test that queries return dict-like rows
- [ ] Monitor pool stats (leaked should be 0)
- [ ] Document changes

---

## 📚 Related Files

- `CURSOR_LEAK_FIX_DEC6_2025.md` - Full analysis and fix
- `CONNECTION_POOL_LEAK_FIX_NOV25.md` - Connection pool architecture
- `shared/database_utils.py` - Pool implementation
- Lines 620-720: `DatabaseCursor` and `DatabaseConnection` classes

---

**Last Updated**: December 6, 2025  
**Status**: ✅ All leaks fixed, pattern documented
