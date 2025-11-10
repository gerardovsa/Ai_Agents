"""
Monitor Render Flask Deploy Progress
"""

import sys
sys.path.insert(0, r'c:\Users\gpoli\GIT\In_House_SQL\G_Folder\tools')

from render_api_client import RenderAPIClient
import time

API_KEY = "rnd_hTZfWT0aHJLeX925X5sIiY5PxWiu"
client = RenderAPIClient(API_KEY)

print("=" * 80)
print("MONITORING FLASK DEPLOY PROGRESS")
print("=" * 80)

flask_service = client.get_flask_service()
service_id = flask_service['id']

print(f"\nService: {flask_service['name']} ({service_id})")
print(f"Watching for new deploys...\n")

last_deploy_id = None

for i in range(30):  # Check for 5 minutes (30 * 10 seconds)
    try:
        deploys = client.list_deploys(service_id, limit=1)
        if deploys:
            deploy = deploys[0].get('deploy', {})
            deploy_id = deploy.get('id')
            status = deploy.get('status')
            created = deploy.get('createdAt')
            
            if deploy_id != last_deploy_id:
                print(f"\n🚀 NEW DEPLOY DETECTED: {deploy_id}")
                print(f"   Status: {status}")
                print(f"   Created: {created}")
                last_deploy_id = deploy_id
            
            # Show status updates
            if status == 'build_in_progress':
                print(f"   🔨 Building... (check #{i+1})")
            elif status == 'update_in_progress':
                print(f"   🔄 Updating... (check #{i+1})")
            elif status == 'live':
                print(f"    LIVE! Deploy complete!")
                print(f"\n{'='*80}")
                print(f"DEPLOY SUCCESSFUL!")
                print(f"{'='*80}")
                print(f"\nFlask URL: https://inhouseprint-flask.onrender.com")
                print(f"Test the fix now in Streamlit!")
                break
            elif status in ['build_failed', 'update_failed', 'canceled']:
                print(f"    DEPLOY FAILED: {status}")
                print(f"\nCheck logs at: https://dashboard.render.com/web/{service_id}")
                break
            else:
                print(f"   Status: {status} (check #{i+1})")
        
        time.sleep(10)  # Wait 10 seconds between checks
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Monitoring stopped by user")
        break
    except Exception as e:
        print(f"   ⚠️  Error: {e}")
        time.sleep(10)

print("\n" + "=" * 80)
print("MONITORING COMPLETE")
print("=" * 80)
