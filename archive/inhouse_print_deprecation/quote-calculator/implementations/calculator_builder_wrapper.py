"""
Calculator Builder Tools Wrapper - Registry V3 Integration

This wrapper provides the 6 calculator builder tools and 7 custom calculator query tools
for TIER 2E Custom Quote Workflow. These tools enable AI agents to build formula-based
calculators and query custom calculator system.

Architecture:
- calculator_builder_* tools: Build custom calculators interactively
- custom_calculator_* tools: Query and analyze custom calculators

File: UI/modules_external/quote-calculator/implementations/calculator_builder_wrapper.py
"""

import sys
from pathlib import Path

# Add backend directory to path for imports
backend_dir = Path(__file__).parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Add root directory for shared imports
root_dir = Path(__file__).parent.parent.parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# Add AI_infrastructure directory for shared.database_utils
ai_infra_dir = root_dir / "AI_infrastructure"
if str(ai_infra_dir) not in sys.path:
    sys.path.insert(0, str(ai_infra_dir))

# Import builder tools
try:
    from calculator_builder_tools import (
        calculator_builder_start,
        calculator_builder_add_parameter,
        calculator_builder_set_formula,
        calculator_builder_add_component,
        calculator_builder_test,
        calculator_builder_save
    )
    print("[Calculator Builder Wrapper] ✓ calculator_builder_tools imported successfully")
except Exception as e:
    print(f"[Calculator Builder Wrapper] ✗ Failed to import calculator_builder_tools: {e}")
    # Create stub functions
    def calculator_builder_start(**kwargs):
        return {"success": False, "error": "calculator_builder_tools not available"}
    def calculator_builder_add_parameter(**kwargs):
        return {"success": False, "error": "calculator_builder_tools not available"}
    def calculator_builder_set_formula(**kwargs):
        return {"success": False, "error": "calculator_builder_tools not available"}
    def calculator_builder_add_component(**kwargs):
        return {"success": False, "error": "calculator_builder_tools not available"}
    def calculator_builder_test(**kwargs):
        return {"success": False, "error": "calculator_builder_tools not available"}
    def calculator_builder_save(**kwargs):
        return {"success": False, "error": "calculator_builder_tools not available"}

# Import query library for custom calculator queries
try:
    from query_library import QueryLibrary
    ql = QueryLibrary()
    print("[Calculator Builder Wrapper] ✓ QueryLibrary imported for custom calculator queries")
    
    # Create wrapper functions for custom calculator queries
    def custom_calculator_get_schema_guide(**kwargs):
        """Get complete schema guide for custom calculator system"""
        # This is a static guide, return it directly
        try:
            # Read from custom_calculator_guide.json
            import json
            guide_path = Path(__file__).parent.parent / "schema" / "custom_calculator_guide.json"
            with open(guide_path, 'r', encoding='utf-8') as f:
                guide_data = json.load(f)
                tool = guide_data['tools'][0]  # First tool is the schema guide
                # Return the schema_guide_content from the tool
                return {
                    "success": True,
                    "guide": tool.get("schema_guide_content", tool.get("description", "Schema guide not available"))
                }
        except Exception as e:
            return {"success": False, "error": f"Failed to load schema guide: {str(e)}"}
    
    def custom_calculator_list(**kwargs):
        """List all custom calculators with filters"""
        try:
            sql = ql._generate_sql('list_custom_calculators', kwargs)
            # Execute would happen in AI agent, return SQL for now
            return {
                "success": True,
                "query_name": "list_custom_calculators",
                "sql": sql,
                "parameters": kwargs,
                "note": "Execute this SQL via calculator_database_query tool"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def custom_calculator_get_detail(**kwargs):
        """Get complete details for specific custom calculator"""
        try:
            sql = ql._generate_sql('get_custom_calculator_detail', kwargs)
            return {
                "success": True,
                "query_name": "get_custom_calculator_detail",
                "sql": sql,
                "parameters": kwargs,
                "note": "Execute this SQL via calculator_database_query tool"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def custom_calculator_search(**kwargs):
        """Search custom calculators by text"""
        try:
            sql = ql._generate_sql('search_custom_calculators', kwargs)
            return {
                "success": True,
                "query_name": "search_custom_calculators",
                "sql": sql,
                "parameters": kwargs,
                "note": "Execute this SQL via calculator_database_query tool"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def custom_calculator_get_parameters(**kwargs):
        """Show which pricing parameters are used by calculators"""
        try:
            sql = ql._generate_sql('get_calculator_parameters_used', kwargs)
            return {
                "success": True,
                "query_name": "get_calculator_parameters_used",
                "sql": sql,
                "parameters": kwargs,
                "note": "Execute this SQL via calculator_database_query tool"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def custom_calculator_get_usage_stats(**kwargs):
        """Get usage statistics over time period"""
        try:
            sql = ql._generate_sql('get_calculator_usage_stats', kwargs)
            return {
                "success": True,
                "query_name": "get_calculator_usage_stats",
                "sql": sql,
                "parameters": kwargs,
                "note": "Execute this SQL via calculator_database_query tool"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def custom_calculator_get_components(**kwargs):
        """List component usage across calculators"""
        try:
            sql = ql._generate_sql('get_custom_calculator_components', kwargs)
            return {
                "success": True,
                "query_name": "get_custom_calculator_components",
                "sql": sql,
                "parameters": kwargs,
                "note": "Execute this SQL via calculator_database_query tool"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
except Exception as e:
    print(f"[Calculator Builder Wrapper] ✗ Failed to import QueryLibrary: {e}")
    # Create stub functions
    def custom_calculator_get_schema_guide(**kwargs):
        return {"success": False, "error": "QueryLibrary not available"}
    def custom_calculator_list(**kwargs):
        return {"success": False, "error": "QueryLibrary not available"}
    def custom_calculator_get_detail(**kwargs):
        return {"success": False, "error": "QueryLibrary not available"}
    def custom_calculator_search(**kwargs):
        return {"success": False, "error": "QueryLibrary not available"}
    def custom_calculator_get_parameters(**kwargs):
        return {"success": False, "error": "QueryLibrary not available"}
    def custom_calculator_get_usage_stats(**kwargs):
        return {"success": False, "error": "QueryLibrary not available"}
    def custom_calculator_get_components(**kwargs):
        return {"success": False, "error": "QueryLibrary not available"}


# Export all functions for module plugin loader
__all__ = [
    # Builder tools
    'calculator_builder_start',
    'calculator_builder_add_parameter',
    'calculator_builder_set_formula',
    'calculator_builder_add_component',
    'calculator_builder_test',
    'calculator_builder_save',
    # Query tools
    'custom_calculator_get_schema_guide',
    'custom_calculator_list',
    'custom_calculator_get_detail',
    'custom_calculator_search',
    'custom_calculator_get_parameters',
    'custom_calculator_get_usage_stats',
    'custom_calculator_get_components'
]
