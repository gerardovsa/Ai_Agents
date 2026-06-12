"""Verify Microsoft Excel tools naming convention is consistent"""
import json
import re
from pathlib import Path

print("=" * 80)
print("MICROSOFT EXCEL TOOLS - NAMING CONVENTION VERIFICATION")
print("=" * 80)

# Load schema
schema_file = Path('tools/schemas/microsoft_excel_tools.json')
schema = json.load(schema_file.open('r', encoding='utf-8'))

# Load implementation
impl_file = Path('tools/implementations/microsoft_excel_tools.py')
impl_content = impl_file.read_text(encoding='utf-8')

print(f"\n📋 SCHEMA TOOLS (from JSON)")
print("-" * 80)

schema_tools = {}
for tool in schema['tools']:
    name = tool['name']
    schema_tools[name] = tool
    print(f"   {name}")

print(f"\n📊 Total schema tools: {len(schema_tools)}")

# Extract method definitions from implementation
print(f"\n🔧 IMPLEMENTATION METHODS (from .py)")
print("-" * 80)

method_pattern = r'def (excel_\w+)\('
impl_methods = set(re.findall(method_pattern, impl_content))

for method in sorted(impl_methods):
    print(f"   {method}()")

print(f"\n📊 Total implementation methods: {len(impl_methods)}")

# Extract module-level exports
print(f"\n📤 MODULE EXPORTS (simple assignments)")
print("-" * 80)

export_pattern = r'^(microsoft_excel_\w+) = microsoft_excel_tools\.(excel_\w+)'
exports = {}
for match in re.finditer(export_pattern, impl_content, re.MULTILINE):
    export_name = match.group(1)
    method_name = match.group(2)
    exports[export_name] = method_name
    print(f"   {export_name} → {method_name}()")

print(f"\n📊 Total simple exports: {len(exports)}")

# Extract function wrappers
print(f"\n🎁 FUNCTION WRAPPERS (with user_id handling)")
print("-" * 80)

wrapper_pattern = r'^def (microsoft_excel_\w+)\(\*\*kwargs\):'
wrappers = set(re.findall(wrapper_pattern, impl_content, re.MULTILINE))

for wrapper in sorted(wrappers):
    print(f"   {wrapper}(**kwargs)")

print(f"\n📊 Total function wrappers: {len(wrappers)}")

# Verification
print(f"\n✅ VERIFICATION CHECKS")
print("=" * 80)

# Check 1: All schema tools should have implementation methods
missing_methods = []
for schema_name in schema_tools.keys():
    # Convert microsoft_excel_xxx to excel_xxx
    method_name = schema_name.replace('microsoft_excel_', 'excel_')
    if method_name not in impl_methods:
        missing_methods.append(f"{schema_name} → {method_name}() NOT FOUND")

if missing_methods:
    print(f"\n❌ Missing implementation methods:")
    for msg in missing_methods:
        print(f"   {msg}")
else:
    print(f"\n✅ All {len(schema_tools)} schema tools have implementation methods")

# Check 2: All schema tools should have exports (simple OR wrapper)
all_exports = set(exports.keys()) | wrappers
missing_exports = []
for schema_name in schema_tools.keys():
    if schema_name not in all_exports:
        missing_exports.append(schema_name)

if missing_exports:
    print(f"\n❌ Missing exports:")
    for name in missing_exports:
        print(f"   {name}")
else:
    print(f"\n✅ All {len(schema_tools)} schema tools have exports")

# Check 3: Naming convention consistency
print(f"\n📝 NAMING CONVENTION CHECK")
print("-" * 80)

convention_ok = True
for schema_name in schema_tools.keys():
    if not schema_name.startswith('microsoft_excel_'):
        print(f"❌ Schema tool doesn't follow convention: {schema_name}")
        convention_ok = False

if convention_ok:
    print(f"✅ All schema tools follow 'microsoft_excel_*' convention")

# Check 4: SMART tools specifically
smart_tools = [name for name in schema_tools.keys() if '_smart_' in name]
print(f"\n⭐ SMART TOOLS ({len(smart_tools)} total)")
print("-" * 80)

for smart_tool in sorted(smart_tools):
    method_name = smart_tool.replace('microsoft_excel_', 'excel_')
    has_method = method_name in impl_methods
    has_export = smart_tool in all_exports
    
    status = "✅" if (has_method and has_export) else "❌"
    print(f"{status} {smart_tool}")
    if not has_method:
        print(f"     Missing method: {method_name}()")
    if not has_export:
        print(f"     Missing export")

print("\n" + "=" * 80)
print("VERIFICATION COMPLETE")
print("=" * 80)

if not missing_methods and not missing_exports and convention_ok:
    print("✅ ALL CHECKS PASSED - Naming convention is consistent!")
else:
    print("⚠️  ISSUES FOUND - See details above")
