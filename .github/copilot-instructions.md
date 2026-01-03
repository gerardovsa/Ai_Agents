# GitHub Copilot Instructions - AI Agents Project
**Last Updated: December 29, 2025**

> **⚠️ When generating SVG diagrams:** Always reference `.github/SVG_CAD_GENERATION_RULES.md` for proper title block spacing and Y-coordinate calculations to prevent text overlap.

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

### **DON'T:**
- ❌ Never create raw `psycopg2.connect()` connections
- ❌ Never hardcode connection strings (use environment variables)
- ❌ Never commit without running pre-commit checks
- ❌ Never use synchronous operations in async contexts
- ❌ Never skip idempotent checks (IF NOT EXISTS) in migrations
- ❌ Never import database_utils at module level in tools (circular imports)

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

**Remember:** This is a modular plugin-based architecture. New features should be added as modules in `UI/modules_external/` with proper tool definitions and implementations following the Registry V3 pattern.
