"""
OAuth Token Enhancement Migration
Adds essential columns for token management, refresh, multi-account support
Date: October 30, 2025
"""

import sqlite3
import os
from datetime import datetime
from pathlib import Path

# Database path - CORRECT: Use data/ai_infrastructure.db from project root
root_dir = Path(__file__).parent.parent  # Up to AI_agents root
DB_PATH = str(root_dir / 'data' / 'ai_infrastructure.db')

def create_backup():
    """Create backup before migration"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = DB_PATH.replace('.db', f'_backup_{timestamp}.db')
    
    import shutil
    shutil.copy2(DB_PATH, backup_path)
    print(f"Backup created: {backup_path}")
    return backup_path

def add_oauth_columns():
    """Add essential OAuth management columns to oauth_tokens table"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    columns_to_add = [
        # Token health
        ("is_valid", "BOOLEAN DEFAULT 1"),
        ("is_active", "BOOLEAN DEFAULT 1"),
        ("refresh_attempts", "INTEGER DEFAULT 0"),
        ("last_refresh_error", "TEXT"),
        ("auto_refresh_enabled", "BOOLEAN DEFAULT 1"),
        
        # Multi-account support
        ("account_identifier", "TEXT"),  # email@example.com
        ("account_name", "TEXT"),  # "Work Account"
        ("is_primary_account", "BOOLEAN DEFAULT 0"),
        
        # Enhanced scope tracking
        ("granted_scopes", "TEXT"),  # What user actually approved
        ("issued_at", "TIMESTAMP"),
        
        # Security & audit
        ("revoked_at", "TIMESTAMP"),
        ("ip_address_granted", "TEXT"),
    ]
    
    print("\n🔧 Adding OAuth enhancement columns...")
    
    for column_name, column_def in columns_to_add:
        try:
            cursor.execute(f"ALTER TABLE oauth_tokens ADD COLUMN {column_name} {column_def}")
            print(f"  Added column: {column_name}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(f"  ⏭️  Column already exists: {column_name}")
            else:
                print(f"   Error adding {column_name}: {e}")
                raise
    
    conn.commit()
    conn.close()
    print("All OAuth columns added successfully")

def initialize_new_columns():
    """Set default values for existing records"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("\n🔄 Initializing new columns for existing records...")
    
    # Set all existing tokens as valid and active
    cursor.execute("""
        UPDATE oauth_tokens 
        SET is_valid = 1, 
            is_active = 1,
            refresh_attempts = 0,
            auto_refresh_enabled = 1,
            is_primary_account = 0
        WHERE is_valid IS NULL
    """)
    
    # Set issued_at to created_at for existing tokens
    cursor.execute("""
        UPDATE oauth_tokens 
        SET issued_at = created_at 
        WHERE issued_at IS NULL AND created_at IS NOT NULL
    """)
    
    # Copy scope to granted_scopes for existing tokens
    cursor.execute("""
        UPDATE oauth_tokens 
        SET granted_scopes = scope 
        WHERE granted_scopes IS NULL AND scope IS NOT NULL
    """)
    
    rows_updated = cursor.rowcount
    conn.commit()
    conn.close()
    
    print(f"Initialized {rows_updated} existing token records")

def verify_schema():
    """Verify new columns were added correctly"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("\n🔍 Verifying oauth_tokens schema...")
    
    cursor.execute("PRAGMA table_info(oauth_tokens)")
    columns = cursor.fetchall()
    
    expected_new_columns = [
        'is_valid', 'is_active', 'refresh_attempts', 'last_refresh_error',
        'auto_refresh_enabled', 'account_identifier', 'account_name',
        'is_primary_account', 'granted_scopes', 'issued_at', 'revoked_at',
        'ip_address_granted'
    ]
    
    column_names = [col[1] for col in columns]
    
    print(f"\n📊 Total columns: {len(columns)}")
    print("\nNew OAuth management columns:")
    for col_name in expected_new_columns:
        if col_name in column_names:
            print(f"  {col_name}")
        else:
            print(f"   MISSING: {col_name}")
    
    # Count tokens with new fields initialized
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN is_valid = 1 THEN 1 ELSE 0 END) as valid_tokens,
            SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) as active_tokens,
            SUM(CASE WHEN auto_refresh_enabled = 1 THEN 1 ELSE 0 END) as auto_refresh
        FROM oauth_tokens
    """)
    
    stats = cursor.fetchone()
    print(f"\n📈 Token Statistics:")
    print(f"  Total tokens: {stats[0]}")
    print(f"  Valid tokens: {stats[1]}")
    print(f"  Active tokens: {stats[2]}")
    print(f"  Auto-refresh enabled: {stats[3]}")
    
    conn.close()

def show_sample_tokens():
    """Show sample of enhanced token records"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("\n📋 Sample Token Records (Enhanced):")
    
    cursor.execute("""
        SELECT 
            id, user_id, platform, 
            is_valid, is_active, refresh_attempts,
            account_identifier, is_primary_account
        FROM oauth_tokens
        LIMIT 3
    """)
    
    tokens = cursor.fetchall()
    
    for token in tokens:
        print(f"\n  Token ID: {token[0]}")
        print(f"    User: {token[1]}")
        print(f"    Platform: {token[2]}")
        print(f"    Valid: {token[3]}")
        print(f"    Active: {token[4]}")
        print(f"    Refresh Attempts: {token[5]}")
        print(f"    Account: {token[6] or 'Not set'}")
        print(f"    Primary: {token[7]}")
    
    conn.close()

def main():
    """Run complete OAuth enhancement migration"""
    
    print("=" * 60)
    print("OAUTH TOKEN ENHANCEMENT MIGRATION")
    print("=" * 60)
    
    try:
        # Step 1: Create backup
        backup_path = create_backup()
        
        # Step 2: Add new columns
        add_oauth_columns()
        
        # Step 3: Initialize existing records
        initialize_new_columns()
        
        # Step 4: Verify schema
        verify_schema()
        
        # Step 5: Show sample data
        show_sample_tokens()
        
        print("\n" + "=" * 60)
        print("MIGRATION COMPLETE!")
        print("=" * 60)
        print("\n📝 Next Steps:")
        print("  1. Create oauth_config.py with client credentials")
        print("  2. Implement OAuthTokenRefresher class")
        print("  3. Update credential_fetcher.py to use new columns")
        print("  4. Test token refresh functionality")
        print("\n💾 Backup saved at:", backup_path)
        
    except Exception as e:
        print(f"\n ERROR: {e}")
        print("\n⚠️  Migration failed! Database backup available.")
        raise

if __name__ == '__main__':
    main()
