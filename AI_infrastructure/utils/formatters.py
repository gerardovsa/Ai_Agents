"""
Formatters - Response formatting utilities
Part of V4 Modular Architecture

Responsibilities:
- Format API responses consistently
- Truncate long text for display
- Format timestamps and dates
- Format tool results for Claude API
- Pretty-print JSON and data structures
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import json
import sys
from pathlib import Path

# Add paths
ai_infra_dir = Path(__file__).parent.parent
if str(ai_infra_dir) not in sys.path:
    sys.path.insert(0, str(ai_infra_dir))

from utils.logger import get_logger

logger = get_logger(__name__)


# ============================================================
# TEXT FORMATTING
# ============================================================

def truncate_text(
    text: str,
    max_length: int = 100,
    suffix: str = "..."
) -> str:
    """
    Truncate text to maximum length with suffix.
    
    Args:
        text: Text to truncate
        max_length: Maximum length (including suffix)
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    truncate_at = max_length - len(suffix)
    return text[:truncate_at] + suffix


def truncate_dict(
    data: dict,
    max_key_length: int = 50,
    max_value_length: int = 100
) -> dict:
    """
    Truncate dictionary keys and values for display.
    
    Args:
        data: Dictionary to truncate
        max_key_length: Maximum key length
        max_value_length: Maximum value length
        
    Returns:
        Dictionary with truncated strings
    """
    result = {}
    for key, value in data.items():
        # Truncate key if string
        if isinstance(key, str):
            key = truncate_text(key, max_key_length)
        
        # Truncate value if string
        if isinstance(value, str):
            value = truncate_text(value, max_value_length)
        elif isinstance(value, dict):
            value = truncate_dict(value, max_key_length, max_value_length)
        elif isinstance(value, list):
            value = truncate_list(value, max_value_length)
        
        result[key] = value
    
    return result


def truncate_list(
    data: list,
    max_item_length: int = 100,
    max_items: Optional[int] = None
) -> list:
    """
    Truncate list items and optionally limit list length.
    
    Args:
        data: List to truncate
        max_item_length: Maximum length per item (if string)
        max_items: Maximum number of items to keep (optional)
        
    Returns:
        List with truncated items
    """
    # Limit list length if specified
    if max_items and len(data) > max_items:
        data = data[:max_items]
        data.append(f"... ({len(data) - max_items} more items)")
    
    # Truncate string items
    result = []
    for item in data:
        if isinstance(item, str):
            item = truncate_text(item, max_item_length)
        elif isinstance(item, dict):
            item = truncate_dict(item, 50, max_item_length)
        result.append(item)
    
    return result


# ============================================================
# DATE/TIME FORMATTING
# ============================================================

def format_timestamp(
    timestamp: Union[datetime, float, int, str],
    format_string: str = "%Y-%m-%d %H:%M:%S"
) -> str:
    """
    Format timestamp to readable string.
    
    Args:
        timestamp: Timestamp (datetime, unix timestamp, or ISO string)
        format_string: strftime format string
        
    Returns:
        Formatted timestamp string
    """
    # Convert to datetime if needed
    if isinstance(timestamp, (int, float)):
        dt = datetime.fromtimestamp(timestamp)
    elif isinstance(timestamp, str):
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    elif isinstance(timestamp, datetime):
        dt = timestamp
    else:
        return str(timestamp)
    
    return dt.strftime(format_string)


def format_duration(seconds: Union[int, float]) -> str:
    """
    Format duration in seconds to human-readable string.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration (e.g., "2h 15m 30s")
    """
    seconds = int(seconds)
    
    if seconds < 60:
        return f"{seconds}s"
    
    minutes = seconds // 60
    seconds = seconds % 60
    
    if minutes < 60:
        return f"{minutes}m {seconds}s"
    
    hours = minutes // 60
    minutes = minutes % 60
    
    if hours < 24:
        return f"{hours}h {minutes}m"
    
    days = hours // 24
    hours = hours % 24
    
    return f"{days}d {hours}h"


# ============================================================
# JSON FORMATTING
# ============================================================

