"""
Run migration 010: Remove 'prime-loaded' location value
Simplifies location to just: prime, agent-N, unassigned
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.database_utils import execute_query

def run_migration():
    """Execute migration 010"""
    print("🔄 Starting migration 010: Remove 'prime-loaded' location value")
    print("📋 Simplifying to 3 location types:")
    print("   - 'prime' = AI Prime sidebar")
    print("   - 'agent-N' = Command Center agent column")
    print("   - 'unassigned' = Not assigned\n")
    
    try:
        # Step 1: Check current state
        print("📊 Checking for prime-loaded threads...")
        count = execute_query(
            "SELECT COUNT(*) as count FROM sessions.threads WHERE location = 'prime-loaded'",
            fetch_mode='value'
        )
        print(f"   Found {count} threads with location='prime-loaded'\n")
        
        # Step 2: Update any remaining 'prime-loaded' threads to 'prime'
        if count > 0:
            print("🔧 Updating prime-loaded → prime...")
            execute_query(
                "UPDATE sessions.threads SET location = 'prime', updated_at = CURRENT_TIMESTAMP WHERE location = 'prime-loaded'",
                fetch_mode=None
            )
            print(f"   ✅ Updated {count} threads\n")
        
        # Step 3: Drop old constraint
        print("🔧 Dropping old location constraint...")
        execute_query(
            "ALTER TABLE sessions.threads DROP CONSTRAINT IF EXISTS chk_location_valid",
            fetch_mode=None
        )
        print("   ✅ Old constraint dropped\n")
        
        # Step 4: Create new constraint WITHOUT 'prime-loaded'
        print("🔧 Creating new constraint without prime-loaded...")
        execute_query("""
            ALTER TABLE sessions.threads ADD CONSTRAINT chk_location_valid CHECK (
              location = ANY (ARRAY[
                'unassigned'::text, 'prime'::text,
                'agent-1'::text, 'agent-2'::text, 'agent-3'::text, 'agent-4'::text, 'agent-5'::text,
                'agent-6'::text, 'agent-7'::text, 'agent-8'::text, 'agent-9'::text, 'agent-10'::text,
                'agent-11'::text, 'agent-12'::text, 'agent-13'::text, 'agent-14'::text, 'agent-15'::text,
                'agent-16'::text, 'agent-17'::text, 'agent-18'::text, 'agent-19'::text, 'agent-20'::text,
                'agent-21'::text, 'agent-22'::text, 'agent-23'::text, 'agent-24'::text, 'agent-25'::text,
                'agent-26'::text, 'synergy'::text
              ])
            )
        """, fetch_mode=None)
        print("   ✅ New constraint created\n")
        
        # Step 5: Verify no prime-loaded threads remain
        print("🔍 Verifying migration...")
        remaining = execute_query(
            "SELECT COUNT(*) as count FROM sessions.threads WHERE location = 'prime-loaded'",
            fetch_mode='value'
        )
        
        if remaining > 0:
            raise Exception(f"Migration failed: {remaining} threads still have location='prime-loaded'")
        
        print("✅ Migration 010 completed successfully")
        print("✅ Database constraint updated")
        print("✅ No 'prime-loaded' threads remain")
        print("✅ Valid locations: prime, agent-1 to agent-26, unassigned, synergy")
        return True
        
    except Exception as e:
        print(f"❌ Migration 010 failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = run_migration()
    sys.exit(0 if success else 1)
