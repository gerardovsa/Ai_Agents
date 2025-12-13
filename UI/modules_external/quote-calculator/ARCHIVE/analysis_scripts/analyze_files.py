from pathlib import Path

# Get all files in quote-calculator (excluding ARCHIVE)
root = Path('.')
all_files = {}

for file in root.rglob('*'):
    if file.is_file():
        rel_path = str(file.relative_to(root))
        
        # Skip ARCHIVE folders
        if 'ARCHIVE' in rel_path or '__pycache__' in rel_path:
            continue
            
        # Categorize by type
        ext = file.suffix
        size = file.stat().st_size
        
        if ext not in all_files:
            all_files[ext] = []
        all_files[ext].append((rel_path, size))

print('📂 QUOTE-CALCULATOR MODULE - ALL ACTIVE FILES')
print('=' * 80)

# Sort by extension
for ext in sorted(all_files.keys()):
    files = all_files[ext]
    total_size = sum(s for _, s in files)
    ext_name = ext if ext else '(no ext)'
    print(f'\n{ext_name} ({len(files)} files, {total_size:,} bytes):')
    for path, size in sorted(files):
        print(f'  {size:>10,}  {path}')

# Now check what's actually LOADED by Registry V3
print('\n\n' + '=' * 80)
print('🔧 ACTIVELY LOADED BY REGISTRY V3')
print('=' * 80)

# The plugin loader loads:
print('\n✅ SCHEMA FILES (loaded by module_plugin_loader.py):')
print('  - schema/calculator_tools.json')
print('  - schema/query_library_tools.json')

print('\n✅ IMPLEMENTATION WRAPPERS (loaded by module_plugin_loader.py):')
print('  - implementations/calculator_wrapper.py')
print('  - implementations/query_library_wrapper.py')

print('\n✅ BACKEND CALCULATORS (imported by wrappers):')
for py_file in sorted((root / 'backend' / 'god_calculators').glob('*.py')):
    if py_file.name != '__init__.py':
        print(f'  - backend/god_calculators/{py_file.name}')

for py_file in sorted((root / 'backend' / 'shopify_calculators').glob('*.py')):
    if py_file.name != '__init__.py':
        print(f'  - backend/shopify_calculators/{py_file.name}')

print('\n✅ UTILITIES (imported by calculators):')
print('  - backend/query_library.py')

print('\n❓ FRONTEND FILES (loaded by browser):')
print('  - manifest.json (module metadata)')
print('  - quote-calculator.js (UI logic)')
print('  - quote-calculator.css (styling)')
print('  - quote-calculator.html (if exists)')

print('\n❌ NOT LOADED BY SYSTEM:')
print('  - CLI test scripts (flyers_cli.py, etc.)')
print('  - Test/analysis Python scripts')
print('  - Documentation files')
