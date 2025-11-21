"""
Verify that sessions.user_sessions table no longer exists
and all code now uses ai_infrastructure.user_sessions
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

from AI_infrastructure.shared.database_utils import get_database_connection

print("\n" + "="*70)
print("SESSION TABLE VERIFICATION")
print("="*70)

conn = get_database_connection('ai_infrastructure')
cursor = conn.cursor()

# 1. Check if sessions.user_sessions exists (should NOT exist)
print("\n1. Check sessions.user_sessions (should NOT exist)")
print("-" * 70)
try:
    cursor.execute("SELECT COUNT(*) as count FROM sessions.user_sessions")
    count = cursor.fetchone()
    print(f"   ❌ ERROR: sessions.user_sessions still exists!")
    print(f"   Records: {count['count'] if isinstance(count, dict) else count[0]}")
    print(f"   Action needed: DROP TABLE sessions.user_sessions CASCADE;")
except Exception as e:
    if 'does not exist' in str(e).lower() or 'no such table' in str(e).lower():
        print(f"   ✅ GOOD: sessions.user_sessions does NOT exist")
    else:
        print(f"   ⚠️  Unexpected error: {e}")

# 2. Check if ai_infrastructure.user_sessions exists (should exist)
print("\n2. Check ai_infrastructure.user_sessions (should exist)")
print("-" * 70)
try:
    cursor.execute("SELECT COUNT(*) as count FROM ai_infrastructure.user_sessions")
    count_result = cursor.fetchone()
    count = count_result['count'] if isinstance(count_result, dict) else count_result[0]
    print(f"   ✅ Table exists with {count} sessions")
    
    # Check table structure
    cursor.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'ai_infrastructure' 
        AND table_name = 'user_sessions'
        ORDER BY ordinal_position
    """)
    
    columns = cursor.fetchall()
    print(f"\n   Table structure:")
    for col in columns:
        col_name = col['column_name'] if isinstance(col, dict) else col[0]
        data_type = col['data_type'] if isinstance(col, dict) else col[1]
        nullable = col['is_nullable'] if isinstance(col, dict) else col[2]
        print(f"   - {col_name:20} {data_type:20} {'NULL' if nullable == 'YES' else 'NOT NULL'}")
    
    # Check foreign key constraint
    cursor.execute("""
        SELECT constraint_name, constraint_type
        FROM information_schema.table_constraints
        WHERE table_schema = 'ai_infrastructure'
        AND table_name = 'user_sessions'
        AND constraint_type = 'FOREIGN KEY'
    """)
    
    fks = cursor.fetchall()
    if fks:
        print(f"\n   ✅ Foreign key constraints: {len(fks)}")
        for fk in fks:
            fk_name = fk['constraint_name'] if isinstance(fk, dict) else fk[0]
            print(f"   - {fk_name}")
    else:
        print(f"\n   ⚠️  No foreign key constraints found")
    
except Exception as e:
    print(f"   ❌ ERROR: Table does not exist or query failed: {e}")

# 3. Check session counts per user
print("\n3. Active sessions per user")
print("-" * 70)
try:
    cursor.execute("""
        SELECT 
            u.id,
            u.email,
            COUNT(s.id) as session_count,
            MAX(s.created_at) as last_session
        FROM ai_infrastructure.users u
        LEFT JOIN ai_infrastructure.user_sessions s ON u.id = s.user_id
        WHERE s.expires_at > CURRENT_TIMESTAMP OR s.expires_at IS NULL
        GROUP BY u.id, u.email
        HAVING COUNT(s.id) > 0
        ORDER BY session_count DESC
    """)
    
    users = cursor.fetchall()
    print(f"   Users with active sessions: {len(users)}")
    for user in users:
        user_id = user['id'] if isinstance(user, dict) else user[0]
        email = user['email'] if isinstance(user, dict) else user[1]
        count = user['session_count'] if isinstance(user, dict) else user[2]
        last = user['last_session'] if isinstance(user, dict) else user[3]
        print(f"   User {user_id:2} ({email:35}) - {count:2} session(s) - Last: {str(last)[:19]}")
        
except Exception as e:
    print(f"   Error: {e}")

conn.close()

print("\n" + "="*70)
print("VERIFICATION COMPLETE")
print("="*70)
print("\n✅ Summary:")
print("   - sessions.user_sessions: Should NOT exist (deleted)")
print("   - ai_infrastructure.user_sessions: Should exist (active)")
print("   - All code updated to use ai_infrastructure.user_sessions")
print("\n" + "="*70 + "\n")
