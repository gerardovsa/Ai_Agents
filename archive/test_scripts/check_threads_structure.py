"""Check threads table structure and understand relationships"""
import sqlite3
from shared.database_utils import convert_sql_placeholders

sessions_db = r'C:\Users\gpoli\GIT\AI_agents\data\sessions.db'
infra_db = r'C:\Users\gpoli\GIT\AI_agents\data\ai_infrastructure.db'

print("=" * 80)
print("CURRENT THREAD ARCHITECTURE:")
print("=" * 80)

# Check sessions.db threads table
conn_sessions = sqlite3.connect(sessions_db)
cursor = conn_sessions.cursor()

print("\nsessions.db - threads table:")
cursor.execute("PRAGMA table_info(threads)")
columns = cursor.fetchall()
for col in columns:
    print(f"  - {col[1]:25s} {col[2]:15s}")

# Check if workspace_id exists
has_workspace_id = any(col[1] == 'workspace_id' for col in columns)
print(f"\n  Has workspace_id? {has_workspace_id}")

# Check sample data
cursor.execute("SELECT thread_slug, name, user_id, message_count FROM threads LIMIT 5")
threads = cursor.fetchall()
print(f"\n  Sample threads ({len(threads)} rows):")
for t in threads:
    print(f"    thread_slug: {t[0]}, name: {t[1]}, user_id: {t[2]}, messages: {t[3]}")

conn_sessions.close()

# Check ai_infrastructure.db workspaces table
conn_infra = sqlite3.connect(infra_db)
cursor = conn_infra.cursor()

print("\n" + "=" * 80)
print("ai_infrastructure.db - workspaces table:")
print("=" * 80)
cursor.execute("PRAGMA table_info(workspaces)")
columns = cursor.fetchall()
for col in columns:
    print(f"  - {col[1]:25s} {col[2]:15s}")

# Check sample data
cursor.execute("SELECT id, user_id, name, description FROM workspaces")
workspaces = cursor.fetchall()
print(f"\n  Existing workspaces ({len(workspaces)} rows):")
for w in workspaces:
    print(f"    id: {w[0]}, user_id: {w[1]}, name: {w[2]}, desc: {w[3]}")

# Check users table
cursor.execute("PRAGMA table_info(users)")
columns = cursor.fetchall()
has_user_slug = any(col[1] == 'user_slug' or col[1] == 'slug' for col in columns)
print(f"\n  Users table has user_slug? {has_user_slug}")

conn_infra.close()

print("\n" + "=" * 80)
print("RECOMMENDATIONS:")
print("=" * 80)
print("""
CURRENT ARCHITECTURE:
- workspaces: In ai_infrastructure.db (user_id based - single owner)
- threads: In sessions.db (no workspace_id yet)
- users: In ai_infrastructure.db (no user_slug yet)

RECOMMENDED CHANGES FOR MULTI-USER WORKSPACES:

1. Add workspace_slug to workspaces table:
   - workspace_slug (unique identifier like 'team-alpha-2025')
   - Makes workspaces shareable via URL

2. Add user_slug to users table:
   - user_slug (unique identifier like 'john-doe-2025')
   - Better than exposing user_id in URLs

3. Add workspace_id to threads table:
   - Links threads to workspaces
   - Required for ThreadManager to work

4. Create workspace_users junction table:
   - workspace_id, user_id, role, permissions
   - Allows multiple users per workspace
   - Supports roles: owner, admin, member, viewer

5. Thread access control - TWO OPTIONS:

   OPTION A: workspace_users (RECOMMENDED for teams):
   - Access controlled at workspace level
   - All workspace members see all threads
   - Simpler, better for collaboration
   
   OPTION B: thread_users junction table:
   - Per-thread access control
   - More granular but complex
   - Use case: personal threads within shared workspace

6. Storage format for user lists (if needed):
   - JSON array: ["user1-slug", "user2-slug"] 
   - Pros: Easy to query, structured
   - Cons: Harder to index/search
   - BETTER: Use junction table (workspace_users)
""")
