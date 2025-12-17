import psycopg2
import json

conn = psycopg2.connect('postgresql://postgres.ryoicrdifiqhqpsnjmdo:inhouseprint@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres')
cur = conn.cursor()

print("🔍 Searching for thread 1765854881504 in ALL possible formats...\n")

# Check if thread exists as string ID
cur.execute("SELECT id, user_id, name, location FROM sessions.threads WHERE CAST(id AS TEXT) = '1765854881504'")
row = cur.fetchone()
if row:
    print(f"✅ Found as string: ID={row[0]}, user={row[1]}, name={row[2]}, location={row[3]}")
else:
    print("❌ Not found as string ID")

# Check if thread exists as bigint
try:
    cur.execute("SELECT id, user_id, name, location FROM sessions.threads WHERE id = 1765854881504")
    row = cur.fetchone()
    if row:
        print(f"✅ Found as bigint: ID={row[0]}, user={row[1]}, name={row[2]}, location={row[3]}")
    else:
        print("❌ Not found as bigint ID")
except Exception as e:
    print(f"❌ Error checking bigint: {e}")

# Check thread_slug
cur.execute("SELECT id, user_id, name, location, thread_slug FROM sessions.threads WHERE thread_slug LIKE '%1765854881504%'")
row = cur.fetchone()
if row:
    print(f"✅ Found by slug: ID={row[0]}, user={row[1]}, name={row[2]}, location={row[3]}, slug={row[4]}")
else:
    print("❌ Not found by thread_slug")

# Check all threads for user 14 with recent activity
print("\n📋 All threads for user_id=14 (showing ID format):\n")
cur.execute("""
    SELECT t.id, t.thread_slug, t.name, t.location, t.created_at,
           (SELECT COUNT(*) FROM sessions.messages m WHERE m.thread_id = t.id) as msg_count
    FROM sessions.threads t 
    WHERE t.user_id = 14
    ORDER BY t.created_at DESC
    LIMIT 20
""")

threads = cur.fetchall()
for t in threads:
    print(f"  ID: {t[0]:20} | Slug: {t[1]:20} | Location: {t[3]:15} | Msgs: {t[5]:3} | {t[2]}")

# Check if there's a thread with that ID in metadata or anywhere
print("\n🔎 Searching metadata for thread reference...")
cur.execute("""
    SELECT id, name, location, metadata::text 
    FROM sessions.threads 
    WHERE metadata::text LIKE '%1765854881504%'
    LIMIT 5
""")
rows = cur.fetchall()
if rows:
    for r in rows:
        print(f"  Found in metadata: ID={r[0]}, name={r[1]}")
else:
    print("  Not found in metadata")

cur.close()
conn.close()
