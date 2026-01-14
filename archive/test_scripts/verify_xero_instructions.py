"""
Verify all Xero tools have AI-readable instructions
"""

import json
from pathlib import Path

# Load Xero tools schema
schema_path = Path('tools/schemas/xero_tools.json')
with open(schema_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

tools = data['tools']

print("="*80)
print("XERO TOOLS INSTRUCTIONS VERIFICATION")
print("="*80)
print(f"\nTotal Xero tools: {len(tools)}\n")

print("Tools with instructions:")
print("-"*80)

with_instructions = 0
without_instructions = 0

for tool in tools:
    has_instr = 'instructions' in tool
    status = "✅" if has_instr else "❌"
    print(f"{status} {tool['name']}")
    
    if has_instr:
        with_instructions += 1
        instr = tool['instructions']
        print(f"   - when_to_use: {len(instr.get('when_to_use', []))} scenarios")
        print(f"   - workflow: {len(instr.get('workflow', []))} steps")
        print(f"   - example_usage: {len(instr.get('example_usage', {}))} examples")
        print(f"   - tips: {len(instr.get('tips', []))} tips")
    else:
        without_instructions += 1

print("\n" + "="*80)
print("SUMMARY:")
print("="*80)
print(f"  ✅ With instructions: {with_instructions}")
print(f"  ❌ Without instructions: {without_instructions}")
print(f"  📊 Completion rate: {with_instructions/len(tools)*100:.0f}%")

if with_instructions == len(tools):
    print("\n🎉 SUCCESS! All Xero tools have AI-readable instructions!")
else:
    print(f"\n⚠️  {without_instructions} tools still need instructions")
