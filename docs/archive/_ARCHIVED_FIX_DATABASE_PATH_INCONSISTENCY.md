# PROMPT: Fix Database Path Inconsistency

**Issue ID**: DATABASE_PATH_FIX_001  
**Priority**: CRITICAL  
**Date**: November 2, 2025

---

## Problem Statement

Some files still reference the **OLD INCORRECT** database path:
```
❌ AI_infrastructure/ai_infrastructure.db (WRONG)
```

The **CORRECT** database path is:
```
✅ data/ai_infrastructure.db (CORRECT)
```

This causes database connection failures because the database files were moved to the `data/` folder per the architecture documentation.

---

## Task for AI Agent

**You are a Python debugging specialist. Your task is to:**

1. **Search for all files** that reference the OLD INCORRECT database path
2. **Update each file** to use the CORRECT path
3. **Verify the fix** by checking the path resolution logic
4. **Test connections** to ensure databases are found

---

## Step-by-Step Instructions

### Step 1: Find All Incorrect References

Search the entire codebase for the OLD path pattern:

```bash
# Search for the incorrect path
grep -r "AI_infrastructure/ai_infrastructure.db" AI_infrastructure/
grep -r "AI_infrastructure\\\\ai_infrastructure.db" AI_infrastructure/
grep -r "os.path.join.*AI_infrastructure.*ai_infrastructure.db" AI_infrastructure/
```

**Look for these patterns:**
- `'AI_infrastructure/ai_infrastructure.db'`
- `"AI_infrastructure/ai_infrastructure.db"`
- `os.path.join(os.path.dirname(__file__), 'ai_infrastructure.db')`
- `os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ai_infrastructure.db')`
- Any hardcoded absolute paths to the old location

**Expected files to check:**
- `AI_infrastructure/routes/*.py` (all route files)
- `AI_infrastructure/auth/user_auth.py`
- `AI_infrastructure/auth/credential_injector.py`
- `AI_infrastructure/core/*.py` (all core files)
- Any file that calls `sqlite3.connect()`

---

### Step 2: Understand the Correct Pattern

**CORRECT Pattern (ALWAYS USE THIS):**

```python
from pathlib import Path

# Calculate path relative to project root
root_dir = Path(__file__).parent.parent.parent  # Go up to AI_agents root
db_path = root_dir / 'data' / 'ai_infrastructure.db'

# Convert to string for sqlite3.connect()
conn = sqlite3.connect(str(db_path))
```

**Why this pattern?**
- Works from any file depth (routes/, auth/, core/)
- Always resolves to correct absolute path
- Cross-platform compatible (Windows/Linux/Mac)
- Easy to verify with debug print

**For different file locations:**

```python
# From AI_infrastructure/routes/agent_routes.py (3 levels deep)
root_dir = Path(__file__).parent.parent.parent  # → AI_agents/

# From AI_infrastructure/auth/user_auth.py (3 levels deep)
root_dir = Path(__file__).parent.parent.parent  # → AI_agents/

# From AI_infrastructure/flask_app.py (2 levels deep)
root_dir = Path(__file__).parent.parent  # → AI_agents/

# From tools/registry_v3.py (2 levels deep)
root_dir = Path(__file__).parent.parent  # → AI_agents/
```

---

### Step 3: Fix Each File

For **EACH file** that has incorrect path:

1. **Import Path at the top:**
   ```python
   from pathlib import Path
   import sqlite3
   ```

2. **Replace the database path logic:**

   **BEFORE (WRONG):**
   ```python
   # Example 1: Relative path (wrong)
   db_path = os.path.join(os.path.dirname(__file__), 'ai_infrastructure.db')
   
   # Example 2: Wrong folder (wrong)
   db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ai_infrastructure.db')
   
   # Example 3: Hardcoded (wrong)
   db_path = 'C:\\Users\\gpoli\\GIT\\AI_agents\\AI_infrastructure\\ai_infrastructure.db'
   ```

   **AFTER (CORRECT):**
   ```python
   # Get project root (AI_agents/)
   root_dir = Path(__file__).parent.parent.parent  # Adjust .parent count based on file depth
   db_path = root_dir / 'data' / 'ai_infrastructure.db'
   
   # Optional: Debug log to verify correct path
   print(f'🔷 [DB CONNECTION] Using: {db_path}')
   
   # Connect to database
   conn = sqlite3.connect(str(db_path))
   ```

