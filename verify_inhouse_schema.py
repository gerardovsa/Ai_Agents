#!/usr/bin/env python3
"""Verify actual InHouse database schema for JobTickets table."""

import sys
import os

# Add inhouse-print directory to path
inhouse_dir = os.path.join(os.path.dirname(__file__), 'UI', 'modules_external', 'inhouse-print')
sys.path.insert(0, inhouse_dir)

from db_connector import InHousePrintDB

def check_job_tickets_schema():
    """Query actual JobTickets columns."""
    print("=" * 70)
    print("VERIFYING JOBTICKTS ACTUAL SCHEMA")
    print("=" * 70)
    
    db = InHousePrintDB()
    
    # Get actual column names
    query = """
    SELECT TOP 1 * FROM JobTickets
    """
    
    try:
        result = db.execute_query(query)
        
        if result is not None and len(result) > 0:
            columns = list(result.columns)
            print(f"\n✅ JobTickets has {len(columns)} columns:")
            print()
            
            # Check specific columns mentioned in guide
            check_columns = ['PrintType', 'ColourStatus', 'TicketNotes', 'QTY', 'Cost', 'TicketID', 'OrderID']
            
            for col in check_columns:
                if col in columns:
                    print(f"  ✅ {col} - EXISTS")
                else:
                    print(f"  ❌ {col} - NOT FOUND (guide is WRONG!)")
            
            print(f"\n📋 ALL ACTUAL COLUMNS:")
            for i, col in enumerate(columns, 1):
                print(f"  {i:2d}. {col}")
                
        else:
            print("❌ No data returned")
            
    except Exception as e:
        print(f"❌ Query failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    check_job_tickets_schema()
