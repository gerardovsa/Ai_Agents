"""Debug feedback tools loading"""
from tools.registry_v3 import RegistryV3
import json

r = RegistryV3()

print("\n" + "="*80)
print("FEEDBACK TOOLS ANALYSIS")
print("="*80)

# Check all tools with 'feedback' in name
print("\n1. Tools with 'feedback' in name:")
feedback_tools = {name: tool for name, tool in r.tools.items() if 'feedback' in name.lower()}
print(f"   Found: {len(feedback_tools)} tools")
for name in feedback_tools:
    print(f"   - {name}")

# Check fetch_user_instructions specifically
print("\n2. Checking fetch_user_instructions:")
if 'fetch_user_instructions' in r.tools:
    tool = r.tools['fetch_user_instructions']
    print(f"   ✅ EXISTS in r.tools")
    print(f"   Platform: {tool.get('platform')}")
    print(f"   Description: {tool.get('description', '')[:100]}...")
else:
    print(f"   ❌ NOT FOUND in r.tools")

# Check implementation module
print("\n3. Checking implementation module:")
import tools.implementations.user_feedback_tools as uf
functions = [f for f in dir(uf) if not f.startswith('_')]
print(f"   Functions in module: {functions}")

# Check if fetch_user_instructions is callable
if hasattr(uf, 'fetch_user_instructions'):
    print(f"   ✅ fetch_user_instructions is callable")
    result = uf.fetch_user_instructions()
    print(f"   Sample call result: {json.dumps(result, indent=2)}")
else:
    print(f"   ❌ fetch_user_instructions not found in module")

# Check schema loading
print("\n4. Checking schema file:")
import json
with open('tools/schemas/user_feedback_tools.json', 'r') as f:
    schema = json.load(f)
    tool_names = [t['name'] for t in schema['tools']]
    print(f"   Tools in schema: {tool_names}")
    
    fetch_tool = [t for t in schema['tools'] if t['name'] == 'fetch_user_instructions']
    if fetch_tool:
        print(f"   ✅ fetch_user_instructions in schema")
        print(f"   Parameters: {fetch_tool[0].get('parameters', {}).get('properties', {}).keys()}")
    else:
        print(f"   ❌ fetch_user_instructions NOT in schema")

# Check Anthropic format
print("\n5. Anthropic format check:")
anthropic_tools = r.get_anthropic_tools()
feedback_anthropic = [t for t in anthropic_tools if 'feedback' in t['name'].lower()]
print(f"   Feedback tools in Anthropic format: {len(feedback_anthropic)}")
for t in feedback_anthropic:
    print(f"   - {t['name']}")

fetch_anthropic = [t for t in anthropic_tools if t['name'] == 'fetch_user_instructions']
if fetch_anthropic:
    print(f"\n   ✅ fetch_user_instructions in Anthropic format")
    print(f"   Schema: {json.dumps(fetch_anthropic[0], indent=2)}")
else:
    print(f"\n   ❌ fetch_user_instructions NOT in Anthropic format")

print("\n" + "="*80)
