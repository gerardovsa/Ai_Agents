"""
Quick check: What messages are in thread 2112 in the DATABASE?
"""
import os
import sys
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()

def check_thread_messages():
    """Query sessions.messages for thread_id = 2112"""
    
    # Import from existing infrastructure
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'AI_infrastructure'))
    from shared.database_utils import get_database_connection
    
    print("🔍 Connecting to database...")
    with get_database_connection('sessions') as conn:
        cursor = conn.cursor()
    
    # Get thread info
    cursor.execute("""
        SELECT id, thread_slug, name 
        FROM sessions.threads 
        WHERE id = 2112 OR thread_slug = '2112'
    """)
    thread = cursor.fetchone()
    
    if not thread:
        print("❌ Thread 2112 not found!")
        return
    
    print(f"✅ Found thread: {thread['name']} (ID: {thread['id']}, Slug: {thread['thread_slug']})")
    print()
    
    # Get message counts by role
    cursor.execute("""
        SELECT role, COUNT(*) as count
        FROM sessions.messages
        WHERE thread_id = %s
        GROUP BY role
        ORDER BY role
    """, (thread['id'],))
    
    role_counts = cursor.fetchall()
    print("📊 Message counts by role:")
    for row in role_counts:
        print(f"   {row['role']}: {row['count']} messages")
    print()
    
    # Get ALL messages
    cursor.execute("""
        SELECT id, role, content, created_at
        FROM sessions.messages
        WHERE thread_id = %s
        ORDER BY created_at ASC
    """, (thread['id'],))
    
    messages = cursor.fetchall()
    print(f"📝 All {len(messages)} messages:")
    print()
    
    for msg in messages:
        role_emoji = "👤" if msg['role'] == 'user' else "🤖"
        content_preview = str(msg['content'])[:100].replace('\n', ' ')
        print(f"{role_emoji} [{msg['id']}] {msg['role']:10s} | {content_preview}...")

if __name__ == '__main__':
    check_thread_messages()
