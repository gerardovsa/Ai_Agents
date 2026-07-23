"""
AI Agents - Tool Integration System
=====================================

This module provides MCP-compatible tool integrations for all platforms.

Usage:
    from tools import ToolRegistry
    
    registry = ToolRegistry()
    result = registry.execute_tool("supabase_query", table="users", select="*")
"""

from .registry import ToolRegistry

__version__ = "1.0.0"
__all__ = ["ToolRegistry"]

# NOTE (July 23, 2026): The previous hard-coded "34 tools across 8 platforms"
# print was stale (real counts are 829+ / 30+) and fired on every `import tools`,
# polluting the Render boot log before any ToolRegistry was instantiated. The
# authoritative boot line now lives in tools/registry.py:ToolRegistry.__init__
# (which knows the actual loaded counts) and in tools/registry_v3.py. Do not
# re-introduce a module-level print here.
