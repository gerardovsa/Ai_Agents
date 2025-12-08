# Fred Database Tools - Complete Testing Instructions for AI

Use these instructions to systematically test all Fred database query tools and workflows. Copy and paste each test case to an AI assistant.

---

## 🧪 TEST SUITE 1: Basic Query Operations

### Test 1.1: Simple SELECT Query
```
Test fred_execute_query with basic SELECT:
- Query: "SELECT TOP 10 OrderID, ClientName, OrderDate, Invoiced FROM Orders ORDER BY OrderDate DESC"

Expected outcomes:
- SUCCESS: Returns 10 most recent orders
- Columns: OrderID, ClientName, OrderDate, Invoiced
- Verify data types: OrderID (int), ClientName (text), OrderDate (date), Invoiced (bit 0/1)

Save a ClientName from results for Test 1.2
```

### Test 1.2: Query with Parameters (LIKE search)
```
Test fred_execute_query with parameterized search:
- Query: "SELECT TOP 20 * FROM Orders WHERE ClientName LIKE ? ORDER BY OrderDate DESC"
- Params: ['%CJ King%']

Expected outcomes:
- Returns orders matching "CJ King" in client name
- Verify case-insensitive search works
- Save an OrderID for Test 1.3
```

### Test 1.3: Query with JOIN
```
Using OrderID from Test 1.2, test JOIN query:
- Query: '''
    SELECT 
        jt.TicketID, jt.QTY, jt.Cost, jt.ShortJobDesc,
        ps.[Desc] as PaperSize, bt.BindTypeDesc
    FROM JobTickets jt
    LEFT JOIN PaperSize ps ON jt.PaperSizeID = ps.SizeID
    LEFT JOIN BindType bt ON jt.BindTypeID = bt.BindID
    WHERE jt.OrderID = ?
  '''
- Params: [OrderID from Test 1.2]

Expected outcomes:
- Returns all job tickets for the order
- Columns include PaperSize and BindTypeDesc from JOINs
- BindTypeDesc may be null (LEFT JOIN)

Save a TicketID for later tests
```

---

## 🧪 TEST SUITE 2: Aggregation Queries

### Test 2.1: COUNT with GROUP BY
```
Test fred_execute_query with aggregation:
- Query: '''
    SELECT TOP 20
        o.ClientName,
        COUNT(jt.TicketID) as JobCount,
        SUM(jt.Cost) as TotalCost
    FROM Orders o
    LEFT JOIN JobTickets jt ON o.OrderID = jt.OrderID
    WHERE o.OrderDate >= DATEADD(month, -3, GETDATE())
    GROUP BY o.ClientName
    ORDER BY TotalCost DESC
  '''

Expected outcomes:
- Returns top 20 customers by total cost (last 3 months)
- Columns: ClientName, JobCount, TotalCost
- TotalCost is SUM of all job tickets per client
- Verify SQL Server DATEADD() function works
```

### Test 2.2: CASE Statement (Calculated Fields)
```
Test fred_execute_query with CASE statement:
- Query: '''
    SELECT TOP 50
        OrderID,
        ClientName,
        DateRequired,
        CASE
            WHEN DateRequired < GETDATE() THEN 'OVERDUE'
            WHEN DateRequired <= DATEADD(day, 1, GETDATE()) THEN 'CRITICAL'
            WHEN DateRequired <= DATEADD(day, 7, GETDATE()) THEN 'HIGH'
            ELSE 'NORMAL'
        END as UrgencyLevel
    FROM Orders
    WHERE Invoiced = 0
    ORDER BY DateRequired
  '''

Expected outcomes:
- Returns unpaid orders with calculated urgency
- UrgencyLevel is OVERDUE/CRITICAL/HIGH/NORMAL
- Verify GETDATE() and DATEADD() work correctly
```

---

## 🧪 TEST SUITE 3: Date Range Queries

