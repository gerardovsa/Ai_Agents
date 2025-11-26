"""Test the actual thread list query"""
import sys
sys.path.insert(0, 'AI_infrastructure')
from shared.database_utils import get_database_connection
from psycopg2.extras import RealDictCursor

conn = get_database_connection('sessions')
cursor = conn.cursor(cursor_factory=RealDictCursor)

# Run the EXACT query from thread_routes.py
query = """
    SELECT 
        t.id,
        t.thread_slug, 
        t.name, 
        t.user_id, 
        t.created_at, 
        t.updated_at, 
        t.metadata, 
        t.location, 
        t.tags, 
        t.synergy_card_id, 
        t.synergy_card_name,
        t.parent_thread_id, 
        t.branch_name,
        t.workflow_id,
        t.workflow_name,
        t.workflow_slug,
        t.workflow_title,
        t.internal_doc_slug,
        t.internal_doc_title,
        COUNT(CASE 
            WHEN m.role = 'user' AND (
                m.metadata IS NULL 
                OR m.metadata::jsonb->>'tool_results' IS NULL 
                OR m.metadata::jsonb->>'tool_results' != 'true'
            ) THEN 1
            WHEN m.role = 'assistant' AND m.content::jsonb::text LIKE '%"type": "text"%' THEN 1
            ELSE NULL
        END) as message_count,
        MAX(m.created_at) as last_message_time,
        (SELECT role FROM sessions.messages WHERE thread_id = t.id ORDER BY created_at DESC LIMIT 1) as last_message_role
    FROM sessions.threads t
    LEFT JOIN sessions.messages m ON t.id = m.thread_id
    WHERE t.user_id = %s
    GROUP BY t.id, t.thread_slug, t.name, t.user_id, t.created_at, t.updated_at, 
             t.metadata, t.location, t.tags, t.synergy_card_id, t.synergy_card_name,
             t.parent_thread_id, t.branch_name, t.workflow_id, t.workflow_name,
             t.workflow_slug, t.workflow_title, t.internal_doc_slug, t.internal_doc_title
    ORDER BY t.updated_at DESC
    LIMIT %s
"""

cursor.execute(query, (14, 50))
rows = cursor.fetchall()

print(f"\n✅ Query returned {len(rows)} threads\n")

for i, row in enumerate(rows[:10], 1):
    print(f"{i}. {row['thread_slug']}: {row['name']}")
    print(f"   Message count: {row['message_count']}")
    print(f"   Location: {row['location']}")
    print()

conn.close()
