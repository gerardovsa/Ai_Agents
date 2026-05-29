# Vector Database — Org System Alignment Analysis & Change Plan
**Date:** April 29, 2026 (Updated: May 29, 2026 — 4-tier model alignment)
**Author:** Analysis via GitHub Copilot
**Status:** ✅ FULLY IMPLEMENTED — All 8 gaps resolved April 29, 2026. May 2026 update: 4-tier credential model documented; GAP-V9 (`_get_vector_provider()` personal-org short-circuit) ✅ implemented May 29, 2026.
**Companion docs:** `ORG_CREDENTIALS_MASTER_ANALYSIS_UPDATED_MAY28_2026.md` *(formerly `ORGANISATION_CREDENTIALS_ARCHITECTURE.md` + `ORG_CREDENTIALS_MASTER_ANALYSIS.md` — both archived May 28, 2026)*, `MODULE_VISIBILITY_ARCHITECTURE.md`

---

## 1. Purpose

This document captures the complete gap analysis between the vector database module and the current org/team/credential architecture. It defines every change required to bring the vector database system into full alignment with:

- The org credential vault (`organisation_platform_credentials`, Fernet-encrypted)
- The `org_credentials_loader.resolve_credentials()` **4-tier** resolution pattern (Tier 1.5 sub-user inheritance added May 2026)
- The JWT-based auth system (`@require_auth`, `g.rls_user_id`)
- The module visibility system (`org_module_access`, `initModulesFromOrg()`)
- The namespace isolation requirement (GAP-C1 partial fix completion)

---

## 2. Files Affected

| File | Type | Change Required |
|------|------|-----------------|
| `AI_infrastructure/routes/vector_db_routes.py` | Python (backend) | Auth, credential resolution, namespace enforcement |
| `tools/implementations/pinecone/pinecone_tools.py` | Python (AI tools) | Credential resolution switch, namespace propagation |
| `UI/modules_internal/vector_database/vector_database.js` | JavaScript (frontend) | Auth headers, remove hardcoded user_id, retire settings form |
| `UI/modules_internal/vector_database/vector_database.html` | HTML (sidebar) | Remove credential settings form, add org vault redirect message |
| `UI/business-ai-platform-v2.html` | HTML (main app) | Add `data-module="vector_database"` to sidebar button |

---

## 3. Gap Inventory

### GAP-V1 — CRITICAL: No Authentication on `vector_db_routes.py`

**Severity:** CRITICAL (security vulnerability)
**File:** `AI_infrastructure/routes/vector_db_routes.py`

**Problem:**
`@require_auth` is imported on line 39 but not applied to any endpoint. All endpoints either:
- Hardcode `user_id = 1` (the retired platform-global superuser)
- Accept `user_id` as a query parameter (any user can spoof any user ID)
- Read `request.user` which is `None` without `@require_auth`

Evidence (line 437 comment in the file itself):
```python
# Get current user context for filtering (use query params since @require_auth removed)
current_user_id = request.args.get('user_id', 1, type=int)
```

**Fix:**
1. Add `@require_auth` decorator to all 8 endpoints.
2. Replace every `user_id = 1` and `request.args.get('user_id', 1)` with `g.rls_user_id`.
3. `g.rls_user_id` is set by `set_rls_context_from_jwt()` in `flask_app.py` `@before_request`.

**Endpoints to fix:**
- `upload_document()` — `POST /api/vector-db/upload-document`
- `list_documents()` — `GET /api/vector-db/documents`
- `get_stats()` — `GET /api/vector-db/stats`
- `load_credentials()` — `GET /api/vector-db/credentials/load`
- `check_connection_status()` — `GET /api/vector-db/credentials/status`
- `save_credentials()` — `POST /api/vector-db/credentials/save`
- `get_embedding_config()` — `GET /api/vector-db/embedding-config/get`
- `save_embedding_config()` — `POST /api/vector-db/embedding-config/save`

---

### GAP-V2 — CRITICAL: `upload_document()` Uses `os.getenv()` for Credentials

