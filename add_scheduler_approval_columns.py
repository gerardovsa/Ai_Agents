"""
Add missing approval and status columns to scheduled_tasks table

Current columns in Supabase:
- is_active (boolean) - currently used
- Missing: enabled, approval_status, requires_approval, status, description

Strategy: Use is_active as the enabled flag, add new columns for approval workflow
"""

import os
import sys

# Add AI_infrastructure to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'AI_infrastructure'))

from shared.database_utils import get_database_connection

def add_missing_columns():
    """Add missing columns to scheduled_tasks table"""
    
    print("\n" + "="*60)
    print("Adding missing columns to ai_infrastructure.scheduled_tasks")
    print("="*60)
    
    conn = get_database_connection('ai_infrastructure')
    cursor = conn.cursor()
    
    # Columns to add
    columns_to_add = [
        ("requires_approval", "BOOLEAN DEFAULT FALSE"),
        ("approval_status", "TEXT DEFAULT 'approved'"),  # Default to approved so existing tasks run
        ("status", "TEXT DEFAULT 'active'"),
        ("description", "TEXT"),
    ]
    
    for col_name, col_def in columns_to_add:
        try:
            print(f"\nAdding column: {col_name}")
            cursor.execute(f"""
                ALTER TABLE ai_infrastructure.scheduled_tasks 
                ADD COLUMN IF NOT EXISTS {col_name} {col_def}
            """)
            conn.commit()
            print(f"  ✅ {col_name} added")
        except Exception as e:
            print(f"  ⚠️  Error adding {col_name}: {e}")
            conn.rollback()
    
    # Verify columns were added
    print("\n" + "-"*60)
    print("Verifying columns:")
    print("-"*60)
    
    cursor.execute("""
        SELECT column_name, data_type, column_default
        FROM information_schema.columns
        WHERE table_schema = 'ai_infrastructure'
        AND table_name = 'scheduled_tasks'
        AND column_name IN ('requires_approval', 'approval_status', 'status', 'description', 'is_active')
        ORDER BY column_name
    """)
    
    results = cursor.fetchall()
    
    for row in results:
        if isinstance(row, dict):
            col_name = row['column_name']
            data_type = row['data_type']
            default = row['column_default']
        else:
            col_name, data_type, default = row
        print(f"  ✅ {col_name:25} {data_type:15} Default: {default}")
    
    conn.close()
    print("\n" + "="*60)
    print("✅ All approval columns added successfully")
    print("="*60 + "\n")

if __name__ == '__main__':
    add_missing_columns()
