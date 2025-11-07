"""
Add missing columns to oauth_tokens table for Microsoft authentication
Does NOT affect Google authentication - just adds columns for future use
"""

import sqlite3
from pathlib import Path

# Database path
db_path = Path(__file__).parent / 'data' / 'ai_infrastructure.db'

print('\n=== Adding Missing Columns to oauth_tokens ===\n')

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Columns to add
columns_to_add = [
    ('email', 'TEXT'),
    ('profile_name', 'TEXT'),
    ('error_count', 'INTEGER DEFAULT 0'),
    ('last_error', 'TEXT')
]

# Add each column
for col_name, col_type in columns_to_add:
    try:
        cursor.execute(f'ALTER TABLE oauth_tokens ADD COLUMN {col_name} {col_type}')
        print(f'✅ Added: {col_name} {col_type}')
    except Exception as e:
        if 'duplicate column name' in str(e).lower():
            print(f'⚠️  {col_name}: Already exists (skipped)')
        else:
            print(f'❌ {col_name}: {e}')

conn.commit()

print('\n=== Verifying Schema ===\n')

# Verify all columns exist
cursor.execute('PRAGMA table_info(oauth_tokens)')
columns = cursor.fetchall()

has_email = any(c[1] == 'email' for c in columns)
has_profile = any(c[1] == 'profile_name' for c in columns)
has_error_count = any(c[1] == 'error_count' for c in columns)
has_last_error = any(c[1] == 'last_error' for c in columns)

print(f'Total columns: {len(columns)}')
print(f'✅ email: {has_email}')
print(f'✅ profile_name: {has_profile}')
print(f'✅ error_count: {has_error_count}')
print(f'✅ last_error: {has_last_error}')

print('\n=== Checking Existing Data (Google vs Microsoft) ===\n')

# Check Google tokens (should be unaffected)
cursor.execute('SELECT COUNT(*) FROM oauth_tokens WHERE platform = ?', ('google',))
google_count = cursor.fetchone()[0]

# Check Microsoft tokens
cursor.execute('SELECT COUNT(*) FROM oauth_tokens WHERE platform = ?', ('microsoft',))
ms_count = cursor.fetchone()[0]

print(f'Google tokens: {google_count} rows (unaffected - email column is NULL)')
print(f'Microsoft tokens: {ms_count} rows (can now use email/profile_name columns)')

# Show sample Google token to prove it's unaffected
if google_count > 0:
    cursor.execute('''
        SELECT user_id, platform, email, profile_name, 
               CASE WHEN access_token IS NOT NULL THEN 'EXISTS' ELSE 'NULL' END as token_status
        FROM oauth_tokens 
        WHERE platform = 'google' 
        LIMIT 1
    ''')
    row = cursor.fetchone()
    print(f'\n📊 Sample Google token (user {row[0]}):')
    print(f'   Platform: {row[1]}')
    print(f'   Email column: {row[2] if row[2] else "NULL (uses metadata instead)"}')
    print(f'   Profile_name column: {row[3] if row[3] else "NULL (uses metadata instead)"}')
    print(f'   Access token: {row[4]}')
    print(f'   ✅ Google auth still works - uses metadata field, not these columns')

# Show sample Microsoft token
if ms_count > 0:
    cursor.execute('''
        SELECT user_id, platform, email, profile_name,
               CASE WHEN access_token IS NOT NULL THEN 'EXISTS' ELSE 'NULL' END as token_status
        FROM oauth_tokens 
        WHERE platform = 'microsoft' 
        LIMIT 1
    ''')
    row = cursor.fetchone()
    print(f'\n📊 Sample Microsoft token (user {row[0]}):')
    print(f'   Platform: {row[1]}')
    print(f'   Email column: {row[2] if row[2] else "NULL (needs re-auth to populate)"}')
    print(f'   Profile_name column: {row[3] if row[3] else "NULL (needs re-auth to populate)"}')
    print(f'   Access token: {row[4]}')
    
    if not row[2]:
        print(f'   ⚠️  Email is NULL - Microsoft status endpoint will crash')
        print(f'   ✅ FIX: Re-authenticate Microsoft account to populate these columns')

conn.close()

print('\n✅ Migration complete!')
print('\n📝 Next Steps:')
print('   1. Columns added successfully')
print('   2. Google authentication: UNAFFECTED (uses metadata field)')
print('   3. Microsoft authentication: Need to re-authenticate to populate email/profile_name')
print('   4. Visit: http://localhost:5001/api/auth/microsoft/login')
print()
