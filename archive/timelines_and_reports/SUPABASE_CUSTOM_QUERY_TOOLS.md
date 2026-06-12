# Supabase Custom Query & Search Tools

## 🎯 Overview

Two powerful tools that allow AI to dynamically query and search **Supabase PostgreSQL** databases:

1. **`supabase_execute_query`** - Execute custom SQL queries
2. **`supabase_search_database`** - Search across all databases for text/keywords

## 📊 Available Supabase Schemas

| Schema | Description | Key Tables |
|--------|-------------|------------|
| **`ai_infrastructure`** | Users, OAuth, workspaces | users, oauth_tokens, workspaces, saved_threads, user_preferences |
| **`sessions`** | Chat threads & messages | messages (chat messages), threads (conversations), saved_threads |
| **`synergy_sessions`** | Kanban, tasks, workspaces | sessions, kanban_cards, workspace_users |
| **`stock_data`** | Inventory, orders, stock | unified_stocks, extracted_jobs, shopify_orders, stocklevels (40+ tables) |

---

## 🔧 Tool 1: supabase_execute_query

### Purpose
Execute custom SQL queries on any Supabase PostgreSQL schema. Full SQL power: SELECT, JOIN, GROUP BY, aggregations, etc.

### Parameters

```python
supabase_execute_query(
    schema_name: str,        # Required: 'ai_infrastructure', 'sessions', 'synergy_sessions', 'stock_data'
    query: str,              # Required: SQL query with %s placeholders
    params: list = None,     # Optional: Values for %s placeholders
    max_rows: int = 100,     # Optional: Limit results (default 100, max 1000)
    read_only: bool = True   # Optional: True = SELECT only, False = allow INSERT/UPDATE/DELETE
)
```

### Examples

#### 1. Find User by Email
```python
supabase_execute_query(
    schema_name='ai_infrastructure',
    query='SELECT id, username, email, role FROM users WHERE email = %s',
    params=['user@example.com']
)
```

**Returns:**
```json
{
  "success": true,
  "rows": [{"id": 1, "username": "john", "email": "user@example.com", "role": "user"}],
  "row_count": 1,
  "columns": ["id", "username", "email", "role"]
}
```

#### 2. Get Recent Chat Messages
```python
supabase_execute_query(
    schema_name='sessions',
    query='''
        SELECT thread_id, role, content, created_at 
        FROM messages 
        WHERE thread_id = %s 
        ORDER BY created_at DESC 
        LIMIT %s
    ''',
    params=['thread-abc-123', 10]
)
```

#### 3. Search Stock by Description (Case-Insensitive)
```python
supabase_execute_query(
    schema_name='stock_data',
    query='''
        SELECT stock_id, stock_type_name, gsm, cost_per_thousand, supplier_name
        FROM unified_stocks 
        WHERE stock_description ILIKE %s 
        LIMIT %s
    ''',
    params=['%business cards%', 20],
    max_rows=50
)
```

#### 4. Get User's Active Kanban Tasks
```python
supabase_execute_query(
    schema_name='synergy_sessions',
    query='''
        SELECT session_id, title, status, priority, created_at 
        FROM sessions 
        WHERE user_id = %s AND status != %s 
        ORDER BY priority DESC, created_at DESC
    ''',
    params=[1, 'completed']
)
```

#### 5. Complex JOIN Query - Workspaces with Member Counts
```python
supabase_execute_query(
    schema_name='ai_infrastructure',
    query='''
        SELECT w.id, w.name, w.description, COUNT(wu.user_id) as member_count
        FROM workspaces w
        LEFT JOIN workspace_users wu ON w.id = wu.workspace_id
        WHERE w.status = %s
        GROUP BY w.id, w.name, w.description
    ''',
    params=['active']
)
```

#### 6. Aggregate Query - Count Messages by Role
```python
supabase_execute_query(
    schema_name='sessions',
    query='''
        SELECT COUNT(*) as total_messages, role 
        FROM messages 
        WHERE thread_id LIKE %s 
        GROUP BY role
    ''',
    params=['thread-%']
)
```

### Common Queries by Schema

