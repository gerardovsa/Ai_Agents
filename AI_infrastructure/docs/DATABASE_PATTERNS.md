# Database Connection Patterns - AI Agents Project

**Last Updated:** December 23, 2024  
**Status:** Production Standard v1.0

---

## 🎯 Quick Reference

**✅ RECOMMENDED:** Use `execute_query()` for 99% of database operations  
**✅ ADVANCED:** Use context manager for multi-statement transactions  
**❌ DEPRECATED:** `get_connection()` wrapper (use execute_query instead)  
**❌ LEGACY:** Manual connection management (causes leaks)

---

## Pattern 1: execute_query() - Canonical Pattern ✅

**Use Cases:**
- ✅ Single SELECT queries
- ✅ Single INSERT/UPDATE/DELETE operations
- ✅ Simple data retrieval
- ✅ 99% of database operations

**Advantages:**
- ✅ Automatic connection cleanup (guaranteed, even on errors)
- ✅ Automatic commit/rollback handling
- ✅ Thread-safe (uses connection pool)
- ✅ No connection leaks possible
- ✅ Concise code (single function call)
- ✅ Clear intent (fetch_mode parameter)

**Import:**
```python
from AI_infrastructure.shared.database_utils import execute_query
```

### Fetch Modes

#### fetch_mode='all' (Default) - Multiple Rows as List[Dict]

```python
# Get all matching rows
users = execute_query(
    "SELECT user_id, email, name FROM users WHERE active = %s",
    (True,),
    fetch_mode='all',
    schema='ai_infrastructure'
)
# Returns: [{'user_id': 1, 'email': 'alice@example.com', 'name': 'Alice'}, ...]
# Empty result: []

for user in users:
    print(f"{user['name']} <{user['email']}>")
```

#### fetch_mode='one' - Single Row as Dict or None

```python
# Get single user by ID
user = execute_query(
    "SELECT user_id, email, name FROM users WHERE user_id = %s",
    (123,),
    fetch_mode='one',
    schema='ai_infrastructure'
)
# Returns: {'user_id': 123, 'email': 'bob@example.com', 'name': 'Bob'}
# Not found: None

if user:
    print(f"Found: {user['name']}")
else:
    print("User not found")
```

#### fetch_mode='value' - Single Value (First Column)

```python
# Get scalar value
user_count = execute_query(
    "SELECT COUNT(*) FROM users WHERE active = %s",
    (True,),
    fetch_mode='value',
    schema='ai_infrastructure'
)
# Returns: 42
# No rows: None

print(f"Active users: {user_count}")

# Get single field
email = execute_query(
    "SELECT email FROM users WHERE user_id = %s",
    (123,),
    fetch_mode='value',
    schema='ai_infrastructure'
)
# Returns: 'bob@example.com'
```

#### fetch_mode=None - Write Operations (INSERT/UPDATE/DELETE)

```python
# Insert new row
rows_inserted = execute_query(
    "INSERT INTO users (email, name, active) VALUES (%s, %s, %s)",
    ('charlie@example.com', 'Charlie', True),
    fetch_mode=None,
    schema='ai_infrastructure'
)
# Returns: 1 (number of rows affected)
# Auto-commits transaction

# Update existing rows
rows_updated = execute_query(
    "UPDATE users SET active = %s WHERE last_login < %s",
    (False, '2024-01-01'),
    fetch_mode=None,
    schema='ai_infrastructure'
)
# Returns: 5 (number of rows updated)

# Delete rows
rows_deleted = execute_query(
    "DELETE FROM sessions WHERE created_at < %s",
    ('2024-01-01',),
    fetch_mode=None,
    schema='sessions'
)
# Returns: 128 (number of rows deleted)
```

### Schema Parameter

```python
# Default schema (ai_infrastructure)
result = execute_query("SELECT * FROM users LIMIT 10")

# Explicit schema
result = execute_query(
    "SELECT * FROM threads",
    fetch_mode='all',
    schema='sessions'
)

# Available schemas
schemas = ['ai_infrastructure', 'sessions', 'synergy_sessions', 
           'stock_data', 'kanban_analytics']
```

### Error Handling

```python
try:
    users = execute_query(
        "SELECT * FROM users WHERE invalid_column = %s",
        (123,),
        fetch_mode='all'
    )
except Exception as e:
    # Connection automatically rolled back and closed
    logger.error(f"Query failed: {e}")
    # Handle error (return default, retry, etc.)
    users = []
```

