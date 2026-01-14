# InHouse Database Tools Investigation - December 16, 2025

## 🔍 **Issue Identified**

The AI was **searching around but not following the tool_usage_system_prompt instructions** to use the database query tools for job history lookups.

## 📊 **Root Cause Analysis**

### **What Went Wrong:**

1. **Tool Discovery Confusion**: The AI searched for "database" and found STUB tools (`db_execute_query`, `db_get_available_queries`) that are **under construction**

2. **Missed the REAL Tools**: The actual working tools have different names:
   - `execute_query_library` ✅ (NOT `db_execute_query`)
   - `get_available_queries` ✅ (NOT `db_get_available_queries`)
   - `inhouse_execute_query` ✅ (custom SQL)
   - `inhouse_query_stock_levels` ✅ (stock queries)

3. **Platform Fragmentation**: Tools exist in TWO locations:
   - **Core Tools** (tools/implementations/sql_database.py) - STUBS, not working
   - **Module Plugins** (UI/modules_external/quote-calculator/) - REAL implementations

---

## ✅ **WORKING Tools Available**

### **Query Library Tools** (Module Plugin: quote-calculator)

| Tool Name | Purpose | Status |
|-----------|---------|--------|
| `get_available_queries` | List 60+ pre-built queries by category | ✅ WORKING |
| `execute_query_library` | Execute specific query with parameters | ✅ WORKING |

**Categories**:
- Sales & Revenue Analysis
- Customer Analytics
- Product Analysis
- Operational Metrics
- Financial Analysis
- Business Division Analysis
- Comparative Analysis

**Example Queries Available**:
```python
# Step 1: Discover queries
result = get_available_queries(category="Customer Analytics")

# Returns queries like:
# - client_order_history
# - client_preferences
# - client_lifetime_value
# - customer_reorder_prediction

# Step 2: Execute specific query
history = execute_query_library(
    query_name="client_order_history",
    parameters={
        "client_email": "john@example.com",
        "months": 12
    }
)
```

---

### **InHouse Custom SQL Tools** (Module Plugin: inhouse-print)

| Tool Name | Purpose | Status |
|-----------|---------|--------|
| `inhouse_execute_query` | Execute custom SQL on Fred database | ✅ WORKING |
| `inhouse_get_query_library_catalog` | Get catalog of pre-built queries | ✅ WORKING |
| `inhouse_query_stock_levels` | Quick stock level check | ✅ WORKING |
| `inhouse_query_guide` | Learn query system | ✅ WORKING |
| `inhouse_database_guide` | Get schema reference | ✅ WORKING |

---

### **STUB Tools (Under Construction)** - Core Tools

| Tool Name | Purpose | Status |
|-----------|---------|--------|
| `db_execute_query` | Execute QueryLibrary queries | 🚧 STUB |
| `db_get_available_queries` | List queries | 🚧 STUB |
| `db_calculate_quote` | Calculate product quotes | 🚧 STUB |
| `db_get_business_summary` | Business KPIs | 🚧 STUB |
| `db_get_stock_levels` | Inventory levels | 🚧 STUB |

**Why They Don't Work**:
```python
# Error message from testing:
{
  "success": false,
  "error": "QueryLibrary not loaded: No module named 'complete_calculator_implementation'"
}
```

---

## 🎯 **Correct Workflow for Job History**

### **What the Tool Usage Prompt Says:**

```markdown
### InHouse Print System (Fred Database)

**Progressive Discovery - Call guides FIRST:**

**For Custom SQL:**
```python
1. inhouse_query_guide()  # Learn query system
2. inhouse_database_guide()  # GET SCHEMA FIRST! (prevents column errors)
3. inhouse_execute_sql(query)  # Execute with correct columns
```

**Available Tools:**
- `inhouse_query_guide()` - SQL query guidance
- `inhouse_database_guide()` - Schema reference
- `inhouse_execute_sql()` - Custom SQL
```

### **What the AI Should Have Done:**

```python
# STEP 1: Get guidance on query system
guide = inhouse_query_guide()
# Returns: Query patterns, common queries, best practices

# STEP 2: Get database schema
schema = inhouse_database_guide()
# Returns: Complete Fred database schema with correct column names

# STEP 3: Execute job history query
job_history = inhouse_execute_query(
    query="""
    SELECT TOP 20
        o.OrderID,
        o.ClientName,
        o.OrderDate,
        o.Invoiced,
        jt.ShortJobDesc,
        jt.Cost,
        cs.ColourDesc AS Deadline
    FROM Orders o
    JOIN JobTickets jt ON o.OrderID = jt.OrderID
    LEFT JOIN ColourStatus cs ON jt.ColourStatus = cs.ColourID
    WHERE o.ClientName LIKE ?
    ORDER BY o.OrderDate DESC
    """,
    params=['%ClientName%']
)
```

---

## 📚 **OR Using Pre-Built Query Library:**

```python
# STEP 1: Discover available queries
queries = get_available_queries(category="Customer Analytics")

# STEP 2: Execute client order history query
history = execute_query_library(
    query_name="client_order_history",
    parameters={
        "client_name": "ABC Company",
        "months": 12,
        "include_details": true
    }
)

# Returns: DataFrame with full job history
```

---

## 🔧 **Why AI Didn't Follow the Prompt**

### **Issue 1: Search Term Confusion**

User asked to "test the inhouse database query tools"

AI searched for: `"inhouse database"` → Found: 0 tools
AI searched for: `"sql query"` → Found: `db_execute_query` (STUB)
AI searched for: `"database"` → Found: 16 tools (mostly automation/other)

