# 📎 Email Attachment Processing Analysis - Communication Hub V4

## Overview

The Communication Hub V4 has a sophisticated **AttachmentProcessor** system that automatically downloads, analyzes, and prepares email attachments for AI consumption. It supports **multimodal AI analysis** using Claude's Vision and Messages API.

---

## 📁 File Type Categories & Handling

### **1. Images 📷 (Fully AI-Accessible)**

**Supported Formats**:
- JPG/JPEG, PNG, GIF, BMP, WebP, SVG

**Processing**:
```javascript
// Detection
if (mimetype.startsWith('image/') || /\.(jpg|jpeg|png|gif|bmp|webp|svg)$/i.test(filename))
```

**How It's Handled**:
1. **Download**: Fetches image from Gmail/Outlook API
2. **Size Check**: Ensures image is under **5MB** (Messages API limit)
3. **Base64 Encoding**: Converts image to base64 for Messages API
4. **Multimodal Message**: Embeds image directly in AI message

**AI Access**:
```javascript
processed.ai_accessible = true;
processed.image_data = {
    type: 'base64',
    media_type: 'image/jpeg',  // Original mimetype
    data: 'iVBORw0KGgoAAAANS...'  // Base64 encoded image
};
processed.ai_note = 'Image encoded as base64 for Messages API analysis';
```

**Claude Message Format**:
```javascript
contentBlocks.push({
    type: 'image',
    source: {
        type: 'base64',
        media_type: 'image/jpeg',
        data: att.image_data.data
    }
});
contentBlocks.push({
    type: 'text',
    text: `[Image: screenshot.png - 2.3 MB]
Please analyze this image in the context of the email above.`
});
```

**What AI Can Do**:
✅ Read text in images (OCR)
✅ Identify objects, logos, brands
✅ Describe charts, graphs, diagrams
✅ Analyze screenshots of websites, apps
✅ Read handwritten notes (if legible)
✅ Detect colors, layouts, designs

**Example**: Email says "See attached mockup" → AI views image → Responds: "The mockup shows a modern website with blue navigation bar, hero image, and 3-column layout. I recommend..."

---

### **2. PDF Documents 📄 (Fully AI-Accessible)**

**Supported Formats**:
- PDF files only

**Processing**:
```javascript
// Detection
if (mimetype.includes('pdf') || filename.endsWith('.pdf'))
```

**How It's Handled**:
1. **Download**: Fetches PDF from Gmail/Outlook API
2. **Size Check**: Ensures PDF is under **4.5MB** (Messages API document limit)
3. **Base64 Encoding**: Converts PDF to base64
4. **Document Message**: Embeds PDF in AI message using Messages API

**AI Access**:
```javascript
processed.ai_accessible = true;
processed.document_data = {
    type: 'base64',
    media_type: 'application/pdf',
    data: 'JVBERi0xLjQKJeLjz9...'
};
processed.ai_note = 'PDF encoded as base64 for Messages API document analysis';
```

**Claude Message Format**:
```javascript
contentBlocks.push({
    type: 'document',
    source: {
        type: 'base64',
        media_type: 'application/pdf',
        data: att.document_data.data
    }
});
contentBlocks.push({
    type: 'text',
    text: `[PDF Document: quote_request.pdf - 1.8 MB]
Please analyze this document and extract relevant information.`
});
```

**What AI Can Do**:
✅ Extract text from PDF pages
✅ Read tables and data
✅ Understand document structure
✅ Extract quote specifications from PDF forms
✅ Read scanned documents (OCR capability)
✅ Summarize multi-page documents

**Example**: Email says "Quote details in attached PDF" → AI reads PDF → Extracts: "Customer wants 1000 business cards, 90mm x 55mm, 350gsm, matt celloglaze"

---

### **3. Text Files 📝 (Fully AI-Accessible)**

**Supported Formats**:
- TXT, MD (Markdown), JSON, XML, HTML, CSS, JS

**Processing**:
```javascript
// Detection
if (mimetype.startsWith('text/') || /\.(txt|md|json|xml|html|css|js)$/i.test(filename))
```

**How It's Handled**:
1. **Direct Download**: Fetches as plain text
2. **Size Limit**: Truncates to **50KB** (50,000 characters) for AI processing
3. **Text Extraction**: Reads file contents as string
4. **Text Prompt**: Includes content in markdown code blocks

**AI Access**:
```javascript
processed.ai_accessible = true;
processed.text_content = 'File contents here...';
processed.processing_status = 'success';
```

