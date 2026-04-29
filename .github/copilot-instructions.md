# GitHub Copilot Instructions - AI Agents Project
**Last Updated: March 26, 2026**

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

### **Finding Org / Platform / Module system:**
- Routes: `AI_infrastructure/routes/organisation_credentials_routes.py`
- Catalog migration: `AI_infrastructure/migrations/036_platform_module_catalog.sql`
- Encryption: `AI_infrastructure/shared/credential_crypto.py`
- Frontend org panel: search for `OrgManager` in `UI/business-ai-platform-v2.html`
- See full section: **Org, Team, Roles, Platform Catalog & Module System** (below)

### **Finding Sidebar / Dashboard / Module Visibility:**
- Full architecture doc: `.github/MODULE_VISIBILITY_ARCHITECTURE.md`
- Sidebar HTML zones: `UI/business-ai-platform-v2.html` lines ~18571–18660
- Dynamic module section: `#sidebarModulesSection` (line ~18632)
- Static module loader (to be replaced): `UI/modules_external/manifest.json`
- Module show/hide function design: see `initModulesFromOrg()` in the architecture doc
- **⚠️ WooCommerce tab (`tab-sales`) is HARDCODED — always visible, needs to be gated**
- DB module toggles DO NOT currently affect sidebar — gap documented in architecture doc

---

## Org, Team, Roles, Platform Catalog & Module System
**Implemented: March 2026 — Migration 036**

This section documents the complete multi-tenant organisation system: org structure, role-based access, credential vault, extensible platform catalog, and per-org module management. This is the authoritative technical reference for any developer working on org features.

---

### Architecture Overview

```
Organisations
  └── Members (users with roles: viewer/member/manager/admin/owner)
  └── Credentials Vault (encrypted API keys, OAuth tokens, DB strings)
        └── Validated against → platform_catalog (DB-driven, extensible)
  └── Module Access (enabled/disabled per org)
        └── Defined in → module_catalog (DB-driven, plan-tiered)
```

**Key principle:** Adding a new platform or module requires only a DB `INSERT` — zero code changes.

---

### Role Hierarchy

| Role | Level | Key Permissions |
|------|-------|-----------------|
| `viewer` | 1 | No credential access (403 on vault) |
| `member` | 2 | Read org info, view platform/module catalog |
| `manager` | 3 | + List credentials (masked), view audit log |
| `admin` | 4 | + Add/edit/delete credentials, toggle modules, invite members |
| `owner` | 5 | + Reveal secrets, vault password, remove members, change roles |

**JWT Invalidation:** When a user's role changes, their `jwt_version` is incremented in `ai_infrastructure.users`. Every request validates `g.jwt_version_valid` via the `@require_auth` middleware — stale tokens are rejected with `"Session expired due to a permission change"`.

**Vault Password:** Optional per-org `bcrypt` hash stored on the `organisations` row. If set, revealing any credential requires the vault password in addition to admin+ role.

---

### Database Tables

All tables live in the `ai_infrastructure` PostgreSQL schema.

#### `ai_infrastructure.organisations`
| Column | Type | Notes |
|--------|------|-------|
| `id` | SERIAL PK | |
| `name` | VARCHAR(255) | Unique, URL-safe slug |
| `slug` | VARCHAR(100) | URL identifier |
| `plan_tier` | VARCHAR(50) | `free` / `starter` / `professional` / `enterprise` |
| `display_name` | VARCHAR(255) | Shown in UI |
| `logo_url` | TEXT | |
| `timezone` | VARCHAR(100) | |
| `country_code` | VARCHAR(10) | |
| `is_active` | BOOLEAN | |
| `description` | TEXT | |
| `visibility` | VARCHAR(50) | |
| `allowed_domains` | TEXT[] | Restrict invite by email domain |
| `ai_provider` | VARCHAR(50) | Default AI model provider |
| `ai_model` | VARCHAR(100) | |
| `ai_max_tokens` | INTEGER | |
| `vault_password_hash` | TEXT | bcrypt hash; NULL = no vault lock |
| `created_at` | TIMESTAMPTZ | |
| `updated_at` | TIMESTAMPTZ | |

#### `ai_infrastructure.users` (org-relevant columns)
| Column | Type | Notes |
|--------|------|-------|
| `organisation_id` | INT | FK to organisations.id |
| `org_role` | VARCHAR(50) | `viewer`/`member`/`manager`/`admin`/`owner` |
| `jwt_version` | INT | Incremented on role change to invalidate tokens |
| `last_login` | TIMESTAMPTZ | |

#### `ai_infrastructure.organisation_platform_credentials`
| Column | Type | Notes |
|--------|------|-------|
| `id` | SERIAL PK | |
| `organisation_id` | INT | FK to organisations |
| `platform` | VARCHAR(100) | e.g. `shopify`, `anthropic`; validated against `platform_catalog` |
| `display_name` | VARCHAR(255) | User-defined label (e.g. "Production Shopify") |
| `environment` | VARCHAR(50) | e.g. `production`, `staging` |
| `credential_value` | TEXT | **Encrypted** single secret. Prefix `enc:v1:` marks encrypted values |
| `credentials` | TEXT (JSON) | **Encrypted** multi-field dict e.g. `{"api_key":"...","shop_url":"..."}` |
| `visible_to_role` | VARCHAR(50) | Min role to list (default `manager`) |
| `reveal_requires_role` | VARCHAR(50) | Min role to reveal plaintext (default `admin`) |
| `expires_at` | TIMESTAMPTZ | Optional expiry |
| `rotation_due_at` | TIMESTAMPTZ | Optional rotation reminder |
| `last_used_at` | TIMESTAMPTZ | Updated on reveal/test |
| `is_active` | BOOLEAN | FALSE = soft-deleted |
| `created_by_user_id` | INT | FK to users.id |
| `created_at` | TIMESTAMPTZ | |
| `updated_at` | TIMESTAMPTZ | |

