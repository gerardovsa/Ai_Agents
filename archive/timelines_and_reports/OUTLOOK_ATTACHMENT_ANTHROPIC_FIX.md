# Outlook Attachment Token Overflow Fix - Complete Solution

**Problem**: Downloading Outlook attachments causes token overflow (237k tokens > 200k limit) because base64 content is too large for conversation history.

**Solution**: Implement THREE different attachment handling modes based on Anthropic's API capabilities.

---

## 🎯 Solution Overview

Anthropic's Messages API supports **three ways to send files**:

### Method 1: Direct Content Blocks (RECOMMENDED) ✅
- **Use Case**: Images (PNG, JPEG, GIF, WebP) and PDFs
- **Max Size**: 5MB per file, 100MB total request
- **Token Cost**: Efficient (images ~800 tokens, PDFs ~3000 tokens/page)
- **How**: Send base64 directly in content blocks

### Method 2: Upload Once, Reference Many ✅
- **Use Case**: Large files or repeated use
- **Max Size**: 100MB per file
- **Token Cost**: Very efficient (file_id is tiny)
- **How**: Upload to Anthropic Files API, then reference by ID

### Method 3: Upload to OneDrive, Send URL ✅
- **Use Case**: Non-PDF documents (DOCX, XLSX, etc.)
- **Max Size**: Unlimited
- **Token Cost**: Zero (URL only)
- **How**: Upload to OneDrive, create share link, AI downloads

---

## 📐 Architecture - Three-Mode Handler

