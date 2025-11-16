"""Debug task-based search"""
import sys
sys.path.insert(0, 'AI_infrastructure')

from tools.registry_v3 import get_registry

registry = get_registry()

# Check if our tool exists and what its description is
tool = registry.tools.get('assign_and_activate_agent_with_slugs')
if tool:
    print("Tool found in registry:")
    print(f"  Name: assign_and_activate_agent_with_slugs")
    print(f"  Platform: {tool.get('platform', 'N/A')}")
    print(f"  Description: {tool.get('description', 'N/A')[:200]}...")
    print()
else:
    print("Tool NOT found in registry!")
    print()

# Test alias matching
query = "distribute work across multiple agents"
query_lower = query.lower()

alias_map = {
    'agent': ['assign_and_activate', 'request_update', 'respond_to'],
    'agents': ['assign_and_activate', 'request_update', 'respond_to'],
    'multi-agent': ['assign_and_activate', 'request_update', 'respond_to'],
    'coordination': ['assign_and_activate', 'request_update', 'respond_to', 'coordination'],
    'distribute': ['assign_and_activate', 'agent'],
    'delegate': ['assign_and_activate', 'agent'],
}

print(f"Query: '{query}'")
print(f"Query lowercase: '{query_lower}'")
print()

# Check for alias matches
print("Checking aliases:")
for alias, expansions in alias_map.items():
    if alias in query_lower:
        print(f"  MATCH: '{alias}' found in query")
        print(f"    Expansions: {expansions}")
    else:
        print(f"  NO MATCH: '{alias}'")
print()

# Now manually check if keywords match the tool
print("Manual keyword matching test:")
keywords = ['assign_and_activate', 'agent']
tool_name_lower = 'assign_and_activate_agent_with_slugs'.lower()
description_lower = tool.get('description', '').lower()

for keyword in keywords:
    in_name = keyword in tool_name_lower
    in_desc = keyword in description_lower
    print(f"  Keyword: '{keyword}'")
    print(f"    In tool name: {in_name}")
    print(f"    In description: {in_desc}")
    print(f"    Should match: {in_name or in_desc}")
