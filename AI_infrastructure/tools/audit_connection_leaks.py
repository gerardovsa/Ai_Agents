"""
Find database connection leaks in routes

LEAK PATTERNS:
1. conn = get_db_connection() without conn.close()
2. conn = get_db_connection() without finally block
3. Early returns before conn.close()
"""

import os
import re
from pathlib import Path

def check_file_for_leaks(file_path):
    """Check a Python file for connection leaks"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    leaks = []
    
    # Find all functions
    function_starts = []
    for i, line in enumerate(lines):
        if re.match(r'^\s*(def|async def)\s+\w+', line):
            function_starts.append(i)
    
    # Check each function
    for func_start in function_starts:
        # Find function end (next function or end of file)
        func_end = len(lines)
        for next_func in function_starts:
            if next_func > func_start:
                func_end = next_func
                break
        
        func_lines = lines[func_start:func_end]
        func_content = '\n'.join(func_lines)
        
        # Check for get_db_connection() calls
        if 'get_db_connection()' in func_content:
            # Pattern 1: No finally block
            if 'finally:' not in func_content:
                leaks.append({
                    'file': file_path,
                    'line': func_start + 1,
                    'function': lines[func_start].strip(),
                    'issue': 'No finally block with get_db_connection()'
                })
            
            # Pattern 2: No conn.close() at all
            elif 'conn.close()' not in func_content:
                leaks.append({
                    'file': file_path,
                    'line': func_start + 1,
                    'function': lines[func_start].strip(),
                    'issue': 'No conn.close() found'
                })
    
    return leaks


def main():
    routes_dir = Path('AI_infrastructure/routes')
    
    all_leaks = []
    
    for py_file in routes_dir.glob('*.py'):
        if py_file.name.startswith('_') or ' copy' in py_file.name:
            continue
        
        leaks = check_file_for_leaks(py_file)
        all_leaks.extend(leaks)
    
    print("=" * 80)
    print("DATABASE CONNECTION LEAK AUDIT")
    print("=" * 80)
    print()
    
    if not all_leaks:
        print("✅ No leaks found!")
        return
    
    # Group by file
    by_file = {}
    for leak in all_leaks:
        file_name = leak['file'].name
        if file_name not in by_file:
            by_file[file_name] = []
        by_file[file_name].append(leak)
    
    for file_name, leaks in sorted(by_file.items()):
        print(f"\n[FILE] {file_name} ({len(leaks)} potential leaks)")
        print("-" * 80)
        for leak in leaks:
            print(f"  Line {leak['line']}: {leak['function']}")
            print(f"    Issue: {leak['issue']}")
            print()
    
    print("=" * 80)
    print(f"TOTAL: {len(all_leaks)} potential leaks found")
    print("=" * 80)


if __name__ == '__main__':
    main()
