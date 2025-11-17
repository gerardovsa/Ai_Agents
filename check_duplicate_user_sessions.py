"""
Check Duplicate user_sessions Tables in Supabase

Identifies which schema has the actual session data and recommends consolidation
"""

import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv('.env.master')

def check_user_sessions_tables():
    """Check both user_sessions tables and compare data"""
    
    print("=" * 70)
    print("DUPLICATE USER_SESSIONS TABLE ANALYSIS")
    print("=" * 70)
    
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
    except ImportError:
        print("ERROR: psycopg2 not installed")
        print("Install: pip install psycopg2-binary")
        return 1
    
    db_url = os.getenv('SUPABASE_DB_URL')
    if not db_url:
        print("ERROR: SUPABASE_DB_URL not set in .env.master")
        return 1
    
    try:
        # Connect to Supabase
        print("\nConnecting to Supabase...")
        conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        
        # Check ai_infrastructure.user_sessions
        print("\n" + "=" * 70)
        print("TABLE 1: ai_infrastructure.user_sessions")
        print("=" * 70)
        
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM ai_infrastructure.user_sessions
        """)
        result = cursor.fetchone()
        ai_count = result['count']
        print(f"Total records: {ai_count}")
        
        if ai_count > 0:
            cursor.execute("""
                SELECT user_id, COUNT(*) as session_count
                FROM ai_infrastructure.user_sessions
                GROUP BY user_id
                ORDER BY session_count DESC
                LIMIT 10
            """)
            users = cursor.fetchall()
            print("\nTop users by session count:")
            for user in users:
                print(f"  User {user['user_id']}: {user['session_count']} sessions")
            
            # Check most recent session
            cursor.execute("""
                SELECT user_id, created_at, expires_at
                FROM ai_infrastructure.user_sessions
                ORDER BY created_at DESC
                LIMIT 1
            """)
            recent = cursor.fetchone()
            if recent:
                print(f"\nMost recent session:")
                print(f"  User ID: {recent['user_id']}")
                print(f"  Created: {recent['created_at']}")
                print(f"  Expires: {recent['expires_at']}")
        
        # Check sessions.user_sessions
        print("\n" + "=" * 70)
        print("TABLE 2: sessions.user_sessions")
        print("=" * 70)
        
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM sessions.user_sessions
        """)
        result = cursor.fetchone()
        sessions_count = result['count']
        print(f"Total records: {sessions_count}")
        
        if sessions_count > 0:
            cursor.execute("""
                SELECT user_id, COUNT(*) as session_count
                FROM sessions.user_sessions
                GROUP BY user_id
                ORDER BY session_count DESC
                LIMIT 10
            """)
            users = cursor.fetchall()
            print("\nTop users by session count:")
            for user in users:
                print(f"  User {user['user_id']}: {user['session_count']} sessions")
            
            # Check most recent session
            cursor.execute("""
                SELECT user_id, created_at, expires_at
                FROM sessions.user_sessions
                ORDER BY created_at DESC
                LIMIT 1
            """)
            recent = cursor.fetchone()
            if recent:
                print(f"\nMost recent session:")
                print(f"  User ID: {recent['user_id']}")
                print(f"  Created: {recent['created_at']}")
                print(f"  Expires: {recent['expires_at']}")
        
        # Analysis and Recommendation
        print("\n" + "=" * 70)
        print("ANALYSIS & RECOMMENDATION")
        print("=" * 70)
        
        if ai_count > 0 and sessions_count > 0:
            print("\nSTATUS: DUPLICATE DATA - Both tables have records!")
            print("\nRECOMMENDATION:")
            print("  1. Consolidate all sessions into ONE table")
            print("  2. Choose sessions.user_sessions (with other session tables)")
            print("  3. Migrate data from ai_infrastructure.user_sessions")
            print("  4. Update all queries to use sessions.user_sessions")
            print("  5. Drop ai_infrastructure.user_sessions")
        
        elif ai_count > 0:
            print(f"\nSTATUS: Data in ai_infrastructure.user_sessions ({ai_count} records)")
            print(f"        No data in sessions.user_sessions")
            print("\nRECOMMENDATION:")
            print("  1. COPY data from ai_infrastructure.user_sessions to sessions.user_sessions")
            print("  2. Update all queries to use sessions.user_sessions")
            print("  3. Drop ai_infrastructure.user_sessions")
        
        elif sessions_count > 0:
            print(f"\nSTATUS: Data in sessions.user_sessions ({sessions_count} records)")
            print(f"        No data in ai_infrastructure.user_sessions")
            print("\nRECOMMENDATION:")
            print("  1. ALL queries should use sessions.user_sessions")
            print("  2. ai_infrastructure.user_sessions is unused - can be dropped")
            print("  3. Update code to ONLY use sessions.user_sessions")
        
        else:
            print("\nSTATUS: BOTH TABLES EMPTY!")
            print("\nRECOMMENDATION:")
            print("  1. Use sessions.user_sessions (logically grouped with session tables)")
            print("  2. Drop ai_infrastructure.user_sessions")
            print("  3. Ensure all login/OAuth flows insert into sessions.user_sessions")
        
        # Check which files are using which table
        print("\n" + "=" * 70)
        print("CODE ANALYSIS NEEDED")
        print("=" * 70)
        print("\nRun these commands to find all references:")
        print("  grep -r 'ai_infrastructure.user_sessions' AI_infrastructure/")
        print("  grep -r 'sessions.user_sessions' AI_infrastructure/")
        print("  grep -r 'INSERT INTO user_sessions' AI_infrastructure/")
        
        cursor.close()
        conn.close()
        
        return 0
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(check_user_sessions_tables())
