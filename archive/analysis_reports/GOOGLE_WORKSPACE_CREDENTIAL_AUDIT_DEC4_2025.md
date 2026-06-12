# Google Workspace - Complete OAuth Credential Audit
**Date:** December 4, 2025  
**Branch:** v10

## Executive Summary

Comprehensive audit of all Google Workspace platform integrations to identify OAuth credential injection issues.

### Platforms Analyzed (11)
1. ✅ **Google Slides** - Fixed (11 functions repaired today)
2. ⚠️ **Google Docs** - 8 functions need fixes
3. ⚠️ **Google Forms** - 2 functions need fixes  
4. ⚠️ **Google Drive** - 8 functions need fixes (edge cases)
5. ✅ **Google Sheets** - Appears correct
6. ✅ **Google Calendar** - Appears correct
7. ✅ **Google Tasks** - Appears correct
8. ✅ **Google Meet** - Appears correct
9. ✅ **Google Analytics** - Appears correct
10. ✅ **Google Cloud Run** - N/A (service account only)
11. ✅ **Google Auth Helper** - Core helper functions

---

## 🔴 HIGH PRIORITY FIXES NEEDED

### Google Docs (8 functions)

All export and utility functions missing credential injection:

#### 1. `google_docs_export_as_pdf` (line 3461)
```python
def google_docs_export_as_pdf(document_id, **kwargs):
    try:
        service = _get_docs_service()  # ❌ No credentials!
```
**Impact:** 403 Forbidden when exporting user documents  
**Fix:** Add `_user_id=None, _injected_credentials=None` parameters

#### 2. `google_docs_add_page_numbers` (line 3495)
```python
def google_docs_add_page_numbers(document_id, position='FOOTER', alignment='CENTER', starting_number=1, **kwargs):
    try:
        service = _get_docs_service()  # ❌ No credentials!
```
**Impact:** 403 Forbidden when modifying user documents  
**Fix:** Add credential injection

#### 3. `google_docs_export_as_html` (line 3609)
```python
def google_docs_export_as_html(document_id, **kwargs):
    try:
        service = _get_docs_service()  # ❌ No credentials!
```
**Impact:** 403 Forbidden when exporting  
**Fix:** Add credential injection

#### 4. `google_docs_export_as_markdown` (line 3641)
```python
def google_docs_export_as_markdown(document_id, **kwargs):
    try:
        service = _get_docs_service()  # ❌ No credentials!
```
**Impact:** 403 Forbidden when exporting  
**Fix:** Add credential injection

#### 5. `google_docs_create_from_template` (line 3677)
```python
def google_docs_create_from_template(template_id, title, **kwargs):
    try:
        service = _get_docs_service()  # ❌ No credentials!
```
**Impact:** May fail copying user templates  
**Fix:** Add credential injection

#### 6. `google_docs_get_suggestions` (line 3699)
```python
def google_docs_get_suggestions(document_id, **kwargs):
    try:
        service = _get_docs_service()  # ❌ No credentials!
```
**Impact:** 403 Forbidden reading suggestions  
**Fix:** Add credential injection

#### 7. `google_docs_add_formatted_content` (line 3080)
```python
def google_docs_add_formatted_content(document_id, **kwargs):
    service = _get_docs_service()  # ❌ No credentials!
```
**Impact:** 403 Forbidden when adding content  
**Fix:** Add credential injection

#### 8. `google_docs_smart_bulk_create_multiple` (line 4768)
```python
def google_docs_smart_bulk_create_multiple(documents, share_with=None, folder_id=None, **kwargs):
    # Calls other functions - depends on their credential handling
```
**Impact:** Depends on underlying functions  
**Status:** May work if it calls fixed functions

---

### Google Forms (2 functions)

#### 1. `google_forms_get_questions_markdown` (line 368)
```python
def google_forms_get_questions_markdown(form_id, **kwargs):
    # Uses _get_forms_service(**kwargs) - GOOD!
    # But needs explicit parameters for clarity
```
**Status:** ⚠️ Works but inconsistent parameter declaration  
**Recommendation:** Add explicit `_user_id=None, _injected_credentials=None` parameters

#### 2. Other forms functions
Most Google Forms functions properly declare credential parameters and use them correctly.

**Status:** ✅ Mostly correct

---

### Google Drive (8 edge cases)

Most Drive functions properly support credentials, but these have potential issues:

#### 1. `google_drive_search_files` (line 446)
```python
def google_drive_search_files(query, max_results=10, **kwargs):
    # Missing explicit credential parameters
```
**Status:** ⚠️ May work via kwargs but inconsistent  
**Recommendation:** Add explicit parameters

#### 2. Conditional service building
Several Drive functions have this pattern:
```python
if 'user_id' not in kwargs or not kwargs['user_id']:
    service = _get_drive_service()  # ❌ No credentials!
else:
    user_id = kwargs['user_id']
    # ... proper credential handling
```
**Location:** Lines 82, 126, 190, 288, 326, 398, 433, 467, 503, 535  
**Issue:** Falls back to service account when user_id missing  
**Impact:** Works but inconsistent with other platforms

---

## ✅ WORKING PLATFORMS

### Google Sheets
- All functions properly declare and use credential parameters
- Uses `_get_sheets_service(user_id, injected_credentials)` pattern
- **Status:** ✅ Correct

### Google Calendar
- All functions properly declare and use credential parameters  
- Consistent `_user_id=None, _injected_credentials=None` pattern
- **Status:** ✅ Correct

### Google Tasks
- All functions properly declare and use credential parameters
- **Status:** ✅ Correct

