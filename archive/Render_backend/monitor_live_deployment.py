"""
Monitor Live Deployment - Real-time deployment monitoring with error details
"""

import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from render_api_client import RenderAPIClient

SERVICE_ID = 'srv-d47nfr2li9vc738s0uc0'

def print_section(title):
    """Print section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")

def get_deploy_details(client, deploy_id):
    """Get detailed deployment information"""
    try:
        # Try to get deploy details (may not be available in API)
        deploys = client.list_deploys(SERVICE_ID, limit=10)
        for item in deploys:
            deploy = item.get('deploy', {})
            if deploy.get('id') == deploy_id:
                return deploy
        return None
    except:
        return None

def monitor_deployment(watch_mode=False):
    """Monitor deployment status with detailed error reporting"""
    
    api_key = os.getenv('RENDER_API_KEY', 'rnd_hTZfWT0aHJLeX925X5sIiY5PxWiu')
    client = RenderAPIClient(api_key)
    
    print_section("RENDER DEPLOYMENT MONITOR")
    print(f"Service ID: {SERVICE_ID}")
    print(f"Dashboard: https://dashboard.render.com/web/{SERVICE_ID}")
    
    # Get service details
    try:
        service = client.get_service(SERVICE_ID)
        service_details = service.get('serviceDetails', {})
        
        print(f"\n📦 Service: {service.get('name')}")
        print(f"   Region: {service_details.get('region')}")
        print(f"   Plan: {service_details.get('plan')}")
        print(f"   URL: {service_details.get('url', 'N/A')}")
        print(f"   Env: {service_details.get('env')}")
        
        # Check environment variables
        env_vars = service_details.get('envVars', [])
        print(f"\n🔐 Environment Variables: {len(env_vars)} configured")
        
        # List critical env vars
        critical_vars = [
            'ANTHROPIC_API_KEY',
            'OPENAI_API_KEY',
            'DEEPSEEK_API_KEY_1',
            'SECRET_KEY',
            'GOOGLE_OAUTH_CLIENT_ID',
            'MICROSOFT_CLIENT_ID'
        ]
        
        missing_vars = []
        for var in critical_vars:
            found = any(ev.get('key') == var for ev in env_vars)
            status = "✅" if found else "❌"
            print(f"   {status} {var}")
            if not found:
                missing_vars.append(var)
        
        if missing_vars:
            print(f"\n⚠️  Missing {len(missing_vars)} critical environment variables!")
            print(f"   Add these in dashboard: https://dashboard.render.com/web/{SERVICE_ID}")
    
    except Exception as e:
        print(f"⚠️  Could not fetch service details: {e}")
    
    # Get recent deployments
    print_section("RECENT DEPLOYMENTS")
    
    try:
        deploys = client.list_deploys(SERVICE_ID, limit=5)
        
        if not deploys:
            print("No deployments found.")
            return
        
        for i, item in enumerate(deploys, 1):
            deploy = item.get('deploy', {})
            deploy_id = deploy.get('id')
            status = deploy.get('status')
            created = deploy.get('createdAt')
            finished = deploy.get('finishedAt', 'In progress...')
            commit = deploy.get('commit', {})
            commit_msg = commit.get('message', 'N/A')
            
            # Status emoji
            status_map = {
                'live': '✅',
                'build_failed': '❌',
                'update_failed': '❌',
                'build_in_progress': '🔄',
                'canceled': '🚫'
            }
            emoji = status_map.get(status, '❓')
            
            print(f"{i}. {emoji} Deploy: {deploy_id}")
            print(f"   Status: {status}")
            print(f"   Created: {created}")
            print(f"   Finished: {finished}")
            print(f"   Commit: {commit_msg[:60]}")
            
            # If this is the latest deploy and it failed, show details
            if i == 1 and status in ['build_failed', 'update_failed']:
                print(f"\n   ⚠️  DEPLOYMENT FAILED")
                print(f"   Common causes:")
                print(f"   - Missing environment variables (check above)")
                print(f"   - Build errors (missing dependencies)")
                print(f"   - Health check timeout (app doesn't start)")
                print(f"   - Port configuration (must use $PORT)")
                print(f"\n   📊 View full logs in dashboard:")
                print(f"   https://dashboard.render.com/web/{SERVICE_ID}")
            
            print()
    
    except Exception as e:
        print(f"❌ Error getting deployments: {e}")
        import traceback
        traceback.print_exc()
    
    # Try to get logs (may not work via API)
    print_section("DEPLOYMENT LOGS")
    print("⚠️  Note: Render API doesn't expose build logs.")
    print("   View logs in dashboard: https://dashboard.render.com/web/{SERVICE_ID}")
    print("\n   Or use Render CLI:")
    print(f"   render logs {SERVICE_ID} --tail")
    
    # Check if we should watch
    if watch_mode:
        print_section("WATCH MODE")
        print("Monitoring deployment every 30 seconds...")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                time.sleep(30)
                
                # Get latest deploy
                deploys = client.list_deploys(SERVICE_ID, limit=1)
                if deploys:
                    deploy = deploys[0].get('deploy', {})
                    status = deploy.get('status')
                    
                    print(f"[{time.strftime('%H:%M:%S')}] Status: {status}")
                    
                    if status == 'live':
                        print("\n✅ DEPLOYMENT SUCCESSFUL!")
                        print(f"   Service URL: https://ai-agents-backend-singapore.onrender.com")
                        print(f"\n   Test health endpoint:")
                        print(f"   curl https://ai-agents-backend-singapore.onrender.com/health")
                        break
                    elif status in ['build_failed', 'update_failed']:
                        print(f"\n❌ DEPLOYMENT FAILED")
                        print(f"   Check dashboard: https://dashboard.render.com/web/{SERVICE_ID}")
                        break
        except KeyboardInterrupt:
            print("\n\n⏹️  Monitoring stopped")
    
    print_section("NEXT STEPS")
    
    # Check latest deploy status and provide guidance
    try:
        deploys = client.list_deploys(SERVICE_ID, limit=1)
        if deploys:
            latest = deploys[0].get('deploy', {})
            status = latest.get('status')
            
            if status == 'live':
                print("✅ Service is LIVE!")
                print("\n🧪 Test commands:")
                print("   curl https://ai-agents-backend-singapore.onrender.com/health")
                print("   python Render_backend/test_deployment.py https://ai-agents-backend-singapore.onrender.com")
            
            elif status in ['build_failed', 'update_failed']:
                print("❌ Deployment failed. Recommended actions:")
                print("\n1. Check dashboard logs:")
                print("   https://dashboard.render.com/web/{SERVICE_ID}")
                print("\n2. Verify environment variables are set:")
                print("   - ANTHROPIC_API_KEY")
                print("   - OPENAI_API_KEY")
                print("   - DEEPSEEK_API_KEY_1")
                print("   - SECRET_KEY (generate: python -c \"import secrets; print(secrets.token_hex(32))\")")
                print("   - GOOGLE_OAUTH_CLIENT_ID")
                print("   - GOOGLE_OAUTH_CLIENT_SECRET")
                print("   - MICROSOFT_CLIENT_ID")
                print("   - MICROSOFT_CLIENT_SECRET")
                print("\n3. Trigger new deployment:")
                print("   python Render_backend/trigger_deploy.py")
                print("\n4. Or commit a change and push:")
                print("   git commit --allow-empty -m \"Trigger redeploy\"")
                print("   git push origin v3")
            
            elif status == 'build_in_progress':
                print("🔄 Build in progress...")
                print("\nMonitor with:")
                print("   python Render_backend/monitor_live_deployment.py --watch")
                print("\nOr check dashboard:")
                print(f"   https://dashboard.render.com/web/{SERVICE_ID}")
    
    except Exception as e:
        print(f"Could not determine next steps: {e}")
    
    print("\n" + "=" * 80 + "\n")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Monitor Render deployment')
    parser.add_argument('--watch', action='store_true', help='Watch deployment in real-time')
    args = parser.parse_args()
    
    monitor_deployment(watch_mode=args.watch)
