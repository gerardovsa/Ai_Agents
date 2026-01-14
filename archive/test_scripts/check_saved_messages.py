"""Check if messages were saved"""
import sqlite3

conn = sqlite3.connect(r'C:\Users\gpoli\GIT\AI_agents\data\sessions.db')
cursor = conn.cursor()

cursor.execute('SELECT id, thread_id, role, content, created_at FROM messages ORDER BY id DESC LIMIT 10')
rows = cursor.fetchall()

print("=" * 80)
print(f"MESSAGES IN DATABASE: {len(rows)} (showing last 10)")
print("=" * 80)

for r in rows:
    print(f"\nID: {r[0]}, Thread: {r[1]}, Role: {r[2]}")
    print(f"Content: {r[3][:80]}...")
    print(f"Created: {r[4]}")

conn.close()
