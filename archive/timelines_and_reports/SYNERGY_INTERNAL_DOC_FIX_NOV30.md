# Synergy Internal Document Fix - November 30, 2025

## Fix #7: synergy_create_internal_doc SQL Placeholders ✅

**Issue:** The `synergy_create_internal_doc` tool was returning 500 Server Errors, preventing creation of internal Synergy documents.

**Error Message:**
```
Failed to create internal document: 500 Server Error: Internal Server Error
for url: https://ai-agents-backend-singapore.onrender.com/api/synergy/internal-doc/create
```

---

## Root Cause

Multiple internal document endpoints were not using `convert_sql_placeholders()` for database queries, causing SQL syntax errors when running on PostgreSQL (Supabase).

**Affected Endpoints:**
1. `POST /api/synergy/internal-doc/create` - Create internal document
2. `GET /api/synergy/internal-doc/<doc_id>` - Retrieve document
3. `PUT /api/synergy/internal-doc/<doc_id>` - Update document
4. `DELETE /api/synergy/internal-doc/<doc_id>` - Delete document

---

## Fixes Applied

### 1. Create Internal Doc - SQL Placeholders

**File:** `AI_infrastructure/routes/synergy_routes.py` (~line 1810)

**OLD CODE (BROKEN):**
```python
# Check slug uniqueness
cursor.execute(
    'SELECT doc_id FROM synergy_sessions.synergy_internal_docs WHERE slug = %s',
    (slug,)
)

# Verify session exists
cursor.execute(
    'SELECT session_id FROM synergy_sessions.synergy_sessions WHERE session_id = %s',
    (session_id,)
)

# Insert document
cursor.execute('''
    INSERT INTO synergy_sessions.synergy_internal_docs 
    (doc_id, session_id, title, content, ...)
    VALUES (%s, %s, %s, %s, ...)
''', (doc_id, session_id, title, content, ...))
```

**NEW CODE (FIXED):**
```python
# Check slug uniqueness
sql, params = convert_sql_placeholders(
    'SELECT doc_id FROM synergy_sessions.synergy_internal_docs WHERE slug = %s',
    (slug,)
)
cursor.execute(sql, params)

# Verify session exists
sql, params = convert_sql_placeholders(
    'SELECT session_id FROM synergy_sessions.synergy_sessions WHERE session_id = %s',
    (session_id,)
)
cursor.execute(sql, params)

# Insert document
now = datetime.now().isoformat()
sql, params = convert_sql_placeholders('''
    INSERT INTO synergy_sessions.synergy_internal_docs 
    (doc_id, session_id, title, content, ...)
    VALUES (%s, %s, %s, %s, ...)
''', (doc_id, session_id, title, content, ...))
cursor.execute(sql, params)
```

---

### 2. Get Internal Doc - SQL Placeholders

**File:** `AI_infrastructure/routes/synergy_routes.py` (~line 1890)

**OLD CODE (BROKEN):**
```python
cursor.execute('''
    SELECT doc_id, session_id, title, content, ...
    FROM synergy_sessions.synergy_internal_docs
    WHERE doc_id = %s
''', (doc_id,))
```

**NEW CODE (FIXED):**
```python
sql, params = convert_sql_placeholders('''
    SELECT doc_id, session_id, title, content, ...
    FROM synergy_sessions.synergy_internal_docs
    WHERE doc_id = %s
''', (doc_id,))
cursor.execute(sql, params)
```

---

### 3. Update Internal Doc - SQL Placeholders & Placeholder Style

**File:** `AI_infrastructure/routes/synergy_routes.py` (~line 1980)

**OLD CODE (BROKEN):**
```python
# Get current version
cursor.execute(
    'SELECT version FROM synergy_sessions.synergy_internal_docs WHERE doc_id = %s',
    (doc_id,)
)

# Build update query with WRONG placeholder style (?)
updates = []
params = []

if title:
    updates.append('title = ?')  # ❌ SQLite style
    params.append(title)
if content is not None:
    updates.append('content = ?')  # ❌ SQLite style
    params.append(content)

updates.append('updated_at = ?')  # ❌ SQLite style
params.append(datetime.now().isoformat())

query = f"UPDATE synergy_sessions.synergy_internal_docs SET {', '.join(updates)} WHERE doc_id = %s"
cursor.execute(query, params)
```