### Test 3.1: Date Range with Parameters
```
Test fred_execute_query with date range:
- Query: '''
    SELECT TOP 100
        OrderID, ClientName, OrderDate, DateRequired, Invoiced
    FROM Orders
    WHERE OrderDate >= ? AND OrderDate < ?
    ORDER BY OrderDate DESC
  '''
- Params: ['2025-11-01', '2025-12-01']

Expected outcomes:
- Returns orders from November 2025 only
- Verify date range filtering works correctly
- Check OrderDate values are within range
```

### Test 3.2: Relative Date Query
```
Test fred_execute_query with relative dates:
- Query: '''
    SELECT TOP 50 *
    FROM Orders
    WHERE OrderDate >= DATEADD(month, -1, GETDATE())
    ORDER BY OrderDate DESC
  '''

Expected outcomes:
- Returns orders from last month
- Verify DATEADD(month, -1, GETDATE()) works
- All dates should be recent
```

---

## 🧪 TEST SUITE 4: Boolean Flag Queries

### Test 4.1: Urgent Orders
```
Test fred_execute_query with boolean filters:
- Query: '''
    SELECT TOP 30
        OrderID, ClientName, OrderDate, DateRequired, Invoiced
    FROM Orders
    WHERE Urgent = 1 AND Invoiced = 0
    ORDER BY DateRequired
  '''

Expected outcomes:
- Returns urgent unpaid orders
- Urgent = 1 (true), Invoiced = 0 (false)
- Verify boolean bit fields work (1/0, not true/false)
```

### Test 4.2: Job Finishing Options
```
Test fred_execute_query with finishing flags:
- Query: '''
    SELECT TOP 20
        jt.TicketID, jt.ShortJobDesc, o.ClientName,
        jt.FrontCelloGloss, jt.FrontCelloMatt, jt.CelloYes
    FROM JobTickets jt
    INNER JOIN Orders o ON jt.OrderID = o.OrderID
    WHERE jt.FrontCelloGloss = 1
    ORDER BY jt.TicketID DESC
  '''

Expected outcomes:
- Returns jobs with front gloss cello lamination
- Finishing flags are bit fields (1/0)
- Verify multiple boolean columns work
```

---

## 🧪 TEST SUITE 5: Search Database Tool

### Test 5.1: Search All Tables (Default)
```
Test fred_search_database with default settings:
- search_text: 'CJ King Printing'

Expected outcomes:
- Searches Orders, JobTickets, Clients (default tables)
- Returns results grouped by table
- total_matches shows count across all tables
- Results include matching rows from each table
```

### Test 5.2: Search Specific Table
```
Test fred_search_database with table filter:
- search_text: '%business cards%'
- tables: ['JobTickets']
- limit_per_table: 20

Expected outcomes:
- Searches only JobTickets table
- Finds jobs with "business cards" in ShortJobDesc or TicketNotes
- Returns up to 20 results
- Wildcard search works (% before and after)
```

### Test 5.3: Search by Email
```
Test fred_search_database for email:
- search_text: '%@cjking.com.au'
- tables: ['Clients']

Expected outcomes:
- Searches Clients table only
- Finds clients with @cjking.com.au email addresses
- Returns ClientID, ClientName, Email
```

### Test 5.4: Search Invoice Number
```
Test fred_search_database for invoice:
- search_text: 'INV-2025-'

Expected outcomes:
- Searches Orders table (InvoiceNumber column)
- Finds orders with invoice numbers starting with "INV-2025-"
- Wildcards added automatically if not present
```

---

## 🧪 TEST SUITE 6: Error Handling

### Test 6.1: Invalid Column Name
```
Test fred_execute_query with non-existent column:
- Query: "SELECT OrderID, Status FROM Orders"

Expected outcomes:
- FAILS: "Invalid column name 'Status'"
- Error hint mentions Status doesn't exist, use Invoiced instead
- Refers to FRED_DATABASE_SCHEMA_ACTUAL.md
```

