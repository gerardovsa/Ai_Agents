# Email Footer & Signature Image Filtering

**Date:** January 4, 2026  
**Purpose:** Prevent email footer images and signature logos from appearing as "attachments" in AI responses

---

## 🎯 The Problem

Email signatures often contain embedded images (company logos, social media icons, photos) that:
- Show up as "attachments" in email tools
- Clutter the attachment list with non-relevant files
- Confuse users who expect only actual document attachments
- Waste tokens processing metadata for signature images

### Example: Neilson Communications Email
```
Amanda Fuller
Designer + Production Manager (BDes)

[PHOTO]  ← This is an inline image, not an attachment

T   07 3832 3500
E   amanda@neilsondesign.com.au
```

The `[PHOTO]` above would incorrectly appear as:
```json
{
  "filename": "Outlook-yokypezq.jpg",
  "size": 637900,
  "contentType": "image/jpeg"
}
```

---

## 🔍 How to Identify Email Footers/Signature Images

### Key Indicators:

1. **`isInline: true`** - Attachment is embedded in email HTML body
2. **`contentId` is set** - Has a Content-ID for HTML `<img>` reference
3. **`Content-Disposition: inline`** - Header indicates inline embedding
4. **Embedded in HTML** - Referenced via `<img src="cid:...">`

### Technical Details:

#### Outlook/Microsoft Graph API:
```json
{
  "@odata.type": "#microsoft.graph.fileAttachment",
  "id": "att123",
  "name": "signature.jpg",
  "contentType": "image/jpeg",
  "size": 50000,
  "isInline": true,              // ← KEY INDICATOR
  "contentId": "image001.jpg",   // ← KEY INDICATOR
  "contentBytes": "..."
}
```

#### Gmail API:
```json
{
  "partId": "1.2",
  "mimeType": "image/jpeg",
  "filename": "logo.png",
  "headers": [
    {
      "name": "Content-Disposition",
      "value": "inline"          // ← KEY INDICATOR
    },
    {
      "name": "Content-ID",
      "value": "<image001>"       // ← KEY INDICATOR
    }
  ],
  "body": {
    "attachmentId": "...",
    "size": 15000
  }
}
```

#### HTML Reference:
```html
<img src="cid:image001.jpg" width="200" height="50">
```

The `cid:` (Content-ID) reference links to the inline attachment.

---

## ✅ Filtering Implementation

### Files Modified:

1. **`tools/implementations/microsoft_outlook_tools.py`** (Line ~330)
2. **`AI_infrastructure/core/email_parser.py`** (Line ~240, ~363)

### Outlook Tool Filter:
```python
# Check if attachment is inline (email footer/signature)
is_inline = att.get('isInline', False)
has_content_id = att.get('contentId') is not None

if is_inline or has_content_id:
    continue  # Skip - don't include in attachment list
```

### Gmail Parser Filter:
```python
# Check Content-Disposition and Content-ID headers
for header in headers:
    header_name = header.get('name', '').lower()
    if header_name == 'content-disposition':
        content_disposition = header.get('value', '').lower()
    elif header_name == 'content-id':
        content_id = header.get('value')

# Skip if marked as inline or has Content-ID
if content_disposition and 'inline' in content_disposition:
    continue
if content_id:
    continue
```

---

## 📊 Attachment Types

### ✅ REAL Attachments (Keep):
- Documents: PDF, DOCX, XLSX, TXT
- Images attached by user: Screenshots, photos sent as files
- Archives: ZIP, RAR
- **Key trait:** `Content-Disposition: attachment` OR no Content-ID

### ❌ Inline Images (Filter Out):
- Company logos in signatures
- Social media icons
- Employee photos in signatures
- Email footer graphics
- **Key trait:** `isInline: true` OR `Content-ID` is set

---

## 🧪 Testing

