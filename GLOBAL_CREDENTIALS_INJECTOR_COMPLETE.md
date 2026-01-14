# 🎯 Global Credentials Injector - Quick Reference

**Date:** November 28, 2025  
**Status:** ✅ TESTED - Google/Microsoft NOT broken  
**File:** `AI_infrastructure/auth/credential_injector.py`

---

## ✅ What Was Added

A **universal credential getter system** for API key platforms that works alongside (NOT replacing) the existing Google and Microsoft OAuth systems.

### New Functions (8 platform-specific + 1 generic):

```python
from AI_infrastructure.auth.credential_injector import (
    # Generic getter (works for any platform)
    get_platform_credentials,
    
    # Platform-specific getters
    get_slack_credentials,
    get_stripe_credentials,
    get_twilio_credentials,
    get_shopify_credentials,
    get_openai_credentials,
    get_anthropic_credentials,
    get_pinecone_credentials,
    get_xero_credentials
)
```

---

## 🔒 What Was NOT Touched (Protected)

**Google Workspace functions** - ALL preserved:
- `get_user_gmail_service`
- `get_user_calendar_service`
- `get_user_tasks_service`
- `get_user_forms_service`
- `get_user_drive_service`
- `get_user_docs_service`
- `get_user_sheets_service`
- `get_user_slides_service`
- `get_user_meet_service`
- `create_google_service_with_user_credentials`

**Microsoft 365 functions** - ALL preserved:
- `get_microsoft_access_token`
- `get_microsoft_headers`
- `create_microsoft_service_with_user_credentials`

---

## 📖 How to Use in Tool Implementations

### Generic Method (Works for Any Platform)

```python
from AI_infrastructure.auth.credential_injector import get_platform_credentials

def my_platform_tool(param1, **kwargs):
    """Execute platform action"""
    user_id = kwargs.get('_user_id')
    
    # Get credentials from database
    creds = get_platform_credentials(user_id, 'platform_name')
    
    # Use credentials
    api_key = creds['api_key']
    # ... initialize client and execute
```

### Platform-Specific Method (Type-Safe)

#### GitHub Example
```python
from AI_infrastructure.auth.credential_injector import get_github_credentials
from github import Github

def github_create_repo(name: str, description: str = None, private: bool = False, **kwargs):
    """Create GitHub repository under user's account"""
    # Get GitHub credentials
    github_creds = get_github_credentials(**kwargs)
    
    # Initialize GitHub client with user's token
    g = Github(github_creds['access_token'])
    user = g.get_user()
    
    # Create repository
    repo = user.create_repo(
        name=name,
        description=description or "",
        private=private
    )
    
    return {
        'name': repo.name,
        'full_name': repo.full_name,
        'clone_url': repo.clone_url,
        'html_url': repo.html_url,
        'owner': user.login,  # Shows user's GitHub username
        'created': True
    }
```

#### Slack Example
```python
from AI_infrastructure.auth.credential_injector import get_slack_credentials
from slack_sdk import WebClient

def slack_post_message(channel: str, text: str, **kwargs):
    """Post message to Slack channel"""
    # Get Slack credentials
    slack_creds = get_slack_credentials(**kwargs)
    
    # Initialize Slack client
    client = WebClient(token=slack_creds['bot_token'])
    
    # Execute API call
    response = client.chat_postMessage(
        channel=channel,
        text=text
    )
    
    return {
        'success': True,
        'message_ts': response['ts'],
        'channel': response['channel']
    }
```

#### Stripe Example
```python
from AI_infrastructure.auth.credential_injector import get_stripe_credentials
import stripe

def stripe_create_charge(amount: int, currency: str, **kwargs):
    """Create Stripe charge"""
    # Get Stripe credentials
    stripe_creds = get_stripe_credentials(**kwargs)
    
    # Set API key
    stripe.api_key = stripe_creds['api_key']
    
    # Execute API call
    charge = stripe.Charge.create(
        amount=amount,
        currency=currency
    )
    
    return charge
```

#### Twilio Example
```python
from AI_infrastructure.auth.credential_injector import get_twilio_credentials
from twilio.rest import Client

def twilio_send_sms(to: str, body: str, **kwargs):
    """Send SMS via Twilio"""
    # Get Twilio credentials
    twilio_creds = get_twilio_credentials(**kwargs)
    
    # Initialize Twilio client
    client = Client(
        twilio_creds['account_sid'],
        twilio_creds['auth_token']
    )
    
    # Send message
    message = client.messages.create(
        to=to,
        from_=twilio_creds['phone_number'],
        body=body
    )
    
    return {
        'success': True,
        'message_sid': message.sid,
        'status': message.status
    }
```

#### Pinecone Example (Already Implemented)
```python
from AI_infrastructure.auth.credential_injector import get_pinecone_credentials
from pinecone import Pinecone

def pinecone_query_vectors(query_text: str, top_k: int = 4, **kwargs):
    """Query Pinecone vector database"""
    user_id = kwargs.get('_user_id')
    
    # Get Pinecone credentials
    pinecone_creds = get_pinecone_credentials(user_id=user_id)
    
    # Initialize Pinecone client
    pc = Pinecone(api_key=pinecone_creds['api_key'])
    index = pc.Index(pinecone_creds['index_name'])
    
    # Execute query
    results = index.query(
        vector=query_vector,
        top_k=top_k,
        include_metadata=True
    )
    
    return results
```

---

## 🗄️ Credential Storage Format (JSONB)

Each platform stores credentials in `ai_infrastructure.user_platform_credentials` table, `credentials` JSONB column:

### Slack
```json
{
  "bot_token": "xoxb-1234567890-...",
  "app_id": "A1234567890",
  "workspace_id": "T1234567890",
  "workspace_name": "My Company"
}
```

