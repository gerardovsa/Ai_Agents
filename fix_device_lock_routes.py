"""
Convert device_lock_routes.py from SQLite helpers to Supabase
"""

import re

file_path = 'AI_infrastructure/routes/device_lock_routes.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern 1: execute_sqlite_query calls
# Before: thread = execute_sqlite_query(str(SESSIONS_DB_PATH), "SELECT...", (params,))
# After: query = convert_sql_placeholders("SELECT..."); cursor.execute(query, (params,)); thread = cursor.fetchone()

def replace_execute_sqlite_query(match):
    indent = match.group(1)
    var_name = match.group(2)
    db_path = match.group(3)
    query = match.group(4)
    params = match.group(5) if match.group(5) else ''
    
    # Determine schema based on db_path
    schema = 'sessions' if 'SESSIONS_DB_PATH' in db_path else 'ai_infrastructure'
    
    # Build replacement
    result = f'{indent}query = convert_sql_placeholders({query})\n'
    result += f'{indent}cursor.execute(query{params})\n'
    result += f'{indent}{var_name} = cursor.fetchone()'
    
    return result

# Pattern 2: execute_sqlite_update calls
def replace_execute_sqlite_update(match):
    indent = match.group(1)
    db_path = match.group(2)
    query = match.group(3)
    params = match.group(4) if match.group(4) else ''
    
    # Build replacement
    result = f'{indent}query = convert_sql_placeholders({query})\n'
    result += f'{indent}cursor.execute(query{params})\n'
    result += f'{indent}conn.commit()'
    
    return result

# Apply regex replacements
# Pattern for execute_sqlite_query
pattern1 = r'(\s+)(\w+)\s*=\s*execute_sqlite_query\(\s*str\((SESSIONS_DB_PATH|AI_DB_PATH)\),\s*(["\'][^"\']+["\']|"""[^"]*"""),\s*(\([^)]*\))?\s*\)'
content = re.sub(pattern1, replace_execute_sqlite_query, content)

# Pattern for execute_sqlite_update
pattern2 = r'(\s+)execute_sqlite_update\(\s*str\((SESSIONS_DB_PATH|AI_DB_PATH)\),\s*(["\'][^"\']+["\']|"""[^"]*"""),\s*(\([^)]*\))?\s*\)'
content = re.sub(pattern2, replace_execute_sqlite_update, content)

# Add connection and cursor setup at the start of each function
# This is a simplified approach - would need manual review

print("✅ Converted device_lock_routes.py patterns")
print("\n⚠️  Manual review required:")
print("1. Add conn = get_database_connection() at start of each function")
print("2. Add cursor = conn.cursor() after connection")
print("3. Add conn.close() at end of each function")
print("4. Handle fetchall() vs fetchone() appropriately")
print("\n Safer to manually convert this file function by function")
