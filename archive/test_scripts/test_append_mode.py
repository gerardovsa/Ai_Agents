"""Test append-only message saving (no deletion)"""
import requests
import json
import sqlite3
from shared.database_utils import convert_sql_placeholders

test_thread_id = "1762664406832"
test_user_id = 12
url = "http://localhost:5001/api/threads/messages/save"

def check_messages():
    """Check current message count in database"""
    conn = sqlite3.connect(r'C:\Users\gpoli\GIT\AI_agents\data\sessions.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM messages WHERE thread_id = 3")
    count = cursor.fetchone()[0]
    cursor.execute("SELECT id, role, content FROM messages WHERE thread_id = 3 ORDER BY id")
    messages = cursor.fetchall()
    conn.close()
    return count, messages

print("=" * 80)
print("TEST: APPEND-ONLY MESSAGE SAVING")
print("=" * 80)

# Step 1: Start with fresh thread (clear manually for test)
print("\n[STEP 1] Clearing thread for test...")
conn = sqlite3.connect(r'C:\Users\gpoli\GIT\AI_agents\data\sessions.db')
cursor = conn.cursor()
cursor.execute("DELETE FROM messages WHERE thread_id = 3")
conn.commit()
conn.close()

count, msgs = check_messages()
print(f"Starting message count: {count}")

# Step 2: Save initial conversation (user message + AI response)
print("\n[STEP 2] Saving initial conversation (2 messages)...")
payload = {
    "thread_id": test_thread_id,
    "user_id": test_user_id,
    "messages": [
        {"role": "user", "content": "Hello, how are you?"},
        {"role": "assistant", "content": "I'm doing well, thank you!"}
    ]
}

response = requests.post(url, json=payload)
result = response.json()
print(f"API Response: messages_saved = {result['data']['messages_saved']}")

count, msgs = check_messages()
print(f"Database message count: {count}")
for msg in msgs:
    print(f"  - ID {msg[0]}: {msg[1]} - {msg[2][:40]}...")

# Step 3: Continue conversation (send ENTIRE history + new messages)
print("\n[STEP 3] Continuing conversation (sending 4 messages total, including previous 2)...")
payload = {
    "thread_id": test_thread_id,
    "user_id": test_user_id,
    "messages": [
        {"role": "user", "content": "Hello, how are you?"},  # Already exists
        {"role": "assistant", "content": "I'm doing well, thank you!"},  # Already exists
        {"role": "user", "content": "What's the weather like?"},  # NEW
        {"role": "assistant", "content": "It's sunny today!"}  # NEW
    ]
}

response = requests.post(url, json=payload)
result = response.json()
print(f"API Response: messages_saved = {result['data']['messages_saved']} (should be 2, not 4)")

count, msgs = check_messages()
print(f"Database message count: {count} (should be 4, not 8)")
for msg in msgs:
    print(f"  - ID {msg[0]}: {msg[1]} - {msg[2][:40]}...")

# Step 4: Continue again (send full history + 1 more)
print("\n[STEP 4] Continuing again (sending 5 messages total)...")
payload = {
    "thread_id": test_thread_id,
    "user_id": test_user_id,
    "messages": [
        {"role": "user", "content": "Hello, how are you?"},
        {"role": "assistant", "content": "I'm doing well, thank you!"},
        {"role": "user", "content": "What's the weather like?"},
        {"role": "assistant", "content": "It's sunny today!"},
        {"role": "user", "content": "Great, thanks!"}  # NEW
    ]
}

response = requests.post(url, json=payload)
result = response.json()
print(f"API Response: messages_saved = {result['data']['messages_saved']} (should be 1)")

count, msgs = check_messages()
print(f"Database message count: {count} (should be 5)")
for msg in msgs:
    print(f"  - ID {msg[0]}: {msg[1]} - {msg[2][:40]}...")

print("\n" + "=" * 80)
if count == 5:
    print("SUCCESS! Append mode working correctly - no duplicates!")
else:
    print(f"FAILED! Expected 5 messages, got {count}")
print("=" * 80)