```python
# tools/implementations/outlook_attachment_handler.py

class OutlookAttachmentHandler:
    """
    Smart attachment handler that chooses optimal method based on file type/size
    """
    
    ANTHROPIC_SUPPORTED_IMAGES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    ANTHROPIC_SUPPORTED_DOCUMENTS = ['application/pdf']
    
    # Size thresholds (in bytes)
    DIRECT_SEND_THRESHOLD = 5 * 1024 * 1024  # 5MB - send directly
    FILES_API_THRESHOLD = 100 * 1024 * 1024   # 100MB - use Files API
    # > 100MB → Use OneDrive
    
    def handle_attachment(self, message_id: str, attachment: Dict, mode: str = 'auto') -> Dict:
        """
        Smart handler that chooses best method based on file type and size
        
        Args:
            message_id: Email message ID
            attachment: Attachment metadata from outlook_get_attachments
            mode: 'auto' | 'direct' | 'files_api' | 'onedrive'
        
        Returns:
            {
                'method': 'direct' | 'files_api' | 'onedrive',
                'content_block': {...} | None,  # For direct/files_api
                'onedrive_url': str | None,     # For onedrive
                'metadata': {...}
            }
        """
        content_type = attachment.get('content_type')
        size = attachment.get('size', 0)
        name = attachment.get('name', 'unknown')
        
        # Auto-detect best method
        if mode == 'auto':
            if self._is_directly_sendable(content_type) and size < self.DIRECT_SEND_THRESHOLD:
                mode = 'direct'
            elif self._is_directly_sendable(content_type) and size < self.FILES_API_THRESHOLD:
                mode = 'files_api'
            else:
                mode = 'onedrive'
        
        # Execute chosen method
        if mode == 'direct':
            return self._handle_direct_send(message_id, attachment)
        elif mode == 'files_api':
            return self._handle_files_api(message_id, attachment)
        else:
            return self._handle_onedrive(message_id, attachment)
    
    def _is_directly_sendable(self, content_type: str) -> bool:
        """Check if Anthropic supports this content type"""
        return (content_type in self.ANTHROPIC_SUPPORTED_IMAGES or 
                content_type in self.ANTHROPIC_SUPPORTED_DOCUMENTS)
    
    def _handle_direct_send(self, message_id: str, attachment: Dict) -> Dict:
        """
        Method 1: Direct base64 in content block
        ✅ Best for small images/PDFs
        """
        # Download attachment content
        result = microsoft_outlook_download_attachment(
            message_id=message_id,
            attachment_id=attachment['id']
        )
        
        if not result['success']:
            return {'success': False, 'error': result.get('error')}
        
        content_type = result['content_type']
        base64_content = result['content']  # Already base64 from API
        
        # Build Anthropic content block
        if content_type in self.ANTHROPIC_SUPPORTED_DOCUMENTS:
            block_type = 'document'
        else:
            block_type = 'image'
        
        content_block = {
            'type': block_type,
            'source': {
                'type': 'base64',
                'media_type': content_type,
                'data': base64_content
            }
        }
        
        return {
            'success': True,
            'method': 'direct',
            'content_block': content_block,
            'metadata': {
                'name': result['name'],
                'size': result['size'],
                'type': content_type,
                'token_estimate': self._estimate_tokens(result['size'], block_type)
            }
        }
    
    def _handle_files_api(self, message_id: str, attachment: Dict) -> Dict:
        """
        Method 2: Upload to Anthropic Files API, reference by ID
        ✅ Best for large files (5-100MB) or repeated use
        """
        # Download attachment
        result = microsoft_outlook_download_attachment(
            message_id=message_id,
            attachment_id=attachment['id']
        )
        
        if not result['success']:
            return {'success': False, 'error': result.get('error')}
        
        # Decode base64 to bytes
        import base64
        file_bytes = base64.b64decode(result['content'])
        
        # Upload to Anthropic Files API
        file_upload_result = self._upload_to_anthropic_files(
            file_bytes=file_bytes,
            filename=result['name'],
            media_type=result['content_type']
        )
        
        if not file_upload_result['success']:
            return file_upload_result
        
        # Build content block with file reference
        file_id = file_upload_result['file_id']
        
        if result['content_type'] in self.ANTHROPIC_SUPPORTED_DOCUMENTS:
            block_type = 'document'
        else:
            block_type = 'image'
        
        content_block = {
            'type': block_type,
            'source': {
                'type': 'file',
                'file_id': file_id
            }
        }
        
        return {
            'success': True,
            'method': 'files_api',
            'content_block': content_block,
            'metadata': {
                'file_id': file_id,
                'name': result['name'],
                'size': result['size'],
                'type': result['content_type'],
                'token_estimate': 50  # File references are tiny
            }
        }
    
    def _handle_onedrive(self, message_id: str, attachment: Dict) -> Dict:
        """
        Method 3: Upload to OneDrive, send URL to AI
        ✅ Best for unsupported types (DOCX, XLSX) or huge files (>100MB)
        """
        # Download attachment
        result = microsoft_outlook_download_attachment(
            message_id=message_id,
            attachment_id=attachment['id']
        )
        
        if not result['success']:
            return {'success': False, 'error': result.get('error')}
        
        # Decode base64 to bytes
        import base64
        file_bytes = base64.b64decode(result['content'])
        
        # Upload to OneDrive
        onedrive_result = self._upload_to_onedrive(
            file_bytes=file_bytes,
            filename=result['name'],
            content_type=result['content_type']
        )
        
        if not onedrive_result['success']:
            return onedrive_result
        
        # Create shareable link
        share_result = microsoft_onedrive_create_share_link(
            item_id=onedrive_result['file_id'],
            share_type='view'
        )
        
        if not share_result['success']:
            return share_result
        
        return {
            'success': True,
            'method': 'onedrive',
            'onedrive_url': share_result['web_url'],
            'metadata': {
                'file_id': onedrive_result['file_id'],
                'name': result['name'],
                'size': result['size'],
                'type': result['content_type'],
                'download_url': share_result['web_url']
            }
        }
    
    def _upload_to_anthropic_files(self, file_bytes: bytes, filename: str, media_type: str) -> Dict:
        """Upload file to Anthropic Files API"""
        import anthropic
        
        client = anthropic.Anthropic(api_key=get_api_key_enhanced('ANTHROPIC'))
        
        try:
            # Create file-like object
            from io import BytesIO
            file_obj = BytesIO(file_bytes)
            file_obj.name = filename
            
            # Upload to Files API
            response = client.files.create(
                file=file_obj,
                purpose='messages'
            )
            
            return {
                'success': True,
                'file_id': response.id,
                'filename': filename,
                'size': len(file_bytes)
            }
        except Exception as e:
            return {'success': False, 'error': f'Files API upload failed: {str(e)}'}
    
    def _upload_to_onedrive(self, file_bytes: bytes, filename: str, content_type: str) -> Dict:
        """Upload file to OneDrive"""
        # Use existing OneDrive upload tool
        result = microsoft_onedrive_upload_file(
            file_path='Attachments/' + filename,
            file_content=file_bytes,
            content_type=content_type
        )
        return result
    
    def _estimate_tokens(self, file_size: int, block_type: str) -> int:
        """Estimate token count for content block"""
        if block_type == 'image':
            # Images: ~800 tokens for 1MB
            return int((file_size / 1_000_000) * 800)
        elif block_type == 'document':
            # PDFs: ~3000 tokens per page (estimate 500KB per page)
            pages = max(1, file_size / 500_000)
            return int(pages * 3000)
        return 0


# Global instance
outlook_attachment_handler = OutlookAttachmentHandler()
```

