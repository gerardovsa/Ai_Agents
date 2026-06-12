"""Detailed breakdown of short_description coverage by platform"""
import json
from pathlib import Path
from collections import defaultdict

# Analyze by schema file
platform_stats = {}

schemas_dir = Path("tools/schemas")
for schema_file in schemas_dir.glob("*.json"):
    if schema_file.name.startswith("ARCHIVE"):
        continue
    
    try:
        with open(schema_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if 'tools' in data:
                platform_name = schema_file.stem.replace('_tools', '')
                total = len(data['tools'])
                with_short = sum(1 for t in data['tools'] if 'short_description' in t and t['short_description'])
                
                platform_stats[platform_name] = {
                    'total': total,
                    'with_short': with_short,
                    'coverage': (with_short / total * 100) if total > 0 else 0,
                    'file': schema_file.name
                }
    except Exception as e:
        pass

# Sort by coverage (worst first)
sorted_platforms = sorted(platform_stats.items(), key=lambda x: x[1]['coverage'])

print("=" * 100)
print("PLATFORM SHORT_DESCRIPTION COVERAGE (Core Tools - Sorted by Worst Coverage)")
print("=" * 100)
print(f"{'Platform':<30} {'Tools':>7} {'With Short':>12} {'Coverage':>10} {'File':<30}")
print("-" * 100)

for platform, stats in sorted_platforms:
    status = "✅" if stats['coverage'] == 100 else "⚠️" if stats['coverage'] >= 50 else "❌"
    print(f"{status} {platform:<28} {stats['total']:>7} {stats['with_short']:>12} {stats['coverage']:>9.1f}% {stats['file']:<30}")

print("-" * 100)

# Summary stats
total_tools = sum(s['total'] for s in platform_stats.values())
total_with_short = sum(s['with_short'] for s in platform_stats.values())
avg_coverage = (total_with_short / total_tools * 100) if total_tools > 0 else 0

platforms_100 = sum(1 for s in platform_stats.values() if s['coverage'] == 100)
platforms_50_99 = sum(1 for s in platform_stats.values() if 50 <= s['coverage'] < 100)
platforms_below_50 = sum(1 for s in platform_stats.values() if s['coverage'] < 50)

print(f"\nSUMMARY:")
print(f"  Total platforms: {len(platform_stats)}")
print(f"  ✅ 100% coverage: {platforms_100} platforms")
print(f"  ⚠️ 50-99% coverage: {platforms_50_99} platforms")
print(f"  ❌ Below 50% coverage: {platforms_below_50} platforms")
print(f"\n  Overall coverage: {avg_coverage:.1f}% ({total_with_short}/{total_tools} tools)")

print("\n" + "=" * 100)
print("TOP 10 PLATFORMS NEEDING ATTENTION (Worst Coverage):")
print("=" * 100)

for i, (platform, stats) in enumerate(sorted_platforms[:10], 1):
    missing = stats['total'] - stats['with_short']
    print(f"{i:2d}. {platform:<30} - Missing {missing:3d} descriptions ({stats['coverage']:5.1f}% coverage)")

print("=" * 100)