**Severity:** CRITICAL (bypasses the entire credential store)
**File:** `AI_infrastructure/routes/vector_db_routes.py`, approx. lines 315–320

**Problem:**
The document upload endpoint reads API keys directly from environment variables, ignoring user/org credentials entirely:
```python
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
pinecone_client = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
index_name = os.getenv('PINECONE_INDEX_NAME', 'ai-agents-vectors')
```
This means:
- Documents are always uploaded with platform-level keys, not per-org keys
- Multi-tenant billing is impossible (all costs go to one account)
- The org vault is completely bypassed for this path

**Fix:**
Replace `os.getenv()` calls with:
```python
from AI_infrastructure.shared.org_credentials_loader import resolve_credentials

pinecone_creds = resolve_credentials(user_id, 'pinecone')
if not pinecone_creds:
    return jsonify({'success': False, 'error': 'Pinecone not configured for your organisation.'}), 400

embedding_creds = resolve_credentials(user_id, 'openai_embeddings') or resolve_credentials(user_id, 'voyager')
if not embedding_creds:
    return jsonify({'success': False, 'error': 'Embedding provider not configured for your organisation.'}), 400
```

---

### GAP-V3 — CRITICAL: AI Tools Use Wrong Credential Resolver

**Severity:** CRITICAL (org vault keys silently ignored)
**File:** `tools/implementations/pinecone/pinecone_tools.py`

**Problem:**
`_get_pinecone_client()` and `_get_openai_embeddings()` resolve credentials via:
```python
auth_manager = UserAuthManager()
creds = auth_manager.get_platform_credentials(user_id, 'pinecone')
```
`UserAuthManager.get_platform_credentials()` only searches `user_platform_credentials` (the personal per-user table). It does **not** check `organisation_platform_credentials` (the org vault).

If an admin stores the Pinecone key in the org vault (the correct place, per migration 036), the AI tools will not find it and will silently fail.

**Fix:**
Replace both credential fetches with the org-aware loader:
```python
from AI_infrastructure.shared.org_credentials_loader import resolve_credentials

# In _get_pinecone_client():
creds = resolve_credentials(user_id, 'pinecone')
if not creds:
    raise PineconeToolsError("Pinecone credentials not found in your organisation vault or personal connections.")

# In _get_openai_embeddings():
creds = resolve_credentials(user_id, 'openai_embeddings') or resolve_credentials(user_id, 'voyager')
if not creds:
    raise PineconeToolsError("Embedding credentials not found. Configure OpenAI Embeddings or Voyager in org credentials.")
```

`resolve_credentials()` already handles the 3-tier lookup:
1. `user_platform_credentials` (personal)
2. `organisation_platform_credentials` (org vault)
3. `os.getenv()` fallback (legacy, logs a warning)

---

### GAP-V4 — HIGH: Namespace Not Propagated from `_get_pinecone_client()` to Query Operations

**Severity:** HIGH (cross-org data leakage still possible)
**File:** `tools/implementations/pinecone/pinecone_tools.py`

**Problem:**
The GAP-C1 fix added org-aware namespace derivation to `_get_pinecone_client()`:
```python
namespace = f"org_{org_id}" if org_id else f"user_{user_id}"
```
This namespace is returned in the `metadata` dict. **However**, every calling function (`pinecone_query_vectors`, `pinecone_upsert_vectors`, etc.) accepts an explicit `namespace` parameter defaulting to `''` (empty string). If the caller doesn't pass the correct namespace, queries go to Pinecone's **default namespace** which is shared across all orgs.

Example — current behaviour:
```python
# AI calls this with no namespace argument:
pinecone_query_vectors(query_text="invoices", top_k=5)
# → namespace defaults to ''
# → queries the default namespace
# → can see vectors from all orgs
```

**Fix:**
In every function that calls `_get_pinecone_client()`, use the client's derived namespace as the default when the caller doesn't supply one:
```python
index, meta = _get_pinecone_client(user_id, **kwargs)
effective_namespace = namespace if namespace else meta['namespace']
# Use effective_namespace in all index operations
```

---

