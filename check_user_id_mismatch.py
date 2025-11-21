"""
Check user_id mismatches across schemas

Compares:
- ai_infrastructure.users (authoritative)
- sessions.user_sessions
- ai_infrastructure.user_sessions (if exists)
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
    print(f"Loaded environment from {env_file}")

# Import database utilities
from AI_infrastructure.shared.database_utils import get_database_connection

def check_user_ids():
    """Check user_id values across all tables"""
    print("\n" + "="*70)
    print("USER ID MISMATCH ANALYSIS")
    print("="*70)
    
    conn = get_database_connection('ai_infrastructure')
    cursor = conn.cursor()
    
    # 1. Check ai_infrastructure.users (authoritative source)
    print("\n1. AUTHORITATIVE TABLE: ai_infrastructure.users")
    print("-" * 70)
    cursor.execute("""
        SELECT id, username, email, password_hash
        FROM ai_infrastructure.users
        ORDER BY id
        LIMIT 20
    """)
    
    users = cursor.fetchall()
    print(f"   Total users: {len(users)}")
    print(f"\n   User ID | Username | Email | Auth Type")
    print("   " + "-" * 66)
    
    user_map = {}
    for user in users:
        user_id = user['id'] if isinstance(user, dict) else user[0]
        username = user['username'] if isinstance(user, dict) else user[1]
        email = user['email'] if isinstance(user, dict) else user[2]
        password_hash = user['password_hash'] if isinstance(user, dict) else user[3]
        
        auth_type = 'local'
        if password_hash == 'oauth_google':
            auth_type = 'google'
        elif password_hash in ('oauth_microsoft', 'OAUTH_USER_NO_PASSWORD'):
            auth_type = 'microsoft'
        
        user_map[user_id] = {'email': email, 'username': username, 'auth': auth_type}
        print(f"   {user_id:7} | {username:15} | {email:25} | {auth_type}")
    
    # 2. Check sessions.user_sessions
    print("\n2. SESSION TABLE: sessions.user_sessions")
    print("-" * 70)
    try:
        cursor.execute("""
            SELECT user_id, COUNT(*) as session_count, MAX(created_at) as last_session
            FROM sessions.user_sessions
            GROUP BY user_id
            ORDER BY user_id
        """)
        
        session_users = cursor.fetchall()
        print(f"   Total unique users with sessions: {len(session_users)}")
        print(f"\n   User ID | Sessions | Last Session | Exists in users?")
        print("   " + "-" * 66)
        
        mismatched_users = []
        for row in session_users:
            user_id = row['user_id'] if isinstance(row, dict) else row[0]
            count = row['session_count'] if isinstance(row, dict) else row[1]
            last_session = row['last_session'] if isinstance(row, dict) else row[2]
            
            exists_in_users = user_id in user_map
            status = "YES" if exists_in_users else "NO (MISMATCH)"
            
            if not exists_in_users:
                mismatched_users.append(user_id)
            
            print(f"   {user_id:7} | {count:8} | {str(last_session)[:19]:19} | {status}")
        
        if mismatched_users:
            print(f"\n   CRITICAL: {len(mismatched_users)} user_ids in sessions.user_sessions")
            print(f"            do NOT exist in ai_infrastructure.users")
            print(f"   Mismatched IDs: {mismatched_users}")
    except Exception as e:
        print(f"   ERROR reading sessions.user_sessions: {e}")
    
    # 3. Check ai_infrastructure.user_sessions (old table)
    print("\n3. OLD TABLE: ai_infrastructure.user_sessions")
    print("-" * 70)
    try:
        cursor.execute("""
            SELECT user_id, COUNT(*) as session_count
            FROM ai_infrastructure.user_sessions
            GROUP BY user_id
            ORDER BY user_id
        """)
        
        old_session_users = cursor.fetchall()
        if old_session_users:
            print(f"   Total unique users with sessions: {len(old_session_users)}")
            print(f"   WARNING: This table should be deprecated")
            print(f"\n   User ID | Sessions | Exists in users?")
            print("   " + "-" * 50)
            
            for row in old_session_users:
                user_id = row['user_id'] if isinstance(row, dict) else row[0]
                count = row['session_count'] if isinstance(row, dict) else row[1]
                
                exists_in_users = user_id in user_map
                status = "YES" if exists_in_users else "NO (MISMATCH)"
                print(f"   {user_id:7} | {count:8} | {status}")
        else:
            print("   (empty table)")
    except Exception as e:
        print(f"   Table does not exist or error: {e}")
    
    # 4. Check for sequence issues
    print("\n4. SEQUENCE ANALYSIS")
    print("-" * 70)
    cursor.execute("SELECT MAX(id) as max_id FROM ai_infrastructure.users")
    result = cursor.fetchone()
    max_user_id = result['max_id'] if isinstance(result, dict) else result[0]
    print(f"   Max user_id in ai_infrastructure.users: {max_user_id}")
    
    try:
        cursor.execute("SELECT MAX(user_id) as max_id FROM sessions.user_sessions")
        result = cursor.fetchone()
        max_session_user_id = result['max_id'] if isinstance(result, dict) else result[0]
        print(f"   Max user_id in sessions.user_sessions: {max_session_user_id}")
        
        if max_session_user_id > max_user_id:
            print(f"\n   CRITICAL: sessions.user_sessions has user_ids ({max_session_user_id})")
            print(f"            HIGHER than max user in users table ({max_user_id})")
            print(f"            This indicates a sequence mismatch!")
    except Exception as e:
        print(f"   Error checking sessions.user_sessions: {e}")
    
    conn.close()
    
    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)

if __name__ == '__main__':
    check_user_ids()
