"""
Update Render environment variable to use Supabase Session Pooler (IPv4)

This fixes the IPv6 connection issue on Render
"""

import requests
import sys
import getpass

def update_supabase_url():
    """Update SUPABASE_DB_URL in Render to use Session Pooler"""
    
    service_id = "srv-d4b2723uibrs73ff02t0"
    api_key = "rnd_hTZfWT0aHJLeX925X5sIiY5PxWiu"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    print("="*70)
    print("RENDER SUPABASE URL UPDATER")
    print("="*70)
    print("\nThis script will update SUPABASE_DB_URL to use the Session Pooler")
    print("(IPv4-only) instead of the direct database URL (IPv6).")
    print()
    
    # Get Supabase password
    print("Please enter your Supabase database password:")
    print("(Find it in: Supabase Dashboard → Settings → Database)")
    print()
    password = getpass.getpass("Password: ")
    
    if not password:
        print("\n❌ Password is required. Exiting.")
        sys.exit(1)
    
    # Build Session Pooler URL
    pooler_url = (
        f"postgresql://postgres.ryoicrdifiqhqpsnjmdo:{password}"
        f"@aws-0-us-east-1.pooler.supabase.com:6543/postgres"
    )
    
    print(f"\n{'='*70}")
    print("UPDATING ENVIRONMENT VARIABLE")
    print(f"{'='*70}")
    print(f"Service: {service_id}")
    print(f"Variable: SUPABASE_DB_URL")
    print(f"New Value: postgresql://postgres.ryoicrdifiqhqpsnjmdo:***@aws-0-us-east-1.pooler.supabase.com:6543/postgres")
    print()
    
    # Confirm before proceeding
    confirm = input("Proceed with update? (yes/no): ")
    if confirm.lower() != 'yes':
        print("\n❌ Update cancelled.")
        sys.exit(0)
    
    # Update environment variable via Render API
    url = f"https://api.render.com/v1/services/{service_id}/env-vars"
    
    # First, get current env vars to find the var ID
    print("\n🔍 Fetching current environment variables...")
    response = requests.get(url, headers=headers, timeout=10)
    
    if response.status_code != 200:
        print(f"❌ Failed to fetch env vars: {response.status_code}")
        print(f"Response: {response.text}")
        sys.exit(1)
    
    env_vars = response.json()
    
    # Find SUPABASE_DB_URL
    supabase_var = None
    for var in env_vars:
        if var.get('key') == 'SUPABASE_DB_URL':
            supabase_var = var
            break
    
    if supabase_var:
        # Update existing variable
        var_id = supabase_var['id']
        update_url = f"{url}/{var_id}"
        
        payload = {
            "key": "SUPABASE_DB_URL",
            "value": pooler_url
        }
        
        print(f"📝 Updating existing variable (ID: {var_id})...")
        response = requests.patch(update_url, json=payload, headers=headers, timeout=10)
    else:
        # Create new variable
        payload = {
            "key": "SUPABASE_DB_URL",
            "value": pooler_url
        }
        
        print(f"➕ Creating new variable...")
        response = requests.post(url, json=payload, headers=headers, timeout=10)
    
    # Check response
    if response.status_code in [200, 201]:
        print(f"\n✅ SUCCESS! Environment variable updated.")
        print(f"\nRender will automatically redeploy the service.")
        print(f"Monitor deployment at:")
        print(f"https://dashboard.render.com/web/{service_id}")
        print()
        print(f"Expected result:")
        print(f"  - No more IPv6 connection errors")
        print(f"  - Logs show: ✅ Connected to Supabase PostgreSQL")
        print(f"  - Chat endpoint returns 200 OK (not 500)")
        print()
    else:
        print(f"\n❌ FAILED to update environment variable")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        print()
        print(f"Manual update instructions:")
        print(f"1. Go to: https://dashboard.render.com/web/{service_id}")
        print(f"2. Click 'Environment' tab")
        print(f"3. Edit SUPABASE_DB_URL")
        print(f"4. Set to: {pooler_url.replace(password, '***')}")
        print(f"5. Save changes")
        sys.exit(1)


if __name__ == "__main__":
    try:
        update_supabase_url()
    except KeyboardInterrupt:
        print("\n\n❌ Update cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
