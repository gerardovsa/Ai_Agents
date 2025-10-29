# Microsoft 365 Integration Module

Python integration with Microsoft 365 services for InHouse Print Management System.

## 🚀 Quick Status

**Current Status:** ⚠️ **NOT CONFIGURED** - Needs Azure AD app registration

**What's Working:**
- ✅ Office 365 SMTP email sending (`printing@inhouseprint.com.au`)
- ✅ Basic email notifications

**What's NOT Working (Needs Setup):**
- ❌ Reading emails from inbox
- ❌ OneDrive file storage
- ❌ Creating Word/Excel documents via API
- ❌ Calendar integration

---

## 🎯 What You Need to Get Connected

### Step 1: Create Azure AD App Registration (5 minutes)

1. **Go to Azure Portal:** https://portal.azure.com
2. **Navigate to:** Azure Active Directory → App registrations
3. **Click:** "New registration"
4. **Fill in:**
   - Name: `InHouse Print Graph API`
   - Supported account types: `Accounts in any organizational directory`
   - Redirect URI: `Web` → `http://localhost:5015/callback`
5. **Click:** "Register"

### Step 2: Copy Client ID (Application ID)

After registration, you'll see the **Overview** page:
- Copy the **Application (client) ID** (looks like: `12345678-1234-1234-1234-123456789abc`)
- This is your `ClientId`

### Step 3: Create Client Secret

1. **Navigate to:** Certificates & secrets (left menu)
2. **Click:** "New client secret"
3. **Description:** `InHouse Print Access`
4. **Expires:** Choose `24 months` or `Never`
5. **Click:** "Add"
6. **⚠️ IMPORTANT:** Copy the **Value** immediately (shown only once!)
7. This is your `ClientSecret`

### Step 4: Set API Permissions

1. **Navigate to:** API permissions (left menu)
2. **Click:** "Add a permission"
3. **Select:** "Microsoft Graph"
4. **Select:** "Delegated permissions"
5. **Add these permissions:**
   - ✅ `Files.ReadWrite.All` - OneDrive access
   - ✅ `Sites.ReadWrite.All` - SharePoint access
   - ✅ `Mail.ReadWrite` - Read/write emails
   - ✅ `Mail.Send` - Send emails
   - ✅ `Calendars.ReadWrite` - Calendar access
   - ✅ `User.Read` - Basic profile
   - ✅ `offline_access` - Refresh tokens
