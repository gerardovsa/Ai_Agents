# 📧🔗 **MICROSOFT PLATFORM INTEGRATION + FILE ATTACHMENTS FOR ORDERS**

**Generated:** January 3, 2026  
**Purpose:** Microsoft Outlook/Exchange/OneDrive integration + artwork file attachment system

---

## 🎯 **OVERVIEW**

The system supports **DUAL EMAIL PLATFORMS**:
- ✅ **Gmail** (Google Workspace)
- ✅ **Outlook** (Microsoft 365)

Both platforms fully integrated with:
- Email tracking for orders
- File attachment download/storage
- Cloud storage integration (OneDrive, Google Drive)
- AI assistant context injection

---

## 📧 **MICROSOFT OUTLOOK INTEGRATION**

### **Current Capabilities (ALREADY IMPLEMENTED)**

| Feature | Status | Tools Available |
|---------|--------|-----------------|
| **Send Email** | ✅ Complete | `microsoft_outlook_send_email` |
| **Read Email** | ✅ Complete | `microsoft_outlook_get_message` |
| **Search Email** | ✅ Complete | `microsoft_outlook_search_messages` |
| **List Emails** | ✅ Complete | `microsoft_outlook_list_messages` |
| **Download Attachments** | ✅ Complete | `microsoft_outlook_download_attachment` |
| **Save to OneDrive** | ✅ Complete | `microsoft_outlook_download_attachment_to_onedrive` |
| **Save to Google Drive** | ✅ Complete | `microsoft_outlook_download_attachment_to_google_drive` |
| **Send to AI** | ✅ Complete | `microsoft_outlook_attachment_convert_and_send_to_ai` |
| **Manage Folders** | ✅ Complete | `microsoft_outlook_create_folder`, `microsoft_outlook_list_folders` |
| **Draft Emails** | ✅ Complete | `microsoft_outlook_create_draft`, `microsoft_outlook_send_draft` |
| **Reply/Forward** | ✅ Complete | `microsoft_outlook_reply_to_message`, `microsoft_outlook_forward_message` |

**Authentication:**
- Microsoft OAuth 2.0 (Graph API)
- Scopes: `Mail.Read`, `Mail.ReadWrite`, `Mail.Send`
- Per-user credential injection (automatic)

---

## 📁 **MICROSOFT ONEDRIVE INTEGRATION**

### **Current Capabilities (ALREADY IMPLEMENTED)**

| Feature | Status | Tools Available |
|---------|--------|-----------------|
| **Upload Files** | ✅ Complete | `microsoft_onedrive_upload_file` |
| **Download Files** | ✅ Complete | `microsoft_onedrive_download_file` |
| **List Files** | ✅ Complete | `microsoft_onedrive_list_files` |
| **Get File Info** | ✅ Complete | `microsoft_onedrive_get_file_info` |
| **Create Folders** | ✅ Complete | `microsoft_onedrive_create_folder` |
| **Delete Items** | ✅ Complete | `microsoft_onedrive_delete_item` |
| **Move Items** | ✅ Complete | `microsoft_onedrive_move_item` |
| **Copy Items** | ✅ Complete | `microsoft_onedrive_copy_item` |
| **Share Files** | ✅ Complete | `microsoft_onedrive_create_share_link` |

**Authentication:**
- Microsoft OAuth 2.0 (Graph API)
- Scopes: `Files.Read`, `Files.ReadWrite`, `Files.ReadWrite.All`
- Per-user credential injection (automatic)

---

## 🗄️ **SHAREPOINT INTEGRATION**

### **Current Capabilities (ALREADY IMPLEMENTED)**

| Feature | Status | Tools Available |
|---------|--------|-----------------|
| **List Sites** | ✅ Complete | `microsoft_sharepoint_list_sites` |
| **Search Content** | ✅ Complete | `microsoft_sharepoint_search_content` |
| **List Document Libraries** | ✅ Complete | `microsoft_sharepoint_list_drives` |
| **Upload Documents** | ✅ Complete | `microsoft_sharepoint_upload_file` |
| **Download Documents** | ✅ Complete | `microsoft_sharepoint_download_file` |
| **Manage Permissions** | ✅ Complete | `microsoft_sharepoint_get_permissions` |

