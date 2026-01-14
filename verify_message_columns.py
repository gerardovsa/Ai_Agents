"""
Verify Message Columns - Check that all columns are being saved
Run this after sending a test message to verify the enhancement
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime

def get_db_connection():
    """Connect to Supabase PostgreSQL database"""
    return psycopg2.connect(
        host="aws-0-us-west-1.pooler.supabase.com",
        database="postgres",
        user="postgres.qyopsjqykrrdianjgtvi",
        password="Gpoli@1608",
        port=6543
    )

def verify_message_columns():
    """Check the latest messages and verify all columns are populated"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    print("\n" + "="*80)
    print("📊 MESSAGE COLUMNS VERIFICATION")
    print("="*80 + "\n")
    
    # Get latest 5 messages
    cursor.execute("""
        SELECT 
            id,
            thread_id,
            session_id,
            role,
            content,
            user_id,
            model,
            tokens_used,
            tool_calls,
            metadata,
            created_at
        FROM sessions.messages
        ORDER BY created_at DESC
        LIMIT 5
    """)
    
    messages = cursor.fetchall()
    
    if not messages:
        print("❌ No messages found in database!")
        print("   Send a test message first, then run this script.\n")
        conn.close()
        return
    
    print(f"✅ Found {len(messages)} recent messages\n")
    
    # Track which columns are populated
    column_stats = {
        'id': 0,
        'thread_id': 0,
        'session_id': 0,
        'role': 0,
        'content': 0,
        'user_id': 0,
        'model': 0,
        'tokens_used': 0,
        'tool_calls': 0,
        'metadata': 0,
        'created_at': 0
    }
    
    for i, msg in enumerate(messages, 1):
        print(f"{'─'*80}")
        print(f"MESSAGE #{i} (ID: {msg['id']})")
        print(f"{'─'*80}")
        
        # Check each column
        for col in column_stats.keys():
            value = msg[col]
            if value is not None:
                column_stats[col] += 1
                
                # Format value for display
                if col == 'content':
                    if isinstance(value, dict) or isinstance(value, list):
                        content_preview = json.dumps(value)[:100]
                        print(f"  ✅ {col:15} = {content_preview}...")
                    else:
                        print(f"  ✅ {col:15} = {str(value)[:100]}...")
                elif col == 'created_at':
                    print(f"  ✅ {col:15} = {value.strftime('%Y-%m-%d %H:%M:%S')}")
                elif col in ['tool_calls', 'metadata']:
                    if value:
                        try:
                            parsed = json.loads(value) if isinstance(value, str) else value
                            preview = json.dumps(parsed)[:80]
                            print(f"  ✅ {col:15} = {preview}...")
                        except:
                            print(f"  ✅ {col:15} = {str(value)[:80]}...")
                    else:
                        print(f"  ⚠️  {col:15} = (empty)")
                else:
                    print(f"  ✅ {col:15} = {value}")
            else:
                print(f"  ⚠️  {col:15} = NULL")
        
        print()
    
    # Print statistics
    print("="*80)
    print("📈 COLUMN POPULATION STATISTICS")
    print("="*80 + "\n")
    
    total_messages = len(messages)
    
    for col, count in column_stats.items():
        percentage = (count / total_messages) * 100
        status = "✅" if percentage == 100 else "⚠️" if percentage > 0 else "❌"
        bar_length = int(percentage / 5)  # 20 chars max
        bar = "█" * bar_length + "░" * (20 - bar_length)
        print(f"{status} {col:15} {bar} {count}/{total_messages} ({percentage:.0f}%)")
    
    print("\n" + "="*80)
    print("🎯 EXPECTED RESULTS")
    print("="*80 + "\n")
    print("✅ Should be 100%: id, thread_id, session_id, role, content, created_at")
    print("✅ Should be 100%: user_id (if authenticated)")
    print("✅ Should be 100%: model (for assistant messages)")
    print("⚠️  May be NULL: tokens_used (if API doesn't return usage)")
    print("⚠️  May be NULL: tool_calls (only for messages that use tools)")
    print("⚠️  May be NULL: metadata (only for assistant messages with extra data)")
    
    print("\n" + "="*80 + "\n")
    
    conn.close()

if __name__ == "__main__":
    try:
        verify_message_columns()
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
