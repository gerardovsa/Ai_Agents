import sqlite3

conn = sqlite3.connect('data/sessions.db')
cursor = conn.cursor()

print("=== THREAD vs MESSAGE STRUCTURE ANALYSIS ===\n")

# Check threads
cursor.execute('SELECT COUNT(*) FROM threads WHERE user_id = 14')
thread_count = cursor.fetchone()[0]
print(f"Total threads for user 14: {thread_count}")

# Check messages
cursor.execute('SELECT COUNT(*) FROM messages')
message_count = cursor.fetchone()[0]
print(f"Total messages in database: {message_count}")

# Check unique session IDs in messages
cursor.execute('SELECT COUNT(DISTINCT session_id) FROM messages WHERE session_id IS NOT NULL')
unique_sessions = cursor.fetchone()[0]
print(f"Unique message session_ids: {unique_sessions}")

# Sample thread IDs
print("\n=== SAMPLE THREAD IDs (from threads table) ===")
cursor.execute('SELECT thread_slug, name FROM threads WHERE user_id = 14 ORDER BY created_at DESC LIMIT 5')
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]}")

# Sample message session_ids
print("\n=== SAMPLE MESSAGE session_ids (from messages table) ===")
cursor.execute('SELECT DISTINCT session_id FROM messages WHERE session_id IS NOT NULL LIMIT 5')
for row in cursor.fetchall():
    print(f"  {row[0]}")

# Check if any thread_slugs match message session_ids
print("\n=== CHECKING FOR MATCHES ===")
cursor.execute('''
    SELECT t.thread_slug, t.name, COUNT(m.id) as msg_count
    FROM threads t
    LEFT JOIN messages m ON t.thread_slug = m.session_id
    WHERE t.user_id = 14
    GROUP BY t.thread_slug, t.name
    ORDER BY t.created_at DESC
    LIMIT 10
''')
print("Thread → Message matches:")
for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]} → {row[2]} messages")

# Check messages table structure
print("\n=== MESSAGES TABLE STRUCTURE ===")
cursor.execute("PRAGMA table_info(messages)")
for col in cursor.fetchall():
    print(f"  {col[1]} ({col[2]})")

conn.close()