### Real-World Examples

#### Check if User Exists
```python
exists = execute_query(
    "SELECT 1 FROM users WHERE email = %s",
    ('user@example.com',),
    fetch_mode='value'
)
if exists:
    print("User already registered")
```

#### Get Latest Session for User
```python
session = execute_query(
    """
    SELECT session_id, thread_id, created_at 
    FROM sessions 
    WHERE user_id = %s 
    ORDER BY created_at DESC 
    LIMIT 1
    """,
    (user_id,),
    fetch_mode='one',
    schema='sessions'
)
if session:
    print(f"Resume session {session['session_id']}")
```

#### Update User Last Login
```python
rows = execute_query(
    "UPDATE users SET last_login = NOW() WHERE user_id = %s",
    (user_id,),
    fetch_mode=None
)
if rows == 0:
    logger.warning(f"User {user_id} not found")
```

#### Create Table (DDL)
```python
execute_query(
    """
    CREATE TABLE IF NOT EXISTS temp_results (
        id SERIAL PRIMARY KEY,
        value TEXT,
        created_at TIMESTAMP DEFAULT NOW()
    )
    """,
    fetch_mode=None,
    schema='ai_infrastructure'
)
```

---

## Pattern 2: Context Manager - Advanced Multi-Statement Transactions ✅

**Use Cases:**
- ✅ Multi-step operations that must succeed together (atomicity)
- ✅ Complex transactions with conditional logic
- ✅ Need to query intermediate results to decide next steps
- ✅ Performance optimization (reuse connection for multiple queries)

**When NOT to Use:**
- ❌ Single SELECT query (use execute_query instead)
- ❌ Single INSERT/UPDATE/DELETE (use execute_query instead)
- ❌ Multiple independent queries (use execute_query multiple times)

**Import:**
```python
from AI_infrastructure.shared.database_utils import get_database_connection
```

### Basic Transaction Pattern

```python
# Transfer credits between users (atomic)
with get_database_connection('ai_infrastructure') as conn:
    cursor = conn.cursor()
    try:
        # Check sender balance
        cursor.execute(
            "SELECT credits FROM users WHERE user_id = %s FOR UPDATE",
            (sender_id,)
        )
        sender_balance = cursor.fetchone()['credits']
        
        if sender_balance < amount:
            raise ValueError("Insufficient credits")
        
        # Deduct from sender
        cursor.execute(
            "UPDATE users SET credits = credits - %s WHERE user_id = %s",
            (amount, sender_id)
        )
        
        # Add to recipient
        cursor.execute(
            "UPDATE users SET credits = credits + %s WHERE user_id = %s",
            (amount, recipient_id)
        )
        
        # Record transaction
        cursor.execute(
            "INSERT INTO transactions (sender_id, recipient_id, amount) VALUES (%s, %s, %s)",
            (sender_id, recipient_id, amount)
        )
        
        conn.commit()  # All succeed or all fail
        logger.info(f"Transferred {amount} credits from {sender_id} to {recipient_id}")
        
    except Exception as e:
        conn.rollback()  # Undo all changes
        logger.error(f"Transaction failed: {e}")
        raise
    finally:
        cursor.close()
```

### Conditional Multi-Step Operations

```python
# Create user with conditional setup
with get_database_connection('ai_infrastructure') as conn:
    cursor = conn.cursor()
    try:
        # Insert user
        cursor.execute(
            "INSERT INTO users (email, name) VALUES (%s, %s) RETURNING user_id",
            (email, name)
        )
        user_id = cursor.fetchone()['user_id']
        
        # Check if premium domain
        if email.endswith('@enterprise.com'):
            cursor.execute(
                "UPDATE users SET tier = 'premium', credits = 1000 WHERE user_id = %s",
                (user_id,)
            )
            logger.info(f"User {user_id} granted premium tier")
        
        # Create default session
        cursor.execute(
            "INSERT INTO sessions (user_id, thread_id) VALUES (%s, %s)",
            (user_id, f"default_{user_id}")
        )
        
        conn.commit()
        return user_id
        
    except Exception as e:
        conn.rollback()
        logger.error(f"User creation failed: {e}")
        raise
    finally:
        cursor.close()
```

### Batch Operations with Intermediate Checks

