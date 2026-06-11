# Tool Development Best Practices - Official Guidelines
**Based on Anthropic, Microsoft Graph, and Google Workspace Documentation**

**Last Updated:** November 3, 2025  
**Version:** 1.0.0  
**Status:** Official Reference Document

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Anthropic Tool Use Standards](#anthropic-tool-use-standards)
3. [Microsoft Graph API Best Practices](#microsoft-graph-api-best-practices)
4. [Google Workspace API Best Practices](#google-workspace-api-best-practices)
5. [Recommended Tool Structure for AI_agents Platform](#recommended-tool-structure)
6. [Naming Conventions](#naming-conventions)
7. [Implementation Patterns Comparison](#implementation-patterns-comparison)
8. [Authentication & Credential Handling](#authentication-credential-handling)
9. [Error Handling Standards](#error-handling-standards)
10. [Performance Optimization](#performance-optimization)
11. [Tool Templates](#tool-templates)
12. [Migration Guide](#migration-guide)

---

## Executive Summary

### Key Findings from Official Documentation

**Anthropic Claude Tool Use:**
- Tools require `input_schema` with `type: "object"`, `properties`, and `required` array
- Tool descriptions critical for Claude's decision-making (LLM reads descriptions)
- Clear naming: `get_weather` not `weather` or `weatherAPI`
- Stateless design preferred for parallel execution
- Return structured data (not raw HTML/XML)

**Microsoft Graph API:**
- RESTful naming: resource-oriented (`/users/{id}/messages`)
- Use projections (`$select`) to limit data transfer
- Implement pagination for large datasets
- OAuth 2.0 delegated permissions for user context
- Application permissions for daemon/background services
- Least privilege principle (only request needed permissions)

**Google Workspace API:**
- Service accounts for app-owned data
- OAuth 2.0 for user-delegated access
- Domain-wide delegation for admin operations
- JSON credentials file for service accounts
- Scopes define API access boundaries

### Current State Analysis (AI_agents Platform)

**4 Distinct Patterns Discovered:**

| Pattern | Platforms | Efficiency | Pros | Cons |
|---------|-----------|------------|------|------|
| **A: Class + Instance Exports** | Microsoft (10 tools) | ⭐⭐⭐⭐⭐ | One instance, efficient, organized | Requires module exports |
| **B: Direct Functions** | Google (12 tools) | ⭐⭐⭐⭐⭐ | Simple, no overhead | Can get messy with many tools |
| **C: Class + Per-Call Instantiation** | Stripe, Slack | ⭐⭐ | Organized | Creates new instance per call (inefficient) |
| **D: Helper + Direct Functions** | GitHub, Supabase | ⭐⭐⭐⭐ | Clean, lazy init | Extra function call overhead |

---

## Anthropic Tool Use Standards

### Official Schema Format (Required)

```json
{
  "name": "tool_name",
  "description": "Clear, concise description of what the tool does",
  "input_schema": {
    "type": "object",
    "properties": {
      "param1": {
        "type": "string",
        "description": "What this parameter does"
      },
      "param2": {
        "type": "integer",
        "description": "Optional parameter",
        "default": 100
      }
    },
    "required": ["param1"]
  }
}
```

### Anthropic Best Practices

**1. Tool Descriptions (Critical)**
- Claude reads descriptions to decide which tool to use
- Be specific: "Get current weather for a city" > "Weather function"
- Include examples of use cases in description
- Mention return value format

**2. Parameter Definitions**
- Use descriptive parameter names: `city_name` not `c`
- Include all parameter types (string, integer, boolean, array, object)
- Specify required vs optional parameters
- Provide defaults for optional parameters
- Add validation constraints in description (e.g., "valid email address")

**3. Tool Naming**
- Use `verb_noun` pattern: `get_weather`, `create_document`, `send_email`
- Avoid abbreviations: `get_user_profile` not `get_usr_prof`
- Prefix with platform for clarity: `gmail_send_email`, `slack_post_message`

**4. Return Value Structure**
- Return JSON objects (not strings)
- Include status indicators: `{"success": true, "data": {...}}`
- Provide error details: `{"success": false, "error": "reason"}`
- Use consistent structure across similar tools

**5. Tool Use Workflow**
```
User Request → Claude Analyzes Tools → Tool Use Request → 
Execute Tool → Return Results → Claude Formulates Response
```

**6. Performance Considerations**
- Tool definitions add ~346-530 tokens per model (system prompt)
- Each tool in `tools` array adds tokens (name + description + schema)
- Use progressive loading for large tool sets (8 meta-tools → 606 tools)
- Batch related operations when possible

---

## Microsoft Graph API Best Practices

### Official Guidelines from Microsoft Learn

**1. Authentication & Authorization**
- Use Microsoft Authentication Library (MSAL) for OAuth 2.0
- Apply least privilege (only request needed permissions)
- Use delegated permissions for user context
- Use application permissions for daemon/background services
- Never use application permissions in interactive scenarios (security risk)

**2. API Design Patterns**
- RESTful resource-oriented design: `/users/{id}/calendar/events`
- Use HTTP methods properly: GET (read), POST (create), PATCH (update), DELETE (remove)
- Follow OData conventions for queries (`$select`, `$filter`, `$orderby`)

**3. Data Handling**
- **Use Projections (`$select`)**: Only request needed properties
  ```
  GET /me/messages?$select=from,subject
  ```
- **Implement Pagination**: Always handle `@odata.nextLink`
  ```json
  {
    "value": [...],
    "@odata.nextLink": "https://graph.microsoft.com/v1.0/me/messages?$skip=23"
  }
  ```
- **Handle Expected Errors**:
  - 403 Forbidden → Access denied (user lacks permissions)
  - 404 Not Found → Resource doesn't exist
  - 429 Throttling → Back off using Retry-After header
  - 503 Service Unavailable → Retry with exponential backoff

**4. Performance Optimization**
- **Delta Query**: Track changes instead of polling
  ```
  GET /me/messages/delta
  ```
- **Webhooks**: Get push notifications for changes
- **Batching**: Combine multiple requests into one
  ```json
  {
    "requests": [
      {"id": "1", "method": "GET", "url": "/me"},
      {"id": "2", "method": "GET", "url": "/me/messages"}
    ]
  }
  ```

**5. Reliability**
- Use TLS 1.2 or 1.3
- Generate unique `client-request-id` for each request (debugging)
- Log full request/response for troubleshooting
- Honor DNS TTL for failover support

**6. Data Storage**
- Only cache data if necessary (covered by privacy policy)
- Implement retention and deletion policies
- Respect Microsoft APIs Terms of Use

---

## Google Workspace API Best Practices

### Official Guidelines from Google Developers

**1. Authentication Methods**

**API Keys** (Public Data Only)
- Used for publicly accessible data
- No user context
- Example: Public Google Drive files shared with "Anyone with link"

**OAuth 2.0 Client ID** (User Data)
- Requires user consent
- Access user's data (email, calendar, drive)
- Supports multiple platforms (web, Android, iOS, desktop)

**Service Accounts** (App-Owned Data)
- Used for app-to-app authentication
- No user consent required
- Can impersonate users via domain-wide delegation
- JSON key file for credentials

**2. Service Account Pattern (Recommended)**
```python
from google.oauth2 import service_account

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
SERVICE_ACCOUNT_FILE = 'credentials.json'

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

# Optional: Impersonate user
delegated_credentials = credentials.with_subject('user@example.com')
```

**3. Domain-Wide Delegation**
- Allows service account to act as any user in domain
- Requires Google Workspace admin approval
- Specify OAuth scopes in Admin Console
- Use for admin operations (user provisioning, audit logs)

**4. OAuth 2.0 Flow**
```
1. Redirect user to Google OAuth consent screen
2. User grants permissions
3. Google returns authorization code
4. Exchange code for access token + refresh token
5. Use access token for API calls
6. Refresh token when expired
```

**5. Credential Security**
- Store JSON key files securely (never commit to git)
- Use environment variables or secret managers
- Rotate service account keys regularly
- Restrict API key usage (IP, API, referrer)

**6. Error Handling**
- 400 Bad Request → Invalid parameters
- 401 Unauthorized → Invalid or expired credentials
- 403 Forbidden → Insufficient permissions
- 429 Too Many Requests → Rate limiting (exponential backoff)
- 503 Service Unavailable → Temporary issue (retry)

---

## Recommended Tool Structure for AI_agents Platform

### Pattern Analysis Summary

After analyzing 34 platforms (606 tools) and official documentation, here's the recommended approach:

### 🏆 **RECOMMENDED: Hybrid Pattern (Best of All Worlds)**

Combines efficiency of Pattern A/B with organization of class-based design.

#### Structure:
```python
"""
Platform Name Tools - Integration with Platform API

Functions:
- platform_action_object: Brief description
- platform_action_object2: Brief description
"""

import requests
from typing import Dict, Any, List, Optional


class PlatformError(Exception):
    """Custom exception for Platform errors"""
    pass


class PlatformToolsManager:
    """
    Manages Platform API interactions.
    Single instance shared across all tool calls (efficient).
    """
    
    def __init__(self):
        """Initialize manager (no credentials stored here)"""
        self.base_url = "https://api.platform.com/v1"
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        access_token: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Internal helper for API calls.
        
        Args:
            method: HTTP method (GET, POST, PATCH, DELETE)
            endpoint: API endpoint (e.g., '/users')
            access_token: OAuth access token
            **kwargs: Additional requests parameters
        
        Returns:
            JSON response as dict
        
        Raises:
            PlatformError: If request fails
        """
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.request(method, url, headers=headers, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                raise PlatformError("Invalid or expired access token")
            elif response.status_code == 403:
                raise PlatformError("Insufficient permissions")
            elif response.status_code == 429:
                raise PlatformError("Rate limit exceeded, retry after delay")
            else:
                raise PlatformError(f"API request failed: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise PlatformError(f"Network error: {str(e)}")
    
    def create_item(
        self,
        title: str,
        content: Optional[str] = None,
        access_token: str = None
    ) -> Dict[str, Any]:
        """
        Create a new item.
        
        Args:
            title: Item title (required)
            content: Item content (optional)
            access_token: OAuth token (injected by credential_injector)
        
        Returns:
            {
                "success": true,
                "item_id": "123",
                "title": "Item Title",
                "url": "https://...",
                "created_at": "2025-11-03T12:00:00Z"
            }
        
        Raises:
            PlatformError: If creation fails
        """
        if not access_token:
            raise PlatformError("access_token required")
        
        payload = {
            "title": title,
            "content": content or ""
        }
        
        data = self._make_request(
            "POST",
            "/items",
            access_token,
            json=payload
        )
        
        return {
            "success": True,
            "item_id": data.get("id"),
            "title": data.get("title"),
            "url": data.get("url"),
            "created_at": data.get("created_at")
        }
    
    def list_items(
        self,
        limit: int = 10,
        access_token: str = None
    ) -> List[Dict[str, Any]]:
        """
        List items with pagination.
        
        Args:
            limit: Max items to return (default: 10, max: 100)
            access_token: OAuth token (injected)
        
        Returns:
            [
                {
                    "item_id": "123",
                    "title": "Item Title",
                    "url": "https://...",
                    "created_at": "2025-11-03T12:00:00Z"
                },
                ...
            ]
        
        Raises:
            PlatformError: If listing fails
        """
        if not access_token:
            raise PlatformError("access_token required")
        
        data = self._make_request(
            "GET",
            f"/items?limit={min(limit, 100)}",
            access_token
        )
        
        return [{
            "item_id": item.get("id"),
            "title": item.get("title"),
            "url": item.get("url"),
            "created_at": item.get("created_at")
        } for item in data.get("items", [])]


# Create single shared instance (efficient, no per-call instantiation)
_platform_manager = PlatformToolsManager()


# Module-level exports (registry discovers these)
def platform_create_item(
    title: str,
    content: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Create a new item in Platform.
    
    Args:
        title: Item title (required)
        content: Item content (optional)
        **kwargs: Credential injection (access_token)
    
    Returns:
        Dict with item_id, title, url, created_at
    
    Raises:
        PlatformError: If creation fails
    """
    access_token = kwargs.get('access_token')
    return _platform_manager.create_item(title, content, access_token)


def platform_list_items(
    limit: int = 10,
    **kwargs
) -> List[Dict[str, Any]]:
    """
    List items from Platform.
    
    Args:
        limit: Max items to return (default: 10)
        **kwargs: Credential injection (access_token)
    
    Returns:
        List of items with id, title, url, created_at
    
    Raises:
        PlatformError: If listing fails
    """
    access_token = kwargs.get('access_token')
    return _platform_manager.list_items(limit, access_token)
```

### Why This Pattern?

✅ **Efficiency**: Single manager instance (not recreated per call)  
✅ **Organization**: Class structure keeps related code together  
✅ **Credential Injection**: `**kwargs` pattern for runtime credentials  
✅ **Error Handling**: Centralized in `_make_request()`  
✅ **Type Hints**: Full typing for IDE support  
✅ **Documentation**: Docstrings for all public functions  
✅ **Registry Compatible**: Module-level exports auto-discovered  
✅ **Testable**: Manager can be mocked for unit tests  

---

## Naming Conventions

### Official Standards Synthesis

**Anthropic Pattern:**
- `verb_noun` format: `get_weather`, `send_email`
- Clear, descriptive, no abbreviations

**Microsoft Graph Pattern:**
- Resource-oriented: `/users/{id}/messages`
- Standard HTTP methods (GET, POST, PATCH, DELETE)

**Google Workspace Pattern:**
- Service-based: `gmail.users().messages().list()`
- Hierarchical resource paths

### 🏆 **RECOMMENDED NAMING FOR AI_AGENTS PLATFORM:**

#### Tool Function Names:
```
{platform}_{action}_{object}
```

**Examples:**
- `gmail_send_email` (not `sendEmail`, `gmailSend`, `email_send`)
- `google_docs_create_document` (not `gdocs_create`, `createDoc`)
- `microsoft_word_create_document` (not `word_create`, `msWordCreate`)
- `slack_post_message` (not `slackPost`, `postSlackMessage`)

#### Class Names:
```
{Platform}ToolsManager
```

**Examples:**
- `GmailToolsManager`
- `GoogleDocsToolsManager`
- `MicrosoftWordToolsManager`
- `SlackToolsManager`

#### Schema File Names:
```
{platform}_tools.json
```

**Examples:**
- `gmail_tools.json`
- `google_docs_tools.json`
- `microsoft_word_tools.json`
- `slack_tools.json`

#### Implementation File Names:
```
{platform}.py
```

**Examples:**
- `gmail.py`
- `google_docs.py` (NOT `google_workspace.py` - too generic)
- `microsoft_word.py` (NOT `microsoft.py` - too generic)
- `slack.py`

### Variable Naming:
- Use `snake_case` for Python
- Be descriptive: `access_token` not `token` or `at`
- Avoid abbreviations: `user_id` not `uid`
- Boolean prefixes: `is_active`, `has_permission`, `can_edit`

### Constant Naming:
- Use `UPPER_SNAKE_CASE`
- Group by purpose: `DEFAULT_TIMEOUT`, `MAX_RETRIES`, `BASE_URL`

---

## Implementation Patterns Comparison

### Pattern A: Class + Instance Exports (Microsoft Tools) ⭐⭐⭐⭐⭐

**Code:**
```python
class MicrosoftWordTools:
    def __init__(self):
        self.credentials = None
    
    def word_create_document(self, title, **kwargs):
        access_token = kwargs.get('access_token')
        # Implementation

# Single instance
microsoft_word_tools = MicrosoftWordTools()

# Module exports (registry discovers these)
microsoft_word_create_document = microsoft_word_tools.word_create_document
```

**Pros:**
- ✅ Single instance (efficient)
- ✅ Organized structure
- ✅ Methods stay together
- ✅ Easy to add shared state

**Cons:**
- ⚠️ Requires module exports (extra step)
- ⚠️ Registry must return MODULE not class

**Use Case:** Complex platforms with many tools (10+ tools)

---

### Pattern B: Direct Functions (Google Tools) ⭐⭐⭐⭐⭐

**Code:**
```python
def google_docs_create_document(title, **kwargs):
    """Create a Google Doc"""
    access_token = kwargs.get('access_token')
    # Implementation
    return result

def google_docs_list_documents(**kwargs):
    """List Google Docs"""
    access_token = kwargs.get('access_token')
    # Implementation
    return results
```

**Pros:**
- ✅ Simple, straightforward
- ✅ No instantiation overhead
- ✅ Registry auto-discovers
- ✅ Fast execution

**Cons:**
- ⚠️ Can get messy with 20+ tools in one file
- ⚠️ Harder to share state/helpers

**Use Case:** Simple platforms with few tools (1-5 tools)

---

### Pattern C: Class + Per-Call Instantiation (Stripe/Slack) ⭐⭐

**Code:**
```python
class StripeTools:
    def __init__(self):
        self.api_key = None
    
    def create_payment_intent(self, amount, **kwargs):
        # Implementation

# Per-call instantiation (inefficient!)
def stripe_create_payment_intent(**kwargs):
    tools = StripeTools()  # NEW INSTANCE EVERY CALL!
    return tools.create_payment_intent(**kwargs)
```

**Pros:**
- ✅ Organized structure
- ✅ Registry auto-discovers exports

**Cons:**
- ❌ Creates new instance per call (inefficient)
- ❌ Wastes memory and CPU
- ❌ Slower than other patterns

**Recommendation:** ⚠️ **AVOID - Migrate to Pattern A or B**

---

### Pattern D: Helper + Direct Functions (GitHub/Supabase) ⭐⭐⭐⭐

**Code:**
```python
def _get_client(access_token):
    """Helper to create/get API client"""
    return GithubClient(access_token)

def github_list_repos(**kwargs):
    """List GitHub repos"""
    access_token = kwargs.get('access_token')
    client = _get_client(access_token)
    return client.list_repos()
```

**Pros:**
- ✅ Lazy initialization
- ✅ Clean separation of concerns
- ✅ Registry auto-discovers

**Cons:**
- ⚠️ Extra function call per operation
- ⚠️ Client creation overhead per call

**Use Case:** When using third-party SDK (PyGithub, Supabase client)

---

## Authentication & Credential Handling

### Current AI_agents Pattern (MUST FOLLOW)

**1. Credential Injection at Runtime**

```python
def tool_function(param1, param2, **kwargs):
    """
    Tool function with credential injection.
    
    Args:
        param1: Business parameter
        param2: Business parameter
        **kwargs: Runtime credential injection
    """
    # Extract credentials from kwargs
    access_token = kwargs.get('access_token')
    refresh_token = kwargs.get('refresh_token')
    user_id = kwargs.get('_user_id')  # Special parameter
    
    if not access_token:
        raise ValueError("access_token required")
    
    # Use credentials for API call
    response = make_api_call(access_token, param1, param2)
    return response
```

**2. Credential Injector (AI_infrastructure/auth/credential_injector.py)**

```python
class CredentialInjector:
    def get_credentials_for_tool(self, platform, user_id):
        """
        Fetch user credentials from database.
        
        Args:
            platform: Platform name (google, microsoft, slack, etc.)
            user_id: User ID
        
        Returns:
            Dict with access_token, refresh_token, etc.
        """
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT access_token, refresh_token, token_expiry
            FROM user_platform_credentials
            WHERE user_id = ? AND platform = ?
            ORDER BY updated_at DESC
            LIMIT 1
        """, (user_id, platform))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return {
            'access_token': row[0],
            'refresh_token': row[1],
            'token_expiry': row[2]
        }
```

**3. Tool Execution with Injection**

```python
# In registry_v3.py or agent worker
injector = CredentialInjector()

# Get credentials for user
creds = injector.get_credentials_for_tool('google', user_id=1)

# Execute tool with injected credentials
result = registry.execute_tool(
    'google_docs_create_document',
    title='My Document',
    **creds  # Inject credentials
)
```

### OAuth Flow Implementation

**Google OAuth:**
```python
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def refresh_google_token(refresh_token):
    """Refresh Google OAuth token"""
    # Implementation using google-auth library
    
def google_docs_create_document(title, **kwargs):
    access_token = kwargs.get('access_token')
    credentials = Credentials(token=access_token)
    service = build('docs', 'v1', credentials=credentials)
    # Use service
```

**Microsoft OAuth:**
```python
import requests

def refresh_microsoft_token(refresh_token):
    """Refresh Microsoft Graph token"""
    # Implementation using MSAL library
    
def microsoft_word_create_document(title, **kwargs):
    access_token = kwargs.get('access_token')
    headers = {'Authorization': f'Bearer {access_token}'}
    # Make API call
```

### Service Account Pattern (Google)

```python
from google.oauth2 import service_account

SERVICE_ACCOUNT_FILE = 'path/to/credentials.json'
SCOPES = ['https://www.googleapis.com/auth/documents']

def get_service_account_credentials(user_email=None):
    """Get service account credentials"""
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    
    # Optional: Impersonate user (domain-wide delegation)
    if user_email:
        credentials = credentials.with_subject(user_email)
    
    return credentials
```

---

## Error Handling Standards

### Comprehensive Error Handling Pattern

```python
class PlatformError(Exception):
    """Base exception for Platform API errors"""
    pass

class PlatformAuthError(PlatformError):
    """Authentication/authorization errors"""
    pass

class PlatformRateLimitError(PlatformError):
    """Rate limiting errors"""
    pass

class PlatformNotFoundError(PlatformError):
    """Resource not found errors"""
    pass

class PlatformValidationError(PlatformError):
    """Input validation errors"""
    pass


def tool_function(param1, **kwargs):
    """Tool with comprehensive error handling"""
    
    # 1. Validate inputs
    if not param1:
        raise PlatformValidationError("param1 is required")
    
    # 2. Get credentials
    access_token = kwargs.get('access_token')
    if not access_token:
        raise PlatformAuthError("access_token required")
    
    # 3. Make API call with error handling
    try:
        response = requests.post(
            url, 
            headers={'Authorization': f'Bearer {access_token}'},
            json={'param1': param1}
        )
        response.raise_for_status()
        
    except requests.exceptions.HTTPError as e:
        status_code = response.status_code
        
        if status_code == 401:
            raise PlatformAuthError("Invalid or expired token")
        elif status_code == 403:
            raise PlatformAuthError("Insufficient permissions")
        elif status_code == 404:
            raise PlatformNotFoundError("Resource not found")
        elif status_code == 429:
            retry_after = response.headers.get('Retry-After', 60)
            raise PlatformRateLimitError(
                f"Rate limit exceeded, retry after {retry_after}s"
            )
        elif status_code >= 500:
            raise PlatformError(f"Server error: {status_code}")
        else:
            raise PlatformError(f"API error: {e}")
            
    except requests.exceptions.Timeout:
        raise PlatformError("Request timeout")
    except requests.exceptions.ConnectionError:
        raise PlatformError("Connection error")
    except Exception as e:
        raise PlatformError(f"Unexpected error: {e}")
    
    # 4. Return structured response
    return {
        "success": True,
        "data": response.json()
    }
```

### Error Response Format

**Success:**
```json
{
  "success": true,
  "data": {
    "id": "123",
    "title": "Document Title"
  }
}
```

**Error:**
```json
{
  "success": false,
  "error": {
    "type": "PlatformAuthError",
    "message": "Invalid or expired token",
    "code": 401
  }
}
```

---

## Performance Optimization

### 1. Use Projections (Microsoft Graph)

**Bad:**
```python
response = requests.get(
    'https://graph.microsoft.com/v1.0/me/messages',
    headers=headers
)
# Returns ALL properties (wastes bandwidth)
```

**Good:**
```python
response = requests.get(
    'https://graph.microsoft.com/v1.0/me/messages?$select=from,subject,receivedDateTime',
    headers=headers
)
# Returns only needed properties
```

### 2. Implement Pagination

**Bad:**
```python
def list_items(**kwargs):
    response = requests.get(url, headers=headers)
    return response.json()['value']
    # Only returns first page!
```

**Good:**
```python
def list_items(limit=100, **kwargs):
    """List all items with pagination"""
    all_items = []
    next_link = url
    
    while next_link and len(all_items) < limit:
        response = requests.get(next_link, headers=headers)
        data = response.json()
        
        all_items.extend(data.get('value', []))
        next_link = data.get('@odata.nextLink')
    
    return all_items[:limit]
```

### 3. Use Delta Queries (Change Tracking)

**Bad (Polling):**
```python
# Poll every 5 minutes
while True:
    messages = get_all_messages()
    process_messages(messages)
    time.sleep(300)
    # Inefficient - retrieves all messages every time
```

**Good (Delta Query):**
```python
# Track changes only
delta_link = get_initial_delta_link()

while True:
    changes = get_delta(delta_link)
    process_changes(changes)
    delta_link = changes['@odata.deltaLink']
    time.sleep(300)
    # Efficient - only retrieves changes
```

### 4. Use Batch Requests (Microsoft Graph)

**Bad:**
```python
# 3 separate API calls
user = get_user()
messages = get_messages()
calendar = get_calendar()
```

**Good:**
```python
# 1 batch API call
batch_request = {
    "requests": [
        {"id": "1", "method": "GET", "url": "/me"},
        {"id": "2", "method": "GET", "url": "/me/messages"},
        {"id": "3", "method": "GET", "url": "/me/calendar"}
    ]
}
response = requests.post(
    'https://graph.microsoft.com/v1.0/$batch',
    json=batch_request
)
```

### 5. Implement Caching

```python
from functools import lru_cache
from datetime import datetime, timedelta

class PlatformToolsManager:
    def __init__(self):
        self._cache = {}
        self._cache_expiry = {}
    
    def _get_cached(self, key, ttl_seconds=300):
        """Get cached value if not expired"""
        if key in self._cache:
            expiry = self._cache_expiry.get(key)
            if expiry and datetime.now() < expiry:
                return self._cache[key]
        return None
    
    def _set_cached(self, key, value, ttl_seconds=300):
        """Set cached value with expiry"""
        self._cache[key] = value
        self._cache_expiry[key] = datetime.now() + timedelta(seconds=ttl_seconds)
    
    def get_user_profile(self, user_id, **kwargs):
        """Get user profile with caching"""
        cache_key = f"user_profile_{user_id}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        # Fetch from API
        result = self._api_call(f"/users/{user_id}")
        self._set_cached(cache_key, result)
        return result
```

### 6. Connection Pooling

```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class PlatformToolsManager:
    def __init__(self):
        # Create session with connection pooling
        self.session = requests.Session()
        
        # Configure retries
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=10
        )
        
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
    
    def _make_request(self, method, url, **kwargs):
        """Use session for connection pooling"""
        return self.session.request(method, url, **kwargs)
```

---

## Tool Templates

### Template 1: Simple Direct Functions (1-5 tools)

```python
"""
Platform Name Tools - Integration with Platform API

Functions:
- platform_action_object: Description
"""

import requests
from typing import Dict, Any, List, Optional


class PlatformError(Exception):
    """Custom exception for Platform errors"""
    pass


def platform_create_item(
    title: str,
    content: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Create a new item in Platform.
    
    Args:
        title: Item title (required)
        content: Item content (optional)
        **kwargs: Credential injection (access_token)
    
    Returns:
        {
            "success": true,
            "item_id": "123",
            "title": "Item Title"
        }
    
    Raises:
        PlatformError: If creation fails
    """
    access_token = kwargs.get('access_token')
    if not access_token:
        raise PlatformError("access_token required")
    
    url = "https://api.platform.com/v1/items"
    headers = {"Authorization": f"Bearer {access_token}"}
    payload = {"title": title, "content": content or ""}
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        return {
            "success": True,
            "item_id": data.get("id"),
            "title": data.get("title")
        }
    except requests.exceptions.RequestException as e:
        raise PlatformError(f"Failed to create item: {e}")


def platform_list_items(
    limit: int = 10,
    **kwargs
) -> List[Dict[str, Any]]:
    """
    List items from Platform.
    
    Args:
        limit: Max items to return (default: 10)
        **kwargs: Credential injection (access_token)
    
    Returns:
        [{"item_id": "123", "title": "Item"}, ...]
    
    Raises:
        PlatformError: If listing fails
    """
    access_token = kwargs.get('access_token')
    if not access_token:
        raise PlatformError("access_token required")
    
    url = f"https://api.platform.com/v1/items?limit={limit}"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        return [{
            "item_id": item.get("id"),
            "title": item.get("title")
        } for item in data.get("items", [])]
    except requests.exceptions.RequestException as e:
        raise PlatformError(f"Failed to list items: {e}")
```

### Template 2: Class-Based Manager (6+ tools)

See "Recommended Tool Structure" section above for full template.

### Template 3: Schema File

```json
{
  "platform": "platform_name",
  "description": "Platform Name API integration",
  "tools": [
    {
      "name": "platform_create_item",
      "description": "Create a new item in Platform. Returns item ID and details.",
      "platform": "platform_name",
      "parameters": {
        "type": "object",
        "properties": {
          "title": {
            "type": "string",
            "description": "Item title (required)"
          },
          "content": {
            "type": "string",
            "description": "Item content (optional)"
          }
        },
        "required": ["title"]
      },
      "returns": {
        "type": "object",
        "description": "Created item with id and title"
      }
    },
    {
      "name": "platform_list_items",
      "description": "List items from Platform with pagination support",
      "platform": "platform_name",
      "parameters": {
        "type": "object",
        "properties": {
          "limit": {
            "type": "integer",
            "description": "Max items to return (default: 10, max: 100)",
            "default": 10
          }
        },
        "required": []
      },
      "returns": {
        "type": "array",
        "description": "List of items with id and title"
      }
    }
  ]
}
```

---

## Migration Guide

### Migrating from Pattern C (Inefficient) to Hybrid Pattern

**Before (Stripe - Per-Call Instantiation):**
```python
class StripeTools:
    def create_payment_intent(self, amount, **kwargs):
        # Implementation

def stripe_create_payment_intent(**kwargs):
    tools = StripeTools()  # NEW INSTANCE EVERY CALL!
    return tools.create_payment_intent(**kwargs)
```

**After (Hybrid - Single Instance):**
```python
class StripeToolsManager:
    def __init__(self):
        pass  # No credentials stored
    
    def create_payment_intent(self, amount, access_token, **kwargs):
        # Implementation

# Single shared instance
_stripe_manager = StripeToolsManager()

def stripe_create_payment_intent(amount, **kwargs):
    access_token = kwargs.get('access_token')
    return _stripe_manager.create_payment_intent(amount, access_token)
```

### Steps to Migrate:

1. **Rename class** to `{Platform}ToolsManager`
2. **Remove credential storage** from `__init__`
3. **Add credential parameters** to methods
4. **Create single instance** at module level: `_platform_manager = PlatformToolsManager()`
5. **Update module exports** to use shared instance
6. **Test thoroughly** to ensure no breaking changes

### Tools to Migrate (Priority Order):

1. ✅ **High Priority** (inefficient pattern):
   - Stripe (12 tools)
   - Slack (8 tools)
   - Twilio (6 tools)
   - WooCommerce (5 tools)

2. ⚠️ **Medium Priority** (review for improvements):
   - Airtable
   - CloudConvert
   - Dropbox

3. ✓ **Low Priority** (already efficient):
   - Microsoft tools (Pattern A)
   - Google tools (Pattern B)
   - GitHub, Supabase (Pattern D)

---

## Checklist for New Tools

### Before Implementation:
- [ ] Read Anthropic tool use documentation
- [ ] Read platform's official API documentation
- [ ] Review existing similar tools in codebase
- [ ] Decide on implementation pattern (direct functions vs class-based)
- [ ] Plan tool names following `{platform}_{action}_{object}` pattern

### During Implementation:
- [ ] Create schema file in `tools/schemas/`
- [ ] Create implementation file in `tools/implementations/`
- [ ] Use recommended pattern (Hybrid or Direct Functions)
- [ ] Add comprehensive docstrings
- [ ] Include type hints
- [ ] Implement error handling with custom exceptions
- [ ] Add credential injection via `**kwargs`
- [ ] Return structured JSON responses
- [ ] Handle pagination for list operations
- [ ] Implement rate limit handling

### After Implementation:
- [ ] Test tool loading with `registry_v3.py`
- [ ] Verify Anthropic schema format (check `get_anthropic_tools()`)
- [ ] Test with real credentials (OAuth or service account)
- [ ] Test error scenarios (invalid credentials, rate limits, etc.)
- [ ] Document in README.md
- [ ] Add examples to documentation
- [ ] Update CHANGELOG.md
- [ ] Verify no warnings during registry loading

---

## Summary & Recommendations

### Key Takeaways

1. **Use Hybrid Pattern** for new tools (6+ tools per platform)
2. **Use Direct Functions** for simple platforms (1-5 tools)
3. **Follow naming convention**: `{platform}_{action}_{object}`
4. **Implement credential injection** via `**kwargs`
5. **Return structured JSON** with `{"success": true/false, "data": {...}}`
6. **Handle errors comprehensively** with custom exceptions
7. **Add pagination support** for list operations
8. **Include type hints** and docstrings
9. **Test with official API documentation** as reference
10. **Migrate inefficient tools** (Stripe, Slack) to recommended pattern

### Platform-Specific Guidelines

**Anthropic Claude:**
- Tool descriptions are critical (LLM reads them)
- Use `input_schema` with `type: "object"`
- Progressive loading for 100+ tools

**Microsoft Graph:**
- Use MSAL for OAuth
- Implement projections (`$select`)
- Handle pagination (`@odata.nextLink`)
- Use delta queries for change tracking
- Batch requests when possible

**Google Workspace:**
- Service accounts for app-owned data
- OAuth 2.0 for user data
- Domain-wide delegation for admin ops
- Handle quota limits gracefully

### Next Steps

1. **Review and update** existing Stripe, Slack, Twilio tools
2. **Create templates** in `tools/templates/` folder
3. **Document examples** for each pattern
4. **Set up automated tests** for tool registration
5. **Implement monitoring** for tool execution performance

---

**END OF DOCUMENT**

**Last Updated:** November 3, 2025  
**Author:** AI_agents Platform Team  
**Version:** 1.0.0  
**Status:** Official Reference
