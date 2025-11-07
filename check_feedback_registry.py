"""Check feedback tools in registry"""
from tools.registry_v3 import RegistryV3

r = RegistryV3()

# Find feedback tools
feedback_tools = [t for t in r.tools.keys() if 'feedback' in t]
print(f'\nFeedback tools found: {len(feedback_tools)}')
for t in feedback_tools:
    print(f'  - {t}')

# Check Anthropic format
anthropic = r.get_anthropic_tools()
feedback_anthropic = [t for t in anthropic if 'feedback' in t['name']]
print(f'\nAnthropic format: {len(feedback_anthropic)} tools')
for t in feedback_anthropic:
    params = t.get('input_schema', {}).get('properties', {})
    print(f'  - {t["name"]}: {len(params)} params')
    if params:
        for p in params:
            print(f'    * {p}')
