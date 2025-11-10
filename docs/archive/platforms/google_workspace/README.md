# Google Workspace Integration Package

## Overview

Centralized Python package for all Google Workspace API integrations. This package provides a unified interface for interacting with Google services including Docs, Sheets, Drive, Gmail, Calendar, Forms, Analytics, and Cloud Run.

## 📦 Package Structure

```
google_workspace/
├── __init__.py                 # Main package entry point with all exports
├── google_auth_helper.py       # Unified service account authentication
├── google_docs.py              # Docs, Sheets, and Charts operations (3583 lines)
├── google_drive.py             # File management, folders, permissions
├── google_forms.py             # Form creation and management
├── google_calendar.py          # Event management and scheduling
├── google_analytics.py         # GA4 tracking and reporting
├── google_cloud_run.py         # Serverless deployments
├── gmail.py                    # Email operations (746 lines, 21 functions)
└── gsheets.py                  # gspread-based sheets operations (186 lines)
```

## 🚀 Installation & Setup

### Prerequisites

```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib gspread
```

### Environment Variables

Set up your Google service account credentials:

```bash
# Required environment variables
GOOGLE_SERVICE_ACCOUNT_JSON=path/to/service-account.json
# OR
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
```

## 📖 Usage Guide

### Import Patterns

**Option 1: Direct import from package (recommended)**
```python
from google_workspace import (
    google_docs_create_from_markdown,
    google_drive_create_folder,
    gmail_send_email,
    gsheets_read
)
```

**Option 2: Import from submodules**
```python
from google_workspace.google_docs import google_docs_create_from_markdown
from google_workspace.google_drive import google_drive_create_folder
from google_workspace.gmail import gmail_send_email
```

**Option 3: Backward compatibility (old import paths)**
```python
# Still works for existing code
from tools.implementations.google_docs import google_docs_create_from_markdown
from tools.implementations.google_drive import google_drive_create_folder
```

### Quick Start Examples

#### Create a Google Doc from Markdown
```python
from google_workspace import google_docs_create_from_markdown

markdown_content = """
# Project Report

## Summary
This is a **bold** statement with *italic* text.

- Point 1
- Point 2
- Point 3

| Column A | Column B |
|----------|----------|
| Data 1   | Data 2   |
"""

doc_info = google_docs_create_from_markdown(
    title="My Report",
    markdown_content=markdown_content
)

print(f"✅ Created document: {doc_info['url']}")
```

#### Create a Google Drive Folder
```python
from google_workspace import google_drive_create_folder

folder_info = google_drive_create_folder(
    folder_name="Financial Reports 2025",
    parent_folder_id=None  # Root folder
)

print(f"✅ Folder ID: {folder_info['id']}")
print(f"✅ Folder URL: {folder_info['url']}")
```

#### Send an Email via Gmail
```python
from google_workspace import gmail_send_email

result = gmail_send_email(
    to="recipient@example.com",
    subject="Test Email",
    body="This is a test email from the Google Workspace package."
)

print(f"✅ Email sent: {result['id']}")
```

#### Read Google Sheets Data
```python
from google_workspace import gsheets_read

data = gsheets_read(
    spreadsheet_id="your_spreadsheet_id",
    range_name="Sheet1!A1:D10"
)

for row in data:
    print(row)
```

#### Create Professional Charts Report
```python
from google_workspace import google_docs_create_professional_report_with_charts

# Sample financial data
chart_data = {
    'Revenue': [100000, 120000, 115000, 130000, 125000, 140000],
    'Expenses': [80000, 85000, 90000, 88000, 92000, 95000],
    'Profit': [20000, 35000, 25000, 42000, 33000, 45000]
}

months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']

doc_info = google_docs_create_professional_report_with_charts(
    title="Q2 Financial Report",
    summary_text="Revenue shows strong growth with profit margins improving.",
    chart_data=chart_data,
    headers=months,
    chart_title="Q2 Financial Performance"
)

print(f"✅ Report created: {doc_info['url']}")
```

## 📚 API Reference

### Authentication Functions (google_auth_helper)

- `get_service_account_credentials(scopes)` - Get service account credentials
- `build_docs_service()` - Build Google Docs API service
- `build_drive_service()` - Build Google Drive API service  
- `build_gmail_service()` - Build Gmail API service
- `build_forms_service()` - Build Google Forms API service
- `build_calendar_service()` - Build Google Calendar API service
- `build_analytics_service()` - Build Google Analytics API service

### Document Operations (google_docs)

**Core Functions:**
- `google_docs_create_document(title, with_sample_content=False)`
- `google_docs_create_from_markdown(title, markdown_content)` 
- `google_docs_smart_update(document_id, markdown_content, insertion_position='end')`
- `google_docs_get_document(document_id)`
- `google_docs_batch_update(document_id, requests)`

