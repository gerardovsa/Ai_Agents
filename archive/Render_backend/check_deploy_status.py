"""Check deployment status"""

import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from render_api_client import RenderAPIClient

SERVICE_ID = 'srv-d47gjbm3jp1c73c0e6m0'
DEPLOY_ID = 'dep-d47gtsk9c44c73c6ltu0'

api_key = os.getenv('RENDER_API_KEY', 'rnd_hTZfWT0aHJLeX925X5sIiY5PxWiu')
client = RenderAPIClient(api_key)

print("=" * 80)
print("  DEPLOYMENT STATUS CHECK")
print("=" * 80)
print(f"\nService ID: {SERVICE_ID}")
print(f"Deploy ID: {DEPLOY_ID}")

# Get latest deploy
deploys = client.list_deploys(SERVICE_ID, limit=1)
if deploys:
    deploy = deploys[0]['deploy']
    
    print(f"\n📊 Latest Deployment:")
    print(f"   Status: {deploy['status']}")
    print(f"   Started: {deploy['startedAt']}")
    print(f"   Trigger: {deploy['trigger']}")
    
    if deploy.get('finishedAt'):
        print(f"   Finished: {deploy['finishedAt']}")
    
    # Status indicators
    if deploy['status'] == 'live':
        print("\n✅ DEPLOYMENT SUCCESSFUL!")
        print(f"\n🌐 Service URL: https://ai-agents-backend-singapore.onrender.com")
        print(f"\n🧪 Test health endpoint:")
        print(f"   curl https://ai-agents-backend-singapore.onrender.com/health")
    elif deploy['status'] == 'build_in_progress':
        print("\n⏳ Build in progress... (Docker build takes 5-10 minutes)")
        print(f"   Check again in a few minutes")
    elif deploy['status'] == 'update_failed':
        print("\n❌ Deployment failed!")
        print(f"   Check logs at: https://dashboard.render.com/web/{SERVICE_ID}")
    else:
        print(f"\n⚠️  Status: {deploy['status']}")
        print(f"   Monitor at: https://dashboard.render.com/web/{SERVICE_ID}")

else:
    print("\n❌ No deployments found")

print("\n" + "=" * 80)