#### ai_infrastructure Schema
```sql
-- Find user
SELECT * FROM users WHERE email = %s

-- List user's workspaces
SELECT * FROM workspaces WHERE user_id = %s

-- Get OAuth tokens
SELECT platform, email, is_valid, expires_at 
FROM oauth_tokens 
WHERE user_id = %s AND is_valid = true

-- User preferences
SELECT * FROM user_preferences WHERE user_id = %s

-- Saved threads
SELECT thread_id, thread_name, created_at, summary
FROM saved_threads 
WHERE user_id = %s 
ORDER BY created_at DESC 
LIMIT 20
```

#### sessions Schema
```sql
-- List chat threads
SELECT session_id, user_query, interface_type, created_at
FROM chat_sessions 
WHERE user_id = %s 
ORDER BY created_at DESC 
LIMIT 50

-- Get thread messages
SELECT * FROM messages 
WHERE thread_id = %s 
ORDER BY created_at

-- Search message content
SELECT thread_id, content, role, created_at
FROM messages 
WHERE content ILIKE %s 
LIMIT 50

-- Thread metadata
SELECT * FROM saved_threads WHERE thread_id = %s
```

#### synergy_sessions Schema
```sql
-- List kanban tasks
SELECT session_id, title, status, priority, tags
FROM sessions 
WHERE user_id = %s
ORDER BY priority DESC

-- Get task details
SELECT * FROM sessions WHERE session_id = %s

-- Filter by status
SELECT * FROM sessions 
WHERE status = %s AND user_id = %s

-- Search tasks by title/content
SELECT session_id, title, content, status
FROM sessions 
WHERE (title ILIKE %s OR content ILIKE %s)
AND user_id = %s
```

#### stock_data Schema
```sql
-- Search stock
SELECT * FROM unified_stocks 
WHERE stock_description ILIKE %s 
OR stock_type_name ILIKE %s
LIMIT 50

-- Get stock by ID
SELECT * FROM unified_stocks WHERE stock_id = %s

-- List client jobs
SELECT ticket_id, client_name, product_type, quantity_ordered, order_date
FROM extracted_jobs 
WHERE client_name ILIKE %s 
ORDER BY order_date DESC
LIMIT 50

-- Shopify orders by email
SELECT order_number, customer_name, total_price, financial_status, created_at
FROM shopify_orders 
WHERE email = %s
ORDER BY created_at DESC

-- Low stock alerts
SELECT StockID, StockTypeDesc, CurrentStockLevel, ReorderPoint
FROM stocklevels 
WHERE CurrentStockLevel < ReorderPoint
AND IsActive = 1
ORDER BY CurrentStockLevel
```

### SQL Tips

✅ **Use %s placeholders** (NOT string concatenation)
```python
# ✅ GOOD - Safe from SQL injection
query = 'SELECT * FROM users WHERE email = %s'
params = ['user@example.com']

# ❌ BAD - SQL injection risk
query = f"SELECT * FROM users WHERE email = '{email}'"  # NEVER DO THIS
```

✅ **Case-insensitive search with ILIKE**
```sql
WHERE email ILIKE '%example.com'  -- Finds 'User@EXAMPLE.COM', 'test@example.com', etc.
```

✅ **Add LIMIT to prevent large results**
```sql
SELECT * FROM messages WHERE thread_id = %s LIMIT 100
```

✅ **Order results**
```sql
ORDER BY created_at DESC  -- Newest first
ORDER BY priority DESC, created_at  -- Priority, then date
```

✅ **Date filtering**
```sql
WHERE created_at >= %s AND created_at < %s
-- params: ['2025-12-01', '2025-12-31']
```

✅ **NULL checks**
```sql
WHERE field IS NULL      -- Find null values
WHERE field IS NOT NULL  -- Find non-null values
```

---

## 🔍 Tool 2: supabase_search_database

### Purpose
Search across **entire Supabase database** for text/keywords. Use when you don't know exact table location. Automatically searches common tables in all schemas.

### Parameters

```python
supabase_search_database(
    search_text: str,                # Required: Text to search (supports % wildcards)
    schemas: list = None,            # Optional: Schemas to search (default: all)
    tables: list = None,             # Optional: Specific tables (default: common tables)
    limit_per_table: int = 10        # Optional: Max results per table (default 10)
)
```

