"""
Add device_info column to sessions.user_sessions table

Adds JSONB column to store:
- browser: Chrome/Firefox/Safari/Edge
- os: Windows/Mac/Linux/iOS/Android
- device_type: desktop/mobile/tablet
- ip_address: User's IP address
- location: City/Country (optional)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'AI_infrastructure'))

from shared.database_utils import get_database_connection

def add_device_info_column():
    """Add device_info JSONB column to user_sessions table"""
    
    print("=" * 70)
    print("ADDING DEVICE_INFO TO USER_SESSIONS TABLE")
    print("=" * 70)
    
    conn = get_database_connection('ai_infrastructure')
    cursor = conn.cursor()
    
    try:
        # Check if column already exists
        print("\n[1/3] Checking if device_info column exists...")
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_schema = 'ai_infrastructure' 
            AND table_name = 'user_sessions'
            AND column_name = 'device_info';
        """)
        
        exists = cursor.fetchone()
        
        if exists:
            print("     INFO - device_info column already exists, skipping creation")
        else:
            print("     device_info column does not exist, creating...")
            
            # Add device_info column
            print("\n[2/3] Adding device_info JSONB column...")
            cursor.execute("""
                ALTER TABLE ai_infrastructure.user_sessions 
                ADD COLUMN device_info JSONB DEFAULT '{}'::jsonb;
            """)
            print("     SUCCESS - Column added")
        
        # Create index on device_info for faster queries
        print("\n[3/3] Creating GIN index on device_info...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_sessions_device_info 
            ON ai_infrastructure.user_sessions USING GIN (device_info);
        """)
        print("     SUCCESS - Index created")
        
        # Commit changes
        conn.commit()
        
        # Verify schema
        cursor.execute("""
            SELECT 
                column_name, 
                data_type,
                column_default
            FROM information_schema.columns 
            WHERE table_schema = 'ai_infrastructure' 
            AND table_name = 'user_sessions'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        
        print("\n" + "=" * 70)
        print("MIGRATION COMPLETE")
        print("=" * 70)
        print(f"\nTable: ai_infrastructure.user_sessions")
        print(f"Total columns: {len(columns)}")
        print("\nUpdated Schema:")
        print("-" * 70)
        for col_name, data_type, default in columns:
            default_str = f" DEFAULT {default[:30]}..." if default and len(default) > 30 else f" DEFAULT {default}" if default else ""
            print(f"  {col_name:20} {data_type:15}{default_str}")
        
        print("\n" + "=" * 70)
        print("EXAMPLE DEVICE_INFO FORMAT:")
        print("=" * 70)
        print("""{
  "browser": "Chrome",
  "browser_version": "120.0.0",
  "os": "Windows",
  "os_version": "11",
  "device_type": "desktop",
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)..."
}""")
        
        print("\n✅ Ready for session management features!")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()
    
    return True

if __name__ == '__main__':
    try:
        success = add_device_info_column()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
