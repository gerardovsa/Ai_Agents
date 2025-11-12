# System Analyzer - Quick Reference Guide

## Run the Analyzer

```powershell
cd C:\Users\gpoli\GIT\AI_agents\data
python show_database_structure.py
```

## What You'll See

### 1. Database Structure (First Section)
- All tables in each database
- Column names, types, constraints
- Row counts
- Foreign key relationships

**Use for:** Understanding data schema, planning migrations

### 2. Script Analysis (Second Section)
- Which Python files access databases
- Line numbers of database connections
- Tables accessed by each script

**Use for:** Finding which scripts to update when changing database

### 3. API Route Mapping (Third Section)
- API endpoints grouped by database
- Tables accessed by each endpoint

**Use for:** Understanding API data flow, debugging API issues

### 4. Inconsistency Report (Fourth Section)
- Missing databases
- Missing tables
- Incorrect paths
- API connection issues

**Use for:** Finding and fixing errors

### 5. UI Data Mapping (Fifth Section)
- Where UI components get data from
- API endpoints for each UI element
- Key fields used

**Use for:** Building new UI features, debugging frontend

### 6. Debugging Guide (Sixth Section)
- Common errors and solutions
- Code examples (BAD vs GOOD)

**Use for:** Fixing database errors quickly

## Quick Problem Solving

### "Table not found" Error
1. Run script
2. Check Database Structure section
3. Find correct table name
4. Update your query

### "Database locked" Error
1. Check Script Analysis for unclosed connections
2. Add `finally: conn.close()`
3. Use `with sqlite3.connect() as conn:`

### API Returns Empty Data
1. Check Database Structure for row count
2. Check API Route Mapping for your endpoint
3. Verify database connection in your route

### Foreign Key Constraint Failed
1. Check Database Structure → Foreign Keys
2. Verify parent record exists
3. Enable foreign keys: `PRAGMA foreign_keys = ON`

### Wrong Database Path
1. Check Inconsistency Report → INCORRECT_PATH
2. Change from `AI_infrastructure/*.db`
3. Change to `data/*.db`

## Common Use Cases

### Building New UI Feature
```
1. Run script
2. Check Database Structure → Find relevant tables
3. Check API Route Mapping → Find existing endpoints
4. Check UI Data Mapping → See similar patterns
5. Build your feature using same approach
```

### Adding New Database Column
```
1. Run script
2. Check Script Analysis → See which files use that table
3. Check API Route Mapping → See which endpoints use it
4. Add column
5. Update all those files
```

### Debugging Database Error
```
1. Run script
2. Check Inconsistency Report for your file
3. Follow suggested fix
4. Verify with Database Structure section
```

### Finding Orphaned Tables
```
1. Run script
2. Check Database Structure → Find tables with 0 rows
3. Check Script Analysis → See if any files use it
4. Check API Route Mapping → See if any endpoints use it
5. Delete or repurpose table
```

## Key Databases

### sessions.db
- **Tables:** threads, messages, thread_assignments
- **Purpose:** Chat conversations and thread management
- **Location:** `data/sessions.db`

### ai_infrastructure.db
- **Tables:** users, oauth_tokens, user_platform_credentials
- **Purpose:** User accounts and OAuth credentials
- **Location:** `data/ai_infrastructure.db`

### synergy_sessions.db
- **Tables:** synergy_sessions
- **Purpose:** Synergy dashboard multi-thread sessions
- **Location:** `data/synergy_sessions.db`

### g_folder.db
- **Tables:** 30+ tables (extracted_jobs, shopify_orders, unified_stocks, etc.)
- **Purpose:** InHouse Print quotes and orders
- **Location:** `data/g_folder.db`

## Correct Database Path Pattern

```python
# ✅ CORRECT
from pathlib import Path
root_dir = Path(__file__).parent.parent.parent
db_path = root_dir / 'data' / 'sessions.db'
conn = sqlite3.connect(str(db_path))

# ❌ WRONG
conn = sqlite3.connect('AI_infrastructure/sessions.db')
conn = sqlite3.connect('../sessions.db')
```

## When to Run This Script

- ✅ Before deploying to production
- ✅ After adding new tables or columns
- ✅ When building new UI features
- ✅ When debugging database errors
- ✅ Weekly system health check
- ✅ After major refactoring
- ✅ When onboarding new developers

## Understanding Issue Counts

The script may report thousands of "issues" - **most are false positives**.

**False Positives (Ignore These):**
```
ERROR: References non-existent table: pathlib
ERROR: References non-existent table: datetime
ERROR: References non-existent table: typing
```
→ These are Python imports, not SQL tables.

**Real Issues (Fix These):**
```
ERROR: References non-existent database: old_sessions.db
ERROR: References non-existent table: archived_users
ERROR: Should use data/ folder: AI_infrastructure/ai_infrastructure.db
```
→ These are actual problems that need fixing.

## Output File Location

The script prints to console. To save output:

```powershell
python show_database_structure.py > output.txt
```

Then open `output.txt` to review at your leisure.

## Quick Stats (Current System)

```
Databases:   4 databases analyzed
Scripts:     515 Python files scanned
API Routes:  154 endpoints mapped
Tables:      38 total tables across all databases
```

## Most Useful Sections

### For Developers:
1. **Database Structure** - See all tables and columns
2. **Script Analysis** - Find which files to update
3. **Inconsistency Report** - Fix errors

### For Frontend Developers:
1. **UI Data Mapping** - See where data comes from
2. **API Route Mapping** - Find correct endpoints
3. **Database Structure** - Understand data schema

### For DevOps/QA:
1. **Inconsistency Report** - Find problems
2. **Script Analysis** - Validate all connections
3. **System Health** - Overall status

## Need More Details?

See full documentation: `SYSTEM_ANALYZER_DOCUMENTATION.md`

## Common Commands

```powershell
# Run analyzer
cd C:\Users\gpoli\GIT\AI_agents\data; python show_database_structure.py

# Save output to file
cd C:\Users\gpoli\GIT\AI_agents\data; python show_database_structure.py > analysis.txt

# Check specific database
sqlite3 data/sessions.db ".tables"
sqlite3 data/sessions.db ".schema threads"

# Verify database location
ls C:\Users\gpoli\GIT\AI_agents\data\*.db
```

## Tips

1. **Run before and after changes** to see what changed
2. **Focus on HIGH severity** issues only
3. **Share output** with team for onboarding
4. **Keep a copy** of output for documentation
5. **Check weekly** for system health monitoring

---

**Last Updated:** November 10, 2025  
**Version:** 1.0  
**Status:** Production Ready
