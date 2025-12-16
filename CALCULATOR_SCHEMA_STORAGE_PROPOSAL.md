# Calculator Schema Storage & JSON-Schema-Implementation-Wrapper Proposal

**Date:** December 17, 2025  
**Context:** Analysis of quote-calculator module structure  
**Comparison:** Workflow-automation system architecture  
**Goal:** Create ubiquitous custom JSON schema implementation wrapper for calculators

---

## 🔍 Current State Analysis

### Quote Calculator Structure

**Current Implementation:**
```
C:\Users\gpoli\GIT\AI_agents\UI\modules_external\quote-calculator\
├── backend/
│   ├── god_calculators/          # Database-driven calculators (3 tools)
│   │   ├── GOD_flyer_calculator.py
│   │   ├── GOD_letterhead_calculator.py
│   │   └── GOD_perfect_bound_books_calculator.py
│   ├── shopify_calculators/      # Hardcoded calculators (24 tools)
│   │   └── [24 calculator files]
│   └── quote_calculator_routes.py
├── schema/
│   ├── calculator_tools.json     # 37 calculator tool schemas
│   └── query_library_tools.json  # 57 query tool schemas
└── implementations/
    └── [Calculator logic files]
```

**Key Characteristics:**
- **37 calculators** total (3 GOD + 24 Shopify + 10 basic)
- **JSON schemas** define tool interface (parameters, enums, descriptions)
- **Python implementations** contain calculation logic
- **Static JSON files** loaded into registry at runtime
- **No database storage** - schemas are file-based

---

## 🏗️ Workflow-Automation System (Comparison Model)

**Current Implementation:**
```
Workflow-Automation Architecture:
├── Database Tables:
│   ├── automation_workflows      # Workflow definitions (JSON)
│   ├── workflow_executions       # Execution history
│   ├── workflow_node_library     # Node type definitions
│   ├── workflow_schedules        # Cron/interval schedules
│   └── workflow_templates        # Reusable templates
├── JSON Schema:
│   └── tools/schemas/automation_tools.json  # 11 AI tools
├── Python Implementation:
│   └── tools/implementations/automation.py  # Tool logic
└── UI Integration:
    └── UI/modules_internal/automation-workflows/automation-workflows.js
```

**Key Features:**
1. **Database-Driven:** Workflow definitions stored in PostgreSQL
2. **JSON Schema Wrapper:** `workflow_json` field stores visual canvas structure
3. **Dynamic Loading:** Workflows loaded from DB at runtime
4. **User-Editable:** Users can create/modify workflows via UI
5. **Versioning:** Track changes over time
6. **Templates:** Share and clone common patterns

---

## 💡 Proposal: Calculator Schema Storage System

### Architecture Option 1: Hybrid (File + Database)

**Best for:** Incremental migration, maintain backwards compatibility

```sql
-- New Database Table
CREATE TABLE calculator_schemas (
    schema_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    calculator_name TEXT NOT NULL UNIQUE,  -- e.g., 'calculate_business_cards'
    platform TEXT NOT NULL,                 -- 'quote_calculator'
    schema_version INTEGER DEFAULT 1,
    
    -- JSON Schema Definition
    tool_schema JSONB NOT NULL,             -- Full tool definition
    parameter_schema JSONB NOT NULL,        -- Just parameters (for validation)
    
    -- Metadata
    source TEXT NOT NULL,                   -- 'file' or 'database' or 'custom'
    is_active BOOLEAN DEFAULT true,
    is_god_calculator BOOLEAN DEFAULT false, -- Database-driven vs hardcoded
    
    -- Versioning & Tracking
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by INTEGER REFERENCES sessions.users(id),
    updated_by INTEGER REFERENCES sessions.users(id),
    
    -- Caching & Performance
    last_loaded_at TIMESTAMPTZ,
    load_count INTEGER DEFAULT 0,
    
    CONSTRAINT valid_source CHECK (source IN ('file', 'database', 'custom'))
);

-- Indexes for performance
CREATE INDEX idx_calculator_schemas_name ON calculator_schemas(calculator_name);
CREATE INDEX idx_calculator_schemas_platform ON calculator_schemas(platform);
CREATE INDEX idx_calculator_schemas_active ON calculator_schemas(is_active);
CREATE INDEX idx_calculator_schemas_source ON calculator_schemas(source);

-- Full-text search on schema content
CREATE INDEX idx_calculator_schemas_tool_schema_gin ON calculator_schemas USING gin(tool_schema);
```

