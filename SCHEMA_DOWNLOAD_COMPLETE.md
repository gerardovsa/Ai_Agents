# Database Schema Download - Complete ✅

**Date:** November 8, 2025
**Purpose:** Extract all database schemas for AI agent reference during code analysis

---

## What Was Generated

### 1. **DATABASE_SCHEMAS.json** (Complete Machine-Readable)
- Full schema export in JSON format
- Includes all tables, columns, indexes, data types
- Contains sample data (first 3 rows per table)
- **Size:** ~200KB
- **Use case:** Programmatic schema validation, automated checks

**Structure:**
```json
{
  "extracted_at": "2025-11-08T20:00:03",
  "databases": {
    "sessions.db": {
      "tables": {
        "threads": {
          "columns": [...],
          "indexes": [...],
          "sample_data": [...]
        }
      }
    }
  }
}
```

---

### 2. **DATABASE_SCHEMAS.md** (Complete Human-Readable)
- Full schema documentation in Markdown
- 1,697 lines of detailed schema information
- Formatted tables with column details
- Sample data in JSON blocks
- **Use case:** Manual reference, documentation

**Contents:**
- All 3 databases (sessions.db, ai_infrastructure.db, synergy_sessions.db)
- 26 total tables
- Full column definitions with types, nullability, defaults
- Index information
- Sample data for each table

---

### 3. **DATABASE_SCHEMAS_SUMMARY.md** (Quick Reference)
- Condensed version with key information
- Focus on most-used tables and patterns
- Common code patterns included
- Critical insights highlighted
- **Use case:** Quick lookup during code analysis

**Key Sections:**
- Thread Assignment Storage (CRITICAL)
- Common Tables (threads, messages, users)
- OAuth Tables
- Code Patterns
- Common Mistakes

---

### 4. **validate_code_against_schemas.py** (Validation Tool)
- Python script to check code against schemas
- Validates SQL queries in Python files
- Checks for invalid column/table references
- Detects deprecated database paths
- **Use case:** Pre-commit validation, code review

**Features:**
- Extracts SQL from Python files
- Validates table names
- Validates column names
- Checks database paths
- Reports errors and warnings

---

## Database Statistics

### sessions.db
- **Location:** `C:\Users\gpoli\GIT\AI_agents\data\sessions.db`
- **Tables:** 8
- **Total Rows:** 650
- **Key Tables:**
  - `threads` (20 rows) - Conversation threads
  - `messages` (460 rows) - Individual messages
  - `users` (2 rows) - User accounts with metadata
  - `workspaces` (1 row) - Workspace definitions
  - `sessions` (160 rows) - Session tracking

### ai_infrastructure.db
- **Location:** `C:\Users\gpoli\GIT\AI_agents\data\ai_infrastructure.db`
- **Tables:** 16
- **Total Rows:** 385
- **Key Tables:**
  - `user_sessions` (338 rows) - Login sessions
  - `oauth_tokens` (5 rows) - OAuth credentials
  - `user_platform_credentials` (2 rows) - Platform credentials
  - `thread_assignments` (0 rows) - **EMPTY - Legacy table**
  - `users` (6 rows) - User accounts
  - `workspaces` (3 rows) - Workspace definitions

### synergy_sessions.db
- **Location:** `C:\Users\gpoli\GIT\AI_agents\data\synergy_sessions.db`
- **Tables:** 2
- **Total Rows:** 20
- **Key Tables:**
  - `synergy_sessions` (15 rows) - Multi-agent sessions
  - `sessions` (5 rows) - Session tracking

---

## Critical Findings

### 1. Thread Assignment Storage Architecture ⚠️

**IMPORTANT DISCOVERY:** Thread assignments are stored in **TWO DIFFERENT WAYS**:

#### **Current System (ACTIVE):**
- **Location:** `sessions.db` → `users` table → `metadata` column
- **Format:** JSON string
- **Structure:** `{"thread_assignments": {"agent-1": "session_id", ...}}`
- **Status:** ✅ ACTIVELY USED
- **Used by:** All `/api/thread-assignments/*` endpoints

**Example:**
```json
{
  "id": 1,
  "username": "default_user",
  "metadata": "{\"thread_assignments\": {\"agent-2\": \"1762411564661\"}}"
}
```

#### **Legacy Table (INACTIVE):**
- **Location:** `ai_infrastructure.db` → `thread_assignments` table
- **Status:** ⚠️ EMPTY (0 rows)
- **Conclusion:** Table exists but is NOT used
- **Code references:** Some comments mention it but actual code uses `users.metadata`

**Recommendation:** Remove references to `thread_assignments` table to avoid confusion.

---

### 2. Database Path Patterns

**CORRECT Paths:**
```python
# ✅ CORRECT - Use data/ folder
root_dir / 'data' / 'sessions.db'
root_dir / 'data' / 'ai_infrastructure.db'
```

**DEPRECATED Paths (Found in some files):**
```python
# ❌ WRONG - Old paths
'AI_infrastructure/ai_infrastructure.db'
'../ai_infrastructure.db'
```

---

### 3. Data Type Patterns

**Thread IDs:**
- Format: String timestamps (e.g., "1762411564661")
- NOT integers
- Generated: `str(int(datetime.now().timestamp() * 1000))`