**Authentication:**
- Microsoft OAuth 2.0 (Graph API)
- Scopes: `Sites.Read.All`, `Sites.ReadWrite.All`

---

## 🎨 **FILE ATTACHMENT WORKFLOW FOR ORDERS**

### **Scenario: Customer Sends Quote Request with Artwork**

```
📧 Email Received (Outlook)
  ↓
From: customer@example.com
Subject: Quote Request - Business Cards
Attachments:
  - logo_final.pdf (250 KB)
  - brand_guidelines.docx (1.2 MB)
  - mockup_v2.jpg (450 KB)
  ↓
AI Agent Workflow:
  1. Detect email with attachments
  2. Extract customer details from email
  3. Create Xero quote
  4. Download attachments from Outlook
  5. Upload attachments to OneDrive folder: /Orders/2025/Quote_QU-0123/
  6. Create order with metadata linking email + attachments
  7. Notify production team with artwork links
```

---

## 🔧 **IMPLEMENTATION: Multi-Platform Order Creation**

### **Tool 1: Create Order from Email (Gmail OR Outlook)**

```python
@tool_executor()
def xero_create_order_from_email_quote(
    business_id: int,
    quote_id: str,
    client_id: str,
    email_id: str,                              # Message ID (any platform)
    email_provider: str = "outlook",            # ⭐ "gmail" OR "outlook"
    email_thread_id: Optional[str] = None,
    download_attachments: bool = True,          # ⭐ Download artwork files
    attachment_storage: str = "onedrive",       # ⭐ "onedrive", "google_drive", "local"
    attachment_folder: Optional[str] = None,    # ⭐ Custom folder path
    create_job_tickets: bool = True,
    **kwargs
) -> Dict[str, Any]:
    """
    Create order from Xero quote with email origin tracking + file attachments
    
    Supports:
    - Gmail OR Outlook emails
    - OneDrive OR Google Drive storage
    - Automatic artwork file organization
    - Production team notifications with file links
    
    Workflow:
    1. Fetch quote from Xero
    2. Fetch email from Gmail/Outlook
    3. Download all attachments
    4. Upload attachments to cloud storage
    5. Create order with metadata
    6. Create AI thread with email + file context
    7. Return order ID + file references
    
    Args:
        email_provider: "gmail" or "outlook"
        email_id: Message ID from respective platform
        download_attachments: If True, download all email attachments
        attachment_storage: Where to store files ("onedrive", "google_drive", "local")
        attachment_folder: Custom folder path (e.g., "/Orders/2025/Order_56230")
    
    Returns:
        {
            "success": True,
            "order_id": 56230,
            "quote_number": "QU-0123",
            "email_reference": {...},
            "attachments": [
                {
                    "filename": "logo_final.pdf",
                    "size": 250000,
                    "storage_location": "onedrive",
                    "storage_path": "/Orders/2025/Order_56230/logo_final.pdf",
                    "share_link": "https://onedrive.live.com/..."
                }
            ]
        }
    """
    try:
        # Get quote from Xero
        quote = xero_get_quote_by_id(business_id, quote_id)
        
        # ========== MULTI-PLATFORM EMAIL FETCHING ==========
        if email_provider == "gmail":
            email = gmail_get_message(message_id=email_id)
            email_attachments = gmail_get_attachments(message_id=email_id)
        elif email_provider == "outlook":
            email = microsoft_outlook_get_message(message_id=email_id)
            email_attachments = microsoft_outlook_get_attachments(message_id=email_id)
        else:
            return {"success": False, "error": f"Unsupported email provider: {email_provider}"}
        
        # ========== ATTACHMENT PROCESSING ==========
        uploaded_attachments = []
        
        if download_attachments and email_attachments.get('attachments'):
            # Determine folder path
            order_folder = attachment_folder or f"/Orders/{datetime.now().year}/Quote_{quote['quote_number']}"
            
            for attachment in email_attachments['attachments']:
                attachment_id = attachment['id']
                filename = attachment['name']
                
                # ========== CLOUD STORAGE UPLOAD ==========
                if attachment_storage == "onedrive":
                    # Option 1: Outlook → OneDrive
                    if email_provider == "outlook":
                        result = microsoft_outlook_download_attachment_to_onedrive(
                            message_id=email_id,
                            attachment_id=attachment_id,
                            onedrive_folder=order_folder,
                            **kwargs
                        )
                    # Option 2: Gmail → OneDrive (download + upload)
                    else:
                        result = gmail_download_attachment_to_onedrive(
                            message_id=email_id,
                            attachment_id=attachment_id,
                            onedrive_folder=order_folder,
                            **kwargs
                        )
                
                elif attachment_storage == "google_drive":
                    # Option 1: Gmail → Google Drive
                    if email_provider == "gmail":
                        result = gmail_download_attachment_to_google_drive(
                            message_id=email_id,
                            attachment_id=attachment_id,
                            **kwargs
                        )
                    # Option 2: Outlook → Google Drive
                    else:
                        result = microsoft_outlook_download_attachment_to_google_drive(
                            message_id=email_id,
                            attachment_id=attachment_id,
                            **kwargs
                        )
                
                elif attachment_storage == "local":
                    # Download to local server storage
                    if email_provider == "gmail":
                        attachment_data = gmail_download_attachment(
                            message_id=email_id,
                            attachment_id=attachment_id,
                            **kwargs
                        )
                    else:
                        attachment_data = microsoft_outlook_download_attachment(
                            message_id=email_id,
                            attachment_id=attachment_id,
                            **kwargs
                        )
                    
                    # Save to local filesystem
                    local_path = f"data/uploads/orders/order_{order_id}/{filename}"
                    save_file_locally(attachment_data['content'], local_path)
                    
                    result = {
                        "success": True,
                        "storage_location": "local",
                        "storage_path": local_path
                    }
                
                # Track uploaded attachment
                if result.get('success'):
                    uploaded_attachments.append({
                        "attachment_id": attachment_id,
                        "filename": filename,
                        "size": attachment.get('size'),
                        "content_type": attachment.get('content_type'),
                        "storage_location": attachment_storage,
                        "storage_path": result.get('storage_path') or result.get('path'),
                        "share_link": result.get('share_link') or result.get('webUrl'),
                        "uploaded_at": datetime.now().isoformat()
                    })
        
        # ========== BUILD METADATA ==========
        metadata = {
            "xero": {
                "quote_id": quote['quote_id'],
                "quote_number": quote['quote_number'],
                "quote_total": quote['total']
            },
            "email_origin": {
                "email_id": email_id,
                "email_thread_id": email_thread_id or email.get('thread_id'),
                "email_subject": email['subject'],
                "email_from": email['from'],
                "email_to": email['to'],
                "email_date": email['date'],
                "email_provider": email_provider,
                "email_has_attachments": len(uploaded_attachments) > 0,
                "email_attachment_count": len(uploaded_attachments),
                "email_attachments": uploaded_attachments,  # ⭐ Full attachment metadata
                "email_message_url": _build_email_url(email_id, email_provider)
            },
            "conversion": {
                "converted_at": datetime.now().isoformat(),
                "converted_by": "ai_agent",
                "trigger": "quote_approval_email",
                "attachment_storage": attachment_storage
            }
        }
        
        # ========== CREATE ORDER ==========
        order = inhouse_create_order(
            business_id=business_id,
            client_id=client_id,
            order_date=datetime.now().strftime('%Y-%m-%d'),
            xero_quote_id=quote_id,
            automation_source="ai_agent",
            metadata=metadata,
            **kwargs
        )
        
        # ========== CREATE AI THREAD ==========
        thread_slug = await create_thread_with_email_and_files(
            email_id=email_id,
            email_provider=email_provider,
            order_id=order['order_id'],
            quote_number=quote['quote_number'],
            attachments=uploaded_attachments
        )
        
        # ========== NOTIFY PRODUCTION TEAM ==========
        if uploaded_attachments:
            await notify_production_team(
                order_id=order['order_id'],
                client_name=email['from'],
                attachments=uploaded_attachments,
                notification_method="email"  # or "teams", "slack"
            )
        
        return {
            "success": True,
            "order_id": order['order_id'],
            "quote_number": quote['quote_number'],
            "email_reference": {
                "email_id": email_id,
                "email_provider": email_provider,
                "email_subject": email['subject'],
                "email_from": email['from'],
                "open_url": metadata['email_origin']['email_message_url'],
                "thread_slug": thread_slug
            },
            "attachments": uploaded_attachments,
            "attachment_count": len(uploaded_attachments),
            "message": f"Order #{order['order_id']} created from {email_provider} email with {len(uploaded_attachments)} artwork files"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e), "traceback": traceback.format_exc()}


def _build_email_url(email_id: str, provider: str) -> str:
    """Build platform-specific email URL"""
    if provider == "gmail":
        # Gmail URL format
        message_id_clean = email_id.replace('gmail_', '')
        return f"https://mail.google.com/mail/u/0/#inbox/{message_id_clean}"
    elif provider == "outlook":
        # Outlook web URL format
        return f"https://outlook.office365.com/mail/inbox/id/{email_id}"
    else:
        return ""
```

