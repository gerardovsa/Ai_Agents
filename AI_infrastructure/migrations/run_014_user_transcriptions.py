"""
Migration Runner: Create user_transcriptions table
Created: December 23, 2025

Purpose: Add table for storing STT/TTS transcription history
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.database_utils import execute_query

def run_migration():
    """Run the user_transcriptions table creation migration"""
    
    print("=" * 60)
    print("MIGRATION: Create user_transcriptions table")
    print("=" * 60)
    
    migration_file = os.path.join(os.path.dirname(__file__), '014_create_user_transcriptions_table.sql')
    
    try:
        with open(migration_file, 'r', encoding='utf-8') as f:
            sql = f.read()
        
        print("\n📄 Executing migration SQL...")
        
        # Execute the migration (DDL doesn't return results, so specify fetch_mode=None)
        execute_query(sql, fetch_mode=None)
        
        print("\n✅ Migration completed successfully!")
        
        # Verify table exists
        print("\n🔍 Verifying table creation...")
        result = execute_query(
            """
            SELECT table_name, column_name, data_type 
            FROM information_schema.columns 
            WHERE table_schema = 'ai_infrastructure' 
              AND table_name = 'user_transcriptions'
            ORDER BY ordinal_position
            """,
            fetch_mode='all'
        )
        
        if result:
            print(f"\n✅ Table created with {len(result)} columns:")
            for row in result:
                # Handle both tuple and dict results
                if isinstance(row, dict):
                    print(f"   - {row['column_name']}: {row['data_type']}")
                else:
                    print(f"   - {row[1]}: {row[2]}")
        else:
            print("\n⚠️  Table not found (may need to check schema)")
        
        # Check indexes
        print("\n🔍 Verifying indexes...")
        indexes = execute_query(
            """
            SELECT indexname, indexdef 
            FROM pg_indexes 
            WHERE schemaname = 'ai_infrastructure' 
              AND tablename = 'user_transcriptions'
            """,
            fetch_mode='all'
        )
        
        if indexes:
            print(f"\n✅ {len(indexes)} indexes created:")
            for idx in indexes:
                if isinstance(idx, dict):
                    print(f"   - {idx['indexname']}")
                else:
                    print(f"   - {idx[0]}")
        
        print("\n" + "=" * 60)
        print("✅ MIGRATION COMPLETE")
        print("=" * 60)
        
    except FileNotFoundError:
        print(f"\n❌ Migration file not found: {migration_file}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    run_migration()
