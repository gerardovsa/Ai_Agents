"""List all Render services"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Render_backend'))
from render_api_client import RenderAPIClient

api_key = os.getenv('RENDER_API_KEY')
client = RenderAPIClient(api_key)
services = client.list_services()

print("\n🔍 Render Services:")
print("=" * 60)
for item in services:
    service = item.get('service', {})
    print(f"Name: {service.get('name')}")
    print(f"ID: {service.get('id')}")
    print(f"Branch: {service.get('branch', 'N/A')}")
    print(f"URL: {service.get('serviceDetails', {}).get('url', 'N/A')}")
    print("-" * 60)
