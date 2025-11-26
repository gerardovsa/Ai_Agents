"""Quick script to check thread data in database"""
import sys
sys.path.insert(0, 'AI_infrastructure')
from shared.database_utils import get_database_connection
from psycopg2.extras import RealDictCursor
import json

conn = get_database_connection('sessions')
cursor = conn.cursor(cursor_factory=RealDictCursor)

# Check total threads
cursor.execute("""
    SELECT COUNT(*) as total FROM sessions.threads WHERE user_id = 14
""")
total = cursor.fetchone()
print(f"\n✅ Total threads for user 14: {total['total']}")

# Check messages per thread
cursor.execute("""
    SELECT 
        t.thread_slug, 
        t.name,
        COUNT(m.id) as total_messages,
        COUNT(CASE WHEN m.role='user' THEN 1 END) as user_msgs,
        COUNT(CASE WHEN m.role='assistant' THEN 1 END) as assistant_msgs
    FROM sessions.threads t
    LEFT JOIN sessions.messages m ON t.id = m.thread_id
    WHERE t.user_id = 14
    GROUP BY t.id, t.thread_slug, t.name
    LIMIT 5
""")
threads = cursor.fetchall()
print(f"\n📊 First 5 threads:")
for r in threads:
    print(f"  {r['thread_slug']}: {r['name']}")
    print(f"    Total: {r['total_messages']} | User: {r['user_msgs']} | Assistant: {r['assistant_msgs']}")

# Check message content structure
cursor.execute("""
    SELECT m.role, m.content, m.metadata
    FROM sessions.messages m
    JOIN sessions.threads t ON m.thread_id = t.id
    WHERE t.user_id = 14
    LIMIT 3
""")
messages = cursor.fetchall()
print(f"\n📝 Sample messages:")
for i, m in enumerate(messages, 1):
    print(f"\nMessage {i}:")
    print(f"  Role: {m['role']}")
    if m['metadata']:
        print(f"  Metadata: {m['metadata']}")
    content = json.loads(m['content']) if isinstance(m['content'], str) else m['content']
    if isinstance(content, list):
        print(f"  Content blocks: {[b.get('type', 'unknown') for b in content]}")
    else:
        print(f"  Content: {str(content)[:100]}...")

# Test the CASE statement logic
cursor.execute("""
    SELECT 
        m.role,
        m.content::jsonb::text LIKE '%"type": "text"%' as has_text_type,
        m.metadata::jsonb->>'tool_results' as has_tool_results,
        CASE 
            WHEN m.role = 'user' AND (m.metadata IS NULL OR m.metadata::jsonb->>'tool_results' IS NULL) THEN 'COUNT'
            WHEN m.role = 'assistant' AND m.content::jsonb::text LIKE '%"type": "text"%' THEN 'COUNT'
            ELSE 'SKIP'
        END as count_decision
    FROM sessions.messages m
    JOIN sessions.threads t ON m.thread_id = t.id
    WHERE t.user_id = 14
    LIMIT 10
""")
decisions = cursor.fetchall()
print(f"\n🔍 CASE statement analysis (first 10 messages):")
for d in decisions:
    print(f"  Role: {d['role']:10} | Text: {d['has_text_type']} | Tool: {d['has_tool_results']} → {d['count_decision']}")

conn.close()
