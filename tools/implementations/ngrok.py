"""
Ngrok Tool Implementations
===========================

This module provides tool implementations for Ngrok tunneling.
"""

import os
from pyngrok import ngrok, conf

try:
    from config import get_api_key_enhanced
    auth_token = get_api_key_enhanced('NGROK_AUTHTOKEN')
    if auth_token:
        conf.get_default().auth_token = auth_token
except ImportError:
    auth_token = os.getenv('NGROK_AUTHTOKEN')
    if auth_token:
        conf.get_default().auth_token = auth_token


def ngrok_start_tunnel(port: int, protocol: str = "http", subdomain: str = None):
    """
    Start an HTTP/HTTPS tunnel to localhost.
    
    Args:
        port: Local port to expose
        protocol: 'http' or 'tcp'
        subdomain: Custom subdomain (requires paid plan)
    
    Returns:
        Tunnel info with public URL
    """
    print(f"🔧 Starting ngrok tunnel for port {port}")
    
    try:
        # Configure tunnel options
        options = {}
        if subdomain:
            options['subdomain'] = subdomain
        
        # Start tunnel
        tunnel = ngrok.connect(port, protocol, **options)
        
        return {
            'public_url': tunnel.public_url,
            'protocol': tunnel.proto,
            'port': port,
            'tunnel_name': tunnel.name,
            'config': tunnel.config
        }
        
    except Exception as e:
        print(f"❌ Failed to start tunnel: {e}")
        raise


def ngrok_list_tunnels():
    """
    List all active ngrok tunnels.
    
    Returns:
        List of active tunnels
    """
    print("🔧 Listing ngrok tunnels")
    
    try:
        tunnels = ngrok.get_tunnels()
        
        return {
            'tunnels': [
                {
                    'name': t.name,
                    'public_url': t.public_url,
                    'protocol': t.proto,
                    'config': t.config
                }
                for t in tunnels
            ],
            'count': len(tunnels)
        }
        
    except Exception as e:
        print(f"❌ Failed to list tunnels: {e}")
        raise


def ngrok_stop_tunnel(tunnel_name: str):
    """
    Stop a specific ngrok tunnel.
    
    Args:
        tunnel_name: Name of the tunnel to stop
    
    Returns:
        Confirmation
    """
    print(f"🔧 Stopping ngrok tunnel: {tunnel_name}")
    
    try:
        # Find and disconnect tunnel
        tunnels = ngrok.get_tunnels()
        for tunnel in tunnels:
            if tunnel.name == tunnel_name:
                ngrok.disconnect(tunnel.public_url)
                return {
                    'stopped': True,
                    'tunnel_name': tunnel_name
                }
        
        return {
            'stopped': False,
            'error': f'Tunnel {tunnel_name} not found'
        }
        
    except Exception as e:
        print(f"❌ Failed to stop tunnel: {e}")
        raise


def ngrok_get_public_url(port: int):
    """
    Get the public URL for a local port.
    
    Args:
        port: Local port number
    
    Returns:
        Public URL for the port
    """
    print(f"🔧 Getting public URL for port {port}")
    
    try:
        tunnels = ngrok.get_tunnels()
        
        for tunnel in tunnels:
            # Check if this tunnel is for the requested port
            if str(port) in tunnel.config.get('addr', ''):
                return {
                    'port': port,
                    'public_url': tunnel.public_url,
                    'tunnel_name': tunnel.name
                }
        
        return {
            'port': port,
            'public_url': None,
            'error': f'No tunnel found for port {port}'
        }
        
    except Exception as e:
        print(f"❌ Failed to get public URL: {e}")
        raise


if __name__ == "__main__":
    print("Ngrok tools loaded")
