# Fred Database Tools - Missing Implementation Issue

**Date**: December 5, 2025  
**Status**: 🚨 CRITICAL - Tools defined but not implemented  
**Impact**: AI cannot query InHouse Print (Fred) database

---

## Problem Summary

The `inhouse_database` platform has **5 tools defined in schema** but **ZERO implementations**:

- ✅ **Schema exists**: `tools/schemas/sql_database_tools.json` (defines 5 tools)
- ❌ **Implementation missing**: No `tools/implementations/sql_database.py` file
- 📊 **Result**: Tools appear in `list_platform_tools()` but fail with "Tool not found" on execution

---

## Root Cause Analysis

### What Happened

1. **Schema Registration (Working)**
   - File: `tools/schemas/sql_database_tools.json`
   - Platform: `inhouse_database`
   - Tools defined:
     * `db_execute_query` - Execute QueryLibrary queries
     * `db_get_available_queries` - List all available queries
     * `db_calculate_quote` - Quote calculations
     * `db_get_business_summary` - Business KPIs
     * `db_get_stock_levels` - Stock inventory

2. **Implementation Loading (Broken)**
   - Expected file: `tools/implementations/sql_database.py`
   - **Actual**: File does NOT exist
   - Registry loads schemas but cannot find functions
   - Tools registered but not callable

3. **Registry Behavior**
   ```python
   # From registry_v3.py line 238-251
   special_modules = ["sql_database", "meta_tools"]
   for module_name in special_modules:
       if module_name in impl_files:  # ← sql_database NOT in impl_files
           try:
               module = importlib.import_module(f"tools.implementations.{module_name}")
               # ... register functions
           except Exception as e:
               logger.warning(f"Failed to load special module {module_name}: {e}")
   ```

4. **Execution Flow**
   ```
   AI calls: db_execute_query(query_name="client_order_history", ...)
   
   ↓
   
   registry.execute_tool(tool_name="db_execute_query", ...)
   
   ↓
   
   registry.get_tool_function("db_execute_query")  # Searches implementations
   
   ↓
   
   Returns: None (function not found)
   
   ↓
   
   ValueError: Tool not found: db_execute_query
   ```

---

## Console Log Evidence

```
ERROR:tools.registry_v3:  Tool function not found: db_execute_query
[META-TOOL ERROR] execute_tool() failed:
  - Tool: db_execute_query
  - Error: Tool not found: db_execute_query
  - Error Type: ValueError
```

**Why This Happens:**
- `list_platform_tools()` → Reads schema → Returns tool names ✅
- `execute_tool()` → Searches implementations → Not found ❌

---

## Missing Implementation File Structure

The file `tools/implementations/sql_database.py` should contain:

```python
"""
InHouse Print Database Tools - Fred SQL Server Integration

Provides query execution, business intelligence, and quote calculations
for the InHouse Print (Fred) SQL Server database.

Functions:
- db_execute_query() - Execute pre-built QueryLibrary queries
- db_get_available_queries() - List available queries
- db_calculate_quote() - Calculate printing quotes
- db_get_business_summary() - Get business KPIs
- db_get_stock_levels() - Get inventory levels
"""

def db_execute_query(query_name: str, params: dict = None, **kwargs):
    """Execute a pre-built SQL query from QueryLibrary"""
    # Implementation needed
    pass

def db_get_available_queries(category: str = None, **kwargs):
    """List all available queries in QueryLibrary"""
    # Implementation needed
    pass

def db_calculate_quote(product_type: str, quantity: int, **kwargs):
    """Calculate accurate quote for printing products"""
    # Implementation needed
    pass

def db_get_business_summary(months: int = 12, **kwargs):
    """Get high-level business summary with KPIs"""
    # Implementation needed
    pass

def db_get_stock_levels(stock_id: int = None, low_stock_only: bool = False, **kwargs):
    """Get current stock inventory levels"""
    # Implementation needed
    pass
```

---

## Related Files That May Help

Found in workspace:
- `c:\Users\gpoli\GIT\In_House_SQL\G_Folder\tools\database_tools\inhouse_database_cli.py`
- `c:\Users\gpoli\GIT\In_House_SQL\InHousePrint\ARCHIVE_G_Folder\tools\inhouse_database_cli.py`

These files may contain the actual database connection and query logic that needs to be adapted.

---

## Solution Options

### Option 1: Create Missing Implementation (Recommended)

**Steps:**
1. Review existing database code in `In_House_SQL` workspace
2. Create `tools/implementations/sql_database.py`
3. Implement the 5 functions with proper error handling
4. Add database connection logic (SQL Server credentials)
5. Test with registry validation

**Template:**
```python
# tools/implementations/sql_database.py
import pyodbc
from typing import Dict, Any, Optional

def _get_db_connection(**kwargs):
    """Get Fred database connection with credential injection"""
    # Extract credentials from kwargs or environment
    # Return pyodbc connection
    pass

def db_execute_query(query_name: str, params: dict = None, **kwargs) -> Dict[str, Any]:
    """Execute pre-built query from QueryLibrary"""
    try:
        conn = _get_db_connection(**kwargs)
        # Execute query logic
        return {"success": True, "data": results}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

### Option 2: Use Existing Database Tools from In_House_SQL

**Steps:**
1. Copy/import from `In_House_SQL` workspace
2. Adapt to registry format (kwargs, credential injection)
3. Place in `tools/implementations/sql_database.py`
4. Test integration

### Option 3: Create Temporary Stub (Quick Fix)

**For immediate testing:**
```python
# tools/implementations/sql_database.py
def db_execute_query(**kwargs):
    return {"success": False, "error": "Implementation in progress"}

def db_get_available_queries(**kwargs):
    return {"success": False, "error": "Implementation in progress"}

