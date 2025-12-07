"""
Comprehensive smoke test for all route files
Tests: Syntax (compilation) and Import dependencies
"""
import py_compile
import sys
from pathlib import Path
import importlib.util

# Setup paths
AI_AGENTS_ROOT = Path(__file__).parent
AI_INFRA_ROOT = AI_AGENTS_ROOT / 'AI_infrastructure'
routes_dir = AI_INFRA_ROOT / 'routes'

sys.path.insert(0, str(AI_AGENTS_ROOT))
sys.path.insert(0, str(AI_INFRA_ROOT))

print("=" * 80)
print("COMPREHENSIVE ROUTE FILES SMOKE TEST")
print("=" * 80)
print()

# Get all route files (excluding copies)
route_files = sorted([f for f in routes_dir.glob('*.py') if 'copy' not in f.name.lower()])

syntax_passed = []
syntax_failed = []
import_passed = []
import_failed = []

print(f"Testing {len(route_files)} route files...\n")

for filepath in route_files:
    filename = filepath.name
    
    # Test 1: Syntax (compilation)
    try:
        py_compile.compile(str(filepath), doraise=True)
        syntax_passed.append(filename)
        syntax_ok = True
    except Exception as e:
        syntax_failed.append((filename, str(e)))
        syntax_ok = False
        print(f"❌ {filename:50} SYNTAX ERROR")
        print(f"   {str(e)[:100]}")
        continue
    
    # Test 2: Import test (can the module be loaded?)
    try:
        spec = importlib.util.spec_from_file_location(filename[:-3], filepath)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            sys.modules[filename[:-3]] = module
            spec.loader.exec_module(module)
            import_passed.append(filename)
            print(f"✅ {filename:50} OK")
        else:
            raise ImportError("Could not create module spec")
    except Exception as e:
        import_failed.append((filename, str(e).split('\n')[0]))
        print(f"⚠️  {filename:50} IMPORT ERROR")
        print(f"   {str(e).split(chr(10))[0][:100]}")

print()
print("=" * 80)
print("RESULTS SUMMARY")
print("=" * 80)
print(f"✅ Syntax Passed:   {len(syntax_passed):3} files")
print(f"❌ Syntax Failed:   {len(syntax_failed):3} files")
print(f"✅ Import Passed:   {len(import_passed):3} files")
print(f"⚠️  Import Failed:   {len(import_failed):3} files")
print(f"📊 Total Tested:    {len(route_files):3} files")
print()

if syntax_failed:
    print("SYNTAX ERRORS:")
    for filename, error in syntax_failed:
        print(f"  • {filename}")
        print(f"    {error[:150]}")
    print()

# Calculate success rate
total_ok = len(import_passed)
success_rate = (total_ok / len(route_files)) * 100 if route_files else 0

print("=" * 80)
if success_rate == 100:
    print(f"🎉 SUCCESS: All {len(route_files)} files passed!")
elif success_rate >= 90:
    print(f"✅ GOOD: {success_rate:.1f}% success rate ({total_ok}/{len(route_files)} files)")
elif success_rate >= 70:
    print(f"⚠️  FAIR: {success_rate:.1f}% success rate ({total_ok}/{len(route_files)} files)")
else:
    print(f"❌ NEEDS WORK: {success_rate:.1f}% success rate ({total_ok}/{len(route_files)} files)")
print("=" * 80)
