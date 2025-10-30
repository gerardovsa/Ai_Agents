#!/usr/bin/env python3
"""
Check Render Service Status
"""

import os
import requests
import json
from dotenv import load_dotenv
from datetime import datetime

# Load environment
load_dotenv('.env.master')

RENDER_API_KEY = os.getenv('RENDER_API_KEY')
SERVICE_ID = 'srv-d40tai15pdvs73ddh4m0'
SERVICE_URL = 'https://ai-agents-backend-2oi8.onrender.com'

def check_service_status():
    """Check service status via Render API"""
    print("=" * 60)
    print("🔍 Checking Render Service Status")
    print("=" * 60)
    
    headers = {
        'Authorization': f'Bearer {RENDER_API_KEY}',
        'Accept': 'application/json'
    }
    
    try:
        # Get service details
        print(f"\n📡 Fetching service details...")
        r = requests.get(f'https://api.render.com/v1/services/{SERVICE_ID}', headers=headers)
        r.raise_for_status()
        
        service = r.json().get('service', {})
        details = service.get('serviceDetails', {})
        
        print(f"\n✅ Service Information:")
        print(f"   Name: {service.get('name', 'N/A')}")
        print(f"   ID: {service.get('id', 'N/A')}")
        print(f"   Status: {service.get('suspended', 'N/A')}")
        print(f"   URL: {details.get('url', 'N/A')}")
        print(f"   Region: {details.get('region', 'N/A')}")
        print(f"   Plan: {details.get('plan', 'N/A')}")
        print(f"   Runtime: {details.get('runtime', 'N/A')}")
        print(f"   Auto Deploy: {service.get('autoDeploy', 'N/A')}")
        print(f"   Created: {service.get('createdAt', 'N/A')}")
        print(f"   Updated: {service.get('updatedAt', 'N/A')}")
        
        # Get recent deploys
        print(f"\n📦 Fetching deployment history...")
        r = requests.get(
            f'https://api.render.com/v1/services/{SERVICE_ID}/deploys',
            headers=headers,
            params={'limit': 5}
        )
        r.raise_for_status()
        
        deploys = r.json()
        
        if deploys:
            print(f"\n🚀 Recent Deployments:")
            for i, deploy_item in enumerate(deploys[:5], 1):
                deploy = deploy_item.get('deploy', deploy_item)
                status = deploy.get('status', 'unknown')
                created = deploy.get('createdAt', 'N/A')
                finished = deploy.get('finishedAt', 'N/A')
                
                # Status emoji
                status_emoji = {
                    'live': '✅',
                    'build_in_progress': '🔄',
                    'update_in_progress': '🔄',
                    'build_failed': '❌',
                    'deactivated': '⏸️',
                    'canceled': '🚫'
                }.get(status, '❓')
                
                print(f"\n   {i}. {status_emoji} Deploy ID: {deploy.get('id', 'N/A')}")
                print(f"      Status: {status}")
                print(f"      Created: {created}")
                print(f"      Finished: {finished if finished else 'In Progress'}")
                
                if status == 'build_failed':
                    print(f"      ⚠️  BUILD FAILED - Check logs in dashboard")
        else:
            print(f"\n⚠️  No deployments found")
        
        # Test health endpoint
        print(f"\n🏥 Testing Health Endpoint...")
        try:
            health_response = requests.get(f"{SERVICE_URL}/health", timeout=10)
            if health_response.status_code == 200:
                print(f"   ✅ Health endpoint is responding!")
                print(f"   Response: {health_response.text[:200]}")
            else:
                print(f"   ⚠️  Health endpoint returned: {health_response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Health endpoint not accessible: {e}")
            print(f"   Service may still be building or there's an error")
        
        # Dashboard link
        print(f"\n📊 Dashboard:")
        print(f"   https://dashboard.render.com/web/{SERVICE_ID}")
        
        return service
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ API Error: {e}")
        return None


def check_logs():
    """Try to fetch recent logs (may not be available via API)"""
    headers = {
        'Authorization': f'Bearer {RENDER_API_KEY}',
        'Accept': 'application/json'
    }
    
    try:
        print(f"\n📋 Attempting to fetch logs...")
        r = requests.get(
            f'https://api.render.com/v1/services/{SERVICE_ID}/logs',
            headers=headers,
            params={'limit': 50}
        )
        
        if r.status_code == 200:
            logs = r.json()
            print(f"\n📜 Recent Logs:")
            for log in logs[:20]:
                print(f"   {log}")
        else:
            print(f"   ⚠️  Logs not available via API (status {r.status_code})")
            print(f"   View logs in dashboard: https://dashboard.render.com/web/{SERVICE_ID}")
    except Exception as e:
        print(f"   ⚠️  Logs not available via API")
        print(f"   View logs in dashboard: https://dashboard.render.com/web/{SERVICE_ID}")


if __name__ == "__main__":
    service = check_service_status()
    
    if service:
        print(f"\n" + "=" * 60)
        
        # Check if latest deploy is live
        headers = {'Authorization': f'Bearer {RENDER_API_KEY}', 'Accept': 'application/json'}
        r = requests.get(f'https://api.render.com/v1/services/{SERVICE_ID}/deploys', headers=headers, params={'limit': 1})
        
        if r.status_code == 200:
            deploys = r.json()
            if deploys:
                latest_deploy = deploys[0].get('deploy', deploys[0])
                status = latest_deploy.get('status', 'unknown')
                
                if status == 'live':
                    print("✅ SERVICE IS LIVE AND READY!")
                elif status in ['build_in_progress', 'update_in_progress']:
                    print("🔄 SERVICE IS BUILDING...")
                    print("   Check back in a few minutes")
                elif status == 'build_failed':
                    print("❌ DEPLOYMENT FAILED")
                    print("   Check logs in dashboard for errors")
                else:
                    print(f"❓ SERVICE STATUS: {status}")
        
        print("=" * 60)
    else:
        print("\n❌ Could not retrieve service information")
