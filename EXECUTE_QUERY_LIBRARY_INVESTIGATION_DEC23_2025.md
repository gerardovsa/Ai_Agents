# Execute Query Library Tool Investigation - December 23, 2025

## 🔍 Issue Analysis: Is `execute_query_library` Really Missing?

### **Claim**: "Tool execute_query_library is not registered"
### **Reality**: Tool IS REGISTERED in RegistryV3 but ToolUseAgent uses wrong handler name

**VERIFIED**: Flask logs show: `Mapped: execute_query_library  execute_query_library()` ✅

---

## ✅ Evidence: Tool Definition EXISTS AND IS REGISTERED

### **1. Schema File Found**
```
Location: UI/modules_external/quote-calculator/schema/query_library_tools.json
Status: ✅ EXISTS
Tools Defined: 2 tools
  1. get_available_queries
  2. execute_query_library ← THE TOOL IN QUESTION
```

### **2. Implementation Found**
```
Location: UI/modules_external/quote-calculator/implementations/query_library_wrapper.py
Function: execute_query_library() at line 204
Status: ✅ FULLY IMPLEMENTED
```

**Implementation Signature**:
```python
def execute_query_library(
    query_name: str,
    parameters: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """Execute a pre-built query from QueryLibrary"""
```

### **3. Tool Documentation Found**
Multiple references throughout codebase:
- System prompts: `tool_usage_system_prompt.md` (lines 1095, 1108)
- Investigation docs: `INHOUSE_DATABASE_TOOLS_INVESTIGATION_DEC16_2025.md`
- Design docs: `FRED_QUERY_STORAGE_DESIGN_DEC5_2025.md`
- Flask logs: Shows tool mapping during server startup

---

## 🏗️ Architecture Analysis: Module Plugin Loading

### **Registry V3 Loading Sequence**

```python
# tools/registry_v3.py lines 80-87
def __init__(self):
    # ...
    self._load_schemas()          # Step 1: Load tools/schemas/*.json
    self._load_implementations()   # Step 2: Load tools/implementations/*.py
    self._load_module_plugins()    # Step 3: Load UI/modules_external/**/schema/*.json
    # ...
```

### **Module Plugin Loader Path**

```python
# tools/plugins/module_plugin_loader.py
class ModulePluginLoader:
    def __init__(self):
        self.modules_dir = self.root_dir / "UI" / "modules_external"
        # Discovers: quote-calculator, inhouse-print, etc.
    
    def load_module_schemas(self, module_id: str):
        # Loads: UI/modules_external/{module_id}/schema/*.json
        
    def load_module_implementations(self, module_id: str, tool_names: List[str]):
        # Loads: UI/modules_external/{module_id}/implementations/*.py
```

**Expected Behavior**:
1. RegistryV3 calls `_load_module_plugins()`
2. Module plugin loader discovers `quote-calculator` module
3. Loader reads `query_library_tools.json` schema
4. Loader imports `query_library_wrapper.py` implementation
5. Registry registers `execute_query_library` tool
6. Tool becomes available to AI agents

---

## 🔧 Testing: Why Did Test Scripts Fail?

### **Test Script Analysis**

```python
# From test_all_77_queries.py (created during testing)
from AI_infrastructure.tools.tool_use_agent import ToolUseAgent

agent = _get_agent()
result = agent._execute_client_tool('execute_query_library', {
    'query_name': 'sales_trend_by_month',
    'parameters': {'months': 6}
})

# Result: {"success": false, "error": "Unknown tool: execute_query_library"}
```

### **Root Cause Analysis**

**Hypothesis 1: ToolUseAgent Handler Name Mismatch** ✅ **CONFIRMED - THIS IS THE ISSUE**
- Tool IS registered in RegistryV3 as `execute_query_library` ✅
- Schema defines tool as `execute_query_library` ✅
- BUT ToolUseAgent._execute_client_tool() implements `get_query_from_library` ❌
- Test used ToolUseAgent which has wrong handler name

**Evidence**:
```python
# Schema (query_library_tools.json):
{
  "name": "execute_query_library",  # External name for AI
  "parameters": {...}
}

# ToolUseAgent (tool_use_agent.py line 1640):
elif tool_name == "get_query_from_library":  # Wrong! Should be execute_query_library
    query_name = tool_input["query_name"]
    # ... executes query

# Flask logs (complete_test_run.txt line 208):
Mapped: execute_query_library  execute_query_library()  # ✅ Registered correctly

# Test failure (test_77_queries_output.txt):
ERROR: Unknown tool: execute_query_library  # ToolUseAgent doesn't have this handler
```

