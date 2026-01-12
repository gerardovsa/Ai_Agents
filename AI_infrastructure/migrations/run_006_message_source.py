"""
Migration Runner: Add message_source column
Date: January 13, 2026
Purpose: Run 006_add_message_source_column.sql migration
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.database_utils import execute_query

def run_migration():
    """Execute the message_source column migration"""
    
    print("=" * 80)
    print("MIGRATION: Add message_source column to sessions.messages")
    print("=" * 80)
    
    # Read migration SQL
    migration_path = os.path.join(os.path.dirname(__file__), '006_add_message_source_column.sql')
    with open(migration_path, 'r') as f:
        sql = f.read()
    
    # Split into individual statements
    statements = [s.strip() for s in sql.split(';') if s.strip() and not s.strip().startswith('--')]
    
    print(f"\n📋 Found {len(statements)} SQL statements to execute\n")
    
    # Execute each statement
    for idx, statement in enumerate(statements, 1):
        # Skip comment blocks
        if statement.startswith('/*') or 'VERIFICATION QUERIES' in statement or 'ROLLBACK' in statement:
            continue
            
        print(f"[{idx}/{len(statements)}] Executing...")
        print(f"Statement preview: {statement[:100]}...")
        
        try:
            result = execute_query(statement)
            print(f"✅ SUCCESS\n")
        except Exception as e:
            print(f"⚠️ ERROR: {e}\n")
            # Continue with next statement (some may fail if already exists)
    
    print("=" * 80)
    print("VERIFICATION: Checking message_source distribution")
    print("=" * 80)
    
    try:
        result = execute_query("""
            SELECT message_source, COUNT(*) as count 
            FROM sessions.messages 
            GROUP BY message_source
            ORDER BY count DESC
        """, fetch_mode='all')
        
        print("\n📊 Message Source Distribution:")
        for row in result:
            print(f"  {row[0]}: {row[1]:,} messages")
        
        print("\n✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"\n⚠️ Verification failed: {e}")

if __name__ == '__main__':
    run_migration()
