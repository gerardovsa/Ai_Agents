"""
Check columns in ai_infrastructure.scheduled_tasks table
"""

import os
import sys

# Add AI_infrastructure to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'AI_infrastructure'))

from shared.database_utils import get_database_connection

def check_scheduled_tasks_columns():
    """Check what columns exist in scheduled_tasks table"""
    
    print("\n" + "="*60)
    print("Checking ai_infrastructure.scheduled_tasks columns")
    print("="*60)
    
    conn = get_database_connection('ai_infrastructure')
    cursor = conn.cursor()
    
    # Query information_schema for column details
    cursor.execute("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_schema = 'ai_infrastructure'
        AND table_name = 'scheduled_tasks'
        ORDER BY ordinal_position
    """)
    
    columns = cursor.fetchall()
    
    if columns:
        print(f"\nFound {len(columns)} columns in ai_infrastructure.scheduled_tasks:\n")
        column_names = []
        for col in columns:
            # Handle both dict and tuple results
            if isinstance(col, dict):
                col_name = col['column_name']
                data_type = col['data_type']
                nullable = col['is_nullable']
                default = col['column_default']
            else:
                col_name, data_type, nullable, default = col
            
            column_names.append(col_name)
            print(f"  - {col_name:30} {data_type:15} NULL: {nullable:3} Default: {default}")
    else:
        print("\n❌ No columns found - table might not exist")
        column_names = []
    
    # Check if specific columns exist
    print("\n" + "-"*60)
    print("Checking for expected columns:")
    print("-"*60)
    
    expected_columns = [
        'id', 'task_name', 'task_type', 'schedule_pattern', 
        'task_config', 'created_at', 'updated_at', 'last_run',
        'next_run', 'status', 'enabled', 'approval_status',
        'user_id', 'description'
    ]
    
    for col in expected_columns:
        if col in column_names:
            print(f"  ✅ {col:30} EXISTS")
        else:
            print(f"  ❌ {col:30} MISSING")
    
    conn.close()
    print("\n" + "="*60 + "\n")

if __name__ == '__main__':
    check_scheduled_tasks_columns()