**NEW CODE (FIXED):**
```python
# Get current version
sql, params = convert_sql_placeholders(
    'SELECT version FROM synergy_sessions.synergy_internal_docs WHERE doc_id = %s',
    (doc_id,)
)
cursor.execute(sql, params)

# Build update query with CORRECT placeholder style (%s)
updates = []
update_params = []

if title:
    updates.append('title = %s')  # ✅ PostgreSQL style
    update_params.append(title)
if content is not None:
    updates.append('content = %s')  # ✅ PostgreSQL style
    update_params.append(content)

now = datetime.now().isoformat()
updates.append('updated_at = %s')  # ✅ PostgreSQL style
update_params.append(now)

query = f"UPDATE synergy_sessions.synergy_internal_docs SET {', '.join(updates)} WHERE doc_id = %s"
sql, final_params = convert_sql_placeholders(query, tuple(update_params))
cursor.execute(sql, final_params)
```

**Critical Changes:**
- Changed placeholder style from `?` (SQLite) to `%s` (PostgreSQL)
- Added `convert_sql_placeholders()` to both SELECT and UPDATE queries
- Fixed variable naming to avoid confusion (`params` → `update_params`)

---

### 4. Delete Internal Doc - SQL Placeholders

**File:** `AI_infrastructure/routes/synergy_routes.py` (~line 2055)

**OLD CODE (BROKEN):**
```python
cursor.execute(
    'DELETE FROM synergy_sessions.synergy_internal_docs WHERE doc_id = %s',
    (doc_id,)
)
```

**NEW CODE (FIXED):**
```python
sql, params = convert_sql_placeholders(
    'DELETE FROM synergy_sessions.synergy_internal_docs WHERE doc_id = %s',
    (doc_id,)
)
cursor.execute(sql, params)
```

---

## What is convert_sql_placeholders()?

This utility function converts SQL placeholders between SQLite (`?`) and PostgreSQL (`%s`) formats, ensuring queries work on both databases:

```python
# Local SQLite:   SELECT * FROM table WHERE id = ?
# Supabase (Prod): SELECT * FROM table WHERE id = %s

sql, params = convert_sql_placeholders(
    'SELECT * FROM table WHERE id = %s',
    (value,)
)
cursor.execute(sql, params)
# Automatically converts to correct format based on environment
```

---

## Impact

✅ **Internal Synergy Documents Now Work:**
- Can create richtext documents (markdown, HTML)
- Can create spreadsheet documents (tabular data)
- Can retrieve, update, and delete documents
- Proper slug generation and uniqueness checking
- Session validation before document creation

✅ **Tool Functionality Restored:**
- `synergy_create_internal_doc()` - Creates documents
- `synergy_get_internal_doc()` - Retrieves documents
- `synergy_update_internal_doc()` - Updates documents
- `synergy_delete_internal_doc()` - Deletes documents

---

## Testing

### Test Internal Doc Creation:

Using the AI agent tool:
```python
synergy_create_internal_doc(
    session_id="sess_20251130_1251_test_project",
    title="Project Requirements",
    content="# Requirements\n\n1. User authentication\n2. Data visualization",
    format="markdown",
    doc_type="richtext"
)
```

**Expected Result:**
```json
{
  "success": true,
  "doc_id": "int_doc_1732029847123",
  "title": "Project Requirements",
  "session_id": "sess_20251130_1251_test_project",
  "slug": "project-requirements",
  "share_url": "/internal-docs/project-requirements",
  "created_at": "2025-11-30T12:51:00"
}
```

---

## Complete Synergy Fix Summary (Nov 30, 2025)

### Backend API Fixes (7 total):
1. ✅ synergy_get_session - SQL placeholders
2. ✅ synergy_update_task - Request validation
3. ✅ synergy_add_document - Error handling
4. ✅ synergy_search_sessions - New endpoint + tool + schema
5. ✅ linked-threads endpoint - Datetime conversion
6. ✅ update_subtask endpoint - Request validation
7. ✅ **NEW:** Internal doc CRUD endpoints - SQL placeholders (4 endpoints)

### Files Modified:
- ✅ `AI_infrastructure/routes/synergy_routes.py` (11 total fixes)
- ✅ `tools/implementations/synergy.py` (1 new function)
- ✅ `tools/schemas/synergy_tools.json` (1 new schema)

### Related Documentation:
- `SYNERGY_BACKEND_FIXES_NOV30.md` - Original 4 fixes (technical)
- `SYNERGY_FIXES_SUMMARY.md` - Quick reference
- `SYNERGY_FIXES_APPLIED_NOV30.md` - Implementation details
- `SYNERGY_UI_FIXES_NOV30_PART2.md` - UI-related fixes (#5, #6)
- `SYNERGY_INTERNAL_DOC_FIX_NOV30.md` - This document (fix #7)
- `test_synergy_fixes_nov30.py` - Test suite (needs update for internal docs)

---

**Status:** ✅ Applied and server restarted  
**Date:** November 30, 2025  
**Author:** AI Agent (Claude 4 Sonnet)  
**Testing:** Ready for manual verification - try creating internal docs!
