"""
Render.com API Client
Provides programmatic access to Render services, logs, deploys, and metrics.

Documentation: https://api-docs.render.com/
API Key: Create at https://dashboard.render.com/u/settings?add-api-key

Usage:
    from render_api_client import RenderAPIClient
    
    client = RenderAPIClient(api_key="rnd_xxxxx")
    
    # List all services
    services = client.list_services()
    
    # Get service details
    service = client.get_service("srv-xxxxx")
    
    # Get logs
    logs = client.get_service_logs("srv-xxxxx", limit=100)
    
    # Trigger deploy
    deploy = client.trigger_deploy("srv-xxxxx")
"""

import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
from zoneinfo import ZoneInfo
import json

# Brisbane timezone constant
BRISBANE_TZ = ZoneInfo("Australia/Brisbane")

def format_brisbane_time(utc_time_str: str) -> str:
    """
    Convert UTC timestamp string to Brisbane time
    
    Args:
        utc_time_str: UTC timestamp string (ISO format)
        
    Returns:
        Formatted Brisbane time string
    """
    if not utc_time_str:
        return "N/A"
    try:
        # Parse UTC time
        utc_time = datetime.fromisoformat(utc_time_str.replace('Z', '+00:00'))
        # Convert to Brisbane
        brisbane_time = utc_time.astimezone(BRISBANE_TZ)
        # Format with timezone
        return brisbane_time.strftime('%Y-%m-%d %H:%M:%S %Z')
    except:
        return utc_time_str  # Return original if parsing fails


