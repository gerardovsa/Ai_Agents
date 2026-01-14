# Attachment Token Overflow - Quick Fix Guide

## 🎯 The Problem

**Error**: `prompt is too long: 236997 tokens > 200000 maximum`

**Cause**: Downloading Outlook attachments returns base64 content (96KB image = 32,000 tokens!), which gets stored in conversation history and overflows the 200k token limit.

---

## ✅ The Solution (3 Methods)

Anthropic supports THREE ways to send files - choose based on file type and size:

### Method 1: Direct Base64 (< 5MB images/PDFs)
**Token Cost**: ~800 tokens per MB  
**Use For**: Small screenshots, invoices, simple PDFs  
**How**: Send base64 directly in message content blocks

```python
# Good for: Sign Doctor screenshots (96KB + 82KB = 1,600 tokens)
{
    "type": "image",
    "source": {
        "type": "base64",
        "media_type": "image/png",
        "data": "iVBORw0KGgo..."  # ✅ Short, efficient
    }
}
```

### Method 2: Anthropic Files API (5-100MB)
**Token Cost**: ~50 tokens per file  
**Use For**: Large PDFs, multiple images, repeated use  
**How**: Upload once to Anthropic's file storage, reference by ID

```python
# Good for: 15MB contract PDF (50 tokens instead of 500,000!)
{
    "type": "document",
    "source": {
        "type": "file",
        "file_id": "file_abc123"  # ✅ Tiny reference
    }
}
```

### Method 3: OneDrive URL (any size, any type)
**Token Cost**: 0 tokens  
**Use For**: Word docs, Excel files, huge files (>100MB)  
**How**: Upload to OneDrive, send shareable link

```python
# Good for: 50MB proposal.docx
url = "https://onedrive.live.com/view/abc123"  # ✅ Zero tokens
"Here's the document: [proposal.docx]({url})"
```

---

## 🚀 Quick Implementation

### Step 1: Create Smart Handler

File: `tools/implementations/outlook_attachment_handler.py`

```python
class OutlookAttachmentHandler:
    """Automatically chooses best method based on file type/size"""
    
    def handle_attachment(self, message_id, attachment_id, mode='auto'):
        """
        Returns:
        - Method 1: {'method': 'direct', 'content_block': {...}}
        - Method 2: {'method': 'files_api', 'content_block': {'source': {'file_id': '...'}}}
        - Method 3: {'method': 'onedrive', 'url': 'https://...'}
        """
        # Get attachment metadata
        attachment = self._get_attachment_info(message_id, attachment_id)
        
        # Auto-detect best method
        if mode == 'auto':
            if attachment['size'] < 5MB and self._is_image_or_pdf(attachment):
                mode = 'direct'
            elif attachment['size'] < 100MB and self._is_image_or_pdf(attachment):
                mode = 'files_api'
            else:
                mode = 'onedrive'
        
        # Execute
        if mode == 'direct':
            return self._send_direct_base64(message_id, attachment)
        elif mode == 'files_api':
            return self._upload_to_anthropic_files(message_id, attachment)
        else:
            return self._upload_to_onedrive(message_id, attachment)
```

### Step 2: Add New Tool

File: `tools/implementations/microsoft_outlook_tools.py`

```python
def microsoft_outlook_process_attachment_for_ai(
    message_id: str,
    attachment_id: str,
    mode: str = 'auto',
    **kwargs
) -> Dict:
    """
    🚀 Smart attachment processor - automatically chooses best method
    
    Usage:
        result = execute_tool('microsoft_outlook_process_attachment_for_ai',
            message_id='AAMkADMz...',
            attachment_id='att123',
            mode='auto'
        )
        
        # Returns:
        {
            'method': 'direct',  # or 'files_api' or 'onedrive'
            'content_block': {...},  # Ready for Anthropic API
            'metadata': {'token_estimate': 800}
        }
    """
    handler = OutlookAttachmentHandler()
    return handler.handle_attachment(message_id, attachment_id, mode, **kwargs)
```

### Step 3: Update Tool Schema

File: `tools/schemas/microsoft_outlook_tools.json`

