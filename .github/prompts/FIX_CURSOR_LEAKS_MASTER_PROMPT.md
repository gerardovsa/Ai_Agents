# Fix Cursor Leaks - Master Prompt for AI Refactoring

## Context
You are refactoring Python Flask route files that have **cursor leak issues**. These files use PostgreSQL connections via psycopg2 with connection pooling, but cursors are not being properly closed, causing resource exhaustion and 500 errors.

## The Problem
**Current (BAD) Pattern:**
```python
with get_database_connection('schema_name') as conn:
    cursor = conn.cursor()  # ❌ Cursor never closed!
    
    cursor.execute("SELECT * FROM table")
    rows = cursor.fetchall()
    
    return jsonify(rows)
```

**Why this is bad:**
- Cursor remains open even after function returns
- Leads to resource exhaustion (245+ cursor leaks found across 36 files)
- Causes connection pool exhaustion
- Results in 500 Internal Server Errors under load

## The Solution
**Fixed (GOOD) Pattern:**
```python
with get_database_connection('schema_name') as conn:
    with conn.cursor() as cursor:  # ✅ Cursor auto-closed!
        
        cursor.execute("SELECT * FROM table")
        rows = cursor.fetchall()
        
        return jsonify(rows)
```

## Critical Rules

### ✅ DO:
1. **Always use nested context managers** for cursors:
   ```python
   with conn.cursor() as cursor:
   ```

2. **Indent ALL cursor operations** inside the `with cursor:` block (add 4 spaces)

3. **Preserve exact SQL queries** - don't change any SQL logic

4. **Keep all business logic** - only change cursor management

5. **Maintain error handling** - keep try/except blocks intact

6. **Test after changes** - file must pass `python -m py_compile`

### ❌ DON'T:
1. **Never leave `cursor = conn.cursor()` without `with`**

2. **Don't remove manual `cursor.close()` calls** - context manager makes them redundant, but removing them won't break anything

3. **Don't change function signatures, return statements, or SQL queries**

4. **Don't mix patterns** - convert ALL cursors in a function, not just some

5. **Don't create syntax errors** - indentation must be perfect

## Step-by-Step Refactoring Process

### Step 1: Identify All Cursor Patterns
Search for:
```python
cursor = conn.cursor()
```

### Step 2: Replace Each Instance
**BEFORE:**
```python
with get_database_connection('ai_infrastructure') as conn:
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    
    if not user:
        return error_response('User not found', 404)
    
    cursor.execute("UPDATE users SET last_login = NOW() WHERE id = %s", (user_id,))
    conn.commit()
    
    return jsonify(user)
```

**AFTER:**
```python
with get_database_connection('ai_infrastructure') as conn:
    with conn.cursor() as cursor:
        
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            return error_response('User not found', 404)
        
        cursor.execute("UPDATE users SET last_login = NOW() WHERE id = %s", (user_id,))
        conn.commit()
        
        return jsonify(user)
```

### Step 3: Handle Complex Cases

#### Multiple Cursors in Same Function:
```python
with get_database_connection('schema') as conn:
    # First query
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM table1")
        data1 = cursor.fetchall()
    
    # Second query (separate context)
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM table2")
        data2 = cursor.fetchall()
    
    return jsonify({'data1': data1, 'data2': data2})
```

#### Early Returns:
```python
with get_database_connection('schema') as conn:
    with conn.cursor() as cursor:
        
        cursor.execute("SELECT * FROM table WHERE id = %s", (id,))
        row = cursor.fetchone()
        
        if not row:
            return error_response('Not found', 404)  # ✅ Context manager handles cleanup
        
        return jsonify(row)
```

#### Exception Handling:
```python
try:
    with get_database_connection('schema') as conn:
        with conn.cursor() as cursor:
            
            cursor.execute("INSERT INTO table VALUES (%s)", (data,))
            conn.commit()
            
            return success_response()
            
except Exception as e:
    return error_response(str(e), 500)
```

## Validation Checklist

After refactoring each file:

- [ ] **Syntax Check**: `python -m py_compile filename.py` passes
- [ ] **Pattern Check**: No `cursor = conn.cursor()` patterns remain
- [ ] **Context Managers**: All cursors use `with conn.cursor() as cursor:`
- [ ] **Indentation**: All cursor operations are 4 spaces deeper inside `with` block
- [ ] **Functionality**: All SQL queries, logic, and returns are unchanged

## Common Pitfalls to Avoid

### Pitfall 1: Wrong Indentation
```python
# ❌ WRONG - cursor operations not indented
with conn.cursor() as cursor:
cursor.execute("SELECT ...")
```

```python
# ✅ CORRECT - cursor operations indented
with conn.cursor() as cursor:
    cursor.execute("SELECT ...")
```

### Pitfall 2: Breaking Out Too Early
```python
# ❌ WRONG - trying to use cursor after context exits
with conn.cursor() as cursor:
    cursor.execute("SELECT ...")

rows = cursor.fetchall()  # ❌ cursor is already closed!
```

```python
# ✅ CORRECT - fetch inside context
with conn.cursor() as cursor:
    cursor.execute("SELECT ...")
    rows = cursor.fetchall()
```

