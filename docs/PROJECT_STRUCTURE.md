# AI_agents Project Structure

## Overview

This document describes the reorganized folder structure of the AI_agents platform.

Last Updated: October 29, 2025  
Version: 2.0.0  
Status: Production

---

## Root Directory

```
AI_agents/
├── BISTART.bat              # Quick startup (wrapper to scripts/startup/)
├── CHAT.bat                 # Quick chat interface (wrapper to scripts/startup/)
├── BISTART.ps1              # Startup shortcut (copy of scripts/startup/BISTART.ps1)
├── chat.ps1                 # Chat shortcut (copy of scripts/startup/chat.ps1)
├── app.py                   # Main entry point (if used)
├── config.py                # Global configuration
├── synergy_backend.py       # Synergy backend service
├── vsa_automation_agent.py  # VSA automation agent
├── README.md                # Main documentation
└── requirements.txt         # Python dependencies
```

**Keep Root Clean:** Only essential entry points and configuration files belong here.

---

## Core Directories

### 1. AI_infrastructure/
**Purpose:** Main Flask application backend

```
AI_infrastructure/
├── flask_app.py            # Main Flask app (port 4000)
├── routes/                 # API endpoints
│   ├── google_auth_routes.py
│   ├── agent_routes.py
│   ├── kanban_routes.py
│   └── ...
├── auth/                   # Authentication modules
├── core/                   # Core business logic
├── tests/                  # Unit tests
├── utils/                  # Utility functions
└── ai_infrastructure.db    # SQLite database
```

**Start Command:** `cd AI_infrastructure; python flask_app.py`

---

### 2. tools/
**Purpose:** Tool registry and platform integrations

```
tools/
├── __init__.py
├── tool_registry.py
└── [platform implementations]
```

**Note:** Platform folders (google_workspace/, Microsoft_365_Connection/) currently in root - to be moved here in future.

---

### 3. UI/
**Purpose:** Frontend HTML files

```
UI/
├── business-ai-platform-v2.html    # Main UI (port 5001)
└── triple_agent.html               # Triple agent interface
```

**Access:** `http://localhost:5001/business-ai-platform-v2.html`

---

### 4. scripts/
**Purpose:** Organized scripts by function (NEW STRUCTURE)

```
scripts/
├── startup/                 # Application startup/shutdown
│   ├── BISTART.ps1         # Main startup script (launches Flask + UI)
│   ├── BISTOP.ps1          # Shutdown script
│   ├── chat.ps1            # Chat interface launcher
│   ├── SYNERGY_START.ps1   # Synergy startup
│   └── SYNERGY_START.bat   # Synergy batch launcher
│
├── setup/                   # Initial setup and configuration
│   ├── setup_microsoft_login.ps1
│   ├── setup_master_account.py
│   └── UPDATE_PROFILE_TO_5001.ps1
│
├── testing/                 # Test and validation scripts
│   ├── test_kanban_integration.py
│   ├── test_oauth_all.py
│   ├── test_task_sync.py
│   ├── test_unified_oauth.py
│   ├── check_db_schema.py
│   ├── check_gmail_tools.py
│   ├── check_routes.py
│   └── table_structure_analysis.py
│
├── maintenance/             # Cleanup and maintenance
│   ├── cleanup_final.ps1
│   ├── execute_phase2_cleanup.ps1
│   └── final_comprehensive_cleanup.ps1
│
├── deployment/              # Deployment scripts
│   └── ai_agent_render_deploy.py
│
└── utilities/               # General utilities
    ├── create_doc_with_chart_images.py
    ├── create_professional_charts.py
    ├── create_professional_charts_with_folder.py
    └── task_sync_universal.py
```

---

### 5. migrations/
**Purpose:** Database migrations and schema updates

```
migrations/
└── run_migration.py
```

---

### 6. docs/
**Purpose:** Documentation organized by topic

```
docs/
├── README.md                           # Documentation index
│
├── features/                           # Feature documentation
│   ├── AGENT_SYSTEM_COMPLETE.md       # Agent orchestration
│   ├── TOOL_PLATFORM_COMPLETE.md      # Tool platform
│   ├── KANBAN_INTEGRATION_COMPLETE.md # Kanban board
│   └── ...
│
├── api/                                # API documentation (to be created)
│   └── API_REFERENCE.md
│
└── archive/                            # Archived documentation
    ├── summaries/         (49 files)
    ├── ai_infrastructure/ (40 files)
    ├── platforms/         (28 files)
    ├── google_workspace/  (28 files)
    ├── ui/                (25 files)
    ├── authentication/    (21 files)
    ├── kanban/            (15 files)
    ├── tools/             (10 files)
    ├── microsoft_365/     (8 files)
    ├── implementations/   (3 files)
    └── scripts/           (7 files - superseded scripts)
```

---

## Platform Folders (Currently in Root)

**Status:** To be moved to `tools/` in future cleanup

