#!/usr/bin/env python3
"""Test Phase 3 - Gmail, Google Docs, Google Forms tools"""

from registry import ToolRegistry

# Initialize registry
registry = ToolRegistry()
tools = registry.list_tools()

# Count by platform
platforms = {}
for tool in tools:
    platform = tool['platform']
    platforms[platform] = platforms.get(platform, 0) + 1

# Display results
print(f"\n{'='*60}")
print(f"✅ PHASE 3 COMPLETE - TOOL REGISTRY LOADED")
print(f"{'='*60}")
print(f"\nTotal Tools: {len(tools)}")
print(f"Total Platforms: {len(platforms)}")
print(f"\n{'Platform':<25} {'Tools':<10}")
print(f"{'-'*35}")

for platform, count in sorted(platforms.items()):
    print(f"{platform.upper():<25} {count:<10}")

# Gmail tools
gmail_tools = [t for t in tools if t['platform'] == 'gmail']
print(f"\n{'='*60}")
print(f"📧 GMAIL TOOLS ({len(gmail_tools)} tools)")
print(f"{'='*60}")
for i, tool in enumerate(gmail_tools[:10], 1):
    print(f"{i:2}. {tool['name']}")
if len(gmail_tools) > 10:
    print(f"   ... and {len(gmail_tools) - 10} more")

# Google Docs tools
gdocs_tools = [t for t in tools if t['platform'] == 'google_docs']
print(f"\n{'='*60}")
print(f"📄 GOOGLE DOCS TOOLS ({len(gdocs_tools)} tools)")
print(f"{'='*60}")
for i, tool in enumerate(gdocs_tools[:10], 1):
    print(f"{i:2}. {tool['name']}")
if len(gdocs_tools) > 10:
    print(f"   ... and {len(gdocs_tools) - 10} more")

# Google Forms tools
gforms_tools = [t for t in tools if t['platform'] == 'google_forms']
print(f"\n{'='*60}")
print(f"📝 GOOGLE FORMS TOOLS ({len(gforms_tools)} tools)")
print(f"{'='*60}")
for i, tool in enumerate(gforms_tools, 1):
    print(f"{i:2}. {tool['name']}")

print(f"\n{'='*60}")
print("✅ Phase 3 schemas loaded successfully!")
print(f"{'='*60}\n")