---

## 📂 **FILE STORAGE ARCHITECTURE**

### **Option 1: Microsoft OneDrive (RECOMMENDED for Microsoft users)**

```
OneDrive Folder Structure:
/Orders/
  ├── 2025/
  │   ├── Order_56230/
  │   │   ├── logo_final.pdf
  │   │   ├── brand_guidelines.docx
  │   │   └── mockup_v2.jpg
  │   ├── Order_56231/
  │   │   └── artwork_v3.ai
  │   └── Quote_QU-0123/
  │       └── draft_proposal.pdf
  └── 2024/
      └── ...
```

**Benefits:**
- ✅ Native integration with Outlook
- ✅ SharePoint library backing (enterprise)
- ✅ Versioning enabled by default
- ✅ Team collaboration built-in
- ✅ Direct links in emails/Teams
- ✅ 1TB+ storage per user

---

### **Option 2: Google Drive (For Google Workspace users)**

```
Google Drive Folder Structure:
Orders/
  ├── 2025/
  │   ├── Order_56230/
  │   └── Order_56231/
  └── 2024/
```

**Benefits:**
- ✅ Native Gmail integration
- ✅ Google Docs/Sheets editing
- ✅ Easy sharing via links
- ✅ 30GB+ storage per user

---

### **Option 3: Local Server Storage (Air-gapped/security-critical)**

