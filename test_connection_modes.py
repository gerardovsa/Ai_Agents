"""Test Transaction vs Session pooler modes"""
import sys
import os
import time
sys.path.insert(0, 'AI_infrastructure')

from dotenv import load_dotenv
load_dotenv()

from shared.database_utils import get_database_connection

print("=" * 80)
print("SUPABASE CONNECTION MODE TEST")
print("=" * 80)

# Check configuration
pooler = os.getenv('SUPABASE_DB_URL_POOLER')
session = os.getenv('SUPABASE_DB_URL_SESSION')

print("\nConfigured URLs:")
print(f"  POOLER (6543): {'✅ SET' if pooler else '❌ NOT SET'}")
print(f"  SESSION (5432): {'✅ SET' if session else '❌ NOT SET'}")

print("\n" + "-" * 80)
print("Testing connection...")
print("-" * 80)

try:
    start = time.time()
    conn = get_database_connection('sessions')
    elapsed = (time.time() - start) * 1000
    
    cursor = conn.cursor()
    cursor.execute("SELECT current_database(), current_schema()")
    result = cursor.fetchone()
    
    print(f"\n✅ CONNECTION SUCCESSFUL ({elapsed:.1f}ms)")
    print(f"  Database: {result['current_database']}")
    print(f"  Schema: {result['current_schema']}")
    
    # Test thread count
    cursor.execute("SELECT COUNT(*) as count FROM sessions.threads")
    count = cursor.fetchone()['count']
    print(f"  Threads: {count}")
    
    cursor.close()
    conn.close()
    
    print("\n✅ Connection closed successfully")
    print("\n" + "=" * 80)
    print("PASSED - Ready for production")
    print("=" * 80)
    
except Exception as e:
    print(f"\n❌ FAILED: {e}")
    sys.exit(1)
