"""
Check actual Supabase schema to identify correct column names
"""

import sys
sys.path.insert(0, 'AI_infrastructure')
from shared.database_utils import get_database_connection

print('='*80)
print('SUPABASE SCHEMA INSPECTION')
print('='*80)
print()

# Check users table schema
print('-'*80)
print('TABLE: ai_infrastructure.users')
print('-'*80)
try:
    conn = get_database_connection('ai_infrastructure')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'ai_infrastructure'
        AND table_name = 'users'
        ORDER BY ordinal_position
    """)
    
    columns = cursor.fetchall()
    print(f'Found {len(columns)} columns:')
    for col in columns:
        print(f'  - {col[0]:30} {col[1]:20} (nullable: {col[2]})')
    
    # Get sample row
    print()
    print('Sample row:')
    cursor.execute("SELECT * FROM ai_infrastructure.users LIMIT 1")
    row = cursor.fetchone()
    if row:
        col_names = [desc[0] for desc in cursor.description]
        for i, (name, value) in enumerate(zip(col_names, row)):
            print(f'  {name}: {value}')
    else:
        print('  No data found')
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()

print()

# Check threads table schema
print('-'*80)
print('TABLE: sessions.threads')
print('-'*80)
try:
    conn = get_database_connection('sessions')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'sessions'
        AND table_name = 'threads'
        ORDER BY ordinal_position
    """)
    
    columns = cursor.fetchall()
    print(f'Found {len(columns)} columns:')
    for col in columns:
        print(f'  - {col[0]:30} {col[1]:20} (nullable: {col[2]})')
    
    # Get sample row
    print()
    print('Sample row:')
    cursor.execute("SELECT * FROM sessions.threads LIMIT 1")
    row = cursor.fetchone()
    if row:
        col_names = [desc[0] for desc in cursor.description]
        for i, (name, value) in enumerate(zip(col_names, row)):
            val_str = str(value)[:50] if value else 'NULL'
            print(f'  {name}: {val_str}')
    else:
        print('  No data found')
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()

print()

# Check oauth_tokens table schema
print('-'*80)
print('TABLE: ai_infrastructure.oauth_tokens')
print('-'*80)
try:
    conn = get_database_connection('ai_infrastructure')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'ai_infrastructure'
        AND table_name = 'oauth_tokens'
        ORDER BY ordinal_position
    """)
    
    columns = cursor.fetchall()
    print(f'Found {len(columns)} columns:')
    for col in columns:
        print(f'  - {col[0]:30} {col[1]:20} (nullable: {col[2]})')
    
    # Get sample row
    print()
    print('Sample row:')
    cursor.execute("SELECT * FROM ai_infrastructure.oauth_tokens LIMIT 1")
    row = cursor.fetchone()
    if row:
        col_names = [desc[0] for desc in cursor.description]
        for i, (name, value) in enumerate(zip(col_names, row)):
            val_str = str(value)[:50] if value else 'NULL'
            print(f'  {name}: {val_str}')
    else:
        print('  No data found')
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()

print()

# Check messages table schema
print('-'*80)
print('TABLE: sessions.messages')
print('-'*80)
try:
    conn = get_database_connection('sessions')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'sessions'
        AND table_name = 'messages'
        ORDER BY ordinal_position
    """)
    
    columns = cursor.fetchall()
    print(f'Found {len(columns)} columns:')
    for col in columns:
        print(f'  - {col[0]:30} {col[1]:20} (nullable: {col[2]})')
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()

print()
print('='*80)
print('SCHEMA INSPECTION COMPLETE')
print('='*80)
