"""Test communication hub emails endpoint simulation"""
import sys
import os
sys.path.insert(0, 'c:\\Users\\gpoli\\GIT\\AI_Agents_V11\\AI_agents\\AI_infrastructure')
try:
    from dotenv import load_dotenv
    load_dotenv('c:\\Users\\gpoli\\GIT\\AI_Agents_V11\\AI_agents\\.env')
except: pass

from shared.database_utils import execute_query
from datetime import datetime, timezone

# 1. Check if the token is expired and needs refresh
token = execute_query(
    "SELECT expires_at, is_valid, is_active, refresh_token IS NOT NULL as has_refresh, last_refresh_error FROM ai_infrastructure.oauth_tokens WHERE user_id=12 AND platform='google' AND is_active=TRUE",
    fetch_mode='one'
)
print('Token status:', token)
if token:
    now = datetime.now(timezone.utc)
    expires = token['expires_at']
    if expires and expires.tzinfo is None:
        from datetime import timezone as tz
        expires = expires.replace(tzinfo=timezone.utc)
    expired = expires < now if expires else True
    print(f'Token expired: {expired} (expires {expires}, now {now})')

# 2. Test what happens when auth_manager fetches credentials
os.chdir('c:\\Users\\gpoli\\GIT\\AI_Agents_V11\\AI_agents\\AI_infrastructure')
from auth.user_auth import UserAuthManager
manager = UserAuthManager()
creds = manager.get_user_google_oauth_credentials(12)
print('Credentials returned:', 'YES' if creds else 'NONE')
if creds:
    print('Has refresh_token:', bool(creds.get('refresh_token')))
    print('Has access_token:', bool(creds.get('access_token')))