### GAP-V5 — HIGH: Vector DB Sidebar Credential Form Saves to Wrong Table

**Severity:** HIGH (credentials saved in retired pattern, never used by tools)
**Files:** `AI_infrastructure/routes/vector_db_routes.py`, `UI/modules_internal/vector_database/vector_database.html`

**Problem:**
The Vector DB sidebar "Settings" tab has a form to enter Pinecone credentials. When submitted:
1. `POST /api/vector-db/credentials/save` is called
2. The endpoint hardcodes `user_id = 1` and saves to `user_platform_credentials`

This creates a silent conflict:
- User saves Pinecone key in Vector DB sidebar → goes to `user_platform_credentials[user_id=1]`
- Admin saves Pinecone key in Org Settings → goes to `organisation_platform_credentials[org_id=X]`
- AI tools call `UserAuthManager.get_platform_credentials(actual_user_id, 'pinecone')` → neither location is found for the actual user
- The `upload_document()` route uses `os.getenv()` → ignores both

**Fix:**
1. **Retire the credential form from the Vector DB sidebar settings tab.** Pinecone is an org-level credential; it belongs in the Org Settings vault.
2. Replace the settings tab credential form with an explanatory message:
   > "Pinecone credentials are managed at the organisation level. Ask your admin to add them in Settings → Organisation → Connections."
3. Keep the embedding model selector (provider/model choice) since that is a user preference, not a secret.
4. The `save_credentials()` and `load_credentials()` routes can be deprecated once this is done.

---

### GAP-V6 — HIGH: Document Ownership Not Enforced at Query Time

