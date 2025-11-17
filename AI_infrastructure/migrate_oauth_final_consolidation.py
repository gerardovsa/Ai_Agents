"""
Final OAuth Consolidation Migration
- Adds 12 columns to oauth_tokens for complete OAuth management
- Migrates gmail addresses from user_gmail_accounts
- Archives old redundant tables
Date: October 30, 2025
"""

import sqlite3
import os
import shutil
from datetime import datetime
from pathlib import Path

# Database path - CORRECT: Use data/ai_infrastructure.db
root_dir = Path(__file__).parent.parent  # Up to AI_agents root
DB_PATH = str(root_dir / 'data' / 'ai_infrastructure.db')

def create_backup():
    """Create backup before migration"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = DB_PATH.replace('.db', f'_backup_final_{timestamp}.db')
    
    shutil.copy2(DB_PATH, backup_path)
    print(f"Backup created: {backup_path}")
    return backup_path

def add_oauth_enhancement_columns():
    """Add 12 essential OAuth management columns"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    columns_to_add = [
        # Multi-account support (from user_gmail_accounts)
        ("account_identifier", "TEXT"),  # email@example.com
        ("account_name", "TEXT"),  # "Work Account"
        ("is_primary_account", "BOOLEAN DEFAULT 0"),
        
        # Token health & status
        ("is_valid", "BOOLEAN DEFAULT 1"),
        ("is_active", "BOOLEAN DEFAULT 1"),
        ("refresh_attempts", "INTEGER DEFAULT 0"),
        ("last_refresh_error", "TEXT"),
        ("auto_refresh_enabled", "BOOLEAN DEFAULT 1"),
        
        # Enhanced OAuth tracking
        ("granted_scopes", "TEXT"),  # What user actually approved
        ("issued_at", "TIMESTAMP"),
        
        # Security & audit
        ("revoked_at", "TIMESTAMP"),
        ("ip_address_granted", "TEXT"),
    ]
    
    print("\n🔧 Adding OAuth enhancement columns to oauth_tokens...")
    
    added_count = 0
    for column_name, column_def in columns_to_add:
        try:
            cursor.execute(f"ALTER TABLE oauth_tokens ADD COLUMN {column_name} {column_def}")
            print(f"  Added: {column_name}")
            added_count += 1
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(f"  ⏭️  Already exists: {column_name}")
            else:
                print(f"   Error adding {column_name}: {e}")
                raise
    
    conn.commit()
    conn.close()
    print(f"Added {added_count} new columns")
    
    return added_count

def migrate_gmail_addresses():
    """Migrate gmail addresses from user_gmail_accounts to oauth_tokens"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("\n📧 Migrating Gmail addresses to oauth_tokens...")
    
    # Get all Gmail accounts
    cursor.execute("""
        SELECT user_id, gmail_address, display_name, is_primary
        FROM user_gmail_accounts
        ORDER BY user_id, is_primary DESC
    """)
    
    gmail_accounts = cursor.fetchall()
    
    if not gmail_accounts:
        print("  ⚠️  No Gmail accounts to migrate")
        conn.close()
        return 0
    
    migrated_count = 0
    
    for user_id, gmail_address, display_name, is_primary in gmail_accounts:
        # Update oauth_tokens for this user's Google platform
        cursor.execute("""
            UPDATE oauth_tokens
            SET account_identifier = %s, account_name = %s, is_primary_account = %s
            WHERE user_id = %s 
            AND platform = 'google'
            AND account_identifier IS NULL
        """, (gmail_address, display_name, is_primary, user_id))
        
        if cursor.rowcount > 0:
            print(f"  User {user_id}: {gmail_address} (primary={is_primary})")
            migrated_count += 1
    
    conn.commit()
    conn.close()
    
    print(f"Migrated {migrated_count} Gmail addresses")
    return migrated_count

def initialize_new_columns():
    """Set default values for existing oauth_tokens records"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("\n🔄 Initializing new columns for existing tokens...")
    
    # Set defaults for all existing tokens
    cursor.execute("""
        UPDATE oauth_tokens 
        SET is_valid = 1,
            is_active = 1,
            refresh_attempts = 0,
            auto_refresh_enabled = 1
        WHERE is_valid IS NULL
    """)
    
    # Set issued_at to created_at
    cursor.execute("""
        UPDATE oauth_tokens 
        SET issued_at = created_at 
        WHERE issued_at IS NULL AND created_at IS NOT NULL
    """)
    
    # Copy scope to granted_scopes
    cursor.execute("""
        UPDATE oauth_tokens 
        SET granted_scopes = scope 
        WHERE granted_scopes IS NULL AND scope IS NOT NULL
    """)
    
    rows_updated = cursor.rowcount
    conn.commit()
    conn.close()
    
    print(f"Initialized {rows_updated} token records")
    return rows_updated