6. **Click:** "Grant admin consent" (if you're admin)

### Step 5: Add Credentials to Config

Edit `config/database-config.json`:

```json
{
  "ExternalAPIs": {
    "Microsoft365": {
      "ClientId": "PASTE_YOUR_CLIENT_ID_HERE",
      "ClientSecret": "PASTE_YOUR_CLIENT_SECRET_HERE",
      "TenantId": "common"
    }
  }
}
```

**Or** set environment variables:
```powershell
# Windows PowerShell
$env:M365_CLIENT_ID = "your_client_id"
$env:M365_CLIENT_SECRET = "your_client_secret"

# Or permanently:
[System.Environment]::SetEnvironmentVariable('M365_CLIENT_ID', 'your_client_id', 'User')
[System.Environment]::SetEnvironmentVariable('M365_CLIENT_SECRET', 'your_client_secret', 'User')
```

### Step 6: Test Connection

```python
from Microsoft_365_Connection.microsoft365_client import Microsoft365Client

# Initialize client
m365 = Microsoft365Client()

# Get authorization URL
auth_url = m365.get_authorization_url('http://localhost:5015/callback')
print(f"Visit: {auth_url}")

# After authorization, exchange code:
# m365.exchange_code_for_token(code, 'http://localhost:5015/callback')

# Test API access
user = m365.get_me()
print(f"Connected as: {user['mail']}")
```

---

## Overview

This module provides seamless integration with Microsoft 365 ecosystem:
- **OneDrive for Business** - Cloud file storage and sharing
- **Microsoft Graph API** - Unified API for Microsoft 365
- **Office Documents** - Create Word, Excel, PowerPoint files
- **Email** - Read and send emails via Microsoft Graph
- **Calendar** - Event management and scheduling

## Features

- ✅ OAuth2 authentication with Microsoft Identity Platform
- ✅ OneDrive file upload/download/management
- ✅ Create Office documents (Word, Excel)
- ✅ Email reading and sending via Graph API
- ✅ Calendar event management
- ✅ User profile and directory access
- ✅ File sharing with link generation
- ✅ Quote request email processing (automated)

## Installation

```bash
pip install requests openpyxl
```

## Quick Start

### 1. Initialize Client

```python
from Microsoft_365_Connection.microsoft365_client import Microsoft365Client

client = Microsoft365Client()
```

### 2. OAuth2 Authentication

```python
# Step 1: Get authorization URL
redirect_uri = "http://localhost:5000/callback"
auth_url = client.get_authorization_url(redirect_uri)
print(f"Visit: {auth_url}")

# Step 2: Exchange code for token (after user authorization)
code = "CODE_FROM_CALLBACK"
tokens = client.exchange_code_for_token(code, redirect_uri)

# Step 3: Get user profile
user = client.get_me()
print(f"Authenticated as: {user['displayName']}")
```

## OneDrive Operations

### Upload Files

```python
# Upload from local file
result = client.upload_file(
    file_path='invoices/invoice_12345.pdf',
    destination_path='InHouse/Invoices/invoice_12345.pdf'
)

# Upload from memory
file_content = b"Invoice content here..."
result = client.upload_file_content(
    file_content=file_content,
    destination_path='InHouse/Invoices/invoice_12346.pdf'
)

print(f"Uploaded: {result['name']}")
print(f"Size: {result['size']} bytes")
print(f"WebUrl: {result['webUrl']}")
```

### Download Files

```python
# Download to local file
client.download_file(
    file_path='InHouse/Invoices/invoice_12345.pdf',
    save_to='downloaded_invoice.pdf'
)

# Download to memory
content = client.download_file_content(
    file_path='InHouse/Invoices/invoice_12345.pdf'
)
```

### List Files

```python
# List root folder
items = client.list_drive_items('root')

# List specific folder
items = client.list_drive_items('InHouse/Invoices')

for item in items:
    print(f"{item['name']} ({item['size']} bytes)")
```

### Create Folders

```python
# Create folder in root
folder = client.create_folder('InHouse', 'root')

# Create nested folder
folder = client.create_folder('Invoices', 'InHouse')
```

### Share Files

```python
# Create view-only link
share_link = client.create_share_link(
    file_path='InHouse/Invoices/invoice_12345.pdf',
    link_type='view'
)
print(f"Share link: {share_link}")

# Create editable link
edit_link = client.create_share_link(
    file_path='InHouse/Documents/quote.docx',
    link_type='edit'
)
```

### Delete Files

```python
client.delete_file('InHouse/Temp/old_file.pdf')
```

## Office Document Creation

### Create Word Documents

```python
# Create simple Word document
result = client.create_word_document(
    file_name='Invoice_12345.docx',
    content='Invoice #12345\nTotal: $1,500.00\nThank you for your business!',
    destination_path='InHouse/Invoices'
)

print(f"Created: {result['webUrl']}")
```

### Create Excel Spreadsheets

```python
# Create Excel with data
data = [
    ['Product', 'Quantity', 'Price', 'Total'],
    ['A4 Flyers', 1000, 0.50, 500.00],
    ['Business Cards', 500, 0.30, 150.00],
    ['Posters', 50, 5.00, 250.00],
    ['', '', 'TOTAL:', 900.00]
]

result = client.create_excel_spreadsheet(
    file_name='Quote_12345.xlsx',
    data=data,
    destination_path='InHouse/Quotes'
)

print(f"Created: {result['webUrl']}")
```

## Email Operations

### Send Email

```python
# Send simple email
client.send_email(
    to_addresses=['customer@example.com'],
    subject='Your Invoice is Ready',
    body='<h1>Invoice #12345</h1><p>Thank you for your business!</p>',
    body_type='HTML'
)

# Send with CC and attachments
client.send_email(
    to_addresses=['customer@example.com'],
    cc_addresses=['manager@inhouseprint.com.au'],
    subject='Quote #12345',
    body='<p>Please find attached your quote.</p>',
    body_type='HTML',
    attachments=[
        {
            '@odata.type': '#microsoft.graph.fileAttachment',
            'name': 'quote.pdf',
            'contentType': 'application/pdf',
            'contentBytes': 'BASE64_ENCODED_CONTENT'
        }
    ]
)
```

## Calendar Operations

### Get Calendar Events

```python
from datetime import datetime, timedelta

# Get events for next 7 days
start = datetime.now()
end = start + timedelta(days=7)

events = client.get_calendar_events(start, end)

for event in events:
    print(f"{event['subject']} - {event['start']['dateTime']}")
```

### Create Calendar Event

```python
from datetime import datetime, timedelta

# Create meeting
start_time = datetime.now() + timedelta(hours=2)
end_time = start_time + timedelta(hours=1)

event = client.create_calendar_event(
    subject='Client Meeting - ABC Corp',
    start_time=start_time,
    end_time=end_time,
    location='Conference Room A',
    body='Discuss new printing project requirements',
    attendees=['client@abccorp.com', 'sales@inhouseprint.com.au']
)

print(f"Created event: {event['webUrl']}")
```

## Practical Use Cases for InHouse Print

### 1. Automated Invoice Generation

```python
# Generate invoice and store in OneDrive
def generate_invoice(order_id, customer_name, amount):
    # Create invoice content
    content = f"""
    INVOICE
    
    Order: {order_id}
    Customer: {customer_name}
    Amount: ${amount:.2f}
    
    Thank you for your business!
    """
    
    # Create Word document in OneDrive
    result = client.create_word_document(
        file_name=f'Invoice_{order_id}.docx',
        content=content,
        destination_path='InHouse/Invoices/2025'
    )
    
    # Create shareable link
    share_link = client.create_share_link(
        file_path=f'InHouse/Invoices/2025/Invoice_{order_id}.docx',
        link_type='view'
    )
    
    # Send email with link
    client.send_email(
        to_addresses=[f'{customer_name}@example.com'],
        subject=f'Invoice #{order_id}',
        body=f'<p>Your invoice is ready: <a href="{share_link}">View Invoice</a></p>'
    )
    
    return share_link
```

### 2. Quote Report Generation

```python
# Generate monthly quote report
def generate_quote_report(month, year):
    # Fetch data from database
    from tools.db_connector import InHousePrintDB
    db = InHousePrintDB("config/database-config.json")
    
    quotes = db.execute_query(f"""
        SELECT TicketID, ClientName, TotalAmount, CreatedDate
        FROM JobTickets
        WHERE MONTH(CreatedDate) = {month} AND YEAR(CreatedDate) = {year}
    """)
    
    # Prepare Excel data
    data = [['Ticket ID', 'Client', 'Amount', 'Date']]
    total = 0
    
    for quote in quotes:
        data.append([
            quote['TicketID'],
            quote['ClientName'],
            quote['TotalAmount'],
            quote['CreatedDate'].strftime('%Y-%m-%d')
        ])
        total += quote['TotalAmount']
    
    data.append(['', '', 'TOTAL:', total])
    
    # Create Excel in OneDrive
    result = client.create_excel_spreadsheet(
        file_name=f'Quotes_{year}_{month:02d}.xlsx',
        data=data,
        destination_path='InHouse/Reports/Monthly'
    )
    
    return result['webUrl']
```

### 3. Job Ticket Archival

```python
# Archive completed job tickets to OneDrive
def archive_job_ticket(ticket_id):
    from tools.db_connector import InHousePrintDB
    db = InHousePrintDB("config/database-config.json")
    
    # Get job ticket data
    ticket = db.execute_query(f"""
        SELECT * FROM JobTickets WHERE TicketID = {ticket_id}
    """)[0]
    
    # Create job ticket PDF content
    content = f"""
    JOB TICKET #{ticket['TicketID']}
    
    Client: {ticket['ClientName']}
    Description: {ticket['Description']}
    Quantity: {ticket['Quantity']}
    Status: {ticket['Status']}
    Total: ${ticket['TotalAmount']:.2f}
    """
    
    # Upload to OneDrive
    result = client.upload_file_content(
        file_content=content.encode('utf-8'),
        destination_path=f'InHouse/Archive/{ticket["CreatedDate"].year}/Ticket_{ticket_id}.txt'
    )
    
    return result['webUrl']
```

### 4. Client Communication Automation

```python
# Send order completion notification
def notify_order_complete(order_id, client_email):
    from tools.db_connector import InHousePrintDB
    db = InHousePrintDB("config/database-config.json")
    
    # Get order details
    order = db.execute_query(f"""
        SELECT * FROM Orders WHERE OrderID = {order_id}
    """)[0]
    
    # Send email
    client.send_email(
        to_addresses=[client_email],
        subject=f'Order #{order_id} Complete - Ready for Pickup',
        body=f"""
        <h2>Your order is complete!</h2>
        <p>Order #{order_id} is ready for pickup.</p>
        <p><strong>Details:</strong></p>
        <ul>
            <li>Description: {order['Description']}</li>
            <li>Quantity: {order['Quantity']}</li>
            <li>Total: ${order['Total']:.2f}</li>
        </ul>
        <p>Thank you for your business!</p>
        """,
        body_type='HTML'
    )
```

### 5. Production Schedule Calendar

```python
# Create calendar events for production schedule
def schedule_production_jobs(date):
    from tools.db_connector import InHousePrintDB
    db = InHousePrintDB("config/database-config.json")
    
    # Get jobs scheduled for date
    jobs = db.execute_query(f"""
        SELECT TicketID, ClientName, Description, ScheduledTime
        FROM JobTickets
        WHERE CAST(ScheduledTime AS DATE) = '{date.strftime('%Y-%m-%d')}'
    """)
    
    # Create calendar event for each job
    for job in jobs:
        start_time = job['ScheduledTime']
        end_time = start_time + timedelta(hours=2)
        
        client.create_calendar_event(
            subject=f"Job #{job['TicketID']} - {job['ClientName']}",
            start_time=start_time,
            end_time=end_time,
            location='Production Floor',
            body=f"<p>{job['Description']}</p>",
            attendees=['production@inhouseprint.com.au']
        )
```

## Error Handling

```python
try:
    result = client.upload_file('local.pdf', 'OneDrive/file.pdf')
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 401:
        print("Token expired, refreshing...")
        client.refresh_access_token()
    else:
        print(f"HTTP Error: {e}")
except ValueError as e:
    print(f"Configuration Error: {e}")
except Exception as e:
    print(f"Unexpected Error: {e}")
```

## Testing

Run the module directly to test:

```bash
cd G_Folder/Microsoft_365_Connection
python microsoft365_client.py
```

## Documentation

- [Microsoft Graph API](https://learn.microsoft.com/en-us/graph/)
- [OneDrive API](https://learn.microsoft.com/en-us/onedrive/developer/)
- [OAuth2 Authentication](https://learn.microsoft.com/en-us/azure/active-directory/develop/)

## Support

For issues or questions, contact the InHouse Print development team.

## License

Internal use only - InHouse Print Management System