3. **Add a helper function for reusable connections:**

   ```python
   def get_db_connection():
       """
       Get database connection to ai_infrastructure.db in data/ folder
       
       CRITICAL: Always use data/ai_infrastructure.db (CORRECT LOCATION)
       Do NOT use AI_infrastructure/ai_infrastructure.db (WRONG - old location)
       """
       from pathlib import Path
       import sqlite3
       
       root_dir = Path(__file__).parent.parent.parent  # Up to AI_agents root
       db_path = root_dir / 'data' / 'ai_infrastructure.db'
       
       # Optional: Debug log to verify correct path
       print(f'🔷 [DB CONNECTION] Using: {db_path}')
       
       conn = sqlite3.connect(str(db_path))
       conn.row_factory = sqlite3.Row  # Return rows as dict-like objects
       return conn
   ```

4. **Replace all `sqlite3.connect()` calls:**

   **BEFORE:**
   ```python
   conn = sqlite3.connect('AI_infrastructure/ai_infrastructure.db')
   cursor = conn.cursor()
   cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
   ```

   **AFTER:**
   ```python
   conn = get_db_connection()
   cursor = conn.cursor()
   cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
   ```

---

### Step 4: Verify the Fix

For **EACH fixed file**, add a verification print statement:

```python
def get_db_connection():
    root_dir = Path(__file__).parent.parent.parent
    db_path = root_dir / 'data' / 'ai_infrastructure.db'
    
    # Verification: Print the resolved path
    print(f'🔷 [DB CONNECTION] File: {__file__}')
    print(f'🔷 [DB CONNECTION] Root: {root_dir}')
    print(f'🔷 [DB CONNECTION] DB Path: {db_path}')
    print(f'🔷 [DB CONNECTION] Exists: {db_path.exists()}')
    
    if not db_path.exists():
        raise FileNotFoundError(f'Database not found: {db_path}')
    
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn
```

**Expected output:**
```
🔷 [DB CONNECTION] File: C:\Users\gpoli\GIT\AI_agents\AI_infrastructure\routes\agent_routes.py
🔷 [DB CONNECTION] Root: C:\Users\gpoli\GIT\AI_agents
🔷 [DB CONNECTION] DB Path: C:\Users\gpoli\GIT\AI_agents\data\ai_infrastructure.db
🔷 [DB CONNECTION] Exists: True
```

---

### Step 5: Test the Fix

**Test 1: Start Flask Server**
```powershell
cd C:\Users\gpoli\GIT\AI_agents
BISTART
```

**Expected**: Server starts without database errors

**Test 2: Test Login Endpoint**
```powershell
# Test user authentication (uses users table)
curl -X POST http://localhost:5001/api/auth/login `
  -H "Content-Type: application/json" `
  -d '{"username": "admin", "password": "password123"}'
```

**Expected**: Returns JWT token (proves database connection works)

**Test 3: Test OAuth Token Retrieval**
```python
# Test OAuth token retrieval
from AI_infrastructure.auth.credential_injector import CredentialInjector

injector = CredentialInjector()
creds = injector.get_google_credentials(user_id=1)
print(f"✅ OAuth tokens retrieved: {creds}")
```

**Expected**: Returns OAuth tokens or empty dict (proves database connection works)

**Test 4: Check Database Files**
```powershell
# Verify database files exist in correct location
ls C:\Users\gpoli\GIT\AI_agents\data\

# Expected output:
# ai_infrastructure.db
# sessions.db
# synergy_sessions.db
```

---

## Files to Fix (Priority Order)

### High Priority (Fix First)

1. **`AI_infrastructure/auth/user_auth.py`**
   - Line ~50-60: Database connection initialization
   - Method: `__init__(self, db_path: str = None)`
   - Current: `db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ai_infrastructure.db')`
   - Fix: Use `root_dir / 'data' / 'ai_infrastructure.db'`

2. **`AI_infrastructure/auth/credential_injector.py`**
   - Method: `get_db_connection()`
   - Current: May reference old path
   - Fix: Use correct path pattern

