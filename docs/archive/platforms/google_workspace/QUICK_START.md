# ⚡ Google Workspace Quick Start

**Need something fast?** This is your cheat sheet.

---

## 📦 Installation

```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib gspread
```

## 🔑 Setup (One-time)

```bash
# Set environment variable
set GOOGLE_SERVICE_ACCOUNT_JSON=C:\path\to\service-account.json
```

## 🚀 Common Tasks

### Create a Document from Markdown

```python
from google_workspace import google_docs_create_from_markdown

doc = google_docs_create_from_markdown(
    "My Report",
    "# Title\n\nThis is **bold** text."
)
print(doc['url'])
```

### Create a Folder

```python
from google_workspace import google_drive_create_folder

folder = google_drive_create_folder("Reports 2025")
print(folder['id'])
```

### Send an Email

```python
from google_workspace import gmail_send_email

gmail_send_email(
    to='user@example.com',
    subject='Test',
    body='Hello!'
)
```

### Read Spreadsheet Data

```python
from google_workspace import gsheets_read

data = gsheets_read('spreadsheet_id', 'Sheet1!A1:D10')
for row in data:
    print(row)
```

### Create Professional Report with Charts

```python
from google_workspace import google_docs_create_professional_report_with_charts

doc = google_docs_create_professional_report_with_charts(
    title='Q4 Report',
    summary_text='Strong growth in Q4',
    chart_data={'Revenue': [100, 120, 150, 180]},
    headers=['Oct', 'Nov', 'Dec', 'Jan'],
    chart_title='Q4 Performance'
)
```

---

## 📚 Need More?

- **Complete Guide:** `google_workspace/COMPLETE_GUIDE.md` (850+ lines, everything you need)
- **API Reference:** Same file, search for function name
- **Troubleshooting:** Same file, check troubleshooting section

---

## 🆘 Quick Troubleshooting

**"Credentials not found"**
```bash
set GOOGLE_SERVICE_ACCOUNT_JSON=C:\full\path\to\file.json
```

**"Cannot import name X"**
```python
# Use these exact names
from google_workspace import (
    google_docs_create_from_markdown,  # NOT create_document_from_markdown
    google_sheets_read_data,           # NOT google_sheets_read
    gmail_send_email                   # NOT send_gmail
)
```

**Gmail not sending?** Use SMTP instead:
```python
from google_workspace import gmail_send_email_smtp

gmail_send_email_smtp('to@example.com', 'Subject', 'Body')
```

---

**That's it! Start coding.** 🚀

For advanced features, see `COMPLETE_GUIDE.md`
