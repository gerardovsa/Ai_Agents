"""Check if communication-hub module is registered in Flask backend"""

from AI_infrastructure.core.module_registry import get_module_registry

registry = get_module_registry()

print(f'\nTotal modules registered: {len(registry.modules)}')
print(f'Module IDs: {list(registry.modules.keys())}\n')

comm_hub = registry.modules.get('communication-hub')

if comm_hub:
    print('✅ Communication Hub module FOUND')
    print(f'   - Name: {comm_hub.name}')
    print(f'   - Show in sidebar: {comm_hub.show_in_sidebar}')
    print(f'   - Main tab: {comm_hub.main_tab}')
    print(f'   - Required platforms: {comm_hub.required_platforms}')
    print(f'   - Credentials required: {comm_hub.credentials_required}')
    print(f'   - Icon: {comm_hub.icon}')
    print(f'   - Color: {comm_hub.color}')
else:
    print('❌ Communication Hub module NOT FOUND')
    print('   The module is not being discovered by Flask backend')