3. **`AI_infrastructure/routes/agent_routes.py`**
   - Any database queries for user verification
   - Fix: Use correct path pattern

4. **`AI_infrastructure/routes/oauth_routes.py`**
   - OAuth token storage/retrieval
   - Fix: Use correct path pattern

### Medium Priority

5. **`AI_infrastructure/routes/google_oauth_routes.py`**
6. **`AI_infrastructure/routes/microsoft_oauth_routes.py`**
7. **`AI_infrastructure/core/agent_worker.py`**
8. **`AI_infrastructure/core/unified_session_manager.py`**

### Low Priority (Check but may not need fixes)

9. Any other files in `AI_infrastructure/core/`
10. Any other files in `AI_infrastructure/routes/`

---

## Expected Changes Summary

**Files Changed**: 5-8 files  
**Lines Changed**: 10-30 lines total  
**Pattern**: Replace old path logic with standardized `get_db_connection()` helper

**Example Diff:**
```diff
- db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ai_infrastructure.db')
- conn = sqlite3.connect(db_path)
+ def get_db_connection():
+     root_dir = Path(__file__).parent.parent.parent
+     db_path = root_dir / 'data' / 'ai_infrastructure.db'
+     conn = sqlite3.connect(str(db_path))
+     conn.row_factory = sqlite3.Row
+     return conn
+ 
+ conn = get_db_connection()
```

---

## Success Criteria

✅ **Fix is complete when:**
1. All files use `data/ai_infrastructure.db` (correct path)
2. No files reference `AI_infrastructure/ai_infrastructure.db` (old path)
3. Flask server starts without database errors
4. User login endpoint works (proves users table access)
5. OAuth token retrieval works (proves oauth_tokens table access)
6. All database queries succeed

✅ **Verification command:**
```bash
# Search for any remaining incorrect references
grep -r "AI_infrastructure/ai_infrastructure.db" AI_infrastructure/
grep -r "AI_infrastructure\\\\ai_infrastructure.db" AI_infrastructure/

# Should return: No matches found
```

---

## Documentation Updates

After fixing, update these files:

1. **Create `DATABASE_PATH_FIX_COMPLETE.md`** with:
   - Summary of changes
   - Files modified (with line numbers)
   - Before/after code examples
   - Test results

2. **Update `ARCHITECTURE.md`** if needed:
   - Confirm database paths are correct
   - Update any references to old paths

3. **Update `.github/copilot-instructions.md`**:
   - Confirm database section shows correct paths

---

## Common Mistakes to Avoid

❌ **DON'T DO THIS:**
```python
# Wrong: Relative path (won't work from different directories)
db_path = 'data/ai_infrastructure.db'

# Wrong: Hardcoded absolute path (not portable)
db_path = 'C:\\Users\\gpoli\\GIT\\AI_agents\\data\\ai_infrastructure.db'

# Wrong: Using os.path with wrong folder
db_path = os.path.join(os.path.dirname(__file__), 'ai_infrastructure.db')
```

✅ **DO THIS:**
```python
# Correct: Path resolution from project root
from pathlib import Path
root_dir = Path(__file__).parent.parent.parent
db_path = root_dir / 'data' / 'ai_infrastructure.db'
conn = sqlite3.connect(str(db_path))
```

---

## AI Agent Execution Prompt

**Copy-paste this to execute the fix:**

```
@workspace
@file:FIX_DATABASE_PATH_INCONSISTENCY.md

I need you to fix the database path inconsistency issue.

Task:
1. Search for ALL files that reference the OLD path: AI_infrastructure/ai_infrastructure.db
2. Update each file to use the CORRECT path: data/ai_infrastructure.db
3. Use the standardized pattern from the instructions
4. Add the get_db_connection() helper function where appropriate
5. Test the fix by starting the Flask server

Start by searching for incorrect references:
grep -r "AI_infrastructure/ai_infrastructure.db" AI_infrastructure/

Then fix each file following the pattern in the instructions.

After fixing, verify by running:
BISTART

Report:
- Files modified (with line numbers)
- Before/after code snippets
- Test results
```

---

**Status**: Ready for AI agent execution  
**Estimated Time**: 15-30 minutes  
**Risk Level**: Low (reverting is easy - just undo path changes)
