"""
Search for Shopify Credentials in Supabase
===========================================
"""

from AI_infrastructure.shared.database_utils import get_database_connection
import json

def search_shopify_credentials():
    """Search for Shopify-related credentials"""
    conn = None
    cursor = None
    
    try:
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        # Search for Shopify credentials
        cursor.execute("""
            SELECT id, user_id, platform, credential_type, credential_key, 
                   is_active, created_at, metadata, credentials
            FROM user_platform_credentials
            WHERE platform LIKE '%shopify%' 
               OR platform LIKE '%shop%'
               OR credential_key LIKE '%shopify%'
            ORDER BY id
        """)
        
        rows = cursor.fetchall()
        
        print("\n🔍 Shopify Credentials Search:")
        print("=" * 80)
        
        if rows:
            for row in rows:
                print(f"ID: {row['id']:3d} | User: {row['user_id']} | Platform: {row['platform']:25s}")
                print(f"     Type: {row['credential_type']:10s} | Key: {row['credential_key']:30s} | Active: {row['is_active']}")
                print(f"     Created: {row['created_at']}")
                if row['metadata']:
                    print(f"     Metadata: {row['metadata']}")
                if row['credentials']:
                    creds = row['credentials']
                    # Mask sensitive data
                    if isinstance(creds, dict):
                        masked = {k: (v[:20] + '...' if isinstance(v, str) and len(v) > 20 else v) 
                                 for k, v in creds.items()}
                        print(f"     Credentials: {json.dumps(masked, indent=10)}")
                print("-" * 80)
        else:
            print("❌ No Shopify credentials found in database")
            print("\n💡 Checking all platforms to help locate Shopify...")
            
            cursor.execute("""
                SELECT DISTINCT platform 
                FROM user_platform_credentials 
                ORDER BY platform
            """)
            platforms = cursor.fetchall()
            print("\n📋 Available Platforms:")
            for p in platforms:
                print(f"   - {p['platform']}")
        
        print("=" * 80 + "\n")
        
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
    except Exception as e:
        print(f"\n❌ Error searching credentials: {e}")
        import traceback
        traceback.print_exc()
        
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
    search_shopify_credentials()
