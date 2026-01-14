import requests

RENDER_API_KEY = "rnd_hTZfWT0aHJLeX925X5sIiY5PxWiu"
SERVICE_ID = "srv-d4b2723uibrs73ff02t0"

headers = {
    'Authorization': f'Bearer {RENDER_API_KEY}',
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

print("Triggering Render deployment...")
response = requests.post(
    f'https://api.render.com/v1/services/{SERVICE_ID}/deploys',
    headers=headers,
    json={'clearCache': 'do_not_clear'}  # Don't clear cache, just redeploy
)

if response.status_code in [200, 201]:
    deploy = response.json().get('deploy', response.json())
    print(f"\n✅ Deployment triggered successfully!")
    print(f"   Deploy ID: {deploy.get('id')}")
    print(f"   Status: {deploy.get('status')}")
    print(f"\n📊 Monitor deployment:")
    print(f"   Dashboard: https://dashboard.render.com/web/{SERVICE_ID}")
    print(f"   Logs: https://dashboard.render.com/web/{SERVICE_ID}/logs")
else:
    print(f"\n❌ Failed to trigger deployment: HTTP {response.status_code}")
    print(f"   Response: {response.text}")