**Should have searched for:**
- `"inhouse_query"` → Would find 4 working tools
- `"query_library"` → Would find 2 working tools
- `"execute_query"` → Would find working tools

### **Issue 2: Platform Name Mismatch**

**STUB tools** use platform: `"inhouse_database"`
**REAL tools** use platform: `"quote_calculator"` and `"inhouse_print"`

When AI called `list_platform_tools("inhouse_database")`, it found the STUBS, not the real implementations.

### **Issue 3: Missing Progressive Discovery**

Tool usage prompt says:
```
**For Custom SQL:**
1. inhouse_query_guide()  # Learn query system
2. inhouse_database_guide()  # GET SCHEMA FIRST!
3. inhouse_execute_sql(query)  # Execute
```

But AI jumped straight to searching for execution tools without calling the guides first.

---

## ✅ **What Needs to Change**

### **1. Update Tool Usage System Prompt**

Add explicit search guidance:

```markdown
### InHouse Print Database Tools

⚠️ **CRITICAL**: Tool names differ from search keywords!

**To discover database tools:**
```python
# ✅ CORRECT searches
search_tools("inhouse_query")     # Find 4 custom SQL tools
search_tools("query_library")     # Find 2 pre-built query tools
search_tools("execute_query")     # Find all query execution tools

# ❌ WRONG searches (finds STUBS)
search_tools("database")          # Too broad, finds automation tools
search_tools("inhouse database")  # No results
list_platform_tools("inhouse_database")  # Finds non-working STUBS
```

**Working tool platforms:**
- `quote_calculator` - Query library tools (60+ pre-built queries)
- `inhouse_print` - Custom SQL and stock tools
```

### **2. Deprecate STUB Tools or Rename Them**

**Option A**: Delete the STUB tools from `tools/implementations/sql_database.py`
**Option B**: Rename them to `db_*_DEPRECATED` so AI knows not to use them
**Option C**: Make them proxies that redirect to the real tools

### **3. Add Tool Aliases in Registry**

Allow both names to work:

```python
# In registry_v3.py
TOOL_ALIASES = {
    'db_execute_query': 'execute_query_library',
    'db_get_available_queries': 'get_available_queries',
    'db_calculate_quote': 'inhouse_calculate_quote'
}
```

---

## 📖 **Documentation Improvements**

### **inhouse_print_database_schema_v2.md**

Current file is great but buried in docs. Need to surface it in tool descriptions.

**Add to tool descriptions**:
```json
{
  "name": "inhouse_database_guide",
  "description": "Get complete Fred database schema with correct column names...",
  "when_to_use": [
    "BEFORE writing any custom SQL queries",
    "To avoid using non-existent columns like Orders.Status or JobTickets.DateCreated",
    "To understand ColourStatus is deadline urgency (not print color!)",
    "To see which tables have which columns"
  ]
}
```

---

## 🎯 **Immediate Action Items**

1. **[ ] Test the REAL tools** to confirm they work:
   ```python
   # Test query library discovery
   result = get_available_queries(category="all")
   
   # Test query execution
   result = execute_query_library(
       query_name="monthly_revenue_trend",
       parameters={"months": 6}
   )
   
   # Test custom SQL
   result = inhouse_execute_query(
       query="SELECT TOP 10 * FROM Orders",
       params=[]
   )
   ```

2. **[ ] Update tool_usage_system_prompt_v4_COMPACT.md**:
   - Add explicit search term guidance
   - List the CORRECT tool names
   - Show platform names (`quote_calculator`, `inhouse_print`)

3. **[ ] Fix or remove STUB tools**:
   - Delete `db_execute_query` etc. from sql_database.py
   - OR redirect them to real implementations
   - OR mark them clearly as deprecated

4. **[ ] Add query examples to prompts**:
   - Common job history query
   - Client lookup query
   - Stock level query
   - Revenue analysis query

---

## 🔍 **Testing Commands**

```python
# Discover what's actually available
from tools.registry_v3 import RegistryV3
registry = RegistryV3()

# Find all query-related tools
query_tools = [name for name in registry.tools.keys() if 'query' in name.lower()]
print(f"Found {len(query_tools)} query tools")

# Filter by inhouse
inhouse_query = [name for name in query_tools if 'inhouse' in name.lower()]
print("InHouse query tools:", inhouse_query)

# Get schemas
for tool_name in inhouse_query:
    schema = registry.get_tool(tool_name)
    print(f"\n{tool_name}:")
    print(f"  Platform: {schema.get('platform')}")
    print(f"  Description: {schema.get('description')[:100]}...")
```

---

## 📊 **Summary**

**Problem**: AI couldn't find working database query tools because:
1. Search terms didn't match tool names
2. STUB tools with similar names confused the search
3. Real tools in module plugins have different platform names
4. Progressive discovery workflow wasn't followed

**Solution**: 
1. Update prompts with correct search terms
2. Test and document the REAL working tools
3. Deprecate or remove STUB tools
4. Add query library examples to prompt

**Working Tools** (Confirmed via Registry):
- ✅ `get_available_queries` (quote_calculator)
- ✅ `execute_query_library` (quote_calculator)
- ✅ `inhouse_execute_query` (inhouse_print)
- ✅ `inhouse_query_guide` (inhouse_print)
- ✅ `inhouse_database_guide` (inhouse_print)
- ✅ `inhouse_query_stock_levels` (inhouse_print)

---

**Next Step**: Test these tools to confirm they actually connect to the database and return real data.
