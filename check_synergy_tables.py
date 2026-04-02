import sys
sys.path.insert(0, 'AI_infrastructure')
from shared.database_utils import get_database_connection

with get_database_connection('synergy_sessions') as conn:
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT table_schema, table_name FROM information_schema.tables "
            "WHERE table_name IN ('milestones','tasks','subtasks') "
            "ORDER BY table_schema, table_name"
        )
        rows = cursor.fetchall()
        if rows:
            for r in rows:
                print(dict(r))
        else:
            print('NONE: milestones/tasks/subtasks not found in any schema')

        # Also check synergy_sessions schema tables
        cursor.execute(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'synergy_sessions' ORDER BY table_name"
        )
        print('\nAll tables in synergy_sessions schema:')
        for r in cursor.fetchall():
            print(' ', dict(r)['table_name'])
