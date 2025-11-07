"""
Validators - Input validation helper functions
Part of V4 Modular Architecture

Responsibilities:
- Validate tool parameters before execution
- Validate user inputs (email, session_id, etc.)
- Validate API responses
- Type checking and conversion
- Schema validation
"""

from typing import Any, Optional, Dict, List, Union
import re
import sys
from pathlib import Path

# Add paths
ai_infra_dir = Path(__file__).parent.parent
if str(ai_infra_dir) not in sys.path:
    sys.path.insert(0, str(ai_infra_dir))

from utils.logger import get_logger
from utils.error_handler import ValidationError

logger = get_logger(__name__)


# ============================================================
# BASIC TYPE VALIDATION
# ============================================================

def validate_type(value: Any, expected_type: type, field_name: str = "field") -> Any:
    """
    Validate that value is of expected type.
    
    Args:
        value: Value to validate
        expected_type: Expected Python type
        field_name: Name of field (for error messages)
        
    Returns:
        Value (unchanged) if valid
        
    Raises:
        ValidationError: If type mismatch
    """
    if not isinstance(value, expected_type):
        raise ValidationError(
            f"{field_name} must be {expected_type.__name__}, got {type(value).__name__}",
            {'field': field_name, 'expected': expected_type.__name__, 'got': type(value).__name__}
        )
    return value


def validate_required(value: Any, field_name: str = "field") -> Any:
    """
    Validate that value is not None or empty.
    
    Args:
        value: Value to validate
        field_name: Name of field (for error messages)
        
    Returns:
        Value (unchanged) if valid
        
    Raises:
        ValidationError: If value is None or empty
    """
    if value is None:
        raise ValidationError(
            f"{field_name} is required",
            {'field': field_name, 'error': 'missing'}
        )
    
    # Check for empty strings, lists, dicts
    if isinstance(value, (str, list, dict)) and not value:
        raise ValidationError(
            f"{field_name} cannot be empty",
            {'field': field_name, 'error': 'empty'}
        )
    
    return value


# ============================================================
# STRING VALIDATION
# ============================================================

