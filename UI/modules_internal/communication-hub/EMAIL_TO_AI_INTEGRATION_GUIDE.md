# Email-to-AI Integration Guide
**Complete workflow for sending emails with attachments (including images) to Claude AI**

---

## 🎯 Overview

This system processes emails with **all attachment types** and sends them to Claude AI with proper formatting:
- ✅ **Images**: Sent as base64 in Claude Vision API format
- ✅ **PDFs**: Text extracted and included
- ✅ **Documents**: Text extracted from Word/Excel/PowerPoint
- ✅ **Text files**: Read directly
- ✅ **Spreadsheets**: Converted to readable tables

---

## 📦 Components

### **1. AttachmentProcessor** (`attachment-processor.js`)
Handles downloading and processing all attachment types.

### **2. EmailAIFormatter** (`email-ai-formatter.js`)
Generates markdown prompts and Claude message content.

### **3. Communication Hub** (`communication-hub-v4-modern.js`)
Main email interface with agent assignment.

---

## 🔄 Complete Integration Flow

### **Step 1: User Assigns Email to Agent**

```javascript
// In communication-hub-v4-modern.js
async assignEmailToAgent(emailId, agentName, cell, agentId, emailData, action) {
    this.log.info(`🤖 Assigning email ${emailId} to ${agentName} with action: ${action}`);
    
    try {
        const userId = window.UserAuth?.user?.id || 1;
        
        // Fetch full email with attachments
        const fullEmail = await this.fetchEmailContent(emailId);
        
        // STEP 1: Process all attachments (including images!)
        const processedAttachments = await AttachmentProcessor.processAttachmentsForAI(
            emailId, 
            fullEmail.attachments, 
            this
        );
        
        this.log.success(`📎 Processed ${processedAttachments.length} attachments`);
        
        // Check for images
        const imageCount = processedAttachments.filter(a => 
            a.detected_type === 'image' && a.image_data
        ).length;
        
        if (imageCount > 0) {
            this.log.info(`📷 ${imageCount} image(s) will be sent to Claude Vision API`);
        }
        
        // ... continue with thread creation
    } catch (error) {
        this.log.error('Failed to assign email:', error);
        this.showError(`Failed to assign email: ${error.message}`);
    }
}
```

---

### **Step 2: Create Thread with Enhanced Metadata**

```javascript
// Store complete email metadata
const metadata = EmailAIFormatter.generateEmailMetadata(fullEmail, action);

// Add processed attachments
metadata.attachments_processed = processedAttachments;
metadata.has_images = processedAttachments.some(a => a.detected_type === 'image' && a.image_data);
metadata.image_count = processedAttachments.filter(a => a.detected_type === 'image' && a.image_data).length;

// Create thread
const threadResponse = await this.api.post('/api/threads/create', {
    user_id: userId,
    title: `Email: ${fullEmail.subject || 'No Subject'}`,
    context_type: 'email',
    location: location,
    tags: ['email', fullEmail.provider, 'assigned', action],
    metadata: metadata
});

const threadSlug = threadResponse.thread_slug;
```

---

### **Step 3: Generate Claude-Compatible Message**

```javascript
// Generate markdown text prompt
const textPrompt = EmailAIFormatter.generateEnhancedPrompt(fullEmail, action);

// Add attachment summary (for text files, PDFs, etc.)
const attachmentSummary = AttachmentProcessor.generateAttachmentSummary(processedAttachments);
const completeTextPrompt = textPrompt + '\n\n' + attachmentSummary;

// Generate Claude message content with images
const messageContent = EmailAIFormatter.generateClaudeMessageContent(
    completeTextPrompt,
    processedAttachments
);

// messageContent structure:
// [
//   { type: 'text', text: 'Email prompt...' },
//   { type: 'image', source: { type: 'base64', media_type: 'image/jpeg', data: '...' } },
//   { type: 'text', text: '[Image: photo.jpg]\nAnalyze this image...' },
//   { type: 'image', source: { type: 'base64', media_type: 'image/png', data: '...' } },
//   { type: 'text', text: '[Image: diagram.png]\nAnalyze this image...' }
// ]
```

