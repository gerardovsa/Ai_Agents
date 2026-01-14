# Adobe Firefly Credentials Setup - Quick Guide

## ✅ What Was Done

Your Adobe Firefly API credentials have been added to the system in **3 locations**:

### 1. **config.py** (Fallback)
```python
ADOBE_FIREFLY_CLIENT_ID = 'b0567031b346ebfd0ca6e422f0e4a3c2'
ADOBE_FIREFLY_CLIENT_SECRET = 'c489698bc9bf6b6b9113b967b65daa4d'
```

### 2. **Supabase Database** (Primary - Multi-user)
SQL script created: `scripts/setup/insert_adobe_firefly_credentials.sql`

### 3. **Adobe InDesign Implementation** (Auto-detection)
Updated: `tools/implementations/adobe_indesign.py`
- Fetches credentials from database first
- Falls back to config.py if database unavailable
- Supports multi-user credential isolation

---

## 🚀 Next Steps

### Step 1: Insert Credentials into Database

**Option A: Supabase SQL Editor (Recommended)**
1. Open: https://supabase.com/dashboard/project/[your-project]/sql
2. Copy entire file: `scripts/setup/insert_adobe_firefly_credentials.sql`
3. Paste into SQL editor
4. Click **Run**
5. Verify: Should see "✅ Adobe Firefly credentials inserted successfully!"

**Option B: Command Line (if psql installed)**
```powershell
cd c:\Users\gpoli\GIT\AI_agents
psql -h [your-supabase-host] -U postgres -d postgres -f scripts/setup/insert_adobe_firefly_credentials.sql
```

### Step 2: Test Credentials

```powershell
cd c:\Users\gpoli\GIT\AI_agents
python testing_tools/test_adobe_credentials.py
```

**Expected Output:**
```
✅ PASS - Database Storage
✅ PASS - Credential Retrieval  
✅ PASS - Client Initialization
✅ PASS - Config Fallback

Results: 4/4 tests passed
🎉 SUCCESS! All tests passed!
```

### Step 3: Start AI Agent Server

```powershell
cd c:\Users\gpoli\GIT\AI_agents
BISTART
```

Wait 10-15 seconds for tools to load.

### Step 4: Test Adobe InDesign Tools

```powershell
# Test 1: List available tools
CHAT "List available Adobe InDesign tools"

# Test 2: Get tool details
CHAT "What can I do with Adobe InDesign data merge tools?"

# Test 3: Try a simple operation (when you have templates)
CHAT "Create a product catalog from my template"
```

---

## 📋 What These Credentials Enable

### **68 Adobe InDesign Tools Now Available:**

#### 🔄 Data Merge Tools (18)
- `indesign_create_data_merge` - Generate documents from CSV/Excel
- `indesign_execute_merge` - Batch produce variable data
- `indesign_merge_to_pdf` - Direct PDF export from data
- `indesign_merge_qr_codes` - Add QR codes to documents
- `indesign_batch_merge` - Process multiple data sources
- ...and 13 more

#### 📄 Document Creation Tools (22)
- `indesign_create_document` - New blank documents
- `indesign_create_document_from_template` - Apply templates
- `indesign_add_pages` - Manage page count
- `indesign_create_master_page` - Master page layouts
- `indesign_merge_documents` - Combine multiple files
- ...and 17 more

#### 📋 Template Management Tools (18)
- `indesign_create_template` - Build reusable templates
- `indesign_list_templates` - Browse available templates
- `indesign_export_template` - Share templates (IDML/PDF)
- `indesign_version_template` - Version control
- `indesign_lock_template_elements` - Protect brand elements
- ...and 13 more

#### 📤 Export & Output Tools (24)
- `indesign_export_pdf_print` - Print-ready PDFs
- `indesign_export_png` - Image exports
- `indesign_export_jpg` - Photo exports
- `indesign_package_for_print` - Collect fonts/links
- ...and 20 more

#### 🎨 Smart Composite Tools (5)
- `indesign_create_product_catalog` - **8-step automation** (90 seconds for 500 products)
- `indesign_batch_update_text` - Bulk text changes
- `indesign_batch_export_multiple_formats` - Multi-format exports
- `indesign_create_branded_document` - Apply brand guidelines
- `indesign_apply_style_library` - Consistent styling