---

## 🔧 New Tool: Smart Attachment Processor

```python
def microsoft_outlook_process_attachment_for_ai(
    message_id: str,
    attachment_id: str,
    mode: str = 'auto',
    **kwargs
) -> Dict:
    """
    🚀 NEW TOOL - Smart attachment handler for AI consumption
    
    Automatically chooses the best method to send attachment to AI:
    - Small images/PDFs → Direct base64 content block
    - Large images/PDFs → Anthropic Files API
    - Other files → Upload to OneDrive, return URL
    
    Args:
        message_id: Email message ID
        attachment_id: Attachment ID from outlook_get_attachments
        mode: 'auto' (default), 'direct', 'files_api', or 'onedrive'
    
    Returns:
        {
            'success': True,
            'method': 'direct' | 'files_api' | 'onedrive',
            'content_block': {...} | None,  # Ready for AI message
            'url': str | None,              # For OneDrive method
            'metadata': {
                'name': 'Screenshot.png',
                'size': 81991,
                'type': 'image/png',
                'token_estimate': 800
            }
        }
    """
    # Get attachment metadata first
    attachments_result = microsoft_outlook_get_attachments(
        message_id=message_id,
        mode='detailed'
    )
    
    if not attachments_result['success']:
        return attachments_result
    
    # Find the specific attachment
    attachment = next(
        (a for a in attachments_result['attachments'] if a['id'] == attachment_id),
        None
    )
    
    if not attachment:
        return {'success': False, 'error': f'Attachment {attachment_id} not found'}
    
    # Use smart handler
    return outlook_attachment_handler.handle_attachment(message_id, attachment, mode)
```

---

## 📋 Tool Schema Update

```json
{
  "name": "microsoft_outlook_process_attachment_for_ai",
  "description": "🚀 Smart attachment processor for AI consumption - automatically chooses best method based on file type and size.\n\nUse this tool when:\n- User wants to analyze an email attachment\n- You need to send attachment content to Claude\n- Avoiding token overflow is critical\n\nThis tool automatically:\n1. Detects file type and size\n2. Chooses optimal method (direct, Files API, or OneDrive)\n3. Returns AI-ready content block OR URL\n4. Estimates token cost\n\nSupported methods:\n- Direct (< 5MB images/PDFs) → Base64 content block\n- Files API (5-100MB) → Upload once, reference by ID\n- OneDrive (> 100MB or unsupported types) → Upload, return URL\n\nExamples:\n- Small image → Direct base64 (800 tokens)\n- Large PDF → Files API reference (50 tokens)\n- DOCX → OneDrive URL (0 tokens)",
  "platform": "microsoft_outlook",
  "parameters": {
    "type": "object",
    "properties": {
      "message_id": {
        "type": "string",
        "description": "Email message ID"
      },
      "attachment_id": {
        "type": "string",
        "description": "Attachment ID from outlook_get_attachments"
      },
      "mode": {
        "type": "string",
        "enum": ["auto", "direct", "files_api", "onedrive"],
        "description": "Delivery mode:\n- 'auto' (default): Smart detection based on size/type\n- 'direct': Force base64 content block\n- 'files_api': Force Anthropic Files API upload\n- 'onedrive': Force OneDrive upload with URL",
        "default": "auto"
      }
    },
    "required": ["message_id", "attachment_id"]
  },
  "returns": {
    "type": "object",
    "description": "Processed attachment ready for AI",
    "properties": {
      "success": {"type": "boolean"},
      "method": {
        "type": "string",
        "enum": ["direct", "files_api", "onedrive"]
      },
      "content_block": {
        "type": "object",
        "description": "Anthropic content block (if direct or files_api)"
      },
      "url": {
        "type": "string",
        "description": "OneDrive URL (if onedrive method)"
      },
      "metadata": {
        "type": "object",
        "description": "File details and token estimate"
      }
    }
  }
}
```

---

## 🎯 Usage Workflow

### Scenario 1: User wants to analyze Sign Doctor email attachments

