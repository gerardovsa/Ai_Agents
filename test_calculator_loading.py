"""Test calculator loading in module plugin system"""
from tools.plugins.module_plugin_loader import ModulePluginLoader

loader = ModulePluginLoader()
data = loader.get_all_module_tools()

print(f"\n{'='*60}")
print(f"MODULE PLUGIN LOADER TEST")
print(f"{'='*60}")
print(f"Total tools found: {len(data['tools'])}")
print(f"Total implementations: {len(data['implementations'])}")

calc_tools = [t['name'] for t in data['tools'] if 'calculate_' in t['name']]
calc_impls = [k for k in data['implementations'].keys() if 'calculate_' in k]

print(f"\nCalculator tools in schema: {len(calc_tools)}")
print(f"Calculator implementations: {len(calc_impls)}")

print(f"\n{'='*60}")
print(f"MISSING IMPLEMENTATIONS:")
print(f"{'='*60}")
missing = set(calc_tools) - set(calc_impls)
for tool in sorted(missing):
    print(f"  ❌ {tool}")

print(f"\n{'='*60}")
print(f"FOUND IMPLEMENTATIONS:")
print(f"{'='*60}")
for impl in sorted(calc_impls)[:10]:  # Show first 10
    print(f"  ✅ {impl}")
if len(calc_impls) > 10:
    print(f"  ... and {len(calc_impls) - 10} more")
