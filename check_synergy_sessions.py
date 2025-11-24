"""Check Synergy sessions in database"""
import sys
sys.path.insert(0, 'AI_infrastructure')
from shared.database_utils import get_synergy_sessions_connection
import psycopg2.extras

conn = get_synergy_sessions_connection()
cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

# Get recent sessions
cursor.execute("""
    SELECT session_id, title, priority, uses_milestones, status, kanban_column
    FROM synergy_sessions.synergy_sessions 
    ORDER BY created_at DESC 
    LIMIT 10
""")

rows = cursor.fetchall()

print('=' * 70)
print('RECENTLY CREATED SYNERGY SESSIONS')
print('=' * 70)
print()

for row in rows:
    print(f'Session: {row["session_id"]}')
    print(f'  Title: {row["title"]}')
    print(f'  Priority: {row["priority"]}')
    print(f'  Uses Milestones: {row["uses_milestones"]}')
    print(f'  Status: {row["status"]}')
    print(f'  Column: {row["kanban_column"]}')
    print()

# Get milestone count
cursor.execute("""
    SELECT COUNT(*) as count FROM synergy_sessions.milestones
""")
milestone_count = cursor.fetchone()['count']

print(f'Total milestones in database: {milestone_count}')

conn.close()
