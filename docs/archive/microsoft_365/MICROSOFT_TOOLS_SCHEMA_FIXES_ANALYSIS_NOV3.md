# MICROSOFT TOOLS SCHEMA ISSUES - COMPLETE ANALYSIS
## November 3, 2025

## CRITICAL ISSUE: TWO DIFFERENT SCHEMA FORMATS

The Microsoft tool schemas are using **TWO INCOMPATIBLE FORMATS**, which breaks the registry's schema conversion:

### Format Problem

**Word Schema (CORRECT Format 1):**
```json
"parameters": {
  "name": {
    "type": "string",
    "required": true,           ← Individual parameter marking
    "description": "..."
  }
}
```

**Outlook Schema (MIXED Format 1 + Array):**
```json
"parameters": {
  "to": {
    "type": "array",
    "items": {"type": "string"},
    "required": true,           ← Individual parameter marking
    "description": "..."
  }
},
"required": ["to", "subject", "body"]  ← ARRAY AT TOP LEVEL (Format 2!)
```

**OneDrive Schema (PROBLEMATIC - needs user_id):**
```json
"parameters": {
  "user_id": {
    "type": "string",
    "required": true,
    "description": "User ID for authentication"  ← SHOULD BE INJECTED!
  }
}
```

---

## ISSUES FOUND

### Issue #1: Mixed Schema Formats (Word vs Outlook)

**Word Tools:** Use Format 1 (parameter-level `required: true/false`)
```json
"parameters": {
  "name": {"type": "string", "required": true},
  "content": {"type": "string", "required": false}
}
```

**Outlook Tools:** Use Format 1 + Format 2 (BOTH parameter-level AND array-level `required`)
```json
"parameters": {
  "to": {"type": "array", "required": true},
  "subject": {"type": "string", "required": true}
},
"required": ["to", "subject"]  ← This is Format 2!
```

**Problem:** Registry converter gets confused and may not properly detect all required parameters.

**Solution:** Standardize to Format 1 ONLY (remove the top-level `required` array from Outlook schemas)

---

### Issue #2: OneDrive Requires `user_id` Parameter

**Current Outlook schema:**
```json
"parameters": {
  "user_id": {
    "type": "string",
    "required": true,
    "description": "User ID for authentication"
  },
  "folder_path": {...}
}
```

**Problem:** `user_id` should NOT be exposed as a required parameter! It's handled by `_user_id` credential injection and `_injected_credentials`.

**Solution:** Remove `user_id` from parameters and let credential injection handle it automatically

---

### Issue #3: Inconsistent Parameter Naming

| Schema | Pattern | Status |
|--------|---------|--------|
| Word | `document_id`, `folder_id` | ✅ Consistent |
| Outlook | `message_id`, `attachment_id` | ✅ Consistent |
| Excel | `workbook_id`, `sheet_id` | ✅ Consistent |
| OneDrive | `user_id`, `folder_path` | ❌ Exposes user_id |

---

## DETAILED FIXES NEEDED

### Fix #1: Outlook Schema - Remove Top-Level `required` Array

**File:** `tools/schemas/microsoft_outlook_tools.json`

**Change outlooks_send_email FROM:**
```json
{
  "parameters": {
    "to": {
      "type": "array",
      "items": {"type": "string"},
      "required": true
    },
    "subject": {
      "type": "string",
      "required": true
    },
    "body": {
      "type": "string",
      "required": true
    }
  },
  "required": ["to", "subject", "body"]  ← DELETE THIS LINE!
}
```

**Change TO:**
```json
{
  "parameters": {
    "to": {
      "type": "array",
      "items": {"type": "string"},
      "required": true
    },
    "subject": {
      "type": "string",
      "required": true
    },
    "body": {
      "type": "string",
      "required": true
    }
  }
  // ✅ No top-level "required" array needed - parameter-level marking is sufficient
}
```

**Apply to all Outlook tools that have top-level `required` array:**
- outlook_send_email
- outlook_smart_bulk_send_personalized
- outlook_get_message
- outlook_search_messages
- outlook_mark_as_read
- outlook_move_message
- outlook_delete_message
- outlook_create_folder
- outlook_create_draft
- outlook_send_draft
- outlook_reply_to_message
- outlook_forward_message
- outlook_add_category
- outlook_flag_message
- outlook_smart_organize_inbox
- outlook_create_inbox_rule
- outlook_get_attachments
- outlook_download_attachment

---

### Fix #2: OneDrive Schema - Remove Exposed `user_id`

**File:** `tools/schemas/microsoft_onedrive_tools.json`

**Current problematic parameter:**
```json
"parameters": {
  "user_id": {
    "type": "string",
    "description": "User ID for authentication",
    "required": true  ← SHOULD NOT BE HERE!
  },
  "folder_path": {
    "type": "string",
    "required": false
  }
}
```

**Should be:**
```json
"parameters": {
  "folder_path": {
    "type": "string",
    "description": "Folder path (root if not specified)",
    "required": false,
    "default": "root"
  }
}
```

**Rationale:** 
- `user_id` is injected via `_user_id` and `_injected_credentials`
- It should NOT be a parameter that Claude needs to provide
- Credential injector handles this automatically

**Apply to ALL OneDrive tools** - Remove `user_id` parameter from ALL of them:
- onedrive_list_files
- onedrive_upload_file
- onedrive_download_file
- onedrive_get_file_info
- onedrive_create_folder
- onedrive_delete_item
- (etc. - all OneDrive tools)

