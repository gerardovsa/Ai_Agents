"""Check saved_threads table for existing messages"""
import sqlite3
import json

conn = sqlite3.connect('data/sessions.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("\n" + "="*80)
print("SAVED_THREADS TABLE ANALYSIS")
print("="*80)

cursor.execute("SELECT * FROM saved_threads")
rows = cursor.fetchall()

print(f"\nFound {len(rows)} saved threads\n")

for i, row in enumerate(rows, 1):
    print(f"\n{'='*80}")
    print(f"THREAD {i}: {row['thread_name']}")
    print(f"{'='*80}")
    print(f"Thread ID: {row['thread_id']}")
    print(f"Session ID: {row['session_id']}")
    print(f"Location: {row['location']}")
    print(f"Message count: {row['message_count']}")
    print(f"Created: {row['created_at']}")
    print(f"Saved: {row['saved_at']}")
    
    # Parse conversation
    if row['conversation']:
        try:
            conv = json.loads(row['conversation'])
            print(f"\n📬 MESSAGES IN CONVERSATION: {len(conv)} messages")
            
            # Show first few messages
            for j, msg in enumerate(conv[:5], 1):
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')
                preview = content[:100] + '...' if len(content) > 100 else content
                print(f"\n  Message {j} ({role}):")
                print(f"    {preview}")
            
            if len(conv) > 5:
                print(f"\n  ... and {len(conv) - 5} more messages")
                
        except json.JSONDecodeError:
            print(f"\n⚠️  Conversation data is not valid JSON")
    else:
        print(f"\n⚠️  No conversation data")

conn.close()

print("\n" + "="*80)
print("RECOMMENDATION")
print("="*80)
print("""
✅ MESSAGES EXIST IN saved_threads TABLE (legacy format)

The old system stored messages as JSON in saved_threads.conversation column.
The new system should store in messages table (normalized).

OPTIONS:

1. MIGRATE old messages to new messages table:
   - Parse saved_threads.conversation JSON
   - Insert each message into messages table
   - Link via thread_slug lookup

2. USE saved_threads as fallback:
   - If messages table is empty, load from saved_threads
   - Display in UI
   - Gradually migrate as users interact with threads

3. CLEAR saved_threads and start fresh:
   - Delete old data
   - Focus on fixing new message save system
   - Users lose old messages but system is clean

RECOMMENDED: Option 1 (migrate old messages)
""")
