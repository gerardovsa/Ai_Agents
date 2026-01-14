"""
SUPABASE CONNECTION VERIFICATION TOOL
Purpose: Verify all database connections work correctly with Supabase PostgreSQL
Date: December 14, 2025
"""

import os
import sys
from pathlib import Path

# Add AI_infrastructure to path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir / 'AI_infrastructure'))

from shared.database_utils import (
    get_ai_infrastructure_connection,
    get_sessions_connection,
    get_synergy_sessions_connection,
    get_pool_stats,
    log_pool_usage,
    is_using_supabase
)

def print_section(title):
    """Print formatted section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def test_connection(conn_func, schema_name):
    """
    Test database connection and verify configuration
    
    Args:
        conn_func: Connection function (e.g., get_ai_infrastructure_connection)
        schema_name: Expected schema name
    
    Returns:
        bool: True if connection successful
    """
    print(f"Testing: {schema_name} schema")
    print("-" * 70)
    
    try:
        # Get connection
        conn = conn_func()
        print(f"✅ Connection acquired")
        
        # Create cursor
        cursor = conn.cursor()
        print(f"✅ Cursor created (RealDictCursor expected)")
        
        # Verify cursor type
        cursor_type = type(cursor).__name__
        print(f"   Cursor type: {cursor_type}")
        
        # Check search_path
        cursor.execute("SHOW search_path")
        search_path = cursor.fetchone()
        print(f"✅ Search path: {search_path}")
        
        # Verify schema exists
        cursor.execute("""
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name = %s
        """, (schema_name,))
        schema_exists = cursor.fetchone()
        
        if schema_exists:
            print(f"✅ Schema '{schema_name}' exists in database")
        else:
            print(f"⚠️  Schema '{schema_name}' NOT FOUND in database")
            return False
        
        # List tables in schema
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = %s 
            ORDER BY table_name
        """, (schema_name,))
        tables = cursor.fetchall()
        
        print(f"✅ Tables in '{schema_name}' schema: {len(tables)}")
        if tables:
            for table in tables[:5]:  # Show first 5
                table_name = table[0] if isinstance(table, tuple) else table.get('table_name', table)
                print(f"   - {table_name}")
            if len(tables) > 5:
                print(f"   ... and {len(tables) - 5} more")
        
        # Test query with dict-like row access
        cursor.execute(f"""
            SELECT table_name, table_type 
            FROM information_schema.tables 
            WHERE table_schema = %s 
            LIMIT 1
        """, (schema_name,))
        test_row = cursor.fetchone()
        
        if test_row:
            # Try dict-like access
            try:
                if isinstance(test_row, dict) or hasattr(test_row, '__getitem__'):
                    if 'table_name' in test_row or (hasattr(test_row, 'keys') and 'table_name' in test_row.keys()):
                        print(f"✅ Dict-like row access working (RealDictCursor)")
                    else:
                        print(f"⚠️  Row is dict-like but missing expected keys")
                else:
                    print(f"⚠️  Row is tuple, not dict (RealDictCursor may not be active)")
            except Exception as e:
                print(f"⚠️  Error testing dict access: {e}")
        
        # Close connection (returns to pool)
        cursor.close()
        conn.close()
        print(f"✅ Connection closed (returned to pool)")
        
        print(f"\n✅ {schema_name} - ALL TESTS PASSED\n")
        return True
        
    except Exception as e:
        print(f"\n❌ {schema_name} - FAILED")
        print(f"   Error: {type(e).__name__}: {e}\n")
        return False