```
C:\AI_agents\data\uploads\orders\
  ├── order_56230\
  │   ├── logo_final.pdf
  │   └── brand_guidelines.docx
  └── order_56231\
```

**Benefits:**
- ✅ Full control
- ✅ No cloud dependency
- ✅ Regulatory compliance

**Limitations:**
- ❌ No automatic backups
- ❌ Harder to share with team
- ❌ Limited storage

---

## 💬 **AI ASSISTANT ENHANCEMENTS**

### **Enhancement 1: AI Can Access Artwork Files**

**User:** "Show me the logo artwork for order #56230"

**AI Workflow:**
```python
# 1. Get order metadata
order = inhouse_get_order_by_id(order_id=56230)
attachments = order['metadata']['email_origin']['email_attachments']

# 2. Find logo file
logo_file = next(f for f in attachments if 'logo' in f['filename'].lower())

# 3. Download from OneDrive
if logo_file['storage_location'] == 'onedrive':
    file_data = microsoft_onedrive_download_file(
        file_path=logo_file['storage_path']
    )
    
    # 4. Convert to AI-readable format
    result = universal_file_handler.process_file(
        file_data=file_data,
        strategy='auto'  # PDF → document block, image → image block
    )
    
    # 5. Send to AI in next message
    # AI can now SEE the logo and discuss it
```

**AI Response:**
```
I've loaded the logo artwork (logo_final.pdf). 

The logo features:
- Primary color: Navy blue (#003366)
- Typography: Bold sans-serif
- Icon: Stylized mountain peak
- Dimensions: 300x300 px

The design looks professional and matches the brand guidelines document. 
Ready to approve for production?
```

---

### **Enhancement 2: Production Instructions with File Links**

**User:** "Create job ticket for order #56230"

