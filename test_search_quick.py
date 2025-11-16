"""Quick test of task-based search"""
import sys
sys.path.insert(0, 'AI_infrastructure')

from tools.implementations.meta_tools import recommend_tools_for_task

# Test the search
result = recommend_tools_for_task('distribute work across multiple agents')

print(f"Query: 'distribute work across multiple agents'")
print(f"Match count: {result.get('match_count', 0)}")
print("\nTop 5 tools:")
for tool in result.get('tools', [])[:5]:
    print(f"  - {tool['name']}")
    print(f"    Platform: {tool.get('platform', 'unknown')}")
    print(f"    Description: {tool['description'][:100]}...")
    print()

# Check if our target tool is in the results
tool_names = [t['name'] for t in result.get('tools', [])]
if 'assign_and_activate_agent_with_slugs' in tool_names:
    print("SUCCESS: Target tool found in search results")
else:
    print("FAIL: Target tool NOT found")
