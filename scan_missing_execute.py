#!/usr/bin/env python3
"""
Scan synergy_routes copy.py for missing cursor.execute() calls after convert_sql_placeholders()
"""

import re

file_path = r"c:\Users\gpoli\GIT\AI_agents\AI_infrastructure\routes\synergy_routes copy.py"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

issues = []
in_sql_block = False
sql_start_line = None
sql_var_name = None

for i, line in enumerate(lines, 1):
    # Look for convert_sql_placeholders assignments
    match = re.search(r'(\w+),\s*(\w+)\s*=\s*convert_sql_placeholders\(', line)
    if match:
        sql_var_name = match.group(1)
        sql_start_line = i
        in_sql_block = True
        continue
    
    # If we're tracking a SQL block, look for cursor.execute
    if in_sql_block:
        # Check next 5 lines for cursor.execute using the sql variable
        if i - sql_start_line > 10:
            # Too far, assume it's missing
            issues.append({
                'line': sql_start_line,
                'sql_var': sql_var_name,
                'context': lines[sql_start_line-1].strip()[:80]
            })
            in_sql_block = False
            sql_var_name = None
            sql_start_line = None
        elif f'cursor.execute({sql_var_name}' in line or f'cursor.execute(sql' in line:
            # Found it, good
            in_sql_block = False
            sql_var_name = None
            sql_start_line = None

print("=" * 80)
print("MISSING cursor.execute() CALLS")
print("=" * 80)
print()

if not issues:
    print("✅ No issues found! All convert_sql_placeholders() calls are followed by cursor.execute()")
else:
    print(f"❌ Found {len(issues)} potential issues:")
    print()
    for issue in issues:
        print(f"Line {issue['line']}: {issue['context']}")
        print(f"  Variable: {issue['sql_var']}")
        print()

print()
print("Note: This is a heuristic scan. Manual review recommended.")
