# Database Query Tools - Complete Guide

## 📚 Overview

You have access to **TWO complete database query tool sets**:

1. **Supabase PostgreSQL Tools** - Query cloud-hosted Supabase databases (4 schemas)
2. **Fred InHouse Tools** - Query on-premises Fred print shop database (SQL Server)

Both tool sets provide:
- ✅ **Custom SQL query execution** - Write your own SELECT/JOIN/GROUP BY queries
- ✅ **Database-wide search** - Find data when you don't know table location
- ✅ **Comprehensive schema documentation** - AI guidance for query formulation
- ✅ **Safety features** - Read-only by default, parameterized queries, max rows limits

---

## 🎯 Quick Decision Guide

**Use Supabase Tools When:**
- Querying user accounts, OAuth tokens, workspaces
- Searching chat sessions, messages, conversation history
- Accessing Synergy Kanban tasks, cards, workspace users
- Querying stock inventory, orders, extracted jobs

**Use Fred Tools When:**
- Querying customer orders and invoicing
- Searching job tickets and production specifications
- Accessing client contact information
- Checking job stages, materials, finishing options

---

## 🗄️ DATABASE 1: Supabase PostgreSQL (Cloud)

### Platform
- **Type**: PostgreSQL (Cloud-hosted on Supabase)
- **Connection**: Transaction Mode Pooler (port 6543)
- **Schemas**: 4 separate schemas in single database
- **Connection Method**: `get_database_connection(schema_name)`

### Available Schemas

#### 1. `ai_infrastructure` Schema
**Purpose**: User accounts, OAuth, workspaces, preferences

**Tables:**
- `users` - User accounts (id, username, email, role, created_at)
- `oauth_tokens` - OAuth credentials (platform, email, is_valid, expires_at)
- `workspaces` - User workspaces (id, name, description, slug, user_id)
- `user_preferences` - User settings (nickname, ai_memories, quick_actions)
- `saved_threads` - Saved conversation threads (thread_id, thread_name, summary)

**Common Queries:**
```python
# Find user by email
supabase_execute_query(
    'ai_infrastructure',
    'SELECT * FROM users WHERE email = %s',
    ['user@example.com']
)

# Get user's workspaces
supabase_execute_query(
    'ai_infrastructure',
    'SELECT * FROM workspaces WHERE user_id = %s',
    [1]
)

# Check OAuth tokens
supabase_execute_query(
    'ai_infrastructure',
    'SELECT platform, email, is_valid FROM oauth_tokens WHERE user_id = %s',
    [1]
)
```

#### 2. `sessions` Schema
**Purpose**: Chat sessions, conversation threads, messages

**Tables:**
- `messages` - All chat messages (id, thread_id, role, content, created_at, user_id)
- `threads` - Chat threads/conversations (id, thread_slug, name, workspace_id, user_id)
- `saved_threads` - Thread metadata (thread_id, thread_name, conversation, tags)
- `messages` - Conversation messages (thread_id, role, content, created_at)

**Common Queries:**
```python
# Get user's recent messages
supabase_execute_query(
    'sessions',
    'SELECT * FROM messages WHERE user_id = %s ORDER BY created_at DESC LIMIT 20',
    [1]
)

# Get thread messages
supabase_execute_query(
    'sessions',
    'SELECT * FROM messages WHERE thread_id = %s ORDER BY created_at',
    ['thread-abc-123']
)

# Search message content
supabase_execute_query(
    'sessions',
    'SELECT thread_id, content, role FROM messages WHERE content ILIKE %s LIMIT 50',
    ['%business cards%']
)
```

#### 3. `synergy_sessions` Schema
**Purpose**: Synergy Kanban board, tasks, cards

**Tables:**
- `sessions` - Kanban tasks (session_id, title, content, status, priority, user_id)
- `kanban_cards` - Card data (title, description, tags, color)
- `workspace_users` - Workspace memberships (workspace_id, user_id, role)

