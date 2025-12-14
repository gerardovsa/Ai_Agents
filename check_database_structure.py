#!/usr/bin/env python3
"""
Check Supabase Database Structure
Verifies that ai_infrastructure and sessions schemas exist with proper tables
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from get_supabase_credentials import get_supabase_credentials_for_backend

def main():
    # Get credentials
    result = get_supabase_credentials_for_backend(1)
    if not result['success']:
        print("❌ Failed to get credentials")
        return
    
    creds = result['credentials']
    
    # Connect
    conn = psycopg2.connect(
        host=creds['db_host'],
        port=creds['db_port'],
        database=creds['db_name'],
        user=creds['db_user'],
        password=creds['db_password'],
        cursor_factory=RealDictCursor
    )
    
    cur = conn.cursor()
    
    # Check for schemas
    cur.execute("""
        SELECT schema_name 
        FROM information_schema.schemata 
        WHERE schema_name IN ('ai_infrastructure', 'sessions')
        ORDER BY schema_name
    """)
    schemas = [row['schema_name'] for row in cur.fetchall()]
    
    print("\n" + "="*80)
    print("DATABASE STRUCTURE VERIFICATION")
    print("="*80)
    
    print(f"\n📁 SCHEMAS FOUND: {len(schemas)}")
    for schema in schemas:
        print(f"   ✓ {schema}")
    
    if 'ai_infrastructure' not in schemas:
        print("   ❌ MISSING: ai_infrastructure")
    if 'sessions' not in schemas:
        print("   ❌ MISSING: sessions")
    
    # Check tables in each schema
    for schema in ['ai_infrastructure', 'sessions']:
        if schema not in schemas:
            continue
            
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = %s 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """, (schema,))
        tables = [row['table_name'] for row in cur.fetchall()]
        
        print(f"\n📋 {schema.upper()} SCHEMA - {len(tables)} tables:")
        
        for table in sorted(tables):
            # Get row count
            try:
                cur.execute(f'SELECT COUNT(*) as cnt FROM {schema}."{table}"')
                count = cur.fetchone()['cnt']
                print(f"   ✓ {table:50} {count:>8,} rows")
            except Exception as e:
                print(f"   ⚠ {table:50} (error: {str(e)[:30]})")
    
    # Check key tables exist
    print(f"\n🔑 CRITICAL TABLES CHECK:")
    
    critical_tables = {
        'ai_infrastructure': [
            'users',
            'user_sessions', 
            'user_platform_credentials',
            'ai_tool_intelligence_log',
            'oauth_tokens'
        ],
        'sessions': [
            'threads',
            'messages',
            'users',
            'sessions'
        ]
    }
    
    for schema, expected_tables in critical_tables.items():
        if schema not in schemas:
            continue
            
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = %s 
            AND table_type = 'BASE TABLE'
        """, (schema,))
        existing = [row['table_name'] for row in cur.fetchall()]
        
        for table in expected_tables:
            if table in existing:
                print(f"   ✓ {schema}.{table}")
            else:
                print(f"   ❌ MISSING: {schema}.{table}")
    
    conn.close()
    
    print("\n" + "="*80)
    print("✅ DATABASE STRUCTURE VERIFICATION COMPLETE")
    print("="*80 + "\n")

if __name__ == '__main__':
    main()
