# Stock Management Module - Supabase Migration (Dec 4, 2025)

## Summary

Successfully migrated the Stock Management module from **SQLite** (`stock_data.db`) to **Supabase PostgreSQL** (`stock_data` schema).

---

## What Changed

### Database Connection

**BEFORE (SQLite):**
```python
import sqlite3
STOCK_DB_PATH = str(Path(__file__).parent.parent.parent.parent.parent / 'data' / 'stock_data.db')
conn = sqlite3.connect(STOCK_DB_PATH)
conn.row_factory = sqlite3.Row
```

**AFTER (Supabase PostgreSQL):**
```python
from shared.database_utils import get_database_connection
conn = get_database_connection('stock_data')  # Connects to Supabase PostgreSQL stock_data schema
```

---

## SQL Syntax Changes

### 1. Date Functions

**SQLite:**
```sql
WHERE date(e.order_date) >= date('now', '-30 days')
```

**PostgreSQL:**
```sql
WHERE e.order_date >= CURRENT_DATE - INTERVAL '30 days'
```

### 2. String Concatenation

**SQLite:**
```sql
(CAST(u.length_mm AS TEXT) || 'x' || CAST(u.width_mm AS TEXT) || 'mm') AS dimensions
```

**PostgreSQL:**
```sql
CONCAT(u.length_mm, 'x', u.width_mm, 'mm') AS dimensions
```

### 3. Rounding with Numeric Types

**SQLite:**
```sql
ROUND(SUM(...) * u.cost_per_thousand / 1000.0, 2) as total_cost
```

**PostgreSQL:**
```sql
ROUND(CAST(SUM(...) * u.cost_per_thousand / 1000.0 AS NUMERIC), 2) as total_cost
```

### 4. Schema-Qualified Table Names

**SQLite:**
```sql
FROM extracted_jobs e
INNER JOIN unified_stocks u ON e.stock_id = u.stock_id
```

**PostgreSQL:**
```sql
FROM stock_data.extracted_jobs e
INNER JOIN stock_data.unified_stocks u ON e.stock_id = u.stock_id
```

### 5. Column Aliases with Spaces

**SQLite:** Doesn't require quotes

**PostgreSQL:** Requires double quotes for mixed case
```sql
SELECT u.stock_id AS "StockID"  -- PostgreSQL requires quotes
```

### 6. Table Metadata Queries

**SQLite:**
```sql
SELECT name FROM sqlite_master WHERE type='table'
PRAGMA table_info(table_name)
```

**PostgreSQL:**
```sql
SELECT table_name FROM information_schema.tables WHERE table_schema = 'stock_data'
SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_schema = 'stock_data'
```

### 7. Parameterized Queries

**SQLite:**
```sql
cursor.execute("UPDATE table SET col = ? WHERE id = ?", (value, id))
```

**PostgreSQL:**
```sql
cursor.execute("UPDATE stock_data.table SET col = %s WHERE id = %s", (value, id))
```

### 8. Row to Dictionary Conversion

**SQLite:**
```python
conn.row_factory = sqlite3.Row
rows = cursor.fetchall()
data = [dict(row) for row in rows]  # sqlite3.Row is dict-like
```

**PostgreSQL:**
```python
rows = cursor.fetchall()
columns = [desc[0] for desc in cursor.description]
data = [dict(zip(columns, row)) for row in rows]  # Manual dict conversion
```

---

## Endpoints Updated

All 7 endpoints in `stock_routes.py` were migrated:

### ✅ 1. `/api/stock/usage-analytics`
- **Changed:** SQLite → Supabase connection
- **Changed:** `date('now', '-N days')` → `CURRENT_DATE - INTERVAL 'N days'`
- **Changed:** String concatenation to `CONCAT()`
- **Changed:** Table names to `stock_data.extracted_jobs`, `stock_data.unified_stocks`
- **Changed:** Row to dict conversion

### ✅ 2. `/api/stock/hierarchy`
- **Changed:** SQLite → Supabase connection
- **Changed:** Date functions
- **Changed:** String concatenation
- **Changed:** `ROUND()` with `CAST(...  AS NUMERIC)`
- **Changed:** Schema-qualified tables
- **Changed:** Row to dict conversion