**AI Workflow:**
```python
order = inhouse_get_order_by_id(order_id=56230)
attachments = order['metadata']['email_origin']['email_attachments']

# Create job ticket with artwork references
job_ticket = inhouse_create_job_ticket(
    order_id=56230,
    description="Business cards - 500 qty",
    metadata={
        "artwork_files": [
            {
                "filename": att['filename'],
                "link": att['share_link'],
                "notes": "Customer provided logo - use as-is"
            }
            for att in attachments
        ]
    }
)
```

**Production Team Sees:**
```
📋 Job Ticket #12345
Order: #56230 - ABC Company
Description: Business cards - 500 qty

🎨 ARTWORK FILES:
📄 logo_final.pdf
   → https://onedrive.live.com/... [Open in OneDrive]
   
📄 brand_guidelines.docx
   → https://onedrive.live.com/... [Open in OneDrive]
   
📄 mockup_v2.jpg
   → https://onedrive.live.com/... [Open in OneDrive]

Notes: Customer provided logo - use as-is
```

---

### **Enhancement 3: Email Reply with Artwork Confirmation**

**User:** "Reply to customer confirming we received their artwork"

**AI Workflow:**
```python
order = inhouse_get_order_by_id(order_id=56230)
email_origin = order['metadata']['email_origin']
attachments = order['metadata']['email_origin']['email_attachments']

# Compose reply
if email_origin['email_provider'] == 'outlook':
    microsoft_outlook_reply_to_message(
        message_id=email_origin['email_id'],
        body=f"""
        Hi {customer_name},
        
        Thank you for your quote request! We've received your artwork files:
        
        ✅ {attachments[0]['filename']} ({_format_size(attachments[0]['size'])})
        ✅ {attachments[1]['filename']} ({_format_size(attachments[1]['size'])})
        ✅ {attachments[2]['filename']} ({_format_size(attachments[2]['size'])})
        
        Our design team is reviewing the files and will send a proof within 24 hours.
        
        Your quote number: {quote_number}
        Estimated completion: {completion_date}
        
        Best regards,
        InHouse Print Team
        """
    )
elif email_origin['email_provider'] == 'gmail':
    gmail_reply_to_message(
        message_id=email_origin['email_id'],
        body=...  # Same content
    )
```

---

## 🔄 **ATTACHMENT SYNC WORKFLOWS**

### **Workflow 1: Outlook → OneDrive → Order**

```
1. Customer sends email to sales@inhouseprint.com.au
2. Email arrives in Outlook inbox
3. AI detects quote request with attachments
4. AI downloads attachments from Outlook
5. AI uploads to OneDrive: /Orders/2025/Order_56230/
6. AI creates order with file metadata
7. Production team receives notification with OneDrive links
```

---

### **Workflow 2: Gmail → Google Drive → Order**

```
1. Customer sends email to printing@inhouseprint.com.au
2. Email arrives in Gmail inbox
3. AI detects quote request with attachments
4. AI downloads attachments from Gmail
5. AI uploads to Google Drive: Orders/2025/Order_56230/
6. AI creates order with file metadata
7. Production team receives notification with Drive links
```

---

### **Workflow 3: Cross-Platform (Outlook → Google Drive)**

```
1. Email arrives in Outlook
2. AI downloads attachments from Outlook
3. AI uploads to Google Drive (cross-platform storage)
4. Production team (Google Workspace users) access via Drive
```

**Use Case:** Company uses Outlook for email but Google Drive for file storage

---

## 📊 **COMPARISON: GMAIL VS OUTLOOK**

| Feature | Gmail | Outlook | Recommendation |
|---------|-------|---------|----------------|
| **Email API** | Gmail API | Microsoft Graph | Both excellent |
| **Attachment Download** | ✅ Yes | ✅ Yes | Equal |
| **Native Cloud Storage** | Google Drive | OneDrive | OneDrive (enterprise) |
| **Team Collaboration** | Google Workspace | Microsoft 365 | Microsoft 365 (fuller suite) |
| **Enterprise Features** | 🟡 Good | ✅ Excellent | Outlook (Teams, SharePoint) |
| **Ease of Setup** | ✅ Easy | 🟡 Moderate | Gmail (simpler OAuth) |
| **Cost** | $6-12/user/month | $12-22/user/month | Gmail (cheaper) |
| **Australia Market** | 40% market share | 60% market share | Outlook (more common) |