**Common Queries:**
```python
# Get user's kanban tasks
supabase_execute_query(
    'synergy_sessions',
    'SELECT * FROM sessions WHERE user_id = %s AND status != %s ORDER BY priority DESC',
    [1, 'completed']
)

# Search tasks by title
supabase_execute_query(
    'synergy_sessions',
    'SELECT * FROM sessions WHERE title ILIKE %s OR content ILIKE %s',
    ['%printing%', '%printing%']
)
```

#### 4. `stock_data` Schema
**Purpose**: Stock inventory, orders, extracted jobs, shopify data

**Tables:** (40+ tables)
- `unified_stocks` - Stock inventory (stock_id, stock_type_name, gsm, cost_per_thousand)
- `extracted_jobs` - AI-extracted jobs (ticket_id, client_name, product_type, quantity_ordered)
- `shopify_orders` - Shopify orders (order_number, email, customer_name, total_price)
- `shopify_products` - Shopify products (title, body_html, vendor, price)
- `stocklevels` - Current stock levels (StockID, CurrentStockLevel, ReorderPoint)

**Common Queries:**
```python
# Search stock by description
supabase_execute_query(
    'stock_data',
    'SELECT * FROM unified_stocks WHERE stock_description ILIKE %s LIMIT 20',
    ['%business cards%']
)

# Get client jobs
supabase_execute_query(
    'stock_data',
    'SELECT * FROM extracted_jobs WHERE client_name ILIKE %s ORDER BY order_date DESC',
    ['%CJ King%']
)

# Low stock alerts
supabase_execute_query(
    'stock_data',
    'SELECT * FROM stocklevels WHERE CurrentStockLevel < ReorderPoint AND IsActive = 1',
    []
)
```

### Supabase SQL Syntax (PostgreSQL)

```sql
-- LIMIT results
SELECT * FROM users LIMIT 20

-- Placeholders (use %s)
WHERE email = %s AND created_at > %s

-- Case-insensitive search
WHERE name ILIKE '%keyword%'

-- String concat
first_name || ' ' || last_name

-- Date functions
WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'

-- NULL checks
WHERE field IS NULL
WHERE field IS NOT NULL
```

### Supabase Tools

**Tool 1: `supabase_execute_query()`**
```python
supabase_execute_query(
    schema_name='sessions',        # Required: which schema
    query='SELECT * FROM messages WHERE thread_id = %s LIMIT 10',
    params=['thread-123'],         # List of values for %s
    max_rows=100,                  # Max results (default 100)
    read_only=True                 # Safety (default True)
)
```

**Tool 2: `supabase_search_database()`**
```python
supabase_search_database(
    search_text='user@example.com',   # Text to find
    schemas=['ai_infrastructure'],     # Which schemas (default: all)
    limit_per_table=10                 # Results per table
)
```

**Documentation:**
- Full Guide: `SUPABASE_CUSTOM_QUERY_TOOLS.md`
- JSON Schema: `tools/schemas/supabase_query_tools.json`
- Implementation: `tools/implementations/supabase_query.py`

---

## 🖨️ DATABASE 2: Fred InHouse (SQL Server)

### Platform
- **Type**: SQL Server (on-premises/hosted)
- **Connection**: Via `inhouse_execute_sql()` wrapper
- **Purpose**: Print shop production database
- **Schema**: Single schema (dbo, implicit)

### Available Tables

#### Core Production Tables

**Orders** - Customer orders and invoicing
- `OrderID` (PK) - Order identifier
- `ClientName` - Customer name
- `OrderDate` - Order creation date
- `DateRequired` - Due date
- `Urgent` - Boolean flag (bit: 1/0)
- `Invoiced` - Boolean flag (bit: 1/0)
- `InvoiceNumber` - Invoice number
- `ClientOrderNum` - Client's order number
- `OrderNotes` - Order notes

⚠️ **Common Mistakes:**
- ❌ `Status` column does NOT exist (use `Invoiced`)
- ❌ `TotalCost` column does NOT exist (sum `JobTickets.Cost`)

