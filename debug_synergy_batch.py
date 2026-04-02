"""Debug script to trace the exact failure in GET /api/synergy/sessions/batch"""
import sys, json, traceback
sys.path.insert(0, 'AI_infrastructure')
from shared.database_utils import get_database_connection, convert_sql_placeholders

try:
    with get_database_connection('synergy_sessions') as conn:
        with conn.cursor() as cursor:
            print('[1] Loading sessions...')
            sql, params = convert_sql_placeholders("""
                SELECT * FROM synergy_sessions
                WHERE status != 'archived'
                ORDER BY last_active DESC
                LIMIT 5
            """, ())
            cursor.execute(sql, params)
            sessions_rows = cursor.fetchall()
            sessions = [dict(r) for r in sessions_rows]
            session_ids = [s['session_id'] for s in sessions]
            print(f'[1] OK - {len(sessions)} sessions, ids: {session_ids[:2]}')

            print('[2] Loading internal docs...')
            if session_ids:
                placeholders = ','.join('%s' for _ in session_ids)
                docs_sql = f"""
                    SELECT session_id, doc_id, title, doc_type, version,
                           created_at, updated_at, slug, share_url
                    FROM synergy_internal_docs
                    WHERE session_id IN ({placeholders})
                    ORDER BY session_id, created_at DESC
                """
                try:
                    cursor.execute(docs_sql, session_ids)
                    docs_rows = cursor.fetchall()
                    print(f'[2] OK - {len(docs_rows)} docs')
                except Exception as e:
                    print(f'[2] SKIPPED: {e}')

            print('[3] Milestone counts...')
            try:
                placeholders = ','.join('%s' for _ in session_ids)
                cursor.execute(
                    f"SELECT session_id, COUNT(*) as count FROM milestones WHERE session_id IN ({placeholders}) GROUP BY session_id",
                    session_ids
                )
                print(f'[3] OK - milestones: {cursor.fetchall()}')
            except Exception as e:
                print(f'[3] ERROR: {e}')
                traceback.print_exc()

            print('[4] Task counts...')
            try:
                cursor.execute(
                    f"""SELECT m.session_id, COUNT(t.task_id) as total_tasks
                        FROM milestones m LEFT JOIN tasks t ON m.milestone_id = t.milestone_id
                        WHERE m.session_id IN ({placeholders}) GROUP BY m.session_id""",
                    session_ids
                )
                print(f'[4] OK')
            except Exception as e:
                print(f'[4] ERROR: {e}')
                traceback.print_exc()

except Exception as e:
    print(f'\nFATAL: {e}')
    traceback.print_exc()
