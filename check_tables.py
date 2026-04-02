import sys
sys.path.insert(0, 'AI_infrastructure')
from shared.database_utils import execute_query

result = execute_query(
    """SELECT table_name FROM information_schema.tables 
       WHERE table_schema = 'ai_infrastructure' 
       AND table_name IN ('teams', 'team_members')
       ORDER BY table_name""",
    fetch_mode='all'
)
if result:
    for r in result:
        print('EXISTS:', r['table_name'])
else:
    print('MISSING: teams/team_members tables not found in production DB')
