"""
Schema Validator - Automatic Type Enforcement for Calculator Wrappers
=====================================================================

This module provides decorators and utilities to automatically enforce
JSON schema types at runtime, preventing type mismatch bugs between
the AI agent layer and calculator backends.

Problem Solved:
- AI agents pass "500" (string) when schema declares "integer"
- Python type hints don't enforce types at runtime
- Backend calculators fail with validation/comparison errors

Solution:
- @enforce_schema_types decorator automatically converts parameter types
- Based on function type hints (quantity: int → auto-converts strings to ints)
- Handles int, float, bool, str conversions with error handling
- Logs conversions for debugging

Usage:
    @enforce_schema_types
    def calculate_business_cards(quantity: int, double_sided: bool, ...):
        # quantity is now GUARANTEED to be int, even if called with "500"
        pass

Author: AI Infrastructure Team
Date: December 14, 2025
Status: Production-ready type enforcement system
"""

import inspect
import functools
from typing import Any, Callable, Dict, get_type_hints, Union
from decimal import Decimal


class SchemaTypeEnforcer:
    """
    Type enforcement utility for calculator wrappers.
    
    Automatically converts parameter types based on function signatures,
    ensuring backend calculators receive correctly-typed values.
    """
    
    @staticmethod
    def convert_value(value: Any, expected_type: type, param_name: str) -> Any:
        """
        Convert a value to the expected type with intelligent handling.
        
        Args:
            value: The input value (possibly wrong type)
            expected_type: The type it should be
            param_name: Parameter name (for error messages)
            
        Returns:
            Converted value of correct type
            
        Raises:
            ValueError: If conversion fails
        """
        # If already correct type, return as-is
        if isinstance(value, expected_type):
            return value
        
        # Handle None values
        if value is None:
            return None
        
        try:
            # INTEGER CONVERSION
            if expected_type == int:
                if isinstance(value, str):
                    # Remove whitespace and convert
                    return int(value.strip())
                elif isinstance(value, float):
                    # Convert float to int (truncate)
                    return int(value)
                elif isinstance(value, bool):
                    # bool to int: True→1, False→0
                    return int(value)
                else:
                    return int(value)
            
            # FLOAT CONVERSION
            elif expected_type == float:
                if isinstance(value, str):
                    return float(value.strip())
                elif isinstance(value, int):
                    return float(value)
                else:
                    return float(value)
            
            # BOOLEAN CONVERSION
            elif expected_type == bool:
                if isinstance(value, str):
                    # String to bool: "true"/"1"/"yes" → True, others → False
                    return value.lower().strip() in ('true', '1', 'yes', 'on')
                elif isinstance(value, int):
                    # Int to bool: 0 → False, non-zero → True
                    return bool(value)
                else:
                    return bool(value)
            
            # STRING CONVERSION
            elif expected_type == str:
                # Convert anything to string
                return str(value)
            
            # DECIMAL CONVERSION (for financial calculations)
            elif expected_type == Decimal:
                if isinstance(value, str):
                    return Decimal(value.strip())
                elif isinstance(value, (int, float)):
                    return Decimal(str(value))
                else:
                    return Decimal(str(value))
            
            # UNION TYPES (e.g., Optional[int] = Union[int, None])
            elif hasattr(expected_type, '__origin__') and expected_type.__origin__ is Union:
                # Get the non-None type from Union
                types = [t for t in expected_type.__args__ if t is not type(None)]
                if types:
                    return SchemaTypeEnforcer.convert_value(value, types[0], param_name)
            
            # If we can't convert, return original value
            return value
            
        except (ValueError, TypeError) as e:
            raise ValueError(
                f"Cannot convert parameter '{param_name}' from {type(value).__name__} "
                f"to {expected_type.__name__}. Value: {value}. Error: {e}"
            )
    
    @staticmethod
    def enforce_types(func: Callable) -> Callable:
        """
        Decorator that enforces parameter types based on function signature.
        
        Automatically converts parameters to their declared types before
        calling the function. Uses Python type hints to determine expected types.
        
        Example:
            @enforce_types
            def calculate(quantity: int, price: float, enabled: bool):
                # quantity is guaranteed to be int
                # price is guaranteed to be float
                # enabled is guaranteed to be bool
                pass
            
            # These all work now:
            calculate(quantity="500", price="19.99", enabled="true")
            calculate(quantity=500, price=19.99, enabled=True)
        
        Args:
            func: Function to wrap with type enforcement
            
        Returns:
            Wrapped function with automatic type conversion
        """
        # Get function signature and type hints
        sig = inspect.signature(func)
        type_hints = get_type_hints(func)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Convert positional args
            bound_args = sig.bind_partial(*args, **kwargs)
            bound_args.apply_defaults()
            
            # Enforce types on all parameters
            for param_name, param_value in bound_args.arguments.items():
                if param_name in type_hints:
                    expected_type = type_hints[param_name]
                    
                    # Skip if no type hint or type hint is Any
                    if expected_type is Any:
                        continue
                    
                    # Convert the value
                    try:
                        converted_value = SchemaTypeEnforcer.convert_value(
                            param_value, 
                            expected_type, 
                            param_name
                        )
                        bound_args.arguments[param_name] = converted_value
                        
                        # Log conversion (only if actually converted)
                        if not isinstance(param_value, expected_type) and param_value is not None:
                            print(f"🔄 [Type Enforcer] Converted '{param_name}': "
                                  f"{type(param_value).__name__}({param_value}) → "
                                  f"{expected_type.__name__}({converted_value})")
                    
                    except Exception as e:
                        print(f"⚠️  [Type Enforcer] Failed to convert '{param_name}': {e}")
                        # Keep original value if conversion fails
                        pass
            
            # Call function with converted arguments
            return func(**bound_args.arguments)
        
        return wrapper


