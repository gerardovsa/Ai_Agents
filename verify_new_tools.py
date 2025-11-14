"""
Verify new Xero smart tools and meta-tools instructions
"""

import json
from pathlib import Path

print("="*80)
print("NEW TOOLS VERIFICATION")
print("="*80)

# Check Xero tools
print("\n1. XERO SMART TOOLS:")
print("-"*80)

xero_path = Path('tools/schemas/xero_tools.json')
with open(xero_path, 'r', encoding='utf-8') as f:
    xero_data = json.load(f)

xero_tools = xero_data['tools']
smart_tools = [t for t in xero_tools if 'smart' in t['name']]

print(f"Total Xero tools: {len(xero_tools)}")
print(f"Smart Xero tools: {len(smart_tools)}\n")

for tool in smart_tools:
    has_instr = 'instructions' in tool
    status = "✅" if has_instr else "❌"
    print(f"{status} {tool['name']}")
    if has_instr:
        instr = tool['instructions']
        print(f"   - when_to_use: {len(instr.get('when_to_use', []))} scenarios")
        print(f"   - workflow: {len(instr.get('workflow', []))} steps")
        print(f"   - examples: {len(instr.get('example_usage', {}))} scenarios")
        print(f"   - tips: {len(instr.get('tips', []))} tips")

# Check meta-tools
print("\n" + "="*80)
print("2. META-TOOLS WITH INSTRUCTIONS:")
print("-"*80)

meta_path = Path('tools/schemas/meta_tools.json')
with open(meta_path, 'r', encoding='utf-8') as f:
    meta_data = json.load(f)

meta_tools = meta_data['tools']
key_tools = ['list_platform_tools', 'get_tool_schema', 'search_tools']

print(f"Total meta-tools: {len(meta_tools)}\n")

for tool in meta_tools:
    if tool['name'] in key_tools:
        has_instr = 'instructions' in tool
        status = "✅" if has_instr else "❌"
        print(f"{status} {tool['name']}")
        if has_instr:
            instr = tool['instructions']
            print(f"   - when_to_use: {len(instr.get('when_to_use', []))} scenarios")
            print(f"   - workflow: {len(instr.get('workflow', []))} steps")
            print(f"   - examples: {len(instr.get('example_usage', {}))} scenarios")
            print(f"   - tips: {len(instr.get('tips', []))} tips")

# Discovery workflow example
print("\n" + "="*80)
print("3. AI DISCOVERY WORKFLOW:")
print("="*80)
print("""
Step 1: User asks "What Xero tools are available?"
   → AI calls: list_platform_tools(platform='xero')
   → Returns: 11 tool names + one-line descriptions
   → AI shows overview to user

Step 2: User says "Tell me about the smart AP tool"
   → AI calls: get_tool_schema(tool_name='xero_smart_export_accounts_payable_stats')
   → Returns: Full schema with parameters, instructions, examples, tips
   → AI learns how to use the tool

Step 3: User says "Run it for last 30 days"
   → AI executes: xero_smart_export_accounts_payable_stats(days_back=30)
   → Returns: Comprehensive AP data + Excel link
   → AI analyzes and presents insights

BENEFITS:
✅ Lightweight discovery (names only, not full schemas)
✅ On-demand detail loading (only for tools being used)
✅ AI learns from instructions in schema
✅ Examples teach proper usage patterns
""")

print("="*80)
print("✅ VERIFICATION COMPLETE")
print("="*80)