```python
# Process batch with validation
with get_database_connection('ai_infrastructure') as conn:
    cursor = conn.cursor()
    try:
        processed = 0
        errors = []
        
        for item in batch_items:
            # Check if already processed
            cursor.execute(
                "SELECT 1 FROM processed_items WHERE item_id = %s",
                (item['id'],)
            )
            if cursor.fetchone():
                continue  # Skip duplicates
            
            try:
                # Process item
                cursor.execute(
                    "INSERT INTO results (item_id, value) VALUES (%s, %s)",
                    (item['id'], item['value'])
                )
                
                # Mark as processed
                cursor.execute(
                    "INSERT INTO processed_items (item_id) VALUES (%s)",
                    (item['id'],)
                )
                processed += 1
                
            except Exception as e:
                errors.append((item['id'], str(e)))
                # Continue processing other items
        
        if errors:
            logger.warning(f"Batch processing had {len(errors)} errors")
        
        conn.commit()
        return {'processed': processed, 'errors': errors}
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Batch processing failed: {e}")
        raise
    finally:
        cursor.close()
```

### Connection Cleanup Rules

**✅ ALWAYS use try/except/finally:**
```python
with get_database_connection(schema) as conn:
    cursor = conn.cursor()
    try:
        # ... operations ...
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise
    finally:
        cursor.close()  # REQUIRED!
```

**❌ NEVER forget cursor.close():**
```python
# BAD - cursor leak
with get_database_connection(schema) as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT ...")
    # Missing cursor.close()!
```

**❌ NEVER create connections without context manager:**
```python
# BAD - connection leak
conn = get_database_connection('ai_infrastructure')
cursor = conn.cursor()
cursor.execute("SELECT ...")
# Missing conn.close()!
```

---

## Pattern 3: DEPRECATED - get_connection() Wrapper ❌

**Status:** Deprecated as of December 23, 2024  
**Will be removed:** Q2 2025

**Why Deprecated:**
- ❌ Requires manual try/finally blocks (error-prone)
- ❌ Easy to forget connection cleanup (causes leaks)
- ❌ More verbose than execute_query()
- ❌ No advantages over canonical pattern

**Migration Path:**

### Before (Deprecated):
```python
from shared.db_connection_wrapper import get_connection

conn = get_connection('ai_infrastructure')
cursor = conn.cursor()
try:
    cursor.execute("SELECT * FROM users WHERE user_id = %s", (123,))
    result = cursor.fetchall()
finally:
    cursor.close()
    conn.close()  # Easy to forget!
```

### After (Canonical):
```python
from AI_infrastructure.shared.database_utils import execute_query

result = execute_query(
    "SELECT * FROM users WHERE user_id = %s",
    (123,),
    fetch_mode='all',
    schema='ai_infrastructure'
)
```

**Current Usage (23 sites):**
- `scheduler.py` - 9 functions
- `auth/user_auth.py` - 3 functions
- `auth/credential_injector.py` - 2 functions
- `builders/` - 8 functions
- `workspace/shared.py` - 1 function

**Migration Strategy:**
Opportunistic refactoring as code is touched for other reasons. No deadline.

---

## Pattern 4: LEGACY - Manual Connection Management ❌

**Status:** Prohibited (causes connection leaks)  
**Action:** Refactor immediately if found

```python
# ❌ NEVER DO THIS
import psycopg2
conn = psycopg2.connect(...)
cursor = conn.cursor()
cursor.execute("SELECT ...")
# Missing cleanup = CONNECTION LEAK!
```

**Why This Fails:**
- If exception occurs, connection never closed
- Connection pool exhausts (max 12 connections per schema)
- Application hangs waiting for available connection
- Requires restart to fix

**Found This Pattern?** Refactor to execute_query() immediately.

---

## Migration Checklist

### Converting get_connection() to execute_query()

**Step 1:** Identify pattern
```python
# OLD
conn = get_connection('ai_infrastructure')
cursor = conn.cursor()
try:
    cursor.execute("SELECT * FROM users WHERE active = %s", (True,))
    users = cursor.fetchall()
finally:
    cursor.close()
    conn.close()
```

**Step 2:** Determine fetch mode
- Multiple rows → `fetch_mode='all'`
- Single row → `fetch_mode='one'`
- Single value → `fetch_mode='value'`
- INSERT/UPDATE/DELETE → `fetch_mode=None`

**Step 3:** Convert
```python
# NEW
from AI_infrastructure.shared.database_utils import execute_query

users = execute_query(
    "SELECT * FROM users WHERE active = %s",
    (True,),
    fetch_mode='all',
    schema='ai_infrastructure'
)
```

