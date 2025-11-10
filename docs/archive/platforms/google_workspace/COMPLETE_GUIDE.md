# 🚀 Google Workspace Integration - Complete Guide

**Version:** 2.0.0  
**Last Updated:** October 27, 2025  
**Status:** ✅ Production Ready

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Setup & Configuration](#setup--configuration)
4. [Package Structure](#package-structure)
5. [API Reference](#api-reference)
6. [Usage Examples](#usage-examples)
7. [Advanced Features](#advanced-features)
8. [Troubleshooting](#troubleshooting)
9. [Migration Notes](#migration-notes)
10. [Best Practices](#best-practices)

---

## Overview

The `google_workspace` package provides a unified Python interface for all Google Workspace services:

- ✅ **103 functions** across 9 modules
- ✅ **Full backward compatibility** with old import paths
- ✅ **Comprehensive error handling** and logging
- ✅ **Service account authentication** for automated access
- ✅ **Professional charts & reports** generation

### Supported Services

| Service | Functions | Key Features |
|---------|-----------|--------------|
| **Docs** | 34 | Markdown conversion, formatting, tables, charts |
| **Drive** | 15 | File management, folders, permissions, sharing |
| **Gmail** | 24 | Email sending (API + SMTP), drafts, labels, filters |
| **Sheets** | 7 | Data read/write, formulas, chart integration |
| **Forms** | 4 | Form creation, questions, response retrieval |
| **Calendar** | 5 | Event CRUD, calendar management |
| **Analytics** | 12 | GA4 reports, metrics, user behavior tracking |
| **Cloud Run** | 4 | Serverless deployment, service management |
| **Auth** | 7 | Unified service account authentication |

---

## Quick Start

### Installation

```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib gspread
```

### Basic Usage

```python
from google_workspace import (
    google_docs_create_from_markdown,
    google_drive_create_folder,
    gmail_send_email
)

# Create a Google Doc from markdown
doc_info = google_docs_create_from_markdown(
    title="My Report",
    markdown_content="# Hello World\n\nThis is **bold** text."
)
print(f"Created: {doc_info['url']}")

# Create a Drive folder
folder = google_drive_create_folder("Reports 2025")
print(f"Folder ID: {folder['id']}")

# Send an email
result = gmail_send_email(
    to="user@example.com",
    subject="Test",
    body="Hello from google_workspace!"
)
```

---

## Setup & Configuration

### 1. Service Account Setup

#### Create Service Account (Google Cloud Console)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create/select project
3. Enable APIs:
   - Google Docs API
   - Google Drive API
   - Gmail API
   - Google Sheets API
   - Google Forms API
   - Google Calendar API
   - Google Analytics API
4. Create Service Account:
   - IAM & Admin → Service Accounts → Create
   - Grant roles: Editor, Service Account User
5. Create JSON key:
   - Click service account → Keys → Add Key → JSON
   - Download `service-account.json`

#### Required API Scopes

```python
SCOPES = [
    'https://www.googleapis.com/auth/documents',      # Docs
    'https://www.googleapis.com/auth/drive',          # Drive
    'https://www.googleapis.com/auth/spreadsheets',   # Sheets
    'https://www.googleapis.com/auth/gmail.send',     # Gmail
    'https://www.googleapis.com/auth/forms',          # Forms
    'https://www.googleapis.com/auth/calendar',       # Calendar
    'https://www.googleapis.com/auth/analytics.readonly'  # Analytics
]
```

### 2. Environment Variables

**Option 1: Set environment variable**
```bash
# Windows
set GOOGLE_SERVICE_ACCOUNT_JSON=C:\path\to\service-account.json

# Linux/Mac
export GOOGLE_SERVICE_ACCOUNT_JSON=/path/to/service-account.json
```

**Option 2: Use .env file**
```bash
# .env file
GOOGLE_SERVICE_ACCOUNT_JSON=C:\path\to\service-account.json
GOOGLE_APPLICATION_CREDENTIALS=C:\path\to\service-account.json
```

### 3. Gmail SMTP Setup (Optional)

For Gmail sending via SMTP (alternative to API):

```bash
# .env file
SMTP_EMAIL=your.email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

**Get Gmail App Password:**
1. Go to Google Account → Security
2. Enable 2-Factor Authentication
3. App Passwords → Generate → Select "Mail" and device
4. Use 16-character password in SMTP_PASSWORD

---

## Package Structure

```
google_workspace/
├── __init__.py                 # Main entry point (103 exports)
├── README.md                   # API documentation
├── COMPLETE_GUIDE.md          # This comprehensive guide
│
├── google_auth_helper.py      # Authentication (7 functions)
│   ├── get_service_account_credentials()
│   ├── build_docs_service()
│   ├── build_drive_service()
│   ├── build_gmail_service()
│   ├── build_forms_service()
│   ├── build_calendar_service()
│   └── build_analytics_service()
│
├── google_docs.py             # Docs/Sheets/Charts (3,583 lines, 34 functions)
│   ├── Document Operations (13 functions)
│   ├── Formatting Operations (9 functions)
│   ├── Content Operations (3 functions)
│   ├── Export Operations (6 functions)
│   ├── Sheets Operations (3 functions)
│   └── Charts Operations (3 functions)
│
├── google_drive.py            # File Management (15 functions)
│   ├── File Operations (7 functions)
│   ├── Folder Management (2 functions)
│   ├── Permissions (3 functions)
│   └── Utilities (3 functions)
│
├── gmail.py                   # Email Operations (24 functions)
│   ├── Email Sending (3 functions: API + SMTP)
│   ├── Draft Management (2 functions)
│   ├── Message Operations (10 functions)
│   ├── Label Management (4 functions)
│   ├── Filter Management (3 functions)
│   └── Account Operations (2 functions)
│
├── gsheets.py                 # Alternative Sheets (4 functions)
│   └── gspread-based implementation
│
├── google_forms.py            # Forms Management (4 functions)
├── google_calendar.py         # Calendar Events (5 functions)
├── google_analytics.py        # Analytics Reports (12 functions)
└── google_cloud_run.py        # Cloud Deployments (4 functions)
```

---

## API Reference

### 🔐 Authentication (google_auth_helper)

#### `get_service_account_credentials(scopes)`
Get authenticated credentials for Google APIs.

```python
from google_workspace import get_service_account_credentials

creds = get_service_account_credentials([
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive'
])
```

#### Service Builders
Pre-configured service builders for each API:

```python
from google_workspace import (
    build_docs_service,
    build_drive_service,
    build_gmail_service,
    build_forms_service,
    build_calendar_service,
    build_analytics_service
)

docs_service = build_docs_service()
drive_service = build_drive_service()
```

---

### 📄 Google Docs Operations

#### Document Creation

**`google_docs_create_document(title, with_sample_content=False)`**

Create a new blank Google Doc.

```python
from google_workspace import google_docs_create_document

doc = google_docs_create_document("My Document", with_sample_content=True)
# Returns: {'id': 'doc_id', 'url': 'https://docs.google.com/...'}
```

**`google_docs_create_from_markdown(title, markdown_content)`**

Create a Google Doc from markdown text (most powerful feature).

```python
from google_workspace import google_docs_create_from_markdown

markdown = """
# Project Report

## Executive Summary
This report covers **Q4 2024** performance.

### Key Metrics
- Revenue: $1.2M (+15% YoY)
- Users: 50,000 (+25% YoY)
- Satisfaction: 4.5/5 stars

## Financial Data

| Quarter | Revenue | Expenses | Profit |
|---------|---------|----------|--------|
| Q1      | $800K   | $600K    | $200K  |
| Q2      | $900K   | $650K    | $250K  |
| Q3      | $1.0M   | $700K    | $300K  |
| Q4      | $1.2M   | $800K    | $400K  |

### Action Items
1. Increase marketing budget
2. Hire 5 new engineers
3. Launch product v2.0

> **Note:** All figures are preliminary
"""

doc = google_docs_create_from_markdown("Q4 Report", markdown)
print(f"Created: {doc['url']}")
```

**Supported Markdown Features:**
- ✅ Headings (H1-H6)
- ✅ **Bold** and *italic* text
- ✅ Bullet lists and numbered lists
- ✅ Tables (with styling)
- ✅ Blockquotes
- ✅ Horizontal rules
- ✅ Inline code and code blocks
- ❌ Images (use `google_docs_insert_image` separately)
- ❌ Links (coming soon)

#### Document Updates

**`google_docs_smart_update(document_id, markdown_content, insertion_position='end')`**

Intelligently update a document with new markdown content.

```python
from google_workspace import google_docs_smart_update

google_docs_smart_update(
    document_id='your_doc_id',
    markdown_content='## New Section\n\nAdditional content here.',
    insertion_position='end'  # or 'start'
)
```

**`google_docs_append_text(document_id, text)`**

Add plain text to end of document.

```python
from google_workspace import google_docs_append_text

google_docs_append_text('doc_id', 'This text goes at the end.')
```

**`google_docs_replace_text(document_id, find_text, replace_text, match_case=True)`**

Find and replace text in document.

```python
from google_workspace import google_docs_replace_text

google_docs_replace_text('doc_id', 'old_value', 'new_value')
```

#### Formatting Operations

**`google_docs_format_text(document_id, start_index, end_index, bold=None, italic=None, font_size=None, foreground_color=None)`**

Format text at specific indices.

```python
from google_workspace import google_docs_format_text

google_docs_format_text(
    'doc_id',
    start_index=1,
    end_index=50,
    bold=True,
    font_size=14,
    foreground_color={'red': 0.0, 'green': 0.0, 'blue': 1.0}  # Blue
)
```

**`google_docs_create_heading(document_id, text, heading_level=1, index=1)`**

Insert a heading.

```python
from google_workspace import google_docs_create_heading

google_docs_create_heading('doc_id', 'Chapter 1', heading_level=1)
```

**`google_docs_create_list(document_id, items, start_index=1, list_type='bullet')`**

Create bullet or numbered list.

```python
from google_workspace import google_docs_create_list

google_docs_create_list(
    'doc_id',
    items=['First item', 'Second item', 'Third item'],
    list_type='bullet'  # or 'numbered'
)
```

**`google_docs_insert_table(document_id, rows, columns, index=1)`**

Insert a table.

```python
from google_workspace import google_docs_insert_table

google_docs_insert_table('doc_id', rows=5, columns=3)
```

**`google_docs_insert_image(document_id, image_url, index=1, width=None, height=None)`**

Insert image from URL.

```python
from google_workspace import google_docs_insert_image

google_docs_insert_image(
    'doc_id',
    'https://example.com/image.png',
    width=400,
    height=300
)
```

#### Export Operations

**`google_docs_export_as_pdf(document_id)`**

Export document as PDF bytes.

```python
from google_workspace import google_docs_export_as_pdf

pdf_bytes = google_docs_export_as_pdf('doc_id')
with open('output.pdf', 'wb') as f:
    f.write(pdf_bytes)
```

**`google_docs_export_as_html(document_id)`**

Export as HTML string.

**`google_docs_export_as_markdown(document_id)`**

Export as markdown (approximate conversion).

---

### 📊 Google Sheets Operations

**`google_sheets_create(title, data=None, headers=None)`**

Create a new spreadsheet with optional data.

```python
from google_workspace import google_sheets_create

data = [
    [100, 200, 300],
    [150, 250, 350],
    [200, 300, 400]
]
headers = ['Q1', 'Q2', 'Q3']

sheet = google_sheets_create('Sales Data', data=data, headers=headers)
print(f"Spreadsheet: {sheet['url']}")
```

**`google_sheets_read_data(spreadsheet_id, range_name='Sheet1!A1:Z1000')`**

Read data from spreadsheet.

```python
from google_workspace import google_sheets_read_data

data = google_sheets_read_data('sheet_id', 'Sheet1!A1:D10')
for row in data:
    print(row)
```

**`google_sheets_append_data(spreadsheet_id, data, sheet_name='Sheet1')`**

Append rows to spreadsheet.

```python
from google_workspace import google_sheets_append_data

new_data = [
    ['Product A', 100, 50, 5000],
    ['Product B', 150, 75, 11250]
]

google_sheets_append_data('sheet_id', new_data)
```

#### Alternative: gspread-based Functions

**`gsheets_read(spreadsheet_id, range_name='Sheet1')`**

```python
from google_workspace import gsheets_read

data = gsheets_read('sheet_id', 'Sheet1')
```

**`gsheets_write(spreadsheet_id, range_name, values)`**

**`gsheets_append(spreadsheet_id, range_name, values)`**

**`gsheets_create(title, data=None, headers=None)`**

---

### 📈 Charts & Professional Reports

**`google_charts_create(title, chart_type, data, headers=None, chart_options=None)`**

Create standalone chart in Google Sheets.

```python
from google_workspace import google_charts_create

data = {
    'Revenue': [100000, 120000, 115000, 130000],
    'Expenses': [80000, 85000, 90000, 88000],
    'Profit': [20000, 35000, 25000, 42000]
}
headers = ['Q1', 'Q2', 'Q3', 'Q4']

chart = google_charts_create(
    title='Quarterly Performance',
    chart_type='column',  # or 'line', 'bar', 'pie'
    data=data,
    headers=headers
)
```

**`google_docs_create_professional_report_with_charts(title, summary_text, chart_data, headers, chart_title, chart_type='column')`**

Create a professional report document with embedded charts.

```python
from google_workspace import google_docs_create_professional_report_with_charts

chart_data = {
    'Revenue': [800000, 900000, 1000000, 1200000],
    'Expenses': [600000, 650000, 700000, 800000],
    'Profit': [200000, 250000, 300000, 400000]
}

headers = ['Q1 2024', 'Q2 2024', 'Q3 2024', 'Q4 2024']

doc = google_docs_create_professional_report_with_charts(
    title='Annual Financial Report 2024',
    summary_text='Strong growth across all quarters with improving margins.',
    chart_data=chart_data,
    headers=headers,
    chart_title='2024 Financial Performance',
    chart_type='column'
)

print(f"Report URL: {doc['url']}")
```

**Features:**
- ✅ Professional document formatting
- ✅ Auto-generated data tables
- ✅ Embedded charts from Google Sheets
- ✅ Styled headers and sections
- ✅ Automatic calculations (totals, averages)

---

### 📁 Google Drive Operations

#### File Management

**`google_drive_list_files(query=None, max_results=100)`**

List files with optional query.

```python
from google_workspace import google_drive_list_files

# List all files
files = google_drive_list_files()

# Search for PDF files
pdfs = google_drive_list_files("mimeType='application/pdf'")

# Find files modified this week
recent = google_drive_list_files("modifiedTime > '2024-10-20T00:00:00'")
```

**`google_drive_upload_file(file_path, file_name=None, parent_folder_id=None)`**

Upload a file to Drive.

```python
from google_workspace import google_drive_upload_file

file_info = google_drive_upload_file(
    'C:\\path\\to\\report.pdf',
    file_name='Q4 Report.pdf',
    parent_folder_id='folder_id_here'
)
print(f"Uploaded: {file_info['url']}")
```

**`google_drive_create_folder(folder_name, parent_folder_id=None)`**

Create a folder.

```python
from google_workspace import google_drive_create_folder

folder = google_drive_create_folder('Financial Reports 2025')
print(f"Folder ID: {folder['id']}")

# Create subfolder
subfolder = google_drive_create_folder('Q1', parent_folder_id=folder['id'])
```

**`google_drive_move_file(file_id, new_parent_folder_id)`**

Move file to different folder.

```python
from google_workspace import google_drive_move_file

google_drive_move_file('file_id', 'new_folder_id')
```

**`google_drive_delete_file(file_id)`**

Delete (trash) a file.

#### Permissions & Sharing

**`google_drive_share_file(file_id, email, role='reader')`**

Share file with user.

```python
from google_workspace import google_drive_share_file

google_drive_share_file(
    'file_id',
    'user@example.com',
    role='writer'  # 'reader', 'writer', 'commenter'
)
```

**`google_drive_list_permissions(file_id)`**

List all permissions on file.

**`google_drive_remove_permission(file_id, permission_id)`**

Remove permission from file.

---

### 📧 Gmail Operations

#### Email Sending (API Method)

**`gmail_send_email(to, subject, body, attachments=None, cc=None, bcc=None)`**

Send email via Gmail API (recommended).

```python
from google_workspace import gmail_send_email

result = gmail_send_email(
    to='recipient@example.com',
    subject='Monthly Report',
    body='Please find the attached report.',
    cc=['manager@example.com'],
    attachments=['C:\\path\\to\\report.pdf']
)
print(f"Sent: {result['id']}")
```

#### Email Sending (SMTP Method)

**`gmail_send_email_smtp(to, subject, body, attachments=None)`**

Send plain text email via SMTP (alternative method).

```python
from google_workspace import gmail_send_email_smtp

gmail_send_email_smtp(
    to='user@example.com',
    subject='Test Email',
    body='This is a plain text email via SMTP.'
)
```

**`gmail_send_email_smtp_html(to, subject, html_body, attachments=None)`**

Send HTML email via SMTP.

```python
from google_workspace import gmail_send_email_smtp_html

html = """
<html>
<body>
<h1>Welcome!</h1>
<p>This is an <strong>HTML</strong> email.</p>
</body>
</html>
"""

gmail_send_email_smtp_html('user@example.com', 'Welcome', html)
```

#### Draft Management

**`gmail_create_draft(to, subject, body, attachments=None)`**

Create email draft.

```python
from google_workspace import gmail_create_draft

draft = gmail_create_draft(
    to='user@example.com',
    subject='Draft Email',
    body='This is saved as a draft.'
)
```

**`gmail_send_draft(draft_id)`**

Send existing draft.

#### Message Operations

**`gmail_list_messages(query=None, max_results=100, label_ids=None)`**

List emails.

```python
from google_workspace import gmail_list_messages

# Unread emails
unread = gmail_list_messages(query='is:unread', max_results=10)

# Emails from specific sender
from_boss = gmail_list_messages(query='from:boss@company.com')

# Emails with label
important = gmail_list_messages(label_ids=['IMPORTANT'])
```

**`gmail_search_messages(query, max_results=100)`**

Search emails.

**`gmail_get_message(message_id)`**

Get full message details.

**`gmail_mark_as_read(message_id)`**

**`gmail_mark_as_unread(message_id)`**

**`gmail_archive_message(message_id)`**

**`gmail_delete_message(message_id)`**

---

### 📋 Google Forms Operations

**`google_forms_create_form(title, description=None)`**

Create a new form.

```python
from google_workspace import google_forms_create_form

form = google_forms_create_form(
    title='Customer Feedback Survey',
    description='Help us improve our service'
)
print(f"Form: {form['url']}")
```

**`google_forms_add_question(form_id, question_text, question_type='short_answer')`**

Add question to form.

```python
from google_workspace import google_forms_add_question

google_forms_add_question(
    form['id'],
    'What is your email address?',
    question_type='short_answer'
)

google_forms_add_question(
    form['id'],
    'Rate our service (1-5)',
    question_type='scale'
)
```

**Question Types:** `short_answer`, `paragraph`, `multiple_choice`, `checkboxes`, `dropdown`, `scale`, `date`, `time`

**`google_forms_get_responses(form_id)`**

Get all form responses.

---

### 📅 Google Calendar Operations

**`google_calendar_create_event(summary, start_time, end_time, description=None, attendees=None)`**

Create calendar event.

```python
from google_workspace import google_calendar_create_event
from datetime import datetime, timedelta

start = datetime.now() + timedelta(days=1)
end = start + timedelta(hours=2)

event = google_calendar_create_event(
    summary='Team Meeting',
    start_time=start.isoformat(),
    end_time=end.isoformat(),
    description='Weekly sync meeting',
    attendees=['team@company.com']
)
```

**`google_calendar_list_events(calendar_id='primary', max_results=10)`**

List upcoming events.

**`google_calendar_update_event(event_id, summary=None, start_time=None, end_time=None)`**

Update event.

**`google_calendar_delete_event(event_id)`**

Delete event.

---

### 📊 Google Analytics Operations

**`google_analytics_run_report(property_id, start_date, end_date, metrics, dimensions=None)`**

Run custom analytics report.

```python
from google_workspace import google_analytics_run_report

report = google_analytics_run_report(
    property_id='123456789',
    start_date='30daysAgo',
    end_date='today',
    metrics=['activeUsers', 'sessions'],
    dimensions=['date', 'country']
)
```

**`google_analytics_get_page_views(property_id, start_date='7daysAgo', end_date='today')`**

Get page view statistics.

**`google_analytics_get_user_behavior(property_id, start_date='7daysAgo', end_date='today')`**

Get user engagement metrics.

**`google_analytics_get_conversions(property_id, start_date='7daysAgo', end_date='today')`**

Get conversion data.

---

## Usage Examples

### Example 1: Create Comprehensive Report

```python
from google_workspace import (
    google_docs_create_from_markdown,
    google_drive_create_folder,
    google_drive_move_file,
    gmail_send_email
)

# Create folder
folder = google_drive_create_folder('Q4 2024 Reports')

# Create report
markdown = """
# Q4 2024 Performance Report

## Summary
Strong quarter with 25% growth.

## Key Metrics
- Revenue: $1.2M
- New customers: 150
- Retention: 95%

## Next Steps
1. Expand to new markets
2. Hire additional staff
3. Launch new product line
"""

doc = google_docs_create_from_markdown('Q4 Report', markdown)

# Move to folder
google_drive_move_file(doc['id'], folder['id'])

# Share with team
gmail_send_email(
    to='team@company.com',
    subject='Q4 Report Ready',
    body=f"View report: {doc['url']}"
)
```

### Example 2: Automated Data Processing

```python
from google_workspace import (
    gsheets_read,
    google_docs_create_from_markdown,
    google_drive_create_folder
)
import pandas as pd

# Read data from sheets
data = gsheets_read('spreadsheet_id', 'Sales!A1:D100')
df = pd.DataFrame(data[1:], columns=data[0])

# Calculate metrics
total_revenue = df['Revenue'].sum()
avg_order = df['Revenue'].mean()

# Generate report
markdown = f"""
# Sales Analysis

## Overview
Total Revenue: ${total_revenue:,.2f}
Average Order: ${avg_order:,.2f}

## Top Products
{df.nlargest(5, 'Revenue')[['Product', 'Revenue']].to_markdown()}
"""

doc = google_docs_create_from_markdown('Sales Analysis', markdown)
```

### Example 3: Bulk File Organization

```python
from google_workspace import (
    google_drive_list_files,
    google_drive_create_folder,
    google_drive_move_file
)

# Create organized folder structure
folders = {}
for year in [2023, 2024, 2025]:
    folder = google_drive_create_folder(f'Reports {year}')
    folders[year] = folder['id']

# List all report files
files = google_drive_list_files("name contains 'Report'")

# Organize by year (extract from filename)
for file in files:
    for year in folders:
        if str(year) in file['name']:
            google_drive_move_file(file['id'], folders[year])
            print(f"Moved {file['name']} to {year} folder")
```

---

## Advanced Features

### Markdown to Google Docs Conversion

The `google_docs_create_from_markdown` function supports advanced markdown:

```python
markdown = """
# Report Title

## Section with Nested Lists

### Numbered List
1. First item
   - Sub-item A
   - Sub-item B
2. Second item
   1. Nested number
   2. Another nested

### Complex Table

| Product | Q1 | Q2 | Q3 | Q4 | Total |
|---------|----|----|----|----|-------|
| Widget A | $10K | $12K | $15K | $18K | $55K |
| Widget B | $8K | $9K | $11K | $13K | $41K |
| **Total** | **$18K** | **$21K** | **$26K** | **$31K** | **$96K** |

### Code Example

```python
def calculate_revenue(sales):
    return sum(sales) * 1.1
```

> **Important Note:** All figures include 10% tax

---

## Next Steps
- Expand to new markets
- Increase production capacity
"""

doc = google_docs_create_from_markdown('Advanced Report', markdown)
```

### Professional Charts with Custom Styling

```python
from google_workspace import google_docs_create_professional_report_with_charts

chart_data = {
    'Product A': [50000, 55000, 60000, 65000, 70000, 75000],
    'Product B': [30000, 32000, 35000, 38000, 40000, 42000],
    'Product C': [20000, 22000, 25000, 27000, 30000, 33000]
}

headers = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']

doc = google_docs_create_professional_report_with_charts(
    title='H1 2024 Product Sales Analysis',
    summary_text='All products showed consistent growth throughout H1 2024. Product A leads with 50% market share.',
    chart_data=chart_data,
    headers=headers,
    chart_title='Product Sales Comparison (H1 2024)',
    chart_type='line'  # Shows trends over time
)
```

**Supported Chart Types:**
- `column` - Vertical bars (best for comparing categories)
- `bar` - Horizontal bars (good for rankings)
- `line` - Line graphs (best for trends over time)
- `pie` - Pie chart (good for showing proportions)
- `area` - Area chart (cumulative trends)

---

## Troubleshooting

### Common Issues

#### 1. "Service account credentials not found"

**Problem:** Environment variable not set or file not found.

**Solution:**
```bash
# Windows
set GOOGLE_SERVICE_ACCOUNT_JSON=C:\full\path\to\service-account.json

# Or in Python
import os
os.environ['GOOGLE_SERVICE_ACCOUNT_JSON'] = r'C:\path\to\service-account.json'
```

#### 2. "Insufficient permissions" / API errors

**Problem:** Service account lacks necessary API permissions.

**Solutions:**
1. **Enable APIs in Google Cloud Console**
   - Go to APIs & Services → Enable APIs
   - Enable: Docs, Drive, Gmail, Sheets, Forms, Calendar

2. **Share files with service account**
   ```python
   # The service account email is in your JSON file
   # Share Drive folders with: service-account@project.iam.gserviceaccount.com
   ```

3. **Grant domain-wide delegation (for Gmail)**
   - Admin Console → Security → API Controls
   - Manage Domain Wide Delegation
   - Add service account client ID
   - Add scopes: https://www.googleapis.com/auth/gmail.send

#### 3. "Cannot import name X"

**Problem:** Using incorrect function name.

**Solution:** Check actual function names:
```python
# Correct
from google_workspace import google_docs_create_from_markdown

# Wrong - function doesn't exist
from google_workspace import google_docs_create_document_from_markdown
```

See API Reference for exact function names.

#### 4. Gmail sending fails

**Problem:** Service account doesn't have Gmail delegation.

**Solutions:**

**Option A: Use SMTP instead**
```python
from google_workspace import gmail_send_email_smtp

gmail_send_email_smtp('to@example.com', 'Subject', 'Body')
```

**Option B: Set up delegation**
1. Admin Console → Security → API Controls
2. Domain-wide delegation → Add service account
3. Add scope: `https://www.googleapis.com/auth/gmail.send`

#### 5. Charts not appearing in documents

**Problem:** Chart images not generated or permissions issue.

**Solution:**
```python
# Ensure Drive API is enabled
# Charts are created in a temporary sheet, then inserted
# Service account needs Drive write permissions
```

#### 6. Tables not formatting correctly

**Problem:** Markdown table syntax issue.

**Solution:**
```python
# Correct table syntax
markdown = """
| Header 1 | Header 2 | Header 3 |
|----------|----------|----------|
| Data 1   | Data 2   | Data 3   |
"""

# Must have header row, separator row with dashes, then data rows
```

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now all google_workspace operations will show detailed logs
from google_workspace import google_docs_create_from_markdown
doc = google_docs_create_from_markdown('Test', '# Hello')
```

---

## Migration Notes

### From Old Import Paths

The package maintains full backward compatibility:

```python
# OLD (still works via redirect files)
from tools.implementations.google_docs import google_docs_create_from_markdown
from tools.implementations.google_drive import google_drive_create_folder

# NEW (recommended)
from google_workspace import google_docs_create_from_markdown, google_drive_create_folder
```

### Migration Checklist

- [ ] Update imports to use `google_workspace` package
- [ ] Test all functionality with new imports
- [ ] Update any scripts that reference old paths
- [ ] Remove `.backup` files once confirmed working
- [ ] Update documentation/comments in your code

### What Changed

**v1.0.0 → v2.0.0:**
- ✅ All functions moved to `google_workspace/` package
- ✅ 103 total functions (added Analytics, Cloud Run, Forms, Calendar)
- ✅ Fixed function names (sheets_read → sheets_read_data)
- ✅ Added Gmail SMTP alternatives
- ✅ Improved error handling and logging
- ✅ Comprehensive documentation

---

## Best Practices

### 1. Use Environment Variables

```python
# ✅ Good - use environment variables
import os
os.environ['GOOGLE_SERVICE_ACCOUNT_JSON'] = r'C:\path\to\creds.json'

# ❌ Bad - hardcode paths in code
service_account_file = 'C:\\hardcoded\\path.json'
```

### 2. Error Handling

```python
# ✅ Good - handle errors gracefully
try:
    doc = google_docs_create_from_markdown('Report', markdown)
    print(f"Success: {doc['url']}")
except Exception as e:
    print(f"Failed to create document: {e}")
    # Implement fallback or retry logic
```

### 3. Organize Files in Drive

```python
# ✅ Good - organize into folders
reports_folder = google_drive_create_folder('Reports 2025')
doc = google_docs_create_from_markdown('Q1 Report', markdown)
google_drive_move_file(doc['id'], reports_folder['id'])

# ❌ Bad - leave files in root
doc = google_docs_create_from_markdown('Report', markdown)
```

### 4. Batch Operations

```python
# ✅ Good - batch create multiple docs
docs = []
for quarter in ['Q1', 'Q2', 'Q3', 'Q4']:
    markdown = generate_report(quarter)
    doc = google_docs_create_from_markdown(f'{quarter} Report', markdown)
    docs.append(doc)

# Then organize all at once
for doc in docs:
    google_drive_move_file(doc['id'], folder_id)
```

### 5. Use Markdown for Complex Documents

```python
# ✅ Good - use markdown for rich formatting
markdown = """
# Professional Report

## Executive Summary
[content]

## Data Analysis
[tables and charts]
"""
doc = google_docs_create_from_markdown('Report', markdown)

# ❌ Tedious - manual formatting with individual API calls
doc = google_docs_create_document('Report')
google_docs_create_heading(doc['id'], 'Professional Report', 1)
google_docs_insert_text(doc['id'], 'Executive Summary')
# ... many more API calls
```

### 6. Share Files Appropriately

```python
# ✅ Good - specific permissions
google_drive_share_file(file_id, 'viewer@company.com', role='reader')
google_drive_share_file(file_id, 'editor@company.com', role='writer')

# ⚠️ Careful - public access
google_drive_share_file(file_id, 'anyone@anyone', role='reader')
```

---

## Performance Tips

1. **Batch API calls** - Create multiple documents before organizing
2. **Use markdown** - Fewer API calls than manual formatting
3. **Cache credentials** - Service builders cache authenticated services
4. **Limit query results** - Use `max_results` parameter to avoid timeouts
5. **Parallel processing** - Use threading for independent operations

---

## Security Considerations

1. **Protect service account JSON** - Never commit to version control
2. **Use environment variables** - Don't hardcode credentials
3. **Limit service account permissions** - Only grant necessary API access
4. **Rotate keys regularly** - Create new service account keys periodically
5. **Monitor API usage** - Check Google Cloud Console for unusual activity
6. **Share files carefully** - Review permissions before sharing

---

## Support & Resources

### Documentation
- **Package README:** `google_workspace/README.md`
- **API Reference:** This guide
- **Migration Notes:** `GOOGLE_WORKSPACE_MIGRATION_COMPLETE.md`

### External Resources
- [Google Docs API Docs](https://developers.google.com/docs/api)
- [Google Drive API Docs](https://developers.google.com/drive/api)
- [Gmail API Docs](https://developers.google.com/gmail/api)
- [Google Sheets API Docs](https://developers.google.com/sheets/api)

### Getting Help

1. Check this guide for common issues
2. Review function signatures in API Reference
3. Enable debug logging to see detailed errors
4. Check Google Cloud Console for API quotas/limits

---

## Package Statistics

| Metric | Value |
|--------|-------|
| **Total Functions** | 103 |
| **Total Modules** | 9 |
| **Lines of Code** | ~6,185 |
| **Documentation** | 100% coverage |
| **Backward Compatible** | ✅ Yes |
| **Production Ready** | ✅ Yes |

---

## Version History

### v2.0.0 (Current - October 27, 2025)
- ✅ Consolidated all documentation into COMPLETE_GUIDE.md
- ✅ Comprehensive API reference
- ✅ 50+ usage examples
- ✅ Troubleshooting guide
- ✅ Best practices section

### v1.0.0 (October 24, 2025)
- ✅ Initial package release
- ✅ 103 functions migrated
- ✅ Backward compatibility layer
- ✅ Basic documentation

---

**🎉 You're ready to use the Google Workspace package!**

Start with the [Quick Start](#quick-start) section and explore the [Usage Examples](#usage-examples).

For questions or issues, enable debug logging and review the [Troubleshooting](#troubleshooting) section.
