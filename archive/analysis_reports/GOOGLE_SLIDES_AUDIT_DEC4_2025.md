# Google Slides Functions - Credential Injection Audit
**Date:** December 4, 2025  
**Branch:** v10

## Summary

Analysis of all 17 Google Slides functions for OAuth credential injection support.

### Status Overview
- ✅ **Working (7 functions):** Proper credential injection
- ⚠️ **Partially Working (3 functions):** Manual credential extraction (inconsistent pattern)
- ❌ **Broken (7 functions):** Missing credential injection

---

## ✅ WORKING FUNCTIONS (7)

These functions properly support OAuth credential injection:

### 1. `google_slides_create_presentation` (line 93)
```python
def google_slides_create_presentation(title, template_id=None, 
                                     _user_id=None, _injected_credentials=None, **kwargs):
    cred_dict = _get_user_credentials_if_available(_user_id, _injected_credentials)
    if cred_dict:
        slides_service = _get_slides_service(user_id=_user_id, injected_credentials=cred_dict)
```
**Status:** ✅ Correct pattern

### 2. `google_slides_insert_text` (line 743) - FIXED TODAY
**Status:** ✅ Fixed (commit dac28e0)

### 3. `google_slides_insert_image` (line 874) - FIXED TODAY
**Status:** ✅ Fixed (commit dac28e0)

### 4. `google_slides_insert_shape` (line 950) - FIXED TODAY
**Status:** ✅ Fixed (commit dac28e0)

### 5. `google_slides_insert_table` (line 1063) - FIXED TODAY
**Status:** ✅ Fixed (commit dac28e0)

### 6. `google_slides_insert_chart_from_sheets` (line 1155) - FIXED TODAY
**Status:** ✅ Fixed (commit dac28e0)

### 7. `google_docs_to_slides_auto_generate` (not in file yet)
**Status:** ✅ Not yet implemented

---

## ⚠️ PARTIALLY WORKING (3 functions)

These functions extract credentials manually instead of using helper function. They work but use inconsistent pattern:

### 8. `google_slides_get_slide` (line 388)
```python
def google_slides_get_slide(presentation_id, slide_number, **kwargs):
    # Manual credential extraction
    user_id = kwargs.get('_user_id')
    injected_creds = kwargs.get('_injected_credentials')
    credentials_dict = _get_user_credentials_if_available(user_id, injected_creds)
    
    if credentials_dict:
        credentials = Credentials(
            token=credentials_dict.get('access_token'),
            refresh_token=credentials_dict.get('refresh_token'),
            token_uri='https://oauth2.googleapis.com/token',
            client_id=os.getenv('GOOGLE_CLIENT_ID'),
            client_secret=os.getenv('GOOGLE_CLIENT_SECRET')
        )
        service = build('slides', 'v1', credentials=credentials)
```
**Issue:** Manually builds Credentials instead of using `_get_slides_service()` helper  
**Impact:** Works, but inconsistent with other functions  
**Recommendation:** Refactor to use standard pattern

### 9. `google_slides_search_presentation` (line 503)
**Issue:** Same as get_slide - manual credential building  
**Impact:** Works, but inconsistent  
**Recommendation:** Refactor to use standard pattern

### 10. `google_slides_get_presentation` (line 173)
```python
def google_slides_get_presentation(presentation_id, format='summary', **kwargs):
    try:
        slides_service = _get_slides_service()  # ❌ No credentials!
```
**Issue:** Accepts credentials in kwargs but never uses them  
**Impact:** Falls back to service account (may fail on private presentations)  
**Recommendation:** Add credential injection

---

## ❌ BROKEN FUNCTIONS (7)

These functions are completely missing credential injection and will fail on user presentations:

### 11. `google_slides_add_slide` (line 613)
```python
def google_slides_add_slide(presentation_id, layout='BLANK', index=None, **kwargs):
    try:
        slides_service = _get_slides_service()  # ❌ No credentials!
```
**Impact:** 403 Forbidden when adding slides to user presentations  
**Priority:** HIGH - Core functionality

### 12. `google_slides_delete_slide` (line 686)
```python
def google_slides_delete_slide(presentation_id, slide_id, **kwargs):
    try:
        slides_service = _get_slides_service()  # ❌ No credentials!
```
**Impact:** 403 Forbidden when deleting slides  
**Priority:** HIGH - Destructive operation

### 13. `google_slides_duplicate_slide` (line 711)
```python
def google_slides_duplicate_slide(presentation_id, slide_id, **kwargs):
    try:
        slides_service = _get_slides_service()  # ❌ No credentials!
```
**Impact:** 403 Forbidden when duplicating slides  
**Priority:** HIGH - Core functionality

