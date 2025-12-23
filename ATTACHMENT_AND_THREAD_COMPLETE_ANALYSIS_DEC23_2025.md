# 📎 Email Attachment & Thread History - Complete Analysis

## 🎯 Quick Answers

### **Q1: Does it handle Word, Excel, PowerPoint?**
**Answer**: ⚠️ **Partially** - Detection works, but text extraction requires backend endpoints (not yet implemented)

### **Q2: Does it get full email thread or just last message?**
**Answer**: ✅ **FULL THREAD HISTORY** - System includes entire conversation chronologically

---

## 📄 Office Document Support (Word/Excel/PowerPoint)

### **Current Status**

| File Type | Detection | Text Extraction | Status |
|-----------|-----------|-----------------|--------|
| **Word (.doc, .docx)** | ✅ Works | ⚠️ Backend needed | Fallback: "Manual review required" |
| **Excel (.xls, .xlsx)** | ✅ Works | ⚠️ Backend needed | Fallback: "Manual review required" |
| **PowerPoint (.ppt, .pptx)** | ✅ Works | ⚠️ Backend needed | Fallback: "Manual review required" |
| **CSV** | ✅ Works | ✅ Works | **Fully supported** |

---

### **What Works Now**

**File Type Detection** (attachment-processor.js, lines 135-168):
```javascript
// Word Documents
if (mimetype.includes('word') || /\.(doc|docx)$/i.test(filename)) {
    return { category: 'document', specific: 'word' };
}

// Excel Spreadsheets
if (mimetype.includes('excel') || mimetype.includes('spreadsheet') || /\.(xls|xlsx)$/i.test(filename)) {
    return { category: 'spreadsheet', specific: 'excel' };
}

// PowerPoint
if (mimetype.includes('presentation') || /\.(ppt|pptx)$/i.test(filename)) {
    return { category: 'document', specific: 'powerpoint' };
}
```

**Result**: System correctly identifies file type and shows in UI with proper icons

---

### **What Needs Backend Implementation**

#### **Missing Flask Endpoints**

**1. Extract Word/PowerPoint Text**: `/extract-document-text`

**Frontend Request** (attachment-processor.js, lines 230-243):
```javascript
const response = await fetch(`${communicationHub.state.apiBase}/extract-document-text`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        email_id: emailId,
        attachment_id: attachment.id,
        user_id: userId,
        provider: attachment.provider || 'gmail'
    })
});
```

**Backend Implementation Needed**:
```python
# Flask endpoint required in AI_infrastructure/flask_app.py
@app.route('/extract-document-text', methods=['POST'])
def extract_document_text():
    """
    Extract text from Word/PowerPoint documents
    Supports: .docx, .pptx, .doc (via LibreOffice)
    """
    import docx  # python-docx library
    from pptx import Presentation  # python-pptx library
    import tempfile
    import os
    
    data = request.json
    email_id = data['email_id']
    attachment_id = data['attachment_id']
    user_id = data['user_id']
    provider = data.get('provider', 'gmail')
    
    # Download attachment from Gmail/Outlook
    if provider == 'gmail':
        attachment_data = gmail_get_attachment(email_id, attachment_id, _user_id=user_id)
    else:  # outlook
        attachment_data = outlook_get_attachment(email_id, attachment_id, user_id=user_id)
    
    # Detect file type from filename or mimetype
    filename = attachment_data.get('filename', '').lower()
    
    try:
        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
            tmp.write(attachment_data['data'])
            tmp_path = tmp.name
        
        # Extract text based on type
        if filename.endswith('.docx'):
            # Word document
            doc = docx.Document(tmp_path)
            text = '\n\n'.join([para.text for para in doc.paragraphs if para.text.strip()])
            
        elif filename.endswith('.pptx'):
            # PowerPoint presentation
            prs = Presentation(tmp_path)
            slides_text = []
            for slide_num, slide in enumerate(prs.slides, 1):
                slide_text = f"--- Slide {slide_num} ---\n"
                for shape in slide.shapes:
                    if hasattr(shape, 'text') and shape.text.strip():
                        slide_text += shape.text + '\n'
                slides_text.append(slide_text)
            text = '\n\n'.join(slides_text)
            
        elif filename.endswith('.doc'):
            # Legacy Word format - requires LibreOffice or antiword
            # Option 1: Use LibreOffice in headless mode
            import subprocess
            subprocess.run(['libreoffice', '--headless', '--convert-to', 'txt', tmp_path])
            txt_path = tmp_path.replace('.doc', '.txt')
            with open(txt_path, 'r', encoding='utf-8') as f:
                text = f.read()
            os.remove(txt_path)
        else:
            text = "Unsupported document format"
        
        # Cleanup temp file
        os.remove(tmp_path)
        
        # Limit to 50KB (50,000 characters)
        text = text[:50000]
        
        return jsonify({
            'success': True,
            'text': text,
            'char_count': len(text),
            'truncated': len(text) == 50000
        })
    
    except Exception as e:
        logger.error(f"Document text extraction failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
```

