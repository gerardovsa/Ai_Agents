"""
Check most recent messages for Team ID data
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'AI_infrastructure'))

from shared.database_utils import get_database_connection

def check_recent_messages():
    """Check the very latest messages"""
    print("\n🔍 Checking MOST RECENT 20 messages for Team ID data...")
    
    conn = get_database_connection('sessions')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            m.id,
            m.role,
            m.sender_team_id,
            m.recipient_team_id,
            m.message_type,
            m.created_at,
            t.thread_slug
        FROM sessions.messages m
        LEFT JOIN sessions.threads t ON m.thread_id = t.id
        ORDER BY m.created_at DESC
        LIMIT 20;
    """)
    
    messages = cursor.fetchall()
    
    print(f"\nFound {len(messages)} recent messages:\n")
    
    has_team_id_data = False
    
    for msg in messages:
        msg_id = msg[0] if isinstance(msg, tuple) else msg['id']
        role = msg[1] if isinstance(msg, tuple) else msg['role']
        sender = msg[2] if isinstance(msg, tuple) else msg['sender_team_id']
        recipient = msg[3] if isinstance(msg, tuple) else msg['recipient_team_id']
        msg_type = msg[4] if isinstance(msg, tuple) else msg['message_type']
        created = msg[5] if isinstance(msg, tuple) else msg['created_at']
        thread_slug = msg[6] if isinstance(msg, tuple) else msg['thread_slug']
        
        if sender or (recipient and recipient != 'null'):
            has_team_id_data = True
            print(f"✅ ID:{msg_id} | Role:{role} | Sender:{sender or 'NULL'} | Recipient:{recipient or 'NULL'} | Type:{msg_type}")
            print(f"   Thread: {thread_slug} | Created: {created}")
        else:
            print(f"⚠️  ID:{msg_id} | Role:{role} | NO TEAM ID DATA")
            print(f"   Thread: {thread_slug} | Created: {created}")
    
    cursor.close()
    conn.close()
    
    print("\n" + "="*80)
    if has_team_id_data:
        print("✅ SUCCESS: Team ID routing is working! Found messages with Team ID data.")
    else:
        print("❌ ISSUE: No Team ID data found in recent messages.")
        print("\nPossible causes:")
        print("   1. Frontend not sending sender_team_id in request")
        print("   2. Backend not extracting from request.json")
        print("   3. save_message_to_database() not receiving parameters")
        print("\nCheck Flask logs for:")
        print("   [DB SAVE] Team ID: sender=... → recipient=...")

if __name__ == "__main__":
    check_recent_messages()
