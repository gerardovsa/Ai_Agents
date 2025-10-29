# GitHub Copilot Instructions - AI Agents Platform

## 🏗️ Architecture Overview

This is a multi-agent AI platform with 564 tools across 19+ platforms. The Flask backend runs on port 5001 and provides a unified API for tool execution, session management, and multi-provider AI interactions.

## 📋 Key Component Pattern

### Core Files & Responsibilities
- `app.py` - **MAIN APPLICATION** - Flask app entry point (legacy)
- `AI_infrastructure/flask_app.py` - **NEW FLASK APP** - Modern Flask backend (port 5001)
- `tools/registry.py` - **TOOL REGISTRY** - Loads 564 tools from schemas and implementations
- `config.py` - **GLOBAL CONFIG** - API keys for all tools
- `AI_infrastructure/config.py` - **FLASK CONFIG** - Flask settings and database paths
- `scripts/` - **ORGANIZED SCRIPTS** - Startup, setup, testing, maintenance utilities

### Tool System Pattern (Critical)
```python
# Tool implementations inherit from base class
class MyToolImplementation:
    def __init__(self, **kwargs):
        self.credentials = None  # Credentials injected at runtime
        
    def my_tool_method(self, param1, param2, **kwargs):
        """Tool method with credential injection"""
        # Get credentials from kwargs (injected by credential_injector)
        access_token = kwargs.get('access_token')
        # Use credentials for API calls
        return self.execute_api_call(access_token, param1, param2)
```

## 🔧 Configuration Architecture (CRITICAL)

### Two Config Files - Correct Architecture

**1. Root `config.py` - Global API keys storage**
   - **Purpose**: Provides API keys for all tools
   - **Contains**: 
     - `DEEPSEEK_API_KEYS` - List of DeepSeek API keys
     - `ANTHROPIC_API_KEYS` - List of Anthropic Claude API keys
     - `OPENAI_API_KEYS` - List of OpenAI API keys
     - `get_api_key_enhanced()` - Helper function for round-robin key rotation
   - **Used by**: Tool implementations in `tools/implementations/`
   - **Import pattern**: `from config import get_api_key_enhanced, DEEPSEEK_API_KEYS`
   - **Location**: `C:\Users\gpoli\GIT\AI_agents\config.py`

**2. AI_infrastructure/config.py - Flask application config**
   - **Purpose**: Flask app settings and database paths
   - **Contains**:
     - `Config` class with Flask configuration
     - `DB_CONFIG_PATH` - Path to database-config.json
     - `SESSION_DB_PATH` - Path to sessions.db
     - `SECRET_KEY` - Flask secret key
     - `DEBUG` - Debug mode setting
     - `CORS_ORIGINS` - CORS allowed origins
   - **Used by**: Flask app (`flask_app.py`) and infrastructure modules
   - **Import pattern**: `from config import Config` (within AI_infrastructure/)
   - **Location**: `C:\Users\gpoli\GIT\AI_agents\AI_infrastructure\config.py`

### Import Rules (MUST FOLLOW)

✅ **DO** - Tool implementations import from root config:
```python
# In tools/implementations/my_tool.py
from config import get_api_key_enhanced, DEEPSEEK_API_KEYS
```

✅ **DO** - Flask infrastructure imports from local config:
```python
# In AI_infrastructure/flask_app.py or AI_infrastructure/routes/*.py
import sys
sys.path.insert(0, os.path.dirname(__file__))
from config import Config
```

❌ **DON'T** - Mix up the configs:
```python
# WRONG - Tool trying to import Flask Config class
from config import Config  # This doesn't exist in root config.py

# WRONG - Flask app trying to import API keys from local config
from config import DEEPSEEK_API_KEYS  # This doesn't exist in AI_infrastructure/config.py
```

## 🚀 Critical Development Commands

### Start the AI Agent Server
```powershell
# From any directory (PATH command)
BISTART

# Or manually
cd C:\Users\gpoli\GIT\AI_agents
BISTART

# Or directly
cd C:\Users\gpoli\GIT\AI_agents\AI_infrastructure
python flask_app.py
```

