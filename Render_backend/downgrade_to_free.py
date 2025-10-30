#!/usr/bin/env python3
"""
Downgrade to Free Plan - Switch Render service from Starter to Free

This script updates a Render service to use the free plan instead of starter,
saving $7/month. Note: Free plan has limitations (sleep after 15min inactivity).
"""

import os
import sys
import json
import requests
from pathlib import Path
from dotenv import dotenv_values

def get_render_api_key():
    """Get Render API key from .env.master"""
    env_path = Path('.env.master')
    
    if not env_path.exists():
        print("❌ .env.master file not found")
        return None
    
    try:
        env_vars = dotenv_values(env_path, encoding='utf-8', errors='ignore')
        api_key = env_vars.get('RENDER_API_KEY')
        
        if not api_key:
            print("❌ RENDER_API_KEY not found in .env.master")
            return None
        
        return api_key
    except Exception as e:
        print(f"❌ Error reading .env.master: {e}")
        return None

def get_service_info(api_key, service_id):
    """Get current service information"""
    url = f"https://api.render.com/v1/services/{service_id}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"   {response.text}")
            return None
    except Exception as e:
        print(f"❌ Request error: {e}")
        return None

def downgrade_to_free(api_key, service_id):
    """Downgrade service to free plan"""
    url = f"https://api.render.com/v1/services/{service_id}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    # Payload to update service plan
    payload = {
        "plan": "free"
    }
    
    try:
        response = requests.patch(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            print("✅ Successfully downgraded to free plan")
            return True
        else:
            print(f"❌ Downgrade failed: {response.status_code}")
            print(f"   {response.text}")
            
            # Try alternative approach via dashboard
            print("\n💡 Alternative: Use Render Dashboard")
            print(f"   1. Open: https://dashboard.render.com/web/{service_id}")
            print("   2. Click 'Settings' tab")
            print("   3. Under 'Instance Type', select 'Free'")
            print("   4. Click 'Save Changes'")
            
            return False
    except Exception as e:
        print(f"❌ Request error: {e}")
        return False

def print_free_plan_limitations():
    """Print limitations of free plan"""
    print("\n" + "=" * 70)
    print("⚠️  Free Plan Limitations")
    print("=" * 70)
    
    print("\n🔴 Automatic Sleep:")
    print("   - Service sleeps after 15 minutes of inactivity")
    print("   - Cold start takes ~30 seconds on first request")
    print("   - Use a cron job to ping every 14 minutes to keep alive")
    
    print("\n🔴 Resource Limits:")
    print("   - 512 MB RAM (vs 2GB on Starter)")
    print("   - Shared CPU (vs dedicated)")
    print("   - Lower priority in queue")
    
    print("\n🔴 Build Minutes:")
    print("   - 500 build minutes/month (usually enough)")
    
    print("\n🟢 What's Still Free:")
    print("   - Automatic HTTPS")
    print("   - Custom domains (1)")
    print("   - Automatic deploys from Git")
    print("   - Environment variables")

def print_keep_alive_solution():
    """Print solution to keep free service alive"""
    print("\n" + "=" * 70)
    print("💡 Keep Service Alive (Prevent Sleep)")
    print("=" * 70)
    
    print("\n📋 Option 1: UptimeRobot (Recommended)")
    print("   1. Sign up at https://uptimerobot.com (free)")
    print("   2. Add new monitor:")
    print("      - Type: HTTP(s)")
    print("      - URL: https://your-service.onrender.com/health")
    print("      - Interval: 14 minutes")
    print("   3. Service will never sleep!")
    
    print("\n📋 Option 2: Cron Job")
    print("   - Add to crontab: */14 * * * * curl https://your-service.onrender.com/health")
    
    print("\n📋 Option 3: GitHub Actions")
    print("   - Create workflow to ping service every 14 minutes")
    print("   - Uses GitHub Actions free tier")

def main():
    print("=" * 70)
    print("💸 Downgrade to Free Plan")
    print("=" * 70)
    
    # Get API key
    api_key = get_render_api_key()
    if not api_key:
        return 1
    
    # Get service ID from command line or use default
    if len(sys.argv) > 1:
        service_id = sys.argv[1]
    else:
        service_id = "srv-d40tai15pdvs73ddh4m0"  # Default
        print(f"\nUsing default service ID: {service_id}")
    
    # Get current service info
    print("\n🔍 Checking current service plan...")
    service = get_service_info(api_key, service_id)
    
    if not service:
        print("❌ Could not fetch service information")
        return 1
    
    current_plan = service.get('plan', 'unknown')
    print(f"   Current plan: {current_plan}")
    
    # Check if already on free plan
    if current_plan == 'free':
        print("\n✅ Service is already on free plan!")
        return 0
    
    # Print limitations before downgrading
    print_free_plan_limitations()
    
    # Confirm downgrade
    print("\n" + "=" * 70)
    response = input("\n❓ Downgrade to free plan? (y/n): ")
    
    if response.lower() != 'y':
        print("\n❌ Downgrade cancelled")
        return 0
    
    # Perform downgrade
    print("\n⬇️  Downgrading to free plan...")
    success = downgrade_to_free(api_key, service_id)
    
    if success:
        print("\n✅ Successfully downgraded to free plan!")
        print("\n💰 Savings: $7/month")
        
        # Print keep-alive solution
        print_keep_alive_solution()
        
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())
