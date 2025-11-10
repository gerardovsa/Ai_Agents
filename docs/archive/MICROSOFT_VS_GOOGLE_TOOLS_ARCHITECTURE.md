# Microsoft vs Google Tools: Key Architectural Differences

**Date:** November 3, 2025  
**Purpose:** Document critical differences in implementation patterns

---

## 🔴 CRITICAL DIFFERENCE #1: Module-Level Exports

### Microsoft Tools (107 tools across 10 platforms)

**Pattern:** Class-based with **MANDATORY module-level exports using `microsoft_*` prefix**

**Example:** `microsoft_word_tools.py`

```python
class MicrosoftWordTools:
    def word_create_document(self, name, content="", **kwargs):
        """Create Word document"""
        # Implementation...

# ========================================
# GLOBAL INSTANCE & MODULE-LEVEL EXPORTS  ← CRITICAL!
# ========================================

microsoft_word_tools = MicrosoftWordTools()

# Export with microsoft_ prefix to match schema!
microsoft_word_create_document = microsoft_word_tools.word_create_document
microsoft_word_get_document = microsoft_word_tools.word_get_document
microsoft_word_list_documents = microsoft_word_tools.word_list_documents
# ... 25 total exports
```

**Why This Matters:**
- Schema names: `microsoft_word_create_document` (with prefix)
- Implementation method: `word_create_document` (without prefix)
- Module export: `microsoft_word_create_document` (with prefix) **BRIDGES THE GAP**
- Registry loads: **MODULE-LEVEL exports**, not class methods

---

### Google Tools (283 tools across 12 platforms)

**Pattern:** **Direct function definitions** (no class wrapper, no exports needed)

**Example:** `google_docs.py`

```python
# Direct function definition - no class!
def google_docs_create_document(title, with_sample_content=False, 
                                _user_id=None, _injected_credentials=None, **kwargs):
    """Create a new Google Doc and make it shareable"""
    # Implementation...
    
def google_docs_smart_create_from_markdown(title, markdown_content, **kwargs):
    """Create formatted doc from markdown"""
    # Implementation...

# NO EXPORTS NEEDED - Functions already at module level!
```

**Why This Works:**
- Schema names: `google_docs_create_document` (function name)
- Implementation: `google_docs_create_document` (same function)
- Registry loads: **FUNCTIONS directly from module**
- No export layer needed!

---

## 🔴 CRITICAL DIFFERENCE #2: Tool Name Format

### Microsoft Tools

**Schema → Implementation Mapping:**

| Schema Name (in JSON) | Implementation Method | Module Export |
|-----------------------|----------------------|---------------|
| `microsoft_word_create_document` | `word_create_document()` | `microsoft_word_create_document` |
| `microsoft_outlook_send_email` | `outlook_send_email()` | `microsoft_outlook_send_email` |
| `microsoft_excel_create_workbook` | `excel_create_workbook()` | `microsoft_excel_create_workbook` |

**Pattern:** `microsoft_[platform]_[action]` → `[platform]_[action]()` → `microsoft_[platform]_[action]`

---

### Google Tools

**Schema → Implementation Mapping:**

| Schema Name (in JSON) | Implementation Function | 
|-----------------------|-------------------------|
| `google_docs_create_document` | `google_docs_create_document()` |
| `gmail_send_email` | `gmail_send_email()` |
| `google_sheets_create` | `google_sheets_create()` |

**Pattern:** `[platform]_[action]` → `[platform]_[action]()` (direct 1:1 match)

---

## 🔴 CRITICAL DIFFERENCE #3: Credential Injection

### Microsoft Tools

**Pattern:** Dynamic credential injection using Graph API

```python
def _get_headers(self, **kwargs) -> Dict[str, str]:
    """Get authorization headers for Microsoft Graph API"""
    if '_user_id' in kwargs:
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'AI_infrastructure'))
        from auth.credential_injector import get_microsoft_access_token
        access_token = get_microsoft_access_token(**kwargs)
    else:
        raise Exception("No user credentials provided. User must be authenticated.")
    
    return {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
```

**Key Points:**
- ✅ No static environment variable checks at `__init__`
- ✅ Credentials fetched per-request using `_user_id`
- ✅ Calls `get_microsoft_access_token()` from credential_injector
- ✅ Supports multi-user with individual Microsoft accounts
- ⚠️ Requires Microsoft OAuth setup per user

---

### Google Tools

**Pattern:** OAuth credentials from database OR service account fallback

```python
def _get_user_credentials_if_available(user_id, injected_credentials_flag):
    """Helper to get user OAuth credentials from database"""
    if user_id and injected_credentials_flag:
        try:
            from AI_infrastructure.auth.user_auth import UserAuthManager
            auth_manager = UserAuthManager()
            cred_dict = auth_manager.get_user_google_oauth_credentials(user_id)
            if cred_dict:
                print(f"🔑 Using database OAuth credentials for user {user_id}")
                return cred_dict
            else:
                print(f"⚠️ User {user_id} has no Google OAuth credentials in database")
        except Exception as e:
            print(f"⚠️ Could not load user credentials: {e}")
    return None

def _get_docs_service(user_id=None, injected_credentials=None):
    """Get authenticated Google Docs API service"""
    # Try user credentials first
    return build_docs_service(user_id=user_id, injected_credentials=injected_credentials)
```

**Key Points:**
- ✅ Tries user OAuth credentials first (from database)
- ✅ Falls back to service account if no user credentials
- ✅ Uses `build_docs_service()` from `google_auth_helper`
- ✅ Supports both service account AND user OAuth
- ✅ Service account works immediately (no setup per user)

---

## 🔴 CRITICAL DIFFERENCE #4: File Location

### Microsoft Tools

**Location:** `tools/implementations/microsoft_[platform]_tools.py`