### Talk to AI Agent
```powershell
# From any directory (PATH command)
CHAT What tools are available?
CHAT List my Gmail messages
CHAT "Create a Google Doc titled 'Test Document'"

# Multi-word queries need quotes
CHAT "Send an email to john@example.com with subject 'Hello'"
```

### Test Tool Loading
```powershell
cd C:\Users\gpoli\GIT\AI_agents
python -c "from tools.registry import ToolRegistry; registry = ToolRegistry(); print(f'Loaded {len(registry.tools)} tools')"
```

## 📊 Tool System Architecture

### Tool Loading Process
1. **Schema Loading** - Loads JSON schemas from `tools/schemas/`
2. **Implementation Loading** - Loads Python implementations from `tools/implementations/`
3. **Registry Creation** - Creates unified registry with 564 tools
4. **Credential Injection** - Injects credentials at runtime via `credential_injector.py`

### Credential Injection Pattern
```python
# AI_infrastructure/auth/credential_injector.py
class CredentialInjector:
    def get_google_credentials(self, user_id):
        """Get Google OAuth credentials for user"""
        # Fetch from user_platform_credentials table
        return {
            'access_token': token,
            'refresh_token': refresh,
            'token_uri': uri
        }
    
    def get_microsoft_credentials(self, user_id):
        """Get Microsoft Graph credentials for user"""
        # Fetch from user_platform_credentials table
        return {
            'access_token': token
        }
```

### Tool Execution Flow
```
User Request → Flask Route → Agent Routes → Tool Registry
    ↓
Credential Injector (adds user credentials)
    ↓
Tool Implementation (executes with credentials)
    ↓
API Call (Google/Microsoft/etc.)
    ↓
Return Result
```

## 🔗 Integration Points

### Flask Routes
```python
# AI_infrastructure/routes/
- agent_routes.py       # Main AI agent conversation endpoints
- thread_routes.py      # Thread management
- export_routes.py      # Export conversations
- task_sync_routes.py   # Universal task sync
- account_linking_routes.py  # OAuth account linking
```

### Authentication Systems
```python
# Google OAuth
from google_workspace.google_auth_manager import GoogleAuthManager

# Microsoft OAuth
from Microsoft_365_Connection.microsoft365_oauth_manager import Microsoft365OAuthManager
```

## 🎨 Script Organization

### scripts/ Folder Structure
```
scripts/
├── startup/           # BISTART, BISTOP, chat, SYNERGY_START
├── setup/            # setup_master_account, setup_microsoft_login
├── testing/          # test_* files (8 test scripts)
├── maintenance/      # cleanup scripts, fix scripts (8 maintenance scripts)
├── deployment/       # ai_agent_render_deploy
└── utilities/        # task_sync_universal, utility helpers
```

### Script Usage Rules

✅ **DO** - Keep essential scripts in root:
- `BISTART.bat` / `BISTART.ps1` - Server startup (PATH command)
- `CHAT.bat` / `chat.ps1` - AI agent CLI (PATH command)
- `app.py` - Legacy Flask entry point
- `config.py` - Global API keys

✅ **DO** - Organize utilities in scripts/:
- Test scripts → `scripts/testing/`
- Setup scripts → `scripts/setup/`
- Maintenance tools → `scripts/maintenance/`

❌ **DON'T** - Put tool implementations in scripts/:
- Tools belong in `tools/implementations/`
- Keep scripts and tools separate

## 🛠️ Common Anti-Patterns (Avoid)

### ❌ Don't: Static credential checks at init
```python
# Bad - Checking for credentials at class init
class MyTool:
    def __init__(self):
        if not os.getenv('MICROSOFT_GRAPH_ACCESS_TOKEN'):
            print('⚠️ Warning: Token not set')  # This will always warn!
```

### ✅ Do: Dynamic credential injection
```python
# Good - Credentials injected at runtime
class MyTool:
    def my_method(self, param1, **kwargs):
        access_token = kwargs.get('access_token')
        if not access_token:
            raise ValueError("access_token required")
        # Use token for API call
```

### ❌ Don't: Import wrong config
```python
# Bad - Tool trying to import Flask Config
from config import Config  # Doesn't exist in root config.py!

# Bad - Flask app trying to import API keys from local config
from config import DEEPSEEK_API_KEYS  # Doesn't exist in AI_infrastructure/config.py!
```