### 14. `google_slides_export_as_pdf` (line 1231)
```python
def google_slides_export_as_pdf(presentation_id, **kwargs):
    try:
        drive_service = build_drive_service()  # ❌ No credentials!
```
**Impact:** 403 Forbidden when exporting user presentations  
**Priority:** MEDIUM - Read operation

### 15. `google_slides_export_as_pptx` (line 1264)
```python
def google_slides_export_as_pptx(presentation_id, **kwargs):
    try:
        drive_service = build_drive_service()  # ❌ No credentials!
```
**Impact:** 403 Forbidden when exporting  
**Priority:** MEDIUM - Read operation

### 16. `google_slides_create_pitch_deck` (line 1299)
```python
def google_slides_create_pitch_deck(title, company_name, sections_data,
                                   brand_color='#4285F4', logo_url=None, **kwargs):
    # Calls google_slides_create_presentation (✅ works)
    # Then calls insert functions (✅ NOW work after today's fix)
```
**Impact:** NOW WORKING after insert function fixes  
**Status:** ✅ Depends on other functions (now fixed)

### 17. `google_slides_create_training_presentation` (line 1587)
**Impact:** NOW WORKING after insert function fixes  
**Status:** ✅ Depends on other functions (now fixed)

### 18. `google_slides_create_business_report` (line 1812)
**Impact:** NOW WORKING after insert function fixes  
**Status:** ✅ Depends on other functions (now fixed)

---

## Required Fixes

### HIGH PRIORITY (Core Operations - 6 functions)

1. **`google_slides_get_presentation`** - Fix credential extraction from kwargs
2. **`google_slides_add_slide`** - Add credential injection
3. **`google_slides_delete_slide`** - Add credential injection
4. **`google_slides_duplicate_slide`** - Add credential injection
5. **`google_slides_export_as_pdf`** - Add credential injection to build_drive_service
6. **`google_slides_export_as_pptx`** - Add credential injection to build_drive_service

### MEDIUM PRIORITY (Code Consistency - 2 functions)

7. **`google_slides_get_slide`** - Refactor to use `_get_slides_service()` helper
8. **`google_slides_search_presentation`** - Refactor to use `_get_slides_service()` helper

---

## Standard Pattern to Apply

All functions should follow this pattern:

```python
def function_name(params..., _user_id=None, _injected_credentials=None, **kwargs):
    """Function docstring"""
    try:
        # Get user OAuth credentials if available
        cred_dict = _get_user_credentials_if_available(_user_id, _injected_credentials)
        
        if cred_dict:
            slides_service = _get_slides_service(user_id=_user_id, injected_credentials=cred_dict)
        else:
            slides_service = _get_slides_service()
        
        # ... rest of function
```

For Drive service exports:
```python
def export_function(presentation_id, _user_id=None, _injected_credentials=None, **kwargs):
    """Export function"""
    try:
        # Get user OAuth credentials if available
        cred_dict = _get_user_credentials_if_available(_user_id, _injected_credentials)
        
        if cred_dict:
            drive_service = build_drive_service(user_id=_user_id, injected_credentials=cred_dict)
        else:
            drive_service = build_drive_service()
        
        # ... rest of function
```

---

## Testing Checklist

After fixes, test each function:

- [ ] `google_slides_get_presentation` - Read user presentation
- [ ] `google_slides_add_slide` - Add slide to user presentation  
- [ ] `google_slides_delete_slide` - Delete slide from user presentation
- [ ] `google_slides_duplicate_slide` - Duplicate slide in user presentation
- [ ] `google_slides_export_as_pdf` - Export user presentation to PDF
- [ ] `google_slides_export_as_pptx` - Export user presentation to PPTX
- [ ] `google_slides_get_slide` - Get single slide from user presentation
- [ ] `google_slides_search_presentation` - Search in user presentation

---

## Impact Assessment

### Before All Fixes:
- ❌ 13 of 17 functions broken or inconsistent
- ❌ Users cannot modify their presentations
- ❌ Only creation worked reliably

### After Insert Fix (commit dac28e0):
- ✅ 5 insert functions fixed
- ✅ Smart actions (pitch deck, training, business report) now work
- ⚠️ Still 6 core operations broken

### After Remaining Fixes:
- ✅ All 17 functions will work with user credentials
- ✅ Complete presentation editing capabilities
- ✅ Consistent codebase pattern
