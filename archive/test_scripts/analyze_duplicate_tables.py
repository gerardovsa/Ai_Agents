"""
Analyze the two tables: 'sessions' vs 'synergy_sessions'
Why do we have both? What's the difference?
"""
import json
from shared.database_utils import convert_sql_placeholders

schema_file = 'c:\\Users\\gpoli\\GIT\\AI_agents\\data\\schema_C__Users_gpoli_GIT_AI_agents_data_synergy_sessions.db.json'

with open(schema_file, 'r') as f:
    schema = json.load(f)

print("=" * 120)
print("DATABASE TABLE ANALYSIS: sessions vs synergy_sessions")
print("=" * 120)

# Extract field names
sessions_fields = [field['name'] for field in schema['sessions']]
synergy_fields = [field['name'] for field in schema['synergy_sessions']]

print(f"\n1. TABLE: 'sessions'")
print("-" * 120)
print(f"Total fields: {len(sessions_fields)}")
print(f"Fields: {', '.join(sessions_fields)}")

print(f"\n\n2. TABLE: 'synergy_sessions'")
print("-" * 120)
print(f"Total fields: {len(synergy_fields)}")
print(f"Fields: {', '.join(synergy_fields)}")

# Find common fields
common_fields = set(sessions_fields) & set(synergy_fields)
print(f"\n\n3. COMMON FIELDS (in both tables)")
print("-" * 120)
print(f"Count: {len(common_fields)}")
print(f"Fields: {', '.join(sorted(common_fields))}")

# Find unique to sessions
unique_to_sessions = set(sessions_fields) - set(synergy_fields)
print(f"\n\n4. UNIQUE TO 'sessions' table")
print("-" * 120)
print(f"Count: {len(unique_to_sessions)}")
print(f"Fields: {', '.join(sorted(unique_to_sessions))}")

# Find unique to synergy_sessions
unique_to_synergy = set(synergy_fields) - set(sessions_fields)
print(f"\n\n5. UNIQUE TO 'synergy_sessions' table")
print("-" * 120)
print(f"Count: {len(unique_to_synergy)}")
print(f"Fields: {', '.join(sorted(unique_to_synergy))}")

print("\n\n" + "=" * 120)
print("ANALYSIS & HYPOTHESIS")
print("=" * 120)

print("\n📊 FIELD COMPARISON:")
print(f"   sessions:         {len(sessions_fields)} fields")
print(f"   synergy_sessions: {len(synergy_fields)} fields")
print(f"   Common:           {len(common_fields)} fields")

print("\n🔍 KEY DIFFERENCES:")
print("\n   'sessions' has:")
for field in sorted(unique_to_sessions):
    print(f"      - {field}")

print("\n   'synergy_sessions' has:")
for field in sorted(unique_to_synergy):
    print(f"      - {field}")

print("\n\n💡 HYPOTHESIS:")
print("-" * 120)
print("""
THEORY 1: Legacy vs New
  - 'sessions' = Old/deprecated table (has google_calendar_event_id, notes, project_name, session_data)
  - 'synergy_sessions' = Current/active table (has thread_ids, assigned_agents, platforms_involved)
  - synergy_sessions looks more feature-rich and specific to Synergy Dashboard

THEORY 2: Different Purposes
  - 'sessions' = Generic AI chat sessions (any conversation)
  - 'synergy_sessions' = Synergy Dashboard project sessions (Kanban board items)
  - This would explain why synergy_sessions has 'platforms_involved', 'thread_ids', 'assigned_agents'

RECOMMENDATION:
  1. Check which table is actively used in code
  2. Check if 'sessions' has any data
  3. Consider deprecating/removing unused table
  4. Consolidate to single source of truth
""")

# Now check actual data
print("\n" + "=" * 120)
print("CHECKING ACTUAL DATA")
print("=" * 120)

import sqlite3

db_path = 'C:\\Users\\gpoli\\GIT\\AI_agents\\data\\synergy_sessions.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check sessions table
try:
    cursor.execute("SELECT COUNT(*) FROM sessions")
    sessions_count = cursor.fetchone()[0]
    print(f"\n✅ 'sessions' table exists: {sessions_count} rows")
except:
    sessions_count = None
    print(f"\n❌ 'sessions' table does not exist or is empty")

# Check synergy_sessions table
try:
    cursor.execute("SELECT COUNT(*) FROM synergy_sessions")
    synergy_count = cursor.fetchone()[0]
    print(f"✅ 'synergy_sessions' table exists: {synergy_count} rows")
except:
    synergy_count = None
    print(f"❌ 'synergy_sessions' table does not exist or is empty")

conn.close()

print("\n" + "=" * 120)
print("CONCLUSION")
print("=" * 120)

if sessions_count is None and synergy_count is not None:
    print("\n🎯 VERDICT: 'sessions' table is UNUSED")
    print("   - Only 'synergy_sessions' has data")
    print("   - 'sessions' is likely a legacy/deprecated table")
    print("   - Schema file may be outdated or include unused table definition")
    print("\n   RECOMMENDATION: Remove 'sessions' table definition from schema")
elif sessions_count == 0 and synergy_count > 0:
    print("\n🎯 VERDICT: 'sessions' table is EMPTY")
    print("   - Only 'synergy_sessions' is actively used")
    print("   - 'sessions' exists but has no data (legacy)")
    print("\n   RECOMMENDATION: Drop 'sessions' table, use only 'synergy_sessions'")
elif sessions_count > 0 and synergy_count > 0:
    print("\n🎯 VERDICT: BOTH tables are in use")
    print("   - Need to check which code uses which table")
    print("   - May serve different purposes")
    print("\n   RECOMMENDATION: Document purpose of each table clearly")
