"""
Quick script to check what tables exist in Supabase
"""

import os
import sys

# Set environment
os.environ['USE_SUPABASE'] = 'true'

# Add AI_infrastructure to path
sys.path.insert(0, 'AI_infrastructure')

from shared.database_utils import get_database_connection

try:
    conn = get_database_connection('ai_infrastructure')
    cursor = conn.cursor()
    
    # Get all tables in public schema
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)
    
    tables = cursor.fetchall()
    
    print(f"\n=== SUPABASE TABLES (public schema) ===")
    print(f"Total: {len(tables)} tables\n")
    
    for table in tables:
        table_name = table['table_name']
        
        # Get column count
        cursor.execute(f"""
            SELECT COUNT(*) as count
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = '{table_name}'
        """)
        col_count = cursor.fetchone()['count']
        
        print(f"  - {table_name} ({col_count} columns)")
    
    conn.close()
    print("\nConnection successful!")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
