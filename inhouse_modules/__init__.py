"""
InHouse Print Modules
=====================

Core database and calculation modules for InHouse Print operations.
These modules were migrated from In_House_SQL/G_Folder to make AI_agents independent.

Modules:
- db_connector: SQL Server database connection (InHousePrintDB)
- query_library: 100+ pre-built business intelligence queries (QueryLibrary)
- complete_calculator_implementation: Print quote calculator (ComprehensiveQuoteCalculator)
- stock_database_tools: Inventory management tools (StockDatabaseTools)

Usage:
    from inhouse_modules.db_connector import InHousePrintDB
    from inhouse_modules.query_library import QueryLibrary
    from inhouse_modules.complete_calculator_implementation import ComprehensiveQuoteCalculator
    from inhouse_modules.stock_database_tools import StockDatabaseTools
"""

__version__ = "1.0.0"
__all__ = [
    "InHousePrintDB",
    "QueryLibrary", 
    "ComprehensiveQuoteCalculator",
    "StockDatabaseTools"
]
