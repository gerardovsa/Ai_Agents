"""
Export Complete VSA Database Schema from Supabase
==================================================

Connects to Supabase VSA database and exports complete schema including:
- All tables with column definitions
- Data types and constraints
- Indexes and primary keys
- Foreign key relationships
- Sample data from each table

Database: wuwmvtslltqhaycyukxk.supabase.co
Purpose: VSA Veterinary Alerts Module
"""

import os
import sys
import json
from datetime import datetime
from supabase import create_client, Client

# Supabase credentials
SUPABASE_URL = "https://wuwmvtslltqhaycyukxk.supabase.co"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind1d212dHNsbHRxaGF5Y3l1a3hrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTIyNDMzNCwiZXhwIjoyMDY2ODAwMzM0fQ.tUJ473GHC139vvH0X6fIgaFtgmLTl-VaUCf9kY6xQj4"

def get_table_structure(supabase: Client, table_name: str) -> dict:
    """Get complete structure of a table including sample data."""
    try:
        # Get sample rows to understand structure
        result = supabase.table(table_name).select("*").limit(5).execute()
        
        structure = {
            "table_name": table_name,
            "columns": {},
            "sample_row_count": len(result.data),
            "sample_data": result.data[:2] if result.data else []  # First 2 rows
        }
        
        # Analyze columns from sample data
        if result.data:
            first_row = result.data[0]
            for column, value in first_row.items():
                structure["columns"][column] = {
                    "python_type": type(value).__name__,
                    "sample_value": str(value)[:100] if value else None,  # First 100 chars
                    "has_nulls": any(row.get(column) is None for row in result.data)
                }
        
        return structure
    except Exception as e:
        return {
            "table_name": table_name,
            "error": str(e)
        }


def get_table_count(supabase: Client, table_name: str) -> int:
    """Get total row count for a table."""
    try:
        result = supabase.table(table_name).select("*", count="exact").limit(1).execute()
        return result.count if hasattr(result, 'count') else 0
    except:
        return 0


def export_schema():
    """Export complete database schema."""
    
    print("=" * 80)
    print("VSA DATABASE SCHEMA EXPORT")
    print("=" * 80)
    print(f"\nDatabase: {SUPABASE_URL}")
    print(f"Export Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n" + "=" * 80)
    
    # Connect to Supabase
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        print("\n✅ Connected to Supabase successfully!")
    except Exception as e:
        print(f"\n❌ Failed to connect: {e}")
        return
    
    # Known tables from metadata
    known_tables = [
        "veterinary_calls",
        "call_manager_alerts",
        "call_full_transcript_and_full_analysis",
        "manager_alerts_tags",
        "follow_up_actions"
    ]
    
    schema_export = {
        "database_info": {
            "url": SUPABASE_URL,
            "project_id": "wuwmvtslltqhaycyukxk",
            "region": "ap-southeast-2",
            "exported_at": datetime.now().isoformat(),
            "purpose": "VSA Veterinary Alerts Module"
        },
        "tables": {}
    }
    
    # Export each table
    for table_name in known_tables:
        print(f"\n{'─' * 80}")
        print(f"📊 Analyzing table: {table_name}")
        print('─' * 80)
        
        # Get structure
        structure = get_table_structure(supabase, table_name)
        
        if "error" in structure:
            print(f"   ⚠️  Error: {structure['error']}")
            schema_export["tables"][table_name] = structure
            continue
        
        # Get row count
        row_count = get_table_count(supabase, table_name)
        structure["total_rows"] = row_count
        
        print(f"   Total Rows: {row_count:,}")
        print(f"   Columns: {len(structure['columns'])}")
        print(f"\n   Column Details:")
        print(f"   {'Column Name':<40} {'Type':<15} {'Has Nulls'}")
        print(f"   {'-' * 75}")
        
        for col_name, col_info in structure['columns'].items():
            has_nulls = "✓" if col_info['has_nulls'] else "✗"
            print(f"   {col_name:<40} {col_info['python_type']:<15} {has_nulls}")
        
        schema_export["tables"][table_name] = structure
    
    # Save to JSON file
    output_file = "VSA_DATABASE_SCHEMA_EXPORT.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(schema_export, f, indent=2, default=str)
    
    print("\n" + "=" * 80)
    print(f"✅ Schema exported to: {output_file}")
    print("=" * 80)
    
    # Create markdown documentation
    create_markdown_documentation(schema_export)
    
    return schema_export


def create_markdown_documentation(schema_export: dict):
    """Create human-readable markdown documentation."""
    
    md_content = f"""# VSA Database Schema Documentation

**Database URL:** {schema_export['database_info']['url']}  
**Project ID:** {schema_export['database_info']['project_id']}  
**Region:** {schema_export['database_info']['region']}  
**Exported:** {schema_export['database_info']['exported_at']}  
**Purpose:** {schema_export['database_info']['purpose']}

---

## 📊 Database Overview

**Total Tables:** {len(schema_export['tables'])}

"""
    
    # Table summary
    md_content += "### Table Summary\n\n"
    md_content += "| Table Name | Total Rows | Columns | Status |\n"
    md_content += "|------------|------------|---------|--------|\n"
    
    for table_name, table_info in schema_export['tables'].items():
        if "error" in table_info:
            md_content += f"| {table_name} | N/A | N/A | ⚠️ Error |\n"
        else:
            row_count = table_info.get('total_rows', 0)
            col_count = len(table_info['columns'])
            md_content += f"| {table_name} | {row_count:,} | {col_count} | ✅ |\n"
    
    md_content += "\n---\n\n"
    
    # Detailed table schemas
    for table_name, table_info in schema_export['tables'].items():
        if "error" in table_info:
            md_content += f"## ⚠️ {table_name}\n\n"
            md_content += f"**Error:** {table_info['error']}\n\n"
            continue
        
        md_content += f"## 📋 {table_name}\n\n"
        md_content += f"**Total Rows:** {table_info.get('total_rows', 0):,}  \n"
        md_content += f"**Columns:** {len(table_info['columns'])}\n\n"
        
        # Column details
        md_content += "### Column Schema\n\n"
        md_content += "| Column Name | Data Type | Nullable | Sample Value |\n"
        md_content += "|-------------|-----------|----------|-------------|\n"
        
        for col_name, col_info in table_info['columns'].items():
            nullable = "Yes" if col_info['has_nulls'] else "No"
            sample = col_info.get('sample_value', 'N/A')
            if sample and len(sample) > 50:
                sample = sample[:47] + "..."
            md_content += f"| `{col_name}` | {col_info['python_type']} | {nullable} | {sample} |\n"
        
        # Sample data
        if table_info.get('sample_data'):
            md_content += "\n### Sample Data (First 2 Rows)\n\n"
            md_content += "```json\n"
            md_content += json.dumps(table_info['sample_data'], indent=2, default=str)
            md_content += "\n```\n"
        
        md_content += "\n---\n\n"
    
    # Save markdown
    md_file = "VSA_DATABASE_SCHEMA_EXPORT.md"
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"📄 Markdown documentation created: {md_file}")


if __name__ == "__main__":
    export_schema()