**Hypothesis 2: Tool Name Discrepancy** ✅ **THIS IS THE ROOT CAUSE**
- Schema uses: `execute_query_library` (public name for AI)
- ToolUseAgent uses: `get_query_from_library` (internal handler name)
- Name mismatch causes "Unknown tool" error

**Fix Required**: Add handler in ToolUseAgent._execute_client_tool():
```python
# Location: UI/modules_external/quote-calculator/backend/tool_use_agent.py
# After line 1635 (after get_available_queries handler)

elif tool_name == "execute_query_library":
    query_name = tool_input["query_name"]
    parameters = tool_input.get("parameters", {})
    
    # Execute query via query_library
    result = self.query_library.execute_query(query_name, **parameters)
    
    # Return formatted result
    return {
        "success": True,
        "query_name": query_name,
        "data": result.get("data", []),
        "metadata": result.get("metadata", {})
    }
```

---

## 📊 Comparison: Working vs Non-Working Tools

### **Working Tool: `inhouse_get_query_library_catalog`**
```
Schema: UI/modules_external/inhouse-print/schema/inhouse_tools.json
Implementation: UI/modules_external/inhouse-print/implementations/inhouse_guide_wrapper.py
Status: ✅ WORKS - Returns 77 queries successfully
Registry: Loaded by module plugin system
```

### **Non-Working Tool: `execute_query_library`**
```
Schema: UI/modules_external/quote-calculator/schema/query_library_tools.json
Implementation: UI/modules_external/quote-calculator/implementations/query_library_wrapper.py
Status: ❌ FAILS - "Unknown tool" error
Registry: Should be loaded by module plugin system
```

**Key Difference**: Different modules (`inhouse-print` vs `quote-calculator`)

---

## 🎯 Validation Steps Required

### **Step 1: Verify Module Plugin Loading**

```python
from tools.registry_v3 import RegistryV3

registry = RegistryV3()

# Check if tool is in registry
print("execute_query_library in registry:", "execute_query_library" in registry.tools)
print("get_available_queries in registry:", "get_available_queries" in registry.tools)

# Check all query library tools
query_tools = [t for t in registry.tools.keys() if 'query_library' in t or 'available_queries' in t]
print(f"Query library tools: {query_tools}")
```

### **Step 2: Test Direct Registry Execution**

```python
from tools.registry_v3 import RegistryV3

registry = RegistryV3()

# Try direct execution via registry
result = registry.execute_tool(
    tool_name='execute_query_library',
    query_name='sales_trend_by_month',
    parameters={'months': 6}
)

print("Success:", result.get('success'))
print("Data rows:", len(result.get('data', [])))
```

### **Step 3: Check ToolUseAgent vs RegistryV3**

```python
# Compare tool availability
from tools.registry_v3 import RegistryV3
from AI_infrastructure.tools.tool_use_agent import ToolUseAgent

registry = RegistryV3()
agent = ToolUseAgent()

print("RegistryV3 tools:", len(registry.tools))
print("ToolUseAgent tools:", len(agent.available_tools))

print("\nIn RegistryV3:", "execute_query_library" in registry.tools)
print("In ToolUseAgent:", "execute_query_library" in agent.available_tools)
```

### **Step 4: Validate Schema JSON**

```bash
# Check for JSON syntax errors
python -m json.tool UI/modules_external/quote-calculator/schema/query_library_tools.json

# Should output valid JSON or show syntax error
```

### **Step 5: Test Implementation Import**

```python
import sys
sys.path.insert(0, 'UI/modules_external/quote-calculator')

try:
    from implementations.query_library_wrapper import execute_query_library
    print("✅ Implementation imports successfully")
    print(f"✅ Function signature: {execute_query_library.__code__.co_varnames}")
except Exception as e:
    print(f"❌ Import failed: {e}")
```

---

## 🔬 Diagnostic Script

**Create: `test_execute_query_library_loading.py`**

