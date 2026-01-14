# AI Agents Integration Guide

## 🏗️ **Folder Architecture**

This folder contains AI integration modules for various backend platforms. Each platform gets its own subfolder with a consistent structure.

---

## 📂 **Current Structure**

```
AI_agents/
├── 🔧 SHARED UTILITIES (Root Level)
│   ├── config.py              # Master AI model & API configuration
│   ├── auth.py                # Google Sheets authentication
│   ├── .env                   # Environment variables (production)
│   └── .env.development       # Environment variables (development)
│
├── ☁️ PLATFORM INTEGRATIONS
│   ├── Cloudflare/            # Cloudflare Workers & API
│   ├── Microsoft_365_Connection/  # Office 365 integration
│   ├── Render_backend/        # Render.com deployment API
│   ├── Supabase/              # Supabase database & auth
│   └── Woocommerce/           # WooCommerce e-commerce
│
└── 📚 DOCUMENTATION
    ├── INTEGRATION_GUIDE.md   # This file
    └── [Platform]/README.md   # Platform-specific docs
```

---

## 🔗 **How Shared Utilities Work**

### **1. `config.py` - Master Configuration** (630 lines)

**Purpose**: Centralized configuration for ALL AI agents and platform integrations

**What it provides**:
- ✅ **10 AI API keys** for DeepSeek (with rotation support)
- ✅ **Multiple AI providers**: DeepSeek, Anthropic (Claude), OpenAI (GPT)
- ✅ **Complete model registry**: 16+ models including Claude 4, GPT-5, DeepSeek V3.1
- ✅ **Model capabilities**: Web search, code execution, thinking modes
- ✅ **Supabase credentials**: URL, anon key, service key
- ✅ **Environment detection**: Production vs Development
- ✅ **Streamlit/Render deployment settings**

**How to use in your integration**:

```python
# In any platform module (e.g., Supabase/supabase_client.py)
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from config
from config import (
    SUPABASE_URL,           # Your Supabase project URL
    SUPABASE_ANON_KEY,      # Public API key
    SUPABASE_SERVICE_KEY,   # Admin API key
    ANTHROPIC_API_KEYS,     # Claude API keys
    DEEPSEEK_API_KEYS,      # DeepSeek API keys
    MODEL_CONFIGS,          # All model configurations
    AI_PROVIDERS            # Provider settings
)

# Use the configuration
supabase_client = SupabaseClient(
    url=SUPABASE_URL,
    key=SUPABASE_ANON_KEY
)
```

**Key functions available**:
```python
from config import (
    get_available_models,      # Get all models by provider
    get_model_capabilities,    # Check model features
    get_model_description,     # Get model info
    validate_model_for_provider,  # Check model availability
    get_models_by_capability   # Find models with specific features
)

# Example: Get all models that support web search
web_search_models = get_models_by_capability('web_search')
# Returns: {'anthropic': ['claude-sonnet-4-20250514', 'claude-3-7-sonnet-20250219', ...]}
```

---

### **2. `auth.py` - Google Sheets Authentication** (173 lines)

**Purpose**: Service account authentication for Google Sheets with caching

**What it provides**:
- ✅ Service account credential management
- ✅ 10-minute credential cache (multi-user safe)
- ✅ Spreadsheet access validation
- ✅ Worksheet retrieval by name or GID
- ✅ Automatic fallback to default credentials

**How to use**:

```python
from auth import (
    get_authenticated_gspread_client_sync,
    validate_spreadsheet_access,
    get_worksheet_by_name_or_gid
)

# Get authenticated client
client = get_authenticated_gspread_client_sync()

# Validate access to specific spreadsheet
client, spreadsheet = validate_spreadsheet_access('1ABC123...')

# Get worksheet by name or GID
worksheet = get_worksheet_by_name_or_gid(spreadsheet, 'Sheet1')
# OR by GID: get_worksheet_by_name_or_gid(spreadsheet, 'Sheet_12345')
```

**Environment variables needed**:
```bash
SERVICE_ACCOUNT_EMAIL=your-service-account@project.iam.gserviceaccount.com
SERVICE_ACCOUNT_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\nMIIE...
SERVICE_ACCOUNT_PRIVATE_KEY_ID=abc123def456...
```

---

### **3. `.env` - Environment Variables**

**Purpose**: Store sensitive credentials and configuration

**Current contents**:
- Cloudflare API tokens
- WooCommerce API keys
- Supabase credentials
- GitHub credentials
- Render deployment settings

**How to add new variables**:

```bash
# 1. Add to .env file
MY_NEW_API_KEY=sk-abc123...
MY_NEW_URL=https://api.example.com

# 2. Access in Python code
import os
api_key = os.getenv('MY_NEW_API_KEY')
api_url = os.getenv('MY_NEW_URL')

# 3. Add to config.py for shared access
# In config.py:
MY_NEW_API_KEY = os.getenv('MY_NEW_API_KEY')
MY_NEW_URL = os.getenv('MY_NEW_URL', 'https://default-url.com')  # With fallback
```

---

## 🎯 **Creating a New Platform Integration**

### **Step 1: Create Folder Structure**

```bash
AI_agents/
└── Your_New_Platform/
    ├── README.md                      # Main documentation
    ├── QUICK_START.md                 # 5-minute setup guide
    ├── your_platform_client.py        # Main client class
    ├── test_connection.py             # Connection test script
    └── [additional modules]           # Feature-specific files
```

### **Step 2: Create Main Client Module**

```python
"""
Your_New_Platform Client
========================

Python client for Your New Platform API.

Created: [Date]
"""

import os
import sys
import requests
from typing import Dict, Optional

# 🔗 IMPORT SHARED CONFIG
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import AI_PROVIDERS, MODEL_CONFIGS  # If you need AI features

class YourPlatformClient:
    """
    Client for Your New Platform API.
    
    Usage:
        client = YourPlatformClient(api_key='your-key')
        result = client.do_something()
    """
    
    def __init__(self, api_key: str = None, base_url: str = None):
        """Initialize client"""
        self.api_key = api_key or os.getenv('YOUR_PLATFORM_API_KEY')
        self.base_url = base_url or os.getenv('YOUR_PLATFORM_BASE_URL', 'https://api.yourplatform.com')
        
        if not self.api_key:
            raise ValueError("API key required. Set YOUR_PLATFORM_API_KEY environment variable.")
        
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def health_check(self) -> Dict:
        """Test API connectivity"""
        try:
            response = requests.get(f'{self.base_url}/health', headers=self.headers, timeout=10)
            response.raise_for_status()
            return {'status': 'ok', 'connected': True}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    # Add your platform-specific methods here
    
    def cli(self):
        """Command-line interface for testing"""
        import argparse
        parser = argparse.ArgumentParser(description='Your Platform CLI')
        parser.add_argument('--test', action='store_true', help='Run connection test')
        args = parser.parse_args()
        
        if args.test:
            result = self.health_check()
            print(f"Connection test: {result}")


if __name__ == '__main__':
    # CLI mode when run directly
    client = YourPlatformClient()
    client.cli()
```

### **Step 3: Create Test Script**

```python
"""
Test connection to Your Platform

Usage:
    python test_connection.py
"""

import os
from your_platform_client import YourPlatformClient

def test_connection():
    """Test API connection and basic operations"""
    
    print("🔧 Testing Your Platform Connection...")
    print("=" * 50)
    
    # Check environment variables
    api_key = os.getenv('YOUR_PLATFORM_API_KEY')
    if not api_key:
        print("❌ YOUR_PLATFORM_API_KEY not set")
        print("   Set it in .env file or environment")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    # Initialize client
    try:
        client = YourPlatformClient()
        print("✅ Client initialized")
    except Exception as e:
        print(f"❌ Client initialization failed: {e}")
        return False
    
    # Test connection
    print("\n🔍 Testing API connection...")
    result = client.health_check()
    
    if result['status'] == 'ok':
        print("✅ Connection successful!")
        return True
    else:
        print(f"❌ Connection failed: {result.get('message')}")
        return False


if __name__ == '__main__':
    success = test_connection()
    exit(0 if success else 1)
```

### **Step 4: Create Documentation**

**README.md**:
```markdown
# Your Platform Integration

Python client for Your Platform API.

## Quick Start

1. Install dependencies:
```bash
pip install requests  # Add your dependencies
```

2. Set environment variables:
```bash
# In .env file
YOUR_PLATFORM_API_KEY=your-api-key-here
YOUR_PLATFORM_BASE_URL=https://api.yourplatform.com
```

3. Use the client:
```python
from Your_New_Platform.your_platform_client import YourPlatformClient

client = YourPlatformClient()
result = client.health_check()
print(result)
```

## Features

- ✅ Feature 1
- ✅ Feature 2
- ✅ Feature 3

## API Reference

[Add your API documentation here]
```