def archive_old_tables():
    """Rename old tables with _ARCHIVED_ prefix"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("\n🗄️  Archiving old redundant tables...")
    
    tables_to_archive = [
        ('user_platform_credentials', 'Key-value OAuth storage (redundant)'),
        ('user_gmail_accounts', 'Gmail addresses (migrated to oauth_tokens)')
    ]
    
    archived_count = 0
    
    for table_name, reason in tables_to_archive:
        try:
            # Check if table exists
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
            if cursor.fetchone():
                # Check if already archived
                archived_name = f"_ARCHIVED_{table_name}"
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{archived_name}'")
                if cursor.fetchone():
                    # Already archived, drop old one
                    cursor.execute(f"DROP TABLE {archived_name}")
                
                # Rename to archived
                cursor.execute(f"ALTER TABLE {table_name} RENAME TO {archived_name}")
                print(f"  Archived: {table_name} → {archived_name}")
                print(f"     Reason: {reason}")
                archived_count += 1
            else:
                print(f"  ⏭️  Table doesn't exist: {table_name}")
        except sqlite3.OperationalError as e:
            print(f"  ⚠️  Error archiving {table_name}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"Archived {archived_count} tables")
    return archived_count

def verify_consolidation():
    """Verify the consolidated oauth_tokens table"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("\n🔍 Verifying OAuth consolidation...")
    
    # Check schema
    cursor.execute("PRAGMA table_info(oauth_tokens)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    
    print(f"\n📊 oauth_tokens schema: {len(columns)} columns")
    
    required_columns = [
        'id', 'user_id', 'platform',
        'access_token', 'refresh_token', 'token_type',
        'expires_at', 'scope', 'created_at', 'updated_at', 'last_refreshed_at',
        'metadata',
        # New columns
        'account_identifier', 'account_name', 'is_primary_account',
        'is_valid', 'is_active', 'refresh_attempts', 'last_refresh_error',
        'auto_refresh_enabled', 'granted_scopes', 'issued_at',
        'revoked_at', 'ip_address_granted'
    ]
    
    print("\nRequired columns:")
    for col in required_columns:
        if col in column_names:
            print(f"  {col}")
        else:
            print(f"   MISSING: {col}")
    
    # Count tokens
    cursor.execute("SELECT COUNT(*) FROM oauth_tokens")
    total_tokens = cursor.fetchone()[0]
    
    # Count by platform
    cursor.execute("""
        SELECT platform, COUNT(*) 
        FROM oauth_tokens 
        GROUP BY platform
    """)
    platform_counts = cursor.fetchall()
    
    print(f"\n📈 Token Statistics:")
    print(f"  Total tokens: {total_tokens}")
    for platform, count in platform_counts:
        print(f"  {platform}: {count} tokens")
    
    # Count tokens with gmail addresses
    cursor.execute("""
        SELECT COUNT(*) 
        FROM oauth_tokens 
        WHERE account_identifier IS NOT NULL
    """)
    with_email = cursor.fetchone()[0]
    
    print(f"\n📧 Multi-Account Support:")
    print(f"  Tokens with email: {with_email}/{total_tokens}")
    
    # Show sample token
    cursor.execute("""
        SELECT id, user_id, platform, account_identifier, is_primary_account,
               is_valid, is_active, auto_refresh_enabled
        FROM oauth_tokens
        WHERE account_identifier IS NOT NULL
        LIMIT 1
    """)
    
    sample = cursor.fetchone()
    if sample:
        print(f"\n📋 Sample Token (Enhanced):")
        print(f"  ID: {sample[0]}")
        print(f"  User: {sample[1]}")
        print(f"  Platform: {sample[2]}")
        print(f"  Email: {sample[3]}")
        print(f"  Primary: {sample[4]}")
        print(f"  Valid: {sample[5]}")
        print(f"  Active: {sample[6]}")
        print(f"  Auto-refresh: {sample[7]}")
    
    # Check archived tables
    cursor.execute("""
        SELECT name 
        FROM sqlite_master 
        WHERE type='table' 
        AND name LIKE '_ARCHIVED_%'
    """)
    
    archived_tables = cursor.fetchall()
    
    print(f"\n🗄️  Archived Tables:")
    if archived_tables:
        for table in archived_tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"  {table[0]}: {count} rows preserved")
    else:
        print("  ⚠️  No tables archived yet")
    
    conn.close()

