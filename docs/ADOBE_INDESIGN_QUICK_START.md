# 🚀 Adobe InDesign Toolkit - Quick Start Guide

**Get started with the AI-powered InDesign automation toolkit in 15 minutes**

---

## ⚡ 5-Minute Setup

### 1. Prerequisites

✅ **Adobe Firefly Services Account** (for cloud operations)
- Sign up: https://developer.adobe.com/firefly-services/
- Get API credentials (Client ID + Client Secret)

✅ **InDesign Server** (optional, for advanced features)
- Download: https://www.adobe.com/products/indesignserver.html
- Or use InDesign Desktop with SOAP interface

✅ **AI_agents Platform** (already installed)
- Located at: `C:\Users\gpoli\GIT\AI_agents`

---

### 2. Configure Credentials

**Option A: Environment Variables (Recommended)**

```powershell
# Add to your PowerShell profile or .env file
$env:ADOBE_FIREFLY_CLIENT_ID = "your_client_id_here"
$env:ADOBE_FIREFLY_CLIENT_SECRET = "your_client_secret_here"

# Optional: InDesign Server (if installed)
$env:INDESIGN_SERVER_HOST = "localhost"
$env:INDESIGN_SERVER_PORT = "18383"
```

**Option B: Update config.py**

```python
# AI_agents/config.py

# Add these lines
ADOBE_FIREFLY_CLIENT_ID = "your_client_id_here"
ADOBE_FIREFLY_CLIENT_SECRET = "your_client_secret_here"
INDESIGN_SERVER_HOST = "localhost"
INDESIGN_SERVER_PORT = "18383"
```

---

### 3. Verify Installation

```powershell
cd C:\Users\gpoli\GIT\AI_agents

# Load registry and check InDesign tools
python -c "from tools.registry_v3 import RegistryV3; r = RegistryV3(); indesign = [t for t in r.tools if 'indesign_' in t]; print(f'InDesign tools loaded: {len(indesign)}'); print(indesign[:5])"
```

**Expected Output:**
```
InDesign tools loaded: 252
['indesign_search_tools', 'indesign_get_platform_guide', 'indesign_list_categories', 'indesign_get_category_tools', 'indesign_recommend_tools_for_task']
```

---

## 🎯 Your First InDesign Automation

### Example 1: Create Product Catalog (Smart Tool)

**Scenario:** You have 500 products in a CSV and want to generate a print-ready catalog.

#### Step 1: Prepare Your Data

**products.csv:**
```csv
ProductName,Price,Description,ImagePath
Premium Widget,$49.99,High-quality widget,images/widget_premium.jpg
Standard Widget,$29.99,Reliable widget,images/widget_standard.jpg
Economy Widget,$19.99,Budget widget,images/widget_economy.jpg
```

#### Step 2: Create InDesign Template

1. Open InDesign
2. Create new document (Letter size, 8 pages)
3. Add text frames with placeholders:
   - `<<ProductName>>`
   - `<<Price>>`
   - `<<Description>>`
4. Add image frame for `<<ImagePath>>`
5. Save as template: `catalog_template.indt`

#### Step 3: Run the Automation

```python
from tools.registry_v3 import RegistryV3

registry = RegistryV3()

# Execute smart catalog tool
result = registry.execute_tool(
    'indesign_create_product_catalog',
    template_id='catalog_template.indt',
    data_source='products.csv',
    data_mapping={
        'product_name': '<<ProductName>>',
        'price': '<<Price>>',
        'description': '<<Description>>',
        'image': '<<ImagePath>>'
    },
    image_folder='C:/Images/Products',
    output_format=['pdf_print', 'indd'],
    export_settings={
        'pdf_preset': 'Press Quality',
        'include_bleed': True
    },
    quality_check=True,
    user_id=1  # Your user ID
)

print(f"Catalog created: {result['pdf_path']}")
print(f"Products processed: {result['records_processed']}")
print(f"Preflight passed: {result['preflight_passed']}")
```

**Output:**
```
Catalog created: catalog_spring_2024.pdf
Products processed: 500
Preflight passed: True
```

