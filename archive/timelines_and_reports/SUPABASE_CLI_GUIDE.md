# Supabase CLI Tools - Complete Usage Guide
**Date:** January 2025  
**Version:** 2.0  
**Status:** Production Ready  

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Installation & Setup](#installation--setup)
4. [Available Tools](#available-tools)
5. [Command Reference](#command-reference)
6. [Common Tasks](#common-tasks)
7. [Troubleshooting](#troubleshooting)
8. [Integration with Application](#integration-with-application)

---

## Overview

The Supabase CLI toolkit provides comprehensive database management capabilities for the AI Agents platform. It includes:

- **Connection Testing** - Verify Supabase connectivity
- **Schema Inspection** - Browse schemas, tables, and columns
- **Data Analysis** - Query data and verify migration results
- **Comparison Tools** - Compare SQLite (local) vs Supabase (production)

### Available Tools

| Tool | Location | Purpose |
|------|----------|---------|
| `supabase_toolkit.py` | `Supabase/` | CLI tool for database operations |
| `test_supabase_connection.py` | `Supabase/` | Connection verification |
| `migrate_to_supabase.py` | `Supabase/` | SQLite → Supabase migration |
| `show_database_structure_v2.py` | `data/` | Dual-mode database analyzer |

---

## Quick Start

### Test Connection
```powershell
cd C:\Users\gpoli\GIT\AI_agents

# Test Supabase connection
python Supabase\supabase_toolkit.py test
```

**Expected Output:**
```
================================================================================
CONNECTION TEST
================================================================================

✓ Connection test successful

PostgreSQL Version: PostgreSQL 15.1 (Ubuntu 15.1-1.pgdg20.04+1) on x86_64...
Database Size: 1024 kB
Custom Schemas: 5

================================================================================
```

### View Database Summary
```powershell
# Full database overview
python Supabase\supabase_toolkit.py summary
```

**Expected Output:**
```
================================================================================
SUPABASE DATABASE SUMMARY
================================================================================

Project: ai-agents-production-inhouse
PostgreSQL Version: PostgreSQL 15.1...
Database Size: 1024 kB
Custom Schemas: 5

--------------------------------------------------------------------------------
SCHEMAS
--------------------------------------------------------------------------------

  • ai_infrastructure
      - users (12 columns)
      - oauth_tokens (8 columns)
      - user_sessions (10 columns)
      ...
  
  • sessions
      - threads (15 columns)
      - messages (10 columns)
      ...
```

---

## Installation & Setup

### Prerequisites

Ensure you have the required Python packages:

```powershell
# Install dependencies
pip install psycopg2-binary python-dotenv
```

### Credentials Setup

Credentials are automatically loaded from `.env.master`. Verify they exist:

```powershell
# Check .env.master contains:
SUPABASE_URL=https://ryoicrdifiqhqpsnjmdo.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGci...
SUPABASE_DB_URL=postgresql://postgres:inhouseprint@db.ryoicrdifiqhqpsnjmdo.supabase.co:5432/postgres
SUPABASE_PROJECT_NAME=ai-agents-production-inhouse
```

**Environment Variables Required:**
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_SERVICE_KEY` - Service role key (full access)
- `SUPABASE_DB_URL` - Direct PostgreSQL connection string
- `SUPABASE_PROJECT_NAME` - Project name (optional, for display)

---

## Available Tools

### 1. Supabase Toolkit (supabase_toolkit.py)

**Location:** `C:\Users\gpoli\GIT\AI_agents\Supabase\supabase_toolkit.py`  
**Purpose:** Main CLI tool for all Supabase operations

**Features:**
- Connection testing
- Schema browsing
- Table inspection
- SQL query execution
- Migration verification

**Usage Pattern:**
```powershell
python Supabase\supabase_toolkit.py <command> [options]
```

---

### 2. Connection Test (test_supabase_connection.py)

**Location:** `C:\Users\gpoli\GIT\AI_agents\Supabase\test_supabase_connection.py`  
**Purpose:** Quick connection verification

**Usage:**
```powershell
python Supabase\test_supabase_connection.py
```

**Output:**
```
Testing Supabase Connection...
✓ Connected successfully!

Database: postgres
Version: PostgreSQL 15.1...
Custom Schemas: 5
```

---

### 3. Migration Tool (migrate_to_supabase.py)

**Location:** `C:\Users\gpoli\GIT\AI_agents\Supabase\migrate_to_supabase.py`  
**Purpose:** Migrate SQLite databases to Supabase

**Features:**
- Automatic schema detection
- Data type conversion (INTEGER→TEXT for mixed data)
- Foreign key preservation
- Row count verification
- Rollback on error

**Usage:**
```powershell
# Full migration (all databases)
python Supabase\migrate_to_supabase.py

# Single database migration
python Supabase\migrate_to_supabase.py --database sessions.db
```

**DO NOT RUN** - Migration already complete (76 tables, 8,773 rows verified)

---

### 4. Database Analyzer v2.0 (show_database_structure_v2.py)

**Location:** `C:\Users\gpoli\GIT\AI_agents\data\show_database_structure_v2.py`  
**Purpose:** Compare SQLite (local) and Supabase (production)

**Features:**
- Dual-mode analysis (SQLite + Supabase)
- Schema comparison
- Row count verification
- Column structure comparison
- Script database usage analysis

**Usage:**
```powershell
python data\show_database_structure_v2.py
```

**Output:**
- SQLite database structure
- Supabase schema structure
- Comparison report (differences, missing tables, row count mismatches)
- Script analysis (which files use direct sqlite3.connect())
- Report saved to: `data/database_analysis_v2_report.txt`

---

## Command Reference

### Test Connection

```powershell
python Supabase\supabase_toolkit.py test
```

**What it does:**
- Connects to Supabase
- Retrieves PostgreSQL version
- Gets database size
- Counts custom schemas
- Verifies credentials

**When to use:**
- Before any database operations
- After updating credentials
- Troubleshooting connection issues

---

### Show Summary

```powershell
python Supabase\supabase_toolkit.py summary
```

**What it does:**
- Displays connection status
- Lists all schemas
- Shows tables in each schema
- Displays column counts
- Shows database size

**When to use:**
- Get overview of entire database
- Verify migration results
- Check what schemas exist

---

### List Schemas

```powershell
python Supabase\supabase_toolkit.py schemas
```

**What it does:**
- Lists all custom schemas (excludes system schemas)
- Shows: ai_infrastructure, sessions, synergy_sessions, kanban_analytics, stock_data

**When to use:**
- Verify all schemas migrated
- Check schema names for queries

**Example Output:**
```
================================================================================
DATABASE SCHEMAS
================================================================================

  • ai_infrastructure
  • sessions
  • synergy_sessions
  • kanban_analytics
  • stock_data

================================================================================
```

---

### List Tables

```powershell
# List tables in default schema (public)
python Supabase\supabase_toolkit.py tables

# List tables in specific schema
python Supabase\supabase_toolkit.py tables --schema sessions
```

**What it does:**
- Lists all tables in specified schema
- Shows column count for each table

**When to use:**
- Verify tables migrated to schema
- Check table names before querying

**Example Output:**
```
================================================================================
TABLES IN SCHEMA: sessions
================================================================================

  • threads (15 columns)
  • messages (10 columns)
  • thread_assignments (8 columns)
  • saved_threads (12 columns)
  • users (7 columns)

================================================================================
```

---

### Table Info

```powershell
# Get info about a specific table
python Supabase\supabase_toolkit.py info --schema sessions --table threads
```

**What it does:**
- Shows detailed table information
- Lists all columns with types
- Shows nullable/not null constraints
- Displays row count
- Shows table size

**When to use:**
- Before writing queries
- Verify column names and types
- Check table structure

**Example Output:**
```
================================================================================
TABLE INFO: sessions.threads
================================================================================

Rows: 82
Size: 64 kB

Columns (15):
  • id: integer NOT NULL DEFAULT nextval('sessions.threads_id_seq'::regclass)
  • thread_slug: text NOT NULL
  • name: text NOT NULL
  • user_id: integer
  • last_message_timestamp: timestamp with time zone
  • last_agent_location: text
  • created_at: timestamp with time zone DEFAULT now()
  ...

================================================================================
```

---

### Execute Query

```powershell
# Basic query
python Supabase\supabase_toolkit.py query --query "SELECT * FROM sessions.threads LIMIT 5"

# Query with WHERE clause
python Supabase\supabase_toolkit.py query --query "SELECT id, name, user_id FROM sessions.threads WHERE user_id = 1"

# Count rows
python Supabase\supabase_toolkit.py query --query "SELECT COUNT(*) FROM sessions.threads"

# Join query
python Supabase\supabase_toolkit.py query --query "SELECT t.name, u.email FROM sessions.threads t JOIN ai_infrastructure.users u ON t.user_id = u.id"
```

**What it does:**
- Executes any SELECT query
- Returns results (first 10 rows by default)
- Formats output for readability

**When to use:**
- Verify data migrated correctly
- Check specific records
- Test query before using in code

**Example Output:**
```
================================================================================
QUERY RESULTS (5 rows)
================================================================================

Row 1:
  id: 1
  thread_slug: main-chat-2025
  name: Main Chat Thread
  user_id: 1
  last_message_timestamp: 2025-01-15 14:30:22+00
  last_agent_location: prime
  created_at: 2025-01-10 08:15:33+00

Row 2:
  ...

================================================================================
```

---

## Common Tasks

### 1. Verify Migration

**Check all tables migrated:**
```powershell
python Supabase\supabase_toolkit.py summary
```

**Verify row counts:**
```powershell
# Check sessions.threads
python Supabase\supabase_toolkit.py query --query "SELECT COUNT(*) FROM sessions.threads"

# Expected: 82 rows (matches local sessions.db)
```

**Compare with local SQLite:**
```powershell
python data\show_database_structure_v2.py
```

This will generate a report showing:
- Row count differences
- Missing tables
- Column mismatches

---

### 2. View Specific User Data

```powershell
# Get user details
python Supabase\supabase_toolkit.py query --query "SELECT id, email, username, role FROM ai_infrastructure.users WHERE id = 1"

# Get user's threads
python Supabase\supabase_toolkit.py query --query "SELECT id, name, created_at FROM sessions.threads WHERE user_id = 1 ORDER BY created_at DESC LIMIT 10"

# Get user's messages in a thread
python Supabase\supabase_toolkit.py query --query "SELECT role, content, timestamp FROM sessions.messages WHERE thread_id = 1 ORDER BY timestamp DESC LIMIT 5"
```

---

### 3. Check OAuth Tokens

```powershell
# View all OAuth connections
python Supabase\supabase_toolkit.py query --query "SELECT user_id, platform, email, created_at FROM ai_infrastructure.user_platform_credentials ORDER BY created_at DESC"

# Check specific user's OAuth tokens
python Supabase\supabase_toolkit.py query --query "SELECT platform, email, token_expiry FROM ai_infrastructure.user_platform_credentials WHERE user_id = 1"
```

---

### 4. Analyze Stock Data

```powershell
# Get stock levels summary
python Supabase\supabase_toolkit.py query --query "SELECT \"StockName\", \"CurrentQuantity\", \"MinLevel\" FROM stock_data.\"StockLevels\" WHERE \"CurrentQuantity\" < \"MinLevel\""

# Count extracted jobs
python Supabase\supabase_toolkit.py query --query "SELECT COUNT(*) FROM stock_data.extracted_jobs"

# View recent orders
python Supabase\supabase_toolkit.py query --query "SELECT order_id, customer_name, order_date, status FROM kanban_analytics.orders ORDER BY order_date DESC LIMIT 10"
```

---

### 5. Check Application Health

```powershell
# Count active threads
python Supabase\supabase_toolkit.py query --query "SELECT COUNT(*) FROM sessions.threads WHERE last_message_timestamp > NOW() - INTERVAL '7 days'"

# Count users by role
python Supabase\supabase_toolkit.py query --query "SELECT role, COUNT(*) FROM ai_infrastructure.users GROUP BY role"

# Check recent Synergy sessions
python Supabase\supabase_toolkit.py query --query "SELECT id, name, created_at FROM synergy_sessions.synergy_sessions ORDER BY created_at DESC LIMIT 5"
```

---

### 6. Find Data Issues

```powershell
# Find threads with no messages
python Supabase\supabase_toolkit.py query --query "SELECT t.id, t.name FROM sessions.threads t LEFT JOIN sessions.messages m ON t.id = m.thread_id WHERE m.id IS NULL"

# Find users without OAuth
python Supabase\supabase_toolkit.py query --query "SELECT u.id, u.email FROM ai_infrastructure.users u LEFT JOIN ai_infrastructure.user_platform_credentials c ON u.id = c.user_id WHERE c.id IS NULL"

# Check for duplicate thread slugs
python Supabase\supabase_toolkit.py query --query "SELECT thread_slug, COUNT(*) FROM sessions.threads GROUP BY thread_slug HAVING COUNT(*) > 1"
```

---

## Troubleshooting

### Connection Issues

**Error: "Connection refused"**

Check:
1. Supabase project is active (not paused)
2. Database URL is correct in `.env.master`
3. Network connectivity (firewall, VPN)

```powershell
# Test connection
python Supabase\test_supabase_connection.py
```

---

**Error: "SSL connection failed"**

Fix: Verify `sslmode='require'` is set in connection string

```python
# In database_utils.py, line 140:
conn = psycopg2.connect(
    connection_string,
    sslmode='require'  # REQUIRED for Supabase
)
```

---

**Error: "Authentication failed"**

Check:
1. `SUPABASE_SERVICE_KEY` is correct (not anon key)
2. Key hasn't expired
3. Copy full key from Supabase Dashboard → Settings → API

---

### Query Issues

**Error: "relation does not exist"**

Fix: Use schema-qualified table names

```powershell
# WRONG:
python Supabase\supabase_toolkit.py query --query "SELECT * FROM threads"

# CORRECT:
python Supabase\supabase_toolkit.py query --query "SELECT * FROM sessions.threads"
```

---

**Error: "column does not exist"**

Fix: Column names are case-sensitive in PostgreSQL

```powershell
# WRONG (if column is "StockName"):
--query "SELECT stockname FROM stock_data.StockLevels"

# CORRECT:
--query "SELECT \"StockName\" FROM stock_data.\"StockLevels\""
```

**Note:** Use double quotes for mixed-case identifiers

---

**Error: "permission denied"**

Check:
1. Using `SUPABASE_SERVICE_KEY` (not anon key)
2. Table exists in Supabase Dashboard
3. Schema name is correct

```powershell
# Verify schema exists:
python Supabase\supabase_toolkit.py schemas
```

---

### Performance Issues

**Slow queries**

Fix: Add LIMIT clause for large tables

```powershell
# SLOW (no limit):
--query "SELECT * FROM sessions.messages"

# FAST (limited):
--query "SELECT * FROM sessions.messages LIMIT 100"
```

---

**Timeout errors**

Fix: Increase timeout in `database_utils.py`

```python
# Line 145:
conn = psycopg2.connect(
    connection_string,
    sslmode='require',
    connect_timeout=30  # Increase from 10 to 30 seconds
)
```

---

## Integration with Application

### Using in Python Code

```python
import sys
from pathlib import Path

# Add Supabase toolkit to path
sys.path.insert(0, str(Path(__file__).parent / 'Supabase'))

from supabase_toolkit import SupabaseToolkit

# Initialize toolkit
toolkit = SupabaseToolkit()

# Test connection
if toolkit.connect():
    # List schemas
    schemas = toolkit.list_schemas()
    print(f"Found {len(schemas)} schemas")
    
    # Query data
    results = toolkit.execute_query(
        "SELECT * FROM sessions.threads WHERE user_id = %s LIMIT 10",
        (1,)
    )
    print(f"Found {len(results)} threads")
    
    # Cleanup
    toolkit.disconnect()
```

---

### Using Centralized Database Utility

**Recommended: Use `get_database_connection()` instead of direct connection**

```python
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'AI_infrastructure'))
from shared.database_utils import get_database_connection

# Auto-detects SQLite vs Supabase based on environment
conn = get_database_connection('sessions')  # Uses sessions schema

# Works with both SQLite and PostgreSQL
cursor = conn.cursor()
cursor.execute("SELECT * FROM threads WHERE user_id = ?", (1,))  # SQLite
cursor.execute("SELECT * FROM threads WHERE user_id = %s", (1,))  # PostgreSQL

# Close connection
conn.close()
```

**Benefits:**
- Automatic SQLite ↔ Supabase switching
- Uses `USE_SUPABASE` + `RENDER` environment variables
- Handles schema mapping (sessions.db → sessions schema)
- Consistent error handling

---

### Environment Detection

The application automatically uses Supabase when:

```python
USE_SUPABASE=true  # Enable Supabase mode
RENDER=true        # Running on Render (production)
```

**Local development (SQLite):**
```bash
USE_SUPABASE=false  # or not set
```

**Production (Supabase):**
```bash
USE_SUPABASE=true
RENDER=true
```

---

## Schema Mappings

SQLite databases map to Supabase schemas:

| SQLite Database | Supabase Schema | Tables |
|----------------|----------------|--------|
| `ai_infrastructure.db` | `ai_infrastructure` | 16 tables (users, oauth_tokens, etc.) |
| `sessions.db` | `sessions` | 11 tables (threads, messages, etc.) |
| `synergy_sessions.db` | `synergy_sessions` | 2 tables (synergy_sessions, docs) |
| `kanban_analytics.db` | `kanban_analytics` | 14 tables (orders, clients, etc.) |
| `stock_data.db` | `stock_data` | 35 tables (StockLevels, extracted_jobs, etc.) |

**Total:** 78 tables (2 were added during migration for metadata)

---

## Best Practices

### 1. Always Use Schema-Qualified Names

```sql
-- GOOD:
SELECT * FROM sessions.threads

-- BAD:
SELECT * FROM threads  -- Which schema?
```

---

### 2. Use Parameterized Queries

```python
# GOOD (prevents SQL injection):
cursor.execute("SELECT * FROM sessions.threads WHERE id = %s", (thread_id,))

# BAD (SQL injection risk):
cursor.execute(f"SELECT * FROM sessions.threads WHERE id = {thread_id}")
```

---

### 3. Close Connections

```python
# GOOD:
conn = get_database_connection('sessions')
try:
    # Use connection
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM threads")
finally:
    conn.close()  # Always close

# BETTER (automatic cleanup):
with get_database_connection('sessions') as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM threads")
```

---

### 4. Test Queries Before Using in Code

```powershell
# Test query first:
python Supabase\supabase_toolkit.py query --query "SELECT COUNT(*) FROM sessions.threads WHERE user_id = 1"

# Then use in code:
cursor.execute("SELECT * FROM sessions.threads WHERE user_id = %s", (1,))
```

---

### 5. Monitor Query Performance

```sql
-- Use EXPLAIN to check query plan:
EXPLAIN SELECT * FROM sessions.threads WHERE user_id = 1;

-- Add indexes for slow queries:
CREATE INDEX idx_threads_user_id ON sessions.threads(user_id);
```

---

## Quick Reference Card

### Most Common Commands

```powershell
# Test connection
python Supabase\supabase_toolkit.py test

# View all schemas and tables
python Supabase\supabase_toolkit.py summary

# List tables in sessions schema
python Supabase\supabase_toolkit.py tables --schema sessions

# Get thread details
python Supabase\supabase_toolkit.py info --schema sessions --table threads

# Query threads
python Supabase\supabase_toolkit.py query --query "SELECT * FROM sessions.threads LIMIT 10"

# Compare local vs production
python data\show_database_structure_v2.py
```

---

### Useful Queries

```sql
-- Count all tables across all schemas
SELECT schemaname, COUNT(*) 
FROM pg_tables 
WHERE schemaname NOT IN ('pg_catalog', 'information_schema') 
GROUP BY schemaname;

-- List all indexes
SELECT schemaname, tablename, indexname 
FROM pg_indexes 
WHERE schemaname NOT IN ('pg_catalog', 'information_schema');

-- Get database size
SELECT pg_size_pretty(pg_database_size(current_database()));

-- Find large tables
SELECT schemaname, tablename, 
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) 
FROM pg_tables 
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC 
LIMIT 10;
```

---

## Next Steps

1. **Test all commands** - Run each command to familiarize yourself
2. **Update high-priority files** - See `SUPABASE_API_ASSESSMENT.md` for files needing updates
3. **Deploy to Render** - Add Supabase env vars and deploy
4. **Monitor performance** - Check Supabase Dashboard for slow queries
5. **Set up backups** - Configure Supabase automatic backups (already enabled on Free Tier)

---

## Resources

- **Supabase Dashboard:** https://supabase.com/dashboard/project/ryoicrdifiqhqpsnjmdo
- **PostgreSQL Docs:** https://www.postgresql.org/docs/
- **Supabase Docs:** https://supabase.com/docs
- **Migration Summary:** `SUPABASE_MIGRATION_SUMMARY.md`
- **API Assessment:** `SUPABASE_API_ASSESSMENT.md`

---

**Last Updated:** January 15, 2025  
**Status:** Production Ready  
**Version:** 2.0  
