"""Validate all tool schema JSON files"""
import json
import os
from pathlib import Path

def validate_schemas():
    """Check all tool schemas for JSON errors"""
    schemas_dir = Path("tools/schemas")
    errors = []
    success = []
    
    for schema_file in schemas_dir.glob("*.json"):
        try:
            with open(schema_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            success.append(schema_file.name)
        except json.JSONDecodeError as e:
            errors.append(f"{schema_file.name}: Line {e.lineno} - {e.msg}")
    
    print(f"Valid: {len(success)} files")
    if errors:
        print(f"Errors: {len(errors)} files")
        for error in errors:
            print(f"  - {error}")
    
    return len(errors) == 0

if __name__ == "__main__":
    valid = validate_schemas()
    exit(0 if valid else 1)
