"""
Fix Synergy Database Schema
============================
Adds missing columns to synergy_sessions and threads tables.

Run: python fix_synergy_database_schema.py
"""

import sqlite3
from pathlib import Path

ROOT_DIR = Path(__file__).parent
SYNERGY_DB = ROOT_DIR / 'data' / 'synergy_sessions.db'
SESSIONS_DB = ROOT_DIR / 'data' / 'sessions.db'

def fix_synergy_sessions_table():
    """Add column_position to synergy_sessions table"""
    print("\n[1] Fixing synergy_sessions table...")
    
    try:
        conn = sqlite3.connect(str(SYNERGY_DB))
        cursor = conn.cursor()
        
        # Check if column exists
        cursor.execute("PRAGMA table_info(synergy_sessions)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'column_position' in columns:
            print("  ✓ column_position already exists")
        else:
            print("  + Adding column_position...")
            cursor.execute('ALTER TABLE synergy_sessions ADD COLUMN column_position INTEGER DEFAULT 0')
            conn.commit()
            print("  ✓ column_position added successfully")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def fix_threads_table():
    """Add agent_id and message_count to threads table"""
    print("\n[2] Fixing threads table...")
    
    if not SESSIONS_DB.exists():
        print(f"  ! Threads database not found: {SESSIONS_DB}")
        return False
    
    try:
        conn = sqlite3.connect(str(SESSIONS_DB))
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='threads'")
        if not cursor.fetchone():
            print("  ! Threads table does not exist")
            conn.close()
            return False
        
        # Check existing columns
        cursor.execute("PRAGMA table_info(threads)")
        columns = [row[1] for row in cursor.fetchall()]
        
        # Add agent_id if missing
        if 'agent_id' in columns:
            print("  ✓ agent_id already exists")
        else:
            print("  + Adding agent_id...")
            cursor.execute('ALTER TABLE threads ADD COLUMN agent_id TEXT DEFAULT "prime"')
            conn.commit()
            print("  ✓ agent_id added successfully")
        
        # Add message_count if missing
        if 'message_count' in columns:
            print("  ✓ message_count already exists")
        else:
            print("  + Adding message_count...")
            cursor.execute('ALTER TABLE threads ADD COLUMN message_count INTEGER DEFAULT 0')
            conn.commit()
            print("  ✓ message_count added successfully")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def initialize_column_positions():
    """Set column_position for existing cards"""
    print("\n[3] Initializing column positions for existing cards...")
    
    try:
        conn = sqlite3.connect(str(SYNERGY_DB))
        cursor = conn.cursor()
        
        # Get all sessions grouped by column
        cursor.execute("""
            SELECT session_id, kanban_column 
            FROM synergy_sessions 
            ORDER BY kanban_column, created_at
        """)
        rows = cursor.fetchall()
        
        if not rows:
            print("  ! No sessions found")
            conn.close()
            return True
        
        # Group by column and assign positions
        columns = {}
        for session_id, kanban_column in rows:
            if kanban_column not in columns:
                columns[kanban_column] = []
            columns[kanban_column].append(session_id)
        
        # Update positions
        updated = 0
        for column_name, session_ids in columns.items():
            for position, session_id in enumerate(session_ids):
                cursor.execute("""
                    UPDATE synergy_sessions 
                    SET column_position = ? 
                    WHERE session_id = ?
                """, (position, session_id))
                updated += 1
        
        conn.commit()
        conn.close()
        
        print(f"  ✓ Initialized positions for {updated} cards across {len(columns)} columns")
        return True
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def verify_changes():
    """Verify all changes were applied"""
    print("\n[4] Verifying changes...")
    
    all_good = True
    
    # Check synergy_sessions
    try:
        conn = sqlite3.connect(str(SYNERGY_DB))
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(synergy_sessions)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'column_position' in columns:
            print("  ✓ synergy_sessions.column_position exists")
        else:
            print("  ✗ synergy_sessions.column_position MISSING")
            all_good = False
        
        conn.close()
    except Exception as e:
        print(f"  ✗ Error checking synergy_sessions: {e}")
        all_good = False
    
    # Check threads
    try:
        if SESSIONS_DB.exists():
            conn = sqlite3.connect(str(SESSIONS_DB))
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(threads)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if 'agent_id' in columns:
                print("  ✓ threads.agent_id exists")
            else:
                print("  ✗ threads.agent_id MISSING")
                all_good = False
            
            if 'message_count' in columns:
                print("  ✓ threads.message_count exists")
            else:
                print("  ✗ threads.message_count MISSING")
                all_good = False
            
            conn.close()
        else:
            print("  ! Threads database not found (skipping verification)")
    except Exception as e:
        print(f"  ✗ Error checking threads: {e}")
        all_good = False
    
    return all_good


if __name__ == '__main__':
    print("="*70)
    print("  SYNERGY DATABASE SCHEMA FIX")
    print("="*70)
    
    success = True
    success &= fix_synergy_sessions_table()
    success &= fix_threads_table()
    success &= initialize_column_positions()
    success &= verify_changes()
    
    print("\n" + "="*70)
    if success:
        print("  ✓ ALL FIXES APPLIED SUCCESSFULLY")
    else:
        print("  ✗ SOME FIXES FAILED - Check errors above")
    print("="*70 + "\n")
    
    exit(0 if success else 1)
