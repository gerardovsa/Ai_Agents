"""
Add Production Log System to Kanban Analytics

Creates comprehensive production log table with:
- Automatic stage transition logging
- Manual user entries (notes, wastage, delays)
- Client notification tracking
- Full edit history
"""

import sqlite3
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def get_db_path():
    """Get path to kanban analytics database"""
    return Path(__file__).parent.parent.parent / 'data' / 'kanban_analytics.db'

def get_schema_path():
    """Get path to production log schema"""
    return Path(__file__).parent.parent.parent / 'data' / 'production_log_schema.sql'

def create_production_log_table():
    """Create production log table and related views"""
    db_path = get_db_path()
    schema_path = get_schema_path()
    
    if not db_path.exists():
        print(f"Error: Database not found at {db_path}")
        print("Run setup_kanban_analytics.py first")
        return False
    
    if not schema_path.exists():
        print(f"Error: Schema file not found at {schema_path}")
        return False
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        print("Reading schema file...")
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        print("Creating production_log table...")
        # Execute schema (handles CREATE IF NOT EXISTS)
        cursor.executescript(schema_sql)
        
        conn.commit()
        
        # Verify table was created
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='production_log'
        """)
        
        if cursor.fetchone():
            print("[OK] production_log table created successfully")
        else:
            print("[FAIL] Table creation failed")
            return False
        
        # Check columns
        cursor.execute("PRAGMA table_info(production_log)")
        columns = cursor.fetchall()
        print(f"\n[OK] Table has {len(columns)} columns:")
        
        key_columns = [
            'log_id', 'ticket_id', 'log_date', 'log_time', 'user_initials',
            'entry_type', 'note_text', 'notification_type', 'notification_recipient'
        ]
        
        existing_cols = [col[1] for col in columns]
        for col in key_columns:
            status = "[OK]" if col in existing_cols else "[MISSING]"
            print(f"  {status} {col}")
        
        # Check views
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='view' AND name LIKE 'production_log%'
        """)
        views = cursor.fetchall()
        print(f"\n[OK] Created {len(views)} views:")
        for view in views:
            print(f"  - {view[0]}")
        
        conn.close()
        return True
        
    except Exception as e:
        conn.rollback()
        conn.close()
        print(f"\n[ERROR] Failed to create table: {e}")
        import traceback
        traceback.print_exc()
        return False

