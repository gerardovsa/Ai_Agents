# AI Agents - Backend Platform Integrations

**Purpose**: Centralized repository for AI-powered backend platform integrations and API clients.

---

## 📁 **Folder Structure**

```
AI_agents/
├── 🔧 SHARED UTILITIES
│   ├── config.py              # Master AI model & API configuration (630 lines)
│   ├── auth.py                # Google Sheets authentication (173 lines)
│   ├── .env                   # Environment variables (production)
│   └── .env.development       # Environment variables (development)
│
├── ☁️ PLATFORM INTEGRATIONS
│   ├── Cloudflare/            # Cloudflare Workers & API (14 scripts + docs)
│   ├── Microsoft_365_Connection/  # Office 365 integration (8 files)
│   ├── Render_backend/        # Render.com deployment API (10 files)
│   ├── Supabase/              # Supabase database & auth (5 files)
│   └── Woocommerce/           # WooCommerce e-commerce
│
└── 📚 DOCUMENTATION
    ├── README.md              # This file
    ├── INTEGRATION_GUIDE.md   # Complete integration guide (432 lines)
    └── ASSESSMENT_SUMMARY.md  # Assessment of root scripts
```

---

## 🚀 **Quick Start**

### **1. Using Existing Integrations**

```python
# Supabase Example
from Supabase.supabase_client import SupabaseClient

client = SupabaseClient()  # Uses config.py automatically
data = client.query('users').select('*').execute()
```

```python
# Microsoft 365 Example
from Microsoft_365_Connection.microsoft365_client import Microsoft365Client

ms_client = Microsoft365Client()
ms_client.send_email(to='user@example.com', subject='Test', body='Hello!')
```

### **2. Creating New Integrations**

See **[INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md)** for complete step-by-step instructions.

Quick template:
```bash
# 1. Create folder
mkdir Your_New_Platform

# 2. Create main client
# See INTEGRATION_GUIDE.md for template

# 3. Add credentials to .env
echo "YOUR_PLATFORM_API_KEY=sk-abc123..." >> .env

# 4. Test connection
python Your_New_Platform/test_connection.py
```

---

## 🔑 **Shared Configuration**

### **`config.py` - Master Configuration**

**Provides**:
- ✅ **10 AI API keys** (DeepSeek) with rotation support
- ✅ **Multiple AI providers**: DeepSeek, Anthropic (Claude), OpenAI (GPT)
- ✅ **16+ AI models**: Claude 4, GPT-5, DeepSeek V3.1, etc.
- ✅ **Model capabilities**: Web search, code execution, thinking modes
- ✅ **Supabase credentials**: URL, keys
- ✅ **Production settings**: Render, Streamlit configuration

**Usage in any platform module**:
```python
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    SUPABASE_URL,           # Supabase project URL
    ANTHROPIC_API_KEYS,     # Claude API keys
    DEEPSEEK_API_KEYS,      # DeepSeek API keys
    MODEL_CONFIGS,          # All model configurations
    AI_PROVIDERS,           # Provider settings
    get_model_capabilities, # Check model features
    get_available_models    # List all models
)
```

### **`auth.py` - Google Sheets Authentication**

**Provides**:
- ✅ Service account authentication
- ✅ Credential caching (10 min)
- ✅ Spreadsheet validation
- ✅ Worksheet retrieval

**Usage**:
```python
from auth import get_authenticated_gspread_client_sync

client = get_authenticated_gspread_client_sync()
spreadsheet = client.open_by_key('1ABC123...')
```

---

## 🏗️ **Available Integrations**

### **Cloudflare** ☁️
- **Purpose**: Cloudflare Workers deployment & management
- **Status**: ✅ Production ready
- **Files**: 14 scripts + comprehensive docs
- **Features**: Worker deployment, monitoring, troubleshooting

### **Microsoft 365 Connection** 📧
- **Purpose**: Office 365 API integration (email, docs)
- **Status**: ✅ Active
- **Files**: 8 Python modules + setup guides
- **Features**: Email sending, document processing, OAuth

### **Render Backend** 🚀
- **Purpose**: Render.com deployment API
- **Status**: ✅ Active
- **Files**: 10 Python scripts + API docs
- **Features**: Service deployment, monitoring, CORS fixes

### **Supabase** 🗄️
- **Purpose**: Supabase database & authentication
- **Status**: ✅ Ready to test
- **Files**: Complete client + documentation
- **Features**: Database CRUD, auth, storage, realtime

### **WooCommerce** 🛒
- **Purpose**: WooCommerce e-commerce API
- **Status**: ✅ Active
- **Files**: Google Apps Script integration
- **Features**: Order management, product sync

### **AssemblyAI** 🎤
- **Purpose**: Speech-to-text & audio intelligence
- **Status**: ✅ Configured
- **Features**: Transcription, speaker diarization, sentiment analysis, topic detection

