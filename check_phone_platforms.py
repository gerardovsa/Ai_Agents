import sys
sys.path.insert(0, 'c:/Users/gpoli/GIT/AI_agents')
from tools.registry_v3 import RegistryV3

registry = RegistryV3()

# Check phone tools
phone_tools = ['phone_add_notes', 'phone_schedule_follow_up', 'phone_prompt_alert_coaching']

for tool_name in phone_tools:
    if tool_name in registry.tools:
        tool = registry.tools[tool_name]
        platform = tool.get('platform', 'MISSING')
        print(f'{tool_name}: platform="{platform}"')
    else:
        print(f'{tool_name}: NOT FOUND')