### Examples

#### 1. Find User Anywhere
```python
supabase_search_database(
    search_text='user@example.com'
)
```

**Returns:**
```json
{
  "success": true,
  "results": {
    "ai_infrastructure.users": [{"id": 1, "email": "user@example.com", "username": "john"}],
    "ai_infrastructure.oauth_tokens": [{"email": "user@example.com", "platform": "google"}],
    "sessions.messages": []
  },
  "total_matches": 2,
  "searched_locations": ["ai_infrastructure.users", "ai_infrastructure.oauth_tokens", "sessions.messages"],
  "message": "Found 2 matches across 2 tables."
}
```

#### 2. Search for Quote Number
```python
supabase_search_database(
    search_text='QU-0123',
    schemas=['stock_data']  # Only search stock_data schema
)
```

#### 3. Search for Content About Printing
```python
supabase_search_database(
    search_text='%printing%',  # Wildcard search
    schemas=['sessions', 'synergy_sessions'],
    limit_per_table=5
)
```

#### 4. Find Workspace by Name
```python
supabase_search_database(
    search_text='Team Workspace',
    schemas=['ai_infrastructure'],
    tables=['workspaces']  # Only search workspaces table
)
```

### Searchable Tables

#### ai_infrastructure Schema
- **users** - username, email
- **oauth_tokens** - email, account_name, profile_name
- **workspaces** - name, description, slug
- **saved_threads** - thread_name, conversation, summary
- **user_preferences** - nickname, ai_memories

#### sessions Schema
- **messages** - id, thread_id, role, content (jsonb), created_at, user_id, workspace_id
- **threads** - id, thread_slug, name, workspace_id, user_id, workflow_title
- **saved_threads** - thread_name, conversation, tags
- **messages** - content, role

#### synergy_sessions Schema
- **sessions** - title, content, tags
- **kanban_cards** - title, description, tags

#### stock_data Schema
- **unified_stocks** - stock_id, stock_type_name, stock_description, supplier_name
- **extracted_jobs** - client_name, job_description, product_type
- **shopify_orders** - order_number, email, customer_name
- **shopify_products** - title, body_html, vendor

### Search Tips

✅ **Wildcards for partial matches**
```python
search_text='%business cards%'  # Finds "Professional Business Cards", "Business Cards - 350GSM", etc.
```

✅ **Exact matches (no wildcards)**
```python
search_text='user@example.com'  # Finds exact email
```

✅ **Narrow search for performance**
```python
schemas=['ai_infrastructure']  # Only search one schema
tables=['users', 'workspaces']  # Only specific tables
```

✅ **Increase results per table**
```python
limit_per_table=50  # Get up to 50 results per table (default 10)
```

---

## 🆚 When to Use Which Tool?

### Use `supabase_execute_query` when:
- ✅ You know the **exact table and columns**
- ✅ Need **complex queries** (JOINs, GROUP BY, aggregations)
- ✅ Need **precise filtering** (dates, numbers, specific conditions)
- ✅ Want to **order/sort results**
- ✅ Need **large result sets** (up to 1000 rows)

### Use `supabase_search_database` when:
- ✅ **Don't know where data is stored**
- ✅ Searching for **text/keywords** across multiple tables
- ✅ Want **quick exploratory search**
- ✅ Looking for **user-generated content** (emails, names, descriptions)
- ✅ Need to **cast a wide net**

---

## 🔐 Security & Safety

### Read-Only by Default
`supabase_execute_query` is **read-only by default** for safety:
- Only `SELECT` queries allowed
- Prevents accidental data modification
- Set `read_only=False` for INSERT/UPDATE/DELETE

### Write Operations
```python
# Enable write operations
supabase_execute_query(
    schema_name='ai_infrastructure',
    query='UPDATE users SET last_active = %s WHERE id = %s',
    params=['2025-12-08', 1],
    read_only=False  # ⚠️ Required for write operations
)
```

### SQL Injection Prevention
- Always use **%s placeholders**
- Never concatenate user input into SQL
- Parameters are automatically escaped

---

## 📊 Real-World Use Cases

