"""Fix users table id column to auto-increment

This script creates a sequence for the users.id column and sets it as the default.
"""
import sys
sys.path.insert(0, 'AI_infrastructure')

from shared.database_utils import get_database_connection

conn = get_database_connection('ai_infrastructure')
cursor = conn.cursor()

try:
    print("Creating sequence for users.id...")
    
    # Check if sequence already exists
    cursor.execute("""
        SELECT 1 FROM pg_sequences 
        WHERE schemaname = 'ai_infrastructure' 
        AND sequencename = 'users_id_seq'
    """)
    
    if cursor.fetchone():
        print("Sequence already exists, dropping it first...")
        cursor.execute('DROP SEQUENCE IF EXISTS ai_infrastructure.users_id_seq CASCADE')
        conn.commit()
    
    # Get the current max id
    cursor.execute('SELECT COALESCE(MAX(id), 0) FROM ai_infrastructure.users')
    max_id = cursor.fetchone()['coalesce']
    print(f"Current max ID: {max_id}")
    
    # Create sequence starting from max_id + 1
    cursor.execute(f'''
        CREATE SEQUENCE ai_infrastructure.users_id_seq
        START WITH {max_id + 1}
        INCREMENT BY 1
        NO MINVALUE
        NO MAXVALUE
        CACHE 1
    ''')
    conn.commit()
    print(f"Created sequence starting at {max_id + 1}")
    
    # Set the sequence as the default for the id column
    cursor.execute('''
        ALTER TABLE ai_infrastructure.users 
        ALTER COLUMN id SET DEFAULT nextval('ai_infrastructure.users_id_seq'::regclass)
    ''')
    conn.commit()
    print("Set sequence as default for id column")
    
    # Associate the sequence with the column (for proper ownership)
    cursor.execute('''
        ALTER SEQUENCE ai_infrastructure.users_id_seq 
        OWNED BY ai_infrastructure.users.id
    ''')
    conn.commit()
    print("Associated sequence with users.id column")
    
    # Verify the fix
    cursor.execute("""
        SELECT column_default 
        FROM information_schema.columns 
        WHERE table_schema = 'ai_infrastructure' 
        AND table_name = 'users' 
        AND column_name = 'id'
    """)
    default = cursor.fetchone()['column_default']
    print(f"\nVerification - id column default: {default}")
    
    # Test insert
    print("\nTesting insert with auto-generated ID...")
    cursor.execute('''
        INSERT INTO ai_infrastructure.users (username, email, password_hash, role) 
        VALUES (%s, %s, %s, %s)
        RETURNING id
    ''', ('test_autoincrement', 'test_auto@example.com', 'oauth_google', 'user'))
    
    new_id = cursor.fetchone()['id']
    print(f"SUCCESS! Auto-generated ID: {new_id}")
    
    # Clean up test user
    cursor.execute('DELETE FROM ai_infrastructure.users WHERE id = %s', (new_id,))
    conn.commit()
    print("Cleaned up test user")
    
    print("\n" + "="*80)
    print("MIGRATION COMPLETE!")
    print("="*80)
    
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
    conn.rollback()
finally:
    conn.close()