**Required Python Libraries**:
```bash
pip install python-docx      # For .docx files
pip install python-pptx      # For .pptx files
pip install openpyxl         # For .xlsx files (needed for Excel endpoint)
```

For legacy formats (.doc, .xls, .ppt):
```bash
# Option 1: Install LibreOffice (headless conversion)
sudo apt-get install libreoffice

# Option 2: Use antiword for .doc only
sudo apt-get install antiword
```

---

**2. Extract Excel Data**: `/extract-spreadsheet-text`

**Frontend Request** (attachment-processor.js, lines 282-294):
```javascript
const response = await fetch(`${communicationHub.state.apiBase}/extract-spreadsheet-text`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        email_id: emailId,
        attachment_id: attachment.id,
        user_id: userId,
        provider: attachment.provider || 'gmail'
    })
});
```

**Backend Implementation Needed**:
```python
@app.route('/extract-spreadsheet-text', methods=['POST'])
def extract_spreadsheet_text():
    """
    Extract data from Excel spreadsheets
    Converts to CSV-style table for AI consumption
    """
    import openpyxl  # For .xlsx files
    import xlrd      # For .xls files (legacy)
    import tempfile
    import os
    
    data = request.json
    email_id = data['email_id']
    attachment_id = data['attachment_id']
    user_id = data['user_id']
    provider = data.get('provider', 'gmail')
    
    # Download attachment
    if provider == 'gmail':
        attachment_data = gmail_get_attachment(email_id, attachment_id, _user_id=user_id)
    else:
        attachment_data = outlook_get_attachment(email_id, attachment_id, user_id=user_id)
    
    filename = attachment_data.get('filename', '').lower()
    
    try:
        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
            tmp.write(attachment_data['data'])
            tmp_path = tmp.name
        
        # Extract data based on format
        if filename.endswith('.xlsx'):
            # Modern Excel format
            wb = openpyxl.load_workbook(tmp_path, data_only=True)
            
            # Process all sheets
            sheets_text = []
            for sheet_name in wb.sheetnames:
                ws = wb[sheet_name]
                
                sheet_text = f"Sheet: {sheet_name}\n\n"
                
                # Get data (first 100 rows only)
                rows = []
                for row_num, row in enumerate(ws.iter_rows(values_only=True), 1):
                    if row_num > 100:  # Limit to 100 rows
                        break
                    # Filter out completely empty rows
                    if any(cell is not None for cell in row):
                        rows.append(','.join([str(cell) if cell is not None else '' for cell in row]))
                
                sheet_text += '\n'.join(rows)
                sheets_text.append(sheet_text)
            
            text = '\n\n---\n\n'.join(sheets_text)
            
        elif filename.endswith('.xls'):
            # Legacy Excel format
            wb = xlrd.open_workbook(tmp_path)
            
            sheets_text = []
            for sheet in wb.sheets():
                sheet_text = f"Sheet: {sheet.name}\n\n"
                
                rows = []
                for row_num in range(min(sheet.nrows, 100)):  # First 100 rows
                    row = sheet.row_values(row_num)
                    rows.append(','.join([str(cell) for cell in row]))
                
                sheet_text += '\n'.join(rows)
                sheets_text.append(sheet_text)
            
            text = '\n\n---\n\n'.join(sheets_text)
        else:
            text = "Unsupported spreadsheet format"
        
        # Cleanup
        os.remove(tmp_path)
        
        # Limit to 50KB
        text = text[:50000]
        
        return jsonify({
            'success': True,
            'text': text,
            'char_count': len(text),
            'truncated': len(text) == 50000
        })
    
    except Exception as e:
        logger.error(f"Spreadsheet extraction failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
```

---

### **Fallback Behavior (Current)**

When backend endpoints don't exist, system shows:

**Word Documents**:
```
[Document: requirements.docx - 245 KB]
Text extraction requires backend processing. Document should be downloaded and reviewed manually.
```

**Excel Files**:
```
[Spreadsheet: inventory.xlsx]
Data extraction requires backend processing. File should be downloaded for manual review.
```

**PowerPoint**:
```
[Document: presentation.pptx]
Text extraction not available. Manual review required.
```

**CSV Files** (Works without backend):
```
[CSV Spreadsheet: products.csv]

ProductID,Name,Price,Stock
001,Business Cards,250.00,500
002,A4 Flyers,180.00,1000
003,Booklets,450.00,200

[...remaining rows truncated...]
```

---

