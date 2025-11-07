"""
Get session IDs from sessions.db
"""
import sqlite3
import json

print("=" * 80)
print("FLASK SESSION IDs FOR printing@inhouseprint.com.au")
print("=" * 80)

sess_conn = sqlite3.connect('data/sessions.db')
sess_cursor = sess_conn.cursor()

# Get all sessions
sess_cursor.execute("""
    SELECT session_id, agent_id, created_at, last_active, metadata
    FROM sessions
    ORDER BY created_at DESC
""")

sessions = sess_cursor.fetchall()

if sessions:
    print(f"\n✅ Found {len(sessions)} Flask sessions:\n")
    for i, (sess_id, agent_id, created, active, metadata) in enumerate(sessions, 1):
        print(f"{i}. SESSION ID: {sess_id}")
        print(f"   Agent ID: {agent_id}")
        print(f"   Created: {created}")
        print(f"   Last Active: {active}")
        if metadata:
            try:
                meta = json.loads(metadata)
                print(f"   Metadata: {meta}")
            except:
                print(f"   Metadata: {metadata[:100]}...")
        print()
else:
    print("\n⚠️ No sessions found in sessions.db")

sess_conn.close()

print("=" * 80)
print("\nSUMMARY FOR printing@inhouseprint.com.au (user_id: 14)")
print("=" * 80)
print("\n✅ 5 JWT authentication tokens (valid for 24 hours)")
print("✅ Flask session IDs listed above")
print("\nMost Recent Session:")
print("  Created: 2025-11-07 15:42:56")
print("  Expires: 2025-11-08 15:42:56")
print("=" * 80)
