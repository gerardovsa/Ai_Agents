"""
Test Supabase database connections for failing API endpoints

Tests:
1. /api/threads/details - Thread details for Synergy canvas
2. /api/auth/profile - User profile with OAuth status

This script connects directly to Supabase to verify:
- Database schema exists
- Tables are accessible
- Queries return data
- Column names match expectations
"""

import sys
import os

# Add AI_infrastructure to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'AI_infrastructure'))

from shared.database_utils import get_database_connection, is_using_supabase, convert_sql_placeholders


def test_connection_info():
    """Display connection configuration"""
    print("=" * 80)
    print("SUPABASE CONNECTION TEST")
    print("=" * 80)
    
    using_supabase = is_using_supabase()
    print(f"\nUsing Supabase: {using_supabase}")
    
    if using_supabase:
        supabase_url = os.getenv('SUPABASE_DB_URL')
        if supabase_url:
            # Mask password for security
            import re
            masked_url = re.sub(r':[^:@]+@', ':****@', supabase_url)
            print(f"Supabase URL: {masked_url}")
        else:
            print("⚠️  SUPABASE_DB_URL not set!")
    else:
        print("Using SQLite (local development)")
    
    print()


def test_threads_table():
    """Test threads table access"""
    print("-" * 80)
    print("TEST 1: Threads Table Access")
    print("-" * 80)
    
    try:
        conn = get_database_connection('sessions')
        print("✅ Connected to sessions database")
        
        cursor = conn.cursor()
        
        # Test 1: Check if threads table exists
        if is_using_supabase():
            query = "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'sessions' AND table_name = 'threads')"
        else:
            query = "SELECT name FROM sqlite_master WHERE type='table' AND name='threads'"
        
        cursor.execute(query)
        result = cursor.fetchone()
        print(f"Threads table exists: {bool(result)}")
        
        # Test 2: Get column names
        if is_using_supabase():
            query = """
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_schema = 'sessions' AND table_name = 'threads'
                ORDER BY ordinal_position
            """
            cursor.execute(query)
            columns = cursor.fetchall()
            print(f"\nThreads table columns ({len(columns)}):")
            for col in columns:
                print(f"  - {col['column_name']}: {col['data_type']}")
        else:
            query = "PRAGMA table_info(threads)"
            cursor.execute(query)
            columns = cursor.fetchall()
            print(f"\nThreads table columns ({len(columns)}):")
            for col in columns:
                print(f"  - {col[1]}: {col[2]}")  # name: type
        
        # Test 3: Count threads
        query = convert_sql_placeholders("SELECT COUNT(*) as count FROM threads")
        cursor.execute(query)
        result = cursor.fetchone()
        count = result['count'] if isinstance(result, dict) else result[0]
        print(f"\nTotal threads: {count}")
        
        # Test 4: Get sample thread with all columns
        if count > 0:
            query = convert_sql_placeholders("""
                SELECT 
                    id, thread_slug, name, location, 
                    created_at, updated_at, synergy_card_id
                FROM threads 
                ORDER BY updated_at DESC 
                LIMIT 1
            """)
            cursor.execute(query)
            thread = cursor.fetchone()
            
            print("\nSample thread:")
            print(f"  ID: {thread['id']}")
            print(f"  Slug: {thread['thread_slug']}")
            print(f"  Name: {thread['name']}")
            print(f"  Location: {thread['location']}")
            print(f"  Synergy Card ID: {thread['synergy_card_id']}")
            print(f"  Updated: {thread['updated_at']}")
        
        # Test 5: Test the actual query used by /api/threads/details
        print("\n" + "-" * 40)
        print("Testing /api/threads/details query:")
        print("-" * 40)
        
        test_thread_ids = ['1762851232975']  # From your error logs
        placeholders = ', '.join(['?' for _ in test_thread_ids])
        
        # FIXED: Only match against thread_slug (TEXT), not id (INTEGER)
        query = f"""
            SELECT 
                t.id,
                t.thread_slug,
                t.name,
                t.created_at,
                t.updated_at,
                t.synergy_card_id,
                t.location
            FROM threads t
            WHERE t.thread_slug IN ({placeholders})
            ORDER BY t.updated_at DESC
        """
        
        query = convert_sql_placeholders(query)
        params = test_thread_ids
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        print(f"Query returned {len(results)} threads")
        for thread in results:
            print(f"  - {thread['name']} (ID: {thread['id']}, Location: {thread['location']})")
        
        cursor.close()
        conn.close()
        print("\n✅ Threads table test PASSED")
        
    except Exception as e:
        print(f"\n❌ Threads table test FAILED: {e}")
        import traceback
        traceback.print_exc()


