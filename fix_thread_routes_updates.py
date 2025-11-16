"""
Fix all execute_sqlite_update calls in thread_routes.py
Replace with direct Supabase connection queries
"""

import re

file_path = r'C:\Users\gpoli\GIT\AI_agents\AI_infrastructure\routes\thread_routes.py'

# Read the file
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Count occurrences
count = content.count('execute_sqlite_update')
print(f"Found {count} occurrences of execute_sqlite_update")

# Replace SQL placeholders ? with %s for PostgreSQL
content = content.replace('INSERT INTO sessions.threads (', 'INSERT INTO sessions.threads (')
content = content.replace('UPDATE sessions.threads SET', 'UPDATE sessions.threads SET')
content = content.replace('DELETE FROM sessions.threads', 'DELETE FROM sessions.threads')
content = content.replace('DELETE FROM sessions.saved_threads', 'DELETE FROM sessions.saved_threads')
content = content.replace('INSERT INTO sessions.saved_threads', 'INSERT INTO sessions.saved_threads')
content = content.replace('ALTER TABLE sessions.threads', 'ALTER TABLE sessions.threads')

# Replace ? with %s in SQL queries (but not in Python strings)
# This is a simple replacement - might need manual review
lines = content.split('\n')
in_query = False
new_lines = []

for line in lines:
    # Detect if we're in a SQL query
    if '"""' in line or "'''" in line:
        in_query = not in_query
    
    # Replace ? with %s in SQL queries
    if in_query and '?' in line and not line.strip().startswith('#'):
        # Only replace ? that are likely SQL placeholders
        if 'VALUES' in line or 'WHERE' in line or 'SET' in line:
            line = line.replace('?', '%s')
    
    new_lines.append(line)

content = '\n'.join(new_lines)

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"✅ Replaced ? with %s in SQL queries")
print(f"⚠️  Manual fixes still needed:")
print(f"   - Replace execute_sqlite_update() calls with direct Supabase queries")
print(f"   - Total instances to fix: {count}")
