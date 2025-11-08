"""Check thread 1762593367878 complete analysis"""

import sqlite3
from pathlib import Path
import json

# Database paths
root_dir = Path(__file__).parent
sessions_db = root_dir / 'data' / 'sessions.db'
ai_db = root_dir / 'data' / 'ai_infrastructure.db'

print("=" * 80)
print("THREAD ANALYSIS: 1762593367878")
print("=" * 80)

# Check saved_threads
conn = sqlite3.connect(str(sessions_db))
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("""
    SELECT * FROM saved_threads 
    WHERE thread_id LIKE '%1762593367878%'
""")

saved_thread = cursor.fetchone()
if saved_thread:
    print("\nFOUND IN SAVED_THREADS:")
    print(f"  Thread ID: {saved_thread['thread_id']}")
    print(f"  Thread Name: {saved_thread['thread_name']}")
    print(f"  Location: {saved_thread['location']}")
    print(f"  Agent: {saved_thread['agent_id']}")
    print(f"  User ID: {saved_thread['user_id']}")
    print(f"  Message Count: {saved_thread['message_count']}")
    print(f"  Saved At: {saved_thread['saved_at']}")
    
    # Parse conversation
    if saved_thread['conversation']:
        try:
            convo = json.loads(saved_thread['conversation'])
            print(f"\n  CONVERSATION ({len(convo)} messages):")
            for i, msg in enumerate(convo, 1):
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')
                preview = content[:150].replace('\n', ' ')
                if len(content) > 150:
                    preview += "..."
                print(f"\n    {i}. [{role.upper()}]")
                print(f"       {preview}")
        except Exception as e:
            print(f"\n  ERROR parsing conversation: {e}")

# Check thread_assignments table structure
print("\n\n" + "=" * 80)
print("THREAD_ASSIGNMENTS TABLE STRUCTURE:")
print("=" * 80)

ai_conn = sqlite3.connect(str(ai_db))
ai_conn.row_factory = sqlite3.Row
ai_cursor = ai_conn.cursor()

ai_cursor.execute("PRAGMA table_info(thread_assignments)")
columns = ai_cursor.fetchall()
print("\nColumns:")
for col in columns:
    print(f"  - {col['name']} ({col['type']})")

# Check all assignments
ai_cursor.execute("SELECT * FROM thread_assignments")
all_assignments = ai_cursor.fetchall()
print(f"\nTotal assignments in table: {len(all_assignments)}")
if all_assignments:
    print("\nALL ASSIGNMENTS:")
    for assign in all_assignments:
        print(f"  ID: {assign['id']}")
        for key in assign.keys():
            if key != 'id':
                print(f"    {key}: {assign[key]}")
        print()

conn.close()
ai_conn.close()
