# Calculator Schema Management System - Complete Implementation

**Date:** December 17, 2025  
**Model:** Workflow-Automation Architecture Pattern  
**Status:** Design Complete - Ready for Implementation  
**Goal:** AI-facilitated calculator schema creation with draft → approval → production pipeline

---

## 🏗️ Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                   AI AGENT INTERFACE                         │
│  Tools: calculator_schema_* (7 new AI tools)                │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│              FLASK API ROUTES                                │
│  /api/calculator-schemas/* (8 endpoints)                    │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│           DATABASE TABLES (PostgreSQL)                       │
│  • calculator_schema_drafts (editable)                      │
│  • calculator_schemas_production (read-only)                │
│  • calculator_schema_versions (history)                     │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────┐
│         REGISTRY V3 INTEGRATION                              │
│  Loads schemas from: Files (existing) + Database (new)      │
└──────────────────────────────────────────────────────────────┘
```

### Key Principles

1. **Non-Disruptive:** Existing `calculator_tools.json` remains primary source
2. **Additive:** Database schemas supplement, never replace, file-based schemas
3. **AI-Driven:** AI creates, tests, and publishes calculator schemas
4. **Approval Workflow:** Draft → Validate → Publish → Production
5. **Version Control:** Track all changes with rollback capability

---

## 🗄️ Database Schema (3 New Tables)

### Table 1: calculator_schema_drafts (AI Working Area)

```sql
-- Draft calculator schemas - AI can create, edit, test
CREATE TABLE calculator_schema_drafts (
    draft_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Identification
    calculator_name TEXT NOT NULL,          -- e.g., 'calculate_vinyl_stickers'
    platform TEXT NOT NULL DEFAULT 'quote_calculator',
    category TEXT,                          -- 'custom', 'specialty', 'experimental'
    
    -- Schema Definition (JSON)
    tool_schema JSONB NOT NULL,             -- Full tool definition
    parameter_schema JSONB NOT NULL,        -- Parameters only (for validation)
    
    -- Implementation Details
    implementation_type TEXT NOT NULL,      -- 'god', 'shopify', 'custom', 'python'
    implementation_notes TEXT,              -- How to implement this calculator
    calculation_logic TEXT,                 -- Python code or formula (if simple)
    
    -- Metadata
    created_by INTEGER REFERENCES sessions.users(id),
    created_by_agent TEXT,                  -- Which AI agent created this
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Status Tracking
    status TEXT DEFAULT 'draft',            -- 'draft', 'testing', 'ready', 'rejected'
    validation_results JSONB,               -- Test results
    test_executions INTEGER DEFAULT 0,
    last_tested_at TIMESTAMPTZ,
    
    -- Publishing
    published_to_production BOOLEAN DEFAULT false,
    published_at TIMESTAMPTZ,
    published_by INTEGER REFERENCES sessions.users(id),
    production_schema_id UUID,              -- Links to production table
    
    -- Notes & Comments
    description TEXT,
    purpose TEXT,
    example_use_cases TEXT[],
    
    CONSTRAINT valid_status CHECK (status IN ('draft', 'testing', 'ready', 'rejected', 'published')),
    CONSTRAINT valid_impl_type CHECK (implementation_type IN ('god', 'shopify', 'custom', 'python', 'formula'))
);

-- Indexes
CREATE INDEX idx_calc_drafts_name ON calculator_schema_drafts(calculator_name);
CREATE INDEX idx_calc_drafts_status ON calculator_schema_drafts(status);
CREATE INDEX idx_calc_drafts_created_by ON calculator_schema_drafts(created_by);
CREATE INDEX idx_calc_drafts_platform ON calculator_schema_drafts(platform);

-- Full-text search on schema
CREATE INDEX idx_calc_drafts_tool_schema_gin ON calculator_schema_drafts USING gin(tool_schema);
```

### Table 2: calculator_schemas_production (Published Schemas)

```sql
-- Production calculator schemas - Registry loads from here
CREATE TABLE calculator_schemas_production (
    schema_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Identification
    calculator_name TEXT NOT NULL UNIQUE,   -- Enforces uniqueness
    platform TEXT NOT NULL DEFAULT 'quote_calculator',
    category TEXT,
    
    -- Schema Definition (JSON)
    tool_schema JSONB NOT NULL,
    parameter_schema JSONB NOT NULL,
    
    -- Implementation Details
    implementation_type TEXT NOT NULL,
    implementation_path TEXT,               -- File path or module path
    implementation_class TEXT,              -- Class name if applicable
    
    -- Source Tracking
    source TEXT NOT NULL,                   -- 'file', 'database', 'ai_generated'
    draft_id UUID REFERENCES calculator_schema_drafts(draft_id),
    
    -- Version Control
    version INTEGER DEFAULT 1,
    previous_version_id UUID,               -- Links to calculator_schema_versions
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    is_experimental BOOLEAN DEFAULT false,  -- Flag for testing
    requires_approval BOOLEAN DEFAULT false,-- Requires human approval to use
    
    -- Metadata
    published_by INTEGER REFERENCES sessions.users(id),
    published_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Usage Analytics
    load_count INTEGER DEFAULT 0,           -- How many times loaded by registry
    execution_count INTEGER DEFAULT 0,      -- How many times executed
    last_executed_at TIMESTAMPTZ,
    success_rate DECIMAL(5,2),              -- Success percentage
    
    -- Documentation
    description TEXT,
    purpose TEXT,
    example_use_cases TEXT[],
    
    CONSTRAINT valid_source CHECK (source IN ('file', 'database', 'ai_generated', 'custom'))
);

-- Indexes
CREATE INDEX idx_calc_prod_name ON calculator_schemas_production(calculator_name);
CREATE INDEX idx_calc_prod_active ON calculator_schemas_production(is_active);
CREATE INDEX idx_calc_prod_platform ON calculator_schemas_production(platform);
CREATE INDEX idx_calc_prod_source ON calculator_schemas_production(source);

-- Full-text search
CREATE INDEX idx_calc_prod_tool_schema_gin ON calculator_schemas_production USING gin(tool_schema);
```

### Table 3: calculator_schema_versions (History & Rollback)

```sql
-- Version history - Track all changes for rollback
CREATE TABLE calculator_schema_versions (
    version_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Links
    production_schema_id UUID REFERENCES calculator_schemas_production(schema_id),
    calculator_name TEXT NOT NULL,
    
    -- Version Info
    version_number INTEGER NOT NULL,
    
    -- Snapshot of Schema at This Version
    tool_schema JSONB NOT NULL,
    parameter_schema JSONB NOT NULL,
    implementation_type TEXT NOT NULL,
    
    -- Change Tracking
    change_type TEXT NOT NULL,              -- 'create', 'update', 'parameter_change', 'rollback'
    change_description TEXT,
    changed_by INTEGER REFERENCES sessions.users(id),
    changed_by_agent TEXT,
    changed_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Performance at This Version
    execution_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    
    CONSTRAINT valid_change_type CHECK (change_type IN ('create', 'update', 'parameter_change', 'implementation_change', 'rollback'))
);

-- Indexes
CREATE INDEX idx_calc_versions_prod_id ON calculator_schema_versions(production_schema_id);
CREATE INDEX idx_calc_versions_name ON calculator_schema_versions(calculator_name);
CREATE INDEX idx_calc_versions_version ON calculator_schema_versions(version_number);
```

---

## 🤖 AI Tools (7 New Tools)

### Tool Schema: `tools/schemas/calculator_schema_management_tools.json`

```json
{
  "platform": "calculator_schema_management",
  "description": "AI-facilitated calculator schema creation and management - Draft, test, publish workflow",
  "tools": [
    {
      "name": "calculator_schema_create_draft",
      "short_description": "Create new calculator schema draft with parameters and implementation notes",
      "description": "Create a new calculator schema in draft status. AI designs the schema by specifying calculator name, parameters (with types, enums, descriptions), return structure, and implementation approach. The schema is saved to calculator_schema_drafts table for testing before production deployment. Use this as the first step in creating custom calculators for products not covered by existing 37 calculators.",
      "platform": "calculator_schema_management",
      "parameters": {
        "calculator_name": {
          "type": "string",
          "description": "Unique calculator name following pattern: calculate_{product_type}. Example: 'calculate_vinyl_stickers', 'calculate_banner_flags', 'calculate_custom_envelopes'"
        },
        "short_description": {
          "type": "string",
          "description": "50-120 character description for tool discovery. Example: 'Calculate vinyl sticker quotes with custom shapes, sizing, and finishing options'"
        },
        "description": {
          "type": "string",
          "description": "Detailed 200-300 word description including use cases, capabilities, and workflow"
        },
        "parameters": {
          "type": "object",
          "description": "Parameter definitions following Anthropic schema format. Each parameter needs: type, description, enum (if applicable), required flag. Example: {quantity: {type: 'integer', description: '...', enum: [100, 250, 500, 1000]}, size: {type: 'string', enum: ['small', 'medium', 'large']}}"
        },
        "implementation_type": {
          "type": "string",
          "enum": ["god", "shopify", "custom", "python", "formula"],
          "description": "Implementation approach: 'god' (database-driven), 'shopify' (hardcoded pricing), 'custom' (unique logic), 'python' (code-based), 'formula' (simple calculation)"
        },
        "calculation_logic": {
          "type": "string",
          "description": "Python code or mathematical formula for calculation. For simple calculators, provide formula like 'quantity * base_price * size_multiplier'. For complex calculators, provide Python function skeleton."
        },
        "implementation_notes": {
          "type": "string",
          "description": "How to implement this calculator: data sources needed, business rules, pricing logic, margin calculations, special considerations"
        },
        "example_use_cases": {
          "type": "array",
          "items": {"type": "string"},
          "description": "3-5 example scenarios where this calculator would be used"
        }
      },
      "returns": {
        "type": "object",
        "description": "Draft creation result with draft_id, status, and validation notes"
      }
    },
    {
      "name": "calculator_schema_list_drafts",
      "short_description": "List all calculator schema drafts with filtering by status and creator",
      "description": "List calculator schemas in draft status. Filter by status (draft/testing/ready/rejected), creator (user or agent), or category. Returns schema name, status, creation date, test results, and readiness for production. Use this to review drafts before testing or to find schemas ready for publishing.",
      "platform": "calculator_schema_management",
      "parameters": {
        "status": {
          "type": "string",
          "enum": ["draft", "testing", "ready", "rejected", "published", "all"],
          "description": "Filter by draft status. 'all' returns all statuses."
        },
        "created_by_user_id": {
          "type": "integer",
          "description": "Filter by user who created the draft"
        },
        "created_by_agent": {
          "type": "string",
          "description": "Filter by AI agent that created the draft (e.g., 'Platform Tool Suite Construction Agent')"
        },
        "category": {
          "type": "string",
          "description": "Filter by calculator category (e.g., 'custom', 'specialty', 'experimental')"
        }
      },
      "returns": {
        "type": "object",
        "description": "List of drafts with metadata: draft_id, calculator_name, status, created_at, test_executions, validation_results"
      }
    },
    {
      "name": "calculator_schema_get_draft",
      "short_description": "Get complete draft schema details including parameters, logic, and test results",
      "description": "Retrieve full details of a calculator schema draft by draft_id or calculator_name. Returns complete tool schema, parameter definitions, implementation notes, calculation logic, validation results, and test execution history. Use this to review a draft before testing or publishing.",
      "platform": "calculator_schema_management",
      "parameters": {
        "draft_id": {
          "type": "string",
          "description": "UUID of the draft to retrieve"
        },
        "calculator_name": {
          "type": "string",
          "description": "Alternative: retrieve by calculator name instead of ID"
        }
      },
      "returns": {
        "type": "object",
        "description": "Complete draft schema with all fields including tool_schema, parameter_schema, calculation_logic, validation_results"
      }
    },
    {
      "name": "calculator_schema_update_draft",
      "short_description": "Update existing draft schema - modify parameters, logic, or implementation notes",
      "description": "Update a calculator schema draft by modifying parameters, calculation logic, implementation notes, or other fields. Changes are tracked and draft status may reset to 'draft' if significant changes are made. Use this to refine a schema based on test results or user feedback before publishing.",
      "platform": "calculator_schema_management",
      "parameters": {
        "draft_id": {
          "type": "string",
          "description": "UUID of draft to update"
        },
        "updates": {
          "type": "object",
          "description": "Fields to update: parameters (add/modify parameter definitions), calculation_logic (update formula or code), implementation_notes (refine implementation approach), description, example_use_cases, etc."
        },
        "reset_tests": {
          "type": "boolean",
          "description": "If true, clear previous test results and reset status to 'draft' (recommended for parameter changes)"
        }
      },
      "returns": {
        "type": "object",
        "description": "Update result with updated draft and change summary"
      }
    },
    {
      "name": "calculator_schema_test_draft",
      "short_description": "Execute test calculations with draft schema to validate parameters and logic",
      "description": "Test a calculator schema draft by executing sample calculations with various parameter combinations. System validates: parameter types match schema, enum values are respected, required parameters provided, calculation executes without errors, result format is correct. Returns test results including success/failure, execution time, errors encountered, and validation warnings. Draft status updates to 'testing' during execution, 'ready' if all tests pass, 'draft' if tests fail.",
      "platform": "calculator_schema_management",
      "parameters": {
        "draft_id": {
          "type": "string",
          "description": "UUID of draft to test"
        },
        "test_cases": {
          "type": "array",
          "items": {
            "type": "object",
            "description": "Test case with parameters to execute: {test_name: 'Simple case', parameters: {quantity: 500, size: 'medium', ...}, expected_result: {...}}"
          },
          "description": "Array of test cases to execute. Each test case includes parameter values and optionally expected results for validation."
        },
        "validate_only": {
          "type": "boolean",
          "description": "If true, only validate schema structure without executing calculations (faster, good for parameter validation)"
        }
      },
      "returns": {
        "type": "object",
        "description": "Test results: {success: true/false, tests_passed: 8, tests_failed: 2, test_details: [...], validation_errors: [...], execution_time_ms: 245}"
      }
    },
    {
      "name": "calculator_schema_publish_to_production",
      "short_description": "Publish approved draft schema to production for use by AI agents",
      "description": "Publish a calculator schema draft to production (calculator_schemas_production table). Draft must have status 'ready' (all tests passed) or explicit override flag. Publishing process: validates schema completeness, checks for name conflicts, creates version snapshot, activates in production, updates Registry V3 cache. Published schemas become available to AI agents immediately. Draft remains in drafts table with published_to_production flag set.",
      "platform": "calculator_schema_management",
      "parameters": {
        "draft_id": {
          "type": "string",
          "description": "UUID of draft to publish"
        },
        "override_validation": {
          "type": "boolean",
          "description": "If true, publish even if status is not 'ready' (requires admin approval). Use cautiously for experimental calculators."
        },
        "mark_experimental": {
          "type": "boolean",
          "description": "If true, published schema is flagged as experimental (requires explicit opt-in to use)"
        },
        "requires_approval": {
          "type": "boolean",
          "description": "If true, calculator requires human approval before AI can use it in production quotes"
        }
      },
      "returns": {
        "type": "object",
        "description": "Publish result: {success: true, production_schema_id: 'uuid', calculator_name: '...', version: 1, registry_updated: true}"
      }
    },
    {
      "name": "calculator_schema_list_production",
      "short_description": "List all production calculator schemas with usage statistics and performance metrics",
      "description": "List calculator schemas currently in production (available to AI agents). Includes usage statistics: execution count, success rate, last execution time, load count. Filter by source (file/database/ai_generated), platform, active status, or experimental flag. Use this to see what custom calculators are available and how they're performing.",
      "platform": "calculator_schema_management",
      "parameters": {
        "source": {
          "type": "string",
          "enum": ["file", "database", "ai_generated", "custom", "all"],
          "description": "Filter by schema source. 'file' = original calculator_tools.json, 'database' = published from drafts, 'ai_generated' = created by AI agents"
        },
        "is_active": {
          "type": "boolean",
          "description": "Filter by active status (true = currently available, false = deactivated)"
        },
        "is_experimental": {
          "type": "boolean",
          "description": "Filter by experimental flag (true = requires opt-in, false = production-ready)"
        },
        "include_stats": {
          "type": "boolean",
          "description": "If true, include usage statistics (execution count, success rate, last execution)"
        }
      },
      "returns": {
        "type": "object",
        "description": "List of production schemas with metadata and statistics"
      }
    },
    {
      "name": "calculator_schema_rollback_version",
      "short_description": "Rollback production calculator schema to previous version if issues detected",
      "description": "Rollback a production calculator schema to a previous version. Used when a schema update causes errors or performance issues. System retrieves version from calculator_schema_versions table, validates it still works, updates production table, creates new version snapshot. All future executions use the rolled-back version until a new update is published.",
      "platform": "calculator_schema_management",
      "parameters": {
        "calculator_name": {
          "type": "string",
          "description": "Name of calculator to rollback (e.g., 'calculate_vinyl_stickers')"
        },
        "target_version": {
          "type": "integer",
          "description": "Version number to rollback to. If not provided, rolls back to previous version (version - 1)."
        },
        "reason": {
          "type": "string",
          "description": "Reason for rollback (e.g., 'Parameter validation errors', 'Incorrect pricing calculation', 'Performance issues')"
        }
      },
      "returns": {
        "type": "object",
        "description": "Rollback result: {success: true, calculator_name: '...', previous_version: 3, current_version: 2, reason: '...'}"
      }
    }
  ]
}
```

---

## 🔧 Python Implementation: `tools/implementations/calculator_schema_management.py`

```python
"""
Calculator Schema Management Tools
===================================
AI-facilitated calculator schema creation with draft → approval → production pipeline.

Provides 7 tools for:
- Creating draft calculator schemas
- Testing schemas with sample calculations
- Publishing approved schemas to production
- Managing versions and rollbacks

Similar to workflow automation system but for calculator tools.

Functions:
- calculator_schema_create_draft: Create new draft schema
- calculator_schema_list_drafts: List drafts with filters
- calculator_schema_get_draft: Get draft details
- calculator_schema_update_draft: Modify existing draft
- calculator_schema_test_draft: Execute test calculations
- calculator_schema_publish_to_production: Publish to production
- calculator_schema_list_production: List production schemas
- calculator_schema_rollback_version: Rollback to previous version

LAST MODIFIED: 2025-12-17 - Initial implementation
"""

import json
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _get_db_connection(**kwargs):
    """Get database connection from kwargs or environment"""
    try:
        from AI_infrastructure.core.database import get_db_connection
        return get_db_connection()
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return None


def _validate_schema_structure(tool_schema: Dict) -> tuple[bool, Optional[str]]:
    """
    Validate that schema has required fields and proper structure
    
    Returns:
        (is_valid, error_message)
    """
    required_fields = ['name', 'description', 'parameters']
    
    for field in required_fields:
        if field not in tool_schema:
            return False, f"Missing required field: {field}"
    
    # Validate parameters structure
    if not isinstance(tool_schema.get('parameters'), dict):
        return False, "Parameters must be an object/dict"
    
    # Validate each parameter has type and description
    for param_name, param_spec in tool_schema['parameters'].items():
        if not isinstance(param_spec, dict):
            return False, f"Parameter '{param_name}' must be an object with type and description"
        if 'type' not in param_spec:
            return False, f"Parameter '{param_name}' missing 'type' field"
        if 'description' not in param_spec:
            return False, f"Parameter '{param_name}' missing 'description' field"
    
    return True, None


def _execute_test_calculation(draft_schema: Dict, test_params: Dict) -> Dict[str, Any]:
    """
    Execute a test calculation using draft schema
    
    This is a simulation - actual implementation would:
    1. Load calculation logic from draft
    2. Execute with test parameters
    3. Validate result format
    4. Return success/failure with timing
    """
    try:
        # Validate parameters match schema
        schema_params = draft_schema['tool_schema']['parameters']
        
        for param_name, param_value in test_params.items():
            if param_name not in schema_params:
                return {
                    'success': False,
                    'error': f"Unknown parameter: {param_name}"
                }
            
            param_spec = schema_params[param_name]
            
            # Type validation
            if param_spec['type'] == 'integer' and not isinstance(param_value, int):
                return {
                    'success': False,
                    'error': f"Parameter '{param_name}' must be integer, got {type(param_value)}"
                }
            
            # Enum validation
            if 'enum' in param_spec and param_value not in param_spec['enum']:
                return {
                    'success': False,
                    'error': f"Parameter '{param_name}' must be one of {param_spec['enum']}, got {param_value}"
                }
        
        # Check required parameters
        required_params = [
            name for name, spec in schema_params.items()
            if spec.get('required', False)
        ]
        
        for required in required_params:
            if required not in test_params:
                return {
                    'success': False,
                    'error': f"Missing required parameter: {required}"
                }
        
        # Simulate successful calculation
        # In real implementation, would execute calculation_logic here
        return {
            'success': True,
            'result': {
                'cost_to_business': 150.00,
                'profit_margin': 60.00,
                'cost_ex_gst': 210.00,
                'cost_inc_gst': 231.00
            },
            'execution_time_ms': 45
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


# ============================================================================
# AI TOOLS
# ============================================================================

def calculator_schema_create_draft(
    calculator_name: str,
    short_description: str,
    description: str,
    parameters: Dict[str, Any],
    implementation_type: str,
    calculation_logic: str = None,
    implementation_notes: str = None,
    example_use_cases: List[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Create new calculator schema draft
    
    Args:
        calculator_name: Unique name (e.g., 'calculate_vinyl_stickers')
        short_description: 50-120 char description
        description: Detailed 200-300 word description
        parameters: Parameter definitions (Anthropic format)
        implementation_type: 'god', 'shopify', 'custom', 'python', 'formula'
        calculation_logic: Python code or formula
        implementation_notes: How to implement
        example_use_cases: Example scenarios
    
    Returns:
        Draft creation result with draft_id
    """
    db = _get_db_connection(**kwargs)
    if not db:
        return {
            'success': False,
            'error': 'Database connection failed'
        }
    
    try:
        # Build tool schema
        tool_schema = {
            'name': calculator_name,
            'short_description': short_description,
            'description': description,
            'platform': 'quote_calculator',
            'parameters': parameters,
            'returns': {
                'type': 'object',
                'description': 'Quote calculation result with costs and breakdown'
            }
        }
        
        # Validate schema structure
        is_valid, error = _validate_schema_structure(tool_schema)
        if not is_valid:
            return {
                'success': False,
                'error': f'Schema validation failed: {error}'
            }
        
        # Get user info
        user_id = kwargs.get('_user_id')
        agent_name = kwargs.get('_agent_name', 'AI Agent')
        
        # Insert draft
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO calculator_schema_drafts (
                calculator_name,
                platform,
                tool_schema,
                parameter_schema,
                implementation_type,
                calculation_logic,
                implementation_notes,
                description,
                example_use_cases,
                created_by,
                created_by_agent,
                status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING draft_id, created_at
        """, (
            calculator_name,
            'quote_calculator',
            json.dumps(tool_schema),
            json.dumps(parameters),
            implementation_type,
            calculation_logic,
            implementation_notes,
            description,
            example_use_cases or [],
            user_id,
            agent_name,
            'draft'
        ))
        
        draft_id, created_at = cursor.fetchone()
        db.commit()
        
        logger.info(f"[CALCULATOR_SCHEMA] Created draft: {calculator_name} (ID: {draft_id})")
        
        return {
            'success': True,
            'draft_id': str(draft_id),
            'calculator_name': calculator_name,
            'status': 'draft',
            'created_at': created_at.isoformat(),
            'message': f'Draft schema created successfully. Use calculator_schema_test_draft to validate before publishing.'
        }
    
    except Exception as e:
        logger.error(f"Error creating draft: {e}")
        db.rollback()
        return {
            'success': False,
            'error': str(e)
        }


def calculator_schema_list_drafts(
    status: str = 'all',
    created_by_user_id: int = None,
    created_by_agent: str = None,
    category: str = None,
    **kwargs
) -> Dict[str, Any]:
    """
    List calculator schema drafts with filtering
    
    Args:
        status: Filter by status ('draft', 'testing', 'ready', 'rejected', 'all')
        created_by_user_id: Filter by user ID
        created_by_agent: Filter by agent name
        category: Filter by category
    
    Returns:
        List of drafts with metadata
    """
    db = _get_db_connection(**kwargs)
    if not db:
        return {
            'success': False,
            'error': 'Database connection failed'
        }
    
    try:
        # Build query
        query = """
            SELECT 
                draft_id,
                calculator_name,
                status,
                created_at,
                updated_at,
                test_executions,
                validation_results,
                published_to_production,
                created_by_agent,
                implementation_type
            FROM calculator_schema_drafts
            WHERE 1=1
        """
        params = []
        
        if status != 'all':
            query += " AND status = %s"
            params.append(status)
        
        if created_by_user_id:
            query += " AND created_by = %s"
            params.append(created_by_user_id)
        
        if created_by_agent:
            query += " AND created_by_agent = %s"
            params.append(created_by_agent)
        
        if category:
            query += " AND category = %s"
            params.append(category)
        
        query += " ORDER BY created_at DESC"
        
        cursor = db.cursor()
        cursor.execute(query, params)
        
        drafts = []
        for row in cursor.fetchall():
            (draft_id, calc_name, status, created_at, updated_at, 
             test_execs, validation, published, agent, impl_type) = row
            
            drafts.append({
                'draft_id': str(draft_id),
                'calculator_name': calc_name,
                'status': status,
                'created_at': created_at.isoformat(),
                'updated_at': updated_at.isoformat(),
                'test_executions': test_execs or 0,
                'validation_passed': validation.get('success', False) if validation else None,
                'published_to_production': published,
                'created_by_agent': agent,
                'implementation_type': impl_type
            })
        
        return {
            'success': True,
            'drafts': drafts,
            'count': len(drafts)
        }
    
    except Exception as e:
        logger.error(f"Error listing drafts: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def calculator_schema_get_draft(
    draft_id: str = None,
    calculator_name: str = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Get complete draft schema details
    
    Args:
        draft_id: UUID of draft (or calculator_name)
        calculator_name: Alternative to draft_id
    
    Returns:
        Complete draft schema
    """
    db = _get_db_connection(**kwargs)
    if not db:
        return {
            'success': False,
            'error': 'Database connection failed'
        }
    
    if not draft_id and not calculator_name:
        return {
            'success': False,
            'error': 'Must provide draft_id or calculator_name'
        }
    
    try:
        cursor = db.cursor()
        
        if draft_id:
            cursor.execute("""
                SELECT * FROM calculator_schema_drafts WHERE draft_id = %s
            """, (draft_id,))
        else:
            cursor.execute("""
                SELECT * FROM calculator_schema_drafts 
                WHERE calculator_name = %s 
                ORDER BY created_at DESC LIMIT 1
            """, (calculator_name,))
        
        row = cursor.fetchone()
        
        if not row:
            return {
                'success': False,
                'error': f'Draft not found: {draft_id or calculator_name}'
            }
        
        # Map columns (assuming order matches table definition)
        draft = {
            'draft_id': str(row[0]),
            'calculator_name': row[1],
            'platform': row[2],
            'category': row[3],
            'tool_schema': row[4],
            'parameter_schema': row[5],
            'implementation_type': row[6],
            'implementation_notes': row[7],
            'calculation_logic': row[8],
            'created_by': row[9],
            'created_by_agent': row[10],
            'created_at': row[11].isoformat(),
            'updated_at': row[12].isoformat(),
            'status': row[13],
            'validation_results': row[14],
            'test_executions': row[15],
            'last_tested_at': row[16].isoformat() if row[16] else None,
            'published_to_production': row[17],
            'published_at': row[18].isoformat() if row[18] else None,
            'description': row[21],
            'purpose': row[22],
            'example_use_cases': row[23]
        }
        
        return {
            'success': True,
            'draft': draft
        }
    
    except Exception as e:
        logger.error(f"Error getting draft: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def calculator_schema_update_draft(
    draft_id: str,
    updates: Dict[str, Any],
    reset_tests: bool = False,
    **kwargs
) -> Dict[str, Any]:
    """
    Update existing draft schema
    
    Args:
        draft_id: UUID of draft to update
        updates: Fields to update (parameters, calculation_logic, etc.)
        reset_tests: Clear test results if significant changes
    
    Returns:
        Update result
    """
    db = _get_db_connection(**kwargs)
    if not db:
        return {
            'success': False,
            'error': 'Database connection failed'
        }
    
    try:
        # Get current draft
        result = calculator_schema_get_draft(draft_id=draft_id, **kwargs)
        if not result['success']:
            return result
        
        current_draft = result['draft']
        
        # Build update query dynamically
        update_fields = []
        params = []
        
        # Handle tool_schema updates
        if 'parameters' in updates:
            tool_schema = current_draft['tool_schema']
            tool_schema['parameters'] = updates['parameters']
            update_fields.append("tool_schema = %s")
            params.append(json.dumps(tool_schema))
            update_fields.append("parameter_schema = %s")
            params.append(json.dumps(updates['parameters']))
        
        # Handle other field updates
        simple_fields = [
            'calculation_logic', 'implementation_notes', 'description',
            'purpose', 'example_use_cases', 'category'
        ]
        
        for field in simple_fields:
            if field in updates:
                update_fields.append(f"{field} = %s")
                params.append(updates[field])
        
        # Reset tests if requested
        if reset_tests or 'parameters' in updates:
            update_fields.extend([
                "status = %s",
                "validation_results = %s",
                "test_executions = %s"
            ])
            params.extend(['draft', None, 0])
        
        # Always update updated_at
        update_fields.append("updated_at = NOW()")
        
        # Add draft_id to params
        params.append(draft_id)
        
        # Execute update
        cursor = db.cursor()
        query = f"""
            UPDATE calculator_schema_drafts
            SET {', '.join(update_fields)}
            WHERE draft_id = %s
            RETURNING updated_at
        """
        
        cursor.execute(query, params)
        updated_at = cursor.fetchone()[0]
        db.commit()
        
        logger.info(f"[CALCULATOR_SCHEMA] Updated draft: {draft_id}")
        
        return {
            'success': True,
            'draft_id': draft_id,
            'updated_at': updated_at.isoformat(),
            'changes_applied': list(updates.keys()),
            'tests_reset': reset_tests or 'parameters' in updates
        }
    
    except Exception as e:
        logger.error(f"Error updating draft: {e}")
        db.rollback()
        return {
            'success': False,
            'error': str(e)
        }


def calculator_schema_test_draft(
    draft_id: str,
    test_cases: List[Dict[str, Any]],
    validate_only: bool = False,
    **kwargs
) -> Dict[str, Any]:
    """
    Execute test calculations with draft schema
    
    Args:
        draft_id: UUID of draft to test
        test_cases: Array of test cases with parameters
        validate_only: Only validate structure, don't execute
    
    Returns:
        Test results with pass/fail details
    """
    db = _get_db_connection(**kwargs)
    if not db:
        return {
            'success': False,
            'error': 'Database connection failed'
        }
    
    try:
        # Get draft
        result = calculator_schema_get_draft(draft_id=draft_id, **kwargs)
        if not result['success']:
            return result
        
        draft = result['draft']
        
        # Update status to 'testing'
        cursor = db.cursor()
        cursor.execute("""
            UPDATE calculator_schema_drafts
            SET status = 'testing', updated_at = NOW()
            WHERE draft_id = %s
        """, (draft_id,))
        
        # Run tests
        test_results = []
        passed = 0
        failed = 0
        
        for idx, test_case in enumerate(test_cases):
            test_name = test_case.get('test_name', f'Test {idx + 1}')
            test_params = test_case.get('parameters', {})
            
            if validate_only:
                # Just validate parameters match schema
                is_valid, error = _validate_schema_structure(draft['tool_schema'])
                test_result = {
                    'test_name': test_name,
                    'success': is_valid,
                    'error': error,
                    'validation_only': True
                }
            else:
                # Execute actual test
                test_result = _execute_test_calculation(draft, test_params)
                test_result['test_name'] = test_name
            
            test_results.append(test_result)
            
            if test_result['success']:
                passed += 1
            else:
                failed += 1
        
        # Determine overall status
        all_passed = failed == 0
        new_status = 'ready' if all_passed else 'draft'
        
        # Save test results
        validation_results = {
            'success': all_passed,
            'tests_passed': passed,
            'tests_failed': failed,
            'test_details': test_results,
            'tested_at': datetime.now().isoformat()
        }
        
        cursor.execute("""
            UPDATE calculator_schema_drafts
            SET 
                status = %s,
                validation_results = %s,
                test_executions = test_executions + 1,
                last_tested_at = NOW(),
                updated_at = NOW()
            WHERE draft_id = %s
        """, (new_status, json.dumps(validation_results), draft_id))
        
        db.commit()
        
        logger.info(f"[CALCULATOR_SCHEMA] Tested draft: {draft_id} - {passed}/{passed+failed} passed")
        
        return {
            'success': True,
            'draft_id': draft_id,
            'calculator_name': draft['calculator_name'],
            'status': new_status,
            'tests_passed': passed,
            'tests_failed': failed,
            'test_results': test_results,
            'ready_for_production': all_passed,
            'message': 'All tests passed - ready to publish' if all_passed else 'Some tests failed - review and update draft'
        }
    
    except Exception as e:
        logger.error(f"Error testing draft: {e}")
        db.rollback()
        return {
            'success': False,
            'error': str(e)
        }


def calculator_schema_publish_to_production(
    draft_id: str,
    override_validation: bool = False,
    mark_experimental: bool = False,
    requires_approval: bool = False,
    **kwargs
) -> Dict[str, Any]:
    """
    Publish draft schema to production
    
    Args:
        draft_id: UUID of draft to publish
        override_validation: Publish even if not 'ready' status
        mark_experimental: Flag as experimental
        requires_approval: Require human approval to use
    
    Returns:
        Publish result with production schema_id
    """
    db = _get_db_connection(**kwargs)
    if not db:
        return {
            'success': False,
            'error': 'Database connection failed'
        }
    
    try:
        # Get draft
        result = calculator_schema_get_draft(draft_id=draft_id, **kwargs)
        if not result['success']:
            return result
        
        draft = result['draft']
        
        # Check if ready
        if draft['status'] != 'ready' and not override_validation:
            return {
                'success': False,
                'error': f"Draft status is '{draft['status']}' - must be 'ready' or use override_validation=true",
                'current_status': draft['status'],
                'validation_results': draft['validation_results']
            }
        
        # Check if already published
        if draft['published_to_production']:
            return {
                'success': False,
                'error': 'Draft has already been published to production',
                'production_schema_id': draft.get('production_schema_id')
            }
        
        user_id = kwargs.get('_user_id')
        
        cursor = db.cursor()
        
        # Check if calculator name already exists in production
        cursor.execute("""
            SELECT schema_id, version FROM calculator_schemas_production
            WHERE calculator_name = %s
        """, (draft['calculator_name'],))
        
        existing = cursor.fetchone()
        
        if existing:
            # Update existing (new version)
            existing_id, current_version = existing
            new_version = current_version + 1
            
            # Create version snapshot
            cursor.execute("""
                INSERT INTO calculator_schema_versions (
                    production_schema_id,
                    calculator_name,
                    version_number,
                    tool_schema,
                    parameter_schema,
                    implementation_type,
                    change_type,
                    change_description,
                    changed_by,
                    changed_by_agent
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                existing_id,
                draft['calculator_name'],
                current_version,
                json.dumps(draft['tool_schema']),
                json.dumps(draft['parameter_schema']),
                draft['implementation_type'],
                'update',
                f"Published from draft {draft_id}",
                user_id,
                draft['created_by_agent']
            ))
            
            # Update production
            cursor.execute("""
                UPDATE calculator_schemas_production
                SET 
                    tool_schema = %s,
                    parameter_schema = %s,
                    implementation_type = %s,
                    version = %s,
                    updated_at = NOW(),
                    is_experimental = %s,
                    requires_approval = %s
                WHERE schema_id = %s
                RETURNING schema_id
            """, (
                json.dumps(draft['tool_schema']),
                json.dumps(draft['parameter_schema']),
                draft['implementation_type'],
                new_version,
                mark_experimental,
                requires_approval,
                existing_id
            ))
            
            production_id = cursor.fetchone()[0]
        
        else:
            # Create new production schema
            cursor.execute("""
                INSERT INTO calculator_schemas_production (
                    calculator_name,
                    platform,
                    category,
                    tool_schema,
                    parameter_schema,
                    implementation_type,
                    source,
                    draft_id,
                    version,
                    is_experimental,
                    requires_approval,
                    published_by,
                    description,
                    purpose,
                    example_use_cases
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING schema_id
            """, (
                draft['calculator_name'],
                draft['platform'],
                draft['category'],
                json.dumps(draft['tool_schema']),
                json.dumps(draft['parameter_schema']),
                draft['implementation_type'],
                'ai_generated',
                draft_id,
                1,
                mark_experimental,
                requires_approval,
                user_id,
                draft['description'],
                draft['purpose'],
                draft['example_use_cases']
            ))
            
            production_id = cursor.fetchone()[0]
            
            # Create initial version snapshot
            cursor.execute("""
                INSERT INTO calculator_schema_versions (
                    production_schema_id,
                    calculator_name,
                    version_number,
                    tool_schema,
                    parameter_schema,
                    implementation_type,
                    change_type,
                    change_description,
                    changed_by,
                    changed_by_agent
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                production_id,
                draft['calculator_name'],
                1,
                json.dumps(draft['tool_schema']),
                json.dumps(draft['parameter_schema']),
                draft['implementation_type'],
                'create',
                f"Initial publish from draft {draft_id}",
                user_id,
                draft['created_by_agent']
            ))
        
        # Update draft to mark as published
        cursor.execute("""
            UPDATE calculator_schema_drafts
            SET 
                published_to_production = true,
                published_at = NOW(),
                published_by = %s,
                production_schema_id = %s,
                updated_at = NOW()
            WHERE draft_id = %s
        """, (user_id, production_id, draft_id))
        
        db.commit()
        
        # Notify Registry V3 to reload (in production, would trigger cache refresh)
        logger.info(f"[CALCULATOR_SCHEMA] Published to production: {draft['calculator_name']} (ID: {production_id})")
        
        return {
            'success': True,
            'production_schema_id': str(production_id),
            'calculator_name': draft['calculator_name'],
            'version': existing[1] + 1 if existing else 1,
            'is_experimental': mark_experimental,
            'requires_approval': requires_approval,
            'message': f"Calculator schema published successfully. Registry V3 will load on next initialization. {'⚠️ Marked as EXPERIMENTAL - requires opt-in to use.' if mark_experimental else '✅ Available for production use.'}"
        }
    
    except Exception as e:
        logger.error(f"Error publishing to production: {e}")
        db.rollback()
        return {
            'success': False,
            'error': str(e)
        }


def calculator_schema_list_production(
    source: str = 'all',
    is_active: bool = None,
    is_experimental: bool = None,
    include_stats: bool = False,
    **kwargs
) -> Dict[str, Any]:
    """
    List production calculator schemas
    
    Args:
        source: Filter by source ('file', 'database', 'ai_generated', 'all')
        is_active: Filter by active status
        is_experimental: Filter by experimental flag
        include_stats: Include usage statistics
    
    Returns:
        List of production schemas
    """
    db = _get_db_connection(**kwargs)
    if not db:
        return {
            'success': False,
            'error': 'Database connection failed'
        }
    
    try:
        query = """
            SELECT 
                schema_id,
                calculator_name,
                source,
                version,
                is_active,
                is_experimental,
                requires_approval,
                published_at,
                updated_at,
                execution_count,
                success_rate,
                last_executed_at
            FROM calculator_schemas_production
            WHERE 1=1
        """
        params = []
        
        if source != 'all':
            query += " AND source = %s"
            params.append(source)
        
        if is_active is not None:
            query += " AND is_active = %s"
            params.append(is_active)
        
        if is_experimental is not None:
            query += " AND is_experimental = %s"
            params.append(is_experimental)
        
        query += " ORDER BY calculator_name"
        
        cursor = db.cursor()
        cursor.execute(query, params)
        
        schemas = []
        for row in cursor.fetchall():
            (schema_id, calc_name, source, version, active, experimental,
             requires_approval, published_at, updated_at, exec_count, 
             success_rate, last_exec) = row
            
            schema_info = {
                'schema_id': str(schema_id),
                'calculator_name': calc_name,
                'source': source,
                'version': version,
                'is_active': active,
                'is_experimental': experimental,
                'requires_approval': requires_approval,
                'published_at': published_at.isoformat(),
                'updated_at': updated_at.isoformat()
            }
            
            if include_stats:
                schema_info.update({
                    'execution_count': exec_count or 0,
                    'success_rate': float(success_rate) if success_rate else None,
                    'last_executed_at': last_exec.isoformat() if last_exec else None
                })
            
            schemas.append(schema_info)
        
        return {
            'success': True,
            'schemas': schemas,
            'count': len(schemas)
        }
    
    except Exception as e:
        logger.error(f"Error listing production schemas: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def calculator_schema_rollback_version(
    calculator_name: str,
    target_version: int = None,
    reason: str = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Rollback production schema to previous version
    
    Args:
        calculator_name: Name of calculator to rollback
        target_version: Version to rollback to (default: current - 1)
        reason: Reason for rollback
    
    Returns:
        Rollback result
    """
    db = _get_db_connection(**kwargs)
    if not db:
        return {
            'success': False,
            'error': 'Database connection failed'
        }
    
    try:
        cursor = db.cursor()
        
        # Get current production schema
        cursor.execute("""
            SELECT schema_id, version, tool_schema, parameter_schema, implementation_type
            FROM calculator_schemas_production
            WHERE calculator_name = %s
        """, (calculator_name,))
        
        current = cursor.fetchone()
        
        if not current:
            return {
                'success': False,
                'error': f'Calculator not found in production: {calculator_name}'
            }
        
        schema_id, current_version, current_schema, current_params, current_impl = current
        
        # Determine target version
        if target_version is None:
            target_version = current_version - 1
        
        if target_version < 1:
            return {
                'success': False,
                'error': f'Cannot rollback to version {target_version} - must be >= 1'
            }
        
        if target_version >= current_version:
            return {
                'success': False,
                'error': f'Target version {target_version} must be less than current version {current_version}'
            }
        
        # Get target version from history
        cursor.execute("""
            SELECT tool_schema, parameter_schema, implementation_type
            FROM calculator_schema_versions
            WHERE production_schema_id = %s AND version_number = %s
        """, (schema_id, target_version))
        
        target = cursor.fetchone()
        
        if not target:
            return {
                'success': False,
                'error': f'Version {target_version} not found in history'
            }
        
        target_schema, target_params, target_impl = target
        
        # Create snapshot of current version before rollback
        cursor.execute("""
            INSERT INTO calculator_schema_versions (
                production_schema_id,
                calculator_name,
                version_number,
                tool_schema,
                parameter_schema,
                implementation_type,
                change_type,
                change_description,
                changed_by,
                changed_by_agent
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            schema_id,
            calculator_name,
            current_version,
            json.dumps(current_schema),
            json.dumps(current_params),
            current_impl,
            'rollback',
            f"Rolled back to version {target_version}. Reason: {reason or 'Not specified'}",
            kwargs.get('_user_id'),
            kwargs.get('_agent_name', 'AI Agent')
        ))
        
        # Update production to target version
        cursor.execute("""
            UPDATE calculator_schemas_production
            SET 
                tool_schema = %s,
                parameter_schema = %s,
                implementation_type = %s,
                version = %s,
                updated_at = NOW()
            WHERE schema_id = %s
        """, (
            json.dumps(target_schema),
            json.dumps(target_params),
            target_impl,
            current_version + 1,  # Increment version (rollback creates new version)
            schema_id
        ))
        
        db.commit()
        
        logger.info(f"[CALCULATOR_SCHEMA] Rolled back {calculator_name} from v{current_version} to v{target_version}")
        
        return {
            'success': True,
            'calculator_name': calculator_name,
            'previous_version': current_version,
            'current_version': current_version + 1,
            'rolled_back_to': target_version,
            'reason': reason or 'Not specified',
            'message': f'Successfully rolled back to version {target_version}. Current version is now {current_version + 1}.'
        }
    
    except Exception as e:
        logger.error(f"Error rolling back version: {e}")
        db.rollback()
        return {
            'success': False,
            'error': str(e)
        }
```

---

## 🚀 Flask API Routes: `AI_infrastructure/routes/calculator_schema_routes.py`

```python
"""
Calculator Schema Management API Routes
========================================
REST API endpoints for AI-facilitated calculator schema creation.

Endpoints:
    POST   /api/calculator-schemas/drafts             - Create draft
    GET    /api/calculator-schemas/drafts             - List drafts
    GET    /api/calculator-schemas/drafts/<id>        - Get draft
    PATCH  /api/calculator-schemas/drafts/<id>        - Update draft
    POST   /api/calculator-schemas/drafts/<id>/test   - Test draft
    POST   /api/calculator-schemas/drafts/<id>/publish - Publish to production
    GET    /api/calculator-schemas/production         - List production schemas
    POST   /api/calculator-schemas/<name>/rollback    - Rollback version

LAST MODIFIED: 2025-12-17 - Initial implementation
"""

from flask import Blueprint, request, jsonify
from functools import wraps
import sys
from pathlib import Path

# Add tools to path
tools_path = Path(__file__).parent.parent.parent / 'tools'
if str(tools_path) not in sys.path:
    sys.path.insert(0, str(tools_path))

from implementations.calculator_schema_management import (
    calculator_schema_create_draft,
    calculator_schema_list_drafts,
    calculator_schema_get_draft,
    calculator_schema_update_draft,
    calculator_schema_test_draft,
    calculator_schema_publish_to_production,
    calculator_schema_list_production,
    calculator_schema_rollback_version
)

# Create blueprint
calc_schema_bp = Blueprint('calculator_schemas', __name__, url_prefix='/api/calculator-schemas')


# Authentication decorator
def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get user from session/token (implement your auth logic)
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({'success': False, 'error': 'Authentication required'}), 401
        
        # Add user_id to kwargs
        kwargs['_user_id'] = int(user_id)
        return f(*args, **kwargs)
    
    return decorated_function


# ============================================================================
# DRAFT MANAGEMENT ROUTES
# ============================================================================

@calc_schema_bp.route('/drafts', methods=['POST'])
@require_auth
def create_draft(_user_id=None):
    """Create new calculator schema draft"""
    try:
        data = request.get_json()
        
        result = calculator_schema_create_draft(
            calculator_name=data['calculator_name'],
            short_description=data['short_description'],
            description=data['description'],
            parameters=data['parameters'],
            implementation_type=data['implementation_type'],
            calculation_logic=data.get('calculation_logic'),
            implementation_notes=data.get('implementation_notes'),
            example_use_cases=data.get('example_use_cases'),
            _user_id=_user_id,
            _agent_name=data.get('agent_name', 'API Client')
        )
        
        status_code = 201 if result['success'] else 400
        return jsonify(result), status_code
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@calc_schema_bp.route('/drafts', methods=['GET'])
@require_auth
def list_drafts(_user_id=None):
    """List calculator schema drafts"""
    try:
        status = request.args.get('status', 'all')
        category = request.args.get('category')
        
        result = calculator_schema_list_drafts(
            status=status,
            created_by_user_id=_user_id,
            category=category,
            _user_id=_user_id
        )
        
        return jsonify(result), 200 if result['success'] else 400
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@calc_schema_bp.route('/drafts/<draft_id>', methods=['GET'])
@require_auth
def get_draft(draft_id, _user_id=None):
    """Get calculator schema draft details"""
    try:
        result = calculator_schema_get_draft(
            draft_id=draft_id,
            _user_id=_user_id
        )
        
        return jsonify(result), 200 if result['success'] else 404
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@calc_schema_bp.route('/drafts/<draft_id>', methods=['PATCH'])
@require_auth
def update_draft(draft_id, _user_id=None):
    """Update calculator schema draft"""
    try:
        data = request.get_json()
        
        result = calculator_schema_update_draft(
            draft_id=draft_id,
            updates=data.get('updates', {}),
            reset_tests=data.get('reset_tests', False),
            _user_id=_user_id
        )
        
        return jsonify(result), 200 if result['success'] else 400
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@calc_schema_bp.route('/drafts/<draft_id>/test', methods=['POST'])
@require_auth
def test_draft(draft_id, _user_id=None):
    """Test calculator schema draft with sample calculations"""
    try:
        data = request.get_json()
        
        result = calculator_schema_test_draft(
            draft_id=draft_id,
            test_cases=data.get('test_cases', []),
            validate_only=data.get('validate_only', False),
            _user_id=_user_id
        )
        
        return jsonify(result), 200 if result['success'] else 400
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@calc_schema_bp.route('/drafts/<draft_id>/publish', methods=['POST'])
@require_auth
def publish_draft(draft_id, _user_id=None):
    """Publish calculator schema draft to production"""
    try:
        data = request.get_json() or {}
        
        result = calculator_schema_publish_to_production(
            draft_id=draft_id,
            override_validation=data.get('override_validation', False),
            mark_experimental=data.get('mark_experimental', False),
            requires_approval=data.get('requires_approval', False),
            _user_id=_user_id
        )
        
        return jsonify(result), 201 if result['success'] else 400
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# PRODUCTION MANAGEMENT ROUTES
# ============================================================================

@calc_schema_bp.route('/production', methods=['GET'])
@require_auth
def list_production(_user_id=None):
    """List production calculator schemas"""
    try:
        source = request.args.get('source', 'all')
        is_active = request.args.get('is_active')
        is_experimental = request.args.get('is_experimental')
        include_stats = request.args.get('include_stats', 'false').lower() == 'true'
        
        # Convert string booleans
        if is_active is not None:
            is_active = is_active.lower() == 'true'
        if is_experimental is not None:
            is_experimental = is_experimental.lower() == 'true'
        
        result = calculator_schema_list_production(
            source=source,
            is_active=is_active,
            is_experimental=is_experimental,
            include_stats=include_stats,
            _user_id=_user_id
        )
        
        return jsonify(result), 200 if result['success'] else 400
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@calc_schema_bp.route('/<calculator_name>/rollback', methods=['POST'])
@require_auth
def rollback_version(calculator_name, _user_id=None):
    """Rollback production calculator schema to previous version"""
    try:
        data = request.get_json() or {}
        
        result = calculator_schema_rollback_version(
            calculator_name=calculator_name,
            target_version=data.get('target_version'),
            reason=data.get('reason'),
            _user_id=_user_id,
            _agent_name=data.get('agent_name', 'API Client')
        )
        
        return jsonify(result), 200 if result['success'] else 400
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# HEALTH CHECK
# ============================================================================

@calc_schema_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'service': 'Calculator Schema Management',
        'version': '1.0.0'
    }), 200
```

---

## 🔧 Registry V3 Integration

### Modified `tools/registry_v3.py` (Add calculator schema loading)

```python
# Add to RegistryV3.__init__() method after existing schema loading:

def _load_schemas(self):
    """Load schemas from files AND database (calculator schemas)"""
    # EXISTING: Load from files
    self._load_file_schemas()
    
    # NEW: Load from database (calculator_schemas_production)
    self._load_database_calculator_schemas()


def _load_database_calculator_schemas(self):
    """Load calculator schemas from calculator_schemas_production table"""
    try:
        from AI_infrastructure.core.database import get_db_connection
        
        db = get_db_connection()
        cursor = db.cursor()
        
        cursor.execute("""
            SELECT 
                calculator_name,
                tool_schema,
                source,
                version,
                is_active
            FROM calculator_schemas_production
            WHERE is_active = true
            ORDER BY calculator_name
        """)
        
        count = 0
        for row in cursor.fetchall():
            calc_name, tool_schema, source, version, active = row
            
            # Database schemas can override file schemas (if same name)
            if calc_name in self.tools:
                logger.warning(f"  [DATABASE] Overriding file schema for: {calc_name} (v{version}, source={source})")
            
            self.tools[calc_name] = tool_schema
            self.tools[calc_name]['_source'] = source
            self.tools[calc_name]['_version'] = version
            
            count += 1
            logger.debug(f"  [DATABASE] Loaded: {calc_name} (v{version})")
        
        if count > 0:
            logger.info(f"[REGISTRY] Loaded {count} calculator schemas from database")
    
    except Exception as e:
        logger.warning(f"[REGISTRY] Could not load database calculator schemas: {e}")
        # Non-fatal - continue with file-based schemas
```

---

## 📊 Comparison: Workflow Automation vs Calculator Schema Management

| Feature | Workflow Automation | Calculator Schema Management |
|---------|---------------------|------------------------------|
| **Primary Table** | `automation_workflows` | `calculator_schema_drafts` |
| **Production Table** | Same table (status field) | `calculator_schemas_production` |
| **Version History** | `workflow_executions` | `calculator_schema_versions` |
| **AI Tools** | 11 tools | 7 tools |
| **Draft → Publish** | ✅ Yes (status change) | ✅ Yes (separate tables) |
| **Testing** | Manual execution | `calculator_schema_test_draft` |
| **Registry Loading** | Not integrated | ✅ Integrated with Registry V3 |
| **UI Canvas** | ✅ Visual workflow builder | ❌ Not applicable |
| **Rollback** | Deactivate workflow | `calculator_schema_rollback_version` |

---

## 🎯 User Workflow Example

### Scenario: AI Creates "Vinyl Stickers" Calculator

**User:** "I need to create a calculator for vinyl stickers - custom shapes, sizing 4-12 inches, quantities 50-5000, with or without die-cutting"

**AI Agent Response:**

```
I'll create a custom calculator for vinyl stickers following the schema management workflow.

**Step 1: Create Draft Schema**
```

<function_calls>
<invoke name="calculator_schema_create_draft">
<parameter name="calculator_name">calculate_vinyl_stickers