---

### Fix #3: Excel Schema - Verify Format Consistency

**File:** `tools/schemas/microsoft_excel_tools.json`

**Status:** ✅ ALREADY CORRECT - Uses Format 1 with parameter-level `required` only

Example (good):
```json
"parameters": {
  "name": {
    "type": "string",
    "required": true
  }
}
```

**Action:** No changes needed - keep as is

---

## SUMMARY OF CHANGES

### Files to Fix

| File | Issue | Fix | Count |
|------|-------|-----|-------|
| `microsoft_outlook_tools.json` | Top-level `required` arrays | Remove all top-level `required` arrays | ~18 tools |
| `microsoft_onedrive_tools.json` | Exposed `user_id` parameters | Remove ALL `user_id` parameters | ~20+ tools |
| `microsoft_word_tools.json` | None | No action needed | 0 |
| `microsoft_excel_tools.json` | None | No action needed | 0 |
| `microsoft_calendar_tools.json` | Need to check | TBD | ? |
| `microsoft_teams_tools.json` | Need to check | TBD | ? |
| `microsoft_sharepoint_tools.json` | Need to check | TBD | ? |

---

## HOW TO FIX OUTLOOK TOOLS

### Step 1: Find all tools with top-level `required` array

```bash
grep -n '"required": \[' tools/schemas/microsoft_outlook_tools.json
```

### Step 2: For each tool, remove the line and closing bracket

**Pattern to find:**
```json
    },
    "required": ["to", "subject", "body"]
  }
```

**Replace with:**
```json
    }
  }
```

### Example Fix:

**outlook_send_email BEFORE:**
```json
      {
        "name": "outlook_send_email",
        "description": "...",
        "parameters": {
          "to": {
            "type": "array",
            "required": true
          },
          "subject": {
            "type": "string",
            "required": true
          },
          "body": {
            "type": "string",
            "required": true
          },
          "body_type": {
            "type": "string",
            "required": false
          }
        },
        "required": ["to", "subject", "body"]  ← DELETE
      }
```

**outlook_send_email AFTER:**
```json
      {
        "name": "outlook_send_email",
        "description": "...",
        "parameters": {
          "to": {
            "type": "array",
            "required": true
          },
          "subject": {
            "type": "string",
            "required": true
          },
          "body": {
            "type": "string",
            "required": true
          },
          "body_type": {
            "type": "string",
            "required": false
          }
        }
        // ✅ Top-level required removed
      }
```

---

## HOW TO FIX ONEDRIVE TOOLS

### Step 1: Find all parameters named `user_id`

```bash
grep -B2 -A2 '"user_id"' tools/schemas/microsoft_onedrive_tools.json | head -30
```

### Step 2: Remove the entire `user_id` parameter object

**Pattern to find:**
```json
        "user_id": {
          "type": "string",
          "description": "User ID for authentication",
          "required": true
        },
```

**Simply delete** the entire 4-5 line block above

### Example Fix:

**onedrive_list_files BEFORE:**
```json
      {
        "name": "onedrive_list_files",
        "parameters": {
          "user_id": {                          ← DELETE
            "type": "string",                   ← DELETE
            "required": true,                   ← DELETE  
            "description": "User ID..."         ← DELETE
          },                                     ← DELETE
          "folder_path": {
            "type": "string",
            "required": false
          }
        }
      }
```

**onedrive_list_files AFTER:**
```json
      {
        "name": "onedrive_list_files",
        "parameters": {
          "folder_path": {
            "type": "string",
            "description": "Folder path (root if not specified)",
            "required": false,
            "default": "root"
          }
        }
      }
```

---

## VERIFICATION

After making fixes, run:

```python
from tools.registry_v3 import RegistryV3
import json

r = RegistryV3()

# Check outlook_send_email has correct required fields
outlook = [t for t in r.get_anthropic_tools() if t['name'] == 'outlook_send_email'][0]
print("Outlook send_email required:", outlook['input_schema']['required'])
# Expected: ['to', 'subject', 'body']

# Check onedrive_list_files does NOT have user_id
onedrive = [t for t in r.get_anthropic_tools() if t['name'] == 'onedrive_list_files'][0]
print("OneDrive list_files properties:", list(onedrive['input_schema']['properties'].keys()))
# Expected: ['folder_path', 'max_results'] - NO user_id!

# Check Word schema unchanged
word = [t for t in r.get_anthropic_tools() if t['name'] == 'word_create_document'][0]
print("Word create required:", word['input_schema']['required'])
# Expected: ['name']
```

---

## IMPACT

### Current Issues
- ❌ Outlook tools may not properly enforce required parameters due to mixed format
- ❌ OneDrive tools expose `user_id` as required parameter (should be injected)
- ❌ Claude may get confused about which parameters are truly required

### After Fix
- ✅ All schemas use consistent Format 1
- ✅ Registry can properly extract required parameters
- ✅ Anthropic API properly enforces required parameters
- ✅ Credentials injected automatically, not exposed as parameters
- ✅ Claude knows exactly which parameters are required vs optional

---

## WHAT HAPPENS WITH THE FIX

### Before:
```
User: "Send an email"
Claude: Calls outlook_send_email() 
Result: ❌ Error - "to" required but missing
```

### After:
```
User: "Send an email"
Claude: Sees `required: true` for 'to', 'subject', 'body'
Result: Claude prompts for missing info OR provides sensible defaults
```

---

## NEXT STEP

Shall I apply these fixes to the schema files?