### Stripe
```json
{
  "api_key": "sk_test_XXXXXXXXXXXXXXXXXXXX",
  "environment": "test",
  "webhook_secret": "whsec_XXXXXXXXXXXXXXXXXXXX"
}
```

### Twilio
```json
{
  "account_sid": "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "auth_token": "your_auth_token_here",
  "phone_number": "+1234567890"
}
```

### Shopify
```json
{
  "api_key": "shpat_...",
  "store_url": "yourstore.myshopify.com",
  "api_version": "2024-01"
}
```

### OpenAI
```json
{
  "api_key": "sk-proj-...",
  "model": "gpt-4",
  "organization_id": "org-..."
}
```

### Anthropic
```json
{
  "api_key": "sk-ant-...",
  "model": "claude-3-opus-20240229"
}
```

### Pinecone
```json
{
  "api_key": "pcsk_...",
  "index_name": "inhouseprint",
  "environment": "us-east-1",
  "namespace": ""
}
```

### GitHub
```json
{
  "access_token": "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "username": "github_username",
  "email": "user@example.com"
}
```

---

## 🔄 Migration Pattern for Existing Tools

### Before (Old - Reads from Environment)
```python
import os
from slack_sdk import WebClient

class SlackTools:
    def __init__(self):
        self.client = WebClient(token=os.getenv('SLACK_BOT_TOKEN'))
    
    def post_message(self, channel, text, **kwargs):
        return self.client.chat_postMessage(channel=channel, text=text)

def slack_post_message(**kwargs):
    tools = SlackTools()
    return tools.post_message(**kwargs)
```

### After (New - Uses Credential Injection)
```python
from AI_infrastructure.auth.credential_injector import get_slack_credentials
from slack_sdk import WebClient

def slack_post_message(channel: str, text: str, **kwargs):
    """Post message to Slack channel"""
    # Get credentials from database
    slack_creds = get_slack_credentials(**kwargs)
    
    # Initialize client with user's bot token
    client = WebClient(token=slack_creds['bot_token'])
    
    # Execute API call
    response = client.chat_postMessage(
        channel=channel,
        text=text
    )
    
    return {
        'success': True,
        'message_ts': response['ts'],
        'channel': response['channel']
    }
```

---

## ⚠️ Error Handling

All credential getters raise descriptive exceptions if credentials are missing:

```python
try:
    slack_creds = get_slack_credentials(**kwargs)
except Exception as e:
    # Error message: "Slack credentials not found for user 14. 
    #                 Please add credentials in Account Settings -> Connections."
    return {
        'success': False,
        'error': str(e),
        'action_required': 'Add Slack credentials via Account Settings'
    }
```

---

## 🧪 Testing

Run the test suite to verify everything works:

```powershell
cd C:\Users\gpoli\GIT\AI_agents
python test_global_credentials.py
```

**Expected Output:**
```
✅ All imports successful
✅ 8 new platform credential getters available
✅ Google Workspace functions NOT broken
✅ Microsoft 365 functions NOT broken
```

---

## 📊 Supported Platforms

| Platform | Function | JSONB Keys |
|----------|----------|------------|
| **Slack** | `get_slack_credentials()` | bot_token, app_id, workspace_id |
| **Stripe** | `get_stripe_credentials()` | api_key, environment, webhook_secret |
| **Twilio** | `get_twilio_credentials()` | account_sid, auth_token, phone_number |
| **Shopify** | `get_shopify_credentials()` | api_key, store_url, api_version |
| **OpenAI** | `get_openai_credentials()` | api_key, model, organization_id |
| **Anthropic** | `get_anthropic_credentials()` | api_key, model |
| **Pinecone** | `get_pinecone_credentials()` | api_key, index_name, environment |
| **Xero** | `get_xero_credentials()` | client_id, client_secret, tenant_id |
| **GitHub** | `get_github_credentials()` | access_token, username, email |

**Generic:** `get_platform_credentials(user_id, 'platform_name')` works for any platform!

---

## 🔐 Security Notes

- Credentials stored in PostgreSQL (Supabase) with encryption
- Never logged or exposed in API responses
- User isolation enforced (each user_id has separate credentials)
- OAuth tokens (Google, Microsoft, Xero) remain in `oauth_tokens` table
- API keys (Slack, Stripe, etc.) in `user_platform_credentials` JSONB column

---

## ✅ Verification Checklist

- [x] Google Workspace functions still work (9 functions)
- [x] Microsoft 365 functions still work (2 functions)
- [x] 9 new platform getters added (including GitHub)
- [x] Generic `get_platform_credentials()` works
- [x] All functions handle `_user_id` from kwargs
- [x] Proper error messages if credentials missing
- [x] Test suite passes (100%)
- [x] No breaking changes to existing code
- [x] GitHub migrated to user-specific credentials (4 tools updated)

---

## 🚀 Next Steps

1. **Update Tool Implementations:**
   - Slack: `tools/implementations/slack.py`
   - Stripe: `tools/implementations/stripe.py`
   - Twilio: `tools/implementations/twilio.py`
   - etc.

2. **Add Credentials via UI:**
   - User goes to Account Settings → Connections
   - Clicks "Add Connection"
   - Selects platform and enters API keys
   - Credentials stored in JSONB format

3. **Test Tool Execution:**
   - Execute tool with `user_id` parameter
   - System auto-injects credentials
   - Tool calls API successfully

---

**Last Updated:** November 28, 2025  
**Tested:** ✅ All tests passing (GitHub + 8 platforms)  
**Breaking Changes:** None - Google/Microsoft preserved  
**GitHub Status:** ✅ Migrated to personal tokens (4 tools updated)
