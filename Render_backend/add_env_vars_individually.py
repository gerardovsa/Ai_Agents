"""
Add environment variables one by one to Render service
Uses PATCH method to update service configuration
"""

import os
import sys
import requests
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import ANTHROPIC_API_KEYS, OPENAI_API_KEYS, DEEPSEEK_API_KEYS

SERVICE_ID = 'srv-d47gjbm3jp1c73c0e6m0'
API_KEY = os.getenv('RENDER_API_KEY', 'rnd_hTZfWT0aHJLeX925X5sIiY5PxWiu')

def get_google_oauth_credentials():
    """Extract Google OAuth from .env.master"""
    env_master = Path(__file__).parent.parent / '.env.master'
    google_client_id = ''
    google_client_secret = ''
    
    if env_master.exists():
        with open(env_master, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if line.startswith('GOOGLE_OAUTH_CLIENT_ID='):
                    google_client_id = line.split('=', 1)[1].strip()
                elif line.startswith('GOOGLE_OAUTH_CLIENT_SECRET='):
                    google_client_secret = line.split('=', 1)[1].strip()
    
    return google_client_id, google_client_secret

def get_microsoft_oauth_credentials():
    """Extract Microsoft OAuth from .env.master"""
    env_master = Path(__file__).parent.parent / '.env.master'
    microsoft_client_id = ''
    microsoft_client_secret = ''
    
    if env_master.exists():
        with open(env_master, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if line.startswith('MICROSOFT_CLIENT_ID='):
                    microsoft_client_id = line.split('=', 1)[1].strip()
                elif line.startswith('MICROSOFT_CLIENT_SECRET='):
                    microsoft_client_secret = line.split('=', 1)[1].strip()
    
    return microsoft_client_id, microsoft_client_secret

def update_service_with_env_vars():
    """Update service with environment variables using PATCH"""
    
    print("=" * 80)
    print("  ADDING ENVIRONMENT VARIABLES TO RENDER SERVICE")
    print("=" * 80)
    
    # Get credentials
    anthropic_key = ANTHROPIC_API_KEYS[0] if ANTHROPIC_API_KEYS else ''
    openai_key = OPENAI_API_KEYS[0] if OPENAI_API_KEYS else ''
    deepseek_key = DEEPSEEK_API_KEYS[0] if DEEPSEEK_API_KEYS else ''
    google_client_id, google_client_secret = get_google_oauth_credentials()
    microsoft_client_id, microsoft_client_secret = get_microsoft_oauth_credentials()
    
    # Generate SECRET_KEY
    import secrets
    secret_key = secrets.token_hex(32)
    
    print(f"\n✅ Credentials loaded:")
    print(f"   - Anthropic: {anthropic_key[:20]}...")
    print(f"   - OpenAI: {openai_key[:20]}...")
    print(f"   - DeepSeek: {deepseek_key[:20]}...")
    print(f"   - Google Client ID: {google_client_id[:30]}...")
    print(f"   - Microsoft Client ID: {microsoft_client_id[:30]}...")
    print(f"   - SECRET_KEY generated: {secret_key[:20]}...")
    
    # Build env vars array
    env_vars = [
        {"key": "ANTHROPIC_API_KEY", "value": anthropic_key},
        {"key": "OPENAI_API_KEY", "value": openai_key},
        {"key": "DEEPSEEK_API_KEY_1", "value": deepseek_key},
        {"key": "GOOGLE_OAUTH_CLIENT_ID", "value": google_client_id},
        {"key": "GOOGLE_OAUTH_CLIENT_SECRET", "value": google_client_secret},
        {"key": "GOOGLE_REDIRECT_URI", "value": "https://ai-agents-backend-singapore.onrender.com/api/auth/google/callback"},
        {"key": "MICROSOFT_CLIENT_ID", "value": microsoft_client_id},
        {"key": "MICROSOFT_CLIENT_SECRET", "value": microsoft_client_secret},
        {"key": "MICROSOFT_TENANT_ID", "value": "common"},
        {"key": "SECRET_KEY", "value": secret_key},
        {"key": "ENVIRONMENT", "value": "production"},
        {"key": "RENDER", "value": "true"},
        {"key": "PYTHONUNBUFFERED", "value": "1"},
        {"key": "DATABASE_PATH", "value": "/app/data/ai_infrastructure.db"},
        {"key": "SESSION_DB_PATH", "value": "/app/data/sessions.db"},
    ]
    
    # Filter out empty values
    env_vars = [ev for ev in env_vars if ev['value']]
    
    print(f"\n📋 Preparing to add {len(env_vars)} environment variables...")
    
    # Try PATCH to update service
    url = f"https://api.render.com/v1/services/{SERVICE_ID}"
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    payload = {
        "serviceDetails": {
            "envVars": env_vars
        }
    }
    
    print(f"\n⏳ Updating service via PATCH...")
    print(f"   URL: {url}")
    
    try:
        response = requests.patch(url, json=payload, headers=headers)
        
        print(f"\n📊 Response Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            print("✅ Environment variables added successfully!")
            print("\n📊 Variables set:")
            for ev in env_vars:
                value_preview = ev['value'][:30] + '...' if len(ev['value']) > 30 else ev['value']
                print(f"   ✓ {ev['key']}: {value_preview}")
            
            print("\n" + "=" * 80)
            print("  DEPLOYMENT WILL AUTO-TRIGGER")
            print("=" * 80)
            print("\n🚀 Monitor with:")
            print("   python Render_backend/monitor_live_deployment.py --watch")
            
            return True
        else:
            print(f"❌ Failed to update service")
            print(f"\nResponse: {response.text}")
            
            print("\n" + "=" * 80)
            print("  ALTERNATIVE: MANUAL SETUP REQUIRED")
            print("=" * 80)
            print("\n📝 Add variables manually in dashboard:")
            print(f"   https://dashboard.render.com/web/{SERVICE_ID}")
            print("\n💾 Copy values from:")
            print("   Render_backend/ENV_VARS_COPY_PASTE.txt")
            
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
        print("\n" + "=" * 80)
        print("  ALTERNATIVE: MANUAL SETUP REQUIRED")
        print("=" * 80)
        print("\n📝 Add variables manually in dashboard:")
        print(f"   https://dashboard.render.com/web/{SERVICE_ID}")
        print("\n💾 Copy values from:")
        print("   Render_backend/ENV_VARS_COPY_PASTE.txt")
        
        return False


if __name__ == '__main__':
    success = update_service_with_env_vars()
    sys.exit(0 if success else 1)
