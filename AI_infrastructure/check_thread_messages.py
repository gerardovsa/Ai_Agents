import psycopg2

conn = psycopg2.connect('postgresql://postgres.ryoicrdifiqhqpsnjmdo:inhouseprint@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres')
cur = conn.cursor()

# Check threads for user 14
print("📋 Checking threads for user_id=14...")
cur.execute("""
    SELECT t.id, t.name, t.location, COUNT(m.id) as msg_count 
    FROM sessions.threads t 
    LEFT JOIN sessions.messages m ON m.thread_id = t.id 
    WHERE t.user_id = 14
    GROUP BY t.id, t.name, t.location
    ORDER BY t.created_at DESC
    LIMIT 10
""")

threads = cur.fetchall()
print(f"\n✅ Found {len(threads)} threads for user 14:\n")
for t in threads:
    print(f"  ID {t[0]:15} | {t[2]:15} | {t[3]:3} msgs | {t[1]}")

# Check the specific thread
print(f"\n🔍 Checking thread 1765854881504...")
cur.execute("SELECT * FROM sessions.threads WHERE id = 1765854881504")
row = cur.fetchone()
if row:
    print("✅ Thread exists but has different user_id!")
else:
    print("❌ Thread 1765854881504 does NOT exist in database")

cur.close()
conn.close()
