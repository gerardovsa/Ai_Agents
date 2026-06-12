"""
Add Environment Variables to Render Service
Programmatically adds all required environment variables
"""

import os
import sys
import requests
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import ANTHROPIC_API_KEYS, OPENAI_API_KEYS, DEEPSEEK_API_KEYS
import secrets

# Service configuration
SERVICE_ID = 'srv-d47nfr2li9vc738s0uc0'
API_KEY = os.getenv('RENDER_API_KEY', 'rnd_hTZfWT0aHJLeX925X5sIiY5PxWiu')

# Load from .env.master
env_master_path = Path(__file__).parent.parent / '.env.master'
env_vars_from_file = {}

if env_master_path.exists():
    with open(env_master_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars_from_file[key.strip()] = value.strip()

# Define environment variables
ENV_VARS = {
    'ANTHROPIC_API_KEY': ANTHROPIC_API_KEYS[0] if ANTHROPIC_API_KEYS else '',
    'OPENAI_API_KEY': OPENAI_API_KEYS[0] if OPENAI_API_KEYS else '',
    'DEEPSEEK_API_KEY_1': DEEPSEEK_API_KEYS[0] if DEEPSEEK_API_KEYS else '',
    'GOOGLE_OAUTH_CLIENT_ID': env_vars_from_file.get('GOOGLE_OAUTH_CLIENT_ID', ''),
    'GOOGLE_OAUTH_CLIENT_SECRET': env_vars_from_file.get('GOOGLE_OAUTH_CLIENT_SECRET', ''),
    'MICROSOFT_CLIENT_ID': env_vars_from_file.get('MICROSOFT_CLIENT_ID', ''),
    'MICROSOFT_CLIENT_SECRET': env_vars_from_file.get('MICROSOFT_CLIENT_SECRET', ''),
    'SECRET_KEY': secrets.token_hex(32),
}

print("=" * 80)
print("ADDING ENVIRONMENT VARIABLES TO RENDER SERVICE")
print("=" * 80)
print(f"\nService ID: {SERVICE_ID}")
print(f"Variables to add: {len(ENV_VARS)}")
print()

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

added_count = 0
failed_vars = []

for key, value in ENV_VARS.items():
    if not value:
        print(f"  ⚠️  {key}: SKIPPED (no value)")
        failed_vars.append(key)
        continue
    
    # Try PUT endpoint for individual env var
    url = f"https://api.render.com/v1/services/{SERVICE_ID}/env-vars/{key}"
    payload = {"value": value}
    
    try:
        response = requests.put(url, json=payload, headers=headers)
        
        if response.status_code in [200, 201]:
            added_count += 1
            print(f"  ✅ {key}: Added")
        else:
            # Try POST to create new env var
            url_post = f"https://api.render.com/v1/services/{SERVICE_ID}/env-vars"
            payload_post = {"key": key, "value": value}
            response_post = requests.post(url_post, json=payload_post, headers=headers)
            
            if response_post.status_code in [200, 201]:
                added_count += 1
                print(f"  ✅ {key}: Added (via POST)")
            else:
                failed_vars.append(key)
                print(f"  ❌ {key}: Failed (PUT: {response.status_code}, POST: {response_post.status_code})")
                if response.text:
                    print(f"     Error: {response.text[:100]}")
    except Exception as e:
        failed_vars.append(key)
        print(f"  ❌ {key}: Error - {str(e)[:80]}")

print()
print("=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Successfully added: {added_count}/{len(ENV_VARS)}")

if failed_vars:
    print(f"Failed: {len(failed_vars)} variables")
    print(f"  {', '.join(failed_vars)}")
    print()
    print("⚠️  You need to add these manually in the dashboard:")
    print(f"   https://dashboard.render.com/web/{SERVICE_ID}/env")
else:
    print()
    print("✅ All environment variables added successfully!")
    print()
    print("Triggering deployment...")
    
    # Trigger deploy
    deploy_url = f"https://api.render.com/v1/services/{SERVICE_ID}/deploys"
    try:
        deploy_response = requests.post(deploy_url, headers=headers)
        if deploy_response.status_code in [200, 201]:
            deploy_data = deploy_response.json()
            print(f"✅ Deployment triggered: {deploy_data.get('id', 'unknown')}")
            print()
            print("Monitor deployment:")
            print("  python Render_backend/monitor_live_deployment.py --watch")
        else:
            print(f"⚠️  Could not trigger deployment: {deploy_response.status_code}")
            print("   Trigger manually in dashboard")
    except Exception as e:
        print(f"⚠️  Could not trigger deployment: {e}")

print()
print("=" * 80)
