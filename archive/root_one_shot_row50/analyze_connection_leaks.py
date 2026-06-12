"""
Comprehensive connection leak analysis for all route files
"""
import os
import re
from pathlib import Path
from collections import defaultdict

routes_dir = Path('AI_infrastructure/routes')
stats = defaultdict(lambda: {
    'get_db_connection_calls': 0, 
    'context_managers': 0, 
    'manual_close': 0, 
    'no_close': 0, 
    'has_helper': False
})

for py_file in routes_dir.glob('*.py'):
    if ' copy' in py_file.name or py_file.name.startswith('_'):
        continue
    
    content = py_file.read_text(encoding='utf-8')
    
    # Check for helper function
    if 'def get_db_connection():' in content:
        stats[py_file.name]['has_helper'] = True
    
    # Count patterns
    stats[py_file.name]['get_db_connection_calls'] = len(re.findall(r'= get_db_connection\(\)', content))
    stats[py_file.name]['context_managers'] = len(re.findall(r'with get_d(?:atabase_connection|b_connection)\(', content))
    stats[py_file.name]['manual_close'] = content.count('conn.close()')
    
    # Estimate no-close (calls - context managers - manual closes)
    calls = stats[py_file.name]['get_db_connection_calls']
    with_blocks = stats[py_file.name]['context_managers']
    closes = stats[py_file.name]['manual_close']
    stats[py_file.name]['no_close'] = max(0, calls - with_blocks - closes)

# Sort by risk (no_close count)
sorted_files = sorted(stats.items(), key=lambda x: x[1]['no_close'], reverse=True)

print('=' * 90)
print('CONNECTION LEAK RISK ANALYSIS - ALL ROUTE FILES')
print('=' * 90)
print()
print('LEGEND:')
print('  Calls: Total get_db_connection() calls')
print('  With: Context manager usage (SAFE)')
print('  Close: Manual conn.close() calls')
print('  Risk: Calls without proper cleanup (Calls - With - Close)')
print('  Helper: Has get_db_connection() helper function')
print()
print(f"{'File':<40} {'Calls':<7} {'With':<6} {'Close':<7} {'Risk':<6} Helper")
print('-' * 90)

for filename, data in sorted_files:
    if data['get_db_connection_calls'] > 0:
        helper_marker = 'YES' if data['has_helper'] else ''
        print(f"{filename:<40} {data['get_db_connection_calls']:<7} {data['context_managers']:<6} {data['manual_close']:<7} {data['no_close']:<6} {helper_marker}")

print()
print('=' * 90)
print('SUMMARY:')
total_calls = sum(d['get_db_connection_calls'] for d in stats.values())
total_with = sum(d['context_managers'] for d in stats.values())
total_close = sum(d['manual_close'] for d in stats.values())
total_risk = sum(d['no_close'] for d in stats.values())
helpers = sum(1 for d in stats.values() if d['has_helper'])

print(f'Total connection calls: {total_calls}')
print(f'Safe (context managers): {total_with}')
print(f'Manual closes: {total_close}')
print(f'At-risk (no proper cleanup): {total_risk}')
print(f'Files with helper functions: {helpers}')
print('=' * 90)

# High-risk files
print('\nHIGH-RISK FILES (Risk >= 10):')
print('-' * 90)
for filename, data in sorted_files:
    if data['no_close'] >= 10:
        print(f"  {filename}: {data['no_close']} potential leaks")

print('\n' + '=' * 90)
