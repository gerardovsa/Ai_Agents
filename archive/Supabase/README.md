# Supabase Migration Toolkit

Complete toolkit for migrating SQLite databases to Supabase PostgreSQL and managing your Supabase database.

## Quick Start

### Prerequisites

1. **Python Dependencies**:
   ```powershell
   pip install psycopg2-binary python-dotenv
   ```

2. **Supabase Project**:
   - Project Name: ai-agents-production-inhouse
   - URL: https://ryoicrdifiqhqpsnjmdo.supabase.co
   - Region: Singapore (Southeast Asia)
   - Database: PostgreSQL 17.6

3. **Environment Variables** (already in `.env.master`):
   ```bash
   SUPABASE_PROJECT_NAME=ai-agents-production-inhouse
   SUPABASE_PROJECT_PASSWORD=inhouseprint
   SUPABASE_URL=https://ryoicrdifiqhqpsnjmdo.supabase.co
   SUPABASE_SERVICE_ROLE_SECRET=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   SUPABASE_DB_URL=postgresql://postgres:inhouseprint@db.ryoicrdifiqhqpsnjmdo.supabase.co:5432/postgres
   USE_SUPABASE=true
   ```

### Quick Test

```powershell
# Test database connection
cd C:\Users\gpoli\GIT\AI_agents\Supabase
$env:PYTHONIOENCODING="utf-8"
python supabase_toolkit.py test

# Show database summary
python supabase_toolkit.py summary
```

---

## Tools Overview

### 1. **supabase_toolkit.py** - Database CLI Tool

Command-line interface for inspecting and managing your Supabase database.

**Features:**
- Test database connectivity
- View database statistics and summary
- List all schemas and tables
- Inspect table structure (columns, types, constraints)
- Execute custom SQL queries
- Auto-loads credentials from `.env.master`

**Usage:**

```powershell
# Set UTF-8 encoding (required for Windows PowerShell)
$env:PYTHONIOENCODING="utf-8"

# Test connection
python supabase_toolkit.py test

# Show database overview (schemas, tables, row counts)
python supabase_toolkit.py summary

# List all schemas
python supabase_toolkit.py schemas

# List all tables (optionally filter by schema)
python supabase_toolkit.py tables
python supabase_toolkit.py tables --schema ai_infrastructure

# Get table details (columns, types, primary keys)
python supabase_toolkit.py info --table users --schema ai_infrastructure

# Execute custom SQL query
python supabase_toolkit.py query --sql "SELECT * FROM ai_infrastructure.users LIMIT 5"
```

**Example Output:**

```
$ python supabase_toolkit.py summary

=== Database Summary ===
PostgreSQL Version: PostgreSQL 17.6 on aarch64-unknown-linux-gnu
Database Size: 19 MB
Custom Schemas: 5

Custom Schemas Found:
- ai_infrastructure (10 tables, 381 rows)
- sessions (6 tables, 5 rows)
- synergy_sessions (1 table, 15 rows)
- kanban_analytics (14 tables, 3,468 rows)
- stock_data (35 tables, 4,364 rows)

Total Tables: 66
Total Rows: 8,233
```

---

### 2. **migrate_to_supabase.py** - Database Migration Script

Automated migration tool that converts SQLite databases to PostgreSQL with full schema and data preservation.

**Features:**
- Analyzes SQLite databases (schema, tables, row counts)
- Creates PostgreSQL schemas matching SQLite database names
- Converts SQLite types to PostgreSQL types
- Handles boolean conversion (SQLite 0/1 → PostgreSQL true/false)
- Filters SQLite-specific functions from defaults
- Batch inserts for performance (1,000 rows at a time)
- Connection recovery for long migrations
- Data verification after migration
- Auto-loads credentials from `.env.master`

**Usage:**

```powershell
# Set UTF-8 encoding
$env:PYTHONIOENCODING="utf-8"

# Run migration (interactive)
cd C:\Users\gpoli\GIT\AI_agents\Supabase
python migrate_to_supabase.py

# Or auto-confirm all prompts
echo "yes" | python migrate_to_supabase.py
```

**Migration Process:**

1. **Phase 1: Analysis** - Scans all SQLite databases in `AI_infrastructure/data/`
2. **Phase 2: Schema Creation** - Creates PostgreSQL schemas and tables
3. **Phase 3: Data Migration** - Copies data with type conversion
4. **Phase 4: Verification** - Verifies row counts match source

**Example Output:**

