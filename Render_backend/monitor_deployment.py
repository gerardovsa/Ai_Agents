#!/usr/bin/env python3
"""
Monitor Deployment - Real-time deployment status monitoring

This script monitors a Render deployment in real-time, showing progress
and notifying when deployment completes (success or failure).
"""

import os
import sys
import time
import json
import requests
from pathlib import Path
from datetime import datetime
from dotenv import dotenv_values

def get_render_api_key():
    """Get Render API key from .env.master"""
    env_path = Path('.env.master')
    
    if not env_path.exists():
        print("❌ .env.master file not found")
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
            print("❌ RENDER_API_KEY not found in .env.master")
            return None
        
        return api_key
    except Exception as e:
        print(f"❌ Error reading .env.master: {e}")
        return None

def get_service_status(api_key, service_id):
    """Get current service status"""
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

def get_latest_deploy(api_key, service_id):
    """Get latest deployment status"""
    url = f"https://api.render.com/v1/services/{service_id}/deploys"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, params={"limit": 1})
        
        if response.status_code == 200:
            data = response.json()
            deploys = data.get('deploys', data) if isinstance(data, dict) else data
            
            if deploys and len(deploys) > 0:
                return deploys[0]
            return None
        else:
            return None
    except Exception as e:
        return None

def format_time_elapsed(start_time):
    """Format time elapsed since start"""
    try:
        start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        now = datetime.now(start.tzinfo)
        elapsed = now - start
        
        minutes = int(elapsed.total_seconds() // 60)
        seconds = int(elapsed.total_seconds() % 60)
        
        return f"{minutes}m {seconds}s"
    except:
        return "Unknown"

def get_status_emoji(status):
    """Get emoji for deployment status"""
    status_map = {
        'created': '🆕',
        'build_in_progress': '🔨',
        'update_in_progress': '🔄',
        'pre_deploy_in_progress': '⚙️',
        'live': '✅',
        'deactivated': '⏸️',
        'build_failed': '❌',
        'update_failed': '❌',
        'canceled': '🚫',
    }
    return status_map.get(status, '❓')

def monitor_deployment(api_key, service_id, check_interval=10):
    """Monitor deployment progress in real-time"""
    print(f"\n🔍 Monitoring deployment for service: {service_id}")
    print(f"   Checking every {check_interval} seconds...")
    print("\n" + "=" * 70)
    
    last_status = None
    start_time = None
    
    try:
        while True:
            # Get latest deployment
            deploy = get_latest_deploy(api_key, service_id)
            
            if not deploy:
                print("⚠️  No deployment found")
                time.sleep(check_interval)
                continue
            
            current_status = deploy.get('status', 'unknown')
            deploy_id = deploy.get('id', 'unknown')
            created_at = deploy.get('createdAt', '')
            finished_at = deploy.get('finishedAt', '')
            
            # Track start time
            if not start_time:
                start_time = created_at
            
            # Print status update if changed
            if current_status != last_status:
                emoji = get_status_emoji(current_status)
                elapsed = format_time_elapsed(start_time) if start_time else "0m 0s"
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                print(f"[{timestamp}] {emoji} {current_status.upper()}")
                print(f"           Deploy ID: {deploy_id}")
                print(f"           Elapsed: {elapsed}")
                
                last_status = current_status
            
            # Check if deployment completed (success or failure)
            if current_status in ['live', 'build_failed', 'update_failed', 'canceled']:
                print("\n" + "=" * 70)
                
                if current_status == 'live':
                    print("✅ Deployment Successful!")
                    
                    # Get service URL
                    service = get_service_status(api_key, service_id)
                    if service:
                        service_url = service.get('serviceUrl', 'Unknown')
                        print(f"\n🌐 Service URL: {service_url}")
                        print(f"\n📋 Next steps:")
                        print(f"   1. Test health endpoint: curl {service_url}/health")
                        print(f"   2. Update OAuth redirects: python Render_backend/update_oauth_redirects.py")
                        print(f"   3. Test deployment: python Render_backend/test_deployment.py")
                    
                    return 0
                else:
                    print(f"❌ Deployment Failed: {current_status}")
                    print(f"\n📋 Next steps:")
                    print(f"   1. Check logs: python Render_backend/fetch_logs.py")
                    print(f"   2. View dashboard: https://dashboard.render.com/web/{service_id}")
                    print(f"   3. Common fixes:")
                    print(f"      - Check runtime.txt has correct Python version")
                    print(f"      - Verify requirements.txt is valid")
                    print(f"      - Check environment variables are set")
                    
                    return 1
            
            # Wait before next check
            time.sleep(check_interval)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Monitoring stopped by user")
        return 0

def main():
    print("=" * 70)
    print("📊 Render Deployment Monitor")
    print("=" * 70)
    
    # Get API key
    api_key = get_render_api_key()
    if not api_key:
        return 1
    
    # Get service ID from command line or prompt
    if len(sys.argv) > 1:
        service_id = sys.argv[1]
    else:
        print("\n💡 Usage: python monitor_deployment.py <service_id>")
        print("\nOr set default service ID in this script")
        
        # Default service ID (update this)
        service_id = "srv-d40tai15pdvs73ddh4m0"
        print(f"\nUsing default service ID: {service_id}")
    
    # Check interval (seconds)
    check_interval = 10
    if len(sys.argv) > 2:
        try:
            check_interval = int(sys.argv[2])
        except:
            pass
    
    # Start monitoring
    return monitor_deployment(api_key, service_id, check_interval)

if __name__ == "__main__":
    sys.exit(main())
