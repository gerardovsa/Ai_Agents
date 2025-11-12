"""Check checklist format in synergy database"""
import sqlite3
import json
from pathlib import Path

db_path = Path('data/synergy_sessions.db')
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

cursor.execute('SELECT session_id, checklist FROM synergy_sessions WHERE checklist IS NOT NULL AND checklist != "[]" LIMIT 5')
rows = cursor.fetchall()

print("CHECKLIST FORMAT ANALYSIS")
print("=" * 60)

for row in rows:
    if row[1]:
        session_id = row[0]
        try:
            checklist_data = json.loads(row[1])
            print(f"\n📋 Session: {session_id}")
            print(f"   Items count: {len(checklist_data)}")
            if checklist_data:
                first_item = checklist_data[0]
                print(f"   First item keys: {list(first_item.keys())}")
                print(f"   First item: {json.dumps(first_item, indent=6)}")
                
                # Check if any items have subtasks
                has_subtasks = any('subtasks' in item for item in checklist_data)
                print(f"   Has subtasks field: {has_subtasks}")
        except json.JSONDecodeError as e:
            print(f"\n❌ Session: {session_id} - Invalid JSON: {e}")

conn.close()
print("\n" + "=" * 60)