**Step 4:** Update result handling (if needed)
```python
# OLD - cursor.fetchall() returns list of RealDictRow
for user in users:
    print(user['email'])

# NEW - execute_query() returns list of dict (same interface)
for user in users:
    print(user['email'])  # No changes needed!
```

### Converting Manual Connections to execute_query()

**Step 1:** Identify pattern
```python
# OLD
import psycopg2
conn = psycopg2.connect(connection_string)
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM users")
count = cursor.fetchone()[0]
cursor.close()
conn.close()
```

**Step 2:** Convert
```python
# NEW
from AI_infrastructure.shared.database_utils import execute_query

count = execute_query(
    "SELECT COUNT(*) FROM users",
    fetch_mode='value',
    schema='ai_infrastructure'
)
```

### When to Use Context Manager Instead

**Use execute_query() when:**
- ✅ Single SELECT query
- ✅ Single INSERT/UPDATE/DELETE
- ✅ Independent operations

**Use context manager when:**
- ✅ Multiple related statements must succeed together
- ✅ Need to query intermediate results to decide next steps
- ✅ Complex conditional logic across multiple queries

**Example requiring context manager:**
```python
# Can't use execute_query() - need transaction atomicity
with get_database_connection('ai_infrastructure') as conn:
    cursor = conn.cursor()
    try:
        # Step 1: Get current value
        cursor.execute("SELECT balance FROM accounts WHERE id = %s FOR UPDATE", (account_id,))
        balance = cursor.fetchone()['balance']
        
        # Step 2: Validate
        if balance < withdrawal_amount:
            raise ValueError("Insufficient funds")
        
        # Step 3: Update
        cursor.execute(
            "UPDATE accounts SET balance = balance - %s WHERE id = %s",
            (withdrawal_amount, account_id)
        )
        
        # Step 4: Record
        cursor.execute(
            "INSERT INTO transactions (account_id, amount) VALUES (%s, %s)",
            (account_id, -withdrawal_amount)
        )
        
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
```

---

## Code Review Checklist

**✅ APPROVED PATTERNS:**
- [ ] Uses `execute_query()` for simple queries
- [ ] Uses context manager for multi-statement transactions
- [ ] Has cursor.close() in finally block (if using context manager)
- [ ] Specifies explicit fetch_mode parameter
- [ ] Specifies explicit schema parameter
- [ ] Has error handling (try/except)

**❌ REQUIRES CHANGES:**
- [ ] Uses `get_connection()` wrapper → Migrate to execute_query()
- [ ] Manual psycopg2.connect() → Migrate to execute_query()
- [ ] Missing finally block with cursor.close() → Add it
- [ ] Missing error handling → Add try/except
- [ ] Creates connection without context manager → Use context manager

**⚠️ WARNINGS:**
- [ ] Very long transaction (>10 statements) → Consider breaking up
- [ ] Nested transactions → Not supported by PostgreSQL
- [ ] Connection stored in instance variable → Causes leaks, use function-scoped

---

## Performance Tips

### Connection Pooling (Automatic)
- Pool size: 4-12 connections per schema
- Reuses existing connections (fast)
- Creates new connections if pool empty (slower first time)
- Thread-safe (multiple requests can query simultaneously)

### Query Optimization
```python
# ✅ GOOD - Use parameters (prevents SQL injection, enables prepared statements)
users = execute_query(
    "SELECT * FROM users WHERE email = %s",
    (email,),
    fetch_mode='all'
)

# ❌ BAD - String concatenation (SQL injection risk, no prepared statements)
users = execute_query(
    f"SELECT * FROM users WHERE email = '{email}'",  # NEVER DO THIS!
    fetch_mode='all'
)
```

### Batch Operations
```python
# ❌ SLOW - 100 separate connections
for user_id in user_ids:
    execute_query(
        "UPDATE users SET active = FALSE WHERE user_id = %s",
        (user_id,),
        fetch_mode=None
    )

# ✅ FAST - Single query with IN clause
execute_query(
    "UPDATE users SET active = FALSE WHERE user_id = ANY(%s)",
    (user_ids,),  # Pass list directly
    fetch_mode=None
)

# ✅ FAST - Single transaction with multiple statements
with get_database_connection('ai_infrastructure') as conn:
    cursor = conn.cursor()
    try:
        for user_id in user_ids:
            cursor.execute(
                "UPDATE users SET active = FALSE WHERE user_id = %s",
                (user_id,)
            )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
```

