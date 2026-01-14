import sqlite3

conn = sqlite3.connect('data/sessions.db')
cur = conn.cursor()

# Total messages
cur.execute('SELECT COUNT(*) FROM messages')
total = cur.fetchone()[0]
print(f'Total messages in database: {total}')

# Messages per thread
cur.execute('SELECT thread_id, COUNT(*) as count FROM messages GROUP BY thread_id ORDER BY count DESC LIMIT 10')
rows = cur.fetchall()
print(f'\nThreads with messages:')
for row in rows:
    print(f'  Thread ID {row[0]}: {row[1]} messages')

# Check if any thread has messages
if total == 0:
    print('\n❌ NO MESSAGES IN DATABASE! This is why threads show 0 messages.')
else:
    print(f'\n✅ Database has {total} messages')

conn.close()
