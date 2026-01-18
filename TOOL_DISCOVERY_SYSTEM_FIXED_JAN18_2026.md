# Tool Discovery System Fixed - January 18, 2026

## Issues Identified

### 1. **Missing Meta/Discovery Tools** ❌
The AI agent couldn't discover tools because meta-tools were not registered:
- `list_platform_tools` - List tools by platform
- `search_tools` - Search tools by keyword
- `get_tool_schema` - Get parameter details for a tool  
- `list_available_platforms` - List all available platforms

**Root Cause:** These tools existed in code (`intelligent_discovery.py`) but were never exposed as callable tools in the registry.

### 2. **Wrong Calculator Name** ❌
InHouse guide listed incorrect calculator name:
- ❌ Listed: `calculate_corflute_signs`
- ✅ Actual: `calculate_corflute_signs_shopify`

**Root Cause:** Guide content in `inhouse_guide_wrapper.py` was outdated.

### 3. **Corflute Not in Wrapper** ❌
The InHouse wrapper didn't support corflute signs:
- Only supported: business_cards, flyers, folded_flyers, perfect_bound_books, wire_bound, spiral_bound
- Missing: corflute_signs

---

## How Tool Access Works (No ToolUseAgent Needed)

```
┌─────────────────────────────────────────────────────────────┐
│                    AI AGENT REQUEST                         │
│         "I need to calculate a corflute quote"              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              FLASK APP (flask_app.py)                       │
│  - Receives Anthropic API tool call                         │
│  - Extracts tool_name and parameters from JSON              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│          REGISTRY V3 (tools/registry_v3.py)                 │
│  - registry.execute_tool(tool_name="calculate_...", ...)    │
│  - Looks up tool in self.tools dict                         │
│  - Gets function from self.implementations                  │
│  - Calls function with parameters                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│    TOOL IMPLEMENTATION (with @tool_executor decorator)      │
│  - Function executes (database query, calculation, etc.)    │
│  - Returns result dict                                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│           RESULT SENT BACK TO AI AGENT                      │
└─────────────────────────────────────────────────────────────┘
```

**Key Points:**
- **No ToolUseAgent class** - Direct function calls via registry
- **@tool_executor() decorator** - Auto-registers functions as tools
- **Module plugin system** - Tools discovered from `UI/modules_external/*/tools/*.json`
- **Registry V3** - Central dispatcher for all tool execution

---

## Solutions Applied

### ✅ Created Meta Tools
**Files Created:**
1. **`UI/modules_external/quote-calculator/tools/meta_tools.json`**
   - Tool definitions for discovery system
   - 4 meta tools defined

2. **`UI/modules_external/quote-calculator/implementations/meta_tools_wrapper.py`**
   - Implementation with @tool_executor decorators
   - Functions:
     ```python
     @tool_executor()
     def list_platform_tools(platform: str)
     
     @tool_executor()
     def search_tools(query: str)
     
     @tool_executor()
     def get_tool_schema(tool_name: str)
     
     @tool_executor()
     def list_available_platforms()
     ```

### ✅ Fixed InHouse Guide
**File Modified:** `UI/modules_external/inhouse-print/implementations/inhouse_guide_wrapper.py`

**Changes:**
```python
# BEFORE
"available_calculators": {
    "corflute_signs": "calculate_corflute_signs"  # ❌ Wrong
}

# AFTER  
"available_calculators": {
    "corflute_signs": "calculate_corflute_signs_shopify"  # ✅ Correct
}
```

### ✅ Added Corflute Support to Wrapper
**File Modified:** `UI/modules_external/inhouse-print/implementations/inhouse_wrapper.py`

**Changes Made (2 locations):**
```python
# BEFORE - Only 6 calculators
calculator_map = {
    "business_cards": "calculate_business_cards",
    "flyers": "calculate_folded_flyers_shopify",
    "folded_flyers": "calculate_folded_flyers_shopify",
    "perfect_bound_books": "calculate_perfect_bound_books_shopify",
    "wire_bound": "calculate_wire_bound_books_shopify",
    "spiral_bound": "calculate_spiral_bound_books_shopify"
}

# AFTER - 7 calculators (corflute added)
calculator_map = {
    "business_cards": "calculate_business_cards",
    "flyers": "calculate_folded_flyers_shopify",
    "folded_flyers": "calculate_folded_flyers_shopify",
    "perfect_bound_books": "calculate_perfect_bound_books_shopify",
    "wire_bound": "calculate_wire_bound_books_shopify",
    "spiral_bound": "calculate_spiral_bound_books_shopify",
    "corflute_signs": "calculate_corflute_signs_shopify"  # ✅ Added
}
```

**Functions Updated:**
1. `inhouse_get_calculator_requirements()` - Line ~350
2. `inhouse_calculate_quote()` - Line ~490

---

## Testing the Fixes

