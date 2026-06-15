"""
Universal Calculator Executor
Executes custom calculators from JSON definitions with formula evaluation and component execution
"""
import json
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import time
import sys
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'AI_infrastructure'))

from shared.database_utils import get_database_connection
from asteval import Interpreter  # Safe Python expression evaluator

# Import common components
from common_components import CommonComponents


@dataclass
class CalculatorExecutionResult:
    """Result from custom calculator execution"""
    total_price: Decimal
    unit_price: Decimal
    quantity: int
    breakdown: Dict[str, Any]
    specifications: Dict[str, Any]
    execution_time_ms: int
    calculator_id: str
    calculator_name: str


class UniversalCalculatorExecutor:
    """
    Execute custom calculators from JSON definitions
    
    Features:
    - Formula evaluation using asteval (safe Python subset)
    - Component execution (calls pre-built logic from common_components)
    - Parameter resolution (checks overrides first, then global values)
    - Context tracking (variables available at each step)
    - Performance monitoring
    """
    
    def __init__(self):
        """Initialize executor"""
        self.components = CommonComponents()
        self.conn = None
        self.cursor = None
        
    def execute(self, calculator_id: str, inputs: Dict[str, Any]) -> CalculatorExecutionResult:
        """
        Execute custom calculator
        
        Args:
            calculator_id: UUID of custom calculator
            inputs: Input parameters from user
        
        Returns:
            CalculatorExecutionResult with pricing breakdown
        """
        start_time = time.time()
        
        try:
            # 1. Load calculator definition from database
            calc_json = self._load_calculator(calculator_id)
            
            # 2. Validate inputs against parameter definitions
            validated_inputs = self._validate_inputs(calc_json['parameters'], inputs)
            
            # 3. Resolve pricing constants (check overrides, then global values)
            pricing_constants = self._resolve_pricing_constants(
                calculator_id, 
                calc_json.get('pricing_constants', {})
            )
            
            # 4. Initialize execution context
            context = self._initialize_context(validated_inputs, pricing_constants)
            
            # 5. Execute calculation steps sequentially
            for step in calc_json['calculation_steps']:
                result = self._execute_step(step, context, calculator_id)
                context['calculated_values'][step['variable']] = result
            
            # 6. Build result structure
            result_obj = self._build_result(
                calc_json['result_structure'], 
                context,
                calculator_id,
                calc_json['name']
            )
            
            # 7. Update usage statistics
            execution_time_ms = int((time.time() - start_time) * 1000)
            result_obj.execution_time_ms = execution_time_ms
            self._update_usage_stats(calculator_id, execution_time_ms)
            
            return result_obj
            
        finally:
            self._close_connection()
    
    def _load_calculator(self, calculator_id: str) -> Dict:
        """Load calculator JSON from database"""
        self.conn = get_database_connection('ai_infrastructure')
        self.cursor = self.conn.cursor()
        
        self.cursor.execute("""
            SELECT calculator_id, name, json_definition
            FROM custom_calculators
            WHERE calculator_id = %s AND is_active = TRUE
        """, (calculator_id,))
        
        row = self.cursor.fetchone()
        if not row:
            raise ValueError(f'Calculator {calculator_id} not found or inactive')
        
        calc = {
            'id': str(row['calculator_id']),
            'name': row['name'],
            **row['json_definition']
        }
        
        return calc
    
    def _validate_inputs(self, param_defs: List[Dict], inputs: Dict) -> Dict:
        """Validate input parameters against definitions"""
        validated = {}
        
        for param_def in param_defs:
            name = param_def['name']
            
            # Check required parameters
            if param_def.get('required', False) and name not in inputs:
                raise ValueError(f'Required parameter missing: {name}')
            
            # Get value or default
            if name in inputs:
                value = inputs[name]
            elif 'default' in param_def:
                value = param_def['default']
            else:
                continue
            
            # Type conversion
            param_type = param_def.get('type', 'string')
            if param_type == 'integer':
                value = int(value)
            elif param_type == 'number':
                value = Decimal(str(value))
            elif param_type == 'select':
                # Validate against options
                options = [opt['value'] if isinstance(opt, dict) else opt 
                          for opt in param_def.get('options', [])]
                if options and value not in options:
                    raise ValueError(f'Invalid value for {name}: {value}. Must be one of: {options}')
            
            validated[name] = value
        
        return validated
    
    def _resolve_pricing_constants(self, calculator_id: str, constants_def: Dict) -> Dict:
        """
        Resolve pricing constants with parameter override support
        
        For each constant that references a parameter, check:
        1. Is there override in custom_calculator_parameters?
        2. If not, use global value from calculator_pricing_parameters
        """
        resolved = {}
        
        for key, value in constants_def.items():
            if isinstance(value, str) and value.startswith('param:'):
                # This is a parameter reference: "param:labor_rate_trade"
                param_name = value[6:]  # Remove "param:" prefix
                resolved[key] = self._get_parameter_value(calculator_id, param_name)
            elif isinstance(value, dict):
                # Nested constants
                resolved[key] = self._resolve_pricing_constants(calculator_id, value)
            else:
                # Literal value
                resolved[key] = value
        
        return resolved
    
    def _get_parameter_value(self, calculator_id: str, param_name: str) -> Decimal:
        """
        Get parameter value with override precedence
        
        1. Check custom_calculator_parameters for override
        2. Fall back to global value in calculator_pricing_parameters
        """
        # Check for override
        self.cursor.execute("""
            SELECT override_value
            FROM custom_calculator_parameters
            WHERE calculator_id = %s 
              AND parameter_name = %s
              AND is_overridden = TRUE
        """, (calculator_id, param_name))
        
        row = self.cursor.fetchone()
        if row and row['override_value'] is not None:
            return Decimal(str(row['override_value']))
        
        # Get global value
        self.cursor.execute("""
            SELECT base_value
            FROM calculator_pricing_parameters
            WHERE parameter_name = %s
        """, (param_name,))
        
        row = self.cursor.fetchone()
        if not row or row['base_value'] is None:
            raise ValueError(f'Parameter not found: {param_name}')
        
        return Decimal(str(row['base_value']))
    
    def _initialize_context(self, inputs: Dict, pricing_constants: Dict) -> Dict:
        """Initialize execution context"""
        return {
            **inputs,  # User inputs
            'pricing': pricing_constants,  # Pricing parameters
            'calculated_values': {},  # Results from each step
            'Decimal': Decimal,  # Make Decimal available in formulas
        }
    
    def _execute_step(self, step: Dict, context: Dict, calculator_id: str) -> Any:
        """Execute a single calculation step"""
        step_type = step.get('type', 'formula')
        
        if step_type == 'formula':
            return self._eval_formula(step['formula'], context)
        elif step_type == 'component':
            return self._call_component(step, context, calculator_id)
        else:
            raise ValueError(f'Unknown step type: {step_type}')
    
    def _eval_formula(self, formula: str, context: Dict) -> Any:
        """
        Safely evaluate formula using asteval
        
        asteval provides a safe subset of Python:
        - Math operations: +, -, *, /, **, %
        - Comparisons: <, >, <=, >=, ==, !=
        - Logic: and, or, not
        - Built-in functions: min, max, abs, round, len
        - No imports, no file access, no system calls
        """
        # Create asteval interpreter with context
        aeval = Interpreter()
        
        # Add context variables
        for key, value in context.items():
            if key != 'calculated_values':
                aeval.symtable[key] = value
        
        # Add calculated values (from previous steps)
        for key, value in context.get('calculated_values', {}).items():
            aeval.symtable[key] = value
        
        # Evaluate formula
        try:
            result = aeval(formula)
            
            if aeval.error:
                raise ValueError(f'Formula error: {aeval.error[0].get_error()}')
            
            return result
            
        except Exception as e:
            raise ValueError(f'Formula evaluation failed: {formula}\nError: {e}')
    
    def _call_component(self, step: Dict, context: Dict, calculator_id: str) -> Any:
        """Call pre-built component from common_components"""
        component_name = step['component']
        inputs = step.get('inputs', {})
        
        # Resolve input values from context
        resolved_inputs = {}
        for input_key, input_value in inputs.items():
            if isinstance(input_value, str) and input_value in context:
                resolved_inputs[input_key] = context[input_value]
            elif isinstance(input_value, str) and input_value in context.get('calculated_values', {}):
                resolved_inputs[input_key] = context['calculated_values'][input_value]
            else:
                resolved_inputs[input_key] = input_value
        
        # Call component method
        if not hasattr(self.components, component_name):
            raise ValueError(f'Component not found: {component_name}')
        
        component_method = getattr(self.components, component_name)
        return component_method(**resolved_inputs)
    
    def _build_result(self, result_structure: Dict, context: Dict, 
                     calculator_id: str, calculator_name: str) -> CalculatorExecutionResult:
        """Build final result object"""
        # Resolve result values from context
        def resolve_value(ref: str) -> Any:
            if ref in context['calculated_values']:
                return context['calculated_values'][ref]
            elif ref in context:
                return context[ref]
            else:
                # Try evaluating as formula
                return self._eval_formula(ref, context)
        
        total_price = Decimal(str(resolve_value(result_structure['total_price'])))
        unit_price = Decimal(str(resolve_value(result_structure['unit_price'])))
        quantity = int(resolve_value(result_structure.get('quantity', context.get('quantity', 1))))
        
        # Build breakdown
        breakdown = {}
        for key, ref in result_structure.get('breakdown', {}).items():
            breakdown[key] = Decimal(str(resolve_value(ref)))
        
        # Build specifications
        specifications = {}
        for key, ref in result_structure.get('specifications', {}).items():
            specifications[key] = resolve_value(ref)
        
        return CalculatorExecutionResult(
            total_price=total_price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            unit_price=unit_price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            quantity=quantity,
            breakdown=breakdown,
            specifications=specifications,
            execution_time_ms=0,  # Will be set by execute()
            calculator_id=calculator_id,
            calculator_name=calculator_name
        )
    
    def _update_usage_stats(self, calculator_id: str, execution_time_ms: int):
        """Update calculator usage statistics"""
        try:
            self.cursor.execute("""
                UPDATE custom_calculators
                SET usage_count = usage_count + 1,
                    last_used_at = NOW(),
                    avg_calculation_time_ms = CASE
                        WHEN avg_calculation_time_ms IS NULL THEN %s
                        ELSE (avg_calculation_time_ms * usage_count + %s) / (usage_count + 1)
                    END,
                    updated_at = NOW()
                WHERE calculator_id = %s
            """, (execution_time_ms, execution_time_ms, calculator_id))
            self.conn.commit()
        except Exception as e:
            print(f'Warning: Failed to update usage stats: {e}')
            self.conn.rollback()
    
    def _close_connection(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