def validate_email(email: str) -> str:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        Email address (lowercased) if valid
        
    Raises:
        ValidationError: If email format invalid
    """
    email = email.strip().lower()
    
    # Basic email regex
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        raise ValidationError(
            f"Invalid email format: {email}",
            {'field': 'email', 'value': email}
        )
    
    return email


def validate_session_id(session_id: str) -> str:
    """
    Validate session ID format (alphanumeric + hyphen).
    
    Args:
        session_id: Session ID to validate
        
    Returns:
        Session ID if valid
        
    Raises:
        ValidationError: If session ID format invalid
    """
    session_id = session_id.strip()
    
    # Allow alphanumeric, hyphens, underscores
    pattern = r'^[a-zA-Z0-9_-]+$'
    
    if not re.match(pattern, session_id):
        raise ValidationError(
            f"Invalid session ID format: {session_id}",
            {'field': 'session_id', 'value': session_id}
        )
    
    # Reasonable length check
    if len(session_id) < 3 or len(session_id) > 128:
        raise ValidationError(
            f"Session ID length must be 3-128 characters, got {len(session_id)}",
            {'field': 'session_id', 'length': len(session_id)}
        )
    
    return session_id


def validate_string_length(
    value: str,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    field_name: str = "field"
) -> str:
    """
    Validate string length constraints.
    
    Args:
        value: String to validate
        min_length: Minimum allowed length (optional)
        max_length: Maximum allowed length (optional)
        field_name: Name of field (for error messages)
        
    Returns:
        String if valid
        
    Raises:
        ValidationError: If length constraints violated
    """
    length = len(value)
    
    if min_length is not None and length < min_length:
        raise ValidationError(
            f"{field_name} must be at least {min_length} characters, got {length}",
            {'field': field_name, 'min': min_length, 'actual': length}
        )
    
    if max_length is not None and length > max_length:
        raise ValidationError(
            f"{field_name} must be at most {max_length} characters, got {length}",
            {'field': field_name, 'max': max_length, 'actual': length}
        )
    
    return value


# ============================================================
# NUMERIC VALIDATION
# ============================================================

def validate_integer(
    value: Union[int, str],
    min_value: Optional[int] = None,
    max_value: Optional[int] = None,
    field_name: str = "field"
) -> int:
    """
    Validate and convert to integer.
    
    Args:
        value: Value to validate (int or string)
        min_value: Minimum allowed value (optional)
        max_value: Maximum allowed value (optional)
        field_name: Name of field (for error messages)
        
    Returns:
        Integer value if valid
        
    Raises:
        ValidationError: If conversion fails or constraints violated
    """
    # Try to convert to int
    try:
        int_value = int(value)
    except (ValueError, TypeError):
        raise ValidationError(
            f"{field_name} must be an integer, got '{value}'",
            {'field': field_name, 'value': str(value)}
        )
    
    # Check constraints
    if min_value is not None and int_value < min_value:
        raise ValidationError(
            f"{field_name} must be at least {min_value}, got {int_value}",
            {'field': field_name, 'min': min_value, 'actual': int_value}
        )
    
    if max_value is not None and int_value > max_value:
        raise ValidationError(
            f"{field_name} must be at most {max_value}, got {int_value}",
            {'field': field_name, 'max': max_value, 'actual': int_value}
        )
    
    return int_value


def validate_positive_integer(value: Union[int, str], field_name: str = "field") -> int:
    """
    Validate positive integer (> 0).
    
    Args:
        value: Value to validate
        field_name: Name of field (for error messages)
        
    Returns:
        Positive integer if valid
        
    Raises:
        ValidationError: If not positive integer
    """
    return validate_integer(value, min_value=1, field_name=field_name)


# ============================================================
# COLLECTION VALIDATION
# ============================================================

def validate_list(
    value: Any,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    field_name: str = "field"
) -> list:
    """
    Validate list and length constraints.
    
    Args:
        value: Value to validate
        min_length: Minimum list length (optional)
        max_length: Maximum list length (optional)
        field_name: Name of field (for error messages)
        
    Returns:
        List if valid
        
    Raises:
        ValidationError: If not list or constraints violated
    """
    validate_type(value, list, field_name)
    
    length = len(value)
    
    if min_length is not None and length < min_length:
        raise ValidationError(
            f"{field_name} must have at least {min_length} items, got {length}",
            {'field': field_name, 'min': min_length, 'actual': length}
        )
    
    if max_length is not None and length > max_length:
        raise ValidationError(
            f"{field_name} must have at most {max_length} items, got {length}",
            {'field': field_name, 'max': max_length, 'actual': length}
        )
    
    return value


def validate_dict_keys(
    value: dict,
    required_keys: List[str],
    optional_keys: Optional[List[str]] = None,
    field_name: str = "field"
) -> dict:
    """
    Validate dictionary has required keys and no extra keys.
    
    Args:
        value: Dictionary to validate
        required_keys: Keys that must be present
        optional_keys: Keys that may be present (optional)
        field_name: Name of field (for error messages)
        
    Returns:
        Dictionary if valid
        
    Raises:
        ValidationError: If required keys missing or extra keys present
    """
    validate_type(value, dict, field_name)
    
    # Check required keys
    missing = set(required_keys) - set(value.keys())
    if missing:
        raise ValidationError(
            f"{field_name} missing required keys: {', '.join(missing)}",
            {'field': field_name, 'missing': list(missing)}
        )
    
    # Check for extra keys (if optional_keys provided)
    if optional_keys is not None:
        allowed = set(required_keys) | set(optional_keys)
        extra = set(value.keys()) - allowed
        if extra:
            raise ValidationError(
                f"{field_name} has unexpected keys: {', '.join(extra)}",
                {'field': field_name, 'extra': list(extra)}
            )
    
    return value


# ============================================================
# TOOL PARAMETER VALIDATION
# ============================================================

def validate_tool_call(tool_name: str, parameters: dict, tool_schema: dict) -> dict:
    """
    Validate tool call parameters against schema.
    
    Args:
        tool_name: Name of tool being called
        parameters: Parameters provided for tool
        tool_schema: Tool schema from registry
        
    Returns:
        Parameters (unchanged) if valid
        
    Raises:
        ValidationError: If parameters invalid
    """
    # Extract input schema
    input_schema = tool_schema.get('input_schema', {})
    required = input_schema.get('required', [])
    properties = input_schema.get('properties', {})
    
    # Check required parameters
    for param in required:
        if param not in parameters:
            raise ValidationError(
                f"Tool {tool_name} missing required parameter: {param}",
                {'tool': tool_name, 'parameter': param}
            )
    
    # Check parameter types (basic validation)
    for param, value in parameters.items():
        if param not in properties:
            logger.warning(f"Tool {tool_name} received unexpected parameter: {param}")
            continue
        
        param_schema = properties[param]
        expected_type = param_schema.get('type')
        
        # Basic type checking
        if expected_type == 'string' and not isinstance(value, str):
            raise ValidationError(
                f"Tool {tool_name} parameter {param} must be string, got {type(value).__name__}",
                {'tool': tool_name, 'parameter': param, 'expected': 'string', 'got': type(value).__name__}
            )
        elif expected_type == 'integer' and not isinstance(value, int):
            raise ValidationError(
                f"Tool {tool_name} parameter {param} must be integer, got {type(value).__name__}",
                {'tool': tool_name, 'parameter': param, 'expected': 'integer', 'got': type(value).__name__}
            )
        elif expected_type == 'boolean' and not isinstance(value, bool):
            raise ValidationError(
                f"Tool {tool_name} parameter {param} must be boolean, got {type(value).__name__}",
                {'tool': tool_name, 'parameter': param, 'expected': 'boolean', 'got': type(value).__name__}
            )
        elif expected_type == 'array' and not isinstance(value, list):
            raise ValidationError(
                f"Tool {tool_name} parameter {param} must be array, got {type(value).__name__}",
                {'tool': tool_name, 'parameter': param, 'expected': 'array', 'got': type(value).__name__}
            )
        elif expected_type == 'object' and not isinstance(value, dict):
            raise ValidationError(
                f"Tool {tool_name} parameter {param} must be object, got {type(value).__name__}",
                {'tool': tool_name, 'parameter': param, 'expected': 'object', 'got': type(value).__name__}
            )
    
    logger.debug(f"Tool {tool_name} parameters validated successfully")
    return parameters


# ============================================================
# MODULE EXPORTS
# ============================================================

__all__ = [
    # Type validation
    'validate_type',
    'validate_required',
    # String validation
    'validate_email',
    'validate_session_id',
    'validate_string_length',
    # Numeric validation
    'validate_integer',
    'validate_positive_integer',
    # Collection validation
    'validate_list',
    'validate_dict_keys',
    # Tool validation
    'validate_tool_call'
]
