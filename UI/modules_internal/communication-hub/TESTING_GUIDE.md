# Testing Guide: Email-to-AI with Images & PDFs
**Step-by-step testing instructions**
**December 18, 2025**

---

## 🎯 What We're Testing

The complete flow of assigning an email with attachments (images and/or PDFs) to an AI agent, where:
1. Attachments are downloaded and converted to base64
2. Message is sent in Messages API format (text + image blocks + document blocks)
3. Claude AI receives and processes multimodal content
4. AI response references the images/documents

---

## 🚀 Pre-Test Setup

### **1. Start Flask Server**
```powershell
cd c:\Users\gpoli\GIT\AI_agents\AI_infrastructure
python flask_app.py
```

**Expected Output**:
```
[REGISTRY] ✅ Loaded 80+ tools
[FLASK] 🚀 Server running on http://localhost:5000
```

### **2. Open Browser Console**
Press `F12` → Console tab (to see frontend logs)

### **3. Open Communication Hub**
Navigate to Communication Hub in the UI

---

## 📧 Test Case 1: Email with Single Image

### **Setup**:
Find an email in your inbox with 1 image attachment (or send yourself one)

### **Steps**:
1. **Click "Assign to Agent"** button in Communication Hub
2. **Select "Agent Alpha"** from dropdown
3. **Watch console logs**:

**Expected Frontend Logs**:
```
🤖 Assigning email 12345 to Agent Alpha (ID: agent-1)
📧 Fetched email: Test Email with Image
📎 Processing 1 attachment(s)...
✅ Processed 1 attachments: 1 images, 0 PDFs
📧 Message prepared: multimodal (3 blocks)
🤖 Triggering AI response...
✅ AI processing started automatically
```

4. **Check Agent Alpha column**: Thread should load automatically
5. **Wait for AI response**: Should reference the image content

**Expected AI Response**:
```
📧 Email Acknowledged

I've received your email with the attached image. 

From the image, I can see:
- [Description of what's in the image]
- [Key details extracted]

How would you like me to proceed?
```

### **Verification**:
- ✅ Console shows "multimodal (3 blocks)"
- ✅ Thread appears in Agent Alpha
- ✅ AI response describes image content
- ✅ No errors in console

---

## 📄 Test Case 2: Email with PDF Document

### **Setup**:
Find an email with 1 PDF attachment (invoice, contract, etc.)

### **Steps**:
1. **Assign to Agent Bravo**
2. **Watch console logs**:

**Expected Frontend Logs**:
```
📎 Processing 1 attachment(s)...
✅ Processed 1 attachments: 0 images, 1 PDFs
📧 Message prepared: multimodal (3 blocks)
```

3. **Wait for AI response**

**Expected AI Response**:
```
📧 Document Analyzed

I've reviewed the PDF document. Here are the key points:

**Document Summary**:
- [Extracted information from PDF]
- [Key sections/data]

Would you like me to extract specific information or take action?
```

### **Verification**:
- ✅ Console shows "1 PDFs"
- ✅ AI response extracts text from PDF
- ✅ AI references document structure/content

---

## 🎨 Test Case 3: Email with Multiple Images

### **Setup**:
Email with 2-3 image attachments

### **Steps**:
1. **Assign to Agent Charlie**
2. **Watch console logs**:

**Expected**:
```
✅ Processed 3 attachments: 3 images, 0 PDFs
📧 Message prepared: multimodal (7 blocks)
```
*(7 blocks = 1 text + 3 images + 3 context texts)*

3. **Check AI response**: Should analyze each image

**Expected AI Response**:
```
📧 Multiple Images Analyzed

I've reviewed all three images:

**Image 1 (photo1.jpg)**:
- [Description]

**Image 2 (photo2.jpg)**:
- [Description]

**Image 3 (photo3.jpg)**:
- [Description]

Let me know how you'd like to proceed with these.
```

### **Verification**:
- ✅ Console shows correct image count
- ✅ AI describes each image separately
- ✅ No duplicate descriptions

---

## 📊 Test Case 4: Mixed Attachments (Image + PDF)

### **Setup**:
Email with 1 image + 1 PDF

### **Steps**:
1. **Assign to Agent Delta**
2. **Watch console logs**:

**Expected**:
```
✅ Processed 2 attachments: 1 images, 1 PDFs
📧 Message prepared: multimodal (5 blocks)
```

3. **Check AI response**: Should reference both

**Expected AI Response**:
```
📧 Mixed Content Analyzed

**Visual Content (Image)**:
- [Image description]

**Document Content (PDF)**:
- [PDF text extraction]

Both the image and document relate to [topic]. Here's my analysis:
[Combined analysis]
```

### **Verification**:
- ✅ Both image and PDF processed
- ✅ AI references both in response
- ✅ Combined analysis makes sense

---

## 🚫 Test Case 5: Oversized File (Error Handling)

### **Setup**:
Email with image > 3.75 MB or PDF > 4.5 MB

### **Steps**:
1. **Assign to Agent Echo**
2. **Watch console logs**:

**Expected Warning**:
```
⚠️ [AttachmentProcessor] Image too large for Messages API: 4500000
✅ Processed 1 attachments: 0 images, 0 PDFs
📧 Message prepared: text-only
```

3. **Check AI response**: Should still process text

**Expected AI Response**:
```
📧 Email Acknowledged

I've received your email. The attached file was too large to process directly (4.3 MB).

Please provide a download link or re-send a smaller version if you need me to analyze the content.
```

### **Verification**:
- ✅ Warning logged (not error)
- ✅ Email still assigned
- ✅ AI explains size issue
- ✅ No crash/freeze

---

## 🔍 Test Case 6: Text-Only Email (No Attachments)

### **Setup**:
Plain text email with no attachments

### **Steps**:
1. **Assign to Agent Foxtrot**
2. **Watch console logs**:

**Expected**:
```
📧 Message prepared: text-only
```

3. **Check AI response**: Normal text processing

**Expected AI Response**:
```
📧 Email Acknowledged

[Normal AI response to email content]
```

### **Verification**:
- ✅ No attachment processing
- ✅ Message is string (not array)
- ✅ Faster response time

---

## 🐛 Debugging Failed Tests

### **Issue**: Console shows "0 attachments processed" when attachments exist

**Check**:
1. `fullEmail.attachments` is populated
2. Email API returning attachment metadata
3. AttachmentProcessor import loaded

**Fix**:
```javascript
console.log('Full email:', fullEmail);
console.log('Attachments:', fullEmail.attachments);
```

---

### **Issue**: Image download fails (null returned)

**Check**:
1. Attachment ID valid
2. API endpoint accessible: `/api/communication-hub/attachment/${id}`
3. File size under 3.75 MB

**Fix**:
```javascript
// In attachment-processor.js
console.log('Downloading image:', attachmentId);
console.log('Blob size:', blob.size);
```

---

### **Issue**: Backend receives string instead of array

**Check**:
1. `messageContent` type before sending
2. `MultiAgent.sendMessage` signature
3. Backend `user_message_content` type

**Fix**:
```javascript
console.log('Message content type:', typeof messageContent);
console.log('Message content:', messageContent);
```

---

### **Issue**: Claude doesn't describe images

**Check**:
1. Message content blocks format
2. Base64 data not empty
3. Media type correct (`image/jpeg`, `image/png`)

**Fix**:
```javascript
console.log('Content blocks:', JSON.stringify(messageContent, null, 2));
```

---

## 📊 Performance Benchmarks

### **Expected Processing Times**:

| Scenario | Attachment Processing | Total Assignment Time |
|----------|----------------------|----------------------|
| Text-only | 0ms | 500-800ms |
| 1 small image (< 500KB) | 200-400ms | 800-1200ms |
| 1 large image (2-3MB) | 600-1000ms | 1500-2000ms |
| 1 PDF (1-2MB) | 400-800ms | 1000-1500ms |
| Multiple attachments (3-5) | 1000-2000ms | 2000-3000ms |

**If processing takes > 5 seconds**: Check network speed, attachment sizes

---

## ✅ Success Criteria

### **Functional Requirements**:
- [x] Images sent as base64 in message content
- [x] PDFs sent as document blocks in message content
- [x] AI describes images accurately
- [x] AI extracts text from PDFs
- [x] Oversized files handled gracefully
- [x] Text-only emails still work

### **Performance Requirements**:
- [x] Image processing < 2 seconds
- [x] PDF processing < 2 seconds
- [x] No UI freeze during processing
- [x] Console logs clear and informative

### **Error Handling Requirements**:
- [x] Oversized files logged (not crashed)
- [x] Failed downloads don't block assignment
- [x] Network errors show user-friendly message
- [x] Backend errors logged properly

---

## 🎯 Final Verification

After all tests pass, verify:

1. **Database**: Check `sessions.threads` table
   - `metadata` column has `has_images` and `has_documents` flags
   - Message `content` column has JSON array (not string) for multimodal

2. **Thread Info Card**: Shows email badge with attachment count

3. **Conversation History**: Multimodal messages saved correctly

4. **Agent Response**: References images/documents naturally

---

## 🐛 Known Limitations

1. **Max 20 images** per message (Messages API limit)
2. **Max 5 PDFs** per message (Messages API limit)
3. **Max 3.75 MB** per image
4. **Max 4.5 MB** per PDF
5. **No Word/Excel support** yet (planned)
6. **No video support** (Messages API doesn't support)

---

## 📞 Support

**If tests fail**:
1. Check console logs (both frontend and backend)
2. Review `AI_infrastructure/flask_app.log`
3. Verify environment variables (ANTHROPIC_API_KEY)
4. Check Claude API status
5. Review [IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md)

**For questions**: Check [EMAIL_TO_AI_INTEGRATION_GUIDE.md](EMAIL_TO_AI_INTEGRATION_GUIDE.md)

---

**Status**: Ready for Testing  
**Last Updated**: December 18, 2025  
**Estimated Test Time**: 30-45 minutes for all cases
