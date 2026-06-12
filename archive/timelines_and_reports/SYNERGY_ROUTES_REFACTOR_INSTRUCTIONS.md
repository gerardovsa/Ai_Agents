# Synergy Routes Refactor Instructions

**File**: `AI_infrastructure/routes/synergy_routes.py`  
**Task**: Convert 64 functions from manual connection cleanup to context managers  
**Impact**: Eliminate 170 manual closes, reduce file size by ~25%, make connection leaks impossible

---

## 🎯 Core Transformation Pattern

### CURRENT PATTERN (Fragile - 15 lines per function)
```python
cursor = None
conn = None
try:
    conn = get_db_connection()
    cursor = conn.cursor()
    # ... database operations ...
    conn.commit()
except Exception as e:
    if conn:
        conn.rollback()
    raise
finally:
    if cursor:
        cursor.close()
        cursor = None
    if conn:
        conn.close()
        conn = None
```

### NEW PATTERN (Bulletproof - 3 lines per function)
```python
try:
    with get_database_connection('synergy_sessions') as conn:
        cursor = conn.cursor()
        # ... database operations ...
        conn.commit()  # optional - context manager handles it
except Exception as e:
    # ... error handling ...
    raise
```

---

## 📋 Step-by-Step Instructions

### Step 1: Update Imports (Lines 42-52)

**FIND:**
```python
from shared.database_utils import get_database_connection
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import database utility with auto-detection
from shared.database_utils import get_synergy_sessions_connection, is_using_supabase, convert_sql_placeholders
```

**REPLACE WITH:**
```python
from shared.database_utils import get_database_connection, is_using_supabase, convert_sql_placeholders
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

---

### Step 2: Deprecate Helper Function (Lines 57-66)

**Option A - Remove entirely** (cleaner):
```python
# DELETE these lines:
def get_db_connection():
    """
    Get database connection to synergy_sessions database
    
    Auto-detects environment:
    - Local dev: SQLite in data/synergy_sessions.db
    - Render: Supabase PostgreSQL (synergy_sessions schema)
    """
    return get_synergy_sessions_connection()
```

**Option B - Keep but deprecate** (safer for incremental refactor):
```python
def get_db_connection():
    """
    ⚠️ DEPRECATED: Use context manager instead:
        with get_database_connection('synergy_sessions') as conn:
            ...
    
    This helper exists for backward compatibility only.
    All functions in this file should use context managers directly.
    """
    return get_database_connection('synergy_sessions')
```

---

### Step 3: Transform All 64 Functions

Find every function matching this pattern:
```python
cursor = None
conn = None
try:
    conn = get_db_connection()
```

Transform to:
```python
try:
    with get_database_connection('synergy_sessions') as conn:
```

---

## 🔧 Concrete Examples

### Example 1: init_database() (Lines 240-358)

**BEFORE:**
```python
def init_database():
    """
    Initialize Synergy database if it doesn't exist
    
    Auto-detects environment:
    - Local dev: Creates SQLite database in data/synergy_sessions.db
    - Render: Uses existing Supabase PostgreSQL schema (synergy_sessions)
    
    ✅ FIXED: Proper cursor management
    """
    # Skip initialization if using Supabase (tables already migrated)
    if is_using_supabase():
        print("🔷 [SYNERGY] Using Supabase - skipping table creation (already migrated)")
        return
    
    cursor = None
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        sql, params = convert_sql_placeholders('''
            CREATE TABLE IF NOT EXISTS synergy_sessions (
                session_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                # ... more columns ...
            )
        ''', ())
        cursor.execute(sql, params)
        
        # Add missing columns if they don't exist
        try:
            if is_using_supabase():
                cursor.execute('ALTER TABLE synergy_sessions ADD COLUMN IF NOT EXISTS thread_ids TEXT')
            else:
                cursor.execute('ALTER TABLE synergy_sessions ADD COLUMN thread_ids TEXT')
        except (Exception):
            pass  # Column already exists
        
        conn.commit()
        print("✅ [SYNERGY] Database initialized successfully")
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"❌ [SYNERGY] Database initialization error: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
            cursor = None
        if conn:
            conn.close()
            conn = None
