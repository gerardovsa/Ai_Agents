"""
Test Connection Pooling + Schema Path Fix
=========================================

Tests:
1. Connection pool creation and performance
2. Schema search_path configuration
3. Table access with and without schema prefix
4. Performance comparison (pool vs direct)
"""

import os
import time
import psycopg2
from dotenv import load_dotenv

load_dotenv('.env.master')

def test_direct_connection():
    """Test direct connection (OLD WAY - SLOW)"""
    print("\n" + "=" * 80)
    print("TEST 1: DIRECT CONNECTION (NO POOL)")
    print("=" * 80)
    
    db_url = os.getenv('SUPABASE_DB_URL')
    
    times = []
    for i in range(5):
        start = time.time()
        conn = psycopg2.connect(db_url, sslmode='require')
        cursor = conn.cursor()
        cursor.execute("SET search_path TO ai_infrastructure, public")
        cursor.execute("SELECT COUNT(*) FROM users")
        result = cursor.fetchone()
        conn.close()
        elapsed = time.time() - start
        times.append(elapsed)
        print(f"  Connection {i+1}: {elapsed*1000:.1f}ms - {result[0]} users")
    
    avg = sum(times) / len(times)
    print(f"\n✅ Average time (direct): {avg*1000:.1f}ms")
    return avg


def test_connection_pool():
    """Test connection pool (NEW WAY - FAST)"""
    print("\n" + "=" * 80)
    print("TEST 2: CONNECTION POOL")
    print("=" * 80)
    
    from psycopg2 import pool
    
    db_url = os.getenv('SUPABASE_DB_URL')
    
    # Create pool
    print("Creating connection pool (2-10 connections)...")
    connection_pool = pool.ThreadedConnectionPool(
        minconn=2,
        maxconn=10,
        dsn=db_url,
        sslmode='require',
        connect_timeout=30
    )
    print("✅ Pool created")
    
    # Test connections from pool
    times = []
    for i in range(5):
        start = time.time()
        conn = connection_pool.getconn()
        cursor = conn.cursor()
        cursor.execute("SET search_path TO ai_infrastructure, public")
        cursor.execute("SELECT COUNT(*) FROM users")
        result = cursor.fetchone()
        connection_pool.putconn(conn)
        elapsed = time.time() - start
        times.append(elapsed)
        print(f"  Connection {i+1}: {elapsed*1000:.1f}ms - {result[0]} users")
    
    avg = sum(times) / len(times)
    print(f"\n✅ Average time (pool): {avg*1000:.1f}ms")
    
    connection_pool.closeall()
    return avg


def test_schema_search_path():
    """Test schema search_path configuration"""
    print("\n" + "=" * 80)
    print("TEST 3: SCHEMA SEARCH PATH")
    print("=" * 80)
    
    db_url = os.getenv('SUPABASE_DB_URL')
    conn = psycopg2.connect(db_url, sslmode='require')
    cursor = conn.cursor()
    
    # Test 1: Without search_path (WILL FAIL)
    print("\n❌ Query WITHOUT search_path set:")
    try:
        cursor.execute("SELECT COUNT(*) FROM user_gmail_accounts")
        result = cursor.fetchone()
        print(f"  Result: {result[0]} accounts")
    except psycopg2.errors.UndefinedTable as e:
        print(f"  ERROR: {e}")
        conn.rollback()
    
    # Test 2: Set search_path
    print("\n✅ Setting search_path to ai_infrastructure...")
    cursor.execute("SET search_path TO ai_infrastructure, public")
    conn.commit()
    
    # Test 3: With search_path (WILL WORK)
    print("\n✅ Query WITH search_path set:")
    try:
        cursor.execute("SELECT COUNT(*) FROM user_gmail_accounts")
        result = cursor.fetchone()
        print(f"  Result: {result[0]} gmail accounts")
    except Exception as e:
        print(f"  ERROR: {e}")
    
    # Test 4: Explicit schema prefix (ALWAYS WORKS)
    print("\n✅ Query with explicit schema prefix:")
    cursor.execute("SELECT COUNT(*) FROM ai_infrastructure.user_gmail_accounts")
    result = cursor.fetchone()
    print(f"  Result: {result[0]} gmail accounts")
    
    # Test 5: Check current search_path
    cursor.execute("SHOW search_path")
    result = cursor.fetchone()
    print(f"\n✅ Current search_path: {result[0]}")
    
    conn.close()


def test_all_tables():
    """Test access to all tables in ai_infrastructure schema"""
    print("\n" + "=" * 80)
    print("TEST 4: ALL TABLES ACCESS")
    print("=" * 80)
    
    db_url = os.getenv('SUPABASE_DB_URL')
    conn = psycopg2.connect(db_url, sslmode='require')
    cursor = conn.cursor()
    
    # Set search_path
    cursor.execute("SET search_path TO ai_infrastructure, public")
    
    # Get all tables
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'ai_infrastructure'
        ORDER BY table_name
    """)
    
    tables = [row[0] for row in cursor.fetchall()]
    print(f"\n📊 Found {len(tables)} tables in ai_infrastructure schema:")
    
    # Test each table
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  ✅ {table:<35} {count:>6} rows")
        except Exception as e:
            print(f"  ❌ {table:<35} ERROR: {str(e)[:50]}")
    
    conn.close()


def main():
    print("=" * 80)
    print("CONNECTION POOL + SCHEMA TEST SUITE")
    print("=" * 80)
    
    # Test 1: Direct connections
    try:
        direct_avg = test_direct_connection()
    except Exception as e:
        print(f"\n❌ Direct connection test failed: {e}")
        direct_avg = None
    
    # Test 2: Connection pool
    try:
        pool_avg = test_connection_pool()
    except Exception as e:
        print(f"\n❌ Connection pool test failed: {e}")
        pool_avg = None
    
    # Performance comparison
    if direct_avg and pool_avg:
        improvement = ((direct_avg - pool_avg) / direct_avg) * 100
        speedup = direct_avg / pool_avg
        
        print("\n" + "=" * 80)
        print("PERFORMANCE COMPARISON")
        print("=" * 80)
        print(f"Direct connection:  {direct_avg*1000:.1f}ms")
        print(f"Connection pool:    {pool_avg*1000:.1f}ms")
        print(f"Improvement:        {improvement:.1f}% faster")
        print(f"Speedup:            {speedup:.1f}x")
    
    # Test 3: Schema search_path
    try:
        test_schema_search_path()
    except Exception as e:
        print(f"\n❌ Schema search_path test failed: {e}")
    
    # Test 4: All tables
    try:
        test_all_tables()
    except Exception as e:
        print(f"\n❌ All tables test failed: {e}")
    
    print("\n" + "=" * 80)
    print("✅ TEST SUITE COMPLETE")
    print("=" * 80)
    print("\nNEXT STEPS:")
    print("1. Connection pooling implemented in database_utils.py")
    print("2. Schema search_path automatically set on each connection")
    print("3. View dashboard: http://localhost:5001/api/pool/dashboard")
    print("4. Deploy to Render: git push origin v6")


if __name__ == '__main__':
    main()
