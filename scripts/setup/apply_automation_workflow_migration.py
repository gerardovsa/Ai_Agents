"""
Apply Automation Workflow Tables Migration to Supabase
=======================================================

This script applies the 005_automation_workflow_tables.sql migration
to your Supabase PostgreSQL database.

Tables Created:
1. automation_workflows - Main workflow definitions
2. workflow_executions - Execution history/logging
3. workflow_templates - Pre-built templates
4. workflow_schedules - Scheduled triggers
5. workflow_node_library - Custom node definitions

Usage:
    python apply_automation_workflow_migration.py
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import psycopg2
    from dotenv import load_dotenv
except ImportError:
    print("❌ Missing dependencies. Install:")
    print("   pip install psycopg2-binary python-dotenv")
    sys.exit(1)

# Load environment variables
load_dotenv()

# Supabase connection details
SUPABASE_DB_URL = os.getenv('SUPABASE_DB_URL')

if not SUPABASE_DB_URL:
    print("❌ SUPABASE_DB_URL not found in environment")
    print("   Set it in .env or .env.master file")
    print("   Format: postgresql://postgres:[password]@db.[ref].supabase.co:5432/postgres")
    sys.exit(1)


def apply_migration():
    """Apply the automation workflow tables migration"""
    
    print("🚀 Starting Automation Workflow Migration")
    print("=" * 60)
    
    # Read migration file - Go up to AI_agents root directory
    root_dir = Path(__file__).parent.parent.parent
    migration_file = root_dir / 'supabase_migrations' / '005_automation_workflow_tables.sql'
    
    if not migration_file.exists():
        print(f"❌ Migration file not found: {migration_file}")
        sys.exit(1)
    
    print(f"📄 Reading migration: {migration_file.name}")
    
    with open(migration_file, 'r', encoding='utf-8') as f:
        sql = f.read()
    
    # Connect to Supabase
    print(f"🔌 Connecting to Supabase...")
    
    try:
        conn = psycopg2.connect(SUPABASE_DB_URL)
        cursor = conn.cursor()
        
        print("✅ Connected to Supabase PostgreSQL")
        
        # Execute migration
        print("⚙️  Executing migration SQL...")
        
        cursor.execute(sql)
        conn.commit()
        
        print("✅ Migration executed successfully")
        
        # Verify tables created
        print("\n📊 Verifying tables...")
        
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE '%workflow%'
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        
        print(f"\n✅ Created {len(tables)} tables:")
        for table in tables:
            print(f"   • {table[0]}")
        
        # Verify indexes
        print("\n📊 Verifying indexes...")
        
        cursor.execute("""
            SELECT tablename, indexname 
            FROM pg_indexes 
            WHERE tablename LIKE '%workflow%'
            ORDER BY tablename, indexname
        """)
        
        indexes = cursor.fetchall()
        
        print(f"\n✅ Created {len(indexes)} indexes:")
        index_count = {}
        for table, index in indexes:
            index_count[table] = index_count.get(table, 0) + 1
        
        for table, count in index_count.items():
            print(f"   • {table}: {count} indexes")
        
        # Verify RLS policies
        print("\n📊 Verifying RLS policies...")
        
        cursor.execute("""
            SELECT tablename, policyname 
            FROM pg_policies 
            WHERE tablename LIKE '%workflow%'
            ORDER BY tablename, policyname
        """)
        
        policies = cursor.fetchall()
        
        print(f"\n✅ Created {len(policies)} RLS policies:")
        policy_count = {}
        for table, policy in policies:
            policy_count[table] = policy_count.get(table, 0) + 1
        
        for table, count in policy_count.items():
            print(f"   • {table}: {count} policies")
        
        # Check seed data
        print("\n📊 Verifying seed data...")
        
        cursor.execute("SELECT COUNT(*) FROM workflow_node_library WHERE user_id IS NULL")
        system_nodes = cursor.fetchone()[0]
        
        print(f"\n✅ Seeded {system_nodes} system nodes in node library")
        
        # List system nodes
        cursor.execute("""
            SELECT name, node_type, category 
            FROM workflow_node_library 
            WHERE user_id IS NULL
            ORDER BY node_type, name
        """)
        
        nodes = cursor.fetchall()
        print("\n   System Nodes:")
        for name, node_type, category in nodes:
            print(f"   • {name} ({node_type}) - {category}")
        
        # Close connection
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("🎉 Migration Complete!")
        print("=" * 60)
        print("\n✅ Next Steps:")
        print("   1. Test tools: python -c \"from tools.registry_v3 import RegistryV3; r = RegistryV3(); print([t for t in r.tools if 'automation_workflow' in t])\"")
        print("   2. Restart Flask: BISTART")
        print("   3. Test workflow creation via UI")
        
    except psycopg2.Error as e:
        print(f"\n❌ Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    apply_migration()