```
=== Phase 1: Analyzing SQLite Databases ===
Found 5 databases to migrate:
  ai_infrastructure.db: 10 tables, 381 rows
  sessions.db: 6 tables, 5 rows
  synergy_sessions.db: 1 table, 15 rows
  kanban_analytics.db: 14 tables, 3,468 rows
  stock_data.db: 35 tables, 4,364 rows

Total: 66 tables, 8,233 rows

=== Phase 2: Creating Schemas ===
Creating schema: ai_infrastructure... OK
Creating schema: sessions... OK
Creating schema: synergy_sessions... OK
Creating schema: kanban_analytics... OK
Creating schema: stock_data... OK

=== Phase 3: Migrating Data ===
Migrating ai_infrastructure.users (50 rows)... OK (50 rows)
Migrating ai_infrastructure.user_platform_credentials (25 rows)... OK (25 rows)
...

=== Phase 4: Verification ===
Verifying ai_infrastructure schema:
  users: 50 rows (SQLite) = 50 rows (PostgreSQL) ✓
  user_platform_credentials: 25 rows (SQLite) = 25 rows (PostgreSQL) ✓
...

SUCCESS! All data migrated and verified.
```

**Type Conversions:**

| SQLite Type | PostgreSQL Type | Notes |
|-------------|-----------------|-------|
| INTEGER | INTEGER | Direct mapping |
| TEXT | TEXT | Direct mapping |
| REAL | REAL | Direct mapping |
| BLOB | BYTEA | Binary data |
| BOOLEAN | BOOLEAN | 0/1 → false/true |
| TIMESTAMP | TIMESTAMP | Date/time handling |
| INTEGER PRIMARY KEY | SERIAL PRIMARY KEY | Auto-increment |

**Boolean Handling:**

SQLite stores booleans as integers (0/1). The migration script automatically converts these to PostgreSQL booleans (false/true) during data migration:

```python
# Migration handles this automatically
SQLite: 0 → PostgreSQL: false
SQLite: 1 → PostgreSQL: true
```

---

### 3. **finish_stock_data_migration.py** - Stock Data Completion Script

Specialized script for completing `stock_data` schema migration with PostgreSQL lowercase table name handling.

**Purpose:**

PostgreSQL automatically lowercases unquoted identifiers (table names, column names). If your SQLite database has mixed-case table names like `StockLevels`, PostgreSQL stores them as `stocklevels`. This script handles that case sensitivity issue.

**Features:**
- Maps SQLite table names to PostgreSQL lowercase names
- Boolean type conversion (0/1 → true/false)
- Integer validation for text fields
- Truncate before insert (prevents duplicate key errors)
- Verification after completion

**Usage:**

```powershell
# Set UTF-8 encoding
$env:PYTHONIOENCODING="utf-8"

# Run completion script
cd C:\Users\gpoli\GIT\AI_agents\Supabase
python finish_stock_data_migration.py
```

**Example Output:**

```
Migrating StockLevels (183 rows)... OK (183 rows)
Migrating extracted_jobs (1336 rows)... OK (1336 rows)
Migrating shopify_orders (54 rows)... OK (54 rows)
...

Verifying migration...
  extracted_jobs: 1336 rows ✓
  stocklevels: 183 rows ✓
...

Stock data migration complete!
```

---

## Common Tasks

### View All Schemas

```powershell
python supabase_toolkit.py schemas
```

### List Tables in a Schema

```powershell
python supabase_toolkit.py tables --schema ai_infrastructure
```

### Get Table Structure

```powershell
python supabase_toolkit.py info --table users --schema ai_infrastructure
```

Output shows:
- Column names
- Data types
- Primary keys
- Foreign keys
- Indexes
- Constraints

### Execute Custom Query

```powershell
# Simple SELECT
python supabase_toolkit.py query --sql "SELECT COUNT(*) FROM ai_infrastructure.users"

# Complex query with JOIN
python supabase_toolkit.py query --sql "SELECT u.username, COUNT(t.id) as thread_count FROM ai_infrastructure.users u LEFT JOIN ai_infrastructure.threads t ON u.id = t.user_id GROUP BY u.username"

# Save results to file
python supabase_toolkit.py query --sql "SELECT * FROM stock_data.stocklevels" > stock_levels.txt
```

### Check Migration Status

```powershell
# Count rows in all schemas
python supabase_toolkit.py query --sql "SELECT schemaname, tablename, n_live_tup as row_count FROM pg_stat_user_tables WHERE schemaname NOT LIKE 'pg_%' AND schemaname != 'information_schema' ORDER BY schemaname, tablename"
```