**QUICK_START.md**:
```markdown
# Quick Start - 5 Minutes

## 1️⃣ Get API Credentials (2 minutes)

1. Go to https://yourplatform.com/settings/api
2. Create new API key
3. Copy the key

## 2️⃣ Configure Environment (1 minute)

```bash
# Edit AI_agents/.env
YOUR_PLATFORM_API_KEY=sk-abc123...
```

## 3️⃣ Test Connection (2 minutes)

```bash
cd AI_agents/Your_New_Platform
python test_connection.py
```

✅ You're ready to use Your Platform integration!
```

### **Step 5: Add to .env File**

```bash
# In AI_agents/.env, add:

# ===========================================
# Your New Platform Configuration
# ===========================================
YOUR_PLATFORM_API_KEY=your-api-key-here
YOUR_PLATFORM_BASE_URL=https://api.yourplatform.com
YOUR_PLATFORM_TIMEOUT=30
```

### **Step 6: Add to config.py (if AI integration needed)**

```python
# In AI_agents/config.py, add near the end:

# ==============================================
# YOUR NEW PLATFORM CONFIGURATION
# ==============================================

YOUR_PLATFORM_API_KEY = os.getenv('YOUR_PLATFORM_API_KEY')
YOUR_PLATFORM_BASE_URL = os.getenv('YOUR_PLATFORM_BASE_URL', 'https://api.yourplatform.com')
YOUR_PLATFORM_TIMEOUT = int(os.getenv('YOUR_PLATFORM_TIMEOUT', '30'))
```

---

## 📊 **Integration Checklist**

When creating a new platform integration, check off these items:

### **Required Files**
- [ ] `README.md` - Main documentation with usage examples
- [ ] `QUICK_START.md` - 5-minute setup guide
- [ ] `[platform]_client.py` - Main client class with proper imports
- [ ] `test_connection.py` - Connection testing script

### **Integration Steps**
- [ ] Import `config.py` for shared configuration (if needed)
- [ ] Add environment variables to `.env`
- [ ] Add configuration to `config.py` (if shared access needed)
- [ ] Test connection with real credentials
- [ ] Document all API methods

### **Code Quality**
- [ ] Type hints on all methods (`def method(arg: str) -> Dict:`)
- [ ] Docstrings on all classes and methods
- [ ] Error handling with try/except
- [ ] CLI interface for testing (`if __name__ == '__main__':`)
- [ ] Logging with emoji prefixes (🔧 ✅ ❌ 🔍 📊)

### **Documentation Quality**
- [ ] Clear usage examples
- [ ] Environment variable list
- [ ] Troubleshooting section
- [ ] API reference
- [ ] Quick start guide

---

## 🔧 **Best Practices**

### **1. Always Use Shared Config**

✅ **Good**:
```python
from config import SUPABASE_URL, AI_PROVIDERS
```

❌ **Bad**:
```python
SUPABASE_URL = "https://hardcoded-url.supabase.co"  # Don't hardcode
```

### **2. Support Multiple Configuration Sources**

```python
# Priority: argument > config.py > environment > default
self.api_key = (
    api_key or                           # 1. Argument
    (CONFIG_API_KEY if CONFIG_AVAILABLE else None) or  # 2. config.py
    os.getenv('API_KEY') or             # 3. Environment
    'default-key'                        # 4. Default
)
```

### **3. Add Health Checks**

Every client should have a `health_check()` method:

```python
def health_check(self) -> Dict:
    """Test API connectivity"""
    try:
        response = requests.get(f'{self.base_url}/health', headers=self.headers, timeout=10)
        response.raise_for_status()
        return {'status': 'ok', 'connected': True, 'response_time': response.elapsed.total_seconds()}
    except requests.exceptions.RequestException as e:
        return {'status': 'error', 'message': str(e), 'connected': False}
```

### **4. Use Consistent Logging**

```python
print('🔧 Processing...')      # Processing/working
print('✅ Success!')            # Success
print('❌ Error:', e)           # Error
print('🔍 Debug info')          # Debug
print('📊 Data:', data)         # Data/metrics
print('⚠️ Warning')             # Warning
```

### **5. Create CLI Interfaces**

```python
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Platform Client CLI')
    parser.add_argument('--test', action='store_true', help='Run connection test')
    parser.add_argument('--query', type=str, help='Run a query')
    args = parser.parse_args()
    
    client = PlatformClient()
    
    if args.test:
        print(client.health_check())
    elif args.query:
        print(client.query(args.query))
    else:
        parser.print_help()
```

---

## 🚀 **AI Integration Patterns**

If your platform integration needs AI capabilities:

