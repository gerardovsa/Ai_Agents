"""
Check short_description coverage across all tools
"""
import sys
sys.path.insert(0, 'AI_infrastructure')

from tools.registry_v3 import RegistryV3

# Load registry
registry = RegistryV3()

# Count tools with short_description
total = len(registry.tools)
with_short = 0
without_short = []

for name in registry.tools.keys():
    tool = registry.get_tool(name)
    if 'short_description' in tool and tool['short_description']:
        with_short += 1
    else:
        without_short.append(name)

missing = total - with_short
coverage = (with_short / total * 100) if total > 0 else 0

print("=" * 80)
print("SHORT DESCRIPTION COVERAGE REPORT")
print("=" * 80)
print(f"\nTotal tools: {total}")
print(f"With short_description: {with_short}")
print(f"Missing short_description: {missing}")
print(f"Coverage: {coverage:.1f}%")

if missing > 0:
    print(f"\n⚠️ WARNING: {missing} tools ({100-coverage:.1f}%) missing short_description")
    print("\nFirst 20 tools without short_description:")
    for tool in without_short[:20]:
        print(f"  - {tool}")
    if len(without_short) > 20:
        print(f"  ... and {len(without_short) - 20} more")
else:
    print("\n✅ SUCCESS: All tools have short_description field!")

print("\n" + "=" * 80)

# Analyze by platform
platforms = {}
for name in registry.tools.keys():
    tool = registry.get_tool(name)
    platform = name.split('_')[0] if '_' in name else 'unknown'
    
    if platform not in platforms:
        platforms[platform] = {'total': 0, 'with_short': 0}
    
    platforms[platform]['total'] += 1
    if 'short_description' in tool and tool['short_description']:
        platforms[platform]['with_short'] += 1

print("\nPLATFORM BREAKDOWN (worst coverage first):")
print("-" * 80)

sorted_platforms = sorted(
    platforms.items(), 
    key=lambda x: x[1]['with_short'] / x[1]['total']
)

for platform, stats in sorted_platforms[:15]:
    coverage = (stats['with_short'] / stats['total'] * 100)
    status = "✅" if coverage == 100 else "⚠️"
    print(f"{status} {platform:25s}: {stats['with_short']:3d}/{stats['total']:3d} ({coverage:5.1f}%)")

print("=" * 80)
