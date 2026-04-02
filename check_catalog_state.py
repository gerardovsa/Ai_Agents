#!/usr/bin/env python
import psycopg2

conn_str = 'postgresql://postgres.ryoicrdifiqhqpsnjmdo:inhouseprint@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres'
conn = psycopg2.connect(conn_str)
cur = conn.cursor()

# What modules are in the catalog?
cur.execute("SELECT module_name, min_plan_tier, is_active FROM ai_infrastructure.module_catalog ORDER BY sort_order")
rows = cur.fetchall()
print('\n=== MODULE CATALOG (24 rows) ===')
for r in rows:
    print(f'  {r[0]:<35} plan={r[1]:<15} active={r[2]}')

# What platforms are in the catalog?
cur.execute("SELECT platform_name, category FROM ai_infrastructure.platform_catalog ORDER BY sort_order")
rows = cur.fetchall()
print('\n=== PLATFORM CATALOG (26 rows) ===')
for r in rows:
    print(f'  {r[0]:<35} category={r[1]}')

# Does user_module_access table exist?
cur.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='ai_infrastructure' AND table_name='user_module_access'")
print(f'\nuser_module_access table exists: {cur.fetchone()[0] == 1}')

# Does plan_modules table exist?
cur.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='ai_infrastructure' AND table_name='plan_modules'")
print(f'plan_modules table exists: {cur.fetchone()[0] == 1}')

# Does user_module_access table exist?
cur.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='ai_infrastructure' AND table_name='teams'")
print(f'teams table exists: {cur.fetchone()[0] == 1}')

cur.close()
conn.close()