### Test 6.2: Invalid Table Name
```
Test fred_execute_query with wrong table:
- Query: "SELECT * FROM Invoice"

Expected outcomes:
- FAILS: "Invalid object name 'Invoice'"
- Error hint lists correct table names (Orders, JobTickets, Clients, etc.)
- Refers to database schema documentation
```

### Test 6.3: Read-Only Enforcement
```
Test fred_execute_query with UPDATE (read_only=True):
- Query: "UPDATE Orders SET Urgent = 1 WHERE OrderID = 12345"
- read_only: True (default)

Expected outcomes:
- FAILS: "UPDATE query blocked by read_only=True"
- Error hint says to set read_only=False for write operations
- Query not executed (safety check works)
```

### Test 6.4: Missing Parameter
```
Test fred_execute_query with missing param:
- Query: "SELECT * FROM Orders WHERE ClientName = ?"
- params: []  (empty list)

Expected outcomes:
- FAILS: Parameter count mismatch
- Error message about missing parameter value
- Query not executed
```

---

## 🧪 TEST SUITE 7: Complex Queries

### Test 7.1: Multiple JOINs
```
Test fred_execute_query with 5-table JOIN:
- Query: '''
    SELECT TOP 50
        o.OrderID, o.ClientName, o.OrderDate,
        jt.TicketID, jt.ShortJobDesc, jt.QTY, jt.Cost,
        ps.[Desc] as PaperSize,
        bt.BindTypeDesc,
        jtype.[Desc] as JobType,
        js.[Desc] as Stage
    FROM Orders o
    INNER JOIN JobTickets jt ON o.OrderID = jt.OrderID
    LEFT JOIN PaperSize ps ON jt.PaperSizeID = ps.SizeID
    LEFT JOIN BindType bt ON jt.BindTypeID = bt.BindID
    LEFT JOIN JobType jtype ON jt.JobTypeID = jtype.JobTypeID
    LEFT JOIN JobStages js ON jt.StageID = js.StageID
    WHERE o.OrderDate >= DATEADD(month, -1, GETDATE())
    ORDER BY o.OrderDate DESC
  '''

Expected outcomes:
- Returns orders with full job details and lookups
- All JOINs work correctly
- LEFT JOINs handle nullable foreign keys (BindTypeID)
- Square brackets work for reserved word [Desc]
```

### Test 7.2: Subquery
```
Test fred_execute_query with subquery:
- Query: '''
    SELECT 
        OrderID,
        ClientName,
        (SELECT COUNT(*) FROM JobTickets WHERE OrderID = o.OrderID) as JobCount,
        (SELECT SUM(Cost) FROM JobTickets WHERE OrderID = o.OrderID) as TotalCost
    FROM Orders o
    WHERE o.Invoiced = 1
    ORDER BY TotalCost DESC
  '''
- max_rows: 50

Expected outcomes:
- Returns invoiced orders with calculated job count and total
- Subqueries execute correctly
- Results limited to 50 rows (max_rows parameter)
```

---

## 🧪 TEST SUITE 8: Max Rows Limiting

### Test 8.1: Default Max Rows (100)
```
Test fred_execute_query with default max_rows:
- Query: "SELECT * FROM Orders WHERE Invoiced = 1"
- max_rows: not specified (default 100)

Expected outcomes:
- Returns up to 100 rows
- truncated: True if more than 100 exist
- Message indicates if results truncated
```

### Test 8.2: Custom Max Rows
```
Test fred_execute_query with custom limit:
- Query: "SELECT TOP 500 * FROM Orders ORDER BY OrderDate DESC"
- max_rows: 50

Expected outcomes:
- Query requests TOP 500 but max_rows=50 overrides
- Returns exactly 50 rows
- truncated: True
- Prevents token overflow
```

