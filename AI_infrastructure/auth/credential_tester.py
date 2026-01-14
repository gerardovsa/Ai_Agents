"""
Credential Tester - Test platform credentials with real API calls

This module tests platform credentials by making simple, non-destructive API calls
to verify that the credentials are valid and properly configured.

Supported Platforms:
- Google Workspace (OAuth)
- Microsoft 365 (OAuth)
- Pinecone (API Key)
- Voyager AI (API Key)
- OpenAI (API Key)
- Anthropic (API Key)
- Stripe (API Key)
- Shopify (API Key)
- Xero (OAuth)
- Twilio (API Key)
- SendGrid (API Key)
- AssemblyAI (API Key)
- Cloudflare (API Key)
- Render (API Key)
- Supabase (API Key)
- PayPal (Client ID + Secret)

Usage:
    tester = CredentialTester()
    
    result = tester.test_credential(
        platform='pinecone',
        credentials={'API_KEY': 'pcsk_...'},
        settings={'index_name': 'myindex'}
    )
    
    # result = {
    #     'success': True,
    #     'message': 'Successfully connected to Pinecone',
    #     'details': {'index_count': 1, 'environment': 'us-east-1'}
    # }

Author: AI Agent Platform Team
Date: November 29, 2025
"""

import logging
import requests
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class CredentialTester:
    """
    Test platform credentials with actual API calls
    """
    
    def __init__(self):
        """Initialize credential tester"""
        self.timeout = 10  # seconds
    
    def test_credential(self, platform: str, credentials: Dict[str, str], settings: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Test credentials for a specific platform
        
        Args:
            platform: Platform identifier (e.g., 'pinecone', 'stripe')
            credentials: Dictionary of credentials (API keys, tokens, etc.)
            settings: Optional settings dictionary (indexes, models, etc.)
        
        Returns:
            Dictionary with test results:
            {
                'success': True/False,
                'message': 'Success or error message',
                'details': {...},  # Platform-specific details
                'error': 'Error details if failed'
            }
        """
        settings = settings or {}
        
        # Map platform to test method
        test_methods = {
            'pinecone': self._test_pinecone,
            'voyager': self._test_voyager,
            'openai': self._test_openai,
            'anthropic': self._test_anthropic,
            'stripe': self._test_stripe,
            'shopify': self._test_shopify,
            'xero': self._test_xero,
            'twilio': self._test_twilio,
            'sendgrid': self._test_sendgrid,
            'assemblyai': self._test_assemblyai,
            'cloudflare': self._test_cloudflare,
            'render': self._test_render,
            'supabase': self._test_supabase,
            'paypal': self._test_paypal,
            'google': self._test_google_oauth,
            'microsoft': self._test_microsoft_oauth,
            'kajabi': self._test_kajabi
        }
        
        test_method = test_methods.get(platform)
        
        if not test_method:
            return {
                'success': False,
                'message': f'Testing not implemented for platform: {platform}',
                'error': 'Unsupported platform'
            }
        
        try:
            return test_method(credentials, settings)
        
        except Exception as e:
            logger.error(f"❌ Credential test failed for {platform}: {e}")
            return {
                'success': False,
                'message': f'Test failed: {str(e)}',
                'error': str(e)
            }
    
    def _test_pinecone(self, credentials: Dict, settings: Dict) -> Dict:
        """Test Pinecone credentials"""
        try:
            api_key = credentials.get('PINECONE_API_KEY') or credentials.get('API_KEY')
            
            if not api_key:
                return {'success': False, 'message': 'API key not provided', 'error': 'Missing API_KEY'}
            
            # Test: List indexes
            from pinecone import Pinecone
            
            pc = Pinecone(api_key=api_key)
            indexes = pc.list_indexes()
            
            index_names = [idx['name'] for idx in indexes] if indexes else []
            
            # Check if specified index exists
            index_name = settings.get('index_name')
            index_exists = index_name in index_names if index_name else True
            
            return {
                'success': True,
                'message': f'Connected to Pinecone successfully',
                'details': {
                    'indexes': index_names,
                    'index_count': len(index_names),
                    'specified_index': index_name,
                    'index_exists': index_exists
                }
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Pinecone connection failed: {str(e)}',
                'error': str(e)
            }
    
    def _test_voyager(self, credentials: Dict, settings: Dict) -> Dict:
        """Test Voyager AI credentials"""
        try:
            api_key = credentials.get('API_KEY')
            
            if not api_key:
                return {'success': False, 'message': 'API key not provided', 'error': 'Missing API_KEY'}
            
            # Test: Ping endpoint or get models
            headers = {'Authorization': f'Bearer {api_key}'}
            response = requests.get('https://api.voyageai.com/v1/models', headers=headers, timeout=self.timeout)
            
            if response.status_code == 200:
                models = response.json().get('data', [])
                model_names = [m['id'] for m in models]
                
                return {
                    'success': True,
                    'message': 'Connected to Voyager AI successfully',
                    'details': {
                        'models': model_names,
                        'model_count': len(model_names)
                    }
                }
            else:
                return {
                    'success': False,
                    'message': f'Voyager AI returned status {response.status_code}',
                    'error': response.text
                }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Voyager AI connection failed: {str(e)}',
                'error': str(e)
            }
    
    def _test_openai(self, credentials: Dict, settings: Dict) -> Dict:
        """Test OpenAI credentials"""
        try:
            api_key = credentials.get('OPENAI_API_KEY') or credentials.get('API_KEY')
            
            if not api_key:
                return {'success': False, 'message': 'API key not provided', 'error': 'Missing API_KEY'}
            
            # Test: List models
            from openai import OpenAI
            
            client = OpenAI(api_key=api_key)
            models = client.models.list()
            
            model_ids = [m.id for m in models.data]
            
            return {
                'success': True,
                'message': 'Connected to OpenAI successfully',
                'details': {
                    'models': model_ids[:10],  # First 10 models
                    'total_models': len(model_ids)
                }
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'OpenAI connection failed: {str(e)}',
                'error': str(e)
            }
    
    def _test_anthropic(self, credentials: Dict, settings: Dict) -> Dict:
        """Test Anthropic credentials"""
        try:
            api_key = credentials.get('ANTHROPIC_API_KEY') or credentials.get('API_KEY')
            
            if not api_key:
                return {'success': False, 'message': 'API key not provided', 'error': 'Missing API_KEY'}
            
            # Test: Simple completion
            import anthropic
            
            client = anthropic.Anthropic(api_key=api_key)
            
            # Minimal test message
            message = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=10,
                messages=[{"role": "user", "content": "Hi"}]
            )
            
            return {
                'success': True,
                'message': 'Connected to Anthropic Claude successfully',
                'details': {
                    'model': 'claude-3-haiku-20240307',
                    'response': message.content[0].text if message.content else ''
                }
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Anthropic connection failed: {str(e)}',
                'error': str(e)
            }
    
    def _test_stripe(self, credentials: Dict, settings: Dict) -> Dict:
        """Test Stripe credentials"""
        try:
            api_key = credentials.get('STRIPE_API_KEY') or credentials.get('API_KEY')
            
            if not api_key:
                return {'success': False, 'message': 'API key not provided', 'error': 'Missing API_KEY'}
            
            # Test: Retrieve account info
            import stripe
            
            stripe.api_key = api_key
            account = stripe.Account.retrieve()
            
            return {
                'success': True,
                'message': 'Connected to Stripe successfully',
                'details': {
                    'account_id': account.id,
                    'email': account.email,
                    'country': account.country,
                    'currency': account.default_currency
                }
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Stripe connection failed: {str(e)}',
                'error': str(e)
            }
    
    def _test_shopify(self, credentials: Dict, settings: Dict) -> Dict:
        """Test Shopify credentials"""
        try:
            api_key = credentials.get('SHOPIFY_API_KEY') or credentials.get('API_KEY')
            store_url = credentials.get('SHOPIFY_STORE_URL')
            
            if not api_key or not store_url:
                return {'success': False, 'message': 'API key or store URL not provided', 'error': 'Missing credentials'}
            
            # Test: Get shop info
            url = f'https://{store_url}/admin/api/2024-01/shop.json'
            headers = {'X-Shopify-Access-Token': api_key}
            
            response = requests.get(url, headers=headers, timeout=self.timeout)
            
            if response.status_code == 200:
                shop = response.json().get('shop', {})
                return {
                    'success': True,
                    'message': 'Connected to Shopify successfully',
                    'details': {
                        'shop_name': shop.get('name'),
                        'email': shop.get('email'),
                        'domain': shop.get('domain'),
                        'currency': shop.get('currency')
                    }
                }
            else:
                return {
                    'success': False,
                    'message': f'Shopify returned status {response.status_code}',
                    'error': response.text
                }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Shopify connection failed: {str(e)}',
                'error': str(e)
            }
    
    def _test_xero(self, credentials: Dict, settings: Dict) -> Dict:
        """Test Xero credentials (OAuth)"""
        return {
            'success': False,
            'message': 'Xero testing requires OAuth flow - not supported yet',
            'error': 'OAuth testing not implemented'
        }
    
    def _test_twilio(self, credentials: Dict, settings: Dict) -> Dict:
        """Test Twilio credentials"""
        try:
            account_sid = credentials.get('TWILIO_ACCOUNT_SID')
            auth_token = credentials.get('TWILIO_AUTH_TOKEN')
            
            if not account_sid or not auth_token:
                return {'success': False, 'message': 'Account SID or Auth Token not provided', 'error': 'Missing credentials'}
            
            # Test: Get account info
            from twilio.rest import Client
            
            client = Client(account_sid, auth_token)
            account = client.api.accounts(account_sid).fetch()
            
            return {
                'success': True,
                'message': 'Connected to Twilio successfully',
                'details': {
                    'account_sid': account.sid,
                    'friendly_name': account.friendly_name,
                    'status': account.status
                }
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Twilio connection failed: {str(e)}',
                'error': str(e)
            }
    
    def _test_sendgrid(self, credentials: Dict, settings: Dict) -> Dict:
        """Test SendGrid credentials"""
        try:
            api_key = credentials.get('SENDGRID_API_KEY') or credentials.get('API_KEY')
            
            if not api_key:
                return {'success': False, 'message': 'API key not provided', 'error': 'Missing API_KEY'}
            
            # Test: Get API key info
            headers = {'Authorization': f'Bearer {api_key}'}
            response = requests.get('https://api.sendgrid.com/v3/scopes', headers=headers, timeout=self.timeout)
            
            if response.status_code == 200:
                scopes = response.json().get('scopes', [])
                return {
                    'success': True,
                    'message': 'Connected to SendGrid successfully',
                    'details': {
                        'scopes': scopes[:10],  # First 10 scopes
                        'total_scopes': len(scopes)
                    }
                }
            else:
                return {
                    'success': False,
                    'message': f'SendGrid returned status {response.status_code}',
                    'error': response.text
                }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'SendGrid connection failed: {str(e)}',
                'error': str(e)
            }
    
    def _test_assemblyai(self, credentials: Dict, settings: Dict) -> Dict:
        """Test AssemblyAI credentials"""
        try:
            api_key = credentials.get('ASSEMBLYAI_API_KEY') or credentials.get('API_KEY')
            
            if not api_key:
                return {'success': False, 'message': 'API key not provided', 'error': 'Missing API_KEY'}
            
            # Test: Get account info
            headers = {'authorization': api_key}
            response = requests.get('https://api.assemblyai.com/v2/transcript', headers=headers, timeout=self.timeout)
            
            if response.status_code in [200, 404]:  # 404 is OK (no transcripts yet)
                return {
                    'success': True,
                    'message': 'Connected to AssemblyAI successfully',
                    'details': {
                        'api_version': 'v2',
                        'status': 'active'
                    }
                }
            else:
                return {
                    'success': False,
                    'message': f'AssemblyAI returned status {response.status_code}',
                    'error': response.text
                }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'AssemblyAI connection failed: {str(e)}',
                'error': str(e)
            }
    
    def _test_cloudflare(self, credentials: Dict, settings: Dict) -> Dict:
        """Test Cloudflare credentials"""
        try:
            api_key = credentials.get('CLOUDFLARE_API_KEY') or credentials.get('API_KEY')
            
            if not api_key:
                return {'success': False, 'message': 'API key not provided', 'error': 'Missing API_KEY'}
            
            # Test: Get zones
            headers = {'Authorization': f'Bearer {api_key}'}
            response = requests.get('https://api.cloudflare.com/client/v4/zones', headers=headers, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                zones = data.get('result', [])
                return {
                    'success': True,
                    'message': 'Connected to Cloudflare successfully',
                    'details': {
                        'zones': [z['name'] for z in zones],
                        'zone_count': len(zones)
                    }
                }
            else:
                return {
                    'success': False,
                    'message': f'Cloudflare returned status {response.status_code}',
                    'error': response.text
                }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Cloudflare connection failed: {str(e)}',
                'error': str(e)
            }
    
    def _test_render(self, credentials: Dict, settings: Dict) -> Dict:
        """Test Render credentials"""
        try:
            api_key = credentials.get('RENDER_API_KEY') or credentials.get('API_KEY')
            
            if not api_key:
                return {'success': False, 'message': 'API key not provided', 'error': 'Missing API_KEY'}
            
            # Test: Get services
            headers = {'Authorization': f'Bearer {api_key}'}
            response = requests.get('https://api.render.com/v1/services', headers=headers, timeout=self.timeout)
            
            if response.status_code == 200:
                services = response.json()
                return {
                    'success': True,
                    'message': 'Connected to Render successfully',
                    'details': {
                        'services': [s['name'] for s in services] if isinstance(services, list) else [],
                        'service_count': len(services) if isinstance(services, list) else 0
                    }
                }
            else:
                return {
                    'success': False,
                    'message': f'Render returned status {response.status_code}',
                    'error': response.text
                }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Render connection failed: {str(e)}',
                'error': str(e)
            }
    
    def _test_supabase(self, credentials: Dict, settings: Dict) -> Dict:
        """Test Supabase credentials"""
        try:
            url = credentials.get('SUPABASE_URL')
            key = credentials.get('SUPABASE_KEY') or credentials.get('API_KEY')
            
            if not url or not key:
                return {'success': False, 'message': 'URL or API key not provided', 'error': 'Missing credentials'}
            
            # Test: Ping REST API
            headers = {'apikey': key, 'Authorization': f'Bearer {key}'}
            response = requests.get(f'{url}/rest/v1/', headers=headers, timeout=self.timeout)
            
            if response.status_code in [200, 404]:  # 404 is OK (root endpoint)
                return {
                    'success': True,
                    'message': 'Connected to Supabase successfully',
                    'details': {
                        'project_url': url,
                        'status': 'active'
                    }
                }
            else:
                return {
                    'success': False,
                    'message': f'Supabase returned status {response.status_code}',
                    'error': response.text
                }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Supabase connection failed: {str(e)}',
                'error': str(e)
            }
    
    def _test_paypal(self, credentials: Dict, settings: Dict) -> Dict:
        """Test PayPal credentials"""
        try:
            client_id = credentials.get('PAYPAL_CLIENT_ID')
            client_secret = credentials.get('PAYPAL_CLIENT_SECRET')
            
            if not client_id or not client_secret:
                return {'success': False, 'message': 'Client ID or Secret not provided', 'error': 'Missing credentials'}
            
            # Test: Get OAuth token
            import base64
            auth = base64.b64encode(f'{client_id}:{client_secret}'.encode()).decode()
            headers = {
                'Authorization': f'Basic {auth}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            data = {'grant_type': 'client_credentials'}
            
            # Use sandbox endpoint for testing
            response = requests.post('https://api-m.sandbox.paypal.com/v1/oauth2/token', 
                                    headers=headers, data=data, timeout=self.timeout)
            
            if response.status_code == 200:
                token_data = response.json()
                return {
                    'success': True,
                    'message': 'Connected to PayPal successfully',
                    'details': {
                        'token_type': token_data.get('token_type'),
                        'scope': token_data.get('scope'),
                        'environment': 'sandbox'
                    }
                }
            else:
                return {
                    'success': False,
                    'message': f'PayPal returned status {response.status_code}',
                    'error': response.text
                }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'PayPal connection failed: {str(e)}',
                'error': str(e)
            }
    
    def _test_google_oauth(self, credentials: Dict, settings: Dict) -> Dict:
        """Test Google OAuth credentials"""
        try:
            access_token = credentials.get('access_token')
            
            if not access_token:
                return {'success': False, 'message': 'Access token not provided', 'error': 'Missing access_token'}
            
            # Test: Get user info
            headers = {'Authorization': f'Bearer {access_token}'}
            response = requests.get('https://www.googleapis.com/oauth2/v2/userinfo', headers=headers, timeout=self.timeout)
            
            if response.status_code == 200:
                user_info = response.json()
                return {
                    'success': True,
                    'message': 'Google OAuth token valid',
                    'details': {
                        'email': user_info.get('email'),
                        'name': user_info.get('name'),
                        'verified_email': user_info.get('verified_email')
                    }
                }
            else:
                return {
                    'success': False,
                    'message': f'Google returned status {response.status_code}',
                    'error': response.text
                }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Google OAuth test failed: {str(e)}',
                'error': str(e)
            }
    
    def _test_microsoft_oauth(self, credentials: Dict, settings: Dict) -> Dict:
        """Test Microsoft OAuth credentials"""
        try:
            access_token = credentials.get('access_token')
            
            if not access_token:
                return {'success': False, 'message': 'Access token not provided', 'error': 'Missing access_token'}
            
            # Test: Get user info
            headers = {'Authorization': f'Bearer {access_token}'}
            response = requests.get('https://graph.microsoft.com/v1.0/me', headers=headers, timeout=self.timeout)
            
            if response.status_code == 200:
                user_info = response.json()
                return {
                    'success': True,
                    'message': 'Microsoft OAuth token valid',
                    'details': {
                        'email': user_info.get('mail') or user_info.get('userPrincipalName'),
                        'display_name': user_info.get('displayName'),
                        'id': user_info.get('id')
                    }
                }
            else:
                return {
                    'success': False,
                    'message': f'Microsoft returned status {response.status_code}',
                    'error': response.text
                }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Microsoft OAuth test failed: {str(e)}',
                'error': str(e)
            }
    
    def _test_kajabi(self, credentials: Dict, settings: Dict) -> Dict:
        """Test Kajabi credentials"""
        try:
            api_key = credentials.get('API_KEY') or credentials.get('api_key')
            
            if not api_key:
                return {'success': False, 'message': 'API key not provided', 'error': 'Missing API_KEY'}
            
            # Test: Get site details
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Accept': 'application/json'
            }
            response = requests.get('https://api.kajabi.com/v1/site', headers=headers, timeout=self.timeout)
            
            if response.status_code == 200:
                site_info = response.json()
                return {
                    'success': True,
                    'message': 'Connected to Kajabi successfully',
                    'details': {
                        'site_name': site_info.get('site', {}).get('name'),
                        'domain': site_info.get('site', {}).get('domain'),
                        'site_id': site_info.get('site', {}).get('id')
                    }
                }
            else:
                return {
                    'success': False,
                    'message': f'Kajabi returned status {response.status_code}',
                    'error': response.text
                }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Kajabi connection failed: {str(e)}',
                'error': str(e)
            }


if __name__ == '__main__':
    """
    Test the credential tester
    
    Usage:
        python credential_tester.py
    """
    print("=" * 60)
    print("Credential Tester - Test Module")
    print("=" * 60)
    
    tester = CredentialTester()
    
    # Test Pinecone (example)
    print("\nTest 1: Pinecone (Mock)")
    result = tester.test_credential(
        platform='pinecone',
        credentials={'API_KEY': 'test_key'},
        settings={'index_name': 'test_index'}
    )
    print(f"  Success: {result['success']}")
    print(f"  Message: {result['message']}")
    
    print("\n" + "=" * 60)
    print("Credential Tester Ready!")
    print("=" * 60)
