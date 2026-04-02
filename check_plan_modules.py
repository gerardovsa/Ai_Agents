#!/usr/bin/env python
import psycopg2

conn_str = 'postgresql://postgres.ryoicrdifiqhqpsnjmdo:inhouseprint@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres'
conn = psycopg2.connect(conn_str)
cur = conn.cursor()

# Check plan_modules contents
cur.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='ai_infrastructure' AND table_name='plan_modules'")
exists = cur.fetchone()[0]
print(f"plan_modules table exists: {exists == 1}")
if exists:
    cur.execute("SELECT plan_tier, module_name FROM ai_infrastructure.plan_modules ORDER BY plan_tier, module_name")
    rows = cur.fetchall()
    print(f"plan_modules rows: {len(rows)}")
    for r in rows:
        print(f"  {r[0]:<15} {r[1]}")

# Check current org settings
cur.execute("SELECT id, name, plan_tier FROM ai_infrastructure.organisations")
orgs = cur.fetchall()
print("\n=== ORGANISATIONS ===")
for r in orgs:
    print(f"  id={r[0]} name={r[1]!r} plan_tier={r[2]}")

# Check org_module_access
cur.execute("SELECT COUNT(*) FROM ai_infrastructure.org_module_access")
print(f"\norg_module_access rows: {cur.fetchone()[0]}")

# Check user_module_access
cur.execute("SELECT COUNT(*) FROM ai_infrastructure.user_module_access")
print(f"user_module_access rows: {cur.fetchone()[0]}")

cur.close()
conn.close()
