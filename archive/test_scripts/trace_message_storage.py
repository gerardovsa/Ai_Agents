"""
Trace where messages are stored and identify why they're not persisting
"""
import sqlite3
from pathlib import Path
from shared.database_utils import convert_sql_placeholders

print("\n" + "="*80)
print("MESSAGE STORAGE DIAGNOSTIC")
print("="*80)

# Check 1: Messages table schema
print("\n1. CHECKING MESSAGES TABLE SCHEMA:")
print("-" * 80)

db_path = Path('data/sessions.db')
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(messages)")
columns = cursor.fetchall()

print("\nMessages table structure:")
for col in columns:
    print(f"  {col['name']:<20} {col['type']:<15} {'NOT NULL' if col['notnull'] else 'NULL OK':<10} {'PK' if col['pk'] else ''}")

# Check 2: Count messages
cursor.execute("SELECT COUNT(*) as count FROM messages")
msg_count = cursor.fetchone()['count']
print(f"\n❌ Total messages in database: {msg_count}")

if msg_count == 0:
    print("\n⚠️  NO MESSAGES STORED! This explains why threads show 0 messages.")

# Check 3: AppState in localStorage (where messages might be stored instead)
print("\n" + "="*80)
print("2. WHERE MESSAGES MIGHT BE STORED:")
print("-" * 80)

print("""
Possible storage locations:

❌ data/sessions.db → messages table (EMPTY - 0 rows)
   Location: C:\\Users\\gpoli\\GIT\\AI_agents\\data\\sessions.db
   
🤔 Browser localStorage → ai_chat_threads
   Location: Browser's localStorage (check DevTools)
   Key: 'ai_chat_threads'
   Note: This is CLIENT-SIDE ONLY, not persistent across devices
   
🤔 Browser memory → AppState.chatMessages
   Location: JavaScript runtime memory (lost on refresh)
   Note: Temporary storage while chatting
   
🤔 data/saved_threads table (legacy)
   Location: C:\\Users\\gpoli\\GIT\\AI_agents\\data\\sessions.db
   Note: Old format, might have conversation data
""")

# Check 4: Check saved_threads table (legacy)
cursor.execute("SELECT COUNT(*) as count FROM saved_threads")
saved_count = cursor.fetchone()['count']
print(f"\nChecking legacy saved_threads table: {saved_count} rows")

if saved_count > 0:
    cursor.execute("SELECT thread_id, thread_name, message_count, conversation FROM saved_threads LIMIT 1")
    row = cursor.fetchone()
    print(f"\n  Sample thread: {row['thread_name']}")
    print(f"  Message count: {row['message_count']}")
    conv = row['conversation']
    if conv:
        print(f"  Conversation data: {len(conv)} characters")
        print(f"  Format: JSON string with messages")
    else:
        print(f"  Conversation data: NULL")

# Check 5: Trace the save flow
print("\n" + "="*80)
print("3. MESSAGE SAVE FLOW:")
print("-" * 80)

print("""
EXPECTED FLOW (what SHOULD happen):

1. User sends message → Frontend adds to AppState.chatMessages[]
   Location: business-ai-platform-v2.html (AppState object)
   
2. AI responds → Message added to AppState.chatMessages[]
   Location: Anthropic API call in streamCompletion()
   
3. Thread updated → ThreadManager.updateCurrentThread(messages)
   Location: business-ai-platform-v2.html line ~15682
   Code: ThreadManager.updateCurrentThread(AppState.chatMessages)
   
4. Save triggered → ThreadManager.saveMessagesToBackend(thread)
   Location: business-ai-platform-v2.html line ~16170
   Code: this.saveMessagesToBackend(thread)
   
5. API call → POST /api/threads/messages/save
   Location: Frontend fetch() call
   Endpoint: http://localhost:5001/api/threads/messages/save
   
6. Backend saves → ThreadManager.add_message()
   Location: AI_infrastructure/routes/thread_routes.py line ~1165
   Code: thread_mgr.add_message(...)
   
7. Database insert → INSERT INTO messages (...)
   Location: thread_manager.py add_message() method
   Result: Should create row in messages table

ACTUAL FLOW (what IS happening):

Steps 1-5: ✅ Likely working (messages show in UI during session)
Step 6-7: ❌ FAILING (no messages in database)

POSSIBLE FAILURES:
- Backend /api/threads/messages/save endpoint not being called
- Backend receiving data but thread_id lookup failing
- ThreadManager.add_message() throwing exception
- Database transaction not committing
- Wrong thread_id format (slug vs internal ID mismatch)
""")

# Check 6: Test thread_id lookup
print("\n" + "="*80)
print("4. TESTING THREAD_ID LOOKUP:")
print("-" * 80)

cursor.execute("SELECT id, thread_slug FROM threads")
threads = cursor.fetchall()

print(f"\nThreads in database: {len(threads)}")
for thread in threads:
    print(f"\n  Thread slug: {thread['thread_slug']} (external ID)")
    print(f"  Internal ID: {thread['id']} (for messages FK)")
    
    # Check if lookup would work
    sql, params = convert_sql_placeholders("SELECT id FROM threads WHERE thread_slug = ?", (thread['thread_slug'],))

    cursor.execute(sql, params)
    result = cursor.fetchone()
    if result:
        print(f"  ✅ Lookup works: thread_slug → id = {result['id']}")
    else:
        print(f"  ❌ Lookup FAILED!")

conn.close()

# Check 7: Recommendations
print("\n" + "="*80)
print("5. DIAGNOSTIC RECOMMENDATIONS:")
print("-" * 80)

print("""
TO DIAGNOSE THE ISSUE:

1. ✅ Check Browser Console Logs:
   - Open DevTools (F12)
   - Look for: [MESSAGE SAVE] logs
   - Look for: API Response logs
   - Look for: Error messages

2. ✅ Check Flask Backend Logs:
   - Look for: POST /api/threads/messages/save
   - Look for: [MESSAGE SAVE] backend logs
   - Look for: Exception tracebacks

3. ✅ Test API Endpoint Manually:
   
   Run this in PowerShell:
   
   $body = @{
       thread_id = "1762664406832"
       user_id = 12
       messages = @(
           @{role="user"; content="Test message"; timestamp=1699999999}
       )
   } | ConvertTo-Json -Depth 10
   
   Invoke-RestMethod -Uri "http://localhost:5001/api/threads/messages/save" `
       -Method POST `
       -ContentType "application/json" `
       -Body $body

4. ✅ Check thread_manager.py:
   - Verify add_message() method exists
   - Check if it's correctly inserting into messages table
   - Look for exception handling that might be swallowing errors

5. ✅ Enable verbose logging:
   - Add print statements in thread_routes.py save_messages()
   - Add print statements in thread_manager.py add_message()
   - Check if messages reach the database layer

NEXT STEPS:
1. Send a test message in the UI
2. Check browser console for [MESSAGE SAVE] logs
3. Check Flask logs for incoming POST request
4. Run manual API test (above PowerShell command)
5. If API works, issue is in frontend; if not, issue is in backend
""")

print("\n" + "="*80)
print("DIAGNOSTIC COMPLETE")
print("="*80 + "\n")