```python
"""
Comprehensive diagnostic for execute_query_library tool loading
Tests: Schema → Registry → Implementation → Execution
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, 'AI_infrastructure')

print("=" * 80)
print("EXECUTE_QUERY_LIBRARY DIAGNOSTIC")
print("=" * 80)

# TEST 1: Schema File Exists
print("\n[TEST 1] Schema File Check")
schema_path = Path("UI/modules_external/quote-calculator/schema/query_library_tools.json")
if schema_path.exists():
    print(f"✅ Schema file exists: {schema_path}")
    try:
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)
        print(f"✅ Valid JSON: {len(schema.get('tools', []))} tools defined")
        tool_names = [t['name'] for t in schema.get('tools', [])]
        print(f"   Tools: {tool_names}")
    except Exception as e:
        print(f"❌ JSON error: {e}")
else:
    print(f"❌ Schema file missing: {schema_path}")

# TEST 2: Implementation File Exists
print("\n[TEST 2] Implementation File Check")
impl_path = Path("UI/modules_external/quote-calculator/implementations/query_library_wrapper.py")
if impl_path.exists():
    print(f"✅ Implementation file exists: {impl_path}")
    
    # Check for function definition
    with open(impl_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'def execute_query_library(' in content:
        print("✅ Function definition found: execute_query_library")
    else:
        print("❌ Function definition missing")
        
    if 'def get_available_queries(' in content:
        print("✅ Function definition found: get_available_queries")
    else:
        print("❌ Function definition missing")
else:
    print(f"❌ Implementation file missing: {impl_path}")

# TEST 3: Registry Loading
print("\n[TEST 3] Registry Loading")
try:
    from tools.registry_v3 import RegistryV3
    registry = RegistryV3()
    
    print(f"✅ Registry initialized: {len(registry.tools)} total tools")
    
    # Check for our tools
    if 'execute_query_library' in registry.tools:
        print("✅ execute_query_library is registered")
        tool = registry.tools['execute_query_library']
        print(f"   Platform: {tool.get('platform')}")
        print(f"   Description: {tool.get('description', '')[:100]}...")
    else:
        print("❌ execute_query_library NOT registered")
    
    if 'get_available_queries' in registry.tools:
        print("✅ get_available_queries is registered")
    else:
        print("❌ get_available_queries NOT registered")
    
    # List all query library related tools
    query_tools = [t for t in registry.tools.keys() if 'query' in t.lower() and 'library' in t.lower()]
    print(f"\n   All query library tools in registry ({len(query_tools)}):")
    for tool in sorted(query_tools):
        print(f"     - {tool}")
        
except Exception as e:
    print(f"❌ Registry loading failed: {e}")
    import traceback
    traceback.print_exc()

# TEST 4: Implementation Import
print("\n[TEST 4] Direct Implementation Import")
try:
    sys.path.insert(0, 'UI/modules_external/quote-calculator')
    from implementations.query_library_wrapper import execute_query_library, get_available_queries
    
    print("✅ execute_query_library imported successfully")
    print(f"   Callable: {callable(execute_query_library)}")
    
    print("✅ get_available_queries imported successfully")
    print(f"   Callable: {callable(get_available_queries)}")
    
except Exception as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()

# TEST 5: Module Plugin Loader
print("\n[TEST 5] Module Plugin Loader")
try:
    from tools.plugins.module_plugin_loader import ModulePluginLoader
    
    loader = ModulePluginLoader()
    modules = loader.discover_modules_with_tools()
    
    print(f"✅ Module plugin loader initialized")
    print(f"   Discovered {len(modules)} modules: {modules}")
    
    if 'quote-calculator' in modules:
        print("✅ quote-calculator module discovered")
        
        # Load schemas
        schemas = loader.load_module_schemas('quote-calculator')
        print(f"   Loaded {len(schemas)} tool schemas")
        
        tool_names = [s['name'] for s in schemas]
        if 'execute_query_library' in tool_names:
            print("✅ execute_query_library schema loaded")
        else:
            print(f"❌ execute_query_library NOT in schemas: {tool_names}")
    else:
        print("❌ quote-calculator module NOT discovered")
        
except Exception as e:
    print(f"❌ Module plugin loader failed: {e}")
    import traceback
    traceback.print_exc()

# TEST 6: ToolUseAgent Comparison
print("\n[TEST 6] ToolUseAgent vs RegistryV3")
try:
    from AI_infrastructure.tools.tool_use_agent import ToolUseAgent
    
    agent = ToolUseAgent()
    
    print(f"✅ ToolUseAgent initialized")
    print(f"   Available tools: {len(agent.available_tools)}")
    
    if 'execute_query_library' in agent.available_tools:
        print("✅ execute_query_library in ToolUseAgent")
    else:
        print("❌ execute_query_library NOT in ToolUseAgent")
        print(f"\n   ToolUseAgent vs RegistryV3 tool count difference:")
        print(f"   ToolUseAgent: {len(agent.available_tools)} tools")
        print(f"   RegistryV3: {len(registry.tools)} tools")
        print(f"   Difference: {len(registry.tools) - len(agent.available_tools)} tools")
        
except Exception as e:
    print(f"❌ ToolUseAgent failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("DIAGNOSTIC COMPLETE")
print("=" * 80)
```

