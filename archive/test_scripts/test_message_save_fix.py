"""Test that messages now save correctly after fix"""
import requests
import json
import sqlite3

# Test data
test_thread_id = "1762664406832"  # Existing thread
test_user_id = 12

# Check current state
print("=" * 80)
print("BEFORE TEST - Current state:")
print("=" * 80)

conn = sqlite3.connect(r'C:\Users\gpoli\GIT\AI_agents\data\sessions.db')
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM messages")
message_count_before = cursor.fetchone()[0]
print(f"Messages in database: {message_count_before}")

conn.close()

# Test message save endpoint
print("\n" + "=" * 80)
print("TESTING MESSAGE SAVE:")
print("=" * 80)

url = "http://localhost:5001/api/threads/messages/save"
payload = {
    "thread_id": test_thread_id,
    "user_id": test_user_id,
    "messages": [
        {
            "role": "user",
            "content": "Test message 1 after workspace_id fix"
        },
        {
            "role": "assistant",
            "content": "Test response 1 after workspace_id fix"
        }
    ]
}

print(f"POST {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(url, json=payload)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    result = response.json()
    
    if result.get('success'):
        messages_saved = result.get('data', {}).get('messages_saved', 0)
        print(f"\n{'SUCCESS' if messages_saved > 0 else 'FAILED'}: {messages_saved} messages saved")
    else:
        print(f"\nFAILED: {result.get('message')}")
        
except Exception as e:
    print(f"\nERROR: {e}")

# Check after state
print("\n" + "=" * 80)
print("AFTER TEST - New state:")
print("=" * 80)

conn = sqlite3.connect(r'C:\Users\gpoli\GIT\AI_agents\data\sessions.db')
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM messages")
message_count_after = cursor.fetchone()[0]
print(f"Messages in database: {message_count_after}")
print(f"New messages added: {message_count_after - message_count_before}")

if message_count_after > message_count_before:
    print("\n" + "=" * 80)
    print("SUCCESS! Messages are now being saved correctly!")
    print("=" * 80)
    
    # Show last few messages
    cursor.execute("""
        SELECT id, thread_id, role, content, created_at
        FROM messages
        ORDER BY id DESC
        LIMIT 5
    """)
    
    print("\nLast 5 messages:")
    for row in cursor.fetchall():
        print(f"  ID: {row[0]}, Thread: {row[1]}, Role: {row[2]}")
        print(f"     Content: {row[3][:60]}...")
        print(f"     Created: {row[4]}")
else:
    print("\n" + "=" * 80)
    print("STILL FAILING! Messages not being saved.")
    print("=" * 80)

conn.close()
