"""
Quick test to verify database connection type (SQLite vs Supabase)
"""

import sys
sys.path.insert(0, 'AI_infrastructure')

from shared.database_utils import is_using_supabase, get_database_connection

print("=" * 80)
print("DATABASE CONNECTION TEST")
print("=" * 80)

# Check environment detection
using_supabase = is_using_supabase()
print(f"\nis_using_supabase(): {using_supabase}")

if using_supabase:
    print("✅ USING SUPABASE POSTGRESQL")
else:
    print("⚠️  USING LOCAL SQLITE")

# Test actual connection
print("\nTesting connection to ai_infrastructure database...")
try:
    conn = get_database_connection('ai_infrastructure')
    print(f"✅ Connection successful!")
    print(f"   Connection type: {type(conn).__name__}")
    
    # Check if it's psycopg2 (Supabase) or sqlite3 (Local)
    if 'psycopg2' in str(type(conn)):
        print("   Database: SUPABASE POSTGRESQL ✅")
    elif 'sqlite3' in str(type(conn)):
        print("   Database: SQLITE (LOCAL) ⚠️")
    else:
        print(f"   Database: UNKNOWN ({type(conn)})")
    
    conn.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")

print("\nTesting connection to synergy_sessions database...")
try:
    conn = get_database_connection('synergy_sessions')
    print(f"✅ Connection successful!")
    print(f"   Connection type: {type(conn).__name__}")
    
    if 'psycopg2' in str(type(conn)):
        print("   Database: SUPABASE POSTGRESQL ✅")
    elif 'sqlite3' in str(type(conn)):
        print("   Database: SQLITE (LOCAL) ⚠️")
    
    conn.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")

print("\n" + "=" * 80)