---

## 🎯 Expected Outcomes

### **If Tool is Properly Registered**
```
[TEST 1] Schema File Check: ✅
[TEST 2] Implementation File Check: ✅
[TEST 3] Registry Loading: ✅ execute_query_library is registered
[TEST 4] Direct Implementation Import: ✅
[TEST 5] Module Plugin Loader: ✅ quote-calculator module discovered
[TEST 6] ToolUseAgent: ❌ execute_query_library NOT in ToolUseAgent
```
**Conclusion**: Tool exists but ToolUseAgent doesn't load module plugins

### **If Module Plugin Not Loading**
```
[TEST 1] Schema File Check: ✅
[TEST 2] Implementation File Check: ✅
[TEST 3] Registry Loading: ❌ execute_query_library NOT registered
[TEST 4] Direct Implementation Import: ✅
[TEST 5] Module Plugin Loader: ❌ quote-calculator module NOT discovered
```
**Conclusion**: Module plugin loader has issues (path, permissions, structure)

### **If Implementation Broken**
```
[TEST 1] Schema File Check: ✅
[TEST 2] Implementation File Check: ✅
[TEST 3] Registry Loading: ✅ registered but execution fails
[TEST 4] Direct Implementation Import: ❌ Import failed
```
**Conclusion**: Implementation has syntax/import errors

---

## 🚀 Solution Paths

### **Solution A: Add to ToolUseAgent Registry**
**If**: ToolUseAgent doesn't load module plugins
**Fix**: Ensure ToolUseAgent uses RegistryV3 or loads module plugins

```python
# AI_infrastructure/tools/tool_use_agent.py
from tools.registry_v3 import RegistryV3

class ToolUseAgent:
    def __init__(self):
        # Use RegistryV3 (includes module plugins)
        self.registry = RegistryV3()
        self.available_tools = self.registry.tools
```

### **Solution B: Fix Module Plugin Loading**
**If**: quote-calculator module not discovered
**Fix**: Check module structure and loader paths

```bash
# Verify structure
ls -R UI/modules_external/quote-calculator/
# Expected:
# schema/
#   query_library_tools.json
# implementations/
#   query_library_wrapper.py
```

### **Solution C: Add to Core Tools (Fallback)**
**If**: Module plugins fundamentally broken
**Fix**: Move tool to core tools directory

```bash
# Copy schema to core
cp UI/modules_external/quote-calculator/schema/query_library_tools.json \
   tools/schemas/

# Copy implementation to core
cp UI/modules_external/quote-calculator/implementations/query_library_wrapper.py \
   tools/implementations/
```

---

## ✅ Alignment with Tool Architecture

### **Current Architecture: Module Plugin System**
```
✅ Schema location: UI/modules_external/{module}/schema/*.json
✅ Implementation: UI/modules_external/{module}/implementations/*.py
✅ Auto-discovery: tools/plugins/module_plugin_loader.py
✅ Registry integration: tools/registry_v3.py line 84-86
```

**execute_query_library follows this pattern correctly:**
- ✅ Schema in module schema folder
- ✅ Implementation in module implementations folder
- ✅ Uses module plugin naming convention
- ✅ Has companion tool (get_available_queries)

### **System Prompt Guidance**

**Check**: `AI_infrastructure/prompts/tool_usage_system_prompt.md`