**Prompt Format**:
```markdown
### Attachment 1: notes.txt

**Extracted Content**:
```
Meeting notes from Dec 20:
- Customer wants business cards
- Urgent delivery needed
- Budget: $500
```

**What AI Can Do**:
✅ Read plain text notes
✅ Parse JSON data structures
✅ Analyze code files (HTML, CSS, JavaScript)
✅ Extract information from logs
✅ Read configuration files

**Example**: Email says "See notes.txt for requirements" → AI reads file → Extracts requirements → Generates quote

---

### **4. Word Documents 📃 (Partially AI-Accessible)**

**Supported Formats**:
- DOC, DOCX (Microsoft Word)

**Processing**:
```javascript
// Detection
if (mimetype.includes('word') || /\.(doc|docx)$/i.test(filename))
```

**How It's Handled**:
1. **Backend API Call**: Attempts `/extract-document-text` endpoint
2. **Text Extraction**: If backend available, extracts text from Word document
3. **Size Limit**: Truncates to **50KB**
4. **Fallback**: If extraction fails, notes manual review needed

**AI Access**:
```javascript
processed.ai_accessible = true;  // If extraction succeeds
processed.text_content = 'Extracted Word document text...';
// OR
processed.text_content = `[Document: requirements.docx - 245 KB]
Text extraction requires backend processing. Document should be downloaded and reviewed manually.`;
```

**Backend Requirement**:
- Requires Flask endpoint: `/extract-document-text`
- Uses libraries like `python-docx` or `mammoth` for extraction

**What AI Can Do** (if extraction works):
✅ Read text from Word documents
✅ Extract requirements, specifications
✅ Summarize document contents
❌ Cannot view formatting, images in Word docs
❌ Cannot access embedded objects

**Current Status**: ⚠️ Backend extraction endpoint may not be implemented yet

---

### **5. Excel Spreadsheets 📊 (Partially AI-Accessible)**

**Supported Formats**:
- XLS, XLSX (Microsoft Excel)
- CSV (Comma-separated values)

**Processing**:
```javascript
// Detection - Excel
if (mimetype.includes('excel') || mimetype.includes('spreadsheet') || /\.(xls|xlsx)$/i.test(filename))

// Detection - CSV
if (mimetype.includes('csv') || filename.endsWith('.csv'))
```

**How It's Handled**:

**CSV Files** (Fully Supported):
1. **Direct Download**: Reads CSV as plain text
2. **Table Formatting**: Converts to readable table format
3. **Row Limit**: First **100 rows** only
4. **Text Prompt**: Includes formatted table

**Excel Files** (Requires Backend):
1. **Backend API Call**: Attempts `/extract-spreadsheet-text` endpoint
2. **Data Extraction**: If backend available, converts Excel to text
3. **Fallback**: Notes manual review needed

**AI Access** (CSV):
```javascript
processed.ai_accessible = true;
processed.text_content = `[CSV Spreadsheet: products.csv]

ProductID,Name,Price,Stock
001,Business Cards,250.00,500
002,A4 Flyers,180.00,1000
003,Booklets,450.00,200

[...remaining rows truncated...]`;
```

**AI Access** (Excel - if backend works):
```javascript
processed.ai_accessible = true;
processed.text_content = 'Extracted Excel data...';
// OR
processed.text_content = `[Spreadsheet: inventory.xlsx]
Data extraction requires backend processing. File should be downloaded for manual review.`;
```

**What AI Can Do**:
✅ Read CSV data tables
✅ Analyze product lists, pricing
✅ Extract quote specifications from spreadsheets
❌ Cannot read Excel formulas (only values)
❌ Cannot view charts/graphs in Excel

**Current Status**: 
- ✅ CSV fully supported
- ⚠️ Excel requires backend endpoint `/extract-spreadsheet-text`

---

### **6. PowerPoint Presentations 📊 (Backend Required)**

**Supported Formats**:
- PPT, PPTX (Microsoft PowerPoint)

**Processing**:
```javascript
// Detection
if (mimetype.includes('presentation') || /\.(ppt|pptx)$/i.test(filename))
```

**How It's Handled**:
1. **Backend API Call**: Attempts `/extract-document-text` endpoint
2. **Slide Text Extraction**: If backend available, extracts text from slides
3. **Fallback**: Notes manual review needed

**AI Access**:
```javascript
processed.ai_accessible = true;  // If extraction works
processed.text_content = 'Extracted PowerPoint text...';
// OR
processed.text_content = `[Document: presentation.pptx]
Text extraction not available. Manual review required.`;
```

**What AI Can Do** (if extraction works):
✅ Read text from PowerPoint slides
❌ Cannot view slide images, charts
❌ Cannot understand slide layouts

**Current Status**: ⚠️ Requires backend extraction

---

### **7. Archive Files 📦 (Not AI-Accessible)**

**Supported Formats**:
- ZIP, RAR, 7Z, TAR, GZ

**Processing**:
```javascript
// Detection
if (/\.(zip|rar|7z|tar|gz)$/i.test(filename))
```

**How It's Handled**:
1. **Detection Only**: System identifies as archive
2. **No Extraction**: Archives are NOT automatically unpacked
3. **Manual Download**: User must download and extract manually

**AI Access**:
```javascript
processed.ai_accessible = false;
processed.processing_status = 'archive_not_supported';
processed.ai_note = 'Archive files must be extracted manually. Contains multiple files.';
```

**What AI Sees**:
```markdown
### Attachment 3: project_files.zip

