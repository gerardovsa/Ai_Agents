"""Add SMART Sheet Builder tool to Excel schema"""
import json

# Load schema
with open('tools/schemas/microsoft_excel_tools.json', 'r', encoding='utf-8') as f:
    schema = json.load(f)

# Find where to insert (after smart_financial_report)
smart_financial_idx = next(
    (i for i, t in enumerate(schema['tools']) if 'smart_financial_report' in t['name']), 
    None
)

# Create SMART Sheet Builder tool
smart_sheet_builder = {
    "name": "microsoft_excel_smart_sheet_builder",
    "short_description": "⭐ SMART: Build complete Excel workbook from natural language description",
    "description": """🚨 CRITICAL EXECUTION RULES:
(1) Execute THIS tool NOW - NEVER use cached/remembered data
(2) MUST return format: 'Created **[Name]** with [X] columns, [Y] formulas, and [chart_type] chart'
(3) Use EXACT values from tool response
(4) If tool fails, say 'Could not build sheet' - suggest simpler structure

⚠️ MUST USE: execute_tool(tool_name='microsoft_excel_smart_sheet_builder', ...) - DO NOT call directly!

⭐ SMART SHEET BUILDER - Create professional Excel workbooks from scratch using natural language.

✨ WHAT IT BUILDS:
- Auto-detects column structure from description
- Generates sample data matching column types
- Adds calculation formulas (SUM, AVERAGE)
- Creates appropriate charts
- Professional formatting
- Summary sheet with metadata

🎯 INTELLIGENCE FEATURES:
- Recognizes patterns: "sales tracker", "expense report", "project timeline"
- Auto-detects numeric columns for formulas
- Smart chart type selection based on description
- Generates realistic sample data

📊 EXAMPLE DESCRIPTIONS:
- "sales tracker with monthly totals and rep performance"
- "expense report with categories and budget tracking"
- "project timeline with milestones and owner assignments"
- "inventory list with stock levels and reorder alerts"
- "customer database with contact info and status tracking"

🔗 SMART WORKFLOW INTEGRATION:
- Uses excel_smart_formula_builder for calculations
- Uses excel_batch_update for efficient data loading
- Creates multi-sheet workbooks automatically

⚙️ CUSTOMIZATION:
- Provide data_structure dict to override auto-detection
- Specify columns, sample_data, formulas, chart_type
- Toggle formulas, charts, formatting on/off""",
    "category": "smart_automation",
    "tier": 1,
    "priority": "high",
    "parameters": {
        "type": "object",
        "properties": {
            "workbook_name": {
                "type": "string",
                "description": "Name for the workbook (e.g., 'Q1 Sales Tracker')"
            },
            "sheet_description": {
                "type": "string",
                "description": "Natural language description of what the sheet should contain. Examples: 'sales tracker with monthly totals', 'expense report with categories', 'project timeline with milestones'"
            },
            "data_structure": {
                "type": "object",
                "description": "Optional custom structure: {'columns': ['Name', 'Date', 'Amount'], 'sample_data': [[...]], 'formulas': ['sum totals'], 'chart_type': 'column'}",
                "required": False
            },
            "include_formulas": {
                "type": "boolean",
                "description": "Auto-add calculation formulas (SUM, AVERAGE) for numeric columns (default: true)",
                "default": True
            },
            "include_charts": {
                "type": "boolean",
                "description": "Auto-generate visualization chart based on data (default: true)",
                "default": True
            },
            "include_formatting": {
                "type": "boolean",
                "description": "Apply professional formatting (default: true)",
                "default": True
            }
        },
        "required": ["workbook_name", "sheet_description"]
    },
    "returns": {
        "type": "object",
        "description": "Dict with workbook_id, web_url, structure (columns, formulas, chart info), sheets created, ready_for_data flag"
    },
    "user_facing_language": {
        "action_verb": "build",
        "resource_name": "workbook",
        "natural_phrases": [
            "create a spreadsheet for",
            "build a tracker for",
            "make a worksheet for",
            "set up a workbook for",
            "generate a sheet for"
        ],
        "capability_description": "I can build complete Excel workbooks from scratch based on your description. Just tell me what you need to track.",
        "example_ai_responses": [
            "I'll create a sales tracker workbook with columns for rep names, monthly sales, and quarterly totals.",
            "I'll build an expense report with categories, amounts, and auto-calculated totals.",
            "I'll set up a project timeline with tasks, owners, dates, and status tracking."
        ]
    },
    "tool_intelligence": {
        "category": "smart_automation",
        "typical_workflow_patterns": [
            "smart_sheet_builder(create structure) → update_range(add real data) → create_chart(visualize)",
            "smart_sheet_builder(template) → share_workbook(team collaboration)"
        ],
        "auto_suggests_when": [
            "User asks to 'create a spreadsheet'",
            "User mentions tracking/reporting without existing data",
            "User needs template or starting point"
        ],
        "success_indicators": {
            "keywords": ["created workbook", "built sheet", "structure ready"]
        },
        "failure_indicators": {
            "keywords": ["could not build", "failed to create"]
        },
        "performance_expectations": {
            "typical_duration_ms": 3000,
            "rate_limit_per_minute": 20
        },
        "smart_offering_based_on_context": {
            "when_user_has_no_data": {
                "should_offer": True,
                "message": "I can build a starter template with sample data"
            },
            "when_user_has_csv": {
                "should_offer": False,
                "alternative": "Use excel_smart_import_csv instead"
            }
        }
    },
    "examples": [
        {
            "scenario": "Create sales tracker from scratch",
            "input": {
                "workbook_name": "Q1 2025 Sales Tracker",
                "sheet_description": "sales tracker with rep names, monthly sales amounts, and quarterly totals",
                "include_formulas": True,
                "include_charts": True
            },
            "output": {
                "success": True,
                "structure": {
                    "columns": ["Sales Rep", "Month", "Amount", "Region"],
                    "sample_rows": 5,
                    "formulas_added": [
                        {"column": "Amount", "formula": "=SUM(C:C)"}
                    ],
                    "chart_created": True,
                    "chart_type": "ColumnClustered"
                },
                "ready_for_data": True
            }
        },
        {
            "scenario": "Create expense report with custom columns",
            "input": {
                "workbook_name": "Monthly Expenses",
                "sheet_description": "expense tracking",
                "data_structure": {
                    "columns": ["Date", "Vendor", "Category", "Amount", "Receipt #"],
                    "chart_type": "pie"
                }
            },
            "output": {
                "success": True,
                "structure": {
                    "columns": ["Date", "Vendor", "Category", "Amount", "Receipt #"],
                    "chart_type": "Pie"
                }
            }
        }
    ],
    "smart_workflow_integration": {
        "uses_internally": [
            "excel_create_workbook",
            "excel_add_worksheet",
            "excel_smart_formula_builder",
            "excel_update_range",
            "excel_create_chart"
        ],
        "enhancement": "Complete end-to-end workbook creation from natural language - no manual setup needed",
        "replaces_manual_workflow": [
            "Manual: Create workbook → Add headers → Format → Add formulas → Create chart (5-10 minutes)",
            "SMART: One call with description (30 seconds)"
        ]
    }
}

# Insert after smart_financial_report
if smart_financial_idx is not None:
    schema['tools'].insert(smart_financial_idx + 1, smart_sheet_builder)
else:
    # Fallback: append to end
    schema['tools'].append(smart_sheet_builder)

# Update version
schema['version'] = "2.2"
schema['description'] = schema['description'].replace(
    'v2.1',
    'v2.2'
).replace(
    'AI Formula Assistant, Batch Updates',
    'SMART Sheet Builder (build from scratch), AI Formula Assistant, Batch Updates'
)

# Save
with open('tools/schemas/microsoft_excel_tools.json', 'w', encoding='utf-8') as f:
    json.dump(schema, f, indent=2, ensure_ascii=False)

print(f"✅ SMART Sheet Builder added!")
print(f"📊 Total tools: {len(schema['tools'])}")
print(f"🎯 SMART workflows: {len([t for t in schema['tools'] if 'smart_' in t['name']])}")
print(f"\n🚀 Build workbooks from natural language like:")
print("  - 'sales tracker with monthly totals'")
print("  - 'expense report with categories'")
print("  - 'project timeline with milestones'")
