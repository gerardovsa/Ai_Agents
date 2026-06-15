"""
Render REST API Client
======================
Thin wrapper over https://api.render.com/v1 for the debug agent.

Why not the render-sdk PyPI package? At time of writing the official SDK is
in beta and doesn't yet cover all the service-management endpoints the
agent needs. The REST API is stable and well-documented, and `requests`
is already in requirements.txt.

Auth: All calls require `RENDER_API_KEY` (get one from
https://dashboard.render.com/u/settings#api-keys). The agent will
degrade to log-only alerting if the key is missing.

Endpoints used:
  GET    /services                                  — list services
  GET    /services/{id}                             — service detail
  GET    /services/{id}/deploys?limit=5             — recent deploys
  POST   /services/{id}/restart                     — manual restart
  GET    /services/{id}/events                      — service events (deploy started, etc.)

Author: Cleanup round 2 (June 15, 2026)
"""
import os
import time
import logging
from typing import Optional, Dict, List, Any

try:
    import requests  # already in requirements.txt
except ImportError:  # pragma: no cover
    requests = None  # type: ignore

logger = logging.getLogger(__name__)

RENDER_API_BASE = 'https://api.render.com/v1'


class RenderClient:
    """
    Minimal Render client. All methods return ``None`` on transport error
    so the caller can decide how loudly to alert — we never raise from
    inside a probe path.
    """

    def __init__(self, api_key: Optional[str] = None, base_url: str = RENDER_API_BASE):
        self.api_key = api_key or os.getenv('RENDER_API_KEY', '').strip()
        self.base_url = base_url.rstrip('/')
        self.enabled = bool(self.api_key) and requests is not None
        if not self.enabled:
            reason = 'RENDER_API_KEY not set' if not self.api_key else 'requests not installed'
            logger.info(f'[RENDER_CLIENT] Disabled: {reason}')

    def _get(self, path: str, params: Optional[dict] = None) -> Optional[dict]:
        if not self.enabled:
            return None
        url = f'{self.base_url}{path}'
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Accept': 'application/json',
        }
        try:
            r = requests.get(url, headers=headers, params=params or {}, timeout=10)
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:  # pragma: no cover
            logger.warning(f'[RENDER_CLIENT] GET {path} failed: {e}')
            return None

    def _post(self, path: str, json_body: Optional[dict] = None) -> Optional[dict]:
        if not self.enabled:
            return None
        url = f'{self.base_url}{path}'
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        try:
            r = requests.post(url, headers=headers, json=json_body or {}, timeout=10)
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:  # pragma: no cover
            logger.warning(f'[RENDER_CLIENT] POST {path} failed: {e}')
            return None

    # ------------------------------------------------------------------------
    # Service-level operations
    # ------------------------------------------------------------------------

    def get_service(self, service_id: str) -> Optional[Dict[str, Any]]:
        """GET /services/{id} — full service detail."""
        return self._get(f'/services/{service_id}')

    def get_recent_deploys(self, service_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """GET /services/{id}/deploys?limit=N — most recent deploys first."""
        data = self._get(f'/services/{service_id}/deploys', params={'limit': limit})
        if not data:
            return []
        return data if isinstance(data, list) else data.get('items', [])

    def get_service_status(self, service_id: str) -> Optional[Dict[str, Any]]:
        """
        Compact status snapshot for the agent loop. Returns:
            {
              'service_id': str,
              'name': str,
              'state': 'active' | 'build_in_progress' | 'suspended' | 'deactivated' | 'deleted',
              'last_deploy': { 'id': str, 'status': str, 'createdAt': str },
              'url': str,
              'suspendedAt': str | None,
            }
        """
        svc = self.get_service(service_id)
        if not svc:
            return None
        deploys = self.get_recent_deploys(service_id, limit=1)
        return {
            'service_id': svc.get('service', {}).get('id', service_id),
            'name': svc.get('service', {}).get('name', 'unknown'),
            'state': svc.get('service', {}).get('suspended', 'active') and 'suspended' or 'active',
            'last_deploy': deploys[0] if deploys else None,
            'url': svc.get('service', {}).get('serviceDetails', {}).get('url'),
            'suspendedAt': svc.get('service', {}).get('suspendedAt'),
        }

    def restart_service(self, service_id: str) -> Optional[Dict[str, Any]]:
        """
        POST /services/{id}/restart — manual restart. Used by the agent's
        self-heal path. Render charges a small amount of build minutes for
        this, so the agent should only call it when /health is failing
        AND the service is not already restarting.
        """
        logger.warning(f'[RENDER_CLIENT] restart_service({service_id}) — manual restart triggered')
        return self._post(f'/services/{service_id}/restart')
