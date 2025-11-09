#!/usr/bin/env python3
"""
Add Supabase Environment Variables to Render Service

This script adds the required Supabase credentials to your Render service
using the Render API. Run this after completing Supabase setup.

Usage:
    python add_supabase_env_vars.py
"""

import requests
import sys

# Render configuration
RENDER_API_KEY = "rnd_hTZfWT0aHJLeX925X5sIiY5PxWiu"
SERVICE_ID = "srv-d47nfr2li9vc738s0uc0"

print("\n" + "="*80)
print("SUPABASE ENVIRONMENT VARIABLES SETUP")
print("="*80 + "\n")

print("This script will add Supabase credentials to your Render service.")
print("Get these values from: Supabase Dashboard -> Settings -> Database\n")

# Get credentials from user
supabase_url = input("Supabase Project URL: ").strip()
supabase_key = input("Supabase Anon Key: ").strip()
supabase_db_url = input("Supabase Database URL: ").strip()

if not all([supabase_url, supabase_key, supabase_db_url]):
    print("\nError: All fields are required")
    sys.exit(1)

# Prepare environment variables
env_vars = {
    'USE_SUPABASE': 'true',
    'SUPABASE_URL': supabase_url,
    'SUPABASE_KEY': supabase_key,
    'SUPABASE_DB_URL': supabase_db_url
}

# API headers
headers = {
    'Authorization': f'Bearer {RENDER_API_KEY}',
    'Content-Type': 'application/json'
}

print("\n" + "="*80)
print("Adding environment variables to Render...")
print("="*80 + "\n")

# Add each variable
success_count = 0
fail_count = 0

for key, value in env_vars.items():
    # Display masked value for security
    display_value = value if key == 'USE_SUPABASE' else (value[:20] + '...' if len(value) > 20 else value)
    
    url = f'https://api.render.com/v1/services/{SERVICE_ID}/env-vars/{key}'
    
    try:
        response = requests.put(url, json={'value': value}, headers=headers)
        
        if response.status_code in [200, 201]:
            print(f"  SUCCESS {key}: {display_value}")
            success_count += 1
        else:
            print(f"  FAILED {key}: HTTP {response.status_code}")
            print(f"    Response: {response.text}")
            fail_count += 1
    
    except Exception as e:
        print(f"  FAILED {key}: {str(e)}")
        fail_count += 1

# Summary
print("\n" + "="*80)
print("RESULTS")
print("="*80)
print(f"\nSuccessful: {success_count}/{len(env_vars)}")
print(f"Failed: {fail_count}/{len(env_vars)}")

if fail_count == 0:
    print("\nSUCCESS All Supabase environment variables added!")
    print("\nNext steps:")
    print("1. Update render.yaml to remove persistent disk")
    print("2. Update Dockerfile to remove database file copying")
    print("3. Commit and push changes")
    print("4. Monitor deployment: python render_toolkit.py monitor")
    print("\n" + "="*80 + "\n")
    sys.exit(0)
else:
    print("\nWARNING Some variables failed to add")
    print("Check the error messages above")
    print("\n" + "="*80 + "\n")
    sys.exit(1)