---

## ✅ **IMPLEMENTATION CHECKLIST**

### **Phase 1: Microsoft Platform Integration (Week 1)** 🔴

- [x] Outlook email tools (DONE - 20+ tools)
- [x] OneDrive storage tools (DONE - 8+ tools)
- [x] SharePoint tools (DONE - 10+ tools)
- [ ] Update `xero_create_order_from_email_quote()` to support Outlook
- [ ] Test Outlook attachment → OneDrive workflow
- [ ] Add `email_provider` parameter to all email-related tools

### **Phase 2: File Attachment System (Week 2)** 🟠

- [ ] Add attachment metadata to Orders.metadata schema
- [ ] Create `attachment_storage` configuration (per business)
- [ ] Implement automatic folder creation (e.g., `/Orders/2025/Order_56230/`)
- [ ] Add file link rendering in order details UI
- [ ] Test cross-platform workflows (Outlook → Google Drive)

### **Phase 3: AI Assistant Enhancements (Week 3)** 🟡

- [ ] Enable AI to view/analyze artwork files
- [ ] Add "Show artwork" command in chat
- [ ] Generate production instructions with file links
- [ ] Implement email reply with artwork confirmation
- [ ] Add file attachment badges to order cards

---

## 🎯 **RECOMMENDED SETUP FOR INHOUSE PRINT**

### **Email Platform:** Microsoft Outlook ✅
**Reason:** 
- Already using Microsoft 365
- Better integration with OneDrive/SharePoint
- Teams collaboration built-in
- 60% market share in Australia

### **File Storage:** Microsoft OneDrive ✅
**Reason:**
- Native integration with Outlook
- Enterprise-grade versioning
- SharePoint library backing
- Team folders for production staff
- 1TB+ storage per user

### **Backup:** Google Drive (Secondary) 🟡
**Reason:**
- Cross-platform redundancy
- Alternative access method
- Cheaper storage expansion

---

## 📚 **EXISTING TOOLS REFERENCE**

### **Microsoft Outlook Tools (20+)**
```python
microsoft_outlook_send_email(to, subject, body, cc, bcc, attachments)
microsoft_outlook_get_message(message_id)
microsoft_outlook_search_messages(query, folder, max_results)
microsoft_outlook_list_messages(folder, max_results)
microsoft_outlook_download_attachment(message_id, attachment_id)
microsoft_outlook_get_attachments(message_id)
microsoft_outlook_reply_to_message(message_id, body)
microsoft_outlook_forward_message(message_id, to, body)
microsoft_outlook_create_draft(to, subject, body)
microsoft_outlook_send_draft(draft_id)
```

### **Microsoft OneDrive Tools (8+)**
```python
microsoft_onedrive_upload_file(local_file_path, onedrive_folder, new_name)
microsoft_onedrive_download_file(file_path, save_to_local)
microsoft_onedrive_list_files(folder_path, max_results)
microsoft_onedrive_get_file_info(file_path)
microsoft_onedrive_create_folder(folder_path)
microsoft_onedrive_delete_item(item_path)
microsoft_onedrive_move_item(item_path, destination_path)
microsoft_onedrive_create_share_link(file_path, link_type)
```

### **Cross-Platform Attachment Tools**
```python
# Outlook → OneDrive
microsoft_outlook_download_attachment_to_onedrive(message_id, attachment_id, onedrive_folder)

# Outlook → Google Drive
microsoft_outlook_download_attachment_to_google_drive(message_id, attachment_id, parent_folder_id)

# Gmail → OneDrive
gmail_download_attachment_to_onedrive(message_id, attachment_id, onedrive_folder)

# Gmail → Google Drive
gmail_download_attachment_to_google_drive(message_id, attachment_id, parent_folder_id)
```

---

**Summary:** Full Microsoft platform integration is ALREADY IMPLEMENTED. Just need to update order creation tools to support Outlook emails and OneDrive file storage. The AI can already read Outlook emails, download attachments, and save to OneDrive - just need to wire it into the order workflow! 🎉
