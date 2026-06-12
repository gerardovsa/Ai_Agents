"""Simple check for short_description coverage"""
import json
from pathlib import Path

# Check core schemas
schemas_dir = Path("tools/schemas")
core_tools = 0
core_with_short = 0

print("Analyzing core tool schemas...")
for schema_file in schemas_dir.glob("*.json"):
    if schema_file.name.startswith("ARCHIVE"):
        continue
    try:
        with open(schema_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if 'tools' in data:
                for tool in data['tools']:
                    core_tools += 1
                    if 'short_description' in tool and tool['short_description']:
                        core_with_short += 1
    except Exception as e:
        print(f"  Error reading {schema_file.name}: {e}")

# Check module plugin schemas
module_dir = Path("UI/modules_external")
module_tools = 0
module_with_short = 0

print("\nAnalyzing module plugin schemas...")
for module_path in module_dir.iterdir():
    if not module_path.is_dir():
        continue
    schema_path = module_path / "schema"
    if schema_path.exists():
        for schema_file in schema_path.glob("*.json"):
            try:
                with open(schema_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'tools' in data:
                        for tool in data['tools']:
                            module_tools += 1
                            if 'short_description' in tool and tool['short_description']:
                                module_with_short += 1
            except Exception as e:
                print(f"  Error reading {schema_file}: {e}")

# Report
total = core_tools + module_tools
with_short = core_with_short + module_with_short
missing = total - with_short
coverage = (with_short / total * 100) if total > 0 else 0

print("\n" + "=" * 80)
print("SHORT DESCRIPTION COVERAGE REPORT")
print("=" * 80)
print(f"\nCore Tools (tools/schemas/):")
print(f"  Total: {core_tools}")
print(f"  With short_description: {core_with_short}")
print(f"  Coverage: {core_with_short/core_tools*100:.1f}%" if core_tools > 0 else "  Coverage: N/A")

print(f"\nModule Plugins (UI/modules_external/):")
print(f"  Total: {module_tools}")
print(f"  With short_description: {module_with_short}")
print(f"  Coverage: {module_with_short/module_tools*100:.1f}%" if module_tools > 0 else "  Coverage: N/A")

print(f"\nOVERALL:")
print(f"  Total tools: {total}")
print(f"  With short_description: {with_short}")
print(f"  Missing short_description: {missing}")
print(f"  Coverage: {coverage:.1f}%")

if coverage < 100:
    print(f"\n⚠️ WARNING: {missing} tools ({100-coverage:.1f}%) missing short_description")
    print("\nRecommendation: Add short_description field (50-120 chars) to all tools")
    print("This is CRITICAL for:")
    print("  - Vectorization and semantic search quality")
    print("  - Token efficiency (98% reduction in tool listings)")
    print("  - AI discovery and tool selection accuracy")
else:
    print("\n✅ SUCCESS: All tools have short_description field!")

print("=" * 80)