**Formatting Functions:**
- `google_docs_create_heading(document_id, text, heading_level=1, index=1)`
- `google_docs_create_list(document_id, items, start_index=1, list_type='bullet')`
- `google_docs_insert_text(document_id, text, index=1)`
- `google_docs_insert_image(document_id, image_url, index=1, width=None, height=None)`
- `google_docs_insert_table(document_id, rows, columns, index=1)`
- `google_docs_insert_page_break(document_id, index=1)`
- `google_docs_format_text(document_id, start_index, end_index, bold, italic, ...)`
- `google_docs_add_formatted_content(document_id)`

**Content Operations:**
- `google_docs_append_text(document_id, text)`
- `google_docs_replace_text(document_id, find_text, replace_text, match_case=True)`
- `google_docs_delete_content(document_id, start_index, end_index)`

**Export Functions:**
- `google_docs_export_as_pdf(document_id)`
- `google_docs_export_as_html(document_id)`
- `google_docs_export_as_markdown(document_id)`
- `google_docs_create_from_template(template_id, title)`
- `google_docs_get_suggestions(document_id)`
- `google_docs_create_named_range(document_id, name, start_index, end_index)`

### Sheets Operations (google_docs)

- `google_sheets_create(title, data=None, headers=None)`
- `google_sheets_read_data(spreadsheet_id, range_name='Sheet1!A1:Z1000')`
- `google_sheets_append_data(spreadsheet_id, data, sheet_name='Sheet1')`

### Charts Operations (google_docs)

- `google_charts_create(title, chart_type, data, headers=None, chart_options=None)`
- `google_docs_insert_chart(document_id, chart_data, chart_type='column', ...)`
- `google_docs_create_professional_report_with_charts(title, summary_text, chart_data, ...)`

### Drive Operations (google_drive)

**File Management:**
- `google_drive_list_files(query=None, max_results=100)`
- `google_drive_get_file(file_id)`
- `google_drive_upload_file(file_path, file_name=None, parent_folder_id=None)`
- `google_drive_update_file(file_id, file_path)`
- `google_drive_delete_file(file_id)`
- `google_drive_copy_file(file_id, new_name)`
- `google_drive_move_file(file_id, new_parent_folder_id)`

**Folder Management:**
- `google_drive_create_folder(folder_name, parent_folder_id=None)`
- `google_drive_search_files(query, max_results=100)`

**Permissions:**
- `google_drive_share_file(file_id, email, role='reader')`
- `google_drive_list_permissions(file_id)`
- `google_drive_remove_permission(file_id, permission_id)`

**Utilities:**
- `google_drive_export_file(file_id, mime_type)`
- `google_drive_get_storage_quota()`
- `google_drive_restore_file(file_id)`

### Gmail Operations (gmail)

**Email Sending:**
- `gmail_send_email(to, subject, body, attachments=None, cc=None, bcc=None)`
- `gmail_send_email_smtp(to, subject, body, attachments=None)` - SMTP alternative
- `gmail_send_email_smtp_html(to, subject, html_body, attachments=None)` - HTML email

**Draft Management:**
- `gmail_create_draft(to, subject, body, attachments=None)`
- `gmail_send_draft(draft_id)`

**Message Operations:**
- `gmail_list_messages(query=None, max_results=100, label_ids=None)`
- `gmail_get_message(message_id)`
- `gmail_search_messages(query, max_results=100)`
- `gmail_get_attachment(message_id, attachment_id)`
- `gmail_delete_message(message_id)`
- `gmail_modify_message(message_id, add_label_ids=None, remove_label_ids=None)`
- `gmail_mark_as_read(message_id)`
- `gmail_mark_as_unread(message_id)`
- `gmail_archive_message(message_id)`
- `gmail_unarchive_message(message_id)`

**Label Management:**
- `gmail_list_labels()`
- `gmail_create_label(name, label_list_visibility='labelShow')`
- `gmail_update_label(label_id, name=None, message_list_visibility=None)`
- `gmail_delete_label(label_id)`

**Filter Management:**
- `gmail_create_filter(criteria, actions)`
- `gmail_list_filters()`
- `gmail_delete_filter(filter_id)`

**Account:**
- `gmail_get_profile()`
- `gmail_list_available_accounts()` - List configured SMTP accounts

### GSheets Operations (gsheets)

*Alternative gspread-based implementation*

- `gsheets_read(spreadsheet_id, range_name='Sheet1')`
- `gsheets_write(spreadsheet_id, range_name, values)`
- `gsheets_append(spreadsheet_id, range_name, values)`
- `gsheets_create(title, data=None, headers=None)`

### Forms Operations (google_forms)

- `google_forms_create_form(title, description=None)`
- `google_forms_get_form(form_id)`
- `google_forms_add_question(form_id, question_text, question_type='short_answer')`
- `google_forms_get_responses(form_id)`

### Calendar Operations (google_calendar)

