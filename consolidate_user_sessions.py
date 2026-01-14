"""
Consolidate user_sessions tables into ai_infrastructure schema

Current situation:
- sessions.user_sessions (used by current code)
- ai_infrastructure.user_sessions (exists but deprecated)

Goal:
- Single table: ai_infrastructure.user_sessions
- Update all code to use ai_infrastructure.user_sessions
- Drop sessions.user_sessions after migration
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'AI_infrastructure'))

# Load environment
from dotenv import load_dotenv
env_file = project_root / '.env.master'
if env_file.exists():
    load_dotenv(env_file)
    print(f"✅ Loaded environment from {env_file}")

from AI_infrastructure.shared.database_utils import get_database_connection

def consolidate_sessions():
    """Migrate all sessions to ai_infrastructure schema"""
    print("\n" + "="*70)
    print("USER SESSIONS CONSOLIDATION")
    print("="*70)
    
    conn = get_database_connection('ai_infrastructure')
    cursor = conn.cursor()
    
    # 1. Check current state
    print("\n📊 STEP 1: Current State Analysis")
    print("-" * 70)
    
    cursor.execute("SELECT COUNT(*) as count FROM sessions.user_sessions")
    sessions_count = cursor.fetchone()
    sessions_total = sessions_count['count'] if isinstance(sessions_count, dict) else sessions_count[0]
    print(f"   sessions.user_sessions: {sessions_total} records")
    
    cursor.execute("SELECT COUNT(*) as count FROM ai_infrastructure.user_sessions")
    ai_count = cursor.fetchone()
    ai_total = ai_count['count'] if isinstance(ai_count, dict) else ai_count[0]
    print(f"   ai_infrastructure.user_sessions: {ai_total} records")
    
    # 2. Check for orphaned sessions (user_id doesn't exist in users table)
    print("\n📊 STEP 2: Data Quality Check")
    print("-" * 70)
    
    cursor.execute("""
        SELECT DISTINCT s.user_id
        FROM sessions.user_sessions s
        LEFT JOIN ai_infrastructure.users u ON s.user_id = u.id
        WHERE u.id IS NULL
    """)
    
    orphaned_users = cursor.fetchall()
    if orphaned_users:
        orphaned_ids = [row['user_id'] if isinstance(row, dict) else row[0] for row in orphaned_users]
        print(f"   ⚠️  Found {len(orphaned_ids)} orphaned user_ids: {orphaned_ids}")
        print(f"   These sessions will be DELETED (users don't exist)")
    else:
        print(f"   ✅ All sessions have valid user_ids")
    
    # 3. Recreate ai_infrastructure.user_sessions with proper schema
    print("\n📊 STEP 3: Recreate ai_infrastructure.user_sessions table")
    print("-" * 70)
    
    print("   Dropping old ai_infrastructure.user_sessions...")
    cursor.execute("DROP TABLE IF EXISTS ai_infrastructure.user_sessions CASCADE")
    
    print("   Creating new ai_infrastructure.user_sessions with SERIAL id...")
    cursor.execute("""
        CREATE TABLE ai_infrastructure.user_sessions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES ai_infrastructure.users(id) ON DELETE CASCADE,
            token TEXT NOT NULL UNIQUE,
            session_token TEXT,
            ip_address TEXT,
            user_agent TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES ai_infrastructure.users(id) ON DELETE CASCADE
        )
    """)
    
    print("   ✅ Table created with SERIAL id and foreign key constraint")
    
    # 4. Copy valid sessions from sessions.user_sessions
    print("\n📊 STEP 4: Copy Valid Sessions")
    print("-" * 70)
    
    cursor.execute("""
        INSERT INTO ai_infrastructure.user_sessions 
            (user_id, token, session_token, ip_address, user_agent, created_at, expires_at, last_activity)
        SELECT 
            s.user_id,
            s.token,
            s.session_token,
            s.ip_address,
            s.user_agent,
            COALESCE(s.created_at, CURRENT_TIMESTAMP),
            s.expires_at,
            COALESCE(s.last_activity, CURRENT_TIMESTAMP)
        FROM sessions.user_sessions s
        INNER JOIN ai_infrastructure.users u ON s.user_id = u.id
        WHERE s.expires_at > CURRENT_TIMESTAMP
        ORDER BY s.created_at
    """)
    
    conn.commit()
    
    cursor.execute("SELECT COUNT(*) as count FROM ai_infrastructure.user_sessions")
    result = cursor.fetchone()
    migrated_count = result['count'] if isinstance(result, dict) else result[0]
    
    print(f"   ✅ Copied {migrated_count} valid, non-expired sessions")
    print(f"   ❌ Skipped {sessions_total - migrated_count} expired/orphaned sessions")
    
    # 5. Verify data integrity
    print("\n📊 STEP 5: Verify Data Integrity")
    print("-" * 70)
    
    cursor.execute("""
        SELECT 
            u.id,
            u.email,
            COUNT(s.id) as session_count
        FROM ai_infrastructure.users u
        LEFT JOIN ai_infrastructure.user_sessions s ON u.id = s.user_id
        GROUP BY u.id, u.email
        HAVING COUNT(s.id) > 0
        ORDER BY u.id
    """)
    
    user_sessions = cursor.fetchall()
    print(f"   Users with active sessions: {len(user_sessions)}")
    for row in user_sessions:
        user_id = row['id'] if isinstance(row, dict) else row[0]
        email = row['email'] if isinstance(row, dict) else row[1]
        count = row['session_count'] if isinstance(row, dict) else row[2]
        print(f"   - User {user_id} ({email}): {count} session(s)")
    
    conn.close()
    
    print("\n" + "="*70)
    print("MIGRATION COMPLETE")
    print("="*70)
    print("\n✅ Next Steps:")
    print("   1. Update all Python code to use 'ai_infrastructure.user_sessions'")
    print("   2. Test authentication flows (Google OAuth, Microsoft OAuth)")
    print("   3. If everything works, drop sessions.user_sessions:")
    print("      DROP TABLE sessions.user_sessions CASCADE;")
    print("\n" + "="*70)

if __name__ == '__main__':
    try:
        consolidate_sessions()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
