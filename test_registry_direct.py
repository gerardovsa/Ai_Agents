from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.registry import ToolRegistry

print("=" * 60)
print("TOOL REGISTRY DIAGNOSTIC TEST")
print("=" * 60)

registry = ToolRegistry()

print(f"\nRegistry location: {registry.tools_dir}")
print(f"Schemas dir exists: {registry.schemas_dir.exists()}")
print(f"Implementations dir exists: {registry.implementations_dir.exists()}")
print(f"\nTotal tools loaded: {len(registry.tools)}")

if len(registry.tools) > 0:
    print(f"\n✅ SUCCESS - Tools loaded properly!")
    print(f"\nFirst 10 tools:")
    for i, tool_name in enumerate(list(registry.tools.keys())[:10]):
        tool = registry.tools[tool_name]
        print(f"  {i+1}. {tool_name} (platform: {tool.get('platform', 'unknown')})")
    
    # Check platforms
    platforms = set(t.get('platform', 'unknown') for t in registry.tools.values())
    print(f"\nPlatforms: {sorted(platforms)}")
else:
    print(f"\n❌ FAILED - No tools loaded")
    print(f"\nChecking schema files:")
    schema_files = list(registry.schemas_dir.glob("*.json"))
    print(f"  Found {len(schema_files)} JSON files in schemas/")
    if schema_files:
        print(f"  Sample: {schema_files[0].name}")
    
    print(f"\nChecking implementation files:")
    impl_files = list(registry.implementations_dir.glob("*.py"))
    impl_files = [f for f in impl_files if not f.name.startswith('_')]
    print(f"  Found {len(impl_files)} Python files in implementations/")
    if impl_files:
        print(f"  Sample: {impl_files[0].name}")

print("\n" + "=" * 60)
