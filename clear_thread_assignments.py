"""
Clear all thread assignments from Supabase database
Resets the metadata column in users table
"""

import psycopg2
import os

def clear_thread_assignments(user_id=1):
    """Clear all thread assignments for a user"""
    
    # Supabase connection string
    connection_string = os.getenv('SUPABASE_DB_URL') or \
        "postgresql://postgres.xnpbpowppyugjvhnmnfk:Tswizzle132$@aws-0-us-east-1.pooler.supabase.com:6543/postgres"
    
    print(f'🔗 Connecting to Supabase PostgreSQL...')
    conn = psycopg2.connect(connection_string)
    conn.autocommit = True
    cursor = conn.cursor()
    
    try:
        # Get current metadata
        cursor.execute("""
            SELECT metadata FROM ai_infrastructure.users WHERE id = %s
        """, [user_id])
        
        row = cursor.fetchone()
        
        if not row:
            print(f'❌ User {user_id} not found')
            return
        
        current_metadata = row[0] or {}
        print(f'📊 Current metadata: {current_metadata}')
        
        # Clear thread_assignments key
        if 'thread_assignments' in current_metadata:
            old_assignments = current_metadata['thread_assignments']
            print(f'🧹 Clearing {len(old_assignments)} thread assignments...')
            current_metadata['thread_assignments'] = {}
        else:
            print('ℹ️  No thread assignments found')
            return
        
        # Update database
        cursor.execute("""
            UPDATE ai_infrastructure.users 
            SET metadata = %s::jsonb
            WHERE id = %s
        """, [psycopg2.extras.Json(current_metadata), user_id])
        
        print(f'✅ Thread assignments cleared for user {user_id}')
        print('🔄 Refresh browser to see changes')
        
    except Exception as e:
        print(f'❌ Error: {e}')
        raise
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    import sys
    user_id = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    print(f'\n🧹 CLEARING THREAD ASSIGNMENTS FOR USER {user_id}\n')
    clear_thread_assignments(user_id)
    print('\n✅ DONE!\n')