```
tools/
└── implementations/
    ├── microsoft_calendar_tools.py (24 tools)
    ├── microsoft_excel_tools.py (30 tools)
    ├── microsoft_forms_tools.py (19 tools)
    ├── microsoft_onedrive_tools.py (29 tools)
    ├── microsoft_onenote_tools.py (21 tools)
    ├── microsoft_outlook_tools.py (30 tools)
    ├── microsoft_sharepoint_tools.py (23 tools)
    ├── microsoft_teams_tools.py (28 tools)
    ├── microsoft_todo_tools.py (29 tools)
    └── microsoft_word_tools.py (25 tools)
```

**Pattern:** Standard tool implementation location

---

### Google Tools

**Location:** `google_workspace/[platform].py`

```
google_workspace/
├── gmail.py (45 tools)
├── google_docs.py (35 tools)
├── google_forms.py (98 tools)
├── google_sheets.py (14 tools)
├── google_drive.py (22 tools)
├── google_calendar.py (11 tools)
├── google_tasks.py (25 tools)
├── google_slides.py (20 tools)
├── google_meet.py (23 tools)
├── google_analytics.py (19 tools)
├── google_cloud_run.py (18 tools)
└── google_auth_helper.py (12 functions)
```

**Pattern:** Separate folder for all Google Workspace integrations

---

## 🔴 CRITICAL DIFFERENCE #5: Registry Loading Logic

### Microsoft Tools - Special Registry Logic

**File:** `tools/registry_v3.py` lines 140-174

```python
def _extract_class_instance(self, module, tool_name: str, is_microsoft_tool: bool = False) -> Any:
    """Extract function or class instance from module"""
    
    if is_microsoft_tool:
        # Microsoft tools: Return MODULE directly (has microsoft_* exports)
        logger.info(f"  ⚡ Microsoft tool: returning MODULE for {tool_name}")
        return module
    
    # For other tools...
    # [standard logic]
```

**Why This Matters:**
- Microsoft tools use **module-level exports**
- Registry returns **MODULE** (not class instance)
- Registry looks up: `module.microsoft_word_create_document`
- WITHOUT this, would try to find class and fail!

---

### Google Tools - Standard Registry Logic

```python
# Google tools use standard loading
for name in dir(module):
    if name.startswith('google_') and callable(getattr(module, name)):
        # Found it! It's a function at module level
        func = getattr(module, name)
        functions[name] = func
```

**Why This Works:**
- Functions already at module level
- No special handling needed
- Registry finds functions via `dir(module)`

---

## 📊 Summary Table

| Aspect | Microsoft Tools | Google Tools |
|--------|----------------|--------------|
| **Structure** | Class-based with module exports | Direct functions |
| **Name Prefix** | `microsoft_[platform]_[action]` | `[platform]_[action]` or `google_[platform]_[action]` |
| **Exports** | Required with prefix | Not needed |
| **Location** | `tools/implementations/` | `google_workspace/` |
| **Registry Logic** | Special handling (return MODULE) | Standard loading |
| **Credentials** | Graph API OAuth (user-specific) | OAuth OR service account |
| **Auth Setup** | User must link Microsoft account | Works with service account |
| **Multi-User** | Yes (per-user OAuth) | Yes (per-user OAuth + fallback) |
| **Tool Count** | 107 tools (10 platforms) | 283 tools (12 platforms) |

---

## 🎯 Key Takeaways

### Why Microsoft Tools Need Module Exports:

1. **Schema uses prefix:** `microsoft_word_create_document`
2. **Class method has no prefix:** `word_create_document()`
3. **Export bridges gap:** `microsoft_word_create_document = microsoft_word_tools.word_create_document`
4. **Registry loads MODULE:** Looks for `module.microsoft_word_create_document`

### Why Google Tools Don't:

1. **Schema matches function:** `google_docs_create_document`
2. **Function defined directly:** `def google_docs_create_document(...):`
3. **No bridging needed:** Registry finds function directly at module level

---

## ⚠️ Common Pitfalls

### Microsoft Tools Mistake #1: Forgetting Module Exports

❌ **WRONG:**
```python
class MicrosoftWordTools:
    def word_create_document(self, ...):
        pass

# Missing: microsoft_word_create_document = microsoft_word_tools.word_create_document
```

**Result:** Tool not found in registry!

---

### Microsoft Tools Mistake #2: Wrong Prefix in Export

❌ **WRONG:**
```python
# Export without microsoft_ prefix
word_create_document = microsoft_word_tools.word_create_document
```

**Result:** Tool not found! Schema expects `microsoft_word_create_document`

---

### Google Tools Mistake: Using Classes

❌ **WRONG:**
```python
class GoogleDocsTools:
    def google_docs_create_document(self, ...):
        pass
```

**Result:** Inconsistent with existing Google tools pattern!

✅ **CORRECT:**
```python
def google_docs_create_document(title, **kwargs):
    """Create document"""
    pass
```

---

## 🔧 When Adding New Tools

### Adding Microsoft Tool:

1. ✅ Create class in `tools/implementations/microsoft_[platform]_tools.py`
2. ✅ Define methods WITHOUT `microsoft_` prefix
3. ✅ Create module-level exports WITH `microsoft_` prefix
4. ✅ Schema names MUST match module exports
5. ✅ Update registry if needed

### Adding Google Tool:

1. ✅ Add function to `google_workspace/[platform].py`
2. ✅ Function name matches schema name exactly
3. ✅ No exports needed
4. ✅ No special registry handling needed

---

**Last Updated:** November 3, 2025  
**Version:** 1.0.0  
**Related:** `MICROSOFT_TOOLS_REGISTRATION_100_PERCENT_SUCCESS.md`, `REGISTRY_V3_ARCHITECTURE.md`
