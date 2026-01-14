import psycopg2

conn = psycopg2.connect('postgresql://postgres.ryoicrdifiqhqpsnjmdo:inhouseprint@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres')
cur = conn.cursor()

print("🔍 Testing thread slug lookup with JOIN\n")

# Test the exact query the API uses
thread_slug = "1765854881504"

print(f"1️⃣ Testing: WHERE t.thread_slug = '{thread_slug}'")
cur.execute("""
    SELECT COUNT(m.id) as total
    FROM sessions.messages m
    JOIN sessions.threads t ON m.thread_id = t.id
    WHERE t.thread_slug = %s
""", (thread_slug,))
count = cur.fetchone()[0]
print(f"   Result: {count} messages\n")

print(f"2️⃣ Getting thread ID first:")
cur.execute("SELECT id, thread_slug FROM sessions.threads WHERE thread_slug = %s", (thread_slug,))
thread = cur.fetchone()
if thread:
    print(f"   Thread: id={thread[0]}, slug={thread[1]}")
    
    print(f"\n3️⃣ Testing: WHERE m.thread_id = {thread[0]}")
    cur.execute("SELECT COUNT(*) FROM sessions.messages WHERE thread_id = %s", (thread[0],))
    count = cur.fetchone()[0]
    print(f"   Result: {count} messages\n")
else:
    print("   ❌ Thread not found!")

cur.close()
conn.close()
