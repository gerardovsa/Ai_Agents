"""
Microsoft 365 OAuth Manager
===========================

Unified OAuth 2.0 authentication for Microsoft 365 login and services:
- User Authentication (Login with Microsoft)
- Outlook Email
- OneDrive
- Microsoft Teams
- Calendar
- Office 365 (Word, Excel, PowerPoint)

Features:
- Single Sign-On (SSO) with Microsoft accounts
- Multi-tenant support (personal + organizational accounts)
- Token refresh and storage
- Secure credential management

Author: Valor AI Platform
Date: October 28, 2025
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Microsoft365OAuthManager:
    """
    Microsoft 365 OAuth 2.0 Manager
    
    Handles authentication for Microsoft 365 services and user login
    """
    
    # Microsoft Identity Platform endpoints
    AUTH_ENDPOINT = "https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize"
    TOKEN_ENDPOINT = "https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"
    GRAPH_ENDPOINT = "https://graph.microsoft.com/v1.0"
    
    # OAuth scopes for different services
    SCOPES = {
        'profile': [
            'openid',                           # OpenID Connect
            'profile',                          # Basic profile info
            'email',                            # Email address
            'User.Read',                        # Read user profile
        ],
        'outlook': [
            'Mail.Read',                        # Read emails
            'Mail.ReadWrite',                   # Read/write emails
            'Mail.Send',                        # Send emails
            'MailboxSettings.Read',             # Read mailbox settings
        ],
        'calendar': [
            'Calendars.Read',                   # Read calendars
            'Calendars.ReadWrite',              # Read/write calendars
        ],
        'onedrive': [
            'Files.Read',                       # Read OneDrive files
            'Files.ReadWrite',                  # Read/write OneDrive files
            'Files.ReadWrite.All',              # Full OneDrive access
        ],
        'teams': [
            'Team.ReadBasic.All',               # Read Teams info
            'Channel.ReadBasic.All',            # Read channel info
        ],
        'office': [
            'Files.ReadWrite',                  # Office document access
        ],
        'tasks': [
            'Tasks.ReadWrite',                  # Read/write tasks (To Do/Planner)
            'Group.ReadWrite.All',              # Planner access
        ],
        'sharepoint': [
            'Sites.ReadWrite.All',              # ✅ NEW: SharePoint site access
        ],
        'onenote': [
            'Notes.ReadWrite.All',              # ✅ NEW: OneNote notebook access
        ]
        # Note: Forms.Read and Forms.ReadWrite are NOT valid Microsoft Graph scopes
        # Microsoft Forms API requires different authentication approach
    }
    
    def __init__(self, 
                 client_id: Optional[str] = None,
                 client_secret: Optional[str] = None,
                 tenant_id: str = "common",
                 token_storage_path: Optional[str] = None):
        """
        Initialize Microsoft 365 OAuth Manager
        
        Args:
            client_id: Azure AD Application (client) ID
            client_secret: Azure AD Application secret
            tenant_id: Azure AD tenant ID (default: "common" for multi-tenant)
            token_storage_path: Path to store OAuth tokens
        """
        self.client_id = client_id or os.environ.get('MICROSOFT_CLIENT_ID')
        self.client_secret = client_secret or os.environ.get('MICROSOFT_CLIENT_SECRET')
        self.tenant_id = tenant_id or os.environ.get('MICROSOFT_TENANT_ID', 'common')
        
        # Check if credentials are placeholder values
        if self.client_id and 'your-' in self.client_id.lower():
            self.client_id = None
            logger.warning("⚠️ MICROSOFT_CLIENT_ID is a placeholder value")
        
        if self.client_secret and 'your-' in self.client_secret.lower():
            self.client_secret = None
            logger.warning("⚠️ MICROSOFT_CLIENT_SECRET is a placeholder value")
        
        if not self.client_id:
            logger.error("❌ MICROSOFT_CLIENT_ID not configured")
        if not self.client_secret:
            logger.error("❌ MICROSOFT_CLIENT_SECRET not configured")
        
        # Token storage
        if token_storage_path:
            self.token_storage_path = Path(token_storage_path)
        else:
            self.token_storage_path = Path(__file__).parent / 'tokens' / 'microsoft365'
        
        self.token_storage_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"✅ Microsoft 365 OAuth Manager initialized (Tenant: {self.tenant_id})")
    
    def get_authorization_url(self, 
                              redirect_uri: str,
                              scopes: Optional[List[str]] = None,
                              state: Optional[str] = None) -> str:
        """
        Generate OAuth2 authorization URL for user consent
        
        Args:
            redirect_uri: Callback URL after authorization
            scopes: List of permission scopes (default: profile + email)
            state: Optional state parameter for CSRF protection
        
        Returns:
            Authorization URL to redirect user to
        
        Example:
            url = manager.get_authorization_url(
                redirect_uri='http://localhost:5000/api/auth/microsoft/callback',
                scopes=['User.Read', 'Mail.Read'],
                state='random_state_token'
            )
        """
        # Default scopes for user login
        if scopes is None:
            scopes = self.SCOPES['profile'] + self.SCOPES['outlook']
        
        # Build authorization URL
        auth_url = self.AUTH_ENDPOINT.format(tenant=self.tenant_id)
        
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': redirect_uri,
            'response_mode': 'query',
            'scope': ' '.join(scopes),
            'state': state or '',
            'prompt': 'select_account',  # ✅ Force account picker (matches Google behavior)
        }
        
        # Construct URL with parameters
        param_string = '&'.join([f"{k}={requests.utils.quote(str(v))}" for k, v in params.items()])
        full_url = f"{auth_url}?{param_string}"
        
        logger.info(f"🔗 Generated Microsoft authorization URL")
        return full_url
    
    def exchange_code_for_tokens(self, 
                                  code: str,
                                  redirect_uri: str) -> Dict[str, any]:
        """
        Exchange authorization code for access token and refresh token
        
        Args:
            code: Authorization code from callback
            redirect_uri: Same redirect URI used in authorization
        
        Returns:
            Dictionary with tokens and user info
        
        Example:
            tokens = manager.exchange_code_for_tokens(
                code='authorization_code_from_callback',
                redirect_uri='http://localhost:5000/api/auth/microsoft/callback'
            )
        """
        token_url = self.TOKEN_ENDPOINT.format(tenant=self.tenant_id)
        
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code',
        }
        
        try:
            logger.info(f"🔄 Exchanging code for tokens...")
            logger.info(f"   Token URL: {token_url}")
            logger.info(f"   Redirect URI: {redirect_uri}")
            logger.info(f"   Client ID: {self.client_id[:20]}...")
            
            response = requests.post(token_url, data=data)
            
            # Log full error details if request fails
            if response.status_code != 200:
                logger.error(f"❌ Token exchange failed with status {response.status_code}")
                logger.error(f"   Response: {response.text}")
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error_description', error_data.get('error', str(response.text)))
                except:
                    error_msg = response.text
                
                return {
                    'success': False,
                    'error': f"{response.status_code} {response.reason}: {error_msg}"
                }
            
            response.raise_for_status()
            
            token_data = response.json()
            
            # Calculate token expiry
            expires_in = token_data.get('expires_in', 3600)
            token_data['expires_at'] = (datetime.now() + timedelta(seconds=expires_in)).isoformat()
            
            logger.info("✅ Successfully exchanged authorization code for tokens")
            return {
                'success': True,
                'access_token': token_data['access_token'],
                'refresh_token': token_data.get('refresh_token'),
                'expires_at': token_data['expires_at'],
                'scope': token_data.get('scope', ''),
                'token_type': token_data.get('token_type', 'Bearer')
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Failed to exchange code for tokens: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def refresh_access_token(self, refresh_token: str) -> Dict[str, any]:
        """
        Refresh access token using refresh token
        
        Args:
            refresh_token: Refresh token from previous authentication
        
        Returns:
            Dictionary with new access token
        """
        token_url = self.TOKEN_ENDPOINT.format(tenant=self.tenant_id)
        
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
        }
        
        try:
            response = requests.post(token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            
            expires_in = token_data.get('expires_in', 3600)
            token_data['expires_at'] = (datetime.now() + timedelta(seconds=expires_in)).isoformat()
            
            logger.info("✅ Successfully refreshed access token")
            return {
                'success': True,
                'access_token': token_data['access_token'],
                'refresh_token': token_data.get('refresh_token', refresh_token),
                'expires_at': token_data['expires_at'],
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Failed to refresh access token: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_user_profile(self, access_token: str) -> Dict[str, any]:
        """
        Get user profile information from Microsoft Graph
        
        Args:
            access_token: Valid access token
        
        Returns:
            Dictionary with user profile data
        """
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(f"{self.GRAPH_ENDPOINT}/me", headers=headers)
            response.raise_for_status()
            
            profile = response.json()
            
            logger.info(f"✅ Retrieved user profile: {profile.get('userPrincipalName')}")
            return {
                'success': True,
                'profile': {
                    'id': profile.get('id'),
                    'email': profile.get('userPrincipalName') or profile.get('mail'),
                    'name': profile.get('displayName'),
                    'first_name': profile.get('givenName'),
                    'last_name': profile.get('surname'),
                    'job_title': profile.get('jobTitle'),
                    'office_location': profile.get('officeLocation'),
                    'mobile_phone': profile.get('mobilePhone'),
                    'business_phones': profile.get('businessPhones', []),
                    'preferred_language': profile.get('preferredLanguage'),
                }
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Failed to get user profile: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def store_tokens(self, user_email: str, tokens: Dict[str, any]):
        """
        Store OAuth tokens for a user
        
        Args:
            user_email: User's email address
            tokens: Token dictionary from exchange_code_for_tokens
        """
        token_file = self.token_storage_path / f"{user_email.replace('@', '_at_')}.json"
        
        token_data = {
            'user_email': user_email,
            'access_token': tokens['access_token'],
            'refresh_token': tokens.get('refresh_token'),
            'expires_at': tokens['expires_at'],
            'scope': tokens.get('scope', ''),
            'updated_at': datetime.now().isoformat()
        }
        
        with open(token_file, 'w') as f:
            json.dump(token_data, f, indent=2)
        
        logger.info(f"✅ Stored tokens for {user_email}")
    
    def load_tokens(self, user_email: str) -> Optional[Dict[str, any]]:
        """
        Load OAuth tokens for a user
        
        Args:
            user_email: User's email address
        
        Returns:
            Token dictionary or None if not found
        """
        token_file = self.token_storage_path / f"{user_email.replace('@', '_at_')}.json"
        
        if not token_file.exists():
            return None
        
        with open(token_file, 'r') as f:
            token_data = json.load(f)
        
        # Check if token is expired
        expires_at = datetime.fromisoformat(token_data['expires_at'])
        if expires_at < datetime.now():
            logger.warning(f"⚠️ Token expired for {user_email}, needs refresh")
            return None
        
        logger.info(f"✅ Loaded tokens for {user_email}")
        return token_data
    
    def get_all_scopes(self) -> List[str]:
        """
        Get all available scopes for full Microsoft 365 access
        
        Returns:
            List of all permission scopes
        """
        all_scopes = []
        for scope_list in self.SCOPES.values():
            all_scopes.extend(scope_list)
        return list(set(all_scopes))  # Remove duplicates


# Global instance
microsoft_oauth_manager = Microsoft365OAuthManager()


def get_microsoft_auth_url(redirect_uri: str, state: Optional[str] = None) -> str:
    """
    Convenience function to get Microsoft authorization URL
    
    Args:
        redirect_uri: OAuth callback URL
        state: Optional state for CSRF protection
    
    Returns:
        Authorization URL
    """
    # ✅ FIX: Request only ESSENTIAL scopes for initial login
    # Requesting all scopes at once causes 400 errors if admin consent not granted
    # Users can grant additional permissions later via /api/auth/microsoft/grant-scopes
    essential_scopes = [
        'openid',
        'profile', 
        'email',
        'User.Read',           # Read user profile (basic)
        'User.ReadWrite',      # ✅ Read and write user profile
        'offline_access'       # ✅ CRITICAL: Enables refresh tokens
    ]
    
    return microsoft_oauth_manager.get_authorization_url(
        redirect_uri=redirect_uri,
        scopes=essential_scopes,
        state=state
    )


def authenticate_user_with_microsoft(code: str, redirect_uri: str) -> Dict[str, any]:
    """
    Authenticate user with Microsoft and get profile
    
    Args:
        code: Authorization code from OAuth callback
        redirect_uri: OAuth callback URL
    
    Returns:
        Dictionary with user profile and tokens
    """
    # Exchange code for tokens
    token_result = microsoft_oauth_manager.exchange_code_for_tokens(code, redirect_uri)
    
    if not token_result['success']:
        return token_result
    
    # Get user profile
    profile_result = microsoft_oauth_manager.get_user_profile(token_result['access_token'])
    
    if not profile_result['success']:
        return profile_result
    
    # Store tokens
    user_email = profile_result['profile']['email']
    microsoft_oauth_manager.store_tokens(user_email, token_result)
    
    return {
        'success': True,
        'profile': profile_result['profile'],
        'tokens': {
            'access_token': token_result['access_token'],
            'refresh_token': token_result['refresh_token'],
            'expires_at': token_result['expires_at']
        }
    }


if __name__ == '__main__':
    print("=" * 60)
    print("🔷 MICROSOFT 365 OAUTH MANAGER")
    print("=" * 60)
    print()
    print("This module provides Microsoft 365 OAuth authentication.")
    print()
    print("Setup Instructions:")
    print("1. Create Azure AD application at https://portal.azure.com")
    print("2. Set MICROSOFT_CLIENT_ID environment variable")
    print("3. Set MICROSOFT_CLIENT_SECRET environment variable")
    print("4. Add redirect URI: http://localhost:5001/api/auth/microsoft/callback")
    print()
    print("Usage:")
    print("   from Microsoft_365_Connection.microsoft365_oauth_manager import get_microsoft_auth_url")
    print("   url = get_microsoft_auth_url('http://localhost:5001/api/auth/microsoft/callback')")
    print("   # Redirect user to this URL")
    print()