class RenderAPIClient:
    """Client for interacting with Render.com REST API"""
    
    BASE_URL = "https://api.render.com/v1"
    
    def __init__(self, api_key: str):
        """
        Initialize Render API client
        
        Args:
            api_key: Render API key (from Account Settings)
        """
        self.api_key = api_key
        self.headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make HTTP request to Render API
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (without base URL)
            **kwargs: Additional arguments for requests
            
        Returns:
            JSON response as dictionary
            
        Raises:
            requests.HTTPError: If request fails
        """
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        response = requests.request(method, url, headers=self.headers, **kwargs)
        response.raise_for_status()
        return response.json()
    
    # ==================== Services ====================
    
    def list_services(self, limit: int = 20, owner_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all services in your account
        
        Args:
            limit: Maximum number of services to return (default 20)
            owner_id: Filter by owner ID (optional)
            
        Returns:
            List of service objects
        """
        params = {'limit': limit}
        if owner_id:
            params['ownerId'] = owner_id
        
        response = self._make_request('GET', 'services', params=params)
        return response
    
    def get_service(self, service_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific service
        
        Args:
            service_id: Service ID (e.g., 'srv-xxxxx')
            
        Returns:
            Service object with full details
        """
        return self._make_request('GET', f'services/{service_id}')
    
    def get_service_by_name(self, service_name: str) -> Optional[Dict[str, Any]]:
        """
        Find service by name
        
        Args:
            service_name: Service name or slug
            
        Returns:
            Service object or None if not found
        """
        services = self.list_services(limit=100)
        for item in services:
            service = item.get('service', {})
            if service.get('name') == service_name or service.get('slug') == service_name:
                return service
        return None
    
    def update_service_env_vars(self, service_id: str, env_vars: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Update environment variables for a service
        
        Args:
            service_id: Service ID
            env_vars: List of env var objects: [{"key": "VAR_NAME", "value": "var_value"}]
            
        Returns:
            Updated service object
        """
        payload = {"envVars": env_vars}
        return self._make_request('PUT', f'services/{service_id}/env-vars', json=payload)
    
    # ==================== Deploys ====================
    
    def list_deploys(self, service_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        List deploy history for a service
        
        Args:
            service_id: Service ID
            limit: Maximum number of deploys to return
            
        Returns:
            List of deploy objects
        """
        params = {'limit': limit}
        response = self._make_request('GET', f'services/{service_id}/deploys', params=params)
        return response
    
    def get_deploy(self, service_id: str, deploy_id: str) -> Dict[str, Any]:
        """
        Get details about a specific deploy
        
        Args:
            service_id: Service ID
            deploy_id: Deploy ID
            
        Returns:
            Deploy object
        """
        return self._make_request('GET', f'services/{service_id}/deploys/{deploy_id}')
    
    def trigger_deploy(self, service_id: str, clear_cache: bool = False) -> Dict[str, Any]:
        """
        Trigger a manual deploy for a service
        
        Args:
            service_id: Service ID
            clear_cache: Whether to clear build cache (default False)
            
        Returns:
            Deploy object
        """
        payload = {"clearCache": "clear" if clear_cache else "do_not_clear"}
        return self._make_request('POST', f'services/{service_id}/deploys', json=payload)
    
    # ==================== Logs ====================
    
    def get_service_logs(
        self, 
        service_id: str, 
        limit: int = 100,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        text_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get logs for a service (NOTE: API endpoint may vary, check docs)
        
        Args:
            service_id: Service ID
            limit: Maximum number of log entries
            start_time: Filter logs after this time
            end_time: Filter logs before this time
            text_filter: Filter logs containing this text
            
        Returns:
            List of log entries
            
        Note:
            The logs endpoint may be different in the actual API.
            Check https://api-docs.render.com/ for correct endpoint.
        """
        params = {'limit': limit}
        if start_time:
            params['startTime'] = start_time.isoformat()
        if end_time:
            params['endTime'] = end_time.isoformat()
        if text_filter:
            params['text'] = text_filter
        
        try:
            return self._make_request('GET', f'services/{service_id}/logs', params=params)
        except requests.HTTPError as e:
            # Logs endpoint may not be available via REST API
            # Use Render Dashboard or CLI for logs
            raise NotImplementedError(
                f"Logs endpoint returned error: {e}. "
                "Logs may require Render CLI or Dashboard access. "
                "Visit: https://dashboard.render.com/web/{service_id}"
            )
    
    # ==================== Helper Methods ====================
    
    def get_flask_service(self) -> Optional[Dict[str, Any]]:
        """
        Get the inhouseprint-flask service
        
        Returns:
            Flask service object or None
        """
        return self.get_service_by_name('inhouseprint-flask')
    
    def get_streamlit_service(self) -> Optional[Dict[str, Any]]:
        """
        Get the inhouseprint-streamlit service
        
        Returns:
            Streamlit service object or None
        """
        return self.get_service_by_name('inhouseprint-streamlit')
    
    def check_service_status(self, service_id: str) -> Dict[str, Any]:
        """
        Check if service is running and get status details
        
        Args:
            service_id: Service ID
            
        Returns:
            Dictionary with status information:
            {
                'id': 'srv-xxxxx',
                'name': 'service-name',
                'status': 'suspended' | 'not_suspended',
                'plan': 'free' | 'starter' | 'standard' | 'pro',
                'url': 'https://service.onrender.com',
                'updated_at': '2025-10-16T09:25:24Z'
            }
        """
        service = self.get_service(service_id)
        return {
            'id': service.get('id'),
            'name': service.get('name'),
            'status': service.get('suspended'),
            'plan': service.get('serviceDetails', {}).get('plan'),
            'url': service.get('serviceDetails', {}).get('url'),
            'updated_at': service.get('updatedAt'),
            'region': service.get('serviceDetails', {}).get('region'),
            'runtime': service.get('serviceDetails', {}).get('runtime')
        }
    
    def restart_service(self, service_id: str) -> Dict[str, Any]:
        """
        Restart a service by triggering a new deploy with cache clear
        
        Args:
            service_id: Service ID
            
        Returns:
            Deploy object
        """
        return self.trigger_deploy(service_id, clear_cache=True)
    
    def print_service_summary(self, service_id: str):
        """
        Print a formatted summary of a service
        
        Args:
            service_id: Service ID
        """
        status = self.check_service_status(service_id)
        print(f"\n{'='*80}")
        print(f"Service: {status['name']} ({status['id']})")
        print(f"{'='*80}")
        print(f"Status:      {status['status']}")
        print(f"Plan:        {status['plan']}")
        print(f"URL:         {status['url']}")
        print(f"Region:      {status['region']}")
        print(f"Runtime:     {status['runtime']}")
        print(f"Updated:     {status['updated_at']}")
        print(f"{'='*80}\n")
    
    def print_all_services(self):
        """Print summary of all services"""
        services = self.list_services(limit=100)
        print(f"\n{'='*80}")
        print(f"All Render Services")
        print(f"{'='*80}\n")
        
        for item in services:
            service = item.get('service', {})
            details = service.get('serviceDetails', {})
            print(f"📦 {service.get('name')} ({service.get('id')})")
            print(f"   Status: {service.get('suspended')}")
            print(f"   Plan: {details.get('plan')}")
            print(f"   URL: {details.get('url')}")
            print(f"   Runtime: {details.get('runtime')}")
            print()


# ==================== CLI Interface ====================

def main():
    """Command-line interface for Render API"""
    import argparse
    import os
    
    parser = argparse.ArgumentParser(description='Render.com API Client')
    parser.add_argument('--api-key', default=os.environ.get('RENDER_API_KEY'),
                        help='Render API key (or set RENDER_API_KEY env var)')
    parser.add_argument('--list', action='store_true',
                        help='List all services')
    parser.add_argument('--service', help='Service ID to inspect')
    parser.add_argument('--service-name', help='Service name to find')
    parser.add_argument('--deploys', help='List deploys for service ID')
    parser.add_argument('--deploy', action='store_true',
                        help='Trigger manual deploy')
    parser.add_argument('--clear-cache', action='store_true',
                        help='Clear build cache when deploying')
    parser.add_argument('--flask', action='store_true',
                        help='Show Flask service status')
    parser.add_argument('--streamlit', action='store_true',
                        help='Show Streamlit service status')
    parser.add_argument('--restart', help='Restart service by ID')
    
    args = parser.parse_args()
    
    if not args.api_key:
        print(" Error: API key required. Set RENDER_API_KEY or use --api-key")
        return
    
    client = RenderAPIClient(args.api_key)
    
    try:
        if args.list:
            client.print_all_services()
        
        elif args.service:
            client.print_service_summary(args.service)
        
        elif args.service_name:
            service = client.get_service_by_name(args.service_name)
            if service:
                client.print_service_summary(service['id'])
            else:
                print(f" Service '{args.service_name}' not found")
        
        elif args.flask:
            service = client.get_flask_service()
            if service:
                client.print_service_summary(service['id'])
            else:
                print(" Flask service not found")
        
        elif args.streamlit:
            service = client.get_streamlit_service()
            if service:
                client.print_service_summary(service['id'])
            else:
                print(" Streamlit service not found")
        
        elif args.deploys:
            deploys = client.list_deploys(args.deploys, limit=10)
            print(f"\n{'='*80}")
            print(f"Recent Deploys for {args.deploys}")
            print(f"{'='*80}\n")
            for item in deploys:
                deploy = item.get('deploy', {})
                print(f"🚀 Deploy {deploy.get('id')}")
                print(f"   Status: {deploy.get('status')}")
                print(f"   Created: {format_brisbane_time(deploy.get('createdAt'))}")
                print(f"   Finished: {format_brisbane_time(deploy.get('finishedAt'))}")
                print()
        
        elif args.restart:
            print(f"🔄 Restarting service {args.restart}...")
            result = client.restart_service(args.restart)
            print(f" Deploy triggered: {result.get('deploy', {}).get('id')}")
        
        elif args.deploy:
            if not args.service:
                print(" Error: --service required with --deploy")
                return
            print(f"🚀 Deploying {args.service}...")
            result = client.trigger_deploy(args.service, clear_cache=args.clear_cache)
            print(f" Deploy triggered: {result.get('deploy', {}).get('id')}")
        
        else:
            parser.print_help()
    
    except requests.HTTPError as e:
        print(f" API Error: {e}")
        if e.response is not None:
            print(f"Response: {e.response.text}")
    except Exception as e:
        print(f" Error: {e}")


if __name__ == '__main__':
    main()