- **Type**: zip (archive)
- **Size**: 15.2 MB
- **AI Accessible**: No ✗
- **Processing Status**: archive_not_supported
- **Note**: Archive files must be extracted manually. Contains multiple files.
```

**Why Not Supported**:
- Archives can contain dozens/hundreds of files
- Unknown file types inside
- Security risk (could contain executables)
- Too large for AI context window

---

### **8. Unknown File Types ❓ (Not AI-Accessible)**

**Examples**:
- EXE, DLL (executables)
- DAT, BIN (binary files)
- Custom proprietary formats

**Processing**:
```javascript
// Detection (fallback)
return { category: 'unknown', specific: 'unknown' };
```

**How It's Handled**:
1. **Detection Only**: System flags as unknown
2. **No Processing**: No extraction attempted
3. **Manual Download**: User must handle manually

**AI Access**:
```javascript
processed.ai_accessible = false;
processed.processing_status = 'unknown_type';
processed.ai_note = 'File type not recognized for automatic processing.';
```

---

## 🔄 Processing Workflow

### **Step 1: Email Arrives with Attachments**
```javascript
email.attachments = [
    {
        id: 'att-12345',
        filename: 'quote_request.pdf',
        mimetype: 'application/pdf',
        size: 1847203,  // 1.8 MB
        provider: 'gmail'
    },
    {
        id: 'att-67890',
        filename: 'mockup.png',
        mimetype: 'image/png',
        size: 2415600,  // 2.4 MB
        provider: 'gmail'
    }
];
```

---

### **Step 2: User Clicks "Send to AI Agent"**
Communication Hub calls:
```javascript
const processedAttachments = await AttachmentProcessor.processAttachmentsForAI(
    emailId,
    email.attachments,
    communicationHub
);
```

---

### **Step 3: Attachment Processing Loop**

For each attachment:

**3a. File Type Detection**:
```javascript
const type = AttachmentProcessor.detectFileType(attachment);
// Returns: { category: 'pdf', specific: 'pdf' }
// OR: { category: 'image', specific: 'png' }
```

**3b. Download & Process** (based on type):

**Images**:
```javascript
// Download image
const response = await fetch(`/gmail/attachment?message_id=${emailId}&attachment_id=att-67890`);
const blob = await response.blob();

// Check size (5MB limit)
if (blob.size > 5 * 1024 * 1024) return null;

// Convert to base64
const reader = new FileReader();
reader.readAsDataURL(blob);
// Returns: 'data:image/png;base64,iVBORw0KG...'
```

**PDFs**:
```javascript
// Download PDF
const response = await fetch(`/gmail/attachment?message_id=${emailId}&attachment_id=att-12345`);
const blob = await response.blob();

// Check size (4.5MB limit)
if (blob.size > 4.5 * 1024 * 1024) return null;

// Convert to base64
const reader = new FileReader();
reader.readAsDataURL(blob);
// Returns: 'data:application/pdf;base64,JVBERi0xL...'
```

**Text Files**:
```javascript
// Download as text
const response = await fetch(`/gmail/attachment?message_id=${emailId}&attachment_id=att-45678`);
const text = await response.text();

// Truncate to 50KB
return text.substring(0, 50000);
```

**CSV Files**:
```javascript
// Download CSV
const csvText = await response.text();

