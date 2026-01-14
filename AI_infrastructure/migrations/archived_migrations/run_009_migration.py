"""
Migration 009: Rename 'prime' location to 'unassigned'
Run this script to update the database schema and data
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.database_utils import execute_query

def run_migration():
    try:
        print("🔄 Starting migration...")
        
        # Check current state
        print("\n📊 Current thread location distribution:")
        rows = execute_query("SELECT location, COUNT(*) as count FROM sessions.threads GROUP BY location ORDER BY count DESC", fetch_mode='all')
        if rows:
            for row in rows:
                print(f"  {row['location']}: {row['count']}")
        else:
            print("  No threads found")
        
        # Drop old constraint
        print("\n🔧 Dropping old constraint...")
        execute_query("ALTER TABLE sessions.threads DROP CONSTRAINT IF EXISTS chk_location_valid", fetch_mode=None)
        
        # Add new constraint
        print("🔧 Adding new constraint with 'unassigned'...")
        execute_query("""
            ALTER TABLE sessions.threads 
            ADD CONSTRAINT chk_location_valid 
            CHECK (
                location IN (
                    'unassigned',
                    'prime',
                    'prime-loaded',
                    'agent-1', 'agent-2', 'agent-3', 'agent-4', 'agent-5',
                    'agent-6', 'agent-7', 'agent-8', 'agent-9', 'agent-10',
                    'agent-11', 'agent-12', 'agent-13', 'agent-14', 'agent-15',
                    'agent-16', 'agent-17', 'agent-18', 'agent-19', 'agent-20',
                    'agent-21', 'agent-22', 'agent-23', 'agent-24', 'agent-25',
                    'agent-26', 'synergy'
                )
            )
        """, fetch_mode=None)
        
        # Update threads table
        print("📝 Updating sessions.threads: 'prime' → 'unassigned'...")
        execute_query("""
            UPDATE sessions.threads 
            SET location = 'unassigned', updated_at = CURRENT_TIMESTAMP
            WHERE location = 'prime'
        """, fetch_mode=None)
        print(f"  ✅ Updated threads")
        
        # Verify results
        print("\n✅ New thread location distribution:")
        rows = execute_query("SELECT location, COUNT(*) as count FROM sessions.threads GROUP BY location ORDER BY count DESC", fetch_mode='all')
        if rows:
            for row in rows:
                print(f"  {row['location']}: {row['count']}")
        
        print("\n🎉 Migration completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        raise

if __name__ == '__main__':
    run_migration()
