"""Get detailed service information"""

import os
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from render_api_client import RenderAPIClient

SERVICE_ID = 'srv-d47gjbm3jp1c73c0e6m0'

api_key = os.getenv('RENDER_API_KEY', 'rnd_hTZfWT0aHJLeX925X5sIiY5PxWiu')
client = RenderAPIClient(api_key)

print("=" * 80)
print("  SERVICE DETAILS")
print("=" * 80)

service = client.get_service(SERVICE_ID)

print(f"\n📦 Service: {service['name']}")
print(f"   ID: {service['id']}")
print(f"   Type: {service.get('type')}")

details = service.get('serviceDetails', {})
print(f"\n🔧 Configuration:")
print(f"   Environment: {details.get('env')}")
print(f"   Region: {details.get('region')}")
print(f"   Plan: {details.get('plan')}")
print(f"   Branch: {service.get('branch')}")
print(f"   Auto Deploy: {service.get('autoDeploy')}")

print(f"\n🌐 URLs:")
print(f"   Service URL: {details.get('url')}")
print(f"   Dashboard: https://dashboard.render.com/web/{SERVICE_ID}")

# Get environment variables
env_vars = details.get('envVars', [])
print(f"\n🔐 Environment Variables: {len(env_vars)} configured")
for var in env_vars[:5]:  # Show first 5
    key = var.get('key')
    value_preview = var.get('value', '')[:20] + '...' if len(var.get('value', '')) > 20 else var.get('value', '')
    print(f"   ✓ {key}: {value_preview}")
if len(env_vars) > 5:
    print(f"   ... and {len(env_vars) - 5} more")

# Get recent deploys
print(f"\n📊 Recent Deployments:")
deploys = client.list_deploys(SERVICE_ID, limit=3)
for item in deploys:
    deploy = item['deploy']
    status_icon = "✅" if deploy['status'] == 'live' else "❌" if 'failed' in deploy['status'] else "⏳"
    print(f"   {status_icon} {deploy['id']}: {deploy['status']}")
    print(f"      Started: {deploy['startedAt']}")
    if deploy.get('finishedAt'):
        print(f"      Finished: {deploy['finishedAt']}")

print("\n" + "=" * 80)
