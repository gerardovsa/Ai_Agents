# Supabase Quick Reference Card
**For AI Agents Platform - Production Database Management**

---

## Connection Info

```
Project: ai-agents-production-inhouse
URL: https://ryoicrdifiqhqpsnjmdo.supabase.co
Region: Singapore (ap-southeast-1)
Database: PostgreSQL 17.6
Size: 22 MB
```

---

## Most Used Commands

```powershell
# Test connection
python Supabase\supabase_toolkit.py test

# View all schemas and tables
python Supabase\supabase_toolkit.py summary

# List schemas
python Supabase\supabase_toolkit.py schemas

# List tables in schema
python Supabase\supabase_toolkit.py tables --schema sessions

# Get table details
python Supabase\supabase_toolkit.py info --schema sessions --table threads

# Execute query
python Supabase\supabase_toolkit.py query --query "SELECT * FROM sessions.threads LIMIT 10"

# Compare local vs production
python data\show_database_structure_v2.py
```

---

## Schema Mappings

| SQLite Database | Supabase Schema | Tables |
|----------------|----------------|--------|
| `ai_infrastructure.db` | `ai_infrastructure` | 16 |
| `sessions.db` | `sessions` | 11 |
| `synergy_sessions.db` | `synergy_sessions` | 2 |
| `kanban_analytics.db` | `kanban_analytics` | 14 |
| `stock_data.db` | `stock_data` | 35 |

---

## Common Queries

```sql
-- Count threads
SELECT COUNT(*) FROM sessions.threads;

-- Get user threads
SELECT id, name, created_at 
FROM sessions.threads 
WHERE user_id = 1 
ORDER BY created_at DESC LIMIT 10;

-- Check OAuth connections
SELECT user_id, platform, email, created_at 
FROM ai_infrastructure.user_platform_credentials 
ORDER BY created_at DESC;

-- Count messages in thread
SELECT COUNT(*) 
FROM sessions.messages 
WHERE thread_id = 1;

-- Get recent orders
SELECT order_id, customer_name, order_date, status 
FROM kanban_analytics.orders 
ORDER BY order_date DESC LIMIT 10;

-- Check stock levels
SELECT "StockName", "CurrentQuantity", "MinLevel" 
FROM stock_data."StockLevels" 
WHERE "CurrentQuantity" < "MinLevel";
```

---

## Environment Variables

**Local Development (SQLite):**
```bash
USE_SUPABASE=false  # or not set
```

**Production (Supabase):**
```bash
USE_SUPABASE=true
RENDER=true
SUPABASE_URL=https://ryoicrdifiqhqpsnjmdo.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGci...
SUPABASE_DB_URL=postgresql://postgres:***@db.ryoicrdifiqhqpsnjmdo.supabase.co:5432/postgres
```

---

## In Python Code

```python
# Use centralized database utility (RECOMMENDED)
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'AI_infrastructure'))
from shared.database_utils import get_database_connection

# Auto-detects SQLite vs Supabase
conn = get_database_connection('sessions')
cursor = conn.cursor()

# Works with both SQLite and PostgreSQL
cursor.execute("SELECT * FROM threads WHERE user_id = %s", (1,))

# Always close
conn.close()
```

---

## Troubleshooting

**Connection refused:**
- Check Supabase project is active (not paused)
- Verify SUPABASE_DB_URL in .env.master
- Test: `python Supabase\test_supabase_connection.py`

**"relation does not exist":**
- Use schema-qualified names: `sessions.threads` not `threads`
- Check schema exists: `python Supabase\supabase_toolkit.py schemas`

**"column does not exist":**
- PostgreSQL is case-sensitive
- Use double quotes for mixed case: `"StockName"` not `stockname`

**Authentication failed:**
- Use SUPABASE_SERVICE_KEY (not anon key)
- Check key in Supabase Dashboard → Settings → API

---

## Files Still Needing Update

**HIGH PRIORITY (3 files - 30 min):**
- `AI_infrastructure/flask_app.py` (Line 153)
- `AI_infrastructure/routes/microsoft_auth_routes_V2_FIXED.py` (Line 100)
- `google_workspace/oauth_credential_loader.py` (Line 45)

**MEDIUM PRIORITY (7 files - 2 hours):**
- `AI_infrastructure/utils/email_alias_helpers.py` (6 occurrences)
- `AI_infrastructure/utils/user_context_builder.py` (1 occurrence)
- `AI_infrastructure/workspace/` files (3 files)
- `tools/implementations/memory_tools.py` (1 occurrence)

**See SUPABASE_API_ASSESSMENT.md for details**

---

## Resources

- **CLI Guide:** `SUPABASE_CLI_GUIDE.md` (900+ lines)
- **API Assessment:** `SUPABASE_API_ASSESSMENT.md` (800+ lines)
- **Database Analyzer:** `data/show_database_structure_v2.py`
- **Migration Summary:** `SUPABASE_MIGRATION_SUMMARY.md`
- **Completion Report:** `SUPABASE_TOOLS_COMPLETE.md`

---

## Supabase Dashboard

**URL:** https://supabase.com/dashboard/project/ryoicrdifiqhqpsnjmdo

**Sections:**
- **Table Editor** - Browse and edit data
- **SQL Editor** - Execute queries
- **Database** - Manage schemas and tables
- **Settings → API** - Get connection credentials

---

**Last Updated:** January 15, 2025
