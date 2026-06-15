"""
Calculator Builder AI Tools
Tools for building custom calculators interactively with AI assistance
"""
import json
import uuid
from decimal import Decimal
from typing import Dict, Any, List, Optional
from datetime import datetime
import sys
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'AI_infrastructure'))

from shared.database_utils import get_database_connection
from universal_calculator_executor import UniversalCalculatorExecutor


class CalculatorBuilderTools:
    """AI tools for building custom calculators"""
    
    def __init__(self):
        """Initialize calculator builder tools"""
        self.executor = UniversalCalculatorExecutor()
    
    def calculator_builder_start(self, name: str, description: str, 
                                 short_description: str = None,
                                 based_on_calculator: str = None,
                                 category: str = 'custom_quote',
                                 tags: List[str] = None) -> Dict[str, Any]:
        """
        Initialize new custom calculator
        
        Args:
            name: Calculator name (e.g., "Custom Acrylic Signs Double-Sided")
            description: Detailed description of calculator purpose
            short_description: Brief description for AI search (auto-generated if not provided)
            based_on_calculator: Optional parent calculator to clone from
            category: Calculator category (custom_quote, specialty_substrate, rush_job, etc.)
            tags: Search tags for categorization
        
        Returns:
            {
                "calculator_id": "uuid",
                "name": "...",
                "status": "draft",
                "draft_json": {...},  # Initial JSON structure
                "suggested_parameters": [...],  # Common parameters to add
                "next_steps": "..."
            }
        """
        try:
            conn = get_database_connection('ai_infrastructure')
            cursor = conn.cursor()
            
            # Generate short description if not provided
            if not short_description:
                short_description = description[:200] if len(description) > 200 else description
            
            # Create initial JSON structure
            draft_json = {
                "parameters": [],
                "pricing_constants": {},
                "calculation_steps": [],
                "result_structure": {
                    "total_price": "total_price",
                    "unit_price": "unit_price",
                    "quantity": "quantity",
                    "breakdown": {},
                    "specifications": {}
                }
            }
            
            # If based on existing calculator, clone it
            if based_on_calculator:
                cursor.execute("""
                    SELECT json_definition, tags, category
                    FROM custom_calculators
                    WHERE calculator_id = %s OR name = %s
                """, (based_on_calculator, based_on_calculator))
                
                row = cursor.fetchone()
                if row:
                    draft_json = row['json_definition']
                    if not tags:
                        tags = row['tags']
                    category = row['category']
            
            # Create calculator record
            calculator_id = str(uuid.uuid4())
            
            cursor.execute("""
                INSERT INTO custom_calculators (
                    calculator_id, name, short_description, description,
                    category, json_definition, tags, is_active
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, FALSE)
            """, (
                calculator_id,
                name,
                short_description,
                description,
                category,
                json.dumps(draft_json),
                tags or []
            ))
            
            conn.commit()
            
            # Get suggested parameters from parameter library
            cursor.execute("""
                SELECT parameter_name, category, description, base_value, value_unit
                FROM calculator_pricing_parameters
                WHERE category IN ('Material', 'Setup', 'Other')
                ORDER BY total_usage_count DESC
                LIMIT 20
            """)
            
            suggested_params = []
            for row in cursor.fetchall():
                suggested_params.append({
                    'parameter_name': row['parameter_name'],
                    'category': row['category'],
                    'description': row['description'],
                    'current_value': float(row['base_value']) if row['base_value'] else None,
                    'unit': row['value_unit']
                })
            
            cursor.close()
            conn.close()
            
            return {
                'success': True,
                'calculator_id': calculator_id,
                'name': name,
                'status': 'draft',
                'draft_json': draft_json,
                'suggested_parameters': suggested_params[:10],  # Top 10 most used
                'next_steps': (
                    f"Calculator '{name}' created (ID: {calculator_id[:8]}...)\n\n"
                    "Next steps:\n"
                    "1. Add input parameters using calculator_builder_add_parameter\n"
                    "2. Define calculation steps using calculator_builder_set_formula or calculator_builder_add_component\n"
                    "3. Test with sample inputs using calculator_builder_test\n"
                    "4. Save and activate using calculator_builder_save"
                )
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def calculator_builder_add_parameter(self, calculator_id: str, parameter_name: str,
                                         parameter_type: str = 'number',
                                         required: bool = True,
                                         source: str = None,
                                         options: List[Any] = None,
                                         default: Any = None,
                                         description: str = None) -> Dict[str, Any]:
        """
        Add input parameter to calculator
        
        Args:
            calculator_id: Calculator UUID
            parameter_name: Parameter name (e.g., "quantity", "width_mm", "substrate_type")
            parameter_type: Type (integer, number, select, boolean)
            required: Whether parameter is required
            source: Optional source from parameter library (e.g., "calculator_pricing_parameters:quantity_standard")
            options: For 'select' type, list of options
            default: Default value
            description: Parameter description
        
        Returns:
            {
                "success": True,
                "parameter_added": {...},
                "total_parameters": 5
            }
        """
        try:
            conn = get_database_connection('ai_infrastructure')
            cursor = conn.cursor()
            
            # Load calculator
            cursor.execute("""
                SELECT json_definition
                FROM custom_calculators
                WHERE calculator_id = %s
            """, (calculator_id,))
            
            row = cursor.fetchone()
            if not row:
                return {'success': False, 'error': f'Calculator {calculator_id} not found'}
            
            calc_json = row['json_definition']
            
            # Build parameter definition
            param_def = {
                'name': parameter_name,
                'type': parameter_type,
                'required': required
            }
            
            if source:
                param_def['source'] = source
            if options:
                param_def['options'] = options
            if default is not None:
                param_def['default'] = default
            if description:
                param_def['description'] = description
            
            # Add to parameters list
            calc_json['parameters'].append(param_def)
            
            # If source is provided, track in custom_calculator_parameters
            if source and ':' in source:
                source_table, source_param_id = source.split(':', 1)
                
                cursor.execute("""
                    INSERT INTO custom_calculator_parameters (
                        calculator_id, parameter_name, source_table, source_parameter_id,
                        formula_variable_name
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (calculator_id, parameter_name) DO NOTHING
                """, (calculator_id, parameter_name, source_table, source_param_id, f'pricing.{parameter_name}'))
            
            # Update calculator
            cursor.execute("""
                UPDATE custom_calculators
                SET json_definition = %s,
                    updated_at = NOW()
                WHERE calculator_id = %s
            """, (json.dumps(calc_json), calculator_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return {
                'success': True,
                'parameter_added': param_def,
                'total_parameters': len(calc_json['parameters']),
                'message': f"Parameter '{parameter_name}' added to calculator"
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def calculator_builder_set_formula(self, calculator_id: str, step_number: int,
                                       variable_name: str, formula: str,
                                       description: str = None) -> Dict[str, Any]:
        """
        Add calculation step with formula
        
        Args:
            calculator_id: Calculator UUID
            step_number: Step number in calculation sequence
            variable_name: Variable to store result (e.g., "area_m2", "total_price")
            formula: Formula expression (e.g., "(width_mm * height_mm) / 1000000")
            description: Step description
        
        Returns:
            {
                "success": True,
                "step_added": {...},
                "total_steps": 8
            }
        """
        try:
            conn = get_database_connection('ai_infrastructure')
            cursor = conn.cursor()
            
            # Load calculator
            cursor.execute("""
                SELECT json_definition
                FROM custom_calculators
                WHERE calculator_id = %s
            """, (calculator_id,))
            
            row = cursor.fetchone()
            if not row:
                return {'success': False, 'error': f'Calculator {calculator_id} not found'}
            
            calc_json = row['json_definition']
            
            # Build step definition
            step_def = {
                'step': step_number,
                'type': 'formula',
                'variable': variable_name,
                'formula': formula
            }
            
            if description:
                step_def['description'] = description
            
            # Add or update step
            existing_step = None
            for i, step in enumerate(calc_json['calculation_steps']):
                if step['step'] == step_number:
                    existing_step = i
                    break
            
            if existing_step is not None:
                calc_json['calculation_steps'][existing_step] = step_def
            else:
                calc_json['calculation_steps'].append(step_def)
            
            # Sort steps by step number
            calc_json['calculation_steps'].sort(key=lambda x: x['step'])
            
            # Update calculator
            cursor.execute("""
                UPDATE custom_calculators
                SET json_definition = %s,
                    updated_at = NOW()
                WHERE calculator_id = %s
            """, (json.dumps(calc_json), calculator_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return {
                'success': True,
                'step_added': step_def,
                'total_steps': len(calc_json['calculation_steps']),
                'message': f"Step {step_number}: {variable_name} = {formula}"
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def calculator_builder_add_component(self, calculator_id: str, step_number: int,
                                         variable_name: str, component_name: str,
                                         inputs: Dict[str, str],
                                         description: str = None) -> Dict[str, Any]:
        """
        Add calculation step using pre-built component
        
        Args:
            calculator_id: Calculator UUID
            step_number: Step number
            variable_name: Variable to store result
            component_name: Component from common_components (e.g., "tiered_pricing_lookup")
            inputs: Input mappings {"lookup_value": "area_m2", "tier_table": "pricing.vinyl_tiers"}
            description: Step description
        
        Returns:
            {
                "success": True,
                "component_added": {...}
            }
        """
        try:
            conn = get_database_connection('ai_infrastructure')
            cursor = conn.cursor()
            
            # Load calculator
            cursor.execute("""
                SELECT json_definition
                FROM custom_calculators
                WHERE calculator_id = %s
            """, (calculator_id,))
            
            row = cursor.fetchone()
            if not row:
                return {'success': False, 'error': f'Calculator {calculator_id} not found'}
            
            calc_json = row['json_definition']
            
            # Build step definition
            step_def = {
                'step': step_number,
                'type': 'component',
                'variable': variable_name,
                'component': component_name,
                'inputs': inputs
            }
            
            if description:
                step_def['description'] = description
            
            # Add or update step
            existing_step = None
            for i, step in enumerate(calc_json['calculation_steps']):
                if step['step'] == step_number:
                    existing_step = i
                    break
            
            if existing_step is not None:
                calc_json['calculation_steps'][existing_step] = step_def
            else:
                calc_json['calculation_steps'].append(step_def)
            
            # Sort steps
            calc_json['calculation_steps'].sort(key=lambda x: x['step'])
            
            # Track component usage
            cursor.execute("""
                INSERT INTO custom_calculator_components (
                    calculator_id, component_name, component_type,
                    source_calculator, source_method, component_config, used_in_step
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                calculator_id,
                component_name,
                'calculation',
                'common_components',
                component_name,
                json.dumps({'inputs': inputs}),
                step_number
            ))
            
            # Update calculator
            cursor.execute("""
                UPDATE custom_calculators
                SET json_definition = %s,
                    updated_at = NOW()
                WHERE calculator_id = %s
            """, (json.dumps(calc_json), calculator_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return {
                'success': True,
                'component_added': step_def,
                'total_steps': len(calc_json['calculation_steps']),
                'message': f"Step {step_number}: {variable_name} = {component_name}({', '.join(inputs.keys())})"
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def calculator_builder_test(self, calculator_id: str, test_inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Test calculator with sample inputs
        
        Args:
            calculator_id: Calculator UUID
            test_inputs: Sample input values {"quantity": 50, "width_mm": 300, "height_mm": 400}
        
        Returns:
            {
                "success": True,
                "test_result": {
                    "total_price": 1250.00,
                    "unit_price": 25.00,
                    "breakdown": {...},
                    "execution_time_ms": 23
                },
                "validation": {
                    "all_parameters_provided": True,
                    "missing_parameters": [],
                    "calculation_errors": []
                }
            }
        """
        try:
            # Execute calculator
            result = self.executor.execute(calculator_id, test_inputs)
            
            # Build validation report
            conn = get_database_connection('ai_infrastructure')
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT json_definition
                FROM custom_calculators
                WHERE calculator_id = %s
            """, (calculator_id,))
            
            row = cursor.fetchone()
            calc_json = row['json_definition']
            
            # Check which parameters were provided
            required_params = [p['name'] for p in calc_json['parameters'] if p.get('required', False)]
            missing_params = [p for p in required_params if p not in test_inputs]
            
            cursor.close()
            conn.close()
            
            return {
                'success': True,
                'test_result': {
                    'total_price': float(result.total_price),
                    'unit_price': float(result.unit_price),
                    'quantity': result.quantity,
                    'breakdown': {k: float(v) for k, v in result.breakdown.items()},
                    'specifications': result.specifications,
                    'execution_time_ms': result.execution_time_ms
                },
                'validation': {
                    'all_parameters_provided': len(missing_params) == 0,
                    'missing_parameters': missing_params,
                    'calculation_errors': []
                },
                'message': f"✓ Test passed - Total: ${result.total_price}, Unit: ${result.unit_price} ({result.execution_time_ms}ms)"
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'validation': {
                    'all_parameters_provided': False,
                    'calculation_errors': [str(e)]
                }
            }
    
    def calculator_builder_save(self, calculator_id: str, as_template: bool = False,
                                usage_instructions: str = None,
                                activate: bool = True) -> Dict[str, Any]:
        """
        Save and optionally activate calculator
        
        Args:
            calculator_id: Calculator UUID
            as_template: Mark as reusable template
            usage_instructions: AI tool usage instructions
            activate: Set calculator to active (ready for use)
        
        Returns:
            {
                "success": True,
                "calculator_id": "...",
                "status": "active",
                "ready_for_use": True
            }
        """
        try:
            conn = get_database_connection('ai_infrastructure')
            cursor = conn.cursor()
            
            # Generate usage instructions if not provided
            if not usage_instructions:
                cursor.execute("""
                    SELECT name, description, json_definition
                    FROM custom_calculators
                    WHERE calculator_id = %s
                """, (calculator_id,))
                
                row = cursor.fetchone()
                calc_json = row['json_definition']
                params = calc_json.get('parameters', [])
                
                usage_instructions = f"""
Use this calculator for: {row['description']}

Required inputs:
{chr(10).join([f"- {p['name']}: {p.get('description', p['type'])}" for p in params if p.get('required', False)])}

Example usage:
calculator_builder_test(
    calculator_id="{calculator_id}",
    test_inputs={{
        {', '.join([f'"{p["name"]}": <value>' for p in params[:3]])}
    }}
)
"""
            
            # Update calculator
            cursor.execute("""
                UPDATE custom_calculators
                SET is_active = %s,
                    is_template = %s,
                    usage_instructions = %s,
                    updated_at = NOW()
                WHERE calculator_id = %s
            """, (activate, as_template, usage_instructions, calculator_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return {
                'success': True,
                'calculator_id': calculator_id,
                'status': 'active' if activate else 'draft',
                'is_template': as_template,
                'ready_for_use': activate,
                'message': f"Calculator saved and {'activated' if activate else 'saved as draft'}"
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}


# Tool wrapper functions for Registry V3
def calculator_builder_start(**kwargs):
    """Start building new custom calculator"""
    tools = CalculatorBuilderTools()
    return tools.calculator_builder_start(**kwargs)


def calculator_builder_add_parameter(**kwargs):
    """Add input parameter to calculator"""
    tools = CalculatorBuilderTools()
    return tools.calculator_builder_add_parameter(**kwargs)


def calculator_builder_set_formula(**kwargs):
    """Add calculation step with formula"""
    tools = CalculatorBuilderTools()
    return tools.calculator_builder_set_formula(**kwargs)


def calculator_builder_add_component(**kwargs):
    """Add calculation step using pre-built component"""
    tools = CalculatorBuilderTools()
    return tools.calculator_builder_add_component(**kwargs)


def calculator_builder_test(**kwargs):
    """Test calculator with sample inputs"""
    tools = CalculatorBuilderTools()
    return tools.calculator_builder_test(**kwargs)


def calculator_builder_save(**kwargs):
    """Save and activate calculator"""
    tools = CalculatorBuilderTools()
    return tools.calculator_builder_save(**kwargs)