---

### **Step 4: Send to Claude AI**

```javascript
// Backend API call (agent_routes_v4.py)
const response = await fetch(`${API_BASE_URL}/api/agent/agent/${agentId}/start`, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${auth_token}`
    },
    body: JSON.stringify({
        message_content: messageContent, // ← Claude-compatible format
        session_id: threadSlug,
        thread_slug: threadSlug,
        agent_name: agentName,
        thread_id: threadSlug,
        tools_enabled: true,
        email_context: {
            email_id: emailId,
            first_time_assignment: true,
            action_type: action
        }
    })
});
```

---

## 🖼️ Claude Messages API Format

### **Text-Only Message**
```json
{
  "role": "user",
  "content": "Analyze this email..."
}
```

### **Message with Images**
```json
{
  "role": "user",
  "content": [
    {
      "type": "text",
      "text": "Analyze this email with attachments..."
    },
    {
      "type": "image",
      "source": {
        "type": "base64",
        "media_type": "image/jpeg",
        "data": "/9j/4AAQSkZJRgABAQEAYABgAAD..."
      }
    },
    {
      "type": "text",
      "text": "\n[Image: invoice.jpg - 245 KB]\nPlease analyze this image..."
    }
  ]
}
```

### **Message with PDF Documents**
```json
{
  "role": "user",
  "content": [
    {
      "type": "text",
      "text": "Analyze this contract..."
    },
    {
      "type": "document",
      "source": {
        "type": "base64",
        "media_type": "application/pdf",
        "data": "JVBERi0xLjQKJeLjz9MKMSAwIG9i..."
      }
    },
    {
      "type": "text",
      "text": "\n[PDF Document: contract.pdf - 1.2 MB]\nPlease analyze this document..."
    }
  ]
}
```

---

## 📝 Backend Changes Required

### **Update `agent_routes_v4.py`**

```python
@app.route('/api/agent/agent/<int:agent_id>/start', methods=['POST'])
def start_agent_conversation(agent_id):
    data = request.get_json()
    
    # Check if message_content is array (multimodal) or string (text-only)
    message_content = data.get('message_content')
    
    if isinstance(message_content, list):
        # Multimodal message (text + images)
        messages = [{
            "role": "user",
            "content": message_content  # Already in Claude format
        }]
    else:
        # Text-only message (backwards compatible)
        messages = [{
            "role": "user",
            "content": message_content
        }]
    
    # Add email context if present
    email_context = data.get('email_context', {})
    if email_context.get('first_time_assignment'):
        # This is first-time email assignment
        system_prompt = generate_email_system_prompt(email_context)
    else:
        system_prompt = default_agent_prompt
    
    # Send to Claude API
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",  # Supports vision
        max_tokens=4096,
        system=system_prompt,
        messages=messages,
        temperature=0.7,
        stream=True
    )
    
    # Stream response back to frontend
    return stream_claude_response(response)
```

---

## 🔍 Example Use Cases

### **Use Case 1: Email with Invoice Image**

**User Action**: Assigns email with attached invoice.jpg to Agent Alpha

**System Process**:
1. Downloads invoice.jpg → Converts to base64
2. Generates prompt: "Analyze this email and invoice image..."
3. Sends to Claude with image embedded
4. Claude analyzes image visually and extracts:
   - Invoice number
   - Total amount
   - Due date
   - Line items

**AI Response**:
```
📧 Email Acknowledged

I've received the invoice email from ABC Corp.

**Invoice Summary**:
- Invoice #: INV-2025-001234
- Total: $15,450.00
- Due Date: January 15, 2025
- Line Items: 3 products/services

**Required Actions**:
1. Review and approve invoice
2. Process payment via accounting system
3. Confirm receipt with vendor

