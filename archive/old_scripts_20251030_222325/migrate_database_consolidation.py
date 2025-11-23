"""
Database Consolidation Migration Script
Simplifies database structure:
- Adds OAuth flags to users table
- Creates simplified oauth_tokens table
- Migrates from key-value to column structure
- Adds dashboard permissions
"""
import sqlite3
import json
from datetime import datetime
from shared.database_utils import convert_sql_placeholders

DB_PATH = 'AI_infrastructure/ai_infrastructure.db'

def backup_database():
    """Create backup before migration"""
    import shutil
    backup_path = f'AI_infrastructure/ai_infrastructure_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
    shutil.copy(DB_PATH, backup_path)
    print(f"Backup created: {backup_path}")
    return backup_path

def migrate_database():
    print("=" * 80)
    print("DATABASE CONSOLIDATION MIGRATION")
    print("=" * 80)
    
    # Backup first
    backup_path = backup_database()
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # STEP 1: Add new columns to users table
        print("\n📝 Step 1: Adding new columns to users table...")
        
        columns_to_add = [
            ("allowed_dashboards", "TEXT DEFAULT '[]'"),
            ("has_google_oauth", "BOOLEAN DEFAULT 0"),
            ("has_microsoft_oauth", "BOOLEAN DEFAULT 0"),
            ("is_active", "BOOLEAN DEFAULT 1")
        ]
        
        for col_name, col_def in columns_to_add:
            try:
                cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_def}")
                print(f"  Added column: {col_name}")
            except sqlite3.OperationalError as e:
                if "duplicate column" in str(e).lower():
                    print(f"  ⏭️  Column already exists: {col_name}")
                else:
                    raise
        
        conn.commit()
        
        # STEP 2: Update OAuth flags from existing credentials
        print("\n🔐 Step 2: Setting OAuth flags from credentials...")
        
        # Google OAuth
        sql, params = convert_sql_placeholders("""
            UPDATE users 
            SET has_google_oauth = 1 
            WHERE id IN (
                SELECT DISTINCT user_id 
                FROM user_platform_credentials 
                WHERE platform LIKE '%google%' AND is_active = 1
            )
        """)
        google_count = cursor.rowcount
        print(f"  Updated {google_count} users with Google OAuth")
        
        # Microsoft OAuth
        cursor.execute("""
            UPDATE users 
            SET has_microsoft_oauth = 1 
            WHERE id IN (
                SELECT DISTINCT user_id 
                FROM user_platform_credentials 
                WHERE platform LIKE '%microsoft%' AND is_active = 1
            )
        """)
        microsoft_count = cursor.rowcount
        print(f"  Updated {microsoft_count} users with Microsoft OAuth")
        
        conn.commit()
        
        # STEP 3: Create new oauth_tokens table
        print("\n🗄️  Step 3: Creating oauth_tokens table...")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS oauth_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                platform TEXT NOT NULL,
                access_token TEXT NOT NULL,
                refresh_token TEXT,
                token_type TEXT DEFAULT 'Bearer',
                expires_at TIMESTAMP,
                scope TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_refreshed_at TIMESTAMP,
                metadata TEXT,
                UNIQUE(user_id, platform),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        print("  oauth_tokens table created")
        
        conn.commit()
        
        # STEP 4: Migrate tokens from key-value to column structure
        print("\n🔄 Step 4: Migrating tokens to new structure...")
        
        # Get all unique user/platform combinations
        cursor.execute("""
            SELECT DISTINCT user_id, platform, created_at, updated_at, metadata
            FROM user_platform_credentials 
            WHERE is_active = 1
        """)
        
        platforms = cursor.fetchall()
        migrated_count = 0
        
        for platform_row in platforms:
            user_id = platform_row['user_id']
            platform = platform_row['platform']
            created_at = platform_row['created_at']
            updated_at = platform_row['updated_at']
            metadata = platform_row['metadata']
            
            # Get access token
            cursor.execute("""
                SELECT credential_value 
                FROM user_platform_credentials 
                WHERE user_id = ? AND platform = ? 
                AND credential_key = 'access_token' 
                AND is_active = 1
            """, (user_id, platform))

        cursor.execute(sql, params)
            
            access_row = cursor.fetchone()
            if not access_row:
                continue
                
            access_token = access_row['credential_value']
            
            # Get refresh token (optional)
            sql, params = convert_sql_placeholders("""
                SELECT credential_value 
                FROM user_platform_credentials 
                WHERE user_id = ? AND platform = ? 
                AND credential_key = 'refresh_token' 
                AND is_active = 1
            """, (user_id, platform))

            cursor.execute(sql, params)
            
            refresh_row = cursor.fetchone()
            refresh_token = refresh_row['credential_value'] if refresh_row else None
            
            # Insert into new table
            sql, params = convert_sql_placeholders("""
                INSERT OR REPLACE INTO oauth_tokens 
                (user_id, platform, access_token, refresh_token, created_at, updated_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, platform, access_token, refresh_token, created_at, updated_at, metadata))

            cursor.execute(sql, params)
            
            migrated_count += 1
            print(f"  Migrated: user_id={user_id}, platform={platform}")
        
        conn.commit()
        print(f"\n  Migrated {migrated_count} OAuth tokens")
        
        # STEP 5: Set default dashboard permissions
        print("\n🎯 Step 5: Setting default dashboard permissions...")
        
        # Admin gets all dashboards
        admin_dashboards = json.dumps([
            "main", "analytics", "admin_panel", 
            "stock_management", "invoice_processor", 
            "user_management", "ai_chat", "kanban"
        ])
        
        sql, params = convert_sql_placeholders("""
            UPDATE users 
            SET allowed_dashboards = ?
            WHERE role = 'admin'
        """, (admin_dashboards,))

        
        cursor.execute(sql, params)
        admin_count = cursor.rowcount
        print(f"  Updated {admin_count} admin users with full dashboard access")
        
        # Regular users get basic dashboards
        user_dashboards = json.dumps(["main", "analytics", "ai_chat"])
        
        sql, params = convert_sql_placeholders("""
            UPDATE users 
            SET allowed_dashboards = ?
            WHERE role = 'user' OR role IS NULL
        """, (user_dashboards,))

        
        cursor.execute(sql, params)
        user_count = cursor.rowcount
        print(f"  Updated {user_count} regular users with basic dashboard access")
        
        conn.commit()
        
        # STEP 6: Verify migration
        print("\nStep 6: Verifying migration...")
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE has_google_oauth = 1")
        google_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE has_microsoft_oauth = 1")
        microsoft_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM oauth_tokens")
        token_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE allowed_dashboards != '[]'")
        dashboard_users = cursor.fetchone()[0]
        
        print(f"  Users with Google OAuth: {google_users}")
        print(f"  Users with Microsoft OAuth: {microsoft_users}")
        print(f"  Total OAuth tokens migrated: {token_count}")
        print(f"  Users with dashboard permissions: {dashboard_users}")
        
        # Show sample migrated data
        print("\n📊 Sample migrated data:")
        cursor.execute("""
            SELECT id, username, email, role, has_google_oauth, has_microsoft_oauth, allowed_dashboards
            FROM users
            LIMIT 3
        """)
        
        for row in cursor.fetchall():
            print(f"\n  User: {row['username']}")
            print(f"    Email: {row['email']}")
            print(f"    Role: {row['role']}")
            print(f"    Google OAuth: {'' if row['has_google_oauth'] else ''}")
            print(f"    Microsoft OAuth: {'' if row['has_microsoft_oauth'] else ''}")
            dashboards = json.loads(row['allowed_dashboards']) if row['allowed_dashboards'] else []
            print(f"    Dashboards: {', '.join(dashboards)}")
        
        conn.close()
        
        print("\n" + "=" * 80)
        print("MIGRATION COMPLETE!")
        print("=" * 80)
        print(f"\n📦 Backup saved: {backup_path}")
        print("🔄 Next steps:")
        print("  1. Update user_profile_builder.py to use has_google_oauth/has_microsoft_oauth flags")
        print("  2. Update credential_fetcher.py to use oauth_tokens table")
        print("  3. Add dashboard permission checks to routes")
        print("  4. Test OAuth login flow")
        
        return True
        
    except Exception as e:
        print(f"\n Migration failed: {e}")
        conn.rollback()
        conn.close()
        print(f"💾 Database restored from backup: {backup_path}")
        return False

if __name__ == "__main__":
    success = migrate_database()
    exit(0 if success else 1)