## 📧 Email Thread History - COMPLETE SUPPORT

### **Answer: System Gets FULL THREAD**

**How It Works**:

**Step 1: Email Formatter Checks for Thread History** (email-ai-formatter.js, lines 41-73)
```javascript
// Thread history (if available)
if (fullEmail.thread_history && fullEmail.thread_history.length > 0) {
    markdown.push('EMAIL THREAD HISTORY');
    markdown.push('');
    markdown.push('This email is part of an ongoing conversation. Messages are shown in chronological order (oldest first):');
    markdown.push('');

    fullEmail.thread_history.forEach((msg, index) => {
        markdown.push(`Message ${index + 1} of ${fullEmail.thread_history.length}`);
        markdown.push('');
        markdown.push(`From: ${msg.from || 'Unknown'}`);
        markdown.push(`Date: ${msg.date || 'Unknown'}`);
        markdown.push(`Subject: ${msg.subject || '(No Subject)'}`);
        markdown.push('');
        markdown.push('Content:');
        markdown.push('```');
        markdown.push(msg.body || '(No content)');
        markdown.push('```');
        markdown.push('');

        // Attachments for this message
        if (msg.attachments && msg.attachments.length > 0) {
            markdown.push('Attachments:');
            msg.attachments.forEach(att => {
                markdown.push(`- ${this.formatAttachment(att)}`);
            });
            markdown.push('');
        }

        markdown.push('---');
        markdown.push('');
    });
}
```

---

### **Gmail Thread Fetching**

**Backend Function**: `gmail_get_thread_parsed()` (google_workspace/gmail.py, lines 360-437)

```python
def gmail_get_thread_parsed(thread_id, max_messages=20, output_format='json', **kwargs):
    """
    Get entire email thread with timeline and parsed content
    
    This reconstructs conversation flow with:
    - Chronological message order
    - Participant list
    - Clean text for each message
    - Thread position markers
    
    Returns:
        {
            'thread_id': str,
            'subject': str,
            'participants': [{'name': str, 'email': str}],
            'start_date': str,
            'last_date': str,
            'message_count': int,
            'messages': [
                {
                    'position': 1,
                    'from': {'name': str, 'email': str},
                    'date': str,
                    'body_text': str,
                    'full_message_id': str
                }
            ]
        }
    """
    service = _get_gmail_service(**kwargs)
    
    # Get thread with all messages
    thread = service.users().threads().get(
        userId='me',
        id=thread_id,
        format='full'
    ).execute()
    
    messages = thread.get('messages', [])[:max_messages]
    
    # Parse each message chronologically
    parser = UniversalEmailParser()
    parsed_messages = [
        parser.parse_gmail_message(msg, download_attachments=True) 
        for msg in messages
    ]
    
    return parser.parse_email_thread_timeline(parsed_messages)
```

---

### **Example: Full Thread in AI Prompt**

**Email Thread**:
```
Message 1 (Dec 15, 2025):
From: john@example.com
Subject: Business Card Quote Request

Hi, I need a quote for 1000 business cards.

---

Message 2 (Dec 16, 2025):
From: sales@printshop.com
Subject: Re: Business Card Quote Request

Hi John, what size and paper type do you prefer?

---

Message 3 (Dec 17, 2025):
From: john@example.com
Subject: Re: Business Card Quote Request

Standard size (90mm x 55mm), 350gsm, matt finish please.
```

**AI Receives**:
```markdown
EMAIL THREAD HISTORY

This email is part of an ongoing conversation. Messages are shown in chronological order (oldest first):

Message 1 of 3

From: john@example.com
Date: 2025-12-15T09:30:00Z
Subject: Business Card Quote Request

Content:
```
Hi, I need a quote for 1000 business cards.
```

---

Message 2 of 3

From: sales@printshop.com
Date: 2025-12-16T10:15:00Z
Subject: Re: Business Card Quote Request

Content:
```
Hi John, what size and paper type do you prefer?
```

---

Message 3 of 3

From: john@example.com
Date: 2025-12-17T08:45:00Z
Subject: Re: Business Card Quote Request

Content:
```
Standard size (90mm x 55mm), 350gsm, matt finish please.
```

---

CURRENT EMAIL BODY
```
Standard size (90mm x 55mm), 350gsm, matt finish please.
```
```

**AI Response**:
```
I can see from your conversation that you need 1000 business cards with the following specifications:

- Size: 90mm x 55mm (standard business card)
- Paper: 350gsm
- Finish: Matt

Let me query the FRED database to check if you've ordered from us before...

[Queries customer history, finds previous order, generates quote]