def test_users_table():
    """Test users table and OAuth tokens access"""
    print("\n" + "-" * 80)
    print("TEST 2: Users Table and OAuth Tokens")
    print("-" * 80)
    
    try:
        conn = get_database_connection('ai_infrastructure')
        print("✅ Connected to ai_infrastructure database")
        
        cursor = conn.cursor()
        
        # Test 1: Check users table
        query = convert_sql_placeholders("SELECT COUNT(*) as count FROM users")
        cursor.execute(query)
        result = cursor.fetchone()
        count = result['count'] if isinstance(result, dict) else result[0]
        print(f"\nTotal users: {count}")
        
        # Test 2: Get sample user
        if count > 0:
            query = convert_sql_placeholders("""
                SELECT id, email, username, password_hash, created_at
                FROM users 
                ORDER BY id ASC 
                LIMIT 1
            """)
            cursor.execute(query)
            user = cursor.fetchone()
            
            print("\nSample user:")
            print(f"  ID: {user['id']}")
            print(f"  Email: {user['email']}")
            print(f"  Username: {user['username']}")
            print(f"  Auth Type: {user['password_hash'][:20]}..." if user['password_hash'] else "None")
            
            user_id = user['id']
            
            # Test 3: Check OAuth tokens for this user
            print(f"\n" + "-" * 40)
            print(f"Checking OAuth tokens for user {user_id}:")
            print("-" * 40)
            
            bool_true = True if is_using_supabase() else 1
            now_sql = "NOW()" if is_using_supabase() else "datetime('now')"
            
            # Google OAuth
            query = convert_sql_placeholders(f"""
                SELECT COUNT(*) as count 
                FROM oauth_tokens 
                WHERE user_id = ? 
                AND platform = 'google' 
                AND access_token IS NOT NULL
                AND (is_active = ? OR is_active IS NULL)
                AND (expires_at IS NULL OR expires_at > {now_sql})
            """)
            cursor.execute(query, (user_id, bool_true))
            result = cursor.fetchone()
            google_count = result['count'] if isinstance(result, dict) else result[0]
            print(f"  Google OAuth tokens: {google_count}")
            
            # Microsoft OAuth
            query = convert_sql_placeholders(f"""
                SELECT COUNT(*) as count 
                FROM oauth_tokens 
                WHERE user_id = ? 
                AND (platform = 'microsoft' OR platform = 'microsoft365')
                AND access_token IS NOT NULL
                AND (is_active = ? OR is_active IS NULL)
                AND (expires_at IS NULL OR expires_at > {now_sql})
            """)
            cursor.execute(query, (user_id, bool_true))
            result = cursor.fetchone()
            microsoft_count = result['count'] if isinstance(result, dict) else result[0]
            print(f"  Microsoft OAuth tokens: {microsoft_count}")
            
            # Test 4: Test the actual query used by /api/auth/profile
            print("\n" + "-" * 40)
            print("Testing /api/auth/profile query:")
            print("-" * 40)
            
            query = convert_sql_placeholders('SELECT password_hash FROM users WHERE id = ?')
            cursor.execute(query, (user_id,))
            user_row = cursor.fetchone()
            
            if user_row:
                password_hash = user_row['password_hash']
                print(f"  Password hash: {password_hash[:50] if password_hash else 'None'}...")
                
                auth_platform = None
                if password_hash == 'oauth_google':
                    auth_platform = 'google'
                elif password_hash in ('oauth_microsoft', 'OAUTH_USER_NO_PASSWORD'):
                    auth_platform = 'microsoft'
                
                print(f"  Detected auth platform: {auth_platform}")
        
        cursor.close()
        conn.close()
        print("\n✅ Users table test PASSED")
        
    except Exception as e:
        print(f"\n❌ Users table test FAILED: {e}")
        import traceback
        traceback.print_exc()


def test_synergy_sessions():
    """Test synergy_sessions database access"""
    print("\n" + "-" * 80)
    print("TEST 3: Synergy Sessions Database")
    print("-" * 80)
    
    try:
        conn = get_database_connection('synergy_sessions')
        print("✅ Connected to synergy_sessions database")
        
        cursor = conn.cursor()
        
        # Test 1: Check synergy_sessions table
        query = convert_sql_placeholders("SELECT COUNT(*) as count FROM synergy_sessions")
        cursor.execute(query)
        result = cursor.fetchone()
        count = result['count'] if isinstance(result, dict) else result[0]
        print(f"\nTotal synergy sessions: {count}")
        
        # Test 2: Check synergy_internal_docs table
        query = convert_sql_placeholders("SELECT COUNT(*) as count FROM synergy_internal_docs")
        cursor.execute(query)
        result = cursor.fetchone()
        count = result['count'] if isinstance(result, dict) else result[0]
        print(f"Total internal docs: {count}")
        
        cursor.close()
        conn.close()
        print("\n✅ Synergy sessions test PASSED")
        
    except Exception as e:
        print(f"\n❌ Synergy sessions test FAILED: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Run all tests"""
    test_connection_info()
    test_threads_table()
    test_users_table()
    test_synergy_sessions()
    
    print("\n" + "=" * 80)
    print("ALL TESTS COMPLETE")
    print("=" * 80)


if __name__ == '__main__':
    main()