### Test 8.3: Max Rows Larger Than Results
```
Test fred_execute_query when results < max_rows:
- Query: "SELECT * FROM Orders WHERE ClientName = 'Very Specific Name That Doesnt Exist'"
- max_rows: 100

Expected outcomes:
- Returns 0 rows (or few rows if exists)
- truncated: False
- row_count shows actual count
```

---

## 🧪 TEST SUITE 9: Real-World Workflows

### Test 9.1: Find Customer's Order History
```
Complete workflow test:

Step 1: Search for customer
fred_search_database('Gerardo Poli')

Step 2: Get customer's orders
fred_execute_query(
  query="SELECT TOP 20 * FROM Orders WHERE ClientName LIKE ? ORDER BY OrderDate DESC",
  params=['%Gerardo Poli%']
)

Step 3: Get job details for an order
fred_execute_query(
  query='''
    SELECT jt.*, ps.[Desc] as PaperSize, bt.BindTypeDesc, jtype.[Desc] as JobType
    FROM JobTickets jt
    LEFT JOIN PaperSize ps ON jt.PaperSizeID = ps.SizeID
    LEFT JOIN BindType bt ON jt.BindTypeID = bt.BindID
    LEFT JOIN JobType jtype ON jt.JobTypeID = jtype.JobTypeID
    WHERE jt.OrderID = ?
  ''',
  params=[OrderID from Step 2]
)

Expected outcomes:
- ✅ Find customer in search
- ✅ Get order history
- ✅ Get detailed job specifications
- ✅ All JOINs return proper data
```

### Test 9.2: Urgent Orders Dashboard
```
Create urgent orders dashboard:

Query urgent unpaid orders:
fred_execute_query(
  query='''
    SELECT 
        o.OrderID,
        o.ClientName,
        o.OrderDate,
        o.DateRequired,
        DATEDIFF(day, GETDATE(), o.DateRequired) as DaysUntilDue,
        COUNT(jt.TicketID) as JobCount,
        SUM(jt.Cost) as TotalCost,
        CASE
            WHEN o.DateRequired < GETDATE() THEN 'OVERDUE'
            WHEN o.DateRequired <= DATEADD(day, 1, GETDATE()) THEN 'CRITICAL'
            WHEN o.DateRequired <= DATEADD(day, 3, GETDATE()) THEN 'HIGH'
            ELSE 'URGENT'
        END as Priority
    FROM Orders o
    LEFT JOIN JobTickets jt ON o.OrderID = jt.OrderID
    WHERE o.Urgent = 1 AND o.Invoiced = 0
    GROUP BY o.OrderID, o.ClientName, o.OrderDate, o.DateRequired
    ORDER BY o.DateRequired
  '''
)

Expected outcomes:
- ✅ Returns all urgent unpaid orders
- ✅ Calculated fields (DaysUntilDue, Priority) work
- ✅ Aggregations (JobCount, TotalCost) correct
- ✅ Sorted by due date (earliest first)
```

---

## 📊 COMPREHENSIVE TEST RESULTS TEMPLATE

After running all tests, document results in this format:

