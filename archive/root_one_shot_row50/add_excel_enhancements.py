"""Add new enhancement tools to Microsoft Excel schema"""
import json

# Load existing schema
with open('tools/schemas/microsoft_excel_tools.json', 'r', encoding='utf-8') as f:
    schema = json.load(f)

print(f"Current tools: {len(schema['tools'])}")

# Define new tools
new_tools = [
    {
        "name": "microsoft_excel_smart_formula_builder",
        "short_description": "⭐ SMART: AI Formula Assistant - Convert natural language to Excel formulas",
        "description": "🚨 CRITICAL EXECUTION RULES:\n(1) Execute THIS tool NOW - NEVER use cached/remembered data\n(2) MUST return format: 'Applied formula **[formula]** to range [range]: [explanation]'\n(3) Use EXACT values from tool response\n(4) If tool fails, say 'Could not generate formula' - suggest alternative phrasing\n\n⚠️ MUST USE: execute_tool(tool_name='microsoft_excel_smart_formula_builder', ...) - DO NOT call directly!\n\n⭐ AI FORMULA ASSISTANT - Converts natural language to Excel formulas automatically.\n\n✨ SUPPORTED PATTERNS:\n- SUM: 'sum column A', 'total of column B'\n- AVERAGE: 'average column D', 'mean of column E'\n- MULTIPLY: 'multiply column B by column C'\n- COUNT: 'count column A'\n\n📊 EXAMPLES:\n- \"sum column A\" → =SUM(A:A)\n- \"multiply column B by column C\" → =B2*C2",
        "category": "smart_automation",
        "tier": 1,
        "priority": "high",
        "parameters": {
            "type": "object",
            "properties": {
                "workbook_id": {
                    "type": "string",
                    "description": "OneDrive item ID of the workbook"
                },
                "worksheet_name": {
                    "type": "string",
                    "description": "Name of the worksheet"
                },
                "natural_language_query": {
                    "type": "string",
                    "description": "Natural language description. Examples: 'sum column A', 'multiply column B by column C'"
                },
                "target_range": {
                    "type": "string",
                    "description": "Cell or range (e.g., 'C1', 'D2:D100')"
                },
                "context": {
                    "type": "object",
                    "description": "Optional context. Example: {'has_headers': true}",
                    "required": False
                }
            },
            "required": ["workbook_id", "worksheet_name", "natural_language_query", "target_range"]
        },
        "returns": {
            "type": "object",
            "description": "Dict with formula, explanation, applied_range, success"
        },
        "user_facing_language": {
            "action_verb": "build",
            "resource_name": "formula",
            "natural_phrases": ["create a formula", "calculate the total", "sum column"],
            "capability_description": "I can convert natural language to Excel formulas. Just tell me what calculation you need.",
            "example_ai_responses": ["I'll create a SUM formula to total column A."]
        },
        "tool_intelligence": {
            "category": "smart_automation",
            "typical_workflow_patterns": [
                "update_range(data) → smart_formula_builder(calculations) → create_chart"
            ],
            "success_indicators": {
                "keywords": ["formula applied", "calculation created"]
            },
            "failure_indicators": {
                "keywords": ["could not generate formula"]
            },
            "performance_expectations": {
                "typical_duration_ms": 500,
                "rate_limit_per_minute": 60
            }
        }
    },
    {
        "name": "microsoft_excel_batch_update",
        "short_description": "⚡ Update multiple ranges in one operation (reduces API calls)",
        "description": "⚠️ MUST USE: execute_tool(tool_name='microsoft_excel_batch_update', ...) - DO NOT call directly!\n\n⚡ PERFORMANCE OPTIMIZATION - Update multiple cell ranges in a single operation.\n\n✨ BENEFITS:\n- Reduces API calls\n- Faster execution\n- Update multiple columns at once",
        "category": "content_management",
        "priority": "medium",
        "parameters": {
            "type": "object",
            "properties": {
                "workbook_id": {
                    "type": "string",
                    "description": "Workbook ID"
                },
                "worksheet_name": {
                    "type": "string",
                    "description": "Worksheet name"
                },
                "updates": {
                    "type": "array",
                    "description": "Array of {'range': 'A1:A10', 'values': [[...]]} objects",
                    "items": {
                        "type": "object",
                        "properties": {
                            "range": {"type": "string"},
                            "values": {"type": "array"}
                        },
                        "required": ["range", "values"]
                    }
                }
            },
            "required": ["workbook_id", "worksheet_name", "updates"]
        },
        "returns": {
            "type": "object",
            "description": "Dict with total_updates, successful, failed, results"
        },
        "user_facing_language": {
            "action_verb": "update",
            "resource_name": "multiple ranges",
            "natural_phrases": ["update multiple ranges", "populate several columns"],
            "capability_description": "I can update multiple cell ranges in one operation, which is faster.",
            "example_ai_responses": ["I'll update all 3 ranges at once."]
        },
        "tool_intelligence": {
            "category": "content_management",
            "typical_workflow_patterns": [
                "create_workbook → batch_update(populate all) → smart_formula_builder"
            ],
            "performance_expectations": {
                "typical_duration_ms": 1200,
                "rate_limit_per_minute": 30
            }
        }
    }
]

# Add new tools
schema['tools'].extend(new_tools)

print(f"New tool count: {len(schema['tools'])}")

# Update version
schema['version'] = "2.1"
schema['description'] = schema['description'].replace('v2.0', 'v2.1').replace(
    'Single-call workflows',
    'AI Formula Assistant, Batch Updates, Single-call workflows'
)

# Save updated schema
with open('tools/schemas/microsoft_excel_tools.json', 'w', encoding='utf-8') as f:
    json.dump(schema, f, indent=2, ensure_ascii=False)

print("✅ Schema updated successfully!")
print(f"Added tools: {[t['name'] for t in new_tools]}")