#### `ai_infrastructure.credential_access_log`
| Column | Type | Notes |
|--------|------|-------|
| `id` | SERIAL PK | |
| `organisation_id` | INT | |
| `credential_id` | INT | |
| `user_id` | INT | |
| `action` | VARCHAR | `list`, `add`, `edit`, `delete`, `reveal`, `test` |
| `platform` | VARCHAR(100) | |
| `display_name` | VARCHAR(255) | |
| `ip_address` | VARCHAR(45) | |
| `user_agent` | TEXT | |
| `vault_password_used` | BOOLEAN | |
| `performed_at` | TIMESTAMPTZ | |

#### `ai_infrastructure.org_invitations`
| Column | Type | Notes |
|--------|------|-------|
| `id` | SERIAL PK | |
| `organisation_id` | INT | |
| `invited_email` | VARCHAR(255) | Optional — nullable |
| `invited_role` | VARCHAR(50) | Role assigned on accept |
| `status` | VARCHAR | `pending` / `accepted` / `expired` / `revoked` |
| `invite_token` | UUID | Shared via email link |
| `expires_at` | TIMESTAMPTZ | |
| `created_at` | TIMESTAMPTZ | |
| `invited_by` | INT | FK to users.id |
| `accepted_at` | TIMESTAMPTZ | |
| `accepted_by` | INT | FK to users.id |

---

### Platform Catalog Tables (Migration 036 — March 2026)

#### `ai_infrastructure.platform_catalog`
| Column | Type | Notes |
|--------|------|-------|
| `platform_name` | VARCHAR(100) PK | Snake-case key e.g. `shopify`, `anthropic` |
| `display_name` | VARCHAR(255) | Human label e.g. `"Shopify"` |
| `icon_class` | VARCHAR(100) | FontAwesome class e.g. `"fab fa-shopify"` |
| `icon_color` | VARCHAR(20) | Hex color e.g. `"#96bf48"` |
| `category` | VARCHAR(50) | See **Platform Categories** below |
| `auth_type` | VARCHAR(50) | `api_key` / `oauth2` / `multi_field` / `connection_string` |
| `required_fields` | JSONB | Array of field descriptors — drives the credential form |
| `description` | TEXT | Short description |
| `docs_url` | TEXT | Link to vendor docs |
| `is_active` | BOOLEAN | Default TRUE; set FALSE to hide without deleting |
| `sort_order` | INTEGER | Sort within category; lower = first |
| `created_at` | TIMESTAMPTZ | |

**`required_fields` JSONB schema** (each element):
```json
{
  "name": "api_key",           // HTML id="dyn-field-api_key"
  "label": "API Key",          // Label text shown in form
  "type": "password",          // input type: text|password|select|textarea
  "placeholder": "sk-ant-...", // Placeholder text
  "required": true,            // Whether field is required
  "help_text": "Found in..."   // Small hint text below input
}
```
> The **first element** in `required_fields` maps to the existing `apiKeyValue` input and `apiKeyLabel` label. All subsequent elements are rendered dynamically with IDs `dyn-field-{name}` by `showApiKeyForm()` in the frontend.

**`auth_type` Behaviour:**
- `api_key` — Single secret field shown
- `multi_field` — All `required_fields` rendered (index 0 uses main input, 1+ use `dyn-field-*`)
- `oauth2` — Client ID + Secret fields; indicates OAuth flow
- `connection_string` — Single connection URL field

**Platform Categories:**
| Category | Platforms |
|----------|-----------|
| `ai` | anthropic, openai, deepseek, assemblyai |
| `vector_db` | pinecone, voyager |
| `ecommerce` | shopify, woocommerce |
| `accounting` | xero, stripe, paypal |
| `communication` | sendgrid, twilio, hunter |
| `shipping` | auspost |
| `team` | google, microsoft, gmail_oauth, outlook_oauth, kajabi |
| `database` | supabase, supabase_vsa, sql_database, inhouseprint_sql |
| `hosting` | render, cloudflare |

**All 27 Seeded Platforms (Migration 036):**

| platform_name | display_name | auth_type | category | sort_order |
|--------------|--------------|-----------|----------|------------|
| `anthropic` | Anthropic Claude | api_key | ai | 10 |
| `openai` | OpenAI | api_key | ai | 11 |
| `deepseek` | DeepSeek | api_key | ai | 12 |
| `assemblyai` | AssemblyAI | api_key | ai | 13 |
| `pinecone` | Pinecone | api_key | vector_db | 20 |
| `voyager` | Voyager AI | api_key | vector_db | 21 |
| `shopify` | Shopify | api_key | ecommerce | 30 |
| `woocommerce` | WooCommerce | multi_field | ecommerce | 31 |
| `xero` | Xero | oauth2 | accounting | 40 |
| `stripe` | Stripe | api_key | accounting | 41 |
| `paypal` | PayPal | multi_field | accounting | 42 |
| `sendgrid` | SendGrid | api_key | communication | 50 |
| `twilio` | Twilio | multi_field | communication | 51 |
| `hunter` | Hunter.io | api_key | communication | 52 |
| `auspost` | Australia Post | api_key | shipping | 60 |
| `google` | Google Workspace | oauth2 | team | 70 |
| `microsoft` | Microsoft 365 | oauth2 | team | 71 |
| `gmail_oauth` | Gmail OAuth | oauth2 | team | 72 |
| `outlook_oauth` | Outlook OAuth | oauth2 | team | 73 |
| `kajabi` | Kajabi | api_key | team | 74 |
| `supabase` | Supabase | multi_field | database | 80 |
| `supabase_vsa` | Supabase (VSA) | multi_field | database | 81 |
| `sql_database` | SQL Database | connection_string | database | 82 |
| `inhouseprint_sql` | InHousePrint SQL | connection_string | database | 83 |
| `render` | Render | api_key | hosting | 90 |
| `cloudflare` | Cloudflare | multi_field | hosting | 91 |

