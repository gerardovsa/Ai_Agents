"""
Platform Credential Requirements Analysis
Generates a comprehensive list of all platforms and their authentication needs
"""

import json
import os
from pathlib import Path

def analyze_platform_credentials():
    """Analyze all tool schemas to determine credential requirements"""
    
    schemas_dir = Path("tools/schemas")
    
    # Platform authentication mappings
    platforms = {
        # OAuth 2.0 Platforms (User grants permission)
        'oauth_platforms': {
            'google_workspace': {
                'services': ['gmail', 'google_docs', 'google_sheets', 'google_slides', 'google_drive', 
                           'google_calendar', 'google_tasks', 'google_forms', 'google_meet'],
                'auth_type': 'OAuth 2.0',
                'scopes_needed': ['gmail', 'drive', 'calendar', 'tasks', 'forms'],
                'oauth_flow': 'google_oauth',
                'stored_in': 'oauth_tokens table',
                'user_action': 'Click "Connect Google Workspace" → Login with Google → Grant permissions'
            },
            'microsoft_365': {
                'services': ['microsoft_outlook', 'microsoft_word', 'microsoft_excel', 'microsoft_powerpoint',
                           'microsoft_onedrive', 'microsoft_calendar', 'microsoft_teams', 'microsoft_todo',
                           'microsoft_onenote', 'microsoft_sharepoint'],
                'auth_type': 'OAuth 2.0',
                'scopes_needed': ['Mail.ReadWrite', 'Files.ReadWrite.All', 'Calendars.ReadWrite', 'Tasks.ReadWrite'],
                'oauth_flow': 'microsoft_oauth',
                'stored_in': 'oauth_tokens table',
                'user_action': 'Click "Connect Microsoft 365" → Login with Microsoft → Grant permissions'
            },
            'github': {
                'services': ['github'],
                'auth_type': 'OAuth 2.0 or Personal Access Token',
                'scopes_needed': ['repo', 'user', 'workflow'],
                'oauth_flow': 'github_oauth',
                'stored_in': 'oauth_tokens or user_platform_credentials',
                'user_action': 'Click "Connect GitHub" → Login → Grant permissions OR Enter Personal Access Token'
            },
            'slack': {
                'services': ['slack'],
                'auth_type': 'OAuth 2.0',
                'scopes_needed': ['chat:write', 'channels:read', 'users:read'],
                'oauth_flow': 'slack_oauth',
                'stored_in': 'oauth_tokens table',
                'user_action': 'Click "Connect Slack" → Select workspace → Grant permissions'
            },
            'instagram': {
                'services': ['instagram'],
                'auth_type': 'OAuth 2.0 (Meta)',
                'scopes_needed': ['instagram_basic', 'instagram_content_publish'],
                'oauth_flow': 'meta_oauth',
                'stored_in': 'oauth_tokens table',
                'user_action': 'Click "Connect Instagram" → Login with Facebook → Grant permissions'
            }
        },
        
        # API Key Platforms (User provides key)
        'api_key_platforms': {
            'stripe': {
                'services': ['stripe'],
                'auth_type': 'API Key (Secret Key)',
                'keys_needed': ['secret_key', 'publishable_key'],
                'stored_in': 'user_platform_credentials table',
                'user_action': 'Enter Stripe Secret Key from dashboard.stripe.com/apikeys'
            },
            'twilio': {
                'services': ['twilio', 'twilio_veterinary'],
                'auth_type': 'API Key (Account SID + Auth Token)',
                'keys_needed': ['account_sid', 'auth_token', 'phone_number'],
                'stored_in': 'user_platform_credentials table',
                'user_action': 'Enter Account SID, Auth Token, and Phone Number from twilio.com/console'
            },
            'assemblyai': {
                'services': ['assemblyai'],
                'auth_type': 'API Key',
                'keys_needed': ['api_key'],
                'stored_in': 'user_platform_credentials table',
                'user_action': 'Enter AssemblyAI API Key from assemblyai.com'
            },
            'cloudflare': {
                'services': ['cloudflare'],
                'auth_type': 'API Token',
                'keys_needed': ['api_token', 'account_id'],
                'stored_in': 'user_platform_credentials table',
                'user_action': 'Enter Cloudflare API Token and Account ID from dash.cloudflare.com'
            },
            'cloudconvert': {
                'services': ['cloudconvert'],
                'auth_type': 'API Key',
                'keys_needed': ['api_key'],
                'stored_in': 'user_platform_credentials table',
                'user_action': 'Enter CloudConvert API Key from cloudconvert.com/dashboard/api'
            },
            'google_analytics': {
                'services': ['google_analytics'],
                'auth_type': 'Service Account JSON or OAuth',
                'keys_needed': ['service_account_json'],
                'stored_in': 'user_platform_credentials table',
                'user_action': 'Upload Google Analytics Service Account JSON file'
            },
            'google_cloud_run': {
                'services': ['google_cloud_run'],
                'auth_type': 'Service Account JSON',
                'keys_needed': ['service_account_json', 'project_id'],
                'stored_in': 'user_platform_credentials table',
                'user_action': 'Upload Google Cloud Service Account JSON with Cloud Run permissions'
            },
            'ngrok': {
                'services': ['ngrok'],
                'auth_type': 'Auth Token',
                'keys_needed': ['auth_token'],
                'stored_in': 'user_platform_credentials table',
                'user_action': 'Enter ngrok Auth Token from dashboard.ngrok.com/get-started/your-authtoken'
            },
            'paypal': {
                'services': ['paypal'],
                'auth_type': 'API Credentials (Client ID + Secret)',
                'keys_needed': ['client_id', 'client_secret', 'mode'],
                'stored_in': 'user_platform_credentials table',
                'user_action': 'Enter PayPal Client ID and Secret from developer.paypal.com'
            },
            'pinecone': {
                'services': ['pinecone'],
                'auth_type': 'API Key',
                'keys_needed': ['api_key', 'environment'],
                'stored_in': 'user_platform_credentials table',
                'user_action': 'Enter Pinecone API Key and Environment from app.pinecone.io'
            },
            'render': {
                'services': ['render'],
                'auth_type': 'API Key',
                'keys_needed': ['api_key'],
                'stored_in': 'user_platform_credentials table',
                'user_action': 'Enter Render API Key from dashboard.render.com/account/settings'
            },
            'resend': {
                'services': ['resend'],
                'auth_type': 'API Key',
                'keys_needed': ['api_key'],
                'stored_in': 'user_platform_credentials table',
                'user_action': 'Enter Resend API Key from resend.com/api-keys'
            },
            'woocommerce': {
                'services': ['woocommerce'],
                'auth_type': 'API Credentials (Consumer Key + Secret)',
                'keys_needed': ['consumer_key', 'consumer_secret', 'store_url'],
                'stored_in': 'user_platform_credentials table',
                'user_action': 'Enter WooCommerce Consumer Key and Secret from WordPress admin → WooCommerce → Settings → Advanced → REST API'
            },
            'xero': {
                'services': ['xero'],
                'auth_type': 'OAuth 2.0',
                'keys_needed': ['client_id', 'client_secret'],
                'stored_in': 'oauth_tokens table',
                'user_action': 'Click "Connect Xero" → Login → Grant permissions'
            }
        },
        
        # Database Platforms (User provides connection string)
        'database_platforms': {
            'sql_database': {
                'services': ['sql_database'],
                'auth_type': 'Connection String or Credentials',
                'keys_needed': ['connection_string', 'host', 'port', 'username', 'password', 'database'],
                'stored_in': 'user_platform_credentials table',
                'user_action': 'Enter database connection details (host, port, username, password, database name)'
            },
            'supabase': {
                'services': ['supabase'],
                'auth_type': 'Project URL + API Key',
                'keys_needed': ['project_url', 'anon_key', 'service_role_key'],
                'stored_in': 'user_platform_credentials table',
                'user_action': 'Enter Supabase Project URL and API keys from supabase.com/dashboard/project/_/settings/api'
            }
        },
        
        # No Authentication Required (Built-in services)
        'no_auth_platforms': {
            'synergy': 'Internal dashboard - no external auth needed',
            'automation': 'Internal automation system - no external auth needed',
            'memory': 'Internal memory system - no external auth needed',
            'scheduler': 'Internal scheduler - no external auth needed',
            'user_feedback': 'Internal feedback system - no external auth needed',
            'calculator': 'Internal calculator - no external auth needed',
            'data_analysis': 'Internal data processing - no external auth needed'
        }
    }
    
    return platforms


