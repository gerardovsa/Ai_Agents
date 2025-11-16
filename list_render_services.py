import requests
import json

RENDER_API_KEY = "rnd_hTZfWT0aHJLeX925X5sIiY5PxWiu"

headers = {
    'Authorization': f'Bearer {RENDER_API_KEY}',
    'Accept': 'application/json'
}

print("Fetching Render services...")
response = requests.get('https://api.render.com/v1/services', headers=headers)

if response.status_code == 200:
    services = response.json()
    print(f"\nFound {len(services)} service(s):\n")
    for i, service in enumerate(services, 1):
        service_data = service.get('service', service)
        print(f"{i}. Name: {service_data.get('name')}")
        print(f"   ID: {service_data.get('id')}")
        print(f"   Type: {service_data.get('type')}")
        print(f"   Status: {service_data.get('suspended', 'active')}")
        print()
else:
    print(f"Error: HTTP {response.status_code}")
    print(response.text)
