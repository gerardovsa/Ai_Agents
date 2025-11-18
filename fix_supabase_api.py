"""
Fix Supabase API calls in automation workflow functions

Changes:
1. client.query('table').insert(data).execute() → client.insert('table', data)
2. client.query('table').update(data).eq().execute() → client.update('table', data, filters)
3. client.query('table').delete().eq().execute() → client.delete('table', filters)
4. query.order('col', desc=True) → query.order('col', ascending=False)
"""

import re

file_path = r'tools\implementations\supabase.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: INSERT operations
# Pattern: client.query('table').insert(data).execute()
# Replace with: client.insert('table', data)
content = re.sub(
    r"client\.query\('([^']+)'\)\.insert\(([^)]+)\)\.execute\(\)",
    r"client.insert('\1', \2)",
    content
)

# Fix 2: UPDATE operations with single eq filter
# Pattern: client.query('table').update(data).eq('col', val).execute()
# Replace with: client.update('table', data, {'col': val})
def replace_update_single_eq(match):
    table = match.group(1)
    data = match.group(2)
    col = match.group(3)
    val = match.group(4)
    return f"client.update('{table}', {data}, {{'{col}': {val}}})"

content = re.sub(
    r"client\.query\('([^']+)'\)\.update\(([^)]+)\)\.eq\('([^']+)',\s*([^)]+)\)\.execute\(\)",
    replace_update_single_eq,
    content
)

# Fix 3: DELETE operations with single eq filter
# Pattern: client.query('table').delete().eq('col', val).execute()
# Replace with: client.delete('table', {'col': val})
def replace_delete_single_eq(match):
    table = match.group(1)
    col = match.group(2)
    val = match.group(3)
    return f"client.delete('{table}', {{'{col}': {val}}})"

content = re.sub(
    r"client\.query\('([^']+)'\)\.delete\(\)\.eq\('([^']+)',\s*([^)]+)\)\.execute\(\)",
    replace_delete_single_eq,
    content
)

# Fix 4: order() with desc=True
# Pattern: query.order('col', desc=True)
# Replace with: query.order('col', ascending=False)
content = re.sub(
    r"\.order\('([^']+)',\s*desc=True\)",
    r".order('\1', ascending=False)",
    content
)

# Fix 5: order() with desc=False
# Pattern: query.order('col', desc=False)
# Replace with: query.order('col', ascending=True)
content = re.sub(
    r"\.order\('([^']+)',\s*desc=False\)",
    r".order('\1', ascending=True)",
    content
)

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Fixed Supabase API calls")
print("  - INSERT operations: query().insert() → client.insert()")
print("  - UPDATE operations: query().update().eq() → client.update()")
print("  - DELETE operations: query().delete().eq() → client.delete()")
print("  - ORDER BY: desc=True/False → ascending=False/True")
