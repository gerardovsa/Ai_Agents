"""Debug recommend_tools_for_task in detail"""
import sys
sys.path.insert(0, 'AI_infrastructure')

# Manually test the logic
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

print(f"Query: {query}")
print(f"Query lowercase: {query_lower}")
print()

# Test the logic from meta_tools.py
search_keywords = []

# Check for exact alias match first
if query_lower in alias_map:
    print(f"Exact match found: {query_lower}")
    search_keywords = alias_map[query_lower]
else:
    print("No exact match, checking substrings...")
    # No alias - check if any alias appears as substring in query
    alias_found = False
    for alias, expansions in alias_map.items():
        if alias in query_lower:
            print(f"  Found alias '{alias}' in query")
            print(f"    Expansions: {expansions}")
            search_keywords.extend(expansions)
            alias_found = True
    
    # If no alias found, use query directly for substring matching
    if not alias_found:
        print("No alias found, using query directly")
        search_keywords = [query_lower]

print()
print(f"Final search_keywords: {search_keywords}")
print()

# Now test if these keywords would match our tool
from tools.registry_v3 import get_registry
registry = get_registry()

tool = registry.tools.get('assign_and_activate_agent_with_slugs')
if tool:
    tool_name_lower = 'assign_and_activate_agent_with_slugs'.lower()
    description_lower = tool.get('description', '').lower()
    
    print("Testing keyword matches:")
    matched = False
    for keyword in search_keywords:
        in_name = keyword in tool_name_lower
        in_desc = keyword in description_lower
        match = in_name or in_desc
        print(f"  Keyword '{keyword}':")
        print(f"    In name: {in_name}")
        print(f"    In desc: {in_desc}")
        print(f"    MATCH: {match}")
        if match:
            matched = True
    
    print()
    if matched:
        print("SUCCESS: Tool would be found with these keywords!")
    else:
        print("FAIL: Tool would NOT be found with these keywords")