// Format as table (first 100 rows)
const rows = csvText.split('\n').slice(0, 100);
return `[CSV Spreadsheet: products.csv]\n\n${rows.join('\n')}\n\n[...remaining rows truncated...]`;
```

---

### **Step 4: Build Processed Attachment Objects**

```javascript
processedAttachments = [
    {
        id: 'att-12345',
        filename: 'quote_request.pdf',
        mimetype: 'application/pdf',
        size: 1847203,
        detected_type: 'pdf',
        file_type: 'pdf',
        processing_status: 'success',
        ai_accessible: true,
        document_data: {
            type: 'base64',
            media_type: 'application/pdf',
            data: 'JVBERi0xLjQKJeLjz9...'
        },
        ai_note: 'PDF encoded as base64 for Messages API document analysis',
        download_url: '/gmail/attachment?message_id=...'
    },
    {
        id: 'att-67890',
        filename: 'mockup.png',
        mimetype: 'image/png',
        size: 2415600,
        detected_type: 'image',
        file_type: 'png',
        processing_status: 'success',
        ai_accessible: true,
        image_data: {
            type: 'base64',
            media_type: 'image/png',
            data: 'iVBORw0KGgoAAAANS...'
        },
        ai_note: 'Image encoded as base64 for Messages API analysis',
        download_url: '/gmail/attachment?message_id=...'
    }
];
```

---

### **Step 5: Generate AI Prompt with Attachments**

**5a. Text Summary** (added to prompt):
```javascript
const attachmentSummary = AttachmentProcessor.generateAttachmentSummary(processedAttachments);
```

Returns:
```markdown
## ATTACHMENTS SUMMARY

Total attachments: 2
- Images: 1 (included inline for visual analysis)
- PDF Documents: 1 (included inline for document analysis)

### Attachment 1: quote_request.pdf

- **Type**: pdf (pdf)
- **Size**: 1.8 MB
- **AI Accessible**: Yes ✓
- **Processing Status**: success
- **Download URL**: `/gmail/attachment?message_id=...`
- **Note**: PDF encoded as base64 for Messages API document analysis

---

### Attachment 2: mockup.png

- **Type**: png (image)
- **Size**: 2.4 MB
- **AI Accessible**: Yes ✓
- **Processing Status**: success
- **Download URL**: `/gmail/attachment?message_id=...`
- **Note**: Image encoded as base64 for Messages API analysis

**📷 IMAGE INCLUDED**: This image has been embedded in the message for you to analyze visually.
Please examine the image carefully and describe what you see in relation to the email context.

---
```

**5b. Multimodal Message** (sent to Claude):
```javascript
const messageContent = EmailAIFormatter.generateClaudeMessageContent(
    basePrompt + attachmentSummary,
    processedAttachments
);
```

Returns:
```javascript
[
    {
        type: 'text',
        text: '[Full email prompt with attachment summary above]'
    },
    {
        type: 'document',
        source: {
            type: 'base64',
            media_type: 'application/pdf',
            data: 'JVBERi0xLjQKJeLjz9...'
        }
    },
    {
        type: 'text',
        text: '\n[PDF Document: quote_request.pdf - 1.8 MB]\nPlease analyze this document and extract relevant information.\n'
    },
    {
        type: 'image',
        source: {
            type: 'base64',
            media_type: 'image/png',
            data: 'iVBORw0KGgoAAAANS...'
        }
    },
    {
        type: 'text',
        text: '\n[Image: mockup.png - 2.4 MB]\nPlease analyze this image in the context of the email above.\n'
    }
]
```

---

### **Step 6: Send to Claude API**

```javascript
const response = await anthropic.messages.create({
    model: 'claude-3-5-sonnet-20241022',
    max_tokens: 4096,
    messages: [
        {
            role: 'user',
            content: messageContent  // Array with text + images + documents
        }
    ]
});
```

Claude receives:
- Email text with attachment summary
- PDF document (can read text from PDF)
- Image (can analyze visually)

Claude responds:
```
I've analyzed the email and attachments:

**Quote Request PDF Analysis**:
The PDF contains a quote request form for 1000 business cards with the following specifications:
- Size: 90mm x 55mm (standard)
- Paper: 350gsm Satin stock
- Finish: Matt celloglaze on front side
- Delivery: Required by December 30, 2025

**Mockup Image Analysis**:
The mockup shows a business card design with:
- Company logo in top-left corner (blue and white)
- Contact details centered
- Modern minimalist layout
- Clean typography

