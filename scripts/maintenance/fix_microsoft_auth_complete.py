"""
Fix Microsoft Authentication - Complete System Fix
==================================================
from shared.database_utils import convert_sql_placeholders

This script fixes ALL Microsoft authentication issues:
1. Migrates old 'microsoft365' tokens to 'microsoft' platform name
2. Updates users.has_microsoft_oauth flag
3. Adds proper metadata (account_identifier, account_name)
4. Fixes expires_at for tokens without expiry
5. Validates all Microsoft tokens

Run this ONCE to fix all Microsoft authentication pathways.
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime, timedelta

def get_db_connection():
    """Get database connection"""
    db_path = Path(__file__).parent.parent.parent / "data" / "ai_infrastructure.db"
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def backup_tokens():
    """Backup oauth_tokens before migration"""
    print("\n" + "="*70)
    print("STEP 1: Backup Current Tokens")
    print("="*70)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create backup table
    sql, params = convert_sql_placeholders("""
        CREATE TABLE IF NOT EXISTS oauth_tokens_backup_jan2025 AS
        SELECT * FROM oauth_tokens WHERE 0
    """)
    
    # Copy Microsoft tokens to backup
    cursor.execute("""
        INSERT INTO oauth_tokens_backup_jan2025
        SELECT * FROM oauth_tokens
        WHERE platform IN ('microsoft', 'microsoft365')
    """)
    
    backed_up = cursor.rowcount
    print(f"   ✅ Backed up {backed_up} Microsoft tokens to oauth_tokens_backup_jan2025")
    
    conn.commit()
    conn.close()


def migrate_microsoft365_to_microsoft():
    """Migrate platform name from 'microsoft365' to 'microsoft'"""
    print("\n" + "="*70)
    print("STEP 2: Migrate 'microsoft365' → 'microsoft'")
    print("="*70)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check for microsoft365 tokens
    cursor.execute("""
        SELECT id, user_id, account_identifier, created_at
        FROM oauth_tokens
        WHERE platform = 'microsoft365'
    """)
    
    old_tokens = cursor.fetchall()
    
    if not old_tokens:
        print("   ℹ️  No 'microsoft365' tokens to migrate")
        conn.close()
        return
    
    print(f"   Found {len(old_tokens)} 'microsoft365' tokens")
    
    for token in old_tokens:
        # Check if user already has a 'microsoft' token
        cursor.execute("""
            SELECT id FROM oauth_tokens
            WHERE user_id = ? AND platform = 'microsoft'
        """, (token['user_id'],))

    cursor.execute(sql, params)
        
        has_microsoft = cursor.fetchone()
        
        if has_microsoft:
            # User has both - delete the old microsoft365 one
            print(f"   🗑️  User {token['user_id']} has 'microsoft' token - deleting old 'microsoft365' token {token['id']}")
            sql, params = convert_sql_placeholders("DELETE FROM oauth_tokens WHERE id = ?", (token['id'],))

            cursor.execute(sql, params)
        else:
            # Migrate the token to 'microsoft'
            print(f"   ✅ Migrating token {token['id']} (user {token['user_id']}) to 'microsoft' platform")
            sql, params = convert_sql_placeholders("""
                UPDATE oauth_tokens
                SET platform = 'microsoft',
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (token['id'],))

            cursor.execute(sql, params)
    
    conn.commit()
    conn.close()
    
    print(f"   ✅ Migration complete")


def fix_missing_expiry():
    """Add expires_at to tokens that don't have it"""
    print("\n" + "="*70)
    print("STEP 3: Fix Missing Token Expiry")
    print("="*70)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Find Microsoft tokens without expiry
    sql, params = convert_sql_placeholders("""
        SELECT id, user_id, created_at
        FROM oauth_tokens
        WHERE platform = 'microsoft' AND expires_at IS NULL
    """)
    
    no_expiry = cursor.fetchall()
    
    if not no_expiry:
        print("   ℹ️  All Microsoft tokens have expiry tracking")
        conn.close()
        return
    
    print(f"   Found {len(no_expiry)} tokens without expiry")
    
    for token in no_expiry:
        # Calculate expiry: created_at + 1 hour (standard Microsoft token lifetime)
        created_at = datetime.strptime(token['created_at'], '%Y-%m-%d %H:%M:%S')
        expires_at = created_at + timedelta(hours=1)
        
        cursor.execute("""
            UPDATE oauth_tokens
            SET expires_at = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (expires_at.strftime('%Y-%m-%d %H:%M:%S'), token['id']))
        
        print(f"   ✅ Set expiry for token {token['id']} (user {token['user_id']})")
    
    conn.commit()
    conn.close()


def fix_missing_metadata():
    """Add account_identifier and account_name from metadata"""
    print("\n" + "="*70)
    print("STEP 4: Fix Missing Account Metadata")
    print("="*70)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Find Microsoft tokens without account_identifier
    cursor.execute("""
        SELECT id, user_id, metadata, account_identifier, account_name
        FROM oauth_tokens
        WHERE platform = 'microsoft'
          AND (account_identifier IS NULL OR account_name IS NULL)
    """)
    
    tokens = cursor.fetchall()
    
    if not tokens:
        print("   ℹ️  All Microsoft tokens have account metadata")
        conn.close()
        return
    
    print(f"   Found {len(tokens)} tokens with missing metadata")
    
    for token in tokens:
        # Try to extract from metadata JSON
        metadata = json.loads(token['metadata']) if token['metadata'] else {}
        
        account_identifier = token['account_identifier']
        account_name = token['account_name']
        
        # Try to get from metadata
        if not account_identifier:
            account_identifier = metadata.get('microsoft_id') or metadata.get('email')
        
        if not account_name:
            account_name = metadata.get('display_name') or metadata.get('email', '').split('@')[0]
        
        if account_identifier or account_name:
            cursor.execute("""
                UPDATE oauth_tokens
                SET account_identifier = ?,
                    account_name = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (account_identifier, account_name, token['id']))

    cursor.execute(sql, params)
            
            print(f"   ✅ Updated token {token['id']} metadata")
    
    conn.commit()
    conn.close()