**Migration Strategy:**
```python
# Phase 1: Seed database from existing JSON files
INSERT INTO calculator_schemas (calculator_name, platform, tool_schema, parameter_schema, source)
SELECT 
    name,
    platform,
    full_definition::JSONB,
    parameters::JSONB,
    'file'
FROM (
    -- Read calculator_tools.json
    SELECT * FROM read_json_file('schema/calculator_tools.json')
) AS schemas;

# Phase 2: Registry loads from BOTH sources
class RegistryV3:
    def _load_schemas(self):
        # Load from files (backwards compatibility)
        self._load_file_schemas()
        
        # Load from database (new system)
        self._load_database_schemas()
        
        # Merge (database takes precedence)
        self._merge_schemas()
```

---

### Architecture Option 2: Full Database-Driven

**Best for:** Greenfield, maximum flexibility, future-proofing

```sql
-- Calculator Definitions (Primary)
CREATE TABLE calculator_definitions (
    calculator_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE,              -- Tool name
    short_description TEXT,
    description TEXT,
    platform TEXT NOT NULL,
    category TEXT,                          -- 'basic', 'god', 'shopify', 'custom'
    
    -- Implementation Details
    implementation_file TEXT,               -- Python file path
    implementation_class TEXT,              -- Class name (if applicable)
    implementation_function TEXT,           -- Function name
    
    -- Status & Visibility
    is_active BOOLEAN DEFAULT true,
    is_public BOOLEAN DEFAULT true,
    requires_database BOOLEAN DEFAULT false, -- GOD calculators
    
    -- Versioning
    version INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by INTEGER REFERENCES sessions.users(id)
);

-- Parameters (Normalized)
CREATE TABLE calculator_parameters (
    parameter_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    calculator_id UUID REFERENCES calculator_definitions(calculator_id) ON DELETE CASCADE,
    
    name TEXT NOT NULL,
    type TEXT NOT NULL,                     -- 'integer', 'string', 'boolean', 'enum'
    description TEXT,
    
    is_required BOOLEAN DEFAULT false,
    default_value JSONB,
    
    -- Validation Rules
    min_value NUMERIC,
    max_value NUMERIC,
    pattern TEXT,                           -- Regex for string validation
    enum_values JSONB,                      -- Array of allowed values
    
    -- UI Hints
    ui_order INTEGER,                       -- Display order
    ui_widget TEXT,                         -- 'input', 'select', 'radio', 'checkbox'
    ui_group TEXT,                          -- Group parameters together
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(calculator_id, name)
);

-- Enum Values (Normalized Further - Optional)
CREATE TABLE calculator_enum_values (
    enum_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    parameter_id UUID REFERENCES calculator_parameters(parameter_id) ON DELETE CASCADE,
    
    value TEXT NOT NULL,
    label TEXT,
    description TEXT,
    display_order INTEGER,
    is_active BOOLEAN DEFAULT true,
    
    UNIQUE(parameter_id, value)
);

-- Examples & Documentation
CREATE TABLE calculator_examples (
    example_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    calculator_id UUID REFERENCES calculator_definitions(calculator_id) ON DELETE CASCADE,
    
    title TEXT,
    description TEXT,
    parameters JSONB NOT NULL,              -- Example input
    expected_result JSONB,                  -- Example output
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Custom User Calculators (Future Extension)
CREATE TABLE custom_calculators (
    custom_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id INTEGER REFERENCES sessions.users(id),
    calculator_id UUID REFERENCES calculator_definitions(calculator_id),
    
    custom_name TEXT,
    custom_parameters JSONB,                -- User-specific overrides
    custom_logic TEXT,                      -- Custom Python code (sandboxed)
    
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 🔧 JSON-Schema-Implementation-Wrapper (Core Component)

### Purpose
Create a **ubiquitous wrapper** that:
1. Loads calculator schemas from **multiple sources** (file, database, custom)
2. Validates parameters against schema
3. Dynamically routes to implementation (GOD/Shopify/Custom)
4. Caches for performance
5. Tracks usage and errors

### Implementation

```python
# File: tools/wrappers/calculator_schema_wrapper.py

