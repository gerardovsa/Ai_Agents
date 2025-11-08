"""Trigger deployment for Render service"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from render_api_client import RenderAPIClient

SERVICE_ID = 'srv-d47gjbm3jp1c73c0e6m0'

api_key = os.getenv('RENDER_API_KEY', 'rnd_hTZfWT0aHJLeX925X5sIiY5PxWiu')
client = RenderAPIClient(api_key)

print(f"🚀 Triggering deployment for service: {SERVICE_ID}")
result = client.trigger_deploy(SERVICE_ID)

print(f"\n✅ Deployment triggered successfully!")
print(f"   Deploy ID: {result.get('id')}")
print(f"   Status: {result.get('status')}")
print(f"\n⏳ Docker build will take 5-10 minutes...")
print(f"\n📊 Monitor at: https://dashboard.render.com/web/{SERVICE_ID}")