---

#### `ai_infrastructure.module_catalog`
| Column | Type | Notes |
|--------|------|-------|
| `module_name` | VARCHAR(100) PK | Snake-case key e.g. `shopify`, `core_chat` |
| `display_name` | VARCHAR(255) | Human label |
| `description` | TEXT | Shown in module catalog UI |
| `icon_class` | VARCHAR(100) | FontAwesome class |
| `icon_color` | VARCHAR(20) | Hex color |
| `category` | VARCHAR(50) | e.g. `core`, `ecommerce`, `finance`, `ai`, `operations`, `dev` |
| `min_plan_tier` | VARCHAR(50) | `free` / `starter` / `professional` / `enterprise` |
| `required_platforms` | TEXT[] | e.g. `ARRAY['shopify']` — platform credentials needed |
| `is_active` | BOOLEAN | Default TRUE |
| `sort_order` | INTEGER | |
| `created_at` | TIMESTAMPTZ | |

#### `ai_infrastructure.org_module_access`
| Column | Type | Notes |
|--------|------|-------|
| `organisation_id` | INT | FK to organisations |
| `module_name` | VARCHAR(100) | FK to module_catalog (CASCADE) |
| `is_enabled` | BOOLEAN | TRUE = org-level override to enable |
| `enabled_at` | TIMESTAMPTZ | Last toggle time |
| `enabled_by` | INT | FK to users.id |

Primary key: `(organisation_id, module_name)` — upsert on conflict.

**All 26 Seeded Modules (Migration 036):**

| module_name | display_name | min_plan_tier | required_platforms |
|------------|--------------|--------------|--------------------|
| `core_chat` | AI Chat | free | — |
| `documents` | Documents | free | — |
| `prompt_library` | Prompt Library | free | — |
| `notifications` | Notifications | free | — |
| `universal_search` | Universal Search | starter | — |
| `synergy` | Synergy | starter | — |
| `automation` | Automation | starter | — |
| `thread_cards` | Thread Cards | starter | — |
| `shopify` | Shopify | professional | `['shopify']` |
| `xero` | Xero Accounting | professional | `['xero']` |
| `auspost_shipping` | Australia Post | professional | `['auspost']` |
| `stock_management` | Stock Management | professional | — |
| `transcription` | Voice Transcription | professional | `['assemblyai']` |
| `vector_database` | Vector Search | professional | `['pinecone']` |
| `customer_reactivation` | Customer Reactivation | professional | — |
| `inhouse_print` | InHouse Print | enterprise | `['inhouseprint_sql']` |
| `inhouse_kanban` | InHouse Kanban | enterprise | `['inhouseprint_sql']` |
| `quote_calculator` | Quote Calculator | enterprise | — |
| `database_visualizer` | DB Visualizer | enterprise | — |
| `github` | GitHub | enterprise | — |
| `render_management` | Render Management | enterprise | `['render']` |
| `local_filesystem` | Local Filesystem | enterprise | — |
| `woocommerce` | WooCommerce | enterprise | `['woocommerce']` |

---

### Credential Encryption

**File:** `AI_infrastructure/shared/credential_crypto.py`
**Algorithm:** Fernet (AES-128-CBC + HMAC-SHA256) — authenticated symmetric encryption

**Setup:**
```bash
# Generate a new key (one-time, store in .env)
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# Add to .env:
CREDENTIAL_ENCRYPTION_KEY=<base64-key>
```

**Storage format:** `enc:v1:<fernet_token>` — prefix `enc:v1:` is the sentinel that marks an encrypted value. Without the prefix, the value is treated as legacy plaintext.

**Functions:**
```python
from AI_infrastructure.shared.credential_crypto import (
    encrypt_credential,   # str -> "enc:v1:..."
    decrypt_credential,   # "enc:v1:..." -> plaintext; passthrough for unencrypted
    is_encryption_enabled # -> bool
)
```

**Behaviour when key is missing:** Passthrough mode — values stored/returned as plaintext. Logs a warning. Never crashes.

---

### All Organisation API Endpoints

**File:** `AI_infrastructure/routes/organisation_credentials_routes.py`
**Blueprint prefix:** (no prefix — routes start with `/api/org/`)

