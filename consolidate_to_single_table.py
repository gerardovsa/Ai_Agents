"""
CONSOLIDATION PLAN: Merge sessions → synergy_sessions
1. Add missing columns to synergy_sessions
2. Migrate 5 rows from sessions to synergy_sessions
3. Drop sessions table
"""
import sqlite3
from datetime import datetime

db_path = 'C:\\Users\\gpoli\\GIT\\AI_agents\\data\\synergy_sessions.db'

print("=" * 120)
print("CONSOLIDATION: sessions → synergy_sessions")
print("=" * 120)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Step 1: Add missing columns to synergy_sessions
print("\n📝 STEP 1: Adding missing columns to synergy_sessions")
print("-" * 120)

missing_columns = [
    ('project_name', 'TEXT'),
    ('notes', 'TEXT'),
    ('session_data', 'TEXT'),
    ('google_calendar_event_id', 'TEXT'),
    ('updated_at', 'TEXT'),
    ('shared_with_users', 'TEXT'),  # NEW: JSON array of user_ids who can access this
    ('owner_user_id', 'INTEGER')    # NEW: User who created this session
]

for col_name, col_type in missing_columns:
    try:
        cursor.execute(f"ALTER TABLE synergy_sessions ADD COLUMN {col_name} {col_type}")
        print(f"   ✅ Added column: {col_name} ({col_type})")
    except sqlite3.OperationalError as e:
        if 'duplicate column name' in str(e):
            print(f"   ⚠️  Column already exists: {col_name}")
        else:
            print(f"   ❌ Error adding {col_name}: {e}")

conn.commit()

# Step 2: Check data in sessions table
print("\n\n📊 STEP 2: Checking sessions table data")
print("-" * 120)

cursor.execute("SELECT * FROM sessions")
sessions_data = cursor.fetchall()
print(f"Found {len(sessions_data)} rows in sessions table")

if sessions_data:
    cursor.execute("PRAGMA table_info(sessions)")
    sessions_columns = [col[1] for col in cursor.fetchall()]
    print(f"Columns: {', '.join(sessions_columns)}")

# Step 3: Migrate data
print("\n\n🔄 STEP 3: Migrating data from sessions → synergy_sessions")
print("-" * 120)

migrated = 0
errors = 0

for row in sessions_data:
    try:
        # Map sessions columns to synergy_sessions
        session_dict = dict(zip(sessions_columns, row))
        
        # Check if already exists in synergy_sessions
        cursor.execute("SELECT COUNT(*) FROM synergy_sessions WHERE session_id = ?", 
                      (session_dict['session_id'],))
        if cursor.fetchone()[0] > 0:
            print(f"   ⚠️  Skipping {session_dict['session_id'][:50]} - already exists")
            continue
        
        # Insert into synergy_sessions
        cursor.execute("""
            INSERT INTO synergy_sessions (
                session_id, title, description, priority, status, kanban_column,
                due_date, created_at, assignees, tags, documents, links,
                next_steps, checklist, google_task_id,
                project_name, notes, session_data, google_calendar_event_id,
                updated_at, last_active,
                platforms_involved, thread_ids, assigned_agents, recent_activity,
                completed_at, google_calendar_id, microsoft_todo_id,
                shared_with_users, owner_user_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_dict.get('session_id'),
            session_dict.get('title'),
            session_dict.get('description'),
            session_dict.get('priority'),
            session_dict.get('status'),
            session_dict.get('kanban_column'),
            session_dict.get('due_date'),
            session_dict.get('created_at'),
            session_dict.get('assignees'),
            session_dict.get('tags'),
            session_dict.get('documents'),
            session_dict.get('links'),
            session_dict.get('next_steps'),
            session_dict.get('checklist'),
            session_dict.get('google_task_id'),
            session_dict.get('project_name'),
            session_dict.get('notes'),
            session_dict.get('session_data'),
            session_dict.get('google_calendar_event_id'),
            session_dict.get('updated_at'),
            session_dict.get('updated_at'),  # Use updated_at for last_active
            '[]',  # platforms_involved - empty array
            '[]',  # thread_ids - empty array
            '[]',  # assigned_agents - empty array
            '[]',  # recent_activity - empty array
            None,  # completed_at
            None,  # google_calendar_id
            None,  # microsoft_todo_id
            '[]',  # shared_with_users - empty array (NEW)
            1      # owner_user_id - default to user 1 (NEW)
        ))
        
        migrated += 1
        print(f"   ✅ Migrated: {session_dict['title'][:60]}")
        
    except Exception as e:
        errors += 1
        print(f"   ❌ Error migrating row: {e}")

conn.commit()

print(f"\n   Migrated: {migrated}/{len(sessions_data)}")
print(f"   Errors: {errors}")

# Step 4: Verify migration
print("\n\n✅ STEP 4: Verifying migration")
print("-" * 120)

cursor.execute("SELECT COUNT(*) FROM synergy_sessions")
total_synergy = cursor.fetchone()[0]
print(f"Total rows in synergy_sessions: {total_synergy}")

# Step 5: Drop sessions table (OPTIONAL - commented out for safety)
print("\n\n🗑️  STEP 5: Dropping sessions table")
print("-" * 120)
print("   ⚠️  MANUAL STEP REQUIRED")
print("   After verifying data, run:")
print("   DROP TABLE sessions;")
print("\n   NOT executing automatically for safety")

conn.close()

print("\n" + "=" * 120)
print("CONSOLIDATION COMPLETE")
print("=" * 120)
print(f"""
✅ Added missing columns to synergy_sessions
✅ Migrated {migrated} rows from sessions → synergy_sessions
✅ Added new columns: shared_with_users, owner_user_id
⚠️  sessions table still exists (drop manually after verification)

NEXT STEPS:
1. Verify data in synergy_sessions
2. Update kanban_routes.py to use synergy_sessions instead of sessions
3. Drop sessions table manually: DROP TABLE sessions;
4. Update schema file
""")
