#!/usr/bin/env python
import psycopg2
import sys

# Use the pooler connection URL from .env
conn_str = "postgresql://postgres.ryoicrdifiqhqpsnjmdo:inhouseprint@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres"

try:
    conn = psycopg2.connect(conn_str)
    cur = conn.cursor()
    
    queries = [
        ('organisation_platform_credentials', 'SELECT COUNT(*) FROM ai_infrastructure.organisation_platform_credentials'),
        ('org_module_access', 'SELECT COUNT(*) FROM ai_infrastructure.org_module_access'),
        ('platform_catalog', 'SELECT COUNT(*) FROM ai_infrastructure.platform_catalog'),
        ('module_catalog', 'SELECT COUNT(*) FROM ai_infrastructure.module_catalog'),
        ('user_platform_credentials', 'SELECT COUNT(*) FROM ai_infrastructure.user_platform_credentials')
    ]
    
    print("\n" + "="*60)
    print("DATABASE TABLE COUNTS")
    print("="*60)
    
    results = {}
    for table_name, query in queries:
        cur.execute(query)
        count = cur.fetchone()[0]
        results[table_name] = count
        print(f'{table_name:<40} : {count:>3}')
    
    print("="*60 + "\n")
    
    cur.close()
    conn.close()
    
    # Print summary
    print("\nSUMMARY:")
    print(f"  Org credentials:       {results['organisation_platform_credentials']} (should be >0)")
    print(f"  Module access:         {results['org_module_access']} (should be ~26)")
    print(f"  Platform catalog:      {results['platform_catalog']} (should be 27)")
    print(f"  Module catalog:        {results['module_catalog']} (should be 26)")
    print(f"  User credentials:      {results['user_platform_credentials']} (has {results['user_platform_credentials']})")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
