"""
Trigger Render deploy with clear cache to pick up new databases
"""
import sys
sys.path.insert(0, 'Render_backend')

from render_api_client import RenderAPIClient

# Render credentials
API_KEY = "rnd_hTZfWT0aHJLeX925X5sIiY5PxWiu"
SERVICE_ID = "srv-d4b2723uibrs73ff02t0"

print("=" * 80)
print("TRIGGERING RENDER DEPLOY")
print("=" * 80)
print()
print(f"Service: ai-agents-backend-singapore")
print(f"Service ID: {SERVICE_ID}")
print(f"Action: Manual Deploy with Clear Cache")
print()

client = RenderAPIClient(API_KEY)

try:
    # Trigger deploy with cache clear
    print("Triggering deploy...")
    result = client.trigger_deploy(SERVICE_ID, clear_cache=True)
    
    print()
    print("[OK] Deploy triggered successfully!")
    print()
    print(f"Deploy ID: {result.get('id')}")
    print(f"Status: {result.get('status')}")
    print(f"Created: {result.get('createdAt')}")
    print()
    print("=" * 80)
    print("NEXT STEPS:")
    print("=" * 80)
    print()
    print("1. Wait 2-3 minutes for deploy to complete")
    print("2. Monitor at: https://dashboard.render.com/web/srv-d4b2723uibrs73ff02t0")
    print("3. Check logs for 'OAuth columns migration' messages")
    print("4. Test OAuth login at: https://ai-agents-backend-singapore.onrender.com")
    print()
    print("The new databases with OAuth columns should now be active!")
    print()
    
except Exception as e:
    print(f"[ERROR] Failed to trigger deploy: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
