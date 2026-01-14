"""
Add priority column to Synergy milestones, tasks, and subtasks tables

This migration adds the missing 'priority' column that the frontend expects.
Priority values: 'low', 'medium', 'high', 'critical'
"""
import sys
sys.path.insert(0, 'AI_infrastructure')

from shared.database_utils import get_synergy_sessions_connection

def add_priority_columns():
    """Add priority column to milestones, tasks, and subtasks tables"""
    conn = get_synergy_sessions_connection()
    cursor = conn.cursor()
    
    try:
        print("Adding priority column to milestones table...")
        cursor.execute("""
            ALTER TABLE synergy_sessions.milestones 
            ADD COLUMN IF NOT EXISTS priority TEXT DEFAULT 'medium'
        """)
        print("✅ Added priority to milestones")
        
        print("\nAdding priority column to tasks table...")
        cursor.execute("""
            ALTER TABLE synergy_sessions.tasks 
            ADD COLUMN IF NOT EXISTS priority TEXT DEFAULT 'medium'
        """)
        print("✅ Added priority to tasks")
        
        print("\nAdding priority column to subtasks table...")
        cursor.execute("""
            ALTER TABLE synergy_sessions.subtasks 
            ADD COLUMN IF NOT EXISTS priority TEXT DEFAULT 'medium'
        """)
        print("✅ Added priority to subtasks")
        
        conn.commit()
        print("\n🎉 Migration completed successfully!")
        
        # Verify the columns were added
        print("\n" + "="*50)
        print("VERIFICATION")
        print("="*50)
        
        for table in ['milestones', 'tasks', 'subtasks']:
            cursor.execute(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_schema = 'synergy_sessions' 
                AND table_name = '{table}'
                AND column_name = 'priority'
            """)
            result = cursor.fetchone()
            if result:
                print(f"✅ {table}.priority column exists")
            else:
                print(f"❌ {table}.priority column NOT found")
        
    except Exception as e:
        print(f"\n❌ Error during migration: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    add_priority_columns()