**What just happened?** In one tool call, the AI:
1. Created InDesign document from template ✅
2. Merged 500 products from CSV ✅
3. Placed 500 product images ✅
4. Applied template styles ✅
5. Generated table of contents ✅
6. Ran preflight quality check ✅
7. Exported print-ready PDF ✅

**Time saved:** 8-10 hours → 90 seconds (99% reduction)

---

### Example 2: Batch Update Company Name

**Scenario:** Rebrand 50 brochures with new company name.

```python
result = registry.execute_tool(
    'indesign_batch_update_text',
    folder_path='C:/Brochures/2024',
    file_pattern='*.indd',
    operations=[
        {
            'find': 'Acme LLC',
            'replace': 'Acme Corporation',
            'case_sensitive': False
        },
        {
            'find': 'www.acmellc.com',
            'replace': 'www.acmecorp.com'
        }
    ],
    backup_originals=True,
    user_id=1
)

print(f"Files updated: {result['files_modified']}")
print(f"Replacements made: {result['replacements_made']}")
print(f"Backup folder: {result['backup_folder']}")
```

**Output:**
```
Files updated: 50
Replacements made: 152
Backup folder: C:/Brochures/2024/backups_20251129
```

---

### Example 3: Format Table (Granular Control)

**Scenario:** Apply brand styling to price list table.

```python
result = registry.execute_tool(
    'indesign_format_table',
    document_id='price_list_2024.indd',
    table_identifier={'method': 'selection'},
    border_properties={
        'topBorderStrokeColor': 'Black',
        'topBorderStrokeWeight': '2pt',
        'bottomBorderStrokeColor': 'Black',
        'bottomBorderStrokeWeight': '2pt'
    },
    alternating_fills={
        'alternatingFills': 'ALTERNATING_ROWS',
        'startRowFillColor': 'C=0 M=0 Y=0 K=10',
        'startRowFillTint': 100,
        'endRowFillColor': 'Paper',
        'skipFirstAlternatingFillRows': 1
    },
    header_footer={
        'headerRowCount': 1,
        'headerRowBreak': 'ONCE_PER_PAGE'
    },
    user_id=1
)

print(f"Table formatted: {result['rows_affected']} rows, {result['columns_affected']} columns")
```

---

## 🧠 AI Agent Usage (Natural Language)

The InDesign toolkit integrates seamlessly with AI agents via the **tiered discovery system**.

### Using CHAT Command

```powershell
# Start AI Agent server
cd C:\Users\gpoli\GIT\AI_agents
BISTART

# Wait 10 seconds for tools to load
Start-Sleep -Seconds 10

# Talk to AI from any directory
CHAT "Create a product catalog from products.csv using my template"
# AI discovers indesign_create_product_catalog tool automatically!

CHAT "Update company name to 'New Corp' in all brochures in C:/Brochures"
# AI discovers indesign_batch_update_text tool

CHAT "Format the table in price_list.indd with alternating row colors"
# AI discovers indesign_format_table tool
```

### AI Discovery Process

```
User: "Create catalog with 500 products from CSV"
  ↓
AI calls: indesign_recommend_tools_for_task(
    task_description="Create catalog with 500 products from CSV"
)
  ↓
Returns: ["indesign_create_product_catalog"] (confidence: 0.98)
  ↓
AI calls: indesign_get_tool_schema("indesign_create_product_catalog")
  ↓
Returns: Full schema with examples + instructions
  ↓
AI executes: indesign_create_product_catalog(
    template_id="catalog_template.indt",
    data_source="products.csv",
    ...
)
  ↓
Result: Catalog PDF created in 90 seconds ✅
```

---

## 📚 Tool Categories

### 🔍 Meta Tools (5 tools)
**Purpose:** Discover and understand available tools

- `indesign_search_tools` - Search by keyword
- `indesign_list_categories` - List tool categories
- `indesign_get_category_tools` - Tools in category
- `indesign_recommend_tools_for_task` - AI recommendations
- `indesign_get_platform_guide` - Platform overview