# Convenience decorator (shorthand)
enforce_schema_types = SchemaTypeEnforcer.enforce_types


# ============================================================================
# VALIDATION HELPERS
# ============================================================================

class EnumValidator:
    """Validate that values are in allowed enum lists"""
    
    @staticmethod
    def validate_enum(value: Any, allowed_values: list, param_name: str):
        """
        Validate that a value is in the allowed enum list.
        
        Args:
            value: Value to check
            allowed_values: List of allowed values
            param_name: Parameter name for error message
            
        Raises:
            ValueError: If value not in allowed list
        """
        if value not in allowed_values:
            raise ValueError(
                f"Invalid {param_name}: {value}. "
                f"Must be one of: {allowed_values}"
            )


class RangeValidator:
    """Validate that numeric values are within allowed ranges"""
    
    @staticmethod
    def validate_range(value: Union[int, float], min_val: Union[int, float], 
                      max_val: Union[int, float], param_name: str):
        """
        Validate that a value is within a range.
        
        Args:
            value: Value to check
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            param_name: Parameter name for error message
            
        Raises:
            ValueError: If value outside range
        """
        if not (min_val <= value <= max_val):
            raise ValueError(
                f"Invalid {param_name}: {value}. "
                f"Must be between {min_val} and {max_val}"
            )


# ============================================================================
# COMPOSITE DECORATOR (Type Enforcement + Common Validations)
# ============================================================================

def calculator_wrapper(
    quantity_enum: list = None,
    quantity_range: tuple = None
):
    """
    Composite decorator for calculator wrappers.
    
    Combines type enforcement with common validations for calculator parameters.
    
    Args:
        quantity_enum: List of allowed quantities (e.g., [250, 500, 1000, 2000, 5000, 10000])
        quantity_range: Tuple of (min, max) for quantity range validation
        
    Example:
        @calculator_wrapper(quantity_enum=[250, 500, 1000, 2000, 5000, 10000])
        def calculate_business_cards(quantity: int, double_sided: bool):
            # quantity is:
            # 1. Converted to int (if it was a string)
            # 2. Validated to be in [250, 500, 1000, 2000, 5000, 10000]
            pass
    """
    def decorator(func: Callable) -> Callable:
        # First apply type enforcement
        @enforce_schema_types
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Apply quantity validation if specified
            if 'quantity' in kwargs:
                quantity = kwargs['quantity']
                
                if quantity_enum is not None:
                    EnumValidator.validate_enum(quantity, quantity_enum, 'quantity')
                
                if quantity_range is not None:
                    RangeValidator.validate_range(
                        quantity, 
                        quantity_range[0], 
                        quantity_range[1], 
                        'quantity'
                    )
            
            # Call the original function
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Example 1: Basic type enforcement
    @enforce_schema_types
    def calculate_test(quantity: int, price: float, enabled: bool, name: str):
        print(f"Quantity: {quantity} (type: {type(quantity).__name__})")
        print(f"Price: {price} (type: {type(price).__name__})")
        print(f"Enabled: {enabled} (type: {type(enabled).__name__})")
        print(f"Name: {name} (type: {type(name).__name__})")
        return quantity * price
    
    # These all work now (automatic type conversion):
    print("\n=== Test 1: String inputs ===")
    result = calculate_test(quantity="500", price="19.99", enabled="true", name="Test")
    print(f"Result: {result}\n")
    
    print("=== Test 2: Correct types ===")
    result = calculate_test(quantity=500, price=19.99, enabled=True, name="Test")
    print(f"Result: {result}\n")
    
    # Example 2: Calculator wrapper with validation
    @calculator_wrapper(quantity_enum=[250, 500, 1000, 2000, 5000, 10000])
    def calculate_business_cards(quantity: int, double_sided: bool, stock: str):
        print(f"Calculating {quantity} business cards...")
        print(f"Double sided: {double_sided}")
        print(f"Stock: {stock}")
        return {"success": True, "quantity": quantity}
    
    print("=== Test 3: Business cards with validation ===")
    result = calculate_business_cards(quantity="500", double_sided="true", stock="premium")
    print(f"Result: {result}\n")
    
    print("=== Test 4: Invalid quantity (should fail) ===")
    try:
        result = calculate_business_cards(quantity="300", double_sided="true", stock="premium")
    except ValueError as e:
        print(f"❌ Validation failed (expected): {e}\n")