### ✅ 3. `/api/stock/reorder-dashboard`
- **Changed:** SQLite → Supabase connection
- **Changed:** Date functions
- **Changed:** Schema-qualified tables

### ✅ 4. `/api/stock/profit-analysis`
- **Changed:** SQLite → Supabase connection
- **Changed:** Date functions
- **Changed:** String concatenation with `CONCAT()`
- **Changed:** Multiple `ROUND()` calls with `CAST(... AS NUMERIC)`
- **Changed:** Schema-qualified tables
- **Changed:** `HAVING total_sheets > 0` → `HAVING SUM(...) > 0` (PostgreSQL requires aggregate in HAVING)
- **Changed:** Row to dict conversion

### ✅ 5. `/api/stock/sql-query` (GET + POST)
- **GET Changed:** SQLite table metadata → PostgreSQL `information_schema` queries
- **GET Changed:** `PRAGMA table_info()` → `information_schema.columns`
- **POST Changed:** SQLite → Supabase connection
- **POST Changed:** Row to dict conversion

### ✅ 6. `/api/stock/update-cell` (POST)
- **Changed:** SQLite → Supabase connection
- **Changed:** `?` placeholders → `%s` (PostgreSQL syntax)
- **Changed:** Table names to `stock_data.table_name`

### ✅ 7. `/api/stock/ai-analytics`
- **No database changes needed** (returns placeholder data)

---

## Files Modified

### 1. `UI/modules_external/stock-management/stock_routes.py`
- **Lines changed:** ~150 lines
- **Changes:**
  - Removed `import sqlite3`
  - Removed `STOCK_DB_PATH` variable
  - Added `from shared.database_utils import get_database_connection`
  - Updated all `sqlite3.connect()` calls to `get_database_connection('stock_data')`
  - Converted all SQLite SQL to PostgreSQL syntax
  - Updated all row-to-dict conversions
  - Updated all table references to use `stock_data.` schema prefix

---

## Database Architecture

### ✅ Correct Setup (After Migration):

```
InHouse Fred Database (SQL Server):
├── Orders
├── JobTickets
├── PaperSize
├── BindType
└── Clients
    └── [Production order data]

Supabase PostgreSQL (stock_data schema):
├── stock_data.extracted_jobs       ← AI-extracted job data
├── stock_data.unified_stocks        ← Stock master data
├── stock_data.stocklevels           ← Inventory levels
├── stock_data.reorderalerts         ← Reorder alerts
├── stock_data.consumableinventory   ← Consumables
├── stock_data.corflutematerials     ← Corflute materials
├── stock_data.shopify_orders        ← Shopify integration
└── stock_data.shopify_products      ← Shopify products
```

### ❌ Old Setup (Before Migration):

```
SQLite (data/stock_data.db):
├── extracted_jobs
├── unified_stocks
└── [Local file, not cloud-accessible]
```

---

## Connection Configuration

The module now connects to Supabase using credentials from `.env.master`:

```bash
# Supabase PostgreSQL Connection
SUPABASE_DB_URL_POOLER=postgresql://postgres.ryoicrdifiqhqpsnjmdo:inhouseprint@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres
USE_SUPABASE=true
```

The `get_database_connection('stock_data')` function:
1. Reads `SUPABASE_DB_URL_POOLER` from environment
2. Connects to Supabase PostgreSQL
3. Sets search path to `stock_data` schema
4. Returns connection with auto-placeholder conversion (`?` → `%s`)

---

## Testing Required

### 1. **Usage Analytics Endpoint**
```bash
GET http://localhost:5001/api/stock/usage-analytics?days=30
```
**Expected:** Returns top 50 stocks with usage counts, dimensions, GSM

### 2. **Stock Hierarchy Endpoint**
```bash
GET http://localhost:5001/api/stock/hierarchy?days=90
```
**Expected:** Returns hierarchical stock data (category → type → stock)

### 3. **Reorder Dashboard**
```bash
GET http://localhost:5001/api/stock/reorder-dashboard
```
**Expected:** Returns stock alerts (critical, warning, healthy)