### Pitfall 3: Missing Blank Line After `with`
```python
# ✅ GOOD STYLE - blank line after with statement
with conn.cursor() as cursor:
    
    cursor.execute("SELECT ...")
```

## Files That Need Fixing

### Priority 1 (Critical - 10+ leaks):
- `thread_routes.py` - 23 leaks
- `automation_routes.py` - 19 leaks  
- `auth_routes.py` - 16 leaks
- `kanban_analytics_routes.py` - 14 leaks
- `google_auth_routes_V2_FIXED.py` - 10 leaks
- `microsoft_auth_routes_V2_FIXED.py` - 10 leaks

### Priority 2 (Medium - 6-9 leaks):
- `kanban_routes.py` - 9 leaks
- `kanban_supabase_routes.py` - 9 leaks
- `message_operations.py` - 9 leaks
- `onboarding_routes.py` - 9 leaks
- `production_log_routes.py` - 8 leaks
- `search_routes.py` - 7 leaks
- Plus 10 more files with 6 leaks each

### Priority 3 (Low - 1-5 leaks):
- 20 files with 1-5 leaks each

**Total: 36 files, 245+ cursor leaks**

## Example: Complete Before/After

### BEFORE (thread_routes.py - Line 79):
```python
@thread_bp.route('/user/<int:user_id>/team/<team_id>/threads', methods=['GET'])
def get_team_threads(user_id, team_id):
    try:
        if not user_id:
            return error_response('user_id required', 400)
        
        with get_database_connection('ai_infrastructure') as conn:
            cursor = conn.cursor()
            
            sql, params = convert_sql_placeholders("""
                SELECT id, username, parent_user_id, is_sub_user
                FROM ai_infrastructure.users
                WHERE username = %s
                  AND is_sub_user = TRUE
                  AND (parent_user_id = %s OR id = %s)
            """, (team_id, user_id, user_id))
            
            cursor.execute(sql, params)
            row = cursor.fetchone()
            
            cursor.close()
            cursor = None
            conn.close()
            conn = None
            
            if not row:
                return error_response('Team not found or access denied', 403)
            
            # ... rest of function
```

### AFTER:
```python
@thread_bp.route('/user/<int:user_id>/team/<team_id>/threads', methods=['GET'])
def get_team_threads(user_id, team_id):
    try:
        if not user_id:
            return error_response('user_id required', 400)
        
        with get_database_connection('ai_infrastructure') as conn:
            with conn.cursor() as cursor:
                
                sql, params = convert_sql_placeholders("""
                    SELECT id, username, parent_user_id, is_sub_user
                    FROM ai_infrastructure.users
                    WHERE username = %s
                      AND is_sub_user = TRUE
                      AND (parent_user_id = %s OR id = %s)
                """, (team_id, user_id, user_id))
                
                cursor.execute(sql, params)
                row = cursor.fetchone()
                
                # Note: Manual close() calls removed - context manager handles this
                
                if not row:
                    return error_response('Team not found or access denied', 403)
                
                # ... rest of function
```

## Success Criteria

A file is successfully refactored when:

1. ✅ **Zero cursor leaks**: `cursor = conn.cursor()` pattern eliminated
2. ✅ **Valid syntax**: `python -m py_compile` succeeds
3. ✅ **Context managers**: All cursors use `with conn.cursor() as cursor:`
4. ✅ **Proper indentation**: All cursor operations indented inside context
5. ✅ **Unchanged logic**: SQL queries and business logic identical
6. ✅ **No regressions**: API endpoints still return correct responses

## Testing After Refactoring

```bash
# 1. Syntax validation
python -m py_compile AI_infrastructure/routes/thread_routes.py

# 2. Cursor leak check
python -c "import re; content=open('AI_infrastructure/routes/thread_routes.py','r').read(); print('Leaks:', len(re.findall(r'cursor = conn\.cursor\(\)', content)))"

# 3. Context manager count
python -c "import re; content=open('AI_infrastructure/routes/thread_routes.py','r').read(); print('Fixed:', len(re.findall(r'with.*cursor.*as cursor', content)))"

# 4. Start Flask server and test endpoints
cd AI_infrastructure
python flask_app.py
```

## Why This Keeps Happening

**Root Cause:** Mixed patterns across the codebase:
- Some files use context managers (correct)
- Some files use manual `cursor.close()` (outdated)
- Some files have no cleanup at all (broken)

**Prevention:** Establish coding standards:
1. Always use context managers for cursors
2. Add pre-commit hooks to catch `cursor = conn.cursor()` pattern
3. Code review checklist for database operations

## Your Task

Fix **ONE file at a time**. For each file:

1. Read the entire file
2. Find all `cursor = conn.cursor()` patterns
3. Convert each to `with conn.cursor() as cursor:`
4. Indent all cursor operations by 4 spaces
5. Validate syntax with `python -m py_compile`
6. Confirm zero leaks remain

Start with the file I provide and ask for the next file when done.

---

**Generated:** 2026-01-01  
**Context:** AI_agents project, Flask route refactoring  
**Scan Results:** 36 files, 245+ cursor leaks identified
