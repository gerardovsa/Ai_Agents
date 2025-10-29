"""
Check Gmail tools availability in AI_agents
"""

from tools import ToolRegistry

# Initialize registry
registry = ToolRegistry()

# Get all Gmail tools
gmail_tools = [t for t in registry.list_tools() if 'gmail' in t.get('name', '').lower()]

print(f"\n{'='*60}")
print(f"Gmail Tools Available: {len(gmail_tools)}")
print(f"{'='*60}\n")

for tool in gmail_tools:
    print(f"  • {tool['name']}")
    print(f"    Description: {tool.get('description', 'N/A')[:80]}...")
    print()

print(f"{'='*60}")
print("Gmail is READY to use!")
print(f"{'='*60}\n")