```
═══════════════════════════════════════════════════════════════
FRED DATABASE TOOLS TEST RESULTS SUMMARY
═══════════════════════════════════════════════════════════════

Test Date: [Date]
Database: Fred InHouse Print Shop (SQL Server)
Total Tests: 24

───────────────────────────────────────────────────────────────
SUITE 1: Basic Query Operations (3 tests)
───────────────────────────────────────────────────────────────
✅ Test 1.1: Simple SELECT - PASS
   - Returned: [X] rows
   - Columns: OrderID, ClientName, OrderDate, Invoiced

✅ Test 1.2: Parameterized LIKE Search - PASS
   - Found: [X] orders matching "CJ King"
   - OrderID saved: [XXXXX]

✅ Test 1.3: JOIN Query - PASS
   - Job tickets: [X]
   - JOINs successful (PaperSize, BindType)

───────────────────────────────────────────────────────────────
SUITE 2: Aggregation Queries (2 tests)
───────────────────────────────────────────────────────────────
✅ Test 2.1: COUNT/SUM with GROUP BY - PASS
   - Top customers by spend returned

✅ Test 2.2: CASE Statement - PASS
   - Urgency levels calculated correctly

───────────────────────────────────────────────────────────────
SUITE 3: Date Range Queries (2 tests)
───────────────────────────────────────────────────────────────
✅ Test 3.1: Date Range Parameters - PASS
✅ Test 3.2: Relative Dates (DATEADD) - PASS

───────────────────────────────────────────────────────────────
SUITE 4: Boolean Flag Queries (2 tests)
───────────────────────────────────────────────────────────────
✅ Test 4.1: Urgent Orders - PASS
✅ Test 4.2: Finishing Options - PASS

───────────────────────────────────────────────────────────────
SUITE 5: Search Database Tool (4 tests)
───────────────────────────────────────────────────────────────
✅ Test 5.1: Search All Tables - PASS
✅ Test 5.2: Search Specific Table - PASS
✅ Test 5.3: Search by Email - PASS
✅ Test 5.4: Search Invoice Number - PASS

───────────────────────────────────────────────────────────────
SUITE 6: Error Handling (4 tests)
───────────────────────────────────────────────────────────────
✅ Test 6.1: Invalid Column - Proper error + hint
✅ Test 6.2: Invalid Table - Proper error + hint
✅ Test 6.3: Read-Only Enforcement - Blocked correctly
✅ Test 6.4: Missing Parameter - Proper validation

───────────────────────────────────────────────────────────────
SUITE 7: Complex Queries (2 tests)
───────────────────────────────────────────────────────────────
✅ Test 7.1: Multiple JOINs (5 tables) - PASS
✅ Test 7.2: Subquery - PASS

───────────────────────────────────────────────────────────────
SUITE 8: Max Rows Limiting (3 tests)
───────────────────────────────────────────────────────────────
✅ Test 8.1: Default Max Rows - PASS
✅ Test 8.2: Custom Max Rows - PASS
✅ Test 8.3: Max Rows > Results - PASS

───────────────────────────────────────────────────────────────
SUITE 9: Real-World Workflows (2 tests)
───────────────────────────────────────────────────────────────
✅ Test 9.1: Customer Order History - PASS
✅ Test 9.2: Urgent Orders Dashboard - PASS

───────────────────────────────────────────────────────────────
OVERALL RESULTS
───────────────────────────────────────────────────────────────
Tests Passed: [X]/24
Tests Failed: [X]/24
Pass Rate: [XX]%

Core Functionality: ✅ FULLY WORKING
Query Execution: ✅ WORKING
Database Search: ✅ WORKING
Error Handling: ✅ WORKING
SQL Server Syntax: ✅ CORRECT

═══════════════════════════════════════════════════════════════
```

---

## 🎯 QUICK REFERENCE: Copy-Paste Test Commands

### Fastest Way to Test Core Functionality
```
Test 1: Simple query
fred_execute_query(query="SELECT TOP 10 * FROM Orders ORDER BY OrderDate DESC")

Test 2: Search customer
fred_execute_query(query="SELECT * FROM Orders WHERE ClientName LIKE ?", params=['%CJ King%'])

Test 3: Get job tickets
fred_execute_query(
  query="SELECT jt.*, ps.[Desc] as PaperSize FROM JobTickets jt LEFT JOIN PaperSize ps ON jt.PaperSizeID = ps.SizeID WHERE jt.OrderID = ?",
  params=[56230]
)

Test 4: Search database
fred_search_database(search_text='CJ King Printing')

Test 5: Search specific table
fred_search_database(search_text='%business cards%', tables=['JobTickets'])

Test 6: Urgent orders
fred_execute_query(query="SELECT TOP 20 * FROM Orders WHERE Urgent = 1 AND Invoiced = 0 ORDER BY DateRequired")
```

---

## ⚠️ IMPORTANT NOTES FOR AI TESTERS

