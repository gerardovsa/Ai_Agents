#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Render Deployment Toolkit - Comprehensive Monitoring and Management
Handles encoding properly for Windows PowerShell/CMD
"""

import sys
import os
import json
import time
import requests
from datetime import datetime
from typing import Optional, Dict, List, Any

# Fix encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Configuration
SERVICE_ID = "srv-d47nfr2li9vc738s0uc0"
API_KEY = os.environ.get('RENDER_API_KEY', 'rnd_hTZfWT0aHJLeX925X5sIiY5PxWiu')
BASE_URL = "https://api.render.com/v1"

HEADERS = {
    'Authorization': f'Bearer {API_KEY}',
    'Accept': 'application/json'
}

# Status icons (ASCII-safe for encoding issues)
STATUS_ICONS = {
    'live': '[OK]',
    'building': '[BUILD]',
    'deploying': '[DEPLOY]',
    'build_in_progress': '[BUILD]',
    'build_failed': '[FAIL-BUILD]',
    'update_failed': '[FAIL]',
    'canceled': '[CANCEL]',
    'not_suspended': '[ACTIVE]',
    'suspended': '[SUSPENDED]'
}


class RenderToolkit:
    """Main toolkit class for Render operations"""
    
    def __init__(self, service_id: str = SERVICE_ID):
        self.service_id = service_id
        self.headers = HEADERS
        self.base_url = BASE_URL
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict]:
        """Make API request with error handling"""
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.request(method, url, headers=self.headers, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API Error: {str(e)}")
            return None
    
    def get_service(self) -> Optional[Dict]:
        """Get service details"""
        return self._make_request('GET', f'services/{self.service_id}')
    
    def list_deploys(self, limit: int = 10) -> Optional[List[Dict]]:
        """List recent deployments"""
        data = self._make_request('GET', f'services/{self.service_id}/deploys', 
                                   params={'limit': limit})
        # API returns array of objects with 'deploy' key
        if isinstance(data, list):
            return [item.get('deploy', {}) for item in data]
        return []
    
    def get_latest_deploy(self) -> Optional[Dict]:
        """Get the most recent deployment"""
        deploys = self.list_deploys(limit=1)
        return deploys[0] if deploys else None
    
    def trigger_deploy(self, clear_cache: bool = False) -> Optional[Dict]:
        """Trigger a new deployment"""
        payload = {'clearCache': 'clear' if clear_cache else 'do_not_clear'}
        return self._make_request('POST', f'services/{self.service_id}/deploys', json=payload)
    
    def get_env_vars(self) -> Optional[List[Dict]]:
        """Get environment variables"""
        return self._make_request('GET', f'services/{self.service_id}/env-vars')
    
    def test_health(self) -> Dict[str, Any]:
        """Test service health endpoint"""
        service = self.get_service()
        if not service:
            return {'status': 'error', 'message': 'Could not fetch service details'}
        
        url = service.get('serviceDetails', {}).get('url')
        if not url:
            return {'status': 'error', 'message': 'No service URL found'}
        
        health_url = f"{url}/health"
        try:
            response = requests.get(health_url, timeout=10)
            return {
                'status': 'healthy' if response.status_code == 200 else 'unhealthy',
                'status_code': response.status_code,
                'response': response.json() if response.status_code == 200 else response.text,
                'url': health_url
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'url': health_url
            }


def print_header(title: str, width: int = 80):
    """Print formatted header"""
    print("\n" + "=" * width)
    print(f"  {title}")
    print("=" * width + "\n")


def print_service_info(toolkit: RenderToolkit):
    """Print service information"""
    print_header("SERVICE INFORMATION")
    
    service = toolkit.get_service()
    if not service:
        print("Failed to fetch service information\n")
        return
    
    details = service.get('serviceDetails', {})
    print(f"Name:         {service.get('name', 'N/A')}")
    print(f"ID:           {service.get('id', 'N/A')}")
    print(f"Type:         {service.get('type', 'N/A')}")
    print(f"Status:       {STATUS_ICONS.get(service.get('suspended', 'unknown'), '[?]')} {service.get('suspended', 'N/A')}")
    print(f"Region:       {details.get('region', 'N/A')}")
    print(f"Plan:         {details.get('plan', 'N/A')}")
    print(f"URL:          {details.get('url', 'N/A')}")
    print(f"Environment:  {details.get('env', 'N/A')}")
    print(f"Created:      {service.get('createdAt', 'N/A')}")
    print(f"Updated:      {service.get('updatedAt', 'N/A')}")
    print()


def print_deploy_status(toolkit: RenderToolkit, show_all: bool = False):
    """Print deployment status"""
    print_header("DEPLOYMENT STATUS")
    
    limit = 10 if show_all else 3
    deploys = toolkit.list_deploys(limit=limit)
    
    if not deploys:
        print("No deployments found\n")
        return
    
    print(f"Recent Deployments (showing {min(len(deploys), limit)}):\n")
    
    for i, deploy in enumerate(deploys, 1):
        status = deploy.get('status', 'unknown')
        icon = STATUS_ICONS.get(status, '[?]')
        deploy_id = deploy.get('id', 'N/A')
        created = deploy.get('createdAt', 'N/A')
        finished = deploy.get('finishedAt', 'In progress...')
        commit_msg = deploy.get('commit', {}).get('message', 'N/A')[:60]
        
        print(f"{i}. {icon} Deploy: {deploy_id}")
        print(f"   Status:   {status}")
        print(f"   Created:  {created}")
        print(f"   Finished: {finished}")
        print(f"   Commit:   {commit_msg}")
        print()


def print_health_check(toolkit: RenderToolkit):
    """Print health check results"""
    print_header("HEALTH CHECK")
    
    health = toolkit.test_health()
    status = health.get('status', 'unknown')
    
    if status == 'healthy':
        print("[OK] Service is HEALTHY")
        print(f"Status Code: {health.get('status_code')}")
        print(f"URL: {health.get('url')}")
        print(f"\nResponse:")
        print(json.dumps(health.get('response', {}), indent=2))
    elif status == 'unhealthy':
        print("[FAIL] Service is UNHEALTHY")
        print(f"Status Code: {health.get('status_code')}")
        print(f"URL: {health.get('url')}")
        print(f"Response: {health.get('response')}")
    else:
        print(f"[ERROR] Cannot reach service")
        print(f"URL: {health.get('url')}")
        print(f"Error: {health.get('message')}")
    print()


def monitor_deployment(toolkit: RenderToolkit, interval: int = 30, max_checks: int = 20):
    """Monitor current deployment until completion"""
    print_header("DEPLOYMENT MONITOR")
    
    initial_deploy = toolkit.get_latest_deploy()
    if not initial_deploy:
        print("No active deployment found\n")
        return
    
    deploy_id = initial_deploy.get('id')
    status = initial_deploy.get('status')
    
    print(f"Monitoring deployment: {deploy_id}")
    print(f"Initial status: {status}")
    print(f"Checking every {interval} seconds (max {max_checks} checks)\n")
    
    for check in range(1, max_checks + 1):
        current_deploy = toolkit.get_latest_deploy()
        if not current_deploy or current_deploy.get('id') != deploy_id:
            print(f"\n[WARN] Deployment ID changed or not found")
            break
        
        status = current_deploy.get('status')
        icon = STATUS_ICONS.get(status, '[?]')
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        print(f"[{timestamp}] Check {check}/{max_checks}: {icon} {status}", end='')
        
        if status in ['live', 'update_failed', 'canceled']:
            print(f"\n\nDeployment completed with status: {status}")
            
            if status == 'live':
                print("\n[SUCCESS] Deployment successful!")
                print_health_check(toolkit)
            else:
                print(f"\n[FAILED] Deployment ended with status: {status}")
                print("Check logs at: https://dashboard.render.com/web/{self.service_id}")
            break
        
        print(f" - waiting {interval}s...")
        
        if check < max_checks:
            time.sleep(interval)
    else:
        print(f"\n\n[TIMEOUT] Max checks ({max_checks}) reached")
        print(f"Final status: {status}")
        print("Deployment may still be in progress")
    
    print()


def print_env_vars(toolkit: RenderToolkit):
    """Print environment variables (counts only, not values for security)"""
    print_header("ENVIRONMENT VARIABLES")
    
    env_vars = toolkit.get_env_vars()
    
    if not env_vars:
        print("No environment variables found or API doesn't return secrets\n")
        return
    
    print(f"Total variables: {len(env_vars)}")
    print("\nNote: Render API doesn't return secret values for security")
    print("View/edit at: https://dashboard.render.com/web/{}/env\n".format(toolkit.service_id))


def quick_status(toolkit: RenderToolkit):
    """Quick status overview"""
    print_header("QUICK STATUS OVERVIEW", width=100)
    
    # Service status
    service = toolkit.get_service()
    if service:
        status = service.get('suspended', 'unknown')
        icon = STATUS_ICONS.get(status, '[?]')
        print(f"Service Status: {icon} {status}")
        print(f"Service URL:    {service.get('serviceDetails', {}).get('url', 'N/A')}")
    
    # Latest deployment
    deploy = toolkit.get_latest_deploy()
    if deploy:
        status = deploy.get('status', 'unknown')
        icon = STATUS_ICONS.get(status, '[?]')
        print(f"\nLatest Deploy:  {icon} {status}")
        print(f"Deploy ID:      {deploy.get('id', 'N/A')}")
        print(f"Created:        {deploy.get('createdAt', 'N/A')}")
    
    # Health check
    health = toolkit.test_health()
    status = health.get('status', 'unknown')
    print(f"\nHealth Status:  [{status.upper()}]")
    
    print("\n" + "=" * 100 + "\n")


def main():
    """Main CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Render Deployment Toolkit - Comprehensive monitoring and management',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('command', choices=[
        'status', 'service', 'deploys', 'health', 'monitor', 'env', 'quick', 'watch'
    ], help='Command to execute')
    
    parser.add_argument('--all', action='store_true', help='Show all items (for deploys)')
    parser.add_argument('--interval', type=int, default=30, help='Check interval for monitoring (seconds)')
    parser.add_argument('--max-checks', type=int, default=20, help='Maximum checks for monitoring')
    parser.add_argument('--service-id', type=str, default=SERVICE_ID, help='Service ID to manage')
    
    args = parser.parse_args()
    
    toolkit = RenderToolkit(service_id=args.service_id)
    
    if args.command == 'status':
        print_service_info(toolkit)
        print_deploy_status(toolkit, show_all=args.all)
    
    elif args.command == 'service':
        print_service_info(toolkit)
    
    elif args.command == 'deploys':
        print_deploy_status(toolkit, show_all=args.all)
    
    elif args.command == 'health':
        print_health_check(toolkit)
    
    elif args.command == 'monitor' or args.command == 'watch':
        monitor_deployment(toolkit, interval=args.interval, max_checks=args.max_checks)
    
    elif args.command == 'env':
        print_env_vars(toolkit)
    
    elif args.command == 'quick':
        quick_status(toolkit)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user\n")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {str(e)}\n")
        sys.exit(1)
