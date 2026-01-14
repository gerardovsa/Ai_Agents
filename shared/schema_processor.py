"""
Dynamic Schema Processor
========================
Injects dynamic configuration values into tool schemas at runtime.

Replaces placeholders like {{DYNAMIC:kanban_columns}} with actual config values.

Usage:
    from shared.schema_processor import process_schema
    
    # Load schema with placeholders
    with open('tools/schemas/synergy_tools.json') as f:
        schema = json.load(f)
    
    # Process and inject dynamic values
    processed_schema = process_schema(schema)
    
    # Now enums are real arrays, not strings!
"""

import json
import re
from typing import Any, Dict, List, Union
from shared.synergy_config import get_synergy_config

# Regex to match {{DYNAMIC:config_id}} placeholders
DYNAMIC_PATTERN = re.compile(r'\{\{DYNAMIC:([a-z_]+)\}\}')


def process_schema(schema: Union[Dict, List, str, Any], config=None) -> Any:
    """
    Recursively process schema and replace {{DYNAMIC:...}} placeholders.
    
    Args:
        schema: Schema object (dict, list, string, or primitive)
        config: SynergyConfig instance (optional, will create if needed)
        
    Returns:
        Processed schema with dynamic values injected
    """
    if config is None:
        config = get_synergy_config()
    
    # Handle strings - check for placeholders
    if isinstance(schema, str):
        match = DYNAMIC_PATTERN.fullmatch(schema)
        if match:
            config_id = match.group(1)
            # Map config_id to config method
            if config_id == 'kanban_columns':
                return config.get_kanban_columns()
            elif config_id == 'priority_levels':
                return config.get_priority_levels()
            elif config_id == 'session_statuses':
                return config.get_session_statuses()
            elif config_id == 'permission_levels':
                return config.get_permission_levels()
            elif config_id == 'blocker_types':
                return config.get_blocker_types()
            elif config_id == 'platform_options':
                return config.get_platform_options()
            else:
                # Unknown config_id - return generic config
                return config.get_config(config_id, default=[])
        return schema
    
    # Handle dictionaries - process all values
    if isinstance(schema, dict):
        return {key: process_schema(value, config) for key, value in schema.items()}
    
    # Handle lists - process all items
    if isinstance(schema, list):
        return [process_schema(item, config) for item in schema]
    
    # Primitives (int, bool, None) - return as-is
    return schema


def load_and_process_schema(schema_path: str) -> Dict:
    """
    Load a JSON schema file and process dynamic placeholders.
    
    Args:
        schema_path: Path to schema file (e.g., 'tools/schemas/synergy_tools.json')
        
    Returns:
        Processed schema with dynamic values injected
    """
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = json.load(f)
    
    return process_schema(schema)


def get_dynamic_enum(config_id: str) -> List[str]:
    """
    Get a dynamic enum value by config_id.
    
    Args:
        config_id: Configuration identifier (e.g., 'kanban_columns')
        
    Returns:
        List of enum values
    """
    config = get_synergy_config()
    
    # Map config_id to config method
    mapping = {
        'kanban_columns': config.get_kanban_columns,
        'priority_levels': config.get_priority_levels,
        'session_statuses': config.get_session_statuses,
        'permission_levels': config.get_permission_levels,
        'blocker_types': config.get_blocker_types,
        'platform_options': config.get_platform_options,
    }
    
    method = mapping.get(config_id)
    if method:
        return method()
    
    # Fallback to generic config
    return config.get_config(config_id, default=[])


if __name__ == "__main__":
    # Test schema processing
    print("🧪 Testing Dynamic Schema Processor\n")
    
    # Test with sample schema
    test_schema = {
        "tool": {
            "name": "test_tool",
            "parameters": {
                "kanban_column": {
                    "type": "string",
                    "enum": "{{DYNAMIC:kanban_columns}}"
                },
                "priority": {
                    "type": "string",
                    "enum": "{{DYNAMIC:priority_levels}}"
                },
                "status": {
                    "type": "string",
                    "enum": "{{DYNAMIC:session_statuses}}"
                }
            }
        }
    }
    
    print("📄 Input Schema (with placeholders):")
    print(json.dumps(test_schema, indent=2))
    
    print("\n🔄 Processing...")
    processed = process_schema(test_schema)
    
    print("\n✅ Processed Schema (with injected values):")
    print(json.dumps(processed, indent=2))
    
    print("\n📊 Dynamic Enums:")
    print(f"  Kanban Columns: {get_dynamic_enum('kanban_columns')}")
    print(f"  Priority Levels: {get_dynamic_enum('priority_levels')}")
    print(f"  Session Statuses: {get_dynamic_enum('session_statuses')}")
