"""
Cloudflare Tool Implementations
================================

This module provides tool implementations for Cloudflare Workers.
"""

import os
import requests

try:
    from config import get_api_key_enhanced
    CLOUDFLARE_ACCOUNT_ID = get_api_key_enhanced('CLOUDFLARE_ACCOUNT_ID')
    CLOUDFLARE_API_TOKEN = get_api_key_enhanced('CLOUDFLARE_AI_AGENT_TOKEN')
except ImportError:
    CLOUDFLARE_ACCOUNT_ID = os.getenv('CLOUDFLARE_ACCOUNT_ID')
    CLOUDFLARE_API_TOKEN = os.getenv('CLOUDFLARE_AI_AGENT_TOKEN')

BASE_URL = "https://api.cloudflare.com/client/v4"


def _get_headers():
    """Get API headers"""
    return {
        'Authorization': f'Bearer {CLOUDFLARE_API_TOKEN}',
        'Content-Type': 'application/json'
    }


def cloudflare_deploy_worker(worker_name: str, script_path: str, routes: list = None):
    """
    Deploy a Cloudflare Worker script.
    
    Args:
        worker_name: Name of the Worker
        script_path: Path to JavaScript file
        routes: Optional routes to bind
    
    Returns:
        Deployment result
    """
    print(f"🔧 Deploying Cloudflare Worker: {worker_name}")
    
    try:
        # Read script content
        with open(script_path, 'r') as f:
            script_content = f.read()
        
        # Deploy Worker
        url = f"{BASE_URL}/accounts/{CLOUDFLARE_ACCOUNT_ID}/workers/scripts/{worker_name}"
        
        headers = _get_headers()
        headers['Content-Type'] = 'application/javascript'
        
        response = requests.put(url, headers=headers, data=script_content)
        response.raise_for_status()
        
        result = {
            'worker_name': worker_name,
            'deployed': True,
            'script_size': len(script_content)
        }
        
        # Bind routes if provided
        if routes:
            for route in routes:
                route_url = f"{BASE_URL}/accounts/{CLOUDFLARE_ACCOUNT_ID}/workers/routes"
                route_data = {
                    'pattern': route,
                    'script': worker_name
                }
                route_response = requests.post(route_url, headers=_get_headers(), json=route_data)
                route_response.raise_for_status()
            
            result['routes'] = routes
        
        return result
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        raise


def cloudflare_list_workers():
    """
    List all deployed Cloudflare Workers.
    
    Returns:
        List of Workers
    """
    print("🔧 Listing Cloudflare Workers")
    
    try:
        url = f"{BASE_URL}/accounts/{CLOUDFLARE_ACCOUNT_ID}/workers/scripts"
        response = requests.get(url, headers=_get_headers())
        response.raise_for_status()
        
        data = response.json()
        
        return {
            'workers': data.get('result', []),
            'count': len(data.get('result', []))
        }
        
    except Exception as e:
        print(f"❌ Failed to list workers: {e}")
        raise


def cloudflare_get_worker_logs(worker_name: str, limit: int = 100):
    """
    Fetch logs for a specific Worker.
    
    Args:
        worker_name: Name of the Worker
        limit: Maximum number of log entries
    
    Returns:
        Worker logs
    """
    print(f"🔧 Fetching logs for Worker: {worker_name}")
    
    try:
        url = f"{BASE_URL}/accounts/{CLOUDFLARE_ACCOUNT_ID}/workers/scripts/{worker_name}/tail"
        
        # Note: This requires Workers Tail API access
        response = requests.get(url, headers=_get_headers(), params={'limit': limit})
        response.raise_for_status()
        
        data = response.json()
        
        return {
            'worker_name': worker_name,
            'logs': data.get('result', []),
            'count': len(data.get('result', []))
        }
        
    except Exception as e:
        print(f"❌ Failed to fetch logs: {e}")
        # Return empty logs instead of failing
        return {
            'worker_name': worker_name,
            'logs': [],
            'error': str(e)
        }


def cloudflare_worker_status(worker_name: str):
    """
    Check the health/status of a Worker.
    
    Args:
        worker_name: Name of the Worker
    
    Returns:
        Worker status
    """
    print(f"🔧 Checking Worker status: {worker_name}")
    
    try:
        url = f"{BASE_URL}/accounts/{CLOUDFLARE_ACCOUNT_ID}/workers/scripts/{worker_name}"
        response = requests.get(url, headers=_get_headers())
        response.raise_for_status()
        
        data = response.json()
        worker = data.get('result', {})
        
        return {
            'worker_name': worker_name,
            'exists': True,
            'created_on': worker.get('created_on'),
            'modified_on': worker.get('modified_on'),
            'etag': worker.get('etag')
        }
        
    except Exception as e:
        print(f"❌ Failed to check status: {e}")
        return {
            'worker_name': worker_name,
            'exists': False,
            'error': str(e)
        }


if __name__ == "__main__":
    print("Cloudflare tools loaded")