| Method | Path | Min Role | Description |
|--------|------|----------|-------------|
| POST | `/api/org/create` | Any auth | Create new org; caller becomes owner |
| GET | `/api/org/info` | member | Org details, member count, vault status |
| PUT | `/api/org/info` | admin | Update org settings |
| GET | `/api/org/members` | manager | List members with roles |
| PUT | `/api/org/members/<user_id>/role` | admin | Change member role |
| DELETE | `/api/org/members/<user_id>` | owner | Remove member |
| GET | `/api/org/credentials` | manager | List credentials (masked) + audit log access |
| POST | `/api/org/credentials` | admin | Add new credential (encrypted on save) |
| PUT | `/api/org/credentials/<id>` | admin | Edit credential |
| DELETE | `/api/org/credentials/<id>` | admin | Soft-delete credential (`is_active=FALSE`) |
| POST | `/api/org/credentials/<id>/test` | manager | Test connectivity (anthropic, openai, shopify, xero…) |
| POST | `/api/org/credentials/<id>/reveal` | admin | Reveal plaintext (+ vault password if set) |
| GET | `/api/org/credentials/audit-log` | admin | Full audit trail with IP, user-agent, timestamps |
| POST | `/api/org/vault-password` | owner | Set/change vault password |
| DELETE | `/api/org/vault-password` | owner | Remove vault password lock |
| **GET** | **`/api/org/platforms`** | member | **Platform catalog grouped by category** |
| **GET** | **`/api/org/modules`** | member | **Enabled module set for this org** |
| **GET** | **`/api/org/modules/catalog`** | member | **Full module catalog with is_enabled per module** |
| **PUT** | **`/api/org/modules/<module_name>`** | admin | **Enable/disable module override** |
| POST | `/api/org/invite` | admin | Create invite (optional email send) |
| GET | `/api/org/invite/pending` | admin | List pending invitations |
| DELETE | `/api/org/invite/<id>` | admin | Revoke invitation |
| GET | `/api/org/invite/accept?token=<uuid>` | None | Validate token, return invite details |
| POST | `/api/org/invite/accept` | Any auth | Accept invite, link user to org |
| POST | `/api/org/invite/<id>/send-email` | admin | Send invite via Gmail/Outlook OAuth |

---

### Frontend Integration

**File:** `UI/business-ai-platform-v2.html`
**Pattern:** Vanilla JS `OrgManager` object + module-level helper functions

**Platform catalog flow:**
1. User opens "Add Connection" modal → `showAddConnectionModal()` calls `loadPlatformCatalog()`
2. `loadPlatformCatalog()` fetches `GET /api/org/platforms`, caches in `_orgPlatformCatalog`
3. `renderPlatformGrid(byCategory)` renders category sections with platform buttons in `#dynamicPlatformGrid`
4. Clicking a platform calls `showApiKeyForm(platform)` (api_key/multi_field) or OAuth handlers
5. `showApiKeyForm()` reads `required_fields` from `_orgPlatformCatalog` → renders `dyn-field-{name}` inputs
6. `submitApiKeyForm()` collects `dyn-field-{name}` values → POSTs to `/api/org/credentials`

**Module catalog flow:**
1. Admin clicks "Modules" subtab in org panel → `OrgManager.loadModuleCatalog()`
2. Fetches `GET /api/org/modules/catalog`, calls `renderModuleCatalog()`
3. Module cards rendered in `#org-modules-catalog` with plan tier badge, required platforms, enable toggle
4. Toggle calls `OrgManager.toggleModule(name, enabled)` → `PUT /api/org/modules/<name>`

**Key JS identifiers (search for these):**
```javascript
_orgPlatformCatalog         // Cache object for platform catalog
CAT_META / CATEGORY_ORDER   // Category display metadata
loadPlatformCatalog()       // Fetch + cache platforms from API
renderPlatformGrid()        // Render platform buttons by category
showApiKeyForm(platform)    // Render credential form with catalog fields
submitApiKeyForm(event)     // Collect dyn-field-* + POST /api/org/credentials
OrgManager.loadModuleCatalog()  // Fetch + render module catalog
OrgManager.renderModuleCatalog() // Render module cards
OrgManager.toggleModule()   // PUT /api/org/modules/<name>
```

**Key HTML element IDs:**
```html
#dynamicPlatformGrid        <!-- Platform buttons container (Add Connection modal) -->
#additionalApiFields        <!-- dyn-field-* inputs rendered here -->
#apiKeyLabel                <!-- Main credential field label (updated per platform) -->
#apiKeyValue                <!-- Main credential input -->
#apiKeyPlatform             <!-- Hidden input: current platform name -->
#org-subtab-modules         <!-- Modules management panel -->
#org-modules-catalog        <!-- Module cards container -->
```

---

### How to Add a New Platform

> **Zero code changes required.** Only a DB `INSERT` is needed.

**Step 1: INSERT into platform_catalog**
```sql
INSERT INTO ai_infrastructure.platform_catalog (
    platform_name,
    display_name,
    icon_class,
    icon_color,
    category,
    auth_type,
    required_fields,
    description,
    docs_url,
    sort_order
) VALUES (
    'facebook_ads',                     -- snake_case, unique key
    'Facebook Ads',                     -- shown in UI
    'fab fa-facebook',                  -- FontAwesome class
    '#1877F2',                          -- brand hex
    'advertising',                      -- new or existing category
    'multi_field',                      -- api_key | multi_field | oauth2 | connection_string
    '[
        {"name": "access_token", "label": "Access Token", "type": "password",
         "placeholder": "EAAxxxxx", "required": true,
         "help_text": "Get from Meta Business Manager > System Users"},
        {"name": "account_id", "label": "Ad Account ID", "type": "text",
         "placeholder": "act_123456789", "required": true}
    ]'::jsonb,
    'Meta Facebook Ads API for campaign management',
    'https://developers.facebook.com/docs/marketing-apis',
    100
);
```

**Step 2: Verify** — Hit `GET /api/org/platforms` — the new platform appears immediately.

**Notes:**
- `required_fields[0]` maps to the main `#apiKeyValue` input
- `required_fields[1+]` are rendered as `dyn-field-{name}` inputs below it
- `auth_type: 'oauth2'` platforms need a corresponding OAuth handler in the backend; the catalog entry alone won't wire up OAuth flow
- `is_active: false` hides the platform from the UI without deleting it