### Google Meet
- All functions properly declare and use credential parameters
- **Status:** ✅ Correct

---

## Pattern Comparison

### ✅ CORRECT PATTERN (Google Slides - After Fix)
```python
def function_name(params..., _user_id=None, _injected_credentials=None, **kwargs):
    """Function docstring"""
    try:
        # Get user OAuth credentials if available
        cred_dict = _get_user_credentials_if_available(_user_id, _injected_credentials)
        
        if cred_dict:
            service = _get_service(user_id=_user_id, injected_credentials=cred_dict)
        else:
            service = _get_service()
        
        # ... rest of function
```

### ❌ BROKEN PATTERN (Google Docs exports)
```python
def function_name(params..., **kwargs):
    """Function docstring"""
    try:
        service = _get_docs_service()  # ❌ Never extracts credentials from kwargs!
        
        # ... rest of function
```

### ⚠️ INCONSISTENT PATTERN (Some Google Drive functions)
```python
def function_name(params..., **kwargs):
    """Function docstring"""
    try:
        if 'user_id' not in kwargs or not kwargs['user_id']:
            service = _get_drive_service()  # Falls back to service account
        else:
            user_id = kwargs['user_id']
            creds = kwargs.get('injected_credentials')
            # ... manual credential extraction
```

---

## Required Fixes Summary

### HIGH PRIORITY (10 functions)

**Google Docs (8):**
1. ✅ Export: `google_docs_export_as_pdf`
2. ✅ Export: `google_docs_export_as_html`
3. ✅ Export: `google_docs_export_as_markdown`
4. ✅ Modify: `google_docs_add_page_numbers`
5. ✅ Create: `google_docs_create_from_template`
6. ✅ Read: `google_docs_get_suggestions`
7. ✅ Create: `google_docs_add_formatted_content`
8. ⚠️ Bulk: `google_docs_smart_bulk_create_multiple` (check dependencies)

**Google Forms (2):**
9. ⚠️ Read: `google_forms_get_questions_markdown` (add explicit parameters)
10. ⚠️ Other: Review all forms functions for consistency

### MEDIUM PRIORITY (8 functions)

**Google Drive:**
- Refactor conditional credential logic to use standard pattern
- Add explicit credential parameters to all functions
- Lines to review: 82, 126, 190, 288, 326, 398, 433, 467, 503, 535

---

## Testing Recommendations

After fixes, test with user OAuth credentials:

### Google Docs
```python
# Test exports
execute_tool(tool_name='google_docs_export_as_pdf', document_id='YOUR_DOC_ID')
execute_tool(tool_name='google_docs_export_as_html', document_id='YOUR_DOC_ID')
execute_tool(tool_name='google_docs_export_as_markdown', document_id='YOUR_DOC_ID')

# Test modifications
execute_tool(tool_name='google_docs_add_page_numbers', document_id='YOUR_DOC_ID')
execute_tool(tool_name='google_docs_create_from_template', template_id='TEMPLATE_ID', title='Test')

# Test utilities
execute_tool(tool_name='google_docs_get_suggestions', document_id='YOUR_DOC_ID')
```

### Google Forms
```python
# Test reading
execute_tool(tool_name='google_forms_get_questions_markdown', form_id='YOUR_FORM_ID')
```

---

## Impact Assessment

### Before All Fixes
- ❌ Google Slides: 11 of 17 functions broken
- ❌ Google Docs: 8 export/utility functions broken
- ⚠️ Google Forms: 2 functions inconsistent
- ⚠️ Google Drive: 8+ functions have inconsistent patterns

### After Slides Fix (Today)
- ✅ Google Slides: All 17 functions working
- ❌ Google Docs: Still 8 functions broken
- ⚠️ Google Forms: Still inconsistent
- ⚠️ Google Drive: Still inconsistent

### After All Fixes
- ✅ Complete OAuth credential support across all platforms
- ✅ Consistent code patterns
- ✅ Users can fully access their Google Workspace resources
- ✅ No more 403 Forbidden errors

---

## Standard Fix Template

For all broken functions, apply this fix:

```python
# BEFORE
def function_name(param1, param2, **kwargs):
    try:
        service = _get_service()

# AFTER
def function_name(param1, param2, _user_id=None, _injected_credentials=None, **kwargs):
    try:
        # Get user OAuth credentials if available
        cred_dict = _get_user_credentials_if_available(_user_id, _injected_credentials)
        
        if cred_dict:
            service = _get_service(user_id=_user_id, injected_credentials=cred_dict)
        else:
            service = _get_service()
```

---

## Files to Modify

1. **google_workspace/google_docs.py** - 8 functions (HIGH PRIORITY)
2. **google_workspace/google_forms.py** - 2 functions (MEDIUM PRIORITY)
3. **google_workspace/google_drive.py** - 8+ functions (MEDIUM PRIORITY)

---

## Estimated Effort

- **Google Docs fixes:** ~30 minutes (8 similar fixes)
- **Google Forms fixes:** ~10 minutes (2 consistency updates)
- **Google Drive refactor:** ~45 minutes (more complex conditional logic)
- **Testing:** ~30 minutes (test each platform)
- **Total:** ~2 hours

---

## Next Steps

1. ✅ Google Slides - COMPLETE (commit dac28e0, be2cfe0)
2. 🔄 Fix Google Docs export/utility functions (8 functions)
3. 🔄 Standardize Google Forms parameter declarations (2 functions)
4. 🔄 Refactor Google Drive conditional logic (8+ functions)
5. 🔄 Comprehensive testing with user credentials
6. 🔄 Update all tool schemas if parameter signatures changed
