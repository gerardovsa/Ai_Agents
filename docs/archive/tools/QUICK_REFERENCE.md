# 🚀 AI Agents Tool System - Quick Reference

## **Installation**
```bash
cd AI_agents/tools
pip install -r requirements.txt
```

## **Basic Usage**
```python
from tools import ToolRegistry
registry = ToolRegistry()

result = registry.execute_tool("tool_name", param1="value", param2="value")
```

## **34 Tools - Quick Reference**

### **Supabase** 🗄️ (Database)
```python
registry.execute_tool("supabase_query", table="users", filters={"status": "active"})
registry.execute_tool("supabase_insert", table="users", data={"name": "John"})
registry.execute_tool("supabase_update", table="users", data={"status": "inactive"}, filters={"id": 123})
registry.execute_tool("supabase_delete", table="users", filters={"id": 123})
registry.execute_tool("supabase_auth_user", email="user@example.com", password="pass123")
registry.execute_tool("supabase_storage_upload", bucket="avatars", file_path="user.jpg", file_content="/path/to/file")
```

### **CloudConvert** 🔄 (File Conversion)
```python
registry.execute_tool("cloudconvert_convert", input_file="doc.docx", input_format="docx", output_format="pdf")
registry.execute_tool("cloudconvert_optimize", input_file="image.jpg", file_type="image", quality=85)
registry.execute_tool("cloudconvert_merge", input_files=["doc1.pdf", "doc2.pdf"], output_format="pdf")
registry.execute_tool("cloudconvert_status", job_id="abc-123")
```

### **AssemblyAI** 🎤 (Speech-to-Text)
```python
registry.execute_tool("assemblyai_transcribe", audio_file="meeting.mp3", speaker_labels=True)
registry.execute_tool("assemblyai_analyze", audio_file="call.wav", sentiment_analysis=True)
registry.execute_tool("assemblyai_speakers", audio_file="interview.mp3", speakers_expected=2)
registry.execute_tool("assemblyai_status", transcript_id="abc-123")
```

### **Ngrok** 🌐 (Tunneling)
```python
registry.execute_tool("ngrok_start_tunnel", port=3000, protocol="http")
registry.execute_tool("ngrok_list_tunnels")
registry.execute_tool("ngrok_stop_tunnel", tunnel_name="http-3000")
registry.execute_tool("ngrok_get_public_url", port=8080)
```

### **Cloudflare** ☁️ (Workers)
```python
registry.execute_tool("cloudflare_deploy_worker", worker_name="api", script_path="worker.js")
registry.execute_tool("cloudflare_list_workers")
registry.execute_tool("cloudflare_get_worker_logs", worker_name="api", limit=100)
registry.execute_tool("cloudflare_worker_status", worker_name="api")
```

### **WooCommerce** 🛒 (E-Commerce)
```python
registry.execute_tool("woocommerce_get_orders", status="processing", limit=20)
registry.execute_tool("woocommerce_create_product", name="Product", price=29.99, stock_quantity=100)
registry.execute_tool("woocommerce_update_order", order_id=123, status="completed")
registry.execute_tool("woocommerce_get_products", limit=10, search="keyword")
```

### **GitHub** 📦 (Version Control)
```python
registry.execute_tool("github_create_repo", name="my-repo", private=False)
registry.execute_tool("github_commit_file", repo="owner/repo", file_path="README.md", content="# Title", message="Update")
registry.execute_tool("github_create_pr", repo="owner/repo", title="New feature", head="feature", base="main")
registry.execute_tool("github_get_issues", repo="owner/repo", state="open", limit=30)
```

### **Google Sheets** 📊 (Spreadsheets)
```python
registry.execute_tool("gsheets_read", spreadsheet_id="abc123", range="Sheet1!A1:D10")
registry.execute_tool("gsheets_write", spreadsheet_id="abc123", range="Sheet1!A1:B2", values=[["A", "B"]])
registry.execute_tool("gsheets_append", spreadsheet_id="abc123", range="Sheet1!A:D", values=[["Row data"]])
registry.execute_tool("gsheets_create", title="New Spreadsheet", sheets=["Sheet1", "Sheet2"])
```

## **Common Patterns**

### **List Available Tools**
```python
tools = registry.list_tools()  # All tools
tools = registry.list_tools(platform="supabase")  # Platform-specific
platforms = registry.get_all_platforms()  # All platform names
```

### **Get Tool Information**
```python
schema = registry.get_tool_schema("tool_name")
print(schema['description'])
print(schema['parameters'])
```

### **Validate Parameters**
```python
valid, error = registry.validate_parameters("tool_name", {"param": "value"})
if not valid:
    print(f"Invalid: {error}")
```

### **Handle Results**
```python
result = registry.execute_tool("tool_name", param="value")

if result['success']:
    data = result['result']
    print(f"Success: {data}")
else:
    print(f"Error: {result['error']}")
```

## **Testing**
```bash
# Test everything
python test_tools.py

# Test specific platform
python test_tools.py --platform supabase

# Test specific tool
python test_tools.py --tool supabase_query
```

## **Use Case Examples**

### **Support Workflow**
```python
# 1. Find customer
user = registry.execute_tool("supabase_query", table="users", filters={"email": "customer@example.com"})

# 2. Get orders
orders = registry.execute_tool("woocommerce_get_orders", customer_id=user['result']['data'][0]['id'])

# 3. Transcribe call
transcript = registry.execute_tool("assemblyai_transcribe", audio_file="call.mp3")

# 4. Log issue
issue = registry.execute_tool("github_create_issue", repo="company/support", title="Issue", body=transcript['result']['text'])
```

### **Deployment Workflow**
```python
# 1. Commit code
commit = registry.execute_tool("github_commit_file", repo="owner/repo", file_path="worker.js", content=code, message="Deploy")

# 2. Deploy Worker
deploy = registry.execute_tool("cloudflare_deploy_worker", worker_name="api", script_path="worker.js")

# 3. Start test tunnel
tunnel = registry.execute_tool("ngrok_start_tunnel", port=3000)
```

### **Report Generation**
```python
# 1. Query data
users = registry.execute_tool("supabase_query", table="users", filters={"created_at": ">= '2025-10-01'"})
orders = registry.execute_tool("woocommerce_get_orders", limit=1000)

# 2. Create spreadsheet
sheet = registry.execute_tool("gsheets_create", title="Monthly Report")

# 3. Write data
registry.execute_tool("gsheets_write", spreadsheet_id=sheet['result']['id'], range="A1:E100", values=report_data)
```

## **Result Format**
All tools return:
```python
{
    'success': True/False,
    'tool': 'tool_name',
    'result': {...},      # Tool-specific data
    'error': '...'        # Only if failed
}
```

## **Documentation Files**
- `README.md` - Overview and introduction
- `USAGE_GUIDE.md` - Detailed examples
- `SYSTEM_STATUS.md` - Implementation summary
- `IMPLEMENTATION_COMPLETE.md` - Technical details
- `QUICK_REFERENCE.md` - This file

## **System Stats**
- **Platforms**: 8
- **Tools**: 34
- **Status**: ✅ Operational
- **Tests**: ✅ Passing

---

**Quick Start**: `from tools import ToolRegistry; registry = ToolRegistry()`

**Test**: `python test_tools.py`

**Status**: ✅ **Ready for Production**