**Adding a new category:**
```javascript
// In business-ai-platform-v2.html, update CATEGORY_META to add display name + icon:
const CATEGORY_META = {
    ...existing...,
    'advertising': { label: 'Advertising', icon: 'fas fa-ad', color: '#1877F2' }
};
// And add to CATEGORY_ORDER array at the desired position.
```

---

### How to Add a New Module

> **Zero code changes required for catalog entry.** The actual module implementation still lives in `UI/modules_external/`.

**Step 1: INSERT into module_catalog**
```sql
INSERT INTO ai_infrastructure.module_catalog (
    module_name,
    display_name,
    description,
    icon_class,
    icon_color,
    category,
    min_plan_tier,
    required_platforms,
    sort_order
) VALUES (
    'facebook_ads',
    'Facebook Ads',
    'Manage Facebook ad campaigns, view spend and ROAS, pause/resume ad sets',
    'fab fa-facebook',
    '#1877F2',
    'marketing',
    'professional',
    ARRAY['facebook_ads'],   -- platform credentials required
    35
);
```

**Step 2 (optional): Pre-enable for an org**
```sql
INSERT INTO ai_infrastructure.org_module_access (organisation_id, module_name, is_enabled, enabled_at, enabled_by)
VALUES (1, 'facebook_ads', TRUE, NOW(), <admin_user_id>)
ON CONFLICT (organisation_id, module_name) DO UPDATE
  SET is_enabled = TRUE, enabled_at = NOW();
```

**Step 3: Create the module implementation** — Follow the Module Plugin System pattern in `UI/modules_external/` (see Module Plugin System Details section below).

---

### Quick Verification Scripts

**Check platform catalog contents:**
```sql
-- Run in Supabase SQL editor
SELECT platform_name, display_name, category, auth_type, sort_order
FROM ai_infrastructure.platform_catalog
WHERE is_active = TRUE
ORDER BY category, sort_order;
```

**Check module catalog + org enabled state:**
```sql
SELECT mc.module_name, mc.display_name, mc.min_plan_tier,
       oma.is_enabled AS org_override
FROM ai_infrastructure.module_catalog mc
LEFT JOIN ai_infrastructure.org_module_access oma
  ON oma.module_name = mc.module_name AND oma.organisation_id = 1
ORDER BY mc.sort_order;
```

**Test platform catalog API:**
```powershell
# With JWT token
$token = "<your_jwt>"
Invoke-RestMethod -Uri "http://localhost:5000/api/org/platforms" `
  -Headers @{Authorization="Bearer $token"} | ConvertTo-Json -Depth 5
```

**Test module catalog API:**
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/api/org/modules/catalog" `
  -Headers @{Authorization="Bearer $token"} | ConvertTo-Json -Depth 5
```

**Toggle a module via API:**
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/api/org/modules/shopify" `
  -Method PUT `
  -Headers @{Authorization="Bearer $token"; 'Content-Type'='application/json'} `
  -Body '{"enabled": true}'
```

**Verify migration 036 was applied:**
```sql
SELECT COUNT(*) FROM ai_infrastructure.platform_catalog;  -- expect 27
SELECT COUNT(*) FROM ai_infrastructure.module_catalog;    -- expect 26
```

---

### Key Files Reference (Org/Platform/Module System)

| File | Purpose |
|------|---------|
| `AI_infrastructure/routes/organisation_credentials_routes.py` | All org API routes (25 endpoints) |
| `AI_infrastructure/migrations/036_platform_module_catalog.sql` | Creates `platform_catalog`, `module_catalog`; seeds all data |
| `AI_infrastructure/migrations/032_org_module_access.sql` | Creates `org_module_access` table |
| `AI_infrastructure/shared/credential_crypto.py` | Fernet encryption for credential values |
| `AI_infrastructure/shared/database_utils.py` | `execute_query()` — all DB operations use this |
| `UI/business-ai-platform-v2.html` | Frontend: `OrgManager` + `loadPlatformCatalog()` + `renderPlatformGrid()` + Modules tab |

---

### Change History

| Date | Migration | Description |
|------|-----------|-------------|
| March 2026 | 036 | `platform_catalog` + `module_catalog` tables. 27 platforms, 26 modules seeded. Dynamic frontend grid. Modules management subtab. Per-org module enable/disable via `org_module_access`. |
| Jan 2026 | 032 | `org_module_access` table (pre-catalog, plan-tier driven logic). |
| Late 2025 | 028–031 | Org credentials vault, audit log, reveal/test endpoints. |
| Late 2025 | 025–027 | Org invitations system (invite tokens, role assignment). |
| Late 2025 | 020–024 | Org member management (roles, JWT invalidation, vault password). |

---

## Pending Work — What Still Needs Building

> **For any AI agent picking up this codebase:** The items below are DESIGNED and DOCUMENTED but NOT yet coded into the application. The database schema and API endpoints are live. The frontend implementation is the missing piece.

### 1. `initModulesFromOrg()` — DB-Driven Sidebar Visibility

**Status: NOT implemented. Design spec exists.**  
**Reference:** `.github/MODULE_VISIBILITY_ARCHITECTURE.md` — Section 6 (full function code provided)

**What it is:** A JavaScript function that runs on login/org switch, calls `GET /api/org/modules`, then shows/hides sidebar items and tab content based on which modules the org has enabled.

**Why it matters:** Right now, ALL sidebar items are visible to ALL users regardless of org or role. The DB module catalog (`org_module_access`) records which modules each org has enabled — but that data is never read to affect the UI. This function is the bridge that connects the DB to the sidebar.

**What the function must do:**
1. Call `GET /api/org/modules` → get `{ enabled_modules: ['core_chat', 'shopify', ...] }`
2. For Zone 1 hardcoded items: check `data-module` attribute on each `<li>` → hide if not in enabled list
3. For Zone 2 dynamic items: replace `manifest.json`-driven `ModuleManager` with DB-driven rendering
4. For Zone 3 (account/settings): always visible — no gating needed
5. Add CSS class `.module-hidden` (display:none) to disabled items

**Files to edit:**
- `UI/business-ai-platform-v2.html` — add `initModulesFromOrg()` function, call it after login/org switch
- Add `data-module="<module_name>"` attributes to all Zone 1 sidebar `<li>` items

**CSS needed (add once to `<style>` block):**
```css
.module-hidden { display: none !important; }
```

---

### 2. WooCommerce Tab Hardcoded — No Gating

**Status: KNOWN ISSUE — hardcoded always-visible**  
**File:** `UI/business-ai-platform-v2.html`  
**Search for:** `data-tab="sales"` (sidebar button) and `id="tab-sales"` (tab content)

The WooCommerce tab (`tab-sales`) is hardcoded in the sidebar with a shopping cart icon and zero module/role gating. It appears for every user in every org. It should only appear when:
- The org has `woocommerce` module enabled in `org_module_access`
- The user has at least `member` role (standard access)

**Fix:** Add `data-module="woocommerce"` to the sidebar `<li>` button and handle it in `initModulesFromOrg()`.

---

### 3. Zone 2 Sidebar Still Driven by `manifest.json`

**Status: Static file still active — DB catalog NOT yet wired to sidebar**  
**File:** `UI/modules_external/manifest.json`

The `ModuleManager` JS class reads `manifest.json` (lists 7 modules: inhouse-kanban, inhouse-print, quote-calculator, stock-management, xero, shopify, local-filesystem) and renders icon buttons in `#sidebarModulesSection`. This is identical for every user.

