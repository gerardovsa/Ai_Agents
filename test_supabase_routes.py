"""
Test Supabase database connections for failing routes
"""

import sys
sys.path.insert(0, 'AI_infrastructure')
from shared.database_utils import get_database_connection, is_using_supabase, convert_sql_placeholders

print('='*80)
print('TESTING SUPABASE DATABASE CONNECTIONS')
print('='*80)
print()

print(f'🔍 Is using Supabase: {is_using_supabase()}')
print()

# Test 1: ai_infrastructure database (for /api/auth/profile)
print('-'*80)
print('TEST 1: ai_infrastructure schema - User Profile Query')
print('-'*80)
try:
    conn = get_database_connection('ai_infrastructure')
    cursor = conn.cursor()
    
    # Check if users table exists
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'ai_infrastructure' 
        AND table_name = 'users'
    """)
    result = cursor.fetchone()
    
    if result:
        print('✅ Users table exists in ai_infrastructure schema')
        
        # Test actual user query (simulating profile endpoint)
        cursor.execute("""
            SELECT user_id, email, username, created_at 
            FROM ai_infrastructure.users 
            WHERE user_id = %s
        """, (1,))
        user = cursor.fetchone()
        
        if user:
            print(f'✅ User query successful')
            print(f'   User ID: {user[0]}')
            print(f'   Email: {user[1]}')
            print(f'   Username: {user[2]}')
            print(f'   Created: {user[3]}')
        else:
            print('⚠️  No user found with ID = 1')
            
            # Check total user count
            cursor.execute("SELECT COUNT(*) FROM ai_infrastructure.users")
            count = cursor.fetchone()[0]
            print(f'   Total users in database: {count}')
    else:
        print('❌ Users table NOT found in ai_infrastructure schema')
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f'❌ Error testing ai_infrastructure: {e}')
    import traceback
    traceback.print_exc()

print()

# Test 2: sessions database (for /api/threads/details)
print('-'*80)
print('TEST 2: sessions schema - Thread Details Query')
print('-'*80)
try:
    conn = get_database_connection('sessions')
    cursor = conn.cursor()
    
    # Check if threads table exists
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'sessions' 
        AND table_name = 'threads'
    """)
    result = cursor.fetchone()
    
    if result:
        print('✅ Threads table exists in sessions schema')
        
        # Test thread count
        cursor.execute("SELECT COUNT(*) FROM sessions.threads")
        count = cursor.fetchone()[0]
        print(f'   Total threads: {count}')
        
        # Test actual thread query (simulating details endpoint)
        cursor.execute("""
            SELECT thread_slug, name, location, message_count, created_at 
            FROM sessions.threads 
            LIMIT 1
        """)
        thread = cursor.fetchone()
        
        if thread:
            print(f'✅ Thread query successful')
            print(f'   Thread slug: {thread[0]}')
            print(f'   Name: {thread[1]}')
            print(f'   Location: {thread[2]}')
            print(f'   Message count: {thread[3]}')
            print(f'   Created: {thread[4]}')
        else:
            print('⚠️  No threads found in database')
    else:
        print('❌ Threads table NOT found in sessions schema')
        
        # List available tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'sessions'
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        print(f'   Available tables in sessions schema: {[t[0] for t in tables]}')
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f'❌ Error testing sessions: {e}')
    import traceback
    traceback.print_exc()

print()

# Test 3: Check thread_details specific query
print('-'*80)
print('TEST 3: Thread Details Endpoint Simulation')
print('-'*80)
try:
    conn = get_database_connection('sessions')
    cursor = conn.cursor()
    
    # Simulate the exact query from thread_routes.py
    test_thread_ids = ['1762663889170', '1762789269210']
    placeholders = ','.join(['%s'] * len(test_thread_ids))
    
    query = f"""
        SELECT 
            thread_slug,
            name,
            location,
            message_count,
            created_at,
            last_message_timestamp
        FROM sessions.threads
        WHERE thread_slug IN ({placeholders})
    """
    
    print(f'Executing query with thread IDs: {test_thread_ids}')
    cursor.execute(query, test_thread_ids)
    threads = cursor.fetchall()
    
    print(f'✅ Query executed successfully')
    print(f'   Found {len(threads)} threads')
    
    for thread in threads:
        print(f'   - {thread[0]}: {thread[1]}')
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f'❌ Error testing thread details query: {e}')
    import traceback
    traceback.print_exc()

print()

# Test 4: Check OAuth tokens (for profile API)
print('-'*80)
print('TEST 4: OAuth Tokens Query (Profile API dependency)')
print('-'*80)
try:
    conn = get_database_connection('ai_infrastructure')
    cursor = conn.cursor()
    
    # Check if oauth_tokens table exists
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'ai_infrastructure' 
        AND table_name = 'oauth_tokens'
    """)
    result = cursor.fetchone()
    
    if result:
        print('✅ oauth_tokens table exists')
        
        # Test OAuth query for user
        cursor.execute("""
            SELECT platform, access_token, created_at 
            FROM ai_infrastructure.oauth_tokens 
            WHERE user_id = %s
            LIMIT 3
        """, (1,))
        tokens = cursor.fetchall()
        
        print(f'   Found {len(tokens)} OAuth tokens for user_id=1')
        for token in tokens:
            print(f'   - {token[0]}: {token[1][:20]}... (created: {token[2]})')
    else:
        print('❌ oauth_tokens table NOT found')
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f'❌ Error testing oauth_tokens: {e}')
    import traceback
    traceback.print_exc()

print()
print('='*80)
print('TEST SUMMARY')
print('='*80)
print('✅ = Working correctly')
print('⚠️  = Working but no data found')
print('❌ = Error/Not working')
print('='*80)