**JobTickets** - Individual print jobs with specifications
- `TicketID` (PK) - Job ticket ID
- `OrderID` (FK) - Links to Orders
- `QTY` - Quantity to produce
- `Cost` - Job cost (per ticket)
- `ShortJobDesc` - Brief description
- `TicketNotes` - Detailed specs and customer delivery info
- `ColourStatus` - Status code (float: 1.0, 2.0, 3.0)
- `StageID` (FK) - Production stage
- `JobTypeID` (FK) - Job type
- `PaperSizeID` (FK) - Paper size
- `BindTypeID` (FK) - Binding type

**Finishing Options** (bit flags):
- `CelloYes`, `FrontCelloGloss`, `FrontCelloMatt`, `BackCelloGloss`, `BackCelloMatt`
- `FoldYes`, `StitchYes`, `DieCutYes`, `DrillYes`, `ScoreYes`, `PerfYes`
- `RingBind`, `PerfectBind`, `PadGlue`, `Books`, `Pages`

⚠️ **Common Mistakes:**
- ❌ `PrintType` column does NOT exist (use finishing flags)
- ❌ `ColourStatus` is NUMERIC (1.0, 2.0, 3.0), not text ('Red', 'Yellow')
- ✅ `Cost` is per-ticket, not order total

**Clients** - Customer contact information
- `ClientID` (PK) - Client identifier
- `ClientName` - Customer name
- `Email` - Email address
- `MYOB_ID` - MYOB UUID

#### Lookup Tables

**PaperSize**
- `SizeID` (PK)
- `[Desc]` - Paper size description (use square brackets!)

**BindType**
- `BindID` (PK)
- `BindTypeDesc` - Binding description (NOT `[Desc]`!)

**JobStages**
- `StageID` (PK)
- `[Desc]` - Stage description

**JobType**
- `JobTypeID` (PK)
- `[Desc]` - Job type description

### Fred SQL Syntax (SQL Server)

```sql
-- LIMIT results (use TOP)
SELECT TOP 20 * FROM Orders

-- Placeholders (use ?)
WHERE ClientName = ? AND OrderDate > ?

-- Case-insensitive search (default)
WHERE ClientName LIKE '%printing%'

-- String concat
ClientName + ' - ' + InvoiceNumber

-- Date functions
WHERE OrderDate > DATEADD(month, -3, GETDATE())

-- Boolean (bit 1/0)
WHERE Invoiced = 1 AND Urgent = 0

-- Reserved words (square brackets)
SELECT [Desc] FROM PaperSize
```

### Fred Common Queries

```sql
-- Find orders by client
SELECT TOP 20 * FROM Orders 
WHERE ClientName LIKE '%CJ King%' 
ORDER BY OrderDate DESC

-- Get job tickets with materials
SELECT 
    jt.TicketID, jt.QTY, jt.Cost, jt.ShortJobDesc,
    ps.[Desc] as PaperSize,
    bt.BindTypeDesc
FROM JobTickets jt
LEFT JOIN PaperSize ps ON jt.PaperSizeID = ps.SizeID
LEFT JOIN BindType bt ON jt.BindTypeID = bt.BindID
WHERE jt.OrderID = ?

-- Urgent unpaid orders
SELECT TOP 50
    o.OrderID, o.ClientName, o.DateRequired,
    COUNT(jt.TicketID) as JobCount,
    SUM(jt.Cost) as TotalCost
FROM Orders o
LEFT JOIN JobTickets jt ON o.OrderID = jt.OrderID
WHERE o.Urgent = 1 AND o.Invoiced = 0
GROUP BY o.OrderID, o.ClientName, o.DateRequired
ORDER BY o.DateRequired

-- Jobs with finishing options
SELECT 
    jt.TicketID, jt.ShortJobDesc, o.ClientName,
    jt.FrontCelloGloss, jt.FrontCelloMatt
FROM JobTickets jt
INNER JOIN Orders o ON jt.OrderID = o.OrderID
WHERE jt.FrontCelloGloss = 1
```