### Test 1: Discovery Tools
```python
# Test list_platform_tools
result = registry.execute_tool(
    tool_name="list_platform_tools",
    platform="quote_calculator"
)
# Should return all quote calculator tools including calculate_corflute_signs_shopify

# Test search_tools
result = registry.execute_tool(
    tool_name="search_tools",
    query="corflute"
)
# Should find calculate_corflute_signs_shopify

# Test get_tool_schema
result = registry.execute_tool(
    tool_name="get_tool_schema",
    tool_name="calculate_corflute_signs_shopify"
)
# Should return complete parameter schema
```

### Test 2: Corflute Quote Calculation
```python
# Test InHouse wrapper
result = registry.execute_tool(
    tool_name="inhouse_get_calculator_requirements",
    product_type="corflute_signs"
)
# Should return parameter requirements (no longer "Unknown product type")

result = registry.execute_tool(
    tool_name="inhouse_calculate_quote",
    product_type="corflute_signs",
    parameters={
        "size": "600x900mm",
        "quantity": 7,
        "thickness": "5mm",
        "sides": 1
    }
)
# Should return quote calculation
```

---

## Module Plugin Loading Process

```
1. Flask starts → imports RegistryV3
2. RegistryV3.__init__() runs
3. Calls _load_module_plugins()
4. Scans UI/modules_external/ for modules
5. For each module:
   - Finds tools/*.json files
   - Loads tool definitions
   - Finds implementations/*.py files
   - Registers @tool_executor functions
6. Tools available via registry.execute_tool()
```

**Example Module Structure:**
```
UI/modules_external/quote-calculator/
├── tools/
│   ├── calculator_tools.json         (37 calculator definitions)
│   └── meta_tools.json                (4 meta tool definitions) ✅ NEW
├── implementations/
│   ├── calculator_wrapper.py          (Calculator implementations)
│   └── meta_tools_wrapper.py          (Meta tool implementations) ✅ NEW
└── backend/
    └── complete_calculator_implementation.py
```

---

## Why This Fix Works

### Before:
1. ❌ AI tries `list_platform_tools()` → **Tool not found**
2. ❌ AI tries `calculate_corflute_signs` → **Tool not found**
3. ❌ AI tries `inhouse_get_calculator_requirements("corflute_signs")` → **Unknown product type**
4. ❌ AI gives up or uses historical data estimate

### After:
1. ✅ AI calls `list_platform_tools("quote_calculator")` → **Gets full tool list**
2. ✅ AI sees `calculate_corflute_signs_shopify` in list
3. ✅ AI calls `get_tool_schema("calculate_corflute_signs_shopify")` → **Gets parameters**
4. ✅ AI calls calculator with correct parameters → **Gets accurate quote**

---

## Key Architectural Notes

### No ToolUseAgent Class Needed
The previous architecture used `ToolUseAgent` class from `quote-calculator/backend/tool_use_agent.py`. This caused issues:
- Circular import dependencies on Render deployment
- Expensive initialization (database + calculator + query library)
- Singleton pattern complexity

**New Architecture (Current):**
- Direct function calls via `@tool_executor()` decorator
- Registry V3 handles all dispatching
- No class instantiation needed
- Simpler, faster, more reliable

### @tool_executor() Pattern
```python
from tools.registry_v3 import tool_executor

@tool_executor()
def my_tool_name(param1: str, param2: int = 10):
    """Tool description for AI agent."""
    # Import inside function to avoid circular imports
    from AI_infrastructure.shared.database_utils import execute_query
    
    result = execute_query("SELECT ...", ())
    return {"success": True, "data": result}
```

**Auto-Registration:**
- Decorator adds function to registry.tools
- Function name matches tool definition name in JSON
- No manual registration needed

---

## Files Modified Summary

| File | Changes | Purpose |
|------|---------|---------|
| `UI/modules_external/quote-calculator/tools/meta_tools.json` | ✅ Created | Define 4 meta tools |
| `UI/modules_external/quote-calculator/implementations/meta_tools_wrapper.py` | ✅ Created | Implement meta tools |
| `UI/modules_external/inhouse-print/implementations/inhouse_guide_wrapper.py` | ✅ Modified | Fix calculator names |
| `UI/modules_external/inhouse-print/implementations/inhouse_wrapper.py` | ✅ Modified | Add corflute support (2 locations) |

---

## Next Steps

1. **Restart Flask server** to load new meta tools
2. **Test discovery tools** with AI agent
3. **Test corflute quote** calculation
4. **Verify no ToolUseAgent imports** (should be disabled)
5. **Monitor logs** for tool registration success

---

## Related Documentation

- `.github/copilot-instructions.md` - Main project architecture
- `INHOUSE_TOOLS_COMPLETE_FIX_JAN13_2026.md` - InHouse tool fixes
- `tools/registry_v3.py` - Registry implementation
- `tools/module_plugin.py` - Module loading system