def print_credential_summary():
    """Print a formatted summary of all platform credential requirements"""
    
    platforms = analyze_platform_credentials()
    
    print("\n" + "="*100)
    print("PLATFORM CREDENTIAL REQUIREMENTS - COMPREHENSIVE GUIDE")
    print("="*100)
    
    # OAuth Platforms
    print("\n📱 OAUTH 2.0 PLATFORMS (User grants permission via browser)")
    print("-" * 100)
    for platform_id, info in platforms['oauth_platforms'].items():
        print(f"\n🔐 {platform_id.upper().replace('_', ' ')}")
        print(f"   Services: {', '.join(info['services'])}")
        print(f"   Auth Type: {info['auth_type']}")
        print(f"   Storage: {info['stored_in']}")
        print(f"   User Action: {info['user_action']}")
    
    # API Key Platforms
    print("\n\n🔑 API KEY PLATFORMS (User provides keys from external service)")
    print("-" * 100)
    for platform_id, info in platforms['api_key_platforms'].items():
        print(f"\n🔑 {platform_id.upper().replace('_', ' ')}")
        print(f"   Services: {', '.join(info['services'])}")
        print(f"   Auth Type: {info['auth_type']}")
        print(f"   Keys Needed: {', '.join(info['keys_needed'])}")
        print(f"   Storage: {info['stored_in']}")
        print(f"   User Action: {info['user_action']}")
    
    # Database Platforms
    print("\n\n🗄️  DATABASE PLATFORMS (User provides connection details)")
    print("-" * 100)
    for platform_id, info in platforms['database_platforms'].items():
        print(f"\n🗄️  {platform_id.upper().replace('_', ' ')}")
        print(f"   Services: {', '.join(info['services'])}")
        print(f"   Auth Type: {info['auth_type']}")
        print(f"   Keys Needed: {', '.join(info['keys_needed'])}")
        print(f"   Storage: {info['stored_in']}")
        print(f"   User Action: {info['user_action']}")
    
    # No Auth Platforms
    print("\n\n✅ NO AUTHENTICATION REQUIRED (Built-in services)")
    print("-" * 100)
    for platform_id, description in platforms['no_auth_platforms'].items():
        print(f"   • {platform_id}: {description}")
    
    # Summary Statistics
    print("\n\n" + "="*100)
    print("SUMMARY STATISTICS")
    print("="*100)
    total_oauth = len(platforms['oauth_platforms'])
    total_api_key = len(platforms['api_key_platforms'])
    total_database = len(platforms['database_platforms'])
    total_no_auth = len(platforms['no_auth_platforms'])
    total = total_oauth + total_api_key + total_database + total_no_auth
    
    print(f"\nTotal Platforms: {total}")
    print(f"   • OAuth 2.0: {total_oauth} platforms")
    print(f"   • API Key: {total_api_key} platforms")
    print(f"   • Database: {total_database} platforms")
    print(f"   • No Auth: {total_no_auth} platforms")
    
    print("\n" + "="*100)
    print("UI REQUIREMENTS FOR CONNECTION MANAGEMENT")
    print("="*100)
    print("\n1. OAuth Platforms: Need 'Connect' button → Opens OAuth flow in browser")
    print("2. API Key Platforms: Need form with input fields for each required key")
    print("3. Database Platforms: Need form with connection details (host, port, etc.)")
    print("4. All platforms: Show connection status (connected/disconnected)")
    print("5. All platforms: Allow disconnection/removal of credentials")
    print("6. All platforms: Show which services are available with current credentials")
    
    print("\n" + "="*100)


if __name__ == '__main__':
    print_credential_summary()