### 4. **Profit Analysis**
```bash
GET http://localhost:5001/api/stock/profit-analysis?days=90
```
**Expected:** Returns profitability analysis with cost/revenue/margin

### 5. **SQL Query Endpoint (GET)**
```bash
GET http://localhost:5001/api/stock/sql-query
```
**Expected:** Returns list of tables in `stock_data` schema with column info

### 6. **SQL Query Endpoint (POST)**
```bash
POST http://localhost:5001/api/stock/sql-query
Body: {"query": "SELECT * FROM stock_data.unified_stocks LIMIT 10"}
```
**Expected:** Returns query results with columns and execution time

### 7. **Update Cell Endpoint**
```bash
POST http://localhost:5001/api/stock/update-cell
Body: {
  "table": "unified_stocks",
  "column": "cost_per_thousand",
  "value": 150.00,
  "where_column": "stock_id",
  "where_value": "S001"
}
```
**Expected:** Updates cell and returns success message

---

## Potential Issues & Fixes

### Issue 1: Connection Timeout
**Symptom:** `psycopg2.OperationalError: timeout`

**Fix:** Check `.env.master` has correct `SUPABASE_DB_URL_POOLER`

### Issue 2: Schema Not Found
**Symptom:** `schema "stock_data" does not exist`

**Fix:** Verify migration script created `stock_data` schema in Supabase

### Issue 3: SQL Syntax Errors
**Symptom:** `syntax error at or near ...`

**Fix:** Check all SQL queries use PostgreSQL syntax (no SQLite syntax remains)

### Issue 4: Placeholder Errors
**Symptom:** `IndexError: tuple index out of range`

**Fix:** Verify all `?` placeholders changed to `%s`

### Issue 5: Column Case Sensitivity
**Symptom:** `column "stockid" does not exist`

**Fix:** PostgreSQL is case-sensitive. Use double quotes: `"StockID"` or all lowercase: `stockid`

---

## Rollback Plan

If migration fails, revert to SQLite:

1. **Undo Changes:**
   ```bash
   git checkout HEAD -- UI/modules_external/stock-management/stock_routes.py
   ```

2. **Verify SQLite Database Exists:**
   ```bash
   Test-Path "C:\Users\gpoli\GIT\AI_agents\data\stock_data.db"
   ```

3. **Restart Flask:**
   ```bash
   BISTART
   ```

---

## Next Steps

### ⏳ Remaining Migration Tasks:

1. **Quote Calculator Module** (`UI/modules_external/quote-calculator`)
   - Check if it uses stock database
   - Migrate if needed

2. **Test All Endpoints**
   - Run comprehensive API tests
   - Verify data accuracy
   - Check performance (PostgreSQL should be faster)

3. **Remove SQLite Database File**
   - Once migration verified, delete `data/stock_data.db`
   - Update documentation

4. **Update Frontend**
   - Verify `stock-management.js` works with new responses
   - Check for any hardcoded SQLite references

---

## Benefits of Supabase Migration

✅ **Cloud-Accessible** - Data available from anywhere, not just local machine

✅ **Concurrent Access** - Multiple users can access simultaneously

✅ **Backup & Recovery** - Automatic backups by Supabase

✅ **Scalability** - PostgreSQL handles larger datasets better

✅ **Consistency** - All data in one place (Supabase) instead of split (SQLite + SQL Server)

✅ **Real-time Updates** - Supabase supports real-time subscriptions (future enhancement)

✅ **Security** - Row-level security policies (future enhancement)

---

## Migration Complete ✅

**Date:** December 4, 2025  
**Modified Files:** 1 (`stock_routes.py`)  
**Endpoints Updated:** 7/7 (100%)  
**Database Connection:** SQLite → Supabase PostgreSQL  
**Schema:** `stock_data` schema in Supabase  
**Testing Status:** ⏳ Pending (requires Flask restart + API tests)

---

**Related Documentation:**
- `INHOUSE_DATABASE_GUIDE_CORRECTIONS_DEC4_2025.md` - InHouse Fred database corrections
- `.env.master` - Supabase connection configuration
- `AI_infrastructure/shared/database_utils.py` - Database connection utility
