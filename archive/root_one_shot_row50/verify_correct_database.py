#!/usr/bin/env python3
"""
Verify Correct Supabase Database (ryoicrdifiqhqpsnjmdo)

This script uses SUPABASE_DB_URL_POOLER environment variable to connect
to the CORRECT database (ryoicrdifiqhqpsnjmdo) with ai_infrastructure and sessions schemas.

Usage: 
    python verify_correct_database.py
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    print("\n" + "="*80)
    print("🔍 VERIFYING CORRECT SUPABASE DATABASE (ryoicrdifiqhqpsnjmdo)")
    print("="*80 + "\n")
    
    # Get pooler URL from environment (what Render uses)
    db_url = os.getenv('SUPABASE_DB_URL_POOLER')
    
    if not db_url:
        print("❌ SUPABASE_DB_URL_POOLER not set in environment")
        print("\n💡 Set it to:")
        print("   postgresql://postgres.ryoicrdifiqhqpsnjmdo:inhouseprint@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres")
        return 1
    
    # Extract project ID for verification
    if 'ryoicrdifiqhqpsnjmdo' in db_url:
        project_id = 'ryoicrdifiqhqpsnjmdo ✅ CORRECT'
    elif 'wuwmvtslltqhaycyukxk' in db_url:
        project_id = 'wuwmvtslltqhaycyukxk ❌ WRONG (Vet Alerts DB)'
    else:
        project_id = 'UNKNOWN'
    
    print(f"📡 Connection String: {db_url[:60]}...")
    print(f"🎯 Project ID: {project_id}\n")
    
    # Connect
    print("🔌 Connecting to Supabase PostgreSQL...")
    try:
        conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
        print("✅ Connected successfully\n")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return 1
    
    cur = conn.cursor()
    
    # Check for ai_infrastructure and sessions schemas
    print("📁 CHECKING FOR REQUIRED SCHEMAS...")
    cur.execute("""
        SELECT schema_name 
        FROM information_schema.schemata 
        WHERE schema_name IN ('ai_infrastructure', 'sessions')
        ORDER BY schema_name
    """)
    schemas = [row['schema_name'] for row in cur.fetchall()]
    
    print(f"\n   Found {len(schemas)} schemas:")
    if 'ai_infrastructure' in schemas:
        print("   ✅ ai_infrastructure")
    else:
        print("   ❌ MISSING: ai_infrastructure")
    
    if 'sessions' in schemas:
        print("   ✅ sessions")
    else:
        print("   ❌ MISSING: sessions")
    
    # If schemas exist, check key tables
    if len(schemas) == 2:
        print("\n📋 CHECKING KEY TABLES...")
        
        # ai_infrastructure critical tables
        ai_tables = [
            'users',
            'user_sessions',
            'user_platform_credentials',
            'ai_tool_intelligence_log',
            'oauth_tokens'
        ]
        
        print("\n   ai_infrastructure schema:")
        for table in ai_tables:
            try:
                cur.execute(f'SELECT COUNT(*) as cnt FROM ai_infrastructure.{table}')
                count = cur.fetchone()['cnt']
                print(f"      ✅ {table:35} {count:>6,} rows")
            except Exception as e:
                print(f"      ❌ {table:35} ERROR")
        
        # sessions critical tables
        session_tables = [
            'threads',
            'messages',
            'users',
            'sessions'
        ]
        
        print("\n   sessions schema:")
        for table in session_tables:
            try:
                cur.execute(f'SELECT COUNT(*) as cnt FROM sessions.{table}')
                count = cur.fetchone()['cnt']
                print(f"      ✅ {table:35} {count:>6,} rows")
            except Exception as e:
                print(f"      ❌ {table:35} ERROR")
    
    conn.close()
    
    print("\n" + "="*80)
    if len(schemas) == 2:
        print("✅ DATABASE STRUCTURE VERIFIED - CORRECT DATABASE")
    else:
        print("❌ WRONG DATABASE - Missing required schemas")
    print("="*80 + "\n")
    
    return 0 if len(schemas) == 2 else 1

if __name__ == '__main__':
    exit(main())