**Metadata Columns:**
- Type: TEXT (JSON strings)
- Require: `json.loads()` to parse
- Common in: `users.metadata`, `threads.metadata`, `messages.metadata`

**Locations:**
- Values: 'prime', 'agent-1', 'agent-2', 'agent-3', etc.
- NOT: 'agent-1 ' (with trailing space) ← **Fixed this bug today!**

---

### 4. Index Coverage

**Well-Indexed:**
- ✅ `threads.thread_slug` (UNIQUE)
- ✅ `threads.user_id`
- ✅ `messages.session_id`
- ✅ `messages.thread_id`
- ✅ `users.username` (UNIQUE)

**Missing Indexes:** None critical found

---

## Common Code Patterns (For Reference)

### Fetch Thread Assignments
```python
# From sessions.db users.metadata
conn = sqlite3.connect('data/sessions.db')
cursor = conn.cursor()
cursor.execute("SELECT metadata FROM users WHERE id = ?", [user_id])
row = cursor.fetchone()
metadata = json.loads(row['metadata'] or '{}')
assignments = metadata.get('thread_assignments', {})
# Result: {"agent-1": "1762411564661", "agent-2": "1762525766686"}
```

### Update Thread Assignments
```python
# Update users.metadata JSON
cursor.execute("SELECT metadata FROM users WHERE id = ?", [user_id])
row = cursor.fetchone()
metadata = json.loads(row['metadata'] or '{}')

# Modify assignments
metadata['thread_assignments'] = {
    'agent-1': '1762411564661',
    'agent-2': '1762525766686'
}

# Save back
cursor.execute(
    "UPDATE users SET metadata = ?, last_active = CURRENT_TIMESTAMP WHERE id = ?",
    [json.dumps(metadata), user_id]
)
conn.commit()
```

### Get Thread with Messages
```python
# Join threads and messages
cursor.execute("""
    SELECT 
        t.*,
        COUNT(m.id) as message_count,
        MAX(m.created_at) as last_message_at
    FROM threads t
    LEFT JOIN messages m ON t.id = m.thread_id
    WHERE t.thread_slug = ?
    GROUP BY t.id
""", [thread_slug])
```

### Check OAuth Token
```python
# From ai_infrastructure.db
conn = sqlite3.connect('data/ai_infrastructure.db')
cursor = conn.cursor()
cursor.execute("""
    SELECT access_token, refresh_token, token_expiry
    FROM oauth_tokens
    WHERE user_id = ? AND platform = ?
    ORDER BY created_at DESC
    LIMIT 1
""", [user_id, 'google'])
```

---

## Usage for AI Agent

When analyzing code, I now have:

1. **Complete table structures** - No guessing about column names
2. **Data types** - Know what each column expects
3. **Indexes** - Understand query performance implications
4. **Sample data** - See actual data format and patterns
5. **Validation tool** - Can check code against actual schemas

### Example Analysis Process:

```
User: "Why is thread assignment not working?"

AI Agent (Me):
1. Check DATABASE_SCHEMAS_SUMMARY.md → Thread Assignment section
2. See: Assignments stored in users.metadata JSON, NOT thread_assignments table
3. Verify: Check code references thread_assignments table? → Bug found!
4. Fix: Update code to use users.metadata
5. Validate: Run validate_code_against_schemas.py
```

---

## Files Created

| File | Size | Purpose | Use When |
|------|------|---------|----------|
| `DATABASE_SCHEMAS.json` | ~200KB | Machine-readable full export | Automated validation |
| `DATABASE_SCHEMAS.md` | 1,697 lines | Human-readable full docs | Detailed reference |
| `DATABASE_SCHEMAS_SUMMARY.md` | ~500 lines | Quick reference guide | Quick lookups |
| `validate_code_against_schemas.py` | ~350 lines | Validation tool | Pre-commit checks |
| `get_all_database_schemas.py` | ~350 lines | Schema extraction tool | Re-generate schemas |

---

## Next Steps

### For User:
- ✅ Schemas extracted and documented
- ✅ Validation tool created
- ✅ Can reference schemas during code review
- 📌 Consider running validator pre-commit

### For AI Agent (Me):
- ✅ Have complete database context
- ✅ Can cross-check code against schemas
- ✅ Can identify schema mismatches
- ✅ Can suggest proper query patterns
- 📌 Reference DATABASE_SCHEMAS_SUMMARY.md during analysis

---

## Validation Results

Ran initial validation on `thread_routes.py`:
- ✅ No critical errors found
- ⚠️ 5 warnings (false positives from SQL in comments)
- ✅ All table references valid
- ✅ All column references valid

---

## Key Insights for Future Development

1. **Thread assignments use JSON storage** - Simple, flexible, no migrations needed
2. **Thread IDs are strings** - Always use string comparisons, never int
3. **Three databases exist** - Know which database to query for what
4. **Metadata is JSON** - Always parse with `json.loads()`
5. **Indexes exist** - Use them in WHERE clauses for performance
6. **OAuth in separate DB** - `ai_infrastructure.db`, not `sessions.db`

---

**Status:** ✅ COMPLETE - All schemas extracted and documented
**Generated:** November 8, 2025
**By:** AI Agent (Claude) + get_all_database_schemas.py
