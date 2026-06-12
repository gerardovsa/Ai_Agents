import json

schema = json.load(open('tools/schemas/microsoft_excel_tools.json', 'r', encoding='utf-8'))

print("=" * 70)
print("📊 MICROSOFT EXCEL TOOLS - COMPLETE INVENTORY")
print("=" * 70)

print(f"\n✅ Total Tools: {len(schema['tools'])}")
print(f"📦 Version: {schema['version']}")

# Count by category
smart_tools = [t for t in schema['tools'] if 'smart_' in t['name']]
basic_tools = [t for t in schema['tools'] if 'smart_' not in t['name']]

print(f"\n🎯 SMART Workflows: {len(smart_tools)}")
for tool in smart_tools:
    print(f"   - {tool['name'].replace('microsoft_excel_', '')}")

print(f"\n🔧 Basic Tools: {len(basic_tools)}")

# Show API limitations
if 'api_limitations' in schema:
    print(f"\n🚫 API Limitations Documented: {len(schema['api_limitations']['limitations'])}")
    for limit in schema['api_limitations']['limitations']:
        print(f"   ❌ {limit['feature']}: {limit['status']}")

# Show new tools
print("\n🆕 Recent Enhancements:")
new_tools = ['smart_sheet_builder', 'smart_formula_builder', 'batch_update']
for tool_name in new_tools:
    tool = next((t for t in schema['tools'] if tool_name in t['name']), None)
    if tool:
        integration = tool.get('smart_workflow_integration', {})
        used_by = integration.get('used_by', [])
        uses_internally = integration.get('uses_internally', [])
        
        print(f"\n   ✨ {tool['name'].replace('microsoft_excel_', '')}")
        print(f"      Description: {tool['short_description']}")
        if used_by:
            print(f"      Used by: {len(used_by)} SMART workflows")
        if uses_internally:
            print(f"      Uses internally: {len(uses_internally)} tools")

print("\n" + "=" * 70)
print("✅ ALL ENHANCEMENTS COMPLETE!")
print("=" * 70)