I'll now generate a quote using the calculate_premium_business_cards_shopify calculator...
```

---

## 📊 Attachment Processing Summary Table

| File Type | Example | AI Accessible | How Processed | Backend Required | Size Limit | Claude API Support |
|-----------|---------|---------------|---------------|------------------|------------|-------------------|
| **Images** | JPG, PNG, GIF | ✅ Yes | Base64 encode | No | 5 MB | Messages API (image) |
| **PDF** | PDF | ✅ Yes | Base64 encode | No | 4.5 MB | Messages API (document) |
| **Text** | TXT, MD, JSON | ✅ Yes | Direct read | No | 50 KB | Text prompt |
| **CSV** | CSV | ✅ Yes | Direct read + format | No | 50 KB | Text prompt |
| **Word** | DOC, DOCX | ⚠️ Partial | Text extraction | Yes | 50 KB | Text prompt (if extracted) |
| **Excel** | XLS, XLSX | ⚠️ Partial | Data extraction | Yes | 50 KB | Text prompt (if extracted) |
| **PowerPoint** | PPT, PPTX | ⚠️ Partial | Text extraction | Yes | 50 KB | Text prompt (if extracted) |
| **Archives** | ZIP, RAR | ❌ No | Detection only | N/A | N/A | Not supported |
| **Unknown** | EXE, DAT | ❌ No | Detection only | N/A | N/A | Not supported |

---

## 🛠️ Backend API Endpoints Required

### **Currently Implemented**:
✅ `/gmail/attachment` - Download Gmail attachments
✅ `/outlook/attachment` - Download Outlook attachments

### **Required for Full Support**:
⚠️ `/extract-document-text` - Extract text from Word/PowerPoint
⚠️ `/extract-spreadsheet-text` - Extract data from Excel files
⚠️ `/extract-pdf-text` - Extract text from PDFs (optional, Messages API handles this)

### **Backend Implementation Example** (Flask):

```python
@app.route('/extract-document-text', methods=['POST'])
def extract_document_text():
    """Extract text from Word/PowerPoint documents"""
    data = request.json
    email_id = data['email_id']
    attachment_id = data['attachment_id']
    provider = data.get('provider', 'gmail')
    
    # Download attachment
    file_content = download_attachment(email_id, attachment_id, provider)
    
    # Extract text based on type
    if file_content.endswith('.docx'):
        import docx
        doc = docx.Document(file_content)
        text = '\n'.join([para.text for para in doc.paragraphs])
    elif file_content.endswith('.pptx'):
        from pptx import Presentation
        prs = Presentation(file_content)
        text = '\n'.join([shape.text for slide in prs.slides for shape in slide.shapes if hasattr(shape, 'text')])
    
    return jsonify({'text': text[:50000]})  # Limit to 50KB
```

---

## 🔐 Security Considerations

### **Size Limits** (Prevent Memory Overflow):
- Images: **5 MB** (Messages API limit)
- PDFs: **4.5 MB** (Messages API document limit)
- Text files: **50 KB** (50,000 characters)
- CSV files: **100 rows** only

### **File Type Restrictions**:
- ❌ **No executables** (EXE, DLL, BAT, SH)
- ❌ **No archives** (ZIP, RAR) - unpredictable contents
- ❌ **No unknown types** - manual review required

### **Download Security**:
- URLs include user authentication: `user_id=${userId}`
- Provider-specific endpoints (Gmail/Outlook separate)
- Error handling for failed downloads

---

## 🎯 Real-World Examples

### **Example 1: Quote Request with PDF Specifications**

**Email**:
```
Subject: Quote Request - Business Cards
From: sarah@abcprinting.com.au

Hi, please quote on the attached specifications.
We need this urgently by end of month.

Attachments:
- quote_specs.pdf (specifications form)
```

**AI Processing**:
1. Downloads `quote_specs.pdf` (2.1 MB)
2. Encodes as base64
3. Sends to Claude with Messages API document support
4. Claude reads PDF → Extracts: 1000 business cards, 90mm x 55mm, 350gsm matt cello
5. Queries FRED database for customer history (if needed)
6. Runs `calculate_premium_business_cards_shopify()`
7. Generates quote: "$467.50 for 1000 cards as per PDF specifications"

---

### **Example 2: Design Approval with Image**

**Email**:
```
Subject: Please review this mockup
From: client@example.com

What do you think of this design?
Can you print this on business cards?

