"""List all Render services"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from render_api_client import RenderAPIClient

api_key = os.getenv('RENDER_API_KEY', 'rnd_hTZfWT0aHJLeX925X5sIiY5PxWiu')
client = RenderAPIClient(api_key)

print("=" * 80)
print("  RENDER SERVICES")
print("=" * 80)

services = client.list_services(limit=10)

for item in services:
    service = item['service']
    details = service.get('serviceDetails', {})
    
    print(f"\n📦 {service['name']}")
    print(f"   ID: {service['id']}")
    print(f"   Type: {service.get('type', 'unknown')}")
    print(f"   Region: {details.get('region', 'unknown')}")
    print(f"   Branch: {service.get('branch', 'unknown')}")
    print(f"   Status: {details.get('serviceStatus', 'unknown')}")
    print(f"   URL: {details.get('url', 'N/A')}")

print("\n" + "=" * 80)
