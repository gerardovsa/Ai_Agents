#!/usr/bin/env python3
"""
Update Render Environment Variables for Supabase Session Pooler

This script updates the Render service to use Supabase Session Pooler
(IPv4 compatible) instead of direct connection.

Session Pooler Benefits:
- IPv4 compatible (works with Render)
- Better connection pooling
- More stable for international connections
"""

import requests
import sys

# Render configuration
RENDER_API_KEY = "rnd_hTZfWT0aHJLeX925X5sIiY5PxWiu"
SERVICE_ID = "srv-d4b2723uibrs73ff02t0"  # ai-agents-backend-singapore

# Supabase Session Pooler configuration (IPv4 compatible)
# Region: ap-southeast-2 (Sydney) - closest to Render Singapore deployment
# Pool mode: Session mode on port 5432
# Username format: postgres.projectref (required for pooler)
SUPABASE_DB_URL = "postgresql://postgres.ryoicrdifiqhqpsnjmdo:inhouseprint@aws-1-ap-southeast-2.pooler.supabase.com:5432/postgres"

# Other Supabase credentials (unchanged)
SUPABASE_URL = "https://wuwmvtslltqhaycyukxk.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind1d212dHNsbHRxaGF5Y3l1a3hrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczMTg2NDEwOSwiZXhwIjoyMDQ3NDQwMTA5fQ.KaJSjxREyUoMlqX1Y5hA_cZ10KtW20VNp8GhSc_TqHc"

print("\n" + "="*80)
print("UPDATING RENDER TO USE SUPABASE SESSION POOLER (IPv4)")
print("="*80 + "\n")

# Environment variables to update/add
env_vars = {
    'USE_SUPABASE': 'true',
    'SUPABASE_URL': SUPABASE_URL,
    'SUPABASE_SERVICE_KEY': SUPABASE_SERVICE_KEY,
    'SUPABASE_DB_URL': SUPABASE_DB_URL,
    'RENDER': 'true'  # Ensures Render-specific code paths are used
}

# API headers
headers = {
    'Authorization': f'Bearer {RENDER_API_KEY}',
    'Content-Type': 'application/json'
}

print("Environment variables to update:")
for key, value in env_vars.items():
    # Mask sensitive values
    if key in ['SUPABASE_SERVICE_KEY', 'SUPABASE_DB_URL']:
        display_value = value[:30] + '...' if len(value) > 30 else value
    else:
        display_value = value
    print(f"  {key}: {display_value}")

print("\n" + "-"*80)
print("Updating variables...")
print("-"*80 + "\n")

# Convert to array format for PATCH request
env_vars_array = [{"key": key, "value": value} for key, value in env_vars.items()]

# Update service with PATCH (updates all env vars at once)
url = f'https://api.render.com/v1/services/{SERVICE_ID}'
payload = {
    "serviceDetails": {
        "envVars": env_vars_array
    }
}

try:
    response = requests.patch(url, json=payload, headers=headers)
    
    if response.status_code in [200, 201]:
        print("  ✅ All environment variables updated successfully!")
        print("\n  Variables updated:")
        for var in env_vars_array:
            key = var['key']
            # Mask sensitive values
            if key in ['SUPABASE_SERVICE_KEY', 'SUPABASE_DB_URL']:
                display_value = var['value'][:30] + '...' if len(var['value']) > 30 else var['value']
            else:
                display_value = var['value']
            print(f"    ✓ {key}: {display_value}")
        
        success_count = len(env_vars)
        fail_count = 0
    else:
        print(f"  ❌ Failed to update service (HTTP {response.status_code})")
        print(f"     Response: {response.text}")
        success_count = 0
        fail_count = len(env_vars)
        
except Exception as e:
    print(f"  ❌ Exception occurred: {str(e)}")
    import traceback
    traceback.print_exc()
    success_count = 0
    fail_count = len(env_vars)

# Summary
print("\n" + "="*80)
print("RESULTS")
print("="*80)
print(f"\nSuccessful: {success_count}/{len(env_vars)}")
print(f"Failed: {fail_count}/{len(env_vars)}")

if fail_count == 0:
    print("\n🎉 SUCCESS! All environment variables updated!")
    print("\nRender is now configured to use Supabase Session Pooler (IPv4)")
    print("\nNext steps:")
    print("1. Trigger Render redeploy (automatic or manual)")
    print("2. Monitor deployment logs for successful Supabase connection")
    print("3. Test API endpoints to verify database connectivity")
    print("4. Verify data is accessible from Render deployment")
else:
    print(f"\n⚠️  WARNING: {fail_count} variable(s) failed to update")
    print("Please check errors above and retry or update manually via Render dashboard")
    sys.exit(1)
