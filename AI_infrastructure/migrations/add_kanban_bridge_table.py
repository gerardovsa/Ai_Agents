"""
Add Kanban Bridge Table to AI Infrastructure
=============================================
Creates a bridge table to link AI agent tasks with Synergy Kanban board tasks

This enables:
- AI agents to work on tasks from the Kanban board
- Kanban tasks to be assigned to AI agents
- Bidirectional sync between systems
- Progress tracking across platforms

Usage:
    python migrations/add_kanban_bridge_table.py
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ai_infrastructure.db')

def run_migration():
    """Create kanban_task_links bridge table"""
    
    print(f"[INFO] Running Kanban Bridge migration on: {DB_PATH}")
    
    if not os.path.exists(DB_PATH):
        print(f"[ERROR] Database not found: {DB_PATH}")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Create bridge table
        print("[STEP 1] Creating kanban_task_links table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS kanban_task_links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                
                -- AI Infrastructure side
                agent_id TEXT NOT NULL,
                agent_name TEXT,
                work_session_id TEXT,  -- Links to agent_sessions if exists
                
                -- Synergy Kanban side
                kanban_session_id TEXT NOT NULL UNIQUE,  -- Links to synergy_sessions.db sessions table
                kanban_title TEXT,
                kanban_status TEXT,
                kanban_column TEXT,  -- backlog, in_progress, review, done
                
                -- Sync configuration
                sync_direction TEXT DEFAULT 'bidirectional' CHECK(sync_direction IN ('ai_to_kanban', 'kanban_to_ai', 'bidirectional')),
                auto_sync_enabled BOOLEAN DEFAULT 1 CHECK(auto_sync_enabled IN (0, 1)),
                
                -- Status tracking
                agent_work_status TEXT DEFAULT 'pending' CHECK(agent_work_status IN ('pending', 'in_progress', 'completed', 'failed', 'paused')),
                last_synced_at TEXT,
                sync_status TEXT DEFAULT 'active' CHECK(sync_status IN ('active', 'paused', 'completed', 'error')),
                
                -- Error handling
                last_error TEXT,
                retry_count INTEGER DEFAULT 0,
                
                -- Metadata
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                completed_at TEXT,
                
                -- Notes
                notes TEXT
            )
        ''')
        print("[OK] kanban_task_links table created")
        
        # Create indexes
        print("[STEP 2] Creating indexes...")
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_kanban_links_agent 
            ON kanban_task_links(agent_id)
        ''')
        print("[OK] Index on agent_id created")
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_kanban_links_session 
            ON kanban_task_links(kanban_session_id)
        ''')
        print("[OK] Index on kanban_session_id created")
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_kanban_links_status 
            ON kanban_task_links(sync_status)
        ''')
        print("[OK] Index on sync_status created")
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_kanban_links_agent_status 
            ON kanban_task_links(agent_id, agent_work_status)
        ''')
        print("[OK] Index on agent_id + agent_work_status created")
        
        # Create trigger for updated_at
        print("[STEP 3] Creating triggers...")
        cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS update_kanban_links_timestamp
            AFTER UPDATE ON kanban_task_links
            BEGIN
                UPDATE kanban_task_links 
                SET updated_at = datetime('now')
                WHERE id = NEW.id;
            END
        ''')
        print("[OK] Auto-update trigger created")
        
        # Create view for active agent tasks
        print("[STEP 4] Creating views...")
        cursor.execute('''
            CREATE VIEW IF NOT EXISTS v_active_agent_kanban_tasks AS
            SELECT 
                ktl.id,
                ktl.agent_id,
                ktl.agent_name,
                ktl.kanban_session_id,
                ktl.kanban_title,
                ktl.kanban_status,
                ktl.kanban_column,
                ktl.agent_work_status,
                ktl.sync_direction,
                ktl.last_synced_at,
                ktl.created_at
            FROM kanban_task_links ktl
            WHERE ktl.sync_status = 'active'
                AND ktl.agent_work_status NOT IN ('completed', 'failed')
            ORDER BY ktl.created_at DESC
        ''')
        print("[OK] v_active_agent_kanban_tasks view created")
        
        cursor.execute('''
            CREATE VIEW IF NOT EXISTS v_agent_kanban_summary AS
            SELECT 
                agent_id,
                agent_name,
                COUNT(*) as total_tasks,
                SUM(CASE WHEN agent_work_status = 'completed' THEN 1 ELSE 0 END) as completed_tasks,
                SUM(CASE WHEN agent_work_status = 'in_progress' THEN 1 ELSE 0 END) as active_tasks,
                SUM(CASE WHEN agent_work_status = 'failed' THEN 1 ELSE 0 END) as failed_tasks,
                MAX(last_synced_at) as last_activity
            FROM kanban_task_links
            WHERE sync_status = 'active'
            GROUP BY agent_id, agent_name
        ''')
        print("[OK] v_agent_kanban_summary view created")
        
        # Commit changes
        conn.commit()
        print("\n[SUCCESS] Migration completed successfully!")
        
        # Verify
        print("\n[VERIFY] Checking database schema...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='kanban_task_links'")
        if cursor.fetchone():
            print("[OK] kanban_task_links table exists")
        
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='index' AND tbl_name='kanban_task_links'")
        index_count = cursor.fetchone()[0]
        print(f"[OK] {index_count} indexes created")
        
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='view' AND name LIKE '%kanban%'")
        view_count = cursor.fetchone()[0]
        print(f"[OK] {view_count} views created")
        
        # Show table info
        print("\n[INFO] Table structure:")
        cursor.execute("PRAGMA table_info(kanban_task_links)")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  - {col[1]}: {col[2]}")
        
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"\n[ERROR] Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        conn.close()


if __name__ == '__main__':
    print("="*60)
    print("KANBAN BRIDGE TABLE MIGRATION")
    print("="*60)
    print(f"Database: {DB_PATH}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    success = run_migration()
    
    if success:
        print("\n" + "="*60)
        print("MIGRATION COMPLETE - Bridge table ready!")
        print("="*60)
        print("\nNext steps:")
        print("1. Test with: python test_kanban_bridge.py")
        print("2. Create AI agent → Kanban task link")
        print("3. Enable bidirectional sync")
    else:
        print("\n" + "="*60)
        print("MIGRATION FAILED - Please check errors above")
        print("="*60)