def populate_historical_stage_transitions():
    """
    Populate production log with historical stage transitions
    from stage_transitions table
    """
    db_path = get_db_path()
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        print("\n\nPopulating historical stage transitions...")
        
        # Get existing stage transitions
        cursor.execute("""
            SELECT 
                st.ticket_id,
                st.from_stage_id,
                st.to_stage_id,
                js_from.stage_description as from_stage_name,
                js_to.stage_description as to_stage_name,
                st.transition_date,
                st.business_hours,
                st.total_hours
            FROM stage_transitions st
            LEFT JOIN job_stages js_from ON st.from_stage_id = js_from.stage_id
            JOIN job_stages js_to ON st.to_stage_id = js_to.stage_id
            ORDER BY st.transition_date
        """)
        
        transitions = cursor.fetchall()
        print(f"Found {len(transitions)} stage transitions to migrate")
        
        migrated = 0
        for trans in transitions:
            ticket_id, from_stage_id, to_stage_id, from_stage_name, to_stage_name, transition_date, biz_hrs, total_hrs = trans
            
            # Check if already migrated
            cursor.execute("""
                SELECT COUNT(*) FROM production_log
                WHERE ticket_id = ? 
                AND entry_type = 'stage_change'
                AND log_date = ?
                AND to_stage_id = ?
            """, (ticket_id, transition_date, to_stage_id))
            
            if cursor.fetchone()[0] > 0:
                continue  # Skip if already exists
            
            # Insert into production log
            cursor.execute("""
                INSERT INTO production_log (
                    ticket_id,
                    log_date,
                    log_time,
                    user_initials,
                    entry_type,
                    from_stage_id,
                    to_stage_id,
                    from_stage_name,
                    to_stage_name,
                    note_text
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ticket_id,
                transition_date,
                transition_date.split('T')[1][:8] if 'T' in transition_date else '00:00:00',
                'AUTO',  # System-generated
                'stage_change',
                from_stage_id,
                to_stage_id,
                from_stage_name or 'Start',
                to_stage_name,
                f"Auto-migrated: {biz_hrs:.1f}h work ({total_hrs:.1f}h total)"
            ))
            migrated += 1
        
        conn.commit()
        print(f"[OK] Migrated {migrated} stage transitions to production log")
        
        # Show sample
        print("\nSample production log entries:")
        cursor.execute("""
            SELECT 
                ticket_id,
                log_date,
                log_time,
                user_initials,
                entry_type,
                COALESCE(from_stage_name, 'Start') || ' → ' || to_stage_name as transition
            FROM production_log
            WHERE entry_type = 'stage_change'
            ORDER BY log_date DESC
            LIMIT 5
        """)
        
        print("\nTicket | Date       | Time     | Init | Type         | Transition")
        print("-" * 80)
        for row in cursor.fetchall():
            print(f"{row[0]:6d} | {row[1][:10]:10s} | {row[2]:8s} | {row[3]:4s} | {row[4]:12s} | {row[5]}")
        
        conn.close()
        return True
        
    except Exception as e:
        conn.rollback()
        conn.close()
        print(f"\n[ERROR] Failed to populate historical data: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_test_entries():
    """Create sample production log entries for testing"""
    db_path = get_db_path()
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        print("\n\nCreating test entries...")
        
        # Get a test ticket
        cursor.execute("SELECT ticket_id FROM job_tickets LIMIT 1")
        result = cursor.fetchone()
        if not result:
            print("No jobs found for test entries")
            return False
        
        ticket_id = result[0]
        
        # Test entries
        test_entries = [
            # Manual note
            {
                'ticket_id': ticket_id,
                'user_initials': 'JD',
                'entry_type': 'note',
                'note_text': 'Client requested color adjustment - updating files'
            },
            # Wastage entry
            {
                'ticket_id': ticket_id,
                'user_initials': 'SM',
                'entry_type': 'wastage',
                'wastage_amount': 50,
                'wastage_unit': 'sheets',
                'wastage_type': 'paper',
                'wastage_reason': 'Color calibration test prints',
                'note_text': 'Wastage: 50 sheets for color calibration'
            },
            # Delay entry
            {
                'ticket_id': ticket_id,
                'user_initials': 'TK',
                'entry_type': 'delay',
                'delay_hours': 2.5,
                'delay_reason': 'equipment_failure',
                'note_text': 'Press 2 maintenance - 2.5 hour delay'
            },
            # Client notification
            {
                'ticket_id': ticket_id,
                'user_initials': 'JD',
                'entry_type': 'client_notification',
                'notification_type': 'email',
                'notification_recipient': 'client@example.com',
                'notification_subject': 'Your print job is ready for review',
                'notification_message': 'Hi, your business cards are ready. Please review and approve.',
                'notification_status': 'sent',
                'notification_sent_at': '2025-11-07T14:30:00',
                'note_text': 'Sent proof approval email to client'
            }
        ]
        
        for entry in test_entries:
            cols = ', '.join(entry.keys())
            placeholders = ', '.join('?' * len(entry))
            values = tuple(entry.values())
            
            cursor.execute(f"""
                INSERT INTO production_log ({cols})
                VALUES ({placeholders})
            """, values)
        
        conn.commit()
        print(f"[OK] Created {len(test_entries)} test entries")
        
        # Show results
        cursor.execute("""
            SELECT 
                log_date,
                log_time,
                user_initials,
                entry_type,
                note_text
            FROM production_log
            WHERE ticket_id = ?
            ORDER BY log_date DESC, log_time DESC
        """, (ticket_id,))
        
        print(f"\nProduction log for Ticket {ticket_id}:")
        print("Date       | Time     | Init | Type                 | Entry")
        print("-" * 90)
        for row in cursor.fetchall():
            print(f"{row[0][:10]:10s} | {row[1]:8s} | {row[2]:4s} | {row[3]:20s} | {row[4][:40]}")
        
        conn.close()
        return True
        
    except Exception as e:
        conn.rollback()
        conn.close()
        print(f"\n[ERROR] Failed to create test entries: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=" * 80)
    print("PRODUCTION LOG SYSTEM SETUP")
    print("=" * 80)
    print()
    
    # Step 1: Create table
    if not create_production_log_table():
        print("\n[FAIL] Table creation failed")
        sys.exit(1)
    
    # Step 2: Populate historical data
    if not populate_historical_stage_transitions():
        print("\n[FAIL] Historical data population failed")
        sys.exit(1)
    
    # Step 3: Create test entries
    if not create_test_entries():
        print("\n[WARN] Test entry creation failed (not critical)")
    
    print("\n" + "=" * 80)
    print("SETUP COMPLETE")
    print("=" * 80)
    print("\nNext steps:")
    print("  1. Create API endpoints for production log CRUD operations")
    print("  2. Update sync engine to auto-log stage changes")
    print("  3. Add production log UI to job details modal")
    print("  4. Implement client notification system")
    print("=" * 80)
    
    sys.exit(0)
