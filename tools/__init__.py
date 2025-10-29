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

print("[OK] AI Agents Tool System loaded - 34 tools across 8 platforms")
