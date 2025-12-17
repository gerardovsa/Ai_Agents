"""
Run migration: Add team_id column to sessions.threads table
Date: 2025-12-17
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.database_utils import get_database_connection

def run_migration():
    """Run the team_id threads migration"""
    print("\n" + "="*80)
    print("MIGRATION: Add team_id to sessions.threads")
    print("="*80 + "\n")
    
    migration_file = os.path.join(os.path.dirname(__file__), 'add_team_id_to_threads.sql')
    
    if not os.path.exists(migration_file):
        print(f"❌ Migration file not found: {migration_file}")
        return False
    
    # Read SQL file
    with open(migration_file, 'r', encoding='utf-8') as f:
        sql = f.read()
    
    try:
        conn = get_database_connection('sessions')
        cursor = conn.cursor()
        
        print("Running migration SQL...")
        cursor.execute(sql)
        conn.commit()
        
        print("✅ Migration completed successfully!")
        
        # Verification
        print("\nVerification:")
        cursor.execute("""
            SELECT 
                COUNT(*) as total_threads,
                COUNT(team_id) as threads_with_team_id,
                COUNT(DISTINCT team_id) as unique_team_ids
            FROM sessions.threads
        """)
        
        result = cursor.fetchone()
        if result:
            if isinstance(result, dict):
                total = result['total_threads']
                with_team = result['threads_with_team_id']
                unique = result['unique_team_ids']
            else:
                total, with_team, unique = result
                
            print(f"  Total threads: {total}")
            print(f"  Threads with Team ID: {with_team}")
            print(f"  Unique Team IDs: {unique}")
            
            if total > 0 and with_team > 0:
                print(f"\n  Team ID coverage: {(with_team/total*100):.1f}%")
                
                # Show sample Team IDs
                cursor.execute("""
                    SELECT team_id, COUNT(*) as thread_count
                    FROM sessions.threads
                    WHERE team_id IS NOT NULL
                    GROUP BY team_id
                    ORDER BY thread_count DESC
                    LIMIT 5
                """)
                
                print("\n  Top 5 Team IDs by thread count:")
                for row in cursor.fetchall():
                    if isinstance(row, dict):
                        team_id = row['team_id']
                        count = row['thread_count']
                    else:
                        team_id, count = row
                    print(f"    - {team_id}: {count} threads")
        
        cursor.close()
        conn.close()
        
        print("\n" + "="*80)
        print("MIGRATION COMPLETE")
        print("="*80 + "\n")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = run_migration()
    sys.exit(0 if success else 1)