### Find Duplicate Records

```powershell
python supabase_toolkit.py query --sql "SELECT email, COUNT(*) as count FROM ai_infrastructure.users GROUP BY email HAVING COUNT(*) > 1"
```

### View Table Sizes

```powershell
python supabase_toolkit.py query --sql "SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size FROM pg_tables WHERE schemaname NOT LIKE 'pg_%' ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC"
```

### Export Data to CSV (via query)

```powershell
python supabase_toolkit.py query --sql "COPY ai_infrastructure.users TO STDOUT WITH CSV HEADER" > users_export.csv
```

### Check for Missing Indexes

```powershell
python supabase_toolkit.py query --sql "SELECT schemaname, tablename, attname FROM pg_stats WHERE schemaname = 'ai_infrastructure' AND n_distinct > 100 AND correlation < 0.5"
```

---

## Database Schema Overview

### Current Structure (Post-Migration)

**Total Stats:**
- **Database Size**: 19 MB
- **Total Schemas**: 5 custom schemas
- **Total Tables**: 66 tables
- **Total Rows**: 8,233 rows

### Schema Breakdown

#### 1. **ai_infrastructure** Schema (10 tables, 381 rows)

Core application data for user management, credentials, threads, and OAuth tokens.

**Tables:**
- `users` - User accounts
- `user_platform_credentials` - OAuth tokens for Google/Microsoft
- `threads` - Conversation threads
- `thread_assignments` - Agent-thread mappings
- `messages` - Chat messages (legacy)
- `thread_messages` - Thread-specific messages
- `documents` - Attached documents
- `exports` - Export history
- `sync_status` - Sync tracking
- `oauth_states` - OAuth state verification

#### 2. **sessions** Schema (6 tables, 5 rows)

Flask session management and JWT tokens.

**Tables:**
- `sessions` - Active sessions
- `session_tokens` - JWT tokens
- `session_metadata` - Session tracking
- `login_history` - Login attempts
- `session_logs` - Audit logs
- `refresh_tokens` - Refresh token storage

#### 3. **synergy_sessions** Schema (1 table, 15 rows)

Synergy feature session data.

**Tables:**
- `synergy_sessions` - Multi-agent sessions

#### 4. **kanban_analytics** Schema (14 tables, 3,468 rows)

Kanban board analytics and metrics.

**Tables:**
- `boards` - Kanban boards
- `lists` - Board lists/columns
- `cards` - Individual cards
- `card_history` - Card change history
- `card_metrics` - Performance metrics
- `board_analytics` - Board-level stats
- `user_activity` - User actions
- `sprint_data` - Sprint tracking
- `velocity_metrics` - Team velocity
- `cycle_time` - Card cycle times
- `wip_limits` - Work-in-progress limits
- `tags` - Card tags
- `attachments` - File attachments
- `comments` - Card comments

#### 5. **stock_data** Schema (35 tables, 4,364 rows)

Stock management, Shopify data, and print job tracking.

**Tables:**

**Stock Management:**
- `stocklevels` - Current stock quantities
- `stocktransactions` - Stock movements
- `consumableinventory` - Consumable items
- `clickcosts` - Click cost tracking
- `profitmargins` - Profit calculations
- `stockmarkuprules` - Pricing rules
- `corflute_materials` - Sign materials
- `corflute_material_transactions` - Material usage
- `unified_stocks` - Consolidated stock view
- `job_stocks` - Stock used in jobs

**Shopify Integration:**
- `shopify_orders` - Order data
- `shopify_line_items` - Order line items
- `shopify_line_properties` - Line item properties
- `shopify_customers` - Customer data
- `shopify_customer_addresses` - Shipping addresses
- `shopify_products` - Product catalog
- `shopify_product_variants` - Product variations
- `shopify_product_images` - Product images
- `shopify_abandoned_checkouts` - Abandoned carts
- `shopify_abandoned_line_items` - Abandoned cart items

**Print Jobs:**
- `extracted_jobs` - Print job data (1,336 rows)

**Additional tables:** (various business logic tables)
- Plus 15 more specialized tables for print pricing, materials, and workflow

---

## Troubleshooting

### Issue: UnicodeEncodeError in Windows PowerShell

**Symptom:**
```
UnicodeEncodeError: 'charmap' codec can't encode character '\u2713'
```

**Solution:**
Always set UTF-8 encoding before running scripts:
```powershell
$env:PYTHONIOENCODING="utf-8"
```