def update_user_flags():
    """Update users.has_microsoft_oauth flag"""
    print("\n" + "="*70)
    print("STEP 5: Update User Microsoft OAuth Flags")
    print("="*70)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all users
    cursor.execute("SELECT id, username FROM users")
    users = cursor.fetchall()
    
    for user in users:
        # Check if user has Microsoft token
        sql, params = convert_sql_placeholders("""
            SELECT COUNT(*) as count
            FROM oauth_tokens
            WHERE user_id = ? AND platform = 'microsoft' AND is_active = 1
        """, (user['id'],))

        cursor.execute(sql, params)
        
        has_token = cursor.fetchone()['count'] > 0
        
        # Update user flag
        sql, params = convert_sql_placeholders("""
            UPDATE users
            SET has_microsoft_oauth = ?
            WHERE id = ?
        """, (1 if has_token else 0, user['id']))

        cursor.execute(sql, params)
        
        status = "✅ HAS" if has_token else "❌ NO"
        print(f"   {status} Microsoft OAuth: User {user['id']} ({user['username']})")
    
    conn.commit()
    conn.close()


def validate_tokens():
    """Validate all Microsoft tokens"""
    print("\n" + "="*70)
    print("STEP 6: Validate Microsoft Tokens")
    print("="*70)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            id,
            user_id,
            platform,
            account_identifier,
            account_name,
            expires_at,
            is_active,
            is_valid,
            created_at
        FROM oauth_tokens
        WHERE platform = 'microsoft'
        ORDER BY user_id, updated_at DESC
    """)
    
    tokens = cursor.fetchall()
    
    print(f"\n   Found {len(tokens)} Microsoft tokens:\n")
    
    for token in tokens:
        print(f"   Token ID: {token['id']}")
        print(f"   User ID: {token['user_id']}")
        print(f"   Platform: {token['platform']} {'✅' if token['platform'] == 'microsoft' else '❌'}")
        print(f"   Account: {token['account_identifier'] or 'N/A'}")
        print(f"   Name: {token['account_name'] or 'N/A'}")
        print(f"   Expires: {token['expires_at'] or 'Missing ⚠️'}")
        print(f"   Active: {token['is_active']}")
        print(f"   Valid: {token['is_valid']}")
        print()
    
    conn.close()


def generate_summary():
    """Generate final summary"""
    print("\n" + "="*70)
    print("MIGRATION COMPLETE - SUMMARY")
    print("="*70)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Count Microsoft tokens
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM oauth_tokens
        WHERE platform = 'microsoft'
    """)
    microsoft_count = cursor.fetchone()['count']
    
    # Count old microsoft365 tokens
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM oauth_tokens
        WHERE platform = 'microsoft365'
    """)
    old_count = cursor.fetchone()['count']
    
    # Count users with Microsoft OAuth
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM users
        WHERE has_microsoft_oauth = 1
    """)
    users_count = cursor.fetchone()['count']
    
    # Check tokens with expiry
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM oauth_tokens
        WHERE platform = 'microsoft' AND expires_at IS NOT NULL
    """)
    expiry_count = cursor.fetchone()['count']
    
    # Check tokens with metadata
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM oauth_tokens
        WHERE platform = 'microsoft' 
          AND account_identifier IS NOT NULL 
          AND account_name IS NOT NULL
    """)
    metadata_count = cursor.fetchone()['count']
    
    print(f"\n   ✅ 'microsoft' tokens: {microsoft_count}")
    print(f"   {'✅' if old_count == 0 else '⚠️ '} 'microsoft365' tokens: {old_count}")
    print(f"   ✅ Users with Microsoft OAuth: {users_count}")
    print(f"   ✅ Tokens with expiry: {expiry_count}/{microsoft_count}")
    print(f"   ✅ Tokens with metadata: {metadata_count}/{microsoft_count}")
    
    print("\n   📋 Next Steps:")
    print("   1. Restart Flask server: BISTART")
    print("   2. Test Microsoft OAuth login")
    print("   3. Test Microsoft tools (Outlook, OneDrive, etc.)")
    
    conn.close()


def main():
    """Run all migration steps"""
    print("\n" + "="*70)
    print("MICROSOFT AUTHENTICATION COMPLETE FIX")
    print("="*70)
    print("\nThis will:")
    print("1. Backup current tokens")
    print("2. Migrate 'microsoft365' → 'microsoft'")
    print("3. Fix missing token expiry")
    print("4. Fix missing account metadata")
    print("5. Update user OAuth flags")
    print("6. Validate all tokens")
    
    response = input("\nProceed? (yes/no): ")
    
    if response.lower() not in ['yes', 'y']:
        print("\n❌ Migration cancelled")
        return
    
    try:
        backup_tokens()
        migrate_microsoft365_to_microsoft()
        fix_missing_expiry()
        fix_missing_metadata()
        update_user_flags()
        validate_tokens()
        generate_summary()
        
        print("\n" + "="*70)
        print("✅ MICROSOFT AUTHENTICATION FIX COMPLETE")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ Error during migration: {e}")
        print("   Database changes may be incomplete")
        print("   Check oauth_tokens_backup_jan2025 table to restore if needed")


if __name__ == "__main__":
    main()
