"""
Calculator Module Backend
Contains tool_use_agent, query_library, and routes
"""

# ToolUseAgent import disabled - causes circular dependency with complete_calculator_implementation
# InHouse Print tools now use direct database access via db_connector.py (Jan 2026)
# See: INHOUSE_TOOLS_COMPLETE_FIX_JAN13_2026.md
try:
    from .tool_use_agent import ToolUseAgent
except ImportError:
    # Expected: complete_calculator_implementation not in standard path
    # All InHouse tools bypass ToolUseAgent and use Registry V3 directly
    ToolUseAgent = None

from .query_library import QueryLibrary

__all__ = ['ToolUseAgent', 'QueryLibrary']
__version__ = '2.0.0'
__author__ = 'InHouse Print'