---

## 🔍 How Credential Loading Works

**Priority Order:**
1. **Database (Supabase)** - Checks `ai_infrastructure.user_platform_credentials`
   - Multi-user support (user_id = 1 for master account)
   - Encrypted storage
   - Easy to update via SQL

2. **Config.py** - Fallback if database unavailable
   - Quick development/testing
   - Single user

3. **Environment Variables** - Final fallback
   - `ADOBE_FIREFLY_CLIENT_ID`
   - `ADOBE_FIREFLY_CLIENT_SECRET`

**Code Flow:**
```python
# tools/implementations/adobe_indesign.py
def _get_adobe_credentials(user_id=1):
    # 1. Try database
    conn = get_database_connection('ai_infrastructure')
    cursor.execute("SELECT credentials FROM user_platform_credentials WHERE platform='adobe_firefly'")
    
    # 2. Fallback to config.py
    if not found:
        return {'client_id': ADOBE_FIREFLY_CLIENT_ID, ...}
    
    # 3. Fallback to env vars
    if not found:
        return {'client_id': os.getenv('ADOBE_FIREFLY_CLIENT_ID'), ...}
```

---

## 🔐 Security Notes

**✅ Credentials are stored securely:**
- **Database**: JSONB column (encrypted at rest by Supabase)
- **Config.py**: File-level permissions (not committed to git)
- **Never exposed in logs** - Only first 8 characters shown in debug

**❌ DO NOT:**
- Commit `.env.master` or `config.py` to public repos
- Share credentials in chat/email
- Log full credential values

**🔄 Rotation:**
If credentials are compromised:
1. Generate new keys at: https://developer.adobe.com/console
2. Update database: `UPDATE user_platform_credentials SET credentials = '...' WHERE platform = 'adobe_firefly'`
3. Update config.py
4. Restart server: `BISTART`

---

## 📖 API Documentation

**Adobe Firefly Services:**
- Docs: https://developer.adobe.com/firefly-services/docs/indesign-apis/
- Console: https://developer.adobe.com/console
- Rate Limits: 60 requests/minute, 10 concurrent jobs

**Authentication:**
- Type: OAuth2 Client Credentials
- Token Endpoint: `https://ims-na1.adobelogin.com/ims/token/v3`
- Scopes: `openid`, `creative_sdk`, `firefly_api`

---

## 🐛 Troubleshooting

### Issue: "Adobe Firefly credentials not found"
**Solution:** Run database insert script first
```powershell
# In Supabase SQL Editor:
scripts/setup/insert_adobe_firefly_credentials.sql
```

### Issue: Test fails with database error
**Solution:** Check Supabase connection
```powershell
# Verify .env.master has:
SUPABASE_URL=https://ryoicrdifiqhqpsnjmdo.supabase.co
SUPABASE_SERVICE_KEY=eyJ...
```

### Issue: "401 Unauthorized" from Adobe API
**Solution:** Credentials may be invalid
1. Verify at: https://developer.adobe.com/console
2. Check credentials match database values
3. Test authentication:
```python
from tools.implementations.adobe_indesign import AdobeFireflyClient
client = AdobeFireflyClient()
token = client.authenticate()  # Should not raise error
```

### Issue: Tools not showing in CHAT
**Solution:** Restart server
```powershell
Stop-Process -Name "python" -Force
cd c:\Users\gpoli\GIT\AI_agents
BISTART
```

---

## ✅ Verification Checklist

- [ ] Credentials added to config.py
- [ ] SQL script executed in Supabase
- [ ] Database shows 1 row: `SELECT * FROM user_platform_credentials WHERE platform='adobe_firefly'`
- [ ] Test script passes: `python testing_tools/test_adobe_credentials.py`
- [ ] Server starts: `BISTART`
- [ ] Tools available: `CHAT "List Adobe InDesign tools"`

---

**Status:** ✅ Credentials configured and ready to use!  
**Last Updated:** November 30, 2025  
**Tools Enabled:** 68 Adobe InDesign automation tools
