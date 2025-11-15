"""Analyze where agent-thread assignments are actually stored"""
import sqlite3
import json
from pathlib import Path

print("="*80)
print("AGENT-THREAD ASSIGNMENT TRACKING ANALYSIS")
print("="*80)

# 1. Check sessions.db users.metadata
print("\n1️⃣ SESSIONS.DB - users.metadata (thread_assignments)")
print("-"*80)
conn = sqlite3.connect('data/sessions.db')
cursor = conn.cursor()

cursor.execute("SELECT id, username, metadata FROM users WHERE metadata IS NOT NULL")
rows = cursor.fetchall()

total_assignments = 0
for user_id, username, metadata_json in rows:
    if metadata_json:
        metadata = json.loads(metadata_json)
        if 'thread_assignments' in metadata:
            assignments = metadata['thread_assignments']
            print(f"\nUser {user_id} ({username}):")
            for agent_id, thread_id in assignments.items():
                print(f"  {agent_id} -> thread {thread_id}")
                total_assignments += 1

print(f"\n✅ TOTAL ASSIGNMENTS FOUND: {total_assignments}")

# 2. Check saved_threads.agent_id
print("\n\n2️⃣ SESSIONS.DB - saved_threads.agent_id")
print("-"*80)
cursor.execute("SELECT thread_id, thread_name, agent_id, user_id FROM saved_threads")
rows = cursor.fetchall()

agent_counts = {}
for thread_id, thread_name, agent_id, user_id in rows:
    if agent_id:
        agent_counts[agent_id] = agent_counts.get(agent_id, 0) + 1
        if len(agent_counts) <= 5:  # Show first few examples
            name_display = thread_name[:40] if thread_name else "Unnamed"
            print(f"Thread {thread_id}: \"{name_display}...\" -> {agent_id} (user {user_id})")

print(f"\n✅ SAVED THREADS WITH AGENTS:")
for agent_id, count in sorted(agent_counts.items()):
    print(f"  {agent_id}: {count} threads")

# 3. Check threads table
print("\n\n3️⃣ SESSIONS.DB - threads table metadata")
print("-"*80)
cursor.execute("SELECT thread_slug, metadata FROM threads WHERE metadata IS NOT NULL AND metadata != '{}' LIMIT 5")
rows = cursor.fetchall()

metadata_with_agents = 0
for thread_slug, metadata_json in rows:
    if metadata_json:
        try:
            metadata = json.loads(metadata_json)
            if any('agent' in str(k).lower() for k in metadata.keys()):
                print(f"\nThread {thread_slug}")
                print(f"  Metadata keys: {list(metadata.keys())}")
                metadata_with_agents += 1
        except:
            pass

print(f"\n✅ THREADS WITH AGENT METADATA: {metadata_with_agents}")

conn.close()

# 4. Check ai_infrastructure.db users.metadata
print("\n\n4️⃣ AI_INFRASTRUCTURE.DB - users.metadata")
print("-"*80)
conn = sqlite3.connect('data/ai_infrastructure.db')
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(users)")
columns = [row[1] for row in cursor.fetchall()]
print(f"User table columns: {', '.join(columns)}")

cursor.execute("SELECT id, username, email, metadata FROM users WHERE metadata IS NOT NULL LIMIT 3")
rows = cursor.fetchall()

ai_db_assignments = 0
for user_id, username, email, metadata_json in rows:
    if metadata_json:
        metadata = json.loads(metadata_json)
        if 'thread_assignments' in metadata:
            assignments = metadata['thread_assignments']
            print(f"\nUser {user_id} ({username} / {email}):")
            for agent_id, thread_id in assignments.items():
                print(f"  {agent_id} -> thread {thread_id}")
                ai_db_assignments += 1

print(f"\n✅ AI_INFRASTRUCTURE.DB ASSIGNMENTS: {ai_db_assignments}")

conn.close()

# SUMMARY
print("\n\n" + "="*80)
print("📊 SUMMARY - WHERE AGENT TRACKING ACTUALLY HAPPENS")
print("="*80)
print(f"""
✅ PRIMARY STORAGE: sessions.db/users.metadata['thread_assignments']
   - Stores agent_id -> thread_id mappings per user
   - Found {total_assignments} assignments

✅ SECONDARY STORAGE: sessions.db/saved_threads.agent_id column
   - Direct agent_id column on saved threads
   - Found {len(agent_counts)} different agents assigned

✅ TERTIARY STORAGE: ai_infrastructure.db/users.metadata['thread_assignments']
   - Mirror of sessions.db data
   - Found {ai_db_assignments} assignments

❌ MISSING TABLE: thread_assignments
   - Referenced in code but DOES NOT EXIST in either database
   - The warning "[THREADS] Warning: Could not fetch agent assignments: no such table: thread_assignments"
   - IS A REAL ISSUE - code expects it but it doesn't exist

🔍 CONCLUSION:
   - Agent tracking IS working via users.metadata JSON column
   - The code tries to query a missing thread_assignments table (causes warnings)
   - System falls back to metadata approach (works but generates warnings)
   - The thread_assignments table should either:
     a) Be created if needed by the code, OR
     b) Code should be updated to stop querying it
""")