### ✅ Do: Import correct config
```python
# Good - Tool importing API keys from root
from config import get_api_key_enhanced

# Good - Flask app importing from local config
sys.path.insert(0, os.path.dirname(__file__))
from config import Config
```

## 🧪 Testing & Debugging

### Tool Registry Testing
```powershell
# Load registry and check tool count
python -c "from tools.registry import ToolRegistry; r = ToolRegistry(); print(f'{len(r.tools)} tools loaded')"

# Check for warnings
python -c "from tools.registry import ToolRegistry; ToolRegistry()"
# Should show NO warnings about MICROSOFT_GRAPH_ACCESS_TOKEN
```

### Flask Startup Testing
```powershell
cd C:\Users\gpoli\GIT\AI_agents\AI_infrastructure
$env:PYTHONIOENCODING="utf-8"
python flask_app.py

# Should start on port 5001 with:
# - 564 tools loaded
# - 35 implementations
# - 19 API endpoints
# - No errors or warnings
```

### Credential Injection Testing
```python
# Test Google credentials
from AI_infrastructure.auth.credential_injector import CredentialInjector
injector = CredentialInjector()
creds = injector.get_google_credentials(user_id=1)
print(creds)  # Should show access_token, refresh_token, etc.

# Test Microsoft credentials
creds = injector.get_microsoft_credentials(user_id=1)
print(creds)  # Should show access_token
```

## 🚨 Critical Performance Notes

- **Tool Loading**: 564 tools load in ~2-3 seconds via registry
- **Credential Injection**: Credentials fetched from SQLite on-demand (not at init)
- **API Key Rotation**: Uses round-robin across multiple keys via `get_api_key_enhanced()`
- **Database**: SQLite for user data (`ai_infrastructure.db`) and sessions (`sessions.db`)

## 📚 Documentation Structure

```
docs/
├── archive/          # Archived old documentation (238 files)
├── active/          # Current documentation (21 files)
├── CLEANUP_COMPLETE.md
├── SCRIPT_ORGANIZATION_COMPLETE.md
├── TOOLS_REORGANIZATION_COMPLETE.md
└── IMPORT_FIX_SUMMARY.md
```

## 🔒 Environment Variables

### Required in .env.master
```bash
# AI Provider Keys
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
DEEPSEEK_API_KEY_1=sk-...

# Microsoft OAuth
MICROSOFT_CLIENT_ID=...
MICROSOFT_CLIENT_SECRET=...
MICROSOFT_TENANT_ID=common

# Google OAuth (uses service-account.json)
# No env vars needed for Google - uses service account file

# Database
# Automatically created in AI_infrastructure/data/
```

---

## 💬 Communication Preferences

**User prefers updates in CHAT only, not terminal commands.**

When completing tasks:
- ✅ **DO**: Provide status updates and summaries directly in chat responses
- ❌ **DON'T**: Use `run_in_terminal` with `Write-Host` commands for summaries
- ✅ **DO**: Use terminal only for functional commands (running scripts, checking status, etc.)
- ❌ **DON'T**: Generate colorful PowerShell reports - just explain changes conversationally

---

## 🎯 Quick Reference Checklist

### Before Making Changes:
- [ ] Understand which config file to import (root for tools, AI_infrastructure for Flask)
- [ ] Check if script belongs in `scripts/` or `tools/implementations/`
- [ ] Verify tool implementations use credential injection (not static checks)
- [ ] Test tool loading: `python -c "from tools.registry import ToolRegistry; ToolRegistry()"`
- [ ] Test Flask startup: `cd AI_infrastructure; python flask_app.py`

### After Making Changes:
- [ ] No warnings about MICROSOFT_GRAPH_ACCESS_TOKEN
- [ ] Flask starts successfully on port 5001
- [ ] All 564 tools load without errors
- [ ] Correct config imports (root vs AI_infrastructure)
- [ ] Scripts organized in proper folders

---

**Last Updated:** October 29, 2025  
**Version:** 1.0.0  
**Status:** ✅ Production Ready
