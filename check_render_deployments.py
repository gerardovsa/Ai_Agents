import requests
from datetime import datetime

RENDER_API_KEY = "rnd_hTZfWT0aHJLeX925X5sIiY5PxWiu"
SERVICE_ID = "srv-d4b2723uibrs73ff02t0"

headers = {
    'Authorization': f'Bearer {RENDER_API_KEY}',
    'Accept': 'application/json'
}

print("Fetching recent deployments...")
response = requests.get(
    f'https://api.render.com/v1/services/{SERVICE_ID}/deploys',
    headers=headers,
    params={'limit': 5}
)

if response.status_code == 200:
    deploys = response.json()
    print(f"\nLast {len(deploys)} deployment(s):\n")
    for i, deploy_wrapper in enumerate(deploys, 1):
        deploy = deploy_wrapper.get('deploy', deploy_wrapper)
        status = deploy.get('status', 'unknown')
        created = deploy.get('createdAt', 'unknown')
        deploy_id = deploy.get('id', 'unknown')
        
        # Parse timestamp
        try:
            dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
            time_str = dt.strftime('%Y-%m-%d %H:%M:%S UTC')
        except:
            time_str = created
        
        # Status emoji
        emoji = {
            'live': '🟢',
            'build_in_progress': '🔵',
            'update_in_progress': '🔵',
            'pre_deploy_in_progress': '🟡',
            'build_failed': '🔴',
            'canceled': '⚫'
        }.get(status, '⚪')
        
        print(f"{i}. {emoji} Status: {status}")
        print(f"   ID: {deploy_id}")
        print(f"   Created: {time_str}")
        print()
else:
    print(f"Error: HTTP {response.status_code}")
    print(response.text)