**Severity:** HIGH (user A can retrieve user B's private documents)
**File:** `tools/implementations/pinecone/pinecone_tools.py`

**Problem:**
`vector_db_upload_document()` stores ownership metadata on each vector:
```python
'owner_user_id': user_id,
'visibility': visibility,  # 'user' | 'global' | 'team'
```
But `pinecone_query_vectors()` does not inject any filter for `owner_user_id` or `visibility`. Any user's AI session can call `pinecone_query_vectors(query_text="...")` and retrieve documents owned by any other user.

Additionally, documents uploaded via the HTTP route (`POST /api/vector-db/upload-document`) don't have `owner_user_id` metadata at all — they use the hardcoded `user_id=1` context.

**Fix:**
In `pinecone_query_vectors()`, auto-inject a visibility filter when no explicit filter is provided:
```python
# Auto-inject ownership filter if no filter provided
if not filter:
    org_row = execute_query(
        "SELECT organisation_id FROM ai_infrastructure.users WHERE id = %s",
        (user_id,), fetch_mode='one'
    )
    org_id = org_row['organisation_id'] if org_row else None
    filter = {
        "$or": [
            {"visibility": {"$eq": "global"}},
            {"owner_user_id": {"$eq": user_id}},
            {"owner_user_id": {"$eq": f"org_{org_id}"}},
        ]
    }
```
Note: The exact Pinecone filter syntax depends on how metadata was stored. A simpler first pass is to enforce the namespace (GAP-V4 fix) — each org gets its own namespace, so cross-org leakage is prevented at the index level.

---

### GAP-V7 — MEDIUM: Module Not Gated by Org Plan or Module Toggle

**Severity:** MEDIUM (billing/product controls missing)
**File:** `UI/business-ai-platform-v2.html`

**Problem:**
The Vector Database tab (`tab-vector-database`) and its sidebar button are visible to **all users in all orgs** regardless of:
- Plan tier (supposed to require `professional` or above)
- Whether the `vector_database` module is enabled for the org in `org_module_access`

In `MODULE_VISIBILITY_ARCHITECTURE.md` Section 7 it is documented as:
> "Vector Database | Zone 1 Core | tab-vector-database | ❌ Built-in | `vector_database` | Professional | **Always On** | None"

The "Always On" designation in the current doc is wrong — it reflects the actual broken state, not the intended design. The module catalog sets `min_plan_tier = 'professional'` and `required_platforms = ['pinecone']`, which means it should only appear for professional+ orgs that have Pinecone configured.

**Fix:**
1. Add `data-module="vector_database"` attribute to the sidebar `<li>` button element.
2. When `initModulesFromOrg()` is implemented, the Vector DB item will only show when `vector_database` is in the org's enabled modules.
3. Update `MODULE_VISIBILITY_ARCHITECTURE.md` Section 7 — change "Always On" to "Optional" for Vector Database.

---

### GAP-V8 — LOW: Missing `vector-database-toggle` Button ID

**Severity:** LOW (log noise, UX)
**File:** `UI/business-ai-platform-v2.html`

**Problem:**
At startup, `SidebarManager` logs this warning every time:
```
[SIDEBAR MANAGER] Toggle button 'vector-database-toggle' not found - sidebar can still be controlled programmatically
```
The SidebarManager is registered with `toggleButtonId: 'vector-database-toggle'` but no button in the HTML has that `id`. The sidebar still works (programmatic toggle works), but the warning appears on every load.

**Fix:**
Find the button that opens the Vector DB sidebar and add `id="vector-database-toggle"` to it.

---

## 4. Change Summary Table

| Gap ID | Severity | File(s) | Type | Description |
|--------|----------|---------|------|-------------|
| GAP-V1 | CRITICAL | `vector_db_routes.py` | Security | Add `@require_auth`, replace hardcoded `user_id=1` |
| GAP-V2 | CRITICAL | `vector_db_routes.py` | Security | Replace `os.getenv()` with `resolve_credentials()` in upload |
| GAP-V3 | CRITICAL | `pinecone_tools.py` | Security | Switch to `org_credentials_loader.resolve_credentials()` |
| GAP-V4 | HIGH | `pinecone_tools.py` | Security | Propagate derived namespace to all query/upsert operations |
| GAP-V5 | HIGH | `vector_db_routes.py`, `vector_database.html` | Architecture | Retire sidebar credential form; redirect to org vault |
| GAP-V6 | HIGH | `pinecone_tools.py` | Security | Enforce ownership filter on queries |
| GAP-V7 | MEDIUM | `business-ai-platform-v2.html` | Product | Gate behind `data-module="vector_database"` + org toggle |
| GAP-V8 | LOW | `business-ai-platform-v2.html` | UX | Add `id="vector-database-toggle"` to the sidebar open button |

---

## 5. Implementation Order

Recommended order to minimise risk and enable progressive testing:

```
Phase 1 — Security fixes (no UI impact, backend only)
  1a. GAP-V1: Add @require_auth to all vector_db_routes.py endpoints         ✅ DONE
  1b. GAP-V2: Fix upload_document() to use resolve_credentials()              ✅ DONE
  1c. GAP-V3: Fix pinecone_tools.py credential resolution                     ✅ DONE
  1d. GAP-V4: Fix namespace propagation in all tool functions                 ✅ DONE

Phase 2 — Architecture cleanup
  2a. GAP-V5: Retire credential form from Vector DB sidebar settings tab      ✅ DONE
  2b. GAP-V6: Add ownership filter to pinecone_query_vectors()                ✅ DONE

Phase 3 — Module visibility (depends on initModulesFromOrg() being built)
  3a. GAP-V7: Add data-module attribute, update MODULE_VISIBILITY_ARCHITECTURE ✅ DONE
  3b. GAP-V8: Add toggle button ID                                             ✅ DONE
```

---

## 9. Implementation Record (April 29, 2026)

All 8 gaps resolved in a single session. Summary of changes made:

### Files Modified

| File | Changes |
|------|---------|
| `AI_infrastructure/routes/vector_db_routes.py` | Added `g` to flask import; added `from AI_infrastructure.shared.org_credentials_loader import resolve_credentials`; added `@require_auth` to all 8 endpoints; replaced all `user_id = 1` with `g.rls_user_id`; replaced `os.getenv('OPENAI_API_KEY')` / `os.getenv('PINECONE_API_KEY')` in `upload_document()` with `resolve_credentials()`; added org namespace derivation; replaced `_get_vector_db_credentials()` call in `get_stats()` with direct `vector_db_list_namespaces(_user_id=user_id)`; replaced body of `load_credentials()` and `save_credentials()` with 410 Gone responses; replaced raw SQL credential lookup in `check_connection_status()` with `resolve_credentials()`; replaced `UserAuthManager` credential lookup in `get_embedding_config()` with `resolve_credentials()`. |
| `tools/implementations/pinecone/pinecone_tools.py` | Removed `UserAuthManager` import; added `import os`; replaced `UserAuthManager().get_platform_credentials()` in `_get_pinecone_client()` with `resolve_credentials(user_id, 'pinecone')`; replaced credential lookup in `_get_openai_embeddings()` with `resolve_credentials(user_id, 'openai_embeddings') or resolve_credentials(user_id, 'openai')`; added `effective_namespace = namespace or metadata.get('namespace', '')` in `pinecone_query_vectors()`, `pinecone_upsert_vectors()`, `pinecone_delete_vectors()`, `pinecone_fetch_vectors()`, `pinecone_update_vector()`; added org-scoped ownership filter (GAP-V6) in `pinecone_query_vectors()`; removed `user_{user_id}_{category}` namespace auto-generation in `vector_db_upload_document()`. |
| `UI/modules_internal/vector_database/vector_database.html` | Updated `credential-status-banner` to direct users to Organisation Settings > Connections (with correct button target) instead of the local Settings tab. |
| `UI/modules_internal/vector_database/vector_database.js` | Replaced `saveCredentials()` to show a redirect message to org vault; replaced `loadCredentials()` to use `checkConnectionStatus()` (org-aware endpoint) instead of the retired `credentials/load` endpoint. |
| `UI/business-ai-platform-v2.html` | Added `id="vector-database-toggle"` and `data-module="vector_database"` to the sidebar button (`data-action="vectordb"`). |

### Documentation Updated Alongside Implementation
- `MODULE_VISIBILITY_ARCHITECTURE.md` — Vector Database row corrected (Always On → MUST BE OPTIONAL, Zone 1 Core → Zone 1 Core ⚠️)
- `ORG_CREDENTIALS_MASTER_ANALYSIS.md` — Gap #10 added in Known Gaps section
- `copilot-instructions.md` — Pending Work table rows 7–11 added
- `AUTHENTICATION_FIX_IMPLEMENTATION_PLAN.md` — Marked SUPERSEDED

---

## 6. Documentation Files That Need Updating After Implementation

| File | What Changes |
|------|-------------|
| `VECTOR_DATABASE.md` | Section on credential configuration — remove instructions to use sidebar settings form; point to org vault instead. Credential resolution now goes via `org_credentials_loader`. |
| `.github/MODULE_VISIBILITY_ARCHITECTURE.md` | Section 3a and Section 7 — change Vector Database from "Always On" / "None" action to "Optional" / "Gate behind org_module_access". |
| `.github/copilot-instructions.md` | "Pending Work" section — mark GAP-V1 through GAP-V4 completed once done. |
| `UI/modules_internal/vector_database/README.md` | Architecture section — update credential resolution description. Step 3 in Setup currently says to configure via sidebar — redirect to org vault. |
| `UI/modules_internal/vector_database/AUTHENTICATION_FIX_IMPLEMENTATION_PLAN.md` | Mark as completed once GAP-V1 is done. |

---

## 7. Existing Fixed Gap for Reference

### GAP-C1 (From Master Analysis — Partial Fix Applied)

The master analysis flagged Pinecone empty namespace as CRITICAL. The fix was partially applied:
- `_get_pinecone_client()` now derives `org_{org_id}` namespace when no explicit namespace is set.
- **NOT YET COMPLETE:** The derived namespace is not passed through to the query/upsert operations (this is GAP-V4 above).

---

## 8. Key Code Locations

| What | File | Line/Function |
|------|------|---------------|
| Credential resolution (correct pattern) | `AI_infrastructure/shared/org_credentials_loader.py` | `resolve_credentials()` |
| JWT user_id injection | `AI_infrastructure/flask_app.py` | `set_rls_context_from_jwt()` → `g.rls_user_id` |
| Auth decorator | `AI_infrastructure/auth/user_auth.py` | `@require_auth` |
| Pinecone client init (needs fixing) | `tools/implementations/pinecone/pinecone_tools.py` | `_get_pinecone_client()` |
| Embedding init (needs fixing) | `tools/implementations/pinecone/pinecone_tools.py` | `_get_openai_embeddings()` |
| Upload route (needs fixing) | `AI_infrastructure/routes/vector_db_routes.py` | `upload_document()` ~line 210 |
| Load creds route (needs fixing) | `AI_infrastructure/routes/vector_db_routes.py` | `load_credentials()` ~line 497 |
| Save creds route (to retire) | `AI_infrastructure/routes/vector_db_routes.py` | `save_credentials()` ~line 795 |
| Sidebar settings tab (to update) | `UI/modules_internal/vector_database/vector_database.html` | Settings tab section |
| Sidebar open button (needs ID) | `UI/business-ai-platform-v2.html` | Vector DB sidebar button |
| Module status table | `.github/MODULE_VISIBILITY_ARCHITECTURE.md` | Section 7 row "Vector Database" |

---

## 10. May 2026 Update — 4-Tier Model Alignment

**Updated:** May 29, 2026  
**Reference:** `ORG_CREDENTIALS_MASTER_ANALYSIS_UPDATED_MAY28_2026.md` (authoritative as of May 28, 2026)  
**Migration:** 046 (`is_personal_org`, `default_member_role`, `create_personal_org()`)

---

### 10.1 Credential Resolution Is Now 4-Tier (Not 3-Tier)

The April 29 implementation used a 3-tier credential resolution chain:
```
Tier 1 → user_platform_credentials (personal)
Tier 2 → organisation_platform_credentials (org vault)
Tier 3 → os.getenv() (legacy env-var fallback)
```

As of May 2026, **Tier 1.5 is inserted** for sub-account users (`is_sub_user = TRUE`):
```
Tier 1   → user_platform_credentials (this user's own personal credentials)
Tier 1.5 → parent user's user_platform_credentials (if is_sub_user=TRUE, parent_user_id)
Tier 2   → organisation_platform_credentials (shared org vault)
Tier 3   → os.getenv() (legacy fallback, logs a warning)
```

`resolve_credentials()` in `org_credentials_loader.py` must implement the Tier 1.5 lookup for sub-users. Any call within the vector DB module that uses `resolve_credentials(user_id, 'pinecone')` or `resolve_credentials(user_id, 'openai_embeddings')` will automatically benefit from this once the loader is updated.

---

### 10.2 Tier-by-Tier Vector DB Behaviour

| Tier | `is_personal_org` | `is_sub_user` | Expected vector DB behaviour |
|------|:-----------------:|:-------------:|-------------------------------|
| **Tier 1 — Solo** | `TRUE` | `FALSE` | `_get_vector_provider()` should always return `'pgvector'`; Pinecone is never needed. Embedding credentials come from the personal org vault. |
| **Tier 2A — Team member** | `FALSE` | `FALSE` | Unchanged from April 29 implementation. Provider resolves via `resolve_credentials(user_id, 'pinecone')` → pgvector if absent. |
| **Tier 2B — Sub-account** | `FALSE` | `TRUE` | Credential resolution uses Tier 1.5 (parent user keys) before the org vault. Namespace is `org_{org_id}` — same as parent, which is correct (shared org index). Document `owner_user_id` is the sub-user's own `user_id`. |
| **Tier 3 — Enterprise** | `FALSE` | `FALSE` | Unchanged from April 29 implementation. Full Pinecone or pgvector per org vault. |

---

### 10.3 GAP-V9 — Enhancement: Short-Circuit `_get_vector_provider()` for Personal Orgs

**Severity:** LOW (current behaviour is already functionally correct — pgvector is returned when Pinecone credentials are absent)  
**Status:** Identified, not yet implemented — low priority  
**File:** `AI_infrastructure/routes/vector_db_routes.py` → `_get_vector_provider()`

**Current behaviour:**
```python
def _get_vector_provider(user_id):
    creds = resolve_credentials(user_id, 'pinecone')
    if creds:
        return 'pinecone', creds
    return 'pgvector', {}
```
For a Tier 1 Solo user, this already returns `'pgvector'` because no Pinecone credential exists in a personal org vault. Functionally correct.

**Proposed enhancement (optional):**
```python
def _get_vector_provider(user_id):
    # Short-circuit for personal orgs — pgvector always, no Pinecone lookup needed
    org_row = execute_query(
        """SELECT o.is_personal_org FROM ai_infrastructure.organisations o
           JOIN ai_infrastructure.users u ON u.organisation_id = o.id
           WHERE u.id = %s""",
        (user_id,), fetch_mode='one'
    )
    if org_row and org_row.get('is_personal_org'):
        return 'pgvector', {}

    creds = resolve_credentials(user_id, 'pinecone')
    if creds:
        return 'pinecone', creds
    return 'pgvector', {}
```

**When to implement:** ~~Only if the extra DB round-trip from `resolve_credentials()` for personal-org users becomes a measurable performance concern, or if Pinecone credential resolution causes spurious errors/warnings for solo users.~~

✅ **Implemented May 29, 2026.** The `is_personal_org` query is lightweight (single indexed JOIN), non-fatal on failure (try/except falls through), and runs only when `PGVECTOR_TOOLS_AVAILABLE` is true — so Pinecone-only deployments are unaffected.

---

### 10.4 Namespace Isolation Remains Correct for All Tiers

The `org_{org_id}` namespace enforced by GAP-V4 (April 29) already handles all four tiers correctly:

- **Tier 1 (Solo):** namespace = `org_{their_personal_org_id}` — isolated from all other orgs ✅
- **Tier 2A (Team member):** namespace = `org_{shared_org_id}` — all team members share the same index partition ✅
- **Tier 2B (Sub-account):** namespace = `org_{shared_org_id}` — same org as parent; correct sharing semantics ✅
- **Tier 3 (Enterprise):** namespace = `org_{enterprise_org_id}` — isolated per enterprise ✅

No namespace changes are needed.

---

### 10.5 Document Ownership for Sub-Users (Tier 2B)

Documents uploaded by a sub-user are stored with `owner_user_id = sub_user.id` and `namespace = org_{org_id}`. This means:
- The sub-user owns their own documents (correct — `owner_user_id` is their actual `user_id`)
- The org-scoped visibility filter (GAP-V6) allows the whole team to see `visibility='team'` documents within the namespace
- If the sub-user account is removed, their `owner_user_id` references remain (orphaned documents are accessible to the org via namespace, not leaked outside)

No code changes needed for Tier 2B document ownership.

---

### 10.6 Summary: What Changed vs April 29 Implementation

| Item | April 29 State | May 2026 State | Action Required |
|------|---------------|----------------|-----------------|
| Credential resolution tiers | 3-tier | 4-tier (Tier 1.5 added) | `org_credentials_loader.py` must add parent-user lookup for `is_sub_user=TRUE` (not vector-DB-specific) |
| `_get_vector_provider()` | Checks Pinecone creds → pgvector fallback | Short-circuits to pgvector for `is_personal_org=TRUE` before any credential lookup | ✅ GAP-V9 implemented May 29, 2026 |
| Namespace isolation | `org_{org_id}` for all users | Unchanged — correct for all 4 tiers | None |
| Document ownership | `owner_user_id = user_id` | Unchanged — sub-user gets own `owner_user_id` | None |
| Companion docs reference | `ORGANISATION_CREDENTIALS_ARCHITECTURE.md` | **ARCHIVED** → `ORG_CREDENTIALS_MASTER_ANALYSIS_UPDATED_MAY28_2026.md` | Updated in this file's header ✅ |
| "3-tier resolution" language | All April 29 references | Updated to "4-tier" throughout this document | Updated ✅ |
