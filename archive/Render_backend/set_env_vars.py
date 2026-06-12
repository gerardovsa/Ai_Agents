"""
Set Environment Variables for Render Service
Programmatically add all required environment variables to the deployed service
"""

import os
import sys
import secrets
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from render_api_client import RenderAPIClient

# Import API keys from config
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import ANTHROPIC_API_KEYS, OPENAI_API_KEYS, DEEPSEEK_API_KEYS

# Service ID
SERVICE_ID = 'srv-d47gjbm3jp1c73c0e6m0'

def main():
    """Set environment variables for Render service"""
    
    print("=" * 80)
    print("  SETTING ENVIRONMENT VARIABLES FOR RENDER SERVICE")
    print("=" * 80)
    print(f"\nService ID: {SERVICE_ID}")
    
    # Initialize API client
    api_key = os.getenv('RENDER_API_KEY', 'rnd_hTZfWT0aHJLeX925X5sIiY5PxWiu')
    client = RenderAPIClient(api_key)
    
    # Generate new SECRET_KEY for production
    secret_key = secrets.token_hex(32)
    print(f"\n✅ Generated new SECRET_KEY: {secret_key[:16]}... (64 chars)")
    
    # Get API keys from config
    anthropic_key = ANTHROPIC_API_KEYS[0] if ANTHROPIC_API_KEYS else ''
    openai_key = OPENAI_API_KEYS[0] if OPENAI_API_KEYS else ''
    deepseek_key = DEEPSEEK_API_KEYS[0] if DEEPSEEK_API_KEYS else ''
    
    print(f"\n✅ Found API keys:")
    print(f"   - Anthropic: {anthropic_key[:20]}..." if anthropic_key else "   - Anthropic: NOT FOUND")
    print(f"   - OpenAI: {openai_key[:20]}..." if openai_key else "   - OpenAI: NOT FOUND")
    print(f"   - DeepSeek: {deepseek_key[:20]}..." if deepseek_key else "   - DeepSeek: NOT FOUND")
    
    # Get Google OAuth from .env.master
    env_master_path = Path(__file__).parent.parent / '.env.master'
    google_client_id = ''
    google_client_secret = ''
    
    if env_master_path.exists():
        with open(env_master_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if line.startswith('GOOGLE_OAUTH_CLIENT_ID='):
                    google_client_id = line.split('=', 1)[1].strip()
                elif line.startswith('GOOGLE_OAUTH_CLIENT_SECRET='):
                    google_client_secret = line.split('=', 1)[1].strip()
        
        print(f"\n✅ Found Google OAuth credentials:")
        print(f"   - Client ID: {google_client_id[:30]}..." if google_client_id else "   - Client ID: NOT FOUND")
        print(f"   - Client Secret: {google_client_secret[:20]}..." if google_client_secret else "   - Client Secret: NOT FOUND")
    else:
        print(f"\n⚠️  .env.master not found at: {env_master_path}")
    
    # Get Microsoft OAuth from .env.master
    microsoft_client_id = ''
    microsoft_client_secret = ''
    
    if env_master_path.exists():
        with open(env_master_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if line.startswith('MICROSOFT_CLIENT_ID='):
                    microsoft_client_id = line.split('=', 1)[1].strip()
                elif line.startswith('MICROSOFT_CLIENT_SECRET='):
                    microsoft_client_secret = line.split('=', 1)[1].strip()
        
        print(f"\n✅ Found Microsoft OAuth credentials:")
        print(f"   - Client ID: {microsoft_client_id[:30]}..." if microsoft_client_id else "   - Client ID: NOT FOUND")
        print(f"   - Client Secret: {microsoft_client_secret[:20]}..." if microsoft_client_secret else "   - Client Secret: NOT FOUND")
    
    # Build environment variables list
    env_vars = [
        # AI Provider Keys
        {"key": "ANTHROPIC_API_KEY", "value": anthropic_key},
        {"key": "OPENAI_API_KEY", "value": openai_key},
        {"key": "DEEPSEEK_API_KEY_1", "value": deepseek_key},
        
        # Google OAuth
        {"key": "GOOGLE_OAUTH_CLIENT_ID", "value": google_client_id},
        {"key": "GOOGLE_OAUTH_CLIENT_SECRET", "value": google_client_secret},
        {"key": "GOOGLE_REDIRECT_URI", "value": "https://ai-agents-backend-singapore.onrender.com/api/auth/google/callback"},
        
        # Microsoft OAuth
        {"key": "MICROSOFT_CLIENT_ID", "value": microsoft_client_id},
        {"key": "MICROSOFT_CLIENT_SECRET", "value": microsoft_client_secret},
        {"key": "MICROSOFT_TENANT_ID", "value": "common"},
        
        # Flask Configuration
        {"key": "SECRET_KEY", "value": secret_key},
        {"key": "ENVIRONMENT", "value": "production"},
        {"key": "RENDER", "value": "true"},
        {"key": "PYTHONUNBUFFERED", "value": "1"},
        
        # Database
        {"key": "DATABASE_PATH", "value": "/app/data/ai_infrastructure.db"},
        {"key": "SESSION_DB_PATH", "value": "/app/data/sessions.db"},
    ]
    
    # Filter out empty values
    env_vars = [ev for ev in env_vars if ev['value']]
    
    print(f"\n📋 Preparing to set {len(env_vars)} environment variables...")
    
    # Update service with environment variables
    try:
        print("\n⏳ Updating service environment variables...")
        
        # Use the dedicated env vars endpoint
        result = client.update_service_env_vars(SERVICE_ID, env_vars)
        
        print("✅ Environment variables updated successfully!")
        print("\n📊 Variables set:")
        for ev in env_vars:
            value_preview = ev['value'][:30] + '...' if len(ev['value']) > 30 else ev['value']
            print(f"   ✓ {ev['key']}: {value_preview}")
        
        print("\n" + "=" * 80)
        print("  ENVIRONMENT VARIABLES SET - READY TO DEPLOY")
        print("=" * 80)
        
        print("\n🚀 Next step: Trigger deployment")
        print(f"   python -c \"from Render_backend.render_api_client import RenderAPIClient; import os; client = RenderAPIClient(os.getenv('RENDER_API_KEY', 'rnd_hTZfWT0aHJLeX925X5sIiY5PxWiu')); print(client.trigger_deploy('{SERVICE_ID}'))\"")
        
        return True
        
    except requests.exceptions.HTTPError as e:
        print(f"\n❌ Error updating environment variables: {e}")
        if hasattr(e.response, 'text'):
            print(f"Error details: {e.response.text}")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
