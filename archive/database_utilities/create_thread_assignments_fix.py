"""
Create and populate thread_assignments table to fix the missing table warnings
from shared.database_utils import convert_sql_placeholders

This script:
1. Creates thread_assignments table in ai_infrastructure.db
2. Populates it from existing data sources:
   - sessions.db/saved_threads.agent_id
   - sessions.db/users.metadata['thread_assignments']
3. Verifies data integrity
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

def main():
    print("="*80)
    print("THREAD ASSIGNMENTS TABLE - FIX MISSING TABLE")
    print("="*80)
    
    # Database paths
    root_dir = Path(__file__).parent
    ai_db_path = root_dir / 'data' / 'ai_infrastructure.db'
    sessions_db_path = root_dir / 'data' / 'sessions.db'
    
    print(f"\nAI DB: {ai_db_path}")
    print(f"Sessions DB: {sessions_db_path}")
    
    # Step 1: Check if table exists
    print("\n" + "="*80)
    print("STEP 1: Check if thread_assignments table exists")
    print("="*80)
    
    ai_conn = sqlite3.connect(str(ai_db_path))
    ai_cursor = ai_conn.cursor()
    
    ai_cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='thread_assignments'
    """)
    
    exists = ai_cursor.fetchone()
    
    if exists:
        print("✅ Table EXISTS")
        ai_cursor.execute("SELECT COUNT(*) FROM thread_assignments")
        count = ai_cursor.fetchone()[0]
        print(f"   Current rows: {count}")
        
        response = input("\n⚠️  Table exists. Drop and recreate? (yes/no): ")
        if response.lower() != 'yes':
            print("❌ Aborted by user")
            ai_conn.close()
            return
        
        print("\n🗑️  Dropping existing table...")
        ai_cursor.execute("DROP TABLE thread_assignments")
        ai_conn.commit()
        print("✅ Table dropped")
    else:
        print("❌ Table DOES NOT EXIST - will create")
    
    # Step 2: Create table
    print("\n" + "="*80)
    print("STEP 2: Create thread_assignments table")
    print("="*80)
    
    create_sql = """
    CREATE TABLE IF NOT EXISTS thread_assignments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        agent_id TEXT NOT NULL,
        session_id TEXT NOT NULL,
        location TEXT NOT NULL,
        assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'active',
        source TEXT DEFAULT 'migration',
        FOREIGN KEY (user_id) REFERENCES users(id),
        UNIQUE(user_id, agent_id, session_id)
    );
    """
    
    print("Creating table...")
    ai_cursor.execute(create_sql)
    ai_conn.commit()
    print("✅ Table created successfully")
    
    # Create index for performance
    print("\nCreating indexes...")
    ai_cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_thread_assignments_user 
        ON thread_assignments(user_id)
    """)
    ai_cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_thread_assignments_session 
        ON thread_assignments(session_id)
    """)
    ai_cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_thread_assignments_agent 
        ON thread_assignments(agent_id)
    """)
    ai_conn.commit()
    print("✅ Indexes created")
    
    # Step 3: Populate from saved_threads
    print("\n" + "="*80)
    print("STEP 3: Populate from sessions.db/saved_threads")
    print("="*80)
    
    sessions_conn = sqlite3.connect(str(sessions_db_path))
    sessions_cursor = sessions_conn.cursor()
    
    sessions_cursor.execute("""
        SELECT thread_id, agent_id, user_id, created_at
        FROM saved_threads
        WHERE agent_id IS NOT NULL
        ORDER BY created_at
    """)
    
    saved_threads_data = sessions_cursor.fetchall()
    print(f"Found {len(saved_threads_data)} saved threads with agent_id")
    
    inserted_from_saved = 0
    for thread_id, agent_id, user_id, created_at in saved_threads_data:
        try:
            ai_cursor.execute("""
                INSERT INTO thread_assignments 
                (user_id, agent_id, session_id, location, assigned_at, source)
                VALUES (?, ?, ?, ?, ?, 'saved_threads')
            """, (user_id, agent_id, thread_id, agent_id, created_at or datetime.now()))
            inserted_from_saved += 1
        except sqlite3.IntegrityError:
            # Duplicate - skip
            pass
    
    ai_conn.commit()
    print(f"✅ Inserted {inserted_from_saved} assignments from saved_threads")
    
    # Step 4: Populate from users.metadata
    print("\n" + "="*80)
    print("STEP 4: Populate from sessions.db/users.metadata")
    print("="*80)
    
    sessions_cursor.execute("""
        SELECT id, username, metadata
        FROM users
        WHERE metadata IS NOT NULL
    """)
    
    users_data = sessions_cursor.fetchall()
    print(f"Found {len(users_data)} users with metadata")
    
    inserted_from_metadata = 0
    for user_id, username, metadata_json in users_data:
        if not metadata_json:
            continue
        
        try:
            metadata = json.loads(metadata_json)
            assignments = metadata.get('thread_assignments', {})
            
            if assignments:
                print(f"\n  User {user_id} ({username}): {len(assignments)} assignments")
                for agent_id, thread_id in assignments.items():
                    try:
                        ai_cursor.execute("""
                            INSERT INTO thread_assignments 
                            (user_id, agent_id, session_id, location, source)
                            VALUES (?, ?, ?, ?, 'user_metadata')
                        """, (user_id, agent_id, thread_id, agent_id))
                        inserted_from_metadata += 1
                        print(f"    ✅ {agent_id} -> {thread_id}")
                    except sqlite3.IntegrityError:
                        print(f"    ⚠️  {agent_id} -> {thread_id} (duplicate)")
        except json.JSONDecodeError:
            print(f"  ⚠️  User {user_id}: Invalid JSON in metadata")
    
    ai_conn.commit()
    print(f"\n✅ Inserted {inserted_from_metadata} new assignments from user metadata")
    
    # Step 5: Verify data
    print("\n" + "="*80)
    print("STEP 5: Verify populated data")
    print("="*80)
    
    ai_cursor.execute("SELECT COUNT(*) FROM thread_assignments")
    total = ai_cursor.fetchone()[0]
    print(f"\n📊 TOTAL ASSIGNMENTS: {total}")
    
    ai_cursor.execute("""
        SELECT agent_id, COUNT(*) as count
        FROM thread_assignments
        GROUP BY agent_id
        ORDER BY count DESC
    """)
    
    print("\n📈 Assignments by agent:")
    for agent_id, count in ai_cursor.fetchall():
        print(f"  {agent_id}: {count} threads")
    
    ai_cursor.execute("""
        SELECT user_id, COUNT(*) as count
        FROM thread_assignments
        GROUP BY user_id
        ORDER BY count DESC
    """)
    
    print("\n👥 Assignments by user:")
    for user_id, count in ai_cursor.fetchall():
        print(f"  User {user_id}: {count} assignments")
    
    ai_cursor.execute("""
        SELECT source, COUNT(*) as count
        FROM thread_assignments
        GROUP BY source
    """)
    
    print("\n📦 Assignments by source:")
    for source, count in ai_cursor.fetchall():
        print(f"  {source}: {count} assignments")
    
    # Step 6: Sample data
    print("\n" + "="*80)
    print("STEP 6: Sample data (first 10 rows)")
    print("="*80)
    
    ai_cursor.execute("""
        SELECT id, user_id, agent_id, session_id, assigned_at, source
        FROM thread_assignments
        ORDER BY id
        LIMIT 10
    """)
    
    print("\nID | User | Agent      | Session         | Assigned At         | Source")
    print("-"*80)
    for row in ai_cursor.fetchall():
        print(f"{row[0]:2d} | {row[1]:4d} | {row[2]:10s} | {row[3]:15s} | {row[4]:19s} | {row[5]}")
    
    # Cleanup
    sessions_conn.close()
    ai_conn.close()
    
    # Final summary
    print("\n" + "="*80)
    print("✅ FIX COMPLETE")
    print("="*80)
    print(f"""
Summary:
- ✅ Created thread_assignments table in ai_infrastructure.db
- ✅ Created 3 indexes for performance
- ✅ Inserted {inserted_from_saved} assignments from saved_threads
- ✅ Inserted {inserted_from_metadata} assignments from user metadata
- 📊 Total assignments: {total}

Next Steps:
1. Restart Flask server (BISTART)
2. Check logs for thread_assignments warnings (should be gone)
3. Test thread loading in UI
4. Monitor for any issues

The warning "[THREADS] Warning: Could not fetch agent assignments: 
no such table: thread_assignments" should now be RESOLVED.
    """)

if __name__ == '__main__':
    main()
