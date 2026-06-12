"""
Replace ALL execute_sqlite_update calls with direct Supabase queries
"""

import re

file_path = r'C:\Users\gpoli\GIT\AI_agents\AI_infrastructure\routes\thread_routes.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern 1: Simple execute_sqlite_update with params
# execute_sqlite_update(db_path, query, params)
pattern1 = r'execute_sqlite_update\(\s*db_path,\s*(\w+),\s*([^)]+)\)'

def replace_pattern1(match):
    query_var = match.group(1)
    params = match.group(2)
    
    return f'''conn = get_database_connection('sessions')
        cursor = conn.cursor()
        cursor.execute({query_var}, {params})
        conn.commit()
        conn.close()'''

# Pattern 2: Assignment from execute_sqlite_update
# rowcount = execute_sqlite_update(db_path, query, params)
pattern2 = r'(\w+)\s*=\s*execute_sqlite_update\(\s*db_path,\s*(\w+),\s*([^)]+)\)'

def replace_pattern2(match):
    var_name = match.group(1)
    query_var = match.group(2)
    params = match.group(3)
    
    return f'''conn = get_database_connection('sessions')
        cursor = conn.cursor()
        cursor.execute({query_var}, {params})
        conn.commit()
        {var_name} = cursor.rowcount
        conn.close()'''

# Apply replacements
content = re.sub(pattern2, replace_pattern2, content)
content = re.sub(pattern1, replace_pattern1, content)

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Replaced all execute_sqlite_update calls with direct Supabase queries")
print("✅ Added conn.commit() and conn.close() calls")
print("✅ Replaced rowcount assignments")
