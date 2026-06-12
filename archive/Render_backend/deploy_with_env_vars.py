"""
Render.com Deployment Script with Environment Variables
Creates/updates service with all environment variables configured
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from Render_backend.render_api_client import RenderAPIClient
from config import ANTHROPIC_API_KEYS, OPENAI_API_KEYS, DEEPSEEK_API_KEYS
import secrets
import time

# Load environment variables from .env.master
env_master_path = Path(__file__).parent.parent / '.env.master'
env_vars_from_file = {}

if env_master_path.exists():
    with open(env_master_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars_from_file[key.strip()] = value.strip()

# Service configuration
SERVICE_CONFIG = {
    'name': 'ai-agents-backend-singapore',
    'region': 'singapore',
    'plan': 'starter',  # $7/month - can downgrade to 'free' later
    'branch': 'v3',
    'repo': 'https://github.com/gerardovsa/AI_agents',
    'buildCommand': 'pip install -r requirements.txt',
    'startCommand': 'cd AI_infrastructure && python flask_app.py',
    'healthCheckPath': '/health',
    'dockerfilePath': './Dockerfile',
}

# Environment variables with proper configuration
ENVIRONMENT_VARIABLES = [
    {
        'key': 'ANTHROPIC_API_KEY',
        'value': ANTHROPIC_API_KEYS[0] if ANTHROPIC_API_KEYS else '',
        'description': 'Anthropic Claude API key for AI operations'
    },
    {
        'key': 'OPENAI_API_KEY',
        'value': OPENAI_API_KEYS[0] if OPENAI_API_KEYS else '',
        'description': 'OpenAI API key for AI operations'
    },
    {
        'key': 'DEEPSEEK_API_KEY_1',
        'value': DEEPSEEK_API_KEYS[0] if DEEPSEEK_API_KEYS else '',
        'description': 'DeepSeek API key for AI operations'
    },
    {
        'key': 'GOOGLE_OAUTH_CLIENT_ID',
        'value': env_vars_from_file.get('GOOGLE_OAUTH_CLIENT_ID', ''),
        'description': 'Google OAuth client ID'
    },
    {
        'key': 'GOOGLE_OAUTH_CLIENT_SECRET',
        'value': env_vars_from_file.get('GOOGLE_OAUTH_CLIENT_SECRET', ''),
        'description': 'Google OAuth client secret'
    },
    {
        'key': 'GOOGLE_REDIRECT_URI',
        'value': 'https://ai-agents-backend-singapore.onrender.com/api/auth/google/callback',
        'description': 'Google OAuth redirect URI'
    },
    {
        'key': 'MICROSOFT_CLIENT_ID',
        'value': env_vars_from_file.get('MICROSOFT_CLIENT_ID', ''),
        'description': 'Microsoft OAuth client ID'
    },
    {
        'key': 'MICROSOFT_CLIENT_SECRET',
        'value': env_vars_from_file.get('MICROSOFT_CLIENT_SECRET', ''),
        'description': 'Microsoft OAuth client secret'
    },
    {
        'key': 'MICROSOFT_TENANT_ID',
        'value': env_vars_from_file.get('MICROSOFT_TENANT_ID', 'common'),
        'description': 'Microsoft OAuth tenant ID'
    },
    {
        'key': 'SECRET_KEY',
        'value': secrets.token_hex(32),
        'description': 'Flask secret key for session management'
    },
    {
        'key': 'ENVIRONMENT',
        'value': 'production',
        'description': 'Environment flag'
    },
    {
        'key': 'RENDER',
        'value': 'true',
        'description': 'Render platform flag'
    },
    {
        'key': 'PYTHONUNBUFFERED',
        'value': '1',
        'description': 'Python unbuffered output'
    },
    {
        'key': 'DATABASE_PATH',
        'value': '/opt/render/project/src/data/ai_infrastructure.db',
        'description': 'Database path'
    },
    {
        'key': 'SESSION_DB_PATH',
        'value': '/opt/render/project/src/data/sessions.db',
        'description': 'Session database path'
    }
]


def validate_env_vars():
    """Validate that all critical environment variables are set"""
    critical_vars = [
        'ANTHROPIC_API_KEY',
        'OPENAI_API_KEY',
        'DEEPSEEK_API_KEY_1',
        'GOOGLE_OAUTH_CLIENT_ID',
        'GOOGLE_OAUTH_CLIENT_SECRET',
        'MICROSOFT_CLIENT_ID',
        'MICROSOFT_CLIENT_SECRET'
    ]
    
    missing = []
    for var_config in ENVIRONMENT_VARIABLES:
        if var_config['key'] in critical_vars and not var_config['value']:
            missing.append(var_config['key'])
    
    if missing:
        print("\nERROR: Missing critical environment variables:")
        for var in missing:
            print(f"  - {var}")
        print("\nPlease ensure config.py and .env.master have the required values.")
        return False
    
    return True


def create_or_update_service():
    """Create new service or update existing service with environment variables"""
    
    print("="*70)
    print("RENDER.COM DEPLOYMENT WITH ENVIRONMENT VARIABLES")
    print("="*70)
    
    # Validate environment variables
    print("\n[1/5] Validating environment variables...")
    if not validate_env_vars():
        sys.exit(1)
    
    print(f"  Found {len(ENVIRONMENT_VARIABLES)} environment variables")
    print("  All critical variables present")
    
    # Initialize Render API client
    print("\n[2/5] Connecting to Render API...")
    api_key = os.getenv('RENDER_API_KEY', 'rnd_hTZfWT0aHJLeX925X5sIiY5PxWiu')
    client = RenderAPIClient(api_key)
    
    # Use known owner ID for Vet Success team
    print("\n[3/5] Using owner ID...")
    owner_id = "tea-d1bv56p5pdvs73e9iobg"  # Vet Success team
    print(f"  Owner ID: {owner_id}")
    
    # Check if service already exists
    print("\n[4/5] Checking for existing service...")
    services = client.list_services()
    existing_service = None
    
    for service in services:
        if service['service']['name'] == SERVICE_CONFIG['name']:
            existing_service = service['service']
            print(f"  Found existing service: {existing_service['id']}")
            break
    
    if existing_service:
        # Update existing service with environment variables
        print("\n[5/5] Updating service with environment variables...")
        service_id = existing_service['id']
        
        # Prepare environment variables for API
        env_vars_payload = []
        for var in ENVIRONMENT_VARIABLES:
            env_vars_payload.append({
                'key': var['key'],
                'value': var['value']
            })
        
        # Update service using PATCH
        import requests
        url = f"https://api.render.com/v1/services/{service_id}"
        headers = {
            "Authorization": f"Bearer {client.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "envVars": env_vars_payload
        }
        
        print(f"  Sending {len(env_vars_payload)} environment variables...")
        response = requests.patch(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            print("  Environment variables updated successfully")
        else:
            print(f"  WARNING: API returned {response.status_code}")
            print(f"  Response: {response.text[:200]}")
        
        # Trigger deployment
        print("\n  Triggering deployment...")
        deploy_result = client.trigger_deploy(service_id)
        
        if deploy_result:
            deploy_id = deploy_result.get('id', 'unknown')
            print(f"  Deploy triggered: {deploy_id}")
        
    else:
        # Create new service with all configuration
        print("\n[5/5] Creating new service with environment variables...")
        
        # Prepare environment variables list
        env_vars_list = []
        for var in ENVIRONMENT_VARIABLES:
            env_vars_list.append({
                'key': var['key'],
                'value': var['value']
            })
        
        print(f"  Creating service with {len(env_vars_list)} environment variables...")
        
        # Create service with proper Render API structure
        service_config = {
            "type": "web_service",
            "name": SERVICE_CONFIG['name'],
            "ownerId": owner_id,
            "repo": SERVICE_CONFIG['repo'],
            "autoDeploy": "yes",
            "branch": SERVICE_CONFIG['branch'],
            "buildFilter": {
                "paths": [],
                "ignoredPaths": []
            },
            "envSpecificDetails": {
                "docker": {
                    "dockerfilePath": SERVICE_CONFIG['dockerfilePath'],
                    "dockerContext": "./"
                }
            },
            "serviceDetails": {
                "env": "docker",
                "region": SERVICE_CONFIG['region'],
                "plan": SERVICE_CONFIG['plan'],
                "healthCheckPath": SERVICE_CONFIG['healthCheckPath'],
                "envVars": env_vars_list
            }
        }
        
        # Create service using the API client
        response = client.create_service(service_config)
        
        if 'service' in response:
            service_data = response['service']
            service_id = service_data.get('id')
            print(f"  Service created: {service_id}")
        else:
            print(f"  ERROR: Failed to create service")
            print(f"  Response: {response}")
            sys.exit(1)
    
    # Print summary
    print("\n" + "="*70)
    print("DEPLOYMENT SUMMARY")
    print("="*70)
    print(f"\nService Name: {SERVICE_CONFIG['name']}")
    print(f"Service ID: {service_id}")
    print(f"Region: {SERVICE_CONFIG['region']}")
    print(f"Branch: {SERVICE_CONFIG['branch']}")
    print(f"URL: https://{SERVICE_CONFIG['name']}.onrender.com")
    
    print(f"\nEnvironment Variables Configured: {len(ENVIRONMENT_VARIABLES)}")
    for var in ENVIRONMENT_VARIABLES:
        status = "SET" if var['value'] else "NOT SET"
        print(f"  - {var['key']}: {status}")
    
    print("\nNext Steps:")
    print("1. Monitor deployment: python Render_backend/monitor_live_deployment.py --watch")
    print("2. Wait 5-10 minutes for build to complete")
    print("3. Test health endpoint: curl https://ai-agents-backend-singapore.onrender.com/health")
    print("4. Update OAuth redirect URLs in Google/Microsoft consoles")
    
    print("\n" + "="*70)


def main():
    """Main execution function"""
    try:
        create_or_update_service()
    except KeyboardInterrupt:
        print("\n\nDeployment cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nERROR: Deployment failed")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
