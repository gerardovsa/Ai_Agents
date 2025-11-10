"""
AI Agents Database Toolkit
===========================

Complete CLI toolkit for managing the AI Agents infrastructure database.

Modules:
--------
- schema_manager: Create, view, and migrate database schemas
- user_manager: Manage users and their credentials
- session_manager: Handle user sessions and cleanup
- query_tool: Interactive SQL query interface
- diagnostics: Health checks and troubleshooting
- migrations: Schema version control

Usage:
------
    python -m AI_infrastructure.database_toolkit.cli --help
    python -m AI_infrastructure.database_toolkit.cli schema --view
    python -m AI_infrastructure.database_toolkit.cli users --list
    python -m AI_infrastructure.database_toolkit.cli sessions --active
"""

__version__ = "1.0.0"
__author__ = "AI Agents Team"

from .schema_manager import SchemaManager
from .user_manager import UserManager
from .session_manager import SessionManager
from .query_tool import QueryTool
from .diagnostics import Diagnostics

__all__ = [
    'SchemaManager',
    'UserManager', 
    'SessionManager',
    'QueryTool',
    'Diagnostics'
]