Quote: $467.50 for 1000 business cards (350gsm matt celloglaze)
Based on your previous order from November 2025.
```

---

### **Where Thread History Comes From**

**Gmail API Call** (google_workspace/gmail.py, line 407-413):
```python
# Get thread with all messages
thread = service.users().threads().get(
    userId='me',
    id=thread_id,
    format='full'
).execute()

messages = thread.get('messages', [])[:max_messages]  # Up to 20 messages
```

**Outlook API Equivalent** (Microsoft_365_Connection/microsoft365_client.py, line 742):
```python
def get_thread_parsed(self, conversation_id, max_messages=20):
    """
    Outlook equivalent of Gmail's gmail_get_thread_parsed()
    Fetches all messages in conversation thread
    """
    # Fetches from Outlook Graph API
    response = self.graph_client.get(
        f'/me/messages?$filter=conversationId eq \'{conversation_id}\'&$top={max_messages}'
    )
    return parse_outlook_thread(response)
```

---

## 📊 Summary Table

### **Attachment Support Status**

| File Type | Detection | Processing | AI Access | Backend Required |
|-----------|-----------|------------|-----------|------------------|
| **Images (JPG, PNG, GIF)** | ✅ | ✅ Base64 encode | ✅ Messages API | No |
| **PDFs** | ✅ | ✅ Base64 encode | ✅ Messages API | No |
| **Text (TXT, JSON, MD)** | ✅ | ✅ Direct read | ✅ Text prompt | No |
| **CSV** | ✅ | ✅ Parse & format | ✅ Text prompt | No |
| **Word (.docx)** | ✅ | ⚠️ Needs endpoint | ⚠️ If extracted | **Yes** - `/extract-document-text` |
| **Excel (.xlsx)** | ✅ | ⚠️ Needs endpoint | ⚠️ If extracted | **Yes** - `/extract-spreadsheet-text` |
| **PowerPoint (.pptx)** | ✅ | ⚠️ Needs endpoint | ⚠️ If extracted | **Yes** - `/extract-document-text` |
| **Legacy (.doc, .xls, .ppt)** | ✅ | ⚠️ Needs LibreOffice | ⚠️ If extracted | **Yes** - LibreOffice + endpoints |
| **Archives (ZIP, RAR)** | ✅ | ❌ Not supported | ❌ | N/A - Security risk |

---

### **Thread History Support**

| Email Provider | Thread History | Max Messages | Implementation |
|----------------|----------------|--------------|----------------|
| **Gmail** | ✅ Full support | 20 messages | `gmail_get_thread_parsed()` |
| **Outlook** | ✅ Full support | 20 messages | `get_thread_parsed()` (Outlook) |
| **Format** | Chronological | Oldest → Newest | With message numbers |
| **Includes** | Body, attachments, dates | All participants | Full metadata |

---

## 🚀 Implementation Priority

### **High Priority** (Enables Office docs):
1. ✅ Implement `/extract-document-text` endpoint (Word/PowerPoint)
2. ✅ Implement `/extract-spreadsheet-text` endpoint (Excel)
3. ✅ Install required libraries: `python-docx`, `python-pptx`, `openpyxl`

### **Medium Priority** (Better quality):
4. ⚠️ Install LibreOffice for legacy formats (.doc, .xls, .ppt)
5. ⚠️ Add error handling for corrupted files
6. ⚠️ Add progress indicators for large file processing

### **Low Priority** (Nice to have):
7. ⚠️ OCR for scanned PDFs (image-based PDFs)
8. ⚠️ Archive extraction (ZIP files with auto-processing)
9. ⚠️ Video transcription (extract audio → Whisper)

---

## 📁 Related Files

**Attachment Processing**:
- [attachment-processor.js](c:\Users\gpoli\GIT\AI_agents\UI\modules_internal\communication-hub\attachment-processor.js) (506 lines)
- [email-ai-formatter.js](c:\Users\gpoli\GIT\AI_agents\UI\modules_internal\communication-hub\email-ai-formatter.js) (344 lines)

**Gmail Thread Functions**:
- [gmail.py](c:\Users\gpoli\GIT\AI_agents\google_workspace\gmail.py) - Lines 360-437 (`gmail_get_thread_parsed`)
- [gmail.py](c:\Users\gpoli\GIT\AI_agents\google_workspace\gmail.py) - Lines 728+ (`gmail_get_thread`)

**Backend Routes** (where to add endpoints):
- [communication_routes.py](c:\Users\gpoli\GIT\AI_agents\AI_infrastructure\routes\communication_routes.py)
- [flask_app.py](c:\Users\gpoli\GIT\AI_agents\AI_infrastructure\flask_app.py)

---

**Last Updated**: December 23, 2025  
**Status**: 
- ✅ Thread history fully working
- ⚠️ Office document extraction needs backend implementation
- ✅ CSV fully supported
- ✅ Images & PDFs fully supported
