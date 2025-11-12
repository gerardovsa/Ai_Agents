# System Database & Script Analyzer Documentation

## Overview

The `show_database_structure.py` script is a comprehensive analysis tool that:

1. **Analyzes ALL databases** (sessions.db, ai_infrastructure.db, synergy_sessions.db, g_folder.db)
2. **Scans ALL Python scripts** (515 scripts found with database access)
3. **Maps API routes to databases** (154 API endpoints analyzed)
4. **Detects inconsistencies** (missing databases, incorrect paths, orphaned tables)
5. **Provides debugging guides** for common errors
6. **Maps UI elements** to data sources

## Usage

### Run Complete Analysis

```powershell
cd C:\Users\gpoli\GIT\AI_agents\data
python show_database_structure.py
```

This will:
- Analyze all 4 databases
- Scan 515+ Python files
- Check 154 API routes
- Generate comprehensive report
- Print results to console

### Output

The script provides:

1. **Database Structure** - All tables, columns, types, constraints, row counts
2. **Script Analysis** - Which Python files access which databases
3. **API Route Mapping** - Which endpoints use which databases
4. **Inconsistency Report** - Problems found (missing tables, wrong paths, etc.)
5. **UI Data Mapping** - Where frontend gets data from
6. **Debugging Guide** - Solutions for common issues

## What It Finds

### 1. Database Information

For each database:
- Location path
- File size
- All tables
- All columns (name, type, NOT NULL, PRIMARY KEY)
- Row counts
- Foreign key relationships

**Example Output:**
```
DATABASE: sessions.db
Location: C:\Users\gpoli\GIT\AI_agents\data\sessions.db
Size: 49,152 bytes
Tables: 3

  TABLE: threads - 8 rows
    thread_id               INTEGER      [PK]
    thread_slug             TEXT         [NOT NULL]
    title                   TEXT
    last_message_timestamp  TIMESTAMP
    
  Foreign Keys:
    None
```

### 2. Script Database Access

For each Python file:
- Full path
- Line count
- Database connections (with line numbers)
- Tables accessed
- SQL queries found

**Example Output:**
```
DIRECTORY: AI_infrastructure/routes

  FILE: agent_routes_v4.py (2148 lines)
  Database Connections:
    Line 45: data/sessions.db
    Line 67: data/ai_infrastructure.db
  Tables: threads, messages, users
```

### 3. API Route Mapping

For each API endpoint:
- Endpoint path
- File location
- Databases accessed
- Tables used

**Example Output:**
```
DATABASE: sessions.db

  /api/threads                     Tables: threads, thread_assignments
  /api/threads/<slug>/messages     Tables: messages, threads
  /api/thread-assignments/assign   Tables: thread_assignments
```

### 4. Inconsistency Detection

**TYPES OF ISSUES FOUND:**

#### HIGH SEVERITY:
- **MISSING_DATABASE**: Script references database that doesn't exist
- **MISSING_TABLE**: Query uses table that doesn't exist
- **BROKEN_CONNECTION**: Database file not found