Attachments:
- business_card_mockup.png (design image)
```

**AI Processing**:
1. Downloads `business_card_mockup.png` (1.8 MB)
2. Encodes as base64 for Messages API
3. Claude analyzes image:
   - Identifies logo, text layout
   - Notes dimensions (if shown in mockup)
   - Checks if design is print-ready
4. Responds: "The mockup looks great! It shows a 90mm x 55mm design with your logo and contact details. For best print quality, I recommend 350gsm satin stock with matt celloglaze. Would you like a quote for 500 or 1000 cards?"

---

### **Example 3: Product List in CSV**

**Email**:
```
Subject: Bulk printing quote request
From: marketing@company.com

We need quotes for all products in the attached list.

Attachments:
- print_products.csv (product list with quantities)
```

**AI Processing**:
1. Downloads `print_products.csv`
2. Reads as text, formats first 100 rows:
   ```
   Product,Quantity,Size,Paper
   Business Cards,1000,90x55mm,350gsm
   A4 Flyers,5000,A4,200gsm
   Booklets,500,A5-24pages,150gsm
   ```
3. Claude parses CSV data
4. For each product:
   - Selects appropriate calculator
   - Generates individual quote
5. Returns: "Bulk quote for 3 products: Business Cards $467.50, A4 Flyers $1,250.00, Booklets $2,800.00. Total: $4,517.50"

---

### **Example 4: Screenshot of Website**

**Email**:
```
Subject: Can you recreate this design?
From: prospect@newbusiness.com

We saw this on a competitor's site. Can you print similar?

Attachments:
- competitor_business_card.jpg (photo of card)
```

**AI Processing**:
1. Downloads `competitor_business_card.jpg`
2. Claude AI analyzes image:
   - Reads text on card (OCR)
   - Identifies paper finish (glossy/matt)
   - Notes colors, fonts, layout
3. Responds: "I can see this is a glossy business card with spot UV finish on the logo. The dimensions appear to be standard 90mm x 55mm. We can recreate this design with our premium business cards. Would you like a quote? Also, I recommend spot UV on your logo for that premium look - adds $75 to the order."

---

## 📈 Processing Status Codes

| Status | Meaning | User Action |
|--------|---------|-------------|
| `success` | AI can access content | None - fully processed |
| `pending` | Processing not started | Wait for processing |
| `no_content` | Empty file | Check if file is valid |
| `requires_extraction` | Backend needed | Contact admin to enable endpoint |
| `download_failed` | Download error | Retry or check permissions |
| `archive_not_supported` | Archive detected | Extract manually |
| `unknown_type` | Unrecognized format | Manual review required |
| `failed` | Processing error | Check logs, retry |

---

## 🚀 Future Enhancements

### **Planned Features**:
1. **Archive Auto-Extraction**: Unzip archives, process individual files
2. **Video Transcription**: Extract audio from videos, transcribe with Whisper
3. **Audio Processing**: Transcribe voice notes, audio memos
4. **OCR for Scanned PDFs**: Enhanced text extraction from image-based PDFs
5. **Spreadsheet Formula Analysis**: Not just values, but understand calculations
6. **Large File Chunking**: Process 20MB+ files in chunks

### **AI Improvements**:
1. **Smart File Matching**: "The PDF mentions Order #12345" → Auto-query FRED for that order
2. **Design Analysis**: "This business card uses Pantone 286 Blue" → Match to closest stock color
3. **Specification Extraction**: Automatically fill calculator parameters from attachments
4. **Multi-Attachment Correlation**: "Image shows mockup, PDF has measurements, CSV lists quantities" → Combine all

---

## 📁 Related Files

**Core Files**:
- **AttachmentProcessor**: [attachment-processor.js](c:\Users\gpoli\GIT\AI_agents\UI\modules_internal\communication-hub\attachment-processor.js) (506 lines)
- **EmailAIFormatter**: [email-ai-formatter.js](c:\Users\gpoli\GIT\AI_agents\UI\modules_internal\communication-hub\email-ai-formatter.js) (344 lines)
- **Communication Hub V4**: [communication-hub-v4-modern.js](c:\Users\gpoli\GIT\AI_agents\UI\modules_internal\communication-hub\communication-hub-v4-modern.js) (5,700+ lines)

**Backend Endpoints** (required):
- Gmail attachment API: `/gmail/attachment`
- Outlook attachment API: `/outlook/attachment`
- Document extraction: `/extract-document-text` (⚠️ needs implementation)
- Spreadsheet extraction: `/extract-spreadsheet-text` (⚠️ needs implementation)

---

**Last Updated**: December 23, 2025  
**Status**: ✅ Images & PDFs fully supported, ⚠️ Backend extraction for Office docs needed