**What needs changing:** Replace the `ModuleManager` manifest-loading with a DB-driven call. When `initModulesFromOrg()` runs, it should render only the modules the org has enabled, using `icon_class` and `icon_color` from `module_catalog`.

**`manifest.json` format (for reference):**
```json
{ "modules": [{ "id": "shopify", "name": "Shopify", "icon": "fab fa-shopify", "color": "#96bf48", "tab": "tab-shopify" }] }
```
This maps directly to `module_catalog` columns — migration is straightforward.

---

### 4. Role-Based Sidebar Gating Not Implemented

**Status: Designed but not applied**

Some sidebar items should be hidden not just by module but by role. Example: viewers shouldn't see org settings. The design calls for `data-org-min-role="admin"` attributes on `<li>` items.

**No code added yet.** After `initModulesFromOrg()` loads modules, a second pass should check `data-org-min-role` vs the user's current `org_role` and hide items the user's role doesn't meet.

---

### 5. Orphaned Tab: `tab-vsa-veterinary-alerts`

**Status: Dead code — inaccessible**  
**File:** `UI/business-ai-platform-v2.html` — approximately line 19202

A tab content div `id="tab-vsa-veterinary-alerts"` exists in the HTML with no corresponding sidebar button — it was never linked up. There is also no `vsa_veterinary_alerts` entry in `module_catalog`. This tab is completely inaccessible to users.

**Action needed:** Either add a sidebar entry + module catalog entry, or delete the orphaned HTML block entirely.

---

### Summary: What a New AI Should Implement Next

| # | Task | File(s) | Complexity |
|---|------|---------|------------|
| 1 | Build `initModulesFromOrg()` | `business-ai-platform-v2.html` | Medium — see Section 6 in `MODULE_VISIBILITY_ARCHITECTURE.md` |
| 2 | Add `data-module` attributes to Zone 1 sidebar items | `business-ai-platform-v2.html` | Low |
| 3 | Gate WooCommerce `tab-sales` with `data-module="woocommerce"` | `business-ai-platform-v2.html` | Low |
| 4 | Replace `manifest.json` Zone 2 rendering with DB-driven | `business-ai-platform-v2.html` | Medium |
| 5 | Add `data-org-min-role` checks for role-based gating | `business-ai-platform-v2.html` | Low |
| 6 | Resolve orphaned `tab-vsa-veterinary-alerts` | `business-ai-platform-v2.html` | Low |
| 7 | **Vector DB — Fix unauthenticated API endpoints (GAP-V1)** | `AI_infrastructure/routes/vector_db_routes.py` | **HIGH PRIORITY** — add `@require_auth`, replace `user_id=1` with `g.rls_user_id` |
| 8 | **Vector DB — Switch credential resolver (GAP-V2/V3)** | `vector_db_routes.py`, `pinecone_tools.py` | High — replace `os.getenv()` + `UserAuthManager` with `org_credentials_loader.resolve_credentials()` |
| 9 | **Vector DB — Propagate namespace isolation (GAP-V4)** | `pinecone_tools.py` | Medium — pass `org_{org_id}` namespace to all `index.query()` / `index.upsert()` calls |
| 10 | **Vector DB — Retire Settings-tab credential form (GAP-V5)** | `vector_database.html` | Low — replace form with org vault redirect message |
| 11 | **Vector DB — Gate sidebar item (GAP-V7/V8)** | `business-ai-platform-v2.html` | Low — add `data-module="vector_database"` + id to sidebar button |