#### MEDIUM SEVERITY:
- **INCORRECT_PATH**: Using old path (AI_infrastructure/*.db instead of data/*.db)
- **API_NO_DATABASE**: API route queries tables but no DB connection found

**Example Output:**
```
HIGH SEVERITY (2 issues)

  MISSING_DATABASE (1 issue):
    ERROR: References non-existent database: old_sessions.db
    File: scripts/migrate_data.py
    Line: 23
    Database: old_sessions.db

  MISSING_TABLE (1 issue):
    ERROR: References non-existent table: archived_users
    File: AI_infrastructure/routes/admin_routes.py
    Table: archived_users
```

### 5. UI Element Data Mapping

Shows where each UI component gets its data:

```
1. THREAD LIST (Left Sidebar)
   Data Source: sessions.db.threads
   API: GET /api/threads
   Key Fields: thread_slug, last_agent_location, last_message_timestamp

2. MESSAGE HISTORY (Chat Area)
   Data Source: sessions.db.messages
   API: GET /api/threads/<thread_slug>/messages
   Key Fields: role, content, timestamp, tool_calls
```

### 6. Debugging Guide

Provides solutions for common problems:

```
ISSUE: "Table not found" error

DIAGNOSIS:
1. Check database connection path (should be data/xxx.db)
2. Run this script to see all tables
3. Check spelling and case sensitivity

FIX:
- BAD:  conn = sqlite3.connect('AI_infrastructure/ai_infrastructure.db')
- GOOD: conn = sqlite3.connect('data/ai_infrastructure.db')
```

## Use Cases

### 1. Creating New UI Elements

**Scenario:** You want to add a "Recent Tasks" widget to the dashboard.

**Steps:**
1. Run the script to see all tables
2. Check `Database Structure` section for relevant tables
3. Check `API Route Mapping` to find existing API that accesses that table
4. Check `UI Element Data Mapping` for similar components
5. Create your UI element using the same patterns

**Example:**
```
# Found in output:
TABLE: synergy_sessions - 15 rows
  session_id, title, description, status, created_at

# Found in API mapping:
GET /api/synergy/sessions → synergy_sessions.db

# Create UI:
fetch('/api/synergy/sessions')
  .then(r => r.json())
  .then(sessions => displayRecentTasks(sessions))
```

### 2. Debugging Database Errors

**Scenario:** Getting "table not found" error in your script.

**Steps:**
1. Run the script
2. Check `Database Structure` for the table name
3. Check `Script Analysis` section for your script
4. Compare table name in error with actual table name
5. Check database connection path

**Example:**
```
# Error: sqlite3.OperationalError: no such table: user_permissions

# Run script, check Database Structure:
DATABASE: ai_infrastructure.db
  TABLE: users (not user_permissions!)

# Fix: Change query from user_permissions to users
```

### 3. Fixing Incorrect Database Paths

**Scenario:** Script fails with "database not found" error.

**Steps:**
1. Run the script
2. Check `Inconsistency Report` → `INCORRECT_PATH` section
3. See which files use wrong paths
4. Update to use data/ folder

**Example:**
```
# Found in Inconsistency Report:
INCORRECT_PATH (5 issues)
  File: scripts/old_migrator.py
  Line: 12
  Path: AI_infrastructure/ai_infrastructure.db
  
# Fix:
- OLD: conn = sqlite3.connect('AI_infrastructure/ai_infrastructure.db')
- NEW: conn = sqlite3.connect('data/ai_infrastructure.db')
```

### 4. Validating API Implementation

**Scenario:** Built new API endpoint, want to verify it's connecting correctly.

**Steps:**
1. Run the script
2. Check `API Route Mapping` section
3. Find your endpoint
4. Verify it shows the correct database and tables
5. Check for "ROUTES WITHOUT EXPLICIT DATABASE" section

**Example:**
```
# Your endpoint: POST /api/users/sub-users
# Should connect to: ai_infrastructure.db.users

# Check output:
DATABASE: ai_infrastructure.db
  /api/users/sub-users    Tables: users

# ✅ Correct! API is properly mapped.
```

### 5. Planning Database Migrations

**Scenario:** Need to add new columns or tables.

**Steps:**
1. Run the script
2. Check `Database Structure` to see current schema
3. Check `Script Analysis` to see which files access those tables
4. Check `API Route Mapping` to see which endpoints use those tables
5. Plan migration carefully

**Example:**
```
# Want to add 'last_login' column to users table

# Check Database Structure:
TABLE: users - 6 rows
  id, username, email, password_hash, created_at

# Check Script Analysis:
Files accessing users: 23 files found
  - AI_infrastructure/routes/auth_routes.py
  - AI_infrastructure/auth/user_auth.py
  - AI_infrastructure/utils/user_context_builder.py
  
# Check API Route Mapping:
Endpoints using users:
  - POST /api/auth/login
  - GET /api/auth/me
  - POST /api/auth/register

# Plan: Add column, update 23 files, test 3 endpoints
```

### 6. Detecting Orphaned Code

**Scenario:** Want to find unused database tables or scripts.

**Steps:**
1. Run the script
2. Check `Database Structure` for tables with 0 rows
3. Check `Script Analysis` to see which files access each table
4. Check `API Route Mapping` to see which endpoints use each table
5. Identify tables with no usage

**Example:**
```
# Found in Database Structure:
TABLE: shopify_webhook_events - 0 rows
TABLE: custom_events - 0 rows
TABLE: shopify_analytics_cache - 0 rows

# Check Script Analysis:
Files accessing shopify_webhook_events: 1 file
  - g_folder/shopify_webhook_handler.py (never called)

# Conclusion: Table is unused, can be removed or repurposed
```

### 7. Troubleshooting Foreign Key Issues

**Scenario:** Getting "foreign key constraint failed" error.

**Steps:**
1. Run the script
2. Check `Database Structure` → Foreign Keys section
3. Identify the constraint
4. Verify parent record exists

**Example:**
```
# Error: FOREIGN KEY constraint failed

# Check Database Structure:
TABLE: messages
  Foreign Keys:
    thread_id → threads.id

# Debug:
1. Check if thread exists: SELECT * FROM threads WHERE id = X
2. Check if foreign keys enabled: PRAGMA foreign_keys = ON
3. Insert parent first, then child
```

## Advanced Features

### Custom Analysis

You can modify the script to:

1. **Filter by directory**: Only analyze specific folders
2. **Check specific databases**: Skip some databases
3. **Export to JSON**: Save results for programmatic processing
4. **Compare schemas**: Track schema changes over time

### Integration with CI/CD

Run as pre-commit hook to:
- Detect broken database references before commit
- Validate API endpoints are properly connected
- Check for incorrect database paths
- Ensure foreign key relationships are valid

**Example `.git/hooks/pre-commit`:**
```bash
#!/bin/bash
cd data
python show_database_structure.py | grep "HIGH SEVERITY"
if [ $? -eq 0 ]; then
    echo "ERROR: High severity database issues found!"
    exit 1
fi
```

## Understanding the Output

### What's a "False Positive"?

The script detects some "missing tables" that are actually Python imports:

```
ERROR: References non-existent table: pathlib
ERROR: References non-existent table: datetime
```

These are **NOT real issues**. They're Python imports being detected as SQL table names. You can safely ignore these.

### Real Issues to Fix

Look for:
```
ERROR: References non-existent database: old_sessions.db
  → FIX: Update connection path

ERROR: References non-existent table: archived_users
  → FIX: Create table or fix query

ERROR: Should use data/ folder: AI_infrastructure/ai_infrastructure.db
  → FIX: Change path to data/ai_infrastructure.db
```

## Maintenance

### When to Run This Script

Run the script when:
- ✅ Adding new database tables
- ✅ Creating new API endpoints
- ✅ Building new UI features
- ✅ Debugging database errors
- ✅ Before deploying to production
- ✅ After major refactoring
- ✅ When onboarding new developers

### Keeping It Updated

The script automatically detects:
- New databases in `data/` folder
- New Python files with database access
- New API routes in `AI_infrastructure/routes/`
- Schema changes in existing databases

No manual updates needed!

## Output Statistics (Current System)

```
Databases analyzed:     4
  - sessions.db:        3 tables, 8 threads, 34 messages
  - ai_infrastructure:  4 tables, 6 users, 12 OAuth tokens
  - synergy_sessions:   1 table, 15 sessions
  - g_folder:          30 tables (InHouse Print data)

Scripts analyzed:       515 Python files with database access
API routes found:       154 endpoints mapped to databases
Issues detected:        2,451 (mostly false positives from imports)
Real issues:            ~10-20 (need manual review)
```

## Tips for Best Results

1. **Run regularly** - Weekly or after major changes
2. **Focus on HIGH severity** - These are real problems
3. **Ignore import "tables"** - pathlib, datetime, etc. are not real tables
4. **Check new files** - Always validate new scripts with this tool
5. **Use for documentation** - Share output with team for onboarding
6. **Export results** - Redirect output to file for later reference

## Troubleshooting the Script Itself

### Script Won't Run

```powershell
# Check Python version
python --version  # Should be 3.8+

# Check dependencies
pip install sqlite3  # (usually built-in)
```

### Script Crashes

```python
# Add debug mode (in script):
import traceback
try:
    main()
except Exception as e:
    traceback.print_exc()
```

### No Databases Found

```powershell
# Verify you're in correct directory
cd C:\Users\gpoli\GIT\AI_agents\data
ls *.db

# Should see: sessions.db, ai_infrastructure.db, synergy_sessions.db, g_folder.db
```

## Future Enhancements

Planned features:
- [ ] JSON export mode
- [ ] HTML report generation
- [ ] Schema comparison (before/after)
- [ ] Automatic fix suggestions
- [ ] Integration with Flask /admin dashboard
- [ ] Real-time monitoring mode
- [ ] Performance analysis (slow queries)
- [ ] Data consistency checks (orphaned records)

## Support

For issues or questions:
1. Check this documentation
2. Review the script output carefully
3. Look at `Debugging Guide` section in output
4. Check `Inconsistency Report` for specific errors

## Version History

- **v1.0** (Nov 10, 2025) - Initial release
  - Database structure analysis
  - Script scanning
  - API route mapping
  - Inconsistency detection
  - UI data mapping
  - Debugging guide

## License

Internal tool for AI Agents Platform project. All rights reserved.
