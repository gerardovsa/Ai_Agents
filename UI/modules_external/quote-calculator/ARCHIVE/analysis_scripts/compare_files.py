import json
import sys
from pathlib import Path

root = Path(__file__).parent.parent.parent.parent

schema1_path = root / "UI" / "modules_external" / "quote-calculator" / "schema" / "calculator_tools.json"
schema2_path = root / "tools" / "schemas" / "calculator_tools.json"

schema1 = json.load(open(schema1_path, 'r', encoding='utf-8-sig'))
schema2 = json.load(open(schema2_path, 'r', encoding='utf-8-sig'))

print('=' * 80)
print('SCHEMA FILE COMPARISON')
print('=' * 80)

print(f'\n1. UI/modules_external/quote-calculator/schema/calculator_tools.json:')
print(f'   Tools: {len(schema1["tools"])}')
print(f'   File size: {schema1_path.stat().st_size:,} bytes')

print(f'\n2. tools/schemas/calculator_tools.json:')
print(f'   Tools: {len(schema2["tools"])}')
print(f'   File size: {schema2_path.stat().st_size:,} bytes')

print('\n' + '=' * 80)
print('WHICH FILE IS LOADED BY REGISTRY V3?')
print('=' * 80)
print('\n✅ UI/modules_external/quote-calculator/schema/calculator_tools.json')
print('   Loaded by: ModulePluginLoader → Registry V3')
print('   Path: tools/plugins/module_plugin_loader.py')
print('   Scans: UI/modules_external/*/schema/*.json')

print('\n❌ tools/schemas/calculator_tools.json')
print('   NOT loaded by Registry V3')
print('   Reason: Registry V3 loads from google_workspace/ and tools/implementations/')
print('   Status: OLD/UNUSED file')

print('\n' + '=' * 80)
print('RECOMMENDATION')
print('=' * 80)
print('\n❌ DELETE: tools/schemas/calculator_tools.json')
print('✅ KEEP: UI/modules_external/quote-calculator/schema/calculator_tools.json')
print('\nThis is the ACTIVE file that Registry V3 loads via module plugin system.')