- `google_calendar_list_events(calendar_id='primary', max_results=10)`
- `google_calendar_create_event(summary, start_time, end_time, description=None)`
- `google_calendar_update_event(event_id, summary=None, start_time=None, end_time=None)`
- `google_calendar_delete_event(event_id)`
- `google_calendar_list_calendars()`

### Analytics Operations (google_analytics)

**Account Management:**
- `google_analytics_list_accounts()`
- `google_analytics_list_properties(account_id=None)`

**Reporting:**
- `google_analytics_run_report(property_id, start_date, end_date, metrics, dimensions=None)`
- `google_analytics_get_realtime_report(property_id, metrics=None, dimensions=None)`
- `google_analytics_get_page_views(property_id, start_date='7daysAgo', end_date='today')`
- `google_analytics_get_user_behavior(property_id, start_date='7daysAgo', end_date='today')`
- `google_analytics_get_conversions(property_id, start_date='7daysAgo', end_date='today')`
- `google_analytics_get_traffic_sources(property_id, start_date='7daysAgo', end_date='today')`
- `google_analytics_get_demographics(property_id, start_date='7daysAgo', end_date='today')`
- `google_analytics_get_device_data(property_id, start_date='7daysAgo', end_date='today')`
- `google_analytics_get_top_pages(property_id, start_date='7daysAgo', end_date='today', limit=20)`
- `google_analytics_get_events(property_id, start_date='7daysAgo', end_date='today')`

### Cloud Run Operations (google_cloud_run)

- `google_cloud_run_list_services(project_id, region='us-central1')`
- `google_cloud_run_deploy_service(service_name, image, project_id, region='us-central1')`
- `google_cloud_run_delete_service(service_name, project_id, region='us-central1')`
- `google_cloud_run_get_service(service_name, project_id, region='us-central1')`

## 🔄 Migration Guide

### Updating Existing Code

If you have existing code using the old import paths:

**Before:**
```python
from tools.implementations.google_docs import google_docs_create_from_markdown
from tools.implementations.google_drive import google_drive_create_folder
```

**After (recommended):**
```python
from google_workspace import google_docs_create_from_markdown, google_drive_create_folder
```

**Note:** Old import paths still work via redirect files for backward compatibility, but updating to the new package structure is recommended.

## 🛠️ Troubleshooting

### Issue: "Cannot import name X"

**Solution:** Make sure you're using the correct function name. Check the API Reference section above.

### Issue: "Service account credentials not found"

**Solution:** Set the environment variable:
```bash
export GOOGLE_SERVICE_ACCOUNT_JSON=/path/to/service-account.json
```

### Issue: "Insufficient permissions"

**Solution:** Ensure your service account has the necessary scopes and permissions:
- Docs: `https://www.googleapis.com/auth/documents`
- Drive: `https://www.googleapis.com/auth/drive`
- Gmail: `https://www.googleapis.com/auth/gmail.send`
- Calendar: `https://www.googleapis.com/auth/calendar`

## 📊 Package Statistics

- **Total Functions:** 100+ across 9 modules
- **Total Lines:** ~10,000+ lines of code
- **Modules:** 9 Google service integrations
- **API Coverage:** 
  - 📄 Docs: 25+ functions
  - 📁 Drive: 15 functions
  - 📧 Gmail: 24 functions
  - 📊 Sheets: 3 functions (google_docs) + 4 functions (gsheets)
  - 📈 Analytics: 12 functions
  - 📅 Calendar: 5 functions
  - 📋 Forms: 4 functions
  - ☁️ Cloud Run: 4 functions

## 🔧 Development Notes

### File Organization

All Google Workspace code has been consolidated into the `google_workspace/` package:

- ✅ **Moved from:** `tools/implementations/google_*.py`
- ✅ **Now in:** `google_workspace/google_*.py`
- ✅ **Backward compatibility:** Redirect files maintain old import paths

### Internal Implementation Details

- **Authentication:** Unified via `google_auth_helper.py` using service accounts
- **Error Handling:** Each function includes try-except blocks with descriptive errors
- **Type Hints:** Functions use type hints where possible
- **Docstrings:** All public functions have comprehensive docstrings
- **Logging:** Uses Python logging for debugging

## 📝 Version History

### Version 1.0.0 (Current)
- ✅ Consolidated all Google Workspace code into unified package
- ✅ Fixed function name mismatches in __init__.py
- ✅ Created backward compatibility layer with redirect files
- ✅ Updated standalone scripts to use new package structure
- ✅ Comprehensive testing of all import paths
- ✅ Full API documentation

## 🤝 Contributing

When adding new Google Workspace functions:

1. Add function to appropriate module (e.g., `google_docs.py`)
2. Import function in `__init__.py`
3. Add function name to `__all__` list in `__init__.py`
4. Update this README with API documentation
5. Test both direct and package imports

## 📄 License

Part of the Valor AI Agent Platform

---

**Last Updated:** October 24, 2025  
**Status:** ✅ Production Ready  
**Total Functions:** 100+  
**Package Version:** 1.0.0