"""
Calculator JSON Schema Implementation Wrapper
==============================================
Ubiquitous wrapper for calculator tool schemas - similar to workflow automation system.

Supports:
- Multiple schema sources (file, database, custom)
- Dynamic parameter validation
- Implementation routing (GOD vs Shopify vs Custom)
- Caching and performance optimization
- Usage tracking and error logging
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class CalculatorSchema:
    """Unified calculator schema representation"""
    name: str
    platform: str
    description: str
    parameters: Dict[str, Any]
    returns: Dict[str, Any]
    source: str  # 'file', 'database', 'custom'
    version: int = 1
    is_active: bool = True
    is_god_calculator: bool = False
    implementation_path: Optional[str] = None
    examples: List[Dict[str, Any]] = None
    
    def validate_parameters(self, **kwargs) -> tuple[bool, Optional[str]]:
        """Validate provided parameters against schema"""
        required_params = [
            name for name, spec in self.parameters.items()
            if spec.get('required', False)
        ]
        
        # Check required parameters
        for param in required_params:
            if param not in kwargs:
                return False, f"Missing required parameter: {param}"
        
        # Validate types and enums
        for param_name, param_value in kwargs.items():
            if param_name not in self.parameters:
                return False, f"Unknown parameter: {param_name}"
            
            param_spec = self.parameters[param_name]
            param_type = param_spec.get('type')
            
            # Type validation
            type_map = {
                'integer': int,
                'string': str,
                'boolean': bool,
                'array': list,
                'object': dict
            }
            
            expected_type = type_map.get(param_type)
            if expected_type and not isinstance(param_value, expected_type):
                return False, f"Parameter {param_name} must be type {param_type}"
            
            # Enum validation
            if 'enum' in param_spec:
                if param_value not in param_spec['enum']:
                    return False, f"Parameter {param_name} must be one of: {param_spec['enum']}"
        
        return True, None


class CalculatorSchemaWrapper:
    """
    Ubiquitous calculator schema wrapper
    
    Similar to workflow automation system, but for calculator tools.
    Handles schema loading, validation, caching, and implementation routing.
    """
    
    def __init__(self, db_connection=None):
        self.db = db_connection
        self.cache: Dict[str, CalculatorSchema] = {}
        self.file_schemas_path = Path(__file__).parent.parent.parent / "UI" / "modules_external" / "quote-calculator" / "schema"
        
        # Load schemas
        self._load_all_schemas()
    
    def _load_all_schemas(self):
        """Load schemas from all sources"""
        logger.info("[CALCULATOR_WRAPPER] Loading schemas from all sources...")
        
        # Load from files
        self._load_file_schemas()
        
        # Load from database (if available)
        if self.db:
            self._load_database_schemas()
        
        logger.info(f"[CALCULATOR_WRAPPER] Loaded {len(self.cache)} calculator schemas")
    
    def _load_file_schemas(self):
        """Load schemas from JSON files (backwards compatibility)"""
        calculator_file = self.file_schemas_path / "calculator_tools.json"
        
        if not calculator_file.exists():
            logger.warning(f"Calculator schema file not found: {calculator_file}")
            return
        
        try:
            with open(calculator_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            platform = data.get('platform', 'quote_calculator')
            
            for tool in data.get('tools', []):
                name = tool.get('name')
                if not name:
                    continue
                
                schema = CalculatorSchema(
                    name=name,
                    platform=platform,
                    description=tool.get('description', ''),
                    parameters=tool.get('parameters', {}),
                    returns=tool.get('returns', {}),
                    source='file',
                    examples=tool.get('examples', [])
                )
                
                self.cache[name] = schema
                logger.debug(f"  [FILE] Loaded: {name}")
        
        except Exception as e:
            logger.error(f"Error loading file schemas: {e}")
    
    def _load_database_schemas(self):
        """Load schemas from database (new system)"""
        if not self.db:
            return
        
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT 
                    calculator_name,
                    platform,
                    tool_schema,
                    parameter_schema,
                    schema_version,
                    is_active,
                    is_god_calculator,
                    source
                FROM calculator_schemas
                WHERE is_active = true
                ORDER BY updated_at DESC
            """)
            
            for row in cursor.fetchall():
                name, platform, tool_schema, param_schema, version, active, is_god, source = row
                
                schema = CalculatorSchema(
                    name=name,
                    platform=platform,
                    description=tool_schema.get('description', ''),
                    parameters=param_schema,
                    returns=tool_schema.get('returns', {}),
                    source=source,
                    version=version,
                    is_active=active,
                    is_god_calculator=is_god,
                    examples=tool_schema.get('examples', [])
                )
                
                # Database schemas override file schemas
                self.cache[name] = schema
                logger.debug(f"  [DATABASE] Loaded: {name} (v{version})")
        
        except Exception as e:
            logger.error(f"Error loading database schemas: {e}")
    
    def get_schema(self, calculator_name: str) -> Optional[CalculatorSchema]:
        """Get schema for a calculator"""
        return self.cache.get(calculator_name)
    
    def validate_parameters(self, calculator_name: str, **kwargs) -> tuple[bool, Optional[str]]:
        """Validate parameters for a calculator"""
        schema = self.get_schema(calculator_name)
        
        if not schema:
            return False, f"Calculator not found: {calculator_name}"
        
        return schema.validate_parameters(**kwargs)
    
    def list_calculators(self, platform: Optional[str] = None, 
                        category: Optional[str] = None) -> List[CalculatorSchema]:
        """List available calculators with optional filtering"""
        calculators = list(self.cache.values())
        
        if platform:
            calculators = [c for c in calculators if c.platform == platform]
        
        if category:
            # Category filtering based on name patterns
            if category == 'god':
                calculators = [c for c in calculators if c.is_god_calculator]
            elif category == 'shopify':
                calculators = [c for c in calculators if 'shopify' in c.name.lower()]
        
        return calculators
    
    def route_to_implementation(self, calculator_name: str) -> Optional[str]:
        """
        Determine which implementation file to use
        
        Returns:
            File path to implementation (relative to tools/implementations/)
        """
        schema = self.get_schema(calculator_name)
        
        if not schema:
            return None
        
        # GOD calculators
        if schema.is_god_calculator or 'GOD' in calculator_name:
            return f"quote_calculator/god_calculators/{calculator_name}.py"
        
        # Shopify calculators
        if 'shopify' in calculator_name.lower():
            return f"quote_calculator/shopify_calculators/{calculator_name}.py"
        
        # Default calculators
        return f"quote_calculator/{calculator_name}.py"
    
    def save_custom_calculator(self, user_id: int, calculator_definition: Dict[str, Any]) -> bool:
        """Save a custom calculator to database (future extension)"""
        if not self.db:
            return False
        
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                INSERT INTO calculator_schemas (
                    calculator_name,
                    platform,
                    tool_schema,
                    parameter_schema,
                    source,
                    created_by
                ) VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING schema_id
            """, (
                calculator_definition['name'],
                calculator_definition.get('platform', 'quote_calculator'),
                json.dumps(calculator_definition),
                json.dumps(calculator_definition.get('parameters', {})),
                'custom',
                user_id
            ))
            
            schema_id = cursor.fetchone()[0]
            self.db.commit()
            
            # Reload schemas to include new custom calculator
            self._load_database_schemas()
            
            logger.info(f"[CUSTOM] Created custom calculator: {calculator_definition['name']}")
            return True
        
        except Exception as e:
            logger.error(f"Error saving custom calculator: {e}")
            self.db.rollback()
            return False
```

---

## 🔄 Integration with Registry V3

### Modified Registry Structure

```python
# File: tools/registry_v3.py (UPDATED)

class RegistryV3:
    def __init__(self):
        self.tools = {}
        self.implementations = {}
        
        # NEW: Calculator schema wrapper
        self.calculator_wrapper = None
        
        # Initialize wrapper
        self._initialize_calculator_wrapper()
        
        # Load schemas (now uses wrapper)
        self._load_schemas()
        self._load_implementations()
    
    def _initialize_calculator_wrapper(self):
        """Initialize calculator schema wrapper with database connection"""
        try:
            from tools.wrappers.calculator_schema_wrapper import CalculatorSchemaWrapper
            from AI_infrastructure.core.database import get_db_connection
            
            db = get_db_connection()
            self.calculator_wrapper = CalculatorSchemaWrapper(db_connection=db)
            
            logger.info("[REGISTRY] Calculator schema wrapper initialized")
        except Exception as e:
            logger.warning(f"[REGISTRY] Calculator wrapper not available: {e}")
    
    def _load_schemas(self):
        """Load schemas using wrapper (if available) or fallback to file loading"""
        if self.calculator_wrapper:
            # NEW METHOD: Load from wrapper (database + files)
            for schema in self.calculator_wrapper.list_calculators():
                self.tools[schema.name] = {
                    'name': schema.name,
                    'platform': schema.platform,
                    'description': schema.description,
                    'parameters': schema.parameters,
                    'returns': schema.returns,
                    'examples': schema.examples,
                    '_schema_source': schema.source,
                    '_schema_version': schema.version
                }
            
            logger.info(f"[REGISTRY] Loaded {len(self.tools)} tools via calculator wrapper")
        else:
            # FALLBACK: Original file-based loading
            self._load_file_schemas()
    
    def validate_tool_parameters(self, tool_name: str, **kwargs) -> tuple[bool, Optional[str]]:
        """Validate parameters using calculator wrapper"""
        if self.calculator_wrapper:
            return self.calculator_wrapper.validate_parameters(tool_name, **kwargs)
        
        # Fallback to original validation
        return self._validate_parameters_legacy(tool_name, **kwargs)
```

---

## 📊 Comparison: Workflow vs Calculator Systems

| Feature | Workflow System | Calculator System (Current) | Calculator System (Proposed) |
|---------|----------------|-----------------------------|-----------------------------|
| **Schema Storage** | Database (automation_workflows) | File (calculator_tools.json) | Hybrid (File + Database) |
| **Schema Format** | JSONB (workflow_json field) | JSON file | JSONB + JSON file |
| **User Editable** | ✅ Yes (via UI canvas) | ❌ No (developer only) | ✅ Yes (custom calculators) |
| **Versioning** | ✅ Yes (updated_at tracking) | ❌ No | ✅ Yes (version field) |
| **Templates** | ✅ Yes (workflow_templates) | ❌ No | ✅ Yes (calculator_templates) |
| **Execution History** | ✅ Yes (workflow_executions) | ❌ No | ⚠️ Could add (calculator_executions) |
| **Scheduling** | ✅ Yes (workflow_schedules) | ❌ N/A | ❌ N/A (calculators don't schedule) |
| **Dynamic Loading** | ✅ Yes (from database) | ⚠️ Partial (file reload) | ✅ Yes (from database) |
| **Caching** | ✅ Yes (in-memory) | ⚠️ Implicit (registry) | ✅ Yes (wrapper cache) |

---

## 🎯 Recommendation

### **Choose: Architecture Option 1 (Hybrid - File + Database)**

**Reasoning:**
1. **Backwards Compatible:** Existing calculator_tools.json files still work
2. **Incremental Migration:** Move calculators to database gradually
3. **Low Risk:** File-based system remains as fallback
4. **Future-Proof:** Can evolve to full database-driven later
5. **User Extensions:** Allows custom calculators without breaking core system

**Implementation Steps:**

#### Phase 1: Database Schema (Week 1)
- Create `calculator_schemas` table
- Seed with existing calculators from JSON files
- Add indexes for performance

#### Phase 2: Wrapper Development (Week 2)
- Build `CalculatorSchemaWrapper` class
- Integrate with Registry V3
- Add parameter validation logic

#### Phase 3: Registry Integration (Week 3)
- Modify Registry V3 to use wrapper
- Add fallback to file-based loading
- Test with existing calculators

#### Phase 4: Custom Calculators (Week 4+)
- Add UI for custom calculator creation
- Build calculator template system
- Implement user-specific overrides

---

## 🚀 Benefits of This Approach

### For Developers
- ✅ **Single Source of Truth:** Schema wrapper is the authoritative source
- ✅ **Type Safety:** Validated parameters before execution
- ✅ **Easy Debugging:** Track schema versions and sources
- ✅ **Performance:** Caching reduces DB queries

### For Users (Future)
- ✅ **Custom Calculators:** Create calculators without coding
- ✅ **Clone & Modify:** Start from templates
- ✅ **Share Calculators:** Publish for other users
- ✅ **Track Usage:** See calculator execution history

### For System
- ✅ **Scalability:** Database handles large numbers of calculators
- ✅ **Analytics:** Track which calculators are used most
- ✅ **Maintenance:** Update schemas without code deployment
- ✅ **A/B Testing:** Test calculator variations with users

---

## 📝 Next Steps

1. **Review & Approve:** Discuss architecture choice (Option 1 recommended)
2. **Create Migration:** Write SQL script for `calculator_schemas` table
3. **Build Wrapper:** Implement `CalculatorSchemaWrapper` class
4. **Integrate Registry:** Modify `registry_v3.py` to use wrapper
5. **Test Thoroughly:** Verify all 37 calculators still work
6. **Document:** Update tool documentation with new architecture

---

## 🔗 Related Systems

- **Workflow Automation:** Similar database-driven pattern
- **Tool Registry V3:** Will integrate with calculator wrapper
- **Tool Intelligence Logger:** Can track calculator usage patterns
- **Schema Processor:** Dynamic value injection for calculator parameters

---

**Conclusion:**

Yes, we should create a calculator schema storage table similar to workflow automation. The hybrid approach (Option 1) provides the best balance of:
- **Backwards compatibility** (files still work)
- **Future flexibility** (database-driven custom calculators)
- **Low migration risk** (gradual rollout)
- **User empowerment** (custom calculator creation)

The `CalculatorSchemaWrapper` will be the ubiquitous implementation wrapper that mirrors the workflow automation system's architecture while respecting the unique needs of calculator tools.
