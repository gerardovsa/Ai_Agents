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
    print(f"   Available tools: {len(agent.available_tools) if hasattr(agent, 'available_tools') else 'N/A'}")
    
    # Check if tool exists in agent
    has_tool = False
    if hasattr(agent, 'available_tools'):
        has_tool = 'execute_query_library' in agent.available_tools
    elif hasattr(agent, 'tools'):
        has_tool = 'execute_query_library' in agent.tools
    
    if has_tool:
        print("✅ execute_query_library in ToolUseAgent")
    else:
        print("❌ execute_query_library NOT in ToolUseAgent")
        
        # Show difference
        agent_tool_count = len(getattr(agent, 'available_tools', getattr(agent, 'tools', [])))
        print(f"\n   ToolUseAgent vs RegistryV3 tool count:")
        print(f"   ToolUseAgent: {agent_tool_count} tools")
        print(f"   RegistryV3: {len(registry.tools)} tools")
        print(f"   Difference: {len(registry.tools) - agent_tool_count} tools")
        
except Exception as e:
    print(f"❌ ToolUseAgent check failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("DIAGNOSTIC COMPLETE")
print("=" * 80)
