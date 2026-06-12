"""Delete Render service"""
import os
import requests

SERVICE_ID = "srv-d47gjbm3jp1c73c0e6m0"
API_KEY = os.getenv('RENDER_API_KEY', 'rnd_hTZfWT0aHJLeX925X5sIiY5PxWiu')

print(f"Deleting service {SERVICE_ID}...")

url = f"https://api.render.com/v1/services/{SERVICE_ID}"
headers = {"Authorization": f"Bearer {API_KEY}"}

response = requests.delete(url, headers=headers)

if response.status_code in [200, 204]:
    print(f"Service deleted successfully!")
else:
    print(f"Delete status: {response.status_code}")
    print(f"Response: {response.text}")
