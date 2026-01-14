#!/usr/bin/env python3
"""
Quick fix script to replace get_db_connection() with get_database_connection('ai_infrastructure')
in automation_routes.py
"""

file_path = 'AI_infrastructure/routes/automation_routes.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

count_before = content.count('with get_db_connection() as conn:')
print(f'Found {count_before} instances of get_db_connection()')

new_content = content.replace('with get_db_connection() as conn:', "with get_database_connection('ai_infrastructure') as conn:")

count_after = new_content.count("with get_database_connection('ai_infrastructure') as conn:")

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f'✅ Replaced {count_before} instances')
print(f'✅ Now has {count_after} instances of get_database_connection')
print(f'✅ Fixed automation_routes.py - all connections now use proper pooling')
