# Quick Reference Card - File Processing with Content Blocks
**January 2, 2026** | Keep this handy for future development

---

## 🎯 The Golden Rule

**Content blocks are STRUCTURED DATA, not text strings!**

```python
# ❌ WRONG (causes token overflow)
content = json.dumps(result)  

# ✅ CORRECT (preserves structure)
if 'content_block' in result:
    content = [
        {'type': 'text', 'text': '...'},
        result['content_block']  # ← Keep as object!
    ]
```

---

## 📦 Content Block Format

### **For Images**:
```python
{
    'type': 'image',
    'source': {
        'type': 'base64',
        'media_type': 'image/jpeg',  # or png/gif/webp
        'data': '<base64_string>'
    }
}
```

### **For PDFs**:
```python
{
    'type': 'document',
    'source': {
        'type': 'base64',
        'media_type': 'application/pdf',
        'data': '<base64_string>'
    }
}
```

### **In Tool Results**:
```python
{
    'type': 'tool_result',
    'tool_use_id': 'toolu_123',
    'content': [
        {'type': 'text', 'text': '✅ Processed file.pdf'},
        {'type': 'document', 'source': {...}}  # ← Content block
    ]
}
```

---

## 🔧 Key Files

| File | Purpose | Key Method |
|------|---------|------------|
| **`email_attachment_tools.py`** | High-level API | `email_process_attachment_for_ai()` |
| **`universal_file_handler.py`** | File processing core | `process_file()` |
| **`tool_processor.py`** | Conversation builder | `build_tool_result_blocks()` ⚡ |
| **`microsoft_outlook_tools.py`** | Outlook API | `outlook_download_attachment()` |

---

## 📊 Token Cost Quick Reference

| File Type | Size | Old Method | New Method | Savings |
|-----------|------|------------|------------|---------|
| **PDF** | 691KB | 230,000 | ~800 | 99.65% |
| **Image** | 82KB | 27,000 | ~267 | 99.01% |
| **DOCX** | 2MB | N/A | ~1,500 | Fits! |

---

## 🚀 Usage Examples

### **Single File**:
```python
# AI calls this:
email_process_attachment_for_ai(
    source='outlook',
    message_id='AAMkAG...',
    attachment_id='AAMkAH...',
    mode='auto'
)

# Returns:
{
    'content_block': {'type': 'document', ...},
    'metadata': {'token_estimate': 800}
}
```

### **Multiple Files**:
```python
email_process_attachments_batch(
    source='gmail',
    attachments=[
        {'message_id': 'msg1', 'attachment_id': 'att1'},
        {'message_id': 'msg1', 'attachment_id': 'att2'}
    ]
)
```

---

## 🐛 Debugging Checklist

### **If AI tries `python_exec`**:
- ✅ Check system prompt has "EMAIL ATTACHMENT HANDLING" section
- ✅ Verify AI sees "YOU CAN NOW SEE THE PDF!" message
- ✅ Confirm content_block is in tool_result.content

### **If token overflow still happens**:
- ✅ Check logs: "📎 Including content_block"
- ✅ Verify AI called `email_process_attachment_for_ai` (not `outlook_download_attachment`)
- ✅ Inspect conversation JSON: content_block should be object, not string

### **If AI says "can't access file"**:
- ✅ Content block might be stringified
- ✅ Check `tool_processor.py` logic
- ✅ Verify `'content_block' in result` condition works

---

## 🎓 Remember

1. **Anthropic's API is stateless** - conversation history is on your side
2. **Content blocks persist** - available in all subsequent turns
3. **Multi-part content works** - text + content_block in same tool_result
4. **AI needs education** - system prompt must explain content blocks
5. **Test with real files** - don't assume it works without testing!

---

## 📞 Quick Commands

### **Test Compilation**:
```bash
python -m py_compile AI_infrastructure/core/tool_processor.py
```

### **Check Logs**:
```bash
Get-Content AI_infrastructure/flask_app.log -Tail 100 | Select-String "content_block"
```

### **Manual Test**:
```python
from AI_infrastructure.core.universal_file_handler import UniversalFileHandler
handler = UniversalFileHandler(user_id=1)
result = handler.process_file(
    source='outlook',
    source_id={'message_id': '...', 'attachment_id': '...'}
)
print(f"Tokens: {result['metadata']['token_estimate']}")
```

---

## ✅ Success Indicators

When everything works correctly, you'll see:

1. ✅ Logs: "📎 Including content_block for email_process_attachment_for_ai"
2. ✅ Token count ~800 (not 230K)
3. ✅ AI analyzes directly (no `python_exec`)
4. ✅ No "prompt is too long" errors
5. ✅ AI response includes file analysis

---

## 🎯 The Fix in One Line

**Old**: `content = json.dumps(result)` → Stringifies everything → Token overflow

**New**: `if 'content_block' in result: content = [text, content_block]` → Preserves structure → Success!

---

**Status**: ✅ **FIXED** - Ready for production testing

**Documentation**: 
- `FILE_PROCESSING_ARCHITECTURE.md` - Full technical reference
- `YOUR_QUESTIONS_ANSWERED_FILE_PROCESSING.md` - Q&A guide
- `COMPLETE_FIX_SUMMARY_JAN2_2026.md` - Implementation summary
- `architecture_diagram_content_blocks.svg` - Visual diagram
