import sys
sys.path.insert(0, 'c:/Users/gpoli/GIT/AI_agents')

from tools.registry import ToolRegistry

registry = ToolRegistry()
cadquery_tools = [t for t in registry.list_tools() if t.get('platform') == 'cadquery']

print(f'\n✓ CadQuery tools registered: {len(cadquery_tools)}')
for t in cadquery_tools:
    print(f'  - {t["name"]}: {t["description"][:70]}...')

print('\n✓ Ready to use!')
