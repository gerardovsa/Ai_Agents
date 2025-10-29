"""
Monitor Streamlit Deploy Progress
"""

import sys
sys.path.insert(0, r'c:\Users\gpoli\GIT\In_House_SQL\G_Folder\Render_backend')

from render_api_client import RenderAPIClient
import time

API_KEY = "rnd_hTZfWT0aHJLeX925X5sIiY5PxWiu"
client = RenderAPIClient(API_KEY)

print("=" * 80)
print("MONITORING STREAMLIT DEPLOY PROGRESS")
print("=" * 80)

streamlit_service = client.get_streamlit_service()
service_id = streamlit_service['id']

print(f"\nService: {streamlit_service['name']} ({service_id})")
print(f"Watching for new deploys...\n")

last_deploy_id = None

for i in range(60):  # Check for 10 minutes (60 * 10 seconds)
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
                print(f"   ✅ LIVE! Deploy complete!")
                print(f"\n{'='*80}")
                print(f"DEPLOY SUCCESSFUL!")
                print(f"{'='*80}")
                print(f"\n✅ Streamlit URL: https://inhouseprint-streamlit.onrender.com")
                print(f"✅ FLASK_URL env var: https://inhouseprint-flask.onrender.com")
                print(f"\n🎉 NOW TEST THE CONNECTION:")
                print(f"   1. Visit: https://inhouseprint-streamlit.onrender.com")
                print(f"   2. Navigate to: 'Stock Management & Analytics' page")
                print(f"   3. It should now load Flask dashboard (no more 'Flask not running' error)")
                break
            elif status in ['build_failed', 'update_failed', 'canceled']:
                print(f"   ❌ DEPLOY FAILED: {status}")
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