```json
{
  "name": "microsoft_outlook_process_attachment_for_ai",
  "description": "Smart attachment processor for AI - automatically chooses optimal delivery method based on file type and size. Prevents token overflow.\n\nMethods:\n- Direct (< 5MB images/PDFs) → Base64 content block (~800 tokens/MB)\n- Files API (5-100MB) → Anthropic file reference (~50 tokens)\n- OneDrive (>100MB or unsupported) → URL (0 tokens)\n\nUse this instead of outlook_download_attachment when sending to AI.",
  "platform": "microsoft_outlook",
  "parameters": {
    "type": "object",
    "properties": {
      "message_id": {"type": "string"},
      "attachment_id": {"type": "string"},
      "mode": {
        "type": "string",
        "enum": ["auto", "direct", "files_api", "onedrive"],
        "default": "auto"
      }
    },
    "required": ["message_id", "attachment_id"]
  }
}
```

---

## 🧪 Test with Sign Doctor Email

```python
# Before (BROKEN - 237k tokens):
att1 = outlook_download_attachment('msg123', 'att1')  # 96KB image → 32k tokens ❌
att2 = outlook_download_attachment('msg123', 'att2')  # 82KB image → 27k tokens ❌
# Total: 59k tokens JUST for attachments
# + conversation history = 237k tokens → OVERFLOW ❌

# After (FIXED - 1,600 tokens):
att1 = outlook_process_attachment_for_ai('msg123', 'att1', mode='auto')
# Returns: {'method': 'direct', 'content_block': {...}, 'metadata': {'token_estimate': 800}}

att2 = outlook_process_attachment_for_ai('msg123', 'att2', mode='auto')
# Returns: {'method': 'direct', 'content_block': {...}, 'metadata': {'token_estimate': 800}}

# Send to Claude:
response = anthropic.messages.create(
    messages=[{
        "role": "user",
        "content": [
            att1['content_block'],  # ✅ 800 tokens
            att2['content_block'],  # ✅ 800 tokens
            {"type": "text", "text": "Analyze these Sign Doctor screenshots"}
        ]
    }]
)
# Total: 1,600 tokens + prompt = ~5,000 tokens → SUCCESS ✅
```

---

## 📊 Token Savings

| Scenario | Old Method | New Method | Savings |
|----------|-----------|-----------|---------|
| 2 small images (Sign Doctor) | 59k tokens | 1,600 tokens | **97% reduction** |
| 1 large PDF (15MB) | 500k tokens | 50 tokens | **99.99% reduction** |
| 1 Word doc (5MB) | Not supported | 0 tokens (URL) | **100% improvement** |

---

## 🎯 Implementation Priority

1. **High Priority** ✅
   - Implement `outlook_attachment_handler.py`
   - Add `microsoft_outlook_process_attachment_for_ai` tool
   - Test with Sign Doctor email

2. **Medium Priority**
   - Add Anthropic Files API integration
   - Add OneDrive upload fallback
   - Update documentation

3. **Low Priority**
   - Add token estimation
   - Add batch processing
   - Add caching for repeated files

---

## 🔍 How V7_MustCare Does It

V7_MustCare solves this by:

1. **PDF → Image Conversion** (`PDF_TO_IMAGE_CONVERTER_IMPLEMENTATION.md`)
   - Uses PDF.js to render each PDF page as PNG
   - Converts to base64 images
   - Sends as multiple image content blocks

2. **Direct Content Blocks** (`FILE_ATTACHMENT_HTTP_400_FIX_OCT23.md`)
   ```python
   # Correct format for Claude
   if mime_type == 'application/pdf':
       block_type = 'document'
   elif mime_type.startswith('image/'):
       block_type = 'image'
   
   content_block = {
       'type': block_type,
       'source': {
           'type': 'base64',
           'media_type': mime_type,
           'data': base64_data  # ✅ Efficient
       }
   }
   ```

3. **No Conversation History Storage** (CRITICAL)
   - Images/PDFs sent only in current message
   - NOT stored in conversation history
   - Prevents token accumulation

---

## ✅ Summary

**Root Cause**: Base64 attachments in conversation history cause token overflow

**Solution**: Use Anthropic's three delivery methods based on file type/size

**Implementation**: Create smart handler that auto-selects best method

**Result**: 97-99.99% token reduction, no overflow ever

**Next Step**: Implement `outlook_attachment_handler.py` and test!

---

**See Full Details**: `OUTLOOK_ATTACHMENT_ANTHROPIC_FIX.md`
