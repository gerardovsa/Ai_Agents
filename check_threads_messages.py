"""Check threads and messages in database"""
import sys
sys.path.insert(0, 'AI_infrastructure')

from shared.database_utils import get_database_connection

conn = get_database_connection('sessions')
cursor = conn.cursor()

# Check threads
print("Recent threads:")
cursor.execute("SELECT id, thread_slug, name FROM sessions.threads ORDER BY created_at DESC LIMIT 5")
threads = cursor.fetchall()
for t in threads:
    print(f"  ID {t['id']}: {t['thread_slug']} - {t['name']}")

# Check messages
print("\nMessages in database:")
cursor.execute("SELECT thread_id, role, LEFT(content, 50) as content_preview FROM sessions.messages ORDER BY created_at DESC LIMIT 10")
messages = cursor.fetchall()
if messages:
    for m in messages:
        print(f"  Thread {m['thread_id']}: [{m['role']}] {m['content_preview']}...")
else:
    print("  ❌ NO MESSAGES FOUND")

# Count messages per thread
print("\nMessage count by thread:")
cursor.execute("""
    SELECT t.thread_slug, t.name, COUNT(m.id) as msg_count
    FROM sessions.threads t
    LEFT JOIN sessions.messages m ON m.thread_id = t.id
    GROUP BY t.id, t.thread_slug, t.name
    ORDER BY t.created_at DESC
    LIMIT 5
""")
counts = cursor.fetchall()
for c in counts:
    print(f"  {c['thread_slug']}: {c['msg_count']} messages ({c['name']})")

conn.close()