def db_calculate_quote(**kwargs):
    return {"success": False, "error": "Implementation in progress"}

def db_get_business_summary(**kwargs):
    return {"success": False, "error": "Implementation in progress"}

def db_get_stock_levels(**kwargs):
    return {"success": False, "error": "Implementation in progress"}
```

This allows tools to execute without crashing, but returns "not implemented" message.

---

## Expected Behavior After Fix

### Before (Current - Broken)
```python
# AI calls tool
result = registry.execute_tool(
    tool_name="db_execute_query",
    query_name="client_order_history",
    params={"client_name": "Simply Signs"}
)

# Result:
# ValueError: Tool not found: db_execute_query
```

### After (Fixed)
```python
# AI calls tool
result = registry.execute_tool(
    tool_name="db_execute_query",
    query_name="client_order_history",
    params={"client_name": "Simply Signs"}
)

# Result:
# {
#   "success": True,
#   "query_name": "client_order_history",
#   "data": [
#     {"JobID": 12345, "Date": "2024-01-15", "Product": "Corflute A-Frame", ...},
#     {"JobID": 12389, "Date": "2024-03-22", "Product": "Corflute Sign", ...}
#   ],
#   "rows": 2,
#   "columns": ["JobID", "Date", "Product", "Quantity", "Price"]
# }
```

---

## Registry Loading Behavior

### How Registry Finds Implementations

From `registry_v3.py`:

```python
def _load_from_implementations(self) -> None:
    """Load from tools/implementations/ - FALLBACK for non-Google tools"""
    
    # Special modules loaded with individual function registration
    special_modules = ["sql_database", "meta_tools"]
    
    for module_name in special_modules:
        if module_name in impl_files:  # ← Checks if .py file exists
            module = importlib.import_module(f"tools.implementations.{module_name}")
            
            # Register each function individually
            for attr_name in dir(module):
                if not attr_name.startswith('_'):
                    attr = getattr(module, attr_name)
                    if callable(attr) and attr_name in self.tools:
                        self.implementations[attr_name] = attr  # ← Function stored
```

**Key Points:**
- Registry looks for `tools/implementations/sql_database.py`
- Extracts all functions (callable, non-private)
- Registers each function by name in `self.implementations`
- Tools must have matching names: `db_execute_query` in schema = `db_execute_query()` function

---

## Testing After Implementation

```python
# Test 1: Verify registry loads
from tools.registry_v3 import RegistryV3
registry = RegistryV3()

# Check implementations loaded
print("sql_database" in registry.implementations)  # Should be True
print("db_execute_query" in registry.implementations)  # Should be True

# Test 2: Execute tool
result = registry.execute_tool(
    tool_name="db_execute_query",
    query_name="test_query",
    _user_id=14
)
print(result)  # Should not raise ValueError

# Test 3: List tools
tools = registry.list_tools_by_platform("inhouse_database")
print(f"Found {len(tools)} tools")  # Should be 5

# Test 4: Get function
func = registry.get_tool_function("db_execute_query")
print(f"Function: {func}")  # Should not be None
```

---

## Dependencies Required

For SQL Server connection:
```bash
pip install pyodbc
```

Connection string format:
```python
conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=your-server.database.windows.net;"
    "DATABASE=fred_database;"
    "UID=username;"
    "PWD=password"
)
```

---

## Next Steps

1. **Immediate**: Create stub implementation to prevent crashes
2. **Short-term**: Review existing Fred database code in `In_House_SQL`
3. **Long-term**: Implement full QueryLibrary integration with:
   - Pre-built query catalog
   - Parameter validation
   - Result formatting
   - Error handling
   - Credential injection support

---

## Additional Notes

### Why AI Couldn't Find Tools

The conversation shows AI tried:
1. `inhouse_get_domain_guide` → Not found (incorrect tool name)
2. `search_tools(query="inhouse database SQL")` → 0 matches (tool names don't contain "SQL")
3. `list_available_platforms()` → Shows "inhouse_database" exists ✅
4. `list_platform_tools(platform="inhouse_database")` → Shows 5 tools ✅
5. `db_get_available_queries()` → Execution fails (no implementation) ❌

**Correct Discovery Flow Should Be:**
```
User: "Search Fred database for Simply Signs jobs"
  ↓
AI: list_available_platforms() → sees "inhouse_database"
  ↓
AI: list_platform_tools(platform="inhouse_database") → sees db_execute_query
  ↓
AI: get_tool_schema(tool_name="db_execute_query") → learns parameters
  ↓
AI: execute_tool(tool_name="db_execute_query", ...) → Gets results ✅
```

Currently fails at last step due to missing implementation.

---

## Schema vs Implementation Matrix

| Tool Name | Schema Exists | Implementation Exists | Status |
|-----------|--------------|---------------------|---------|
| `db_execute_query` | ✅ | ❌ | BROKEN |
| `db_get_available_queries` | ✅ | ❌ | BROKEN |
| `db_calculate_quote` | ✅ | ❌ | BROKEN |
| `db_get_business_summary` | ✅ | ❌ | BROKEN |
| `db_get_stock_levels` | ✅ | ❌ | BROKEN |

**Required**: Create `tools/implementations/sql_database.py` with all 5 functions.

---

## Contact & Resources

- **Schema File**: `tools/schemas/sql_database_tools.json`
- **Missing File**: `tools/implementations/sql_database.py`
- **Registry Code**: `tools/registry_v3.py` (lines 238-251, 340-393, 520-523)
- **Related Code**: `In_House_SQL` workspace (database connection logic)
- **Error Log**: See console output with "Tool not found: db_execute_query"

---

**Status**: Implementation required to enable Fred database access for AI agents.
