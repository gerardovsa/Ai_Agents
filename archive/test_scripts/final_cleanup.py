"""Final cleanup - keep only real user conversation"""
from shared.database_utils import convert_sql_placeholders

import sqlite3
from pathlib import Path

root_dir = Path(__file__).parent
db_path = root_dir / 'data' / 'sessions.db'

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Delete test messages by ID
test_message_ids = [54, 61, 62, 63]

print("="*60)
print("FINAL CLEANUP")
print("="*60)
print(f"\nDeleting test messages: {test_message_ids}")

placeholders = ','.join('?' * len(test_message_ids))
cursor.execute(f"DELETE FROM messages WHERE id IN ({placeholders})", test_message_ids)

deleted = cursor.rowcount
conn.commit()

print(f"✅ Deleted {deleted} test messages")

# Show remaining
cursor.execute("""
    SELECT id, role, content, created_at 
    FROM messages 
    WHERE thread_id = 1 
    ORDER BY created_at
""")
remaining = cursor.fetchall()

print(f"\n📊 FINAL MESSAGES ({len(remaining)}):")
for msg_id, role, content, created_at in remaining:
    preview = content[:70] + '...' if len(content) > 70 else content
    print(f"\n  {msg_id}. [{role}]")
    print(f"     {preview}")
    print(f"     {created_at}")

conn.close()

print("\n" + "="*60)
print("✅ DONE! You now have only your real conversation.")
print("   Restart Flask and refresh browser.")
print("="*60)
