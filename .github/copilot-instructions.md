# GitHub Copilot Instructions - AI Agents Project
**Last Updated: January 5, 2026**

> **⚠️ When generating SVG diagrams:** Always reference `.github/SVG_CAD_GENERATION_RULES.md` for proper title block spacing and Y-coordinate calculations to prevent text overlap.

> **🔒 CRITICAL FILE ENCODING:** All JavaScript, HTML, CSS, and JSON files MUST be saved as **UTF-8 without BOM**. BOM causes production module loading failures. Run `.vscode/fix-bom.ps1` before committing.

---

## Project Overview
Multi-tenant AI agent system with Flask backend, custom HTML/JavaScript frontend, and modular tool architecture. Supports quote calculations, Shopify integration, Xero accounting, document processing, and custom calculator builders. Deployed on Render with Supabase PostgreSQL database.

---

## Project Architecture Map

### **Core Directories (Search Here First)**

**AI_infrastructure/** - Backend core
- `flask_app.py` - Main Flask server, tool registry initialization, WebSocket handlers
- `shared/database_utils.py` - **ALL database operations** - connection pooling, execute_query(), schema management
- `shared/supabase_client.py` - Supabase connection setup
- `migrations/` - Database schema migrations (idempotent SQL)
- `logs/` - Application logs (flask_app.log)
- `tools/audit_connection_leaks.py` - **Database connection audit tool** - scans route files for potential connection leaks

**tools/** - Tool system core
- `registry_v3.py` - Tool discovery, registration, execution (@tool_executor decorator)
- `module_plugin.py` - Auto-discovers modules from UI/modules_external/
- `tool_definitions.py` - Legacy tool definitions (being migrated to modules_external)

**UI/modules_external/** - **Plugin modules** (where most features live)
- `quote-calculator/` - Quote calculation tools (80 tools, 5 domains)
- `shopify/` - Shopify product management
- `xero/` - Xero accounting integration
- Each module has: `tools/*.json` (definitions) + `implementations/*_wrapper.py` (code)

**UI/** - Frontend
- `business-ai-platform-v2.html` - **Main frontend** (single-page application)
- `pages/` - Additional HTML pages
- `fragments/` - Reusable UI components

### **Key Configuration Files**
- `.env` - Environment variables (SUPABASE_URL, API keys, POOL_ENABLED)
- `.vscode/settings.json` - **UTF-8 encoding enforced** (prevents BOM issues)
- `.vscode/fix-bom.ps1` - **BOM removal script** (run before commits)
- `requirements.txt` - Python dependencies (grouped by function)
- `.github/workflows/` - CI/CD deployment to Render
- `tasks.json` - VS Code tasks (BISTART command to start server)

---

## How to Find Things

### **Finding tool implementations:**
1. Search `UI/modules_external/*/tools/*.json` for tool name
2. Find corresponding wrapper in `UI/modules_external/*/implementations/`
3. Check `tools/tool_definitions.py` for legacy tools

### **Finding database schemas:**
1. Search `AI_infrastructure/migrations/*.sql` for CREATE TABLE
2. Check `shared/database_utils.py` for schema creation logic
3. Look for schema name patterns: `customer_{customer_id}`, `user_{user_id}`

### **Finding API integrations:**
- Shopify: `UI/modules_external/shopify/`
- Xero: `UI/modules_external/xero/`
- OpenAI/Anthropic: `AI_infrastructure/shared/` (API clients)

### **Finding UI components:**
- Main app: `UI/business-ai-platform-v2.html`
- Pages: `UI/pages/*.html`
- Fragments: `UI/fragments/`
- Quote calculator UI: `UI/modules_external/quote-calculator/ui/`

### **Generating CAD/SVG diagrams:**
- **ALWAYS follow:** `.github/SVG_CAD_GENERATION_RULES.md`
- Key rules: Title blocks need 40-60px clearance, text Y-position = block top + (font × 1.2)
- Templates available for schematics (1200×900px) and blueprints (1400×1100px)

---

## Critical Patterns

### **Database Operations (ALWAYS use these)**
```python
from AI_infrastructure.shared.database_utils import execute_query

# Read operation
rows = execute_query(
    "SELECT * FROM table WHERE id = %s", 
    (id,), 
    fetch_mode='all'  # or 'one', 'value'
)

# Write operation (auto-uses transaction mode)
execute_query(
    "INSERT INTO table (col) VALUES (%s)", 
    (value,)
)

# Schema creation (with error handling)
try:
    execute_query(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")
except Exception as e:
    # Rollback happens automatically
    logger.warning(f"Schema creation failed: {e}")
```

### **Tool Registration (Module Plugin System)**
```python
# In UI/modules_external/my-module/implementations/my_wrapper.py
from tools.registry_v3 import tool_executor

@tool_executor()
def my_tool_name(param1: str, param2: int = 10):
    """Description shown to AI agent."""
    # Import inside function to avoid circular imports
    from AI_infrastructure.shared.database_utils import execute_query
    
    result = execute_query("SELECT ...", ())
    return {"success": True, "data": result}
```

### **Module Structure**
```
UI/modules_external/my-module/
├── tools/
│   ├── my_tools.json              # Tool definitions
│   └── my_guide.json              # Guide/documentation tool
├── implementations/
│   └── my_wrapper.py              # Tool implementations
├── docs/
│   └── README.md                  # Module documentation
└── ui/                            # Optional UI components
    └── my_module_ui.html
```

---

## Tech Stack Reference

### **Backend**
- **Flask 3.0.0** - REST API & WebSocket server
- **Flask-SocketIO** - Real-time WebSocket communication
- **Flask-CORS** - Cross-origin resource sharing
- **psycopg2-binary** - PostgreSQL adapter
- **Supabase** - Hosted PostgreSQL with connection pooling

### **Frontend**
- **business-ai-platform-v2.html** - Single-page application (vanilla HTML/CSS/JS)
- **WebSockets** - Real-time communication with Flask backend
- **No framework** - Pure JavaScript (no React/Vue/Angular)

### **AI/ML**
- **anthropic** - Claude API (primary AI model)
- **openai** - GPT-4 & embeddings
- **openai-whisper** - Voice transcription

### **Data Processing**
- **pandas 2.3.3** - Data manipulation
- **numpy 2.3.3** - Numerical operations
- **asteval 1.0.7** - Safe formula evaluation (for custom calculators)

### **Integrations**
- **xero-python** - Xero accounting API
- **shopify-api** - Shopify e-commerce integration
- **google-api-python-client** - Google services

---

## Common Search Queries

**"How do I add a new tool?"**
→ Look at `UI/modules_external/quote-calculator/implementations/calculator_wrapper.py` as template

**"Database connection issues"**
→ Check `AI_infrastructure/shared/database_utils.py` connection pooling
→ Look at recent migrations in `AI_infrastructure/migrations/`

**"Tool not registering"**
→ Check `tools/module_plugin.py` loading logic
→ Verify JSON schema in `UI/modules_external/*/tools/*.json`
→ Check Flask startup logs for module loading errors

**"Deployment failing on Render"**
→ Check `.github/workflows/deploy.yml`
→ Look at environment variable usage in `shared/supabase_client.py`
→ Review migration idempotency in `migrations/`

**"Circular import errors"**
→ Move imports inside functions (see tool_executor pattern)
→ Check import order in `AI_infrastructure/shared/`

**"Quote calculator not working"**
→ Start at `UI/modules_external/quote-calculator/`
→ Check `implementations/calculator_wrapper.py`
→ Review `backend/query_library.py` (5,958 lines of SQL queries)
→ Check migrations `005_custom_calculators_tables.sql`

**"InHouse Print database tools failing"**
→ Check `UI/modules_external/inhouse-print/implementations/inhouse_wrapper.py`
→ Verify credentials in Supabase table `ai_infrastructure.user_platform_credentials`
→ Check `db_connector.py` has proper Supabase credential fetching (line 42-56)
→ **CRITICAL FIX (Jan 5, 2026)**: Bypass ToolUseAgent dependency, use `InHousePrintDB` directly

---

## Testing & Debugging

### **Verify tool registration:**
```python
python -c "from tools.registry_v3 import RegistryV3; r = RegistryV3(); print(f'Total: {len(r.tools)}'); print(list(r.tools.keys())[:10])"
```

### **Check database connection:**
```python
python -c "from AI_infrastructure.shared.database_utils import execute_query; print(execute_query('SELECT version()', fetch_mode='value'))"
```

### **View recent logs:**
```powershell
Get-Content AI_infrastructure/flask_app.log -Tail 50
```

### **Test migration idempotency:**
```bash
python AI_infrastructure/migrations/run_my_migration.py
# Should run twice without errors
```

### **Audit database connections:**
```powershell
python AI_infrastructure/tools/audit_connection_leaks.py
# Scans all route files for missing conn.close() or context managers
# Note: Flags "No finally block" but context managers (with statements) are safe
```

### **Test InHouse Print database access:**
```python
# Verify credentials are in Supabase
python -c "from AI_infrastructure.shared.database_utils import execute_query; print(execute_query('SELECT platform, connection_string FROM ai_infrastructure.user_platform_credentials WHERE user_id=1', fetch_mode='all'))"

# Test SQL execution (requires Flask server running)
# Use inhouse_execute_sql tool via AI agent or test db_connector directly:
python -c "from UI.modules_external.inhouse-print.db_connector import InHousePrintDB; db = InHousePrintDB(); print(db.execute_query('SELECT TOP 5 * FROM JobTickets'))"
```

---

## Development Workflow

1. **Feature branch:** Work on `v10` (main development branch)
2. **Pre-commit checks:** Automatic security scan + code quality validation
3. **Commit format:** `feat(scope): description` (conventional commits required)
4. **Push to Render:** Auto-deploys on push to `v10` branch
5. **Migrations:** Run locally first, test idempotency, then deploy

---

## Emergency Patterns

### **"Server crashed, need to restart Flask"**
```powershell
Stop-Process -Name python -Force
cd AI_infrastructure
python flask_app.py
```

### **"Database schema corrupted"**
→ Look in `migrations/` for CREATE statements
→ Check `database_utils.py` for schema creation with IF NOT EXISTS

### **"Tool execution failing"**
→ Check `tools/registry_v3.py` error handling
→ Review `@tool_executor()` decorator implementation
→ Check Flask logs for stack traces

---

## Important Constraints

### **DO:**
- ✅ Always use `execute_query()` from database_utils
- ✅ Add error handling with try/except and rollback for schema operations
- ✅ Use connection pooling (POOL_ENABLED=True in .env)
- ✅ Import heavy modules inside functions to avoid circular imports
- ✅ Add comprehensive logging with `[COMPONENT]` prefixes
- ✅ Use conventional commits format: `feat(scope): description`
- ✅ Add IF NOT EXISTS to all migrations
- ✅ Add CASCADE to foreign keys for clean deletions
- ✅ **Save all .js/.html/.css/.json files as UTF-8 without BOM**
- ✅ **Run `.vscode/fix-bom.ps1` before committing changes**
- ✅ **Verify no emoji corruption in column titles or string literals**

### **DON'T:**
- ❌ Never create raw `psycopg2.connect()` connections
- ❌ Never hardcode connection strings (use environment variables)
- ❌ Never commit without running pre-commit checks
- ❌ Never use synchronous operations in async contexts
- ❌ Never skip idempotent checks (IF NOT EXISTS) in migrations
- ❌ Never import database_utils at module level in tools (circular imports)
- ❌ **Never save files with UTF-8 BOM encoding (breaks ES6 modules)**
- ❌ **Never use emoji characters in code without verifying UTF-8 encoding**
- ❌ **Never bypass `.vscode/fix-bom.ps1` when editing .js files**

---

## Module Plugin System Details

### **Tool Definition JSON Schema**
```json
{
  "name": "my_tool_name",
  "description": "What the tool does (shown to AI agent)",
  "parameters": {
    "type": "object",
    "properties": {
      "param1": {
        "type": "string",
        "description": "Parameter description"
      }
    },
    "required": ["param1"]
  },
  "platform": "my_module"
}
```

### **Tool Implementation Pattern**
```python
from tools.registry_v3 import tool_executor

@tool_executor()
def my_tool_name(param1: str, param2: int = 10):
    """
    Tool description for AI agent.
    
    Args:
        param1: First parameter
        param2: Second parameter with default
        
    Returns:
        dict: {"success": bool, "data": any, "error": str}
    """
    try:
        from AI_infrastructure.shared.database_utils import execute_query
        
        result = execute_query(
            "SELECT * FROM table WHERE col = %s",
            (param1,),
            fetch_mode='all'
        )
        
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
```

---

## Environment Variables Reference

Required in `.env` file:

```bash
# Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_DB_PASSWORD=your-db-password
POOL_ENABLED=True

# AI APIs
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...

# Integrations
XERO_CLIENT_ID=...
XERO_CLIENT_SECRET=...
SHOPIFY_API_KEY=...
SHOPIFY_API_SECRET=...

# Google Services
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json
```

---

## Pre-Commit Hooks

**Security Scan:**
- Secrets detection (API keys, passwords, tokens)
- Vulnerability scanning in dependencies
- Hardcoded credentials check

**Code Quality:**
- Unused imports detection
- Missing docstrings warning
- Code style consistency

**Encoding Validation:**
- ✅ **Run `.vscode/fix-bom.ps1`** to remove BOM from all files
- ✅ Verify no emoji corruption in JavaScript files
- ✅ Check VS Code settings enforce UTF-8 without BOM

**Commit Message Validation:**
- Conventional commits format required
- Valid types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`, `build`, `ci`, `revert`
- Format: `type(scope): description`

---

## Quick Reference Commands

### **Start Flask Server**
```powershell
cd AI_infrastructure
python flask_app.py
```

### **Fix File Encoding Issues (CRITICAL)**
```powershell
# Remove BOM from all JS/HTML/CSS/JSON files
.\.vscode\fix-bom.ps1

# Check specific file for BOM
$bytes = Get-Content "path/to/file.js" -Encoding Byte -TotalCount 3
if ($bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
    Write-Host "BOM DETECTED" -ForegroundColor Red
} else {
    Write-Host "No BOM" -ForegroundColor Green
}
```

### **Run Migration**
```powershell
cd AI_infrastructure/migrations
python run_my_migration.py
```

### **Check Tool Registry**
```python
from tools.registry_v3 import RegistryV3
r = RegistryV3()
print(f"Total tools: {len(r.tools)}")
print(r.tools.keys())
```

### **Test Database Connection**
```python
from AI_infrastructure.shared.database_utils import execute_query
version = execute_query("SELECT version()", fetch_mode='value')
print(version)
```

### **View Logs**
```powershell
Get-Content AI_infrastructure/flask_app.log -Tail 50 -Wait
```

---

## File Encoding Rules (CRITICAL FOR PRODUCTION)

### **Why UTF-8 without BOM Matters**

**BOM (Byte Order Mark)** = `EF BB BF` hex bytes at file start
- ❌ **BREAKS** ES6 module imports in production
- ❌ **BREAKS** JavaScript parsing in browsers
- ❌ **BREAKS** build tools and minifiers
- ✅ **SAFE** UTF-8 without BOM works everywhere

**Production Failure Example:**
```javascript
// File with BOM (invisible in editor):
[EF BB BF]export default { name: 'Module' };

// Browser error:
Uncaught SyntaxError: Unexpected token '﻿'
// Module fails to load silently
```

### **VS Code Settings (Already Configured)**

`.vscode/settings.json` enforces UTF-8 without BOM:
```json
{
    "files.encoding": "utf8",
    "files.autoGuessEncoding": false,
    "[javascript]": { "files.encoding": "utf8" },
    "[html]": { "files.encoding": "utf8" },
    "[css]": { "files.encoding": "utf8" },
    "[json]": { "files.encoding": "utf8" }
}
```

### **Pre-Commit Workflow**

```powershell
# 1. Fix any BOM issues
.\.vscode\fix-bom.ps1

# 2. Verify clean
# Output should show: "Files fixed: 0" (all clean)

# 3. Commit safely
git add -A
git commit -m "feat(module): description"
git push
```

### **Emoji Character Safety**

When using emoji in code:
```javascript
// ❌ UNSAFE (can corrupt with BOM):
title: "💬"  // May render as � in production

// ✅ SAFE (use text labels):
title: "Messages"
tooltip: "💬 Messages in conversation"  // OK in tooltip/title attributes
```

---

## Troubleshooting: InHouse Print Database Access (Jan 5, 2026)

### **Problem: "ToolUseAgent could not be imported" Error**

**Symptoms:**
- `inhouse_execute_sql` tool fails with import error
- Error message: "ToolUseAgent could not be imported - check backend path and dependencies"
- Credentials ARE properly stored in Supabase table `ai_infrastructure.user_platform_credentials`

**Root Cause:**
- `inhouse_wrapper.py` tried to initialize `ToolUseAgent` from `quote-calculator/backend/tool_use_agent.py`
- `tool_use_agent.py` line 69-71 imports `complete_calculator_implementation`
- This file doesn't exist in AI_agents project (only in external In_House_SQL project)
- Import fails → `ToolUseAgent = None` → raises error when SQL tool tries to use it

**Solution Applied (Jan 5, 2026):**

Modified `UI/modules_external/inhouse-print/implementations/inhouse_wrapper.py` line 201:

```python
def inhouse_execute_sql(query: str, **kwargs) -> List[Dict[str, Any]]:
    """Execute SQL query against InHouse Print database (Fred)"""
    # ✅ FIX: Bypass ToolUseAgent and use InHousePrintDB directly
    try:
        from db_connector import InHousePrintDB
        
        # Initialize DB connection (auto-detects Supabase vs local config)
        db = InHousePrintDB()
        
        # Execute query and return results as list of dicts
        results = db.execute_query(query)
        
        if results is None:
            return []
        
        # Convert DataFrame to list of dicts if needed
        if hasattr(results, 'to_dict'):
            return results.to_dict('records')
        
        return results
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        raise RuntimeError(
            f"SQL execution failed: {e}\n"
            f"Query: {query}\n"
            f"Details: {error_details}"
        )
```

**Why This Works:**
1. `InHousePrintDB` class in `db_connector.py` already has Supabase credential fetching (line 42-56)
2. Auto-detects Render environment vs local development
3. No dependency on ToolUseAgent or calculator implementations
4. Direct SQL execution with proper error handling

**Testing:**
```python
# Test credential fetching
from AI_infrastructure.shared.database_utils import execute_query
creds = execute_query(
    "SELECT platform, connection_string FROM ai_infrastructure.user_platform_credentials WHERE user_id=1",
    fetch_mode='all'
)
print(creds)

# Test SQL execution via db_connector
from UI.modules_external.inhouse-print.db_connector import InHousePrintDB
db = InHousePrintDB()
results = db.execute_query("SELECT TOP 5 * FROM JobTickets ORDER BY DateCreated DESC")
print(results)
```

**Key Lessons:**
- ToolUseAgent was unnecessary dependency for simple SQL execution
- `db_connector.py` already had all needed functionality
- Bypass complex import chains when simpler solution exists
- Always verify credentials are in Supabase before debugging connection logic

---

**Remember:** 
1. This is a modular plugin-based architecture - add features as modules in `UI/modules_external/`
2. **Always save files as UTF-8 without BOM** - run `.vscode/fix-bom.ps1` before commits
3. Use Registry V3 pattern for tool definitions and implementations
4. Test locally before deploying to Render (v10 branch auto-deploys)

**Production Checklist:**
- [ ] Run `.vscode/fix-bom.ps1` to verify encoding
- [ ] Check no emoji corruption in JavaScript files  
- [ ] Verify no console errors in browser DevTools
- [ ] Test module loading in production URL
- [ ] Monitor Render deployment logs