1. **SQL Server Syntax**: Fred uses SQL Server, NOT PostgreSQL
   - Use `TOP N` (not LIMIT)
   - Use `?` placeholders (not %s or $1)
   - Use `DATEADD()`, `GETDATE()` for dates
   - Use `[Desc]` square brackets for reserved words

2. **Common Column Mistakes**:
   - ❌ `Orders.Status` does NOT exist → use `Invoiced` (bit)
   - ❌ `Orders.TotalCost` does NOT exist → sum `JobTickets.Cost`
   - ❌ `JobTickets.PrintType` does NOT exist → use finishing flags
   - ❌ `JobTickets.ColourStatus` is NUMERIC (1.0, 2.0), not text

3. **Boolean Fields**: Use bit (1/0), not true/false
   - `WHERE Invoiced = 1` (paid)
   - `WHERE Urgent = 0` (not urgent)

4. **Read-Only Mode**: Enabled by default for safety
   - Only SELECT queries allowed
   - Set `read_only=False` for INSERT/UPDATE/DELETE

5. **Database Schema**: Full reference at:
   - `FRED_DATABASE_SCHEMA_ACTUAL.md` (complete schema)
   - `tools/schemas/fred_query_tools.json` (tool docs)

6. **Connection**: Uses `inhouse_execute_sql()` wrapper
   - No direct connection needed
   - Handles connection pooling internally

7. **Max Rows**: Default 100, max 1000
   - Prevents token overflow
   - Set `max_rows` parameter to adjust

8. **Case-Insensitive**: LIKE search is case-insensitive by default
   - `WHERE ClientName LIKE '%printing%'` matches "Printing", "PRINTING", "printing"

---

## 🚀 AUTOMATION SCRIPT (Optional)

If testing via Python script, use this template:

```python
import json
from tools.implementations.fred_query import fred_execute_query, fred_search_database

# Test configuration
test_results = {"passed": 0, "failed": 0, "tests": []}

def run_test(name, func, *args, **kwargs):
    try:
        result = func(*args, **kwargs)
        if result.get('success'):
            test_results["passed"] += 1
            test_results["tests"].append(f"✅ {name}")
            print(f"✅ {name}")
            return result
        else:
            test_results["failed"] += 1
            test_results["tests"].append(f"❌ {name}: {result.get('error')}")
            print(f"❌ {name}: {result.get('error')}")
            return None
    except Exception as e:
        test_results["failed"] += 1
        test_results["tests"].append(f"❌ {name}: {str(e)}")
        print(f"❌ {name}: {str(e)}")
        return None

# Run tests
print("Starting Fred Database Tools Test Suite...\\n")

# Test 1: Simple query
orders = run_test(
    "Simple SELECT Query",
    fred_execute_query,
    query="SELECT TOP 10 OrderID, ClientName FROM Orders ORDER BY OrderDate DESC"
)

# Test 2: Search
run_test(
    "Search Database",
    fred_search_database,
    search_text='CJ King'
)

# Test 3: Parameterized query
if orders and orders.get('rows'):
    run_test(
        "Parameterized Query",
        fred_execute_query,
        query="SELECT * FROM Orders WHERE ClientName LIKE ?",
        params=['%CJ King%']
    )

# Print summary
print(f"\\n{'='*60}")
print(f"Test Results: {test_results['passed']} passed, {test_results['failed']} failed")
print(f"{'='*60}")
for test in test_results['tests']:
    print(test)
```

---

## 📚 ADDITIONAL RESOURCES

- **Database Schema**: `FRED_DATABASE_SCHEMA_ACTUAL.md`
- **Tool Implementation**: `tools/implementations/fred_query.py`
- **Tool Schema**: `tools/schemas/fred_query_tools.json`
- **Architecture Guide**: `DATABASE_ARCHITECTURE_DEC4_2025.md`

---

**Testing Complete!** Use these instructions to thoroughly test all Fred database functionality.
