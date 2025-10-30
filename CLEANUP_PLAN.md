# AI_agents Folder Cleanup Plan

## Files to Delete

### Root Level - Redundant Documentation
- ❌ `ARCHITECTURE_ANALYSIS_COMPLETE.md` - Outdated architecture notes
- ❌ `CLEANUP_COMPLETE.md` - Old cleanup notes
- ❌ `CLEANUP_PHASE1_COMPLETE.md` - Old cleanup notes
- ❌ `FINAL_CLEANUP_SUMMARY.md` - Old cleanup notes
- ❌ `IMPORT_FIX_SUMMARY.md` - Outdated fix notes
- ❌ `PHASE2_COMPLETE_SUMMARY.md` - Old phase notes
- ❌ `PHASE2_EXECUTION_PLAN.md` - Old phase notes
- ❌ `SCRIPT_ORGANIZATION_COMPLETE.md` - Already documented in Render_backend/README.md
- ❌ `TOOLS_REORGANIZATION_COMPLETE.md` - Outdated tool notes
- ❌ `COMPLETE_AI_TOOL_FLOW_EXPLANATION.md` - Redundant with current code
- ❌ `MICROSOFT_365_SETUP.md` - Outdated setup docs
- ❌ `MICROSOFT_CREDENTIALS_FIX_COMPLETE.md` - Old fix notes
- ❌ `MICROSOFT_MULTITENANT_FIX.md` - Old fix notes
- ❌ `RENDER_DEPLOYMENT_GUIDE.md` - Superseded by Render_backend/DEPLOYMENT_GUIDE_FOR_AI.md
- ❌ `verify_azure_app.md` - Old verification notes

### Root Level - Redundant Scripts
- ❌ `app.py` - LEGACY Flask app (superseded by AI_infrastructure/flask_app.py)
- ❌ `deploy_to_render.py` - Duplicate of deploy_to_render_api.py
- ❌ `get_render_logs.py` - Superseded by Render_backend/fetch_logs.py
- ❌ `check_flask_env.py` - Testing script no longer needed
- ❌ `check_microsoft_creds.py` - Testing script no longer needed
- ❌ `check_database_schema.py` - Testing script (move to scripts/testing if needed)
- ❌ `count_priority_tools.py` - One-time analysis script
- ❌ `create_test_users.py` - Testing script (move to scripts/testing if needed)
- ❌ `diagnose_m365_oauth.py` - Diagnostic script no longer needed
- ❌ `find_user_db.py` - Diagnostic script
- ❌ `fix_azure_multitenant.py` - One-time fix script
- ❌ `fix_render_deployment.py` - Superseded by Render_backend scripts
- ❌ `get_auth_token.py` - Testing script
- ❌ `initialize_database.py` - One-time setup script (already done)
- ❌ `organize_scripts.ps1` - One-time organization script
- ❌ `simple_tool_test.py` - Testing script
- ❌ `test_*.py` (18 files) - Move to scripts/testing/
- ❌ `update_microsoft_secret.ps1` - One-time update script
- ❌ `vsa_automation_agent.py` - Unused automation script

### Root Level - Redundant Config Files
- ❌ `.env copy.master` - Backup file (not needed in repo)
- ❌ `.env.development` - Not used
- ❌ `BISTART_NEW_VERSION.txt` - Text file superseded by actual scripts
- ❌ `test_credentials_m365.txt` - Test credentials file

### Root Level - Redundant Token Files
- ❌ `credentials_desktop.json` - Should not be in repo
- ❌ `credentials_web.json` - Should not be in repo
- ❌ `token_*.json` (6 files) - Should not be in repo
- ❌ `google-auth.js` - Should not be in repo (has embedded credentials)
- ❌ `service-account.json` - Should not be in repo
- ❌ `vsa-anythingllm-project-*.json` - Should not be in repo

