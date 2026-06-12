#!/usr/bin/env python3
"""
Fetch Logs - Retrieve deployment logs from Render

This script fetches logs from a Render deployment to help debug issues.
Note: Render API v1 doesn't expose logs endpoint, so this uses web scraping
or provides instructions for manual log access.
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
        print(" .env.master file not found")
        return None
    
    try:
        # Read file with UTF-8 encoding
        with open(env_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        # Parse environment variables manually
        env_vars = {}
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
        
        api_key = env_vars.get('RENDER_API_KEY')
        
        if not api_key:
            print(" RENDER_API_KEY not found in .env.master")
            return None
        
        return api_key
    except Exception as e:
        print(f" Error reading .env.master: {e}")
        return None

def get_latest_deploy_info(api_key, service_id):
    """Get latest deployment information"""
    url = f"https://api.render.com/v1/services/{service_id}/deploys"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, params={"limit": 5})
        
        if response.status_code == 200:
            data = response.json()
            deploys = data.get('deploys', data) if isinstance(data, dict) else data
            return deploys
        else:
            print(f" API Error: {response.status_code}")
            return None
    except Exception as e:
        print(f" Request error: {e}")
        return None

def print_deploy_summary(deploys):
    """Print summary of recent deployments"""
    print("\n📋 Recent Deployments:")
    print("=" * 70)
    
    for i, deploy in enumerate(deploys[:5], 1):
        deploy_id = deploy.get('id', 'unknown')
        status = deploy.get('status', 'unknown')
        created_at = deploy.get('createdAt', 'unknown')
        finished_at = deploy.get('finishedAt', 'not finished')
        
        status_emoji = {
            'live': '',
            'build_failed': '',
            'update_failed': '',
            'build_in_progress': '🔨',
            'canceled': '🚫',
        }.get(status, '❓')
        
        print(f"\n{i}. {status_emoji} Deploy: {deploy_id}")
        print(f"   Status: {status}")
        print(f"   Created: {created_at}")
        print(f"   Finished: {finished_at}")

def provide_log_access_instructions(service_id, deploy_id):
    """Provide instructions for accessing logs"""
    print("\n" + "=" * 70)
    print("📖 How to Access Deployment Logs")
    print("=" * 70)
    
    print("\n⚠️  Note: Render API v1 doesn't expose build logs endpoint")
    print("   You must use the dashboard or CLI to view logs.")
    
    print("\n📊 Option 1: Render Dashboard (Easiest)")
    print("   1. Open: https://dashboard.render.com")
    print(f"   2. Navigate to your service: srv-{service_id}")
    print("   3. Click 'Logs' tab")
    print("   4. Select deployment from dropdown")
    
    print("\n💻 Option 2: Render CLI")
    print("   1. Install CLI: npm install -g render")
    print("   2. Login: render login")
    print(f"   3. View logs: render logs {service_id}")
    print(f"   4. Follow live: render logs {service_id} --tail")
    
    print("\n🔍 Option 3: API (Limited)")
    print("   The API provides deployment status but not logs.")
    print("   Use this script to get deployment details:")
    print(f"   python Render_backend/check_render_service.py")
    
    if deploy_id and deploy_id != 'unknown':
        print(f"\n🔗 Direct Dashboard Link:")
        print(f"   https://dashboard.render.com/web/{service_id}/deploys/{deploy_id}")

def fetch_service_events(api_key, service_id):
    """Fetch service events (alternative to logs)"""
    url = f"https://api.render.com/v1/services/{service_id}/events"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, params={"limit": 20})
        
        if response.status_code == 200:
            data = response.json()
            events = data.get('events', data) if isinstance(data, dict) else data
            
            if events:
                print("\n📅 Recent Service Events:")
                print("=" * 70)
                
                for event in events[:10]:
                    timestamp = event.get('timestamp', 'unknown')
                    text = event.get('text', 'No description')
                    print(f"\n[{timestamp}]")
                    print(f"   {text}")
                
                return True
        
        return False
    except Exception as e:
        print(f"\n⚠️  Could not fetch events: {e}")
        return False

def main():
    print("=" * 70)
    print("📜 Fetch Render Deployment Logs")
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
    
    # Get recent deployments
    print("\n🔍 Fetching deployment information...")
    deploys = get_latest_deploy_info(api_key, service_id)
    
    if not deploys:
        print(" Could not fetch deployment information")
        return 1
    
    # Print deployment summary
    print_deploy_summary(deploys)
    
    # Get latest deploy ID
    latest_deploy_id = deploys[0].get('id', 'unknown') if deploys else 'unknown'
    
    # Try to fetch service events
    print("\n")
    fetch_service_events(api_key, service_id)
    
    # Provide instructions for accessing full logs
    provide_log_access_instructions(service_id, latest_deploy_id)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