### Use Case 1: User Profile & Activity
```python
# Get complete user profile
user_data = supabase_execute_query(
    'ai_infrastructure',
    'SELECT * FROM users WHERE email = %s',
    ['user@example.com']
)

# Get user's recent threads
threads = supabase_execute_query(
    'sessions',
    'SELECT * FROM messages WHERE user_id = %s ORDER BY created_at DESC LIMIT 20',
    [user_data['rows'][0]['id']]
)

# Get user's kanban tasks
tasks = supabase_execute_query(
    'synergy_sessions',
    'SELECT * FROM sessions WHERE user_id = %s AND status != %s',
    [user_data['rows'][0]['id'], 'completed']
)
```

### Use Case 2: Find Customer's Orders
```python
# Search for customer by name (don't know exact table)
customer_search = supabase_search_database(
    search_text='ABC Corp',
    schemas=['stock_data']
)

# Get customer's orders
orders = supabase_execute_query(
    'stock_data',
    '''
        SELECT order_number, customer_name, total_price, financial_status, created_at
        FROM shopify_orders
        WHERE customer_name ILIKE %s
        ORDER BY created_at DESC
    ''',
    ['%ABC Corp%']
)
```

### Use Case 3: Conversation History
```python
# Find thread by keyword
thread_search = supabase_search_database(
    search_text='%quote for business cards%',
    schemas=['sessions'],
    tables=['messages']
)

# Get full conversation
if thread_search['total_matches'] > 0:
    thread_id = thread_search['results']['sessions.messages'][0]['thread_id']
    
    messages = supabase_execute_query(
        'sessions',
        'SELECT * FROM messages WHERE thread_id = %s ORDER BY created_at',
        [thread_id]
    )
```

### Use Case 4: Stock Inventory Check
```python
# Find stock by description
stock = supabase_execute_query(
    'stock_data',
    '''
        SELECT s.stock_id, s.stock_type_name, s.gsm, 
               sl.CurrentStockLevel, sl.ReorderPoint,
               s.cost_per_thousand, s.supplier_name
        FROM unified_stocks s
        LEFT JOIN stocklevels sl ON s.stock_id = CAST(sl.StockID AS TEXT)
        WHERE s.stock_description ILIKE %s
        AND s.is_active = true
        LIMIT 20
    ''',
    ['%business cards%']
)

# Check low stock
low_stock = supabase_execute_query(
    'stock_data',
    '''
        SELECT StockID, StockTypeDesc, CurrentStockLevel, ReorderPoint
        FROM stocklevels
        WHERE CurrentStockLevel < ReorderPoint
        AND IsActive = 1
        ORDER BY CurrentStockLevel
        LIMIT 50
    ''',
    []
)
```

---

## ⚠️ Important Notes

1. **Connection Pooling**: Uses Supabase connection pooling (4-12 connections per schema)
2. **Token Limits**: Default `max_rows=100` prevents token overflow. Increase carefully.
3. **Performance**: Complex queries on large tables may be slow. Use LIMIT and WHERE clauses.
4. **Permissions**: Tools respect database permissions. Some tables may be restricted.
5. **Schema Names**: Must be exact: `ai_infrastructure`, `sessions`, `synergy_sessions`, `stock_data`

---

## 🚀 Quick Start

### Installation
Tools are in:
- **Implementation**: `tools/implementations/supabase_query.py`
- **Schema**: `tools/schemas/supabase_query_tools.json`

### Test Query
```python
# Simple test - get user count
result = supabase_execute_query(
    schema_name='ai_infrastructure',
    query='SELECT COUNT(*) as total_users FROM users'
)
print(result)
```

### Test Search
```python
# Simple search - find your email
result = supabase_search_database(
    search_text='your.email@example.com'
)
print(result)
```

---

## 📖 Related Documentation

- **Database Schema**: See PostgreSQL schemas at top of document
- **Database Utils**: `AI_infrastructure/shared/database_utils.py`
- **Connection Pooling**: Supabase Transaction Mode (port 6543)
- **Supabase Studio**: Visual database browser

---

**Created**: December 8, 2025  
**Tools**: supabase_execute_query, supabase_search_database  
**Database**: 100% Supabase PostgreSQL (Zero SQLite)
