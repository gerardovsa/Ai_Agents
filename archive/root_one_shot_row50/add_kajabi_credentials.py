"""
Add Kajabi API credentials to user_platform_credentials table
Run this script to securely store Kajabi credentials in the database
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent / 'AI_infrastructure'))

from shared.database_utils import get_database_connection
import json

def add_kajabi_credentials(user_id=1):
    """
    Add Kajabi API credentials to database
    
    Args:
        user_id: User ID to associate credentials with (default: 1)
    """
    # Kajabi credentials
    api_key = '8MN3FQ62xbYuZXUVqDcib8af'
    api_secret = 'YLTJPeTusmULuADeAhX3reoz'
    
    print(f"🔐 Adding Kajabi credentials for user {user_id}...")
    
    # Get database connection
    conn = get_database_connection('ai_infrastructure')
    cursor = conn.cursor()
    
    try:
        # Check if credentials already exist
        cursor.execute("""
            SELECT user_id, platform 
            FROM ai_infrastructure.user_platform_credentials
            WHERE user_id = %s AND platform = 'kajabi'
        """, (user_id,))
        
        existing = cursor.fetchone()
        
        if existing:
            print(f"⚠️  Kajabi credentials already exist for user {user_id}")
            print("   Updating existing credentials...")
            
            # Update existing credentials
            cursor.execute("""
                UPDATE ai_infrastructure.user_platform_credentials
                SET credential_type = %s,
                    credential_key = %s,
                    credential_value = %s,
                    credentials = %s,
                    updated_at = NOW()
                WHERE user_id = %s AND platform = 'kajabi'
            """, (
                'api_key',
                'api_key',
                api_key,
                json.dumps({
                    'api_key': api_key,
                    'api_secret': api_secret
                }),
                user_id
            ))
            
            print("✅ Kajabi credentials updated successfully!")
        else:
            # Insert new credentials
            cursor.execute("""
                INSERT INTO ai_infrastructure.user_platform_credentials (
                    user_id,
                    platform,
                    credential_type,
                    credential_key,
                    credential_value,
                    credentials,
                    is_active,
                    created_at,
                    updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            """, (
                user_id,
                'kajabi',
                'api_key',
                'api_key',
                api_key,
                json.dumps({
                    'api_key': api_key,
                    'api_secret': api_secret
                }),
                True
            ))
            
            print("✅ Kajabi credentials added successfully!")
        
        conn.commit()
        
        # Verify credentials were added
        cursor.execute("""
            SELECT user_id, platform, credentials, is_active
            FROM ai_infrastructure.user_platform_credentials
            WHERE user_id = %s AND platform = 'kajabi'
        """, (user_id,))
        
        result = cursor.fetchone()
        if result:
            print(f"\n📊 Verification:")
            user_id_result = result[0] if isinstance(result, tuple) else result
            platform_result = result[1] if isinstance(result, tuple) else None
            credentials_result = result[2] if isinstance(result, tuple) else None
            active_result = result[3] if isinstance(result, tuple) else None
            
            print(f"   User ID: {user_id_result}")
            print(f"   Platform: {platform_result}")
            print(f"   Active: {active_result}")
            print(f"   API Key: {api_key[:10]}...")
            print(f"   API Secret: {api_secret[:10]}...")
            
            # Test credential retrieval
            print(f"\n🧪 Testing credential retrieval...")
            from AI_infrastructure.auth.credential_injector import get_kajabi_credentials
            
            try:
                creds = get_kajabi_credentials(user_id=user_id)
                print(f"✅ Credential retrieval test passed!")
                print(f"   Retrieved API Key: {creds.get('api_key', '')[:10]}...")
                print(f"   Retrieved API Secret: {creds.get('api_secret', '')[:10]}...")
            except Exception as e:
                print(f"❌ Credential retrieval test failed: {e}")
        
    except Exception as e:
        print(f"❌ Error adding Kajabi credentials: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    # Get user ID from command line or use default (1)
    user_id = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    
    print(f"🚀 Kajabi Credential Setup")
    print(f"   User ID: {user_id}")
    print(f"   Platform: Kajabi\n")
    
    add_kajabi_credentials(user_id)
    
    print(f"\n✨ Setup complete! Kajabi tools can now access credentials.")
    print(f"   Test with: python -c \"from tools.registry_v3 import RegistryV3; r = RegistryV3(); print(r.execute_tool('kajabi_list_products', _user_id={user_id}, _injected_credentials=True))\"")
