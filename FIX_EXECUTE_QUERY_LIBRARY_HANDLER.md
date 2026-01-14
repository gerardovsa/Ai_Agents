# FIX: Add execute_query_library Handler to ToolUseAgent

## Issue
- Tool `execute_query_library` is registered in RegistryV3 ✅
- Schema defines tool as `execute_query_library` ✅  
- BUT ToolUseAgent._execute_client_tool() only has `get_query_from_library` handler ❌
- Result: "Unknown tool: execute_query_library" error

## Solution
Add execute_query_library handler after get_available_queries (line ~1640)

**Location:** UI/modules_external/quote-calculator/backend/tool_use_agent.py

**Add after line 1635** (after the get_available_queries handler):

```python
elif tool_name == "execute_query_library":
    # Execute pre-built query from library
    query_name = tool_input["query_name"]
    parameters = tool_input.get("parameters", {})
    
    self._print_and_log(f"QUERY NAME: {query_name}")
    self._print_and_log(f"PARAMETERS:")
    self._print_and_log(json.dumps(parameters, indent=2))
    self._print_and_log("")
    
    try:
        # Execute query via query library
        result = self.query_library.execute_query(query_name, **parameters)
        
        self._print_and_log(f" QUERY RESULT:")
        self._print_and_log(f"   Query: {result.get('query_name', query_name)}")
        self._print_and_log(f"   Rows: {len(result.get('data', []))}")
        self._print_and_log(f"   Category: {result.get('metadata', {}).get('category', 'N/A')}")
        
        # Format result
        result_data = {
            "success": True,
            "query_name": query_name,
            "parameters_used": result.get("parameters_used", parameters),
            "data": result.get("data", []),
            "metadata": result.get("metadata", {})
        }
        
        # Emit client_tool_execution event
        self._log_event("client_tool_execution", {
            "tool_name": tool_name,
            "tool_input": tool_input,
            "result": result_data,
            "summary": f"Executed query '{query_name}': {len(result.get('data', []))} rows returned"
        })
        
        return result_data
        
    except Exception as e:
        error_msg = f"Query execution failed: {str(e)}"
        self._print_and_log(f" ERROR: {error_msg}")
        
        return {
            "success": False,
            "error": error_msg,
            "query_name": query_name,
            "parameters": parameters
        }
```

## Testing
After adding the handler, test with:

```python
from UI.modules_external.inhouse-print.implementations.inhouse_wrapper import _get_agent

agent = _get_agent()

# Test execute_query_library
result = agent._execute_client_tool('execute_query_library', {
    'query_name': 'sales_trend_by_month',
    'parameters': {'months': 6}
})

print(f"Success: {result.get('success')}")
print(f"Rows: {len(result.get('data', []))}")
```

Expected: Success with data rows (not "Unknown tool" error)

## Files to Update

1. **UI/modules_external/quote-calculator/backend/tool_use_agent.py**
   - Add handler around line 1640 (after get_available_queries)
   
2. **Test again:**
   - Run: `python test_all_77_queries.py`
   - Expected: 77/77 queries pass (not 0/77)

## Why This Fix Works

**Before:**
- Schema says: `execute_query_library` (what AI calls)
- ToolUseAgent has: `get_query_from_library` (internal name)
- Mismatch causes "Unknown tool" error

**After:**
- Schema says: `execute_query_library` ✅
- ToolUseAgent has: `execute_query_library` ✅
- Names match, tool works ✅

**Architecture:**
- Tool IS registered in RegistryV3 (module plugin system) ✅
- inhouse_wrapper.py routes calls to ToolUseAgent._execute_client_tool() ✅
- ToolUseAgent now has correct handler name ✅
- Complete execution path works end-to-end ✅
