"""
Setup and Test Supabase Database Connection
Helps configure Supabase credentials and verify database access
"""

import os
import sys
from pathlib import Path

def get_supabase_connection_string():
    """Get Supabase connection string from environment or prompt user"""
    
    # Check if already set in environment
    db_url = os.getenv('SUPABASE_DB_URL')
    
    if db_url:
        print(f"✅ Found SUPABASE_DB_URL in environment")
        return db_url
    
    print("\n" + "="*70)
    print("SUPABASE DATABASE CONNECTION SETUP")
    print("="*70)
    print()
    print("You need the Supabase Session Pooler connection string.")
    print()
    print("Where to find it:")
    print("  1. Go to: https://supabase.com/dashboard/project/YOUR_PROJECT")
    print("  2. Click 'Database' in left sidebar")
    print("  3. Click 'Connection string' tab")
    print("  4. Select 'Session pooler' mode (NOT Transaction pooler)")
    print("  5. Copy the connection string")
    print()
    print("Format should be:")
    print("  postgresql://postgres.PROJECT:[PASSWORD]@aws-X-region.pooler.supabase.com:5432/postgres")
    print()
    
    connection_string = input("Paste your Supabase connection string here: ").strip()
    
    if not connection_string:
        print("❌ No connection string provided")
        return None
    
    # Validate format
    if not connection_string.startswith('postgresql://'):
        print("⚠️  Warning: Connection string should start with 'postgresql://'")
    
    if 'pooler.supabase.com' not in connection_string:
        print("⚠️  Warning: Should use Session Pooler (*.pooler.supabase.com)")
    
    return connection_string


def save_to_env_file(connection_string):
    """Save connection string to .env.master file"""
    
    env_file = Path(__file__).parent / '.env.master'
    
    if not env_file.exists():
        print(f"❌ .env.master not found at: {env_file}")
        return False
    
    # Read existing content
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if SUPABASE_DB_URL already exists
    if 'SUPABASE_DB_URL=' in content:
        print("\n⚠️  SUPABASE_DB_URL already exists in .env.master")
        replace = input("Replace existing value? (y/n): ").strip().lower()
        
        if replace != 'y':
            print("Skipping save to .env.master")
            return False
        
        # Replace existing value
        lines = content.split('\n')
        new_lines = []
        for line in lines:
            if line.startswith('SUPABASE_DB_URL='):
                new_lines.append(f'SUPABASE_DB_URL={connection_string}')
            else:
                new_lines.append(line)
        content = '\n'.join(new_lines)
    else:
        # Add new section
        supabase_section = f"""

# ========================================
# SUPABASE POSTGRESQL DATABASE
# ========================================
# Production database for Render deployment
# Connection: Session Pooler (IPv4 compatible)
# Schemas: ai_infrastructure, sessions

SUPABASE_DB_URL={connection_string}
USE_SUPABASE=true
"""
        content += supabase_section
    
    # Write back to file
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Saved SUPABASE_DB_URL to .env.master")
    return True


def test_connection(connection_string):
    """Test connection to Supabase database"""
    
    print("\n" + "="*70)
    print("TESTING SUPABASE CONNECTION")
    print("="*70)
    
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
    except ImportError:
        print("❌ psycopg2 not installed")
        print("   Install with: pip install psycopg2-binary")
        return False
    
    # Test connection
    print("\n🔷 Attempting connection to Supabase...")
    
    try:
        conn = psycopg2.connect(
            connection_string,
            cursor_factory=RealDictCursor,
            connect_timeout=30
        )
        
        print("✅ Connection successful!")
        
        # Test queries
        cursor = conn.cursor()
        
        # 1. List all schemas
        print("\n📊 Listing schemas:")
        cursor.execute("""
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
            ORDER BY schema_name
        """)
        schemas = cursor.fetchall()
        
        for schema in schemas:
            schema_name = schema['schema_name']
            print(f"  - {schema_name}")
            
            # Count tables in each schema
            cursor.execute(f"""
                SELECT COUNT(*) as count
                FROM information_schema.tables
                WHERE table_schema = %s
            """, (schema_name,))
            result = cursor.fetchone()
            table_count = result['count']
            print(f"    Tables: {table_count}")
        
        # 2. Check ai_infrastructure schema
        print("\n📊 ai_infrastructure schema tables:")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables
            WHERE table_schema = 'ai_infrastructure'
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        
        for table in tables:
            print(f"  - {table['table_name']}")
        
        # 3. Check sessions schema
        print("\n📊 sessions schema tables:")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables
            WHERE table_schema = 'sessions'
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        
        for table in tables:
            print(f"  - {table['table_name']}")
        
        # 4. Test cross-schema query
        print("\n🔍 Testing cross-schema query:")
        cursor.execute("SET search_path TO ai_infrastructure, public")
        cursor.execute("SELECT COUNT(*) as count FROM sessions.user_sessions")
        result = cursor.fetchone()
        print(f"  ✅ Found {result['count']} records in sessions.user_sessions")
        
        # 5. Check permissions
        print("\n🔐 Checking schema permissions:")
        cursor.execute("""
            SELECT schema_name, 
                   pg_catalog.has_schema_privilege(current_user, schema_name, 'USAGE') as has_usage,
                   pg_catalog.has_schema_privilege(current_user, schema_name, 'CREATE') as has_create
            FROM information_schema.schemata
            WHERE schema_name IN ('ai_infrastructure', 'sessions', 'public')
        """)
        perms = cursor.fetchall()
        
        for perm in perms:
            usage = "✅" if perm['has_usage'] else "❌"
            create = "✅" if perm['has_create'] else "❌"
            print(f"  {perm['schema_name']}:")
            print(f"    USAGE: {usage}")
            print(f"    CREATE: {create}")
        
        cursor.close()
        conn.close()
        
        print("\n" + "="*70)
        print("✅ ALL TESTS PASSED - Supabase database is properly configured!")
        print("="*70)
        
        return True
        
    except psycopg2.OperationalError as e:
        print(f"\n❌ Connection failed: {e}")
        print("\nTroubleshooting:")
        print("  1. Check connection string format")
        print("  2. Verify password is correct")
        print("  3. Ensure using Session Pooler (not Transaction)")
        print("  4. Check Supabase project is active")
        print("  5. Verify network connectivity")
        return False
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main setup and test flow"""
    
    print("\n" + "="*70)
    print("SUPABASE DATABASE SETUP & VERIFICATION")
    print("="*70)
    
    # Step 1: Get connection string
    connection_string = get_supabase_connection_string()
    
    if not connection_string:
        print("\n❌ Setup cancelled - no connection string provided")
        return 1
    
    # Step 2: Save to .env.master
    print("\n" + "="*70)
    print("SAVE TO .env.master FILE")
    print("="*70)
    
    save = input("\nSave connection string to .env.master? (y/n): ").strip().lower()
    
    if save == 'y':
        save_to_env_file(connection_string)
    
    # Step 3: Test connection
    success = test_connection(connection_string)
    
    if success:
        print("\n✅ Setup complete! Your Supabase database is ready to use.")
        print("\nNext steps:")
        print("  1. Commit the changes: git add . && git commit -m 'Fix: Supabase schema fixes'")
        print("  2. Push to Render: git push origin v6")
        print("  3. Monitor Render deployment logs")
        return 0
    else:
        print("\n❌ Setup incomplete - connection test failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
