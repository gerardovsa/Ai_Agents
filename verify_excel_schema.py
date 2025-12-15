import json

schema = json.load(open('tools/schemas/microsoft_excel_tools.json', 'r', encoding='utf-8'))

print(f"✅ Total tools: {len(schema['tools'])}")
print(f"✅ Has api_limitations: {'api_limitations' in schema}")
print(f"✅ Documented limitations: {len(schema.get('api_limitations', {}).get('limitations', []))}")

formula_tool = next((t for t in schema['tools'] if 'formula_builder' in t['name']), None)
batch_tool = next((t for t in schema['tools'] if 'batch_update' in t['name']), None)

print(f"\n📊 Formula Builder:")
print(f"  - Has integration docs: {'smart_workflow_integration' in formula_tool if formula_tool else False}")
if formula_tool and 'smart_workflow_integration' in formula_tool:
    print(f"  - Used by: {len(formula_tool['smart_workflow_integration'].get('used_by', []))} SMART workflows")

print(f"\n⚡ Batch Update:")
print(f"  - Has integration docs: {'smart_workflow_integration' in batch_tool if batch_tool else False}")
if batch_tool and 'smart_workflow_integration' in batch_tool:
    print(f"  - Used by: {len(batch_tool['smart_workflow_integration'].get('used_by', []))} SMART workflows")

print(f"\n🚫 API Limitations:")
for limit in schema.get('api_limitations', {}).get('limitations', []):
    print(f"  - {limit['feature']}: {limit['status']}")