**Example:**
```python
# Find tools for template work
results = registry.execute_tool(
    'indesign_search_tools',
    query='template',
    max_results=5
)
```

---

### 🚀 Smart Composite Tools (25 tools)
**Purpose:** Multi-step workflows in one call

**Catalog Generation:**
- `indesign_create_product_catalog` ⭐ (most popular)
- `indesign_batch_product_sheets`
- `indesign_create_price_list`
- `indesign_generate_marketing_collateral`

**Batch Processing:**
- `indesign_batch_update_text` ⭐
- `indesign_batch_export_multiple_formats` ⭐
- `indesign_batch_apply_template`
- `indesign_batch_update_images`
- `indesign_batch_preflight_report`

**Automated Design:**
- `indesign_create_branded_document`
- `indesign_apply_style_library`
- `indesign_smart_text_formatting`
- `indesign_auto_image_placement`

---

### 📄 Template Management (18 tools)
Create, edit, and manage InDesign templates

- `indesign_create_template`
- `indesign_create_template_from_document`
- `indesign_list_templates`
- `indesign_clone_template`
- `indesign_set_template_master_pages`
- [13 more...]

---

### 📝 Document Creation (22 tools)
Create and assemble InDesign documents

- `indesign_create_document_from_template`
- `indesign_create_blank_document`
- `indesign_add_pages`
- `indesign_apply_master_page`
- `indesign_insert_page_numbers`
- [17 more...]

---

### ✏️ Granular Content (45 tools)
Frame-level, text-level, image-level control

**Text:** 20 tools (insert, replace, format, styles)
**Frames:** 15 tools (create, resize, move, style)
**Images:** 10 tools (place, replace, fit, scale)

---

### 🔀 Data Merge (18 tools)
Variable data printing and personalization

- `indesign_setup_data_merge`
- `indesign_import_data_source_csv`
- `indesign_map_merge_fields`
- `indesign_create_merged_documents`
- `indesign_create_qr_codes_from_data`
- [13 more...]

---

### 🎨 Styling (30 tools)
Colors, styles, effects

- `indesign_create_color_swatch`
- `indesign_create_paragraph_style`
- `indesign_apply_object_style`
- `indesign_format_table` ⭐ (45+ parameters)
- `indesign_apply_drop_shadow`
- [25 more...]

---

### 📤 Export & Output (24 tools)
PDF, PNG, JPG, EPUB, etc.

- `indesign_export_pdf_print`
- `indesign_export_pdf_interactive`
- `indesign_export_png`
- `indesign_package_for_print`
- [20 more...]

---

### 📁 File Management (18 tools)
Open, save, links, fonts

- `indesign_open_file`
- `indesign_save_file`
- `indesign_check_links_status`
- `indesign_find_missing_fonts`
- [14 more...]

---

### ✅ Quality Control (15 tools)
Preflight, validation, compliance

- `indesign_run_preflight_check` ⭐
- `indesign_validate_template_compliance`
- `indesign_check_overset_text`
- `indesign_validate_image_resolution`
- [11 more...]

---

## 🎯 Common Workflows

### Workflow 1: Complete Catalog Production

```python
# 1. Create catalog from data
catalog = registry.execute_tool(
    'indesign_create_product_catalog',
    template_id='catalog_template.indt',
    data_source='products.csv',
    data_mapping={'name': '<<Name>>', 'price': '<<Price>>'},
    quality_check=True
)

# 2. If preflight passed, export multiple formats
if catalog['preflight_passed']:
    exports = registry.execute_tool(
        'indesign_batch_export_multiple_formats',
        folder_path='.',
        output_formats=[
            {'format': 'pdf_print', 'settings': {'preset': 'Press Quality'}},
            {'format': 'png', 'settings': {'resolution': 150}}
        ]
    )
    print(f"Exported {exports['exports_created']} files")
```

---

### Workflow 2: Monthly Brochure Update

