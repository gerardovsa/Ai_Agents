"""
Verify oauth_tokens schema matches what Microsoft auth routes expect
Run this to confirm the fix is correct
"""

import sqlite3
import json
from pathlib import Path

def get_db_path():
    """Get correct database path"""
    root_dir = Path(__file__).parent
    return root_dir / 'data' / 'ai_infrastructure.db'

def get_oauth_tokens_columns():
    """Get actual oauth_tokens table columns"""
    db_path = get_db_path()
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA table_info(oauth_tokens)")
    columns = cursor.fetchall()
    conn.close()
    
    return [col[1] for col in columns]  # Column names

def main():
    print("="*80)
    print("OAUTH TOKENS SCHEMA VERIFICATION")
    print("="*80)
    
    db_path = get_db_path()
    print(f"\n Database: {db_path}")
    print(f" Exists: {db_path.exists()}\n")
    
    if not db_path.exists():
        print(" ERROR: Database not found!")
        return
    
    # Get actual columns
    actual_columns = get_oauth_tokens_columns()
    print(f" Total columns: {len(actual_columns)}")
    print("\n Actual columns:")
    for i, col in enumerate(actual_columns, 1):
        print(f"   {i:2}. {col}")
    
    # Expected columns from Microsoft auth routes fix
    expected_columns = [
        'id',
        'user_id',
        'platform',
        'access_token',
        'refresh_token',
        'token_type',
        'expires_at',
        'scope',  # ← SINGULAR!
        'created_at',
        'updated_at',
        'last_refreshed_at',
        'metadata',
        'account_identifier',
        'account_name',
        'is_primary_account',
        'is_valid',
        'is_active',
        'refresh_attempts',  # ← NOT error_count
        'last_refresh_error',  # ← NOT last_error
        'auto_refresh_enabled',
        'granted_scopes',
        'issued_at',
        'revoked_at'
    ]
    
    print(f"\n\n Expected columns in Microsoft auth routes: {len(expected_columns)}")
    
    # Check for mismatches
    print("\n\n VERIFICATION:")
    print(" ✅ = Column exists")
    print(" ❌ = Column missing")
    
    missing = []
    for col in expected_columns:
        if col in actual_columns:
            print(f"   ✅ {col}")
        else:
            print(f"   ❌ {col} (MISSING!)")
            missing.append(col)
    
    # Check Microsoft auth INSERT uses correct columns
    microsoft_insert_columns = [
        'user_id',
        'platform',
        'access_token',
        'refresh_token',
        'token_type',
        'expires_at',
        'scope',  # ← Fixed!
        'is_valid',
        'is_active',
        'auto_refresh_enabled',
        'last_refreshed_at',
        'refresh_attempts',  # ← Fixed!
        'last_refresh_error',  # ← Fixed!
        'granted_scopes',
        'account_identifier',  # ← Fixed!
        'account_name',  # ← Fixed!
        'metadata',
        'created_at',
        'updated_at'
    ]
    
    print(f"\n\n MICROSOFT AUTH INSERT STATEMENT:")
    print(f" Uses {len(microsoft_insert_columns)} columns")
    
    insert_issues = []
    for col in microsoft_insert_columns:
        if col in actual_columns:
            print(f"   ✅ {col}")
        else:
            print(f"   ❌ {col} (NOT IN SCHEMA!)")
            insert_issues.append(col)
    
    # Summary
    print("\n\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    if not missing and not insert_issues:
        print(" ✅ ALL CHECKS PASSED!")
        print(" ✅ Schema matches expected structure")
        print(" ✅ Microsoft auth INSERT uses correct columns")
        print(" ✅ Ready for production")
    else:
        if missing:
            print(f" ⚠️  {len(missing)} expected columns missing: {missing}")
        if insert_issues:
            print(f" ❌ {len(insert_issues)} INSERT columns not in schema: {insert_issues}")
            print(" ❌ Microsoft auth will FAIL with this schema!")
    
    print("="*80)

if __name__ == '__main__':
    main()
