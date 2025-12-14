"""
Activate Xero Credentials in Supabase
======================================
Enables xero_print, xero_publishing, and xero_signs credentials for user 1
"""

from AI_infrastructure.shared.database_utils import get_database_connection

def activate_xero_credentials():
    """Activate all Xero platform credentials"""
    conn = None
    cursor = None
    
    try:
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        # Update all Xero credentials to active
        cursor.execute("""
            UPDATE user_platform_credentials
            SET is_active = true,
                updated_at = CURRENT_TIMESTAMP
            WHERE platform IN ('xero_print', 'xero_publishing', 'xero_signs')
              AND user_id = 1
            RETURNING id, platform, is_active
        """)
        
        updated_rows = cursor.fetchall()
        conn.commit()
        
        print("\n✅ Xero Credentials Activated:")
        print("=" * 60)
        for row in updated_rows:
            print(f"   ID: {row['id']:2d} | Platform: {row['platform']:20s} | Active: {row['is_active']}")
        print("=" * 60)
        print(f"\nTotal activated: {len(updated_rows)} credentials\n")
        
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error activating credentials: {e}")
        if conn:
            try:
                conn.rollback()
            except:
                pass
        return False
        
    finally:
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if conn:
            try:
                conn.close()
            except:
                pass


if __name__ == '__main__':
    print("\n🔧 Activating Xero Credentials...")
    print("-" * 60)
    
    success = activate_xero_credentials()
    
    if success:
        print("✅ Done! Xero module should now work correctly.\n")
    else:
        print("❌ Failed to activate credentials.\n")
