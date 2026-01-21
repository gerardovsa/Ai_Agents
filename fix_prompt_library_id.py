"""
Quick fix for prompt_library ID auto-increment
Uses database_utils connection with autocommit
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'AI_infrastructure'))

from shared.database_utils import get_database_connection

print("\n" + "="*80)
print("FIX: prompt_library ID Auto-Increment")
print("="*80 + "\n")

try:
    # Get connection using database_utils (handles Supabase properly)
    conn = get_database_connection('ai_infrastructure')
    conn.autocommit = True  # Important for DO blocks and CREATE SEQUENCE
    cursor = conn.cursor()
    
    print("Step 1: Creating sequence...")
    cursor.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_sequences 
                WHERE schemaname = 'ai_infrastructure' 
                AND sequencename = 'prompt_library_id_seq'
            ) THEN
                CREATE SEQUENCE ai_infrastructure.prompt_library_id_seq;
                RAISE NOTICE 'Created sequence';
            ELSE
                RAISE NOTICE 'Sequence exists';
            END IF;
        END
        $$
    """)
    print("✅ Sequence ready\n")
    
    print("Step 2: Setting sequence ownership...")
    cursor.execute("""
        ALTER SEQUENCE ai_infrastructure.prompt_library_id_seq 
        OWNED BY ai_infrastructure.prompt_library.id
    """)
    print("✅ Ownership set\n")
    
    print("Step 3: Setting sequence value...")
    cursor.execute("""
        SELECT setval(
            'ai_infrastructure.prompt_library_id_seq', 
            COALESCE((SELECT MAX(id) FROM ai_infrastructure.prompt_library), 0) + 1,
            false
        ) as new_val
    """)
    result = cursor.fetchone()
    seq_val = result[0] if isinstance(result, tuple) else result['new_val']
    print(f"✅ Sequence value set to: {seq_val}\n")
    
    print("Step 4: Setting default value for id column...")
    cursor.execute("""
        ALTER TABLE ai_infrastructure.prompt_library 
        ALTER COLUMN id SET DEFAULT nextval('ai_infrastructure.prompt_library_id_seq')
    """)
    print("✅ Default value set\n")
    
    # Verify
    print("Verification:")
    print("-" * 80)
    
    cursor.execute("""
        SELECT column_default
        FROM information_schema.columns
        WHERE table_schema = 'ai_infrastructure'
        AND table_name = 'prompt_library'
        AND column_name = 'id'
    """)
    result = cursor.fetchone()
    default = result[0] if isinstance(result, tuple) else result['column_default']
    print(f"✅ ID column default: {default}")
    
    cursor.execute("SELECT last_value FROM ai_infrastructure.prompt_library_id_seq")
    result = cursor.fetchone()
    last_val = result[0] if isinstance(result, tuple) else result['last_value']
    print(f"✅ Sequence current value: {last_val}")
    print(f"✅ Next ID will be: {last_val + 1}\n")
    
    # Test INSERT
    print("Testing INSERT...")
    cursor.execute("""
        INSERT INTO ai_infrastructure.prompt_library
        (user_id, name, category, prompt_text, visibility, created_at, updated_at)
        VALUES (1, 'Test Auto-Increment', 'Test', 'Test prompt', 'private', NOW(), NOW())
        RETURNING id
    """)
    result = cursor.fetchone()
    test_id = result[0] if isinstance(result, tuple) else result['id']
    print(f"✅ Test INSERT successful! Generated ID: {test_id}")
    
    # Cleanup
    cursor.execute("DELETE FROM ai_infrastructure.prompt_library WHERE id = %s", (test_id,))
    print(f"✅ Cleaned up test record\n")
    
    print("="*80)
    print("✅ FIX COMPLETE - Prompt library save will now work!")
    print("="*80 + "\n")
    
    cursor.close()
    conn.close()

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