def verify_environment():
    """Verify environment variables are set correctly"""
    print_section("ENVIRONMENT VERIFICATION")
    
    required_vars = [
        'SUPABASE_URL',
        'SUPABASE_ANON_KEY',
        'SUPABASE_DB_URL_POOLER',
    ]
    
    optional_vars = [
        'SUPABASE_DB_URL_SESSION',
        'SUPABASE_SERVICE_KEY',
        'SUPABASE_ACCESS_TOKEN'
    ]
    
    all_ok = True
    
    print("Required Variables:")
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if 'KEY' in var or 'TOKEN' in var:
                display_value = f"{value[:10]}...{value[-10:]}" if len(value) > 20 else "***"
            elif 'URL' in var:
                display_value = value.split('@')[-1] if '@' in value else value
            else:
                display_value = value
            print(f"  ✅ {var}: {display_value}")
        else:
            print(f"  ❌ {var}: NOT SET")
            all_ok = False
    
    print("\nOptional Variables:")
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            if 'KEY' in var or 'TOKEN' in var:
                display_value = f"{value[:10]}...{value[-10:]}" if len(value) > 20 else "***"
            else:
                display_value = value.split('@')[-1] if '@' in value else value
            print(f"  ✅ {var}: {display_value}")
        else:
            print(f"  ⚠️  {var}: Not set (optional)")
    
    # Check Supabase mode
    print(f"\nSupabase Mode:")
    print(f"  is_using_supabase(): {is_using_supabase()}")
    
    return all_ok

def test_all_connections():
    """Test all schema connections"""
    print_section("DATABASE CONNECTION TESTS")
    
    results = {
        'ai_infrastructure': test_connection(get_ai_infrastructure_connection, 'ai_infrastructure'),
        'sessions': test_connection(get_sessions_connection, 'sessions'),
        'synergy_sessions': test_connection(get_synergy_sessions_connection, 'synergy_sessions'),
    }
    
    return results

def verify_connection_pooling():
    """Verify connection pooling is working"""
    print_section("CONNECTION POOL VERIFICATION")
    
    # Get pool stats
    stats = get_pool_stats()
    
    print("Pool Statistics:")
    print(f"  Pools created: {stats['pools_created']}")
    print(f"  Connections acquired: {stats['connections_acquired']}")
    print(f"  Connections returned: {stats['connections_returned']}")
    print(f"  Leaked connections: {stats['connections_acquired'] - stats['connections_returned']}")
    print(f"  Pool hits: {stats['pool_hits']}")
    print(f"  Pool misses: {stats['pool_misses']}")
    
    if stats['connections_acquired'] > 0:
        avg_wait = stats['avg_wait_time']
        print(f"  Avg wait time: {avg_wait*1000:.1f}ms")
    
    # Detailed pool usage
    log_pool_usage()
    
    # Check for leaks
    leaked = stats['connections_acquired'] - stats['connections_returned']
    if leaked > 0:
        print(f"\n⚠️  WARNING: {leaked} leaked connections detected!")
        print(f"   This indicates missing conn.close() calls in code")
        return False
    else:
        print(f"\n✅ No leaked connections - pool is healthy")
        return True

def main():
    """Run all verification tests"""
    print("\n")
    print("=" * 70)
    print("  SUPABASE CONNECTION VERIFICATION")
    print("  Date: December 14, 2025")
    print("=" * 70)
    
    # Step 1: Verify environment
    env_ok = verify_environment()
    
    if not env_ok:
        print("\n❌ ENVIRONMENT VERIFICATION FAILED")
        print("   Fix environment variables before testing connections")
        return 1
    
    # Step 2: Test connections
    results = test_all_connections()
    
    # Step 3: Verify pooling
    pool_ok = verify_connection_pooling()
    
    # Final report
    print_section("FINAL VERIFICATION REPORT")
    
    print("Environment Variables:")
    print(f"  {'✅ PASS' if env_ok else '❌ FAIL'}")
    
    print("\nDatabase Connections:")
    all_connections_ok = all(results.values())
    for schema, ok in results.items():
        status = '✅ PASS' if ok else '❌ FAIL'
        print(f"  {schema:20} {status}")
    
    print("\nConnection Pooling:")
    print(f"  {'✅ PASS' if pool_ok else '⚠️  WARNING'}")
    
    print("\nOverall Status:")
    if env_ok and all_connections_ok and pool_ok:
        print("  ✅ ALL SYSTEMS OPERATIONAL")
        print("  🎉 Supabase connections verified successfully!")
        return 0
    else:
        print("  ❌ ISSUES DETECTED")
        print("  Review the errors above and fix before proceeding")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
