"""
Test Render API Client - Check Flask Service Status
"""

import sys
sys.path.insert(0, r'c:\Users\gpoli\GIT\In_House_SQL\G_Folder\tools')

from render_api_client import RenderAPIClient

# Initialize client with your API key
API_KEY = "rnd_hTZfWT0aHJLeX925X5sIiY5PxWiu"
client = RenderAPIClient(API_KEY)

print("=" * 80)
print("RENDER SERVICE DIAGNOSTICS")
print("=" * 80)

# Check Flask service
print("\n🔍 Checking Flask Service...")
flask_service = client.get_flask_service()

if flask_service:
    service_id = flask_service['id']
    print(f"\n Flask Service Found: {flask_service['name']}")
    print(f"   ID: {service_id}")
    
    # Get detailed status
    status = client.check_service_status(service_id)
    print(f"\n📊 Service Status:")
    print(f"   Suspended: {status['status']}")
    print(f"   Plan: {status['plan']}")
    print(f"   URL: {status['url']}")
    print(f"   Region: {status['region']}")
    print(f"   Runtime: {status['runtime']}")
    print(f"   Last Updated: {status['updated_at']}")
    
    # Check recent deploys
    print(f"\n📜 Recent Deploys:")
    try:
        deploys = client.list_deploys(service_id, limit=5)
        for item in deploys:
            deploy = item.get('deploy', {})
            print(f"   • {deploy.get('id')}: {deploy.get('status')} (Created: {deploy.get('createdAt')})")
    except Exception as e:
        print(f"   ⚠️  Could not fetch deploys: {e}")
    
    # Check if suspended
    if status['status'] != 'not_suspended':
        print(f"\n⚠️  WARNING: Service is {status['status']}!")
        print(f"   This is why Streamlit can't connect to Flask!")
        print(f"\n💡 To fix: Go to Render Dashboard and resume the service")
        print(f"   URL: https://dashboard.render.com/web/{service_id}")
    else:
        print(f"\n Service is running (not suspended)")
        print(f"\n🤔 If Streamlit still can't connect, check:")
        print(f"   1. Environment variables (FLASK_URL in Streamlit)")
        print(f"   2. CORS configuration in Flask")
        print(f"   3. Network/firewall issues")
        print(f"   4. Recent deploy failures")

else:
    print(" Flask service not found!")
    print("\n📋 Available services:")
    client.print_all_services()

# Check Streamlit service too
print("\n" + "=" * 80)
print("🔍 Checking Streamlit Service...")
streamlit_service = client.get_streamlit_service()

if streamlit_service:
    service_id = streamlit_service['id']
    status = client.check_service_status(service_id)
    print(f"\n Streamlit Service Found: {streamlit_service['name']}")
    print(f"   ID: {service_id}")
    print(f"   Status: {status['status']}")
    print(f"   Plan: {status['plan']}")
    print(f"   URL: {status['url']}")
else:
    print(" Streamlit service not found!")

print("\n" + "=" * 80)
print("DIAGNOSTIC COMPLETE")
print("=" * 80)
