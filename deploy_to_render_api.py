#!/usr/bin/env python3
"""
Deploy AI Agents to Render.com using Render API

This script uses the Render API to create a web service for the AI Agents platform.
Reads configuration from .env.master and creates the service programmatically.

Requirements:
    - RENDER_API_KEY in .env.master
    - GitHub repository already pushed (gerardovsa/Ai_Agents, V2_clean branch)
    - All API keys configured in .env.master

Usage:
    python deploy_to_render_api.py
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent / '.env.master'
load_dotenv(env_path)

# Render API Configuration
RENDER_API_KEY = os.getenv('RENDER_API_KEY')
RENDER_API_BASE = "https://api.render.com/v1"

if not RENDER_API_KEY:
    print("❌ Error: RENDER_API_KEY not found in .env.master")
    sys.exit(1)

# GitHub Repository Configuration
GITHUB_REPO_URL = "https://github.com/gerardovsa/Ai_Agents"
GITHUB_BRANCH = "V2_clean"

# Service Configuration
SERVICE_NAME = "ai-agents-backend"
SERVICE_TYPE = "web_service"
REGION = "oregon"  # Oregon (US West)
PLAN = "starter"  # API doesn't support 'free' - use 'starter' then downgrade in dashboard
PYTHON_VERSION = "3.11"

# Environment Variables from .env.master
ENV_VARS = {
    # AI Provider Keys
    "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY", ""),
    "ANTHROPIC_KEYS": os.getenv("ANTHROPIC_KEYS", ""),
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
    "OPENAI_KEYS": os.getenv("OPENAI_KEYS", ""),
    "DEEPSEEK_API_KEY_1": os.getenv("DEEPSEEK_API_KEY_1", ""),
    "DEEPSEEK_KEYS": os.getenv("DEEPSEEK_KEYS", ""),
    
    # Microsoft 365 OAuth
    "MICROSOFT_CLIENT_ID": os.getenv("MICROSOFT_CLIENT_ID", ""),
    "MICROSOFT_CLIENT_SECRET": os.getenv("MICROSOFT_CLIENT_SECRET", ""),
    "MICROSOFT_TENANT_ID": os.getenv("MICROSOFT_TENANT_ID", "common"),
    
    # Google OAuth (Note: Service account JSON should be added as secret file)
    "GOOGLE_CLIENT_ID": os.getenv("GOOGLE_CLIENT_ID", ""),
    "GOOGLE_CLIENT_SECRET": os.getenv("GOOGLE_CLIENT_SECRET", ""),
    
    # Platform API Keys
    "RENDER_API_KEY": os.getenv("RENDER_API_KEY", ""),
    "CLOUDFLARE_API_KEY": os.getenv("CLOUDFLARE_API_KEY", ""),
    "SUPABASE_URL": os.getenv("SUPABASE_URL", ""),
    "SUPABASE_KEY": os.getenv("SUPABASE_KEY", ""),
    "STRIPE_API_KEY": os.getenv("STRIPE_API_KEY", ""),
    "TWILIO_ACCOUNT_SID": os.getenv("TWILIO_ACCOUNT_SID", ""),
    "TWILIO_AUTH_TOKEN": os.getenv("TWILIO_AUTH_TOKEN", ""),
    
    # Flask Configuration
    "FLASK_ENV": "production",
    "PORT": "10000",
    "PYTHONUNBUFFERED": "1",
    "SECRET_KEY": os.getenv("SECRET_KEY", "change-me-in-production-" + os.urandom(16).hex()),
}

# Remove empty values
ENV_VARS = {k: v for k, v in ENV_VARS.items() if v}


def make_render_request(method: str, endpoint: str, **kwargs):
    """Make authenticated request to Render API"""
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {RENDER_API_KEY}'
    }
    
    url = f"{RENDER_API_BASE}/{endpoint.lstrip('/')}"
    response = requests.request(method, url, headers=headers, **kwargs)
    
    try:
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as e:
        print(f"❌ API Error: {e}")
        print(f"Response: {response.text}")
        raise


def list_services():
    """List all existing Render services"""
    print("📋 Fetching existing services...")
    try:
        result = make_render_request('GET', 'services', params={'limit': 100})
        services = result if isinstance(result, list) else result.get('data', [])
        print(f"✅ Found {len(services)} existing services")
        return services
    except Exception as e:
        print(f"⚠️  Warning: Could not list services: {e}")
        return []


def check_service_exists(service_name: str) -> dict:
    """Check if service with name already exists"""
    services = list_services()
    for item in services:
        service = item.get('service', item)
        if service.get('name') == service_name or service.get('slug') == service_name:
            print(f"⚠️  Service '{service_name}' already exists!")
            print(f"   ID: {service.get('id')}")
            print(f"   URL: {service.get('serviceDetails', {}).get('url', 'N/A')}")
            return service
    return None


def create_web_service():
    """Create new web service on Render"""
    print(f"\n🚀 Creating Render Web Service: {SERVICE_NAME}")
    print(f"   Repository: {GITHUB_REPO_URL}")
    print(f"   Branch: {GITHUB_BRANCH}")
    print(f"   Region: {REGION}")
    print(f"   Plan: {PLAN}")
    
    # Check if service already exists
    existing = check_service_exists(SERVICE_NAME)
    if existing:
        choice = input("\nService exists. Update it? (y/n): ").strip().lower()
        if choice == 'y':
            return update_service(existing['id'])
        else:
            print("❌ Deployment cancelled")
            return None
    
    # Prepare environment variables for API
    env_vars_list = [
        {"key": key, "value": value}
        for key, value in ENV_VARS.items()
    ]
    
    # Get owner ID from existing services
    services = list_services()
    owner_id = None
    if services:
        first_service = services[0].get('service', services[0])
        owner_id = first_service.get('ownerId')
    
    if not owner_id:
        print("❌ Error: Could not determine owner ID from existing services")
        return None
    
    print(f"   Owner ID: {owner_id}")
    
    # Service creation payload (matching Render API structure)
    payload = {
        "type": SERVICE_TYPE,
        "name": SERVICE_NAME,
        "ownerId": owner_id,
        "repo": GITHUB_REPO_URL,
        "branch": GITHUB_BRANCH,
        "autoDeploy": "yes",
        "serviceDetails": {
            "env": "python",
            "runtime": "python",
            "plan": PLAN,
            "region": REGION,
            "pullRequestPreviewsEnabled": "no",
            "envSpecificDetails": {
                "buildCommand": "pip install -r requirements.txt",
                "startCommand": "python AI_infrastructure/flask_app.py",
            },
            "envVars": env_vars_list,
        },
    }
    
    print(f"\n📦 Payload preview:")
    print(f"   Environment Variables: {len(env_vars_list)} configured")
    print(f"   Build Command: {payload['serviceDetails']['envSpecificDetails']['buildCommand']}")
    print(f"   Start Command: {payload['serviceDetails']['envSpecificDetails']['startCommand']}")
    
    try:
        print("\n🔄 Creating service via Render API...")
        result = make_render_request('POST', 'services', json=payload)
        
        service = result.get('service', result)
        service_id = service.get('id')
        service_url = service.get('serviceDetails', {}).get('url')
        
        print(f"\n✅ Service created successfully!")
        print(f"   Service ID: {service_id}")
        print(f"   Service URL: {service_url}")
        print(f"   Dashboard: https://dashboard.render.com/web/{service_id}")
        
        print(f"\n⏳ Render is now building and deploying your service...")
        print(f"   This may take 5-10 minutes for the first deploy")
        print(f"   Monitor progress: https://dashboard.render.com/web/{service_id}")
        
        print(f"\n📝 Next Steps:")
        print(f"   1. Monitor deployment in Render dashboard")
        print(f"   2. Update OAuth redirect URLs:")
        print(f"      - Microsoft Azure: {service_url}/api/auth/microsoft/callback")
        print(f"      - Google Console: {service_url}/api/auth/google/callback")
        print(f"   3. Test health endpoint: {service_url}/health")
        print(f"   4. Test agent endpoint: {service_url}/api/agent/query")
        
        return service
        
    except Exception as e:
        print(f"\n❌ Failed to create service: {e}")
        return None


def update_service(service_id: str):
    """Update existing service with new environment variables"""
    print(f"\n🔄 Updating service: {service_id}")
    
    env_vars_list = [
        {"key": key, "value": value}
        for key, value in ENV_VARS.items()
    ]
    
    try:
        result = make_render_request(
            'PUT', 
            f'services/{service_id}/env-vars',
            json={"envVars": env_vars_list}
        )
        print(f"✅ Environment variables updated!")
        print(f"   Updated {len(env_vars_list)} variables")
        
        # Trigger new deploy
        print(f"\n🔄 Triggering new deployment...")
        deploy_result = make_render_request(
            'POST',
            f'services/{service_id}/deploys',
            json={"clearCache": "do_not_clear"}
        )
        
        deploy_id = deploy_result.get('deploy', {}).get('id')
        print(f"✅ Deployment triggered: {deploy_id}")
        print(f"   Monitor: https://dashboard.render.com/web/{service_id}")
        
        return result
        
    except Exception as e:
        print(f"❌ Failed to update service: {e}")
        return None


def main():
    """Main deployment function"""
    print("=" * 60)
    print("🚀 AI Agents - Render.com API Deployment")
    print("=" * 60)
    
    # Validate prerequisites
    print("\n✅ Checking prerequisites...")
    print(f"   RENDER_API_KEY: {'✅ Found' if RENDER_API_KEY else '❌ Missing'}")
    print(f"   ANTHROPIC_API_KEY: {'✅ Found' if ENV_VARS.get('ANTHROPIC_API_KEY') else '⚠️  Missing'}")
    print(f"   MICROSOFT_CLIENT_ID: {'✅ Found' if ENV_VARS.get('MICROSOFT_CLIENT_ID') else '⚠️  Missing'}")
    print(f"   GitHub Repo: {GITHUB_REPO_URL}")
    print(f"   GitHub Branch: {GITHUB_BRANCH}")
    
    if not RENDER_API_KEY:
        print("\n❌ Cannot proceed without RENDER_API_KEY")
        sys.exit(1)
    
    # Create or update service
    service = create_web_service()
    
    if service:
        print("\n" + "=" * 60)
        print("✅ DEPLOYMENT INITIATED SUCCESSFULLY!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ DEPLOYMENT FAILED")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