```

**AFTER:**
```python
def init_database():
    """
    Initialize Synergy database if it doesn't exist
    
    Auto-detects environment:
    - Local dev: Creates SQLite database in data/synergy_sessions.db
    - Render: Uses existing Supabase PostgreSQL schema (synergy_sessions)
    """
    # Skip initialization if using Supabase (tables already migrated)
    if is_using_supabase():
        print("🔷 [SYNERGY] Using Supabase - skipping table creation (already migrated)")
        return
    
    try:
        with get_database_connection('synergy_sessions') as conn:
            cursor = conn.cursor()
            
            sql, params = convert_sql_placeholders('''
                CREATE TABLE IF NOT EXISTS synergy_sessions (
                    session_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    # ... more columns ...
                )
            ''', ())
            cursor.execute(sql, params)
            
            # Add missing columns if they don't exist
            try:
                if is_using_supabase():
                    cursor.execute('ALTER TABLE synergy_sessions ADD COLUMN IF NOT EXISTS thread_ids TEXT')
                else:
                    cursor.execute('ALTER TABLE synergy_sessions ADD COLUMN thread_ids TEXT')
            except (Exception):
                pass  # Column already exists
            
            conn.commit()
            print("✅ [SYNERGY] Database initialized successfully")
            
    except Exception as e:
        print(f"❌ [SYNERGY] Database initialization error: {e}")
        raise
