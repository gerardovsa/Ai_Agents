#!/usr/bin/env python3
"""Verify all Microsoft tools have implementations"""
import sys
sys.path.insert(0, 'tools')

from registry_v3 import RegistryV3

r = RegistryV3()
ms_schemas = [name for name in r.tools.keys() if name.startswith('microsoft_')]
ms_impls = {name: r.get_tool_function(name) for name in ms_schemas}
missing = [name for name, func in ms_impls.items() if func is None]

print(f'Total Microsoft tools in schemas: {len(ms_schemas)}')
print(f'Tools with implementations: {len([f for f in ms_impls.values() if f])}')
print(f'Missing implementations: {len(missing)}')

if len(missing) == 0:
    print('\n✅ ALL MICROSOFT TOOLS HAVE IMPLEMENTATIONS!')
else:
    print('\n❌ MISSING TOOLS:')
    for name in missing[:20]:
        print(f'  - {name}')

print('\n--- VERIFICATION: Testing 4 Fixed Tools ---')
fixed_tools = [
    'microsoft_excel_create_workbook',
    'microsoft_forms_list_forms',
    'microsoft_onenote_list_notebooks',
    'microsoft_todo_list_tasks'
]

for tool in fixed_tools:
    func = r.get_tool_function(tool)
    status = '✅ FOUND' if func else '❌ MISSING'
    print(f'{tool}: {status}')