### Test Case 1: Email with Real Attachments + Footer
```python
# Email has:
# - 1 PDF invoice (real attachment)
# - 1 company logo (inline signature)
# - 2 social media icons (inline footer)

result = microsoft_outlook_get_message(
    message_id='...',
    include_attachments=True
)

# Expected result:
attachments = result['message']['attachments']
assert len(attachments) == 1  # Only PDF, footers filtered out
assert attachments[0]['name'].endswith('.pdf')
```

### Test Case 2: Email with Only Footer Images
```python
# Email has:
# - 1 signature photo (inline)
# - 3 social media icons (inline)

result = microsoft_outlook_get_message(
    message_id='...',
    include_attachments=True
)

# Expected result:
attachments = result['message']['attachments']
assert len(attachments) == 0  # All inline, nothing to show
```

---

## 📝 Log Output

When filtering is active, you'll see:
```
🚀 [RENDER FIX] Stripped binary content from 2 attachment(s)
🎯 [INLINE FILTER] Excluded 3 inline attachment(s) (email footers/signatures)
```

This indicates:
- 2 real attachments kept (metadata only)
- 3 inline images filtered out

---

## 🎨 User Experience

### Before Filtering:
```
📧 Email from Amanda Fuller

ATTACHMENTS (5):
📎 Outlook-yokypezq.jpg (637.9 KB)  ← Email footer photo
📎 linkedin-icon.png (5 KB)         ← Social media icon
📎 twitter-icon.png (4 KB)          ← Social media icon
📎 company-logo.png (50 KB)         ← Footer logo
📎 invoice.pdf (1.2 MB)             ← Real attachment
```

### After Filtering:
```
📧 Email from Amanda Fuller

ATTACHMENTS (1):
📎 invoice.pdf (1.2 MB)
```

Much cleaner! Users only see actual document attachments.

---

## 🔧 Configuration

### Disable Filtering (if needed):
To temporarily disable inline filtering, modify the filter logic:

```python
# In microsoft_outlook_tools.py or email_parser.py
FILTER_INLINE_ATTACHMENTS = True  # Set to False to disable

if FILTER_INLINE_ATTACHMENTS and (is_inline or has_content_id):
    continue
```

### Adjust Filter Criteria:
You can make filtering more aggressive or lenient:

```python
# More aggressive (filter images < 100KB)
if is_inline or has_content_id or (size < 100000 and 'image/' in content_type):
    continue

# More lenient (only filter if explicitly inline AND has content_id)
if is_inline and has_content_id:
    continue
```

---

## 🐛 Edge Cases

### Case 1: User-Attached Screenshot with Content-ID
Some email clients set Content-ID on all images. Use size heuristic:
```python
# Don't filter large images even if inline
if (is_inline or has_content_id) and size < 500000:  # 500KB threshold
    continue
```

### Case 2: Inline Charts/Diagrams in Body
Business emails may have inline charts that should be kept:
```python
# Check filename patterns
common_footer_patterns = ['logo', 'icon', 'signature', 'photo', 'avatar']
is_likely_footer = any(pattern in filename.lower() for pattern in common_footer_patterns)

if (is_inline or has_content_id) and is_likely_footer:
    continue
```

---

## 📚 Standards Reference

- **RFC 2045:** MIME Content-Disposition header
- **RFC 2392:** Content-ID for MHTML and email
- **Microsoft Graph API:** `isInline` property documentation
- **Gmail API:** Message parts and headers structure

---

## ✅ Summary

**Problem:** Email footer images appearing as attachments  
**Solution:** Filter out attachments with `isInline: true` or `contentId` set  
**Result:** Cleaner attachment lists, better UX, fewer tokens wasted

**Files Changed:**
- [microsoft_outlook_tools.py](../tools/implementations/microsoft_outlook_tools.py#L330-L360)
- [email_parser.py](../AI_infrastructure/core/email_parser.py#L240-L270)

**Status:** ✅ COMPLETE - Deployed to all email tools