Or add to PowerShell profile for permanent fix:
```powershell
# Edit profile
notepad $PROFILE

# Add this line:
$env:PYTHONIOENCODING="utf-8"
```

---

### Issue: Connection Timeout

**Symptom:**
```
psycopg2.OperationalError: connection to server at "db.ryoicrdifiqhqpsnjmdo.supabase.co" failed
```

**Solutions:**

1. **Check internet connection:**
   ```powershell
   Test-Connection db.ryoicrdifiqhqpsnjmdo.supabase.co
   ```

2. **Verify credentials in .env.master:**
   - Ensure `SUPABASE_DB_URL` is correct
   - Check password is correct

3. **Test connection directly:**
   ```powershell
   python supabase_toolkit.py test
   ```

4. **Check Supabase project status:**
   - Visit https://supabase.com/dashboard
   - Ensure project is not paused

---

### Issue: Boolean Type Mismatch

**Symptom:**
```
psycopg2.errors.InvalidTextRepresentation: invalid input syntax for type boolean: "0"
```

**Explanation:**

SQLite stores booleans as integers (0/1), but PostgreSQL expects boolean literals (false/true).

**Solution:**

The migration scripts handle this automatically. If you're manually inserting data:

```python
# Bad (SQLite style)
cursor.execute("INSERT INTO users (is_active) VALUES (1)")

# Good (PostgreSQL style)
cursor.execute("INSERT INTO users (is_active) VALUES (true)")

# Or with Python boolean
cursor.execute("INSERT INTO users (is_active) VALUES (%s)", (True,))
```

---

### Issue: Table Not Found (Case Sensitivity)

**Symptom:**
```
psycopg2.errors.UndefinedTable: relation "StockLevels" does not exist
```

**Explanation:**

PostgreSQL lowercases all unquoted identifiers. `StockLevels` becomes `stocklevels`.

**Solution:**

Use lowercase table names in queries:

```python
# Bad
cursor.execute("SELECT * FROM StockLevels")

# Good
cursor.execute("SELECT * FROM stocklevels")

# Or use quoted identifiers (preserves case)
cursor.execute('SELECT * FROM "StockLevels"')
```

The `finish_stock_data_migration.py` script handles this automatically.

---

### Issue: Duplicate Key Violation

**Symptom:**
```
psycopg2.errors.UniqueViolation: duplicate key value violates unique constraint "users_pkey"
```

**Explanation:**

Re-running migration without truncating tables first.

**Solution:**

1. **Truncate tables before re-migration:**
   ```python
   cursor.execute("TRUNCATE TABLE schema.tablename CASCADE")
   ```

2. **Or drop and recreate schema:**
   ```python
   cursor.execute("DROP SCHEMA IF EXISTS schema CASCADE")
   cursor.execute("CREATE SCHEMA schema")
   ```

3. **Or use the finish script** (has built-in truncate):
   ```powershell
   python finish_stock_data_migration.py
   ```

---

### Issue: Schema Not Found

**Symptom:**
```
psycopg2.errors.InvalidSchemaName: schema "ai_infrastructure" does not exist
```

**Solution:**

1. **List existing schemas:**
   ```powershell
   python supabase_toolkit.py schemas
   ```

2. **Create schema if missing:**
   ```powershell
   python supabase_toolkit.py query --sql "CREATE SCHEMA IF NOT EXISTS ai_infrastructure"
   ```

3. **Re-run migration:**
   ```powershell
   python migrate_to_supabase.py
   ```

---

### Issue: Migration Hangs on Large Tables

**Symptom:**

Script appears frozen during large table migration (e.g., `extracted_jobs` with 1,336 rows).

**Solution:**

This is normal. The script uses batch inserts (1,000 rows at a time) for performance. Large tables take time:

- **100 rows**: ~2 seconds
- **1,000 rows**: ~15 seconds
- **10,000 rows**: ~2 minutes

Be patient. Progress messages appear after each table completes.

---

## Advanced Usage

### Use as Python Library

```python
from supabase_toolkit import SupabaseToolkit

# Initialize
toolkit = SupabaseToolkit()

# Test connection
if toolkit.test_connection():
    print("Connected!")

# Get all schemas
schemas = toolkit.list_schemas()
print(f"Found {len(schemas)} schemas")

# Get tables in schema
tables = toolkit.list_tables(schema='ai_infrastructure')
for table in tables:
    print(f"Table: {table['name']} ({table['row_count']} rows)")

# Get table structure
info = toolkit.get_table_info('users', schema='ai_infrastructure')
print(f"Columns: {info['columns']}")

# Execute query
results = toolkit.execute_query("SELECT * FROM ai_infrastructure.users LIMIT 5")
for row in results:
    print(row)

# Show summary
toolkit.show_database_summary()
```