> **Architecture doc:** All implementation details (full function code, CSS, module inventory table) are in `.github/MODULE_VISIBILITY_ARCHITECTURE.md`.
> **Vector DB gap analysis & fix code:** `.github/VECTOR_DB_ORG_ALIGNMENT_ANALYSIS_APR29_2026.md`

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

**"How do I add a new platform (Facebook, Instagram, etc.)?"**
→ See **How to Add a New Platform** in the Org/Platform/Module section above
→ Only a DB `INSERT INTO ai_infrastructure.platform_catalog` is needed — no code changes
→ `required_fields` JSONB drives the entire credential form automatically

**"How do I add a new module to the catalog?"**
→ See **How to Add a New Module** in the Org/Platform/Module section above
→ `INSERT INTO ai_infrastructure.module_catalog` then build implementation in `UI/modules_external/`

**"Platform not showing in Add Connection modal"**
→ Check `is_active = TRUE` in `ai_infrastructure.platform_catalog`
→ Hit `GET /api/org/platforms` to confirm it's returned by API
→ If migration 036 not run: falls back to `LEGACY_ALLOWED_PLATFORMS` hardcoded set in the route file

**"Module toggle not working / module not appearing"**
→ Check `ai_infrastructure.module_catalog` — `is_active = TRUE`?
→ Check `ai_infrastructure.org_module_access` for existing overrides
→ Admin+ role required for PUT `/api/org/modules/<name>`

**"Credential not saving / 'platform not allowed' error"**
→ `add_credential()` validates via `platform_catalog`; add platform to table if missing
→ Fallback: add to `LEGACY_ALLOWED_PLATFORMS` set in `organisation_credentials_routes.py`

**"Credential value is garbled / decrypt error"**
→ Check `CREDENTIAL_ENCRYPTION_KEY` is set in `.env`
→ Values with `enc:v1:` prefix are Fernet-encrypted; must use same key to decrypt
→ See `AI_infrastructure/shared/credential_crypto.py`

**"User lost access after role change"**
→ Expected: `jwt_version` incremented on role change invalidates JWT
→ User must log in again to get fresh token with new role
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

1. **Feature branch:** Work on `v11` (main development branch)
2. **Pre-commit checks:** Automatic security scan + code quality validation
3. **Commit format:** `feat(scope): description` (conventional commits required)
4. **Push to production:** `git push gerardo v11:v11` (deploys to Render via gerardovsa/Ai_Agents)
5. **Auto-deploy:** Render monitors `gerardovsa/Ai_Agents` v11 branch
6. **Migrations:** Run locally first, test idempotency, then deploy

### **Git Remotes Configuration:**
- **gerardo:** https://github.com/gerardovsa/Ai_Agents.git (PRODUCTION - Render deployment)
- ~~origin (InHouseGuy/BusinessAiSuite) — REMOVED Feb 26, 2026. No longer active or involved.~~

### **Standard Commit & Push Pattern:**
```powershell
git add <files>
git commit -m "type(scope): description"
git push gerardo v11:v11     # Push to production (Render deployment)
```

**⚠️ CRITICAL:** Always push to **gerardo** remote for production deployment. There is only one remote (`gerardo`) — do NOT add or push to any other remote.

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
- ✅ **Push to production:** `git push gerardo v11:v11`
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
SUPABASE_DB_URL=postgresql://postgres:<password>@<host>:5432/postgres
POOL_ENABLED=True

# Security
CREDENTIAL_ENCRYPTION_KEY=<base64-fernet-key>  # REQUIRED for credential vault encryption
# Generate: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# WARNING: Changing this key makes all existing encrypted credentials unreadable

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

## Troubleshooting: InHouse Print Database Access (Jan 5-13, 2026)

### **✅ COMPLETE FIX: All InHouse Tools Working (Jan 13, 2026)**

**Status: 4 of 6 functions fixed, 2 pending user request**

### **Fixed Functions:**

1. ✅ `inhouse_execute_sql` - Path resolution fix (Jan 5, 2026)
2. ✅ `inhouse_get_query_library_catalog` - Hardcoded catalog bypass (Jan 13, 2026)
3. ✅ `inhouse_get_calculator_requirements` - Direct calculator access (Jan 13, 2026)
4. ✅ `inhouse_calculate_quote` - Direct calculator access (Jan 13, 2026)

### **Stock Level Functions (Present but Not Actively Used):**

5. ⚠️ `inhouse_query_stock_levels` - Stock inventory tool (not actively used - stock types are maintained but levels are not tracked)
6. ⚠️ `inhouse_get_reorder_alerts` - Stock reorder alerts (not actively used - stock types are maintained but reorder alerts are not tracked)

### **Problem: "ToolUseAgent could not be imported" Error**

**Symptoms:**
- InHouse database tools fail with import error
- Error message: "ToolUseAgent could not be imported - check backend path and dependencies"
- Credentials ARE properly stored in Supabase table `ai_infrastructure.user_platform_credentials`

**Root Cause:**
- `inhouse_wrapper.py` tried to initialize `ToolUseAgent` from `quote-calculator/backend/tool_use_agent.py`
- `tool_use_agent.py` line 69-71 imports `complete_calculator_implementation`
- Import failed → `ToolUseAgent = None` → raises error when tools try to use it

### **Solution Applied:**

Modified `UI/modules_external/inhouse-print/implementations/inhouse_wrapper.py`:

**Function 1: `inhouse_execute_sql` (Line ~201)**
```python
def inhouse_execute_sql(query: str, **kwargs) -> List[Dict[str, Any]]:
    """Execute SQL query against InHouse Print database (Fred)"""
    # ✅ FIX: Add path resolution before import
    try:
        import sys
        from pathlib import Path
        
        db_connector_dir = Path(__file__).resolve().parent.parent
        if str(db_connector_dir) not in sys.path:
            sys.path.insert(0, str(db_connector_dir))
        
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

**Function 2: `inhouse_get_query_library_catalog` (Line ~133)**
```python
def inhouse_get_query_library_catalog(category: Optional[str] = None, **kwargs):
    """Get catalog of available pre-built queries"""
    # ✅ FIX: Bypass ToolUseAgent, return hardcoded catalog
    queries = [
        {
            "name": "customer_order_history",
            "category": "Customer Analytics",
            "description": "Order history for specific customer with totals"
        },
        {
            "name": "recent_job_tickets",
            "category": "Operational Metrics",
            "description": "Recent job tickets with full specifications"
        },
        # ... 3 more common queries
    ]
    
    if category:
        queries = [q for q in queries if q["category"] == category]
    
    return {
        "success": True,
        "queries": queries,
        "total": len(queries)
    }
```

**Function 3: `inhouse_get_calculator_requirements` (Line ~286)**
```python
def inhouse_get_calculator_requirements(product_type: str, **kwargs):
    """Get parameter requirements for quote calculator"""
    # ✅ FIX (Jan 13, 2026): Bypass ToolUseAgent and import calculator directly
    try:
        import sys
        from pathlib import Path
        
        # Add backend path to sys.path (quote-calculator/backend/)
        backend_dir = Path(__file__).resolve().parent.parent.parent / 'quote-calculator' / 'backend'
        sys.path.insert(0, str(backend_dir))
        
        # Import calculator class
        from complete_calculator_implementation import ComprehensiveQuoteCalculator
        
        # Import database connector from parent directory
        db_connector_dir = Path(__file__).resolve().parent.parent
        sys.path.insert(0, str(db_connector_dir))
        from db_connector import InHousePrintDB
        
        # Initialize database connection
        db = InHousePrintDB()
        
        # Initialize calculator
        calculator = ComprehensiveQuoteCalculator(db)
        
        # Get requirements
        result = calculator.get_calculator_requirements(product_type)
        
        # Convert Decimal types to JSON-serializable
        return convert_to_json_serializable({
            "success": True,
            "product_type": product_type,
            "requirements": result
        })
        
    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": f"Failed to get calculator requirements: {e}",
            "details": traceback.format_exc()
        }
```

**Function 4: `inhouse_calculate_quote` (Line ~398)**
```python
def inhouse_calculate_quote(product_type: str, parameters: Dict[str, Any], **kwargs):
    """Calculate quote for print products"""
    # ✅ FIX (Jan 13, 2026): Bypass ToolUseAgent and import calculator directly
    try:
        import sys
        import json
        from pathlib import Path
        
        # Add backend path to sys.path
        backend_dir = Path(__file__).resolve().parent.parent.parent / 'quote-calculator' / 'backend'
        sys.path.insert(0, str(backend_dir))
        
        # Import calculator class
        from complete_calculator_implementation import ComprehensiveQuoteCalculator
        
        # Import database connector
        db_connector_dir = Path(__file__).resolve().parent.parent
        sys.path.insert(0, str(db_connector_dir))
        from db_connector import InHousePrintDB
        
        # Initialize database connection
        db = InHousePrintDB()
        
        # Initialize calculator
        calculator = ComprehensiveQuoteCalculator(db)
        
        # Handle both JSON string and dict parameters (from registry)
        if isinstance(parameters, str):
            parameters = json.loads(parameters)
        
        # Calculate quote
        result = calculator.calculate_quote(product_type, parameters)
        
        # Convert Decimal types to JSON-serializable
        return convert_to_json_serializable({
            "success": True,
            "product_type": product_type,
            "quote": result
        })
        
    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": f"Failed to calculate quote: {e}",
            "details": traceback.format_exc()
        }
```

### **Why This Works:**
1. `InHousePrintDB` class in `db_connector.py` already has Supabase credential fetching (line 42-56)
2. Auto-detects Render environment vs local development
3. No dependency on ToolUseAgent or calculator implementations (except for calculator functions)
4. Direct SQL execution or calculator access with proper error handling
5. Explicit path resolution ensures imports work regardless of context

### **Testing:**
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

# Test calculator requirements
from UI.modules_external.inhouse-print.implementations.inhouse_wrapper import inhouse_get_calculator_requirements
requirements = inhouse_get_calculator_requirements("business_cards")
print(requirements)

# Test quote calculation
from UI.modules_external.inhouse-print.implementations.inhouse_wrapper import inhouse_calculate_quote
quote = inhouse_calculate_quote("business_cards", {
    "quantity": 1000,
    "stock_type": "satin_350gsm",
    "sides": 2,
    "celloglaze": "2_side_matt",
    "artworks": 1
})
print(quote)
```

### **Key Lessons:**
- ToolUseAgent was unnecessary dependency for simple SQL execution and calculator access
- `db_connector.py` already had all needed database functionality
- Direct calculator import with path resolution is simpler and more reliable
- Bypass complex import chains when simpler solution exists
- Always verify credentials are in Supabase before debugging connection logic

### **Related Documentation:**
- `INHOUSE_EXECUTE_SQL_FIX_JAN13_2026.md` - Initial SQL fix
- `INHOUSE_TOOLS_COMPLETE_FIX_JAN13_2026.md` - Complete tool audit and fixes
- `INHOUSE_CALCULATOR_TOOLS_FIXED_JAN13_2026.md` - Calculator functions fix

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