def format_json(
    data: Any,
    indent: int = 2,
    truncate: bool = False,
    max_length: int = 1000
) -> str:
    """
    Format data as pretty-printed JSON.
    
    Args:
        data: Data to format
        indent: Indentation spaces
        truncate: Whether to truncate long values
        max_length: Maximum length if truncating
        
    Returns:
        Formatted JSON string
    """
    try:
        # Truncate if requested
        if truncate:
            if isinstance(data, dict):
                data = truncate_dict(data, max_value_length=max_length)
            elif isinstance(data, list):
                data = truncate_list(data, max_item_length=max_length)
        
        return json.dumps(data, indent=indent, ensure_ascii=False, default=str)
    except Exception as e:
        logger.warning(f"Failed to format JSON: {e}")
        return str(data)


# ============================================================
# TOOL RESULT FORMATTING
# ============================================================

def format_tool_result(
    tool_name: str,
    result: Any,
    success: bool = True,
    error: Optional[str] = None
) -> Dict[str, Any]:
    """
    Format tool execution result for Claude API.
    
    Args:
        tool_name: Name of tool executed
        result: Tool execution result
        success: Whether execution succeeded
        error: Error message if failed
        
    Returns:
        Formatted tool result dictionary
    """
    if success:
        # Format successful result
        if isinstance(result, (dict, list)):
            content = format_json(result, truncate=True, max_length=500)
        else:
            content = str(result)
        
        return {
            'type': 'tool_result',
            'tool_name': tool_name,
            'content': content,
            'is_error': False
        }
    else:
        # Format error result
        return {
            'type': 'tool_result',
            'tool_name': tool_name,
            'content': error or "Tool execution failed",
            'is_error': True
        }


# ============================================================
# API RESPONSE FORMATTING
# ============================================================

def format_success_response(
    data: Any,
    message: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Format successful API response.
    
    Args:
        data: Response data
        message: Optional success message
        metadata: Optional metadata (pagination, etc.)
        
    Returns:
        Formatted success response
    """
    response = {
        'success': True,
        'data': data
    }
    
    if message:
        response['message'] = message
    
    if metadata:
        response['metadata'] = metadata
    
    return response


def format_error_response(
    error: str,
    error_type: str = 'unknown',
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Format error API response.
    
    Args:
        error: Error message
        error_type: Error category
        details: Optional error details
        
    Returns:
        Formatted error response
    """
    response = {
        'success': False,
        'error': error,
        'error_type': error_type
    }
    
    if details:
        response['details'] = details
    
    return response


# ============================================================
# DISPLAY FORMATTING
# ============================================================

def format_list_display(
    items: List[Any],
    title: Optional[str] = None,
    numbered: bool = True,
    max_items: Optional[int] = None
) -> str:
    """
    Format list for display with optional title and numbering.
    
    Args:
        items: List of items to display
        title: Optional title
        numbered: Whether to number items
        max_items: Maximum items to display
        
    Returns:
        Formatted list string
    """
    lines = []
    
    if title:
        lines.append(title)
        lines.append("-" * len(title))
    
    display_items = items[:max_items] if max_items else items
    
    for i, item in enumerate(display_items, 1):
        if numbered:
            lines.append(f"{i}. {item}")
        else:
            lines.append(f"  {item}")
    
    if max_items and len(items) > max_items:
        lines.append(f"  ... and {len(items) - max_items} more")
    
    return "\n".join(lines)


def format_dict_display(
    data: Dict[str, Any],
    title: Optional[str] = None,
    indent: int = 0
) -> str:
    """
    Format dictionary for display.
    
    Args:
        data: Dictionary to display
        title: Optional title
        indent: Indentation level
        
    Returns:
        Formatted dictionary string
    """
    lines = []
    prefix = "  " * indent
    
    if title:
        lines.append(prefix + title)
        lines.append(prefix + "-" * len(title))
    
    for key, value in data.items():
        if isinstance(value, dict):
            lines.append(f"{prefix}{key}:")
            lines.append(format_dict_display(value, indent=indent + 1))
        elif isinstance(value, list):
            lines.append(f"{prefix}{key}: [{len(value)} items]")
        else:
            value_str = truncate_text(str(value), 80)
            lines.append(f"{prefix}{key}: {value_str}")
    
    return "\n".join(lines)


# ============================================================
# MODULE EXPORTS
# ============================================================

__all__ = [
    # Text formatting
    'truncate_text',
    'truncate_dict',
    'truncate_list',
    # Date/time formatting
    'format_timestamp',
    'format_duration',
    # JSON formatting
    'format_json',
    # Tool result formatting
    'format_tool_result',
    # API response formatting
    'format_success_response',
    'format_error_response',
    # Display formatting
    'format_list_display',
    'format_dict_display'
]
