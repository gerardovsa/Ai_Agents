use Print Module
====================

Database connection module for InHouse Print operations.

Modules:
- db_connector: SQL Server database connection (InHousePrintDB)

Usage:
    from UI.modules_external.inhouse_print.db_connector import InHousePrintDB
"""

__version__ = "2.0.0"
__all__ = ["InHousePrintDB"]

from .db_connector import InHousePrintDB