### **Pattern 1: Use Shared AI Models**

```python
from config import AI_PROVIDERS, MODEL_CONFIGS, get_model_capabilities

class YourPlatformClient:
    def __init__(self, ai_model='deepseek-chat'):
        # Get AI configuration
        self.ai_model = ai_model
        self.ai_config = MODEL_CONFIGS.get(ai_model, {})
        self.ai_provider = self.ai_config.get('provider', 'deepseek')
        
        # Get API keys for the provider
        provider_config = AI_PROVIDERS.get(self.ai_provider, {})
        self.ai_api_keys = provider_config.get('api_keys', [])
    
    def analyze_with_ai(self, content: str) -> Dict:
        """Use AI to analyze content"""
        capabilities = get_model_capabilities(self.ai_provider, self.ai_model)
        
        if capabilities.get('web_search'):
            print(f"✅ Using {self.ai_model} with web search capability")
        
        # Make AI API call here
        pass
```

### **Pattern 2: Multi-Model Support**

```python
from config import get_available_models, validate_model_for_provider

class YourPlatformClient:
    def set_ai_model(self, model: str, provider: str = 'deepseek'):
        """Change AI model"""
        if validate_model_for_provider(provider, model):
            self.ai_model = model
            self.ai_provider = provider
            print(f"✅ Switched to {provider}/{model}")
        else:
            available = get_available_models(provider)
            raise ValueError(f"Model {model} not available. Try: {available}")
```

---

## 📚 **Examples from Existing Integrations**

### **Supabase Integration** (Complete Example)

Location: `AI_agents/Supabase/`

```python
# Demonstrates:
# ✅ Importing from config.py
# ✅ Multiple configuration sources
# ✅ Query builder pattern
# ✅ Authentication methods
# ✅ Storage operations
# ✅ CLI interface
# ✅ Comprehensive documentation

from config import SUPABASE_URL, SUPABASE_ANON_KEY

client = SupabaseClient()  # Uses config.py automatically
data = client.query('users').select('*').eq('status', 'active').execute()
```

### **Cloudflare Integration** (Serverless Pattern)

Location: `AI_agents/Cloudflare/`

```
# Demonstrates:
# ✅ Worker deployment with Wrangler
# ✅ 14 utility scripts organized in /scripts
# ✅ Comprehensive documentation (5 markdown files)
# ✅ Error handling and logging
# ✅ Production deployment patterns
```

### **Microsoft 365 Integration** (OAuth Pattern)

Location: `AI_agents/Microsoft_365_Connection/`

```python
# Demonstrates:
# ✅ OAuth authentication
# ✅ Email sending via Microsoft Graph
# ✅ Document processing
# ✅ Comprehensive setup guides
```

---

## ⚠️ **Common Pitfalls to Avoid**

### **1. Hardcoding Credentials**
❌ Don't do this:
```python
api_key = "sk-abc123..."  # Exposed in code!
```

✅ Do this:
```python
api_key = os.getenv('API_KEY') or raise ValueError("API_KEY required")
```

### **2. Not Testing Imports**
❌ Don't assume config.py will always be available:
```python
from config import MY_CONFIG  # Crashes if file missing
```

✅ Do this:
```python
try:
    from config import MY_CONFIG
    CONFIG_AVAILABLE = True
except ImportError:
    MY_CONFIG = None
    CONFIG_AVAILABLE = False
```

### **3. Missing Error Handling**
❌ Don't let errors crash silently:
```python
response = requests.get(url)  # What if it fails?
```

✅ Do this:
```python
try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    print(f"❌ API request failed: {e}")
    return {'error': str(e)}
```

### **4. Not Providing Defaults**
❌ Don't require all arguments:
```python
def __init__(self, url, key, timeout, retry, max_connections):
    # Too many required arguments!
```

✅ Do this:
```python
def __init__(self, url=None, key=None, timeout=30, retry=3):
    # Sensible defaults, only critical args required
```

---

## 🎯 **Next Steps**

1. **Review existing integrations** in `Cloudflare/`, `Supabase/`, `Microsoft_365_Connection/`
2. **Create your new integration** following the template above
3. **Test thoroughly** with `test_connection.py`
4. **Document everything** in README.md and QUICK_START.md
5. **Update this guide** if you discover new patterns

---

## 📞 **Support**

If you need help creating a new integration:

1. Check existing integrations for similar patterns
2. Review `config.py` for available utilities
3. Test with `test_connection.py` first
4. Use logging with emoji prefixes for debugging

**Happy integrating! 🚀**
