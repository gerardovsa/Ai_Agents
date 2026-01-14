"""Test ThreadManager.add_message() directly"""
import sys
sys.path.insert(0, 'AI_infrastructure')

from thread_manager import ThreadManager

print("=" * 80)
print("TESTING ThreadManager.add_message() DIRECTLY")
print("=" * 80)

thread_mgr = ThreadManager()

# Test adding a message
try:
    print("\n1. Attempting to add message...")
    result = thread_mgr.add_message(
        workspace_slug='default',
        thread_slug='1762664406832',
        role='user',
        content='Direct test message',
        user_id=12,
        prompt='Direct test message',
        include=True,
        tool_calls=None,
        tokens_used=10,
        response_time_ms=100,
        metadata={}
    )
    print(f"   SUCCESS! Result: {result}")
    
    print("\n2. Checking database...")
    import sqlite3
    conn = sqlite3.connect(r'C:\Users\gpoli\GIT\AI_agents\data\sessions.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM messages")
    count = cursor.fetchone()[0]
    print(f"   Messages in database: {count}")
    
    if count > 0:
        cursor.execute("SELECT id, role, content FROM messages ORDER BY id DESC LIMIT 1")
        last_msg = cursor.fetchone()
        print(f"   Last message: ID={last_msg[0]}, role={last_msg[1]}, content={last_msg[2][:50]}...")
    
    conn.close()
    
except Exception as e:
    print(f"\n   ERROR: {e}")
    import traceback
    traceback.print_exc()