### Docs - Archive (Keep, but confirm no active usage)
- ✅ Keep `docs/archive/` (246 files) - Historical reference

### Docs - Redundant Root Documentation
- ❌ `docs/COMPLETE_AUTH_FLOW.md` - Outdated auth flow
- ❌ `docs/SYNERGY_*` (4 files) - Synergy project moved to separate repo/deprecated

## Files to Keep

### Root Level - Essential
- ✅ `BISTART.bat` / `BISTART.ps1` - Server startup (PATH command)
- ✅ `CHAT.bat` / `chat.ps1` - AI CLI (PATH command)
- ✅ `CHATM.bat` / `CHATM.ps1` - Multi-line chat variant
- ✅ `config.py` - Global API keys
- ✅ `config.example.py` - Example config
- ✅ `.env.example` - Example environment file
- ✅ `.env.master` - Actual environment file (in .gitignore)
- ✅ `requirements.txt` - Python dependencies
- ✅ `runtime.txt` - Python version for Render
- ✅ `render.yaml` - Render deployment config
- ✅ `README.md` - Main project documentation
- ✅ `docker-compose.yml` - Docker setup

### Root Level - Current Deployment Scripts
- ✅ `deploy_to_render_api.py` - API deployment (referenced by Render_backend)
- ✅ `check_render_service.py` - Service status checker
- ✅ `check_users.py` - User management
- ✅ `check_users_and_credentials.py` - Credential verification

### Root Level - Active Documentation
- ✅ `CALCULATOR_INTEGRATION_COMPLETE.md` - Recent calculator integration
- ✅ `CALCULATOR_QUICK_START.md` - Calculator quick reference
- ✅ `UNIVERSAL_CONTENT_BLOCKS_COMPLETE.md` - Current content system
- ✅ `UNIVERSAL_CONTENT_BLOCKS_QUICK_START.md` - Content system guide

### Folders - Essential
- ✅ `AI_infrastructure/` - Main Flask application
- ✅ `tools/` - 564 tool implementations
- ✅ `Render_backend/` - Deployment toolkit (just created)
- ✅ `scripts/` - Organized utility scripts
- ✅ `docs/` - Documentation (keep active docs, archive old)
- ✅ `google_workspace/` - Google integrations
- ✅ `Microsoft_365_Connection/` - Microsoft integrations
- ✅ `routes/` - Legacy routes (check if still used)
- ✅ `templates/` - HTML templates
- ✅ `UI/` - UI assets
- ✅ `data/` - Database files
- ✅ `.github/` - GitHub configuration

## Execution Steps

1. Delete redundant documentation (15 files)
2. Delete redundant scripts (30+ files)
3. Delete redundant config files (4 files)
4. Delete sensitive files that shouldn't be in repo (10+ files)
5. Update .gitignore to prevent future issues
6. Move active test scripts to scripts/testing/
7. Update README.md with clean structure
8. Create MIGRATION_NOTES.md for reference

## Post-Cleanup Structure

```
AI_agents/
├── 📖 README.md
├── 📖 CALCULATOR_INTEGRATION_COMPLETE.md
├── 📖 CALCULATOR_QUICK_START.md
├── 📖 UNIVERSAL_CONTENT_BLOCKS_*.md
├── 🔧 config.py (in .gitignore)
├── 🔧 config.example.py
├── 🔧 requirements.txt
├── 🔧 runtime.txt
├── 🔧 render.yaml
├── 🚀 BISTART.bat/ps1
├── 🚀 CHAT.bat/ps1
├── 🚀 deploy_to_render_api.py
├── 🚀 check_render_service.py
├── 🚀 check_users*.py
├── 📁 AI_infrastructure/
├── 📁 tools/
├── 📁 Render_backend/
├── 📁 scripts/
├── 📁 docs/
├── 📁 google_workspace/
├── 📁 Microsoft_365_Connection/
└── 📁 data/
```

Clean, organized, and ready for production deployment!
