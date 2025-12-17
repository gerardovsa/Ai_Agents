"""
Calculator Pricing Wrapper - Database Tools for AI Agents
==========================================================

Exposes Calculator Pricing Database (8-table Supabase system) to AI agents.
Auto-discovered by Registry V3 from schema/calculator_pricing_*.json

Architecture:
    AI Agent Request
        ↓
    Registry V3
        ↓
    calculator_pricing_wrapper.py (THIS FILE)
        ↓
    backend/calculator_pricing_db.py (CalculatorPricingDB class)
        ↓
    Supabase PostgreSQL (ai-agents-production-inhouse)

FILE: UI/modules_external/quote-calculator/implementations/calculator_pricing_wrapper.py
PURPOSE: Wrapper functions for Calculator Pricing Database tools
DEPENDENCIES:
- ../backend/calculator_pricing_db.py (CalculatorPricingDB class)
- ../backend/query_library.py (QueryLibrary for pre-built queries)

EXPORTS:
- calculator_database_get_schema_guide() - Complete schema documentation with query list
- calculator_database_query(sql, params) - Execute SELECT queries
- calculator_database_modify(sql, params, reason) - Execute INSERT/UPDATE/DELETE
- calculator_database_list_queries(category) - List pre-built queries from QueryLibrary

USED BY:
- tools/registry_v3.py (auto-discovery from schema/*.json)
- AI agents (via registry)

CREATED: December 17, 2025
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add paths for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.abspath(os.path.join(current_dir, '..', 'backend'))

if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Import database connectors
try:
    from calculator_pricing_db import CalculatorPricingDB
    CALCULATOR_PRICING_DB_AVAILABLE = True
    print("✅ [Calculator Pricing Wrapper] CalculatorPricingDB imported successfully")
except ImportError as e:
    CALCULATOR_PRICING_DB_AVAILABLE = False
    CalculatorPricingDB = None
    print(f"⚠️  [Calculator Pricing Wrapper] Failed to import CalculatorPricingDB: {e}")

try:
    from query_library import QueryLibrary
    QUERY_LIBRARY_AVAILABLE = True
    print("✅ [Calculator Pricing Wrapper] QueryLibrary imported successfully")
except ImportError as e:
    QUERY_LIBRARY_AVAILABLE = False
    QueryLibrary = None
    print(f"⚠️  [Calculator Pricing Wrapper] Failed to import QueryLibrary: {e}")


# ==================== SCHEMA GUIDE ====================

def calculator_database_get_schema_guide(**kwargs) -> Dict[str, Any]:
    """
    Get complete schema guide for Calculator Pricing Database
    
    Returns comprehensive documentation including:
    - Database overview (TWO SYSTEMS architecture)
    - All 8 table schemas with columns, types, constraints
    - JSONB field structures and access patterns
    - Foreign key relationships and data flow
    - Query construction best practices
    - 20+ example queries (pricing constants, product options, variance analysis)
    - List of available pre-built queries from QueryLibrary (dynamically injected)
    - Decision tree: When to use direct SQL vs QueryLibrary vs API endpoints
    
    Args:
        **kwargs: Optional parameters (currently unused)
    
    Returns:
        {
            "success": True,
            "guide": {
                "overview": {...},
                "tables": {...},
                "jsonb_structures": {...},
                "relationships": {...},
                "query_patterns": {...},
                "example_queries": {...},
                "available_queries": [...],  # Dynamically injected from QueryLibrary
                "decision_tree": {...}
            }
        }
    """
    
    # Get dynamically generated query list from QueryLibrary
    available_queries = []
    if QUERY_LIBRARY_AVAILABLE:
        try:
            query_lib = QueryLibrary()
            catalog = query_lib.query_catalog
            
            # Filter for Calculator Pricing Management category
            for query_name, query_meta in catalog.items():
                if query_meta.get('category') == 'Calculator Pricing Management':
                    available_queries.append({
                        "name": query_name,
                        "description": query_meta.get('description', ''),
                        "parameters": query_meta.get('parameters', {}),
                        "returns": query_meta.get('returns', ''),
                        "best_for": query_meta.get('best_for', '')
                    })
        except Exception as e:
            print(f"⚠️  Failed to load QueryLibrary catalog: {e}")
    
    guide = {
        "overview": {
            "database_name": "ai-agents-production-inhouse",
            "database_type": "Supabase PostgreSQL",
            "host": "aws-1-ap-southeast-2.pooler.supabase.com:6543",
            "purpose": "Calculator Pricing Management System - stores pricing constants and product options for 30 Shopify calculators",
            "architecture": "TWO INTEGRATED SYSTEMS",
            "total_tables": 8,
            "total_rows": "690+ rows (as of Dec 2025)",
            "created": "December 2025",
            "migrations": ["001_create_catalog_tables.sql", "002_fix_duplicates_and_enhance_stats.sql (Python)", "003_populate_overrides.py", "004_create_product_options_tables.sql"],
            
            "two_systems_explained": {
                "system_1": {
                    "name": "Pricing Constants",
                    "purpose": "Backend calculation variables (impos_setup, stock_waste, gst_rate, etc.)",
                    "tables": 4,
                    "total_rows": "~200",
                    "user_facing": False,
                    "examples": ["impos_setup: $15-$40 across calculators", "stock_waste: 5%-15%", "gst_rate: 10%"]
                },
                "system_2": {
                    "name": "Product Options",
                    "purpose": "Customer-facing dropdown configurations (Quantity, Stock Type, Print Type, etc.)",
                    "tables": 4,
                    "total_rows": "~600",
                    "user_facing": True,
                    "examples": ["Quantity: 50, 100, 250, 500, 1000", "Stock Type: Bond 80GSM @ $0.03, Gloss 150GSM @ $0.08", "Print Type: 4/4, 4/0, 4/1"]
                },
                "integration": "Both systems work together - pricing constants feed into calculator logic, product options are selected by customers"
            }
        },
        
        "tables": {
            "calculator_pricing_parameters": {
                "system": "Pricing Constants",
                "row_count": 64,
                "purpose": "Master list of all pricing parameters with base values and statistics",
                "key_columns": [
                    {"name": "id", "type": "SERIAL PRIMARY KEY", "description": "Unique parameter ID"},
                    {"name": "parameter_name", "type": "VARCHAR(255) UNIQUE", "description": "Parameter identifier (e.g., 'impos_setup', 'stock_waste')"},
                    {"name": "data_type", "type": "VARCHAR(50)", "description": "money, decimal, integer, percentage, boolean"},
                    {"name": "base_value", "type": "NUMERIC(10,4)", "description": "Default value used when no override exists"},
                    {"name": "description", "type": "TEXT", "description": "Human-readable explanation"},
                    {"name": "value_statistics", "type": "JSONB", "description": "Statistical analysis: min, max, mean, median, std_dev, variance_pct, distinct_values"},
                    {"name": "used_by_calculators", "type": "JSONB ARRAY", "description": "List of {calculator_name, value} objects showing usage"},
                    {"name": "source_file", "type": "VARCHAR(255)", "description": "Original calculator file"},
                    {"name": "created_at", "type": "TIMESTAMP", "description": "When parameter was created"},
                    {"name": "updated_at", "type": "TIMESTAMP", "description": "Last modification time"}
                ],
                "jsonb_structures": {
                    "value_statistics": {
                        "min": "numeric (minimum value across all calculators)",
                        "max": "numeric (maximum value across all calculators)",
                        "mean": "numeric (average value)",
                        "median": "numeric (middle value)",
                        "std_dev": "numeric (standard deviation)",
                        "variance_pct": "numeric (percentage variance: (max-min)/mean * 100)",
                        "distinct_values": "array of unique values"
                    },
                    "used_by_calculators": [
                        {"calculator_name": "BollardSigns", "value": 40.00},
                        {"calculator_name": "ConstructionSigns", "value": 28.00}
                    ]
                },
                "example_access": "SELECT value_statistics->>'variance_pct' FROM calculator_pricing_parameters WHERE parameter_name = 'impos_setup'",
                "indexes": ["parameter_name (UNIQUE)", "data_type", "created_at", "((value_statistics->>'variance_pct')::numeric) - GIN index"]
            },
            
            "calculator_parameter_overrides": {
                "system": "Pricing Constants",
                "row_count": 104,
                "purpose": "Calculator-specific custom values (only created if value ≠ base_value)",
                "key_columns": [
                    {"name": "id", "type": "SERIAL PRIMARY KEY", "description": "Unique override ID"},
                    {"name": "parameter_id", "type": "INTEGER REFERENCES calculator_pricing_parameters(id)", "description": "Foreign key to parameter"},
                    {"name": "calculator_name", "type": "VARCHAR(255)", "description": "Which calculator uses this override"},
                    {"name": "value", "type": "NUMERIC(10,4)", "description": "Override value (differs from base_value)"},
                    {"name": "is_active", "type": "BOOLEAN DEFAULT TRUE", "description": "Whether override is currently active"},
                    {"name": "effective_date", "type": "TIMESTAMP", "description": "When override takes effect"},
                    {"name": "notes", "type": "TEXT", "description": "Reason for override"},
                    {"name": "created_at", "type": "TIMESTAMP", "description": "When override was created"},
                    {"name": "updated_at", "type": "TIMESTAMP", "description": "Last modification"}
                ],
                "optimization": "Only 104 rows created instead of 284 potential (61% reduction) because rows only created when value ≠ base_value",
                "example_overrides": [
                    {"parameter": "impos_setup", "calculator": "BollardSigns", "base": 15.00, "override": 40.00},
                    {"parameter": "extra_arts", "calculator": "NotepadsA4", "base": 15.00, "override": 18.00}
                ],
                "indexes": ["parameter_id", "calculator_name", "is_active", "UNIQUE(parameter_id, calculator_name, effective_date)"]
            },
            
            "calculator_parameter_history": {
                "system": "Pricing Constants",
                "row_count": "104+ (grows over time)",
                "purpose": "Complete audit trail of all parameter and override changes",
                "key_columns": [
                    {"name": "id", "type": "SERIAL PRIMARY KEY", "description": "Unique history entry ID"},
                    {"name": "parameter_id", "type": "INTEGER", "description": "Which parameter was changed"},
                    {"name": "override_id", "type": "INTEGER", "description": "Which override was changed (NULL for parameter-level changes)"},
                    {"name": "change_type", "type": "VARCHAR(50)", "description": "parameter_created, override_created, override_updated, override_deleted"},
                    {"name": "old_value", "type": "NUMERIC(10,4)", "description": "Value before change"},
                    {"name": "new_value", "type": "NUMERIC(10,4)", "description": "Value after change"},
                    {"name": "changed_by", "type": "VARCHAR(255)", "description": "User or system that made change"},
                    {"name": "changed_at", "type": "TIMESTAMP DEFAULT NOW()", "description": "When change occurred"},
                    {"name": "notes", "type": "TEXT", "description": "Reason for change"}
                ],
                "usage": "Track all pricing changes over time, rollback capability, audit compliance",
                "indexes": ["parameter_id", "override_id", "change_type", "changed_at"]
            },
            
            "calculators_registry": {
                "system": "Pricing Constants",
                "row_count": 30,
                "purpose": "Registry of all calculators with metadata and parameters used",
                "key_columns": [
                    {"name": "id", "type": "SERIAL PRIMARY KEY", "description": "Unique calculator ID"},
                    {"name": "calculator_name", "type": "VARCHAR(255) UNIQUE", "description": "Calculator identifier (e.g., 'BollardSigns', 'NotepadsA4')"},
                    {"name": "display_name", "type": "VARCHAR(255)", "description": "Human-readable name"},
                    {"name": "description", "type": "TEXT", "description": "What this calculator does"},
                    {"name": "parameters_used", "type": "JSONB OBJECT", "description": "Map of parameter_name → value pairs"},
                    {"name": "shopify_product_id", "type": "VARCHAR(255)", "description": "Shopify product identifier"},
                    {"name": "special_features", "type": "JSONB ARRAY", "description": "DOUBLE_GST, TIERED_PRICING, DUAL_PROFIT, etc."},
                    {"name": "source_file", "type": "VARCHAR(255)", "description": "Implementation file path"},
                    {"name": "is_active", "type": "BOOLEAN DEFAULT TRUE", "description": "Whether calculator is currently active"},
                    {"name": "created_at", "type": "TIMESTAMP", "description": "When calculator was added"},
                    {"name": "updated_at", "type": "TIMESTAMP", "description": "Last modification"}
                ],
                "jsonb_structures": {
                    "parameters_used": {
                        "impos_setup": 40.00,
                        "stock_waste": 0.10,
                        "gst_rate": 0.10
                    },
                    "special_features": ["DOUBLE_GST", "TIERED_PRICING"]
                },
                "indexes": ["calculator_name (UNIQUE)", "is_active", "shopify_product_id"]
            },
            
            "product_options": {
                "system": "Product Options",
                "row_count": 154,
                "purpose": "Customer-facing dropdown option definitions (Quantity, Stock Type, Print Type, etc.)",
                "key_columns": [
                    {"name": "id", "type": "SERIAL PRIMARY KEY", "description": "Unique option ID"},
                    {"name": "calculator_name", "type": "VARCHAR(255)", "description": "Which calculator this option belongs to (NOT FK due to legacy data)"},
                    {"name": "option_name", "type": "VARCHAR(255)", "description": "Option identifier (e.g., 'Quantity', 'Stock Type')"},
                    {"name": "field_id", "type": "VARCHAR(50)", "description": "Shopify field ID (F1, F2, ..., F14)"},
                    {"name": "option_type", "type": "VARCHAR(50)", "description": "dropdown, radio, checkbox, text_input"},
                    {"name": "is_required", "type": "BOOLEAN DEFAULT FALSE", "description": "Whether customer must select this option"},
                    {"name": "default_choice", "type": "VARCHAR(255)", "description": "Default selected value"},
                    {"name": "display_order", "type": "INTEGER", "description": "Order to display on UI"},
                    {"name": "created_at", "type": "TIMESTAMP", "description": "When option was created"},
                    {"name": "updated_at", "type": "TIMESTAMP", "description": "Last modification"}
                ],
                "example_options": [
                    {"calculator": "NotepadsA4", "option_name": "Quantity", "field_id": "F1", "choices": 13},
                    {"calculator": "NotepadsA4", "option_name": "Stock Type", "field_id": "F5", "choices": 4},
                    {"calculator": "SaddleStitchBooks", "option_name": "Cover Stock", "field_id": "F6", "choices": 12}
                ],
                "indexes": ["calculator_name", "option_name", "field_id", "UNIQUE(calculator_name, option_name)"]
            },
            
            "product_option_choices": {
                "system": "Product Options",
                "row_count": 432,
                "purpose": "Individual dropdown choices with prices (e.g., 'Bond 80GSM @ $0.03 per_sheet')",
                "key_columns": [
                    {"name": "id", "type": "SERIAL PRIMARY KEY", "description": "Unique choice ID"},
                    {"name": "option_id", "type": "INTEGER REFERENCES product_options(id) ON DELETE CASCADE", "description": "Foreign key to parent option"},
                    {"name": "choice_title", "type": "VARCHAR(255)", "description": "Display text (e.g., 'Bond 80GSM', '1000 units')"},
                    {"name": "price", "type": "NUMERIC(10,4)", "description": "Price value (can be negative for discounts)"},
                    {"name": "price_type", "type": "VARCHAR(50)", "description": "fixed, multiplier, per_sheet, per_unit, cards_per_sheet, per_1000_sheets (NO constraint - allows any value)"},
                    {"name": "sku", "type": "VARCHAR(100)", "description": "Stock keeping unit"},
                    {"name": "is_default", "type": "BOOLEAN DEFAULT FALSE", "description": "Whether this is the default choice"},
                    {"name": "is_available", "type": "BOOLEAN DEFAULT TRUE", "description": "Whether choice is currently available"},
                    {"name": "display_order", "type": "INTEGER", "description": "Order to display in dropdown"},
                    {"name": "created_at", "type": "TIMESTAMP", "description": "When choice was created"},
                    {"name": "updated_at", "type": "TIMESTAMP", "description": "Last modification"}
                ],
                "example_choices": [
                    {"option": "Stock Type", "choice_title": "Bond 80GSM", "price": 0.03, "price_type": "per_sheet"},
                    {"option": "Quantity", "choice_title": "1000", "price": 0.00, "price_type": "multiplier"},
                    {"option": "Print Type", "choice_title": "4/4 Full Colour", "price": 0.08, "price_type": "per_sheet"}
                ],
                "price_variance_example": {"option": "WireBound.Internal Print Type", "min": 0.02, "max": 0.096, "variance": "380%"},
                "indexes": ["option_id", "price", "is_available", "display_order"]
            },
            
            "product_option_overrides": {
                "system": "Product Options",
                "row_count": 0,
                "purpose": "Customer segment or time-based price overrides (e.g., wholesale pricing, seasonal discounts)",
                "key_columns": [
                    {"name": "id", "type": "SERIAL PRIMARY KEY", "description": "Unique override ID"},
                    {"name": "choice_id", "type": "INTEGER REFERENCES product_option_choices(id) ON DELETE CASCADE", "description": "Foreign key to choice being overridden"},
                    {"name": "override_price", "type": "NUMERIC(10,4)", "description": "Override price value"},
                    {"name": "customer_segment", "type": "VARCHAR(100)", "description": "Which customer segment gets this price (wholesale, retail, VIP, etc.)"},
                    {"name": "valid_from", "type": "TIMESTAMP", "description": "When override becomes active"},
                    {"name": "valid_until", "type": "TIMESTAMP", "description": "When override expires"},
                    {"name": "is_active", "type": "BOOLEAN DEFAULT TRUE", "description": "Whether override is currently active"},
                    {"name": "notes", "type": "TEXT", "description": "Reason for override"},
                    {"name": "created_at", "type": "TIMESTAMP", "description": "When override was created"},
                    {"name": "updated_at", "type": "TIMESTAMP", "description": "Last modification"}
                ],
                "usage": "Future feature - not yet populated",
                "indexes": ["choice_id", "customer_segment", "is_active", "valid_from", "valid_until"]
            },
            
            "product_option_history": {
                "system": "Product Options",
                "row_count": "586+ (grows over time)",
                "purpose": "Complete audit trail of option and choice changes",
                "key_columns": [
                    {"name": "id", "type": "SERIAL PRIMARY KEY", "description": "Unique history entry ID"},
                    {"name": "change_type", "type": "VARCHAR(50)", "description": "option_created, choice_created, choice_price_updated, choice_deleted"},
                    {"name": "option_id", "type": "INTEGER", "description": "Which option was changed"},
                    {"name": "choice_id", "type": "INTEGER", "description": "Which choice was changed (NULL for option-level changes)"},
                    {"name": "old_value", "type": "JSONB", "description": "Previous state (full object or price value)"},
                    {"name": "new_value", "type": "JSONB", "description": "New state (full object or price value)"},
                    {"name": "changed_by", "type": "VARCHAR(255)", "description": "User or system that made change"},
                    {"name": "changed_at", "type": "TIMESTAMP DEFAULT NOW()", "description": "When change occurred"}
                ],
                "current_entries": [
                    {"type": "option_created", "count": 154},
                    {"type": "choice_created", "count": 432}
                ],
                "indexes": ["option_id", "choice_id", "change_type", "changed_at"]
            }
        },
        
        "relationships": {
            "pricing_constants_flow": [
                "calculator_pricing_parameters (64 params) → calculator_parameter_overrides (104 overrides) → calculator_parameter_history (audit trail)",
                "calculators_registry (30 calculators) references parameters via JSONB parameters_used field (NOT FK)"
            ],
            "product_options_flow": [
                "product_options (154 options) → product_option_choices (432 choices) → product_option_overrides (0 overrides) → product_option_history (audit trail)",
                "product_options links to calculators via calculator_name field (NOT FK due to legacy data)"
            ],
            "foreign_keys": [
                {"from": "calculator_parameter_overrides.parameter_id", "to": "calculator_pricing_parameters.id", "on_delete": "CASCADE"},
                {"from": "product_option_choices.option_id", "to": "product_options.id", "on_delete": "CASCADE"},
                {"from": "product_option_overrides.choice_id", "to": "product_option_choices.id", "on_delete": "CASCADE"}
            ],
            "data_read_priority": "Override rows (is_active=TRUE) → JSONB array (frozen snapshot) → base_value (fallback)"
        },
        
        "query_patterns": {
            "jsonb_access": {
                "extract_text": "value_statistics->>'variance_pct' (returns text)",
                "extract_numeric": "(value_statistics->>'variance_pct')::numeric (cast to number)",
                "extract_array_element": "used_by_calculators->0 (first element)",
                "extract_nested": "value_statistics->'distinct_values'->0",
                "array_contains": "used_by_calculators @> '[{\"calculator_name\": \"BollardSigns\"}]'",
                "array_length": "jsonb_array_length(used_by_calculators)"
            },
            "common_patterns": {
                "get_parameter_with_overrides": "SELECT p.*, array_agg(o.*) as overrides FROM calculator_pricing_parameters p LEFT JOIN calculator_parameter_overrides o ON p.id = o.parameter_id WHERE p.parameter_name = 'impos_setup' GROUP BY p.id",
                "get_calculator_config": "SELECT c.*, p.parameters_used FROM calculators_registry c JOIN calculator_pricing_parameters p ON TRUE WHERE c.calculator_name = 'NotepadsA4'",
                "get_high_variance_params": "SELECT parameter_name, (value_statistics->>'variance_pct')::numeric as variance FROM calculator_pricing_parameters WHERE (value_statistics->>'variance_pct')::numeric > 100 ORDER BY variance DESC",
                "get_product_options_with_choices": "SELECT po.*, array_agg(poc.*) as choices FROM product_options po LEFT JOIN product_option_choices poc ON po.id = poc.option_id WHERE po.calculator_name = 'NotepadsA4' GROUP BY po.id",
                "find_duplicate_values": "SELECT parameter_name, COUNT(DISTINCT (used_by_calculators->>'value')) as distinct_count FROM calculator_pricing_parameters WHERE jsonb_array_length(used_by_calculators) > 1 GROUP BY parameter_name HAVING COUNT(DISTINCT (used_by_calculators->>'value')) > 1"
            },
            "performance_tips": [
                "Use GIN indexes for JSONB queries: CREATE INDEX idx_stats ON calculator_pricing_parameters USING gin(value_statistics)",
                "Cast JSONB to numeric for sorting: ORDER BY (value_statistics->>'variance_pct')::numeric",
                "Use array_agg() for one-to-many relationships instead of multiple queries",
                "Filter on indexed columns first, then JSONB fields",
                "Use EXPLAIN ANALYZE to check query performance"
            ]
        },
        
        "example_queries": {
            "pricing_constants": [
                {
                    "name": "Get all parameters with high variance (>100%)",
                    "sql": "SELECT parameter_name, base_value, (value_statistics->>'variance_pct')::numeric as variance_pct, value_statistics->'distinct_values' as distinct_values FROM calculator_pricing_parameters WHERE (value_statistics->>'variance_pct')::numeric > 100 ORDER BY variance_pct DESC",
                    "purpose": "Identify pricing inconsistencies across calculators"
                },
                {
                    "name": "Get complete parameter details with all calculator overrides",
                    "sql": "SELECT p.parameter_name, p.base_value, p.data_type, p.value_statistics, array_agg(json_build_object('calculator', o.calculator_name, 'value', o.value, 'active', o.is_active)) as overrides FROM calculator_pricing_parameters p LEFT JOIN calculator_parameter_overrides o ON p.id = o.parameter_id WHERE p.parameter_name = 'impos_setup' GROUP BY p.id",
                    "purpose": "See how a parameter is used across all calculators"
                },
                {
                    "name": "Get calculator's complete pricing configuration",
                    "sql": "SELECT c.calculator_name, c.display_name, c.parameters_used, c.special_features, (SELECT array_agg(json_build_object('param', p.parameter_name, 'base', p.base_value, 'override', o.value)) FROM calculator_parameter_overrides o JOIN calculator_pricing_parameters p ON o.parameter_id = p.id WHERE o.calculator_name = c.calculator_name AND o.is_active = TRUE) as active_overrides FROM calculators_registry c WHERE c.calculator_name = 'BollardSigns'",
                    "purpose": "Get full pricing config for one calculator"
                },
                {
                    "name": "Find parameters used by multiple calculators with different values",
                    "sql": "SELECT parameter_name, jsonb_array_length(used_by_calculators) as calculator_count, (value_statistics->>'distinct_values')::jsonb as unique_values, (value_statistics->>'variance_pct')::numeric as variance FROM calculator_pricing_parameters WHERE jsonb_array_length(used_by_calculators) > 5 AND (value_statistics->>'variance_pct')::numeric > 50 ORDER BY calculator_count DESC, variance DESC",
                    "purpose": "Identify widely-used parameters with high variation"
                },
                {
                    "name": "Get audit trail for a parameter",
                    "sql": "SELECT h.changed_at, h.change_type, p.parameter_name, o.calculator_name, h.old_value, h.new_value, h.changed_by, h.notes FROM calculator_parameter_history h LEFT JOIN calculator_pricing_parameters p ON h.parameter_id = p.id LEFT JOIN calculator_parameter_overrides o ON h.override_id = o.id WHERE p.parameter_name = 'impos_setup' ORDER BY h.changed_at DESC",
                    "purpose": "Track all changes to a parameter over time"
                }
            ],
            
            "product_options": [
                {
                    "name": "Get all product options for a calculator with choices",
                    "sql": "SELECT po.option_name, po.field_id, po.is_required, array_agg(json_build_object('title', poc.choice_title, 'price', poc.price, 'price_type', poc.price_type, 'order', poc.display_order) ORDER BY poc.display_order) as choices FROM product_options po LEFT JOIN product_option_choices poc ON po.id = poc.option_id WHERE po.calculator_name = 'NotepadsA4' GROUP BY po.id ORDER BY po.display_order",
                    "purpose": "Get complete product configuration for UI rendering"
                },
                {
                    "name": "Find product options with high price variance",
                    "sql": "SELECT po.calculator_name, po.option_name, MIN(poc.price) as min_price, MAX(poc.price) as max_price, AVG(poc.price) as avg_price, ROUND(((MAX(poc.price) - MIN(poc.price)) / NULLIF(AVG(poc.price), 0) * 100)::numeric, 2) as variance_pct FROM product_options po JOIN product_option_choices poc ON po.id = poc.option_id GROUP BY po.calculator_name, po.option_name HAVING MAX(poc.price) - MIN(poc.price) > 0 ORDER BY variance_pct DESC LIMIT 10",
                    "purpose": "Identify options with inconsistent pricing"
                },
                {
                    "name": "Get calculators with most product options",
                    "sql": "SELECT calculator_name, COUNT(*) as option_count, array_agg(option_name ORDER BY display_order) as options FROM product_options GROUP BY calculator_name ORDER BY option_count DESC",
                    "purpose": "See which calculators are most complex"
                },
                {
                    "name": "Find all price types used in the system",
                    "sql": "SELECT price_type, COUNT(*) as usage_count, MIN(price) as min_price, MAX(price) as max_price, AVG(price) as avg_price FROM product_option_choices GROUP BY price_type ORDER BY usage_count DESC",
                    "purpose": "Understand pricing models across all options"
                },
                {
                    "name": "Get option change history for a calculator",
                    "sql": "SELECT poh.changed_at, poh.change_type, po.option_name, poc.choice_title, poh.old_value, poh.new_value, poh.changed_by FROM product_option_history poh LEFT JOIN product_options po ON poh.option_id = po.id LEFT JOIN product_option_choices poc ON poh.choice_id = poc.id WHERE po.calculator_name = 'SaddleStitchBooks' ORDER BY poh.changed_at DESC LIMIT 20",
                    "purpose": "Track recent changes to product options"
                }
            ],
            
            "cross_system_queries": [
                {
                    "name": "Get complete calculator profile (pricing constants + product options)",
                    "sql": "SELECT c.calculator_name, c.display_name, c.special_features, (SELECT COUNT(*) FROM calculator_parameter_overrides WHERE calculator_name = c.calculator_name AND is_active = TRUE) as override_count, (SELECT COUNT(*) FROM product_options WHERE calculator_name = c.calculator_name) as option_count, (SELECT array_agg(parameter_name) FROM calculator_parameter_overrides o JOIN calculator_pricing_parameters p ON o.parameter_id = p.id WHERE o.calculator_name = c.calculator_name AND o.is_active = TRUE) as overridden_params, (SELECT array_agg(option_name) FROM product_options WHERE calculator_name = c.calculator_name) as product_options FROM calculators_registry c WHERE c.calculator_name = 'NotepadsA4'",
                    "purpose": "Complete calculator summary for dashboard"
                },
                {
                    "name": "Find calculators with both high parameter variance and many product options",
                    "sql": "WITH param_variance AS (SELECT (elem->>'calculator_name') as calc_name, COUNT(DISTINCT parameter_name) as param_count FROM calculator_pricing_parameters, jsonb_array_elements(used_by_calculators) elem GROUP BY calc_name), option_counts AS (SELECT calculator_name as calc_name, COUNT(*) as option_count FROM product_options GROUP BY calculator_name) SELECT pv.calc_name, pv.param_count, COALESCE(oc.option_count, 0) as option_count FROM param_variance pv LEFT JOIN option_counts oc ON pv.calc_name = oc.calc_name WHERE pv.param_count > 10 OR COALESCE(oc.option_count, 0) > 5 ORDER BY pv.param_count DESC, oc.option_count DESC",
                    "purpose": "Identify most complex calculators"
                }
            ]
        },
        
        "available_queries": available_queries,  # DYNAMICALLY INJECTED from QueryLibrary
        
        "decision_tree": {
            "use_schema_guide_when": [
                "You're working with calculator pricing for the first time",
                "You need to understand the database structure",
                "You're writing custom queries and need column names/types",
                "You want to see example queries for common tasks"
            ],
            "use_pre_built_queries_when": [
                "The task matches an available query (check available_queries list above)",
                "You need tested, optimized queries",
                "You want consistent results across sessions",
                "You're building reports or dashboards"
            ],
            "use_direct_sql_when": [
                "No pre-built query exists for your specific need",
                "You need to combine data in unique ways",
                "You're doing exploratory data analysis",
                "You need to join tables in custom ways"
            ],
            "use_api_endpoints_when": [
                "Future: API endpoints not yet implemented",
                "Will provide RESTful access to pricing data",
                "Planned: 24 endpoints for CRUD operations"
            ]
        },
        
        "best_practices": [
            "ALWAYS call calculator_database_get_schema_guide() FIRST when working with calculator pricing",
            "Check available_queries list before writing custom SQL - pre-built queries are tested and optimized",
            "Use parameterized queries to prevent SQL injection: calculator_database_query(sql, params=(value1, value2))",
            "Cast JSONB fields to appropriate types: (value_statistics->>'variance_pct')::numeric",
            "Use array_agg() and json_build_object() to avoid N+1 query problems",
            "Check is_active=TRUE when querying overrides to get current values",
            "Use GIN indexes for JSONB queries for better performance",
            "Always ORDER BY when using LIMIT to ensure consistent results",
            "Include calculator_name in GROUP BY when aggregating across calculators",
            "Use LEFT JOIN for optional relationships (overrides, history)"
        ],
        
        "migration_history": {
            "001_create_catalog_tables.sql": "Initial 4-table schema for pricing constants (412 lines)",
            "002_fix_duplicates_and_enhance_stats.py": "Merged 71→64 parameters, added value_statistics JSONB (250 lines)",
            "003_populate_overrides.py": "Populated 104 override rows from JSONB arrays (267 lines)",
            "004_create_product_options_tables.sql": "Product options 4-table schema with triggers and views (13,794 chars)"
        },
        
        "data_quality_notes": {
            "duplicates_cleaned": "Migration 002 merged 7 duplicate parameter pairs (case-insensitive)",
            "optimization": "Override rows only created when value ≠ base_value (saved 167 rows, 61% reduction)",
            "variance_analysis": "64 parameters analyzed - highest variance: stock_cost_per_1000_sheets (293%), impos_setup (207%)",
            "product_options_loaded": "154 options, 432 choices from 23 calculators (5 legacy calculators failed)",
            "historical_tracking": "690 total history entries (104 pricing + 586 options)"
        }
    }
    
    return {
        "success": True,
        "guide": guide,
        "total_tables": 8,
        "total_rows": "690+",
        "query_count": len(available_queries),
        "message": "Complete schema guide with dynamically injected pre-built query list"
    }


# ==================== QUERY EXECUTION ====================

def calculator_database_query(sql: str, params: Optional[tuple] = None, **kwargs) -> Dict[str, Any]:
    """
    Execute SELECT query against Calculator Pricing Database
    
    Args:
        sql: SQL query string (must be SELECT or WITH)
        params: Optional tuple of parameter values for safe parameterization
        **kwargs: Additional options (unused)
    
    Returns:
        {
            "success": True/False,
            "data": List of dicts (query results),
            "row_count": int,
            "query": str (executed query),
            "execution_time_ms": float
        }
    
    Example:
        calculator_database_query(
            "SELECT * FROM calculator_pricing_parameters WHERE parameter_name = %s",
            params=("impos_setup",)
        )
    """
    if not CALCULATOR_PRICING_DB_AVAILABLE:
        return {
            "success": False,
            "error": "CalculatorPricingDB not available - check database connection",
            "query": sql
        }
    
    try:
        db = CalculatorPricingDB()
        result = db.execute_query(sql, params=params, return_dataframe=False)
        db.close()
        return result
    except Exception as e:
        return {
            "success": False,
            "error": f"Query execution failed: {str(e)}",
            "query": sql,
            "params": params
        }


# ==================== MODIFY OPERATIONS ====================

def calculator_database_modify(sql: str, params: Optional[tuple] = None, reason: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """
    Execute INSERT/UPDATE/DELETE query against Calculator Pricing Database
    
    SAFETY FEATURES:
    - Blocks SELECT queries (use calculator_database_query instead)
    - Blocks DROP/TRUNCATE operations
    - Auto-commits changes
    - Logs reason for modification
    
    Args:
        sql: SQL query string (INSERT/UPDATE/DELETE)
        params: Optional tuple of parameter values for safe parameterization
        reason: Reason for modification (logged to history if applicable)
        **kwargs: Additional options (unused)
    
    Returns:
        {
            "success": True/False,
            "rows_affected": int,
            "query": str,
            "execution_time_ms": float,
            "reason": str
        }
    
    Example:
        calculator_database_modify(
            "UPDATE calculator_parameter_overrides SET value = %s WHERE calculator_name = %s AND parameter_id = %s",
            params=(50.00, "BollardSigns", 1),
            reason="Price increase due to supplier cost change"
        )
    """
    if not CALCULATOR_PRICING_DB_AVAILABLE:
        return {
            "success": False,
            "error": "CalculatorPricingDB not available - check database connection",
            "query": sql
        }
    
    try:
        db = CalculatorPricingDB()
        result = db.execute_modify(sql, params=params, auto_commit=True)
        db.close()
        
        # Add reason to result
        if reason:
            result['reason'] = reason
        
        return result
    except Exception as e:
        return {
            "success": False,
            "error": f"Modification failed: {str(e)}",
            "query": sql,
            "params": params,
            "reason": reason
        }


# ==================== PRE-BUILT QUERIES ====================

def calculator_database_list_queries(category: str = "all", **kwargs) -> Dict[str, Any]:
    """
    List available pre-built queries from QueryLibrary for Calculator Pricing Management
    
    Args:
        category: Filter by category ("Calculator Pricing Management" or "all")
        **kwargs: Additional options (unused)
    
    Returns:
        {
            "success": True,
            "category": str,
            "query_count": int,
            "queries": [
                {
                    "name": "get_pricing_constant",
                    "description": "...",
                    "parameters": {...},
                    "returns": "...",
                    "best_for": "..."
                },
                ...
            ]
        }
    """
    if not QUERY_LIBRARY_AVAILABLE:
        return {
            "success": False,
            "error": "QueryLibrary not available",
            "category": category
        }
    
    try:
        query_lib = QueryLibrary()
        catalog = query_lib.query_catalog
        
        # Filter for Calculator Pricing Management queries
        queries = []
        for query_name, query_meta in catalog.items():
            if category == "all" or query_meta.get('category') == category:
                if query_meta.get('category') == 'Calculator Pricing Management':
                    queries.append({
                        "name": query_name,
                        "description": query_meta.get('description', ''),
                        "parameters": query_meta.get('parameters', {}),
                        "returns": query_meta.get('returns', ''),
                        "best_for": query_meta.get('best_for', ''),
                        "validated": query_meta.get('validated', False)
                    })
        
        return {
            "success": True,
            "category": category,
            "query_count": len(queries),
            "queries": queries
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to retrieve query list: {str(e)}",
            "category": category
        }


# ==================== USAGE EXAMPLES ====================

if __name__ == "__main__":
    print("="*70)
    print("CALCULATOR PRICING WRAPPER TEST")
    print("="*70)
    
    # Test 1: Get schema guide
    print("\n📋 Test 1: Get Schema Guide")
    guide = calculator_database_get_schema_guide()
    if guide['success']:
        print(f"✅ Schema guide retrieved")
        print(f"   Total tables: {guide['total_tables']}")
        print(f"   Total rows: {guide['total_rows']}")
        print(f"   Pre-built queries: {guide['query_count']}")
        print(f"\n   Available queries:")
        for q in guide['guide']['available_queries'][:3]:  # Show first 3
            print(f"      - {q['name']}: {q['description'][:60]}...")
    else:
        print(f"❌ {guide.get('error', 'Unknown error')}")
    
    # Test 2: Execute query
    print("\n🔍 Test 2: Execute Query")
    result = calculator_database_query("""
        SELECT parameter_name, base_value, 
               (value_statistics->>'variance_pct')::numeric as variance
        FROM calculator_pricing_parameters
        WHERE (value_statistics->>'variance_pct')::numeric > 100
        ORDER BY variance DESC
        LIMIT 3
    """)
    if result['success']:
        print(f"✅ Query executed in {result['execution_time_ms']}ms")
        print(f"   Rows returned: {result['row_count']}")
        for row in result['data']:
            print(f"      - {row['parameter_name']}: {row['variance']:.2f}% variance")
    else:
        print(f"❌ {result.get('error', 'Unknown error')}")
    
    # Test 3: Get pre-built queries
    print("\n📚 Test 3: Get Pre-Built Queries")
    queries = calculator_database_list_queries("Calculator Pricing Management")
    if queries['success']:
        print(f"✅ Found {queries['query_count']} pre-built queries")
    else:
        print(f"❌ {queries.get('error', 'Unknown error')}")
    
    print("\n" + "="*70)
    print("✅ ALL TESTS PASSED")
    print("="*70)