```python
# Step 1: List attachments (metadata only - lightweight)
attachments = execute_tool('microsoft_outlook_get_attachments',
    message_id='AAMkADMz...',
    mode='summary'  # ✅ Just names and sizes
)
# Returns:
# {
#   "count": 2,
#   "attachments": [
#     {"id": "att1", "name": "Screenshot1.png", "size": 96331},
#     {"id": "att2", "name": "Screenshot2.png", "size": 81991}
#   ]
# }

# Step 2: Process each attachment for AI (smart method selection)
attachment1 = execute_tool('microsoft_outlook_process_attachment_for_ai',
    message_id='AAMkADMz...',
    attachment_id='att1',
    mode='auto'  # ✅ Automatically chooses best method
)
# Returns:
# {
#   "method": "direct",
#   "content_block": {
#     "type": "image",
#     "source": {
#       "type": "base64",
#       "media_type": "image/png",
#       "data": "iVBORw0KGgo..."
#     }
#   },
#   "metadata": {
#     "token_estimate": 800  # ✅ Safe to include
#   }
# }

# Step 3: Send to Claude with content blocks
response = anthropic.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=4096,
    messages=[{
        "role": "user",
        "content": [
            attachment1['content_block'],  # ✅ Image content
            attachment2['content_block'],  # ✅ Second image
            {
                "type": "text",
                "text": "Analyze these screenshots from Sign Doctor email. What printing services are they requesting?"
            }
        ]
    }]
)
```

### Scenario 2: Large PDF attachment

```python
# Large PDF (15MB) - auto-switches to Files API
result = execute_tool('microsoft_outlook_process_attachment_for_ai',
    message_id='AAMkADMz...',
    attachment_id='large_pdf_id',
    mode='auto'
)
# Returns:
# {
#   "method": "files_api",
#   "content_block": {
#     "type": "document",
#     "source": {
#       "type": "file",
#       "file_id": "file_abc123"  # ✅ Tiny reference, 50 tokens
#     }
#   }
# }

# Send to Claude
response = anthropic.messages.create(
    messages=[{
        "role": "user",
        "content": [
            result['content_block'],  # ✅ File reference (50 tokens)
            {"type": "text", "text": "Summarize this contract"}
        ]
    }]
)
```

### Scenario 3: Word document (unsupported by Claude)

```python
# DOCX file - uploads to OneDrive
result = execute_tool('microsoft_outlook_process_attachment_for_ai',
    message_id='AAMkADMz...',
    attachment_id='word_doc_id',
    mode='auto'
)
# Returns:
# {
#   "method": "onedrive",
#   "url": "https://onedrive.live.com/view/abc123",
#   "metadata": {"name": "proposal.docx"}
# }

# Tell user about the file
"I've uploaded the Word document to OneDrive. Here's the link: [proposal.docx]({url})"
```

---

## ✅ Implementation Checklist

- [ ] Create `outlook_attachment_handler.py` implementation
- [ ] Add `microsoft_outlook_process_attachment_for_ai` tool
- [ ] Update `microsoft_outlook_tools.json` schema
- [ ] Implement Anthropic Files API integration
- [ ] Test with Sign Doctor email attachments
- [ ] Update conversation handling to use new tool
- [ ] Document token savings in README

---

## 🎉 Benefits

**Before** (current):
- ❌ 237k tokens (2 small images) → Overflow error
- ❌ Full base64 content in conversation history
- ❌ Manual OneDrive upload required

**After** (with smart handler):
- ✅ ~1,600 tokens (2 small images, direct method)
- ✅ OR ~100 tokens (2 images via Files API)
- ✅ OR 0 tokens (OneDrive URL method)
- ✅ Automatic method selection
- ✅ No token overflow ever

**Token Comparison**:
| Method | Small Image (96KB) | Large PDF (15MB) | DOCX (5MB) |
|--------|-------------------|------------------|------------|
| Current | 32,000 tokens ❌ | 500,000 tokens ❌ | Not supported ❌ |
| Direct | 800 tokens ✅ | N/A (too large) | N/A |
| Files API | 50 tokens ✅ | 50 tokens ✅ | N/A |
| OneDrive | 0 tokens ✅ | 0 tokens ✅ | 0 tokens ✅ |

---

## 📚 References

- [Anthropic Vision API](https://docs.anthropic.com/en/docs/build-with-claude/vision)
- [Anthropic PDF Support](https://docs.anthropic.com/en/docs/build-with-claude/pdf-support)
- [Anthropic Files API](https://docs.anthropic.com/en/api/files)
- `AI_agents/tools/implementations/microsoft_outlook_tools.py`
- `V7_MustCare/docs/PDF_TO_IMAGE_CONVERTER_IMPLEMENTATION.md`
- `In_House_SQL/FILE_ATTACHMENT_HTTP_400_FIX_OCT23.md`

---

**Status**: 📋 Design Complete - Ready for Implementation  
**Next Step**: Implement `outlook_attachment_handler.py` and test with Sign Doctor email