```
/ (root)
├── google_workspace/           # Google Workspace integration
├── Microsoft_365_Connection/   # Microsoft 365 integration
├── Cloudflare/                 # Cloudflare integration
├── Supabase/                   # Supabase integration
├── Render_backend/             # Render deployment
└── Woocommerce/                # WooCommerce integration
```

**Future Location:** `tools/[platform_name]/`

---

## Quick Start Commands

### Start the Platform
```powershell
# From anywhere
BISTART

# Or explicitly
.\BISTART.ps1

# Or manually
cd AI_infrastructure
python flask_app.py
```

### Talk to AI Agent
```powershell
# From anywhere
CHAT "What tools are available?"

# Or explicitly
.\chat.ps1 "List my Gmail messages"
```

### Stop Services
```powershell
.\scripts\startup\BISTOP.ps1
```

### Run Tests
```powershell
# Test Kanban integration
python .\scripts\testing\test_kanban_integration.py

# Test OAuth
python .\scripts\testing\test_oauth_all.py

# Check database schema
python .\scripts\testing\check_db_schema.py
```

### Setup Commands
```powershell
# Setup Microsoft login
.\scripts\setup\setup_microsoft_login.ps1

# Setup master account
python .\scripts\setup\setup_master_account.py
```

---

## File Organization Rules

### Root Directory
 **ALLOWED:**
- Entry points (BISTART.bat, CHAT.bat)
- Quick shortcuts (BISTART.ps1, chat.ps1 - copies from scripts/)
- Main app files (app.py, config.py)
- Core services (synergy_backend.py, vsa_automation_agent.py)
- Documentation (README.md)
- Configuration (requirements.txt, .env files)

 **NOT ALLOWED:**
- Test scripts → Move to `scripts/testing/`
- Setup scripts → Move to `scripts/setup/`
- Utility scripts → Move to `scripts/utilities/`
- Old/superseded scripts → Move to `docs/archive/scripts/`

### Scripts Directory
All scripts should be categorized into appropriate subfolders:
- `startup/` - Application lifecycle (start/stop)
- `setup/` - Initial configuration
- `testing/` - Tests and validation
- `maintenance/` - Cleanup and maintenance
- `deployment/` - Deployment scripts
- `utilities/` - General purpose utilities

### Documentation
- Active docs → `docs/` or `docs/features/`
- Archived docs → `docs/archive/[category]/`
- Follow `_COMPLETE.md` pattern for feature docs

---

## Migration Status

### Phase 1: Documentation Consolidation 
- Created 4 comprehensive `_COMPLETE.md` files
- Total: 5,650+ lines of consolidated documentation
- Status: Complete

### Phase 2: Initial Cleanup 
- Archived 135 scattered documentation files
- Removed superseded BISTART update scripts
- Status: Complete

### Phase 3: Comprehensive Cleanup 
- Removed backup folders
- Archived 103 additional documentation files
- Total reduction: 93% (301 → 21 active docs)
- Status: Complete

### Phase 4: Script Organization 
- Created `scripts/` folder structure
- Moved 32 scripts to organized locations
- Archived 7 superseded scripts
- Status: Complete (October 29, 2025)

### Phase 5: Platform Consolidation (Future)
**Pending:** Move platform folders to `tools/`
- google_workspace/ → tools/google_workspace/
- Microsoft_365_Connection/ → tools/microsoft_365/
- Cloudflare/ → tools/cloudflare/
- Supabase/ → tools/supabase/
- Render_backend/ → tools/render/
- Woocommerce/ → tools/woocommerce/

### Phase 6: API Documentation (Future)
**Pending:** Create comprehensive API reference
- Document all Flask endpoints
- Request/response examples
- Authentication requirements

---

## Maintenance Guidelines

### Weekly
- Check root directory for new scattered scripts
- Move any test/utility scripts to appropriate `scripts/` folders

### Monthly
- Review `docs/archive/` organization
- Verify shortcuts in root still work
- Update this structure document

### Quarterly
- Audit platform folder locations
- Review script organization
- Update version numbers

---

## Version History

**v2.0.0** (October 29, 2025)
- Created `scripts/` folder structure
- Organized all root scripts into categories
- Archived superseded scripts
- Reduced root clutter: 40+ files → 9 essential files

**v1.0.0** (October 24, 2025)
- Initial documentation consolidation
- Created archive system
- Reduced documentation: 301 → 21 active files

---

## Support

For questions about project structure:
1. Check `docs/README.md` for documentation index
2. Review `docs/features/` for feature-specific guides
3. Check `scripts/` for available automation

For platform details:
- Agent System: `docs/features/AGENT_SYSTEM_COMPLETE.md`
- Tool Platform: `docs/features/TOOL_PLATFORM_COMPLETE.md`
- Kanban Integration: `docs/features/KANBAN_INTEGRATION_COMPLETE.md`
