"""
Direct Supabase query to check message order for thread 2112
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Add AI_infrastructure to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'AI_infrastructure'))

from shared.database_utils import execute_query

def check_message_order():
    """Query messages for thread 2112 in exact database order"""
    
    print("🔍 Querying Supabase database for thread 2112...\n")
    
    # Get messages ordered by created_at ASC (same as API)
    rows = execute_query("""
        SELECT 
            id,
            role,
            created_at,
            LEFT(content::text, 80) as content_preview
        FROM sessions.messages
        WHERE thread_id = 2112
        ORDER BY created_at ASC
    """, fetch_mode='all')
    
    print(f"📊 Found {len(rows)} messages in database\n")
    
    print("📝 Database order (by created_at ASC):")
    print("-" * 100)
    
    for i, row in enumerate(rows, 1):
        role = row['role'].upper()
        msg_id = row['id']
        timestamp = row['created_at']
        preview = row['content_preview']
        
        print(f"{i:3d}. [ID:{msg_id:4d}] {role:10s} | {timestamp} | {preview}...")
    
    # Count by role
    user_count = sum(1 for r in rows if r['role'] == 'user')
    assistant_count = sum(1 for r in rows if r['role'] == 'assistant')
    
    print("-" * 100)
    print(f"\n📊 Summary:")
    print(f"   Total: {len(rows)}")
    print(f"   User: {user_count}")
    print(f"   Assistant: {assistant_count}")
    
    # Check for role pattern
    print(f"\n🔍 Role sequence pattern (first 40):")
    pattern = ' '.join([r['role'][0].upper() for r in rows[:40]])
    print(f"   {pattern}")
    
    # Expected alternating pattern
    expected_pattern = ' '.join(['U', 'A'] * 20)
    if pattern.startswith(expected_pattern[:20]):
        print(f"   ✅ Follows alternating U-A pattern")
    else:
        print(f"   ⚠️ Does NOT follow alternating pattern")

if __name__ == '__main__':
    check_message_order()
