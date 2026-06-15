"""Check product options tables status"""
import psycopg2

DB_URL = 'postgresql://postgres.ryoicrdifiqhqpsnjmdo:inhouseprint@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres'

conn = psycopg2.connect(DB_URL)
cur = conn.cursor()

print("\n=== PRODUCT OPTIONS TABLES ===")
cur.execute("""
    SELECT table_name, 
           (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
    FROM information_schema.tables t
    WHERE table_schema = 'public' 
    AND table_name LIKE '%product%option%'
    ORDER BY table_name
""")
for row in cur.fetchall():
    print(f"  {row[0]}: {row[1]} columns")
    
    # Count rows
    cur.execute(f"SELECT COUNT(*) FROM {row[0]}")
    count = cur.fetchone()[0]
    print(f"    Rows: {count}")

print("\n=== INDEXES ===")
cur.execute("""
    SELECT indexname 
    FROM pg_indexes 
    WHERE schemaname = 'public' 
    AND indexname LIKE '%product%option%'
    ORDER BY indexname
""")
indexes = cur.fetchall()
print(f"Total: {len(indexes)}")
for idx in indexes[:10]:
    print(f"  - {idx[0]}")
if len(indexes) > 10:
    print(f"  ... and {len(indexes) - 10} more")

conn.close()
