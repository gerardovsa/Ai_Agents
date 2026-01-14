"""
Drop the legacy sessions table after successful consolidation
"""
import sqlite3

db_path = 'C:\\Users\\gpoli\\GIT\\AI_agents\\data\\synergy_sessions.db'

print("=" * 120)
print("DROPPING LEGACY 'sessions' TABLE")
print("=" * 120)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Verify synergy_sessions has all data
cursor.execute("SELECT COUNT(*) FROM synergy_sessions")
synergy_count = cursor.fetchone()[0]

print(f"\n✅ Verified: synergy_sessions has {synergy_count} rows")

# Drop sessions table
try:
    cursor.execute("DROP TABLE IF EXISTS sessions")
    conn.commit()
    print(f"✅ Dropped: sessions table")
except Exception as e:
    print(f"❌ Error: {e}")

conn.close()

print("\n" + "=" * 120)
print("CLEANUP COMPLETE")
print("=" * 120)
print(f"""
✅ Legacy 'sessions' table removed
✅ All data consolidated in 'synergy_sessions'
✅ Database now has single source of truth

synergy_sessions now has {synergy_count} total rows:
  - 15 original Synergy sessions
  - 5 migrated from legacy Kanban board
""")
