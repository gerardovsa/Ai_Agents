"""
Run migration 013: Fix prompt_library ID auto-increment
Date: January 21, 2026
"""
import sys
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.database_utils import execute_query

def run_migration():
    """Execute the prompt_library ID fix migration"""
    
    print("\n" + "="*80)
    print("MIGRATION 013: Fix prompt_library ID Auto-Increment")
    print("="*80 + "\n")
    
    # Read migration SQL
    migration_file = Path(__file__).parent / '013_fix_prompt_library_id_sequence.sql'
    with open(migration_file, 'r', encoding='utf-8') as f:
        migration_sql = f.read()
    
    try:
        print("Executing migration SQL...")
        print("-" * 80)
        
        # Execute each statement separately
        statements = [
            # Step 1: Create sequence
            """
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_sequences 
                    WHERE schemaname = 'ai_infrastructure' 
                    AND sequencename = 'prompt_library_id_seq'
                ) THEN
                    CREATE SEQUENCE ai_infrastructure.prompt_library_id_seq;
                    RAISE NOTICE 'Created sequence: ai_infrastructure.prompt_library_id_seq';
                ELSE
                    RAISE NOTICE 'Sequence already exists: ai_infrastructure.prompt_library_id_seq';
                END IF;
            END
            $$
            """,
            # Step 2: Set sequence ownership
            """
            ALTER SEQUENCE ai_infrastructure.prompt_library_id_seq 
            OWNED BY ai_infrastructure.prompt_library.id
            """,
            # Step 3: Set sequence value
            """
            SELECT setval(
                'ai_infrastructure.prompt_library_id_seq', 
                COALESCE((SELECT MAX(id) FROM ai_infrastructure.prompt_library), 0) + 1,
                false
            )
            """,
            # Step 4: Set default value
            """
            ALTER TABLE ai_infrastructure.prompt_library 
            ALTER COLUMN id SET DEFAULT nextval('ai_infrastructure.prompt_library_id_seq')
            """
        ]
        
        for i, stmt in enumerate(statements, 1):
            print(f"\nStep {i}...")
            execute_query(stmt)
            print(f"✅ Step {i} complete")
        
        print("\n" + "-" * 80)
        print("✅ Migration completed successfully!\n")
        
        # Verify the fix
        print("Verification:")
        print("-" * 80)
        
        # Check column default
        result = execute_query(
            """
            SELECT column_default
            FROM information_schema.columns
            WHERE table_schema = 'ai_infrastructure'
            AND table_name = 'prompt_library'
            AND column_name = 'id'
            """,
            fetch_mode='one'
        )
        
        print(f"✅ ID column default: {result['column_default']}")
        
        # Check sequence value
        seq_val = execute_query(
            "SELECT last_value FROM ai_infrastructure.prompt_library_id_seq",
            fetch_mode='one'
        )
        
        print(f"✅ Sequence current value: {seq_val['last_value']}")
        print(f"✅ Next ID will be: {seq_val['last_value'] + 1}")
        
        # Test INSERT
        print("\nTesting INSERT...")
        test_result = execute_query(
            """
            INSERT INTO ai_infrastructure.prompt_library
            (user_id, name, category, prompt_text, visibility, created_at, updated_at)
            VALUES (1, 'Test Auto-Increment', 'Test', 'Test prompt', 'private', NOW(), NOW())
            RETURNING id
            """,
            fetch_mode='one'
        )
        
        print(f"✅ Test INSERT successful! Generated ID: {test_result['id']}")
        
        # Cleanup test record
        execute_query(
            "DELETE FROM ai_infrastructure.prompt_library WHERE id = %s",
            (test_result['id'],)
        )
        print(f"✅ Cleaned up test record (ID: {test_result['id']})")
        
        print("\n" + "="*80)
        print("✅ MIGRATION COMPLETE - Prompt library save will now work!")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == '__main__':
    success = run_migration()
    sys.exit(0 if success else 1)