### Fetching Large Results
```python
# ✅ GOOD - Use LIMIT for large tables
recent_users = execute_query(
    "SELECT * FROM users ORDER BY created_at DESC LIMIT 100",
    fetch_mode='all'
)

# ⚠️ WARNING - fetch_mode='all' loads entire result into memory
# For very large results (millions of rows), consider:
# 1. Add LIMIT clause
# 2. Use pagination (OFFSET)
# 3. Use cursor with context manager (server-side cursor)
```

---

## FAQ

**Q: When should I use execute_query() vs context manager?**  
A: Use execute_query() for 99% of cases. Only use context manager when you need to run multiple related statements that must succeed together (transactions).

**Q: What if I need to run multiple independent queries?**  
A: Call execute_query() multiple times. Each call is independent and thread-safe.

**Q: Can I use execute_query() for DDL (CREATE TABLE, ALTER, etc.)?**  
A: Yes! Use `fetch_mode=None` for DDL statements.

**Q: What happens if my query fails?**  
A: execute_query() automatically rolls back the transaction and closes the connection, then raises the exception for you to handle.

**Q: Can I use execute_query() in async functions?**  
A: No, execute_query() is synchronous. For async code, use asyncpg or async context managers.

**Q: How do I get the ID of an inserted row?**  
A: Use RETURNING clause:
```python
user_id = execute_query(
    "INSERT INTO users (email, name) VALUES (%s, %s) RETURNING user_id",
    (email, name),
    fetch_mode='value'
)
```

**Q: Can I use transactions with execute_query()?**  
A: execute_query() runs each statement in its own transaction. For multi-statement transactions, use context manager.

**Q: What about connection timeouts?**  
A: Connection pool handles timeouts automatically. If no connection available after timeout, raises exception.

**Q: How do I test code that uses execute_query()?**  
A: Mock execute_query() in your tests:
```python
from unittest.mock import patch

with patch('AI_infrastructure.shared.database_utils.execute_query') as mock_query:
    mock_query.return_value = [{'user_id': 1, 'email': 'test@example.com'}]
    # Test your function
```

---

## Troubleshooting

### "Too many connections" Error

**Symptom:**
```
psycopg2.OperationalError: FATAL:  remaining connection slots are reserved
```

**Causes:**
1. Using deprecated get_connection() without cleanup
2. Creating manual connections without closing
3. Very high concurrent load (>12 requests per schema)

**Solutions:**
1. Migrate to execute_query() (automatic cleanup)
2. Check for missing finally blocks in context managers
3. Review connection pool stats: GET http://localhost:5001/api/pool-health

### Connection Leaks Detected

**Symptom:**
```
[CONNECTION_LEAK_DETECTOR] Found 4 idle connections (warning threshold: 3)
```

**Causes:**
1. Missing cursor.close() in finally block
2. Missing conn.close() after manual connection
3. Exception raised before cleanup code

**Solutions:**
1. Use execute_query() instead (no manual cleanup needed)
2. If using context manager, ensure cursor.close() in finally block
3. Check scheduler.py for functions using old patterns

### Query Performance Issues

**Symptom:** Slow query execution

**Debug Steps:**
1. Use EXPLAIN to analyze query plan:
```python
plan = execute_query(
    "EXPLAIN ANALYZE SELECT * FROM users WHERE email = %s",
    (email,),
    fetch_mode='all'
)
print(plan)
```

2. Check for missing indexes:
```python
execute_query(
    "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)",
    fetch_mode=None
)
```

3. Review connection pool health:
```python
import requests
response = requests.get('http://localhost:5001/api/pool-health')
print(response.json())
```

---

## Version History

**v1.0 (December 23, 2024):**
- Initial release
- Documented canonical execute_query() pattern
- Deprecated get_connection() wrapper
- Added migration guide and code review checklist

---

## Related Documentation

- `AI_infrastructure/shared/database_utils.py` - Source code with docstrings
- `AI_infrastructure/test_execute_query.py` - Comprehensive test suite
- `.github/copilot-instructions.md` - GitHub Copilot patterns
- Connection pool health: http://localhost:5001/api/pool-health

---

**Questions?** Check Flask logs at `AI_infrastructure/logs/flask_app.log`