Would you like me to create a quote, draft a response, or process the payment?
```

---

### **Use Case 2: Email with Product Photos**

**User Action**: Customer sends email with 3 product photos asking for quote

**System Process**:
1. Downloads 3 images → Converts each to base64
2. Generates prompt with action: "Search & Create Quote"
3. Sends to Claude with all 3 images
4. Claude identifies products visually

**AI Response**:
```
📧 Customer Quote Request Analyzed

I can see 3 product images:
1. Stainless steel cabinet (36" x 24")
2. Custom signage (acrylic with LED)
3. Display stand (rotating base)

I'll search our database for similar products and generate a quote...

[Tool: search_products...]
[Tool: calculate_quote...]

**Quote Ready**: QT-2025-00789
Total: $2,850.00
```

---

### **Use Case 3: Email with Mixed Attachments**

**Attachments**: 
- contract.pdf (text extracted)
- pricing_sheet.xlsx (data extracted)
- logo.png (image analyzed)
- specs.docx (text extracted)

**Claude receives**:
- Text prompt with contract text
- Spreadsheet data as table
- Logo image (visual analysis)
- Specifications text

**AI can**:
- Review contract terms visually and textually
- Analyze pricing structure from Excel
- Describe logo design and branding
- Cross-reference specifications

---

## 🚦 File Size Limits

<cite index="1-16,1-17,1-18,1-19,1-20,1-21">Claude Messages API has file size limits:
- **Max per image**: 3.75 MB (up to 20 images)
- **Max per document**: 4.5 MB (up to 5 PDFs)
- **Images and documents**: Only allowed in user role messages</cite>
- **Recommended**: Keep files under 2 MB each for faster processing

### **Automatic Handling**:
```javascript
// In downloadImageAsBase64()
if (blob.size > 3.75 * 1024 * 1024) {
    console.warn('Image too large for Messages API:', blob.size);
    return null; // Image skipped
}

// In downloadDocumentAsBase64()
if (blob.size > 4.5 * 1024 * 1024) {
    console.warn('Document too large for Messages API:', blob.size);
    return null; // Document skipped
}
```

---

## ✅ Testing Checklist

- [ ] Text-only email → AI receives markdown prompt
- [ ] Email with 1 image → Image sent in base64, Claude describes it
- [ ] Email with multiple images → All images sent, Claude analyzes each
- [ ] Email with PDF → Text extracted and included
- [ ] Email with Excel → Data converted to table format
- [ ] Email with image > 5MB → Falls back to download URL
- [ ] Email with mixed attachments → All types handled correctly
- [ ] Thread card shows email badge (amber)
- [ ] Attachment count shown in thread metadata
- [ ] Quick actions work (Analyze, Draft, Quote, etc.)

---

## 🐛 Troubleshooting

### **Issue**: Images not appearing in AI response

**Check**:
1. `processedAttachments` has `image_data` field
2. `image_data.type === 'base64'`
3. `image_data.data` is not empty
4. Backend receives `message_content` as array
5. Claude model supports vision (claude-3-sonnet, claude-3-opus, claude-3-5-sonnet)

### **Issue**: PDF text not extracted

**Check**:
1. Backend endpoint `/extract-pdf-text` exists
2. PyPDF2 or pdfplumber installed
3. PDF not password-protected
4. Fallback message appears in prompt

### **Issue**: Excel data not readable

**Check**:
1. Backend endpoint `/extract-spreadsheet-text` exists
2. pandas or openpyxl installed
3. CSV fallback working for .csv files

---

## 📚 Related Files

- [`attachment-processor.js`](attachment-processor.js) - Attachment processing logic
- [`email-ai-formatter.js`](email-ai-formatter.js) - Prompt generation and Claude formatting
- [`communication-hub-v4-modern.js`](communication-hub-v4-modern.js) - Email UI and assignment
- `AI_infrastructure/routes/agent_routes_v4.py` - Backend API (needs update)

---

**Status**: ✅ Frontend implementation complete  
**Remaining**: Backend multimodal message handling  
**Last Updated**: December 18, 2025
