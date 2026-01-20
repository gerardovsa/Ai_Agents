#!/usr/bin/env python3
"""Quick test to verify meta-tools are loaded in Registry V3"""

from tools.registry_v3 import get_registry

r = get_registry()

meta_tools = [
    'search_tools',
    'list_platform_tools',
    'list_available_platforms',
    'get_tool_schema',
    'execute_tool'
]

print('\n🔍 Meta-Tools Status Check:')
print('=' * 50)

for tool in meta_tools:
    status = '✅ FOUND' if tool in r.tools else '❌ MISSING'
    print(f'  {status}: {tool}')

print(f'\n📊 Registry Statistics:')
print(f'  Total tools loaded: {len(r.tools)}')
print(f'  Meta-tool platform count: {len([t for t in r.tools if r.tools[t].get("platform") == "meta_tools"])}')

# Test anthropic tools format
anthropic_tools = r.get_anthropic_tools()
meta_in_anthropic = [t for t in anthropic_tools if t['name'] in meta_tools]
print(f'  Meta-tools in Anthropic format: {len(meta_in_anthropic)}/{len(meta_tools)}')

if len(meta_in_anthropic) < len(meta_tools):
    print('\n❌ WARNING: Not all meta-tools are in Anthropic format!')
    print('   This means AI cannot see them even though they\'re loaded.')
else:
    print('\n✅ All meta-tools are available to AI')