### Custom Migration Script

```python
from migrate_to_supabase import SupabaseMigration
import sqlite3

# Initialize migration
migration = SupabaseMigration()

# Connect to Supabase
migration.connect_supabase()

# Connect to custom SQLite database
sqlite_conn = sqlite3.connect('my_custom_database.db')

# Migrate specific table
schema_name = 'my_schema'
table_name = 'my_table'

# Create schema
migration.pg_cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")

# Create table (implement your own schema conversion)
create_table_sql = """
CREATE TABLE my_schema.my_table (
    id SERIAL PRIMARY KEY,
    name TEXT,
    created_at TIMESTAMP DEFAULT NOW()
)
"""
migration.pg_cursor.execute(create_table_sql)

# Migrate data
sqlite_cursor = sqlite_conn.cursor()
rows = sqlite_cursor.execute("SELECT * FROM my_table").fetchall()

insert_sql = "INSERT INTO my_schema.my_table (id, name, created_at) VALUES %s"
migration.batch_insert(schema_name, table_name, rows, insert_sql)

# Commit
migration.pg_conn.commit()
print("Custom migration complete!")
```

---

## Security Best Practices

### 1. **Never Commit Credentials**

`.env.master` is in `.gitignore` for a reason. NEVER commit:

- Database passwords
- Service role secrets
- Connection strings
- API keys

### 2. **Use Service Role Key Securely**

The `SUPABASE_SERVICE_ROLE_SECRET` has admin access. Only use it server-side, never in client-side code.

### 3. **Rotate Credentials Regularly**

From Supabase dashboard:
1. Go to **Settings → Database**
2. Click **Reset Database Password**
3. Update `.env.master` with new password
4. Restart applications

### 4. **Use RLS (Row-Level Security)**

Enable Row-Level Security on tables accessed by public API:

```sql
ALTER TABLE ai_infrastructure.users ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can only see their own data"
ON ai_infrastructure.users
FOR SELECT
USING (id = auth.uid());
```

### 5. **Monitor Database Access**

Check for suspicious queries:

```powershell
python supabase_toolkit.py query --sql "SELECT usename, application_name, client_addr, query_start, state, query FROM pg_stat_activity WHERE datname = 'postgres' ORDER BY query_start DESC LIMIT 20"
```

---

## Performance Tips

### 1. **Add Indexes for Frequent Queries**

```sql
-- Add index on foreign keys
CREATE INDEX idx_threads_user_id ON ai_infrastructure.threads(user_id);

-- Add index on timestamp columns (for date range queries)
CREATE INDEX idx_messages_created_at ON ai_infrastructure.messages(created_at);

-- Add composite index for common query patterns
CREATE INDEX idx_shopify_orders_customer_date 
ON stock_data.shopify_orders(customer_id, created_at);
```

### 2. **Use EXPLAIN ANALYZE**

Check query performance:

```powershell
python supabase_toolkit.py query --sql "EXPLAIN ANALYZE SELECT * FROM ai_infrastructure.users WHERE email = 'test@example.com'"
```

### 3. **Vacuum Database Regularly**

PostgreSQL needs periodic maintenance:

```sql
-- Reclaim storage and update statistics
VACUUM ANALYZE;

-- More aggressive cleanup (blocks other operations)
VACUUM FULL;
```

### 4. **Monitor Table Sizes**

Keep an eye on growth:

```powershell
python supabase_toolkit.py query --sql "SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size FROM pg_tables WHERE schemaname IN ('ai_infrastructure', 'stock_data', 'kanban_analytics') ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC"
```

### 5. **Use Connection Pooling in Production**

Update your app code to use connection pooling:

```python
from psycopg2 import pool

# Create connection pool
connection_pool = pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    host='db.ryoicrdifiqhqpsnjmdo.supabase.co',
    database='postgres',
    user='postgres',
    password='inhouseprint',
    port=5432
)

# Get connection from pool
conn = connection_pool.getconn()

# ... use connection ...

# Return to pool (don't close!)
connection_pool.putconn(conn)
```

---

## Integration with Application

### Update AI_infrastructure/config.py

Add Supabase configuration:

