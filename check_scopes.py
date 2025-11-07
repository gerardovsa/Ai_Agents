"""
Check Microsoft token scopes and permissions
"""

import sqlite3
import json
from pathlib import Path

db_path = Path(__file__).parent / 'data' / 'ai_infrastructure.db'
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

print('\n=== Microsoft Token Scopes ===\n')

cursor.execute('''
    SELECT 
        scope, granted_scopes, metadata
    FROM oauth_tokens
    WHERE user_id = 9 AND platform = 'microsoft'
''')

row = cursor.fetchone()

if row:
    scope, granted_scopes, metadata = row
    
    print('Requested scopes:')
    if scope:
        for s in scope.split():
            print(f'  - {s}')
    else:
        print('  (none)')
    
    print('\nGranted scopes:')
    if granted_scopes:
        for s in granted_scopes.split():
            print(f'  - {s}')
    else:
        print('  (none)')
    
    if metadata:
        try:
            meta = json.loads(metadata)
            print('\nMetadata:')
            for k, v in meta.items():
                if k == 'profile':
                    print(f'  {k}: {type(v).__name__} (profile data)')
                else:
                    print(f'  {k}: {v}')
        except:
            print(f'\nMetadata: {metadata}')
    
    # Check required scopes for tools
    print('\n=== Required Scopes for Tools ===\n')
    
    required_scopes = {
        'Files.ReadWrite.All': 'Word/Excel document creation',
        'Mail.Send': 'Outlook email sending',
        'Mail.ReadWrite': 'Outlook email management',
        'User.Read': 'User profile access',
        'offline_access': 'Token refresh'
    }
    
    granted_set = set(granted_scopes.split()) if granted_scopes else set()
    
    for scope_name, purpose in required_scopes.items():
        if scope_name in granted_set:
            print(f'✅ {scope_name:<25} - {purpose}')
        else:
            print(f'❌ {scope_name:<25} - {purpose} (MISSING!)')
    
    # Check if Files.ReadWrite.All is present
    if 'Files.ReadWrite.All' not in granted_set:
        print('\n❌ MISSING CRITICAL SCOPE!')
        print('   Files.ReadWrite.All is required for:')
        print('   - microsoft_word_create_document')
        print('   - microsoft_excel_create_workbook')
        print('   - OneDrive file operations')
        print('\n✅ Solution: Re-authenticate with correct scopes')
        print('   Visit: http://localhost:5001/api/auth/microsoft/login')

conn.close()
print()
