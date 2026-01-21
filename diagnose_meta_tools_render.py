"""
RENDER META-TOOLS DIAGNOSTIC SCRIPT
Run this on Render to diagnose why meta-tools aren't registering

Usage:
    python diagnose_meta_tools_render.py
"""

import sys
from pathlib import Path

# Add project root to path
root_dir = Path(__file__).parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

print("=" * 80)
print("RENDER META-TOOLS DIAGNOSTIC")
print("=" * 80)

# Step 1: Check if meta_tools.json schema exists
print("\n[STEP 1] Checking meta_tools.json schema file...")
schema_path = root_dir / "tools" / "schemas" / "meta_tools.json"
if schema_path.exists():
    print(f"✅ Schema file exists: {schema_path}")
    with open(schema_path, 'r', encoding='utf-8') as f:
        import json
        schema_data = json.load(f)
        tool_names = [t['name'] for t in schema_data.get('tools', [])]
        print(f"✅ Schema defines {len(tool_names)} tools:")
        for name in tool_names:
            print(f"   - {name}")
else:
    print(f"❌ Schema file NOT FOUND: {schema_path}")
    sys.exit(1)

# Step 2: Check if meta_tools.py implementation exists
print("\n[STEP 2] Checking meta_tools.py implementation file...")
impl_path = root_dir / "tools" / "implementations" / "meta_tools.py"
if impl_path.exists():
    print(f"✅ Implementation file exists: {impl_path}")
    
    # Count functions in the file
    try:
        import tools.implementations.meta_tools as meta_tools_module
        func_names = [name for name in dir(meta_tools_module) if not name.startswith('_') and callable(getattr(meta_tools_module, name))]
        print(f"✅ Implementation has {len(func_names)} callable functions:")
        for name in func_names:
            print(f"   - {name}")
    except Exception as e:
        print(f"❌ Failed to import meta_tools module: {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"❌ Implementation file NOT FOUND: {impl_path}")
    sys.exit(1)

# Step 3: Load Registry V3 and check tool registration
print("\n[STEP 3] Loading Registry V3...")
try:
    from tools.registry_v3 import get_registry
    registry = get_registry()
    print(f"✅ Registry loaded: {len(registry.tools)} total tools")
except Exception as e:
    print(f"❌ Failed to load registry: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 4: Check if meta-tools are registered
print("\n[STEP 4] Checking meta-tool registration in registry...")
meta_tool_names = [
    'list_available_platforms',
    'list_platform_tools',
    'get_tool_schema',
    'search_tools',
    'get_platform_guide',
    'recommend_tools_for_task',
    'get_workflow_steps',
    'execute_tool'
]

registered_count = 0
missing_count = 0

for tool_name in meta_tool_names:
    if tool_name in registry.tools:
        print(f"   ✅ REGISTERED: {tool_name}")
        registered_count += 1
    else:
        print(f"   ❌ MISSING: {tool_name}")
        missing_count += 1

print(f"\nSummary: {registered_count}/{len(meta_tool_names)} meta-tools registered")

if missing_count > 0:
    print(f"\n⚠️ WARNING: {missing_count} meta-tools are NOT registered!")
    print("This explains why the AI gets 'Tool not found' errors.")

# Step 5: Check if meta-tools are exposed to Anthropic API
print("\n[STEP 5] Checking if meta-tools are exposed to Anthropic API...")
try:
    anthropic_tools = registry.get_anthropic_tools()
    anthropic_tool_names = [t['name'] for t in anthropic_tools]
    
    exposed_count = 0
    hidden_count = 0
    
    for tool_name in meta_tool_names:
        if tool_name in anthropic_tool_names:
            print(f"   ✅ EXPOSED: {tool_name}")
            exposed_count += 1
        else:
            print(f"   ❌ HIDDEN: {tool_name}")
            hidden_count += 1
    
    print(f"\nSummary: {exposed_count}/{len(meta_tool_names)} meta-tools exposed to Anthropic API")
    
    if hidden_count > 0:
        print(f"\n⚠️ WARNING: {hidden_count} meta-tools are NOT exposed to AI!")
        print("The AI cannot see these tools even if they're registered.")
except Exception as e:
    print(f"❌ Failed to get Anthropic tools: {e}")
    import traceback
    traceback.print_exc()

# Step 6: Check implementations mapping
print("\n[STEP 6] Checking implementations mapping...")
meta_impl_count = 0
missing_impl_count = 0

for tool_name in meta_tool_names:
    if tool_name in registry.implementations:
        impl = registry.implementations[tool_name]
        impl_type = type(impl).__name__
        print(f"   ✅ HAS IMPL: {tool_name} → {impl_type}")
        meta_impl_count += 1
    else:
        print(f"   ❌ NO IMPL: {tool_name}")
        missing_impl_count += 1

print(f"\nSummary: {meta_impl_count}/{len(meta_tool_names)} meta-tools have implementations")

if missing_impl_count > 0:
    print(f"\n⚠️ WARNING: {missing_impl_count} meta-tools have NO implementation!")
    print("This will cause 'Tool not found' errors when executed.")

# Step 7: Final diagnosis
print("\n" + "=" * 80)
print("FINAL DIAGNOSIS")
print("=" * 80)

all_ok = (registered_count == len(meta_tool_names) and 
          exposed_count == len(meta_tool_names) and 
          meta_impl_count == len(meta_tool_names))

if all_ok:
    print("✅ ALL CHECKS PASSED - Meta-tools should work correctly!")
    print("\nIf AI still reports 'Tool not found', check:")
    print("1. System prompt is loading correctly (check Flask startup logs)")
    print("2. AI is using execute_tool() wrapper (not calling meta-tools directly)")
else:
    print("❌ ISSUES DETECTED - Meta-tools will NOT work correctly!")
    print("\nProblems found:")
    if registered_count < len(meta_tool_names):
        print(f"   - {missing_count} tools not registered in registry")
    if exposed_count < len(meta_tool_names):
        print(f"   - {hidden_count} tools not exposed to Anthropic API")
    if meta_impl_count < len(meta_tool_names):
        print(f"   - {missing_impl_count} tools missing implementations")
    
    print("\nLikely causes:")
    print("   - meta_tools.json schema not loading correctly")
    print("   - meta_tools.py implementation not importing correctly")
    print("   - Registry V3 initialization error")

print("=" * 80)
