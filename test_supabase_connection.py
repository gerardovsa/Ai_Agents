#!/usr/bin/env python3
"""
Test Supabase Connection - Verify Fix
Run this locally or in Render shell to verify database connection
"""

import os
import sys

def test_connection():
    """Test Supabase connection with both modes"""
    
    print("=" * 70)
    print("SUPABASE CONNECTION TEST")
    print("=" * 70)
    
    # Check environment variables
    print("\n1️⃣  Checking Environment Variables...")
    
    pooler_url = os.getenv('SUPABASE_DB_URL_POOLER')
    session_url = os.getenv('SUPABASE_DB_URL_SESSION')
    legacy_url = os.getenv('SUPABASE_DB_URL')
    
    if pooler_url:
        print(f"   ✅ SUPABASE_DB_URL_POOLER: {pooler_url[:60]}...")
    else:
        print(f"   ❌ SUPABASE_DB_URL_POOLER: NOT SET")
    
    if session_url:
        print(f"   ✅ SUPABASE_DB_URL_SESSION: {session_url[:60]}...")
    else:
        print(f"   ⚠️  SUPABASE_DB_URL_SESSION: NOT SET (optional)")
    
    if legacy_url:
        print(f"   ℹ️  SUPABASE_DB_URL: {legacy_url[:60]}... (legacy)")
    
    if not (pooler_url or session_url or legacy_url):
        print("\n❌ ERROR: No Supabase connection URL found!")
        print("\nAdd one of these environment variables:")
        print("  - SUPABASE_DB_URL_POOLER (recommended)")
        print("  - SUPABASE_DB_URL_SESSION (fallback)")
        print("  - SUPABASE_DB_URL (legacy)")
        return False
    
    # Test connection
    print("\n2️⃣  Testing Database Connection...")
    
    try:
        import psycopg2
    except ImportError:
        print("   ❌ ERROR: psycopg2 not installed")
        print("   Run: pip install psycopg2-binary")
        return False
    
    # Try Transaction Mode first
    if pooler_url:
        print("\n   Testing Transaction Mode (port 6543)...")
        try:
            conn = psycopg2.connect(pooler_url, connect_timeout=10)
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(f"   ✅ Connected successfully!")
            print(f"   PostgreSQL version: {version[:60]}...")
            
            # Test schema access
            cursor.execute("SELECT current_database(), current_schema();")
            db, schema = cursor.fetchone()
            print(f"   Database: {db}, Schema: {schema}")
            
            cursor.close()
            conn.close()
            print("   ✅ Transaction Mode: WORKING")
            return True
            
        except Exception as e:
            print(f"   ❌ Transaction Mode FAILED: {e}")
    
    # Try Session Mode fallback
    if session_url:
        print("\n   Testing Session Mode (port 5432)...")
        try:
            conn = psycopg2.connect(session_url, connect_timeout=10)
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(f"   ✅ Connected successfully!")
            print(f"   PostgreSQL version: {version[:60]}...")
            
            cursor.close()
            conn.close()
            print("   ✅ Session Mode: WORKING")
            return True
            
        except Exception as e:
            print(f"   ❌ Session Mode FAILED: {e}")
    
    # Try legacy variable
    if legacy_url and not (pooler_url or session_url):
        print("\n   Testing Legacy URL...")
        try:
            conn = psycopg2.connect(legacy_url, connect_timeout=10)
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(f"   ✅ Connected successfully!")
            print(f"   PostgreSQL version: {version[:60]}...")
            
            # Detect port
            port = "6543" if ":6543/" in legacy_url else "5432" if ":5432/" in legacy_url else "unknown"
            print(f"   ⚠️  Legacy URL working (port: {port})")
            print(f"   ⚠️  Recommend migrating to SUPABASE_DB_URL_POOLER")
            
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            print(f"   ❌ Legacy URL FAILED: {e}")
    
    print("\n❌ All connection attempts failed!")
    return False


def test_connection_pool():
    """Test connection pool creation"""
    
    print("\n3️⃣  Testing Connection Pool...")
    
    try:
        # Add AI_infrastructure to path
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'AI_infrastructure'))
        
        from shared.database_utils import get_database_connection
        
        print("   Creating connection pool for 'ai_infrastructure'...")
        conn = get_database_connection('ai_infrastructure')
        
        print("   ✅ Connection pool created successfully!")
        
        # Test query
        cursor = conn.cursor()
        cursor.execute("SELECT 1 as test")
        result = cursor.fetchone()
        
        if result and result[0] == 1:
            print("   ✅ Test query successful!")
        
        cursor.close()
        conn.close()
        
        print("   ✅ Connection pool: WORKING")
        return True
        
    except Exception as e:
        print(f"   ❌ Connection pool FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    
    print("\n🔍 Supabase Connection Diagnostic Tool")
    print("=" * 70)
    
    # Test 1: Basic connection
    basic_ok = test_connection()
    
    if not basic_ok:
        print("\n" + "=" * 70)
        print("❌ BASIC CONNECTION FAILED - Fix environment variables first")
        print("=" * 70)
        return 1
    
    # Test 2: Connection pool
    pool_ok = test_connection_pool()
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Basic Connection:  {'✅ PASS' if basic_ok else '❌ FAIL'}")
    print(f"Connection Pool:   {'✅ PASS' if pool_ok else '❌ FAIL'}")
    
    if basic_ok and pool_ok:
        print("\n🎉 All tests passed! Supabase connection is working.")
        print("\nNext steps:")
        print("  1. Deploy to Render")
        print("  2. Test OAuth flows")
        print("  3. Monitor logs for connection pool stats")
        return 0
    else:
        print("\n⚠️  Some tests failed. Review errors above.")
        print("\nTroubleshooting:")
        print("  1. Verify environment variables are set correctly")
        print("  2. Check password is URL-encoded if it has special characters")
        print("  3. Verify Supabase project is active")
        print("  4. Check IP whitelist in Supabase settings")
        return 1


if __name__ == '__main__':
    sys.exit(main())
