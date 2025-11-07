"""Check actual platform names"""
import sys
sys.path.insert(0, 'tools')

from registry_v3 import get_registry

registry = get_registry()

# Get unique platforms
platforms = set()
for tool_name, tool in registry.tools.items():
    platform = tool.get("platform", "unknown")
    platforms.add(platform)

print("Available platforms:")
for p in sorted(platforms):
    count = len([t for t in registry.tools.values() if t.get("platform") == p])
    print(f"  {p}: {count} tools")
    
    # Show first few tools for this platform
    tools_for_platform = [t for t in registry.tools.keys() if registry.tools[t].get("platform") == p]
    if tools_for_platform:
        print(f"    Examples: {', '.join(tools_for_platform[:3])}")