```

---

### Example 2: API Endpoints with jsonify() Returns

**BEFORE:**
```python
@synergy_bp.route('/list', methods=['GET'])
def list_synergy_sessions():
    """
    List all Synergy sessions with pagination and filtering
    
    Query Params:
        workspace_slug: Filter by workspace
        status: Filter by status (active, completed, archived)
        limit: Max results (default: 100)
        offset: Pagination offset (default: 0)
    
    Returns:
        JSON: {sessions: [...], total: int}
    """
    workspace_slug = request.args.get('workspace_slug')
    status = request.args.get('status')
    limit = int(request.args.get('limit', 100))
    offset = int(request.args.get('offset', 0))
    
    cursor = None
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build query with filters
        sql = "SELECT * FROM synergy_sessions WHERE 1=1"
        params = []
        
        if workspace_slug:
            sql += " AND workspace_slug = %s"
            params.append(workspace_slug)
        
        if status:
            sql += " AND status = %s"
            params.append(status)
        
        sql += " ORDER BY last_active DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        sql, params = convert_sql_placeholders(sql, tuple(params))
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        
        # Get total count
        count_sql, count_params = convert_sql_placeholders(
            "SELECT COUNT(*) FROM synergy_sessions WHERE 1=1", ()
        )
        cursor.execute(count_sql, count_params)
        total = cursor.fetchone()[0]
        
        return jsonify({
            'sessions': rows,
            'total': total,
            'limit': limit,
            'offset': offset
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        if cursor:
            cursor.close()
            cursor = None
        if conn:
            conn.close()
            conn = None
```

**AFTER:**
```python
@synergy_bp.route('/list', methods=['GET'])
def list_synergy_sessions():
    """
    List all Synergy sessions with pagination and filtering
    
    Query Params:
        workspace_slug: Filter by workspace
        status: Filter by status (active, completed, archived)
        limit: Max results (default: 100)
        offset: Pagination offset (default: 0)
    
    Returns:
        JSON: {sessions: [...], total: int}
    """
    workspace_slug = request.args.get('workspace_slug')
    status = request.args.get('status')
    limit = int(request.args.get('limit', 100))
    offset = int(request.args.get('offset', 0))
    
    try:
        with get_database_connection('synergy_sessions') as conn:
            cursor = conn.cursor()
            
            # Build query with filters
            sql = "SELECT * FROM synergy_sessions WHERE 1=1"
            params = []
            
            if workspace_slug:
                sql += " AND workspace_slug = %s"
                params.append(workspace_slug)
            
            if status:
                sql += " AND status = %s"
                params.append(status)
            
            sql += " ORDER BY last_active DESC LIMIT %s OFFSET %s"
            params.extend([limit, offset])
            
            sql, params = convert_sql_placeholders(sql, tuple(params))
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            # Get total count
            count_sql, count_params = convert_sql_placeholders(
                "SELECT COUNT(*) FROM synergy_sessions WHERE 1=1", ()
            )
            cursor.execute(count_sql, count_params)
            total = cursor.fetchone()[0]
            
            return jsonify({
                'sessions': rows,
                'total': total,
                'limit': limit,
                'offset': offset
            })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

---

### Example 3: Functions with Early Returns

**BEFORE:**
```python
def get_session_by_id(session_id):
    """Get synergy session by ID"""
    cursor = None
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        sql, params = convert_sql_placeholders(
            "SELECT * FROM synergy_sessions WHERE session_id = %s",
            (session_id,)
        )
        cursor.execute(sql, params)
        row = cursor.fetchone()
        
        if not row:
            return None  # ❌ Problem: Returns before finally block!
        
        return dict(row)
    
    except Exception as e:
        logger.error(f"Error fetching session {session_id}: {e}")
        return None
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
```

**AFTER:**
```python
def get_session_by_id(session_id):
    """Get synergy session by ID"""
    try:
        with get_database_connection('synergy_sessions') as conn:
            cursor = conn.cursor()
            
            sql, params = convert_sql_placeholders(
                "SELECT * FROM synergy_sessions WHERE session_id = %s",
                (session_id,)
            )
            cursor.execute(sql, params)
            row = cursor.fetchone()
            
            if not row:
                return None  # ✅ Safe: Context manager closes connection
            
            return dict(row)
    
    except Exception as e:
        logger.error(f"Error fetching session {session_id}: {e}")
        return None
```

---

## ⚠️ Critical Rules

### DO:
1. ✅ **Keep `try-except` blocks** - error handling stays!
2. ✅ **Keep `conn.commit()` calls** - still needed for write operations
3. ✅ **Keep business logic unchanged** - only change connection management
4. ✅ **Keep error messages and logging** - don't change diagnostics
5. ✅ **Keep early returns** - context manager handles cleanup before return

### DON'T:
1. ❌ **Remove `try-except` blocks** - we still need error handling
2. ❌ **Remove `finally` blocks** - context manager makes them unnecessary
3. ❌ **Keep `cursor = None` and `conn = None`** - not needed with context manager
4. ❌ **Keep `conn.close()` and `cursor.close()` calls** - context manager handles this
5. ❌ **Change SQL queries or business logic** - only refactor connection pattern

---

## 🎯 Search Patterns for Automation

### Pattern 1: Find functions with manual pattern
```regex
cursor = None\s*\n\s*conn = None\s*\n\s*try:\s*\n\s*conn = get_db_connection\(\)
```

**Replace with:**
```python
try:
    with get_database_connection('synergy_sessions') as conn:
```

### Pattern 2: Remove finally blocks
```regex
finally:\s*\n\s*if cursor:.*?cursor\.close\(\).*?cursor = None\s*\n\s*if conn:.*?conn\.close\(\).*?conn = None
```

**Replace with:** (empty string - delete)

### Pattern 3: Remove manual rollback in except blocks
```regex
except.*?:\s*\n\s*if conn:\s*\n\s*conn\.rollback\(\)\s*\n
```

**Replace with:**
```python
except Exception as e:
```

---

## ✅ Testing Checklist

After transformation, verify:

### Import Verification
- [ ] `from shared.database_utils import get_database_connection` exists at top
- [ ] `get_synergy_sessions_connection` import removed (or helper deprecated)

### Pattern Verification
- [ ] Search `conn.close()` → should find **0 results**
- [ ] Search `cursor.close()` → should find **0 results**
- [ ] Search `cursor = None` → should find **0 results**
- [ ] Search `conn = None` → should find **0 results**
- [ ] Search `with get_database_connection` → should find **64 results**
- [ ] Search `finally:` → should find **0 results** (or very few edge cases)

### Syntax Verification
- [ ] File parses without Python syntax errors
- [ ] No indentation errors
- [ ] All `try` blocks have matching structure
- [ ] All context managers properly closed

### Functional Testing
- [ ] Flask starts without import errors
- [ ] GET `/api/synergy/list` returns sessions
- [ ] POST `/api/synergy/create` creates new session
- [ ] PATCH `/api/synergy/<id>` updates session
- [ ] DELETE `/api/synergy/<id>` deletes session
- [ ] No "connection pool exhausted" errors in logs
- [ ] No "LEAKED" warnings in Flask output

---

## 📊 Expected Results

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| **File size** | 6,273 lines | ~4,800 lines | **-23%** |
| **Functions** | 64 | 64 | Same |
| **Manual closes** | 170 | 0 | **-100%** |
| **Context managers** | 0 | 64 | **+64** |
| **Try-finally blocks** | 64 | 0 | **-100%** |
| **Boilerplate code** | ~1,500 lines | ~200 lines | **-87%** |
| **Connection leak risk** | Medium (fragile) | Zero | **Eliminated** |

---

## 🚀 One-Shot Transformation Prompt

```
TASK: Refactor AI_infrastructure/routes/synergy_routes.py to use context managers

SCOPE: 64 functions need transformation

TRANSFORMATION PATTERN:

FROM (15 lines):
    cursor = None
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # operations
    except Exception as e:
        if conn:
            conn.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

TO (3 lines):
    try:
        with get_database_connection('synergy_sessions') as conn:
            cursor = conn.cursor()
            # operations
    except Exception as e:
        raise

RULES:
1. Change imports: Remove get_synergy_sessions_connection, keep get_database_connection
2. Replace get_db_connection() with get_database_connection('synergy_sessions')
3. Wrap connection in context manager: with ... as conn:
4. Remove all cursor = None and conn = None initializations
5. Remove all finally blocks with cursor.close() and conn.close()
6. Remove all conn.rollback() calls (context manager handles it)
7. Keep all try-except blocks (error handling stays)
8. Keep all conn.commit() calls (write operations need explicit commit)
9. Keep all business logic unchanged
10. Keep all error messages and logging unchanged

FIND: 64 functions with manual connection pattern
REPLACE: All with context manager pattern

DO NOT change business logic, SQL queries, or error handling.
ONLY change connection management pattern.
```

---

## 🔍 Common Issues & Solutions

### Issue 1: Indentation Errors After Transformation
**Problem:** Context manager adds extra indentation level
**Solution:** All code inside `with` block needs +4 spaces indentation

### Issue 2: Early Returns Not Closing Connections
**Problem:** Worried about `return` statements inside `with` block
**Solution:** Context manager automatically closes connection on return - this is safe!

### Issue 3: Transaction Rollback Missing
**Problem:** Removed rollback logic in except blocks
**Solution:** Context manager handles rollback automatically on exception

### Issue 4: Import Errors After Refactor
**Problem:** Still importing `get_synergy_sessions_connection`
**Solution:** Update imports to only import `get_database_connection`

### Issue 5: Helper Function Still Being Called
**Problem:** Functions still calling `get_db_connection()` helper
**Solution:** Replace all calls with `get_database_connection('synergy_sessions')`

---

## 📝 Commit Message Template

```
refactor(synergy-routes): convert to context managers for connection safety

TRANSFORMATION:
- Converted 64 functions from manual cleanup to context managers
- Removed 170 manual conn.close() calls
- Eliminated all try-finally boilerplate (64 blocks removed)
- Reduced file size from 6,273 to ~4,800 lines (-23%)

IMPACT:
- Connection leaks now impossible (guaranteed by context manager)
- Code 87% less boilerplate (1,500 → 200 lines of cleanup code)
- Maintenance burden eliminated (no manual close tracking needed)
- Future-proof pattern (can't forget to close connections)

SAFETY:
- All business logic unchanged
- All error handling preserved
- All SQL queries identical
- All API endpoints functionally equivalent

TESTING:
- Verified all 64 Synergy Dashboard endpoints
- No connection pool exhaustion errors
- No "LEAKED" warnings in Flask logs
- Database operations perform identically

FILES CHANGED:
- AI_infrastructure/routes/synergy_routes.py
```

---

## 🎓 Learning Resources

**Why Context Managers?**
- Python PEP 343: https://peps.python.org/pep-0343/
- "with" statement guarantees cleanup even on exception/return
- Database connections are perfect use case for context managers

**Connection Pool Behavior:**
- `conn.close()` returns connection to pool (doesn't actually close)
- Context manager calls `conn.close()` automatically on exit
- Pool exhaustion = no available connections (max 12 for Supabase)

**Best Practices:**
- Always use context managers for resources (files, connections, locks)
- Never manually manage connection cleanup
- Let Python's `with` statement handle resource lifecycle

---

**END OF INSTRUCTIONS**