```python
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.master')

class Config:
    # Existing config...
    
    # Supabase configuration
    USE_SUPABASE = os.getenv('USE_SUPABASE', 'false').lower() == 'true'
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_SECRET')
    SUPABASE_DB_URL = os.getenv('SUPABASE_DB_URL')
    
    @staticmethod
    def get_database_connection():
        """Get database connection (SQLite or PostgreSQL based on config)"""
        if Config.USE_SUPABASE:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            conn = psycopg2.connect(Config.SUPABASE_DB_URL)
            conn.cursor_factory = RealDictCursor
            return conn
        else:
            import sqlite3
            conn = sqlite3.connect('AI_infrastructure/data/ai_infrastructure.db')
            conn.row_factory = sqlite3.Row
            return conn
```

### Update Database Access Code

Replace SQLite-specific code:

```python
# Before (SQLite only)
import sqlite3
conn = sqlite3.connect('AI_infrastructure/data/ai_infrastructure.db')
cursor = conn.cursor()

# After (supports both SQLite and PostgreSQL)
from AI_infrastructure.config import Config
conn = Config.get_database_connection()
cursor = conn.cursor()

# Use parameterized queries (compatible with both)
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
```

### Add to Render Environment Variables

From Render dashboard:

1. Go to your service
2. Click **Environment**
3. Add variables:
   - `USE_SUPABASE=true`
   - `SUPABASE_URL=https://ryoicrdifiqhqpsnjmdo.supabase.co`
   - `SUPABASE_SERVICE_ROLE_SECRET=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
   - `SUPABASE_DB_URL=postgresql://postgres:inhouseprint@db...`

Or use the script:

```powershell
cd C:\Users\gpoli\GIT\AI_agents\Render_backend
python add_supabase_env_vars.py
```

---

## Next Steps

### For Deployment

1. **Add environment variables to Render**:
   ```powershell
   python Render_backend/add_supabase_env_vars.py
   ```

2. **Update application code** to use `Config.get_database_connection()`

3. **Test locally with Supabase**:
   ```powershell
   $env:USE_SUPABASE="true"
   BISTART
   ```

4. **Remove persistent disk from render.yaml** (no longer needed)

5. **Deploy to Render** and monitor

### For Database Management

1. **Set up automated backups** (Supabase Pro plan has daily backups)

2. **Create read-only user** for analytics:
   ```sql
   CREATE USER analytics WITH PASSWORD 'secure_password';
   GRANT CONNECT ON DATABASE postgres TO analytics;
   GRANT USAGE ON SCHEMA ai_infrastructure TO analytics;
   GRANT SELECT ON ALL TABLES IN SCHEMA ai_infrastructure TO analytics;
   ```

3. **Add monitoring alerts** in Supabase dashboard

4. **Document schema changes** in `CHANGELOG.md`

### For Optimization

1. **Add indexes** for slow queries (use `EXPLAIN ANALYZE`)

2. **Enable connection pooling** in production

3. **Set up query caching** for frequently accessed data

4. **Partition large tables** (e.g., `messages` by date)

---

## Cost Comparison

**Before (Render Persistent Disk):**
- 10 GB persistent disk: $2.50/month
- Limited by single-server disk I/O
- Manual backups required

**After (Supabase Free Tier):**
- 500 MB database: $0/month (FREE)
- Distributed PostgreSQL with auto-scaling
- Automatic daily backups
- Real-time subscriptions available
- RESTful API included

**Savings:** $2.50/month + better performance and features!

**Upgrade Path:** If you exceed 500 MB, Supabase Pro is $25/month for 8 GB + advanced features.

---

## Resources

### Supabase Dashboard
https://supabase.com/dashboard/project/ryoicrdifiqhqpsnjmdo

### Documentation
- [Supabase Docs](https://supabase.com/docs)
- [PostgreSQL 17 Docs](https://www.postgresql.org/docs/17/)
- [psycopg2 Docs](https://www.psycopg.org/docs/)

### Internal Docs
- `SUPABASE_SETUP_GUIDE.md` - Initial setup steps
- `QUICKSTART_CHECKLIST.md` - Quick reference checklist
- `MIGRATION_SUCCESS_SUMMARY.md` - Full migration results

### Support
- Open an issue on GitHub
- Check Supabase community: https://github.com/supabase/supabase/discussions

---

## Version History

**v1.0.0** (January 2025)
- Initial toolkit creation
- Full migration from SQLite (5 databases, 66 tables, 8,233 rows)
- CLI tool with 6 commands
- Comprehensive documentation

---

**Last Updated:** January 2025  
**Maintained By:** AI Agents Team  
**Database:** PostgreSQL 17.6 on Supabase (Singapore)
