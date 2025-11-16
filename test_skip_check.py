"""Check if tool is being skipped"""

tool_name = 'assign_and_activate_agent_with_slugs'

# Check if it starts with skip prefixes
skip_prefixes = ('list_', 'get_platform', 'recommend_', 'execute_', 'search_')

will_skip = tool_name.startswith(skip_prefixes)

print(f"Tool name: {tool_name}")
print(f"Skip prefixes: {skip_prefixes}")
print(f"Will be skipped: {will_skip}")

if not will_skip:
    print("\nGood! Tool will NOT be skipped")
else:
    print("\nProblem! Tool WILL be skipped")