### Fred Tools

**Tool 1: `fred_execute_query()`**
```python
fred_execute_query(
    query='SELECT TOP 10 * FROM Orders WHERE ClientName LIKE ? ORDER BY OrderDate DESC',
    params=['%CJ King%'],      # List of values for ?
    max_rows=100,              # Max results (default 100)
    read_only=True             # Safety (default True)
)
```

**Tool 2: `fred_search_database()`**
```python
fred_search_database(
    search_text='CJ King Printing',      # Text to find
    tables=['Orders', 'JobTickets'],     # Which tables (default: Orders, JobTickets, Clients)
    limit_per_table=10                   # Results per table
)
```

**Documentation:**
- Testing Guide: `FRED_TOOLS_TESTING_INSTRUCTIONS.md`
- Schema Reference: `UI/modules_external/inhouse-kanban/FRED_DATABASE_SCHEMA_ACTUAL.md`
- JSON Schema: `tools/schemas/fred_query_tools.json`
- Implementation: `tools/implementations/fred_query.py`

---

## 🆚 Key Differences

| Feature | Supabase (PostgreSQL) | Fred (SQL Server) |
|---------|----------------------|-------------------|
| **Platform** | Cloud PostgreSQL | On-premises SQL Server |
| **Schemas** | 4 schemas (ai_infrastructure, sessions, synergy_sessions, stock_data) | 1 schema (dbo, implicit) |
| **LIMIT** | `LIMIT 20` | `TOP 20` |
| **Placeholders** | `%s` | `?` |
| **String Concat** | `\|\|` or `CONCAT()` | `+` or `CONCAT()` |
| **Case Search** | `ILIKE '%text%'` | `LIKE '%text%'` (case-insensitive default) |
| **Date Functions** | `CURRENT_DATE`, `INTERVAL` | `GETDATE()`, `DATEADD()` |
| **Reserved Words** | Use quotes `"Desc"` | Use brackets `[Desc]` |
| **Boolean** | `true`/`false` or `1`/`0` | `bit` (1/0 only) |

---

## 🎯 Common Use Cases

### Use Case 1: Find User Profile and Activity
```python
# Step 1: Find user (Supabase)
user = supabase_execute_query(
    'ai_infrastructure',
    'SELECT * FROM users WHERE email = %s',
    ['user@example.com']
)

# Step 2: Get chat history (Supabase)
sessions = supabase_execute_query(
    'sessions',
    'SELECT * FROM messages WHERE user_id = %s ORDER BY created_at DESC LIMIT 20',
    [user['rows'][0]['id']]
)

# Step 3: Get kanban tasks (Supabase)
tasks = supabase_execute_query(
    'synergy_sessions',
    'SELECT * FROM sessions WHERE user_id = %s AND status != %s',
    [user['rows'][0]['id'], 'completed']
)
```

### Use Case 2: Find Customer Orders
```python
# Step 1: Search for customer (Fred)
customer_search = fred_search_database('ABC Printing')

# Step 2: Get order history (Fred)
orders = fred_execute_query(
    query='SELECT TOP 20 * FROM Orders WHERE ClientName LIKE ? ORDER BY OrderDate DESC',
    params=['%ABC Printing%']
)

# Step 3: Get job details (Fred)
for order in orders['rows']:
    jobs = fred_execute_query(
        query='''
            SELECT jt.*, ps.[Desc] as PaperSize, bt.BindTypeDesc
            FROM JobTickets jt
            LEFT JOIN PaperSize ps ON jt.PaperSizeID = ps.SizeID
            LEFT JOIN BindType bt ON jt.BindTypeID = bt.BindID
            WHERE jt.OrderID = ?
        ''',
        params=[order['OrderID']]
    )
```