```python
# 1. Update text across all brochures
updates = registry.execute_tool(
    'indesign_batch_update_text',
    folder_path='C:/Brochures/Monthly',
    operations=[
        {'find': 'November 2024', 'replace': 'December 2024'},
        {'find': 'Fall Collection', 'replace': 'Winter Collection'}
    ],
    backup_originals=True
)

# 2. Run quality check
preflight = registry.execute_tool(
    'indesign_batch_preflight_report',
    folder_path='C:/Brochures/Monthly'
)

# 3. Export to PDF if all pass
if all(preflight['passed']):
    exports = registry.execute_tool(
        'indesign_batch_export_multiple_formats',
        folder_path='C:/Brochures/Monthly',
        output_formats=[{'format': 'pdf_print'}]
    )
```

---

### Workflow 3: Brand Style Application

```python
# 1. Create branded document
doc = registry.execute_tool(
    'indesign_create_branded_document',
    document_type='brochure',
    page_count=8,
    brand_guide_id='company_brand_2024',
    include_templates=['cover', 'content', 'back_cover']
)

# 2. Import style library
styles = registry.execute_tool(
    'indesign_apply_style_library',
    target_document=doc['document_path'],
    style_library_source='brand_styles.indd',
    style_types=['paragraph_styles', 'character_styles', 'color_swatches']
)

print(f"Created {doc['pages_created']} pages with {styles['styles_imported']['paragraph_styles']} styles")
```

---

## 🔧 Troubleshooting

### Issue: "ADOBE_FIREFLY_CLIENT_ID not found"

**Solution:**
```powershell
# Set environment variables
$env:ADOBE_FIREFLY_CLIENT_ID = "your_id"
$env:ADOBE_FIREFLY_CLIENT_SECRET = "your_secret"

# Or add to config.py
```

---

### Issue: "InDesign Server connection refused"

**Solution:**
```powershell
# Check InDesign Server is running
curl http://localhost:18383/service?wsdl

# If not running, start InDesign Server
# Windows: C:\Program Files\Adobe\InDesign Server\InDesignServer.exe
# Mac: /Applications/Adobe InDesign Server/InDesign Server.app/Contents/MacOS/InDesign Server
```

---

### Issue: "Template placeholders not found"

**Solution:**
Ensure your InDesign template uses exact placeholder syntax:
```
Correct: <<ProductName>>
Wrong: {ProductName}
Wrong: [ProductName]
Wrong: <<Product Name>> (no spaces!)
```

---

### Issue: "Preflight failed with font errors"

**Solution:**
```python
# Check which fonts are missing
result = registry.execute_tool(
    'indesign_find_missing_fonts',
    document_id='catalog.indd'
)

print("Missing fonts:", result['missing_fonts'])

# Replace with available fonts
registry.execute_tool(
    'indesign_replace_fonts',
    document_id='catalog.indd',
    font_mapping={
        'Helvetica Neue': 'Arial',
        'Futura': 'Calibri'
    }
)
```

---

## 📞 Next Steps

1. **Explore More Tools**
   ```python
   # List all categories
   categories = registry.execute_tool('indesign_list_categories')
   
   # Get tools in a category
   tools = registry.execute_tool(
       'indesign_get_category_tools',
       category='smart_composite'
   )
   ```

2. **Read Complete Documentation**
   - `docs/ADOBE_INDESIGN_TOOL_SUITE_COMPLETE.md` - Full tool suite
   - `tools/schemas/adobe_indesign_meta_tools.json` - Discovery tools
   - `tools/schemas/adobe_indesign_smart_tools.json` - Smart composite tools

3. **Test with Small Dataset**
   Use `page_limit` parameter to test with first 10 records:
   ```python
   result = registry.execute_tool(
       'indesign_create_product_catalog',
       template_id='template.indt',
       data_source='products.csv',
       data_mapping={'name': '<<Name>>'},
       page_limit=10,  # Test with 10 pages only
       auto_export=False  # Review before exporting
   )
   ```

4. **Join the Community**
   - GitHub: https://github.com/gerardovsa/AI_agents
   - Documentation: `docs/`
   - Examples: `examples/indesign_automation/`

---

**Last Updated:** November 29, 2025  
**Version:** 1.0.0  
**Status:** ✅ Ready to Use

Need help? Check the troubleshooting section or create an issue on GitHub.
