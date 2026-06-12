#!/usr/bin/env python
"""Full audit + seed script for the module tier system."""
import psycopg2

conn_str = 'postgresql://postgres.ryoicrdifiqhqpsnjmdo:inhouseprint@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres'
conn = psycopg2.connect(conn_str)
cur = conn.cursor()

# 1. All active modules
cur.execute("SELECT module_name FROM ai_infrastructure.module_catalog WHERE is_active = TRUE ORDER BY sort_order")
all_modules = [r[0] for r in cur.fetchall()]
print(f"All active modules ({len(all_modules)}): {all_modules}")

# 2. Missing from enterprise
cur.execute("SELECT module_name FROM ai_infrastructure.plan_modules WHERE plan_tier = 'enterprise'")
enterprise_modules = [r[0] for r in cur.fetchall()]
missing = [m for m in all_modules if m not in enterprise_modules]
print(f"\nMissing from enterprise plan_modules: {missing}")

# 3. Check if developer tier already exists
cur.execute("SELECT COUNT(*) FROM ai_infrastructure.plan_modules WHERE plan_tier = 'developer'")
dev_count = cur.fetchone()[0]
print(f"\n'developer' tier rows already: {dev_count}")

# 4. Check plan_tier constraint on organisations table
cur.execute("""
    SELECT cc.constraint_name, cc.check_clause
    FROM information_schema.check_constraints cc
    JOIN information_schema.constraint_column_usage cu ON cu.constraint_name = cc.constraint_name
    WHERE cu.table_schema = 'ai_infrastructure'
      AND cu.table_name = 'organisations'
      AND cu.column_name = 'plan_tier'
""")
constraints = cur.fetchall()
print(f"\nplan_tier constraints on organisations: {constraints}")

cur.close()
conn.close()