### **CloudConvert** 🔄
- **Purpose**: Universal file conversion (200+ formats)
- **Status**: ✅ Configured
- **Features**: Document/image/video/audio conversion, optimization

### **Ngrok** 🌐
- **Purpose**: Secure tunneling & webhook testing
- **Status**: ✅ Configured
- **Features**: Local dev tunnels, webhook testing, request inspection

---

## 📊 **AI Model Support**

Using `config.py`, all integrations have access to:

### **DeepSeek Models**
- `deepseek-chat` - Fast non-thinking mode with function calling
- `deepseek-reasoner` - Advanced reasoning with step-by-step thinking

### **Anthropic Claude Models**
- `claude-sonnet-4-20250514` - Claude 4 with full tool support
- `claude-3-7-sonnet-20250219` - Extended thinking mode
- `claude-3-5-haiku-20241022` - Fastest with web search

### **OpenAI GPT Models**
- `gpt-5` - Latest GPT-5 with enhanced capabilities
- `gpt-5-mini` - Cost-efficient GPT-5
- `gpt-4o` - Reliable with vision support
- `o1` / `o1-mini` - Advanced reasoning models

**Get model capabilities**:
```python
from config import get_model_capabilities

caps = get_model_capabilities('anthropic', 'claude-sonnet-4-20250514')
# Returns: {'web_search': True, 'code_execution': True, 'thinking_budget': 4096, ...}
```

---

## 🔐 **Environment Variables**

All credentials stored in `.env` file:

```bash
# Cloudflare
CLOUDFLARE_ACCOUNT_ID=...
CLOUDFLARE_AI_AGENT_TOKEN=...

# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=...
SUPABASE_SERVICE_ROLE_KEY=...

# WooCommerce
WC_CONSUMER_KEY=...
WC_CONSUMER_SECRET=...
WC_BASE_URL=...

# GitHub
GITHUB_EMAIL=...
GITHUB_PASSWORD=...

# Add your new platform credentials here
```

---

## 🎯 **Integration Patterns**

### **Pattern 1: Simple API Client**
```python
class YourPlatformClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('YOUR_PLATFORM_API_KEY')
        
    def health_check(self):
        # Test connection
        pass
```

### **Pattern 2: AI-Powered Integration**
```python
from config import AI_PROVIDERS, MODEL_CONFIGS

class AIEnabledClient:
    def __init__(self, ai_model='deepseek-chat'):
        self.ai_model = ai_model
        self.ai_config = MODEL_CONFIGS[ai_model]
        
    def analyze_with_ai(self, content):
        # Use AI for analysis
        pass
```

### **Pattern 3: Multi-Provider Support**
```python
from config import get_available_models

class MultiProviderClient:
    def list_models(self):
        return get_available_models('anthropic')
        # Returns: ['claude-sonnet-4-20250514', ...]
```

---

## 📚 **Documentation**

- **[INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md)** - Complete guide for creating new integrations
- **[ASSESSMENT_SUMMARY.md](./ASSESSMENT_SUMMARY.md)** - Assessment of root-level scripts
- **Platform-specific READMEs** - In each platform folder

---

## 🧪 **Testing**

Each integration provides test scripts:

```bash
# Test Supabase connection
cd Supabase
python test_supabase_connection.py

# Test Render API
cd Render_backend
python test_render_connection.py

# Test Microsoft 365
cd Microsoft_365_Connection
python test_email_integration.py
```

---

## 🛠️ **Common Operations**

### **Add New API Key**
```bash
# 1. Add to .env
echo "NEW_API_KEY=sk-abc123..." >> .env

# 2. Reference in code
api_key = os.getenv('NEW_API_KEY')
```

### **Switch AI Model**
```python
from config import AI_PROVIDERS

# Change default model
os.environ['AI_MODEL'] = 'claude-sonnet-4-20250514'
```

### **Check Model Capabilities**
```python
from config import get_models_by_capability

# Find all models with web search
models = get_models_by_capability('web_search')
print(models)
# {'anthropic': ['claude-sonnet-4-20250514', 'claude-3-7-sonnet-20250219', ...]}
```

---

## ⚠️ **Known Issues**

1. ✅ **Fixed**: `auth.py` import issue resolved
2. ✅ **Fixed**: Supabase client now uses `config.py`
3. ⚠️ **Todo**: Update `.env` with actual Supabase credentials (currently placeholders)

---

## 🚀 **Next Steps**

1. **Review** existing integrations for patterns
2. **Read** [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md) for creating new integrations
3. **Test** existing integrations with your credentials
4. **Create** new integration following the template

---

## 📞 **Support**

- Check platform-specific README files for detailed usage
- See [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md) for best practices
- Review [ASSESSMENT_SUMMARY.md](./ASSESSMENT_SUMMARY.md) for architecture details

---

**Last Updated**: January 2025  
**Maintained By**: Gerardo Poli  
**Total Integrations**: 8 platforms + shared utilities  
**New Services**: AssemblyAI, CloudConvert, Ngrok (Oct 2025)
