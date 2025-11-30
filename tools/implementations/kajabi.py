"""
Kajabi Knowledge Commerce Platform API Implementation
Handles courses, memberships, members, products, offers, and webhooks
"""
import requests
from typing import Dict, Any, Optional, List


class KajabiError(Exception):
    """Custom exception for Kajabi API errors"""
    pass


class KajabiTools:
    """Kajabi API Tools - Knowledge Commerce Platform"""
    
    def __init__(self):
        """Initialize Kajabi API client"""
        self.base_url = "https://api.kajabi.com"
        self.api_key = None
        self.site_id = None
    
    def _get_headers(self, **kwargs) -> Dict[str, str]:
        """Get headers for API requests with credential injection"""
        api_key = kwargs.get('kajabi_api_key') or kwargs.get('api_key')
        
        if not api_key:
            raise KajabiError("Kajabi API key not provided")
        
        return {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make API request with error handling"""
        headers = self._get_headers(**kwargs)
        url = f"{self.base_url}{endpoint}"
        
        try:
            params = kwargs.get('params', {})
            data = kwargs.get('json')
            
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=data,
                timeout=30
            )
            
            response.raise_for_status()
            
            if response.status_code == 204:  # No content
                return {'success': True, 'message': 'Operation completed successfully'}
            
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"Kajabi API error: {e.response.status_code}"
            try:
                error_data = e.response.json()
                error_msg += f" - {error_data.get('message', str(error_data))}"
            except:
                error_msg += f" - {e.response.text}"
            raise KajabiError(error_msg)
        
        except requests.exceptions.RequestException as e:
            raise KajabiError(f"Request failed: {str(e)}")
    
    # ==================== PRODUCTS ====================
    
    def list_products(self, page: int = 1, per_page: int = 25, type: Optional[str] = None, **kwargs) -> Dict:
        """List all products (courses, memberships, coaching programs)"""
        params = {'page': page, 'per_page': min(per_page, 100)}
        if type:
            params['type'] = type
        
        return self._make_request('GET', '/v1/products', params=params, **kwargs)
    
    def get_product(self, product_id: str, **kwargs) -> Dict:
        """Get product details by ID"""
        return self._make_request('GET', f'/v1/products/{product_id}', **kwargs)
    
    # ==================== OFFERS ====================
    
    def list_offers(self, page: int = 1, per_page: int = 25, product_id: Optional[str] = None, **kwargs) -> Dict:
        """List all offers (payment plans)"""
        params = {'page': page, 'per_page': min(per_page, 100)}
        if product_id:
            params['product_id'] = product_id
        
        return self._make_request('GET', '/v1/offers', params=params, **kwargs)
    
    def get_offer(self, offer_id: str, **kwargs) -> Dict:
        """Get offer details by ID"""
        return self._make_request('GET', f'/v1/offers/{offer_id}', **kwargs)
    
    # ==================== MEMBERS ====================
    
    def list_members(self, page: int = 1, per_page: int = 25, email: Optional[str] = None, 
                    status: Optional[str] = None, **kwargs) -> Dict:
        """List all members (customers/students)"""
        params = {'page': page, 'per_page': min(per_page, 100)}
        if email:
            params['email'] = email
        if status:
            params['status'] = status
        
        return self._make_request('GET', '/v1/members', params=params, **kwargs)
    
    def get_member(self, member_id: str, **kwargs) -> Dict:
        """Get member details by ID"""
        return self._make_request('GET', f'/v1/members/{member_id}', **kwargs)
    
    def search_members(self, query: str, page: int = 1, per_page: int = 25, **kwargs) -> Dict:
        """Search members by email, name, or custom fields"""
        params = {
            'query': query,
            'page': page,
            'per_page': min(per_page, 100)
        }
        return self._make_request('GET', '/v1/members/search', params=params, **kwargs)
    
    # ==================== MEMBER ACCESS ====================
    
    def grant_product_access(self, member_id: str, product_id: str, offer_id: Optional[str] = None, **kwargs) -> Dict:
        """Grant a member access to a product"""
        data = {
            'member_id': member_id,
            'product_id': product_id
        }
        if offer_id:
            data['offer_id'] = offer_id
        
        return self._make_request('POST', '/v1/member_access', json=data, **kwargs)
    
    def revoke_product_access(self, member_id: str, product_id: str, **kwargs) -> Dict:
        """Revoke a member's access to a product"""
        return self._make_request('DELETE', f'/v1/member_access/{member_id}/{product_id}', **kwargs)
    
    # ==================== WEBHOOKS ====================
    
    def list_webhooks(self, page: int = 1, per_page: int = 25, **kwargs) -> Dict:
        """List all webhooks"""
        params = {'page': page, 'per_page': min(per_page, 100)}
        return self._make_request('GET', '/v1/webhooks', params=params, **kwargs)
    
    def create_webhook(self, url: str, events: List[str], active: bool = True, **kwargs) -> Dict:
        """Create a new webhook"""
        data = {
            'url': url,
            'events': events,
            'active': active
        }
        return self._make_request('POST', '/v1/webhooks', json=data, **kwargs)
    
    def delete_webhook(self, webhook_id: str, **kwargs) -> Dict:
        """Delete a webhook"""
        return self._make_request('DELETE', f'/v1/webhooks/{webhook_id}', **kwargs)
    
    # ==================== FORM SUBMISSIONS ====================
    
    def list_form_submissions(self, form_id: Optional[str] = None, page: int = 1, per_page: int = 25,
                             start_date: Optional[str] = None, end_date: Optional[str] = None, **kwargs) -> Dict:
        """List form submissions"""
        params = {'page': page, 'per_page': min(per_page, 100)}
        if form_id:
            params['form_id'] = form_id
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        
        return self._make_request('GET', '/v1/form_submissions', params=params, **kwargs)
    
    def get_form_submission(self, submission_id: str, **kwargs) -> Dict:
        """Get form submission details by ID"""
        return self._make_request('GET', f'/v1/form_submissions/{submission_id}', **kwargs)
    
    # ==================== SITE ====================
    
    def get_site_details(self, **kwargs) -> Dict:
        """Get site details (account info)"""
        return self._make_request('GET', '/v1/site', **kwargs)
    
    # ==================== TAGS ====================
    
    def list_tags(self, page: int = 1, per_page: int = 25, **kwargs) -> Dict:
        """List all member tags"""
        params = {'page': page, 'per_page': min(per_page, 100)}
        return self._make_request('GET', '/v1/tags', params=params, **kwargs)
    
    def add_member_tag(self, member_id: str, tag: str, **kwargs) -> Dict:
        """Add a tag to a member"""
        data = {'tag': tag}
        return self._make_request('POST', f'/v1/members/{member_id}/tags', json=data, **kwargs)
    
    def remove_member_tag(self, member_id: str, tag: str, **kwargs) -> Dict:
        """Remove a tag from a member"""
        return self._make_request('DELETE', f'/v1/members/{member_id}/tags/{tag}', **kwargs)


# ============================================================================
# TOOL FUNCTIONS (Exported for registry)
# ============================================================================

def kajabi_list_products(**kwargs):
    """List all products"""
    tools = KajabiTools()
    return tools.list_products(**kwargs)


def kajabi_get_product(**kwargs):
    """Get product details"""
    tools = KajabiTools()
    return tools.get_product(**kwargs)


def kajabi_list_offers(**kwargs):
    """List all offers"""
    tools = KajabiTools()
    return tools.list_offers(**kwargs)


def kajabi_get_offer(**kwargs):
    """Get offer details"""
    tools = KajabiTools()
    return tools.get_offer(**kwargs)


def kajabi_list_members(**kwargs):
    """List all members"""
    tools = KajabiTools()
    return tools.list_members(**kwargs)


def kajabi_get_member(**kwargs):
    """Get member details"""
    tools = KajabiTools()
    return tools.get_member(**kwargs)


def kajabi_search_members(**kwargs):
    """Search members"""
    tools = KajabiTools()
    return tools.search_members(**kwargs)


def kajabi_grant_product_access(**kwargs):
    """Grant product access to member"""
    tools = KajabiTools()
    return tools.grant_product_access(**kwargs)


def kajabi_revoke_product_access(**kwargs):
    """Revoke product access from member"""
    tools = KajabiTools()
    return tools.revoke_product_access(**kwargs)


def kajabi_list_webhooks(**kwargs):
    """List all webhooks"""
    tools = KajabiTools()
    return tools.list_webhooks(**kwargs)


def kajabi_create_webhook(**kwargs):
    """Create a webhook"""
    tools = KajabiTools()
    return tools.create_webhook(**kwargs)


def kajabi_delete_webhook(**kwargs):
    """Delete a webhook"""
    tools = KajabiTools()
    return tools.delete_webhook(**kwargs)


def kajabi_list_form_submissions(**kwargs):
    """List form submissions"""
    tools = KajabiTools()
    return tools.list_form_submissions(**kwargs)


def kajabi_get_form_submission(**kwargs):
    """Get form submission details"""
    tools = KajabiTools()
    return tools.get_form_submission(**kwargs)


def kajabi_get_site_details(**kwargs):
    """Get site details"""
    tools = KajabiTools()
    return tools.get_site_details(**kwargs)


def kajabi_list_tags(**kwargs):
    """List all tags"""
    tools = KajabiTools()
    return tools.list_tags(**kwargs)


def kajabi_add_member_tag(**kwargs):
    """Add tag to member"""
    tools = KajabiTools()
    return tools.add_member_tag(**kwargs)


def kajabi_remove_member_tag(**kwargs):
    """Remove tag from member"""
    tools = KajabiTools()
    return tools.remove_member_tag(**kwargs)
