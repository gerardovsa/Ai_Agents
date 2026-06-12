#!/usr/bin/env python3
"""
Find and fix ALL missing cursor.execute() calls in synergy_routes copy.py
"""

import re

file_path = r"c:\Users\gpoli\GIT\AI_agents\AI_infrastructure\routes\synergy_routes copy.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()
    lines = content.split('\n')

# Find all convert_sql_placeholders patterns
pattern = r'(\s*)([\w_]+),\s*([\w_]+)\s*=\s*convert_sql_placeholders\('

bugs_found = []

for i, line in enumerate(lines):
    match = re.search(pattern, line)
    if match:
        indent = match.group(1)
        sql_var = match.group(2)
        params_var = match.group(3)
        
        # Check next 15 lines for cursor.execute
        found_execute = False
        for j in range(i+1, min(i+15, len(lines))):
            if 'cursor.execute(' in lines[j]:
                found_execute = True
                break
            # If we hit another statement block or function, stop looking
            if lines[j].strip() and not lines[j].strip().startswith((')', ',', '"""', "'''", '#', 'FROM', 'WHERE', 'VALUES', 'SET', 'AND', 'OR', 'ORDER', 'GROUP')):
                # Check if this line is part of the SQL string
                if not lines[j-1].strip().endswith((',', '(', 'AND', 'OR', 'WHERE', 'SET', 'VALUES')):
                    break
        
        if not found_execute:
            bugs_found.append({
                'line_num': i + 1,
                'line': line,
                'sql_var': sql_var,
                'params_var': params_var,
                'indent': indent,
                'context_before': lines[max(0, i-2):i],
                'context_after': lines[i+1:min(i+6, len(lines))]
            })

print("=" * 80)
print(f"BUGS FOUND: {len(bugs_found)} missing cursor.execute() calls")
print("=" * 80)
print()

for bug in bugs_found:
    print(f"Line {bug['line_num']}:")
    print(f"  {bug['line'][:80]}")
    print(f"  Variables: {bug['sql_var']}, {bug['params_var']}")
    print(f"  Next line: {bug['context_after'][0][:80] if bug['context_after'] else 'EOF'}")
    print()

print()
print("SUMMARY:")
print(f"  Total bugs: {len(bugs_found)}")
print(f"  Need to add cursor.execute({bugs_found[0]['sql_var']}, {bugs_found[0]['params_var']}) after each")
