import sys
sys.path.insert(0, 'c:/Users/gpoli/GIT/AI_agents')
from tools.registry_v3 import RegistryV3

registry = RegistryV3()

# Check if google_calendar_check_availability exists
tool_name = 'google_calendar_check_availability'

if tool_name in registry.tools:
    tool = registry.tools[tool_name]
    print(f'✅ FOUND: {tool_name}')
    print(f'Platform: {tool.get("platform", "MISSING")}')
    print(f'Short Description: {tool.get("short_description", "MISSING")}')
else:
    print(f'❌ NOT FOUND: {tool_name}')
    print(f'\nSearching for similar names...')
    matches = [name for name in registry.tools.keys() if 'availability' in name or 'check' in name.lower() and 'calendar' in name.lower()]
    print(f'Found {len(matches)} potential matches:')
    for match in matches[:10]:
        print(f'  - {match}')
