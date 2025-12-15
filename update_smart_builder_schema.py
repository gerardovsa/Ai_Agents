"""Update microsoft_excel_smart_sheet_builder schema to reflect comprehensive capabilities"""
import json

# Load schema
with open('tools/schemas/microsoft_excel_tools.json', 'r', encoding='utf-8') as f:
    schema = json.load(f)

# Find the smart_sheet_builder tool
for i, tool in enumerate(schema['tools']):
    if tool['name'] == 'microsoft_excel_smart_sheet_builder':
        # Update with comprehensive description
        schema['tools'][i] = {
            "name": "microsoft_excel_smart_sheet_builder",
            "short_description": "⭐ SMART: THE comprehensive Excel builder - create/update workbooks, sheets, formulas, charts - ONE TOOL DOES IT ALL",
            "description": """🚨 CRITICAL EXECUTION RULES:
(1) Execute THIS tool NOW - NEVER use cached/remembered data
(2) MUST return format: 'Created/Updated workbook with [X] sheets, [Y] formulas, [Z] charts'
(3) Use EXACT values from tool response

⚠️ MUST USE: execute_tool(tool_name='microsoft_excel_smart_sheet_builder', ...) - DO NOT call directly!

⭐ COMPREHENSIVE EXCEL BUILDER - ONE TOOL TO DO IT ALL

🎯 MODES:
1. **CREATE FROM SCRATCH**: Provide workbook_name + worksheets
2. **UPDATE EXISTING**: Provide workbook_id + changes
3. **LEGACY SIMPLE**: Provide workbook_name + sheet_description (backward compatible)

✨ CAPABILITIES:
- **Multiple Worksheets**: Create entire workbooks with many sheets
- **Natural Language Formulas**: "sum column A", "multiply B by C", or direct Excel formulas
- **Cross-Sheet References**: "=SUM('Sales Data'!C:C)"
- **Multiple Charts**: Different chart types on different sheets
- **Granular Updates**: Add formulas/charts to existing workbooks
- **Smart Auto-Detection**: Columns, data types, formulas from descriptions

📊 COMPREHENSIVE EXAMPLES:

**Example 1: Full Workbook from Scratch**
```python
{
    "workbook_name": "Q1 Sales Report",
    "worksheets": [
        {
            "name": "Sales Data",
            "columns": ["Rep", "Month", "Amount", "Region"],
            "data": [["Alice", "Jan", 1000, "West"], ["Bob", "Jan", 1200, "East"]],
            "formulas": [
                {"cell": "C10", "formula": "sum column C"}
            ],
            "chart": {
                "type": "column",
                "range": "A1:C10",
                "title": "Sales by Rep"
            }
        },
        {
            "name": "Summary",
            "columns": ["Metric", "Value"],
            "formulas": [
                {"cell": "B1", "formula": "=SUM('Sales Data'!C:C)"},
                {"cell": "B2", "formula": "=AVERAGE('Sales Data'!C:C)"},
                {"cell": "B3", "formula": "=COUNT('Sales Data'!A:A)"}
            ]
        },
        {
            "name": "Charts",
            "chart": {
                "type": "pie",
                "range": "'Sales Data'!D1:D10",
                "title": "Sales by Region"
            }
        }
    ]
}
```

**Example 2: Update Existing Workbook (Granular)**
```python
{
    "workbook_id": "existing_wb_id",
    "formulas": [
        {"sheet": "Data", "cell": "E1", "formula": "multiply column B by column C"},
        {"sheet": "Data", "cell": "F1", "formula": "=B1*1.1"}
    ],
    "charts": [
        {"sheet": "Data", "type": "line", "range": "A1:C20", "title": "Trend"}
    ]
}
```

**Example 3: Simple (Legacy)**
```python
{
    "workbook_name": "Sales Tracker",
    "sheet_description": "sales tracker with rep performance"
}
```

🔧 ADVANCED FEATURES:
- **Multi-Sheet**: Create 10+ sheets in one call
- **Formula Types**: Natural language OR direct Excel syntax
- **Chart Positioning**: Specify exact ranges and types
- **Data Validation**: Columns auto-detected (numeric, date, text)
- **Cross-References**: Link data across sheets
- **Batch Operations**: Multiple formulas/charts in one call

📋 PARAMETERS:
- `workbook_name`: (optional) Name for NEW workbook
- `workbook_id`: (optional) ID of EXISTING workbook to update
- `worksheets`: (optional) Array of worksheet definitions
- `formulas`: (optional) Global formulas to add
- `charts`: (optional) Global charts to add
- `sheet_description`: (optional) Legacy simple mode
- `include_formulas`: (optional) Auto-add formulas (default: true)
- `include_charts`: (optional) Auto-generate charts (default: true)

⚙️ RETURNS:
```python
{
    "success": true,
    "mode": "create|update",
    "workbook_id": "...",
    "web_url": "...",
    "worksheets_created": [...],
    "worksheets_updated": [...],
    "formulas_added": 5,
    "formulas": [{...}],
    "charts_created": 2,
    "charts": [{...}]
}
```

🎯 USE CASES:
✅ **Creating Full Reports**: Multi-sheet workbooks with calculations and visualizations
✅ **Updating Existing**: Add formulas/charts to existing workbooks
✅ **Complex Analysis**: Cross-sheet references and advanced formulas
✅ **Quick Templates**: Simple single-sheet creation
✅ **Dashboards**: Multiple chart types across sheets

⚡ This replaces the need for multiple tool calls:
- Instead of: create_workbook → add_worksheet → update_range → set_formula → create_chart (5+ calls)
- Use this: ONE CALL with all specifications""",
            "category": "smart_automation",
            "tier": 1,
            "priority": "critical",
            "parameters": {
                "type": "object",
                "properties": {
                    "workbook_name": {
                        "type": "string",
                        "description": "Name for NEW workbook (creates new)",
                        "required": False
                    },
                    "workbook_id": {
                        "type": "string",
                        "description": "ID of EXISTING workbook to update",
                        "required": False
                    },
                    "worksheets": {
                        "type": "array",
                        "description": "Array of worksheet definitions with name, columns, data, formulas, charts",
                        "required": False
                    },
                    "formulas": {
                        "type": "array",
                        "description": "Global formulas: [{sheet, cell/range, formula}]",
                        "required": False
                    },
                    "charts": {
                        "type": "array",
                        "description": "Global charts: [{sheet, type, range, title}]",
                        "required": False
                    },
                    "sheet_description": {
                        "type": "string",
                        "description": "LEGACY: Simple single-sheet description",
                        "required": False
                    },
                    "data_structure": {
                        "type": "object",
                        "description": "LEGACY: Simple single-sheet structure",
                        "required": False
                    },
                    "include_formulas": {
                        "type": "boolean",
                        "description": "Auto-add formulas (default: true)",
                        "default": True
                    },
                    "include_charts": {
                        "type": "boolean",
                        "description": "Auto-generate charts (default: true)",
                        "default": True
                    }
                },
                "required": []
            },
            "returns": {
                "type": "object",
                "description": "Dict with mode, workbook_id, web_url, worksheets_created, worksheets_updated, formulas_added, formulas array, charts_created, charts array"
            },
            "user_facing_language": {
                "action_verb": "build",
                "resource_name": "Excel workbook",
                "natural_phrases": [
                    "create an Excel workbook with",
                    "build a spreadsheet with multiple sheets",
                    "add formulas to existing workbook",
                    "create comprehensive Excel report"
                ],
                "capability_description": "I can create complete Excel workbooks with multiple sheets, formulas, and charts in one operation. I can also update existing workbooks with new formulas or charts.",
                "example_ai_responses": [
                    "I'll create a comprehensive workbook with Sales Data, Summary, and Charts sheets.",
                    "I'll add those formulas and charts to your existing workbook.",
                    "I'll build a complete sales report with cross-sheet calculations."
                ]
            },
            "tool_intelligence": {
                "category": "smart_automation",
                "replaces_tools": [
                    "microsoft_excel_create_workbook",
                    "microsoft_excel_add_worksheet",
                    "microsoft_excel_update_range",
                    "microsoft_excel_set_formula",
                    "microsoft_excel_create_chart"
                ],
                "typical_workflow_patterns": [
                    "smart_sheet_builder(complete spec) → share_workbook",
                    "smart_sheet_builder(create) → smart_sheet_builder(update with new formulas)",
                    "data_analysis → smart_sheet_builder(create report)"
                ],
                "auto_suggests_when": [
                    "User needs multi-sheet workbook",
                    "User wants formulas and charts together",
                    "User needs to update existing workbook"
                ],
                "performance_expectations": {
                    "typical_duration_ms": 5000,
                    "rate_limit_per_minute": 15
                }
            }
        }
        break

# Save
with open('tools/schemas/microsoft_excel_tools.json', 'w', encoding='utf-8') as f:
    json.dump(schema, f, indent=2, ensure_ascii=False)

print("✅ Updated microsoft_excel_smart_sheet_builder schema")
print("📊 Now supports:")
print("   - Multiple worksheets")
print("   - Natural language + Excel formulas")
print("   - Cross-sheet references")
print("   - Create NEW or UPDATE EXISTING workbooks")
print("   - Granular formula/chart updates")
