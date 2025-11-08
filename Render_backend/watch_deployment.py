"""
Watch deployment until complete - Simple continuous monitoring
"""
import os
import time
import requests
from render_api_client import RenderAPIClient

SERVICE_ID = 'srv-d47nfr2li9vc738s0uc0'
api_key = os.getenv('RENDER_API_KEY', 'rnd_hTZfWT0aHJLeX925X5sIiY5PxWiu')
client = RenderAPIClient(api_key)

print("=" * 70)
print("WATCHING DEPLOYMENT - Press Ctrl+C to stop")
print("=" * 70)
print(f"\nService: {SERVICE_ID}")
print(f"Dashboard: https://dashboard.render.com/web/{SERVICE_ID}")
print(f"URL: https://ai-agents-backend-singapore.onrender.com\n")

last_status = None
check_count = 0

while True:
    check_count += 1
    try:
        # Get latest deployment
        deploys = client.list_deploys(SERVICE_ID, limit=1)
        if deploys:
            deploy = deploys[0].get('deploy', {})
            deploy_id = deploy.get('id', 'unknown')
            status = deploy.get('status', 'unknown')
            created = deploy.get('createdAt', '')
            finished = deploy.get('finishedAt', 'In progress...')
            
            # Only print if status changed
            if status != last_status:
                timestamp = time.strftime('%H:%M:%S')
                print(f"[{timestamp}] Check #{check_count}: {status}")
                last_status = status
                
                # If completed, try health check
                if status == 'live':
                    print("\n" + "=" * 70)
                    print("DEPLOYMENT SUCCESSFUL!")
                    print("=" * 70)
                    print(f"\nTesting health endpoint...")
                    
                    try:
                        response = requests.get(
                            'https://ai-agents-backend-singapore.onrender.com/health',
                            timeout=10
                        )
                        print(f"Status Code: {response.status_code}")
                        if response.status_code == 200:
                            print(f"Response: {response.json()}")
                            print("\nSUCCESS! Service is healthy and running!")
                        else:
                            print(f"Response: {response.text[:200]}")
                    except Exception as e:
                        print(f"Health check error: {e}")
                        print("Service may still be starting up...")
                    
                    print("\n" + "=" * 70)
                    break
                    
                elif status == 'update_failed' or status == 'build_failed':
                    print("\n" + "=" * 70)
                    print("DEPLOYMENT FAILED")
                    print("=" * 70)
                    print(f"Deploy ID: {deploy_id}")
                    print(f"Status: {status}")
                    print(f"\nCheck logs in dashboard:")
                    print(f"https://dashboard.render.com/web/{SERVICE_ID}")
                    print("=" * 70)
                    break
            
        else:
            if last_status != 'no_deploys':
                print(f"No deployments found")
                last_status = 'no_deploys'
        
        # Wait before next check
        time.sleep(30)  # Check every 30 seconds
        
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped by user")
        break
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(30)
