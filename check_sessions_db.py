"""
Check sessions database for thread and message data
"""
import sys
sys.path.insert(0, r'c:\Users\gpoli\GIT\AI_agents\AI_infrastructure')

from shared.database_utils import get_database_connection

def check_sessions_database():
    """Check sessions database schema and recent data"""
    
    conn = None
    cursor = None
    
    try:
        print("\n" + "="*80)
        print("SESSIONS DATABASE DIAGNOSTIC")
        print("="*80)
        
        conn = get_database_connection('sessions')
        cursor = conn.cursor()
        
        # Check if sessions schema exists
        print("\n1. Checking schemas...")
        cursor.execute("""
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name = 'sessions'
        """)
        schema_result = cursor.fetchone()
        
        if schema_result:
            print("   ✅ 'sessions' schema EXISTS")
        else:
            print("   ❌ 'sessions' schema DOES NOT EXIST!")
            print("   This is likely why the agent stream is failing!")
            return
        
        # Check tables in sessions schema
        print("\n2. Checking tables in 'sessions' schema...")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'sessions'
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        
        if tables:
            print(f"   Found {len(tables)} tables:")
            for t in tables:
                table_name = t[0] if isinstance(t, tuple) else t['table_name']
                print(f"     - {table_name}")
        else:
            print("   ❌ NO tables found in 'sessions' schema!")
            return
        
        # Check threads table
        print("\n3. Checking 'threads' table...")
        try:
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM sessions.threads
            """)
            count_result = cursor.fetchone()
            thread_count = count_result[0] if isinstance(count_result, tuple) else count_result['count']
            print(f"   ✅ threads table exists with {thread_count} threads")
            
            # Show recent threads
            if thread_count > 0:
                cursor.execute("""
                    SELECT thread_slug, name, created_at
                    FROM sessions.threads
                    ORDER BY created_at DESC
                    LIMIT 5
                """)
                recent_threads = cursor.fetchall()
                print(f"\n   Recent threads:")
                for t in recent_threads:
                    if isinstance(t, tuple):
                        slug, name, created = t
                    else:
                        slug = t['thread_slug']
                        name = t['name']
                        created = t['created_at']
                    print(f"     - {slug}: {name} ({created})")
        except Exception as e:
            print(f"   ❌ Error accessing threads table: {e}")
        
        # Check messages table
        print("\n4. Checking 'messages' table...")
        try:
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM sessions.messages
            """)
            count_result = cursor.fetchone()
            message_count = count_result[0] if isinstance(count_result, tuple) else count_result['count']
            print(f"   ✅ messages table exists with {message_count} messages")
            
            # Show recent messages
            if message_count > 0:
                cursor.execute("""
                    SELECT m.session_id, m.role, 
                           LEFT(CAST(m.content AS TEXT), 50) as content_preview,
                           m.created_at
                    FROM sessions.messages m
                    ORDER BY m.created_at DESC
                    LIMIT 5
                """)
                recent_messages = cursor.fetchall()
                print(f"\n   Recent messages:")
                for m in recent_messages:
                    if isinstance(m, tuple):
                        sess_id, role, content, created = m
                    else:
                        sess_id = m['session_id']
                        role = m['role']
                        content = m['content_preview']
                        created = m['created_at']
                    print(f"     - {sess_id} [{role}]: {content}... ({created})")
        except Exception as e:
            print(f"   ❌ Error accessing messages table: {e}")
        
        # Check specific thread from error
        print("\n5. Checking specific thread: 1765301658174...")
        try:
            cursor.execute("""
                SELECT id, thread_slug, name, created_at
                FROM sessions.threads
                WHERE thread_slug = %s
            """, ('1765301658174',))
            thread_result = cursor.fetchone()
            
            if thread_result:
                if isinstance(thread_result, tuple):
                    thread_id, slug, name, created = thread_result
                else:
                    thread_id = thread_result['id']
                    slug = thread_result['thread_slug']
                    name = thread_result['name']
                    created = thread_result['created_at']
                
                print(f"   ✅ Thread EXISTS:")
                print(f"      ID: {thread_id}")
                print(f"      Slug: {slug}")
                print(f"      Name: {name}")
                print(f"      Created: {created}")
                
                # Check messages for this thread
                cursor.execute("""
                    SELECT COUNT(*) as count
                    FROM sessions.messages
                    WHERE session_id = %s OR thread_id = %s
                """, (slug, thread_id))
                msg_count_result = cursor.fetchone()
                msg_count = msg_count_result[0] if isinstance(msg_count_result, tuple) else msg_count_result['count']
                
                print(f"      Messages: {msg_count}")
                
                if msg_count > 0:
                    cursor.execute("""
                        SELECT role, LEFT(CAST(content AS TEXT), 100) as content_preview, created_at
                        FROM sessions.messages
                        WHERE session_id = %s OR thread_id = %s
                        ORDER BY created_at ASC
                    """, (slug, thread_id))
                    messages = cursor.fetchall()
                    print(f"\n      Messages in thread:")
                    for m in messages:
                        if isinstance(m, tuple):
                            role, content, created = m
                        else:
                            role = m['role']
                            content = m['content_preview']
                            created = m['created_at']
                        print(f"        [{role}] {content}... ({created})")
            else:
                print(f"   ❌ Thread 1765301658174 DOES NOT EXIST in database!")
                print(f"   This means start_agent() did NOT successfully create/save the thread!")
        except Exception as e:
            print(f"   ❌ Error checking specific thread: {e}")
        
        print("\n" + "="*80)
        print("DIAGNOSTIC COMPLETE")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if conn:
            try:
                conn.close()
            except:
                pass

if __name__ == '__main__':
    check_sessions_database()
