"""
Clone Render Deployment for v10 Branch

This script clones your existing AI Agents Render deployment and creates 
a new v10 deployment with the v10 branch.

Usage:
    python clone_render_deployment_v10.py

Requirements:
    - Render API key in environment: RENDER_API_KEY
    - Or authenticated via: render login
"""

import sys
import os

# Add Render_backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Render_backend'))

from render_api_client import RenderAPIClient


def clone_deployment_for_v10():
    """Clone existing deployment for v10 branch"""
    
    print("🚀 Cloning AI Agents Render Deployment for v10")
    print("=" * 60)
    
    # Initialize Render API client
    api_key = os.getenv('RENDER_API_KEY')
    if not api_key:
        print("❌ ERROR: RENDER_API_KEY environment variable not set")
        print("\nGet your API key from:")
        print("https://dashboard.render.com/account/api-keys")
        print("\nThen set it:")
        print("  $env:RENDER_API_KEY='your-api-key-here'")
        return False
    
    client = RenderAPIClient(api_key)
    
    try:
        # Step 1: List all services to find the v9 deployment
        print("\n📋 Step 1: Finding existing v9 deployment...")
        services = client.list_services()
        
        # Find v9 service (look for ai-agents-backend or similar)
        v9_service = None
        for item in services:
            service = item.get('service', {})
            name = service.get('name', '')
            # Look for service with "ai-agents" in name
            if 'ai-agents' in name.lower() and 'v10' not in name.lower():
                v9_service = service
                print(f"✅ Found v9 service: {name} (ID: {service.get('id')})")
                break
        
        if not v9_service:
            print("❌ ERROR: Could not find existing AI Agents service")
            print("\nAvailable services:")
            for item in services:
                service = item.get('service', {})
                print(f"  - {service.get('name')} (ID: {service.get('id')})")
            return False
        
        # Step 2: Get detailed service configuration
        print("\n📦 Step 2: Fetching service configuration...")
        v9_id = v9_service.get('id')
        v9_details = client.get_service(v9_id)
        
        # Step 3: Create v10 service configuration
        print("\n🔧 Step 3: Creating v10 service configuration...")
        
        # Get service details from v9
        v9_service_details = v9_details.get('serviceDetails', {})
        
        # Build service details for v10
        v10_service_details = {
            "env": v9_details.get('env', 'docker'),
            "region": v9_details.get('region', 'singapore'),
            "plan": v9_details.get('plan', 'starter'),
            "pullRequestPreviewsEnabled": v9_service_details.get('pullRequestPreviewsEnabled', 'no'),
            "healthCheckPath": v9_service_details.get('healthCheckPath', '/health')
        }
        
        # Add Docker configuration
        if v9_details.get('env') == 'docker':
            v10_service_details['dockerfilePath'] = v9_service_details.get('dockerfilePath', './AI_infrastructure/Dockerfile')
            v10_service_details['dockerContext'] = v9_service_details.get('dockerContext', '.')
            if v9_service_details.get('dockerCommand'):
                v10_service_details['dockerCommand'] = v9_service_details.get('dockerCommand')
        
        # Copy environment variables
        env_vars = v9_details.get('envVars', [])
        if env_vars:
            v10_service_details['envVars'] = env_vars
            print(f"   ✅ Copied {len(env_vars)} environment variables")
        
        # Build top-level config
        v10_config = {
            "type": "web_service",
            "name": "ai-agents-v10",  # New name for v10
            "ownerID": v9_details.get('ownerId'),
            "repo": v9_details.get('repo', 'https://github.com/gerardovsa/AI_agents'),
            "autoDeploy": "yes",
            "branch": "v10",  # ⚠️ CHANGED FROM v9 TO v10
            "serviceDetails": v10_service_details
        }
        
        print("\n📝 v10 Configuration:")
        print(f"   Name: {v10_config['name']}")
        print(f"   Branch: {v10_config['branch']}")
        print(f"   Region: {v10_service_details['region']}")
        print(f"   Plan: {v10_service_details['plan']}")
        print(f"   Env: {v10_service_details['env']}")
        
        # Step 4: Create the v10 service
        print("\n🚀 Step 4: Creating v10 deployment...")
        print("   (This may take a few moments...)")
        
        # Debug: Print config being sent
        import json
        print("\n🔍 DEBUG - Config being sent:")
        print(json.dumps(v10_config, indent=2))
        
        new_service = client.create_service(v10_config)
        
        # Response might have service wrapped in dict
        service_data = new_service.get('service', new_service)
        
        print("\n✅ SUCCESS! v10 deployment created!")
        print("=" * 60)
        print(f"Service ID: {service_data.get('id')}")
        print(f"Name: {service_data.get('name')}")
        
        # Get URL from service details
        service_details = service_data.get('serviceDetails', {})
        url = service_details.get('url', 'Will be available after first deploy')
        print(f"URL: {url}")
        
        print("\n📊 Dashboard:")
        print(f"https://dashboard.render.com/web/{service_data.get('id')}")
        
        # Note about disk
        if v9_details.get('disk'):
            print("\n⚠️  NOTE: Disk volumes need to be added manually:")
            print("   1. Go to service settings in Render dashboard")
            print("   2. Add a new disk: ai-agents-v10-data (10GB)")
            print(f"   3. Mount path: {v9_details.get('disk', {}).get('mountPath', '/data')}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        print("\n🔍 Full traceback:")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = clone_deployment_for_v10()
    sys.exit(0 if success else 1)