### Use Case 3: Stock Inventory Check
```python
# Search stock (Supabase)
stock = supabase_execute_query(
    'stock_data',
    '''
        SELECT s.stock_id, s.stock_type_name, s.gsm,
               sl.CurrentStockLevel, sl.ReorderPoint
        FROM unified_stocks s
        LEFT JOIN stocklevels sl ON s.stock_id = CAST(sl.StockID AS TEXT)
        WHERE s.stock_description ILIKE %s AND s.is_active = true
        LIMIT 20
    ''',
    ['%business cards%']
)

# Check low stock (Supabase)
low_stock = supabase_execute_query(
    'stock_data',
    '''
        SELECT StockID, StockTypeDesc, CurrentStockLevel, ReorderPoint
        FROM stocklevels
        WHERE CurrentStockLevel < ReorderPoint AND IsActive = 1
        ORDER BY CurrentStockLevel
    ''',
    []
)
```

---

## 🔐 Safety Features

Both tool sets include:

### Read-Only by Default
- Only `SELECT` queries allowed by default
- Set `read_only=False` for INSERT/UPDATE/DELETE
- Prevents accidental data modification

### Parameterized Queries
- Use placeholders (`%s` for Supabase, `?` for Fred)
- Values automatically escaped
- Prevents SQL injection attacks

### Token Overflow Prevention
- `max_rows` parameter limits results (default 100, max 1000)
- Prevents context window overflow
- Use LIMIT/TOP in query for better control

### Helpful Error Messages
- Clear error descriptions
- Hints for common mistakes
- References to schema documentation

---

## 📖 Complete Documentation

### Supabase Tools
- **Complete Guide**: `SUPABASE_CUSTOM_QUERY_TOOLS.md` (400+ lines)
- **JSON Schema**: `tools/schemas/supabase_query_tools.json`
- **Implementation**: `tools/implementations/supabase_query.py`
- **Testing**: Included in Supabase guide

### Fred Tools
- **Testing Guide**: `FRED_TOOLS_TESTING_INSTRUCTIONS.md` (600+ lines)
- **Schema Reference**: `UI/modules_external/inhouse-kanban/FRED_DATABASE_SCHEMA_ACTUAL.md`
- **JSON Schema**: `tools/schemas/fred_query_tools.json`
- **Implementation**: `tools/implementations/fred_query.py`

### General
- **Architecture**: `DATABASE_ARCHITECTURE_DEC4_2025.md`
- **Database Utils**: `AI_infrastructure/shared/database_utils.py`

---

## 🚀 Quick Start

### Supabase Query Test
```python
# Simple test
result = supabase_execute_query(
    schema_name='ai_infrastructure',
    query='SELECT COUNT(*) as total_users FROM users'
)
print(result)
```

### Fred Query Test
```python
# Simple test
result = fred_execute_query(
    query='SELECT TOP 10 OrderID, ClientName FROM Orders ORDER BY OrderDate DESC'
)
print(result)
```

### Supabase Search Test
```python
# Search test
result = supabase_search_database(
    search_text='your.email@example.com'
)
print(result)
```

### Fred Search Test
```python
# Search test
result = fred_search_database(
    search_text='CJ King Printing'
)
print(result)
```

---

## ⚠️ Important Reminders

1. **Supabase uses PostgreSQL syntax** (LIMIT, %s, ILIKE)
2. **Fred uses SQL Server syntax** (TOP, ?, LIKE)
3. **Fred's Orders.Status doesn't exist** - use `Invoiced` (bit)
4. **Fred's JobTickets.ColourStatus is numeric** (1.0, 2.0), not text
5. **Read-only by default** - set `read_only=False` for writes
6. **Use schema documentation** - both have comprehensive guides
7. **Search tools for exploration** - when table location unknown
8. **Custom queries for precision** - when you know exact table/columns

---

**Created**: December 8, 2025  
**Status**: Complete - Both tool sets ready for use  
**Databases**: 100% PostgreSQL/SQL Server (Zero SQLite)
