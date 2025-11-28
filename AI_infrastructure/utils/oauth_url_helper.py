"""
OAuth URL Helper - Smart Frontend URL Detection
================================================

Automatically detects the correct frontend URL for OAuth redirects,
solving the problem where request.url_root returns the Render service name
instead of custom domain aliases (e.g., v10, v9).

Detection Priority:
1. Session storage (oauth_origin_url) - Most reliable
2. Referer header - Where user came from
3. Origin header - Browser-provided origin
4. FRONTEND_URL env var - Manual override
5. request.url_root - Fallback (service name)

Usage:
    from AI_infrastructure.utils.oauth_url_helper import get_frontend_url, capture_oauth_origin
    
    # At OAuth start:
    capture_oauth_origin(request, session)
    
    # At OAuth callback:
    frontend_url = get_frontend_url(request, session)
    return redirect(f'{frontend_url}/?token={jwt_token}')
"""

import os
from urllib.parse import urlparse
from flask import request, session


def capture_oauth_origin(request_obj, session_obj):
    """
    Capture the origin URL where user started OAuth flow.
    Call this at the START of OAuth (e.g., /login endpoint).
    
    Args:
        request_obj: Flask request object
        session_obj: Flask session object
    
    Returns:
        str: Captured origin URL or None
    """
    origin_url = None
    
    # Try Referer header first (most common)
    if request_obj.referrer:
        parsed = urlparse(request_obj.referrer)
        origin_url = f"{parsed.scheme}://{parsed.netloc}"
        session_obj['oauth_origin_url'] = origin_url
        print(f"🌐 [OAuth Origin] Captured from Referer: {origin_url}")
        return origin_url
    
    # Try Origin header (CORS requests)
    if request_obj.headers.get('Origin'):
        origin_url = request_obj.headers.get('Origin')
        session_obj['oauth_origin_url'] = origin_url
        print(f"🌐 [OAuth Origin] Captured from Origin header: {origin_url}")
        return origin_url
    
    # Try Host header as last resort
    if request_obj.host:
        scheme = 'https' if request_obj.is_secure else 'http'
        origin_url = f"{scheme}://{request_obj.host}"
        session_obj['oauth_origin_url'] = origin_url
        print(f"🌐 [OAuth Origin] Captured from Host header: {origin_url}")
        return origin_url
    
    print(f"⚠️  [OAuth Origin] Could not capture origin URL")
    return None


def get_frontend_url(request_obj, session_obj=None):
    """
    Get the correct frontend URL for OAuth redirects.
    Uses smart detection to find the actual user-facing URL.
    
    Args:
        request_obj: Flask request object
        session_obj: Flask session object (optional)
    
    Returns:
        str: Frontend URL to redirect to
    """
    frontend_url = None
    detection_method = None
    
    # Priority 1: OAuth origin from session (captured at OAuth start)
    if session_obj and 'oauth_origin_url' in session_obj:
        frontend_url = session_obj['oauth_origin_url']
        detection_method = "session (oauth_origin_url)"
    
    # Priority 2: Referer header
    if not frontend_url and request_obj.referrer:
        parsed = urlparse(request_obj.referrer)
        frontend_url = f"{parsed.scheme}://{parsed.netloc}"
        detection_method = "Referer header"
    
    # Priority 3: Origin header
    if not frontend_url and request_obj.headers.get('Origin'):
        frontend_url = request_obj.headers.get('Origin')
        detection_method = "Origin header"
    
    # Priority 4: FRONTEND_URL environment variable (manual override)
    if not frontend_url and os.getenv('FRONTEND_URL'):
        frontend_url = os.getenv('FRONTEND_URL')
        detection_method = "FRONTEND_URL env var"
    
    # Priority 5: request.url_root (fallback - may return service name)
    if not frontend_url:
        frontend_url = request_obj.url_root.rstrip('/')
        detection_method = "request.url_root (fallback)"
    
    # Ensure HTTPS for Render deployments
    if 'onrender.com' in frontend_url or os.getenv('RENDER') == 'true':
        frontend_url = frontend_url.replace('http://', 'https://')
    
    # Force HTTP for localhost (prevent browser HTTPS upgrade)
    if 'localhost' in frontend_url or '127.0.0.1' in frontend_url:
        frontend_url = frontend_url.replace('https://', 'http://')
    
    print(f"🔀 [Frontend URL] Detected via {detection_method}: {frontend_url}")
    
    return frontend_url


def clear_oauth_origin(session_obj):
    """
    Clear OAuth origin from session after successful redirect.
    
    Args:
        session_obj: Flask session object
    """
    if 'oauth_origin_url' in session_obj:
        del session_obj['oauth_origin_url']
        print(f"🧹 [OAuth Origin] Cleared from session")