def create_oauth_config():
    """Create OAuth configuration file template"""
    
    config_path = os.path.join(os.path.dirname(__file__), 'config', 'oauth_config.py')
    
    # Create config directory if doesn't exist
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    if os.path.exists(config_path):
        print(f"\n⏭️  oauth_config.py already exists: {config_path}")
        return
    
    config_content = '''"""
OAuth Provider Configuration
Client credentials and endpoints for OAuth authentication
"""

import os

OAUTH_PROVIDERS = {
    'google': {
        'client_id': os.getenv('GOOGLE_CLIENT_ID'),
        'client_secret': os.getenv('GOOGLE_CLIENT_SECRET'),
        'redirect_uri': 'http://localhost:5001/oauth/google/callback',
        'token_uri': 'https://oauth2.googleapis.com/token',
        'auth_uri': 'https://accounts.google.com/o/oauth2/v2/auth',
        'scopes': [
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.send',
            'https://www.googleapis.com/auth/drive.readonly',
            'https://www.googleapis.com/auth/calendar.readonly'
        ]
    },
    'microsoft': {
        'client_id': os.getenv('MICROSOFT_CLIENT_ID'),
        'client_secret': os.getenv('MICROSOFT_CLIENT_SECRET'),
        'tenant_id': os.getenv('MICROSOFT_TENANT_ID', 'common'),
        'redirect_uri': 'http://localhost:5001/oauth/microsoft/callback',
        'token_uri': 'https://login.microsoftonline.com/common/oauth2/v2.0/token',
        'auth_uri': 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize',
        'scopes': [
            'https://graph.microsoft.com/Mail.Read',
            'https://graph.microsoft.com/Mail.Send',
            'https://graph.microsoft.com/Files.Read.All',
            'https://graph.microsoft.com/Calendars.Read'
        ]
    },
    'microsoft365': {
        'client_id': os.getenv('MICROSOFT_CLIENT_ID'),
        'client_secret': os.getenv('MICROSOFT_CLIENT_SECRET'),
        'tenant_id': os.getenv('MICROSOFT_TENANT_ID', 'common'),
        'redirect_uri': 'http://localhost:5001/oauth/microsoft365/callback',
        'token_uri': 'https://login.microsoftonline.com/common/oauth2/v2.0/token',
        'auth_uri': 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize',
        'scopes': [
            'https://graph.microsoft.com/.default'
        ]
    }
}

def get_provider_config(platform):
    """Get OAuth configuration for a specific platform"""
    return OAUTH_PROVIDERS.get(platform)

def get_client_credentials(platform):
    """Get just client_id and client_secret for a platform"""
    config = OAUTH_PROVIDERS.get(platform)
    if config:
        return {
            'client_id': config['client_id'],
            'client_secret': config['client_secret']
        }
    return None
'''
    
    with open(config_path, 'w') as f:
        f.write(config_content)
    
    print(f"\nCreated oauth_config.py: {config_path}")
    print("   ⚠️  Remember to set environment variables:")
    print("      - GOOGLE_CLIENT_ID")
    print("      - GOOGLE_CLIENT_SECRET")
    print("      - MICROSOFT_CLIENT_ID")
    print("      - MICROSOFT_CLIENT_SECRET")

def main():
    """Run complete OAuth final consolidation"""
    
    print("=" * 60)
    print("OAUTH FINAL CONSOLIDATION MIGRATION")
    print("=" * 60)
    
    try:
        # Step 1: Backup
        backup_path = create_backup()
        
        # Step 2: Add columns
        columns_added = add_oauth_enhancement_columns()
        
        # Step 3: Initialize defaults
        rows_initialized = initialize_new_columns()
        
        # Step 4: Migrate Gmail addresses
        emails_migrated = migrate_gmail_addresses()
        
        # Step 5: Archive old tables
        tables_archived = archive_old_tables()
        
        # Step 6: Verify
        verify_consolidation()
        
        # Step 7: Create OAuth config
        create_oauth_config()
        
        print("\n" + "=" * 60)
        print("FINAL CONSOLIDATION COMPLETE!")
        print("=" * 60)
        
        print(f"\n📊 Migration Summary:")
        print(f"  Columns added: {columns_added}")
        print(f"  Rows initialized: {rows_initialized}")
        print(f"  Gmail addresses migrated: {emails_migrated}")
        print(f"  Tables archived: {tables_archived}")
        
        print(f"\n📝 Next Steps:")
        print("  1. Set OAuth environment variables in .env")
        print("  2. Update credential_fetcher.py to use new columns")
        print("  3. Implement OAuthTokenRefresher class")
        print("  4. Test token refresh functionality")
        print("  5. Remove references to archived tables in code")
        
        print(f"\n💾 Backup: {backup_path}")
        
    except Exception as e:
        print(f"\n ERROR: {e}")
        print("\n⚠️  Migration failed! Database backup available.")
        raise

if __name__ == '__main__':
    main()
