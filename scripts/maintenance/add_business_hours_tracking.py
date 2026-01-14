"""
Add Business Hours Tracking to Kanban Analytics
from shared.database_utils import convert_sql_placeholders

Adds two new columns to stage_transitions:
- business_hours: Time in business hours only (Mon-Fri 8am-6pm)
- total_hours: Total elapsed time (calendar hours)

Business hours definition:
- Monday-Friday: 8:00 AM - 6:00 PM (10 hours/day)
- Weekends excluded
- Nights excluded (6 PM - 8 AM)
- Holidays excluded (future enhancement)
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def get_db_path():
    """Get path to kanban analytics database"""
    return Path(__file__).parent.parent.parent / 'data' / 'kanban_analytics.db'

def calculate_business_hours(start_dt, end_dt, debug=False):
    """
    Calculate business hours between two datetimes
    
    Business hours: Mon-Fri 8:00 AM - 6:00 PM (10 hours/day)
    Excludes: Weekends, nights
    
    Args:
        start_dt: Start datetime
        end_dt: End datetime
        debug: Print debug output
        
    Returns:
        float: Business hours between dates
    """
    if start_dt >= end_dt:
        return 0.0
    
    business_hours = 0.0
    current = start_dt
    
    # Define business hours
    BUSINESS_START = 8  # 8 AM
    BUSINESS_END = 18   # 6 PM
    
    if debug:
        print(f"\nDEBUG: Calculating from {start_dt} to {end_dt}")
    
    while current < end_dt:
        # Get current day's business hours
        current_day_start = current.replace(hour=BUSINESS_START, minute=0, second=0, microsecond=0)
        current_day_end = current.replace(hour=BUSINESS_END, minute=0, second=0, microsecond=0)
        
        # Skip weekends (0=Monday, 6=Sunday)
        if current.weekday() >= 5:  # Saturday or Sunday
            current = (current + timedelta(days=1)).replace(hour=BUSINESS_START, minute=0, second=0, microsecond=0)
            continue
        
        # If before business hours, jump to start of business day
        if current < current_day_start:
            current = current_day_start
        
        # If after business hours for this day, move to next day
        if current >= current_day_end:
            current = (current + timedelta(days=1)).replace(hour=BUSINESS_START, minute=0, second=0, microsecond=0)
            continue
        
        # Calculate hours for this business day segment
        # End is either end of business day or the target end_dt, whichever is earlier
        segment_end = min(end_dt, current_day_end)
        
        if segment_end > current:
            segment_hours = (segment_end - current).total_seconds() / 3600
            business_hours += segment_hours
            if debug:
                print(f"  Day {current.date()}: {current.strftime('%H:%M')} to {segment_end.strftime('%H:%M')} = {segment_hours:.2f}h")
        
        # Move to next day's business start
        current = (current + timedelta(days=1)).replace(hour=BUSINESS_START, minute=0, second=0, microsecond=0)
    
    return round(business_hours, 2)

def add_columns_to_database():
    """Add business_hours and total_hours columns to stage_transitions"""
    db_path = get_db_path()
    
    if not db_path.exists():
        print(f"Error: Database not found at {db_path}")
        print("Run setup_kanban_analytics.py first")
        return False
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(stage_transitions)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'business_hours' in columns and 'total_hours' in columns:
            print("Columns already exist. Updating values...")
        else:
            print("Adding new columns...")
            
            # Add business_hours column
            if 'business_hours' not in columns:
                cursor.execute("""
                    ALTER TABLE stage_transitions 
                    ADD COLUMN business_hours REAL DEFAULT 0.0
                """)
                print("  - Added business_hours column")
            
            # Add total_hours column
            if 'total_hours' not in columns:
                cursor.execute("""
                    ALTER TABLE stage_transitions 
                    ADD COLUMN total_hours REAL DEFAULT 0.0
                """)
                print("  - Added total_hours column")
            
            conn.commit()
        
        # Update existing records
        print("\nRecalculating hours for existing transitions...")
        
        cursor.execute("""
            SELECT transition_id, transition_date
            FROM stage_transitions
            ORDER BY ticket_id, transition_id
        """)
        transitions = cursor.fetchall()
        
        print(f"Found {len(transitions)} transitions to process")
        
        # Group by ticket to calculate stage durations
        cursor.execute("""
            SELECT 
                t1.transition_id,
                t1.ticket_id,
                t1.transition_date as entry_date,
                t2.transition_date as exit_date
            FROM stage_transitions t1
            LEFT JOIN stage_transitions t2 
                ON t1.ticket_id = t2.ticket_id 
                AND t2.transition_id = (
                    SELECT MIN(transition_id) 
                    FROM stage_transitions 
                    WHERE ticket_id = t1.ticket_id 
                    AND transition_id > t1.transition_id
                )
            ORDER BY t1.ticket_id, t1.transition_id
        """)
        
        updates = []
        for row in cursor.fetchall():
            transition_id, ticket_id, entry_date_str, exit_date_str = row
            
            if not exit_date_str:
                # Still in this stage - calculate from entry to now
                exit_date_str = datetime.now().isoformat()
            
            try:
                entry_date = datetime.fromisoformat(entry_date_str)
                exit_date = datetime.fromisoformat(exit_date_str)
                
                # Calculate total hours
                total_hours = (exit_date - entry_date).total_seconds() / 3600
                
                # Calculate business hours
                business_hours = calculate_business_hours(entry_date, exit_date)
                
                updates.append((business_hours, total_hours, transition_id))
                
            except Exception as e:
                print(f"  Warning: Could not parse dates for transition {transition_id}: {e}")
                continue
        
        # Batch update
        if updates:
            cursor.executemany("""
                UPDATE stage_transitions 
                SET business_hours = ?, total_hours = ?
                WHERE transition_id = ?
            """, updates)
            
            conn.commit()
            print(f"Updated {len(updates)} transitions with business/total hours")
        
        # Show sample results
        print("\nSample results:")
        cursor.execute("""
            SELECT 
                ticket_id,
                transition_date,
                business_hours,
                total_hours,
                ROUND((business_hours * 1.0 / NULLIF(total_hours, 0)) * 100, 1) as efficiency_pct
            FROM stage_transitions
            WHERE business_hours > 0
            ORDER BY transition_id DESC
            LIMIT 5
        """)
        
        print("\nTicket | Entry Date          | Business Hrs | Total Hrs | Efficiency %")
        print("-" * 75)
        for row in cursor.fetchall():
            ticket_id, trans_date, biz_hrs, total_hrs, efficiency = row
            print(f"{ticket_id:6d} | {trans_date[:19]:19s} | {biz_hrs:11.1f} | {total_hrs:9.1f} | {efficiency or 0:11.1f}%")
        
        conn.close()
        print("\n✅ Migration complete!")
        return True
        
    except Exception as e:
        conn.rollback()
        conn.close()
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_business_hours_calculation():
    """Test the business hours calculation"""
    print("\n=== Testing Business Hours Calculation ===\n")
    
    test_cases = [
        # Case 1: Same business day
        (
            datetime(2025, 11, 7, 9, 0),   # Thursday 9 AM
            datetime(2025, 11, 7, 11, 0),  # Thursday 11 AM
            2.0,  # Expected: 2 hours
            "Same business day (Thu 9am-11am)"
        ),
        # Case 2: Overnight (excludes night)
        (
            datetime(2025, 11, 6, 16, 0),  # Thursday 4 PM
            datetime(2025, 11, 7, 10, 0),  # Friday 10 AM
            4.0,  # Expected: 2 hours Thu (4pm-6pm) + 2 hours Fri (8am-10am) = 4 hours
            "Overnight (Thu 4pm to Fri 10am)"
        ),
        # Case 3: Over weekend
        (
            datetime(2025, 11, 7, 16, 0),  # Friday 4 PM
            datetime(2025, 11, 10, 10, 0), # Monday 10 AM
            4.0,  # Expected: 2 hours Fri + 0 weekend + 2 hours Mon = 4 hours
            "Over weekend (Fri 4pm to Mon 10am)"
        ),
        # Case 4: Full business week
        (
            datetime(2025, 11, 3, 8, 0),   # Monday 8 AM
            datetime(2025, 11, 7, 18, 0),  # Friday 6 PM
            50.0,  # Expected: 5 days * 10 hours = 50 hours
            "Full business week (Mon-Fri)"
        ),
        # Case 5: Before business hours
        (
            datetime(2025, 11, 7, 6, 0),   # Thursday 6 AM
            datetime(2025, 11, 7, 12, 0),  # Thursday 12 PM
            4.0,  # Expected: 8am-12pm = 4 hours
            "Starting before business hours (6am-12pm)"
        ),
    ]
    
    all_passed = True
    for start, end, expected, description in test_cases:
        result = calculate_business_hours(start, end, debug=False)
        passed = abs(result - expected) < 0.1
        status = "[PASS]" if passed else "[FAIL]"
        if not passed:
            all_passed = False
            # Re-run with debug for failed cases
            print(f"{status} | {description}")
            print(f"       Expected: {expected:.1f}h, Got: {result:.1f}h")
            calculate_business_hours(start, end, debug=True)
        else:
            print(f"{status} | {description}")
            print(f"       Expected: {expected:.1f}h, Got: {result:.1f}h")
    
    return all_passed

if __name__ == '__main__':
    print("=" * 75)
    print("Kanban Analytics: Add Business Hours Tracking")
    print("=" * 75)
    
    # Run tests first
    if test_business_hours_calculation():
        print("\nAll tests passed!\n")
    else:
        print("\nSome tests failed!\n")
        sys.exit(1)
    
    # Run migration
    success = add_columns_to_database()
    
    if success:
        print("\n" + "=" * 75)
        print("Next steps:")
        print("  1. Update sync engine to calculate business hours on new transitions")
        print("  2. Update API to return both business_hours and total_hours")
        print("  3. Update frontend to display both metrics")
        print("=" * 75)
    
    sys.exit(0 if success else 1)
