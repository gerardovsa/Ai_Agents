"""Test milestone number query directly"""

import sys
sys.path.insert(0, 'AI_infrastructure')

from shared.database_utils import get_database_connection, convert_sql_placeholders

session_id = 'sess_20251124_1842_test_milestone_creation_fix'

conn = get_database_connection('synergy_sessions')
cursor = conn.cursor()

# Test the query
sql, params = convert_sql_placeholders('''
    SELECT COALESCE(MAX(milestone_number), 0) + 1 
    FROM synergy_sessions.milestones 
    WHERE session_id = %s
''', (session_id,))

print(f"SQL: {sql}")
print(f"Params: {params}")

cursor.execute(sql, params)
result = cursor.fetchone()

print(f"Result type: {type(result)}")
print(f"Result: {result}")

if result:
    milestone_number = result[0]
    print(f"Milestone number: {milestone_number}")

conn.close()