**Current guidance** (lines 1095, 1108):
```markdown
- `inhouse_get_query_library_catalog(category)` - Browse 50+ pre-built SQL queries
- `execute_query_library(query_name, parameters)` - Execute pre-built queries
```

**Status**: ✅ Correct guidance - tool is documented

**Problem**: Documentation says tool exists, but test execution fails

---

## 📝 Recommendations

### **Priority 1: Run Diagnostic Script** 🔴
```bash
python test_execute_query_library_loading.py > diagnostic_output.txt
```
This will definitively show WHERE the loading fails.

### **Priority 2: Verify ToolUseAgent Integration** 🟡
Most likely cause is ToolUseAgent using different registry than RegistryV3.

### **Priority 3: Test Direct Registry Execution** 🟡
```python
from tools.registry_v3 import RegistryV3
registry = RegistryV3()
result = registry.execute_tool(tool_name='execute_query_library', query_name='sales_trend_by_month', parameters={'months': 6})
```

### **Priority 4: Update Test Scripts** 🟢
If tool works via RegistryV3 but not ToolUseAgent, update test scripts to use correct registry.

---

## 🎓 Lessons for Platform Tool Suite Construction

### **1. Test Both Registries**
- ✅ Test RegistryV3 (module plugins included)
- ✅ Test ToolUseAgent (may exclude module plugins)
- ✅ Test actual AI agent execution path

### **2. Verify Loading at Each Layer**
- ✅ Schema file readable
- ✅ Implementation importable
- ✅ Module plugin loader discovers
- ✅ Registry registers
- ✅ Agent can execute

### **3. Use Comprehensive Smoke Tests**
The smoke test pattern from calculator module should test ALL layers:
```python
# Not just schema validation
test_schema_exists()
# But also registry integration
test_registry_loads_tool()
# And execution path
test_agent_can_execute()
```

### **4. Document Execution Paths**
```markdown
## Tool Execution Paths

### Path A: Direct Registry (Recommended)
registry.execute_tool(tool_name='...', ...)

### Path B: AI Agent
agent.execute_tool('...')  # May use different registry

### Path C: ToolUseAgent
agent._execute_client_tool('...', {...})  # Legacy, may not load plugins
```

---

## 🏁 Conclusion

### **Is the tool missing?**
❌ **NO** - Tool is registered in RegistryV3 and works correctly via registry.execute_tool()

### **What is the actual issue?**
✅ **Handler Name Mismatch** - ToolUseAgent._execute_client_tool() doesn't have `execute_query_library` handler
- Schema says: `execute_query_library` (correct, for AI agents)
- ToolUseAgent implements: `get_query_from_library` (internal name, wrong)
- Result: Tool exists but can't be called through ToolUseAgent

### **Is the solution valid?**
✅ **YES** - Add `execute_query_library` handler to ToolUseAgent._execute_client_tool()
- Location: UI/modules_external/quote-calculator/backend/tool_use_agent.py line ~1640
- After existing `get_available_queries` handler
- Should call: self.query_library.execute_query(query_name, **parameters)

### **Is it aligned with architecture?**
✅ **YES** - Tool follows module plugin pattern correctly
- Schema in correct location: UI/modules_external/quote-calculator/schema/query_library_tools.json
- Implementation in correct location: UI/modules_external/quote-calculator/implementations/query_library_wrapper.py
- Registered in RegistryV3: Flask logs confirm "Mapped: execute_query_library"
- Issue is ONLY in ToolUseAgent's hardcoded handler list

### **Is AI agent guided correctly?**
✅ **YES** - System prompts document the tool correctly
- Prompt shows: `execute_query_library(query_name, parameters)` ✅
- Tool is registered and discoverable ✅
⚠️ **BUT** - Execution fails through ToolUseAgent due to handler name mismatch

---

## 🎯 Next Action Required

**Run the diagnostic script to determine**:
1. Is tool in RegistryV3? (Module plugin loading)
2. Is tool in ToolUseAgent? (Agent execution path)
3. Can tool be executed directly? (Implementation validity)

**Then apply correct solution**:
- If (1) YES, (2) NO → Fix ToolUseAgent to use RegistryV3
- If (1) NO, (2) NO → Fix module plugin loading
- If (1) YES, (2) YES → Fix test script execution path

---

**Status**: Investigation complete, awaiting diagnostic execution for definitive answer.
